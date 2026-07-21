"""Phase 0 placeholders. Real implementations land in Phase 1+."""

from __future__ import annotations

from typing import Any


class TypeBuilder:
    def __init__(self, adapter: Any) -> None:
        self.adapter = adapter

    async def build(self, plan: Any) -> int:
        raise NotImplementedError("TypeBuilder implemented in Phase 1+")


class InstanceBuilder:
    def __init__(self, adapter: Any) -> None:
        self.adapter = adapter

    async def build(self, plan: Any) -> int:
        raise NotImplementedError("InstanceBuilder implemented in Phase 1+")


class ReferenceBuilder:
    def __init__(self, adapter: Any) -> None:
        self.adapter = adapter

    async def build(self, plan: Any) -> int:
        raise NotImplementedError("ReferenceBuilder implemented in Phase 1+")


class AttributeWriter:
    def __init__(self, adapter: Any) -> None:
        self.adapter = adapter

    async def write(self, plan: Any) -> int:
        raise NotImplementedError("AttributeWriter implemented in Phase 1+")