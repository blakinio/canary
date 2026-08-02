---
task_id: CAN-20260802-agent-governance-sync
program_id: ""
coordination_id: PORTFOLIO-AGENT-GOVERNANCE-20260802
status: implementing
agent: chat-github
branch: docs/CAN-20260802-agent-governance-sync
base_branch: main
created: 2026-08-02T12:33:00Z
updated: 2026-08-02T12:33:00Z
last_verified_commit: ""
risk: medium
related_issue: ""
related_pr: ""
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
    - AGENTS.md
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

- [ ] Shared task/invocation status semantics are unambiguous.
- [ ] Anti-stall task-count policy no longer contradicts programme continuation.
- [ ] Exact-head validation and temporary-workflow rules are deterministic.
- [ ] Current-task governance edits cannot expand their own authority.
- [ ] Checkpoint validation accepts waiting/completed and NOT_APPLICABLE.
- [ ] Agent governance checks pass on the exact PR head.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-02T12:33:00Z
head: UNKNOWN
branch: docs/CAN-20260802-agent-governance-sync
pr: none
status: implementing
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
  - The current checkpoint validator rejects waiting and completed task states.
  - The anti-stall contract limits task starts to one while programme continuation requires a next READY task.
derived:
  - A backward-compatible additive policy revision can repair the conflict without migrating existing checkpoints.
unknown:
  - Exact governance workflow results on the future PR head.
conflicts: []
first_failure:
  marker: none
  evidence: none
rejected_hypotheses: []
changed_paths:
  - docs/agents/tasks/active/CAN-20260802-agent-governance-sync.md
validation:
  - command: Agent Governance workflow
    result: NOT_RUN
    evidence: PR not yet opened
blockers: []
next_action: update the shared governance contracts and checkpoint validator on this branch
```
