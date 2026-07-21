"""Phase 1 integration test: start the rebuild server and verify the
multi-namespace smoke set via an external asyncua Client.

This test does NOT depend on UAExpert.  It is meant to be runnable in
CI and validates the Phase 1 success criteria programmatically:

    * server starts
    * NamespaceArray matches the export
    * 5 (or 6) smoke nodes exist with correct NodeIds / BrowseNames
    * legal attributes read back as Good
    * no BadNodeIdUnknown, no BadTypeMismatch
"""

from __future__ import annotations

import asyncio
import json
import socket
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import subprocess

from asyncua import Client, ua

from ua_rebuild.external_verifier import ExternalVerifier


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


async def _run_external_verification(url: str) -> dict:
    verifier = ExternalVerifier(url)
    return await verifier.run()


def _spawn_server(port: int) -> subprocess.Popen:
    return subprocess.Popen(
        [sys.executable, str(REPO_ROOT / "ua_rebuild_server.py"),
         "--model", str(REPO_ROOT / "real_server_export_v2.json"),
         "--scope", "namespace-smoke",
         "--host", "127.0.0.1",
         "--port", str(port),
         "--profile", "debug",
         "--report", str(REPO_ROOT / "phase1_startup_report.json")],
        cwd=str(REPO_ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


class Phase1ServerIntegrationTests(unittest.TestCase):
    def test_server_starts_and_serves_multi_namespace(self):
        port = _free_port()
        proc = _spawn_server(port)
        try:
            # Wait for the port to open (up to 60s because asyncua's
            # internal address-space instantiation is slow on first run).
            ready = False
            for _ in range(120):
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(0.5)
                    try:
                        s.connect(("127.0.0.1", port))
                        ready = True
                        break
                    except OSError:
                        pass
                if proc.poll() is not None:
                    self.fail(f"server died early, exit code {proc.returncode}")
                asyncio.run(asyncio.sleep(0.5))
            self.assertTrue(ready, "server did not start listening on port")

            url = f"opc.tcp://127.0.0.1:{port}/ua-rebuild/"
            summary = asyncio.run(_run_external_verification(url))

            # NamespaceArray must match the export.
            expected_ns = [
                "http://opcfoundation.org/UA/",
                "http://SUPCON.UAServer.Product",
                "http://supcon.com/UA",
                "http://opcfoundation.org/UA/Dictionary/IRDI",
                "http://opcfoundation.org/UA/DI/",
                "http://opcfoundation.org/UA/PADIM/",
                "http://www.OPCFoundation.org/UA/2013/01/ISA95",
            ]
            self.assertEqual(summary["namespace_array"], expected_ns)

            # Each smoke node must exist and read Good on every legal
            # attribute.
            self.assertEqual(summary["totals"]["missing"], 0)
            self.assertEqual(summary["totals"]["bad"], 0)
            self.assertGreater(summary["totals"]["good"], 0)

            # Each target node must have the expected NodeClass.
            targets_by_label = {n["label"]: n for n in summary["nodes"]}
            self.assertEqual(targets_by_label["DeviceSetView"]["node_class"], "Object")
            self.assertEqual(targets_by_label["SOV1"]["node_class"], "Object")
            self.assertEqual(targets_by_label["AssetId"]["node_class"], "Variable")
            self.assertEqual(targets_by_label["Current"]["node_class"], "Variable")
            self.assertEqual(targets_by_label["EURange"]["node_class"], "Variable")

        finally:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)


if __name__ == "__main__":
    unittest.main()