"""Adapter isolating direct asyncua Server internals.

All access to `server.iserver`, `server.iserver.isession.add_nodes`,
`server.iserver.isession.add_references` and the low-level AddNodes /
AddReferences services must go through this module.  Other rebuild
modules are forbidden from reaching into the asyncua Server object
directly so we can swap implementations or pin to a specific asyncua
version without touching the rest of the rebuild code.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Optional

from asyncua import ua
from asyncua.ua.uatypes import NodeId


log = logging.getLogger("ua_rebuild.asyncua_adapter")


@dataclass
class AddNodeRecord:
    """One node-creation record produced by `add_node_exact`."""
    requested_node_id: NodeId
    parent_node_id: NodeId
    reference_type_id: NodeId
    type_definition: NodeId
    node_class: ua.NodeClass
    browse_name: ua.QualifiedName
    added_node_id: NodeId
    status_code: ua.StatusCode


class AsyncuaAddressSpaceAdapter:
    """Thin wrapper around an asyncua Server for low-level address-space ops.

    Phase 1 implements only the operations actually used by the
    namespace-smoke builder; later phases can extend it with
    `add_reference_exact`, `reference_exists`, and
    `write_value_exact`.
    """

    def __init__(self, server: Any) -> None:
        self.server = server

    # ---------- read ----------

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

    # ---------- write (low-level) ----------

    async def add_node_exact(
        self,
        *,
        parent_node_id: NodeId,
        reference_type_id: NodeId,
        requested_new_node_id: NodeId,
        browse_name: ua.QualifiedName,
        node_class: ua.NodeClass,
        node_attributes: Any,
        type_definition: Optional[NodeId] = None,
    ) -> AddNodeRecord:
        """Add a single node via the low-level AddNodesItem service.

        Construction of AddNodesItem and invocation of
        `server.iserver.isession.add_nodes` are isolated here so other
        rebuild modules do not have to know how asyncua encodes the
        parameters.
        """
        item = ua.AddNodesItem()
        item.ParentNodeId = parent_node_id
        item.ReferenceTypeId = reference_type_id
        item.RequestedNewNodeId = requested_new_node_id
        item.BrowseName = browse_name
        item.NodeClass_ = node_class
        item.NodeAttributes = node_attributes
        item.TypeDefinition = type_definition if type_definition is not None else NodeId()

        log.info(
            "[ADAPTER] add_node_exact: requested=%s parent=%s refType=%s typeDef=%s cls=%s",
            requested_new_node_id,
            parent_node_id,
            reference_type_id,
            type_definition,
            node_class,
        )

        # NB: asyncua's `internal_session.add_nodes` accepts an
        # `AddNodesParameters` object but then passes it to the service
        # which iterates over `addnodeitems`.  Workaround: call the
        # service directly with the item list and a User with Admin role.
        from asyncua.server.internal_server import User, UserRole
        admin = User(role=UserRole.Admin)
        results = self.server.iserver.node_mgt_service.add_nodes([item], admin)
        result = results[0]

        record = AddNodeRecord(
            requested_node_id=requested_new_node_id,
            parent_node_id=parent_node_id,
            reference_type_id=reference_type_id,
            type_definition=type_definition if type_definition is not None else NodeId(),
            node_class=node_class,
            browse_name=browse_name,
            added_node_id=result.AddedNodeId,
            status_code=result.StatusCode,
        )

        log.info(
            "[ADAPTER] add_node_exact result: status=%s added=%s",
            result.StatusCode,
            result.AddedNodeId,
        )
        return record

    async def write_value_exact(self, *args: Any, **kwargs: Any) -> None:
        """Deferred to a later phase."""
        raise NotImplementedError("write_value_exact implemented in Phase 2+")

    async def add_reference_exact(self, *args: Any, **kwargs: Any) -> None:
        """Deferred to a later phase."""
        raise NotImplementedError("add_reference_exact implemented in Phase 2+")

    async def reference_exists(self, *args: Any, **kwargs: Any) -> bool:
        """Deferred to a later phase."""
        raise NotImplementedError("reference_exists implemented in Phase 2+")