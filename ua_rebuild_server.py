"""ua_rebuild_server.py

Phase 0 entry point: validate the export and print the BuildPlan.
Phase 1+ will start a real asyncua Server.

Usage:
    python ua_rebuild_server.py --model real_server_export_v2.json --scope sov1
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from ua_rebuild.build_planner import plan_for_scope
from ua_rebuild.model_validator import validate_export
from ua_rebuild.model_loader import load_export


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("ua_rebuild_server")


def main() -> int:
    parser = argparse.ArgumentParser(description="OPC UA Server rebuild (asyncua)")
    parser.add_argument("--model", default="real_server_export_v2.json",
                        help="Path to the exported model JSON")
    parser.add_argument("--scope", default="namespace-smoke",
                        choices=["namespace-smoke", "sov1", "all-sov", "full-custom"],
                        help="Rebuild scope")
    parser.add_argument("--host", default="0.0.0.0", help="(Phase 1+) listen host")
    parser.add_argument("--port", type=int, default=18639, help="(Phase 1+) listen port")
    parser.add_argument("--profile", default="debug",
                        choices=["debug", "clone"], help="(Phase 1+) server identity profile")
    parser.add_argument("--enable-simulation", action="store_true",
                        help="(Phase 4+) enable dynamic simulator")
    parser.add_argument("--output", help="(Optional) write BuildPlan to this JSON file")
    parser.add_argument("--dry-run", action="store_true",
                        help="Phase 0: validate + plan only, do not start a server")
    args = parser.parse_args()

    log.info("[MODEL] loading %s", args.model)
    model = load_export(args.model)
    log.info("[MODEL] schema_version=%s nodes=%d types=%d refs=%d",
             model.schema_version, len(model.nodes_by_text),
             len(model.types_by_text), len(model.raw_references))

    log.info("[VALIDATE] checking export")
    res = validate_export(model)
    for w in res.warnings:
        log.warning("[VALIDATE] %s", w)
    for i in res.info:
        log.info("[VALIDATE] %s", i)
    for f in res.fatal:
        log.error("[VALIDATE] %s", f)

    if not res.fatal_or_ok():
        log.error("[VALIDATE] %d fatal errors; aborting", len(res.fatal))
        return 1
    log.info("[VALIDATE] OK: %s", res.summary())

    log.info("[PLAN] scope=%s", args.scope)
    plan = plan_for_scope(args.model, args.scope)
    log.info("[PLAN] reused=%d custom_types=%d declarations=%d instances=%d refs=%d",
             len(plan.reused_standard_nodes), len(plan.custom_type_nodes),
             len(plan.type_declaration_nodes), len(plan.instance_nodes),
             len(plan.references_to_add))

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(
            json.dumps(plan.to_jsonable(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        log.info("[PLAN] wrote %s", args.output)

    # Phase 0 always exits here (server start is Phase 1+).
    if args.dry_run or True:
        log.info("[PHASE 0] dry run complete; server start deferred to Phase 1+")
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())