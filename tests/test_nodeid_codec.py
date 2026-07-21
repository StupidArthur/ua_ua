"""Tests for ua_rebuild.nodeid_codec."""

from __future__ import annotations

import sys
import unittest
import uuid

from asyncua import ua

sys.path.insert(0, r"F:\github\ua_ua")

from ua_rebuild.nodeid_codec import decode_node_id, _infer_type_from_text  # noqa: E402


class DecodeNodeIdTests(unittest.TestCase):
    def test_two_byte_in_ns0(self):
        nid = decode_node_id({
            "text": "i=85",
            "namespace_index": 0,
            "namespace_uri": "http://opcfoundation.org/UA/",
            "identifier_type": "TwoByte",
            "identifier": 85,
        })
        self.assertIsInstance(nid, ua.NodeId)
        self.assertEqual(nid.NamespaceIndex, 0)
        self.assertEqual(int(nid.Identifier), 85)

    def test_four_byte(self):
        nid = decode_node_id({
            "text": "ns=2;i=1110",
            "namespace_index": 2,
            "namespace_uri": "http://supcon.com/UA",
            "identifier_type": "FourByte",
            "identifier": 1110,
        })
        self.assertEqual(nid.NamespaceIndex, 2)
        self.assertEqual(int(nid.Identifier), 1110)

    def test_numeric(self):
        nid = decode_node_id({
            "text": "ns=4;i=1005",
            "namespace_index": 4,
            "namespace_uri": "http://opcfoundation.org/UA/DI/",
            "identifier_type": "Numeric",
            "identifier": 1005,
        })
        self.assertEqual(nid.NamespaceIndex, 4)
        self.assertEqual(int(nid.Identifier), 1005)

    def test_string(self):
        nid = decode_node_id({
            "text": "ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch1",
            "namespace_index": 1,
            "namespace_uri": "http://SUPCON.UAServer.Product",
            "identifier_type": "String",
            "identifier": "7c8af738ba72d0e9226c57c70ab0310d_ch1",
        })
        self.assertEqual(nid.NamespaceIndex, 1)
        self.assertEqual(str(nid.Identifier), "7c8af738ba72d0e9226c57c70ab0310d_ch1")

    def test_guid(self):
        g = uuid.uuid4()
        nid = decode_node_id({
            "text": f"ns=5;g={g}",
            "namespace_index": 5,
            "namespace_uri": "http://opcfoundation.org/UA/PADIM/",
            "identifier_type": "Guid",
            "identifier": str(g),
        })
        self.assertEqual(nid.NamespaceIndex, 5)
        self.assertEqual(str(nid.Identifier), str(g))

    def test_bytestring(self):
        nid = decode_node_id({
            "text": "ns=6;b=AAAA",
            "namespace_index": 6,
            "namespace_uri": "http://www.OPCFoundation.org/UA/2013/01/ISA95",
            "identifier_type": "ByteString",
            "identifier": "AAAA",
        })
        self.assertEqual(nid.NamespaceIndex, 6)
        self.assertEqual(bytes(nid.Identifier), b"\x00\x00\x00")

    def test_inference_from_text(self):
        self.assertEqual(_infer_type_from_text("i=85"), "TwoByte")
        self.assertEqual(_infer_type_from_text("ns=0;i=1110"), "Numeric")
        self.assertEqual(_infer_type_from_text("ns=2;i=1110"), "Numeric")
        self.assertEqual(_infer_type_from_text("ns=1;s=abc"), "String")
        self.assertEqual(_infer_type_from_text("ns=1;g=00000000-0000-0000-0000-000000000000"), "Guid")
        self.assertEqual(_infer_type_from_text("ns=1;b=AAAA"), "ByteString")

    def test_none_returns_none(self):
        self.assertIsNone(decode_node_id(None))


if __name__ == "__main__":
    unittest.main()