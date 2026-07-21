"""ReferenceBuilder: add non-implied references via the AddReferences service.

AddNodes already creates:

    * the parent -> child hierarchical reference
    * the child -> parent inverse reference
    * HasTypeDefinition (when item.TypeDefinition is set)

So Phase 2 only needs to add references NOT implied by AddNodes.  The
BuildPlanner splits these into `references_to_add` (call AddReferences)
and `expected_existing_references` (already present in the standard
address space or implied by AddNodes).

Before adding a reference we verify both endpoints exist and that the
reference is not already present.
"""

from __future__ import annotations

import logging
from typing import Any

from asyncua import ua
from asyncua.ua.uatypes import NodeId

from .asyncua_adapter import AsyncuaAddressSpaceAdapter
from .build_planner import BuildPlan


log = logging.getLogger("ua_rebuild.reference_builder")


def _decode_node_id(text: str) -> NodeId:
    from .type_builder import _decode as td_decode
    return td_decode(text)


def _admin_user():
    from asyncua.server.internal_server import User, UserRole
    return User(role=UserRole.Admin)


class ReferenceBuilder:
    def __init__(self, adapter: AsyncuaAddressSpaceAdapter, plan: BuildPlan) -> None:
        self.adapter = adapter
        self.plan = plan

    async def build(self) -> list:
        results = []
        for ref in self.plan.references_to_add:
            src = _decode_node_id(ref.source_node_id)
            tgt = _decode_node_id(ref.target_node_id)
            rt_id = ua.NodeId(ref.reference_type_id, 0)

            if not await self.adapter.node_exists(src):
                log.error("[REF] skip missing source %s -> %s", src, tgt)
                continue
            if not await self.adapter.node_exists(tgt):
                log.error("[REF] skip missing target %s -> %s", src, tgt)
                continue
            if await self._reference_exists(src, rt_id, ref.is_forward, tgt):
                log.info("[REF] SKIP existing %s --[%s]--> %s",
                         src, ref.reference_type_browse_name, tgt)
                continue

            item = ua.AddReferencesItem()
            item.SourceNodeId = src
            item.ReferenceTypeId = rt_id
            item.IsForward = bool(ref.is_forward)
            item.TargetNodeId = tgt
            item.TargetNodeClass = ua.NodeClass.Unspecified

            result_list = self.adapter.server.iserver.node_mgt_service.add_references(
                [item], _admin_user())
            result = result_list[0] if result_list else None
            if result is not None and result.is_good():
                log.info("[REF] ADD %s --[%s:%s]--> %s",
                         src, ref.reference_type_browse_name,
                         "F" if ref.is_forward else "R", tgt)
                results.append({"source": ref.source_node_id,
                                 "type": ref.reference_type_browse_name,
                                 "is_forward": ref.is_forward,
                                 "target": ref.target_node_id,
                                 "status": "Good"})
            else:
                log.error("[REF] FAIL %s --[%s]--> %s status=%s",
                          src, ref.reference_type_browse_name, tgt,
                          result)
                results.append({"source": ref.source_node_id,
                                 "type": ref.reference_type_browse_name,
                                 "is_forward": ref.is_forward,
                                 "target": ref.target_node_id,
                                 "status": str(result)})
        return results

    async def _reference_exists(self, source: NodeId, ref_type: NodeId,
                               is_forward: bool, target: NodeId) -> bool:
        """Check whether a reference already exists in the address space."""
        try:
            refs = await self.adapter.server.iserver.isession.read_references(
                source, ref_type, 0, 0
            )
        except Exception:
            return False
        for r in (refs or []):
            if bool(r.IsForward) == bool(is_forward) and r.NodeId == target:
                return True
        return False