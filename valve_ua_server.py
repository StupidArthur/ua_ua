"""Valve UA Server v1.0 launcher.

Prints a fixed banner, then runs the rebuild server with the all-sov
scope, the clone profile, and the dynamic simulator enabled.  No CLI
arguments are accepted.

Usage:
    valve_ua_server_v1.0.exe
    python valve_ua_server.py
"""

from __future__ import annotations

import sys
from pathlib import Path


BANNER = "v1.0 designed by @yuzechao"


def _bundled_model_path() -> Path:
    """Return the model JSON path, supporting PyInstaller's _MEIPASS layout."""
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass is not None:
        candidate = Path(meipass) / "real_server_export_v2.json"
        if candidate.exists():
            return candidate
    # Source-tree fallback (when running from the repo without PyInstaller)
    here = Path(__file__).resolve().parent
    candidate = here / "real_server_export_v2.json"
    if candidate.exists():
        return candidate
    # When PyInstaller onefile unpacks to a temp dir, fall back to cwd.
    return Path.cwd() / "real_server_export_v2.json"


def main() -> int:
    print(BANNER, flush=True)

    sys.argv = [
        "valve_ua_server.py",
        "--model", str(_bundled_model_path()),
        "--scope", "all-sov",
        "--host", "0.0.0.0",
        "--port", "18639",
        "--profile", "clone",
        "--enable-simulation",
        "--tick-ms", "250",
        "--snapshot-interval-ms", "1000",
        "--seed", "12345",
    ]

    # Import lazily so the banner prints first even if asyncua startup
    # has to wait on something heavy.
    from ua_rebuild_server import main as server_main
    return server_main()


if __name__ == "__main__":
    sys.exit(main())