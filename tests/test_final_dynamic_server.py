"""Final dynamic-server integration test.

Verifies that:

    * SOV1..SOV8 Current nodes update and fire subscriptions
    * SOV1..SOV8 ActionSnapshot nodes emit 1440-byte ByteString values
    * at least two devices produce distinct Current values
    * the server exits cleanly via the harness
"""

from __future__ import annotations

import asyncio
import sys
import time
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from asyncua import Client

from tests.process_harness import ServerProcessHarness
from ua_rebuild.build_planner import plan_for_scope


class _SubscriptionHandler:
    def __init__(self) -> None:
        self.values: dict[str, list[object]] = {}
        self.event = asyncio.Event()

    def datachange_notification(self, node, value, data):
        key = node.nodeid.to_string()
        self.values.setdefault(key, []).append(value)
        self.event.set()


async def _wait_distinct(handler, node_id, *, minimum, timeout):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        values = handler.values.get(node_id, [])
        distinct = {repr(v) for v in values}
        if len(distinct) >= minimum:
            return values
        handler.event.clear()
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        try:
            await asyncio.wait_for(handler.event.wait(), timeout=min(1.0, remaining))
        except asyncio.TimeoutError:
            pass
    raise TimeoutError(
        f"did not receive {minimum} distinct values for {node_id}; "
        f"received={handler.values.get(node_id, [])}"
    )


def _runtime_node_ids():
    plan = plan_for_scope(
        str(REPO_ROOT / "real_server_export_v2.json"),
        "all-sov",
    )
    current_ids: list[str] = []
    snapshot_ids: list[str] = []
    for spec in plan.instance_nodes:
        path = spec.path or ""
        if path.endswith("/Current"):
            current_ids.append(spec.node_id.text)
        if path.endswith("/ActionSnapshot"):
            snapshot_ids.append(spec.node_id.text)
    if len(current_ids) != 8:
        raise AssertionError(
            f"expected 8 Current nodes, got {len(current_ids)}"
        )
    if len(snapshot_ids) != 8:
        raise AssertionError(
            f"expected 8 ActionSnapshot nodes, got {len(snapshot_ids)}"
        )
    return current_ids, snapshot_ids


async def _verify(endpoint):
    current_ids, snapshot_ids = _runtime_node_ids()
    handler = _SubscriptionHandler()
    async with Client(url=endpoint, timeout=10) as client:
        subscription = await asyncio.wait_for(
            client.create_subscription(100, handler),
            timeout=10,
        )
        try:
            current_nodes = [client.get_node(t) for t in current_ids]
            snapshot_nodes = [client.get_node(t) for t in snapshot_ids]

            handles = await asyncio.wait_for(
                subscription.subscribe_data_change(
                    current_nodes + snapshot_nodes
                ),
                timeout=20,
            )

            # Each Current: ≥ 3 distinct values, all floats.
            for nid in current_ids:
                values = await _wait_distinct(
                    handler, nid, minimum=3, timeout=20,
                )
                non_null = [v for v in values if v is not None]
                assert non_null, f"{nid}: all values are None"
                for v in non_null:
                    assert isinstance(v, float), (nid, type(v), v)

            # Each ActionSnapshot: ≥ 2 non-null byte-strings of length 1440.
            for nid in snapshot_ids:
                values = await _wait_distinct(
                    handler, nid, minimum=2, timeout=20,
                )
                non_null = [v for v in values if v is not None]
                assert non_null, f"{nid}: no non-null snapshot received"
                for v in non_null:
                    assert isinstance(v, (bytes, bytearray)), (nid, type(v))
                    assert len(v) == 1440, (nid, len(v))

            # At least two devices must produce distinct Current values.
            latest = {
                nid: handler.values[nid][-1] for nid in current_ids
            }
            distinct_count = len(
                {round(float(v), 3) for v in latest.values()}
            )
            assert distinct_count > 1, (
                f"all devices produced the same Current value: {latest}"
            )

            await asyncio.wait_for(
                subscription.unsubscribe(handles),
                timeout=10,
            )
        finally:
            await asyncio.wait_for(
                subscription.delete(),
                timeout=10,
            )


class FinalDynamicServerTests(unittest.TestCase):
    def test_dynamic_server(self) -> None:
        harness = ServerProcessHarness(
            REPO_ROOT,
            scope="all-sov",
            enable_simulation=True,
        )
        try:
            harness.start()
            ready = harness.wait_ready(timeout=120)
            self.assertEqual(ready["status"], "ready")
            self.assertEqual(ready["devices_registered"], 8)
            self.assertTrue(ready["simulation_enabled"])

            asyncio.run(
                asyncio.wait_for(
                    _verify(harness.endpoint),
                    timeout=180,
                )
            )
        except Exception as exc:
            self.fail(
                f"{exc}\n\nSERVER LOG:\n{harness.read_log_tail()}"
            )
        finally:
            harness.stop()


if __name__ == "__main__":
    unittest.main()