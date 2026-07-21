"""Compute a BuildPlan for a given scope.

Scope semantics:

    namespace-smoke  -> Objects + DeviceSetView + SOV1 + AssetId + EURange +
                        full ancestor/descendant closure for each anchor
    sov1             -> Objects + DeviceSetView + SOV1 + SOV1 subtree only
                        (NEVER SOV2-SOV8)
    all-sov          -> Objects + DeviceSetView + SOV1..SOV8 + necessary type closure
    full-custom      -> every non-builtin custom node from the export

The planner performs:

    *   type closure expansion via reference indices
        (NOT instance children_by_parent).
    *   ancestor closure expansion via parent_reference_by_child.
    *   NodeSpec parent_node_id derived from references (HasComponent /
        HasProperty / Organizes / HasSubtype) for every node.
    *   creation order: topological sort by real dependencies (parent
        instance, parent type, declaration owner, TypeDefinition), never
        by NodeId string comparison.
    *   reference grouping: AddNodes-implied references vs. references
        we must explicitly add via AddReferences.

`_is_standard_builtin()` deliberately accepts ONLY `ns=0` numeric
NodeIds, so custom namespaces such as `ns=2;i=85` are NEVER mistakenly
treated as builtins.
"""

from __future__ import annotations

from collections import deque
from typing import Any

from .config import (
    EXPECTED_NAMESPACE_URIS,
    NS0_BASEOBJECTTYPE,
    NS0_BASEDATAVARIABLETYPE,
    NS0_PROPERTYTYPE,
    NS0_FOLDERTYPE,
    NS0_ANALOGITEMTYPE,
    NS0_OBJECTS,
    REF_HAS_COMPONENT,
    REF_HAS_PROPERTY,
    REF_ORGANIZES,
    REF_HAS_TYPE_DEFINITION,
    REF_HAS_SUBTYPE,
    REF_HAS_MODELLING_RULE,
    SMOKE_SCOPE_NODE_IDS,
    STANDARD_NS0_NUMERIC,
)
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
    ExportModel as _ExportModel,  # noqa: F401  (re-export)
    _id_from_text,
    load_export,
    localized_text_spec_from_export,
    node_id_spec_from_export,
    node_id_spec_from_text,
    qualified_name_spec_from_export,
)


# Smoke test scope: 5 hand-picked NodeIds that prove multi-namespace binding.
# Each entry maps a key to the exported node's text id.
SMOKE_NODE_IDS: list[str] = list(SMOKE_SCOPE_NODE_IDS.values())


def plan_for_scope(export_path: str, scope: str) -> BuildPlan:
    model = load_export(export_path)
    return _build_plan(model, scope)


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


# ---------------------------------------------------------------------------
# Per-scope planners
# ---------------------------------------------------------------------------

def _plan_namespace_smoke(model: ExportModel) -> BuildPlan:
    """Pick the 5 hand-picked smoke nodes + full ancestor closure.

    Selecting EURange must pull in Current, Runtime, SOV1, DeviceSetView,
    Objects.
    """
    selected = _collect_with_closure(model, SMOKE_NODE_IDS, include_descendants=False)
    # Always include the root so the model has somewhere to attach.
    selected.add(_text(NS0_OBJECTS))
    return _build_plan_from_selected(model, "namespace-smoke", selected)


def _plan_sov1(model: ExportModel) -> BuildPlan:
    """SOV1 subtree ONLY — never SOV2..SOV8.

    Anchor = SOV1.  Ancestor closure pulls in DeviceSetView + Objects.
    Descendant closure pulls in AssetId, Configuration, Runtime, etc.
    """
    sov1_text = "ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch1"
    selected = _collect_with_closure(model, [sov1_text], include_descendants=True)
    selected.add(_text(NS0_OBJECTS))  # always include root
    return _build_plan_from_selected(model, "sov1", selected)


def _plan_all_sov(model: ExportModel) -> BuildPlan:
    """All 8 SOVs with their subtrees."""
    sov_texts = [f"ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch{i}" for i in range(1, 9)]
    selected = _collect_with_closure(model, sov_texts, include_descendants=True)
    dsv_text = "ns=2;s=P_7765a8f78a9266d7a83581ba1b39176a"
    selected.add(dsv_text)
    selected.add(_text(NS0_OBJECTS))
    return _build_plan_from_selected(model, "all-sov", selected)


def _plan_full_custom(model: ExportModel) -> BuildPlan:
    """Every non-builtin custom node from the export."""
    selected: set[str] = set()
    for text in model.nodes_by_text:
        if not _is_standard_builtin(text):
            selected.add(text)
    for text in model.types_by_text:
        if not _is_standard_builtin(text):
            selected.add(text)
    selected.add(_text(NS0_OBJECTS))
    return _build_plan_from_selected(model, "full-custom", selected)


# ---------------------------------------------------------------------------
# Closure computation
# ---------------------------------------------------------------------------

def _collect_with_closure(model: ExportModel, anchors: list[str],
                         include_descendants: bool) -> set[str]:
    """Walk anchors + ancestors (+ optional descendants) and return selected ids.

    Implementation note: ancestor and descendant collection are kept
    strictly separate.  Walking up to an ancestor MUST NOT pull in the
    ancestor's other children — that is what made the previous
    implementation incorrectly include SOV2..SOV8 in the `sov1` scope.
    """
    selected: set[str] = set()
    ancestors: set[str] = set()
    for anchor in anchors:
        cur: str | None = anchor
        while cur is not None:
            if cur in ancestors:
                break
            ancestors.add(cur)
            parent_info = model.parent_reference_by_child.get(cur)
            cur = parent_info[0] if parent_info else None
    selected.update(ancestors)

    if include_descendants:
        for anchor in anchors:
            _collect_descendants(model, anchor, selected)
    return selected


def _collect_descendants(model: ExportModel, nid: str, selected: set[str]) -> None:
    for child_text in model.children_of(nid):
        if child_text in selected:
            continue
        selected.add(child_text)
        _collect_descendants(model, child_text, selected)


def _build_plan_from_selected(model: ExportModel, scope: str,
                              selected: set[str]) -> BuildPlan:
    """Materialize NodeSpecs from the selected set and assemble the BuildPlan."""
    inst_specs: list[NodeSpec] = []
    type_specs: list[NodeSpec] = []
    decl_specs: list[NodeSpec] = []
    reused: list[NodeSpec] = []

    # 1. instances
    for nid in sorted(selected):
        rec = model.nodes_by_text.get(nid)
        if rec is None:
            continue
        spec = _make_instance_spec(model, rec)
        if spec is None:
            continue
        if spec.reuse_existing:
            reused.append(spec)
        else:
            inst_specs.append(spec)

    # 2. type closure (uses reference indices, never instance children).
    # `visited` is shared across all instance closures so two instances
    # pointing at the same TypeDefinition only add the type once.
    visited_types: set[str] = set()
    visited_decls: set[str] = set()
    for spec in list(inst_specs):
        if spec.type_definition is not None:
            _expand_type_closure(model, spec.type_definition,
                                 type_specs, decl_specs,
                                 visited_types, visited_decls)

    # 3. De-duplicate spec lists (preserving order) — a single type may
    # have been reached via multiple parents.
    type_specs = _dedupe_specs(type_specs)
    decl_specs = _dedupe_specs(decls_specs := decl_specs) if False else decl_specs
    decl_specs = _dedupe_specs(decl_specs)

    # 4. Topologically sort creation order across ALL plan nodes
    # (instances + types + declarations), not just the instance closure.
    all_specs: dict[str, NodeSpec] = {}
    for s in inst_specs + type_specs + decl_specs:
        all_specs[s.node_id.text] = s
    full_selected: set[str] = selected | set(all_specs.keys())
    creation_order = topo_sort(full_selected, all_specs, model)

    # 5. References among selected nodes
    refs = _collect_forward_references(model, full_selected)

    return _assemble(model, scope=scope,
                     reused=reused, custom_types=type_specs,
                     decls=decl_specs, instances=inst_specs,
                     refs=refs, creation_order=creation_order)


def _dedupe_specs(specs: list[NodeSpec]) -> list[NodeSpec]:
    seen: set[str] = set()
    out: list[NodeSpec] = []
    for s in specs:
        if s.node_id.text in seen:
            continue
        seen.add(s.node_id.text)
        out.append(s)
    return out


# ---------------------------------------------------------------------------
# Type closure (uses reference indices, NOT instance children)
# ---------------------------------------------------------------------------

def _expand_type_closure(model: ExportModel, type_def: NodeIdSpec | None,
                         type_specs: list[NodeSpec],
                         decl_specs: list[NodeSpec],
                         visited_types: set[str] | None = None,
                         visited_decls: set[str] | None = None) -> None:
    if type_def is None:
        return
    target = type_def.text
    # Normalize to the canonical key the loader uses (always `ns=0;i=N` for
    # standard numeric NodeIds, never the bare `i=N` form).
    canonical = _canonical_node_id_text(target)
    if visited_types is None:
        visited_types = set()
    if visited_decls is None:
        visited_decls = set()

    # For declarations, we need a separate visited set so that two
    # instances whose TypeDefinitions share a common sub-type do not
    # duplicate work.
    is_target_decl = False
    type_record = model.types_by_text.get(canonical)
    if type_record is not None and type_record.get("is_type_declaration"):
        is_target_decl = True
        if canonical in visited_decls:
            return
        visited_decls.add(canonical)
    else:
        if canonical in visited_types:
            return
        visited_types.add(canonical)

    if type_record is None:
        return

    spec = _make_type_spec(model, type_record)
    if spec is None:
        return

    if spec.is_type_declaration:
        decl_specs.append(spec)
    else:
        type_specs.append(spec)

    # Recurse into parent type (via HasSubtype inverse from the index).
    supertype_text = model.supertype_by_subtype.get(canonical)
    if supertype_text:
        supertype_record = model.types_by_text.get(supertype_text)
        if supertype_record is not None:
            _expand_type_closure(model,
                                 node_id_spec_from_export(supertype_record["node_id"]),
                                 type_specs, decl_specs,
                                 visited_types, visited_decls)

    # Recurse into declarations owned by this type.
    if not is_target_decl:
        for decl_text in model.declarations_by_owner.get(canonical, []):
            if decl_text in visited_decls:
                continue
            decl_record = model.types_by_text.get(decl_text)
            if decl_record is None:
                continue
            dspec = _make_type_spec(model, decl_record)
            if dspec is not None:
                decl_specs.append(dspec)
                visited_decls.add(decl_text)
            # declarations may themselves have a TypeDefinition that needs
            # to be in the plan (FunctionalGroupType, AnalogItemType, etc.)
            decl_td_text = model.type_definition_by_node.get(decl_text)
            if decl_td_text:
                decl_td_canonical = _canonical_node_id_text(decl_td_text)
                decl_td_record = model.types_by_text.get(decl_td_canonical)
                if decl_td_record is not None:
                    _expand_type_closure(model,
                                         node_id_spec_from_export(decl_td_record["node_id"]),
                                         type_specs, decl_specs,
                                         visited_types, visited_decls)


def _canonical_node_id_text(text: str) -> str:
    """Convert a NodeId text to the canonical form used by the loader.

    The exporter (and the loader) always stores standard ns=0 numeric
    NodeIds as `ns=0;i=N`.  Bare `i=N` is normalized to that form so
    dictionary lookups succeed.
    """
    if not text:
        return text
    if text.startswith("i=") and ";" not in text:
        return f"ns=0;{text}"
    return text


# ---------------------------------------------------------------------------
# NodeSpec construction
# ---------------------------------------------------------------------------

def _make_instance_spec(model: ExportModel, n: dict[str, Any]) -> NodeSpec | None:
    """Build a NodeSpec for an instance node (Object/Variable/Method)."""
    nid_text = n["node_id"]["text"]
    nid = node_id_spec_from_export(n["node_id"])
    attrs = n.get("attributes", {})
    bn = qualified_name_spec_from_export(attrs.get("browse_name"))
    dn = localized_text_spec_from_export(attrs.get("display_name"))
    de = localized_text_spec_from_export(attrs.get("description"))

    parent_info = model.parent_reference_by_child.get(nid_text)
    parent_text = parent_info[0] if parent_info else None
    parent_ref_id = parent_info[1] if parent_info else None

    td_text = model.type_definition_by_node.get(nid_text)
    td = node_id_spec_from_text(td_text) if td_text else None

    if parent_text == nid_text:
        raise ValueError(f"self-parent detected in raw export: {nid_text}")

    var = _variable_attrs(attrs, n.get("node_class"))
    obj = _object_attrs(attrs, n.get("node_class"))

    return NodeSpec(
        node_id=nid,
        node_class=n["node_class"],
        browse_name=bn,
        display_name=dn,
        description=de,
        write_mask=attrs.get("write_mask", 0),
        user_write_mask=attrs.get("user_write_mask", 0),
        type_definition=td,
        parent_node_id=NodeIdSpec(text=parent_text, namespace_index=None,
                                   namespace_uri=None, identifier_type=None,
                                   identifier=None) if parent_text else None,
        parent_reference_type_id=parent_ref_id,
        path=n.get("path"),
        value=attrs.get("value"),
        data_type=node_id_spec_from_text(attrs["data_type"]["text"])
            if attrs.get("data_type") and attrs["data_type"].get("text") else None,
        value_rank=var["value_rank"],
        array_dimensions=var["array_dimensions"],
        access_level=var["access_level"],
        user_access_level=var["user_access_level"],
        minimum_sampling_interval=var["minimum_sampling_interval"],
        historizing=var["historizing"],
        access_level_ex=var["access_level_ex"],
        event_notifier=obj,
        is_abstract=None,
        modelling_rule_node_id_text=model.modelling_rule_by_node.get(nid_text),
        is_type_declaration=False,
        reuse_existing=_is_standard_builtin(nid_text),
    )


def _make_type_spec(model: ExportModel, t: dict[str, Any]) -> NodeSpec | None:
    """Build a NodeSpec for a type node (ObjectType/VariableType) or a
    type declaration (Object/Variable living inside a type).

    Standard builtins are emitted with `reuse_existing=True` so the plan
    records the dependency; Phase 1's builder will skip creation.
    Declarations of standard builtins (Mandatory/Optional/...) are skipped
    entirely because asyncua already provides them in the default address
    space.
    """
    nid_text = t["node_id"]["text"]
    is_standard = _is_standard_builtin(nid_text)
    is_decl = bool(t.get("is_type_declaration", False))
    if is_standard and is_decl:
        return None

    nid = node_id_spec_from_export(t["node_id"])
    attrs = t.get("attributes", {})
    bn = qualified_name_spec_from_export(attrs.get("browse_name"))
    dn = localized_text_spec_from_export(attrs.get("display_name"))
    de = localized_text_spec_from_export(attrs.get("description"))

    is_decl = bool(t.get("is_type_declaration", False))
    var = _variable_attrs(attrs, t.get("node_class"))
    obj = _object_attrs(attrs, t.get("node_class"))

    if is_decl:
        # declaration: parent is the owning type (HasComponent/HasProperty source)
        parent_info = model.parent_reference_by_child.get(nid_text)
        parent_text = parent_info[0] if parent_info else None
        parent_ref_id = parent_info[1] if parent_info else None
        td_text = model.type_definition_by_node.get(nid_text)
        td = node_id_spec_from_text(td_text) if td_text else None
        mr_text = model.modelling_rule_by_node.get(nid_text)
    else:
        # type node: parent is its supertype (HasSubtype inverse)
        parent_text = model.supertype_by_subtype.get(nid_text)
        parent_ref_id = REF_HAS_SUBTYPE
        td = None
        mr_text = None

    if parent_text == nid_text:
        raise ValueError(f"self-parent detected for type node: {nid_text}")
    if td is not None and td.text == nid_text:
        raise ValueError(f"self-TypeDefinition detected for node: {nid_text}")

    return NodeSpec(
        node_id=nid,
        node_class=t["node_class"],
        browse_name=bn,
        display_name=dn,
        description=de,
        write_mask=attrs.get("write_mask", 0),
        user_write_mask=attrs.get("user_write_mask", 0),
        type_definition=td,
        parent_node_id=NodeIdSpec(text=parent_text, namespace_index=None,
                                   namespace_uri=None, identifier_type=None,
                                   identifier=None) if parent_text else None,
        parent_reference_type_id=parent_ref_id,
        path=t.get("path"),
        value=attrs.get("value"),
        data_type=node_id_spec_from_text(attrs["data_type"]["text"])
            if attrs.get("data_type") and attrs["data_type"].get("text") else None,
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
        reuse_existing=is_standard,
    )


def _variable_attrs(attrs: dict[str, Any], node_class: str | None) -> dict[str, Any]:
    """Normalize the exporter's lowercase / mixed-case attribute keys.

    asyncua's read_attribute() returns attributes keyed by their attribute
    id names.  The exporter preserves those names verbatim, so a Variable's
    attribute dict contains both `access_level` (normalized by the exporter)
    and `minimumsamplinginterval` (verbatim from asyncua).  We normalize
    everything to underscored Python-friendly keys so downstream code does
    not have to know about asyncua's quirky naming.
    """
    if node_class not in ("Variable", "VariableType"):
        return {
            "value_rank": None, "array_dimensions": [], "access_level": None,
            "user_access_level": None, "minimum_sampling_interval": None,
            "historizing": None, "access_level_ex": None,
        }
    array_dimensions = attrs.get("array_dimensions") or attrs.get("arraydimensions") or []
    try:
        array_dimensions = [int(x) for x in array_dimensions]
    except Exception:
        array_dimensions = []
    return {
        "value_rank": _maybe_int(attrs.get("valuerank") or attrs.get("value_rank")),
        "array_dimensions": array_dimensions,
        "access_level": _maybe_int(attrs.get("accesslevel") or attrs.get("access_level")),
        "user_access_level": _maybe_int(attrs.get("useraccesslevel") or attrs.get("user_access_level")),
        "minimum_sampling_interval": attrs.get("minimumsamplinginterval")
            if attrs.get("minimumsamplinginterval") is not None
            else attrs.get("minimum_sampling_interval"),
        "historizing": attrs.get("historizing"),
        "access_level_ex": attrs.get("accesslevelex")
            if attrs.get("accesslevelex") is not None
            else attrs.get("access_level_ex"),
    }


def _object_attrs(attrs: dict[str, Any], node_class: str | None) -> int | None:
    if node_class != "Object":
        return None
    return _maybe_int(attrs.get("event_notifier"))


def _maybe_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Topological sort (real dependency graph, not NodeId string order)
# ---------------------------------------------------------------------------

def topo_sort(selected: set[str], specs: dict[str, NodeSpec],
              model: ExportModel | None) -> list[str]:
    """Return creation order honoring real dependencies.

    Dependency edges:

        instance -> its parent instance
        instance -> its TypeDefinition
        type     -> its supertype
        decl     -> its owner type
        decl     -> its TypeDefinition
    """
    deps: dict[str, set[str]] = {nid: set() for nid in selected}

    def add_dep(child: str, parent: str | None) -> None:
        if not parent or parent not in selected or parent == child:
            return
        deps[child].add(parent)

    for nid, spec in specs.items():
        if nid not in selected:
            continue
        # parent
        if spec.parent_node_id and spec.parent_node_id.text:
            add_dep(nid, spec.parent_node_id.text)
        # type_definition
        if spec.type_definition and spec.type_definition.text:
            add_dep(nid, spec.type_definition.text)

    if model is not None:
        for nid in list(selected):
            # supertype edge for type nodes
            supertype = model.supertype_by_subtype.get(nid)
            if supertype:
                add_dep(nid, supertype)

    in_degree: dict[str, int] = {nid: len(d) for nid, d in deps.items()}
    edges: dict[str, list[str]] = {nid: [] for nid in selected}
    for nid, dset in deps.items():
        for dep in dset:
            edges[dep].append(nid)

    queue: deque[str] = deque(nid for nid, deg in in_degree.items() if deg == 0)
    order: list[str] = []
    while queue:
        nid = queue.popleft()
        order.append(nid)
        for child in edges[nid]:
            in_degree[child] -= 1
            if in_degree[child] == 0:
                queue.append(child)

    if len(order) != len(selected):
        cycle = sorted(nid for nid, deg in in_degree.items() if deg > 0)
        raise ValueError(f"cycle detected: {cycle[:5]}{'...' if len(cycle) > 5 else ''}")
    return order


# ---------------------------------------------------------------------------
# Reference collection
# ---------------------------------------------------------------------------

def _collect_forward_references(model: ExportModel,
                                scope_node_ids: set[str]) -> list[ReferenceSpec]:
    out: list[ReferenceSpec] = []
    seen: set[tuple] = set()
    for r in model.raw_references:
        if not r.get("is_forward"):
            continue
        src = r["source_node_id"]
        tgt = r["target_node_id"]
        if src not in scope_node_ids and tgt not in scope_node_ids:
            continue
        key = (src, tgt, r["reference_type"].get("node_id", ""))
        if key in seen:
            continue
        seen.add(key)
        out.append(ReferenceSpec(
            source_node_id=src,
            target_node_id=tgt,
            reference_type_node_id=r["reference_type"].get("node_id", ""),
            reference_type_id=_id_from_text(r["reference_type"].get("node_id", "")) or 0,
            reference_type_browse_name=r["reference_type"].get("browse_name", ""),
            is_forward=True,
            target_node_class=r.get("target_node_class"),
            target_browse_name=qualified_name_spec_from_export(r.get("target_browse_name")),
        ))
    return out


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_standard_builtin(text: str) -> bool:
    """Return True ONLY for genuine standard ns=0 numeric NodeIds.

    The OPC UA spec reserves ns=0 numeric NodeIds below ~30k for built-in
    ObjectTypes, VariableTypes, ReferenceTypes, DataTypes and well-known
    instance nodes (Objects, FolderType, etc.).  Anything with `ns!=0`,
    or any string / guid / bytestring identifier, is ALWAYS treated as
    custom — even when the identifier matches a builtin integer by
    coincidence (e.g. `ns=2;i=85` or `ns=4;i=68`).

    Phase 0 trusts the full ns=0 numeric namespace; Phase 1 confirms
    every reused node via `node_exists` + NodeClass check at build time.
    """
    if not text:
        return False
    if text.startswith("i="):
        if ";" in text:
            return False
    elif text.startswith("ns=0;i="):
        pass
    else:
        return False
    nid = _id_from_text(text)
    return nid is not None


def _text(numeric_id: int) -> str:
    """Format a standard ns=0 numeric NodeId as `i=N`."""
    return f"i={numeric_id}"


def _assemble(model: ExportModel, *, scope: str,
              reused: list[NodeSpec], custom_types: list[NodeSpec],
              decls: list[NodeSpec], instances: list[NodeSpec],
              refs: list[ReferenceSpec],
              creation_order: list[str]) -> BuildPlan:
    expected = [r for r in refs
                if r.reference_type_id in (REF_HAS_TYPE_DEFINITION, REF_HAS_SUBTYPE)
                and _is_standard_builtin(r.target_node_id)]
    to_add = [r for r in refs if r not in expected]

    stats = {
        "reused_standard_nodes": len(reused),
        "custom_type_nodes": len(custom_types),
        "type_declaration_nodes": len(decls),
        "instance_nodes": len(instances),
        "references_to_add": len(to_add),
        "expected_existing_references": len(expected),
        "creation_order_length": len(creation_order),
    }

    return BuildPlan(
        namespaces=model.namespace_uris,
        reused_standard_nodes=reused,
        custom_type_nodes=custom_types,
        type_declaration_nodes=decls,
        instance_nodes=instances,
        node_creation_order=creation_order,
        references_to_add=to_add,
        expected_existing_references=expected,
        values_to_update=[],
        statistics=stats,
        scope=scope,
    )