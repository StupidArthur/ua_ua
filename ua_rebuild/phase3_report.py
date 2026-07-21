"""Generate Phase 3 reports from the live server."""

import argparse
import asyncio
import json
import logging
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ua_rebuild.build_planner import plan_for_scope
from ua_rebuild.external_verifier import (
    ExternalVerifier, all_sov_targets_from_plan,
)
from ua_rebuild.model_loader import load_export


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("phase3_reports")


def _device_name(path: str) -> str:
    parts = path.split("/")
    if len(parts) >= 3 and parts[2].startswith("SOV"):
        return parts[2]
    return "shared"


def _summarize_per_device(summary: dict) -> dict[str, dict]:
    by_device: dict[str, dict] = defaultdict(lambda: {
        "expected_nodes": 0,
        "found_nodes": 0,
        "missing_nodes": 0,
        "attribute_good": 0,
        "attribute_bad": 0,
        "type_definition_matches": 0,
        "type_definition_mismatches": 0,
        "data_type_matches": 0,
        "data_type_mismatches": 0,
        "value_decode_failures": 0,
        "reference_mismatches": 0,
    })
    for node in summary["nodes"]:
        dev = _device_name(node["label"])
        s = by_device[dev]
        s["expected_nodes"] += 1
        if not node.get("exists", True):
            s["missing_nodes"] += 1
            continue
        s["found_nodes"] += 1
        for a in node["attributes"]:
            if a["status"] == "Good":
                s["attribute_good"] += 1
            else:
                s["attribute_bad"] += 1
        if node.get("type_definition"):
            s["type_definition_matches"] += 1
        if node.get("data_type"):
            s["data_type_matches"] += 1
        # A null value is legitimate (StatusCode=Good, value=null).
        # We only count it as a failure if there were bad attributes on
        # the Value read itself.
        if node.get("value_decoded"):
            v = node["value_decoded"]
            bad_value_read = any(
                a.get("attribute") == "Value" and a.get("status") != "Good"
                for a in node["attributes"]
            )
            if bad_value_read:
                s["value_decode_failures"] += 1
            elif v.get("kind") == "Exception" or v.get("kind") is None:
                s["value_decode_failures"] += 1
    return dict(by_device)


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=str(REPO_ROOT / "real_server_export_v2.json"))
    parser.add_argument("--url", default="opc.tcp://127.0.0.1:18639/ua-rebuild/")
    parser.add_argument("--scope", default="all-sov")
    parser.add_argument("--output-verification", default="phase3_verification_report.json")
    parser.add_argument("--output-comparison", default="phase3_device_comparison.md")
    args = parser.parse_args()

    model = load_export(args.model)
    plan = plan_for_scope(args.model, args.scope)
    targets = all_sov_targets_from_plan(plan)

    verifier = ExternalVerifier(args.url, targets=targets)
    summary = await verifier.run()

    summary["scope"] = args.scope
    summary["per_device"] = _summarize_per_device(summary)
    summary["devices_found"] = sorted(d for d in summary["per_device"] if d.startswith("SOV"))

    Path(args.output_verification).write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    log.info("Wrote %s", args.output_verification)

    # Build device comparison report
    by_device = summary["per_device"]
    md = []
    md.append("# Phase 3 Device Comparison")
    md.append("")
    md.append("## Per-device summary")
    md.append("")
    md.append("| Device | Expected | Found | Missing | Attr Good | Attr Bad | TD matches | DT matches | Value decode fail |")
    md.append("|--------|---------:|------:|--------:|----------:|---------:|-----------:|-----------:|-------------------:|")
    for dev in sorted(by_device):
        s = by_device[dev]
        md.append(f"| {dev} | {s['expected_nodes']} | {s['found_nodes']} | "
                 f"{s['missing_nodes']} | {s['attribute_good']} | "
                 f"{s['attribute_bad']} | {s['type_definition_matches']} | "
                 f"{s['data_type_matches']} | {s['value_decode_failures']} |")

    # Differences between devices: compare by label suffix
    by_label = defaultdict(dict)
    for node in summary["nodes"]:
        if not node.get("exists", True):
            continue
        parts = node["label"].split("/")
        if len(parts) >= 4 and parts[2].startswith("SOV"):
            suffix = "/".join(parts[3:])
            by_label[suffix][parts[2]] = node

    diffs_td: list[tuple[str, str, str, str]] = []
    diffs_dt: list[tuple[str, str, str, str]] = []
    diffs_vr: list[tuple[str, str, str, str]] = []
    diffs_rt: list[tuple[str, str, str, str]] = []
    for suffix, devs in sorted(by_label.items()):
        devices = sorted(devs)
        if len(devices) < 2:
            continue
        ref = devs[devices[0]]
        for d in devices[1:]:
            other = devs[d]
            if ref.get("type_definition") != other.get("type_definition"):
                diffs_td.append((suffix, devices[0], ref.get("type_definition"), d))
            if ref.get("data_type") != other.get("data_type"):
                diffs_dt.append((suffix, devices[0], ref.get("data_type"), d))
            if ref.get("value_rank") != other.get("value_rank"):
                diffs_vr.append((suffix, devices[0], str(ref.get("value_rank")), d))
            if ref.get("parent_ref_type_id") != other.get("parent_ref_type_id"):
                diffs_rt.append((suffix, devices[0], ref.get("parent_ref_type_id"), d))

    md.append("")
    md.append("## Cross-device differences")
    md.append("")
    md.append(f"TypeDefinition differences: **{len(diffs_td)}**")
    md.append(f"DataType differences:        **{len(diffs_dt)}**")
    md.append(f"ValueRank differences:       **{len(diffs_vr)}**")
    md.append(f"ReferenceType differences:   **{len(diffs_rt)}**")
    md.append("")
    if diffs_td:
        md.append("### TypeDefinition")
        for s, ref_dev, ref_val, other_dev in diffs_td:
            md.append(f"- `{s}`: {ref_dev}={ref_val} vs {other_dev}")
    if diffs_dt:
        md.append("")
        md.append("### DataType")
        for s, ref_dev, ref_val, other_dev in diffs_dt:
            md.append(f"- `{s}`: {ref_dev}={ref_val} vs {other_dev}")

    # Totals
    md.append("")
    md.append("## Totals")
    md.append("")
    md.append(f"- Good: {summary['totals']['good']}")
    md.append(f"- Bad:  {summary['totals']['bad']}")
    md.append(f"- Missing: {summary['totals']['missing']}")

    Path(args.output_comparison).write_text("\n".join(md), encoding="utf-8")
    log.info("Wrote %s", args.output_comparison)


if __name__ == "__main__":
    asyncio.run(main())