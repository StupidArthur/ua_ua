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
    from ua_rebuild.model_validator import validate_export
    from ua_rebuild.model_loader import load_export

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
        log.info("[PLAN] reused=%d custom=%d decls=%d instances=%d",
                 len(plan.reused_standard_nodes),
                 len(plan.custom_type_nodes),
                 len(plan.type_declaration_nodes),
                 len(plan.instance_nodes))
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

    # Step 5: build the Phase 1 smoke-test nodes.
    if args.scope != "namespace-smoke":
        log.error("[SCOPE] Phase 1 only implements namespace-smoke, got %s",
                  args.scope)
        return 2
    builder = InstanceBuilder(adapter, args.model)
    records = await builder.build()
    fail = sum(1 for r in records if r.status_code.is_bad())
    log.info("[BUILD] created=%d failed=%d",
             len(records) - fail, fail)

    # SelfCheck
    self_check = SelfCheck(adapter, records)
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
                "created": len(records) - fail,
                "failed": fail,
                "records": [
                    {"requested": str(r.requested_node_id),
                     "added": str(r.added_node_id),
                     "status": r.status_code.name,
                     "node_class": r.node_class.name}
                    for r in records
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
        log.info("[READY] ns=0/1/2/4 target nodes ready for UAExpert")
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