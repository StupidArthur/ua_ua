"""Tests for ua_rebuild.value_codec."""

from __future__ import annotations

import base64
import sys
import unittest
from pathlib import Path

from asyncua import ua

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ua_rebuild.value_codec import decode_exported_value, make_data_value_for_init  # noqa: E402


_FLOAT = ua.NodeId(ua.ObjectIds.Float)
_DOUBLE = ua.NodeId(ua.ObjectIds.Double)
_BOOLEAN = ua.NodeId(ua.ObjectIds.Boolean)
_STRING = ua.NodeId(ua.ObjectIds.String)
_BYTES = ua.NodeId(ua.ObjectIds.ByteString)
_RANGE = ua.NodeId(ua.ObjectIds.Range)
_ENUM = ua.NodeId(ua.ObjectIds.EnumValueType)


class ScalarValueTests(unittest.TestCase):
    def test_float_keeps_float_type(self):
        dv = decode_exported_value(
            {"value": 216.0, "status_code": "Good"}, _FLOAT)
        self.assertEqual(dv.Value.VariantType, ua.VariantType.Float)
        self.assertAlmostEqual(float(dv.Value.Value), 216.0, places=4)

    def test_double_for_double_datatype(self):
        dv = decode_exported_value({"value": 1.23}, _DOUBLE)
        self.assertEqual(dv.Value.VariantType, ua.VariantType.Double)

    def test_boolean(self):
        dv = decode_exported_value({"value": True}, _BOOLEAN)
        self.assertEqual(dv.Value.VariantType, ua.VariantType.Boolean)
        self.assertTrue(bool(dv.Value.Value))

    def test_string(self):
        dv = decode_exported_value({"value": "AirTac4V210-08"}, _STRING)
        self.assertEqual(dv.Value.VariantType, ua.VariantType.String)
        self.assertEqual(str(dv.Value.Value), "AirTac4V210-08")


class ByteStringTests(unittest.TestCase):
    def test_bytestring_base64(self):
        payload = b"\x00\x01\x02\x03\x04"
        dv = decode_exported_value(
            {"value": {"__type__": "ByteString", "base64": base64.b64encode(payload).decode(), "length": len(payload)}},
            _BYTES,
        )
        self.assertEqual(dv.Value.VariantType, ua.VariantType.ByteString)
        self.assertEqual(bytes(dv.Value.Value), payload)


class StructuredValueTests(unittest.TestCase):
    def test_range(self):
        dv = decode_exported_value(
            {"value": {"__type__": "Range", "encoding_id": "ns=0;i=884",
                       "fields": {"Low": 0.0, "High": 600.0}}},
            _RANGE,
        )
        self.assertEqual(dv.Value.VariantType, ua.VariantType.ExtensionObject)
        self.assertIsInstance(dv.Value.Value, ua.Range)
        self.assertAlmostEqual(dv.Value.Value.Low, 0.0)
        self.assertAlmostEqual(dv.Value.Value.High, 600.0)

    def test_enum_value_type(self):
        dv = decode_exported_value(
            {"value": {"__type__": "EnumValueType",
                       "fields": {"Value": 3,
                                  "DisplayName": {"text": "SnapshotPeriodEnum", "locale": "en-US"},
                                  "Description": {"text": "2880ms", "locale": "en-US"}}}},
            _ENUM,
        )
        self.assertEqual(dv.Value.VariantType, ua.VariantType.ExtensionObject)
        self.assertIsInstance(dv.Value.Value, ua.EnumValueType)
        self.assertEqual(dv.Value.Value.Value, 3)
        self.assertEqual(dv.Value.Value.DisplayName.Text, "SnapshotPeriodEnum")


class TimestampTests(unittest.TestCase):
    def test_startup_timestamp_mode(self):
        dv = make_data_value_for_init(True, _BOOLEAN, timestamp_mode="startup")
        self.assertIsNotNone(dv.SourceTimestamp)
        self.assertIsNotNone(dv.ServerTimestamp)

    def test_preserve_timestamp_mode(self):
        dv = make_data_value_for_init(True, _BOOLEAN, timestamp_mode="preserve")
        self.assertIsNone(dv.SourceTimestamp)
        self.assertIsNone(dv.ServerTimestamp)


if __name__ == "__main__":
    unittest.main()