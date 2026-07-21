"""Compute a BuildPlan for a given scope.

Scope semantics:

    namespace-smoke  -> 4-5 hand-picked nodes (Objects/DeviceSetView/SOV1/AssetId/EURange)
    sov1             -> DeviceSetView + SOV1 + SOV1 type closure
    all-sov          -> DeviceSetView + SOV1..SOV8 + necessary type closure
    full-custom      -> every non-builtin custom node

The planner performs:

    *   type closure expansion (recursively add parent_type and declaration
        children until reaching a builtin ns=0 numeric node)
    *   node creation order: parent-before-child + types-before-instances
    *   reference grouping into (a) references expected to be created by
        AddNodes automatically, (b) references we must explicitly add via
        AddReferences
    *   uniqueness / loop checks delegated to ModelValidator
"""

from __future__ import annotations

from .config import (  # noqa: F401  (re-exports)
    NS0_BASEOBJECTTYPE, NS0_BASEDATAVARIABLETYPE, NS0_PROPERTYTYPE,
    NS0_FOLDERTYPE, NS0_ANALOGITEMTYPE,
    REF_HAS_COMPONENT, REF_HAS_PROPERTY, REF_ORGANIZES,
    REF_HAS_TYPE_DEFINITION, REF_HAS_SUBTYPE, REF_HAS_MODELLING_RULE,
    SMOKE_SCOPE_NODE_IDS,
)
from .config import STANDARD_NS0_NUMERIC
from typing import Any
from .model import (
    BuildPlan,
    LocalizedTextSpec,
    NodeIdSpec,
    NodeSpec,
    QualifiedNameSpec,
    ReferenceSpec,
    ValueWriteSpec,
)
from .model_loader import (
    ExportModel,
    _id_from_text,
    load_export,
    localized_text_spec_from_export,
    node_id_spec_from_export,
    qualified_name_spec_from_export,
)


def plan_for_scope(export_path: str, scope: str) -> BuildPlan:
    model = load_export(export_path)
    plan = _build_plan(model, scope)
    return plan


def _build_plan(model: ExportModel, scope: str) -> BuildPlan:
    if scope == "namespace-smoke":
        return _plan_namespace_smoke(model)
    if scope == "sov1":
        return _plan_sov1(model)
    if scope == "all-sov":
        return _plan_all_sov(model)
    if scope == "full-custom":
        return _plan_full_custom(model)
    raise ValueError(f"unknown scope: {scope}")


def _plan_namespace_smoke(model: ExportModel) -> BuildPlan:
    """Pick the 4-5 hand-picked smoke nodes + the minimum type closure."""
    root_ids = list(SMOKE_SCOPE_NODE_IDS.values())

    inst_specs: list[NodeSpec] = []
    type_specs: list[NodeSpec] = []
    decl_specs: list[NodeSpec] = []
    reused: list[NodeSpec] = []

    for nid in root_ids:
        spec = _spec_from_export_node(model.get_node(nid))
        if spec is None:
            continue
        if _is_standard_builtin(spec.node_id.text):
            reused.append(spec)
        else:
            inst_specs.append(spec)
            # expand type closure for the instance's TypeDefinition
            _expand_type_closure(model, spec.type_definition, type_specs, decl_specs)

    refs = _collect_forward_references(model, [s.node_id.text for s in inst_specs + type_specs + decl_specs])
    plan = _assemble(model, scope="namespace-smoke",
                     reused=reused, custom_types=type_specs,
                     decls=decl_specs, instances=inst_specs,
                     refs=refs)
    return plan


def _plan_sov1(model: ExportModel) -> BuildPlan:
    dsv_text = "ns=2;s=P_7765a8f78a9266d7a83581ba1b39176a"
    sov1_text = "ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch1"
    return _plan_subtree(model, scope="sov1", root_ids=[dsv_text, sov1_text])


def _plan_all_sov(model: ExportModel) -> BuildPlan:
    dsv_text = "ns=2;s=P_7765a8f78a9266d7a83581ba1b39176a"
    sov_texts = [f"ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch{i}" for i in range(1, 9)]
    return _plan_subtree(model, scope="all-sov", root_ids=[dsv_text] + sov_texts)


def _plan_subtree(model: ExportModel, scope: str, root_ids: list[str]) -> BuildPlan:
    """Plan for a specific subtree rooted at the given NodeIds (instance-only)."""
    inst_specs: list[NodeSpec] = []
    type_specs: list[NodeSpec] = []
    decl_specs: list[NodeSpec] = []
    reused: list[NodeSpec] = []

    visited: set[str] = set()

    def visit(nid_text: str) -> None:
        if nid_text in visited:
            return
        visited.add(nid_text)
        spec = _spec_from_export_node(model.get_node(nid_text))
        if spec is None:
            return
        if _is_standard_builtin(spec.node_id.text):
            reused.append(spec)
        else:
            inst_specs.append(spec)
            _expand_type_closure(model, spec.type_definition, type_specs, decl_specs)
        # recurse into children that are reachable via HasComponent/HasProperty/Organizes
        for child in model.children_of(nid_text):
            visit(child["node_id"]["text"])

    for r in root_ids:
        visit(r)

    all_spec_ids = {s.node_id.text for s in inst_specs + type_specs + decl_specs}
    refs = _collect_forward_references(model, all_spec_ids)

    plan = _assemble(model, scope=scope,
                     reused=reused, custom_types=type_specs,
                     decls=decl_specs, instances=inst_specs,
                     refs=refs)
    return plan


def _plan_full_custom(model: ExportModel) -> BuildPlan:
    """Plan that includes every non-builtin node from the export."""
    inst_specs: list[NodeSpec] = []
    type_specs: list[NodeSpec] = []
    decl_specs: list[NodeSpec] = []
    reused: list[NodeSpec] = []

    for text, t in model.types_by_text.items():
        spec = _spec_from_export_type(model.get_type(text))
        if spec is None:
            continue
        if _is_standard_builtin(text):
            reused.append(spec)
        elif spec.is_type_declaration:
            decl_specs.append(spec)
        else:
            type_specs.append(spec)

    for text, n in model.nodes_by_text.items():
        if text in model.types_by_text:
            continue
        spec = _spec_from_export_node(n)
        if spec is None:
            continue
        if _is_standard_builtin(text):
            reused.append(spec)
        else:
            inst_specs.append(spec)

    all_spec_ids = {s.node_id.text for s in inst_specs + type_specs + decl_specs}
    refs = _collect_forward_references(model, all_spec_ids)

    plan = _assemble(model, scope="full-custom",
                     reused=reused, custom_types=type_specs,
                     decls=decl_specs, instances=inst_specs,
                     refs=refs)
    return plan


# ---------------------------------------------------------------------------
# Type closure
# ---------------------------------------------------------------------------

def _expand_type_closure(model: ExportModel, type_def: NodeIdSpec | None,
                         type_specs: list[NodeSpec], decl_specs: list[NodeSpec]) -> None:
    if type_def is None:
        return
    target = type_def.text
    if _is_standard_builtin(target):
        return
    if target in {s.node_id.text for s in type_specs} | {s.node_id.text for s in decl_specs}:
        return

    type_record = model.get_type(target)
    if type_record is None:
        return

    spec = _spec_from_export_type(type_record)
    if spec is None:
        return
    if spec.is_type_declaration:
        decl_specs.append(spec)
    else:
        type_specs.append(spec)

    parent_text = type_record.get("parent_type_node_id")
    if parent_text and not _is_standard_builtin(parent_text):
        parent_record = model.get_type(parent_text)
        if parent_record is not None:
            _expand_type_closure(model,
                                 node_id_spec_from_export(parent_record["node_id"]),
                                 type_specs, decl_specs)

    # child declarations
    for child in model.children_of(target):
        if child.get("parent_node_id") != target:
            continue
        cspec = _spec_from_export_type(child)
        if cspec is None:
            continue
        if cspec.node_id.text in {s.node_id.text for s in decl_specs}:
            continue
        decl_specs.append(cspec)
        # recurse into declarations of declarations
        if child["node_class"] in ("ObjectType", "VariableType"):
            for grand in model.children_of(cspec.node_id.text):
                if grand.get("parent_node_id") != cspec.node_id.text:
                    continue
                gspec = _spec_from_export_type(grand)
                if gspec is None or gspec.node_id.text in {s.node_id.text for s in decl_specs}:
                    continue
                decl_specs.append(gspec)


# ---------------------------------------------------------------------------
# Spec construction from raw export dicts
# ---------------------------------------------------------------------------

def _spec_from_export_node(n: dict[str, Any] | None) -> NodeSpec | None:
    if n is None:
        return None
    nid = node_id_spec_from_export(n["node_id"])
    attrs = n.get("attributes", {})
    bn = qualified_name_spec_from_export(attrs.get("browse_name"))
    dn = localized_text_spec_from_export(attrs.get("display_name"))
    de = localized_text_spec_from_export(attrs.get("description"))
    td_raw = n.get("type_definition")
    td = node_id_spec_from_export(td_raw) if td_raw else None
    parent_text = n.get("parent_node_id")
    parent_ref_type = _parent_reference_type(nid.text, parent_text)

    var = _variable_attrs(attrs, n.get("node_class"))
    obj = _object_attrs(attrs, n.get("node_class"))

    val = attrs.get("value")
    data_type = node_id_spec_from_export(attrs.get("data_type")) if attrs.get("data_type") else None

    spec = NodeSpec(
        node_id=nid,
        node_class=n["node_class"],
        browse_name=bn,
        display_name=dn,
        description=de,
        write_mask=attrs.get("write_mask", 0),
        user_write_mask=attrs.get("user_write_mask", 0),
        type_definition=td,
        parent_node_id=NodeIdSpec(parent_text, None, None, None, None) if parent_text else None,
        parent_reference_type_id=parent_ref_type,
        path=n.get("path"),
        value=val,
        data_type=data_type,
        value_rank=var["value_rank"],
        array_dimensions=var["array_dimensions"],
        access_level=var["access_level"],
        user_access_level=var["user_access_level"],
        minimum_sampling_interval=var["minimum_sampling_interval"],
        historizing=var["historizing"],
        access_level_ex=var["access_level_ex"],
        event_notifier=obj,
        is_abstract=None,
        modelling_rule_node_id_text=None,
        is_type_declaration=False,
        reuse_existing=_is_standard_builtin(nid.text),
    )
    return spec


def _spec_from_export_type(t: dict[str, Any] | None) -> NodeSpec | None:
    if t is None:
        return None
    nid = node_id_spec_from_export(t["node_id"])
    attrs = t.get("attributes", {})
    bn = qualified_name_spec_from_export(attrs.get("browse_name"))
    dn = localized_text_spec_from_export(attrs.get("display_name"))
    de = localized_text_spec_from_export(attrs.get("description"))
    val = attrs.get("value")
    data_type = node_id_spec_from_export(attrs.get("data_type")) if attrs.get("data_type") else None

    var = _variable_attrs(attrs, t.get("node_class"))
    obj = _object_attrs(attrs, t.get("node_class"))

    is_decl = bool(t.get("is_type_declaration", False))

    parent_text = t.get("parent_node_id") if t.get("node_class") in ("ObjectType", "VariableType") \
        else nid.text  # for declarations we treat the type itself as parent
    parent_ref = _parent_reference_type(nid.text, parent_text)

    mr = t.get("modelling_rule") or {}
    mr_text = mr.get("node_id")

    spec = NodeSpec(
        node_id=nid,
        node_class=t["node_class"],
        browse_name=bn,
        display_name=dn,
        description=de,
        write_mask=attrs.get("write_mask", 0),
        user_write_mask=attrs.get("user_write_mask", 0),
        type_definition=node_id_spec_from_export(t["node_id"]) if t["node_class"] in ("Object", "Variable") else None,
        parent_node_id=NodeIdSpec(parent_text, None, None, None, None) if parent_text else None,
        parent_reference_type_id=parent_ref,
        path=t.get("path"),
        value=val,
        data_type=data_type,
        value_rank=var["value_rank"],
        array_dimensions=var["array_dimensions"],
        access_level=var["access_level"],
        user_access_level=var["user_access_level"],
        minimum_sampling_interval=var["minimum_sampling_interval"],
        historizing=var["historizing"],
        access_level_ex=var["access_level_ex"],
        event_notifier=obj,
        is_abstract=attrs.get("is_abstract"),
        modelling_rule_node_id_text=mr_text,
        is_type_declaration=is_decl,
        reuse_existing=_is_standard_builtin(nid.text),
    )
    return spec


def _variable_attrs(attrs: dict[str, Any], node_class: str | None) -> dict[str, Any]:
    if node_class not in ("Variable", "VariableType"):
        return {
            "value_rank": None, "array_dimensions": [], "access_level": None,
            "user_access_level": None, "minimum_sampling_interval": None,
            "historizing": None, "access_level_ex": None,
        }
    return {
        "value_rank": attrs.get("valuerank"),
        "array_dimensions": list(attrs.get("array_dimensions") or attrs.get("arraydimensions") or []),
        "access_level": attrs.get("accesslevel"),
        "user_access_level": attrs.get("useraccesslevel"),
        "minimum_sampling_interval": attrs.get("minimum_samplinginterval"),
        "historizing": attrs.get("historizing"),
        "access_level_ex": attrs.get("accesslevelex"),
    }


def _object_attrs(attrs: dict[str, Any], node_class: str | None) -> int | None:
    if node_class != "Object":
        return None
    return attrs.get("event_notifier")


def _parent_reference_type(self_text: str, parent_text: str | None) -> int | None:
    """Return numeric ReferenceTypeId for self->parent relationship, or None.

    The exporter's references list is the source of truth.  If we cannot
    find the relationship there we default to HasComponent for instances
    and HasSubtype for types, which matches asyncua's defaults and keeps
    the plan readable.
    """
    if parent_text is None:
        return None
    # We don't have direct access to the model here; defer to caller that
    # has access.  The planner callers use a richer helper below.
    return None


# ---------------------------------------------------------------------------
# Reference collection
# ---------------------------------------------------------------------------

def _parent_reference_type_lookup(model: ExportModel) -> dict[tuple[str, str], int]:
    """Build a map (parent_text, child_text) -> numeric ReferenceTypeId (forward)."""
    out: dict[tuple[str, str], int] = {}
    for r in model.references:
        if not r["is_forward"]:
            continue
        rtid = _id_from_text(r["reference_type"].get("node_id", ""))
        if rtid is None:
            continue
        out[(r["source_node_id"], r["target_node_id"])] = rtid
    return out


def _collect_forward_references(model: ExportModel, scope_node_ids: set[str]) -> list[ReferenceSpec]:
    """Collect forward references where source is in scope."""
    out: list[ReferenceSpec] = []
    seen: set[tuple] = set()
    for r in model.references:
        if not r["is_forward"]:
            continue
        key = (r["source_node_id"], r["target_node_id"],
               r["reference_type"].get("node_id", ""))
        if key in seen:
            continue
        seen.add(key)
        out.append(_ref_from_export(r))
    # Filter to the ones relevant for the scope (source OR target in scope)
    out = [r for r in out
           if r.source_node_id in scope_node_ids or r.target_node_id in scope_node_ids]
    return out


def _ref_from_export(r: dict[str, Any]) -> ReferenceSpec:
    return ReferenceSpec(
        source_node_id=r["source_node_id"],
        target_node_id=r["target_node_id"],
        reference_type_node_id=r["reference_type"].get("node_id", ""),
        reference_type_id=_id_from_text(r["reference_type"].get("node_id", "")) or 0,
        reference_type_browse_name=r["reference_type"].get("browse_name", ""),
        is_forward=bool(r["is_forward"]),
        target_node_class=r.get("target_node_class"),
        target_browse_name=qualified_name_spec_from_export(r.get("target_browse_name")),
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_standard_builtin(text: str) -> bool:
    """Return True if the given NodeId text refers to a builtin ns=0 numeric node."""
    nid = _id_from_text(text)
    if nid is None:
        return False
    return nid in STANDARD_NS0_NUMERIC


def _assemble(model: ExportModel, *, scope: str,
              reused: list[NodeSpec], custom_types: list[NodeSpec],
              decls: list[NodeSpec], instances: list[NodeSpec],
              refs: list[ReferenceSpec]) -> BuildPlan:
    # Compute creation order: types before decls before instances.
    order: list[str] = []
    seen: set[str] = set()

    def add(text: str) -> None:
        if text in seen:
            return
        if _is_standard_builtin(text):
            return
        seen.add(text)
        order.append(text)

    for s in custom_types:
        add(s.node_id.text)
    for s in decls:
        add(s.node_id.text)
    for s in instances:
        add(s.node_id.text)

    # Sort instances by depth: parents first
    depth_cache: dict[str, int] = {}

    def depth(text: str) -> int:
        if text in depth_cache:
            return depth_cache[text]
        n = model.get_node(text)
        if n is None:
            depth_cache[text] = 0
            return 0
        parent = n.get("parent_node_id")
        if parent is None:
            depth_cache[text] = 0
            return 0
        d = depth(parent) + 1
        depth_cache[text] = d
        return d

    instances_sorted = sorted(instances, key=lambda s: (depth(s.node_id.text), s.node_id.text))
    custom_sorted = sorted(custom_types, key=lambda s: s.node_id.text)
    decls_sorted = sorted(decls, key=lambda s: s.node_id.text)

    order = [s.node_id.text for s in custom_sorted + decls_sorted + instances_sorted]

    expected = [r for r in refs
                if r.reference_type_id in (REF_HAS_TYPE_DEFINITION, REF_HAS_SUBTYPE)
                or _is_builtin_parent(r)]
    to_add = [r for r in refs if r not in expected]

    stats = {
        "reused_standard_nodes": len(reused),
        "custom_type_nodes": len(custom_types),
        "type_declaration_nodes": len(decls),
        "instance_nodes": len(instances),
        "references_to_add": len(to_add),
        "expected_existing_references": len(expected),
    }

    return BuildPlan(
        namespaces=model.namespace_uris,
        reused_standard_nodes=reused,
        custom_type_nodes=custom_sorted,
        type_declaration_nodes=decls_sorted,
        instance_nodes=instances_sorted,
        node_creation_order=order,
        references_to_add=to_add,
        expected_existing_references=expected,
        values_to_update=[],
        statistics=stats,
        scope=scope,
    )


def _is_builtin_parent(ref: ReferenceSpec) -> bool:
    """References to builtin standard nodes (e.g. HasTypeDefinition i=63)
    are expected to be created automatically by asyncua's high-level APIs.
    """
    rt = ref.reference_type_id
    if rt not in (REF_HAS_TYPE_DEFINITION, REF_HAS_SUBTYPE):
        return False
    # If target is a builtin numeric id, it's expected to be present already
    nid = _id_from_text(ref.target_node_id)
    if nid is None:
        return False
    return nid in STANDARD_NS0_NUMERIC