"""ua_verify_server.py

Phase 0 stub: validate the export and plan a verification scope.
Real external verification against a running server is implemented in Phase 1+.
"""

from __future__ import annotations

import argparse
import logging
import sys

from ua_rebuild.build_planner import plan_for_scope
from ua_rebuild.model_loader import load_export
from ua_rebuild.model_validator import validate_export


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("ua_verify_server")


def main() -> int:
    parser = argparse.ArgumentParser(description="External verification client")
    parser.add_argument("--model", default="real_server_export_v2.json")
    parser.add_argument("--url", default="opc.tcp://127.0.0.1:18639/ua-rebuild/",
                        help="OPC UA endpoint to connect to")
    parser.add_argument("--scope", default="namespace-smoke",
                        choices=["namespace-smoke", "sov1", "all-sov", "full-custom"])
    parser.add_argument("--output", default="verification_report.json")
    args = parser.parse_args()

    model = load_export(args.model)
    res = validate_export(model)
    if not res.fatal_or_ok():
        log.error("validation failed: %d fatal", len(res.fatal))
        return 1

    plan = plan_for_scope(args.model, args.scope)
    log.info("[VERIFY] planned %d nodes for scope=%s url=%s",
             len(plan.node_creation_order), args.scope, args.url)
    log.info("[VERIFY] Phase 0 stub; live verification implemented in Phase 1+")
    return 0


if __name__ == "__main__":
    sys.exit(main())