"""ua_rebuild package.

Reconstructs an OPC UA address space from `real_server_export_v2.json`
using asyncua as the underlying server framework.

Layered architecture:

    JSON model
       |
    ModelLoader + ModelValidator
       |
    BuildPlanner
       |
    AsyncuaAddressSpaceAdapter
       |
    TypeBuilder / InstanceBuilder / ReferenceBuilder
       |
    SelfCheck + ExternalVerifier
"""

__all__ = [
    "config",
    "model",
    "model_loader",
    "model_validator",
    "nodeid_codec",
    "value_codec",
    "build_planner",
    "asyncua_adapter",
    "type_builder",
    "instance_builder",
    "reference_builder",
    "attribute_writer",
    "runtime_registry",
    "simulator",
    "self_check",
    "external_verifier",
    "report_writer",
]