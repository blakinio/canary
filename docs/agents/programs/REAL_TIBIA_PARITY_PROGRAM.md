---
program_id: CAN-PROGRAM-REAL-TIBIA-PARITY
name: Real Tibia Parity Program
status: active
owner: repository-wide
created: 2026-07-14T09:00:00+02:00
updated: 2026-07-14T09:00:00+02:00
last_verified_commit: "bd5c7bee5a0524dedcd786ef52152f475dd424a6"
primary_paths:
  - docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md
  - docs/agents/REAL_TIBIA_PARITY_PLAYBOOK.md
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
- module-specific long-lived programs;
- small active tasks and PRs;
- technical validation reports;
- cross-repository and physical-client proof.

# Authoritative documents

| Purpose | Document |
|---|---|
| Source roles, provenance and donor registry | `docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md` |
| Mandatory operational procedure | `docs/agents/REAL_TIBIA_PARITY_PLAYBOOK.md` |
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
module program (long-lived queue and baselines)
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
separate lifecycle/archive PR + module queue update
```

A chat may initiate work, but it is never the durable source of truth.

# Module-program contract

Create a module program when a module has at least two independent findings, multiple planned PRs, cross-repository dependencies, blocked reference questions or a long-running validation effort.

A module program must contain:

- stable `program_id`;
- module scope and excluded areas;
- target server/client versions separated from map/datapack versions;
- current pinned repository baselines;
- authoritative validation report;
- completed PRs and merge commits;
- active task and PR, or an explicit statement that none exists;
- bounded queue with one row per independently testable package;
- source conflicts and `BLOCKED_BY_REFERENCE` items;
- reusable modules and test infrastructure;
- cross-repository requirements;
- exact next action;
- handoff instructions that do not require the old chat.

A module program must not claim that all findings are fixed merely because one broad PR title says “complete” or “parity.”

# Required queue fields

Use this minimum table:

| ID | Scope | Status | Evidence baseline | Dependencies | Risk | Exact next action |
|---|---|---|---|---|---|---|

Recommended statuses:

- `planned`;
- `active`;
- `blocked-by-reference`;
- `blocked-by-overlap`;
- `client-coupled`;
- `runtime-untested`;
- `merged`;
- `archived`;
- `superseded`;
- `rejected`;
- `no-longer-applicable`.

# Initial module registry

This table is a discovery index, not a replacement for live GitHub state. Every agent must re-fetch current heads, PRs and task records.

| Module / program | Primary durable state | Current governance action |
|---|---|---|
| Wheel of Destiny | `docs/agents/programs/WHEEL_OF_DESTINY_PARITY_PROGRAM.md`, `docs/ai-agent/OTS_AI_WHEEL_OF_DESTINY_VALIDATION.md` | Continue only the first bounded open queue item; do not reuse merged #230 as a general branch. |
| Cyclopedia / Bestiary / Bosstiary / Charms | Cyclopedia validation documents under `docs/ai-agent/**`; historical PRs #170, #188, #192, #203; paused physical-client experiment #224 | Treat non-E2E validation and physical-client E2E as separate proof tracks. Create a module program before new multi-PR work. |
| Equipment Upgrade / Exaltation Forge | `docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_VALIDATION.md` and active Forge tasks/PRs | Revalidate historical findings against current main; one bounded finding group per PR. |
| Imbuements | `docs/ai-agent/IMBUEMENT_VALIDATION_REPORT.md`, runtime plan and validators | Reuse existing validation and storage tools; do not create a duplicate report or validator. |
| Achievements | achievement validation documents, validators and current program/task records | Pin achievement IDs and authoritative criteria; keep award hooks, registry metadata and persistence proof separate. |
| Quests and world semantics | `docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md`, Quest Map Validator and OTBM tools | Reuse existing parser/index/resolver/rendering pipeline; never infer unresolved handlers or use AI images as map evidence. |
| OTBM tooling | `docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md` | Continue phase queue from current main; no duplicate parser, renderer, pathfinder or resolver. |
| CrystalServer comparison | `docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md` | CrystalServer stays read-only; one candidate per bounded task after current-Canary proof. |
| Universal physical-client E2E | program/PR associated with #245 when merged and stable | Reuse it for client proof; do not build parallel module-specific orchestration. |
| Protocol and maintained client | `CROSS_REPO_CONTRACTS.md` plus server/client task records | Require byte-exact evidence, version gates and atomic coordination when partial rollout is unsafe. |
| Maps, spawns and NPCs | OTBM World Index, reachability, spawn/NPC and script-resolution tools | Separate geometry, mechanic, spawn, definition and runtime evidence. |

# Adding another Tibia module

When work starts on a module not listed above:

1. search current files, tasks, PRs and module catalogue;
2. locate or create a technical validation report under `docs/ai-agent/`;
3. create a module program only if more than one independent package is expected;
4. register the program in this table;
5. pin current Canary, upstream, CrystalServer and maintained-client SHAs as applicable;
6. create the first bounded task only after the comparison matrix identifies a real finding;
7. do not create an empty implementation PR merely to show activity.

Suggested program filename:

```text
docs/agents/programs/<MODULE>_PARITY_PROGRAM.md
```

Suggested identifiers:

```text
CAN-PROGRAM-<MODULE>-PARITY
<MODULE>-001
CAN-YYYYMMDD-<module>-<bounded-scope>
```

# Source update policy

Module programs pin the last verified baselines, but they must not hide source drift.

Before each new task:

- record current `blakinio/canary:main`;
- record current relevant `blakinio/otclient` commit when protocol/UI matters;
- record current `opentibiabr/canary` commit when used;
- record current or intentionally selected `zimbadev/crystalserver` commit;
- record official source date/client build;
- explain whether the task continues from the last audited donor commit or deliberately re-audits an older area.

# Broad-task prevention

Do not create tasks such as:

- “complete Wheel 15.25”;
- “fix all Forge findings”;
- “validate every achievement”;
- “make Cyclopedia fully compatible”;
- “import CrystalServer improvements.”

Instead, split by independently testable state transition, protocol contract, formula family, persistence boundary, quest package, geometry region or validator contract.

A broad historical task that partially delivered must be archived as superseded/partially completed and decomposed into module queue entries. It must not remain an active lock forever.

# Staleness rules

The following are stale-state signals:

- a merged PR still shown as draft/active;
- an archived or deleted branch shown as current work;
- a task with old head SHA or blank PR after merge;
- acceptance criteria claiming an entire module while only one package merged;
- `ACTIVE_WORK.md` disagreeing with live PRs and tasks;
- a validation report presenting historical CI as current-main evidence;
- a moving external branch recorded without exact SHA.

Repair stale state in a dedicated docs/coordination PR. Do not combine it with gameplay changes.

# Program-level validation matrix

Each module program should maintain or link a matrix with these dimensions:

| Mechanic | Definition | Registration | Runtime | Persistence | Protocol | Behavior test | Gameplay/E2E | Source agreement | Current status |
|---|---|---|---|---|---|---|---|---|---|

This prevents one green test or one matching source from being misrepresented as full parity.

# Global safety invariants

- no writes to upstream/donor repositories;
- no direct push to `main`;
- no whole-module donor copy;
- no invented values, IDs, handlers, coordinates or packet fields;
- no `unresolved` promoted to handled;
- no manual `ACTIVE_WORK.md` edits in normal feature tasks;
- no `.otbm`, `.widx`, `items.otb`, proprietary assets, secrets or large generated reports committed;
- no AI-generated image used as map proof;
- no cross-branch staging workflow used to mutate another PR;
- no claim of full parity without explicit proof at every required level.

# Active tasks

At creation of this program, the governance task is:

| Task | Branch | State | Exact next action |
|---|---|---|---|
| `CAN-20260714-real-tibia-parity-governance` | `docs/real-tibia-parity-governance` | implementing | Add the playbook, seed module programs, repair stale Wheel coordination, validate and merge. |

After this task is archived, this section should normally say `none`; module work is tracked in the relevant module program.

# Handoff

A new agent starting any Real Tibia parity task must first identify the module program. When no module program exists and the scope has multiple independent findings, the first deliverable is a docs-only program record and evidence inventory, not a speculative broad implementation.
