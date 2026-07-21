"""Minimal InstanceBuilder for Phase 1 namespace-smoke scope.

Phase 1 deliberately avoids the full type closure and only creates the
six smoke-test nodes with simplified TypeDefinitions:

    Objects (reused)
    └── DeviceSetView    (Object)    FolderType
        └── SOV1         (Object)    BaseObjectType
            ├── AssetId  (Variable)  PropertyType
            └── Runtime (Object)    BaseObjectType
                └── Current (Variable) AnalogItemType
                    └── EURange (Variable) PropertyType

NodeIds, BrowseNames, DisplayNames and Variable Values are taken
verbatim from `real_server_export_v2.json`.  TypeDefinitions are
**simplified** to standard ns=0 types per the Phase 1 spec.
"""

from __future__ import annotations

import logging
from typing import Any

from asyncua import ua
from asyncua.ua.uatypes import NodeId

from .asyncua_adapter import AsyncuaAddressSpaceAdapter, AddNodeRecord
from .model_loader import load_export, _infer_id_fields_from_text


log = logging.getLogger("ua_rebuild.instance_builder")


def _qualified_name(name: str, namespace_index: int) -> ua.QualifiedName:
    return ua.QualifiedName(name, namespace_index)


def _localized_text(text: str | None, locale: str | None) -> ua.LocalizedText:
    return ua.LocalizedText(Text=text or "", Locale=locale or "")


# Hand-curated Phase 1 node specs.  Each entry mirrors a record in
# `real_server_export_v2.json` but uses a SIMPLIFIED TypeDefinition.
# Order matters: it is the topological creation order.
PHASE1_NODE_SPECS: list[dict[str, Any]] = [
    {
        "key": "DeviceSetView",
        "node_id_text": "ns=2;s=P_7765a8f78a9266d7a83581ba1b39176a",
        "parent_text": "i=85",                      # Objects
        "reference_type_id": 47,                    # HasComponent
        "type_definition_text": "i=61",              # FolderType
        "node_class": ua.NodeClass.Object,
        "browse_name": ("DeviceSetView", 2),
        "display_name": ("DeviceSetView", "en-US"),
        "description": ("", ""),
        "event_notifier": 1,
        "write_mask": 0,
        "user_write_mask": 0,
    },
    {
        "key": "SOV1",
        "node_id_text": "ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch1",
        "parent_text": "ns=2;s=P_7765a8f78a9266d7a83581ba1b39176a",
        "reference_type_id": 47,                    # HasComponent
        "type_definition_text": "i=58",              # BaseObjectType
        "node_class": ua.NodeClass.Object,
        "browse_name": ("SOV1", 1),
        "display_name": ("SOV1", "en-US"),
        "description": ("", "en-US"),
        "event_notifier": 1,
        "write_mask": 0,
        "user_write_mask": 0,
    },
    {
        "key": "AssetId",
        "node_id_text": "ns=4;s=P_318b26d74fcca15eeb08a56d2f1b6f3a",
        "parent_text": "ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch1",
        "reference_type_id": 46,                    # HasProperty
        "type_definition_text": "i=68",              # PropertyType
        "node_class": ua.NodeClass.Variable,
        "browse_name": ("AssetId", 4),
        "display_name": ("DeviceId", ""),
        "description": ("", ""),
        "value": "7c8af738ba72d0e9226c57c70ab0310d_ch1",
        "data_type_text": "i=12",                    # String
        "value_rank": -2,
        "array_dimensions": [],
        "access_level": 1,
        "user_access_level": 1,
        "minimum_sampling_interval": 0.0,
        "historizing": False,
        "write_mask": 0,
        "user_write_mask": 0,
    },
    {
        "key": "Runtime",
        "node_id_text": "ns=1;s=P_cadfd5973419d77015b9410f9ceda34e",
        "parent_text": "ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch1",
        "reference_type_id": 47,                    # HasComponent
        "type_definition_text": "i=58",              # BaseObjectType
        "node_class": ua.NodeClass.Object,
        "browse_name": ("Runtime", 1),
        "display_name": ("Runtime", "en-US"),
        "description": ("", ""),
        "event_notifier": 1,
        "write_mask": 0,
        "user_write_mask": 0,
    },
    {
        "key": "Current",
        "node_id_text": "ns=1;s=P_fb349055a732ddf6511d1367e07bf492",
        "parent_text": "ns=1;s=P_cadfd5973419d77015b9410f9ceda34e",
        "reference_type_id": 47,                    # HasComponent
        "type_definition_text": "i=2368",            # AnalogItemType
        "node_class": ua.NodeClass.Variable,
        "browse_name": ("Current", 1),
        "display_name": ("Current", "en-US"),
        "description": ("", "en-US"),
        "value": 0.0,                                # overwritten from export below
        "data_type_text": "i=10",                    # Float
        "value_rank": -1,
        "array_dimensions": [],
        "access_level": 1,
        "user_access_level": 1,
        "minimum_sampling_interval": 0.0,
        "historizing": False,
        "write_mask": 0,
        "user_write_mask": 0,
    },
    {
        "key": "EURange",
        "node_id_text": "ns=0;s=P_d96e61438d6080321565c5718839603d",
        "parent_text": "ns=1;s=P_fb349055a732ddf6511d1367e07bf492",
        "reference_type_id": 46,                    # HasProperty
        "type_definition_text": "i=68",              # PropertyType
        "node_class": ua.NodeClass.Variable,
        "browse_name": ("EURange", 0),
        "display_name": ("EURange", ""),
        "description": ("", ""),
        # Range is set via the post-create write step because asyncua's
        # AddNodesItem Value field expects a Variant, and Range must be
        # encoded as an ExtensionObject Variant.
        "value": None,
        "data_type_text": "i=884",                   # Range
        "value_rank": -2,
        "array_dimensions": [],
        "access_level": 3,
        "user_access_level": 3,
        "minimum_sampling_interval": 0.0,
        "historizing": False,
        "write_mask": 0,
        "user_write_mask": 0,
    },
]


def _decode_node_id(text: str) -> NodeId:
    """Decode a NodeId text in any of the exporter forms."""
    id_type, ident = _infer_id_fields_from_text(text)
    if text.startswith("ns="):
        _, _, rest = text.partition(";")
        try:
            ns = int(text.split(";", 1)[0].split("=", 1)[1])
        except Exception:
            ns = 0
    elif text.startswith("i="):
        ns = 0
    else:
        ns = 0
    if id_type == "Numeric" or id_type == "FourByte" or id_type == "TwoByte":
        return NodeId(int(ident), ns)
    if id_type == "String":
        return NodeId(str(ident), ns)
    if id_type == "Guid":
        return NodeId(ident, ns)
    if id_type == "ByteString":
        return NodeId(ident, ns)
    return NodeId(int(ident), ns)


def _make_object_attributes(spec: dict[str, Any]) -> ua.ObjectAttributes:
    attrs = ua.ObjectAttributes()
    attrs.DisplayName = _localized_text(spec["display_name"][0], spec["display_name"][1])
    attrs.Description = _localized_text(spec["description"][0], spec["description"][1])
    attrs.WriteMask = spec.get("write_mask", 0)
    attrs.UserWriteMask = spec.get("user_write_mask", 0)
    attrs.EventNotifier = spec.get("event_notifier", 0)
    attrs.SpecifiedAttributes = (
        ua.NodeAttributesMask.DisplayName
        | ua.NodeAttributesMask.Description
        | ua.NodeAttributesMask.WriteMask
        | ua.NodeAttributesMask.UserWriteMask
        | ua.NodeAttributesMask.EventNotifier
    )
    return attrs


def _make_variable_attributes(spec: dict[str, Any], model) -> ua.VariableAttributes:
    """Build VariableAttributes; for Variable nodes whose `value` field
    should come from the export we substitute the real value here."""
    attrs = ua.VariableAttributes()
    attrs.DisplayName = _localized_text(spec["display_name"][0], spec["display_name"][1])
    attrs.Description = _localized_text(spec["description"][0], spec["description"][1])
    attrs.WriteMask = spec.get("write_mask", 0)
    attrs.UserWriteMask = spec.get("user_write_mask", 0)

    # DataType NodeId
    dt_nid = _decode_node_id(spec["data_type_text"])

    # Value
    val = spec.get("value", None)
    raw_export_node = None
    if spec["key"] == "Current":
        raw_export_node = model.get_node(spec["node_id_text"])
    elif spec["key"] == "EURange":
        raw_export_node = model.get_node(spec["node_id_text"])
    elif spec["key"] == "AssetId":
        raw_export_node = model.get_node(spec["node_id_text"])

    if raw_export_node is not None:
        raw_value = (raw_export_node.get("attributes") or {}).get("value", {})
        v = raw_value.get("value") if isinstance(raw_value, dict) else None
        if v is not None:
            val = v

    if val is not None:
        attrs.Value = _variant_for(val, dt_nid)

    attrs.DataType = dt_nid
    attrs.ValueRank = spec.get("value_rank", -1)
    attrs.ArrayDimensions = spec.get("array_dimensions", [])
    attrs.AccessLevel = _u8(spec.get("access_level", 1))
    attrs.UserAccessLevel = _u8(spec.get("user_access_level", 1))
    attrs.MinimumSamplingInterval = spec.get("minimum_sampling_interval", 0.0)
    attrs.Historizing = spec.get("historizing", False)

    attrs.SpecifiedAttributes = (
        ua.NodeAttributesMask.DisplayName
        | ua.NodeAttributesMask.Description
        | ua.NodeAttributesMask.WriteMask
        | ua.NodeAttributesMask.UserWriteMask
        | ua.NodeAttributesMask.Value
        | ua.NodeAttributesMask.DataType
        | ua.NodeAttributesMask.ValueRank
        | ua.NodeAttributesMask.ArrayDimensions
        | ua.NodeAttributesMask.AccessLevel
        | ua.NodeAttributesMask.UserAccessLevel
        | ua.NodeAttributesMask.MinimumSamplingInterval
        | ua.NodeAttributesMask.Historizing
    )
    return attrs


def _u8(value: int) -> ua.Byte:
    return ua.Byte(value & 0xFF)


def _variant_for(value: Any, dt_nid: NodeId) -> ua.Variant:
    """Construct a Variant whose VariantType matches the DataType NodeId.

    Mirrors the rules in `value_codec.decode_exported_value` but stays
    narrow: we only need Float / Boolean / String / Range / null for the
    smoke scope.
    """
    if value is None:
        return ua.Variant(None)
    oid = dt_nid.Identifier
    if isinstance(oid, int) and oid == 884:  # Range
        obj = ua.Range()
        if isinstance(value, dict):
            obj.Low = float(value.get("fields", {}).get("Low", 0.0))
            obj.High = float(value.get("fields", {}).get("High", 0.0))
        return ua.Variant(obj, ua.VariantType.ExtensionObject)
    if isinstance(oid, int) and oid == 12:  # String
        return ua.Variant(str(value), ua.VariantType.String)
    if isinstance(oid, int) and oid == 10:  # Float
        return ua.Variant(float(value), ua.VariantType.Float)
    if isinstance(oid, int) and oid == 11:  # Double
        return ua.Variant(float(value), ua.VariantType.Double)
    if isinstance(oid, int) and oid == 1:   # Boolean
        return ua.Variant(bool(value), ua.VariantType.Boolean)
    if isinstance(oid, int) and oid == 6:   # Int32
        return ua.Variant(int(value), ua.VariantType.Int32)
    # Fallback: best effort.
    return ua.Variant(value)


class InstanceBuilder:
    """Builds the six Phase 1 smoke nodes via the AsyncuaAddressSpaceAdapter."""

    def __init__(self, adapter: AsyncuaAddressSpaceAdapter, model_path: str) -> None:
        self.adapter = adapter
        self.model = load_export(model_path)
        self.records: list[AddNodeRecord] = []

    async def build(self) -> list[AddNodeRecord]:
        for spec in PHASE1_NODE_SPECS:
            node_id = _decode_node_id(spec["node_id_text"])
            parent_id = _decode_node_id(spec["parent_text"])
            td_id = _decode_node_id(spec["type_definition_text"])
            ref_id = NodeId(spec["reference_type_id"], 0)
            bn = ua.QualifiedName(*spec["browse_name"])

            if spec["node_class"] == ua.NodeClass.Object:
                attrs = _make_object_attributes(spec)
            else:
                attrs = _make_variable_attributes(spec, self.model)

            record = await self.adapter.add_node_exact(
                parent_node_id=parent_id,
                reference_type_id=ref_id,
                requested_new_node_id=node_id,
                browse_name=bn,
                node_class=spec["node_class"],
                node_attributes=attrs,
                type_definition=td_id,
            )
            self.records.append(record)

            if record.status_code.is_bad():
                log.error(
                    "[BUILD] FAIL key=%s requested=%s added=%s status=%s",
                    spec["key"], record.requested_node_id,
                    record.added_node_id, record.status_code,
                )
            else:
                log.info(
                    "[BUILD] OK   key=%s nodeId=%s td=%s refType=%s",
                    spec["key"], record.added_node_id,
                    td_id, ref_id,
                )
        return self.records