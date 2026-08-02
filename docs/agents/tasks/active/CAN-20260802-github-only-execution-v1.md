---
task_id: CAN-20260802-github-only-execution-v1
program_id: CAN-PROGRAM-AGENT-GOVERNANCE
coordination_id: GITHUB-ONLY-EXECUTION-V1
status: review
agent: "GPT-5.6 Thinking"
branch: docs/github-only-execution-v1-20260802
base_branch: main
created: 2026-08-02T11:43:00+02:00
updated: 2026-08-02T11:43:00+02:00
last_verified_commit: "3fd2d509265bcf5b5b17005c4c69e70b61c05042"
risk: low
related_pr: "PENDING"
owned_paths:
  exclusive:
    - AGENTS.override.md
    - docs/agents/AGENTS.md
    - docs/agents/GITHUB_ONLY_EXECUTION.md
    - docs/agents/tasks/active/CAN-20260802-github-only-execution-v1.md
  shared: []
  read_only:
    - docs/agents/ANTI_STALL_AND_EXECUTION_BUDGET.md
    - docs/agents/AUTONOMOUS_PROGRAM_CONTINUATION.md
    - docs/agents/DELIVERY_COMPLETENESS_AND_CLOSEOUT.md
---

# GitHub-only execution v1

## Goal

Make the GitHub connection and GitHub Actions the mandatory fallback execution path when Codex or a local terminal is unavailable, without weakening safety, authorization, scope, validation, or anti-stall limits.

## Acceptance

- [x] Add the normative GitHub-only execution contract.
- [x] Require it from the automatically loaded root bootstrap.
- [x] Route local agent execution through it.
- [x] Define remote validation, minimal CI, temporary workflow, artifact, PR hygiene, blocker, merge, and production rules.
- [ ] Pass exact-head ownership and CI.
- [ ] Present a merge-ready PR without merging.

## Context checkpoint

```yaml
checkpoint_version: 1
policy_version: 2
updated_at: 2026-08-02T11:43:00+02:00
head: 3fd2d509265bcf5b5b17005c4c69e70b61c05042
branch: docs/github-only-execution-v1-20260802
pr: PENDING
status: validating
phase: validate
session_id: chat-20260802-github-only-execution-v1
session_role: coordinator
execution_mode: chat-github
run_scope: coordinated_governance_rollout
continuation_policy: continue_until_real_stop
task_completion_policy: prepare_validated_pr_without_merge
user_communication: low_noise
context_routes:
  - agent-governance
owned_paths:
  - AGENTS.override.md
  - docs/agents/AGENTS.md
  - docs/agents/GITHUB_ONLY_EXECUTION.md
  - docs/agents/tasks/active/CAN-20260802-github-only-execution-v1.md
proven:
  - The contract has been added on the dedicated branch.
  - Root and local routing require the contract when Codex or a local terminal is unavailable.
  - Merge, auto-merge and production remain unauthorized without explicit or durable authority.
derived:
  - Missing Codex or local terminal can no longer be reported as a blocker without exhausting the GitHub-only alternatives.
unknown:
  - Exact-head ownership and CI results after PR creation.
conflicts: []
first_failure:
  marker: none
  evidence: no validation failure observed
rejected_hypotheses:
  - GitHub-only execution should permit unbounded retries
  - GitHub-only execution should authorize merge or production deployment
changed_paths:
  - AGENTS.override.md
  - docs/agents/AGENTS.md
  - docs/agents/GITHUB_ONLY_EXECUTION.md
  - docs/agents/tasks/active/CAN-20260802-github-only-execution-v1.md
validation: []
blockers: []
invocation_started_at: 2026-08-02T11:43:00+02:00
last_progress_at: 2026-08-02T11:43:00+02:00
runtime_limit_minutes: 60
no_progress_minutes: 15
ci_checks_for_current_head: 0
unchanged_state_checks: 0
identical_failure_retries: 0
repair_cycles_for_current_gate: 0
context_reconstruction_attempts: 0
stall_warnings: 0
next_action: open the draft PR, bind this task to its number, and verify exact-head required checks
```
