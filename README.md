# OPC UA Rebuild Server

A re-implementation of the SUPCON OPC UA server for development and
testing, built on `asyncua`.

## Install

```bash
python -m pip install -r requirements-rebuild.txt
```

`requirements-rebuild.txt` pins `asyncua==1.1.8` so the build is
reproducible across Linux and Windows.

## Start the static server

```bash
python ua_rebuild_server.py \
  --scope all-sov \
  --host 0.0.0.0 \
  --port 18639
```

This command:

* Aligns `NamespaceArray` with the SUPCON export (`ns=0` … `ns=6`)
* Creates the type closure for `SolenoidValveType`,
  `DiagnosisVariableType` and `FunctionalGroupType` plus their
  declarations
* Creates 105 instance nodes: `DeviceSetView` plus 13 nodes for each
  of SOV1 … SOV8
* Adds the modelling-rule, has-component, has-property,
  has-subtype and has-type-definition references the address space
  actually needs
* Opens an OPC UA endpoint at `opc.tcp://<host>:18639/ua-rebuild/`

## Start the dynamic simulator

```bash
python ua_rebuild_server.py \
  --scope all-sov \
  --host 0.0.0.0 \
  --port 18639 \
  --enable-simulation \
  --tick-ms 250 \
  --snapshot-interval-ms 1000 \
  --seed 12345
```

* Each tick: every SOV's `Current` is updated as a `Float` between
  `0.0` and `600.0`, computed from a per-device sine wave plus small
  random noise
* Each `snapshot-interval-ms`: a 1440-byte `ByteString` snapshot is
  written to every SOV's `ActionSnapshot`
* OPC UA subscribers see the changes as `DataChangeNotification`s

The simulator writes through the asyncua **internal** Server
(`iserver.write_attribute_value`) so that `AccessLevel = 1`
(read-only) on the client side is preserved — clients still cannot
write to `Current` or `ActionSnapshot`.

## UAExpert connect

```text
Endpoint: opc.tcp://<host>:18639/ua-rebuild/
```

A fresh project is recommended to avoid caching stale address spaces.

## Profiles

| Profile | ApplicationUri                  | Use case                |
|---------|----------------------------------|-------------------------|
| `debug` | `urn:ua-rebuild:debug`           | Day-to-day development  |
| `clone` | `http://SUPCON.UAServer.Application` | Mimics the real SUPCON server |

`clone` is required if the client caches Server certificates by
ApplicationUri.  `debug` avoids that constraint.

## Scopes

| Scope             | Contents                                             |
|-------------------|------------------------------------------------------|
| `namespace-smoke` | 6 hand-picked nodes (Objects / DeviceSetView / SOV1 / AssetId / Runtime / Current / EURange) |
| `sov1`            | SOV1 subtree + minimal type closure (Phase 2)        |
| `all-sov`         | All 8 SOVs + full type closure (Phase 3+, default)     |
| `full-custom`     | Every non-builtin custom node in the export           |

## Implemented

* Real `NamespaceArray` (7 namespaces matching the SUPCON export)
* Real `NodeId`, `BrowseName`, `BrowseName.NamespaceIndex`
* Real `DisplayName`, `Description`, `WriteMask`, `UserWriteMask`
* Real `TypeDefinition` per instance (`SolenoidValveType`,
  `FunctionalGroupType`, `AnalogItemType`, `PropertyType`, etc.)
* Real `DataType`, `ValueRank`, `AccessLevel`, `MinimumSamplingInterval`,
  `Historizing`
* `EventNotifier` for Objects
* `Range` (`Low`, `High`), `EnumValueType` (`Value`, `DisplayName`,
  `Description`), `ByteString` value payloads
* `HasModellingRule` references (`Mandatory`, `Optional`, etc.)
* Multi-namespace binding (verified end-to-end with an external
  `asyncua` Client and exercised via UAExpert manually)
* Current and ActionSnapshot dynamic simulation
* OPC UA Subscription / DataChange notification

## Not implemented

* Non-SOV address space (Server Diagnostics, Aliases, Publish/Subscribe,
  History Server Capabilities, etc.)
* All 13,467 references in the source export — only the references
  required for the SOV subtrees are restored
* GUI
* Open-source replacement of `asyncua` (e.g. open62541)
* Full OPC UA Server conformance test certification
* Reads of `ServerStatus.CurrentTime` etc. remain on the default
  asyncua clock and may drift relative to a host clock; the
  simulator's SourceTimestamp is the wall-clock at the write moment,
  not the value's actual acquisition time

These items do not affect the current SOV-simulation goal.

## Tests

```bash
python -m unittest discover -s tests -v
```

* `test_phase1_integration.py` — namespace smoke test
* `test_phase2_integration.py` — SOV1 subtree test
* `test_phase3_integration.py` — all-sov static test
* `test_final_dynamic_server.py` — dynamic subscription test
* `test_nodeid_codec.py`, `test_value_codec.py`,
  `test_model_validator.py`, `test_build_planner.py`,
  `test_server_integration.py` — unit and CLI tests

`process_harness.py` is the single supported way for tests to spawn
and tear down the server.  Earlier Phase 1/2/3 tests are gradually
being migrated onto it.

## Repository layout

```text
ua_full_exporter.py        — Phase 0 exporter; writes real_server_export_v2.json
real_server_export_v2.json — the model consumed by the server
ua_rebuild_server.py       — CLI entry point
ua_rebuild/
  config.py                — constants
  model.py                 — dataclasses
  model_loader.py          — load + index the export
  model_validator.py       — validate the export
  build_planner.py         — compute BuildPlan for a scope
  nodeid_codec.py          — NodeId text -> ua.NodeId
  value_codec.py           — value dict -> ua.DataValue
  asyncua_adapter.py       — thin asyncua wrapper (Phase 1+)
  namespace_fix.py         — apply the real NamespaceArray (Phase 1)
  instance_builder.py      — Phase 1 smoke builder
  full_instance_builder.py — Phase 2+ instance builder
  type_builder.py          — Phase 2+ type builder
  reference_builder.py     — Phase 2+ reference builder
  self_check.py           — Phase 1+ SelfCheck
  external_verifier.py    — Phase 2+ external verifier
  phase3_report.py        — Phase 3 report generator
  runtime_registry.py     — Phase 4 registry
  simulator.py            — Phase 4 simulator
  ready_signal.py         — Phase 4 ready-file helpers
  graceful_shutdown.py    — Phase 4 signal handlers
tests/
  process_harness.py
  test_*.py
FINAL_ACCEPTANCE_REPORT.md — Phase 4 acceptance report
```

## Validation pipeline

```bash
python -m unittest discover -s tests -v
```

This is the canonical check.  Phase 0 dry-runs are available via:

```bash
python ua_rebuild_server.py --model real_server_export_v2.json \
  --scope all-sov --dry-run
```

which prints the BuildPlan without starting the server.