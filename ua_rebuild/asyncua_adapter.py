"""Adapter isolating direct asyncua Server internals.

All access to `server.iserver`, `session.add_nodes`, `session.add_references`,
and the low-level AddNodes / AddReferences services must go through this
module.  Other rebuild modules are forbidden from reaching into the asyncua
Server object directly.
"""

from __future__ import annotations

from typing import Any

from asyncua import ua
from asyncua.ua.uatypes import NodeId


class AsyncuaAddressSpaceAdapter:
    """Thin wrapper around an asyncua Server for low-level address-space ops.

    Phase 0 keeps the adapter as a stub.  Phases 1+ populate concrete
    implementations of add_node_exact, add_reference_exact, write_value_exact
    using `server.iserver.isession.add_nodes` / `add_references` and the
    asyncua `ua.AddNodesItem` / `ua.AddReferencesItem` structures.
    """

    def __init__(self, server: Any) -> None:
        self.server = server

    async def node_exists(self, node_id: NodeId) -> bool:
        """Check whether a NodeId already exists in the address space."""
        try:
            node = self.server.get_node(node_id)
            await node.read_node_class()
            return True
        except Exception:
            return False

    async def read_node_class(self, node_id: NodeId):
        node = self.server.get_node(node_id)
        return await node.read_node_class()

    async def add_node_exact(self, *args: Any, **kwargs: Any) -> NodeId:
        """Add a node with full control over NodeId and references.

        Implementation deferred to Phase 1.
        """
        raise NotImplementedError("add_node_exact implemented in Phase 1+")

    async def add_reference_exact(self, *args: Any, **kwargs: Any) -> None:
        """Add an explicit reference between two existing nodes."""
        raise NotImplementedError("add_reference_exact implemented in Phase 1+")

    async def reference_exists(self, *args: Any, **kwargs: Any) -> bool:
        """Check whether a specific reference already exists."""
        raise NotImplementedError("reference_exists implemented in Phase 1+")

    async def write_value_exact(self, *args: Any, **kwargs: Any) -> None:
        """Write a value with explicit DataType / VariantType."""
        raise NotImplementedError("write_value_exact implemented in Phase 1+")