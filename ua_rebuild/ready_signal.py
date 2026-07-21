"""Ready-signal file: written after Server is fully initialised and
listening, removed during graceful shutdown."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def write_ready_file(
    path: str | Path | None,
    payload: dict[str, Any],
) -> None:
    if path is None:
        return

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    temporary = target.with_suffix(
        target.suffix + f".tmp.{os.getpid()}"
    )

    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    temporary.replace(target)


def remove_ready_file(path: str | Path | None) -> None:
    if path is None:
        return

    try:
        Path(path).unlink(missing_ok=True)
    except Exception:
        pass