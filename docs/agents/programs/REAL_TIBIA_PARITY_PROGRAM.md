---
program_id: CAN-PROGRAM-REAL-TIBIA-PARITY
name: Real Tibia Parity Program
status: active
owner: repository-wide
created: 2026-07-14T09:00:00+02:00
updated: 2026-07-14T13:02:00+02:00
last_verified_commit: "dddf8e453512547c979ebd7ed6cb60e8fcac2d65"
primary_paths:
  - docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md
  - docs/agents/REAL_TIBIA_PARITY_PLAYBOOK.md
  - docs/agents/real-tibia/**
  - docs/agents/programs/*_PROGRAM.md
  - docs/ai-agent/**
shared_integration_paths:
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
  - docs/agents/CROSS_REPO_CONTRACTS.md
related_programs:
  - CAN-PROGRAM-CRYSTALSERVER-COMPARISON
cross_repo_contracts: []
---

# Mission

Provide one durable system for validating and improving many Tibia modules without depending on chat memory, repeated giant prompts or one agent remembering every source, PR and caveat.

The program separates:

- repository-wide evidence and delivery rules;
- machine-readable module identity, dependency, path, maturity and freshness metadata;
- module-specific long-lived programs;
- one bounded active task and PR at a time;
- technical validation reports;
- cross-repository and physical-client proof.

A chat may initiate work, but it is never the durable source of truth.

# Authoritative documents

| Purpose | Document |
|---|---|
| Source roles, provenance and donor registry | `docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md` |
| Mandatory operational procedure | `docs/agents/REAL_TIBIA_PARITY_PLAYBOOK.md` |
| Machine-readable module discovery, relationships, maturity and freshness | `docs/agents/real-tibia/README.md`, `docs/agents/real-tibia/registry/**`, generated indexes |
| Repository reusable-module discovery | `docs/agents/MODULE_CATALOG.md` |
| Build and test selection | `docs/agents/BUILD_TEST_MATRIX.md` |
| Cross-repository rollout and protocol coordination | `docs/agents/CROSS_REPO_CONTRACTS.md` |
| Current active ownership | live GitHub PRs plus `docs/agents/tasks/active/**` |
| Historical work | `docs/agents/tasks/archive/**` and merged PRs |
| Module findings and evidence | relevant `docs/ai-agent/**` validation report |
| Module queue and exact next scope | module program under `docs/agents/programs/**` |

# Operating model

```text
REAL_TIBIA_EVIDENCE_SOURCES.md
        +
REAL_TIBIA_PARITY_PLAYBOOK.md
        |
        v
module registry record + generated discovery indexes
        |
        v
optional module program (long-lived queue and baselines)
        |
        v
one bounded active task + one branch + one draft PR
        |
        v
focused implementation + tests + full affected CI
        |
        v
squash merge
        |
        v
separate lifecycle/archive PR + module/program update
```

Registry metadata is an inventory and navigation contract. It never replaces a program, task, validation report, source code, tests, runtime evidence or live GitHub state, and it never proves gameplay parity.

# Module-program contract

Create a module program when a module has at least two independent findings, multiple planned PRs, cross-repository dependencies, blocked reference questions or a long-running validation effort.

A module program must contain:

- stable `program_id` and matching registry `module_id`;
- module scope and exclusions;
- target server/client versions separated from map/datapack versions;
- pinned repository and external-source baselines;
- authoritative validation report;
- completed PRs and merge commits;
- active task and PR, or an explicit `none`;
- bounded queue with one row per independently testable package;
- source conflicts and `blocked-by-reference` items;
- reusable modules and test infrastructure;
- cross-repository requirements;
- exact next action;
- a handoff that does not require the old chat.

A module program must not claim that all findings are fixed merely because one broad PR title says “complete” or “parity.” Do not create empty program files for inventory-only modules.

# Queue contract

Use at least:

| ID | Scope | Status | Evidence baseline | Dependencies | Risk | Exact next action |
|---|---|---|---|---|---|---|

Recommended statuses include `planned`, `active`, `blocked-by-reference`, `blocked-by-overlap`, `client-coupled`, `runtime-untested`, `merged`, `archived`, `superseded`, `rejected` and `no-longer-applicable`.

# Module registry

The machine-readable registry under `docs/agents/real-tibia/registry/` is the canonical module discovery graph. Each module has one independent JSON-compatible YAML record to reduce multi-agent conflicts. Generated Markdown under `docs/agents/real-tibia/generated/` is derived and must not be edited manually.

Every agent must still re-fetch current heads, PRs and active tasks. Registry path patterns are discovery hints, not edit permissions. Maturity dimensions are conservative evidence states, not release badges.

Use:

```bash
python tools/agents/real_tibia_registry.py validate
python tools/agents/real_tibia_registry.py module <module-id>
python tools/agents/real_tibia_registry.py lookup-path <repository-path>
python tools/agents/real_tibia_registry.py affected --base <base> --head <head>
python tools/agents/real_tibia_registry.py stale --only-stale
```

The initial discovery table below remains a human-oriented overview; exact identities and relationships live in the generated index.

| Module / program | Primary durable state | Governance action |
|---|---|---|
| Wheel of Destiny | module registry record, `docs/agents/programs/WHEEL_OF_DESTINY_PARITY_PROGRAM.md`, Wheel validation report | Continue only the first still-valid bounded queue item; do not reuse merged #230 as a general branch. |
| Cyclopedia / Bestiary / Bosstiary / Charms | module records, Cyclopedia validation docs and historical PRs #170, #188, #192, #203; physical-client proof is separate | Keep non-E2E validation and physical-client E2E as separate proof tracks. Create a module program before new multi-PR work. |
| Equipment Upgrade / Exaltation Forge | module record, `docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_VALIDATION.md` and current Forge tasks/PRs | Revalidate findings against current main; one bounded finding group per PR. |
| Imbuements | module record, `docs/ai-agent/IMBUEMENT_VALIDATION_REPORT.md`, runtime plan and validators | Reuse existing validation and storage tools; do not create a duplicate report or validator. |
| Achievements | module record, achievement validation docs, validators and current task/program records | Pin IDs and authoritative criteria; separate registry, award hooks, persistence and runtime proof. |
| Quests and world semantics | module records, world validation docs, Quest Map Validator and OTBM tools | Reuse the existing index/parser/resolver/rendering pipeline; never infer unresolved handlers or use AI images as map evidence. |
| OTBM tooling | module record and `docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md` | Continue the current phase queue; no duplicate parser, renderer, pathfinder or resolver. |
| CrystalServer comparison | `docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md` | CrystalServer stays read-only; one candidate per bounded task after proving the current Canary gap. |
| Universal physical-client E2E | module record and current universal E2E program/platform | Reuse the platform; do not build parallel module-specific orchestration. |
| Protocol and maintained client | module record, `CROSS_REPO_CONTRACTS.md` plus server/client task records | Require byte-exact evidence, capability gates and atomic coordination when partial rollout is unsafe. |
| Maps, spawns and NPCs | module records, OTBM World Index, reachability, spawn/NPC and script-resolution tools | Separate geometry, mechanic, spawn, definition and runtime evidence. |

# Adding another module

1. Search current files, tasks, PRs, generated path index and the module catalogue.
2. Add or update exactly one `docs/agents/real-tibia/registry/modules/<module-id>.yaml` record.
3. Locate or create a technical validation report under `docs/ai-agent/` only when detailed evidence is needed.
4. Create a module program only when multiple independent packages are expected.
5. Register the program path in the module record and keep both documents consistent.
6. Pin current Canary, maintained client, upstream and donor SHAs as applicable.
7. Create the first bounded task only after the comparison matrix identifies a real finding.
8. Regenerate and validate derived indexes.
9. Do not create an empty implementation PR merely to show activity.

Suggested names:

```text
docs/agents/real-tibia/registry/modules/<module-id>.yaml
docs/agents/programs/<MODULE>_PARITY_PROGRAM.md
CAN-PROGRAM-<MODULE>-PARITY
<MODULE>-001
CAN-YYYYMMDD-<module>-<bounded-scope>
```

# Source refresh policy

Before each new task record:

- current `blakinio/canary:main`;
- relevant `blakinio/otclient` SHA when protocol/UI matters;
- relevant `opentibiabr/canary` SHA when used;
- exact selected `zimbadev/crystalserver` SHA when used;
- official publication date and client build;
- whether the task continues the last audited donor baseline or intentionally re-audits another one;
- registry freshness and whether the module record's scope/relationships still match current source.

# Broad-task prevention

Do not create tasks such as “complete Wheel 15.25,” “fix all Forge findings,” “validate every achievement,” “make Cyclopedia fully compatible” or “import CrystalServer improvements.”

Split by independently testable state transition, protocol contract, formula family, persistence boundary, quest package, geometry region or validator contract. A broad historical task that partially delivered must be archived as superseded/partially completed and decomposed into queue entries.

# Staleness rules

Signals requiring a dedicated documentation/coordination repair include:

- a merged PR still shown as draft or active;
- an archived/deleted branch shown as current;
- a task with an old head or blank PR after merge;
- acceptance criteria claiming an entire module where only one package merged;
- `ACTIVE_WORK.md` disagreeing with live PRs/tasks;
- a validation report presenting historical CI as current-main proof;
- a moving external branch recorded without an exact SHA;
- a registry module past its warning/invalid freshness threshold;
- generated indexes differing from the registry records.

Do not combine stale-state repair with gameplay changes.

# Program validation matrix

Each module program must maintain or link:

| Mechanic | Definition | Registration | Runtime | Persistence | Protocol | Behavior test | Gameplay/E2E | Source agreement | Current status |
|---|---|---|---|---|---|---|---|---|---|---|

One green test, one maturity field or one matching source is not full parity.

# Global safety invariants

- no writes to upstream or donor repositories;
- no direct push to `main`;
- no whole-module donor copy;
- no invented values, IDs, handlers, coordinates or packet fields;
- no `unresolved` promoted to handled;
- no manual `ACTIVE_WORK.md` edits in normal feature tasks;
- no manual edits to `docs/agents/real-tibia/generated/**`;
- no `.otbm`, `.widx`, `items.otb`, proprietary assets, secrets or large generated reports committed;
- no AI-generated image used as map proof;
- no cross-branch staging workflow used to mutate another PR;
- no claim of full parity without explicit proof at every required level.

# Governance bootstrap

The repository-wide parity governance bootstrap was completed by task `CAN-20260714-real-tibia-parity-governance` and PR #318.

- final feature head: `845260ff8f67144a8850e47129d1fdd90e54ff21`;
- squash merge: `8dd09bddbc7a492660472e29ef576578691f3d91`;
- delivered playbook, global program, Wheel program, startup routing, catalogue/changelog entries and stale Wheel task/index repair;
- archived task: `docs/agents/tasks/archive/CAN-20260714-real-tibia-parity-governance.md`.

The registry-as-code foundation was completed by task `CAN-20260714-real-tibia-module-registry` and PR #324.

- final feature head: `9710dddfd370fe32ed940c676279dbb77ccbd996`;
- squash merge: `dddf8e453512547c979ebd7ed6cb60e8fcac2d65`;
- delivered 18 module records, schemas, deterministic tooling/tests, five generated indexes, templates, ADR and required CI;
- archived task: `docs/agents/tasks/archive/CAN-20260714-real-tibia-module-registry.md`.

# Active tasks

None at program level. Module work belongs in the relevant module program and its own bounded task. Upstream monitoring must use a separate program and must not turn observations directly into implementation.

# Handoff

A new agent starting any Real Tibia parity task must identify the registry module, re-fetch live GitHub state and source baselines, inspect its dependency/path/source/freshness metadata, and select one bounded still-valid queue item. When no module program exists and multiple findings are expected, the first deliverable is a docs-only program/evidence record, not speculative broad implementation.
