"""ExternalVerifier connects to a running Server with a brand-new asyncua
Client and reads every legal attribute of the smoke-test nodes.

Phase 1 only verifies the four (or five, including Runtime) smoke-test
nodes that Phase 1 builds; the full Phase 2 verifier can extend this
to the complete SOV1 subtree.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from asyncua import Client, ua
from asyncua.ua.uatypes import NodeId


log = logging.getLogger("ua_rebuild.external_verifier")


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


# Smoke-test verification targets (NodeId text -> label).
VERIFICATION_TARGETS: list[tuple[str, str]] = [
    ("ns=2;s=P_7765a8f78a9266d7a83581ba1b39176a", "DeviceSetView"),
    ("ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch1", "SOV1"),
    ("ns=4;s=P_318b26d74fcca15eeb08a56d2f1b6f3a", "AssetId"),
    ("ns=1;s=P_cadfd5973419d77015b9410f9ceda34e", "Runtime"),
    ("ns=1;s=P_fb349055a732ddf6511d1367e07bf492", "Current"),
    ("ns=0;s=P_d96e61438d6080321565c5718839603d", "EURange"),
]


class ExternalVerifier:
    def __init__(self, url: str) -> None:
        self.url = url

    async def run(self) -> dict[str, Any]:
        summary: dict[str, Any] = {
            "url": self.url,
            "namespace_array": [],
            "nodes": [],
            "totals": {"good": 0, "bad": 0, "missing": 0},
        }

        async with Client(url=self.url) as client:
            ns_node = client.get_node(ua.NodeId(ua.ObjectIds.Server_NamespaceArray))
            ns_array = list(await ns_node.read_value())
            summary["namespace_array"] = ns_array

            for text, label in VERIFICATION_TARGETS:
                node = client.get_node(text)
                entry: dict[str, Any] = {
                    "label": label,
                    "node_id": text,
                    "exists": True,
                    "node_class": None,
                    "attributes": [],
                }
                try:
                    nc = await node.read_node_class()
                except Exception as e:
                    entry["exists"] = False
                    entry["error"] = str(e)
                    summary["totals"]["missing"] += 1
                    summary["nodes"].append(entry)
                    continue

                entry["node_class"] = nc.name
                attr_ids = (OBJECT_ATTR_IDS if nc == ua.NodeClass.Object
                            else VARIABLE_ATTR_IDS)
                for aid in attr_ids:
                    try:
                        dv = await node.read_attribute(aid)
                        sc = dv.StatusCode
                        if sc.is_bad():
                            entry["attributes"].append({
                                "attribute": aid.name,
                                "status": sc.name,
                            })
                            summary["totals"]["bad"] += 1
                        else:
                            entry["attributes"].append({
                                "attribute": aid.name,
                                "status": "Good",
                            })
                            summary["totals"]["good"] += 1
                    except Exception as e:
                        entry["attributes"].append({
                            "attribute": aid.name,
                            "status": "Exception",
                            "message": str(e),
                        })
                        summary["totals"]["bad"] += 1
                summary["nodes"].append(entry)

        log.info("[VERIFY] GOOD=%d BAD=%d MISSING=%d",
                 summary["totals"]["good"],
                 summary["totals"]["bad"],
                 summary["totals"]["missing"])
        return summary

    async def write_report(self, path: Path, summary: dict[str, Any]) -> None:
        path.write_text(json.dumps(summary, ensure_ascii=False, indent=2),
                         encoding="utf-8")