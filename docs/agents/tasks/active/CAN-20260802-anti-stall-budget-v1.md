---
task_id: CAN-20260802-anti-stall-budget-v1
program_id: CAN-PROGRAM-AGENT-GOVERNANCE
coordination_id: ANTI-STALL-BUDGET-V1
status: review
agent: "GPT-5.6 Thinking"
branch: docs/anti-stall-budget-v1-20260802
base_branch: main
created: 2026-08-02T10:29:00+02:00
updated: 2026-08-02T11:04:00+02:00
last_verified_commit: "ab7269618b2a3155e4b82823ad4f302a1fd231b4"
risk: low
related_pr: "1059"
owned_paths:
  exclusive:
    - AGENTS.override.md
    - docs/agents/AGENTS.md
    - docs/agents/ANTI_STALL_AND_EXECUTION_BUDGET.md
    - docs/agents/tasks/active/CAN-20260802-anti-stall-budget-v1.md
  shared: []
  read_only:
    - docs/agents/AUTONOMOUS_PROGRAM_CONTINUATION.md
    - docs/agents/DELIVERY_COMPLETENESS_AND_CLOSEOUT.md
---

# Anti-stall and execution budget v1

## Goal

Prevent autonomous agents from polling, retrying, repairing, or selecting tasks indefinitely while preserving durable progress and safe continuation.

## Acceptance

- [x] Add a normative anti-stall and execution-budget contract.
- [x] Make the root bootstrap require it before autonomous or long-running work.
- [x] Route local task execution through the contract.
- [x] Define measurable progress, wall-clock and counter fallbacks, CI polling limits, retry limits, repair limits, command timeouts, next-task gates, and terminal response fields.
- [ ] Pass exact-head governance and CI.
- [ ] Merge and archive.

## Context checkpoint

```yaml
checkpoint_version: 1
policy_version: 2
updated_at: 2026-08-02T11:04:00+02:00
head: ab7269618b2a3155e4b82823ad4f302a1fd231b4
branch: docs/anti-stall-budget-v1-20260802
pr: 1059
status: validating
phase: validate
session_id: chat-20260802-anti-stall-budget-v1-continuation
session_role: coordinator
execution_mode: chat
run_scope: autonomous_program
continuation_policy: continue_until_real_stop
task_completion_policy: finalize_archive_and_continue
user_communication: low_noise
context_routes:
  - agent-governance
owned_paths:
  - AGENTS.override.md
  - docs/agents/AGENTS.md
  - docs/agents/ANTI_STALL_AND_EXECUTION_BUDGET.md
  - docs/agents/tasks/active/CAN-20260802-anti-stall-budget-v1.md
proven:
  - The root bootstrap requires the anti-stall contract before autonomous or long-running work.
  - The local agent router requires budget counters and bounded stop conditions.
  - The contract limits CI checks, retries, repair cycles, context reconstruction, commands, runtime and no-progress time.
  - Repository CI run 6787 passed on the prior exact head.
  - task_ownership.py defines review as an active status.
  - task_lifecycle.py permits checkpoint status validating when task status is review.
derived:
  - Autonomous continuation can no longer legitimately justify indefinite polling or overnight execution without a declared budget.
unknown:
  - Exact-head ownership and CI result after selecting the validator-supported review status.
conflicts: []
first_failure:
  marker: active-status-enum
  evidence: Agent Task Ownership run 5620 and task_ownership.py show that literal active is not an allowed active task status.
rejected_hypotheses:
  - a task under tasks/active must use literal frontmatter status active
  - checkpoint and frontmatter must use identical status strings
changed_paths:
  - AGENTS.override.md
  - docs/agents/AGENTS.md
  - docs/agents/ANTI_STALL_AND_EXECUTION_BUDGET.md
  - docs/agents/tasks/active/CAN-20260802-anti-stall-budget-v1.md
validation:
  - command: python -m unittest -v test_task_ownership.py test_context_orchestration.py test_task_lifecycle.py test_efficiency_eval.py test_supervisor_queue.py test_ci_incremental_validation.py
    result: PASS
    evidence: Agent Task Ownership run 5620 focused unit-test step
  - command: GitHub Actions CI
    result: PASS
    evidence: CI run 6787 on prior head ab7269618b2a3155e4b82823ad4f302a1fd231b4
blockers: []
invocation_started_at: 2026-08-02T10:56:00+02:00
last_progress_at: 2026-08-02T11:04:00+02:00
runtime_limit_minutes: 60
no_progress_minutes: 15
ci_checks_for_current_head: 0
unchanged_state_checks: 0
identical_failure_retries: 0
repair_cycles_for_current_gate: 3
context_reconstruction_attempts: 1
stall_warnings: 0
next_action: verify exact-head checks for PR 1059 and merge when green
```
