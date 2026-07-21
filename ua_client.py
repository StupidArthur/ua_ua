"""
OPC UA Client — 枚举节点 & 采集数据快照

用法:
    python ua_client.py --url opc.tcp://host:port --node ns=2;s=xxx --out snapshot.json
    python ua_client.py --config config.json
    python ua_client.py --url opc.tcp://host:port --browse-root "ns=2;s=P_xxx" --out snapshot.json
"""

import asyncio
import argparse
import base64
import json
import logging
import sys
from pathlib import Path
from datetime import datetime, timezone

from asyncua import Client, Node, ua
from asyncua.ua.uatypes import VariantType

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("ua_client")


# ---------- 值序列化 ----------

def serialize_value(val, vt: VariantType) -> object:
    """将 UA Variant 值转为可 JSON 序列化的对象。"""
    if val is None:
        return None

    # 基本标量
    if vt in (
        VariantType.Boolean,
        VariantType.SByte, VariantType.Int16, VariantType.Int32, VariantType.Int64,
        VariantType.Byte, VariantType.UInt16, VariantType.UInt32, VariantType.UInt64,
        VariantType.Float, VariantType.Double,
    ):
        return val

    if vt in (VariantType.String, VariantType.XmlElement):
        return str(val)

    if vt == VariantType.DateTime:
        return val.isoformat() if hasattr(val, "isoformat") else str(val)

    if vt == VariantType.Guid:
        return str(val)

    if vt == VariantType.ByteString:
        if isinstance(val, bytes):
            return {"__type__": "ByteString", "b64": base64.b64encode(val).decode()}
        return str(val)

    if vt == VariantType.LocalizedText:
        return {"__type__": "LocalizedText", "Text": val.Text, "Locale": val.Locale}

    if vt == VariantType.QualifiedName:
        return {"__type__": "QualifiedName", "Name": val.Name, "NamespaceIndex": val.NamespaceIndex}

    if vt == VariantType.NodeId:
        return {"__type__": "NodeId", "NodeId": str(val)}

    if vt == VariantType.StatusCode:
        return {"__type__": "StatusCode", "value": val.value}

    if vt == VariantType.ExtensionObject:
        return serialize_extension_object(val)

    # 数组
    if isinstance(val, (list, tuple)):
        return [serialize_value(item, vt) for item in val]

    return str(val)


def serialize_extension_object(obj) -> dict | None:
    """序列化 ExtensionObject，按类型名提取字段。"""
    if obj is None:
        return None

    cls_name = obj.__class__.__name__

    # EnumValueType: Value(int) + DisplayName(LocalizedText) + Description(LocalizedText)
    if cls_name == "EnumValueType":
        return {
            "__type__": "EnumValueType",
            "Value": obj.Value,
            "DisplayName": serialize_value(obj.DisplayName, VariantType.LocalizedText) if obj.DisplayName else None,
            "Description": serialize_value(obj.Description, VariantType.LocalizedText) if obj.Description else None,
        }

    # Range: Low(float) + High(float)
    if cls_name == "Range":
        return {
            "__type__": "Range",
            "Low": obj.Low,
            "High": obj.High,
        }

    # EUInformation: NamespaceUri, UnitId, DisplayName, Description
    if cls_name == "EUInformation":
        return {
            "__type__": "EUInformation",
            "NamespaceUri": str(obj.NamespaceUri) if obj.NamespaceUri else None,
            "UnitId": obj.UnitId,
            "DisplayName": serialize_value(obj.DisplayName, VariantType.LocalizedText) if obj.DisplayName else None,
            "Description": serialize_value(obj.Description, VariantType.LocalizedText) if obj.Description else None,
        }

    # 通用 ExtensionObject 回退
    if hasattr(obj, "Body") and hasattr(obj, "TypeId"):
        result = {"__type__": "ExtensionObject", "TypeId": str(obj.TypeId)}
        if obj.Body is not None:
            result["Body"] = str(obj.Body)
        return result

    # 已解码但未知类型 — 用 __ua_types__ 遍历字段
    if hasattr(obj, "__ua_types__"):
        fields = {}
        for field_name in obj.__ua_types__:
            if hasattr(obj, field_name):
                fields[field_name] = str(getattr(obj, field_name))
        return {"__type__": cls_name, **fields}

    return {"__type__": cls_name, "raw": str(obj)}


# ---------- 节点读取 ----------

async def read_node_info(node: Node) -> dict:
    """读取单个节点的 browse_name, display_name, node_class, value。"""
    info = {
        "node_id": str(node.nodeid),
        "browse_name": None,
        "display_name": None,
        "node_class": None,
        "data_type": None,
        "value": None,
        "timestamp": None,
    }

    try:
        bn = await node.read_browse_name()
        info["browse_name"] = bn.Name
    except Exception:
        pass

    try:
        dn = await node.read_display_name()
        info["display_name"] = dn.Text if dn else None
    except Exception:
        pass

    try:
        nc = await node.read_node_class()
        info["node_class"] = nc.name
    except Exception:
        pass

    # 只对 Variable 节点读值
    try:
        if info["node_class"] == "Variable":
            dv = await node.read_data_value()
            if dv and dv.Value is not None:
                vt = dv.Value.VariantType
                info["data_type"] = vt.name if vt else None
                info["value"] = serialize_value(dv.Value.Value, vt)
                if dv.ServerTimestamp:
                    info["timestamp"] = dv.ServerTimestamp.isoformat()
                elif dv.SourceTimestamp:
                    info["timestamp"] = dv.SourceTimestamp.isoformat()
    except Exception as e:
        info["_read_error"] = str(e)

    return info


# ---------- 递归浏览 ----------

async def browse_subtree(
    node: Node,
    max_depth: int = 10,
    _depth: int = 0,
) -> dict:
    """递归浏览节点树，返回嵌套字典。"""
    if _depth > max_depth:
        return {"node_id": str(node.nodeid), "_truncated": True}

    info = await read_node_info(node)

    children = []
    try:
        for child in await node.get_children():
            child_info = await browse_subtree(child, max_depth, _depth + 1)
            children.append(child_info)
    except Exception as e:
        info["_browse_error"] = str(e)

    if children:
        info["children"] = children

    return info


# ---------- 按 BrowseName 路径查找节点 ----------

async def resolve_browse_path(client: Client, start_node: Node, path: list[str]) -> Node:
    """从 start_node 出发，按 BrowseName 路径逐层查找。
    path 例如 ["DeviceSetView"] 或 ["SOV1", "Runtime"]
    """
    current = start_node
    for name in path:
        found = None
        for child in await current.get_children():
            bn = await child.read_browse_name()
            if bn.Name == name:
                found = child
                break
        if found is None:
            raise ValueError(f"在 {current.nodeid} 下找不到 BrowseName={name}")
        current = found
    return current


# ---------- 采集主流程 ----------

async def collect_snapshot(
    url: str,
    node_ids: list[str] = None,
    browse_roots: list[str] = None,
    browse_path: list[str] = None,
    max_depth: int = 10,
    timeout: float = 30.0,
    username: str = None,
    password: str = None,
) -> dict:
    """连接 UA 服务器，采集指定节点的快照。"""
    snapshot = {
        "server_url": url,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "nodes": [],
    }

    async with Client(url, timeout=timeout) as client:
        if username:
            await client.set_user(username)
        if password:
            await client.set_password(password)
        log.info("已连接: %s", url)

        # 按 node_id 直接采集
        if node_ids:
            for nid in node_ids:
                node = client.get_node(nid)
                log.info("采集节点: %s", nid)
                tree = await browse_subtree(node, max_depth=max_depth)
                snapshot["nodes"].append(tree)

        # 按 browse_root (NodeId) 采集，可选按 browse_path 进一步定位
        if browse_roots:
            for root_nid in browse_roots:
                root = client.get_node(root_nid)
                if browse_path:
                    log.info("从 %s 按路径 %s 定位...", root_nid, browse_path)
                    root = await resolve_browse_path(client, root, browse_path)
                    log.info("定位到: %s (BN=%s)", root.nodeid, (await root.read_browse_name()).Name)
                log.info("采集子树: %s", root.nodeid)
                tree = await browse_subtree(root, max_depth=max_depth)
                snapshot["nodes"].append(tree)

    return snapshot


# ---------- CLI ----------

def main():
    parser = argparse.ArgumentParser(description="OPC UA 数据采集客户端")
    parser.add_argument("--url", required=True, help="OPC UA 服务器地址, e.g. opc.tcp://host:4840")
    parser.add_argument("--node", action="append", default=[], help="要采集的 NodeId (可多次指定)")
    parser.add_argument("--browse-root", action="append", default=[], help="浏览根节点 NodeId (可多次指定)")
    parser.add_argument("--browse-path", help="从 browse-root 出发的 BrowseName 路径, 逗号分隔, e.g. Objects,DeviceSetView")
    parser.add_argument("--nodes-from", help="从文件读取 NodeId 列表 (每行一个)")
    parser.add_argument("--out", default="snapshot.json", help="输出 JSON 文件路径")
    parser.add_argument("--depth", type=int, default=10, help="递归浏览最大深度")
    parser.add_argument("--timeout", type=float, default=30.0, help="连接超时(秒)")
    parser.add_argument("--user", help="用户名")
    parser.add_argument("--password", help="密码")
    parser.add_argument("--config", help="从 JSON 配置文件读取参数")
    args = parser.parse_args()

    if args.config:
        cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
        args.url = cfg.get("url", args.url)
        args.node = cfg.get("nodes", args.node)
        args.browse_root = cfg.get("browse_roots", args.browse_root)
        args.browse_path = cfg.get("browse_path", args.browse_path)
        args.depth = cfg.get("depth", args.depth)
        args.out = cfg.get("output", args.out)
        args.timeout = cfg.get("timeout", args.timeout)
        args.user = cfg.get("user", args.user)
        args.password = cfg.get("password", args.password)

    if args.nodes_from:
        lines = Path(args.nodes_from).read_text(encoding="utf-8").splitlines()
        args.node.extend(line.strip() for line in lines if line.strip() and not line.startswith("#"))

    browse_path = None
    if args.browse_path:
        browse_path = [p.strip() for p in args.browse_path.split(",") if p.strip()]

    if not args.node and not args.browse_root:
        print("错误: 至少指定 --node / --browse-root / --nodes-from", file=sys.stderr)
        sys.exit(1)

    snapshot = asyncio.run(collect_snapshot(
        url=args.url,
        node_ids=args.node or None,
        browse_roots=args.browse_root or None,
        browse_path=browse_path,
        max_depth=args.depth,
        timeout=args.timeout,
        username=args.user,
        password=args.password,
    ))

    out_path = Path(args.out)
    out_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    log.info("快照已保存: %s (%d 个节点)", out_path, len(snapshot["nodes"]))


if __name__ == "__main__":
    main()
