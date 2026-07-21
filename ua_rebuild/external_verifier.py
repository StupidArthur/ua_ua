"""ExternalVerifier connects to a running Server with a brand-new asyncua
Client and reads every legal attribute of the verification targets.

Phase 1 only verifies the six smoke-test nodes.  Phase 2 verifies the
14 SOV1 subtree nodes.  Phase 3 verifies all 105 all-sov instances,
grouped by device.
"""

from __future__ import annotations

import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

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

METHOD_ATTR_IDS = [
    ua.AttributeIds.BrowseName,
    ua.AttributeIds.DisplayName,
    ua.AttributeIds.Description,
    ua.AttributeIds.WriteMask,
    ua.AttributeIds.UserWriteMask,
    ua.AttributeIds.Executable,
    ua.AttributeIds.UserExecutable,
    ua.AttributeIds.NodeId,
    ua.AttributeIds.NodeClass,
]


# Phase 1: hard-coded smoke set.
SMOKE_TARGETS: list[tuple[str, str, str]] = [
    ("DeviceSetView", "ns=2;s=P_7765a8f78a9266d7a83581ba1b39176a", "Object"),
    ("SOV1",          "ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch1", "Object"),
    ("AssetId",       "ns=4;s=P_318b26d74fcca15eeb08a56d2f1b6f3a", "Variable"),
    ("Runtime",       "ns=1;s=P_cadfd5973419d77015b9410f9ceda34e", "Object"),
    ("Current",       "ns=1;s=P_fb349055a732ddf6511d1367e07bf492", "Variable"),
    ("EURange",       "ns=0;s=P_d96e61438d6080321565c5718839603d", "Variable"),
]


# Phase 2: SOV1 subtree.
SOV1_TARGETS: list[tuple[str, str, str]] = [
    ("DeviceSetView", "ns=2;s=P_7765a8f78a9266d7a83581ba1b39176a", "Object"),
    ("SOV1",          "ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch1", "Object"),
    ("AssetId",       "ns=4;s=P_318b26d74fcca15eeb08a56d2f1b6f3a", "Variable"),
    ("DeviceClass",   "ns=1;s=P_10384fe20b16c81537f93e40558636e6", "Variable"),
    ("Configuration", "ns=1;s=P_0f82c9b911a44bc3a4185b1fe83be125", "Object"),
    ("SnapshotPeriod", "ns=1;s=P_c4e95c9b3819dd8bb1f24ca02b5127b6", "Variable"),
    ("CurrentType",   "ns=1;s=P_cdc75745a8441147e448e8f845243c64", "Variable"),
    ("Runtime",       "ns=1;s=P_cadfd5973419d77015b9410f9ceda34e", "Object"),
    ("FaultState",    "ns=1;s=P_79d0616e3e1a8613be1456bd90f5e544", "Variable"),
    ("TypeMismatch",  "ns=1;s=P_cb0a950cc7e57148a93bd1d6027a720c", "Variable"),
    ("Current",       "ns=1;s=P_fb349055a732ddf6511d1367e07bf492", "Variable"),
    ("EURange",       "ns=0;s=P_d96e61438d6080321565c5718839603d", "Variable"),
    ("ActionSnapshot", "ns=1;s=P_3c9fcf915366945544cd1b4032d0afe0", "Variable"),
    ("OnlineState",   "ns=1;s=P_0fd57de4b78346a354e7f8725d4cd95f", "Variable"),
]


def all_sov_targets_from_plan(plan) -> list[tuple[str, str, str]]:
    """Build the verification target list from the BuildPlan's instance_nodes.

    The Phase 3 scope (`all-sov`) already restricts the plan to the
    SOV subtree (plus DeviceSetView + Objects).  Using
    `plan.instance_nodes` avoids reading non-SOV variables (e.g.
    ServerDiagnostics) that are not in the address space.
    """
    out: list[tuple[str, str, str]] = []
    for spec in plan.instance_nodes:
        path = spec.path or spec.node_id.text
        out.append((path, spec.node_id.text, spec.node_class))
    return out


class ExternalVerifier:
    """Connect to a running Server and verify its address space.

    If ``targets`` is None, the default smoke set is used.
    """

    def __init__(self, url: str,
                 targets: Iterable[tuple[str, str, str]] | None = None) -> None:
        self.url = url
        self.targets = list(targets) if targets is not None else list(SMOKE_TARGETS)

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

            for label, text, expected_cls in self.targets:
                node = client.get_node(text)
                entry: dict[str, Any] = {
                    "label": label,
                    "node_id": text,
                    "expected_node_class": expected_cls,
                    "exists": True,
                    "node_class": None,
                    "browse_name": None,
                    "display_name": None,
                    "type_definition": None,
                    "parent_node_id": None,
                    "parent_ref_type_id": None,
                    "data_type": None,
                    "value_rank": None,
                    "value_decoded": None,
                    "attributes": [],
                    "attribute_status": {},
                }
                try:
                    nc = await node.read_node_class()
                    entry["node_class"] = nc.name
                except Exception as e:
                    entry["exists"] = False
                    entry["error"] = str(e)
                    summary["totals"]["missing"] += 1
                    summary["nodes"].append(entry)
                    continue

                try:
                    entry["browse_name"] = (await node.read_browse_name()).Name
                except Exception:
                    pass

                try:
                    entry["display_name"] = (await node.read_display_name()).Text
                except Exception:
                    pass

                try:
                    td = await node.read_type_definition()
                    entry["type_definition"] = str(td)
                except Exception:
                    pass

                # Parent + parent ref type (one of the incoming refs)
                try:
                    refs = await node.get_references()
                    for r in refs:
                        if not r.IsForward and r.NodeId != text:
                            entry["parent_node_id"] = str(r.NodeId)
                            rt_node = client.get_node(r.ReferenceTypeId)
                            entry["parent_ref_type_id"] = (await rt_node.read_browse_name()).Name
                            break
                except Exception:
                    pass

                attr_ids = (
                    VARIABLE_ATTR_IDS if nc == ua.NodeClass.Variable
                    else METHOD_ATTR_IDS if nc == ua.NodeClass.Method
                    else OBJECT_ATTR_IDS
                )
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
                        # Capture specific fields
                        if aid == ua.AttributeIds.DataType and dv.Value:
                            entry["data_type"] = str(dv.Value.Value)
                        elif aid == ua.AttributeIds.ValueRank and dv.Value:
                            entry["value_rank"] = int(dv.Value.Value)
                        elif aid == ua.AttributeIds.Value and dv.Value:
                            v = dv.Value.Value
                            entry["value_decoded"] = _describe_value(v)
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
        path.write_text(json.dumps(summary, ensure_ascii=False, indent=2,
                                  default=str),
                         encoding="utf-8")


def _describe_value(value: Any) -> dict[str, Any]:
    """Render a value in a JSON-safe way."""
    if value is None:
        return {"kind": "null"}
    cls = type(value).__name__
    if isinstance(value, (bool, int, float, str)):
        return {"kind": cls, "value": value}
    if isinstance(value, (bytes, bytearray)):
        import base64
        b = bytes(value)
        return {"kind": "bytes", "length": len(b),
                "base64": base64.b64encode(b).decode("ascii")}
    if cls == "Range":
        return {"kind": "Range", "Low": value.Low, "High": value.High}
    if cls == "EnumValueType":
        return {"kind": "EnumValueType",
                "Value": value.Value,
                "DisplayName": (value.DisplayName.Text if value.DisplayName else None),
                "Description": (value.Description.Text if value.Description else None)}
    if cls == "ExtensionObject":
        return {"kind": "ExtensionObject", "type_id": str(value.TypeId)}
    return {"kind": cls, "repr": str(value)[:80]}