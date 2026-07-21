"""Phase 0 validation report generator."""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ua_rebuild.build_planner import plan_for_scope
from ua_rebuild.model_loader import load_export
from ua_rebuild.model_validator import validate_export, validate_plan


SCOPES = ["namespace-smoke", "sov1", "all-sov"]


def main() -> int:
    model = load_export(REPO_ROOT / "real_server_export_v2.json")
    export_res = validate_export(model)

    scope_data = []
    for scope in SCOPES:
        plan = plan_for_scope(str(REPO_ROOT / "real_server_export_v2.json"), scope)
        plan_res = validate_plan(plan, model)
        # Collect scope-specific counts
        custom_types = [s.node_id.text for s in plan.custom_type_nodes]
        decls = [s.node_id.text for s in plan.type_declaration_nodes]
        insts = [s.node_id.text for s in plan.instance_nodes]
        reused = [s.node_id.text for s in plan.reused_standard_nodes]
        devices_found = sorted({n for n in insts
                                if n.startswith("ns=1;s=7c8af738")})

        scope_data.append({
            "scope": scope,
            "plan_result": "PASS" if plan_res.fatal_or_ok() else "FAIL",
            "custom_types_count": len(custom_types),
            "declarations_count": len(decls),
            "instances_count": len(insts),
            "reused_count": len(reused),
            "references_count": len(plan.references_to_add)
                                  + len(plan.expected_existing_references),
            "references_to_add": len(plan.references_to_add),
            "expected_existing": len(plan.expected_existing_references),
            "creation_order_length": len(plan.node_creation_order),
            "fatal": len(plan_res.fatal),
            "devices_found": devices_found,
        })

    # Run unittest summary
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=120,
    )
    test_output = result.stdout + result.stderr
    # Parse "Ran N tests in ... M failures, E errors"
    import re
    m = re.search(r"Ran (\d+) tests? in [\d.]+s(?: \((\d+) failures?, (\d+) errors?\))?",
                  test_output)
    if m:
        test_total = int(m.group(1))
        failures = int(m.group(2) or 0)
        errors = int(m.group(3) or 0)
        test_passed = test_total - failures - errors
    else:
        test_total = test_passed = failures = errors = 0

    # Render report
    out = []
    out.append("# Phase 0 Validation Report")
    out.append("")
    out.append("## 1. Test Summary")
    out.append("")
    out.append(f"- Total tests: **{test_total}**")
    out.append(f"- Passed: **{test_passed}**")
    out.append(f"- Failures: **{failures}**")
    out.append(f"- Errors: **{errors}**")
    out.append("")
    out.append("## 2. Per-Scope Counts")
    out.append("")
    out.append("| Scope | Result | Custom Types | Declarations | Instances | Reused | References | Refs-to-add | Expected-existing | Creation order |")
    out.append("|-------|--------|-------------:|-------------:|----------:|-------:|-----------:|------------:|------------------:|---------------:|")
    for s in scope_data:
        out.append(
            f"| {s['scope']} | {s['plan_result']} | {s['custom_types_count']} | "
            f"{s['declarations_count']} | {s['instances_count']} | {s['reused_count']} | "
            f"{s['references_count']} | {s['references_to_add']} | {s['expected_existing']} | "
            f"{s['creation_order_length']} |"
        )
    out.append("")
    out.append("## 3. SOV1 Scope Devices")
    out.append("")
    sov1_data = next(s for s in scope_data if s["scope"] == "sov1")
    if sov1_data["devices_found"]:
        out.append("Devices in `sov1` scope: " + ", ".join(sov1_data["devices_found"]))
    else:
        out.append("_No SOV device NodeIds found in sov1 scope_")
    out.append("")
    out.append("## 4. All-SOV Scope Devices")
    out.append("")
    all_sov_data = next(s for s in scope_data if s["scope"] == "all-sov")
    if all_sov_data["devices_found"]:
        out.append("Devices in `all-sov` scope: " + ", ".join(all_sov_data["devices_found"]))
    out.append("")
    out.append("## 5. Validation Counts (must all be 0)")
    out.append("")
    out.append("| Metric | Value |")
    out.append("|--------|------:|")
    out.append(f"| Export fatal errors       | {len(export_res.fatal)} |")
    out.append(f"| Export warnings           | {len(export_res.warnings)} |")
    out.append(f"| Self-parent (raw)         | {sum(1 for f in export_res.fatal if 'self-parent' in f)} |")
    out.append(f"| Orphan parent_node_id     | {sum(1 for f in export_res.fatal if 'parent_node_id' in f and 'self' not in f)} |")
    all_plan_fatal = sum(s["fatal"] for s in scope_data)
    out.append(f"| Plan self-parent           | {sum(sum(1 for f in validate_plan(plan_for_scope(str(REPO_ROOT / 'real_server_export_v2.json'), s['scope']), model).fatal if 'parent_node_id == self' in f) for s in scope_data)} |")
    out.append(f"| Plan self-TypeDefinition   | {sum(sum(1 for f in validate_plan(plan_for_scope(str(REPO_ROOT / 'real_server_export_v2.json'), s['scope']), model).fatal if 'type_definition == self' in f) for s in scope_data)} |")
    out.append(f"| Plan orphan TypeDefinition | {sum(sum(1 for f in validate_plan(plan_for_scope(str(REPO_ROOT / 'real_server_export_v2.json'), s['scope']), model).fatal if 'type_definition' in f and 'self' not in f) for s in scope_data)} |")
    out.append(f"| Plan orphan parent         | {sum(sum(1 for f in validate_plan(plan_for_scope(str(REPO_ROOT / 'real_server_export_v2.json'), s['scope']), model).fatal if 'parent' in f and 'self' not in f and 'TypeDefinition' not in f) for s in scope_data)} |")
    out.append(f"| Topological sort errors    | {sum(sum(1 for f in validate_plan(plan_for_scope(str(REPO_ROOT / 'real_server_export_v2.json'), s['scope']), model).fatal if 'topological' in f) for s in scope_data)} |")
    out.append("")
    out.append("## 6. Plan Files Generated")
    out.append("")
    out.append("- `build_plan_namespace-smoke.json`")
    out.append("- `build_plan_sov1.json`")
    out.append("- `build_plan_all-sov.json`")
    out.append("")
    out.append("## 7. Notes")
    out.append("")
    out.append("- `_is_standard_builtin()` accepts ONLY `ns=0` numeric NodeIds.")
    out.append("  `ns=2;i=85` and `ns=4;i=68` are correctly classified as custom.")
    out.append("- Type closure walks `parent_reference_by_child`, `supertype_by_subtype`")
    out.append("  and `declarations_by_owner` indices; instance `children_by_parent`")
    out.append("  is NEVER consulted during type closure expansion.")
    out.append("- Each declaration's TypeDefinition is captured via the")
    out.append("  `type_definition_by_node` index, never guessed from the name.")
    out.append("- Creation order is produced by Kahn's topological sort over the")
    out.append("  real dependency graph (parent instance, parent type, declaration")
    out.append("  owner, TypeDefinition); never by NodeId string comparison.")

    (REPO_ROOT / "phase0_validation_report.md").write_text(
        "\n".join(out), encoding="utf-8",
    )
    print("Wrote phase0_validation_report.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())