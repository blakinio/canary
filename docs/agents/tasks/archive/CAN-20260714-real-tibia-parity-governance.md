---
task_id: CAN-20260714-real-tibia-parity-governance
program_id: CAN-PROGRAM-REAL-TIBIA-PARITY
coordination_id: REAL-TIBIA-PARITY
status: merged
agent: GPT-5.6 Thinking
branch: docs/real-tibia-parity-governance
base_branch: main
created: 2026-07-14T09:00:00+02:00
updated: 2026-07-14T10:55:00+02:00
last_verified_commit: "845260ff8f67144a8850e47129d1fdd90e54ff21"
risk: low
related_issue: ""
related_pr: "#318"
depends_on:
  - "AGENTS.md and docs/agents governance"
  - "docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md"
  - "docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md"
blocks: []
owned_paths:
  exclusive:
    - docs/agents/REAL_TIBIA_PARITY_PLAYBOOK.md
    - docs/agents/programs/REAL_TIBIA_PARITY_PROGRAM.md
    - docs/agents/programs/WHEEL_OF_DESTINY_PARITY_PROGRAM.md
    - docs/agents/tasks/archive/CAN-20260714-real-tibia-parity-governance.md
    - docs/agents/tasks/archive/CAN-20260713-wheel-15-25-runtime-completion.md
  shared:
    - docs/agents/README.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
    - docs/agents/ACTIVE_WORK.md
  read_only:
    - AGENTS.md
    - docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md
    - docs/agents/REPOSITORY_MAP.md
    - docs/agents/KNOWN_RISKS.md
    - docs/agents/BUILD_TEST_MATRIX.md
    - docs/agents/CROSS_REPO_CONTRACTS.md
    - docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md
    - docs/ai-agent/OTS_AI_WHEEL_OF_DESTINY_VALIDATION.md
    - docs/ai-agent/OTS_AI_WHEEL_OF_DESTINY_VALIDATION_PROJECT.md
modules_touched:
  - Real Tibia parity governance
  - evidence precedence and provenance
  - module program lifecycle
  - Wheel of Destiny parity program
reuses:
  - existing task/program records
  - Real Tibia evidence registry
  - CrystalServer comparison methodology
  - current autonomous merge and ownership policy
public_interfaces:
  - repository-wide Real Tibia parity playbook
  - program record and module queue contract
cross_repo_tasks: []
---

# Goal

Make repository documentation, rather than chat history or large repeated prompts, the durable source of truth for evidence-based Real Tibia parity work across all Tibia modules.

# Delivered

PR #318 added:

- `docs/agents/REAL_TIBIA_PARITY_PLAYBOOK.md`;
- `docs/agents/programs/REAL_TIBIA_PARITY_PROGRAM.md`;
- `docs/agents/programs/WHEEL_OF_DESTINY_PARITY_PROGRAM.md`;
- the mandatory parity startup route in `docs/agents/README.md`;
- module-catalogue and changelog discovery entries;
- truthful archival of the broad historical Wheel task as `superseded`;
- dedicated removal of merged PR #230 from the stale `ACTIVE_WORK.md` snapshot.

The governance requires exact source provenance, question-specific source precedence, cross-source comparison matrices, explicit proof levels, one bounded task/branch/PR per independently testable package, honest DNS/CI boundaries and durable program/task handoff.

# Validation

Feature final head: `845260ff8f67144a8850e47129d1fdd90e54ff21`.

- Agent Task Ownership run `29319009640`: success.
- Ready-state CI run `29319009674`: success.
- Detect Build Scope job `87039548705`: success.
- Fast Checks job `87039548725`: success.
- Lua Tests job `87039548780`: success.
- Linux release compile/configuration and generated-doc validation job `87039815644`: success.
- Required job `87041024161`: success.
- Windows, macOS and Docker were correctly skipped for docs-only scope.
- PR #318 was mergeable, had no requested changes and zero unresolved review threads.
- Exact changed-file list contained only ten documentation/coordination paths.
- No runtime, Lua, protocol, workflow, database, map, OTBM, item, asset, secret or upstream repository mutation was included.

These checks prove repository governance/documentation integration. They do not prove gameplay, protocol, persistence or physical-client behavior, which PR #318 did not change.

# Completion

- Final status: merged.
- Feature PR: #318.
- Final feature head: `845260ff8f67144a8850e47129d1fdd90e54ff21`.
- Feature squash merge: `8dd09bddbc7a492660472e29ef576578691f3d91`.
- Rollback: revert `8dd09bddbc7a492660472e29ef576578691f3d91`.
- Archived at: `docs/agents/tasks/archive/CAN-20260714-real-tibia-parity-governance.md`.

# Handoff

New agents must start with `AGENTS.md`, `docs/agents/README.md`, `REAL_TIBIA_EVIDENCE_SOURCES.md`, `REAL_TIBIA_PARITY_PLAYBOOK.md`, the global parity program and the relevant module program. They must re-fetch current GitHub state and create only one bounded active task. For Wheel of Destiny, use `WHEEL_OF_DESTINY_PARITY_PROGRAM.md`; do not reopen #230 or continue `feat/wheel-15-25-runtime-completion`.