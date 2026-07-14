---
task_id: CAN-20260714-tibia-system-decomposition-engine-foundation
program_id: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
coordination_id: REAL-TIBIA-SYSTEM-DECOMPOSITION-TSD-002A
status: active
agent: "GPT-5.6 Thinking"
branch: docs/tibia-system-decomposition-engine-foundation
base_branch: main
created: 2026-07-14T17:50:00+02:00
updated: 2026-07-14T17:50:00+02:00
last_verified_commit: "6d368766cc47794ec0145b4b32613edaf7588adb"
risk: low
related_issue: ""
related_pr: ""
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
    - docs/agents/real-tibia/TIBIA_SYSTEM_DECOMPOSITION_REPORT.md
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
  - engine-runtime-lifecycle
  - configuration
  - lua-runtime
reuses:
  - existing Real Tibia registry-as-code
  - existing deterministic generator and lookup/affected commands
  - source-role-aware Upstream Intelligence mapper
public_interfaces:
  - bounded engine-foundation module discovery records
cross_repo_tasks: []
---

# Goal

Complete TSD-002A as a bounded engine-foundation inventory. Reclassify `engine-scheduler`, `engine-service-container`, `lua-bindings`, `data-registries`, `build-system` and `platform-compatibility`, add only records with durable boundaries and verified current paths, and leave database/persistence/transaction candidates for a later TSD-002B task.

# Why TSD-002 was split

The original TSD-002 candidate set combines engine infrastructure with database and persistence boundaries. Current open PR #308 actively changes schema, migrations and multichannel DB/runtime code. Mixing that moving persistence evidence with stable engine discovery would make the package too broad and could create misleading path or relationship decisions.

Therefore:

- `TSD-002A` owns engine foundation only;
- `TSD-002B` will inventory database connection, migrations, transaction boundaries, world/player persistence and save/restart/reload only after TSD-002A is merged and archived and current `main` is re-read;
- the two implementation PRs will never be open concurrently.

# Exact base and preflight

- Task-start main: `6d368766cc47794ec0145b4b32613edaf7588adb`.
- PR #338 is merged and the source-role-aware prerequisite is archived.
- Open PRs inspected: #339, #316, #308 and #245.
- No open PR modifies `docs/agents/real-tibia/**`.
- PR #308 modifies database/migration/runtime paths; those paths remain read-only and deferred to TSD-002B.
- PR #339 modifies protocol connection/runtime paths; those paths remain read-only.
- PR #245 owns physical-client E2E paths; this task adds no E2E scenarios or orchestration.
- `ACTIVE_WORK.md` remains read-only.

# Candidate decisions required

Every candidate must receive one final TSD-002A decision:

```text
ADD_NOW
ALREADY_COVERED
KEEP_AS_UMBRELLA
MERGE_WITH_ANOTHER_MODULE
DEFER
REJECT_AS_TOO_GRANULAR
```

Candidates:

- `engine-scheduler`;
- `engine-service-container`;
- `lua-bindings`;
- `data-registries`;
- `build-system`;
- `platform-compatibility`.

No record may be added merely because a class, directory or build file exists.

# Acceptance criteria

- [ ] Current implementation paths and lifecycle boundaries are inventoried from exact task-start main.
- [ ] All six candidates receive explicit decisions and reasons.
- [ ] New records use only stable verified paths; no narrow module receives `src/**`.
- [ ] Existing `engine-runtime-lifecycle`, `configuration` and `lua-runtime` records remain compatible.
- [ ] New maturity starts at lifecycle/implementation/evidence `inventory`; all other dimensions remain `not-assessed` unless exact narrow evidence justifies otherwise.
- [ ] Source-aware server mapping tests assert correct modules and exclude client-only buckets.
- [ ] Generated indexes remain exact deterministic generator output.
- [ ] Registry validation, generation check, stale, module, lookup-path, affected and dependency graph validation pass.
- [ ] All registry and Upstream Intelligence focused tests pass.
- [ ] Ownership and required repository CI pass on the exact final head and ready-state head.
- [ ] No database/persistence record is added or modified in TSD-002A.
- [ ] No gameplay, runtime, C++, Lua gameplay, protocol implementation, client, DB, map, OTBM, datapack, asset, watcher or E2E change occurs.

# Safety boundary

This task is documentation, registry metadata, generated navigation and focused discovery tests only. It does not refactor scheduler/services/Lua/build code, change startup behavior, alter dependency injection, modify compiler/platform support, claim runtime correctness, or implement Oteryn.

# Handoff

After the TSD-002A feature PR passes exact-head and ready-state gates, squash merge it and create a separate lifecycle-only archive PR. Only after that archive merges may `CAN-20260714-tibia-system-decomposition-persistence-transactions` / TSD-002B begin from then-current `main`.
