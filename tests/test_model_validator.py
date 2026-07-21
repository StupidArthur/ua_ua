"""Tests for ua_rebuild.model_validator."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ua_rebuild.model_loader import load_export  # noqa: E402
from ua_rebuild.model_validator import validate_export  # noqa: E402


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.path = Path(self.tmpdir) / "export.json"
        self.export = {
            "schema_version": "2.0",
            "source_server": {
                "endpoint_url": "opc.tcp://10.10.58.117:18639",
                "application_uri": "http://SUPCON.UAServer.Application",
                "product_uri": "http://www.supcon.com",
                "application_name": {"text": "NeuroShellForCMS Server", "locale": "en-US"},
            },
            "namespace_array": [
                {"index": i, "uri": u} for i, u in enumerate([
                    "http://opcfoundation.org/UA/",
                    "http://SUPCON.UAServer.Product",
                    "http://supcon.com/UA",
                    "http://opcfoundation.org/UA/Dictionary/IRDI",
                    "http://opcfoundation.org/UA/DI/",
                    "http://opcfoundation.org/UA/PADIM/",
                    "http://www.OPCFoundation.org/UA/2013/01/ISA95",
                ])
            ],
            "roots": [],
            "nodes": [
                {
                    "node_id": {"text": "i=85", "namespace_index": 0,
                                "namespace_uri": "http://opcfoundation.org/UA/",
                                "identifier_type": "TwoByte", "identifier": 85},
                    "node_class": "Object",
                    "attributes": {
                        "browse_name": {"name": "Objects", "namespace_index": 0,
                                        "namespace_uri": "http://opcfoundation.org/UA/"},
                        "display_name": {"text": "Objects", "locale": ""},
                        "description": {"text": None, "locale": None},
                        "write_mask": 0, "user_write_mask": 0,
                        "event_notifier": 0,
                    },
                    "type_definition": {"node_id": "i=61", "browse_name": "FolderType",
                                       "namespace_index": 0,
                                       "namespace_uri": "http://opcfoundation.org/UA/"},
                    "parent_node_id": None, "path": "Objects", "read_errors": [],
                },
                {
                    "node_id": {"text": "ns=2;s=P_xyz", "namespace_index": 2,
                                "namespace_uri": "http://supcon.com/UA",
                                "identifier_type": "String", "identifier": "P_xyz"},
                    "node_class": "Object",
                    "attributes": {
                        "browse_name": {"name": "DeviceSetView", "namespace_index": 2,
                                        "namespace_uri": "http://supcon.com/UA"},
                        "display_name": {"text": "DeviceSetView", "locale": "en-US"},
                        "description": {"text": None, "locale": None},
                        "write_mask": 0, "user_write_mask": 0, "event_notifier": 1,
                    },
                    "type_definition": {"node_id": "i=61", "browse_name": "FolderType",
                                       "namespace_index": 0,
                                       "namespace_uri": "http://opcfoundation.org/UA/"},
                    "parent_node_id": "i=85", "path": "Objects/DeviceSetView",
                    "read_errors": [],
                },
            ],
            "types": [],
            "references": [
                {"source_node_id": "i=85", "target_node_id": "ns=2;s=P_xyz",
                 "reference_type": {"node_id": "i=35", "browse_name": "Organizes",
                                    "namespace_index": 0},
                 "is_forward": True,
                 "target_node_class": "Object",
                 "target_browse_name": {"name": "DeviceSetView", "namespace_index": 2,
                                        "namespace_uri": "http://supcon.com/UA"}},
            ],
            "errors": [],
            "statistics": {},
        }
        self.path.write_text(json.dumps(self.export, ensure_ascii=False), encoding="utf-8")
        self.model = load_export(self.path)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_clean_export_validates(self):
        res = validate_export(self.model)
        self.assertTrue(res.fatal_or_ok(), msg=f"fatal: {res.fatal}")
        self.assertEqual(len(self.model.namespace_uris), 7)

    def test_wrong_namespace_count_is_fatal(self):
        self.export["namespace_array"] = self.export["namespace_array"][:5]
        self.path.write_text(json.dumps(self.export, ensure_ascii=False), encoding="utf-8")
        model = load_export(self.path)
        res = validate_export(model)
        self.assertFalse(res.fatal_or_ok())
        self.assertTrue(any("length mismatch" in f for f in res.fatal))

    def test_missing_parent_is_fatal(self):
        self.export["nodes"][1]["parent_node_id"] = "ns=99;s=nonexistent"
        self.path.write_text(json.dumps(self.export, ensure_ascii=False), encoding="utf-8")
        model = load_export(self.path)
        res = validate_export(model)
        self.assertFalse(res.fatal_or_ok())

    def test_self_parent_is_fatal(self):
        self.export["nodes"][1]["parent_node_id"] = self.export["nodes"][1]["node_id"]["text"]
        self.path.write_text(json.dumps(self.export, ensure_ascii=False), encoding="utf-8")
        model = load_export(self.path)
        res = validate_export(model)
        self.assertFalse(res.fatal_or_ok())
        self.assertTrue(any("self-parent" in f for f in res.fatal))

    def test_duplicate_references_are_fatal(self):
        ref = self.export["references"][0]
        self.export["references"].append(dict(ref))
        self.path.write_text(json.dumps(self.export, ensure_ascii=False), encoding="utf-8")
        model = load_export(self.path)
        res = validate_export(model)
        self.assertFalse(res.fatal_or_ok())
        self.assertTrue(any("duplicate reference" in f for f in res.fatal))

    def test_raw_duplicate_node_id_is_fatal(self):
        dup = dict(self.export["nodes"][1])
        self.export["nodes"].append(dup)
        self.path.write_text(json.dumps(self.export, ensure_ascii=False), encoding="utf-8")
        model = load_export(self.path)
        res = validate_export(model)
        self.assertFalse(res.fatal_or_ok())
        self.assertTrue(any("duplicate node_id" in f for f in res.fatal))


if __name__ == "__main__":
    unittest.main()