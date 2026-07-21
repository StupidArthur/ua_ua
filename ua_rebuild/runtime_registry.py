"""RuntimeRegistry keeps handles to the live nodes that the simulator
needs to write.

The registry is built by the server once the address space is fully
populated; the server walks `BuildPlan.instance_nodes`, looks up the
real Node objects via the Server, and hands them to the registry.

We never derive NodeIds from SOV1 by string substitution: each device's
Current and ActionSnapshot NodeId is taken verbatim from the BuildPlan.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class DeviceRuntime:
    """One SOV device's runtime hooks."""

    name: str
    current_node: Any
    action_snapshot_node: Any
    online_state_node: Any | None
    fault_state_node: Any | None
    current_node_id: str
    action_snapshot_node_id: str
    initial_current: float


class RuntimeRegistry:
    """Build a name -> DeviceRuntime map from a BuildPlan."""

    def __init__(self) -> None:
        self.devices: dict[str, DeviceRuntime] = {}

    def add(self, device: DeviceRuntime) -> None:
        if device.name in self.devices:
            raise ValueError(f"duplicate runtime device: {device.name}")
        self.devices[device.name] = device

    def require_complete(self) -> None:
        expected = {f"SOV{i}" for i in range(1, 9)}
        actual = set(self.devices)

        missing = sorted(expected - actual)
        unexpected = sorted(actual - expected)

        if missing or unexpected:
            raise RuntimeError(
                f"runtime registry mismatch: missing={missing}, "
                f"unexpected={unexpected}"
            )

        for name, device in self.devices.items():
            if device.current_node is None:
                raise RuntimeError(f"{name}: Current node missing")
            if device.action_snapshot_node is None:
                raise RuntimeError(f"{name}: ActionSnapshot node missing")