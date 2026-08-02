---
task_id: CAN-20260802-agent-governance-sync
program_id: ""
coordination_id: PORTFOLIO-AGENT-GOVERNANCE-20260802
status: review
agent: chat-github
branch: docs/CAN-20260802-agent-governance-sync
base_branch: main
created: 2026-08-02T12:33:00Z
updated: 2026-08-02T13:08:00Z
last_verified_commit: 0664abf4ff2bad2c5c980a4b440515770a800796
risk: medium
related_issue: ""
related_pr: "1063"
depends_on: []
blocks: []
owned_paths:
  exclusive:
    - AGENTS.override.md
    - docs/agents/AGENTS.md
    - docs/agents/ANTI_STALL_AND_EXECUTION_BUDGET.md
    - docs/agents/AUTONOMOUS_PROGRAM_CONTINUATION.md
    - docs/agents/DELIVERY_COMPLETENESS_AND_CLOSEOUT.md
    - docs/agents/GITHUB_ONLY_EXECUTION.md
    - tools/agents/checkpoint.py
  shared:
    - docs/agents/CONTEXT_HANDOFF.md
    - docs/agents/templates/TASK.md
  read_only: []
modules_touched:
  - agent-governance
reuses: []
public_interfaces: []
cross_repo_tasks:
  - OTC-20260802-agent-governance-sync
  - OTH-20260802-agent-governance-sync
  - OTERYN-20260802-agent-governance-sync
  - FTAI-20260802-agent-governance-sync
---

# Goal

Synchronize the shared autonomous-agent governance contract without changing product code or production behavior.

# Acceptance criteria

- [x] Shared task/invocation status semantics are unambiguous.
- [x] Anti-stall task-count policy no longer contradicts programme continuation.
- [x] Exact-head validation and temporary-workflow rules are deterministic.
- [x] Current-task governance edits cannot expand their own authority.
- [x] Checkpoint validation accepts waiting/completed and NOT_APPLICABLE.
- [ ] Agent Governance checks pass on the exact PR head.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-02T13:08:00Z
head: 0664abf4ff2bad2c5c980a4b440515770a800796
branch: docs/CAN-20260802-agent-governance-sync
pr: 1063
status: validating
context_routes:
  - agent-governance
owned_paths:
  - AGENTS.override.md
  - docs/agents/AGENTS.md
  - docs/agents/ANTI_STALL_AND_EXECUTION_BUDGET.md
  - docs/agents/AUTONOMOUS_PROGRAM_CONTINUATION.md
  - docs/agents/DELIVERY_COMPLETENESS_AND_CLOSEOUT.md
  - docs/agents/GITHUB_ONLY_EXECUTION.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/templates/TASK.md
  - tools/agents/checkpoint.py
proven:
  - The shared documents now separate checkpoint task status from terminal invocation result.
  - The anti-stall contract now permits at most one additional task after the terminal entry task.
  - The Canary checkpoint validator accepts waiting, completed and NOT_APPLICABLE.
derived:
  - The original status and task-count contradictions are repaired without invalidating existing checkpoint version 1 records.
unknown:
  - Exact-head Agent Governance workflow result for the current PR.
conflicts: []
first_failure:
  marker: none
  evidence: none
rejected_hypotheses: []
changed_paths:
  - AGENTS.override.md
  - docs/agents/AGENTS.md
  - docs/agents/ANTI_STALL_AND_EXECUTION_BUDGET.md
  - docs/agents/AUTONOMOUS_PROGRAM_CONTINUATION.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/DELIVERY_COMPLETENESS_AND_CLOSEOUT.md
  - docs/agents/GITHUB_ONLY_EXECUTION.md
  - docs/agents/tasks/active/CAN-20260802-agent-governance-sync.md
  - docs/agents/templates/TASK.md
  - tools/agents/checkpoint.py
validation:
  - command: Agent Governance workflow
    result: NOT_RUN
    evidence: draft PR 1063 opened; exact-head checks pending
blockers: []
next_action: inspect exact-head workflow results for PR 1063 and repair any governance failure
```
