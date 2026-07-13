---
task_id: CAN-20260713-agent-program-ownership
program_id: CAN-PROGRAM-COORDINATION
status: ready
agent: chatgpt-coordination
branch: feat/agent-program-ownership-coordination
base_branch: main
created: 2026-07-13T00:00:00+02:00
updated: 2026-07-13T00:40:00+02:00
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
- [x] Focused tests and ownership validation passed on implementation head `ebfb1e3645c24e3b1d11a82ec7ca6257372ecb8d`.
- [x] CI / Required passed on implementation head `ebfb1e3645c24e3b1d11a82ec7ca6257372ecb8d`.
- [x] Full changed-file list and diff scope reviewed.
- [ ] Autonomous merge gate satisfied on the final metadata head.

# Confirmed context

- Current task files and live PR state are authoritative.
- `ACTIVE_WORK.md` is a coordination snapshot and must not be used as a shared writable lock.
- Canary already has Docker quickstart lifecycle, deterministic test fixtures, build artifacts, and global smoke tests.
- PR #224 is the first real MySQL + Canary + OTClient/Xvfb experiment but currently duplicates orchestration inside a Cyclopedia-specific workflow.

# Ownership and overlap check

- Open PRs inspected: current coordination PRs, PR #224, and active autonomous-program PRs.
- Active tasks inspected: legacy records remain read-only migration inputs.
- Ownership checker: passed on implementation head; legacy overlaps are warnings, structured exclusive overlaps are errors.
- Overlaps: shared task template and repository-wide coordination README.
- Resolution: narrow edits on a dedicated coordination branch; no modification of PR #224 files.

# Current state

Implementation is complete. The final task-record metadata commit requires the normal current-head checks before PR readiness and merge.

# Delivered

1. Persistent autonomous-program records and template.
2. Structured `exclusive`, `shared`, and `read_only` task ownership.
3. Migration-safe handling and optional strict audit of legacy flat claims.
4. Deterministic conflict validation and generated ownership-index artifact.
5. Repository-wide startup and lifecycle documentation.
6. Universal E2E platform program with explicit reuse of existing Canary infrastructure.
7. Reusable physical-client scenario template.
8. Ordered extraction path from Cyclopedia prototype PR #224 to a shared platform.

# Work log

## 2026-07-13T00:00:00+02:00

- Changed: claimed coordination paths and branch.
- Learned: existing rules already required task records and advisory ownership but lacked deterministic validation.
- Result: implementation started.

## 2026-07-13T00:35:00+02:00

- Changed: rebuilt the checker to enforce new structured claims while preserving legacy records as warnings; expanded tests from five to ten cases; made startup rules repository-wide; converted E2E design into an active program record.
- Failed/blocked: first ownership workflow rejected legacy active records and then parsed the active-directory README as a task.
- Result: both root causes fixed.

## 2026-07-13T00:40:00+02:00

- Changed: excluded task-directory README files, reran current implementation validation, reviewed all eleven changed paths and the base/head comparison.
- Result: Agent Task Ownership and CI completed successfully on `ebfb1e3645c24e3b1d11a82ec7ca6257372ecb8d`; task marked ready for final-head gate.

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| local reconstructed tool | `python -m unittest -v test_task_ownership.py` | passed | 10 focused cases. |
| f4a3ad9bcc017339636a5a3d5a77653cd120c6d8 | Agent Task Ownership | failed | new identity requirements were applied to legacy records; repaired. |
| 52d52a891e3a64c1d1371d1dd55a6e834b66c4bd | Agent Task Ownership | failed | `tasks/active/README.md` was parsed as a task; repaired. |
| ebfb1e3645c24e3b1d11a82ec7ca6257372ecb8d | Agent Task Ownership | passed | run 16. |
| ebfb1e3645c24e3b1d11a82ec7ca6257372ecb8d | CI | passed | run 1011. |
| final metadata head | Agent Task Ownership and CI | pending | verify immediately before readiness and merge. |

# Remaining work

1. Verify final-head checks.
2. Mark PR #222 ready and merge when every gate passes.
3. Archive this task in a post-merge coordination cleanup.
4. Continue universal E2E implementation through a separate bounded platform task.

# Handoff

## Start here

Read this task, `AGENTS.md`, `docs/agents/README.md`, `docs/agents/programs/E2E_AUTOMATION_PROGRAM.md`, PR #222, and prototype PR #224.

## Do not repeat

- Do not create another manually maintained ownership index.
- Do not enforce new structured fields retroactively on all legacy records in default CI.
- Do not parse directory README files as task records.
- Do not create one full Canary/OTClient workflow per feature.
- Do not commit client assets, map binaries, database dumps, or credentials.

## Required reads

- `AGENTS.md`
- `docs/agents/README.md`
- `docs/agents/templates/TASK.md`
- `docs/agents/templates/PROGRAM.md`
- `docs/agents/templates/E2E_SCENARIO.md`
- `docs/agents/programs/E2E_AUTOMATION_PROGRAM.md`
- PR #224 and its current workflow evidence

## Open questions

- The canonical E2E implementation task must decide the first supported database target and stable OTClient artifact contract from real evidence.
