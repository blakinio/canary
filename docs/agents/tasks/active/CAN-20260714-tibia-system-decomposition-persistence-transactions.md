---
task_id: CAN-20260714-tibia-system-decomposition-persistence-transactions
program_id: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
coordination_id: REAL-TIBIA-SYSTEM-DECOMPOSITION-TSD-002B
status: active
agent: "GPT-5.6 Thinking"
branch: docs/tibia-system-decomposition-persistence-transactions
base_branch: main
created: 2026-07-14T18:24:00+02:00
updated: 2026-07-14T18:52:00+02:00
last_verified_commit: "8c24598067c7d3791800342622dbd4d37c9d647b"
risk: low
related_issue: ""
related_pr: "342"
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
    - docs/agents/real-tibia/registry/modules/world-persistence.yaml
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
    - src/kv/**
    - src/game/scheduling/save_manager.*
    - src/canary_server.cpp
    - src/game/multichannel/**
    - tests/**
modules_touched:
  - Real Tibia module registry
  - database-connection
  - database-migrations
  - world-persistence
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

Complete TSD-002B as a bounded persistence and transaction inventory over current `main`. Classify `database-connection`, `database-migrations`, `transaction-boundaries`, `world-persistence`, `database-reconciliation` and `save-restart-reload`, add only durable independent records with verified paths, and preserve `player-persistence` as the compatibility umbrella.

# Exact base and preflight

- Task-start main: `709693b4cca42214c52e63ea15a1a22b93f9a113`.
- TSD-002A feature and lifecycle cycles were merged first.
- PR #308 was merged as `4de9350e62e2ca9ddf717e16628f87084a74aa86`; its code is current-main inventory evidence, but its PR claims and tests do not prove transactionality, idempotency or runtime safety.
- The still-active `CAN-20260714-cross-process-db-row-handoff` task owns its multichannel runtime paths; this task read them only and made no edit there.
- Open PRs inspected: #339, #316 and #245. None modified `docs/agents/real-tibia/**`.
- PR #339 changed connection/protocol runtime paths; those remained read-only.
- PR #245 owned physical-client E2E paths; no E2E scenario or orchestrator change was made.
- `ACTIVE_WORK.md` remained read-only.

# Candidate decisions

| Candidate | Decision | Result |
|---|---|---|
| `database-connection` | `ADD_NOW` | Added narrow DB handle/query/result/retry/batch/transaction-capability discovery. |
| `database-migrations` | `ADD_NOW` | Added fresh schema, DB version and ordered Lua migration lifecycle discovery. |
| `transaction-boundaries` | `MERGE_WITH_ANOTHER_MODULE` | Kept as DB-core and functional-call-site capability, not a false helper-class module. |
| `world-persistence` | `ADD_NOW` | Added non-player save orchestration for guild, house/map serialization and KV state. |
| `database-reconciliation` | `DEFER` | No generic cross-domain reconciliation subsystem or stable implementation root exists. |
| `save-restart-reload` | `MERGE_WITH_ANOTHER_MODULE` | Kept as a cross-module validation package across runtime and persistence owners. |

Detailed evidence and exclusions are in `docs/agents/real-tibia/TSD_002B_PERSISTENCE_TRANSACTIONS_REPORT.md`.

# Delivered registry result

- Registry records: 26 → 29.
- Added only:
  - `database-connection`;
  - `database-migrations`;
  - `world-persistence`.
- Existing records modified: 0.
- `player-persistence` remained byte-for-byte unchanged as the compatibility umbrella.
- Categories, registry schema, generator and source-aware mapper remained unchanged.
- Generated indexes were produced through the existing deterministic contract and passed `generate --check`.

# Maturity and relationships

All three records start at lifecycle/implementation/evidence `inventory`; all proof dimensions remain `not-assessed`.

- `database-migrations` depends on `database-connection`.
- `world-persistence` depends on `database-connection`.
- `database-connection` has no dependency edge.
- Other edges are descriptive `interacts_with` relationships.

Dependency validation remains acyclic.

# Validation history

Implementation/focused-test head `8c24598067c7d3791800342622dbd4d37c9d647b`:

- Real Tibia Module Registry #152: success;
- focused registry tests: success;
- schema and dependency validation: success;
- deterministic `generate --check`: success;
- stale/module/lookup-path/affected discovery commands: success;
- broad `player-persistence` plus narrow DB mapping regression: success;
- source-aware mapping excludes client-only `protocol` matches and preserves triage/decision state.

Later program, catalogue, changelog and task-record commits are documentation-only. This task record cannot embed its own SHA; live PR #342 metadata and exact-head workflows are authoritative for final readiness and merge.

# Acceptance criteria

- [x] Current-main connection, query/result, transaction, migration, player/world save and startup/shutdown/reload paths were inventoried.
- [x] All six candidates received explicit decisions with exclusions and evidence limits.
- [x] `player-persistence` remains the unchanged stable umbrella.
- [x] New records use narrow verified paths; no narrow module uses `src/**`.
- [x] DB classes, SQL, tests and migrations are not treated as proof of atomicity, rollback, crash safety, retry safety, idempotency, reconciliation, restart/reload safety or production compatibility.
- [x] New maturity is conservative inventory/not-assessed.
- [x] Source-aware server mapping covers allowed DB/persistence matches and excludes client buckets.
- [x] Generated indexes match exact deterministic generator output.
- [x] Registry validate/generate/stale/module/lookup-path/affected and dependency graph checks pass.
- [ ] Exact final current-head and ready-state registry/UI/ownership/repository CI must pass before merge.
- [x] No schema, migration, runtime, C++, Lua gameplay, protocol, client, map, OTBM, datapack, asset, workflow or E2E implementation change occurred.

# Safety and limitations

This task is documentation, registry metadata, generated navigation and focused discovery tests only. It proves no ACID semantics, rollback completeness, retry/reconnect safety, migration reversibility, idempotency, exactly-once processing, crash consistency, save completeness, restart/reload safety, production MariaDB compatibility, Real Tibia parity, E2E behavior or Oteryn readiness.

# Handoff

After PR #342 passes exact final-head checks, changed-file/review inspection and ready-state Linux/Required, squash merge it and archive this task in a separate lifecycle-only PR. Only after that lifecycle merge may the next task start from then-current `main`:

```text
task: CAN-20260714-tibia-system-decomposition-account-character-progression
package: TSD-003
branch: docs/tibia-system-decomposition-account-character-progression
```
