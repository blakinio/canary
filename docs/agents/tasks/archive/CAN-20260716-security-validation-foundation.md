---
task_id: CAN-20260716-security-validation-foundation
program_id: CAN-PROGRAM-SECURITY-VALIDATION
coordination_id: OTS-SEC-001
status: completed
agent: "GPT-5.5 Thinking"
branch: feat/security-validation-foundation
base_branch: main
created: 2026-07-16T20:10:00+02:00
updated: 2026-07-16T18:51:22Z
last_verified_commit: "6503f5312dbf13d0fddcc1da98a10343ed30525c"
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
completed: 2026-07-16T18:51:22Z
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
- [x] Update module catalogue and changelog narrowly.
- [ ] Review exact changed-file scope and pass required exact-head CI before merge.

# Evidence and constraints

- `PROVEN`: task-start `main` was `0f25e7fd4d41e90f17fc95d13dba84b7e81d1681`; current `main` advanced through `6374230a40b70d3e0cffe8d93a3171393ece7cd7` without changing this task's intended diff.
- `PROVEN`: Universal E2E already owns disposable MariaDB, Canary, controlled OTClient, evidence and cleanup lifecycle; this task does not create a second runtime orchestrator.
- `PROVEN`: Universal Agent Load already enforces literal-loopback-only targets for its status-protocol load runner; this task does not duplicate that runner.
- `PROVEN`: PR #326 removed shell execution from `FS.mkdir`/`FS.mkdir_p`; PR #328 removed `loadstring` evaluation from `table.unserialize`.
- `PROVEN`: compared with current `main@6374230a40b70d3e0cffe8d93a3171393ece7cd7`, the PR contains exactly 11 intended paths; `MODULE_CATALOG.md` and `CHANGELOG.md` each contain exactly one additive line.
- `PROVEN`: PR #433 has no review submissions, inline review threads or comments at readiness checkpoint time.
- `UNKNOWN`: final exact-head gate result for the readiness commit created from this checkpoint.
- `UNKNOWN`: final runtime offensive-security adapter shape; explicitly deferred until the static registry/report contract is merged.

# Validation plan

- `python -m unittest discover -s tests/security -p 'test_*.py'`
- `python -m py_compile tools/security/security_validation.py tests/security/test_security_validation.py`
- `python tools/security/security_validation.py validate`
- `python tools/security/security_validation.py run-all --authorized-repository blakinio/canary`
- workflow YAML/required-check observation on the live PR
- exact changed-file and diff review before readiness

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T20:45:00+02:00
head: 68ffab1e1b279d9af29e54f2406c7c932de2c722
branch: feat/security-validation-foundation
pr: 433
status: ready
context_routes:
  - agent-governance
owned_paths:
  - tools/security/**
  - tests/security/**
  - docs/security/**
  - docs/agents/programs/SECURITY_VALIDATION_PROGRAM.md
  - docs/agents/decisions/ADR-20260716-security-validation-platform-boundary.md
  - docs/agents/tasks/active/CAN-20260716-security-validation-foundation.md
  - .github/workflows/security-validation.yml
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - draft PR 433 targets blakinio/canary main from feat/security-validation-foundation
  - Universal OTS E2E remains the owned disposable runtime lifecycle and this PR introduces no competing runtime orchestrator
  - the foundation implements strict source-regex manifests with explicit repository authorization and deterministic SHA-256 reports
  - two critical source regressions cover the merged PR 326 shell-execution boundary and PR 328 arbitrary-evaluation boundary
  - local scratch bytecode compilation 11 focused unit tests registry validation and both seeded scenarios passed
  - Security Validation run 29524313456 passed on 68ffab1e1b279d9af29e54f2406c7c932de2c722
  - CI run 29524313866 passed on 68ffab1e1b279d9af29e54f2406c7c932de2c722
  - Agent Task Ownership run 29524313508 passed on 68ffab1e1b279d9af29e54f2406c7c932de2c722
  - current-main comparison shows exactly 11 intended paths with one additive MODULE_CATALOG line and one additive CHANGELOG line
  - PR 433 has no reviews comments or unresolved review threads
  - ci:final-gate label was applied before this final readiness checkpoint commit
derived:
  - implementation and governance validation are ready for the exact-final-head full gate
unknown:
  - exact-final-head CI and required workflow result for the readiness commit
conflicts: []
first_failure:
  marker: active-task-checkpoint-format-and-lifecycle-status
  evidence: early Agent Task Ownership runs exposed heading fenced-YAML and frontmatter lifecycle-state contract defects; run 29524313508 proves the corrected record passes
rejected_hypotheses:
  - security runner failure: dedicated Security Validation runs passed while early ownership failures were isolated to changed-task governance validation
  - main CI implementation failure: repository CI passed on the validated implementation head
  - shared-index overwrite: current-main comparison shows only one additive line in each shared index
changed_paths:
  - .github/workflows/security-validation.yml
  - docs/agents/CHANGELOG.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/decisions/ADR-20260716-security-validation-platform-boundary.md
  - docs/agents/programs/SECURITY_VALIDATION_PROGRAM.md
  - docs/agents/tasks/active/CAN-20260716-security-validation-foundation.md
  - docs/security/SECURITY_VALIDATION_PLATFORM.md
  - tests/security/scenarios/server/lua-fs-shell-execution.json
  - tests/security/scenarios/server/lua-table-unserialize-arbitrary-eval.json
  - tests/security/test_security_validation.py
  - tools/security/security_validation.py
validation:
  - command: local Python security foundation validation
    result: PASS
    evidence: py_compile 11 focused unittests registry validation and two seeded source scenarios passed in scratch reconstruction
  - command: Security Validation run 29524313456
    result: PASS
    evidence: dedicated security workflow passed on 68ffab1e1b279d9af29e54f2406c7c932de2c722
  - command: CI run 29524313866
    result: PASS
    evidence: repository CI passed on 68ffab1e1b279d9af29e54f2406c7c932de2c722
  - command: Agent Task Ownership run 29524313508
    result: PASS
    evidence: changed-task checkpoint validation and ownership index both passed on 68ffab1e1b279d9af29e54f2406c7c932de2c722
blockers: []
next_action: Let the ci:final-gate workflows run on this readiness commit; if every required current-head check passes and PR 433 remains mergeable with the same intended diff and no review blockers, mark it ready and squash-merge without any further commit.
```

## Automated lifecycle completion

- Feature PR: #433.
- Feature head: `b2ceed93b4b9d4cd64d2a59757f583cf25648845`.
- Merge commit: `6503f5312dbf13d0fddcc1da98a10343ed30525c`.
- Merged at: `2026-07-16T18:51:22Z`.
- This record was moved from `tasks/active` by the post-merge lifecycle automation.
