---
task_id: CAN-20260713-agent-program-ownership
program_id: CAN-PROGRAM-COORDINATION
status: implementing
agent: chatgpt-coordination
branch: feat/agent-program-ownership-coordination
base_branch: main
created: 2026-07-13T00:00:00+02:00
updated: 2026-07-13T00:00:00+02:00
last_verified_commit: main
risk: low
related_issue: ""
related_pr: ""
depends_on: []
blocks: []
owned_paths:
  exclusive:
    - tools/agents/task_ownership.py
    - tools/agents/test_task_ownership.py
    - .github/workflows/agent-task-ownership.yml
    - docs/agents/programs/README.md
    - docs/agents/templates/PROGRAM.md
  shared:
    - AGENTS.md
    - docs/agents/README.md
    - docs/agents/templates/TASK.md
  read_only:
    - docs/agents/tasks/active/**
modules_touched:
  - agent coordination
reuses:
  - docs/agents/tasks/active task records
  - live pull requests as coordination source of truth
public_interfaces:
  - task front matter ownership schema
cross_repo_tasks: []
---

# Goal

Add program-level autonomous-agent coordination and deterministic task-path ownership validation without changing runtime, gameplay, map, asset, protocol, or deployment behavior.

# Acceptance criteria

- [ ] Autonomous programs have a canonical persistent record template.
- [ ] Task ownership distinguishes exclusive, shared, and read-only paths.
- [ ] A standard-library checker detects conflicting exclusive claims.
- [ ] CI runs the checker and its focused tests.
- [ ] Existing flat `owned_paths` task records remain compatible during migration.
- [ ] Agent startup instructions require program and ownership inspection.
- [ ] Autonomous merge gate satisfied.

# Confirmed context

Current task files and live PR state are authoritative. `ACTIVE_WORK.md` is a coordination snapshot and must not be used as a shared writable lock.

# Ownership and overlap check

- Open PRs inspected: current coordination PRs and autonomous program PRs.
- Active tasks inspected: current task records are intentionally treated as read-only inputs.
- Overlaps: shared agent instructions and task template.
- Resolution: narrow additive edits on a dedicated coordination branch.

# Current state

Implementation in progress.

# Plan

1. Add program record documentation and template.
2. Extend task ownership metadata compatibly.
3. Add deterministic ownership checker, tests, and CI.
4. Update mandatory startup protocol.
5. Validate and open a draft PR.

# Work log

## 2026-07-13T00:00:00+02:00

- Changed: claimed coordination paths and branch.
- Learned: existing rules already require task records and advisory ownership but lack deterministic validation.
- Failed/blocked: none.
- Result: implementation started.

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| pending | focused Python unit tests | not-run | |

# Remaining work

1. Implement and validate the coordination tooling.

# Handoff

## Start here

Read this task, `AGENTS.md`, and `docs/agents/README.md`, then inspect the branch diff.

## Do not repeat

Do not create another shared manually maintained ownership index.

## Required reads

- `AGENTS.md`
- `docs/agents/README.md`
- `docs/agents/templates/TASK.md`

## Open questions

None.
