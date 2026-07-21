"""ua_rebuild_server.py — asyncua-based rebuild server.

Supports four scopes (--scope):

    * namespace-smoke — 6 hard-coded Phase 1 smoke nodes
    * sov1           — full SOV1 subtree (Phase 2)
    * all-sov        — SOV1..SOV8 subtrees (Phase 3+)
    * full-custom    — every non-builtin node in the export

Two profiles:

    * debug  — ApplicationUri = urn:ua-rebuild:debug, easier UAExpert setup
    * clone  — ApplicationUri = http://SUPCON.UAServer.Application,
               matches the real SUPCON server

Optional simulation (Phase 4) populates Current + ActionSnapshot
dynamically when --enable-simulation is passed.

Ready-signal and graceful shutdown are wired in automatically.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path

from asyncua import Server

from ua_rebuild.asyncua_adapter import AsyncuaAddressSpaceAdapter
from ua_rebuild.graceful_shutdown import (
    cancel_background_tasks,
    install_signal_handlers,
    shutdown_simulator,
)
from ua_rebuild.instance_builder import InstanceBuilder
from ua_rebuild.namespace_fix import apply_namespace_array, EXPECTED_NAMESPACE_URIS
from ua_rebuild.ready_signal import write_ready_file, remove_ready_file
from ua_rebuild.runtime_registry import RuntimeRegistry, DeviceRuntime
from ua_rebuild.self_check import SelfCheck
from ua_rebuild.simulator import SimulatorConfig, SovSimulator


logging.basicConfig(
    level=logging.WARNING,
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


def _decode(text: str):
    from ua_rebuild.type_builder import _decode
    return _decode(text)


async def _build_runtime_registry(server, plan) -> RuntimeRegistry:
    """Resolve each SOV's Current and ActionSnapshot nodes and wire
    DeviceRuntime entries.  No NodeId derivation from SOV1 is allowed."""
    registry = RuntimeRegistry()
    by_name: dict[str, dict[str, object]] = {}
    for spec in plan.instance_nodes:
        path = spec.path or ""
        parts = path.split("/")
        if len(parts) < 4:
            continue
        device_name = parts[2]
        leaf = parts[-1]
        if not device_name.startswith("SOV"):
            continue
        by_name.setdefault(device_name, {})[leaf] = spec

    for name in sorted(by_name.keys()):
        leaves = by_name[name]
        current_spec = leaves.get("Current")
        snapshot_spec = leaves.get("ActionSnapshot")
        online_spec = leaves.get("OnlineState")
        fault_spec = leaves.get("FaultState")
        if current_spec is None or snapshot_spec is None:
            raise RuntimeError(
                f"{name}: required Current/ActionSnapshot leaf missing"
            )
        current_node = server.get_node(_decode(current_spec.node_id.text))
        snapshot_node = server.get_node(_decode(snapshot_spec.node_id.text))
        online_node = (server.get_node(_decode(online_spec.node_id.text))
                       if online_spec else None)
        fault_node = (server.get_node(_decode(fault_spec.node_id.text))
                      if fault_spec else None)

        initial_current = 0.0
        try:
            dv = await current_node.read_data_value()
            if dv and dv.Value and dv.Value.Value is not None:
                initial_current = float(dv.Value.Value)
        except Exception:
            pass

        device = DeviceRuntime(
            name=name,
            current_node=current_node,
            action_snapshot_node=snapshot_node,
            online_state_node=online_node,
            fault_state_node=fault_node,
            current_node_id=current_spec.node_id.text,
            action_snapshot_node_id=snapshot_spec.node_id.text,
            initial_current=initial_current,
        )
        registry.add(device)
        log.info(
            "[RUNTIME] %s Current=%s ActionSnapshot=%s",
            name, device.current_node_id, device.action_snapshot_node_id,
        )
    return registry


async def _run(args: argparse.Namespace) -> int:
    from ua_rebuild.build_planner import plan_for_scope
    from ua_rebuild.model_validator import validate_export, validate_plan
    from ua_rebuild.model_loader import load_export
    from ua_rebuild.type_builder import TypeBuilder
    from ua_rebuild.full_instance_builder import FullInstanceBuilder
    from ua_rebuild.reference_builder import ReferenceBuilder

    profile = PROFILES[args.profile]
    server = Server()
    await server.init()

    adapter = AsyncuaAddressSpaceAdapter(server)

    # NamespaceArray alignment
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

    model = load_export(args.model)
    plan = plan_for_scope(args.model, args.scope)
    plan_res = validate_plan(plan, model)
    if not plan_res.fatal_or_ok():
        log.error("[PLAN] validation failed:")
        for f in plan_res.fatal:
            log.error("  %s", f)
        return 1

    all_records = []
    simulator = None
    try:
        if args.scope == "namespace-smoke":
            builder = InstanceBuilder(adapter, args.model)
            records = await builder.build()
            all_records.extend(records)
        elif args.scope in ("sov1", "all-sov", "full-custom"):
            type_builder = TypeBuilder(adapter, plan, model)
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
            await type_builder.build_modelling_rules()
            ref_builder = ReferenceBuilder(adapter, plan)
            await ref_builder.build()
        else:
            log.error("[SCOPE] unsupported scope %s", args.scope)
            return 2

        # Runtime registry + simulator (Phase 4)
        runtime_registry = None
        if args.enable_simulation and args.scope in ("sov1", "all-sov", "full-custom"):
            try:
                runtime_registry = await _build_runtime_registry(server, plan)
                runtime_registry.require_complete()
                log.info("[RUNTIME] registry complete devices=%d",
                         len(runtime_registry.devices))
            except Exception as e:
                log.error("[RUNTIME] build failed: %s", e)
                write_ready_file(args.ready_file, {
                    "status": "failed",
                    "pid": os.getpid(),
                    "stage": "runtime_registry",
                    "error_type": type(e).__name__,
                    "error": str(e),
                })
                return 1

        fail = sum(1 for r in all_records if r.status_code.is_bad())
        log.info("[BUILD] created=%d failed=%d", len(all_records) - fail, fail)

        # SelfCheck
        self_check = SelfCheck(adapter, all_records)
        sc_summary = await self_check.run()

        # Endpoint
        endpoint = f"opc.tcp://{args.host}:{args.port}/ua-rebuild/"
        server.set_endpoint(endpoint)
        server.set_server_name(profile["application_name"])

        # Startup report
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report).write_text(
            json.dumps({
                "endpoint": endpoint,
                "namespace_array": actual_ns,
                "scope": args.scope,
                "build": {
                    "created": len(all_records) - fail,
                    "failed": fail,
                },
                "self_check": {
                    "good": sc_summary["good"],
                    "bad": sc_summary["bad"],
                },
                "runtime_devices": list(runtime_registry.devices) if runtime_registry else [],
            }, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
        log.info("[REPORT] wrote %s", args.report)

        # Start simulator AFTER the address space is fully populated and
        # the endpoint is configured.
        if runtime_registry is not None and args.enable_simulation:
            sim_cfg = SimulatorConfig(
                tick_ms=args.tick_ms,
                snapshot_interval_ms=args.snapshot_interval_ms,
                seed=args.seed,
            )
            simulator = SovSimulator(runtime_registry, sim_cfg, server.iserver)
            simulator.start()

        # Ready file — only after everything that could fail is done.
        devices_count = len(runtime_registry.devices) if runtime_registry else 0
        print("启动成功", flush=True)
        write_ready_file(args.ready_file, {
            "status": "ready",
            "pid": os.getpid(),
            "endpoint": endpoint,
            "scope": args.scope,
            "instances_created": len(all_records) - fail,
            "devices_registered": devices_count,
            "simulation_enabled": bool(simulator),
            "tick_ms": args.tick_ms,
            "snapshot_interval_ms": args.snapshot_interval_ms,
        })

        # Signal handlers
        async def _on_stop():
            log.info("[SHUTDOWN] beginning graceful stop")
            await shutdown_simulator(simulator)
            await cancel_background_tasks(timeout=2.0)

        install_signal_handlers(asyncio.get_event_loop(), _on_stop)

        async with server:
            log.info("[READY] %s", endpoint)
            log.info("[READY] scope=%s devices=%d simulation=%s",
                     args.scope, devices_count, "on" if simulator else "off")
            try:
                while True:
                    await asyncio.sleep(1)
            except asyncio.CancelledError:
                pass
        return 0

    finally:
        if simulator is not None:
            try:
                await shutdown_simulator(simulator)
            except Exception:
                pass
        remove_ready_file(args.ready_file)


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
    parser.add_argument("--ready-file", default=None,
                        help="path to write ready-signal JSON")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate and plan only, do not start the server")
    parser.add_argument("--enable-simulation", action="store_true",
                        help="Phase 4: drive Current/ActionSnapshot dynamically")
    parser.add_argument("--tick-ms", type=int, default=250,
                        help="simulation tick interval (ms)")
    parser.add_argument("--snapshot-interval-ms", type=int, default=1000,
                        help="simulation ActionSnapshot interval (ms)")
    parser.add_argument("--seed", type=int, default=12345,
                        help="RNG seed for the simulator")
    args = parser.parse_args()

    if args.dry_run:
        from ua_rebuild.build_planner import plan_for_scope
        from ua_rebuild.model_validator import validate_export
        from ua_rebuild.model_loader import load_export

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

    try:
        return asyncio.run(_run(args))
    except KeyboardInterrupt:
        log.warning("interrupted")
        return 130
    except Exception as e:
        log.exception("uncaught: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())