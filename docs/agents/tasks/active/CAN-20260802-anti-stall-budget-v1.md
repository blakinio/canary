---
task_id: CAN-20260802-anti-stall-budget-v1
program_id: CAN-PROGRAM-AGENT-GOVERNANCE
coordination_id: ANTI-STALL-BUDGET-V1
status: validating
agent: "GPT-5.6 Thinking"
branch: docs/anti-stall-budget-v1-20260802
base_branch: main
created: 2026-08-02T10:29:00+02:00
updated: 2026-08-02T10:44:00+02:00
last_verified_commit: "b8f2053d435d8a92ecb463fcade8f5102beb5e7d"
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
updated_at: 2026-08-02T10:44:00+02:00
head: b8f2053d435d8a92ecb463fcade8f5102beb5e7d
branch: docs/anti-stall-budget-v1-20260802
pr: 1059
status: validating
phase: validate
session_id: chat-20260802-anti-stall-budget-v1
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
  - Repository CI run 6783 passed on the prior exact head.
derived:
  - Autonomous continuation can no longer legitimately justify indefinite polling or overnight execution without a declared budget.
unknown:
  - Exact-head ownership and CI result after this checkpoint syntax repair.
conflicts: []
first_failure:
  marker: validation-evidence-shape
  evidence: Agent Task Ownership run 5616 required validation entries to be key/value mappings.
rejected_hypotheses:
  - the contract content itself caused the ownership failure
  - repeating the unchanged validation entry would pass
changed_paths:
  - AGENTS.override.md
  - docs/agents/AGENTS.md
  - docs/agents/ANTI_STALL_AND_EXECUTION_BUDGET.md
  - docs/agents/tasks/active/CAN-20260802-anti-stall-budget-v1.md
validation:
  - check: focused agent tooling unit tests
    result: PASS
    evidence: Agent Task Ownership run 5615
  - check: repository CI
    result: PASS
    evidence: CI run 6783 on head b8f2053d435d8a92ecb463fcade8f5102beb5e7d
blockers: []
invocation_started_at: 2026-08-02T10:29:00+02:00
last_progress_at: 2026-08-02T10:44:00+02:00
runtime_limit_minutes: 60
no_progress_minutes: 15
ci_checks_for_current_head: 0
unchanged_state_checks: 0
identical_failure_retries: 0
repair_cycles_for_current_gate: 2
context_reconstruction_attempts: 0
stall_warnings: 0
next_action: verify exact-head checks for PR 1059
```
