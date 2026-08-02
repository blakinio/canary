---
task_id: CAN-20260802-agent-governance-sync
program_id: CAN-PROGRAM-AGENT-GOVERNANCE
coordination_id: PORTFOLIO-AGENT-GOVERNANCE-20260802
status: review
agent: chat-github
branch: docs/CAN-20260802-agent-governance-sync
base_branch: main
created: 2026-08-02T12:33:00Z
updated: 2026-08-02T14:18:00Z
last_verified_commit: 5de3c6518da3c08d623f53b94c3ad52292da0566
risk: medium
related_issue: ""
related_pr: "1063"
depends_on:
  - CAN-20260802-active-task-lifecycle-isolation / PR 1064 merged as 61de87db6e5695b62b8949a377379a1d7b172049
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
- [ ] Agent Governance checks pass on the exact final PR head after the lifecycle dependency merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-02T14:18:00Z
head: 5de3c6518da3c08d623f53b94c3ad52292da0566
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
  - CI run 30750583942 passed on governance head 5de3c6518da3c08d623f53b94c3ad52292da0566.
  - Agent Task Ownership run 30750583820 passed all 63 focused tests and changed-task checkpoint validation.
  - PR 1064 merged as 61de87db6e5695b62b8949a377379a1d7b172049 and removed the stale ACO-005 checkpoint.py ownership from main.
derived:
  - A new pull-request run against current main can now prove the governance branch without the previous ownership conflict.
unknown:
  - Exact-final-head Agent Task Ownership and CI conclusions for the checkpoint commit created from this record.
conflicts: []
first_failure:
  marker: Agent Task Ownership ownership index on the pre-isolation base
  evidence: run 30749784797 job 91501650172 reported empty program_id and stale ACO-005 checkpoint.py ownership overlap
rejected_hypotheses:
  - ResumePromptTests.test_generate_prompt_is_bounded requires a tooling change; focused tests passed unchanged after lifecycle isolation.
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
  - command: Canary PR 1064 exact-head Agent Task Ownership and CI
    result: PASS
    evidence: lifecycle isolation merged normally as 61de87db6e5695b62b8949a377379a1d7b172049
  - command: Canary PR 1063 previous exact-head CI and focused ownership tests
    result: PASS
    evidence: CI run 30750583942 and focused tests in run 30750583820
blockers: []
next_action: inspect exact-final-head Agent Task Ownership and CI triggered by this checkpoint commit; if green, finalize PR 1063 and coordinated rollout
```
