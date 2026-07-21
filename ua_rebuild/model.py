"""Structured data classes used by the rebuild pipeline.

Everything here is JSON-safe so that BuildPlanner output can be cached as
`build_plan_<scope>.json` for debugging without re-running the loader.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class NodeIdSpec:
    """Structured NodeId, mirrored from `ua_full_exporter.py`'s `node_id_dict`."""

    text: str
    namespace_index: int | None
    namespace_uri: str | None
    identifier_type: str | None
    identifier: int | str | None


@dataclass(frozen=True)
class QualifiedNameSpec:
    name: str | None
    namespace_index: int | None
    namespace_uri: str | None


@dataclass(frozen=True)
class LocalizedTextSpec:
    text: str | None
    locale: str | None


@dataclass(frozen=True)
class NodeSpec:
    """A specification for one node to be created or reused."""

    node_id: NodeIdSpec
    node_class: str
    browse_name: QualifiedNameSpec
    display_name: LocalizedTextSpec
    description: LocalizedTextSpec
    write_mask: int
    user_write_mask: int
    type_definition: NodeIdSpec | None
    parent_node_id: NodeIdSpec | None
    parent_reference_type_id: int | None  # numeric ReferenceTypeId (ns=0)
    path: str | None = None
    # Variable-only fields (None when not Variable/VariableType)
    value: dict | None = None
    data_type: NodeIdSpec | None = None
    value_rank: int | None = None
    array_dimensions: list[int] = field(default_factory=list)
    access_level: int | None = None
    user_access_level: int | None = None
    minimum_sampling_interval: float | None = None
    historizing: bool | None = None
    access_level_ex: int | None = None
    # Object-only fields (None when not Object)
    event_notifier: int | None = None
    # Type/VariableType-only fields
    is_abstract: bool | None = None
    # Declaration-only fields
    modelling_rule_node_id_text: str | None = None
    is_type_declaration: bool = False
    # Reuse flag: when True, this node already exists in the standard ns=0
    # address space and must not be created.
    reuse_existing: bool = False


@dataclass(frozen=True)
class ReferenceSpec:
    source_node_id: str
    target_node_id: str
    reference_type_node_id: str
    reference_type_id: int  # numeric (ns=0)
    reference_type_browse_name: str
    is_forward: bool
    target_node_class: str | None = None
    target_browse_name: QualifiedNameSpec | None = None


@dataclass(frozen=True)
class ValueWriteSpec:
    """An explicit value write to be applied after a node is created."""

    node_id: str
    data_value: dict
    reason: str = ""


@dataclass(frozen=True)
class BuildPlan:
    namespaces: list[str]
    reused_standard_nodes: list[NodeSpec]
    custom_type_nodes: list[NodeSpec]
    type_declaration_nodes: list[NodeSpec]
    instance_nodes: list[NodeSpec]
    node_creation_order: list[str]
    references_to_add: list[ReferenceSpec]
    expected_existing_references: list[ReferenceSpec]
    values_to_update: list[ValueWriteSpec]
    statistics: dict[str, int]
    scope: str = ""

    def to_jsonable(self) -> dict[str, Any]:
        return {
            "scope": self.scope,
            "namespaces": self.namespaces,
            "statistics": self.statistics,
            "node_creation_order": self.node_creation_order,
            "reused_standard_nodes": [_spec_to_dict(n) for n in self.reused_standard_nodes],
            "custom_type_nodes": [_spec_to_dict(n) for n in self.custom_type_nodes],
            "type_declaration_nodes": [_spec_to_dict(n) for n in self.type_declaration_nodes],
            "instance_nodes": [_spec_to_dict(n) for n in self.instance_nodes],
            "references_to_add": [_ref_to_dict(r) for r in self.references_to_add],
            "expected_existing_references": [_ref_to_dict(r) for r in self.expected_existing_references],
            "values_to_update": [v.__dict__ for v in self.values_to_update],
        }


def _spec_to_dict(spec: NodeSpec) -> dict[str, Any]:
    d: dict[str, Any] = {
        "node_id": spec.node_id.__dict__,
        "node_class": spec.node_class,
        "browse_name": spec.browse_name.__dict__,
        "display_name": spec.display_name.__dict__,
        "description": spec.description.__dict__,
        "write_mask": spec.write_mask,
        "user_write_mask": spec.user_write_mask,
        "type_definition": spec.type_definition.__dict__ if spec.type_definition else None,
        "parent_node_id": spec.parent_node_id.__dict__ if spec.parent_node_id else None,
        "parent_reference_type_id": spec.parent_reference_type_id,
        "path": spec.path,
        "value": spec.value,
        "data_type": spec.data_type.__dict__ if spec.data_type else None,
        "value_rank": spec.value_rank,
        "array_dimensions": spec.array_dimensions,
        "access_level": spec.access_level,
        "user_access_level": spec.user_access_level,
        "minimum_sampling_interval": spec.minimum_sampling_interval,
        "historizing": spec.historizing,
        "access_level_ex": spec.access_level_ex,
        "event_notifier": spec.event_notifier,
        "is_abstract": spec.is_abstract,
        "modelling_rule_node_id_text": spec.modelling_rule_node_id_text,
        "is_type_declaration": spec.is_type_declaration,
        "reuse_existing": spec.reuse_existing,
    }
    return d


def _ref_to_dict(spec: ReferenceSpec) -> dict[str, Any]:
    return {
        "source_node_id": spec.source_node_id,
        "target_node_id": spec.target_node_id,
        "reference_type_node_id": spec.reference_type_node_id,
        "reference_type_id": spec.reference_type_id,
        "reference_type_browse_name": spec.reference_type_browse_name,
        "is_forward": spec.is_forward,
        "target_node_class": spec.target_node_class,
        "target_browse_name": spec.target_browse_name.__dict__ if spec.target_browse_name else None,
    }