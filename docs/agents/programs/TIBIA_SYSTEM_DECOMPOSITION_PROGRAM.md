---
program_id: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
name: Tibia System Decomposition
status: active
owner: repository-wide
created: 2026-07-14T15:43:00+02:00
updated: 2026-07-14T15:43:00+02:00
last_verified_commit: "21c51174ded78b8f07ff07607a927b66de430246"
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

Generated indexes under `docs/agents/real-tibia/generated/` remain derived artifacts. This program and its classification report explain sequencing and decisions; they do not form a second module registry.

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

A formula, packet field, boss, spell, NPC, quest, storage, map coordinate, bug or PR is normally a finding/task inside a module.

# Umbrella and child policy

Broad existing IDs remain stable umbrella/discovery modules when agents and Upstream Intelligence already rely on them. TSD-001 preserves at least:

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

The current schema has no parent/child field. TSD-001 therefore records hierarchy through:

- the module description and scope boundaries;
- this program;
- `TIBIA_SYSTEM_DECOMPOSITION_REPORT.md`;
- explicit `KEEP_AS_UMBRELLA` classifications.

`depends_on` must not be abused as parenthood. A schema field may be reconsidered only when a concrete consumer such as `lookup-path`, `affected`, generated navigation or Upstream Intelligence requires it and focused tests prove the value.

# Discovery path policy

Module records use only verified repository paths grouped into `server`, `client`, `data`, `tests` and `docs`.

Path hints:

- are discovery metadata, not ownership;
- may overlap;
- do not prove completeness or parity;
- do not authorize edits;
- must stay empty for planned domains with no verified implementation;
- must be rechecked against current source before each bounded task.

# Relationship policy

- `depends_on` means a fundamental implementation or validation dependency and must remain acyclic.
- `interacts_with` means behavior crosses a boundary.
- Shared use of `Player`, `Game`, Lua, database or protocol classes is not enough to add a relation.
- Use the smallest defensible relationship set.
- Never create relationships solely to render a visually complete architecture graph.

# Maturity policy

Every module separately records implementation, evidence, persistence, protocol, automated tests, runtime validation and gameplay E2E.

File existence supports at most inventory. A serializer, DB column, parser, unit test, build or wiki page does not establish a higher proof level. Runtime and physical-client proof remain separate.

Planned architecture, analytics, security, AI and event-director modules use conservative values until their implementation and evidence are independently established.

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

Upstream Intelligence continues to use registry path matches as conservative discovery hints.

New child records may cause one external path to map to both an umbrella and a narrower module. This is expected when:

- every match comes from a registered path pattern;
- mapped paths and module IDs remain stably sorted;
- unmapped paths remain explicit;
- no mapping changes triage into a confirmed defect;
- reviewed decisions remain pinned to the exact candidate revision.

This program does not implement UI-002, does not change source watchers and does not create implementation branches from candidates.

# Relationship with Universal Physical-Client E2E

There is one shared E2E platform. Functional modules own future scenario definitions and assertions; they do not own or duplicate database/server/client orchestration.

The decomposition may document expected scenario roots, but TSD packages do not add gameplay scenarios.

# Bounded package queue

| ID | Scope | Status | Evidence baseline | Dependencies | Exact next action |
|---|---|---|---|---|---|
| `TSD-001` | taxonomy and hierarchy foundation; full candidate classification; three-record engine pilot | active | main `21c51174ded78b8f07ff07607a927b66de430246`; registry schema v1; 19 records | registry and Upstream Intelligence focused tests | finish draft PR, validate deterministic mapping and preserve runtime read-only boundary |
| `TSD-002` | remaining engine foundation and persistence | planned | TSD-001 hierarchy/path policy | current source inventory and DB/runtime evidence boundaries | add only proven long-lived records for scheduler/services/Lua bindings/build/platform and core DB/transaction lifecycle |
| `TSD-003` | account, character and progression | planned | TSD-001 classification | TSD-002 persistence boundaries | separate account, entitlement, character lifecycle and progression state without duplicating current records |
| `TSD-004` | Cyclopedia family | planned | current `cyclopedia` and `charms` records | maintained-client and persistence inventory | preserve `cyclopedia` umbrella; evaluate Bestiary/Bosstiary/items/map/character/houses children |
| `TSD-005` | combat, weapons and vocations | planned | current `combat` and `spells` records | engine/runtime and progression boundaries | split only durable formula, state, weapon and vocation domains |
| `TSD-006` | creatures, hunting, raids and bosses | planned | current `spawns`, `prey`, `cyclopedia` records | OTBM/spawn tools and combat boundaries | separate physical spawn, encounter, credit, rewards and scheduling |
| `TSD-007` | items and economy | planned | current `market`, `imbuements`, `exaltation-forge` records | persistence and transaction boundaries | classify item lifecycle, movement, trade, market and reward domains |
| `TSD-008` | world content | planned | current quests/NPCs/houses/OTBM records | OTBM toolchain | classify map, movement, quest, house, travel and instance domains without a new parser |
| `TSD-009` | social, communication and trust | planned | social-account category | account/character boundaries | separate communication, party/guild and sanction/audit domains |
| `TSD-010` | protocol and client | planned | current `protocol` record and maintained client | cross-repository contract | preserve protocol umbrella and classify wire/session/client-feature domains |
| `TSD-011` | analytics, security and AI | planned | Gameplay Analytics and proposed safety boundaries | persistence/telemetry policy | add only durable read-only/analysis domains with deterministic human enforcement boundaries |
| `TSD-012` | validation and live-operations tooling | planned | existing OTBM, E2E and Upstream Intelligence modules | prior domain decomposition | register only non-duplicative long-lived analyzers and operations tools |
| `TSD-013` | Oteryn migration classification | planned | completed inventories and proof packages | runtime and E2E evidence | classify bounded modules; do not copy code or create another registry |

# Completed packages

None. TSD-001 is a bootstrap in progress and must not be described as full Tibia decomposition.

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
- no second registry, generator, watcher, OTBM parser/renderer or E2E platform;
- no automatic parity claims;
- no automatic upstream adoption;
- no AI model with direct unrestricted runtime, Lua, economy or sanction authority;
- no `ACTIVE_WORK.md` edits from normal TSD tasks.

# Exact next bounded task

After TSD-001, create:

```text
task: CAN-20260714-tibia-system-decomposition-engine-persistence
package: TSD-002
branch: docs/tibia-system-decomposition-engine-persistence
```

Start by re-fetching current `main`, open PRs and active tasks. Inventory exact paths and boundaries for:

```text
engine-scheduler
engine-service-container
lua-bindings
data-registries
build-system
platform-compatibility
database-connection
database-migrations
transaction-boundaries
save-restart-reload
```

Do not add a record when the candidate is only a class/file grouping, duplicates an umbrella, or lacks a durable lifecycle/validation boundary.

# Handoff

A new agent must read the active task, this program, the classification report, generated module indexes, all current registry records, current open PRs and Upstream Intelligence policies. Continue only one package and one task/PR at a time. Preserve current umbrella IDs and proof boundaries.
