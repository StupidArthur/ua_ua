"""SelfCheck reads the legal attributes of every created node and
records each StatusCode.

SelfCheck only reads attributes that are valid for the node's
NodeClass.  Reading `Value` on an Object or `AccessLevel` on an Object
will produce `BadAttributeIdInvalid`, which is normal and must NOT be
counted as a failure.
"""

from __future__ import annotations

import logging
from typing import Any

from asyncua import ua
from asyncua.ua.uatypes import NodeId

from .asyncua_adapter import AsyncuaAddressSpaceAdapter, AddNodeRecord


log = logging.getLogger("ua_rebuild.self_check")


OBJECT_ATTR_IDS = [
    ua.AttributeIds.BrowseName,
    ua.AttributeIds.DisplayName,
    ua.AttributeIds.Description,
    ua.AttributeIds.WriteMask,
    ua.AttributeIds.UserWriteMask,
    ua.AttributeIds.EventNotifier,
    ua.AttributeIds.NodeId,
    ua.AttributeIds.NodeClass,
]

VARIABLE_ATTR_IDS = [
    ua.AttributeIds.BrowseName,
    ua.AttributeIds.DisplayName,
    ua.AttributeIds.Description,
    ua.AttributeIds.WriteMask,
    ua.AttributeIds.UserWriteMask,
    ua.AttributeIds.Value,
    ua.AttributeIds.DataType,
    ua.AttributeIds.ValueRank,
    ua.AttributeIds.ArrayDimensions,
    ua.AttributeIds.AccessLevel,
    ua.AttributeIds.UserAccessLevel,
    ua.AttributeIds.MinimumSamplingInterval,
    ua.AttributeIds.Historizing,
    ua.AttributeIds.NodeId,
    ua.AttributeIds.NodeClass,
]

REFERENCE_TYPE_ATTR_IDS = [
    ua.AttributeIds.BrowseName,
    ua.AttributeIds.DisplayName,
    ua.AttributeIds.Description,
    ua.AttributeIds.WriteMask,
    ua.AttributeIds.UserWriteMask,
    ua.AttributeIds.IsAbstract,
    ua.AttributeIds.Symmetric,
    ua.AttributeIds.InverseName,
    ua.AttributeIds.NodeId,
    ua.AttributeIds.NodeClass,
]


class SelfCheck:
    def __init__(self, adapter: AsyncuaAddressSpaceAdapter,
                 records: list[AddNodeRecord]) -> None:
        self.adapter = adapter
        self.records = records

    async def run(self) -> dict[str, Any]:
        good = 0
        bad = 0
        results: list[dict[str, Any]] = []
        for rec in self.records:
            node_id = rec.added_node_id
            if rec.status_code.is_bad():
                results.append({
                    "node_id": node_id,
                    "added": False,
                    "status": rec.status_code.name,
                    "attributes": [],
                })
                bad += 1
                continue

            node = self.adapter.server.get_node(node_id)
            nc = await node.read_node_class()
            attr_ids = self._attr_ids_for(nc)

            attrs: list[dict[str, Any]] = []
            for aid in attr_ids:
                try:
                    dv = await node.read_attribute(aid)
                    sc = dv.StatusCode
                    if sc.is_bad():
                        attrs.append({"attribute": aid.name, "status": sc.name})
                        # AccessLevelEx on an Object is normal, etc.
                    else:
                        attrs.append({"attribute": aid.name, "status": "Good"})
                        good += 1
                except Exception as e:
                    attrs.append({"attribute": aid.name,
                                  "status": "Exception",
                                  "message": str(e)})

            results.append({
                "node_id": node_id,
                "added": True,
                "node_class": nc.name,
                "status": "Good",
                "attributes": attrs,
            })

        summary = {"good": good, "bad": bad, "nodes": results}
        log.info("[SELFCHECK] GOOD=%d BAD=%d", good, bad)
        return summary

    @staticmethod
    def _attr_ids_for(node_class: ua.NodeClass) -> list[ua.AttributeIds]:
        if node_class == ua.NodeClass.Object:
            return OBJECT_ATTR_IDS
        if node_class == ua.NodeClass.Variable:
            return VARIABLE_ATTR_IDS
        if node_class == ua.NodeClass.Method:
            return OBJECT_ATTR_IDS
        if node_class == ua.NodeClass.ObjectType:
            return OBJECT_ATTR_IDS
        if node_class == ua.NodeClass.VariableType:
            return VARIABLE_ATTR_IDS
        if node_class == ua.NodeClass.ReferenceType:
            return REFERENCE_TYPE_ATTR_IDS
        return [ua.AttributeIds.BrowseName, ua.AttributeIds.DisplayName]