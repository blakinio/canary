---
task_id: CAN-20260802-anti-stall-budget-v1
program_id: CAN-PROGRAM-AGENT-GOVERNANCE
coordination_id: ANTI-STALL-BUDGET-V1
status: implementing
agent: "GPT-5.6 Thinking"
branch: docs/anti-stall-budget-v1-20260802
base_branch: main
created: 2026-08-02T10:29:00+02:00
updated: 2026-08-02T10:29:00+02:00
risk: low
related_pr: ""
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

## Budget checkpoint

```yaml
invocation_started_at: 2026-08-02T10:29:00+02:00
last_progress_at: 2026-08-02T10:29:00+02:00
runtime_limit_minutes: 60
no_progress_minutes: 15
ci_checks_for_current_head: 0
unchanged_state_checks: 0
identical_failure_retries: 0
repair_cycles_for_current_gate: 0
context_reconstruction_attempts: 0
stall_warnings: 0
next_action: open the implementation PR and verify exact-head checks
```
