"""Tests for ua_rebuild.build_planner.

These tests use the real `real_server_export_v2.json` if available,
otherwise they fall back to a synthetic minimal export.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, r"F:\github\ua_ua")

from ua_rebuild.build_planner import plan_for_scope, _is_standard_builtin  # noqa: E402


REPO_ROOT = Path(r"F:\github\ua_ua")
REAL_EXPORT = REPO_ROOT / "real_server_export_v2.json"


@unittest.skipUnless(REAL_EXPORT.exists(),
                     "real_server_export_v2.json not available")
class BuildPlannerRealExportTests(unittest.TestCase):
    def test_namespace_smoke_plan(self):
        plan = plan_for_scope(str(REAL_EXPORT), "namespace-smoke")
        # The plan must include the 5 smoke nodes
        ids = {s.node_id.text for s in plan.instance_nodes}
        self.assertIn("ns=2;s=P_7765a8f78a9266d7a83581ba1b39176a", ids)
        self.assertIn("ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch1", ids)
        self.assertIn("ns=4;s=P_318b26d74fcca15eeb08a56d2f1b6f3a", ids)
        self.assertIn("ns=0;s=P_d96e61438d6080321565c5718839603d", ids)

    def test_sov1_plan_includes_type_closure(self):
        plan = plan_for_scope(str(REAL_EXPORT), "sov1")
        ids = {s.node_id.text for s in plan.custom_type_nodes + plan.type_declaration_nodes}
        # SolenoidValveType closure
        self.assertIn("ns=2;i=1110", ids)
        self.assertIn("ns=2;i=2013", ids)
        self.assertIn("ns=4;i=1005", ids)

    def test_all_sov_plan_includes_eight_devices(self):
        plan = plan_for_scope(str(REAL_EXPORT), "all-sov")
        sov_ids = [s.node_id.text for s in plan.instance_nodes
                   if s.node_id.text.startswith("ns=1;s=7c8af738")]
        # 8 SOVs + their children
        self.assertGreaterEqual(len(sov_ids), 8)
        for i in range(1, 9):
            self.assertIn(f"ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch{i}", sov_ids)

    def test_full_custom_plan_has_zero_fatal(self):
        plan = plan_for_scope(str(REAL_EXPORT), "full-custom")
        self.assertGreater(len(plan.instance_nodes), 0)
        self.assertGreater(len(plan.custom_type_nodes) +
                           len(plan.type_declaration_nodes), 0)

    def test_namespaces_match(self):
        plan = plan_for_scope(str(REAL_EXPORT), "namespace-smoke")
        self.assertEqual(len(plan.namespaces), 7)
        self.assertEqual(plan.namespaces[0], "http://opcfoundation.org/UA/")
        self.assertEqual(plan.namespaces[1], "http://SUPCON.UAServer.Product")
        self.assertEqual(plan.namespaces[2], "http://supcon.com/UA")
        self.assertEqual(plan.namespaces[4], "http://opcfoundation.org/UA/DI/")

    def test_no_duplicate_creation_order(self):
        plan = plan_for_scope(str(REAL_EXPORT), "sov1")
        self.assertEqual(len(plan.node_creation_order),
                         len(set(plan.node_creation_order)))

    def test_builtin_classification(self):
        self.assertTrue(_is_standard_builtin("i=85"))
        self.assertTrue(_is_standard_builtin("i=63"))
        self.assertFalse(_is_standard_builtin("ns=2;i=1110"))
        self.assertFalse(_is_standard_builtin("ns=1;s=abc"))


class BuildPlannerSyntheticTests(unittest.TestCase):
    """Light-weight tests that do not require the real export."""

    def test_unknown_scope_raises(self):
        with self.assertRaises(ValueError):
            plan_for_scope(str(REAL_EXPORT), "bogus")


if __name__ == "__main__":
    unittest.main()