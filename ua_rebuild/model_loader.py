"""Load `real_server_export_v2.json` into typed structures.

The loader is read-only and must never mutate the export file.  Derived
build plans may be persisted as `build_plan_<scope>.json` but the source
JSON is treated as immutable input.
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


class ExportModel:
    """In-memory representation of the export, indexed for fast lookup."""

    def __init__(self, raw: dict[str, Any]) -> None:
        self.raw = raw
        self.schema_version: str = raw.get("schema_version", "")
        self.source_server: dict[str, Any] = raw.get("source_server", {})
        self.namespace_array: list[dict[str, Any]] = list(raw.get("namespace_array", []))
        self.roots: list[dict[str, Any]] = list(raw.get("roots", []))
        self.errors: list[dict[str, Any]] = list(raw.get("errors", []))

        # Indexes
        self.nodes_by_text: dict[str, dict[str, Any]] = {}
        self.types_by_text: dict[str, dict[str, Any]] = {}
        self.children_by_parent: dict[str | None, list[dict[str, Any]]] = {}

        for n in raw.get("nodes", []):
            self.nodes_by_text[n["node_id"]["text"]] = n
            self.children_by_parent.setdefault(n.get("parent_node_id"), []).append(n)
        for t in raw.get("types", []):
            self.types_by_text[t["node_id"]["text"]] = t

        self.references: list[dict[str, Any]] = list(raw.get("references", []))

    # ---------------- helpers ----------------

    def get_node(self, text: str) -> dict[str, Any] | None:
        return self.nodes_by_text.get(text)

    def get_type(self, text: str) -> dict[str, Any] | None:
        return self.types_by_text.get(text)

    def children_of(self, parent_text: str | None) -> list[dict[str, Any]]:
        return list(self.children_by_parent.get(parent_text, []))

    def forward_references_from(self, source_text: str) -> list[dict[str, Any]]:
        return [r for r in self.references
                if r["source_node_id"] == source_text and r["is_forward"]]

    def reference_from_to(self, source: str, target: str, ref_type_id: int) -> dict | None:
        for r in self.references:
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
            return ("FourByte" if ns < 256 else "Numeric", int(rest[2:]))
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