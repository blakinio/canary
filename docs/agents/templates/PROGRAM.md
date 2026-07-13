---
program_id: CAN-PROGRAM-SHORT-NAME
name: Human-readable program name
status: active
owner: autonomous-agent-name
created: YYYY-MM-DDTHH:MM:SSZ
updated: YYYY-MM-DDTHH:MM:SSZ
last_verified_commit: ""
primary_paths: []
shared_integration_paths: []
related_programs: []
cross_repo_contracts: []
---

# Mission

State the long-lived outcome this autonomous program owns.

# Scope

- Included responsibility.

# Explicit exclusions

- Work this program must not perform.

# Existing systems to reuse

| Module/tool/contract | Source | Required reuse rule |
|---|---|---|
| | | |

# Active tasks

| Task ID | Branch | PR | State | Exact next action |
|---|---|---:|---|---|
| | | | | |

# Queue

1. Next evidence-backed task.

# Completed work

| Task/PR | Result | Merge commit | Follow-up |
|---|---|---|---|
| | | | |

# Dependencies and blockers

- None.

# Decisions and invariants

- Persistent rule that every future task must preserve.

# Validation strategy

- Required focused validation.
- Required integration or CI validation.

# Handoff

## Start here

Read `AGENTS.md`, `docs/agents/README.md`, this program record, all active task records, and open PRs before selecting work.

## Task creation protocol

1. Select one bounded task from the queue.
2. Inspect active ownership and overlapping PRs.
3. Create one task record, branch, worktree, and draft PR.
4. Declare exact exclusive/shared/read-only paths.
5. Implement, validate, merge, archive the task, and update this program record.

## Do not repeat

- Record abandoned approaches and duplicated work to avoid.

## Open questions

- None.
