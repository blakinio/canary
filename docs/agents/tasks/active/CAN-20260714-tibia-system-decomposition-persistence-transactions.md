---
task_id: CAN-20260714-tibia-system-decomposition-persistence-transactions
program_id: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
coordination_id: REAL-TIBIA-SYSTEM-DECOMPOSITION-TSD-002B
status: active
agent: "GPT-5.6 Thinking"
branch: docs/tibia-system-decomposition-persistence-transactions
base_branch: main
created: 2026-07-14T18:24:00+02:00
updated: 2026-07-14T18:24:00+02:00
last_verified_commit: "709693b4cca42214c52e63ea15a1a22b93f9a113"
risk: low
related_issue: ""
related_pr: ""
depends_on:
  - completed and archived TSD-002A
blocks:
  - TSD-003 account, character and progression decomposition
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260714-tibia-system-decomposition-persistence-transactions.md
    - docs/agents/real-tibia/TSD_002B_PERSISTENCE_TRANSACTIONS_REPORT.md
    - docs/agents/real-tibia/registry/modules/database-connection.yaml
    - docs/agents/real-tibia/registry/modules/database-migrations.yaml
    - docs/agents/real-tibia/registry/modules/save-restart-reload.yaml
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
    - docs/agents/real-tibia/registry/modules/player-persistence.yaml
    - docs/agents/real-tibia/registry/modules/engine-runtime-lifecycle.yaml
    - docs/agents/real-tibia/registry/modules/engine-scheduler.yaml
    - docs/agents/real-tibia/registry/modules/configuration.yaml
    - docs/agents/upstream/**
    - tools/agents/real_tibia_registry*.py
    - tools/agents/upstream_intelligence*.py
    - .github/workflows/**
    - schema.sql
    - data-otservbr-global/migrations/**
    - src/database/**
    - src/io/**
    - src/game/scheduling/save_manager.*
    - src/canary_server.cpp
    - src/game/multichannel/**
    - tests/**
modules_touched:
  - Real Tibia module registry
  - player-persistence
reuses:
  - existing Real Tibia registry-as-code
  - existing deterministic generator and discovery commands
  - source-role-aware Upstream Intelligence mapper
public_interfaces:
  - bounded persistence and transaction discovery records
cross_repo_tasks: []
---

# Goal

Complete TSD-002B as a bounded persistence and transaction inventory over current `main`. Classify `database-connection`, `database-migrations`, `transaction-boundaries`, `world-persistence`, `database-reconciliation` and `save-restart-reload`, add only durable independent records with verified paths, and preserve `player-persistence` as the compatibility umbrella unless a narrower boundary is independently proven.

# Exact base and preflight

- Task-start main: `709693b4cca42214c52e63ea15a1a22b93f9a113`.
- TSD-002A feature and lifecycle cycles are merged.
- PR #308 is merged as `4de9350e62e2ca9ddf717e16628f87084a74aa86`; its code is current-main inventory evidence, but its PR claims do not prove transactionality or runtime safety.
- The still-active `CAN-20260714-cross-process-db-row-handoff` task owns its multichannel runtime paths; this task reads them only and makes no edit there.
- Open PRs inspected: #339, #316 and #245. None modifies `docs/agents/real-tibia/**`.
- PR #339 modifies connection/protocol runtime paths; those remain read-only.
- PR #245 owns physical-client E2E paths; no E2E scenario or orchestrator change is allowed.
- `ACTIVE_WORK.md` remains read-only.

# Candidate decisions required

Each candidate must receive exactly one bounded decision:

```text
ADD_NOW
ALREADY_COVERED
KEEP_AS_UMBRELLA
MERGE_WITH_ANOTHER_MODULE
DEFER
REJECT_AS_TOO_GRANULAR
```

Candidates:

- `database-connection`;
- `database-migrations`;
- `transaction-boundaries`;
- `world-persistence`;
- `database-reconciliation`;
- `save-restart-reload`.

# Acceptance criteria

- [ ] Current-main connection, query/result, transaction, migration, player/world save and startup/shutdown/reload paths are inventoried.
- [ ] All six candidates receive explicit decisions with exclusions and evidence limits.
- [ ] `player-persistence` remains the stable umbrella unless a safe independent child boundary is proven.
- [ ] New records use narrow verified paths; no narrow module uses `src/**`.
- [ ] Presence of DB classes, SQL, tests or migrations is not treated as proof of atomicity, rollback, crash safety, retry safety, idempotency, reconciliation, restart/reload safety or production MariaDB compatibility.
- [ ] New maturity starts at lifecycle/implementation/evidence `inventory`; all other dimensions remain `not-assessed`.
- [ ] Source-aware server mapping tests cover allowed DB/persistence matches and exclude client buckets.
- [ ] Generated indexes are exact deterministic output.
- [ ] Registry validate/generate/stale/module/lookup-path/affected and dependency graph checks pass.
- [ ] Registry and Upstream Intelligence focused tests, ownership and required current-head/ready-state CI pass.
- [ ] No schema, migration, runtime, C++, Lua gameplay, protocol, client, map, OTBM, datapack, asset, workflow or E2E implementation change occurs.

# Safety boundary

This task is documentation, registry metadata, generated navigation and focused discovery tests only. It does not repair transactions, change database code, alter migrations, refactor serializers, modify save order, add reconciliation, run destructive database operations or claim persistence correctness.

# Handoff

After the feature PR passes exact-head and ready-state gates, squash merge it and archive this task in a separate lifecycle-only PR. Only after that lifecycle merge may TSD-003 start from then-current `main`.
