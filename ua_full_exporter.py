"""
OPC UA 完整地址空间导出器 v2.0

连接真实 OPC UA Server，将地址空间（实例节点、类型节点、引用、值）
完整导出为结构化 JSON，供后续离线重建 Server 使用。

特性：
    * NodeId、BrowseName、TypeDefinition、DataType 全部保留 NamespaceIndex/URI
    * ByteString -> base64；LocalizedText / QualifiedName / NodeId 结构化
    * EnumValueType / Range / ExtensionObject / BuildInfo / ServerStatusDataType
      按字段结构化展开
    * 引用分类（Organizes / HasComponent / HasProperty / HasTypeDefinition /
      HasSubtype / HasModellingRule / HasInterface / 其他）
    * ModellingRule 与 TypeDefinition 分别记录
    * 单点失败不中断导出；遇到错误写入 errors 数组
    * 节点通过 NodeId 去重，避免双向引用循环

用法:
    python ua_full_exporter.py \\
        --url opc.tcp://10.10.58.117:18639 \\
        --output real_server_export_v2.json

    python ua_full_exporter.py \\
        --url opc.tcp://10.10.58.117:18639 \\
        --output real_server_export_v2.json \\
        --root "ns=2;s=P_7765a8f78a9266d7a83581ba1b39176a"
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import logging
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from asyncua import Client, Node, ua
from asyncua.ua import AttributeIds
from asyncua.ua.uaerrors import UaStatusCodeError
from asyncua.ua.uatypes import (
    ByteString,
    DataValue,
    DateTime,
    ExtensionObject,
    LocalizedText,
    NodeId,
    NodeIdType,
    QualifiedName,
    StatusCode,
    Variant,
    VariantType,
)

log = logging.getLogger("ua_full_exporter")

SCHEMA_VERSION = "2.0"

# Limits
MAX_INSTANCE_DEPTH = 20
MAX_TYPE_DEPTH = 20
MAX_NODES = 10000

# Common reference type NodeIds (ns=0)
REF_ORGANIZES = NodeId(35, 0)
REF_HAS_TYPE_DEFINITION = NodeId(40, 0)
REF_HAS_SUBTYPE = NodeId(45, 0)
REF_HAS_PROPERTY = NodeId(46, 0)
REF_HAS_COMPONENT = NodeId(47, 0)
REF_HAS_MODELLING_RULE = NodeId(37, 0)
REF_HAS_DESCRIPTION = NodeId(39, 0)
REF_HAS_ENCODING = NodeId(38, 0)

# Modelling rule NodeIds (ns=0)
MODELLING_RULES = {
    NodeId(78, 0): "Mandatory",
    NodeId(80, 0): "Optional",
    NodeId(11508, 0): "MandatoryPlaceholder",
    NodeId(11510, 0): "OptionalPlaceholder",
    NodeId(11469, 0): "ExposesItsArray",
}

# Standard NodeIds of common root objects (ns=0)
NS0_OBJECTS = NodeId(85, 0)
NS0_SERVER = NodeId(2253, 0)
NS0_SERVER_STATUS = NodeId(2256, 0)
NS0_SERVER_ARRAY = NodeId(2254, 0)
NS0_NAMESPACE_ARRAY = NodeId(2255, 0)
NS0_TYPES = NodeId(86, 0)
NS0_OBJECT_TYPES = NodeId(88, 0)
NS0_VARIABLE_TYPES = NodeId(89, 0)
NS0_REFERENCE_TYPES = NodeId(91, 0)
NS0_DATA_TYPES = NodeId(90, 0)


# ---------------------------------------------------------------------------
# Errors helper
# ---------------------------------------------------------------------------

class ErrorCollector:
    def __init__(self) -> None:
        self.items: list[dict] = []

    def add(
        self,
        *,
        node_id: str | None,
        operation: str,
        attribute: str | None = None,
        status_code: str | None = None,
        exception_type: str | None = None,
        message: str | None = None,
        fatal: bool = False,
    ) -> None:
        self.items.append(
            {
                "node_id": node_id,
                "operation": operation,
                "attribute": attribute,
                "status_code": status_code,
                "exception_type": exception_type,
                "message": message,
                "fatal": fatal,
            }
        )

    def to_list(self) -> list[dict]:
        return self.items


ERR = ErrorCollector()


# ---------------------------------------------------------------------------
# NodeId serialization
# ---------------------------------------------------------------------------

NODE_ID_TYPE_NAME = {
    NodeIdType.TwoByte: "TwoByte",
    NodeIdType.FourByte: "FourByte",
    NodeIdType.Numeric: "Numeric",
    NodeIdType.String: "String",
    NodeIdType.Guid: "Guid",
    NodeIdType.ByteString: "ByteString",
}


def node_id_text(nid: NodeId | None) -> str:
    """Return standard OPC UA NodeId text representation."""
    if nid is None:
        return ""
    try:
        t = nid.NodeIdType
    except Exception:
        return f"ns={nid.NamespaceIndex};?={nid.Identifier}"

    if t == NodeIdType.TwoByte:
        # ns=0 implicit; identifier must be < 256
        return f"i={nid.Identifier}"
    if t == NodeIdType.FourByte:
        if nid.NamespaceIndex == 0:
            return f"i={nid.Identifier}"
        return f"ns={nid.NamespaceIndex};i={nid.Identifier}"
    if t == NodeIdType.Numeric:
        return f"ns={nid.NamespaceIndex};i={nid.Identifier}"
    if t == NodeIdType.String:
        s = str(nid.Identifier)
        return f"ns={nid.NamespaceIndex};s={s}"
    if t == NodeIdType.Guid:
        g = str(nid.Identifier)
        return f"ns={nid.NamespaceIndex};g={g}"
    if t == NodeIdType.ByteString:
        b = nid.Identifier
        if isinstance(b, (bytes, bytearray)):
            return f"ns={nid.NamespaceIndex};b={base64.b64encode(bytes(b)).decode('ascii')}"
        return f"ns={nid.NamespaceIndex};b={b}"
    return f"ns={nid.NamespaceIndex};?={nid.Identifier}"


def node_id_dict(nid: NodeId | None, namespace_array: list[str]) -> dict:
    """Serialize a NodeId into a structured dict.

    Fields:
        text            - standard text form (ns=X;i=...)
        namespace_index - integer
        namespace_uri   - resolved from namespace_array, may be None
        identifier_type - string: TwoByte/FourByte/Numeric/String/Guid/ByteString
        identifier      - the identifier value (str/int/None for bytestring)
    """
    if nid is None:
        return {
            "text": "",
            "namespace_index": None,
            "namespace_uri": None,
            "identifier_type": None,
            "identifier": None,
        }
    try:
        ns_idx = int(nid.NamespaceIndex)
    except Exception:
        ns_idx = None
    ns_uri = None
    if ns_idx is not None and 0 <= ns_idx < len(namespace_array):
        ns_uri = namespace_array[ns_idx]
    id_type = NODE_ID_TYPE_NAME.get(getattr(nid, "NodeIdType", None), None)
    raw = nid.Identifier
    if isinstance(raw, (bytes, bytearray)):
        ident: Any = base64.b64encode(bytes(raw)).decode("ascii")
    else:
        ident = raw
    return {
        "text": node_id_text(nid),
        "namespace_index": ns_idx,
        "namespace_uri": ns_uri,
        "identifier_type": id_type,
        "identifier": ident,
    }


def qualified_name_dict(qn: QualifiedName | None, namespace_array: list[str]) -> dict:
    if qn is None:
        return {"name": None, "namespace_index": None, "namespace_uri": None}
    ns_idx = int(qn.NamespaceIndex) if qn.NamespaceIndex is not None else 0
    ns_uri = namespace_array[ns_idx] if 0 <= ns_idx < len(namespace_array) else None
    return {"name": str(qn.Name), "namespace_index": ns_idx, "namespace_uri": ns_uri}


def localized_text_dict(lt: LocalizedText | None) -> dict:
    if lt is None:
        return {"text": None, "locale": None}
    return {"text": lt.Text, "locale": lt.Locale}


# ---------------------------------------------------------------------------
# Value serialization
# ---------------------------------------------------------------------------

def _is_builtin_type(vt: VariantType) -> bool:
    return vt in (
        VariantType.Boolean,
        VariantType.SByte, VariantType.Int16, VariantType.Int32, VariantType.Int64,
        VariantType.Byte, VariantType.UInt16, VariantType.UInt32, VariantType.UInt64,
        VariantType.Float, VariantType.Double,
        VariantType.String, VariantType.XmlElement,
        VariantType.DateTime, VariantType.Guid,
        VariantType.ByteString,
        VariantType.LocalizedText,
        VariantType.QualifiedName,
        VariantType.NodeId,
        VariantType.StatusCode,
        VariantType.ExtensionObject,
    )


def serialize_extension_object(obj: ExtensionObject | Any) -> dict:
    """Serialize an ExtensionObject (decoded or not) into a structured dict.

    Decoded structs are dataclasses (EnumValueType, Range, EUInformation,
    BuildInfo, ServerStatusDataType, etc.) — they have __dataclass_fields__
    but no Body/TypeId attributes.

    Undecoded ExtensionObjects carry Body (bytes or struct) and TypeId.
    """
    if obj is None:
        return {"__type__": "ExtensionObject", "value": None}

    cls_name = obj.__class__.__name__
    is_dataclass = hasattr(obj, "__dataclass_fields__")
    has_ua_types = hasattr(obj, "__ua_types__")
    is_extension_object = isinstance(obj, ExtensionObject)

    # Try to extract TypeId if present
    type_id = getattr(obj, "TypeId", None)
    type_id_text = node_id_text(type_id) if isinstance(type_id, NodeId) else None

    # Decoded dataclass-like struct
    if (is_dataclass or has_ua_types) and not is_extension_object:
        field_names: list[str] = []
        if has_ua_types:
            field_names = list(obj.__ua_types__)
        elif is_dataclass:
            field_names = [f.name for f in obj.__dataclass_fields__.values()]
        fields: dict[str, Any] = {}
        for fname in field_names:
            try:
                fval = getattr(obj, fname)
            except Exception:
                fields[fname] = None
                continue
            fields[fname] = serialize_value(fval, None)
        return {
            "__type__": cls_name,
            "encoding_id": type_id_text,
            "fields": fields,
        }

    # Undecoded ExtensionObject
    encoding = getattr(obj, "Encoding", None)
    encoding_name = None
    if encoding is not None:
        try:
            encoding_name = encoding.name
        except Exception:
            encoding_name = str(encoding)
    body = getattr(obj, "Body", None)

    result: dict[str, Any] = {
        "__type__": "ExtensionObject",
        "type_id": type_id_text,
        "encoding": encoding_name,
    }
    if isinstance(body, (bytes, bytearray)):
        result["body_base64"] = base64.b64encode(bytes(body)).decode("ascii")
        result["body_length"] = len(body)
    elif body is not None:
        result["body"] = str(body)
    return result


def serialize_value(val: Any, vt: VariantType | None = None) -> Any:
    """Convert any UA Variant value into a JSON-safe representation."""
    if val is None:
        return None

    # Auto-detect vt if missing
    if vt is None:
        if isinstance(val, bool):
            vt = VariantType.Boolean
        elif isinstance(val, (bytes, bytearray)):
            vt = VariantType.ByteString
        elif isinstance(val, int):
            vt = VariantType.Int64
        elif isinstance(val, float):
            vt = VariantType.Double
        elif isinstance(val, str):
            vt = VariantType.String
        elif isinstance(val, LocalizedText):
            vt = VariantType.LocalizedText
        elif isinstance(val, QualifiedName):
            vt = VariantType.QualifiedName
        elif isinstance(val, NodeId):
            vt = VariantType.NodeId
        elif isinstance(val, DateTime):
            vt = VariantType.DateTime
        elif isinstance(val, ExtensionObject):
            vt = VariantType.ExtensionObject

    if vt in (
        VariantType.Boolean,
        VariantType.SByte, VariantType.Int16, VariantType.Int32, VariantType.Int64,
        VariantType.Byte, VariantType.UInt16, VariantType.UInt32, VariantType.UInt64,
        VariantType.Float, VariantType.Double,
    ):
        return val

    if vt == VariantType.String or vt == VariantType.XmlElement:
        return str(val)

    if vt == VariantType.DateTime:
        if isinstance(val, DateTime):
            return val.isoformat()
        return str(val)

    if vt == VariantType.Guid:
        return str(val)

    if vt == VariantType.ByteString:
        if isinstance(val, (bytes, bytearray)):
            b = bytes(val)
            return {
                "__type__": "ByteString",
                "base64": base64.b64encode(b).decode("ascii"),
                "length": len(b),
            }
        return {"__type__": "ByteString", "base64": "", "length": 0}

    if vt == VariantType.LocalizedText:
        if isinstance(val, LocalizedText):
            return {"__type__": "LocalizedText", "text": val.Text, "locale": val.Locale}
        return {"__type__": "LocalizedText", "text": str(val)}

    if vt == VariantType.QualifiedName:
        if isinstance(val, QualifiedName):
            return {
                "__type__": "QualifiedName",
                "name": str(val.Name),
                "namespace_index": int(val.NamespaceIndex) if val.NamespaceIndex is not None else 0,
            }
        return {"__type__": "QualifiedName", "name": str(val)}

    if vt == VariantType.NodeId:
        if isinstance(val, NodeId):
            return {
                "__type__": "NodeId",
                "node_id": {
                    "text": node_id_text(val),
                    "namespace_index": int(val.NamespaceIndex),
                    "identifier_type": NODE_ID_TYPE_NAME.get(val.NodeIdType),
                    "identifier": (
                        base64.b64encode(bytes(val.Identifier)).decode("ascii")
                        if isinstance(val.Identifier, (bytes, bytearray)) else val.Identifier
                    ),
                },
            }
        return {"__type__": "NodeId", "node_id": {"text": str(val)}}

    if vt == VariantType.StatusCode:
        if isinstance(val, StatusCode):
            return {"__type__": "StatusCode", "name": val.name, "value": int(val.value)}
        return {"__type__": "StatusCode", "value": int(val)}

    if vt == VariantType.ExtensionObject:
        return serialize_extension_object(val)

    if isinstance(val, (list, tuple)):
        items = [serialize_value(v) for v in val]
        elem_vt = vt
        # try to derive a more specific element variant type from the python type
        if val:
            sample = val[0]
            elem_vt = _infer_variant_type(sample)
        return {
            "__type__": "Array",
            "element_variant_type": elem_vt.name if hasattr(elem_vt, "name") else str(elem_vt),
            "length": len(val),
            "items": items,
        }

    return str(val)


def _infer_variant_type(sample: Any) -> VariantType:
    if isinstance(sample, bool):
        return VariantType.Boolean
    if isinstance(sample, int):
        return VariantType.Int64
    if isinstance(sample, float):
        return VariantType.Double
    if isinstance(sample, (bytes, bytearray)):
        return VariantType.ByteString
    if isinstance(sample, str):
        return VariantType.String
    if isinstance(sample, LocalizedText):
        return VariantType.LocalizedText
    if isinstance(sample, QualifiedName):
        return VariantType.QualifiedName
    if isinstance(sample, NodeId):
        return VariantType.NodeId
    if isinstance(sample, DateTime):
        return VariantType.DateTime
    if isinstance(sample, ExtensionObject):
        return VariantType.ExtensionObject
    return VariantType.Variant


def serialize_data_value(dv: DataValue | None) -> dict:
    """Serialize a DataValue (Value + status + timestamps)."""
    if dv is None:
        return {"value": None, "status_code": None, "source_timestamp": None, "server_timestamp": None}

    val = dv.Value
    vt = None
    if val is not None:
        vt = val.VariantType if hasattr(val, "VariantType") else None
    serialized_value = serialize_value(val.Value if val is not None else None, vt)

    return {
        "value": serialized_value,
        "status_code": dv.StatusCode.name if dv.StatusCode else None,
        "source_timestamp": dv.SourceTimestamp.isoformat() if dv.SourceTimestamp else None,
        "server_timestamp": dv.ServerTimestamp.isoformat() if dv.ServerTimestamp else None,
    }


# ---------------------------------------------------------------------------
# Reference type lookup
# ---------------------------------------------------------------------------

class ReferenceTypeCache:
    def __init__(self, client: Client) -> None:
        self.client = client
        self._cache: dict[str, tuple[str, NodeId]] = {}

    async def lookup(self, ref_type_id: NodeId) -> tuple[str, NodeId]:
        """Return (BrowseName, NodeId) for a reference type NodeId."""
        key = node_id_text(ref_type_id)
        if key in self._cache:
            return self._cache[key]
        try:
            n = self.client.get_node(ref_type_id)
            bn = await n.read_browse_name()
            name = str(bn.Name)
        except Exception as e:
            log.debug("ReferenceType lookup failed for %s: %s", key, e)
            name = "Unknown"
        result = (name, ref_type_id)
        self._cache[key] = result
        return result


# ---------------------------------------------------------------------------
# Attribute readers
# ---------------------------------------------------------------------------

async def _read_attr_safe(
    client: Client,
    node: Node,
    attr_id: AttributeIds | int,
    errors: list[dict],
    record_errors: bool = True,
) -> tuple[Any, StatusCode | None]:
    """Read a single attribute; never raises."""
    try:
        # asyncua's high-level helper expects AttributeIds enum
        dv = await node.read_attribute(attr_id)
        return dv.Value.Value if dv else None, (dv.StatusCode if dv else None)
    except UaStatusCodeError as sc:
        sc_value = sc.code if hasattr(sc, "code") else sc
        name = "Unknown"
        try:
            name = StatusCode(int(sc_value)).name
        except Exception:
            name = str(sc_value)
        if record_errors:
            errors.append({
                "attribute": str(attr_id),
                "status_code": name,
                "exception_type": "UaStatusCodeError",
                "message": str(sc),
            })
        return None, StatusCode(int(sc_value)) if sc_value is not None else None
    except Exception as e:
        if record_errors:
            errors.append({
                "attribute": str(attr_id),
                "status_code": None,
                "exception_type": type(e).__name__,
                "message": str(e),
            })
        return None, None


async def _read_attributes_batch(
    client: Client,
    node: Node,
    attr_ids: list[AttributeIds | int],
) -> list[DataValue | None]:
    """Read multiple attributes in a single round trip; never raises."""
    try:
        return list(await node.read_attributes(attr_ids))
    except Exception as e:
        log.debug("Batch read_attributes failed on %s: %s", node.nodeid, e)
        return [None] * len(attr_ids)


async def read_node_full(
    client: Client,
    node: Node,
    node_class_name: str | None,
    ref_cache: ReferenceTypeCache,
    namespace_array: list[str],
) -> dict:
    """Read all attributes for a single node. Returns a flat dict.

    Does not include references (handled separately).
    """
    errors: list[dict] = []
    nid = node.nodeid

    attrs: dict[str, Any] = {}

    # Standard attributes — read in a single batch
    base_attr_ids: list[AttributeIds] = [
        AttributeIds.BrowseName,
        AttributeIds.DisplayName,
        AttributeIds.Description,
        AttributeIds.WriteMask,
        AttributeIds.UserWriteMask,
    ]
    base_results = await _read_attributes_batch(client, node, base_attr_ids)
    bn = (base_results[0].Value.Value if base_results[0] and base_results[0].Value else None)
    dn = (base_results[1].Value.Value if base_results[1] and base_results[1].Value else None)
    desc = (base_results[2].Value.Value if base_results[2] and base_results[2].Value else None)
    wm = (base_results[3].Value.Value if base_results[3] and base_results[3].Value else None)
    uwm = (base_results[4].Value.Value if base_results[4] and base_results[4].Value else None)

    if isinstance(bn, QualifiedName):
        attrs["browse_name"] = qualified_name_dict(bn, namespace_array)
    else:
        attrs["browse_name"] = {"name": None, "namespace_index": None, "namespace_uri": None}
    if isinstance(dn, LocalizedText):
        attrs["display_name"] = localized_text_dict(dn)
    else:
        attrs["display_name"] = {"text": None, "locale": None}
    if isinstance(desc, LocalizedText):
        attrs["description"] = localized_text_dict(desc)
    else:
        attrs["description"] = {"text": None, "locale": None}
    attrs["write_mask"] = int(wm) if isinstance(wm, int) else 0
    attrs["user_write_mask"] = int(uwm) if isinstance(uwm, int) else 0

    nc_value = node_class_name

    if nc_value == "Object":
        en, _ = await _read_attr_safe(client, node, AttributeIds.EventNotifier, errors)
        attrs["event_notifier"] = int(en) if en is not None else None

    elif nc_value == "Variable":
        # Value
        try:
            dv = await node.read_data_value()
            attrs["value"] = serialize_data_value(dv)
        except Exception as e:
            attrs["value"] = {"value": None, "status_code": None, "source_timestamp": None, "server_timestamp": None}
            errors.append({"attribute": "Value", "exception_type": type(e).__name__, "message": str(e)})

        var_attr_ids = [
            AttributeIds.DataType,
            AttributeIds.ValueRank,
            AttributeIds.ArrayDimensions,
            AttributeIds.AccessLevel,
            AttributeIds.UserAccessLevel,
            AttributeIds.MinimumSamplingInterval,
            AttributeIds.Historizing,
        ]
        var_results = await _read_attributes_batch(client, node, var_attr_ids)
        for idx, name in enumerate([
                "DataType", "ValueRank", "ArrayDimensions",
                "AccessLevel", "UserAccessLevel",
                "MinimumSamplingInterval", "Historizing"]):
            if idx >= len(var_results):
                continue
            r = var_results[idx]
            val = r.Value.Value if r and r.Value else None
            if val is None:
                continue
            if name == "DataType" and isinstance(val, NodeId):
                attrs["data_type"] = node_id_dict(val, namespace_array)
            elif name == "ArrayDimensions":
                try:
                    attrs["array_dimensions"] = [int(x) for x in val]
                except Exception:
                    attrs["array_dimensions"] = []
            else:
                try:
                    attrs[name.lower()] = int(val) if not isinstance(val, float) else val
                except Exception:
                    pass

        # AccessLevelEx — best-effort, do not pollute errors if unsupported
        alex, _ = await _read_attr_safe(client, node, AttributeIds.AccessLevelEx, errors, record_errors=False)
        if alex is not None:
            try:
                attrs["access_level_ex"] = int(alex)
            except Exception:
                pass

    elif nc_value == "Method":
        ex, _ = await _read_attr_safe(client, node, AttributeIds.Executable, errors)
        attrs["executable"] = bool(ex) if ex is not None else None
        uex, _ = await _read_attr_safe(client, node, AttributeIds.UserExecutable, errors)
        attrs["user_executable"] = bool(uex) if uex is not None else None
        try:
            ia_node = await node.get_child(["0:InputArguments"])
            attrs["input_arguments"] = serialize_data_value(await ia_node.read_data_value())
        except Exception:
            # Most Methods have no InputArguments; silence
            pass
        try:
            oa_node = await node.get_child(["0:OutputArguments"])
            attrs["output_arguments"] = serialize_data_value(await oa_node.read_data_value())
        except Exception:
            pass

    elif nc_value in ("ObjectType", "VariableType"):
        ia, _ = await _read_attr_safe(client, node, AttributeIds.IsAbstract, errors)
        attrs["is_abstract"] = bool(ia) if ia is not None else None

        if nc_value == "VariableType":
            vt_attr_ids = [AttributeIds.DataType, AttributeIds.ValueRank, AttributeIds.ArrayDimensions]
            vt_results = await _read_attributes_batch(client, node, vt_attr_ids)
            for idx, name in enumerate(["DataType", "ValueRank", "ArrayDimensions"]):
                if idx >= len(vt_results):
                    continue
                r = vt_results[idx]
                val = r.Value.Value if r and r.Value else None
                if val is None:
                    continue
                if name == "DataType" and isinstance(val, NodeId):
                    attrs["data_type"] = node_id_dict(val, namespace_array)
                elif name == "ArrayDimensions":
                    try:
                        attrs["array_dimensions"] = [int(x) for x in val]
                    except Exception:
                        attrs["array_dimensions"] = []
                elif name == "ValueRank":
                    try:
                        attrs["value_rank"] = int(val)
                    except Exception:
                        pass

        # Value attribute: read best-effort (do not pollute errors if unsupported)
        try:
            dv = await node.read_data_value()
            if dv is not None:
                sc = dv.StatusCode
                if sc is not None and not sc.is_bad():
                    attrs["value"] = serialize_data_value(dv)
                else:
                    attrs["value"] = {"value": None, "status_code": sc.name if sc else None,
                                      "source_timestamp": None, "server_timestamp": None}
        except Exception:
            pass

    elif nc_value == "ReferenceType":
        sym, _ = await _read_attr_safe(client, node, AttributeIds.Symmetric, errors)
        attrs["symmetric"] = bool(sym) if sym is not None else None
        inv, _ = await _read_attr_safe(client, node, AttributeIds.InverseName, errors)
        if isinstance(inv, LocalizedText):
            attrs["inverse_name"] = localized_text_dict(inv)
        else:
            attrs["inverse_name"] = {"text": None, "locale": None}

    elif nc_value == "DataType":
        attrs["is_abstract"] = None
        try:
            dtd, _ = await _read_attr_safe(client, node, AttributeIds.DataTypeDefinition, errors)
            if dtd is not None:
                attrs["data_type_definition"] = serialize_value(dtd, VariantType.ExtensionObject)
        except Exception:
            pass

    if errors:
        for e in errors:
            e["node_id"] = node_id_text(nid)
        ERR.items.extend(errors)

    return attrs


# ---------------------------------------------------------------------------
# References
# ---------------------------------------------------------------------------

async def collect_references(
    client: Client,
    node: Node,
    node_class_name: str | None,
    ref_cache: ReferenceTypeCache,
    namespace_array: list[str],
    seen_refs: set[tuple[str, str, str, str]],
) -> list[dict]:
    """Collect all references for a node, deduplicated.

    Returns list of reference dicts.
    """
    refs_out: list[dict] = []
    try:
        raw_refs = await node.get_references()
    except Exception as e:
        ERR.add(
            node_id=node_id_text(node.nodeid),
            operation="get_references",
            exception_type=type(e).__name__,
            message=str(e),
        )
        return refs_out

    source_text = node_id_text(node.nodeid)

    # Gather unique ref type ids and unique target ids for batch reads
    unique_ref_types: dict[str, NodeId] = {}
    unique_targets: dict[str, NodeId] = {}

    candidate_refs: list[dict] = []
    for ref in raw_refs:
        try:
            rt_name, _ = await ref_cache.lookup(ref.ReferenceTypeId)
        except Exception:
            rt_name = "Unknown"

        target_text = node_id_text(ref.NodeId)
        is_forward = bool(ref.IsForward)
        key = (source_text, rt_name, str(is_forward), target_text)
        if key in seen_refs:
            continue
        seen_refs.add(key)

        unique_ref_types.setdefault(node_id_text(ref.ReferenceTypeId), ref.ReferenceTypeId)
        unique_targets.setdefault(target_text, ref.NodeId)

        candidate_refs.append({
            "source": source_text,
            "target": target_text,
            "rt_name": rt_name,
            "rt_id": ref.ReferenceTypeId,
            "is_forward": is_forward,
        })

    # Batch read target BrowseName + NodeClass
    target_nids = list(unique_targets.values())
    target_bn: dict[str, QualifiedName | None] = {}
    target_nc: dict[str, str | None] = {}
    if target_nids:
        try:
            bn_results = await client.uaclient.read_attributes(target_nids, ua.AttributeIds.BrowseName)
            for nid, dv in zip(target_nids, bn_results):
                target_bn[node_id_text(nid)] = dv.Value.Value if dv and dv.Value else None
        except Exception:
            for nid in target_nids:
                target_bn[node_id_text(nid)] = None
        try:
            nc_results = await client.uaclient.read_attributes(target_nids, ua.AttributeIds.NodeClass)
            for nid, dv in zip(target_nids, nc_results):
                if dv and dv.Value:
                    val = dv.Value.Value
                    target_nc[node_id_text(nid)] = val.name if hasattr(val, "name") else str(val)
                else:
                    target_nc[node_id_text(nid)] = None
        except Exception:
            for nid in target_nids:
                target_nc[node_id_text(nid)] = None

    for c in candidate_refs:
        bn_val = target_bn.get(c["target"])
        if isinstance(bn_val, QualifiedName):
            target_browse_name = qualified_name_dict(bn_val, namespace_array)
        else:
            target_browse_name = {"name": None, "namespace_index": None, "namespace_uri": None}
        target_node_class = target_nc.get(c["target"])
        rt_id = c["rt_id"]
        refs_out.append({
            "source_node_id": c["source"],
            "target_node_id": c["target"],
            "reference_type": {
                "node_id": node_id_text(rt_id),
                "browse_name": c["rt_name"],
                "namespace_index": int(rt_id.NamespaceIndex) if rt_id is not None else None,
            },
            "is_forward": c["is_forward"],
            "target_node_class": target_node_class,
            "target_browse_name": target_browse_name,
        })

    return refs_out


# ---------------------------------------------------------------------------
# Modelling rule
# ---------------------------------------------------------------------------

def find_modelling_rule(references: list[dict]) -> dict | None:
    for r in references:
        if r["reference_type"]["browse_name"] == "HasModellingRule" and r["is_forward"]:
            return {
                "node_id": r["target_node_id"],
                "browse_name": r["target_browse_name"]["name"],
            }
    return None


# ---------------------------------------------------------------------------
# Tree walker for instance nodes
# ---------------------------------------------------------------------------

class InstanceCollector:
    def __init__(
        self,
        client: Client,
        namespace_array: list[str],
        ref_cache: ReferenceTypeCache,
    ) -> None:
        self.client = client
        self.namespace_array = namespace_array
        self.ref_cache = ref_cache
        self.nodes: dict[str, dict] = {}
        self.references: list[dict] = []
        self.seen_refs: set[tuple[str, str, str, str]] = set()
        self.parent_map: dict[str, str] = {}
        self.path_map: dict[str, str] = {}
        self.type_defs_to_fetch: set[str] = set()

    async def collect(
        self,
        node: Node,
        path: str,
        depth: int,
        max_depth: int,
    ) -> None:
        if len(self.nodes) >= MAX_NODES:
            return
        if depth > max_depth:
            return
        nid_text = node_id_text(node.nodeid)
        if nid_text in self.nodes:
            # Already visited, but still update parent if not set
            if nid_text not in self.parent_map:
                # Don't overwrite parent, but track this as alternative path
                pass
            return

        # NodeClass
        try:
            nc = await node.read_node_class()
            nc_name = nc.name if hasattr(nc, "name") else str(nc)
        except Exception as e:
            ERR.add(node_id=nid_text, operation="read_node_class", exception_type=type(e).__name__, message=str(e))
            return

        # Read all attributes
        attrs = await read_node_full(self.client, node, nc_name, self.ref_cache, self.namespace_array)

        # Read references
        refs = await collect_references(
            self.client, node, nc_name, self.ref_cache, self.namespace_array, self.seen_refs
        )

        # Identify TypeDefinition
        type_def = None
        for r in refs:
            if r["reference_type"]["browse_name"] == "HasTypeDefinition" and r["is_forward"]:
                td_nid = self.client.get_node(r["target_node_id"])
                try:
                    td_bn = await td_nid.read_browse_name()
                    type_def = {
                        "node_id": r["target_node_id"],
                        "browse_name": str(td_bn.Name),
                        "namespace_index": int(td_bn.NamespaceIndex) if td_bn.NamespaceIndex is not None else 0,
                        "namespace_uri": self.namespace_array[int(td_bn.NamespaceIndex)]
                            if td_bn.NamespaceIndex is not None and 0 <= int(td_bn.NamespaceIndex) < len(self.namespace_array) else None,
                    }
                    self.type_defs_to_fetch.add(r["target_node_id"])
                except Exception:
                    type_def = {
                        "node_id": r["target_node_id"],
                        "browse_name": None,
                        "namespace_index": None,
                        "namespace_uri": None,
                    }
                    self.type_defs_to_fetch.add(r["target_node_id"])
                break

        node_entry = {
            "node_id": node_id_dict(node.nodeid, self.namespace_array),
            "node_class": nc_name,
            "attributes": attrs,
            "type_definition": type_def,
            "parent_node_id": self.parent_map.get(nid_text),
            "path": path,
            "read_errors": [e for e in ERR.items[-50:] if e.get("node_id") == nid_text] if False else [],
        }
        # Drop accumulated temp errors from attrs; they are already merged globally
        node_entry["read_errors"] = []

        self.nodes[nid_text] = node_entry
        self.path_map[nid_text] = path
        self.references.extend(refs)

        # Find forward hierarchical children
        # We treat Organizes, HasComponent, HasProperty as child-bearing
        child_ref_types = {"Organizes", "HasComponent", "HasProperty"}
        for r in refs:
            if r["is_forward"] and r["reference_type"]["browse_name"] in child_ref_types:
                child_node = self.client.get_node(r["target_node_id"])
                child_text = r["target_node_id"]
                if child_text not in self.nodes:
                    self.parent_map[child_text] = nid_text
                    child_path = f"{path}/{r['target_browse_name']['name']}"
                    await self.collect(child_node, child_path, depth + 1, max_depth)

    async def collect_all(self, roots: list[Node]) -> None:
        for root in roots:
            root_text = node_id_text(root.nodeid)
            self.parent_map[root_text] = None  # explicit
            try:
                bn = await root.read_browse_name()
                root_name = str(bn.Name)
            except Exception:
                root_name = root_text
            await self.collect(root, root_name, 0, MAX_INSTANCE_DEPTH)


# ---------------------------------------------------------------------------
# Type node collector
# ---------------------------------------------------------------------------

class TypeCollector:
    def __init__(
        self,
        client: Client,
        namespace_array: list[str],
        ref_cache: ReferenceTypeCache,
    ) -> None:
        self.client = client
        self.namespace_array = namespace_array
        self.ref_cache = ref_cache
        self.types: dict[str, dict] = {}
        self.references: list[dict] = []
        self.seen_refs: set[tuple[str, str, str, str]] = set()

    async def visit(self, type_node_id: NodeId, depth: int) -> None:
        if depth > MAX_TYPE_DEPTH:
            return
        if len(self.types) >= MAX_NODES:
            return
        text = node_id_text(type_node_id)
        if text in self.types:
            return

        node = self.client.get_node(type_node_id)
        try:
            nc = await node.read_node_class()
            nc_name = nc.name if hasattr(nc, "name") else str(nc)
        except Exception as e:
            ERR.add(node_id=text, operation="read_node_class",
                    exception_type=type(e).__name__, message=str(e))
            return

        # Accept both TypeDefinition nodes and declaration children
        if nc_name not in ("ObjectType", "VariableType", "DataType", "ReferenceType",
                            "Object", "Variable"):
            return

        # Read attributes (skip Value for non-Variable/VariableType to avoid spurious errors)
        attrs = await read_node_full(self.client, node, nc_name, self.ref_cache, self.namespace_array)

        # Read refs
        refs = await collect_references(
            self.client, node, nc_name, self.ref_cache, self.namespace_array, self.seen_refs
        )

        modelling_rule = find_modelling_rule(refs)

        # Find parent type via HasSubtype (inverse)
        parent_type_text = None
        for r in refs:
            if r["reference_type"]["browse_name"] == "HasSubtype" and not r["is_forward"]:
                parent_type_text = r["target_node_id"]
                break

        type_entry = {
            "node_id": node_id_dict(type_node_id, self.namespace_array),
            "node_class": nc_name,
            "attributes": attrs,
            "modelling_rule": modelling_rule,
            "parent_type_node_id": parent_type_text,
            "is_type_declaration": nc_name in ("Object", "Variable"),
            "path": None,
            "read_errors": [],
        }
        self.types[text] = type_entry
        self.references.extend(refs)

        # Recurse parent type (only if non ns=0)
        if parent_type_text and not parent_type_text.startswith("ns=0;i=") \
                and not (parent_type_text.startswith("i=") and ";" not in parent_type_text):
            try:
                parent_nid = self.client.get_node(parent_type_text).nodeid
                await self.visit(parent_nid, depth + 1)
            except Exception:
                pass

        # Recurse into forward type-declared children (HasComponent/HasProperty)
        for r in refs:
            if not r["is_forward"]:
                continue
            rt_name = r["reference_type"]["browse_name"]
            if rt_name == "HasModellingRule":
                continue
            if rt_name in ("HasComponent", "HasProperty", "HasTypeDefinition"):
                target_text = r["target_node_id"]
                if target_text in self.types:
                    continue
                try:
                    tnode = self.client.get_node(target_text)
                    tnc = await tnode.read_node_class()
                    tnc_name = tnc.name if hasattr(tnc, "name") else str(tnc)
                except Exception:
                    continue
                if tnc_name in ("ObjectType", "VariableType", "DataType", "ReferenceType",
                                 "Object", "Variable"):
                    await self.visit(tnode.nodeid, depth + 1)

    async def collect_from(self, type_node_ids: Iterable[NodeId]) -> None:
        for tid in type_node_ids:
            await self.visit(tid, 0)


# ---------------------------------------------------------------------------
# Source server metadata
# ---------------------------------------------------------------------------

async def collect_source_server(client: Client, endpoint_url: str) -> dict:
    out: dict[str, Any] = {"endpoint_url": endpoint_url}

    try:
        endpoints = await client.get_endpoints()
        ed = endpoints[0]
        sd = ed.Server
        out["application_uri"] = str(sd.ApplicationUri) if sd.ApplicationUri else None
        out["product_uri"] = str(sd.ProductUri) if sd.ProductUri else None
        if sd.ApplicationName:
            out["application_name"] = {
                "text": sd.ApplicationName.Text,
                "locale": sd.ApplicationName.Locale,
            }
        else:
            out["application_name"] = {"text": None, "locale": None}
        try:
            out["application_type"] = sd.ApplicationType.name
        except Exception:
            out["application_type"] = str(sd.ApplicationType) if sd.ApplicationType is not None else None
        out["gateway_server_uri"] = str(sd.GatewayServerUri) if sd.GatewayServerUri else None
        out["discovery_profile_uri"] = str(sd.DiscoveryProfileUri) if sd.DiscoveryProfileUri else None
        try:
            out["server_capabilities_uri"] = str(ed.ServerCertificate) if ed.ServerCertificate else None
        except Exception:
            pass
    except Exception as e:
        ERR.add(node_id=None, operation="get_endpoints",
                exception_type=type(e).__name__, message=str(e))
        for k in ("application_uri", "product_uri", "application_name",
                  "application_type", "gateway_server_uri", "discovery_profile_uri"):
            out.setdefault(k, None)

    # ServerArray
    try:
        sa_node = client.get_node(NS0_SERVER_ARRAY)
        out["server_array"] = list(await sa_node.read_value())
    except Exception as e:
        out["server_array"] = []
        ERR.add(node_id=node_id_text(NS0_SERVER_ARRAY),
                operation="read_value", attribute="ServerArray",
                exception_type=type(e).__name__, message=str(e))

    # ServerStatus (BuildInfo, state, start_time, current_time)
    try:
        ss_node = client.get_node(NS0_SERVER_STATUS)
        ss = await ss_node.read_value()
        bi = ss.BuildInfo_
        out["server_status"] = {
            "start_time": ss.StartTime.isoformat() if ss.StartTime else None,
            "current_time": ss.CurrentTime.isoformat() if ss.CurrentTime else None,
            "state": ss.State.name if hasattr(ss.State, "name") else str(ss.State),
            "build_info": {
                "product_uri": str(bi.ProductUri) if bi.ProductUri else None,
                "manufacturer_name": str(bi.ManufacturerName) if bi.ManufacturerName else None,
                "product_name": str(bi.ProductName) if bi.ProductName else None,
                "software_version": str(bi.SoftwareVersion) if bi.SoftwareVersion else None,
                "build_number": str(bi.BuildNumber) if bi.BuildNumber else None,
                "build_date": bi.BuildDate.isoformat() if bi.BuildDate else None,
            },
        }
    except Exception as e:
        out["server_status"] = None
        ERR.add(node_id=node_id_text(NS0_SERVER_STATUS),
                operation="read_value", attribute="ServerStatus",
                exception_type=type(e).__name__, message=str(e))

    out["exported_at"] = datetime.now(timezone.utc).isoformat()
    return out


# ---------------------------------------------------------------------------
# Locate DeviceSetView
# ---------------------------------------------------------------------------

async def locate_device_set_view(client: Client, known_id: str | None) -> Node | None:
    """Try the known NodeId first; fall back to scanning Objects by BrowseName."""
    if known_id:
        try:
            n = client.get_node(known_id)
            bn = await n.read_browse_name()
            if bn.Name == "DeviceSetView":
                return n
        except Exception as e:
            ERR.add(node_id=known_id, operation="locate_device_set_view",
                    exception_type=type(e).__name__, message=str(e))

    # Fallback: browse Objects
    try:
        objects = client.get_node(NS0_OBJECTS)
        children = await objects.get_children()
        for c in children:
            try:
                bn = await c.read_browse_name()
                if bn.Name == "DeviceSetView":
                    return c
            except Exception:
                continue
    except Exception as e:
        ERR.add(node_id=node_id_text(NS0_OBJECTS),
                operation="browse_objects",
                exception_type=type(e).__name__, message=str(e))
    return None


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

async def run_export(
    url: str,
    output_path: Path,
    root_id: str | None,
    timeout: float,
    report_path: Path,
) -> None:
    log.info("=== ua_full_exporter v%s ===", SCHEMA_VERSION)
    log.info("连接: %s", url)
    log.info("超时: %.1f s", timeout)

    namespace_array: list[str] = []
    instance_collector: InstanceCollector | None = None
    type_collector: TypeCollector | None = None
    source_server: dict = {}

    try:
        async with Client(url, timeout=timeout) as client:
            log.info("连接成功")
            ref_cache = ReferenceTypeCache(client)

            # Namespace
            try:
                namespace_array = list(await client.get_namespace_array())
                log.info("NamespaceArray:")
                for i, uri in enumerate(namespace_array):
                    log.info("  ns=%d  %s", i, uri)
            except Exception as e:
                ERR.add(node_id=None, operation="get_namespace_array",
                        exception_type=type(e).__name__, message=str(e))
                raise

            # Server metadata
            source_server = await collect_source_server(client, url)
            log.info("服务器元数据: %s", source_server.get("application_name"))

            # Locate DeviceSetView
            dsv = await locate_device_set_view(client, root_id)
            if dsv is None:
                log.error("未找到 DeviceSetView")
                ERR.add(node_id=None, operation="locate_device_set_view",
                        exception_type="NotFound", message="DeviceSetView not found", fatal=True)
                # still export whatever we have
            else:
                dsv_text = node_id_text(dsv.nodeid)
                log.info("找到 DeviceSetView: %s", dsv_text)

                # Collect instance tree starting from Objects -> DeviceSetView
                instance_collector = InstanceCollector(client, namespace_array, ref_cache)
                # We include Objects as root as well so the model has the root context
                objects_node = client.get_node(NS0_OBJECTS)
                await instance_collector.collect_all([objects_node])

                # Find SOVs
                sov_names = []
                if dsv_text in instance_collector.nodes:
                    # Walk children via parent_map
                    for nid_text, parent in instance_collector.parent_map.items():
                        if parent == dsv_text:
                            node_info = instance_collector.nodes.get(nid_text)
                            if node_info:
                                sov_names.append(node_info["attributes"]["browse_name"]["name"])
                if sov_names:
                    log.info("找到 SOV1～SOV%d: %s", len(sov_names), ", ".join(sorted(sov_names)))
                else:
                    log.warning("DeviceSetView 下未发现 SOV 节点")

            # Collect types referenced by instances
            if instance_collector is not None and instance_collector.type_defs_to_fetch:
                type_collector = TypeCollector(client, namespace_array, ref_cache)
                # Build NodeId list from texts
                type_nids: list[NodeId] = []
                for t in instance_collector.type_defs_to_fetch:
                    try:
                        type_nids.append(client.get_node(t).nodeid)
                    except Exception:
                        continue
                await type_collector.collect_from(type_nids)

                # Also include specific known types if they were missed
                extras = ["ns=2;i=1110", "ns=2;i=2013", "ns=4;i=1005",
                          "ns=0;i=2368", "ns=0;i=68", "ns=0;i=63"]
                for t in extras:
                    if t in type_collector.types:
                        continue
                    try:
                        await type_collector.visit(client.get_node(t).nodeid, 0)
                    except Exception as e:
                        ERR.add(node_id=t, operation="visit_type_extra",
                                exception_type=type(e).__name__, message=str(e))

                log.info("已采集类型节点数量: %d", len(type_collector.types))

    except Exception as e:
        ERR.add(node_id=None, operation="run_export",
                exception_type=type(e).__name__, message=str(e),
                fatal=True)
        log.exception("连接或主流程失败: %s", e)

    # Build result
    nodes_list = []
    if instance_collector:
        nodes_list = list(instance_collector.nodes.values())

    refs_list = []
    if instance_collector:
        refs_list.extend(instance_collector.references)
    if type_collector:
        refs_list.extend(type_collector.references)

    # Deduplicate references (across instance + type collectors)
    seen: set[tuple] = set()
    deduped_refs: list[dict] = []
    for r in refs_list:
        key = (r["source_node_id"], r["target_node_id"],
               r["reference_type"]["browse_name"], str(r["is_forward"]))
        if key in seen:
            continue
        seen.add(key)
        deduped_refs.append(r)

    types_list = list(type_collector.types.values()) if type_collector else []

    # Statistics
    nc_counts: dict[str, int] = {}
    for n in nodes_list:
        nc_counts[n["node_class"]] = nc_counts.get(n["node_class"], 0) + 1
    for n in types_list:
        nc_counts[n["node_class"]] = nc_counts.get(n["node_class"], 0) + 1

    # Devices found (from instance collector)
    devices_found: list[str] = []
    if instance_collector:
        for n in nodes_list:
            bn = n.get("attributes", {}).get("browse_name", {})
            name = bn.get("name") if isinstance(bn, dict) else None
            if name and name.startswith("SOV") and n["node_class"] == "Object":
                devices_found.append(name)

    ref_type_counts: dict[str, int] = {}
    for r in deduped_refs:
        rt = r["reference_type"]["browse_name"]
        ref_type_counts[rt] = ref_type_counts.get(rt, 0) + 1

    statistics = {
        "instance_node_count": len(nodes_list),
        "type_node_count": len(types_list),
        "reference_count": len(deduped_refs),
        "object_count": nc_counts.get("Object", 0),
        "variable_count": nc_counts.get("Variable", 0),
        "method_count": nc_counts.get("Method", 0),
        "object_type_count": nc_counts.get("ObjectType", 0),
        "variable_type_count": nc_counts.get("VariableType", 0),
        "data_type_count": nc_counts.get("DataType", 0),
        "reference_type_count": nc_counts.get("ReferenceType", 0),
        "error_count": len(ERR.items),
        "devices_found": sorted(set(devices_found)),
        "reference_type_counts": ref_type_counts,
    }

    result = {
        "schema_version": SCHEMA_VERSION,
        "source_server": source_server,
        "namespace_array": [
            {"index": i, "uri": u} for i, u in enumerate(namespace_array)
        ],
        "roots": [
            {"name": "Objects", "node_id": node_id_dict(NS0_OBJECTS, namespace_array)},
        ],
        "nodes": nodes_list,
        "references": deduped_refs,
        "types": types_list,
        "errors": ERR.to_list(),
        "statistics": statistics,
    }

    # Save JSON
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    log.info("结果文件保存路径: %s", output_path)

    # Report
    write_report(report_path, result)
    log.info("报告文件保存路径: %s", report_path)


# ---------------------------------------------------------------------------
# Report writer
# ---------------------------------------------------------------------------

def write_report(path: Path, result: dict) -> None:
    """Generate a human-readable Markdown summary report."""
    src = result.get("source_server", {})
    stats = result.get("statistics", {})
    ns_array = result.get("namespace_array", [])

    lines: list[str] = []
    lines.append("# Real OPC UA Server 地址空间导出报告")
    lines.append("")
    lines.append("## 1. 基本信息")
    lines.append("")
    lines.append(f"- 连接地址: `{src.get('endpoint_url', '')}`")
    lines.append(f"- 导出时间: `{result.get('source_server', {}).get('exported_at', '')}`")
    app_name = src.get("application_name") or {}
    lines.append(f"- ApplicationName: `{app_name.get('text')}` (locale=`{app_name.get('locale')}`)")
    lines.append(f"- ApplicationUri: `{src.get('application_uri')}`")
    lines.append(f"- ProductUri: `{src.get('product_uri')}`")
    lines.append(f"- ApplicationType: `{src.get('application_type')}`")
    lines.append(f"- GatewayServerUri: `{src.get('gateway_server_uri')}`")
    lines.append(f"- DiscoveryProfileUri: `{src.get('discovery_profile_uri')}`")
    lines.append(f"- ServerArray: `{src.get('server_array')}`")
    if src.get("server_status"):
        ss = src["server_status"]
        bi = ss.get("build_info", {})
        lines.append(f"- ServerStatus.State: `{ss.get('state')}`")
        lines.append(f"- ServerStatus.StartTime: `{ss.get('start_time')}`")
        lines.append(f"- ServerStatus.CurrentTime: `{ss.get('current_time')}`")
        lines.append(f"- BuildInfo.ProductUri: `{bi.get('product_uri')}`")
        lines.append(f"- BuildInfo.ManufacturerName: `{bi.get('manufacturer_name')}`")
        lines.append(f"- BuildInfo.ProductName: `{bi.get('product_name')}`")
        lines.append(f"- BuildInfo.SoftwareVersion: `{bi.get('software_version')}`")
        lines.append(f"- BuildInfo.BuildNumber: `{bi.get('build_number')}`")
        lines.append(f"- BuildInfo.BuildDate: `{bi.get('build_date')}`")
    lines.append("")
    lines.append("### NamespaceArray")
    lines.append("")
    lines.append("| Index | URI |")
    lines.append("|------:|-----|")
    for entry in ns_array:
        lines.append(f"| {entry.get('index')} | `{entry.get('uri')}` |")
    lines.append("")
    lines.append("### 采集数量")
    lines.append("")
    lines.append(f"- 实例节点数量: **{stats.get('instance_node_count', 0)}**")
    lines.append(f"- 类型节点数量: **{stats.get('type_node_count', 0)}**")
    lines.append(f"- 引用数量: **{stats.get('reference_count', 0)}**")
    lines.append(f"- Object 节点: **{stats.get('object_count', 0)}**")
    lines.append(f"- Variable 节点: **{stats.get('variable_count', 0)}**")
    lines.append(f"- Method 节点: **{stats.get('method_count', 0)}**")
    lines.append(f"- ObjectType 节点: **{stats.get('object_type_count', 0)}**")
    lines.append(f"- VariableType 节点: **{stats.get('variable_type_count', 0)}**")
    lines.append(f"- DataType 节点: **{stats.get('data_type_count', 0)}**")
    lines.append(f"- ReferenceType 节点: **{stats.get('reference_type_count', 0)}**")
    lines.append(f"- 错误数量: **{stats.get('error_count', 0)}**")
    lines.append(f"- 找到的设备: `{', '.join(stats.get('devices_found', []))}`")
    lines.append("")

    # Root structure (instance tree)
    lines.append("## 2. 根结构（实例树）")
    lines.append("")
    lines.append("```")
    lines.extend(_render_instance_tree(result))
    lines.append("```")
    lines.append("")

    # Type summary
    lines.append("## 3. 类型摘要")
    lines.append("")
    if result.get("types"):
        lines.append("| NodeId | NodeClass | BrowseName | NamespaceIndex | NamespaceURI | ParentType |")
        lines.append("|--------|-----------|------------|---------------:|-------------|------------|")
        for t in result["types"]:
            nid = t["node_id"]
            attrs = t.get("attributes", {})
            bn = attrs.get("browse_name", {})
            parent = t.get("parent_type_node_id") or "-"
            lines.append(
                f"| `{nid['text']}` | {t['node_class']} | "
                f"`{bn.get('name')}` | {bn.get('namespace_index')} | "
                f"`{bn.get('namespace_uri')}` | `{parent}` |"
            )
    else:
        lines.append("_无_")
    lines.append("")

    # Reference summary
    lines.append("## 4. 引用摘要")
    lines.append("")
    rtc = stats.get("reference_type_counts", {})
    if rtc:
        lines.append("| ReferenceType | 数量 |")
        lines.append("|---------------|----:|")
        for rt, cnt in sorted(rtc.items(), key=lambda x: (-x[1], x[0])):
            lines.append(f"| {rt} | {cnt} |")
    else:
        lines.append("_无_")
    lines.append("")

    # Errors
    lines.append("## 5. 异常和缺失")
    lines.append("")
    errs = result.get("errors", [])
    if not errs:
        lines.append("_无错误_")
    else:
        lines.append(f"共 {len(errs)} 条错误。最多展示前 50 条：")
        lines.append("")
        lines.append("| NodeId | Operation | Attribute | StatusCode | Exception | Message |")
        lines.append("|--------|-----------|-----------|------------|-----------|---------|")
        for e in errs[:50]:
            lines.append(
                f"| `{e.get('node_id') or '-'}` | {e.get('operation')} | "
                f"{e.get('attribute') or '-'} | `{e.get('status_code') or '-'}` | "
                f"{e.get('exception_type') or '-'} | "
                f"`{(e.get('message') or '')[:120]}` |"
            )
        if len(errs) > 50:
            lines.append("")
            lines.append(f"_剩余 {len(errs) - 50} 条未列出_")
    lines.append("")

    # Required type checks
    lines.append("## 6. 验收检查")
    lines.append("")
    required_types = ["ns=2;i=1110", "ns=2;i=2013", "ns=4;i=1005"]
    existing = {t["node_id"]["text"] for t in result.get("types", [])}
    for r in required_types:
        present = "OK" if r in existing else "MISSING"
        lines.append(f"- 自定义类型 `{r}`: **{present}**")
    # Required devices
    required_devices = [f"SOV{i}" for i in range(1, 9)]
    devices = set(stats.get("devices_found", []))
    for d in required_devices:
        present = "OK" if d in devices else "MISSING"
        lines.append(f"- 设备 `{d}`: **{present}**")
    lines.append("")

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _render_instance_tree(result: dict) -> list[str]:
    """Return lines representing the instance tree as ASCII art."""
    nodes = {n["node_id"]["text"]: n for n in result.get("nodes", [])}
    parent_map: dict[str, str | None] = {n["node_id"]["text"]: n.get("parent_node_id") for n in nodes.values()}

    # Find roots
    roots = [nid for nid, parent in parent_map.items() if parent is None]

    lines: list[str] = []
    for root in roots:
        _render_subtree(root, "", True, nodes, parent_map, lines)
    if not roots:
        lines.append("(no instance nodes)")
    return lines


def _render_subtree(
    nid: str,
    prefix: str,
    is_last: bool,
    nodes: dict,
    parent_map: dict,
    lines: list[str],
) -> None:
    node = nodes.get(nid)
    if not node:
        return
    name = (node.get("attributes", {}).get("browse_name", {}) or {}).get("name") or nid
    nc = node.get("node_class", "")
    connector = "└─ " if is_last else "├─ "
    if prefix:
        lines.append(f"{prefix}{connector}{name}  ({nc})  [{nid}]")
    else:
        lines.append(f"{name}  ({nc})  [{nid}]")

    new_prefix = prefix + ("   " if is_last else "│  ")
    children = [n for n, p in parent_map.items() if p == nid]
    # Stable order by browse_name
    children.sort(key=lambda x: (nodes.get(x, {}).get("attributes", {}).get("browse_name", {}).get("name") or x))
    for i, child in enumerate(children):
        _render_subtree(child, new_prefix, i == len(children) - 1, nodes, parent_map, lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="OPC UA 完整地址空间导出器",
    )
    parser.add_argument("--url", required=True, help="OPC UA Server URL, e.g. opc.tcp://host:18639")
    parser.add_argument("--output", default="real_server_export_v2.json", help="输出 JSON 路径")
    parser.add_argument(
        "--root",
        default="ns=2;s=P_7765a8f78a9266d7a83581ba1b39176a",
        help="DeviceSetView NodeId（已知 ID）",
    )
    parser.add_argument("--report", default="real_server_export_report.md", help="报告 Markdown 路径")
    parser.add_argument("--timeout", type=float, default=30.0, help="连接超时(秒)")
    parser.add_argument("--user", help="用户名")
    parser.add_argument("--password", help="密码")
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    # Quiet down asyncua's per-browse chatter
    for noisy in ("asyncua.client.ua_client.UaClient",
                  "asyncua.client.client",
                  "asyncua.client.ua_client.UASocketProtocol"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    try:
        asyncio.run(run_export(
            url=args.url,
            output_path=Path(args.output),
            root_id=args.root,
            timeout=args.timeout,
            report_path=Path(args.report),
        ))
    except KeyboardInterrupt:
        log.warning("用户中断")
        return 130
    except Exception as e:
        log.exception("未捕获异常: %s", e)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())