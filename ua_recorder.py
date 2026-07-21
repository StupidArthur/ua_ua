"""
OPC UA 交互式录制工具

用法:
    python ua_recorder.py
    python ua_recorder.py --url opc.tcp://host:port --interval 5 --out recording.json

交互命令:
    SOV1              开始录制 SOV1 (可多个: SOV1 SOV3)
    stop SOV1         停止录制 SOV1
    stop all          停止所有录制
    list              查看当前录制状态
    devices           列出可用设备
    quit / exit       退出程序 (自动保存)

数据自动保存到 --out 指定的文件，默认 recording.json，每次变化实时写入。
"""

import asyncio
import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from asyncua import Client, Node, ua
from asyncua.ua.uatypes import VariantType

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("recorder")

# ---------- 值序列化 ----------

def serialize_value(val, vt: VariantType) -> object:
    if val is None:
        return None
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
        import base64
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
        return _serialize_ext(obj=val)
    if isinstance(val, (list, tuple)):
        return [serialize_value(item, vt) for item in val]
    return str(val)

def _serialize_ext(obj) -> dict | None:
    if obj is None:
        return None
    cls = obj.__class__.__name__
    if cls == "EnumValueType":
        return {"__type__": "EnumValueType", "Value": obj.Value,
                "DisplayName": serialize_value(obj.DisplayName, VariantType.LocalizedText) if obj.DisplayName else None,
                "Description": serialize_value(obj.Description, VariantType.LocalizedText) if obj.Description else None}
    if cls == "Range":
        return {"__type__": "Range", "Low": obj.Low, "High": obj.High}
    if hasattr(obj, "__ua_types__"):
        return {"__type__": cls, **{k: str(getattr(obj, k)) for k in obj.__ua_types__ if hasattr(obj, k)}}
    return {"__type__": cls, "raw": str(obj)}

def format_val_short(val) -> str:
    if val is None:
        return "null"
    if isinstance(val, dict):
        t = val.get("__type__", "")
        if t == "EnumValueType":
            desc = val.get("Description", {})
            return f"Enum({desc.get('Text', '?')})"
        if t == "Range":
            return f"Range({val.get('Low')}-{val.get('High')})"
        if t == "ByteString":
            return f"ByteString({len(val.get('b64', ''))}b64)"
        if t == "LocalizedText":
            return val.get("Text", str(val))
        return str(val)
    if isinstance(val, float):
        return f"{val:.2f}"
    return str(val)

# ---------- 节点发现 ----------

async def discover_device_nodes(client: Client, device_node: Node) -> list[dict]:
    nodes = []
    async def _walk(node: Node, prefix: str):
        nc = await node.read_node_class()
        bn = (await node.read_browse_name()).Name
        dn = (await node.read_display_name()).Text
        full_path = f"{prefix}/{bn}" if prefix else bn
        if nc == ua.NodeClass.Variable:
            try:
                dv = await node.read_data_value()
                vt = dv.Value.VariantType if dv.Value else None
                nodes.append({
                    "path": full_path,
                    "node": node,
                    "browse_name": bn,
                    "display_name": dn,
                    "data_type": vt.name if vt else "Unknown",
                    "last_value": serialize_value(dv.Value.Value, vt) if dv.Value else None,
                    "last_ts": (dv.ServerTimestamp or dv.SourceTimestamp).isoformat() if (dv.ServerTimestamp or dv.SourceTimestamp) else None,
                })
            except Exception as e:
                log.warning("读取 %s 失败: %s", full_path, e)
        try:
            for child in await node.get_children():
                await _walk(child, full_path)
        except Exception:
            pass
    await _walk(device_node, "")
    return nodes

# ---------- 录制器 ----------

class DeviceRecorder:
    def __init__(self, device_name: str, device_node: Node, client: Client, interval: float, on_change=None):
        self.device_name = device_name
        self.device_node = device_node
        self.client = client
        self.interval = interval
        self.nodes: list[dict] = []
        self.changes: list[dict] = []
        self.running = False
        self._task: asyncio.Task | None = None
        self._on_change = on_change  # 变化回调

    async def start(self):
        log.info("[%s] 正在发现节点...", self.device_name)
        self.nodes = await discover_device_nodes(self.client, self.device_node)
        log.info("[%s] 发现 %d 个 Variable 节点，开始每 %.0f 秒采集", self.device_name, len(self.nodes), self.interval)
        for n in self.nodes:
            log.info("  %-40s  %s = %s", n["path"], n["data_type"], format_val_short(n["last_value"]))
        self.running = True
        self._task = asyncio.create_task(self._poll_loop())

    async def stop(self):
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        log.info("[%s] 已停止录制，共记录 %d 次变化", self.device_name, len(self.changes))

    async def _poll_loop(self):
        while self.running:
            try:
                await asyncio.sleep(self.interval)
                await self._poll_once()
            except asyncio.CancelledError:
                break
            except Exception as e:
                log.error("[%s] 采集异常: %s", self.device_name, e)

    async def _poll_once(self):
        now = datetime.now(timezone.utc).isoformat()
        for n in self.nodes:
            try:
                dv = await n["node"].read_data_value()
                vt = dv.Value.VariantType if dv.Value else None
                new_val = serialize_value(dv.Value.Value, vt) if dv.Value else None
                ts = (dv.ServerTimestamp or dv.SourceTimestamp).isoformat() if (dv.ServerTimestamp or dv.SourceTimestamp) else now
            except Exception:
                continue

            if new_val != n["last_value"]:
                old_short = format_val_short(n["last_value"])
                new_short = format_val_short(new_val)
                log.info("[%s] %s  %s -> %s", self.device_name, n["path"], old_short, new_short)
                change = {
                    "timestamp": ts,
                    "path": n["path"],
                    "browse_name": n["browse_name"],
                    "display_name": n["display_name"],
                    "data_type": n["data_type"],
                    "old_value": n["last_value"],
                    "new_value": new_val,
                }
                self.changes.append(change)
                n["last_value"] = new_val
                n["last_ts"] = ts

                if self._on_change:
                    self._on_change()

    def summary(self) -> dict:
        return {
            "device": self.device_name,
            "node_count": len(self.nodes),
            "change_count": len(self.changes),
            "nodes": [{"path": n["path"], "browse_name": n["browse_name"], "data_type": n["data_type"]} for n in self.nodes],
            "changes": self.changes,
        }

# ---------- 主控制器 ----------

class RecorderApp:
    def __init__(self, url: str, interval: float, out_path: str):
        self.url = url
        self.interval = interval
        self.out_path = Path(out_path)
        self.client: Client | None = None
        self.recorders: dict[str, DeviceRecorder] = {}
        self.device_nodes: dict[str, Node] = {}
        self._started_at = datetime.now(timezone.utc).isoformat()

    async def _find_device_set_view(self) -> Node | None:
        """在 Objects 下查找 BrowseName 为 DeviceSetView 的节点。"""
        objects = self.client.get_objects_node()
        for child in await objects.get_children():
            bn = (await child.read_browse_name()).Name
            if bn == "DeviceSetView":
                return child
        return None

    async def run(self):
        self.client = Client(self.url, timeout=30)
        await self.client.connect()
        log.info("已连接: %s", self.url)

        dsv = await self._find_device_set_view()
        if not dsv:
            log.error("未找到 DeviceSetView 节点")
            return
        for child in await dsv.get_children():
            bn = (await child.read_browse_name()).Name
            self.device_nodes[bn] = child
        log.info("可用设备: %s", ", ".join(sorted(self.device_nodes.keys())))
        log.info("数据自动保存到: %s", self.out_path)
        print()
        self._print_help()

        loop = asyncio.get_event_loop()
        while True:
            try:
                line = await loop.run_in_executor(None, lambda: input("> ").strip())
            except (EOFError, KeyboardInterrupt):
                break
            if not line:
                continue
            await self._handle_cmd(line)

        for r in self.recorders.values():
            if r.running:
                await r.stop()
        self._flush()
        await self.client.disconnect()
        log.info("已断开连接，数据已保存到: %s", self.out_path)

    def _print_help(self):
        print("命令:")
        print("  SOV1              开始录制 SOV1 (可多个: SOV1 SOV3)")
        print("  stop SOV1         停止录制 SOV1")
        print("  stop all          停止所有录制")
        print("  list              查看当前录制状态")
        print("  devices           列出可用设备")
        print("  quit / exit       退出程序 (自动保存)")
        print()

    async def _handle_cmd(self, line: str):
        parts = line.split()
        cmd = parts[0].lower()

        if cmd in ("quit", "exit", "q"):
            for r in self.recorders.values():
                if r.running:
                    await r.stop()
            self._flush()
            await self.client.disconnect()
            log.info("已断开连接，数据已保存到: %s", self.out_path)
            sys.exit(0)

        elif cmd == "help":
            self._print_help()

        elif cmd == "devices":
            log.info("可用设备: %s", ", ".join(sorted(self.device_nodes.keys())))

        elif cmd == "list":
            if not self.recorders:
                log.info("当前无录制任务")
            for name, r in self.recorders.items():
                status = "录制中" if r.running else "已停止"
                log.info("  [%s] %s, %d 个节点, %d 次变化", name, status, len(r.nodes), len(r.changes))

        elif cmd == "stop":
            if len(parts) < 2:
                log.error("用法: stop <设备名> 或 stop all")
                return
            target = parts[1].lower()
            if target == "all":
                for name, r in list(self.recorders.items()):
                    if r.running:
                        await r.stop()
            elif target in self.recorders:
                await self.recorders[target].stop()
            else:
                log.error("未找到录制: %s", target)

        else:
            await self._start_devices(parts)

    async def _start_devices(self, names: list[str]):
        for name in names:
            uname = name.upper()
            matched = None
            for dn in self.device_nodes:
                if dn.upper() == uname:
                    matched = dn
                    break
            if not matched:
                log.error("未知设备: %s (输入 devices 查看可用列表)", name)
                continue
            if matched in self.recorders and self.recorders[matched].running:
                log.info("[%s] 已在录制中", matched)
                continue
            rec = DeviceRecorder(matched, self.device_nodes[matched], self.client, self.interval, on_change=self._flush)
            self.recorders[matched] = rec
            await rec.start()
            self._flush()  # 录制开始时先写一次（含初始值信息）

    def _flush(self):
        """将当前所有录制数据写入文件。"""
        data = {
            "server_url": self.url,
            "interval_seconds": self.interval,
            "started_at": self._started_at,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "devices": {name: r.summary() for name, r in self.recorders.items()},
        }
        self.out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

# ---------- CLI ----------

def main():
    parser = argparse.ArgumentParser(description="OPC UA 交互式录制工具")
    parser.add_argument("--url", default="opc.tcp://10.30.70.77:12345", help="OPC UA 服务器地址")
    parser.add_argument("--interval", type=float, default=5.0, help="采集间隔(秒)")
    parser.add_argument("--out", default="recording.json", help="自动保存的输出文件路径")
    args = parser.parse_args()

    app = RecorderApp(args.url, args.interval, args.out)
    asyncio.run(app.run())

if __name__ == "__main__":
    main()
