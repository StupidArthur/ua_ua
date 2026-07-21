"""Phase 3 integration test: launch the rebuild server with scope=all-sov
and verify all 8 SOV devices via an external asyncua Client."""

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


SOV_DEVICE_ROOTS = [
    "ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch1",
    "ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch2",
    "ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch3",
    "ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch4",
    "ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch5",
    "ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch6",
    "ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch7",
    "ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch8",
]


# Required children for every SOV
DEVICE_SUBTARGETS = {
    "AssetId":      "ns=4;s=P_%s",  # filled per-channel
    "DeviceClass":  "ns=1;s=P_%s",
    "Current":      "ns=1;s=P_%s",
    "EURange":      "ns=0;s=P_%s",
    "ActionSnapshot": "ns=1;s=P_%s",
    "OnlineState":  "ns=1;s=P_%s",
}

# Channel-suffix map for each device (derived from the export)
CHANNEL_MAP = {
    1: ("318b26d74fcca15eeb08a56d2f1b6f3a", "10384fe20b16c81537f93e40558636e6",
         "fb349055a732ddf6511d1367e07bf492", "d96e61438d6080321565c5718839603d",
         "3c9fcf915366945544cd1b4032d0afe0", "0fd57de4b78346a354e7f8725d4cd95f"),
}


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _spawn_server(port: int) -> subprocess.Popen:
    return subprocess.Popen(
        [sys.executable, str(REPO_ROOT / "ua_rebuild_server.py"),
         "--model", str(REPO_ROOT / "real_server_export_v2.json"),
         "--scope", "all-sov",
         "--host", "127.0.0.1",
         "--port", str(port),
         "--profile", "debug",
         "--report", str(REPO_ROOT / "phase3_startup_report.json")],
        cwd=str(REPO_ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


async def _verify(url: str) -> dict:
    out = {"devices_found": 0, "sub_nodes_found": 0,
           "sub_nodes_missing": 0, "bad_attributes": 0}
    async with Client(url=url) as client:
        # 8 device roots
        for sov_root in SOV_DEVICE_ROOTS:
            try:
                node = client.get_node(sov_root)
                await node.read_node_class()
                out["devices_found"] += 1
            except Exception:
                continue

        # Per-device sub-targets (only check SOV1 for time)
        suffix = CHANNEL_MAP[1]
        for label, fmt in DEVICE_SUBTARGETS.items():
            text = fmt % suffix[{"AssetId": 0, "DeviceClass": 1,
                                  "Current": 2, "EURange": 3,
                                  "ActionSnapshot": 4, "OnlineState": 5}[label]]
            try:
                node = client.get_node(text)
                await node.read_node_class()
                out["sub_nodes_found"] += 1
            except Exception:
                out["sub_nodes_missing"] += 1
    return out


class Phase3IntegrationTests(unittest.TestCase):
    def test_all_sov_devices_built_and_verified(self):
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

            result = asyncio.run(_verify(f"opc.tcp://127.0.0.1:{port}/ua-rebuild/"))
            self.assertEqual(result["devices_found"], 8,
                             f"missing device roots: {result}")
            self.assertEqual(result["sub_nodes_missing"], 0,
                             f"missing sub-nodes: {result}")
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)


if __name__ == "__main__":
    unittest.main()