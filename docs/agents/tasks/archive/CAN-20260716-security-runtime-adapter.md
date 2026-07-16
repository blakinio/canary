---
task_id: CAN-20260716-security-runtime-adapter
program_id: CAN-PROGRAM-SECURITY-VALIDATION
coordination_id: OTS-SEC-002
status: completed
agent: "GPT-5.5 Thinking"
branch: feat/security-runtime-adapter
base_branch: main
created: 2026-07-16T21:05:00+02:00
updated: 2026-07-16T20:55:27Z
last_verified_commit: "597011f0ea0673c005a5a513806df9f65a3d28e6"
risk: medium
related_issue: ""
related_pr: "440"
depends_on:
  - "OTS-SEC-001 / PR #433"
  - "Universal OTS E2E automation / CAN-PROGRAM-E2E-PLATFORM"
blocks:
  - "OTS-SEC-003 malformed packet and parser security scenarios"
owned_paths:
  exclusive:
    - tools/security/runtime_adapter.py
    - tests/security/test_runtime_adapter.py
    - tests/security/runtime_adapters/**
    - docs/agents/tasks/active/CAN-20260716-security-runtime-adapter.md
  shared:
    - .github/workflows/security-validation.yml
    - docs/security/SECURITY_VALIDATION_PLATFORM.md
    - docs/agents/programs/SECURITY_VALIDATION_PROGRAM.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/e2e/**
    - tests/e2e/**
    - .github/workflows/universal-agent-e2e.yml
    - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
    - docs/agents/decisions/ADR-20260716-security-validation-platform-boundary.md
modules_touched:
  - OTS Security Validation Platform runtime adapter
reuses:
  - tools/e2e/run_agent_e2e.py scenario discovery and validation
  - tools/e2e/run_physical_e2e.sh lifecycle entrypoint identity
  - .github/workflows/universal-agent-e2e.yml disposable runtime ownership
public_interfaces:
  - ots-security-runtime-adapter-v1
  - ots-security-runtime-delegation-v1
  - tools/security/runtime_adapter.py CLI
cross_repo_tasks: []
completed: 2026-07-16T20:55:27Z
---

# Goal

Add the first code-owned runtime security adapter for Canary without creating a second runtime orchestrator. The adapter must resolve and prove an authorized, confined delegation into the existing Universal OTS E2E platform so later offensive scenarios can execute through an already-owned disposable lifecycle.

# Acceptance criteria

- [x] Add a strict versioned `ots-security-runtime-adapter-v1` manifest contract with no arbitrary command, executable, credential or free-form network-target fields.
- [x] Add a Python 3.12 standard-library runtime-adapter CLI with `list`, `validate` and deterministic `resolve` operations.
- [x] Reuse `tools/e2e/run_agent_e2e.py` to resolve the delegated E2E scenario instead of duplicating E2E scenario parsing.
- [x] Fail closed unless the caller-provided repository exactly matches adapter authorization.
- [x] Fail closed unless the resolved E2E fixture host is a literal loopback IP address.
- [x] Pin the canonical Universal E2E workflow, resolver and physical runner as code-owned provider paths and include their SHA-256 evidence in the delegation report.
- [x] Emit deterministic `ots-security-runtime-delegation-v1` evidence identifying the adapter, repository authorization, selected E2E scenario, confined host/port and provider file hashes.
- [x] Seed `canary-universal-e2e` as the first adapter delegating to the existing `login/relog` E2E baseline.
- [x] Add focused tests covering exact-field rejection, unsupported provider, repository mismatch, non-literal/non-loopback host rejection, missing scenario, deterministic evidence and provider hashing.
- [x] Extend Security Validation CI to compile/test/validate/resolve the runtime adapter and upload its report.
- [x] Update module catalogue and changelog narrowly.
- [ ] Review the exact diff and pass current-head plus exact-final-head required CI before squash merge.

# Evidence and constraints

- `PROVEN`: OTS-SEC-001 merged as PR #433 at `6503f5312dbf13d0fddcc1da98a10343ed30525c`.
- `PROVEN`: the accepted security-platform ADR requires code-owned runtime adapters and forbids a second security-specific full-stack launcher.
- `PROVEN`: Universal E2E owns disposable MariaDB/Canary/OTClient lifecycle, evidence and cleanup.
- `PROVEN`: `.github/workflows/universal-agent-e2e.yml` delegates physical execution to `tools/e2e/run_physical_e2e.sh` and scenario resolution to `tools/e2e/run_agent_e2e.py`.
- `PROVEN`: lifecycle PR #437 merged as `819efef130c0f498ba958956ec9964f7c79fa144`; SEC-002 no longer overlaps an open SEC-001 lifecycle task.
- `PROVEN`: branch was synchronized with `main@819efef130c0f498ba958956ec9964f7c79fa144` before shared-index finalization and is zero commits behind that base.
- `PROVEN`: exact PR diff review found nine intended paths and no `tools/e2e/**`, `tests/e2e/**` or Universal E2E workflow modification.
- `PROVEN`: shared-index patch review shows exactly one added CHANGELOG entry and one replaced Security Platform catalogue row.
- `PROVEN`: Security Validation run `29532801331`, Agent Task Ownership run `29532801314` and CI run `29532801559` passed on `6faa23141a833e4a7f94c82065245bb343711126`.
- `PROVEN`: PR #440 had no review submissions, comments or unresolved review threads before readiness.
- `PROVEN`: `ci:final-gate` was applied before this final readiness checkpoint commit.
- `UNKNOWN`: exact-final-head gate result for the readiness commit created from this checkpoint.
- `UNKNOWN`: the generic E2E interface required for malformed-packet execution; deliberately deferred to OTS-SEC-003 rather than changing E2E platform ownership in this task.

# Validation plan

- `python -m py_compile tools/security/runtime_adapter.py tests/security/test_runtime_adapter.py`
- `python -m unittest discover -v -s tests/security -p 'test_*.py'`
- `python tools/security/runtime_adapter.py validate`
- `python tools/security/runtime_adapter.py resolve --adapter canary-universal-e2e --authorized-repository blakinio/canary`
- dedicated Security Validation workflow evidence
- exact changed-file and full diff review before readiness

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T22:45:00+02:00
head: 6faa23141a833e4a7f94c82065245bb343711126
branch: feat/security-runtime-adapter
pr: 440
status: ready
context_routes:
  - agent-governance
  - universal-e2e
owned_paths:
  - tools/security/runtime_adapter.py
  - tests/security/test_runtime_adapter.py
  - tests/security/runtime_adapters/**
  - docs/agents/tasks/active/CAN-20260716-security-runtime-adapter.md
  - .github/workflows/security-validation.yml
  - docs/security/SECURITY_VALIDATION_PLATFORM.md
  - docs/agents/programs/SECURITY_VALIDATION_PROGRAM.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - OTS-SEC-001 merged through PR 433 at 6503f5312dbf13d0fddcc1da98a10343ed30525c
  - SEC-001 lifecycle PR 437 merged at 819efef130c0f498ba958956ec9964f7c79fa144
  - accepted ADR requires explicit code-owned adapters and reuse of Universal OTS E2E
  - runtime adapter imports the existing E2E scenario resolver and keeps tools/e2e tests/e2e plus the Universal Agent E2E workflow read-only
  - canary-universal-e2e resolves login/relog through a strict repository-authorized literal-loopback-only contract
  - provider workflow resolver runner and selected scenario are represented by deterministic SHA-256 evidence
  - exact diff contains nine intended paths and no Universal E2E lifecycle code changes
  - CHANGELOG diff is exactly one new SEC-002 entry
  - MODULE_CATALOG diff is exactly one Security Platform row replacement
  - Security Validation run 29532801331 passed on 6faa23141a833e4a7f94c82065245bb343711126
  - Agent Task Ownership run 29532801314 passed on 6faa23141a833e4a7f94c82065245bb343711126
  - CI run 29532801559 passed on 6faa23141a833e4a7f94c82065245bb343711126
  - PR 440 had no reviews comments or unresolved review threads before readiness
  - ci:final-gate label was applied before this final readiness checkpoint commit
derived:
  - SEC-002 establishes the safe delegation boundary required before adding security-specific runtime attack drivers
unknown:
  - exact-final-head gate result for the readiness commit
  - generic attack-driver execution hook for OTS-SEC-003
conflicts: []
first_failure:
  marker: active-task-checkpoint-status-enum
  evidence: early Agent Task Ownership runs exposed checkpoint contract mismatches; run 29532801314 proves the corrected validating checkpoint passes
rejected_hypotheses:
  - security adapter implementation failure: rejected because Security Validation and normal CI pass on the validated reviewed head
  - build a second security E2E launcher: rejected by the accepted platform ADR and existing Universal E2E ownership
  - allow adapter manifests to provide runner commands or arbitrary hosts: rejected because it would reopen an unbounded execution and target boundary
  - shared-index overwrite: rejected by exact per-file patch review against current main
changed_paths:
  - .github/workflows/security-validation.yml
  - docs/agents/CHANGELOG.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/programs/SECURITY_VALIDATION_PROGRAM.md
  - docs/agents/tasks/active/CAN-20260716-security-runtime-adapter.md
  - docs/security/SECURITY_VALIDATION_PLATFORM.md
  - tests/security/runtime_adapters/canary-universal-e2e.json
  - tests/security/test_runtime_adapter.py
  - tools/security/runtime_adapter.py
validation:
  - command: Security Validation run 29532801331
    result: PASS
    evidence: runtime adapter compile focused unit discovery registry validation authorized delegation resolution and source-regression execution passed
  - command: Agent Task Ownership run 29532801314
    result: PASS
    evidence: changed-task checkpoint validation and ownership index passed
  - command: CI run 29532801559
    result: PASS
    evidence: repository CI passed on the validated reviewed head
blockers: []
next_action: Let the ci:final-gate workflows run on this readiness commit; if every required current-head check passes and PR 440 remains mergeable with the same intended diff and no review blockers, mark it ready and squash-merge without any further commit.
```

## Automated lifecycle completion

- Feature PR: #440.
- Feature head: `e7c5562d0d63b813cc4b5951c628465ca800c595`.
- Merge commit: `597011f0ea0673c005a5a513806df9f65a3d28e6`.
- Merged at: `2026-07-16T20:55:27Z`.
- This record was moved from `tasks/active` by the post-merge lifecycle automation.
