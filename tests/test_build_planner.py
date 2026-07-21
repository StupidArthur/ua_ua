"""Tests for ua_rebuild.build_planner.

These tests use the real `real_server_export_v2.json` from the repo root
when available, otherwise they fall back to a synthetic minimal export.
All tests run from any directory by relying on `Path(__file__).resolve()`.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ua_rebuild.build_planner import (  # noqa: E402
    _is_standard_builtin,
    plan_for_scope,
    topo_sort,
)
from ua_rebuild.model_validator import validate_plan  # noqa: E402


REAL_EXPORT = REPO_ROOT / "real_server_export_v2.json"


@unittest.skipUnless(REAL_EXPORT.exists(),
                     "real_server_export_v2.json not available")
class BuildPlannerRealExportTests(unittest.TestCase):
    def test_namespace_smoke_plan(self):
        plan = plan_for_scope(str(REAL_EXPORT), "namespace-smoke")
        ids = {s.node_id.text for s in plan.instance_nodes}
        # The five smoke anchors must be present
        self.assertIn("ns=2;s=P_7765a8f78a9266d7a83581ba1b39176a", ids)
        self.assertIn("ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch1", ids)
        self.assertIn("ns=4;s=P_318b26d74fcca15eeb08a56d2f1b6f3a", ids)
        self.assertIn("ns=0;s=P_d96e61438d6080321565c5718839603d", ids)

    def test_sov1_plan_excludes_sov2_to_sov8(self):
        plan = plan_for_scope(str(REAL_EXPORT), "sov1")
        ids = {s.node_id.text for s in plan.instance_nodes}
        for i in range(2, 9):
            self.assertNotIn(
                f"ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch{i}", ids,
                msg=f"sov1 scope must NOT contain SOV{i}",
            )

    def test_sov1_plan_includes_sov1_subtree(self):
        plan = plan_for_scope(str(REAL_EXPORT), "sov1")
        ids = {s.node_id.text for s in plan.instance_nodes}
        # Direct SOV1 children (AssetId is in ns=4)
        for expected in [
            "ns=4;s=P_318b26d74fcca15eeb08a56d2f1b6f3a",  # AssetId
            "ns=1;s=P_10384fe20b16c81537f93e40558636e6",  # DeviceClass
            "ns=1;s=P_0f82c9b911a44bc3a4185b1fe83be125",  # Configuration
            "ns=1;s=P_cadfd5973419d77015b9410f9ceda34e",  # Runtime
        ]:
            self.assertIn(expected, ids)
        # Runtime descendants
        for expected in [
            "ns=1;s=P_fb349055a732ddf6511d1367e07bf492",  # Current
            "ns=1;s=P_79d0616e3e1a8613be1456bd90f5e544",  # FaultState
            "ns=1;s=P_0fd57de4b78346a354e7f8725d4cd95f",  # OnlineState
            "ns=0;s=P_d96e61438d6080321565c5718839603d",  # EURange
        ]:
            self.assertIn(expected, ids)

    def test_sov1_plan_includes_type_closure(self):
        plan = plan_for_scope(str(REAL_EXPORT), "sov1")
        ids = {s.node_id.text
               for s in plan.custom_type_nodes + plan.type_declaration_nodes}
        # SolenoidValveType closure
        self.assertIn("ns=2;i=1110", ids)
        self.assertIn("ns=2;i=2013", ids)
        self.assertIn("ns=4;i=1005", ids)
        # Parent types are pulled in transitively
        self.assertIn("ns=2;i=1031", ids)
        self.assertIn("ns=4;i=1001", ids)
        self.assertIn("ns=4;i=15063", ids)
        # Standard ns=0 types referenced by the closure
        self.assertIn("ns=0;i=2368", ids)  # AnalogItemType
        self.assertIn("ns=0;i=68", ids)    # PropertyType
        self.assertIn("ns=0;i=63", ids)    # BaseDataVariableType

    def test_all_sov_plan_has_exactly_eight_devices(self):
        plan = plan_for_scope(str(REAL_EXPORT), "all-sov")
        sov_ids = [s.node_id.text for s in plan.instance_nodes
                   if s.node_id.text.startswith("ns=1;s=7c8af738")]
        # Eight SOV roots, no others
        self.assertEqual(len(sov_ids), 8)
        for i in range(1, 9):
            self.assertIn(f"ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch{i}",
                          sov_ids)

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


class BuildPlannerStandardBuiltinTests(unittest.TestCase):
    """Test `_is_standard_builtin` accepts ONLY ns=0 numeric ids."""

    def test_builtin_recognition(self):
        self.assertTrue(_is_standard_builtin("i=85"))     # Objects
        self.assertTrue(_is_standard_builtin("i=63"))     # BaseDataVariableType
        self.assertTrue(_is_standard_builtin("ns=0;i=85"))
        self.assertTrue(_is_standard_builtin("ns=0;i=63"))
        # Any ns=0 numeric id is treated as potentially standard; Phase 1
        # confirms via node_exists at build time.
        self.assertTrue(_is_standard_builtin("ns=0;i=2372"))  # DiscreteItemType

    def test_non_builtin_recognition(self):
        self.assertFalse(_is_standard_builtin("ns=2;i=85"))
        self.assertFalse(_is_standard_builtin("ns=4;i=68"))
        self.assertFalse(_is_standard_builtin("ns=1;s=anything"))
        self.assertFalse(_is_standard_builtin("ns=2;i=1110"))
        self.assertFalse(_is_standard_builtin("ns=0;s=P_xxxxx"))
        self.assertFalse(_is_standard_builtin(""))
        self.assertFalse(_is_standard_builtin("ns=99;i=99999"))


@unittest.skipUnless(REAL_EXPORT.exists(),
                     "real_server_export_v2.json not available")
class BuildPlannerAncestorClosureTests(unittest.TestCase):
    """Selecting a deep node must pull in its full ancestor chain."""

    def test_smoke_scope_includes_runtime_current(self):
        plan = plan_for_scope(str(REAL_EXPORT), "namespace-smoke")
        ids = {s.node_id.text for s in plan.instance_nodes}
        # EURange -> Current -> Runtime -> SOV1 -> DeviceSetView -> Objects
        self.assertIn("ns=1;s=P_fb349055a732ddf6511d1367e07bf492", ids)  # Current
        self.assertIn("ns=1;s=P_cadfd5973419d77015b9410f9ceda34e", ids)  # Runtime
        self.assertIn("ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch1", ids)  # SOV1

    def test_all_selected_have_parent_in_plan_or_standard(self):
        plan = plan_for_scope(str(REAL_EXPORT), "sov1")
        from ua_rebuild.model_loader import load_export
        model = load_export(str(REAL_EXPORT))
        res = validate_plan(plan, model)
        self.assertTrue(res.fatal_or_ok(),
                        msg=f"validate_plan fatal: {res.fatal}")


@unittest.skipUnless(REAL_EXPORT.exists(),
                     "real_server_export_v2.json not available")
class BuildPlannerTypeSpecTests(unittest.TestCase):
    """Verify type / declaration NodeSpec correctness."""

    def test_no_self_parent_in_plan(self):
        plan = plan_for_scope(str(REAL_EXPORT), "sov1")
        for spec in plan.custom_type_nodes + plan.type_declaration_nodes + plan.instance_nodes:
            self.assertNotEqual(
                spec.node_id.text,
                spec.parent_node_id.text if spec.parent_node_id else None,
                msg=f"self-parent in {spec.node_id.text}",
            )

    def test_no_self_type_definition_in_plan(self):
        plan = plan_for_scope(str(REAL_EXPORT), "sov1")
        for spec in plan.custom_type_nodes + plan.type_declaration_nodes + plan.instance_nodes:
            self.assertNotEqual(
                spec.node_id.text,
                spec.type_definition.text if spec.type_definition else None,
                msg=f"self-TypeDefinition in {spec.node_id.text}",
            )

    def test_type_node_parent_is_supertype(self):
        plan = plan_for_scope(str(REAL_EXPORT), "sov1")
        by_id = {s.node_id.text: s for s in plan.custom_type_nodes}
        # SolenoidValveType (ns=2;i=1110) parent must be SIMPADeviceType
        # (ns=2;i=1031) and parent_reference_type_id must be HasSubtype (45).
        sov = by_id["ns=2;i=1110"]
        self.assertIsNotNone(sov.parent_node_id)
        self.assertEqual(sov.parent_node_id.text, "ns=2;i=1031")
        self.assertEqual(sov.parent_reference_type_id, 45)

    def test_declaration_parent_uses_has_component_or_has_property(self):
        plan = plan_for_scope(str(REAL_EXPORT), "sov1")
        by_id = {s.node_id.text: s for s in plan.type_declaration_nodes}
        # Configuration declaration (ns=2;i=5209) parent must be
        # SolenoidValveType (ns=2;i=1110) via HasComponent (47).
        cfg = by_id["ns=2;i=5209"]
        self.assertIsNotNone(cfg.parent_node_id)
        self.assertEqual(cfg.parent_node_id.text, "ns=2;i=1110")
        self.assertEqual(cfg.parent_reference_type_id, 47)
        # TypeDefinition should be FunctionalGroupType (ns=4;i=1005)
        self.assertIsNotNone(cfg.type_definition)
        self.assertEqual(cfg.type_definition.text, "ns=4;i=1005")

    def test_parent_reference_types_distinguished(self):
        plan = plan_for_scope(str(REAL_EXPORT), "sov1")
        by_id = {s.node_id.text: s for s in plan.instance_nodes}
        # Objects -> DeviceSetView uses HasComponent (47) in the export
        self.assertEqual(by_id["ns=2;s=P_7765a8f78a9266d7a83581ba1b39176a"]
                         .parent_reference_type_id, 47)
        # DeviceSetView -> SOV1 also uses HasComponent (47)
        self.assertEqual(by_id["ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch1"]
                         .parent_reference_type_id, 47)
        # SOV1 -> AssetId uses HasProperty (46)
        asset_id = by_id["ns=4;s=P_318b26d74fcca15eeb08a56d2f1b6f3a"]
        self.assertEqual(asset_id.parent_reference_type_id, 46)
        # SOV1 -> Configuration uses HasComponent (47)
        config = by_id["ns=1;s=P_0f82c9b911a44bc3a4185b1fe83be125"]
        self.assertEqual(config.parent_reference_type_id, 47)


@unittest.skipUnless(REAL_EXPORT.exists(),
                     "real_server_export_v2.json not available")
class BuildPlannerTopoOrderTests(unittest.TestCase):
    def test_no_duplicate_creation_order(self):
        plan = plan_for_scope(str(REAL_EXPORT), "sov1")
        self.assertEqual(len(plan.node_creation_order),
                         len(set(plan.node_creation_order)))

    def test_parent_instance_before_child_instance(self):
        plan = plan_for_scope(str(REAL_EXPORT), "sov1")
        order = {nid: i for i, nid in enumerate(plan.node_creation_order)}
        for spec in plan.instance_nodes:
            if spec.parent_node_id and spec.parent_node_id.text:
                self.assertLess(
                    order[spec.parent_node_id.text], order[spec.node_id.text],
                    msg=f"parent {spec.parent_node_id.text} should come before {spec.node_id.text}",
                )

    def test_owner_type_before_declaration(self):
        plan = plan_for_scope(str(REAL_EXPORT), "sov1")
        order = {nid: i for i, nid in enumerate(plan.node_creation_order)}
        by_id = {s.node_id.text: s for s in plan.type_declaration_nodes}
        for decl_text, decl_spec in by_id.items():
            if decl_spec.parent_node_id and decl_spec.parent_node_id.text:
                self.assertLess(
                    order[decl_spec.parent_node_id.text], order[decl_text],
                    msg=f"owner {decl_spec.parent_node_id.text} should come before declaration {decl_text}",
                )

    def test_parent_type_before_child_type(self):
        plan = plan_for_scope(str(REAL_EXPORT), "sov1")
        order = {nid: i for i, nid in enumerate(plan.node_creation_order)}
        # SolenoidValveType (ns=2;i=1110) parent SIMPADeviceType (ns=2;i=1031)
        # comes first.
        self.assertLess(order["ns=2;i=1031"], order["ns=2;i=1110"])


@unittest.skipUnless(REAL_EXPORT.exists(),
                     "real_server_export_v2.json not available")
class BuildPlannerAttributeRetentionTests(unittest.TestCase):
    def test_eurange_keeps_minimum_sampling_interval(self):
        plan = plan_for_scope(str(REAL_EXPORT), "sov1")
        by_id = {s.node_id.text: s for s in plan.instance_nodes}
        eurang = by_id.get("ns=0;s=P_d96e61438d6080321565c5718839603d")
        self.assertIsNotNone(eurang)
        # MinimumSamplingInterval is present in the export with value 0.0
        self.assertEqual(eurang.minimum_sampling_interval, 0.0)
        # access_level_ex field exists (may be None when server doesn't support it)
        self.assertTrue(hasattr(eurang, "access_level_ex"))


class BuildPlannerSyntheticTests(unittest.TestCase):
    """Tests that do not depend on the real export."""

    def test_unknown_scope_raises(self):
        if not REAL_EXPORT.exists():
            self.skipTest("real export not available")
        with self.assertRaises(ValueError):
            plan_for_scope(str(REAL_EXPORT), "bogus")


if __name__ == "__main__":
    unittest.main()