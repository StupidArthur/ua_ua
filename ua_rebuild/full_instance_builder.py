"""FullInstanceBuilder: create Object/Variable instance nodes from a BuildPlan.

Used by Phase 2+ where the scope produces more than the 6 hard-coded
smoke-test nodes.  The Phase 1 builder in `instance_builder.py`
remains untouched for the namespace-smoke scope.
"""

from __future__ import annotations

import logging
from typing import Any

from asyncua import ua
from asyncua.ua.uatypes import NodeId

from .asyncua_adapter import AsyncuaAddressSpaceAdapter
from .build_planner import BuildPlan
from .model import NodeSpec


log = logging.getLogger("ua_rebuild.full_instance_builder")


def _decode(text: str) -> NodeId:
    from .type_builder import _decode as td_decode
    return td_decode(text)


def _build_qname(spec: NodeSpec) -> ua.QualifiedName:
    from .type_builder import _build_qname as tb_qname
    return tb_qname(spec)


def _build_lt(text: str | None, locale: str | None) -> ua.LocalizedText:
    from .type_builder import _build_lt as tb_lt
    return tb_lt(text, locale)


def _make_variant(raw: Any, data_type: NodeId) -> ua.Variant | None:
    from .type_builder import _make_variant as tb_var
    return tb_var(raw, data_type)


def _u8(value: int) -> ua.Byte:
    from .type_builder import _u8 as tb_u8
    return tb_u8(value)


def _make_object_attrs(spec: NodeSpec) -> ua.ObjectAttributes:
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


def _make_variable_attrs(spec: NodeSpec) -> ua.VariableAttributes:
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


class FullInstanceBuilder:
    def __init__(self, adapter: AsyncuaAddressSpaceAdapter, plan: BuildPlan) -> None:
        self.adapter = adapter
        self.plan = plan

    async def build(self) -> list:
        results = []
        for spec in self.plan.instance_nodes:
            results.extend(await self.build_one(spec))
        return results

    async def build_one(self, spec) -> list:
        if spec.reuse_existing:
            log.info("[INSTANCE] REUSE %s  cls=%s",
                     spec.node_id.text, spec.node_class)
            return []
        if spec.node_class == "Object":
            attrs = _make_object_attrs(spec)
            nc = ua.NodeClass.Object
        elif spec.node_class == "Variable":
            attrs = _make_variable_attrs(spec)
            nc = ua.NodeClass.Variable
        else:
            log.warning("[INSTANCE] skip unsupported class %s for %s",
                        spec.node_class, spec.node_id.text)
            return []

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
        log.info("[INSTANCE] %s  %s cls=%s parent=%s td=%s status=%s",
                 "OK" if record.status_code.is_good() else "FAIL",
                 spec.node_id.text, nc.name, parent_id, td_id, record.status_code)
        return [record]