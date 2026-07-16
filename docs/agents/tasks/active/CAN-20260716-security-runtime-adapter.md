---
task_id: CAN-20260716-security-runtime-adapter
program_id: CAN-PROGRAM-SECURITY-VALIDATION
coordination_id: OTS-SEC-002
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/security-runtime-adapter
base_branch: main
created: 2026-07-16T21:05:00+02:00
updated: 2026-07-16T21:05:00+02:00
last_verified_commit: "6503f5312dbf13d0fddcc1da98a10343ed30525c"
risk: medium
related_issue: ""
related_pr: ""
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

- [ ] Add a strict versioned `ots-security-runtime-adapter-v1` manifest contract with no arbitrary command, executable, credential or free-form network-target fields.
- [ ] Add a Python 3.12 standard-library runtime-adapter CLI with `list`, `validate` and deterministic `resolve` operations.
- [ ] Reuse `tools/e2e/run_agent_e2e.py` to resolve the delegated E2E scenario instead of duplicating E2E scenario parsing.
- [ ] Fail closed unless the caller-provided repository exactly matches adapter authorization.
- [ ] Fail closed unless the resolved E2E fixture host is a literal loopback IP address.
- [ ] Pin the canonical Universal E2E workflow, resolver and physical runner as code-owned provider paths and include their SHA-256 evidence in the delegation report.
- [ ] Emit deterministic `ots-security-runtime-delegation-v1` evidence identifying the adapter, repository authorization, selected E2E scenario, confined host/port and provider file hashes.
- [ ] Seed `canary-universal-e2e` as the first adapter delegating to the existing `login/relog` E2E baseline.
- [ ] Add focused tests covering exact-field rejection, unsupported provider, repository mismatch, non-literal/non-loopback host rejection, missing scenario, deterministic evidence and provider hashing.
- [ ] Extend Security Validation CI to compile/test/validate/resolve the runtime adapter and upload its report.
- [ ] Update security docs, program queue, module catalogue and changelog narrowly.
- [ ] Review the exact diff and pass current-head plus exact-final-head required CI before squash merge.

# Evidence and constraints

- `PROVEN`: OTS-SEC-001 merged as PR #433 at `6503f5312dbf13d0fddcc1da98a10343ed30525c`.
- `PROVEN`: the accepted security-platform ADR requires code-owned runtime adapters and forbids a second security-specific full-stack launcher.
- `PROVEN`: Universal E2E owns disposable MariaDB/Canary/OTClient lifecycle, evidence and cleanup.
- `PROVEN`: `.github/workflows/universal-agent-e2e.yml` delegates physical execution to `tools/e2e/run_physical_e2e.sh` and scenario resolution to `tools/e2e/run_agent_e2e.py`.
- `PROVEN`: open lifecycle PR #437 changes only the archived SEC-001 task record and does not overlap SEC-002 owned implementation paths.
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
updated_at: 2026-07-16T21:05:00+02:00
head: 6503f5312dbf13d0fddcc1da98a10343ed30525c
branch: feat/security-runtime-adapter
pr: null
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
  - accepted ADR requires explicit code-owned adapters and reuse of Universal OTS E2E
  - Universal Agent E2E owns scenario resolution disposable MariaDB exact-head Canary controlled OTClient physical execution evidence and cleanup
  - open lifecycle PR 437 changes only the archived SEC-001 task record
  - no open runtime-security adapter PR was found before task creation
derived:
  - SEC-002 can remain read-only over tools/e2e and still provide a safe delegation boundary by importing the existing scenario resolver and pinning canonical provider paths
unknown:
  - generic attack-driver execution hook for OTS-SEC-003
conflicts: []
first_failure: null
rejected_hypotheses:
  - build a second security E2E launcher: rejected by the accepted platform ADR and existing Universal E2E ownership
  - allow adapter manifests to provide runner commands or arbitrary hosts: rejected because it would reopen an unbounded execution/target boundary
changed_paths:
  - docs/agents/tasks/active/CAN-20260716-security-runtime-adapter.md
validation: []
blockers: []
next_action: Open the draft PR, then implement the strict adapter resolver and focused tests without modifying Universal E2E lifecycle code.
```
