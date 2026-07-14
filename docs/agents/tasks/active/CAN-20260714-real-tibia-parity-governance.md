---
task_id: CAN-20260714-real-tibia-parity-governance
program_id: CAN-PROGRAM-REAL-TIBIA-PARITY
coordination_id: REAL-TIBIA-PARITY
status: ready
agent: GPT-5.6 Thinking
branch: docs/real-tibia-parity-governance
base_branch: main
created: 2026-07-14T09:00:00+02:00
updated: 2026-07-14T10:40:00+02:00
last_verified_commit: "b723ce42cdbb6b3e5f98b2ea28efe684d64cd3c9"
risk: low
related_issue: ""
related_pr: "#318"
depends_on:
  - "AGENTS.md and docs/agents governance"
  - "docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md"
  - "docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md"
blocks:
  - "future Real Tibia module audits should use this governance before implementation"
owned_paths:
  exclusive:
    - docs/agents/REAL_TIBIA_PARITY_PLAYBOOK.md
    - docs/agents/programs/REAL_TIBIA_PARITY_PROGRAM.md
    - docs/agents/programs/WHEEL_OF_DESTINY_PARITY_PROGRAM.md
    - docs/agents/tasks/active/CAN-20260714-real-tibia-parity-governance.md
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
  - program record template and module queue contract
cross_repo_tasks: []
---

# Goal

Make repository documentation, rather than chat history or large repeated prompts, the durable source of truth for evidence-based Real Tibia parity work across all Tibia modules.

# Problem

The repository contains many independent systems such as Wheel of Destiny, Cyclopedia, Equipment Upgrade, Imbuements, Achievements, quests, NPCs, spawns, protocol, persistence and map mechanics. Repeating source precedence, provenance, task lifecycle, CI, DNS and handoff rules in every prompt is error-prone and does not survive context exhaustion.

# Acceptance criteria

- [x] Add one mandatory parity playbook covering startup, evidence precedence, source pinning, comparison matrix, bounded implementation, validation, CI and lifecycle.
- [x] Add one repository-wide program record explaining how module-specific parity programs are registered and continued.
- [x] Add a Wheel of Destiny program record reflecting merged PRs #220, #229 and #230 and the still-open bounded queue.
- [x] Require agents to treat official Tibia material, current Canary, maintained OTClient, OpenTibiaBR, CrystalServer and wiki sources according to their evidence dimension rather than one global ranking.
- [x] Require exact repository SHAs, paths, symbols, dates and proof levels for conclusions.
- [x] Require one bounded task/branch/PR per independently testable finding.
- [x] Require stale broad tasks to be archived or superseded instead of reused indefinitely.
- [x] Document local DNS failure handling without claiming that CI replaces local testing.
- [x] Document physical-client E2E as a separate proof level and require reuse of the universal E2E program when ready.
- [x] Make the new governance discoverable from mandatory startup documentation and the module catalogue.
- [x] Repair the stale #230 coordination state only through this dedicated governance/index task; normal feature tasks must not edit ACTIVE_WORK.md.
- [x] No runtime, Lua, protocol, database, map, asset, workflow or production configuration changes.
- [x] Review exact changed files and confirm no upstream repository mutation.
- [x] Current-head required documentation/ownership checks pass.
- [ ] Merge this docs-only PR and archive this task separately.

# Confirmed baseline

- Current observed `main` at PR creation: `d88e7f354eb5b33068cdded7696e9cdb89b05268`.
- `REAL_TIBIA_EVIDENCE_SOURCES.md` defines source roles and prohibits treating one public source as complete truth.
- `CRYSTALSERVER_COMPARISON_PROGRAM.md` defines bounded read-only candidate comparison and classifications.
- PR #230 is merged as `d4e8933b78587445afd9347a6d05b6e715c6c0e4`.
- PR #230 delivered Hunting Task Shop Wheel points, not full Wheel 15.25 parity.
- The historical task is archived as `superseded` and its broad ownership claim is removed.
- Normal feature tasks must not edit `docs/agents/ACTIVE_WORK.md`; this task is intentionally a dedicated governance/index repair.

# Delivered files

1. `docs/agents/REAL_TIBIA_PARITY_PLAYBOOK.md` — mandatory operational procedure.
2. `docs/agents/programs/REAL_TIBIA_PARITY_PROGRAM.md` — repository-wide registry and module-program contract.
3. `docs/agents/programs/WHEEL_OF_DESTINY_PARITY_PROGRAM.md` — current Wheel state and bounded queue.
4. `docs/agents/README.md` — mandatory startup route for parity work.
5. `docs/agents/MODULE_CATALOG.md` and `docs/agents/CHANGELOG.md` — discovery entries.
6. `docs/agents/tasks/archive/CAN-20260713-wheel-15-25-runtime-completion.md` — truthful superseded lifecycle record.
7. `docs/agents/ACTIVE_WORK.md` — stale merged #230 row removed by this dedicated coordination repair.

# Validation

- Local checkout: not used for this task.
- Repository read/write operations: GitHub API.
- The branch was rebuilt as one commit directly on current `main` after the initial branch diverged; PR #318 is mergeable.
- Exact changed files: ten documentation/coordination paths listed in PR #318; no runtime, workflow, map, OTBM, asset, database or upstream path.
- Agent Task Ownership run `29318027196`: success on head `b723ce42cdbb6b3e5f98b2ea28efe684d64cd3c9`.
- Ready-state repository CI run `29318083332`: success on the same head.
- CI job `87036638662` Fast Checks: success.
- CI job `87036638675` Detect Build Scope: success.
- CI job `87036638688` Lua Tests: success.
- CI job `87037119817` Linux release configure/compile and generated-doc validation: success; runtime/database/test steps correctly skipped for the docs-only scope.
- CI job `87038915798` Required: success.
- Windows, macOS and Docker jobs were skipped by the detected docs-only scope; no runtime build claim is derived from those skipped jobs.
- Review threads: zero before this validation update.

This validation proves repository policy, formatting, Lua test, Linux release compile/configuration and aggregate required-check success for the reviewed documentation head. It does not constitute gameplay, protocol, persistence or physical-client proof, none of which is changed by this PR.

# Rollback

Revert the eventual squash merge. The change affects only agent-facing documentation, module/program discovery and stale coordination metadata.

# Remaining work

1. Verify the checks produced for this final task-record update.
2. Reconfirm mergeability, changed files, requested reviews and review threads.
3. Squash-merge PR #318 after the final-head `Required` succeeds.
4. Create a separate lifecycle PR that archives this governance task and marks the global program's governance bootstrap complete.

# Handoff

Read this task, the three new governance/program files, `REAL_TIBIA_EVIDENCE_SOURCES.md`, `CRYSTALSERVER_COMPARISON_PROGRAM.md`, PR #318, current open PRs and current active tasks. Do not start a module implementation until the playbook preflight and overlap checks are complete. Do not reopen PR #230 or reuse its historical branch.