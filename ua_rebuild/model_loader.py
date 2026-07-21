"""Load `real_server_export_v2.json` into typed structures.

The loader is read-only and never mutates the export file.  Derived
build plans may be persisted as `build_plan_<scope>.json` but the source
JSON is treated as immutable input.

The loader also builds several reference-derived indices that the
BuildPlanner and ModelValidator rely on:

    * parent_reference_by_child           child -> (parent, ref_type_id)
                                          forward HasComponent / HasProperty /
                                          Organizes only.
    * type_definition_by_node             node -> type_definition NodeId text
    * supertype_by_subtype                subtype -> supertype NodeId text
                                          (HasSubtype inverse)
    * modelling_rule_by_node              declaration -> modelling_rule text
    * declaration_owner_by_node           declaration -> owning type
                                          (= parent_reference_by_child entry
                                          when the parent is a type node)
    * declarations_by_owner               type -> [declaration_node_ids]
    * children_by_parent                  parent -> [child_node_ids]
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .model import (
    LocalizedTextSpec,
    NodeIdSpec,
    QualifiedNameSpec,
)


# ReferenceType numeric identifiers in ns=0 (from OPC UA spec).
REF_ORGANIZES = 35
REF_HAS_TYPE_DEFINITION = 40
REF_HAS_SUBTYPE = 45
REF_HAS_PROPERTY = 46
REF_HAS_COMPONENT = 47
REF_HAS_MODELLING_RULE = 37

HIERARCHICAL_REF_TYPES = (REF_ORGANIZES, REF_HAS_PROPERTY, REF_HAS_COMPONENT)


class ExportModel:
    """In-memory representation of the export, indexed for fast lookup."""

    def __init__(self, raw: dict[str, Any]) -> None:
        self.raw = raw
        self.schema_version: str = raw.get("schema_version", "")
        self.source_server: dict[str, Any] = raw.get("source_server", {})
        self.namespace_array: list[dict[str, Any]] = list(raw.get("namespace_array", []))
        self.roots: list[dict[str, Any]] = list(raw.get("roots", []))
        self.errors: list[dict[str, Any]] = list(raw.get("errors", []))

        # Raw list snapshots for duplicate-detection in the validator.
        self.raw_nodes: list[dict[str, Any]] = list(raw.get("nodes", []))
        self.raw_types: list[dict[str, Any]] = list(raw.get("types", []))
        self.raw_references: list[dict[str, Any]] = list(raw.get("references", []))

        # NodeId -> record (covers both instances and types).
        self.nodes_by_text: dict[str, dict[str, Any]] = {}
        self.types_by_text: dict[str, dict[str, Any]] = {}

        for n in self.raw_nodes:
            self.nodes_by_text[n["node_id"]["text"]] = n
        for t in self.raw_types:
            self.types_by_text[t["node_id"]["text"]] = t

        # Reference-derived indices.
        self.parent_reference_by_child: dict[str, tuple[str, int]] = {}
        self.type_definition_by_node: dict[str, str] = {}
        self.supertype_by_subtype: dict[str, str] = {}
        self.modelling_rule_by_node: dict[str, str] = {}
        self.children_by_parent: dict[str | None, list[str]] = {}
        self._build_indices()

        # Indices derived from the type declarations (post-pass).
        self.declaration_owner_by_node: dict[str, str] = {}
        self.declaration_parent_reference_by_node: dict[str, int] = {}
        self.declarations_by_owner: dict[str, list[str]] = {}
        self._build_declaration_indices()

    # ---------------- index construction ----------------

    def _build_indices(self) -> None:
        """Walk the reference list once and populate the base indices."""
        for r in self.raw_references:
            try:
                rtid = _id_from_text(r["reference_type"].get("node_id", ""))
            except Exception:
                continue
            if rtid is None:
                continue
            src = r.get("source_node_id") or ""
            tgt = r.get("target_node_id") or ""
            if not src or not tgt:
                continue
            is_fwd = bool(r.get("is_forward"))

            if is_fwd:
                if rtid == REF_HAS_TYPE_DEFINITION:
                    self.type_definition_by_node[src] = tgt
                elif rtid == REF_HAS_MODELLING_RULE:
                    self.modelling_rule_by_node[src] = tgt
                elif rtid in HIERARCHICAL_REF_TYPES:
                    # The child may have multiple hierarchical parents in pathological
                    # cases; keep the first we encounter (organizes < has_property <
                    # has_component preference encoded by iteration order, but we just
                    # accept the first).
                    if tgt not in self.parent_reference_by_child:
                        self.parent_reference_by_child[tgt] = (src, rtid)
                    self.children_by_parent.setdefault(src, []).append(tgt)
                else:
                    # HasInterface / HasDictionaryEntry / HasEncoding / GeneratesEvent
                    # etc. are stored as plain references for Phase 5 but do not
                    # affect the structural indices here.
                    pass
            else:
                # Inverse references
                if rtid == REF_HAS_TYPE_DEFINITION:
                    # instance -> TypeDefinition (the forward direction is the canonical
                    # one but asyncua returns both; we already set it from the forward
                    # entry above, so this is idempotent)
                    self.type_definition_by_node.setdefault(src, tgt)
                elif rtid == REF_HAS_SUBTYPE:
                    # src = subtype, tgt = supertype
                    self.supertype_by_subtype[src] = tgt
                # The inverse of HasComponent / HasProperty / Organizes is the parent
                # map; we already captured it from the forward direction so we
                # don't need to handle it again here.

    def _build_declaration_indices(self) -> None:
        """Populate declaration-specific indices after the type set is known."""
        for owner_text, decl_texts in self.children_by_parent.items():
            if not owner_text:
                continue
            for child_text in decl_texts:
                rec = self.types_by_text.get(child_text)
                if rec is None:
                    continue
                if rec.get("is_type_declaration"):
                    self.declaration_owner_by_node[child_text] = owner_text
                    parent_info = self.parent_reference_by_child.get(child_text)
                    if parent_info is not None:
                        self.declaration_parent_reference_by_node[child_text] = parent_info[1]
                    self.declarations_by_owner.setdefault(owner_text, []).append(child_text)

    # ---------------- helpers ----------------

    def get_node(self, text: str) -> dict[str, Any] | None:
        return self.nodes_by_text.get(text)

    def get_type(self, text: str) -> dict[str, Any] | None:
        return self.types_by_text.get(text)

    def get_record(self, text: str) -> dict[str, Any] | None:
        """Return a record from either nodes[] or types[] (whichever has it)."""
        n = self.nodes_by_text.get(text)
        if n is not None:
            return n
        return self.types_by_text.get(text)

    def children_of(self, parent_text: str | None) -> list[str]:
        return list(self.children_by_parent.get(parent_text, []))

    def forward_references_from(self, source_text: str) -> list[dict[str, Any]]:
        return [r for r in self.raw_references
                if r["source_node_id"] == source_text and r["is_forward"]]

    def reference_from_to(self, source: str, target: str, ref_type_id: int) -> dict | None:
        for r in self.raw_references:
            if r["source_node_id"] == source and r["target_node_id"] == target \
                    and r["is_forward"] and _id_from_text(r["reference_type"]["node_id"]) == ref_type_id:
                return r
        return None

    @property
    def namespace_uris(self) -> list[str]:
        return [n["uri"] for n in sorted(self.namespace_array, key=lambda x: x["index"])]


def _id_from_text(text: str) -> int | None:
    """Extract numeric identifier from a NodeId text form like 'i=47' or 'ns=0;i=47'."""
    if not text:
        return None
    if text.startswith("ns="):
        _, _, rest = text.partition(";")
        if rest.startswith("i="):
            try:
                return int(rest[2:])
            except Exception:
                return None
        return None
    if text.startswith("i="):
        try:
            return int(text[2:])
        except Exception:
            return None
    return None


def load_export(path: str | Path) -> ExportModel:
    """Read and parse the export JSON file."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"export file not found: {p}")
    raw = json.loads(p.read_text(encoding="utf-8"))
    return ExportModel(raw)


def node_id_spec_from_export(data: dict[str, Any]) -> NodeIdSpec:
    """Build a NodeIdSpec from an export dict.

    `type_definition` dicts in the export may only contain
    {node_id, browse_name, namespace_index, namespace_uri} — without
    identifier_type/identifier.  We fall back to inferring those from
    the text form so the downstream code can still build a ua.NodeId.
    """
    text = data.get("text") or data.get("node_id") or ""
    id_type = data.get("identifier_type")
    ident = data.get("identifier")
    if id_type is None or ident is None:
        inferred_type, inferred_ident = _infer_id_fields_from_text(text)
        if id_type is None:
            id_type = inferred_type
        if ident is None:
            ident = inferred_ident
    return NodeIdSpec(
        text=text,
        namespace_index=data.get("namespace_index"),
        namespace_uri=data.get("namespace_uri"),
        identifier_type=id_type,
        identifier=ident,
    )


def node_id_spec_from_text(text: str) -> NodeIdSpec:
    """Build a NodeIdSpec from a NodeId text alone (e.g. 'ns=2;i=1110')."""
    id_type, ident = _infer_id_fields_from_text(text)
    ns_idx = 0
    if text.startswith("ns="):
        try:
            ns_idx = int(text.split(";", 1)[0].split("=", 1)[1])
        except Exception:
            ns_idx = 0
    return NodeIdSpec(
        text=text,
        namespace_index=ns_idx,
        namespace_uri=None,
        identifier_type=id_type,
        identifier=ident,
    )


def _infer_id_fields_from_text(text: str) -> tuple[str, Any]:
    """Infer (identifier_type, identifier) from a NodeId text form."""
    if not text:
        return ("String", "")
    if text.startswith("i="):
        body = text[2:]
        if ";" in body:
            ns, _, ident = body.partition(";")
            return ("Numeric", int(ident))
        return ("TwoByte", int(body))
    if text.startswith("ns="):
        head, _, rest = text.partition(";")
        try:
            ns = int(head.split("=")[1])
        except Exception:
            ns = 0
        if rest.startswith("i="):
            # ns=0 numerics may be classified TwoByte by asyncua, but the
            # exporter uses "Numeric" for the explicit `ns=0;i=N` form.
            return ("Numeric", int(rest[2:]))
        if rest.startswith("s="):
            return ("String", rest[2:])
        if rest.startswith("g="):
            return ("Guid", rest[2:])
        if rest.startswith("b="):
            import base64 as _b64
            try:
                return ("ByteString", _b64.b64decode(rest[2:]))
            except Exception:
                return ("ByteString", rest[2:])
    return ("String", text)


def qualified_name_spec_from_export(data: dict[str, Any] | None) -> QualifiedNameSpec:
    if not data:
        return QualifiedNameSpec(None, None, None)
    return QualifiedNameSpec(
        name=data.get("name"),
        namespace_index=data.get("namespace_index"),
        namespace_uri=data.get("namespace_uri"),
    )


def localized_text_spec_from_export(data: dict[str, Any] | None) -> LocalizedTextSpec:
    if not data:
        return LocalizedTextSpec(None, None)
    return LocalizedTextSpec(
        text=data.get("text"),
        locale=data.get("locale"),
    )