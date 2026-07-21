# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for valve_ua_server_v1.0.exe."""

import sys
from pathlib import Path

# Resolve project root once.  SPECPATH is the directory holding this
# spec file; depending on how PyInstaller was invoked it can be wrong,
# so we try a couple of fallbacks.
def _project_root():
    candidates = [
        Path(SPECPATH).resolve().parent,
        Path(r"F:\github\ua_ua"),
    ]
    for c in candidates:
        if (c / "valve_ua_server.py").exists():
            return c
    return candidates[0]

ROOT = _project_root()

block_cipher = None


a = Analysis(
    [str(ROOT / "valve_ua_server.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[(str(ROOT / "real_server_export_v2.json"), ".")],
    hiddenimports=[
        "asyncua",
        "asyncua.ua",
        "asyncua.ua.uatypes",
        "asyncua.server",
        "asyncua.client",
        "asyncua.common",
        "asyncua.common.node",
        "asyncua.crypto",
        "asyncua.utils",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="valve_ua_server_v1.0",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)