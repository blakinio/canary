---
task_id: CAN-20260802-active-task-lifecycle-isolation
program_id: CAN-PROGRAM-AGENT-ORCHESTRATION
coordination_id: ACO-005-LIFECYCLE-ISOLATION
status: implementing
agent: chat-github
branch: fix/CAN-20260802-active-task-lifecycle-isolation
base_branch: main
created: 2026-08-02T13:38:00Z
updated: 2026-08-02T13:42:00Z
last_verified_commit: a818d4af5f262c0bd7a28046012506627dcc7cec
risk: low
related_issue: ""
related_pr: "1064"
depends_on:
  - ACO-005 feature PR 623 merged as cf0d4fcb1c7d44d6633037b2d4cac761383a9f4e
blocks:
  - CAN-20260802-agent-governance-sync
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260802-active-task-lifecycle-isolation.md
    - docs/agents/tasks/active/CAN-20260720-agent-context-efficiency.md
    - docs/agents/tasks/archive/CAN-20260720-agent-context-efficiency.md
    - docs/agents/programs/AGENT_CONTEXT_ORCHESTRATION_PROGRAM.md
  shared: []
  read_only:
    - tools/agents/resume.py
    - tools/agents/test_context_orchestration.py
modules_touched:
  - autonomous agent task lifecycle
reuses:
  - ACO-002 task lifecycle and ownership validation
public_interfaces:
  - active task inventory
cross_repo_tasks:
  - CAN-20260802-agent-governance-sync
---

# Goal

Isolate and repair the stale active-task lifecycle state left after ACO-005 PR #623 merged, then prove that the repository's resume-prompt tests remain fixture-bounded without changing agent tooling.

# Acceptance criteria

- [x] Move the terminal ACO-005 task from active to archive with ownership released.
- [x] Mark ACO-005 completed in the orchestration programme and remove the stale current-task handoff.
- [ ] Confirm focused context/resume tests pass unchanged.
- [ ] Pass Agent Task Ownership and required CI on the exact final head.
- [x] Keep changes limited to task/program lifecycle records.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-02T13:42:00Z
head: a818d4af5f262c0bd7a28046012506627dcc7cec
branch: fix/CAN-20260802-active-task-lifecycle-isolation
pr: 1064
status: validating
context_routes:
  - agent-governance
  - ci-repair
owned_paths:
  - docs/agents/tasks/active/CAN-20260802-active-task-lifecycle-isolation.md
  - docs/agents/tasks/active/CAN-20260720-agent-context-efficiency.md
  - docs/agents/tasks/archive/CAN-20260720-agent-context-efficiency.md
  - docs/agents/programs/AGENT_CONTEXT_ORCHESTRATION_PROGRAM.md
proven:
  - PR 623 merged ACO-005 as cf0d4fcb1c7d44d6633037b2d4cac761383a9f4e.
  - The stale ACO-005 active task was replaced by a terminal archive record with empty ownership.
  - The orchestration programme now marks ACO-005 and the programme completed.
  - Agent Task Ownership run 30749784797 for governance PR 1063 failed after focused unit tests passed, on stale ownership plus an empty programme ID in the governance task.
derived:
  - This PR removes the independent stale-ownership blocker without changing resume or ownership tooling.
unknown:
  - Exact-final-head Agent Task Ownership and CI conclusions for PR 1064.
conflicts: []
first_failure:
  marker: Agent Task Ownership validate active ownership
  evidence: run 30749784797 job 91501650172 reported stale checkpoint.py ownership overlap
rejected_hypotheses:
  - The latest governance failure is ResumePromptTests.test_generate_prompt_is_bounded; the focused unit-test step passed before ownership validation failed.
changed_paths:
  - docs/agents/tasks/active/CAN-20260802-active-task-lifecycle-isolation.md
  - docs/agents/tasks/active/CAN-20260720-agent-context-efficiency.md
  - docs/agents/tasks/archive/CAN-20260720-agent-context-efficiency.md
  - docs/agents/programs/AGENT_CONTEXT_ORCHESTRATION_PROGRAM.md
validation:
  - command: Agent Task Ownership workflow
    result: NOT_RUN
    evidence: final-gate label applied; exact-final-head run pending after this checkpoint commit
blockers: []
next_action: verify exact-final-head Agent Task Ownership and CI for PR 1064, then merge if every gate is green
```
