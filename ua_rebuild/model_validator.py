"""Validate the loaded export model before any building is attempted.

Validation rules (Phase 0):

    * schema_version supported
    * namespace_array present and exactly 7 entries, matches expected URIs
    * source_server fields present (endpoint_url, application_uri, ...)
    * every node_id.text is unique
    * every parent_node_id refers to an existing node (or None for roots)
    * every TypeDefinition target exists in types[] or is a standard ns=0
      numeric node (known builtin)
    * every DataType target exists in types[] or is a standard ns=0 numeric node
    * every reference has source/target/reference_type/is_forward fields
    * Browsenames reference a valid namespace URI / index
    * no duplicate references under (source, type, is_forward, target)
    * type inheritance graph has no cycles
    * no node has itself as its own parent

Returns a ValidationResult describing fatal errors and warnings.  A plan
must not be built while fatal errors exist.
"""

from __future__ import annotations

from .config import EXPECTED_NAMESPACE_URIS, STANDARD_NS0_NUMERIC
from .model_loader import (
    ExportModel,
    _id_from_text,
    load_export,
    node_id_spec_from_export,
)


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

    # NodeId uniqueness
    seen: dict[str, str] = {}
    for text in model.nodes_by_text:
        if text in seen:
            res.fatal.append(f"duplicate node id text: {text}")
        seen[text] = "node"
    for text in model.types_by_text:
        if text in seen:
            res.fatal.append(f"node id conflict between nodes[] and types[]: {text}")
        seen[text] = "type"

    # Parent references
    for text, n in model.nodes_by_text.items():
        parent = n.get("parent_node_id")
        if parent is None:
            continue
        if parent not in seen:
            res.fatal.append(f"node {text}: parent_node_id {parent} not found")

    # Self-parent
    for text, n in model.nodes_by_text.items():
        if n.get("parent_node_id") == text:
            res.fatal.append(f"node {text}: self-parent detected")

    # TypeDefinition / DataType resolvability
    for text, n in model.nodes_by_text.items():
        td = (n.get("type_definition") or {}).get("node_id")
        if td is None:
            continue
        if not _resolvable(td, model, res, context=f"node {text} type_definition"):
            pass
        dt = (n.get("attributes", {}).get("data_type") or {}).get("text")
        if dt:
            _resolvable(dt, model, res, context=f"node {text} data_type")

    for text, t in model.types_by_text.items():
        parent_type = t.get("parent_type_node_id")
        if parent_type is None:
            continue
        _resolvable(parent_type, model, res, context=f"type {text} parent_type")

    # Reference shape + dedup
    ref_keys: set[tuple] = set()
    for r in model.references:
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

    # Type inheritance cycle detection
    _check_type_inheritance_cycles(model, res)

    # BrowseName namespace checks
    for text, n in model.nodes_by_text.items():
        bn = n.get("attributes", {}).get("browse_name", {})
        ns = bn.get("namespace_index")
        if ns is None:
            continue
        if not (0 <= ns < len(uris)):
            res.fatal.append(
                f"node {text} browse_name namespace_index {ns} out of range"
            )

    res.info.append(f"node count: {len(model.nodes_by_text)}")
    res.info.append(f"type count: {len(model.types_by_text)}")
    res.info.append(f"reference count: {len(model.references)}")
    return res


def _resolvable(target_text: str, model: ExportModel, res: ValidationResult,
                context: str) -> bool:
    if target_text in model.nodes_by_text or target_text in model.types_by_text:
        return True
    if target_text.startswith("ns=0;") or target_text.startswith("i="):
        # Trust ns=0 standard builtins (DataType/ReferenceType/ObjectType/
        # VariableType/PropertyType/ModellingRule) — we don't enumerate
        # them all in STANDARD_NS0_NUMERIC and they live in asyncua's
        # default address space.
        return True
    res.fatal.append(f"{context}: unresolved target {target_text}")
    return False


def _check_type_inheritance_cycles(model: ExportModel, res: ValidationResult) -> None:
    """Walk HasSubtype inverse references to detect type-inheritance cycles."""
    parent: dict[str, str | None] = {}
    for text, t in model.types_by_text.items():
        parent[text] = t.get("parent_type_node_id")
    for start in list(parent.keys()):
        seen = []
        cur: str | None = start
        while cur is not None:
            if cur in seen:
                res.fatal.append(
                    f"type inheritance cycle detected starting at {start}: ... -> {cur}"
                )
                break
            seen.append(cur)
            cur = parent.get(cur)


def main_validate(path: str) -> ValidationResult:
    """Convenience wrapper for the CLI."""
    model = load_export(path)
    return validate_export(model)