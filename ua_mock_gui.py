"""
OPC UA 电磁阀仿真服务器 (GUI)

基于录制数据分析归纳的物理规律，模拟 SOV1~SOV8 的电流行为:
- 关阀: Current = 0
- 开阀恢复: Current → 峰值 (227~236 mA)
- 缓慢下降: 单调下降，速率递减，趋向 ~215 mA
- ActionSnapshot: 恢复后 10 秒推送吸合波形
"""

import asyncio
import base64
import json
import logging
import math
import random
import struct
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QLabel, QLineEdit, QPushButton, QTextEdit, QSpinBox,
    QDoubleSpinBox, QStatusBar, QTableWidget, QTableWidgetItem,
    QHeaderView, QSplitter
)
from PyQt6.QtGui import QColor, QFont

from asyncua import Server, ua
from asyncua.ua import NodeId, NodeIdType

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("mock_server")

# ================================================================
# ActionSnapshot 波形模板 (来自录制数据的真实瞬态)
# ================================================================

_WAVEFORM_TRANSIENT = [
    0, 0, 1, 30, 95, 148, 179, 198, 209, 215, 218, 220, 220, 215, 200,
    173, 169, 183, 197, 208, 216, 222, 227, 229, 231, 233
]

def build_action_snapshot(peak_ma: float) -> bytes:
    """生成 ActionSnapshot 二进制数据。
    前 26 个样本: 瞬态波形 (缩放到 peak_ma)
    后 686 个样本: 填充 peak_ma
    """
    header = b'\x00' * 16
    scale = peak_ma / 235.0
    samples = []
    for v in _WAVEFORM_TRANSIENT:
        samples.append(max(0, min(65535, int(v * scale))))
    # 填充到 712 个样本
    while len(samples) < 712:
        samples.append(int(peak_ma))
    waveform = struct.pack(f'<{len(samples)}H', *samples)
    return header + waveform

# ================================================================
# 单设备仿真状态机
# ================================================================

class DeviceState:
    OFF = 0
    DECLINING = 1

class SimDevice:
    def __init__(self, name: str):
        self.name = name
        self.state = DeviceState.OFF
        self.current = 0.0
        self.peak = 0.0
        self.time_in_state = 0.0  # 当前状态持续时间 (秒)
        self.snapshot_pending = False
        self.snapshot_delay = 0.0
        self.snapshot_ready = False
        self.snapshot_peak = 0.0
        self.action_snapshot = b''  # 初始为空，恢复后才有值
        self.decline_rate = 0.0  # 当前下降速率 mA/s

    def start_on(self, schedule_snapshot: bool = True):
        """开阀。schedule_snapshot=False 用于初始化时不安排快照推送。"""
        self.state = DeviceState.DECLINING
        self.time_in_state = 0.0
        self.peak = random.uniform(227, 236)
        self.current = self.peak
        # 下降参数: 初始速率约 0.3 mA/s, 递减
        self.decline_rate = random.uniform(0.25, 0.4)
        # 10 秒后推送 ActionSnapshot (用恢复瞬间的峰值)
        self.snapshot_pending = schedule_snapshot
        self.snapshot_delay = 10.0
        self.snapshot_ready = False
        self.snapshot_peak = self.peak  # 记录峰值用于生成快照

    def start_off(self):
        """关阀"""
        self.state = DeviceState.OFF
        self.time_in_state = 0.0
        self.current = 0.0
        self.snapshot_pending = False
        self.snapshot_ready = False

    def tick(self, dt: float):
        """推进 dt 秒"""
        self.time_in_state += dt

        if self.state == DeviceState.OFF:
            self.current = 0.0
            return

        if self.state == DeviceState.DECLINING:
            # 单调下降，速率递减
            # 模型: dI/dt = -k * (I - I_min), 指数衰减趋向 I_min
            i_min = 215.0
            k = 0.015  # 衰减常数 (越大下降越快)
            di = -k * (self.current - i_min) * dt
            # 加噪声
            di += random.gauss(0, 0.15) * math.sqrt(dt)
            self.current = max(i_min - 5, self.current + di)
            self.current = round(self.current, 1)

            # ActionSnapshot 延迟推送
            if self.snapshot_pending:
                self.snapshot_delay -= dt
                if self.snapshot_delay <= 0:
                    self.snapshot_pending = False
                    self.action_snapshot = build_action_snapshot(self.snapshot_peak)
                    self.snapshot_ready = True

# ================================================================
# UA Server 后端
# ================================================================

class MockUAServer:
    def __init__(self, port: int, devices: list[SimDevice]):
        self.port = port
        self.devices = {d.name: d for d in devices}
        self.server = None
        self.var_current = {}
        self.var_snapshot = {}
        self.var_online = {}
        self._last_current = {}
        self._static_vars = []  # [(node, value, varianttype), ...] 静态变量初始值
        self.running = False
        self._loop = None
        self._thread = None

    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False

    def _run(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._serve())

    async def _serve(self):
        self.server = Server()
        await self.server.init()
        self.server.set_endpoint(f"opc.tcp://0.0.0.0:{self.port}")
        
        # 注册多个 namespace 以匹配真实服务器
        ns1 = 1  # 默认命名空间
        ns2 = await self.server.register_namespace("urn:mock:2")  # → ns=2
        ns3 = await self.server.register_namespace("urn:mock:3")  # → ns=3 (占位)
        ns4 = await self.server.register_namespace("urn:mock:4")  # → ns=4
        
        log.info("Namespace 注册完成: ns1=%d, ns2=%d, ns3=%d, ns4=%d", ns1, ns2, ns3, ns4)

        objects = self.server.get_objects_node()
        dsv = await self._add_obj(objects, ns2, "DeviceSetView", browse_name="DeviceSetView", locale="en-US")

        for dev in self.devices.values():
            await self._build_device(dsv, dev, ns1, ns2, ns4)

        self.running = True
        async with self.server:
            await self._write_initial_values()
            log.info("Mock UA Server started on port %d", self.port)
            while self.running:
                await self._update_values()
                await asyncio.sleep(1)

    async def _write_initial_values(self):
        """服务器启动后立即写入所有静态变量值，确保客户端订阅能收到。"""
        now = datetime.now(timezone.utc)
        tasks = []
        for node, value, vtype in self._static_vars:
            if vtype:
                variant = ua.Variant(value, vtype)
            else:
                variant = ua.Variant(value)
            dv = ua.DataValue(variant, SourceTimestamp=now, ServerTimestamp=now)
            tasks.append(node.write_value(dv))
        if tasks:
            await asyncio.gather(*tasks)
            log.info("已写入 %d 个静态变量初始值", len(tasks))

    def _dn(self, name: str, locale: str = "en-US") -> ua.LocalizedText:
        return ua.LocalizedText(Text=name, Locale=locale)

    async def _set_dn(self, node, name: str, locale: str = "en-US", desc_locale: str = None):
        """设置 DisplayName。Description 设为 None（与真实服务器一致）。"""
        await node.write_attribute(ua.AttributeIds.DisplayName, ua.DataValue(self._dn(name, locale)))
        # Description 始终为 None
        await node.write_attribute(ua.AttributeIds.Description, ua.DataValue(ua.LocalizedText(Text=None, Locale=desc_locale)))

    async def _add_var(self, parent, ns, name, initial, varianttype=None, static=True, browse_name=None, 
                       locale="en-US", desc_locale=None, access_level=1):
        """创建变量节点。access_level: 1=Read, 3=Read|Write, 5=Read|HistoryRead"""
        bn = browse_name or name
        node_id = ua.NodeId(name, ns)
        qname = ua.QualifiedName(bn, ns)
        if varianttype:
            n = await parent.add_variable(node_id, qname, initial, varianttype=varianttype)
        else:
            n = await parent.add_variable(node_id, qname, initial)
        # 设置 AccessLevel（替代 set_writable(False)）
        await n.write_attribute(ua.AttributeIds.AccessLevel, ua.DataValue(ua.Variant(access_level, ua.VariantType.Byte)))
        await n.write_attribute(ua.AttributeIds.UserAccessLevel, ua.DataValue(ua.Variant(access_level, ua.VariantType.Byte)))
        await self._set_dn(n, bn, locale=locale, desc_locale=desc_locale)
        if static:
            self._static_vars.append((n, initial, varianttype))
        return n

    async def _add_obj(self, parent, ns, name, browse_name=None, locale="en-US"):
        """创建对象节点。"""
        bn = browse_name or name
        node_id = ua.NodeId(name, ns)
        qname = ua.QualifiedName(bn, ns)
        n = await parent.add_object(node_id, qname, ua.ObjectIds.BaseObjectType)
        await self._set_dn(n, bn, locale=locale, desc_locale=None)  # Object 的 Description 为 None
        return n

    async def _build_device(self, parent, dev: SimDevice, ns1: int, ns2: int, ns4: int):
        # SOV 设备节点 (ns=1)
        dev_node = await self._add_obj(parent, ns1, dev.name, browse_name=dev.name, locale="en-US")

        # DeviceClass (ns=1, locale=en-US, access_level=5)
        await self._add_var(dev_node, ns1, f"{dev.name}.DeviceClass", "AirTac4V210-08", 
                          browse_name="DeviceClass", locale="en-US", desc_locale="en-US", access_level=5)

        # AssetId (ns=4, locale='', desc_locale=None, access_level=1, DisplayName=DeviceId)
        idx = dev.name.replace("SOV", "")
        asset_node = await self._add_var(dev_node, ns4, f"{dev.name}.AssetId", f"mock_{idx}", 
                                       browse_name="AssetId", locale="", desc_locale=None, access_level=1)
        # 覆盖 DisplayName 为 DeviceId
        await asset_node.write_attribute(ua.AttributeIds.DisplayName, 
                                       ua.DataValue(ua.LocalizedText(Text="DeviceId", Locale="")))
        
        # Configuration (ns=1, locale=en-US)
        cfg = await self._add_obj(dev_node, ns1, f"{dev.name}.Configuration", 
                                browse_name="Configuration", locale="en-US")

        # SnapshotPeriod (ns=1, locale=en-US, access_level=5)
        snap_period = ua.EnumValueType()
        snap_period.Value = 3
        snap_period.DisplayName = ua.LocalizedText(Text="SnapshotPeriodEnum", Locale="en-US")
        snap_period.Description = ua.LocalizedText(Text="2880ms", Locale="en-US")
        await self._add_var(cfg, ns1, f"{dev.name}.SnapshotPeriod", snap_period, 
                          ua.VariantType.ExtensionObject, browse_name="SnapshotPeriod",
                          locale="en-US", desc_locale="en-US", access_level=5)

        # CurrentType (ns=1, locale=en-US, access_level=5)
        current_type = ua.EnumValueType()
        current_type.Value = 0
        current_type.DisplayName = ua.LocalizedText(Text="CurrentTypeEnum", Locale="en-US")
        current_type.Description = ua.LocalizedText(Text="DC", Locale="en-US")
        await self._add_var(cfg, ns1, f"{dev.name}.CurrentType", current_type, 
                          ua.VariantType.ExtensionObject, browse_name="CurrentType",
                          locale="en-US", desc_locale="en-US", access_level=5)

        # Runtime (ns=1, locale=en-US)
        runtime = await self._add_obj(dev_node, ns1, f"{dev.name}.Runtime", 
                                    browse_name="Runtime", locale="en-US")

        # FaultState (ns=1, locale=en-US, access_level=1)
        fault = ua.EnumValueType()
        fault.Value = 0
        fault.DisplayName = ua.LocalizedText(Text="FaultState", Locale="en-US")
        fault.Description = ua.LocalizedText(Text="Normal", Locale="en-US")
        fault_node = await self._add_var(runtime, ns1, f"{dev.name}.FaultState", fault, 
                                       ua.VariantType.ExtensionObject, browse_name="FaultState",
                                       locale="en-US", desc_locale="en-US", access_level=1)

        # TypeMismatch (ns=1, locale=en-US, access_level=1)
        mismatch = ua.EnumValueType()
        mismatch.Value = 0
        mismatch.DisplayName = ua.LocalizedText(Text="Normal", Locale="en-US")
        mismatch.Description = ua.LocalizedText(Text="Normal", Locale="en-US")
        await self._add_var(fault_node, ns1, f"{dev.name}.TypeMismatch", mismatch, 
                          ua.VariantType.ExtensionObject, browse_name="TypeMismatch",
                          locale="en-US", desc_locale="en-US", access_level=1)

        # Current (ns=1, locale=en-US, access_level=1)
        current_node = await self._add_var(runtime, ns1, f"{dev.name}.Current", 0.0, 
                                         ua.VariantType.Float, browse_name="Current",
                                         locale="en-US", desc_locale="en-US", access_level=1)
        self.var_current[dev.name] = current_node

        # EURange (ns=0, locale='', desc_locale=None, access_level=3)
        eur = ua.Range()
        eur.Low = 0.0
        eur.High = 600.0
        await self._add_var(current_node, 0, f"{dev.name}.EURange", eur, 
                          ua.VariantType.ExtensionObject, browse_name="EURange",
                          locale="", desc_locale=None, access_level=3)

        # ActionSnapshot (ns=1, locale=en-US, access_level=1)
        v = await self._add_var(runtime, ns1, f"{dev.name}.ActionSnapshot", dev.action_snapshot, 
                              ua.VariantType.ByteString, static=False, browse_name="ActionSnapshot",
                              locale="en-US", desc_locale="en-US", access_level=1)
        self.var_snapshot[dev.name] = v

        # OnlineState (ns=1, locale=en-US, access_level=1)
        await self._add_var(runtime, ns1, f"{dev.name}.OnlineState", True, 
                          browse_name="OnlineState", locale="en-US", desc_locale="en-US", access_level=1)

    async def _update_values(self):
        """更新 Current 和 ActionSnapshot 值（操作 node 对象，不需要 namespace）。"""
        now = datetime.now(timezone.utc)
        tasks = []
        for name, dev in self.devices.items():
            # 只在 Current 值有变化时写入 (差值 > 0.05 mA)
            if name in self.var_current:
                last = self._last_current.get(name)
                if last is None or abs(dev.current - last) > 0.05:
                    dv = ua.DataValue(ua.Variant(dev.current, ua.VariantType.Float),
                                      SourceTimestamp=now, ServerTimestamp=now)
                    tasks.append(self.var_current[name].write_value(dv))
                    self._last_current[name] = dev.current

            # ActionSnapshot 只在 ready 时写入
            if name in self.var_snapshot and dev.snapshot_ready:
                dv = ua.DataValue(ua.Variant(dev.action_snapshot, ua.VariantType.ByteString),
                                  SourceTimestamp=now, ServerTimestamp=now)
                tasks.append(self.var_snapshot[name].write_value(dv))
                dev.snapshot_ready = False

        if tasks:
            await asyncio.gather(*tasks)

# ================================================================
# 仿真引擎 (后台线程)
# ================================================================

class SimEngine(QThread):
    log_signal = pyqtSignal(str)
    state_signal = pyqtSignal()

    def __init__(self, off_period: float, on_period: float, port: int):
        super().__init__()
        self.off_period = off_period
        self.on_period = on_period
        self.port = port
        self.running = False
        self.devices = [SimDevice(f"SOV{i}") for i in range(1, 9)]
        self.ua_server = None

    def run(self):
        self.running = True
        self.ua_server = MockUAServer(self.port, self.devices)
        self.ua_server.start()

        # 所有设备初始状态: 开阀，随机错开时间，不安排快照（初始无恢复事件）
        for i, dev in enumerate(self.devices):
            dev.start_on(schedule_snapshot=False)
            dev.time_in_state = random.uniform(0, self.on_period * 0.8)

        self.log_signal.emit(f"仿真启动: 关{self.off_period:.0f}s 开{self.on_period:.0f}s 端口{self.port}")

        while self.running:
            for dev in self.devices:
                if dev.state == DeviceState.OFF:
                    if dev.time_in_state >= self.off_period:
                        dev.start_on()
                        self.log_signal.emit(f"[{dev.name}] 开阀, 峰值 {dev.peak:.1f} mA")
                elif dev.state == DeviceState.DECLINING:
                    if dev.snapshot_ready:
                        self.log_signal.emit(f"[{dev.name}] ActionSnapshot 推送, Current={dev.current:.1f} mA")
                    if dev.current <= 215.5 or dev.time_in_state >= self.on_period:
                        self.log_signal.emit(
                            f"[{dev.name}] 关阀, Current={dev.current:.1f} mA, "
                            f"持续 {dev.time_in_state:.0f}s")
                        dev.start_off()

                dev.tick(1.0)  # 固定 1 秒步长

            self.state_signal.emit()
            time.sleep(1)

        if self.ua_server:
            self.ua_server.stop()
        self.log_signal.emit("仿真已停止")

    def stop(self):
        self.running = False

# ================================================================
# GUI 主窗口
# ================================================================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.engine = None
        self.setWindowTitle("电磁阀UA仿真工具")
        self.setMinimumSize(700, 550)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # --- 配置区 ---
        cfg_group = QGroupBox("仿真参数")
        cfg_layout = QHBoxLayout(cfg_group)

        cfg_layout.addWidget(QLabel("关阀周期 (秒):"))
        self.spin_off = QSpinBox()
        self.spin_off.setRange(5, 600)
        self.spin_off.setValue(10)
        cfg_layout.addWidget(self.spin_off)

        cfg_layout.addWidget(QLabel("开阀周期 (秒):"))
        self.spin_on = QSpinBox()
        self.spin_on.setRange(5, 600)
        self.spin_on.setValue(290)
        cfg_layout.addWidget(self.spin_on)

        cfg_layout.addWidget(QLabel("UA 端口:"))
        self.spin_port = QSpinBox()
        self.spin_port.setRange(1024, 65535)
        self.spin_port.setValue(18639)
        cfg_layout.addWidget(self.spin_port)

        cfg_layout.addWidget(QLabel("地址: 0.0.0.0 ns=1"))
        cfg_layout.addStretch()

        layout.addWidget(cfg_group)

        # --- 按钮区 ---
        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("启动仿真")
        self.btn_start.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 8px 24px; }")
        self.btn_start.clicked.connect(self._on_start)
        btn_layout.addWidget(self.btn_start)

        self.btn_stop = QPushButton("停止")
        self.btn_stop.setStyleSheet("QPushButton { background-color: #f44336; color: white; font-weight: bold; padding: 8px 24px; }")
        self.btn_stop.clicked.connect(self._on_stop)
        self.btn_stop.setEnabled(False)
        btn_layout.addWidget(self.btn_stop)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # --- 状态表格 + 日志 分割 ---
        splitter = QSplitter(Qt.Orientation.Vertical)

        # 设备状态表格
        self.table = QTableWidget(8, 4)
        self.table.setHorizontalHeaderLabels(["设备", "状态", "Current (mA)", "趋势"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        for i in range(8):
            self.table.setItem(i, 0, QTableWidgetItem(f"SOV{i+1}"))
        splitter.addWidget(self.table)

        # 日志
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setFont(QFont("Consolas", 9))
        splitter.addWidget(self.log_box)

        splitter.setSizes([200, 300])
        layout.addWidget(splitter)

        # --- 水印 ---
        watermark = QLabel("v0.03 designed by @yuzechao")
        watermark.setStyleSheet("color: #999999; font-size: 11px;")
        watermark.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(watermark)

        # --- 状态栏 ---
        self.statusBar().showMessage("就绪")

        # --- 刷新定时器 ---
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._refresh_table)

    def _on_start(self):
        off = self.spin_off.value()
        on = self.spin_on.value()
        port = self.spin_port.value()

        self.spin_off.setEnabled(False)
        self.spin_on.setEnabled(False)
        self.spin_port.setEnabled(False)
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)

        self.engine = SimEngine(off, on, port)
        self.engine.log_signal.connect(self._append_log)
        self.engine.state_signal.connect(self._refresh_table)
        self.engine.start()
        self.refresh_timer.start(500)
        self.statusBar().showMessage(f"运行中 | 0.0.0.0:{port} ns=1 | 关{off}s 开{on}s")

    def _on_stop(self):
        if self.engine:
            self.engine.stop()
            self.engine.wait(5000)
            self.engine = None
        self.refresh_timer.stop()
        self.spin_off.setEnabled(True)
        self.spin_on.setEnabled(True)
        self.spin_port.setEnabled(True)
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.statusBar().showMessage("已停止")

    def _append_log(self, msg: str):
        self.log_box.append(msg)

    def _refresh_table(self):
        if not self.engine:
            return
        for i, dev in enumerate(self.engine.devices):
            state_text = "关阀" if dev.state == DeviceState.OFF else "开阀"
            self.table.setItem(i, 1, QTableWidgetItem(state_text))
            self.table.setItem(i, 2, QTableWidgetItem(f"{dev.current:.1f}"))

            # 趋势指示
            if dev.state == DeviceState.OFF:
                trend = "—"
                color = QColor(150, 150, 150)
            elif dev.time_in_state < 2:
                trend = "↑ 峰值"
                color = QColor(76, 175, 80)
            else:
                trend = "↓ 下降"
                color = QColor(255, 152, 0)
            item = QTableWidgetItem(trend)
            item.setForeground(color)
            self.table.setItem(i, 3, item)

    def closeEvent(self, event):
        if self.engine:
            self.engine.stop()
            self.engine.wait(3000)
        event.accept()

# ================================================================

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
