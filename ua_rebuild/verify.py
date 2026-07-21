"""SelfCheck + ExternalVerifier placeholders for Phase 0."""

from __future__ import annotations

from typing import Any


class SelfCheck:
    def __init__(self, adapter: Any, plan: Any) -> None:
        self.adapter = adapter
        self.plan = plan

    async def run(self) -> dict[str, Any]:
        raise NotImplementedError("SelfCheck implemented in Phase 1+")


class ExternalVerifier:
    def __init__(self, url: str, plan: Any) -> None:
        self.url = url
        self.plan = plan

    async def run(self) -> dict[str, Any]:
        raise NotImplementedError("ExternalVerifier implemented in Phase 1+")


class ReportWriter:
    def __init__(self, path: str) -> None:
        self.path = path

    def write(self, payload: dict[str, Any]) -> None:
        import json
        from pathlib import Path
        p = Path(self.path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str),
                     encoding="utf-8")