---
task_id: CAN-20260716-security-validation-foundation
program_id: CAN-PROGRAM-SECURITY-VALIDATION
coordination_id: OTS-SEC-001
status: active
agent: "GPT-5.5 Thinking"
branch: feat/security-validation-foundation
base_branch: main
created: 2026-07-16T20:10:00+02:00
updated: 2026-07-16T20:25:00+02:00
last_verified_commit: "89fbf6c8097fefcad14a5dca5b195aa4672bbb14"
risk: medium
related_issue: ""
related_pr: "433"
depends_on:
  - "Universal OTS E2E automation / CAN-PROGRAM-E2E-PLATFORM"
blocks:
  - "future runtime offensive-security adapters"
owned_paths:
  exclusive:
    - tools/security/**
    - tests/security/**
    - docs/security/**
    - docs/agents/programs/SECURITY_VALIDATION_PROGRAM.md
    - docs/agents/decisions/ADR-20260716-security-validation-platform-boundary.md
    - docs/agents/tasks/active/CAN-20260716-security-validation-foundation.md
    - .github/workflows/security-validation.yml
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/e2e/**
    - tests/e2e/**
    - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
    - data/libs/functions/fs.lua
    - data/libs/functions/tables.lua
    - tests/lua/test_fs.lua
    - tests/lua/test_tables.lua
    - tests/unit/lua/filesystem_functions_test.cpp
modules_touched:
  - OTS Security Validation Platform foundation
reuses:
  - Universal OTS E2E automation for future disposable runtime lifecycle
  - existing shell-free Lua filesystem regression from PR #326
  - existing safe table.unserialize regression from PR #328
public_interfaces:
  - ots-security-scenario-v1
  - ots-security-validation-report-v1
  - tools/security/security_validation.py CLI
cross_repo_tasks: []
---

# Goal

Create the smallest reusable foundation for an OTS-wide security validation platform without duplicating Universal E2E lifecycle orchestration. The first slice provides a strict security-scenario registry, deterministic source-regression executor and machine-readable reports for the current Canary target, while keeping runtime fuzzing, protocol attack drivers, MyAAC, client, database and Otheryn adapters as later bounded extensions.

# Acceptance criteria

- [x] Define an ADR separating reusable security-scenario orchestration from existing Universal E2E runtime lifecycle.
- [x] Add a strict versioned scenario contract with explicit repository authorization and no arbitrary command execution from manifests.
- [x] Add a Python 3.12 standard-library CLI to list, validate and execute deterministic source-regex security scenarios.
- [x] Constrain scenario source/evidence paths to repository-relative regular files and reject escapes, symlinks and oversized inputs.
- [x] Emit deterministic machine-readable `ots-security-validation-report-v1` reports with source SHA-256 evidence and exact findings.
- [x] Seed the registry with regressions for the merged `FS.mkdir` shell-execution fix (#326) and `table.unserialize` arbitrary-evaluation fix (#328), reusing their existing test evidence rather than replacing it.
- [x] Add focused unit tests for schema rejection, path confinement, regex validation, pass/fail behavior and report determinism.
- [x] Add a dedicated security-validation workflow that runs registry validation, focused tests, bytecode compilation and all seeded scenarios.
- [x] Document the future adapter boundary for Canary/Otheryn server, maintained client, MyAAC, MariaDB and Redis; runtime execution must reuse Universal E2E and remain isolated/authorized.
- [ ] Update module catalogue and changelog narrowly.
- [ ] Review exact changed-file scope and pass required exact-head CI before merge.

# Evidence and constraints

- `PROVEN`: task-start `main` was `0f25e7fd4d41e90f17fc95d13dba84b7e81d1681`; current `main` advanced through lifecycle cleanup `e7f7b9601d41436a105308efa933f16917bc1b39`.
- `PROVEN`: open PR #432 owns only OAM-005 documentation/task paths and does not overlap this task.
- `PROVEN`: open PR #426 marks `MODULE_CATALOG.md` and `CHANGELOG.md` as shared, not exclusive; this task will edit them narrowly from current main content.
- `PROVEN`: Universal E2E already owns disposable MariaDB, Canary, controlled OTClient, evidence and cleanup lifecycle; this task does not create a second runtime orchestrator.
- `PROVEN`: Universal Agent Load already enforces literal-loopback-only targets for its status-protocol load runner; this task does not duplicate that runner.
- `PROVEN`: PR #326 removed shell execution from `FS.mkdir`/`FS.mkdir_p`; PR #328 removed `loadstring` evaluation from `table.unserialize`.
- `UNKNOWN`: final runtime offensive-security adapter shape; explicitly deferred until the static registry/report contract is merged.

# Validation plan

- `python -m unittest discover -s tests/security -p 'test_*.py'`
- `python -m py_compile tools/security/security_validation.py tests/security/test_security_validation.py`
- `python tools/security/security_validation.py validate`
- `python tools/security/security_validation.py run-all --authorized-repository blakinio/canary`
- workflow YAML/required-check observation on the live PR
- exact changed-file and diff review before readiness

## Context checkpoint

### Current state

- Draft PR #433 targets `blakinio/canary:main` from `blakinio/canary:feat/security-validation-foundation`.
- Current implementation head before this checkpoint commit: `89fbf6c8097fefcad14a5dca5b195aa4672bbb14`.
- Foundation scope is complete except shared catalogue/changelog finalization and final-head merge-gate validation.
- No runtime packets, fuzzing, database mutation, MyAAC probing, client attack driver or external target is included in this PR.

### Proven evidence

- `AGENTS.md`, `REPOSITORY_MAP.md`, `CONTEXT_ROUTING.md`, `BUILD_TEST_MATRIX.md`, matching `MODULE_CATALOG.md` entries and `E2E_AUTOMATION_PROGRAM.md` were read.
- No open security-platform PR was found before task creation.
- Open PRs #432 and #426 were checked for path overlap; only the two shared agent indexes overlap #426.
- Local scratch validation passed: Python bytecode compilation, 11 focused unit tests, registry validation and both seeded scenarios.
- GitHub `Security Validation` run `29523380220` passed on `89fbf6c8097fefcad14a5dca5b195aa4672bbb14`.
- GitHub main `CI` run `29523381029` passed on the same head.
- Agent Task Ownership run `29523380316` failed only because this task used `# Context checkpoint` instead of the required `## Context checkpoint`; artifact `CHANGED_TASK_VALIDATION.txt` proved the exact error. This commit corrects the heading and binds `related_pr` to `433`.

### Blockers

- Shared `MODULE_CATALOG.md` and `CHANGELOG.md` still require narrow current-main-preserving edits.
- Final exact-head validation has not yet run.

### Next action

Update the two shared indexes from current main without overwriting PR #426 work, re-check ownership/CI, then apply the `ci:final-gate` label before the final checkpoint commit and perform no post-green commit.
