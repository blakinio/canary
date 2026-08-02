---
task_id: CAN-20260802-agent-governance-sync
program_id: CAN-PROGRAM-AGENT-GOVERNANCE
coordination_id: PORTFOLIO-AGENT-GOVERNANCE-20260802
status: review
agent: chat-github
branch: docs/CAN-20260802-agent-governance-sync
base_branch: main
created: 2026-08-02T12:33:00Z
updated: 2026-08-02T13:46:00Z
last_verified_commit: 8698b07eab532dd64bf287b21bf62844e046a73a
risk: medium
related_issue: ""
related_pr: "1063"
depends_on:
  - CAN-20260802-active-task-lifecycle-isolation / PR 1064
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
- [ ] Agent Governance checks pass on the exact final PR head after the lifecycle dependency merges.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-02T13:46:00Z
head: 8698b07eab532dd64bf287b21bf62844e046a73a
branch: docs/CAN-20260802-agent-governance-sync
pr: 1063
status: validating
context_routes:
  - agent-governance
  - ci-repair
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
  - The shared documents separate checkpoint task status from terminal invocation result.
  - The anti-stall contract permits at most one additional task after the terminal entry task.
  - The Canary checkpoint validator accepts waiting, completed and NOT_APPLICABLE.
  - Main CI passed on governance head 8698b07eab532dd64bf287b21bf62844e046a73a.
  - Agent Task Ownership run 30749784797 passed focused unit tests and changed-task checkpoint validation before failing ownership indexing.
  - PR 1064 removes the stale ACO-005 active ownership that caused the checkpoint.py overlap.
derived:
  - The remaining branch-local defect is the empty programme ID, repaired by using the established CAN-PROGRAM-AGENT-GOVERNANCE identifier.
unknown:
  - Exact-final-head Agent Task Ownership conclusion after this metadata repair and PR 1064 merge.
conflicts: []
first_failure:
  marker: Agent Task Ownership validate active ownership
  evidence: run 30749784797 job 91501650172 reported empty program_id and stale checkpoint.py ownership overlap
rejected_hypotheses:
  - ResumePromptTests.test_generate_prompt_is_bounded is the latest failing gate; the focused unit-test step passed in run 30749784797.
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
  - command: Agent Task Ownership run 30749784797 focused unit tests
    result: PASS
    evidence: all 63 focused tests passed before ownership indexing
  - command: Agent Task Ownership run 30749784797 ownership index
    result: FAIL
    evidence: empty programme ID and stale ACO-005 checkpoint.py overlap; both now have bounded repairs
blockers:
  - PR 1064 must merge so the stale active ownership is absent from the trusted base.
next_action: verify PR 1064 merged, then inspect exact-final-head Agent Task Ownership and CI for PR 1063
```
