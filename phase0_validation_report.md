# Phase 0 Validation Report

## 1. Test Summary

- Total tests: **50**
- Passed: **50**
- Failures: **0**
- Errors: **0**

## 2. Per-Scope Counts

| Scope | Result | Custom Types | Declarations | Instances | Reused | References | Refs-to-add | Expected-existing | Creation order |
|-------|--------|-------------:|-------------:|----------:|-------:|-----------:|------------:|------------------:|---------------:|
| namespace-smoke | PASS | 17 | 69 | 6 | 1 | 492 | 335 | 157 | 93 |
| sov1 | PASS | 18 | 70 | 14 | 1 | 528 | 365 | 163 | 103 |
| all-sov | PASS | 18 | 70 | 105 | 1 | 745 | 526 | 219 | 194 |

## 3. SOV1 Scope Devices

Devices in `sov1` scope: ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch1

## 4. All-SOV Scope Devices

Devices in `all-sov` scope: ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch1, ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch2, ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch3, ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch4, ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch5, ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch6, ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch7, ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch8

## 5. Validation Counts (must all be 0)

| Metric | Value |
|--------|------:|
| Export fatal errors       | 0 |
| Export warnings           | 0 |
| Self-parent (raw)         | 0 |
| Orphan parent_node_id     | 0 |
| Plan self-parent           | 0 |
| Plan self-TypeDefinition   | 0 |
| Plan orphan TypeDefinition | 0 |
| Plan orphan parent         | 0 |
| Topological sort errors    | 0 |

## 6. Plan Files Generated

- `build_plan_namespace-smoke.json`
- `build_plan_sov1.json`
- `build_plan_all-sov.json`

## 7. Notes

- `_is_standard_builtin()` accepts ONLY `ns=0` numeric NodeIds.
  `ns=2;i=85` and `ns=4;i=68` are correctly classified as custom.
- Type closure walks `parent_reference_by_child`, `supertype_by_subtype`
  and `declarations_by_owner` indices; instance `children_by_parent`
  is NEVER consulted during type closure expansion.
- Each declaration's TypeDefinition is captured via the
  `type_definition_by_node` index, never guessed from the name.
- Creation order is produced by Kahn's topological sort over the
  real dependency graph (parent instance, parent type, declaration
  owner, TypeDefinition); never by NodeId string comparison.