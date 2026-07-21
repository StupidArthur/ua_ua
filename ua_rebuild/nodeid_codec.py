"""Decode structured NodeId dicts (as written by `ua_full_exporter.py`)
into asyncua `ua.NodeId` instances.

The exporter deliberately keeps both the textual form and the individual
fields so we never have to parse the legacy `NodeId(Identifier=..., ...)`
repr string used by `ua_client.py` / `ua_server.py`.
"""

from __future__ import annotations

from typing import Any

from asyncua import ua


# Map identifier_type -> asyncua NodeId subclass + factory.
# TwoByte is encoded as plain `i=N` in ns=0 by the exporter.
_NODEID_FACTORIES: dict[str, Any] = {
    "TwoByte": lambda ns, ident: ua.NodeId(int(ident), 0),
    "FourByte": lambda ns, ident: ua.NodeId(int(ident), int(ns)),
    "Numeric": lambda ns, ident: ua.NodeId(int(ident), int(ns)),
    "String": lambda ns, ident: ua.NodeId(str(ident), int(ns)),
    "Guid": lambda ns, ident: ua.NodeId(_parse_guid(ident), int(ns)),
    "ByteString": lambda ns, ident: ua.NodeId(_parse_bytestring(ident), int(ns)),
}


def _parse_guid(value: Any):
    """Accept Guid as uuid.UUID, hex string, or `str(uuid.UUID(...))`."""
    import uuid as _uuid
    if isinstance(value, _uuid.UUID):
        return value
    s = str(value)
    try:
        return _uuid.UUID(s)
    except Exception:
        return _uuid.UUID(hex=s.replace("-", ""))


def _parse_bytestring(value: Any) -> bytes:
    """Accept either raw bytes, hex string, or base64 string."""
    import base64 as _b64
    if isinstance(value, (bytes, bytearray)):
        return bytes(value)
    s = str(value)
    try:
        return _b64.b64decode(s, validate=True)
    except Exception:
        pass
    try:
        return bytes.fromhex(s)
    except Exception:
        pass
    return s.encode("utf-8", errors="replace")


def decode_node_id(data: dict | None) -> ua.NodeId | None:
    """Convert the exporter's node_id dict into a `ua.NodeId`.

    Returns None when input is None or missing essential fields.
    """
    if data is None:
        return None
    if not isinstance(data, dict):
        raise TypeError(f"decode_node_id expects dict, got {type(data).__name__}")

    text = data.get("text") or ""
    ns_idx = data.get("namespace_index")
    id_type = data.get("identifier_type")
    ident = data.get("identifier")

    if id_type is None:
        id_type = _infer_type_from_text(text)

    factory = _NODEID_FACTORIES.get(id_type)
    if factory is None:
        raise ValueError(f"Unsupported identifier_type: {id_type!r}")

    ns = ns_idx if ns_idx is not None else 0
    try:
        nid = factory(ns, ident)
    except Exception:
        nid = _parse_text(text)

    assert nid.NamespaceIndex == ns, (
        f"namespace mismatch after decode: {nid.NamespaceIndex} != {ns} for {text}"
    )
    # For ByteString/Guid, identifier is opaque bytes; skip equality check.
    if id_type not in ("ByteString", "Guid"):
        assert _matches_identifier(nid.Identifier, ident), (
            f"identifier mismatch after decode: {nid.Identifier!r} != {ident!r} for {text}"
        )
    return nid


def _matches_identifier(actual: Any, expected: Any) -> bool:
    if isinstance(expected, int):
        try:
            return int(actual) == expected
        except Exception:
            return False
    return str(actual) == str(expected)


def _infer_type_from_text(text: str) -> str:
    if not text:
        return "String"
    if text.startswith("i="):
        # Bare `i=N` is always TwoByte (per exporter rules).
        return "TwoByte"
    if text.startswith("ns="):
        head, _, rest = text.partition(";")
        ns = int(head.split("=")[1])
        if rest.startswith("i="):
            # Anything written as `ns=N;i=M` is Numeric, even when N==0;
            # only the bare `i=N` form is TwoByte.
            return "Numeric"
        if rest.startswith("s="):
            return "String"
        if rest.startswith("g="):
            return "Guid"
        if rest.startswith("b="):
            return "ByteString"
    return "String"


def _parse_text(text: str) -> ua.NodeId:
    if not text:
        return ua.NodeId("", 0)
    if text.startswith("i="):
        body = text[2:]
        if ";" in body:
            ns, _, ident = body.partition(";")
            return ua.NodeId(int(ident), int(ns.split("=")[1]))
        return ua.NodeId(int(body), 0)
    if text.startswith("ns="):
        head, _, rest = text.partition(";")
        ns = int(head.split("=")[1])
        if rest.startswith("i="):
            return ua.NodeId(int(rest[2:]), ns)
        if rest.startswith("s="):
            return ua.NodeId(rest[2:], ns)
        if rest.startswith("g="):
            import uuid as _uuid
            return ua.NodeId(_uuid.UUID(rest[2:]), ns)
        if rest.startswith("b="):
            import base64 as _b64
            return ua.NodeId(_b64.b64decode(rest[2:]), ns)
    return ua.NodeId(text, 0)