---
task_id: CAN-20260713-agent-program-ownership
program_id: CAN-PROGRAM-COORDINATION
status: implementing
agent: chatgpt-coordination
branch: feat/agent-program-ownership-coordination
base_branch: main
created: 2026-07-13T00:00:00+02:00
updated: 2026-07-13T00:35:00+02:00
last_verified_commit: 97639776bb37c4f9aa1fa301cf43e7693a03a735
risk: low
related_issue: ""
related_pr: "222"
depends_on: []
blocks:
  - canonical universal E2E platform extraction from prototype PR 224
owned_paths:
  exclusive:
    - tools/agents/task_ownership.py
    - tools/agents/test_task_ownership.py
    - .github/workflows/agent-task-ownership.yml
    - docs/agents/AGENTS.md
    - docs/agents/programs/README.md
    - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
    - docs/agents/templates/PROGRAM.md
    - docs/agents/templates/E2E_SCENARIO.md
  shared:
    - docs/agents/README.md
    - docs/agents/templates/TASK.md
  read_only:
    - AGENTS.md
    - docs/agents/tasks/active/**
    - .github/workflows/cyclopedia-live-e2e.yml
    - tools/e2e/cyclopedia_otclient_e2e.lua
modules_touched:
  - agent coordination
  - universal E2E ownership contract
reuses:
  - docs/agents/tasks/active task records
  - live pull requests as coordination source of truth
  - Docker quickstart lifecycle and fixtures
  - draft live E2E prototype PR 224
public_interfaces:
  - task front matter ownership schema
  - autonomous program record contract
  - feature-suite versus E2E-platform ownership boundary
cross_repo_tasks:
  - OTS-E2E-CANARY-OTCLIENT
---

# Goal

Add program-level autonomous-agent coordination, deterministic task-path ownership validation, and a durable ownership contract for one universal Canary/OTClient E2E platform without changing runtime, gameplay, map, asset, protocol, schema, database, or deployment behavior.

# Acceptance criteria

- [x] Autonomous programs have a canonical persistent record template.
- [x] Task ownership distinguishes exclusive, shared, and read-only paths.
- [x] A standard-library checker detects conflicting structured exclusive claims.
- [x] Existing flat `owned_paths` records remain readable and migration-safe.
- [x] A generated ownership index exposes task, program, agent, branch, schema, and source record.
- [x] Repository-wide startup documentation requires program and ownership inspection.
- [x] One universal E2E platform is defined for all feature agents.
- [x] PR #224 is classified as a prototype to extract, not permanent Cyclopedia-owned infrastructure.
- [ ] Current-head focused tests and ownership workflow pass.
- [ ] Full diff and changed-file list are reviewed.
- [ ] Autonomous merge gate satisfied.

# Confirmed context

- Current task files and live PR state are authoritative.
- `ACTIVE_WORK.md` is a coordination snapshot and must not be used as a shared writable lock.
- Canary already has Docker quickstart lifecycle, deterministic test fixtures, build artifacts, and global smoke tests.
- PR #224 is the first real MySQL + Canary + OTClient/Xvfb experiment but currently duplicates orchestration inside a Cyclopedia-specific workflow.

# Ownership and overlap check

- Open PRs inspected: current coordination PRs, PR #224, and active autonomous-program PRs.
- Active tasks inspected: legacy records remain read-only migration inputs.
- Overlaps: shared task template and repository-wide coordination README.
- Resolution: narrow edits on a dedicated coordination branch; no modification of PR #224 files.

# Current state

The PR has been rebuilt around two deliverables: migration-safe path ownership and the universal E2E program contract. CI repair is in progress after the first checker version rejected legacy active records too aggressively.

# Plan

1. Make structured claims enforceable without breaking legacy task records.
2. Publish the ownership index as a CI artifact.
3. Make program rules visible through the repository-wide required README.
4. Record the universal E2E platform, scenario contract, existing reusable foundations, and PR #224 migration path.
5. Run CI, inspect the full diff, mark ready, and merge when the gate is satisfied.

# Work log

## 2026-07-13T00:00:00+02:00

- Changed: claimed coordination paths and branch.
- Learned: existing rules already require task records and advisory ownership but lacked deterministic validation.
- Result: implementation started.

## 2026-07-13T00:35:00+02:00

- Changed: rebuilt the checker to enforce new structured claims while preserving legacy records as warnings; expanded tests from five to ten cases; made startup rules repository-wide through `docs/agents/README.md`; converted the E2E design into an active program record.
- Learned: PR #224 provides useful physical-client evidence but common orchestration must be extracted before it becomes the pattern for other modules.
- Failed/blocked: first Agent Task Ownership workflow failed because legacy active records were required to contain new identity fields.
- Result: root cause fixed; new CI run pending.

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| local design revision | `python -m unittest -v test_task_ownership.py` | passed | 10 focused tests in the reconstructed tool environment. |
| f4a3ad9bcc017339636a5a3d5a77653cd120c6d8 | Agent Task Ownership | failed | legacy active records were treated as if already migrated; fixed in subsequent commits. |
| current head | Agent Task Ownership | pending | must pass before readiness. |
| current head | CI / Required | pending | must pass before readiness. |

# Remaining work

1. Add the reusable E2E scenario template.
2. Verify current-head CI and inspect logs.
3. Review every changed file and update the PR body with exact validation.
4. Mark ready and merge only when all gates pass.

# Handoff

## Start here

Read this task, `AGENTS.md`, `docs/agents/README.md`, `docs/agents/programs/E2E_AUTOMATION_PROGRAM.md`, PR #222, and prototype PR #224.

## Do not repeat

- Do not create another manually maintained ownership index.
- Do not enforce new structured fields retroactively on all legacy task records in default CI.
- Do not create one full Canary/OTClient workflow per feature.
- Do not commit client assets, map binaries, database dumps, or credentials.

## Required reads

- `AGENTS.md`
- `docs/agents/README.md`
- `docs/agents/templates/TASK.md`
- `docs/agents/templates/PROGRAM.md`
- `docs/agents/programs/E2E_AUTOMATION_PROGRAM.md`
- PR #224 and its current workflow evidence

## Open questions

- The canonical E2E implementation task must decide the first supported database target and stable OTClient artifact contract from real evidence.
