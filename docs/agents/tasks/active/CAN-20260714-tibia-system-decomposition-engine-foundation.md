---
task_id: CAN-20260714-tibia-system-decomposition-engine-foundation
program_id: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
coordination_id: REAL-TIBIA-SYSTEM-DECOMPOSITION-TSD-002A
status: active
agent: "GPT-5.6 Thinking"
branch: docs/tibia-system-decomposition-engine-foundation
base_branch: main
created: 2026-07-14T17:50:00+02:00
updated: 2026-07-14T18:12:00+02:00
last_verified_commit: "eed25aa207418d3bd6cbf8b32d5162629a7163c0"
risk: low
related_issue: ""
related_pr: "340"
depends_on:
  - completed TSD-001 feature and lifecycle cycles
  - completed UI-001A source-role-aware mapping feature and lifecycle cycles
blocks:
  - CAN-20260714-tibia-system-decomposition-persistence-transactions
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260714-tibia-system-decomposition-engine-foundation.md
    - docs/agents/real-tibia/TSD_002A_ENGINE_FOUNDATION_REPORT.md
    - docs/agents/real-tibia/registry/modules/engine-scheduler.yaml
    - docs/agents/real-tibia/registry/modules/engine-service-container.yaml
    - docs/agents/real-tibia/registry/modules/lua-bindings.yaml
    - docs/agents/real-tibia/registry/modules/build-system.yaml
  shared:
    - docs/agents/programs/TIBIA_SYSTEM_DECOMPOSITION_PROGRAM.md
    - docs/agents/real-tibia/generated/**
    - tools/agents/test_real_tibia_registry.py
    - tools/agents/test_upstream_intelligence_decomposition.py
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - AGENTS.md
    - docs/agents/ACTIVE_WORK.md
    - docs/agents/real-tibia/TAXONOMY.md
    - docs/agents/real-tibia/MATURITY_MODEL.md
    - docs/agents/real-tibia/registry/categories.yaml
    - docs/agents/real-tibia/registry/schemas/**
    - docs/agents/real-tibia/registry/modules/engine-runtime-lifecycle.yaml
    - docs/agents/real-tibia/registry/modules/configuration.yaml
    - docs/agents/real-tibia/registry/modules/lua-runtime.yaml
    - docs/agents/real-tibia/registry/modules/player-persistence.yaml
    - docs/agents/upstream/**
    - tools/agents/real_tibia_registry*.py
    - tools/agents/upstream_intelligence*.py
    - .github/workflows/**
    - src/**
    - data/**
    - tests/**
    - CMakeLists.txt
    - CMakePresets.json
    - cmake/**
    - vcproj/**
modules_touched:
  - Real Tibia module registry
  - build-system
  - engine-scheduler
  - engine-service-container
  - lua-bindings
reuses:
  - existing Real Tibia registry-as-code
  - existing deterministic generator and lookup/affected commands
  - source-role-aware Upstream Intelligence mapper
public_interfaces:
  - bounded engine-foundation module discovery records
cross_repo_tasks: []
---

# Goal

Complete TSD-002A as a bounded engine-foundation inventory. Reclassify `engine-scheduler`, `engine-service-container`, `lua-bindings`, `data-registries`, `build-system` and `platform-compatibility`, add only records with durable boundaries and verified current paths, and leave database/persistence/transaction candidates for TSD-002B.

# Why TSD-002 was split

The original TSD-002 candidate set combined engine infrastructure with database and persistence boundaries. Task-start open PR #308 actively changed schema, migrations and multichannel DB/runtime code. Mixing that moving persistence evidence with stable engine discovery would have made one package too broad and risked misleading path and relationship decisions.

Therefore:

- `TSD-002A` owns engine foundation only;
- `TSD-002B` will inventory database connection, migrations, transaction boundaries, world/player persistence, reconciliation and save/restart/reload only after TSD-002A is merged and archived and current `main` is re-read;
- the two feature PRs are never open concurrently.

# Exact base and preflight

- Task-start main: `6d368766cc47794ec0145b4b32613edaf7588adb`.
- PR #338 was merged and the source-role-aware prerequisite was archived before this branch was created.
- Open PRs inspected at task start: #339, #316, #308 and #245.
- None modified `docs/agents/real-tibia/**`.
- PR #308 changed database/migration/runtime paths; those paths stayed read-only and were deferred to TSD-002B.
- PR #339 changed protocol connection/runtime paths; those paths stayed read-only.
- PR #245 owned physical-client E2E paths; this task added no E2E scenarios or orchestration.
- `ACTIVE_WORK.md` remained read-only.

# Candidate decisions

| Candidate | Decision | Result |
|---|---|---|
| `engine-scheduler` | `ADD_NOW` | Added a narrow dispatcher/task/thread-pool lifecycle record. |
| `engine-service-container` | `ADD_NOW` | Added a narrow DI container and lifetime-contract record. |
| `lua-bindings` | `ADD_NOW` | Added a narrow Lua function-registration and conversion-surface record. |
| `data-registries` | `MERGE_WITH_ANOTHER_MODULE` | Loader ordering stays in `engine-runtime-lifecycle`; loaded registries stay in functional modules. |
| `build-system` | `ADD_NOW` | Added one CMake/vcpkg/preset/Visual Studio/required-build-gate record. |
| `platform-compatibility` | `MERGE_WITH_ANOTHER_MODULE` | Platform/compiler/CPU support remains a capability and evidence queue inside `build-system`. |

Detailed evidence, verified paths, exclusions and limitations are in `docs/agents/real-tibia/TSD_002A_ENGINE_FOUNDATION_REPORT.md`.

# Delivered registry result

- Registry records: 22 → 26.
- Added only:
  - `build-system`;
  - `engine-scheduler`;
  - `engine-service-container`;
  - `lua-bindings`.
- Existing records modified: 0.
- `player-persistence` remained byte-for-byte unchanged by this task.
- Categories, registry schema, generator and source-aware mapper remained unchanged.
- Generated indexes were updated through the existing deterministic generator contract and passed `generate --check`.

# Maturity and relationships

Every new record starts at:

```text
lifecycle: inventory
implementation: inventory
evidence: inventory
persistence: not-assessed
protocol: not-assessed
automated_tests: not-assessed
runtime_validation: not-assessed
gameplay_e2e: not-assessed
```

Only `lua-bindings` has a `depends_on` edge, to `lua-runtime`. Other cross-boundary references are descriptive `interacts_with` edges. Dependency graph validation remains acyclic.

# Validation history

Implementation/focused-test head `d9c860048dc755291b97fead4c12398f72e17e53`:

- Real Tibia Module Registry #128: success;
- focused registry tests: success;
- schema and relationship validation: success;
- deterministic `generate --check`: success;
- stale/module/lookup-path/affected discovery commands: success;
- Upstream Intelligence #156: success;
- Agent Task Ownership #980: success.

Reviewed documentation/catalogue head `eed25aa207418d3bd6cbf8b32d5162629a7163c0`:

- Real Tibia Module Registry #130: success;
- Upstream Intelligence #158: success;
- Agent Task Ownership #983: success;
- repository CI #2095: success.

The later changelog and task-record commits are documentation-only. This task record cannot embed the SHA of the commit containing itself; live PR #340 metadata and exact-head workflows are authoritative for the final readiness and merge gate.

# Acceptance criteria

- [x] Current implementation paths and lifecycle boundaries were inventoried from exact task-start main.
- [x] All six candidates received explicit decisions and reasons.
- [x] New records use only stable verified paths; no narrow server module uses `src/**`.
- [x] Existing `engine-runtime-lifecycle`, `configuration`, `lua-runtime` and `player-persistence` records remain unchanged and compatible.
- [x] New maturity is conservative inventory/not-assessed.
- [x] Source-aware server mapping tests assert correct modules and exclude client-only buckets.
- [x] Generated indexes match exact deterministic generator output.
- [x] Registry validation, generation check, stale, module, lookup-path, affected and dependency graph validation pass.
- [x] All registry and Upstream Intelligence focused tests pass.
- [x] Ownership and required repository CI passed on reviewed implementation/documentation heads.
- [ ] Exact final live head and ready-state CI must pass before squash merge.
- [x] No database/persistence record was added or modified.
- [x] No gameplay, runtime, C++, Lua gameplay, protocol implementation, client, DB, map, OTBM, datapack, asset, watcher or E2E change occurred.

# Safety and known limitations

This task is documentation, registry metadata, deterministic generated navigation and focused discovery tests only. It does not prove scheduler fairness or race safety, DI lifetime correctness, Lua binding safety, platform portability, restart/reload safety, persistence correctness, Real Tibia parity, physical-client E2E or Oteryn readiness.

# Handoff

After PR #340 passes exact final-head checks, changed-file and review-thread inspection, mark it ready, pass the ready-state Linux/Required gate and squash merge. Then create a separate lifecycle-only archive PR. Only after that archive merges may this next task begin from then-current `main`:

```text
task: CAN-20260714-tibia-system-decomposition-persistence-transactions
package: TSD-002B
branch: docs/tibia-system-decomposition-persistence-transactions
```
