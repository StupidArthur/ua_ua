"""RuntimeRegistry + Simulator placeholders for Phase 0.

The simulator only comes online in Phase 4.  The registry tracks Node
objects so dynamic updates don't have to re-resolve NodeIds.
"""

from __future__ import annotations

from typing import Any


class RuntimeRegistry:
    def __init__(self) -> None:
        self.node_by_id: dict[str, Any] = {}
        self.node_by_path: dict[str, Any] = {}
        self.current_nodes: dict[str, Any] = {}
        self.snapshot_nodes: dict[str, Any] = {}
        self.online_nodes: dict[str, Any] = {}

    def register(self, node_id_text: str, node: Any, path: str | None = None,
                 role: str | None = None) -> None:
        self.node_by_id[node_id_text] = node
        if path is not None:
            self.node_by_path[path] = node
        if role == "current":
            self.current_nodes[node_id_text] = node
        elif role == "snapshot":
            self.snapshot_nodes[node_id_text] = node
        elif role == "online":
            self.online_nodes[node_id_text] = node


class Simulator:
    def __init__(self, registry: RuntimeRegistry) -> None:
        self.registry = registry
        self._task = None

    async def start(self) -> None:
        raise NotImplementedError("Simulator implemented in Phase 4")

    async def stop(self) -> None:
        raise NotImplementedError("Simulator implemented in Phase 4")