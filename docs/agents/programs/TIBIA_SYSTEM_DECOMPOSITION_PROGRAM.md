---
program_id: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
name: Tibia System Decomposition
status: active
owner: repository-wide
created: 2026-07-14T15:43:00+02:00
updated: 2026-07-14T18:05:00+02:00
last_verified_commit: "d9c860048dc755291b97fead4c12398f72e17e53"
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

Maintain one durable, logical decomposition of Tibia and Canary through the existing Real Tibia registry so agents can discover bounded domains, coordinate work, map upstream changes, assign proof layers and later classify migration work for Oteryn without changing gameplay or physically reorganizing the legacy source tree.

This program is architecture, registry metadata, documentation and coordination only. It must never be used as authority to alter runtime behavior.

# Source-of-truth contract

The only canonical module inventory is:

```text
docs/agents/real-tibia/registry/**
```

Generated indexes under `docs/agents/real-tibia/generated/` remain derived artifacts. Program and classification reports explain sequencing and decisions; they do not form a second module registry.

The program extends, rather than replaces:

- Real Tibia Parity governance;
- Upstream Intelligence and Drift Tracking;
- the Universal Physical-Client E2E platform;
- the existing OTBM analysis pipeline;
- task ownership and module catalogue discovery.

# Module boundary rules

A module is a stable functional or technical domain with several of these properties:

- coherent responsibility and vocabulary;
- a lifecycle or state machine;
- a persistence or protocol boundary;
- a server/client/data contract;
- multiple independent findings or bounded tasks;
- a long-lived validation queue;
- repeated need as agent context;
- meaningful architectural dependencies.

A formula, packet field, boss, spell, NPC, quest, storage, map coordinate, bug, class or PR is normally a finding/task inside a module.

# Umbrella and child policy

Broad existing IDs remain stable umbrella/discovery modules when agents and Upstream Intelligence already rely on them. TSD-001 preserved at least:

```text
combat
cyclopedia
market
prey
protocol
quests
spawns
```

Child modules may overlap umbrella path hints. A path can map to several correct modules, and output must remain deterministic.

The current schema has no hierarchy field. Hierarchy is expressed through:

- stable umbrella IDs;
- child scope and description boundaries;
- package classification reports;
- overlapping verified path hints where appropriate;
- no fake `depends_on` parent edges.

A hierarchy schema field may be reconsidered only when a concrete consumer such as `lookup-path`, `affected`, generated navigation or Upstream Intelligence requires it and focused tests prove the value.

# Discovery path policy

Module records use only verified repository paths grouped into `server`, `client`, `data`, `tests` and `docs`.

Path hints:

- are discovery metadata, not ownership;
- may overlap;
- do not prove completeness or parity;
- do not authorize edits;
- must stay empty for planned domains with no verified implementation;
- must be rechecked against current source before each bounded task;
- must not assign broad `src/**` to a narrow server module.

# Relationship policy

- `depends_on` means a fundamental implementation or validation dependency and must remain acyclic.
- `interacts_with` means behavior crosses a boundary.
- Shared use of `Player`, `Game`, Lua, database or protocol classes is not enough to add a relation.
- Use the smallest defensible relationship set.
- Never create relationships solely to render a visually complete architecture graph.

# Maturity policy

Every module separately records implementation, evidence, persistence, protocol, automated tests, runtime validation and gameplay E2E.

File existence supports at most inventory. A serializer, DB column, parser, unit test, build or wiki page does not establish a higher proof level. Runtime and physical-client proof remain separate.

New decomposition records start at lifecycle/implementation/evidence `inventory`; other dimensions stay `not-assessed` unless exact evidence for the narrow contract is reviewed in that package.

# Relationship with Real Tibia Parity

This program organizes domains and bounded work. The Real Tibia Parity Program owns evidence precedence, source pinning, comparison matrices and proof conclusions.

A decomposition record cannot claim:

- Real Tibia parity;
- correct formulas or values;
- persistence safety;
- protocol compatibility;
- runtime behavior;
- gameplay or physical-client success.

Those conclusions require the normal parity finding/task lifecycle.

# Relationship with Upstream Intelligence

Upstream Intelligence uses registry path matches as conservative discovery hints.

New records may cause one external path to map to both an umbrella and a narrower module. This is expected only when:

- every match comes from a registered pattern in a source-policy-allowed bucket;
- mapped paths and module IDs remain stably sorted;
- unmapped paths remain explicit;
- no mapping changes triage into a confirmed defect;
- reviewed decisions remain pinned to the exact candidate revision.

The source-role prerequisite was completed by UI-001A / PR #337 and merge `09f7049401253dd38c8f34506946c2fbe287d220`. Server, client and editor sources use explicit path-bucket policies in the existing source registry; unsupported context maps conservatively to no modules.

This program does not implement UI-002, create another watcher or mapper, or create implementation branches from candidates.

# Relationship with Universal Physical-Client E2E

There is one shared E2E platform. Functional modules own future scenario definitions and assertions; they do not own or duplicate database/server/client orchestration.

Decomposition may document expected scenario roots, but TSD packages do not add gameplay scenarios.

# TSD-002 split decision

The original TSD-002 set combined stable engine infrastructure with database and persistence boundaries. It is split sequentially because current open PR #308 changes schema, migrations and multichannel database/runtime paths.

- `TSD-002A` — engine scheduling, dependency injection, Lua binding surface and build contracts;
- `TSD-002B` — database connection, migrations, transaction boundaries, world/player persistence, reconciliation and save/restart/reload.

TSD-002B cannot start until TSD-002A feature and lifecycle PRs are merged and current `main` is re-read. The two feature PRs may not be open concurrently.

# Bounded package queue

| ID | Scope | Status | Evidence baseline | Dependencies | Exact next action |
|---|---|---|---|---|---|
| `TSD-001` | taxonomy and hierarchy foundation; full candidate classification; three-record engine pilot | completed | PR #335; merge `44fe3af9f29b3ae0164ac5d60fc1f14137b5cea5`; registry 19 → 22 | registry and Upstream Intelligence focused tests | preserve completed archive |
| `TSD-002A` | scheduler, service container, Lua bindings, data-registry decision, build and platform decision | active | task-start `main@6d368766cc47794ec0145b4b32613edaf7588adb`; source-aware mapping | TSD-001 and archived UI-001A | finish PR #340, exact-head/ready CI, squash merge, lifecycle archive |
| `TSD-002B` | database connection, migrations, transaction boundaries, player/world persistence, reconciliation and save/restart/reload | planned | current `player-persistence` umbrella plus then-current DB/runtime inventory | merged and archived TSD-002A; re-check PR #308 state | create one bounded persistence task from current main |
| `TSD-003` | account, character and progression | planned | TSD-001 classification | completed TSD-002B persistence boundaries | separate account, entitlement, character lifecycle and progression without duplicating records |
| `TSD-004` | Cyclopedia family | planned | current `cyclopedia` and `charms` records | maintained-client and persistence inventory | preserve `cyclopedia` umbrella; evaluate durable children |
| `TSD-005` | combat, weapons and vocations | planned | current `combat` and `spells` records | engine and progression boundaries | split only durable formula, state, weapon and vocation domains |
| `TSD-006` | creatures, hunting, raids and bosses | planned | current `spawns`, `prey`, `cyclopedia` records | OTBM/spawn tools and combat boundaries | separate physical spawn, encounter, credit, reward and scheduling domains |
| `TSD-007` | items and economy | planned | current `market`, `imbuements`, `exaltation-forge` records | persistence and transaction boundaries | classify item lifecycle, movement, trade, market and reward domains |
| `TSD-008` | world content | planned | current quests/NPCs/houses/OTBM records | OTBM toolchain | classify map, movement, quest, house, travel and instance domains without a new parser |
| `TSD-009` | social, communication and trust | planned | social-account category | account/character boundaries | separate communication, party/guild and sanction/audit domains |
| `TSD-010` | protocol and client | planned | current `protocol` record and maintained client | cross-repository contract | preserve protocol umbrella and classify wire/session/client-feature domains |
| `TSD-011` | analytics, security and AI | planned | Gameplay Analytics and proposed safety boundaries | persistence/telemetry policy | add only durable read-only/analysis domains with deterministic human enforcement boundaries |
| `TSD-012` | validation and live-operations tooling | planned | existing OTBM, E2E and Upstream Intelligence modules | prior domain decomposition | register only non-duplicative long-lived analyzers and operations tools |
| `TSD-013` | Oteryn migration classification | planned | completed inventories and proof packages | runtime and E2E evidence | classify bounded modules; do not copy code or create another registry |

# Completed packages and prerequisites

## TSD-001 — taxonomy and hierarchy foundation

- Feature PR: #335.
- Final head: `f8524a7a51d6c5b84bcd847da9a2a7923af34dfb`.
- Squash merge: `44fe3af9f29b3ae0164ac5d60fc1f14137b5cea5`.
- Merged at: `2026-07-14T14:35:43Z`.
- Lifecycle merge: `cc8b3bdc9b34fb8e6802bd1a0fc0d535de2dd9ba`.
- Registry: 19 → 22 records.
- Added only `engine-runtime-lifecycle`, `configuration` and `lua-runtime`.
- No runtime, schema, generator, mapper or `protocol.yaml` change.
- Archive: `docs/agents/tasks/archive/CAN-20260714-tibia-system-decomposition-bootstrap.md`.

## Source-role mapping prerequisite

- Program/package: `CAN-PROGRAM-UPSTREAM-INTELLIGENCE` / UI-001A.
- Feature PR: #337.
- Final head: `f8a501a3362ae42079e899b03848a606f7224626`.
- Squash merge: `09f7049401253dd38c8f34506946c2fbe287d220`.
- Lifecycle merge: `6d368766cc47794ec0145b4b32613edaf7588adb`.
- Source registry schema: v1 → v2.
- Modules added/modified: 0/0.
- Archive: `docs/agents/tasks/archive/CAN-20260714-upstream-intelligence-source-role-path-mapping.md`.

# Current active package — TSD-002A

Task: `CAN-20260714-tibia-system-decomposition-engine-foundation`.

Candidate decisions:

| Candidate | Decision |
|---|---|
| `engine-scheduler` | `ADD_NOW` |
| `engine-service-container` | `ADD_NOW` |
| `lua-bindings` | `ADD_NOW` |
| `data-registries` | `MERGE_WITH_ANOTHER_MODULE` |
| `build-system` | `ADD_NOW` |
| `platform-compatibility` | `MERGE_WITH_ANOTHER_MODULE` |

Detailed evidence and exclusions are in `docs/agents/real-tibia/TSD_002A_ENGINE_FOUNDATION_REPORT.md`.

The package increases the registry from 22 to 26 records and adds only:

```text
build-system
engine-scheduler
engine-service-container
lua-bindings
```

It does not modify `player-persistence`, database paths, runtime code, workflow behavior or source-role mapping implementation.

# Oteryn migration policy

The legacy repository remains the evidence laboratory. No code is copied to Oteryn by this program.

Future bounded classifications are:

```text
REUSE
ADAPT
REVALIDATE
REWRITE
DO_NOT_MIGRATE
EXPERIMENTAL_ONLY
```

No module receives `REUSE` merely because code exists. The default is undecided or `REVALIDATE` until the required proof exists.

Required flow:

```text
legacy inventory
→ evidence
→ runtime proof
→ E2E proof
→ migration classification
→ bounded Oteryn package
```

Migration classification belongs to TSD-013 or a later approved bounded task; it is not stored in a second Oteryn registry.

# Safety invariants

- no gameplay/runtime changes;
- no physical source-tree domain refactor;
- no DB schema or migration changes;
- no protocol/client changes;
- no map, OTBM, datapack or asset changes;
- no second registry, generator, watcher, mapper, OTBM parser/renderer or E2E platform;
- no automatic parity claims;
- no automatic upstream adoption;
- no AI model with direct unrestricted runtime, Lua, economy or sanction authority;
- no `ACTIVE_WORK.md` edits from normal TSD tasks.

# Exact next operational steps

1. Complete PR #340 from its exact live head.
2. Verify registry, Upstream Intelligence, ownership, repository CI, review threads, mergeability and changed-file scope.
3. Mark ready only after exact-head checks are green.
4. Pass the ready-state Linux/Required gate and squash merge.
5. Archive TSD-002A in a separate lifecycle-only PR.
6. Re-read then-current main and open PR #308 before creating:

```text
task: CAN-20260714-tibia-system-decomposition-persistence-transactions
package: TSD-002B
branch: docs/tibia-system-decomposition-persistence-transactions
```

# Handoff

A new agent must read this program, TSD-001 archive/report, UI-001A archive, `TSD_002A_ENGINE_FOUNDATION_REPORT.md`, generated indexes, current registry records, active tasks and open PRs. Continue only one task/branch/PR at a time. Never infer runtime, transaction, platform or Lua safety from inventory paths or passing builds.
