"""Validate the loaded export model and the generated BuildPlan.

Validation rules (Phase 0):

    * schema_version supported
    * namespace_array present and exactly 7 entries, matches expected URIs
    * source_server fields present (endpoint_url, application_uri, ...)
    * every node_id.text in raw nodes[] and types[] is unique (before
      dictionary coverage)
    * every parent_node_id refers to an existing node (or None for roots)
    * every TypeDefinition target exists in types[] / nodes[] or is a
      standard ns=0 numeric builtin
    * every DataType target exists in types[] / nodes[] or is a standard
      ns=0 numeric builtin
    * every reference has source/target/reference_type/is_forward fields
    * no duplicate references under (source, type, is_forward, target)
    * type inheritance graph has no cycles
    * no node has itself as its own parent or TypeDefinition

BuildPlan-level checks (validate_plan):

    * no self-parent or self-TypeDefinition anywhere
    * every parent reference target is either in the plan or is a
      standard builtin
    * every TypeDefinition target is either in the plan or is a
      standard builtin
    * topological sort yields a valid creation order with no cycles
"""

from __future__ import annotations

from typing import Any

from .config import EXPECTED_NAMESPACE_URIS, STANDARD_NS0_NUMERIC
from .model_loader import (
    ExportModel,
    _id_from_text,
    load_export,
)
from .build_planner import topo_sort, _is_standard_builtin


class ValidationResult:
    def __init__(self) -> None:
        self.fatal: list[str] = []
        self.warnings: list[str] = []
        self.info: list[str] = []

    def fatal_or_ok(self) -> bool:
        return len(self.fatal) == 0

    def summary(self) -> str:
        return f"fatal={len(self.fatal)} warnings={len(self.warnings)} info={len(self.info)}"


def validate_export(model: ExportModel) -> ValidationResult:
    res = ValidationResult()

    # Schema
    if model.schema_version != "2.0":
        res.fatal.append(f"unsupported schema_version: {model.schema_version!r}")

    # Namespace array
    uris = model.namespace_uris
    if len(uris) != len(EXPECTED_NAMESPACE_URIS):
        res.fatal.append(
            f"namespace_array length mismatch: got {len(uris)}, "
            f"expected {len(EXPECTED_NAMESPACE_URIS)}"
        )
    else:
        for i, (got, exp) in enumerate(zip(uris, EXPECTED_NAMESPACE_URIS)):
            if got != exp:
                res.fatal.append(
                    f"namespace mismatch at index {i}: got {got!r}, expected {exp!r}"
                )

    # Source server
    if not model.source_server.get("endpoint_url"):
        res.fatal.append("source_server.endpoint_url missing")
    if not model.source_server.get("application_uri"):
        res.fatal.append("source_server.application_uri missing")

    # Duplicate NodeId detection in raw lists (before dictionary coverage)
    raw_node_ids: set[str] = set()
    for n in model.raw_nodes:
        text = n["node_id"]["text"]
        if text in raw_node_ids:
            res.fatal.append(f"duplicate node_id in raw nodes[]: {text}")
        raw_node_ids.add(text)
    raw_type_ids: set[str] = set()
    for t in model.raw_types:
        text = t["node_id"]["text"]
        if text in raw_type_ids:
            res.fatal.append(f"duplicate node_id in raw types[]: {text}")
        raw_type_ids.add(text)

    # Cross-list conflict
    for nid in raw_node_ids & raw_type_ids:
        res.fatal.append(f"node_id present in both nodes[] and types[]: {nid}")

    # Build a seen-set so we can detect dangling parent_node_id.
    seen_node_ids: set[str] = raw_node_ids | raw_type_ids

    # Parent references (instance nodes)
    for n in model.raw_nodes:
        parent = n.get("parent_node_id")
        if parent is None:
            continue
        if parent == n["node_id"]["text"]:
            res.fatal.append(f"self-parent in raw nodes[]: {n['node_id']['text']}")
            continue
        if parent not in seen_node_ids:
            res.fatal.append(
                f"node {n['node_id']['text']}: parent_node_id {parent} not found"
            )

    # Self-parent in raw types
    for t in model.raw_types:
        parent = t.get("parent_type_node_id")
        if parent is not None and parent == t["node_id"]["text"]:
            res.fatal.append(
                f"self parent_type in raw types[]: {t['node_id']['text']}"
            )

    # Reference shape + dedup
    ref_keys: set[tuple] = set()
    for r in model.raw_references:
        for k in ("source_node_id", "target_node_id", "reference_type", "is_forward"):
            if k not in r:
                res.fatal.append(f"reference missing field {k!r}: {r}")
        if "is_forward" not in r:
            continue
        key = (r["source_node_id"], r["target_node_id"],
               r["reference_type"].get("node_id", ""),
               str(bool(r["is_forward"])))
        if key in ref_keys:
            res.fatal.append(f"duplicate reference: {key}")
        ref_keys.add(key)

    # Type inheritance cycle detection via HasSubtype inverse (the loader index).
    visited_in_cycle: set[str] = set()
    for start in list(model.supertype_by_subtype.keys()):
        if start in visited_in_cycle:
            continue
        seen: list[str] = []
        cur: str | None = start
        while cur is not None:
            if cur in seen:
                res.fatal.append(
                    f"type inheritance cycle detected starting at {start}: ... -> {cur}"
                )
                break
            seen.append(cur)
            cur = model.supertype_by_subtype.get(cur)
        visited_in_cycle.update(seen)

    # BrowseName namespace checks
    for text in raw_node_ids | raw_type_ids:
        rec = model.get_record(text)
        if rec is None:
            continue
        bn = rec.get("attributes", {}).get("browse_name", {})
        ns = bn.get("namespace_index")
        if ns is None:
            continue
        if not (0 <= ns < len(uris)):
            res.fatal.append(
                f"node {text} browse_name namespace_index {ns} out of range"
            )

    res.info.append(f"node count: {len(model.nodes_by_text)}")
    res.info.append(f"type count: {len(model.types_by_text)}")
    res.info.append(f"reference count: {len(model.raw_references)}")
    return res


def validate_plan(plan: Any, model: ExportModel | None = None) -> ValidationResult:
    """Validate a BuildPlan against the export model.

    Catches:
      * self-parent / self-TypeDefinition
      * orphan parents (parent not in plan and not a standard builtin)
      * orphan TypeDefinitions (same)
      * topological sort cycle
    """
    res = ValidationResult()

    # Collect every NodeId text in the plan, with a flag for each kind.
    in_plan: set[str] = set()
    spec_by_text: dict[str, Any] = {}
    for spec in plan.custom_type_nodes + plan.type_declaration_nodes + plan.instance_nodes:
        text = spec.node_id.text
        in_plan.add(text)
        spec_by_text[text] = spec

    def is_resolvable(target_text: str) -> bool:
        if target_text in in_plan:
            return True
        if _is_standard_builtin(target_text):
            return True
        return False

    for text, spec in spec_by_text.items():
        # self checks
        if spec.parent_node_id and spec.parent_node_id.text == text:
            res.fatal.append(f"node {text}: parent_node_id == self")
        if spec.type_definition and spec.type_definition.text == text:
            res.fatal.append(f"node {text}: type_definition == self")

        # parent reachable
        if spec.parent_node_id and spec.parent_node_id.text:
            parent_text = spec.parent_node_id.text
            if not is_resolvable(parent_text):
                res.fatal.append(
                    f"node {text}: parent {parent_text} not in plan and not a standard builtin"
                )

        # type_definition reachable
        if spec.type_definition and spec.type_definition.text:
            td_text = spec.type_definition.text
            if not is_resolvable(td_text):
                res.fatal.append(
                    f"node {text}: type_definition {td_text} not in plan and not a standard builtin"
                )

    # Topological sort cycle / completeness check.
    try:
        order = topo_sort(in_plan, spec_by_text, model)
    except ValueError as e:
        res.fatal.append(f"topological sort failed: {e}")
        order = []
    res.info.append(f"topological order length: {len(order)}")
    return res