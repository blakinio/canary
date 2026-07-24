---
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
name: Real Tibia Evidence Collection
status: active
owner: Real Tibia evidence coordination / platform tooling
created: 2026-07-24T20:20:00+02:00
updated: 2026-07-24T22:40:00+02:00
last_verified_commit: "23e5717a3cd0ed4246be51401f46e63330b2b6bd"
primary_paths:
  - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
  - docs/ai-agent/REAL_TIBIA_EVIDENCE_COLLECTOR_ARCHITECTURE.md
  - docs/agents/templates/REAL_TIBIA_EVIDENCE_*.yaml
  - docs/agents/templates/REAL_TIBIA_MODULE_DOSSIER.md
  - docs/agents/templates/REAL_TIBIA_EVIDENCE_COLLECTOR_PROMPT.md
  - docs/agents/real-tibia/evidence/**
shared_integration_paths:
  - docs/agents/programs/REAL_TIBIA_PARITY_PROGRAM.md
  - docs/agents/real-tibia/registry/modules/*.yaml
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
related_programs:
  - CAN-PROGRAM-REAL-TIBIA-PARITY
  - CAN-PROGRAM-E2E-PLATFORM
  - CAN-PROGRAM-OTBM-WORLD-ASSURANCE-OPERATIONS
  - CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
  - CAN-PROGRAM-UPSTREAM-INTELLIGENCE
cross_repo_contracts: []
---

# Mission

Build and maintain a version-aware, provenance-pinned, auditable evidence corpus describing how every canonical Real Tibia module is expected to behave, how current `blakinio/canary` behaves, where they differ and which additional owner-produced proof is required before a parity claim can be made.

The programme is an evidence coordination layer. It does not implement gameplay, execute physical E2E, parse OTBM, parse official-client reference packages, mutate maps or datapacks, infer hidden formulas, or replace any existing programme.

# Outcomes

For each of the 62 canonical modules, the long-running programme should eventually provide:

1. a detailed module dossier;
2. a state and transition model where applicable;
3. a source-pinned evidence matrix;
4. a version history recording introduction, changes, deprecations and removals;
5. current Canary comparison findings;
6. explicit conflicts and unknowns;
7. architecture and implementation rationale records;
8. requests to the correct owner programme for missing physical, map, protocol, persistence or client-reference proof;
9. a bounded queue of independently testable follow-up findings;
10. a freshness policy and refresh history.

A dossier is not a parity badge. Full parity remains unclaimed until every required evidence dimension reaches the necessary proof level.

# Authoritative boundaries

## This programme owns

- evidence-collection policy and schemas;
- module dossier structure;
- source pinning and claim decomposition;
- version-history normalization;
- source conflict and unknown tracking;
- deduplication and cross-module evidence references;
- evidence requests directed to owning programmes;
- factual coverage and freshness summaries over collected records;
- coordinator-managed scheduling of bounded evidence-only module tasks;
- reusable prompts for coordinator, worker and reviewer agents.

## This programme does not own

- physical client execution or Universal E2E lifecycle;
- feature-specific E2E implementation owned by feature programmes;
- OTBM parsing, World Index, Script Resolution, Reachability/BFS, Semantic Diff, map certification or factual rendering;
- official-client reference package parsing, normalization or identifier correlation owned by TCR;
- packet-capture infrastructure, maintained-client changes or cross-repository rollout;
- gameplay/runtime implementation, persistence migrations or datapack changes;
- donor imports or upstream synchronization;
- release certification, deployment or production promotion.

# Source-of-truth rule

There is no universal source of truth for the whole game. Every claim declares an `authority_dimension` and uses the strongest source appropriate to that dimension.

| Dimension | Primary authority | Secondary evidence | Never proves by itself |
|---|---|---|---|
| feature existence/name/release | official Tibia release/news/guide | maintained wiki, official forum clarification | runtime implementation |
| visible gameplay behavior | reproducible official-client observation plus official material | multiple independent captures, maintained wiki | hidden server state |
| current Canary behavior | exact current Canary source, registrations, tests and runtime | upstream Canary | Real Tibia parity |
| protocol/client interpretation | byte-exact tests, maintained OTClient, controlled capture | official-client observation | server authorization or persistence |
| persistence/rollback | Canary load/save/schema/migrations/failure tests | donor implementation | UI observation |
| map geometry/walkability | official-client-derived minimap plus repeated observation | audited donor OTBM | item stacks, AID/UID or quest mechanics |
| map mechanics | canonical OTBM evidence plus handler resolution and runtime proof | donor scripts/wiki | geometry alone |
| implementation candidate | current Canary architecture and deterministic tests | pinned upstream/Crystal candidate | official behavior |
| historical introduction/change | exact official release/update material | maintained historical references, dated captures | exact hidden implementation date |

When sources conflict, preserve `CONFLICT`. When evidence is absent, preserve `UNKNOWN`. Never select the most convenient source or promote an inference into fact.

# Version-history contract

Every behavior claim and module dossier must distinguish:

- `announced_in`: first exact official announcement, when known;
- `introduced_in`: first proven live version or release state;
- `observed_in`: exact client build/date where behavior was reproduced;
- `changed_in`: one or more exact versions where the behavior changed;
- `deprecated_in`: version where use became discouraged or compatibility-only;
- `removed_in`: version where the behavior ceased to exist;
- `effective_from` and `effective_until`: bounded applicability interval when proven;
- `current_official_baseline`: latest official behavior baseline used by the finding;
- `canary_baseline`: exact Canary commit, server/protocol build and relevant datapack/map/assets revisions.

An official announcement proves announcement and intended release behavior, not necessarily the exact final live implementation. A wiki history note remains secondary until independently confirmed. Filenames, directory names, OTBM labels and donor branch names never prove a Tibia version.

Official release, official client build, protocol profile, Canary commit, maintained OTClient commit, map SHA-256, datapack revision, appearances/items revision, spawn/NPC sidecar revision and database schema revision remain separate axes. They must not be compressed into one ambiguous `version` value.

# Evidence states and levels

Record states:

- `PROVEN`;
- `DERIVED`;
- `UNKNOWN`;
- `CONFLICT`;
- `STALE`;
- `SUPERSEDED`;
- `REJECTED`.

Record the strongest proof level actually reached:

1. `definition-found`;
2. `registration-proven`;
3. `runtime-path-proven`;
4. `persistence-proven`;
5. `protocol-proven`;
6. `behavior-proven`;
7. `gameplay-proven`;
8. `physical-client-proven`.

Never promote a lower level into a higher level.

# Durable file model

RTEC-001 defines and validates this source layout:

```text
docs/agents/real-tibia/evidence/
├── README.md
├── schemas/
│   ├── evidence-record.schema.json
│   ├── owner-request.schema.json
│   ├── module-evidence-index.schema.json
│   ├── version-history.schema.json
│   └── generated-indexes.schema.json
├── generated/
│   └── EVIDENCE_INDEXES.json
├── modules/
│   └── <module-id>/
│       ├── MODULE.md
│       ├── BEHAVIOR_MODEL.md
│       ├── VERSION_HISTORY.yaml
│       ├── EVIDENCE_INDEX.yaml
│       ├── DECISIONS.md
│       ├── records/
│       │   └── RT-<MODULE>-NNNN.yaml
│       └── reviews/
│           └── <review-id>.md
└── requests/
    ├── e2e/
    ├── otbm/
    ├── tcr/
    ├── protocol/
    └── feature/
```

The validator forbids empty module directories and index-only placeholder dossier trees. Broad population remains blocked until RTEC-001 merges, then RTEC-002 must prove the full flow on one bounded module before any parallel wave.

Generated large reports, captures, screenshots, videos, maps, client packages and proprietary assets remain outside Git. Git stores compact metadata, hashes, references, findings and proof boundaries only.

# Module dossier contract

Every module dossier must cover applicable sections:

- scope and exclusions;
- official purpose and player-visible outcomes;
- actors and ownership boundaries;
- inputs, outputs and preconditions;
- complete states and transitions;
- formulas, values and selection rules with per-value evidence;
- cooldowns, time windows and server-save behavior;
- account/character/world scope;
- persistence, migration, rollback and exactly-once behavior;
- protocol fields, capability gates and client UI interpretation;
- map, NPC, spawn, item, quest and dependency interactions;
- concurrency and multi-client behavior;
- failure, disconnect, relog, restart and stale-data behavior;
- security/authorization boundaries;
- historical version timeline;
- current Canary comparison;
- decisions, rationale and rejected alternatives;
- evidence gaps and owner requests;
- strongest proven maturity per dimension.

The dossier records auditable rationale, not private chain-of-thought. Decisions state the selected option, evidence, constraints, trade-offs and rejected alternatives without reproducing hidden internal reasoning.

# Cooperation contracts

## Universal E2E

The Collector may identify missing physical/runtime proof, prepare a structured request, reference stable scenario/result IDs, consume retained result envelopes and update records with exactly what those results prove and do not prove.

The Collector must not create a second runner/lifecycle/workflow, edit `tools/e2e/**`, invent feature expectations, run or reclassify E2E without the owning task, or promote M0/static evidence to physical gameplay proof.

Capability-oriented E2E suggestions must be separate owner-reviewed proposals, never implementation inside a Collector task.

## OTBM/OWA

The Collector may request exact World Index, Script Resolution, Reachability, Semantic Diff, certification or factual-render evidence; reference stable finding IDs and hashes; consume owner outputs without reinterpreting authority; and report missing/stale evidence as a blocker.

The Collector must not parse OTBM, create another World Index/pathfinder/renderer/certifier, infer mechanics from visuals, classify a static gap as a gameplay defect without owner proof, or mutate map/datapack/proprietary assets.

## TCR

The Collector consumes stable TCR manifests, indexes, parity and drift records. It does not parse official-client files, infer client builds or join identifier namespaces without explicit reviewed mappings.

Suggested TCR expansions identify the missing client-reference dimension and exact downstream consumer while retaining proprietary inputs outside Git.

# Concurrency model

## Roles and cap

- **1 Coordinator** owns the programme queue, shared schemas, cross-module deduplication, shared indexes and wave planning.
- **Up to 8 Collector workers** may run concurrently after RTEC-002/003 when each owns one distinct module dossier or non-overlapping bounded package.
- **Up to 2 Reviewers** may independently review completed worker outputs without editing worker-owned files until handoff.
- E2E, OTBM/OWA, TCR and feature agents retain their own queues and safe concurrency.

Default campaign cap: **8 parallel Collector workers**, with at most **4 concurrently open Collector PRs**. The Coordinator may reduce this cap for CI, source, review or owner-queue constraints. Raising it requires a recorded concurrency experiment and ownership evidence.

## Serialization groups

The following tightly coupled groups require one worker or an explicit coordination ID:

1. `network-transport`, `login-protocol`, `protocol`, `protocol-compatibility`, `protocol-session-handoff`;
2. `world-map-runtime`, `world-zones`, `houses`, `quests`, `npcs`, `spawns`, `raids`, `boss-encounters`, `instances` when sharing one region/mechanic package;
3. `database-connection`, `database-migrations`, `player-persistence`, `world-persistence`, `account-lifecycle`, `character-lifecycle` when sharing stored state;
4. `combat`, `combat-conditions`, `spells`, `weapons`, `vocations` when investigating one formula/state machine;
5. `cyclopedia`, `bestiary`, `bosstiary`, `charms`, `prey`, `achievements`, `titles` when sharing identifiers or UI/protocol surfaces.

Different modules in a group may run concurrently only when owned dossier paths and investigated behavior surfaces are demonstrably independent.

## Worker write restrictions

Workers may edit only their task record, one module dossier/bounded package directory and their own evidence/request records.

Workers must not edit the programme record, schemas/templates, shared generated indexes, owner implementation paths or another worker's dossier/requests. The Coordinator performs shared-file integration after worker PRs merge.

# Queue

| ID | Scope | Status | Dependencies | Risk | Exact next action |
|---|---|---|---|---|---|
| RTEC-000 | Architecture, structure, boundaries, concurrency and prompts | merged | existing parity/E2E/OTBM/TCR governance | low | Architecture delivered by PR #889; lifecycle archived by PR #893. |
| RTEC-001 | Evidence/request schemas, validator, deterministic indexes and tests | active — draft PR #897 | RTEC-000 | medium | Complete current-head CI/review/final gate and merge before any module worker starts. |
| RTEC-002 | Pilot dossier on one bounded low-coupling module | blocked | RTEC-001 | medium | After RTEC-001 merges, select exactly one module after fresh ownership/source preflight and prove the end-to-end collection/review flow. |
| RTEC-003 | Owner-request lifecycle integration | planned | RTEC-001/002 | medium | Validate request state transitions and stable output consumption for E2E/OTBM/TCR. |
| RTEC-004 | Parallel campaign wave 1 | planned | RTEC-002/003 | medium | Start at most eight workers and four concurrent PRs using isolated dossier paths. |
| RTEC-005 | Remaining module waves | planned | RTEC-004 evidence and concurrency review | medium | Continue bounded waves until all 62 modules have non-placeholder dossiers. |
| RTEC-006 | Release/version refresh and drift operation | planned | populated dossiers and validator | medium | Add deterministic stale/version-delta selection for future Tibia/Canary changes. |
| RTEC-007 | Coverage, confidence and unresolved-evidence dashboard | planned | stable records and owner results | medium | Generate factual dimensions without opaque parity score. |

# Completion rules

A module is `dossier-complete` only when every applicable dossier section is evidence-backed or explicitly marked `UNKNOWN`, `CONFLICT`, `not-applicable` or `blocked-by-owner-request`.

A module is not `parity-complete` unless all required behavior, persistence, protocol, map, gameplay and physical-client dimensions are proven at the necessary level for its scope.

The entire programme cannot claim that Canary faithfully reproduces Real Tibia merely because all 62 dossiers exist.

# Handoff

Start from this programme, the Collector architecture, current registry module record and the first active bounded task. Re-fetch live PR/task/source state. Do not restart the full 62-module audit from chat history and do not create parallel execution infrastructure.
