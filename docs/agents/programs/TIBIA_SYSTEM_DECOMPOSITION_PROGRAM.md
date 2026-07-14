---
program_id: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
name: Tibia System Decomposition
status: active
owner: repository-wide
created: 2026-07-14T15:43:00+02:00
updated: 2026-07-14T18:46:00+02:00
last_verified_commit: "8c24598067c7d3791800342622dbd4d37c9d647b"
primary_paths:
  - docs/agents/real-tibia/**
  - docs/agents/programs/TIBIA_SYSTEM_DECOMPOSITION_PROGRAM.md
shared_integration_paths:
  - tools/agents/real_tibia_registry*.py
  - tools/agents/upstream_intelligence*.py
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
related_programs:
  - CAN-PROGRAM-REAL-TIBIA-PARITY
  - CAN-PROGRAM-UPSTREAM-INTELLIGENCE
  - CAN-PROGRAM-E2E-PLATFORM
cross_repo_contracts: []
---

# Mission

Maintain one durable logical decomposition of Tibia and Canary through the existing Real Tibia registry so agents can discover bounded domains, coordinate work, map upstream changes, assign proof layers and later classify migration work for Oteryn without changing gameplay or physically reorganizing the legacy source tree.

This program is architecture, registry metadata, documentation and coordination only. It never authorizes runtime changes.

# Source-of-truth contract

The only canonical module inventory is:

```text
docs/agents/real-tibia/registry/**
```

Generated indexes are derived artifacts. Program and package reports explain sequencing and decisions; they are not a second registry.

The program reuses:

- Real Tibia Parity governance;
- Upstream Intelligence and its source-role-aware mapper;
- the shared physical-client E2E platform;
- the existing OTBM analysis pipeline;
- task ownership and module catalogue discovery.

# Module boundary rules

A module needs a durable responsibility plus several of: coherent vocabulary, lifecycle/state machine, persistence/protocol boundary, stable contract, multiple independent findings, a long-lived validation queue, repeated agent context or meaningful dependencies.

A formula, packet field, boss, spell, NPC, storage, map coordinate, bug, helper class or PR is normally a finding inside a module.

Broad existing IDs remain stable umbrellas. Child records may overlap verified path hints. `depends_on` is never used as hierarchy.

# Discovery, relationship and maturity rules

Path hints:

- use only verified current paths grouped into server/client/data/tests/docs;
- are discovery, not ownership or edit authorization;
- may overlap;
- do not prove completeness, parity or runtime behavior;
- must not assign broad `src/**` to a narrow server module.

Relationships:

- `depends_on` means a fundamental implementation/validation dependency and must be acyclic;
- `interacts_with` is descriptive;
- shared use of Player, Game, Lua, DB or protocol classes is insufficient by itself.

New decomposition records start at:

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

File, schema, helper, migration or test presence does not justify a higher proof level.

# Program integrations

## Real Tibia Parity

Decomposition cannot claim Real Tibia parity, formula correctness, persistence safety, wire compatibility, runtime behavior or physical-client success. Those require normal parity findings and proof.

## Upstream Intelligence

Registry matches remain source-policy-filtered discovery hints. Outputs stay deterministic, unmapped paths explicit, triage unchanged and reviewed decisions revision-pinned. UI-001A was merged in PR #337 and archived; no second mapper or watcher exists.

## Physical-client E2E

There is one shared orchestrator. TSD packages do not add gameplay scenarios or duplicate orchestration.

# TSD-002 split

The original package combined stable engine infrastructure with DB/persistence boundaries, so it was delivered sequentially:

- `TSD-002A` — scheduler, DI, Lua binding and build boundaries;
- `TSD-002B` — DB connection, migrations, transaction capability, world/player persistence and save/restart/reload classification.

PR #308 was merged before TSD-002B task start. Its code is current-main inventory evidence; its PR claims and tests are not proof of atomicity, idempotency or runtime safety.

# Bounded package queue

| ID | Scope | Status | Evidence baseline | Dependencies | Exact next action |
|---|---|---|---|---|---|
| `TSD-001` | taxonomy/hierarchy foundation and three-record pilot | completed | PR #335; merge `44fe3af9f29b3ae0164ac5d60fc1f14137b5cea5`; registry 19 → 22 | registry/UI tests | preserve archive |
| `TSD-002A` | engine foundation | completed | PR #340; merge `82f35c0147fdd33c8d4e70d98d003385daf61de6`; registry 22 → 26 | TSD-001 and UI-001A | preserve archive |
| `TSD-002B` | DB connection/migrations, transaction and world persistence classification | active | task-start `main@709693b4cca42214c52e63ea15a1a22b93f9a113`; merged PR #308 | archived TSD-002A | finish PR #342, exact-head/ready CI, squash merge, lifecycle archive |
| `TSD-003` | account, character and progression | planned | TSD-001 classification plus TSD-002 persistence boundaries | completed TSD-002B | separate durable account/character/progression domains |
| `TSD-004` | Cyclopedia family | planned | `cyclopedia` and `charms` umbrellas | persistence/client inventory | preserve umbrella and evaluate durable children |
| `TSD-005` | combat, weapons and vocations | planned | `combat` and `spells` umbrellas | engine/progression boundaries | split only durable formula/state/weapon/vocation domains |
| `TSD-006` | creatures, hunting, raids and bosses | planned | `spawns`, `prey`, `cyclopedia` | OTBM/spawn/combat boundaries | separate spawn, encounter, credit, reward and scheduling |
| `TSD-007` | items and economy | planned | `market`, `imbuements`, `exaltation-forge` | persistence/transaction boundaries | classify item lifecycle, movement, trade, market and rewards |
| `TSD-008` | world content | planned | quests/NPCs/houses/OTBM records | OTBM toolchain | classify map, movement, quest, house, travel and instances |
| `TSD-009` | social, communication and trust | planned | social/account category | account/character boundaries | separate communication, party/guild and sanctions/audit |
| `TSD-010` | protocol and client | planned | `protocol` umbrella and maintained client | cross-repo contract | classify wire/session/client-feature domains |
| `TSD-011` | analytics, security and AI | planned | analytics/safety boundaries | persistence/telemetry policy | register durable read-only/analysis domains only |
| `TSD-012` | validation and live-operations tooling | planned | OTBM/E2E/UI modules | prior decomposition | register only non-duplicative long-lived tooling |
| `TSD-013` | Oteryn migration classification | planned | completed inventories/proof packages | runtime/E2E evidence | classify modules; do not copy code or create another registry |

# Completed packages and prerequisites

## TSD-001

- Feature PR #335, head `f8524a7a51d6c5b84bcd847da9a2a7923af34dfb`.
- Merge `44fe3af9f29b3ae0164ac5d60fc1f14137b5cea5`; lifecycle merge `cc8b3bdc9b34fb8e6802bd1a0fc0d535de2dd9ba`.
- Registry 19 → 22; added only `engine-runtime-lifecycle`, `configuration`, `lua-runtime`.
- Archive: `docs/agents/tasks/archive/CAN-20260714-tibia-system-decomposition-bootstrap.md`.

## Source-role mapping prerequisite

- UI-001A feature PR #337, merge `09f7049401253dd38c8f34506946c2fbe287d220`.
- Lifecycle merge `6d368766cc47794ec0145b4b32613edaf7588adb`.
- Source registry v1 → v2; modules changed 0.
- Archive: `docs/agents/tasks/archive/CAN-20260714-upstream-intelligence-source-role-path-mapping.md`.

## TSD-002A

- Feature PR #340, head `4a044a0f93a23aa7c610c41d1003d5f83d7fc62c`.
- Merge `82f35c0147fdd33c8d4e70d98d003385daf61de6`; lifecycle merge `709693b4cca42214c52e63ea15a1a22b93f9a113`.
- Registry 22 → 26; added only `build-system`, `engine-scheduler`, `engine-service-container`, `lua-bindings`.
- Existing records modified 0; `data-registries` and `platform-compatibility` merged into existing boundaries.
- Archive: `docs/agents/tasks/archive/CAN-20260714-tibia-system-decomposition-engine-foundation.md`.

# Current active package — TSD-002B

Task: `CAN-20260714-tibia-system-decomposition-persistence-transactions`; PR #342.

| Candidate | Decision |
|---|---|
| `database-connection` | `ADD_NOW` |
| `database-migrations` | `ADD_NOW` |
| `transaction-boundaries` | `MERGE_WITH_ANOTHER_MODULE` |
| `world-persistence` | `ADD_NOW` |
| `database-reconciliation` | `DEFER` |
| `save-restart-reload` | `MERGE_WITH_ANOTHER_MODULE` |

`player-persistence` remains the unchanged compatibility umbrella.

The package increases the registry 26 → 29 and adds only:

```text
database-connection
database-migrations
world-persistence
```

Detailed evidence and limits: `docs/agents/real-tibia/TSD_002B_PERSISTENCE_TRANSACTIONS_REPORT.md`.

No record or code claims transaction isolation, rollback completeness, retry safety, migration reversibility, idempotency, crash consistency, restart/reload safety or production MariaDB compatibility.

# Oteryn migration policy

The legacy repository remains the evidence laboratory. No code is copied to Oteryn by this program.

Future classifications are `REUSE`, `ADAPT`, `REVALIDATE`, `REWRITE`, `DO_NOT_MIGRATE` and `EXPERIMENTAL_ONLY`. Default is undecided or `REVALIDATE`; code presence is insufficient.

Required flow:

```text
legacy inventory
→ evidence
→ runtime proof
→ E2E proof
→ migration classification
→ bounded Oteryn package
```

# Safety invariants

- no gameplay/runtime or physical source-tree refactor;
- no DB schema/migration implementation changes;
- no protocol/client/map/OTBM/datapack/asset changes;
- no second registry/generator/watcher/mapper/parser/renderer/E2E platform;
- no automatic parity or upstream-adoption claims;
- no unrestricted AI runtime authority;
- no normal-task edits to `ACTIVE_WORK.md`.

# Exact next operational steps

1. Complete PR #342 from its exact live head.
2. Verify registry/UI/ownership/repository CI, review threads, mergeability and changed-file scope.
3. Mark ready only after exact-head checks pass.
4. Pass ready-state Linux/Required and squash merge.
5. Archive TSD-002B in a separate lifecycle-only PR.
6. Re-read current main before creating:

```text
task: CAN-20260714-tibia-system-decomposition-account-character-progression
package: TSD-003
branch: docs/tibia-system-decomposition-account-character-progression
```

# Handoff

Read this program, TSD-001/UI-001A/TSD-002A archives, the TSD-002B report, generated indexes, current records, open PRs and active ownership. Continue only one task/branch/PR at a time. Never infer persistence, transaction, restart/reload, runtime or E2E safety from inventory paths or passing tests.
