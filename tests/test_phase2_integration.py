"""Phase 2 integration test: launch the rebuild server with scope=sov1
and verify the full SOV1 subtree via an external asyncua Client."""

from __future__ import annotations

import asyncio
import socket
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import subprocess

from asyncua import Client, ua


SOV1_INSTANCE_TARGETS = [
    ("DeviceSetView", "ns=2;s=P_7765a8f78a9266d7a83581ba1b39176a", 2),
    ("SOV1",          "ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch1",   1),
    ("AssetId",       "ns=4;s=P_318b26d74fcca15eeb08a56d2f1b6f3a",   4),
    ("DeviceClass",   "ns=1;s=P_10384fe20b16c81537f93e40558636e6",   1),
    ("Configuration", "ns=1;s=P_0f82c9b911a44bc3a4185b1fe83be125",   1),
    ("SnapshotPeriod", "ns=1;s=P_c4e95c9b3819dd8bb1f24ca02b5127b6",   1),
    ("CurrentType",   "ns=1;s=P_cdc75745a8441147e448e8f845243c64",   1),
    ("Runtime",       "ns=1;s=P_cadfd5973419d77015b9410f9ceda34e",   1),
    ("FaultState",    "ns=1;s=P_79d0616e3e1a8613be1456bd90f5e544",   1),
    ("TypeMismatch",  "ns=1;s=P_cb0a950cc7e57148a93bd1d6027a720c",   1),
    ("Current",       "ns=1;s=P_fb349055a732ddf6511d1367e07bf492",   1),
    ("EURange",       "ns=0;s=P_d96e61438d6080321565c5718839603d",   0),
    ("ActionSnapshot", "ns=1;s=P_3c9fcf915366945544cd1b4032d0afe0",   1),
    ("OnlineState",   "ns=1;s=P_0fd57de4b78346a354e7f8725d4cd95f",   1),
]


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _spawn_server(port: int) -> subprocess.Popen:
    return subprocess.Popen(
        [sys.executable, str(REPO_ROOT / "ua_rebuild_server.py"),
         "--model", str(REPO_ROOT / "real_server_export_v2.json"),
         "--scope", "sov1",
         "--host", "127.0.0.1",
         "--port", str(port),
         "--profile", "debug",
         "--report", str(REPO_ROOT / "phase2_startup_report.json")],
        cwd=str(REPO_ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


async def _verify(url: str) -> tuple[int, int, int]:
    good = bad = missing = 0
    async with Client(url=url) as client:
        for _, text, _ in SOV1_INSTANCE_TARGETS:
            try:
                node = client.get_node(text)
                nc = await node.read_node_class()
                _ = nc
                bn = await node.read_browse_name()
                _ = bn
                td = await node.read_type_definition()
                _ = td
                good += 1
            except Exception:
                missing += 1
    return good, bad, missing


class Phase2IntegrationTests(unittest.TestCase):
    def test_sov1_subtree_built_and_verified(self):
        port = _free_port()
        proc = _spawn_server(port)
        try:
            ready = False
            for _ in range(180):
                if proc.poll() is not None:
                    self.fail(f"server died early, exit code {proc.returncode}")
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(0.5)
                    try:
                        s.connect(("127.0.0.1", port))
                        ready = True
                        break
                    except OSError:
                        pass
                asyncio.run(asyncio.sleep(0.5))
            self.assertTrue(ready, "server did not start listening on port")

            good, bad, missing = asyncio.run(
                _verify(f"opc.tcp://127.0.0.1:{port}/ua-rebuild/"))
            self.assertEqual(missing, 0)
            self.assertGreater(good, 0)
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)


if __name__ == "__main__":
    unittest.main()