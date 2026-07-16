---
task_id: CAN-20260716-security-runtime-adapter
program_id: CAN-PROGRAM-SECURITY-VALIDATION
coordination_id: OTS-SEC-002
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/security-runtime-adapter
base_branch: main
created: 2026-07-16T21:05:00+02:00
updated: 2026-07-16T22:25:00+02:00
last_verified_commit: "a9edc1f81f22298dabd0aaa43932b8daf004c4b1"
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
- [ ] Update module catalogue and changelog narrowly.
- [ ] Review the exact diff and pass current-head plus exact-final-head required CI before squash merge.

# Evidence and constraints

- `PROVEN`: OTS-SEC-001 merged as PR #433 at `6503f5312dbf13d0fddcc1da98a10343ed30525c`.
- `PROVEN`: the accepted security-platform ADR requires code-owned runtime adapters and forbids a second security-specific full-stack launcher.
- `PROVEN`: Universal E2E owns disposable MariaDB/Canary/OTClient lifecycle, evidence and cleanup.
- `PROVEN`: `.github/workflows/universal-agent-e2e.yml` delegates physical execution to `tools/e2e/run_physical_e2e.sh` and scenario resolution to `tools/e2e/run_agent_e2e.py`.
- `PROVEN`: lifecycle PR #437 merged as `819efef130c0f498ba958956ec9964f7c79fa144`; SEC-002 no longer overlaps an open SEC-001 lifecycle task.
- `PROVEN`: Security Validation run `29531473776` and normal CI run `29531474508` passed on `a9edc1f81f22298dabd0aaa43932b8daf004c4b1`.
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
updated_at: 2026-07-16T22:25:00+02:00
head: a9edc1f81f22298dabd0aaa43932b8daf004c4b1
branch: feat/security-runtime-adapter
pr: 440
status: implementing
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
  - runtime adapter imports the existing E2E scenario resolver and keeps tools/e2e plus the Universal Agent E2E workflow read-only
  - canary-universal-e2e resolves login/relog through a strict repository-authorized literal-loopback-only contract
  - provider workflow resolver runner and selected scenario are represented by deterministic SHA-256 evidence
  - Security Validation run 29531473776 passed on a9edc1f81f22298dabd0aaa43932b8daf004c4b1
  - CI run 29531474508 passed on a9edc1f81f22298dabd0aaa43932b8daf004c4b1
derived:
  - SEC-002 establishes the safe delegation boundary required before adding security-specific runtime attack drivers
unknown:
  - generic attack-driver execution hook for OTS-SEC-003
conflicts: []
first_failure:
  marker: active-task-checkpoint-first-failure-type
  evidence: Agent Task Ownership run 29531473822 rejected first_failure null because the checkpoint contract requires a YAML mapping; this commit supplies the mapping
rejected_hypotheses:
  - security adapter implementation failure: rejected because Security Validation and normal CI both passed on the same head
  - build a second security E2E launcher: rejected by the accepted platform ADR and existing Universal E2E ownership
  - allow adapter manifests to provide runner commands or arbitrary hosts: rejected because it would reopen an unbounded execution and target boundary
changed_paths:
  - .github/workflows/security-validation.yml
  - docs/agents/programs/SECURITY_VALIDATION_PROGRAM.md
  - docs/agents/tasks/active/CAN-20260716-security-runtime-adapter.md
  - docs/security/SECURITY_VALIDATION_PLATFORM.md
  - tests/security/runtime_adapters/.gitkeep
  - tests/security/runtime_adapters/canary-universal-e2e.json
  - tests/security/test_runtime_adapter.py
  - tools/security/runtime_adapter.py
validation:
  - command: Security Validation run 29531473776
    result: PASS
    evidence: runtime adapter compile focused unit discovery registry validation authorized delegation resolution and source-regression execution passed
  - command: CI run 29531474508
    result: PASS
    evidence: repository CI passed on a9edc1f81f22298dabd0aaa43932b8daf004c4b1
  - command: Agent Task Ownership run 29531473822
    result: FAIL
    evidence: governance-only checkpoint schema error first_failure must be a YAML mapping; corrected by this commit
blockers: []
next_action: Remove the unnecessary runtime-adapter .gitkeep, update MODULE_CATALOG and CHANGELOG from current main, then revalidate ownership and CI before final-head gate.
```
