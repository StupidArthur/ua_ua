"""Project-wide configuration constants.

These values come from `real_server_export_v2.json`; they are kept here only
so that the loader/validator/builder can perform sanity checks.  The single
source of truth for runtime values is the exported JSON, never the constants
below.
"""

from __future__ import annotations

EXPECTED_NAMESPACE_URIS: list[str] = [
    "http://opcfoundation.org/UA/",
    "http://SUPCON.UAServer.Product",
    "http://supcon.com/UA",
    "http://opcfoundation.org/UA/Dictionary/IRDI",
    "http://opcfoundation.org/UA/DI/",
    "http://opcfoundation.org/UA/PADIM/",
    "http://www.OPCFoundation.org/UA/2013/01/ISA95",
]

EXPECTED_APPLICATION_URI: str = "http://SUPCON.UAServer.Application"
EXPECTED_PRODUCT_URI: str = "http://www.supcon.com"
EXPECTED_APPLICATION_NAME: str = "NeuroShellForCMS Server"

# Schema version of the export that this build understands.
SUPPORTED_SCHEMA_VERSION: str = "2.0"

# Server identity presets for the two build profiles.
PROFILES: dict[str, dict] = {
    "debug": {
        "application_name": "UA-Rebuild-Debug",
        "application_uri": "urn:ua-rebuild:debug",
        "product_uri": "urn:ua-rebuild",
    },
    "clone": {
        "application_name": "NeuroShellForCMS Server",
        "application_uri": "http://SUPCON.UAServer.Application",
        "product_uri": "http://www.supcon.com",
    },
}

# Reference type NodeIds used for filtering / short-circuit checks.
REF_ORGANIZES: int = 35
REF_HAS_TYPE_DEFINITION: int = 40
REF_HAS_SUBTYPE: int = 45
REF_HAS_PROPERTY: int = 46
REF_HAS_COMPONENT: int = 47
REF_HAS_MODELLING_RULE: int = 37
REF_HAS_DESCRIPTION: int = 39
REF_HAS_ENCODING: int = 38

# Modelling rule NodeIds in ns=0.
MODELLING_RULE_NODES: dict[str, int] = {
    "Mandatory": 78,
    "Optional": 80,
    "MandatoryPlaceholder": 11510,
    "OptionalPlaceholder": 11508,
    "ExposesItsArray": 11469,
}

# Phase 1 / smoke test scope: minimal set of nodes that prove multi-namespace
# binding works.  Each entry maps a key to the exported node's text id.
SMOKE_SCOPE_NODE_IDS: dict[str, str] = {
    "Objects": "i=85",
    "DeviceSetView": "ns=2;s=P_7765a8f78a9266d7a83581ba1b39176a",
    "SOV1": "ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch1",
    "AssetId": "ns=4;s=P_318b26d74fcca15eeb08a56d2f1b6f3a",
    "EURange": "ns=0;s=P_d96e61438d6080321565c5718839603d",
}

# Standard ns=0 NodeIds reused as TypeDefinitions / reference targets.
NS0_OBJECTS: int = 85
NS0_BASEOBJECTTYPE: int = 58
NS0_BASEDATAVARIABLETYPE: int = 63
NS0_PROPERTYTYPE: int = 68
NS0_FOLDERTYPE: int = 61
NS0_ANALOGITEMTYPE: int = 2368
NS0_MANDATORY: int = 78
NS0_OPTIONAL: int = 80

# Builtin standard ns=0 numeric NodeIds the rebuild may rely on without
# having to add them to the export.  Anything outside this set must appear
# in the export's types[] or be flagged as a fatal error.
STANDARD_NS0_NUMERIC: set[int] = {
    NS0_BASEOBJECTTYPE, NS0_BASEDATAVARIABLETYPE, NS0_PROPERTYTYPE,
    NS0_FOLDERTYPE, NS0_ANALOGITEMTYPE,
    NS0_OBJECTS,
    NS0_MANDATORY, NS0_OPTIONAL,
    11508,  # OptionalPlaceholder
    11510,  # MandatoryPlaceholder
    11469,  # ExposesItsArray
}