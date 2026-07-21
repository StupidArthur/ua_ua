"""
OPC UA Server — 回放采集数据

用法:
    python ua_server.py
    python ua_server.py --port 4840 --snapshot snapshot.json

服务启动后会暴露与原服务器一致的节点结构 (DeviceSetView / SOV1~SOV8),
默认值来自 snapshot.json, 时间戳使用启动时间。
"""

import asyncio
import argparse
import base64
import json
import logging
import sys
from pathlib import Path
from datetime import datetime, timezone

from asyncua import Server, ua
from asyncua.ua import NodeId, NodeIdType, QualifiedName, LocalizedText
from asyncua.ua.uatypes import VariantType

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("ua_server")

# ---------- 值反序列化: JSON → UA Variant ----------

def json_to_variant(val, data_type: str, ts: datetime = None):
    """将 JSON 值转为 DataValue，可选带时间戳。"""
    if val is None:
        return None

    if data_type == "Boolean":
        variant = ua.Variant(bool(val), VariantType.Boolean)
    elif data_type in ("Int16", "Int32", "Int64"):
        variant = ua.Variant(int(val), getattr(VariantType, data_type))
    elif data_type in ("UInt16", "UInt32", "UInt64"):
        variant = ua.Variant(int(val), getattr(VariantType, data_type))
    elif data_type == "Float":
        variant = ua.Variant(float(val), VariantType.Float)
    elif data_type == "Double":
        variant = ua.Variant(float(val), VariantType.Double)
    elif data_type == "String":
        variant = ua.Variant(str(val), VariantType.String)
    elif data_type == "ByteString":
        if isinstance(val, dict) and val.get("__type__") == "ByteString":
            raw = base64.b64decode(val["b64"])
            variant = ua.Variant(raw, VariantType.ByteString)
        else:
            variant = ua.Variant(str(val).encode(), VariantType.ByteString)
    elif data_type == "ExtensionObject":
        ext = _json_to_extension_object(val)
        if ext:
            variant = ua.Variant(ext, VariantType.ExtensionObject)
        else:
            variant = ua.Variant(str(val), VariantType.String)
    else:
        variant = ua.Variant(str(val), VariantType.String)

    return ua.DataValue(variant, SourceTimestamp=ts, ServerTimestamp=ts)


def _json_to_extension_object(val: dict):
    """将 JSON 中的结构体转为 UA ExtensionObject。"""
    if not isinstance(val, dict):
        return None
    t = val.get("__type__")

    if t == "EnumValueType":
        obj = ua.EnumValueType()
        obj.Value = int(val.get("Value", 0))
        lt = val.get("DisplayName")
        if lt:
            obj.DisplayName = LocalizedText(Text=lt.get("Text", ""), Locale=lt.get("Locale", ""))
        lt2 = val.get("Description")
        if lt2:
            obj.Description = LocalizedText(Text=lt2.get("Text", ""), Locale=lt2.get("Locale", ""))
        return obj

    if t == "Range":
        obj = ua.Range()
        obj.Low = float(val.get("Low", 0))
        obj.High = float(val.get("High", 0))
        return obj

    return None


# ---------- NodeId 解析 ----------

def parse_node_id(raw: str) -> NodeId:
    """从 snapshot 中的 node_id 字符串解析出 NodeId。
    格式: NodeId(Identifier='xxx', NamespaceIndex=N, NodeIdType=<NodeIdType.String: 3>)
    """
    import re
    m_id = re.search(r"Identifier='([^']+)'", raw)
    m_ns = re.search(r"NamespaceIndex=(\d+)", raw)
    m_type = re.search(r"NodeIdType=<NodeIdType\.(\w+):", raw)

    identifier = m_id.group(1) if m_id else raw
    ns = int(m_ns.group(1)) if m_ns else 0
    id_type = m_type.group(1) if m_type else "String"

    if id_type == "String":
        return NodeId(identifier, ns, NodeIdType.String)
    elif id_type == "Numeric":
        return NodeId(int(identifier), ns, NodeIdType.Numeric)
    elif id_type == "FourByte":
        return NodeId(int(identifier), ns, NodeIdType.FourByte)
    else:
        return NodeId(identifier, ns, NodeIdType.String)


# ---------- 值更新接口 ----------

class ValueUpdater:
    """外部可通过此类更新节点值。"""
    def __init__(self, server: Server):
        self.server = server
        self._nodes: dict[str, any] = {}  # path -> Node

    def register(self, path: str, node):
        self._nodes[path] = node

    async def update(self, path: str, value, data_type: str):
        """按路径更新节点值。"""
        node = self._nodes.get(path)
        if not node:
            log.warning("未注册的节点路径: %s", path)
            return
        now = datetime.now(timezone.utc)
        dv = json_to_variant(value, data_type, ts=now)
        if dv:
            await node.write_value(dv)
            log.info("已更新 %s = %s", path, str(value)[:50])

    async def update_from_change(self, change: dict):
        """从录制的 change 记录更新值。"""
        path = change["path"]
        new_val = change["new_value"]
        data_type = change["data_type"]
        await self.update(path, new_val, data_type)

    @property
    def paths(self):
        return list(self._nodes.keys())


# ---------- 主流程 ----------

async def main(snapshot_path: str, port: int):
    # 加载快照
    snapshot = json.loads(Path(snapshot_path).read_text(encoding="utf-8"))
    log.info("加载快照: %s (%s)", snapshot_path, snapshot["server_url"])

    server = Server()
    await server.init()
    server.set_endpoint(f"opc.tcp://0.0.0.0:{port}")
    server.set_server_name("UA-Replay-Server")

    # 注册 namespace (与原始服务器保持一致的名称)
    # 原始服务器 ns=2 是 http://www.supcon.com/NeuroShellCMS 等
    # 我们只需要一个自定义 ns，用 ns=1
    ns_idx = await server.register_namespace("urn:ua-replay")
    log.info("注册 namespace: idx=%d", ns_idx)

    startup_ts = datetime.now(timezone.utc)
    log.info("启动时间戳: %s", startup_ts.isoformat())

    # 获取 Objects 节点
    objects = server.get_objects_node()

    # 从快照中提取 DeviceSetView
    root_data = snapshot["nodes"][0]  # DeviceSetView

    # 创建 DeviceSetView
    dsv_id = NodeId(root_data["node_id"].split("Identifier='")[1].split("'")[0], 1, NodeIdType.String)
    dsv_node = await objects.add_object(dsv_id, "DeviceSetView")
    log.info("创建 DeviceSetView")

    # 构建子设备树
    updater = ValueUpdater(server)

    for device_data in root_data.get("children", []):
        device_name = device_data["browse_name"]
        log.info("创建设备: %s", device_name)
        await _build_and_register(server, dsv_node, device_data, updater, startup_ts, device_name)

    log.info("节点总数: %d", len(updater.paths))
    log.info("启动服务器: opc.tcp://0.0.0.0:%d", port)

    async with server:
        log.info("服务器已启动，按 Ctrl+C 停止")
        # 保持运行
        try:
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass


async def _build_and_register(server, parent, node_data, updater: ValueUpdater, startup_ts, path_prefix):
    """构建节点并注册到 updater。"""
    node_id_str = node_data["node_id"]
    orig_id = parse_node_id(node_id_str)
    new_node_id = NodeId(orig_id.Identifier, 1, orig_id.NodeIdType)
    browse_name = node_data["browse_name"]
    display_name = node_data["display_name"]
    node_class = node_data["node_class"]

    qname = QualifiedName(browse_name, 1)
    dname = LocalizedText(Text=display_name, Locale="en-US")

    path = f"{path_prefix}/{browse_name}" if path_prefix else browse_name

    if node_class == "Object":
        obj = await parent.add_object(new_node_id, browse_name)
        for child in node_data.get("children", []):
            await _build_and_register(server, obj, child, updater, startup_ts, path)

    elif node_class == "Variable":
        data_type = node_data.get("data_type", "String")
        value = node_data.get("value")
        dv = json_to_variant(value, data_type, ts=startup_ts)
        if dv and dv.Value:
            var = await parent.add_variable(new_node_id, browse_name, dv.Value.Value, varianttype=dv.Value.VariantType)
            await var.write_value(dv)
        else:
            var = await parent.add_variable(new_node_id, browse_name, "", varianttype=VariantType.String)

        updater.register(path, var)

        for child in node_data.get("children", []):
            await _build_and_register(server, var, child, updater, startup_ts, path)


# ---------- CLI ----------

def main_cli():
    parser = argparse.ArgumentParser(description="OPC UA 回放服务器")
    parser.add_argument("--snapshot", default="snapshot.json", help="快照文件路径")
    parser.add_argument("--port", type=int, default=4840, help="监听端口")
    args = parser.parse_args()

    asyncio.run(main(args.snapshot, args.port))

if __name__ == "__main__":
    main_cli()
