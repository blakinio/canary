---
task_id: CAN-YYYYMMDD-short-slug
program_id: CAN-PROGRAM-SHORT-NAME
coordination_id: ""
status: planned
agent: ""
branch: type/task-id-short-slug
base_branch: main
created: YYYY-MM-DDTHH:MM:SSZ
updated: YYYY-MM-DDTHH:MM:SSZ
last_verified_commit: ""
risk: low
related_issue: ""
related_pr: ""
depends_on: []
blocks: []
owned_paths:
  exclusive:
    - path/the/task/may/edit
  shared:
    - narrow/shared/index/or/contract
  read_only:
    - dependency/the/task/must/not/edit
modules_touched: []
reuses: []
public_interfaces: []
cross_repo_tasks: []
---

# Goal

State one exact, observable outcome.

# Acceptance criteria

- [ ] Observable behavior or artifact.
- [ ] Relevant focused checks completed.
- [ ] Current-head GitHub checks verified.
- [ ] Module catalogue impact handled or none.
- [ ] Documentation/changelog impact handled or none.
- [ ] Program queue/handoff impact handled or none.
- [ ] Cross-repository impact handled or none.
- [ ] Autonomous merge gate satisfied.

# Confirmed context

Verified facts, commits, PRs, versions, and constraints; mark assumptions and uncertainty explicitly.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| | | | |

# Ownership and overlap check

- Program record:
- Open PRs inspected:
- Active tasks inspected:
- Ownership checker result:
- Exclusive claims:
- Shared claims:
- Read-only dependencies:
- Overlaps:
- Resolution:

Before implementation, run when a local checkout is available:

```text
python tools/agents/task_ownership.py
```

# Current state

# Plan

1. Exact next action.

# Work log

## YYYY-MM-DDTHH:MM:SSZ

- Changed:
- Learned:
- Failed/blocked:
- Result:

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| | | |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| | exclusive/shared/read_only | | planned |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| | | not-run | |

Never write `passed` without verification on the stated commit.

# Failed approaches and dead ends

# Risks and compatibility

- Runtime:
- Data/migration:
- Security:
- Backward compatibility:
- Cross-repo rollout:
- Rollback:

# Remaining work

1. Exact next action.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: YYYY-MM-DDTHH:MM:SSZ
head: <commit-sha-or-UNKNOWN>
branch: <branch>
pr: <number-or-none>
status: investigating|implementing|validating|blocked|ready
context_routes:
  - <route>
owned_paths:
  - <path/glob>
proven:
  - <fact backed by source/tool/test evidence>
derived:
  - <explicitly derived conclusion>
unknown:
  - <unresolved fact>
conflicts:
  - <conflicting evidence that still needs resolution>
first_failure:
  marker: <first unmet invariant/check or none>
  evidence: <artifact/log/test reference>
rejected_hypotheses:
  - <hypothesis>: <disproving evidence>
changed_paths:
  - <path>
validation:
  - command: <command/workflow/job>
    result: PASS|FAIL|BLOCKED|NOT_RUN
    evidence: <short reference>
blockers:
  - <blocker or none>
next_action: <one concrete next step>
```

This `## Context checkpoint` is the authoritative machine-readable continuation state. Keep exactly one concrete top-level `next_action` and update the checkpoint after material state changes.

# Handoff

This section is optional human-readable context only. It does not replace or override the authoritative `## Context checkpoint` above.

## Start here

## Do not repeat

## Required reads

- `AGENTS.md`
- `docs/agents/README.md`
- relevant program record under `docs/agents/programs/`
- all overlapping active task records under `docs/agents/tasks/active/**`
- `docs/agents/MODULE_CATALOG.md`
- relevant source, tests, docs, contracts, and ADRs

## Open questions

# Completion

- Final status:
- PR:
- Merge commit:
- Program record updated:
- Catalogue updated:
- Changelog updated:
- Archived at:
