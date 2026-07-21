"""Decode the exporter's structured `value` dicts into asyncua Variants.

The exporter writes:

    Boolean -> bool
    SByte/Int16/Int32/Int64 -> int
    Byte/UInt16/UInt32/UInt64 -> int
    Float / Double -> float
    String / XmlElement -> str
    DateTime -> ISO 8601 string
    Guid -> str
    ByteString -> {"__type__": "ByteString", "base64": "...", "length": N}
    LocalizedText -> {"__type__": "LocalizedText", "text": ..., "locale": ...}
    QualifiedName -> {"__type__": "QualifiedName", "name": ..., "namespace_index": N}
    NodeId -> {"__type__": "NodeId", "node_id": {...}}
    StatusCode -> {"__type__": "StatusCode", "name": ..., "value": N}
    ExtensionObject decoded -> {"__type__": "ClassName", "encoding_id": ..., "fields": {...}}
    ExtensionObject raw -> {"__type__": "ExtensionObject", "type_id": ..., "encoding": ..., "body_base64": ...}
    Array -> {"__type__": "Array", "element_variant_type": ..., "length": N, "items": [...]}

The VariantType is decided by `data_type_node_id` (the Variable's DataType),
NOT by the Python type of the value.  This keeps e.g. `Current` (DataType=Float)
distinct from a Double even though both arrive as Python float.
"""

from __future__ import annotations

import base64
import datetime as _dt
from typing import Any

from asyncua import ua


_FLOAT_NODE_IDS = {ua.ObjectIds.Float, ua.ObjectIds.Double}
_INT_NODE_IDS = {
    ua.ObjectIds.Boolean,
    ua.ObjectIds.SByte, ua.ObjectIds.Int16, ua.ObjectIds.Int32, ua.ObjectIds.Int64,
    ua.ObjectIds.Byte, ua.ObjectIds.UInt16, ua.ObjectIds.UInt32, ua.ObjectIds.UInt64,
}


# DataType identifier (numeric) -> VariantType.
# The numeric identifier matches the VariantType enum value for most
# primitive types because the OPC UA spec assigns DataType NodeIds in
# numeric order that mirrors VariantType values.
_DATATYPE_TO_VARIANT: dict[int, ua.VariantType] = {
    1: ua.VariantType.Boolean,
    2: ua.VariantType.SByte,
    3: ua.VariantType.Byte,
    4: ua.VariantType.Int16,
    5: ua.VariantType.UInt16,
    6: ua.VariantType.Int32,
    7: ua.VariantType.UInt32,
    8: ua.VariantType.Int64,
    9: ua.VariantType.UInt64,
    10: ua.VariantType.Float,
    11: ua.VariantType.Double,
    12: ua.VariantType.String,
    13: ua.VariantType.DateTime,
    14: ua.VariantType.Guid,
    15: ua.VariantType.ByteString,
    16: ua.VariantType.XmlElement,
    17: ua.VariantType.NodeId,
    18: ua.VariantType.ExpandedNodeId,
    19: ua.VariantType.StatusCode,
    20: ua.VariantType.QualifiedName,
    21: ua.VariantType.LocalizedText,
    22: ua.VariantType.ExtensionObject,
}


def variant_type_for_data_type(data_type_nid: ua.NodeId | None) -> ua.VariantType | None:
    """Return the OPC UA VariantType corresponding to a given DataType NodeId.

    Returns None for unknown / structured DataTypes so the caller can decide
    whether to use ExtensionObject encoding.
    """
    if data_type_nid is None:
        return None
    oid = data_type_nid.Identifier
    if not isinstance(oid, int):
        return None
    return _DATATYPE_TO_VARIANT.get(oid)


def decode_exported_value(
    exported_data_value: dict | None,
    data_type_node_id: ua.NodeId | None,
) -> ua.DataValue | None:
    """Build a `ua.DataValue` from an exported `attributes.value` dict."""
    if exported_data_value is None:
        return None

    raw_value = exported_data_value.get("value")
    if raw_value is None:
        variant = ua.Variant(None)
    else:
        variant = _decode_variant(raw_value, data_type_node_id)

    src_ts = _parse_iso_timestamp(exported_data_value.get("source_timestamp"))
    srv_ts = _parse_iso_timestamp(exported_data_value.get("server_timestamp"))
    status_code = _parse_status_code(exported_data_value.get("status_code"))

    kwargs: dict = {"Value": variant}
    if src_ts is not None:
        kwargs["SourceTimestamp"] = src_ts
    if srv_ts is not None:
        kwargs["ServerTimestamp"] = srv_ts
    if status_code is not None:
        kwargs["StatusCode_"] = status_code
    return ua.DataValue(**kwargs)


def _decode_variant(raw_value: Any, data_type_nid: ua.NodeId | None) -> ua.Variant:
    vt = variant_type_for_data_type(data_type_nid)

    if vt is None:
        # Structured / unknown DataType.  Most common cases:
        #   - ExtensionObject (Range, EnumValueType, ...)
        #   - Generic ByteString fallthrough
        return _decode_structured(raw_value, data_type_nid)

    # Scalar / simple value
    if isinstance(raw_value, dict) and raw_value.get("__type__") == "ByteString":
        raw_bytes = base64.b64decode(raw_value["base64"])
        return ua.Variant(raw_bytes, ua.VariantType.ByteString)

    if isinstance(raw_value, dict) and raw_value.get("__type__") == "Array":
        items = raw_value.get("items", [])
        decoded_items = [_decode_variant(x, data_type_nid) for x in items]
        return ua.Variant(decoded_items, vt)

    if vt == ua.VariantType.Boolean:
        return ua.Variant(bool(raw_value), vt)
    if vt in (
        ua.VariantType.SByte, ua.VariantType.Int16, ua.VariantType.Int32, ua.VariantType.Int64,
        ua.VariantType.Byte, ua.VariantType.UInt16, ua.VariantType.UInt32, ua.VariantType.UInt64,
    ):
        try:
            return ua.Variant(int(raw_value), vt)
        except Exception:
            return ua.Variant(int(float(raw_value)), vt)
    if vt == ua.VariantType.Float:
        return ua.Variant(float(raw_value), ua.VariantType.Float)
    if vt == ua.VariantType.Double:
        return ua.Variant(float(raw_value), ua.VariantType.Double)
    if vt == ua.VariantType.String or vt == ua.VariantType.XmlElement:
        return ua.Variant(str(raw_value), vt)
    if vt == ua.VariantType.DateTime:
        ts = _parse_iso_timestamp(raw_value)
        return ua.Variant(ts if ts is not None else raw_value, vt)
    if vt == ua.VariantType.Guid:
        return ua.Variant(str(raw_value), vt)
    if vt == ua.VariantType.NodeId:
        if isinstance(raw_value, dict) and raw_value.get("__type__") == "NodeId":
            sub = raw_value.get("node_id")
            from .nodeid_codec import decode_node_id
            return ua.Variant(decode_node_id(sub), vt)
        return ua.Variant(str(raw_value), vt)
    if vt == ua.VariantType.LocalizedText:
        if isinstance(raw_value, dict) and raw_value.get("__type__") == "LocalizedText":
            return ua.Variant(ua.LocalizedText(Text=raw_value.get("text"),
                                                Locale=raw_value.get("locale")), vt)
        return ua.Variant(str(raw_value), vt)
    if vt == ua.VariantType.QualifiedName:
        if isinstance(raw_value, dict) and raw_value.get("__type__") == "QualifiedName":
            return ua.Variant(ua.QualifiedName(raw_value.get("name"),
                                               int(raw_value.get("namespace_index", 0))), vt)
        return ua.Variant(str(raw_value), vt)
    if vt == ua.VariantType.StatusCode:
        if isinstance(raw_value, dict) and raw_value.get("__type__") == "StatusCode":
            return ua.Variant(int(raw_value.get("value", 0)), vt)
        return ua.Variant(int(raw_value), vt)
    if vt == ua.VariantType.ByteString:
        if isinstance(raw_value, str):
            try:
                return ua.Variant(base64.b64decode(raw_value, validate=True), vt)
            except Exception:
                pass
        return ua.Variant(base64.b64decode(raw_value["base64"]), vt) \
            if isinstance(raw_value, dict) and raw_value.get("__type__") == "ByteString" \
            else ua.Variant(str(raw_value).encode(), vt)
    if vt == ua.VariantType.ExtensionObject:
        return _decode_extension_object(raw_value)

    # Fallback
    return ua.Variant(raw_value, vt)


def _decode_structured(raw_value: Any, data_type_nid: ua.NodeId | None) -> ua.Variant:
    """Decode a value whose DataType is not a simple primitive (Range, Enum, etc.)."""
    if data_type_nid is not None and data_type_nid.Identifier == ua.ObjectIds.Range:
        obj = ua.Range()
        if isinstance(raw_value, dict) and raw_value.get("__type__") == "Range":
            obj.Low = float(raw_value.get("fields", {}).get("Low", 0))
            obj.High = float(raw_value.get("fields", {}).get("High", 0))
        return ua.Variant(obj, ua.VariantType.ExtensionObject)

    if data_type_nid is not None and data_type_nid.Identifier == ua.ObjectIds.EnumValueType:
        obj = ua.EnumValueType()
        if isinstance(raw_value, dict) and raw_value.get("__type__") == "EnumValueType":
            fields = raw_value.get("fields", {})
            obj.Value = int(fields.get("Value", 0))
            dn = fields.get("DisplayName") or {}
            obj.DisplayName = ua.LocalizedText(Text=dn.get("text"),
                                               Locale=dn.get("locale"))
            de = fields.get("Description") or {}
            obj.Description = ua.LocalizedText(Text=de.get("text"),
                                               Locale=de.get("locale"))
        return ua.Variant(obj, ua.VariantType.ExtensionObject)

    # Best-effort: try ExtensionObject
    return _decode_extension_object(raw_value)


def _decode_extension_object(raw_value: Any) -> ua.Variant:
    """Decode any value into an ExtensionObject Variant.

    Supports:
        * Decoded dict (e.g. Range, EnumValueType, BuildInfo, ...)
        * Raw undecoded dict (body_base64)
        * Already-constructed ua.ExtensionObject (passthrough)
    """
    if isinstance(raw_value, ua.ExtensionObject):
        return ua.Variant(raw_value, ua.VariantType.ExtensionObject)
    if not isinstance(raw_value, dict):
        return ua.Variant(str(raw_value), ua.VariantType.ExtensionObject)

    t = raw_value.get("__type__")
    if t == "ExtensionObject" and "body_base64" in raw_value:
        body = base64.b64decode(raw_value["body_base64"])
        eo = ua.ExtensionObject()
        eo.Body = body
        if raw_value.get("type_id"):
            from .nodeid_codec import decode_node_id
            try:
                eo.TypeId = decode_node_id({"text": raw_value["type_id"],
                                            "namespace_index": 0,
                                            "identifier_type": "Numeric",
                                            "identifier": 0})
            except Exception:
                pass
        return ua.Variant(eo, ua.VariantType.ExtensionObject)

    if t == "Range":
        obj = ua.Range()
        obj.Low = float(raw_value.get("fields", {}).get("Low", 0))
        obj.High = float(raw_value.get("fields", {}).get("High", 0))
        return ua.Variant(obj, ua.VariantType.ExtensionObject)

    if t == "EnumValueType":
        obj = ua.EnumValueType()
        fields = raw_value.get("fields", {})
        obj.Value = int(fields.get("Value", 0))
        dn = fields.get("DisplayName") or {}
        obj.DisplayName = ua.LocalizedText(Text=dn.get("text"),
                                           Locale=dn.get("locale"))
        de = fields.get("Description") or {}
        obj.Description = ua.LocalizedText(Text=de.get("text"),
                                           Locale=de.get("locale"))
        return ua.Variant(obj, ua.VariantType.ExtensionObject)

    # BuildInfo / ServerStatus / other typed structs: pass through __ua_types__ fields
    if t and t in _KNOWN_DATACLASS_NAMES():
        cls = getattr(ua, t, None)
        if cls is not None:
            try:
                obj = cls()
                for fname, fval in raw_value.get("fields", {}).items():
                    if hasattr(obj, fname):
                        setattr(obj, fname, fval)
                return ua.Variant(obj, ua.VariantType.ExtensionObject)
            except Exception:
                pass

    # Unknown: fall back to string
    return ua.Variant(str(raw_value), ua.VariantType.ExtensionObject)


def _KNOWN_DATACLASS_NAMES() -> set[str]:
    import dataclasses
    out: set[str] = set()
    for name in dir(ua):
        obj = getattr(ua, name)
        if isinstance(obj, type) and dataclasses.is_dataclass(obj):
            out.add(name)
    return out


def _parse_iso_timestamp(value: Any) -> _dt.datetime | None:
    if value is None:
        return None
    if isinstance(value, _dt.datetime):
        return value
    s = str(value)
    try:
        # Python 3.7+ fromisoformat handles "+00:00" but not always "Z"
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        return _dt.datetime.fromisoformat(s)
    except Exception:
        return None


def _parse_status_code(value: Any) -> ua.StatusCode | None:
    if value is None:
        return None
    if isinstance(value, ua.StatusCode):
        return value
    name = str(value)
    try:
        return ua.StatusCode(name)
    except Exception:
        pass
    try:
        return ua.StatusCode(int(name, 0))
    except Exception:
        return ua.StatusCode(0)


def make_data_value_for_init(value: Any, data_type_nid: ua.NodeId | None,
                            timestamp_mode: str = "startup") -> ua.DataValue:
    """Build a startup-mode DataValue for a freshly-created Variable.

    timestamp_mode:
        * "startup"   -> SourceTimestamp = ServerTimestamp = now()
        * "preserve"  -> leave timestamps None (server will fill in)
    """
    variant = _decode_variant(value, data_type_nid)
    if timestamp_mode == "startup":
        now = _dt.datetime.now(_dt.timezone.utc)
        return ua.DataValue(Value=variant, SourceTimestamp=now, ServerTimestamp=now)
    return ua.DataValue(Value=variant)