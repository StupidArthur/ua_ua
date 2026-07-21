"""ua_rebuild_server.py — Phase 1 namespace-smoke server.

Phase 1 launches a real asyncua Server, fixes the NamespaceArray to
match the export, creates the six smoke-test nodes with simplified
TypeDefinitions and lets the operator drive UAExpert against it.

Usage:

    python ua_rebuild_server.py \\
        --model real_server_export_v2.json \\
        --scope namespace-smoke \\
        --host 127.0.0.1 \\
        --port 18639 \\
        --profile debug

The `--scope` flag is accepted for forward compatibility but Phase 1
only implements `namespace-smoke`.  Other scopes abort with a clear
error.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

from asyncua import Server

from ua_rebuild.asyncua_adapter import AsyncuaAddressSpaceAdapter
from ua_rebuild.instance_builder import InstanceBuilder
from ua_rebuild.namespace_fix import apply_namespace_array, EXPECTED_NAMESPACE_URIS
from ua_rebuild.self_check import SelfCheck


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("ua_rebuild_server")


PROFILES: dict[str, dict[str, str]] = {
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


async def _run(args: argparse.Namespace) -> int:
    from ua_rebuild.build_planner import plan_for_scope
    from ua_rebuild.model_validator import validate_export, validate_plan
    from ua_rebuild.model_loader import load_export
    from ua_rebuild.type_builder import TypeBuilder
    from ua_rebuild.full_instance_builder import FullInstanceBuilder
    from ua_rebuild.reference_builder import ReferenceBuilder

    if args.dry_run:
        # Phase 0 style: validate + plan, then exit.
        model = load_export(args.model)
        log.info("[MODEL] schema=%s nodes=%d types=%d refs=%d",
                 model.schema_version, len(model.nodes_by_text),
                 len(model.types_by_text), len(model.raw_references))
        res = validate_export(model)
        if not res.fatal_or_ok():
            for f in res.fatal:
                log.error("[VALIDATE] %s", f)
            return 1
        plan = plan_for_scope(args.model, args.scope)
        log.info("[PLAN] reused=%d custom=%d decls=%d instances=%d refs=%d",
                 len(plan.reused_standard_nodes),
                 len(plan.custom_type_nodes),
                 len(plan.type_declaration_nodes),
                 len(plan.instance_nodes),
                 len(plan.references_to_add))
        log.info("[PHASE 0] dry run complete; server start deferred to Phase 1+")
        return 0

    profile = PROFILES[args.profile]
    server = Server()
    await server.init()

    adapter = AsyncuaAddressSpaceAdapter(server)

    # Step 1..4: align NamespaceArray with the real export.
    actual_ns = await apply_namespace_array(
        server,
        application_uri=profile["application_uri"],
        product_uri=profile["product_uri"],
        server_name=profile["application_name"],
        expected_uris=list(EXPECTED_NAMESPACE_URIS),
    )
    if actual_ns != EXPECTED_NAMESPACE_URIS:
        log.error("[NAMESPACE] mismatch; aborting")
        return 1

    # Step 5: build the requested scope.
    model = load_export(args.model)
    plan = plan_for_scope(args.model, args.scope)
    plan_res = validate_plan(plan, model)
    if not plan_res.fatal_or_ok():
        log.error("[PLAN] validation failed:")
        for f in plan_res.fatal:
            log.error("  %s", f)
        return 1

    all_records = []

    # Phase 1: hard-coded smoke scope.
    if args.scope == "namespace-smoke":
        builder = InstanceBuilder(adapter, args.model)
        records = await builder.build()
        all_records.extend(records)

    # Phase 2+: full BuildPlan-driven build driven by topo order.
    elif args.scope in ("sov1", "all-sov", "full-custom"):
        type_builder = TypeBuilder(adapter, plan, model)
        # Build specs by node_creation_order to honour parent-before-child
        # for both types and declarations.
        spec_by_text: dict[str, object] = {}
        for s in plan.custom_type_nodes + plan.type_declaration_nodes + plan.instance_nodes:
            spec_by_text[s.node_id.text] = s

        for nid_text in plan.node_creation_order:
            spec = spec_by_text.get(nid_text)
            if spec is None:
                continue
            if getattr(spec, "is_type_declaration", False):
                records = await type_builder.build_declaration(spec)
                all_records.extend(records)
            elif spec.node_class in ("ObjectType", "VariableType"):
                records = await type_builder.build_type(spec)
                all_records.extend(records)
            elif spec.node_class in ("Object", "Variable", "Method"):
                instance_builder = FullInstanceBuilder(adapter, plan)
                records = await instance_builder.build_one(spec)
                all_records.extend(records)

        # Modelling rules and references come last.
        await type_builder.build_modelling_rules()
        ref_builder = ReferenceBuilder(adapter, plan)
        ref_results = await ref_builder.build()
    else:
        log.error("[SCOPE] unsupported scope %s", args.scope)
        return 2

    fail = sum(1 for r in all_records if r.status_code.is_bad())
    log.info("[BUILD] created=%d failed=%d",
             len(all_records) - fail, fail)

    # SelfCheck
    self_check = SelfCheck(adapter, all_records)
    sc_summary = await self_check.run()

    # Endpoint
    endpoint = f"opc.tcp://{args.host}:{args.port}/ua-rebuild/"
    server.set_endpoint(endpoint)
    server.set_server_name(profile["application_name"])

    # Save startup summary for the operator.
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(
        json.dumps({
            "endpoint": endpoint,
            "namespace_array": actual_ns,
            "build": {
                "scope": args.scope,
                "created": len(all_records) - fail,
                "failed": fail,
                "records": [
                    {"requested": str(r.requested_node_id),
                     "added": str(r.added_node_id),
                     "status": r.status_code.name,
                     "node_class": r.node_class.name}
                    for r in all_records
                ],
            },
            "self_check": {
                "good": sc_summary["good"],
                "bad": sc_summary["bad"],
                "nodes": sc_summary["nodes"],
            },
        }, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    log.info("[REPORT] wrote %s", args.report)

    async with server:
        log.info("[READY] %s", endpoint)
        log.info("[READY] scope=%s ready for UAExpert", args.scope)
        try:
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="OPC UA Server rebuild (asyncua)")
    parser.add_argument("--model", default="real_server_export_v2.json",
                        help="Path to the exported model JSON")
    parser.add_argument("--scope", default="namespace-smoke",
                        choices=["namespace-smoke", "sov1", "all-sov", "full-custom"],
                        help="Rebuild scope")
    parser.add_argument("--host", default="127.0.0.1", help="listen host")
    parser.add_argument("--port", type=int, default=18639, help="listen port")
    parser.add_argument("--profile", default="debug",
                        choices=["debug", "clone"], help="server identity profile")
    parser.add_argument("--report", default="phase1_startup_report.json",
                        help="startup summary output")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate and plan only, do not start the server")
    args = parser.parse_args()

    try:
        return asyncio.run(_run(args))
    except KeyboardInterrupt:
        log.warning("interrupted")
        return 130


if __name__ == "__main__":
    sys.exit(main())