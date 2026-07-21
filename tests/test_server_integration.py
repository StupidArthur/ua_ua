"""Integration smoke tests.

These tests run the rebuild CLI and verify file layout.  They use
`Path(__file__).resolve().parents[1]` so they work regardless of the
caller's working directory.
"""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


class FileLayoutTests(unittest.TestCase):
    def test_required_files_exist(self):
        expected = [
            "ua_full_exporter.py",
            "real_server_export_v2.json",
            "real_server_export_report.md",
            "ua_rebuild_server.py",
            "ua_verify_server.py",
            "requirements-rebuild.txt",
            ".gitignore",
            "ua_rebuild/__init__.py",
            "ua_rebuild/config.py",
            "ua_rebuild/model.py",
            "ua_rebuild/model_loader.py",
            "ua_rebuild/model_validator.py",
            "ua_rebuild/nodeid_codec.py",
            "ua_rebuild/value_codec.py",
            "ua_rebuild/build_planner.py",
            "ua_rebuild/asyncua_adapter.py",
            "ua_rebuild/builders.py",
            "ua_rebuild/runtime.py",
            "ua_rebuild/verify.py",
            "tests/__init__.py",
            "tests/test_nodeid_codec.py",
            "tests/test_value_codec.py",
            "tests/test_model_validator.py",
            "tests/test_build_planner.py",
        ]
        for f in expected:
            self.assertTrue((REPO_ROOT / f).exists(), f"missing {f}")

    def test_requirements_rebuild_pins_asyncua(self):
        text = (REPO_ROOT / "requirements-rebuild.txt").read_text(encoding="utf-8")
        self.assertIn("asyncua==", text)
        self.assertNotIn(">=", text)


class CliTests(unittest.TestCase):
    def test_dry_run_exits_zero_from_repo_root(self):
        result = subprocess.run(
            [sys.executable, "ua_rebuild_server.py",
             "--model", "real_server_export_v2.json",
             "--scope", "namespace-smoke",
             "--dry-run"],
            cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=60,
        )
        self.assertEqual(result.returncode, 0,
                         msg=f"stdout={result.stdout}\nstderr={result.stderr}")

    def test_dry_run_exits_zero_from_temp_dir(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            result = subprocess.run(
                [sys.executable, str(REPO_ROOT / "ua_rebuild_server.py"),
                 "--model", str(REPO_ROOT / "real_server_export_v2.json"),
                 "--scope", "namespace-smoke",
                 "--dry-run"],
                cwd=td, capture_output=True, text=True, timeout=60,
            )
            self.assertEqual(result.returncode, 0,
                             msg=f"stdout={result.stdout}\nstderr={result.stderr}")


if __name__ == "__main__":
    unittest.main()