---
task_id: CAN-20260802-active-task-lifecycle-isolation
program_id: CAN-PROGRAM-AGENT-ORCHESTRATION
coordination_id: ACO-005-LIFECYCLE-ISOLATION
status: implementing
agent: chat-github
branch: fix/CAN-20260802-active-task-lifecycle-isolation
base_branch: main
created: 2026-08-02T13:38:00Z
updated: 2026-08-02T13:38:00Z
last_verified_commit: b33048677befeb88bc1365c0f3a7b268eb4b0aec
risk: low
related_issue: ""
related_pr: ""
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

- [ ] Move the terminal ACO-005 task from active to archive with ownership released.
- [ ] Mark ACO-005 completed in the orchestration programme and remove the stale current-task handoff.
- [ ] Confirm focused context/resume tests pass unchanged.
- [ ] Pass Agent Task Ownership and required CI on the exact final head.
- [ ] Keep changes limited to task/program lifecycle records.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-02T13:38:00Z
head: b33048677befeb88bc1365c0f3a7b268eb4b0aec
branch: fix/CAN-20260802-active-task-lifecycle-isolation
pr: null
status: implementing
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
  - The ACO-005 task remains under tasks/active and still claims tools/agents/checkpoint.py exclusively.
  - Agent Task Ownership run 30749784797 for governance PR 1063 fails on that stale ownership claim and an empty programme ID in the governance task.
derived:
  - Archiving the already-merged ACO-005 task is the smallest independent repair for the ownership half of the governance failure.
unknown:
  - Exact-head focused context/resume and ownership workflow results for this isolation task.
conflicts: []
first_failure:
  marker: Agent Task Ownership validate active ownership
  evidence: run 30749784797 job 91501650172 reports stale checkpoint.py ownership overlap
rejected_hypotheses:
  - The latest governance failure is ResumePromptTests.test_generate_prompt_is_bounded; the focused unit-test step passed before ownership validation failed.
changed_paths:
  - docs/agents/tasks/active/CAN-20260802-active-task-lifecycle-isolation.md
validation:
  - command: Agent Task Ownership workflow
    result: NOT_RUN
    evidence: draft PR not opened yet
blockers: []
next_action: archive the terminal ACO-005 task and update the programme record
```
