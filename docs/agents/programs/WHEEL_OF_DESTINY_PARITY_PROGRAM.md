---
program_id: CAN-PROGRAM-WHEEL-OF-DESTINY-PARITY
name: Wheel of Destiny Parity
status: active
owner: unassigned
created: 2026-07-14T09:00:00+02:00
updated: 2026-07-14T10:20:00+02:00
last_verified_commit: "d88e7f354eb5b33068cdded7696e9cdb89b05268"
primary_paths:
  - src/creatures/players/components/wheel/**
  - src/io/io_wheel.*
  - src/server/network/protocol/protocolgame.*
  - src/creatures/combat/**
  - data/scripts/spells/**
  - data/modules/scripts/taskboard/**
  - tests/unit/players/**
  - tests/integration/**
  - docs/ai-agent/OTS_AI_WHEEL_OF_DESTINY_VALIDATION.md
  - docs/ai-agent/OTS_AI_WHEEL_OF_DESTINY_VALIDATION_PROJECT.md
shared_integration_paths:
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
related_programs:
  - CAN-PROGRAM-REAL-TIBIA-PARITY
  - CAN-PROGRAM-CRYSTALSERVER-COMPARISON
cross_repo_contracts: []
---

# Mission

Continue evidence-based Wheel of Destiny parity as a sequence of bounded, independently testable packages. Do not rely on the title of a historical PR, a single wiki page or a donor implementation as proof of full Tibia 15.25 compatibility.

# Mandatory reads

Before starting a Wheel task, read:

- `AGENTS.md`;
- `docs/agents/README.md`;
- `docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md`;
- `docs/agents/REAL_TIBIA_PARITY_PLAYBOOK.md`;
- `docs/agents/programs/REAL_TIBIA_PARITY_PROGRAM.md`;
- this program;
- `docs/ai-agent/OTS_AI_WHEEL_OF_DESTINY_VALIDATION.md`;
- `docs/ai-agent/OTS_AI_WHEEL_OF_DESTINY_VALIDATION_PROJECT.md`;
- current active Wheel task and PR, when any exists;
- current CrystalServer comparison program and selected Wheel files when CrystalServer is used;
- current maintained OTClient packet/UI implementation when protocol or client interpretation is involved.

# Baseline register

These are historical pinned facts. Re-fetch current heads before each new task.

| Role | Repository/source | Recorded baseline | Access | Purpose |
|---|---|---|---|---|
| implementation target | `blakinio/canary` | current observed main at last program update: `d88e7f354eb5b33068cdded7696e9cdb89b05268` | task branches/PRs | authoritative current server behavior |
| maintained client | `blakinio/otclient` | pin per task | read-only unless separately authorized | packet fields, capability gates and UI interpretation |
| maintained upstream | `opentibiabr/canary` | pin per task | read-only | upstream conventions and already-available fixes |
| donor comparison | `zimbadev/crystalserver` | pin exact SHA per task | read-only | candidate implementation and architectural comparison |
| official behavior | Tibia official update material and controlled observation | pin publication/client build per task | read-only | announced names, values and visible behavior |
| secondary gameplay reference | TibiaWiki/Fandom Wheel of Destiny | capture date per task | read-only | terminology, values, thresholds and history; never sufficient alone |

Server protocol version, official client build, map/datapack revision and source repository SHA are separate baselines and must not be conflated.

# Completed history

| Package | PR | Final result | Merge commit | Proof boundary |
|---|---:|---|---|---|
| Evidence-based Wheel audit and hardening | #220 | allocation, persistence/protocol hardening, Gem Atelier safety and supported 15.25 values | `35ff51ac022e36d215db9d0fa86053b326a0bdf0` | source, focused tests and full affected CI; not full gameplay parity |
| Audit-document synchronization | #229 | validation report records integration and remaining gaps | `ac218d540d9b357f6d895d4d1fc38326f47071d4` | documentation only |
| Hunting Task Shop promotion points | #230 | official Bonus Promotion offer, bounded 1–50 purchase cost, player KV/cache, Wheel accounting and corrected client payload field | `d4e8933b78587445afd9347a6d05b6e715c6c0e4` | dedicated validation and full platform CI; runtime purchase/relogin/failure-injection remains separate proof |

PR #230 had the broad title `complete Tibia 15.25 runtime parity`, but its actual diff delivered the Hunting Task Shop package. It did not complete every remaining Wheel subsystem.

Historical branch `feat/wheel-15-25-runtime-completion` and PR #230 are complete and must not be continued or reopened.

Technical staging PR #279 for Blessing critical healing was closed without merge and is obsolete. It is not a source branch and must not be reused.

# Current state

The audit/hardening baseline and Hunting Task Shop points are merged. The historical broad task `CAN-20260713-wheel-15-25-runtime-completion` is archived as `superseded`; it is not an active ownership lock. Several independently testable 15.25 packages remain open or blocked by evidence and are tracked only through the queue below.

# Queue

| ID | Scope | Status | Evidence baseline | Dependencies | Risk | Exact next action |
|---|---|---|---|---|---|---|
| `WHEEL-001` | Audit and confirmed hardening | merged | PR #220/#229 and validation report | none | high | Preserve regressions; do not reopen without new evidence. |
| `WHEEL-002` | Hunting Task Shop Wheel points | merged; runtime scenarios incomplete | PR #230, client payload interpretation, player KV/cache | optional universal E2E for physical-client proof | medium | Add a separate runtime/persistence test package only if current evidence identifies a specific missing proof or defect. |
| `WHEEL-003` | Blessing of the Grove critical healing | planned; next preferred bounded behavior package | official 15.25 description, current healing/critical runtime, wiki as secondary, CrystalServer/upstream comparison if present | exact formula/order and deterministic RNG seam | high | Build a source matrix, prove current absence, then create one focused task/PR. |
| `WHEEL-004` | Vocation stance state contract | planned | official behavior, client fields/capabilities, current server state lifecycle, donor comparison | persistence, login/death/vocation-change decisions | high | Produce a docs/evidence contract before runtime implementation if protocol/state mapping remains uncertain. |
| `WHEEL-005` | Knight replacement spells | blocked-by-reference until exact behavior is pinned | official source/captures, current spell runtime, maintained client where relevant | stance contract | high | Split Shield Bash and Shield Slam only after exact formulas, restrictions and registration names are proven. |
| `WHEEL-006` | Paladin replacement spells | blocked-by-reference until exact behavior is pinned | official source/captures and current spell runtime | stance contract | high | Split Divine Barrage and Ethereal Barrage into the smallest coherent packages. |
| `WHEEL-007` | Sorcerer/Druid replacement spells | blocked-by-reference until exact behavior is pinned | official source/captures and current spell runtime | stance contract | high | Separate Death Echo, Forked Glacier and Forked Thorns by independently testable behavior. |
| `WHEEL-008` | Thousand Fist Blows / Monk replacement behavior | blocked-by-reference | official source/captures and current Monk runtime | stance and Monk-specific contracts | high | Do not infer from an obsolete spell with a similar name. |
| `WHEEL-009` | Remaining passive and Revelation reworks | planned; must be decomposed | validation report, official values, current runtime and donor comparison | independent per passive/family | high | Create one queue/task entry per state transition or formula family, not one broad PR. |
| `WHEEL-010` | Strong Ice Wave authoritative geometry | blocked-by-reference | reproducible official visual/geometry evidence | deterministic area tests | medium | Do not implement a guessed tile shape. Store evidence and exact orientation transforms first. |
| `WHEEL-011` | DB/KV round trip and failure injection | planned | current persistence paths and #220/#230 changes | temporary DB/KV test environment | high | Split by state boundary: slots, gems/grades, Task Shop counter and rollback. |
| `WHEEL-012` | Protocol malformed-input and version-profile coverage | planned/client-coupled | server parser, maintained client and byte-exact fixtures | cross-repository contract if client changes | high | Prove exact packet layouts and capability behavior before change. |
| `WHEEL-013` | Gameplay and physical-client E2E | depends on reusable platform | universal E2E program/PR after merge and stabilization | all targeted feature packages | high | Reuse universal platform; never create another Wheel-only orchestration stack. |

# Preferred next bounded scope

`WHEEL-003` — Blessing of the Grove critical healing — is the preferred next behavior package only after a fresh overlap search and current source comparison confirm it remains missing.

A task must not be created merely because this table says `planned`. First revalidate current `main`, active PRs and source baselines.

# Required Wheel comparison matrix

For each queue item, add or update a matrix in the task and validation report:

| Mechanic | Official Tibia | TibiaWiki/Fandom | CrystalServer | OpenTibiaBR | current Canary | maintained OTClient | tests/runtime | Conclusion |
|---|---|---|---|---|---|---|---|---|

For critical healing specifically, determine:

- whose critical chance is used;
- whose critical extra value is used;
- ordering relative to Blessing low-health scaling, Battle Healing, Healing Link and other modifiers;
- self-heal versus healing another player;
- non-player sources;
- damage/negative values;
- visual/message behavior, if part of the contract;
- deterministic testability without changing production randomness semantics.

Do not implement from a chat summary alone.

# Bounded task rules

Each Wheel task must:

- own only the relevant Wheel/combat/spell/persistence paths;
- keep `docs/agents/ACTIVE_WORK.md` read-only;
- update the validation report after a behavior conclusion changes;
- update this program queue and completed history;
- add focused deterministic tests;
- run full affected CI on the final ready head;
- archive the task separately after merge.

Do not combine stance state, multiple vocation spell families, critical healing, geometry and persistence failure injection in one PR.

# CrystalServer use

When CrystalServer contains a corresponding Wheel implementation:

- pin exact SHA;
- inventory selected files and active registrations;
- identify Crystal-only dependencies;
- compare exact behavior with current Canary and official evidence;
- classify the candidate using the parity playbook;
- adapt only a proven, smallest unit.

Similar names are not proof of equivalent mechanics. CrystalServer constants are not official values unless independently confirmed.

# Validation expectations

A C++ Wheel behavior PR normally requires:

- focused deterministic unit tests;
- Wheel validation workflow;
- Agent Task Ownership and AI Agent Tools;
- Fast Checks;
- Linux debug plus C++ tests and schema import;
- Linux release and runtime smoke;
- Windows, macOS and Docker affected builds;
- actual `Required` success on the final head;
- confirmation that builds were not skipped because the PR remained draft.

Persistence/protocol packages additionally require round-trip, corrupt/missing/legacy state, malformed packet and rollback/failure tests as applicable.

# Active tasks

None. A new task may be created only from current `main` after a fresh overlap and evidence preflight.

# Handoff

Start by re-fetching current main, open PRs, active tasks and the current Wheel validation report. Never reopen #220, #229 or #230. Select only the first still-valid bounded queue item, create a new task/branch/draft PR, and preserve all evidence and CI state in GitHub before context exhaustion.