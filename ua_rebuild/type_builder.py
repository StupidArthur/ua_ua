"""TypeBuilder: create ObjectType and VariableType nodes from a BuildPlan.

The builder only creates *custom* type nodes — i.e. those not in the
ns=0 builtin address space.  Standard ns=0 numeric types
(e.g. `i=58` BaseObjectType, `i=68` PropertyType, `i=2368` AnalogItemType)
are reused via the asyncua default address space.

Order of operations:

    parent_type (HasSubtype)
        -> child_type (HasSubtype)
            -> declaration Object/Variable (HasComponent or HasProperty)
"""

from __future__ import annotations

import logging
from typing import Any

from asyncua import ua
from asyncua.ua.uatypes import NodeId

from .asyncua_adapter import AsyncuaAddressSpaceAdapter
from .build_planner import BuildPlan
from .model_loader import (
    ExportModel,
    _infer_id_fields_from_text,
    node_id_spec_from_text,
)
from .model import NodeSpec


log = logging.getLogger("ua_rebuild.type_builder")


def _decode(text: str) -> NodeId:
    id_type, ident = _infer_id_fields_from_text(text)
    if text.startswith("ns="):
        try:
            ns = int(text.split(";", 1)[0].split("=", 1)[1])
        except Exception:
            ns = 0
    elif text.startswith("i="):
        ns = 0
    else:
        ns = 0
    if id_type in ("Numeric", "FourByte", "TwoByte"):
        return NodeId(int(ident), ns)
    return NodeId(str(ident), ns)


def _build_qname(spec: NodeSpec) -> ua.QualifiedName:
    return ua.QualifiedName(
        spec.browse_name.name or "",
        spec.browse_name.namespace_index or 0,
    )


def _build_lt(text: str | None, locale: str | None) -> ua.LocalizedText:
    return ua.LocalizedText(Text=text or "", Locale=locale or "")


def _mask_value(mask: str) -> ua.NodeId:
    """Map our mask name (e.g. 'ObjectType') to the NodeAttributesMask constant."""
    return getattr(ua.NodeAttributesMask, mask)


def _make_object_type_attrs(spec: NodeSpec) -> ua.ObjectTypeAttributes:
    attrs = ua.ObjectTypeAttributes()
    attrs.DisplayName = _build_lt(spec.display_name.text, spec.display_name.locale)
    attrs.Description = _build_lt(spec.description.text, spec.description.locale)
    attrs.WriteMask = spec.write_mask
    attrs.UserWriteMask = spec.user_write_mask
    attrs.IsAbstract = bool(spec.is_abstract) if spec.is_abstract is not None else False
    attrs.SpecifiedAttributes = (
        ua.NodeAttributesMask.DisplayName
        | ua.NodeAttributesMask.Description
        | ua.NodeAttributesMask.WriteMask
        | ua.NodeAttributesMask.UserWriteMask
        | ua.NodeAttributesMask.IsAbstract
    )
    return attrs


def _make_variable_type_attrs(spec: NodeSpec) -> ua.VariableTypeAttributes:
    attrs = ua.VariableTypeAttributes()
    attrs.DisplayName = _build_lt(spec.display_name.text, spec.display_name.locale)
    attrs.Description = _build_lt(spec.description.text, spec.description.locale)
    attrs.WriteMask = spec.write_mask
    attrs.UserWriteMask = spec.user_write_mask

    if spec.data_type is not None:
        attrs.DataType = _decode(spec.data_type.text)
    else:
        attrs.DataType = NodeId()

    attrs.ValueRank = spec.value_rank if spec.value_rank is not None else -2
    attrs.ArrayDimensions = list(spec.array_dimensions or [])
    attrs.IsAbstract = bool(spec.is_abstract) if spec.is_abstract is not None else False

    # The value, if present in the export
    if spec.value is not None and isinstance(spec.value, dict):
        raw = spec.value.get("value")
        if raw is not None:
            attrs.Value = _make_variant(raw, attrs.DataType)

    attrs.SpecifiedAttributes = (
        ua.NodeAttributesMask.DisplayName
        | ua.NodeAttributesMask.Description
        | ua.NodeAttributesMask.WriteMask
        | ua.NodeAttributesMask.UserWriteMask
        | ua.NodeAttributesMask.DataType
        | ua.NodeAttributesMask.ValueRank
        | ua.NodeAttributesMask.ArrayDimensions
        | ua.NodeAttributesMask.IsAbstract
    )
    if attrs.Value is not None:
        attrs.SpecifiedAttributes |= ua.NodeAttributesMask.Value
    return attrs


def _make_variant(raw: Any, data_type: NodeId) -> ua.Variant | None:
    """Construct a ua.Variant matching the DataType, mirroring `value_codec`.

    Returns None when the raw payload cannot be decoded.
    """
    if raw is None:
        return None
    if isinstance(raw, dict) and raw.get("__type__") == "Range":
        obj = ua.Range()
        fields = raw.get("fields") or {}
        obj.Low = float(fields.get("Low", 0.0))
        obj.High = float(fields.get("High", 0.0))
        return ua.Variant(obj, ua.VariantType.ExtensionObject)
    if isinstance(raw, dict) and raw.get("__type__") == "EnumValueType":
        obj = ua.EnumValueType()
        fields = raw.get("fields") or {}
        obj.Value = int(fields.get("Value", 0))
        dn = fields.get("DisplayName") or {}
        obj.DisplayName = ua.LocalizedText(Text=dn.get("text", ""),
                                           Locale=dn.get("locale", ""))
        de = fields.get("Description") or {}
        obj.Description = ua.LocalizedText(Text=de.get("text", ""),
                                           Locale=de.get("locale", ""))
        return ua.Variant(obj, ua.VariantType.ExtensionObject)
    if isinstance(raw, dict) and raw.get("__type__") == "ByteString":
        import base64
        return ua.Variant(base64.b64decode(raw["base64"]), ua.VariantType.ByteString)
    if isinstance(raw, str):
        return ua.Variant(raw, ua.VariantType.String)
    if isinstance(raw, bool):
        return ua.Variant(raw, ua.VariantType.Boolean)
    if isinstance(raw, (int, float)):
        # Choose Float / Double based on the DataType identifier
        if isinstance(data_type.Identifier, int):
            if data_type.Identifier == 10:
                return ua.Variant(float(raw), ua.VariantType.Float)
            if data_type.Identifier == 11:
                return ua.Variant(float(raw), ua.VariantType.Double)
        return ua.Variant(raw, ua.VariantType.Int64)
    return None


class TypeBuilder:
    def __init__(self, adapter: AsyncuaAddressSpaceAdapter, plan: BuildPlan,
                 model: ExportModel) -> None:
        self.adapter = adapter
        self.plan = plan
        self.model = model

    async def build_types(self) -> list:
        """Create every custom (non-builtin) ObjectType/VariableType."""
        return [r for spec in self.plan.custom_type_nodes
                for r in (await self.build_type(spec),) if r is not None]

    async def build_type(self, spec) -> list:
        """Build a single type spec. Returns a list with one record."""
        if spec.reuse_existing:
            log.info("[TYPE] REUSE %s %s", spec.node_id.text, spec.browse_name.name)
            return []
        if spec.node_class not in ("ObjectType", "VariableType"):
            return []
        if spec.node_class == "ObjectType":
            attrs = _make_object_type_attrs(spec)
            nc = ua.NodeClass.ObjectType
        else:
            attrs = _make_variable_type_attrs(spec)
            nc = ua.NodeClass.VariableType

        parent_id = _decode(spec.parent_node_id.text) if spec.parent_node_id else NodeId()
        ref_id = ua.NodeId(spec.parent_reference_type_id or 45, 0)

        record = await self.adapter.add_node_exact(
            parent_node_id=parent_id,
            reference_type_id=ref_id,
            requested_new_node_id=_decode(spec.node_id.text),
            browse_name=_build_qname(spec),
            node_class=nc,
            node_attributes=attrs,
            type_definition=NodeId(),
        )
        log.info("[TYPE] %s  %s parent=%s status=%s",
                 "OK" if record.status_code.is_good() else "FAIL",
                 spec.node_id.text, parent_id, record.status_code)
        return [record]

    async def build_declarations(self) -> list:
        """Create every type declaration Object/Variable inside its owning type."""
        return [r for spec in self.plan.type_declaration_nodes
                for r in (await self.build_declaration(spec),) if r is not None]

    async def build_declaration(self, spec) -> list:
        """Build a single declaration spec."""
        if spec.reuse_existing:
            return []
        if spec.node_class not in ("Object", "Variable"):
            return []
        attrs = self._make_declaration_attrs(spec)
        nc = (ua.NodeClass.Object if spec.node_class == "Object"
              else ua.NodeClass.Variable)
        parent_id = _decode(spec.parent_node_id.text) if spec.parent_node_id else NodeId()
        ref_id = ua.NodeId(spec.parent_reference_type_id or 47, 0)
        td_id = _decode(spec.type_definition.text) if spec.type_definition else NodeId()

        record = await self.adapter.add_node_exact(
            parent_node_id=parent_id,
            reference_type_id=ref_id,
            requested_new_node_id=_decode(spec.node_id.text),
            browse_name=_build_qname(spec),
            node_class=nc,
            node_attributes=attrs,
            type_definition=td_id,
        )
        log.info("[DECL] %s  %s parent=%s td=%s status=%s",
                 "OK" if record.status_code.is_good() else "FAIL",
                 spec.node_id.text, parent_id, td_id, record.status_code)
        return [record]

    async def build_modelling_rules(self) -> list:
        """Add HasModellingRule references for declarations that need them."""
        results = []
        for spec in self.plan.type_declaration_nodes:
            if spec.modelling_rule_node_id_text is None:
                continue
            item = ua.AddReferencesItem()
            item.SourceNodeId = _decode(spec.node_id.text)
            item.ReferenceTypeId = ua.NodeId(ua.ObjectIds.HasModellingRule)
            item.IsForward = True
            item.TargetNodeId = _decode(spec.modelling_rule_node_id_text)
            item.TargetNodeClass = ua.NodeClass.Object  # ModellingRule nodes are Objects
            result = self.adapter.server.iserver.node_mgt_service.add_references(
                [item], _admin_user())
            if result and result[0].is_bad():
                log.error("[MODELLING] FAIL %s -> %s status=%s",
                          spec.node_id.text, spec.modelling_rule_node_id_text,
                          result[0])
            else:
                log.info("[MODELLING] OK   %s -> %s",
                          spec.node_id.text, spec.modelling_rule_node_id_text)
            results.append(result[0] if result else None)
        return results

    def _make_declaration_attrs(self, spec: NodeSpec):
        if spec.node_class == "Object":
            attrs = ua.ObjectAttributes()
            attrs.DisplayName = _build_lt(spec.display_name.text, spec.display_name.locale)
            attrs.Description = _build_lt(spec.description.text, spec.description.locale)
            attrs.WriteMask = spec.write_mask
            attrs.UserWriteMask = spec.user_write_mask
            attrs.EventNotifier = spec.event_notifier or 0
            attrs.SpecifiedAttributes = (
                ua.NodeAttributesMask.DisplayName
                | ua.NodeAttributesMask.Description
                | ua.NodeAttributesMask.WriteMask
                | ua.NodeAttributesMask.UserWriteMask
                | ua.NodeAttributesMask.EventNotifier
            )
            return attrs
        # Variable
        attrs = ua.VariableAttributes()
        attrs.DisplayName = _build_lt(spec.display_name.text, spec.display_name.locale)
        attrs.Description = _build_lt(spec.description.text, spec.description.locale)
        attrs.WriteMask = spec.write_mask
        attrs.UserWriteMask = spec.user_write_mask
        attrs.DataType = _decode(spec.data_type.text) if spec.data_type else NodeId()
        attrs.ValueRank = spec.value_rank if spec.value_rank is not None else -1
        attrs.ArrayDimensions = list(spec.array_dimensions or [])
        attrs.AccessLevel = _u8(spec.access_level if spec.access_level is not None else 1)
        attrs.UserAccessLevel = _u8(spec.user_access_level if spec.user_access_level is not None else 1)
        attrs.MinimumSamplingInterval = spec.minimum_sampling_interval or 0.0
        attrs.Historizing = bool(spec.historizing) if spec.historizing is not None else False
        if spec.value is not None and isinstance(spec.value, dict):
            raw = spec.value.get("value")
            if raw is not None:
                attrs.Value = _make_variant(raw, attrs.DataType)
        attrs.SpecifiedAttributes = (
            ua.NodeAttributesMask.DisplayName
            | ua.NodeAttributesMask.Description
            | ua.NodeAttributesMask.WriteMask
            | ua.NodeAttributesMask.UserWriteMask
            | ua.NodeAttributesMask.DataType
            | ua.NodeAttributesMask.ValueRank
            | ua.NodeAttributesMask.ArrayDimensions
            | ua.NodeAttributesMask.AccessLevel
            | ua.NodeAttributesMask.UserAccessLevel
            | ua.NodeAttributesMask.MinimumSamplingInterval
            | ua.NodeAttributesMask.Historizing
        )
        if attrs.Value is not None:
            attrs.SpecifiedAttributes |= ua.NodeAttributesMask.Value
        return attrs


def _u8(value: int) -> ua.Byte:
    return ua.Byte(value & 0xFF)


def _admin_user():
    from asyncua.server.internal_server import User, UserRole
    return User(role=UserRole.Admin)