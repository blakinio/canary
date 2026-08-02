---
task_id: CAN-20260802-github-only-execution-v1
program_id: CAN-PROGRAM-AGENT-GOVERNANCE
coordination_id: GITHUB-ONLY-EXECUTION-V1
status: review
agent: "GPT-5.6 Thinking"
branch: docs/github-only-execution-v1-20260802
base_branch: main
created: 2026-08-02T11:43:00+02:00
updated: 2026-08-02T12:05:00+02:00
last_verified_commit: "2f35c74e3df88523721002680062d62df97997ce"
risk: low
related_pr: "1061"
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

Make the GitHub connection and GitHub Actions the mandatory fallback execution path when Codex or a local terminal is unavailable, while allowing gated autonomous merge or auto-merge and preserving separate production authorization.

## Acceptance

- [x] Add the normative GitHub-only execution contract.
- [x] Require it from the automatically loaded root bootstrap.
- [x] Route local agent execution through it.
- [x] Define bounded remote validation, temporary workflow, artifact, PR hygiene, blocker, merge, auto-merge, and production rules.
- [ ] Pass exact-head ownership and CI.
- [ ] Complete autonomous merge and archival.

## Context checkpoint

```yaml
checkpoint_version: 1
policy_version: 2
updated_at: 2026-08-02T12:05:00+02:00
head: 2f35c74e3df88523721002680062d62df97997ce
branch: docs/github-only-execution-v1-20260802
pr: 1061
status: validating
phase: validate
session_id: chat-20260802-github-only-execution-v1
session_role: coordinator
execution_mode: chat-github
run_scope: coordinated_governance_rollout
continuation_policy: continue_until_real_stop
task_completion_policy: complete_merge_and_archive
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
  - The owner durably authorizes gated autonomous merge or auto-merge of the current task PR.
  - Production deployment and protected operations remain separately unauthorized.
derived:
  - Missing Codex or local terminal can no longer be reported as a blocker without exhausting GitHub-only alternatives.
unknown:
  - Exact-head ownership and CI results after the auto-merge authorization update.
conflicts: []
first_failure:
  marker: none
  evidence: no validation failure observed
rejected_hypotheses:
  - GitHub-only execution should permit unbounded retries
  - merge authority is equivalent to production-deployment authority
changed_paths:
  - AGENTS.override.md
  - docs/agents/AGENTS.md
  - docs/agents/GITHUB_ONLY_EXECUTION.md
  - docs/agents/tasks/active/CAN-20260802-github-only-execution-v1.md
validation: []
blockers: []
invocation_started_at: 2026-08-02T11:43:00+02:00
last_progress_at: 2026-08-02T12:05:00+02:00
runtime_limit_minutes: 60
no_progress_minutes: 15
ci_checks_for_current_head: 0
unchanged_state_checks: 0
identical_failure_retries: 0
repair_cycles_for_current_gate: 0
context_reconstruction_attempts: 0
stall_warnings: 0
next_action: verify exact-head checks, mark PR 1061 ready, enable auto-merge, and archive after merge
```
