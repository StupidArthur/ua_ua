"""SovSimulator: dynamic Current + ActionSnapshot for the SOV1..SOV8
devices. Each tick writes a fresh DataValue with the current monotonic
timestamp; subscriptions see the change because asyncua dispatches
DataChange notifications when internal writes mutate a Variable's
Value attribute.
"""

from __future__ import annotations

import asyncio
import logging
import math
import random
import struct
import time
from dataclasses import dataclass
from datetime import datetime, timezone

from asyncua import ua

from .runtime_registry import RuntimeRegistry


log = logging.getLogger("ua_rebuild.simulator")


@dataclass(slots=True)
class SimulatorConfig:
    tick_ms: int = 250
    snapshot_interval_ms: int = 1000
    seed: int = 12345


class SovSimulator:
    def __init__(
        self,
        registry: RuntimeRegistry,
        config: SimulatorConfig,
        iserver,  # asyncua InternalServer; used for write_attribute_value
    ) -> None:
        self.registry = registry
        self.config = config
        self.iserver = iserver
        self._stop_event = asyncio.Event()
        self._random = random.Random(config.seed)
        self._start_monotonic = time.monotonic()
        self._last_snapshot: dict[str, float] = {}
        # previous Current value per device; used to detect zero <-> non-zero
        # transitions and only print the user-visible "开阀/关阀" event then.
        self._prev_open: dict[str, bool] = {}
        self._task: asyncio.Task | None = None

    def stop(self) -> None:
        self._stop_event.set()

    async def run(self) -> None:
        tick_seconds = max(self.config.tick_ms, 10) / 1000.0
        log.info("[SIM] start tick=%dms snapshot=%dms",
                 self.config.tick_ms, self.config.snapshot_interval_ms)
        while not self._stop_event.is_set():
            cycle_started = time.monotonic()
            try:
                await asyncio.gather(
                    *[
                        self._update_device(index, device)
                        for index, device in enumerate(
                            self.registry.devices.values(),
                            start=1,
                        )
                    ],
                    return_exceptions=True,
                )
            except Exception as e:
                log.exception("[SIM] cycle error: %s", e)

            elapsed = time.monotonic() - cycle_started
            sleep_seconds = max(0.0, tick_seconds - elapsed)
            try:
                await asyncio.wait_for(
                    self._stop_event.wait(),
                    timeout=sleep_seconds,
                )
            except asyncio.TimeoutError:
                pass
        log.info("[SIM] stopped")

    async def _update_device(self, index: int, device) -> None:
        now_monotonic = time.monotonic()
        elapsed = now_monotonic - self._start_monotonic

        phase = index * 0.67
        amplitude = 15.0 + index * 1.5
        period_seconds = 8.0 + index * 0.5
        noise = self._random.uniform(-0.8, 0.8)

        current = (
            device.initial_current
            + amplitude * math.sin((2.0 * math.pi * elapsed / period_seconds) + phase)
            + noise
        )
        current = max(0.0, min(600.0, current))

        timestamp = datetime.now(timezone.utc)

        current_value = ua.DataValue(
            Value=ua.Variant(float(current), ua.VariantType.Float),
            StatusCode_=ua.StatusCode(ua.StatusCodes.Good),
            SourceTimestamp=timestamp,
            ServerTimestamp=timestamp,
        )
        await self._safe_write(device.current_node, current_value, "Current")

        last_snapshot = self._last_snapshot.get(device.name, 0.0)
        snapshot_interval = self.config.snapshot_interval_ms / 1000.0
        if now_monotonic - last_snapshot >= snapshot_interval:
            payload = self._build_snapshot(
                device_index=index,
                current=current,
                timestamp=timestamp,
            )
            snapshot_value = ua.DataValue(
                Value=ua.Variant(payload, ua.VariantType.ByteString),
                StatusCode_=ua.StatusCode(ua.StatusCodes.Good),
                SourceTimestamp=timestamp,
                ServerTimestamp=timestamp,
            )
            await self._safe_write(
                device.action_snapshot_node, snapshot_value, "ActionSnapshot"
            )
            self._last_snapshot[device.name] = now_monotonic
            # Only print on zero <-> non-zero transitions, i.e. valve
            # open/close events, to keep the operator console quiet.
            is_open = current > 0.0
            prev = self._prev_open.get(device.name)
            if prev is None or prev != is_open:
                self._prev_open[device.name] = is_open
                if is_open:
                    msg = "开阀生成快照"
                else:
                    msg = "关阀生成快照"
                print(
                    f"{msg} device={device.name} current={current:.1f}",
                    flush=True,
                )

    async def _safe_write(self, node, datavalue, label: str) -> None:
        """Write via the internal Server (bypasses AccessLevel checks).

        Falls back to `node.write_value` if the internal path is
        unavailable for any reason.
        """
        try:
            nodeid = node.nodeid
            await self.iserver.write_attribute_value(
                nodeid, datavalue, ua.AttributeIds.Value,
            )
        except Exception as e:
            log.warning("[SIM] internal write failed for %s: %s — falling back",
                        label, e)
            try:
                await node.write_value(datavalue)
            except Exception as e2:
                log.error("[SIM] fallback write failed for %s: %s",
                          label, e2)

    @staticmethod
    def _build_snapshot(
        device_index: int,
        current: float,
        timestamp: datetime,
    ) -> bytes:
        timestamp_us = int(timestamp.timestamp() * 1_000_000)
        header = struct.pack(
            "<4sB3xQf",
            b"SOV1",       # signature
            device_index,  # device index (1..8)
            timestamp_us,  # µs unix timestamp
            float(current),
        )
        target_length = 1440
        if len(header) > target_length:
            raise RuntimeError("snapshot header exceeds target length")
        return header + bytes(target_length - len(header))

    def start(self) -> None:
        self._task = asyncio.create_task(self.run())

    async def wait(self, timeout: float = 5.0) -> None:
        if self._task is not None:
            try:
                await asyncio.wait_for(self._task, timeout=timeout)
            except asyncio.TimeoutError:
                self._task.cancel()
                try:
                    await self._task
                except (asyncio.CancelledError, Exception):
                    pass