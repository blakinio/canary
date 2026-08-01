---
task_id: CAN-20260801-agent-governance-v2-1
program_id: CAN-PROGRAM-AGENT-GOVERNANCE
coordination_id: AGENT-GOVERNANCE-V2-1
status: review
agent: "GPT-5.6 Thinking"
branch: docs/agent-governance-v2-1-20260801
base_branch: main
created: 2026-08-01T23:46:00+02:00
updated: 2026-08-02T00:10:00+02:00
last_verified_commit: "6a3546dae80e5c5b9f24383da4548ff27b87bd4e"
risk: low
related_issue: ""
related_pr: "1052"
depends_on: []
blocks: []
owned_paths:
  exclusive:
    - docs/agents/PROMPTING_STANDARD.md
    - docs/agents/PROMPTING_HANDOVER.md
    - docs/agents/AUTONOMOUS_PROGRAM_CONTINUATION.md
    - docs/agents/PROMPT_EVAL_STANDARD.md
    - docs/agents/TRUST_AND_CONTEXT_BOUNDARIES.md
    - docs/agents/END_TO_END_FEATURE_COMPLETENESS.md
    - docs/agents/TASK_CLOSEOUT_AUDIT_E2E.md
    - docs/agents/tasks/active/CAN-20260801-agent-governance-v2-1.md
  shared: []
  read_only:
    - AGENTS.md
    - docs/agents/EXECUTION_PROTOCOL.md
    - docs/agents/CONTEXT_HANDOFF.md
modules_touched:
  - agent-governance
reuses:
  - autonomous programme continuation v2
  - checkpoint contract v1
  - task lifecycle archive tooling
public_interfaces: []
cross_repo_tasks:
  - blakinio/freqtrade#985
  - blakinio/Oteryn-Platform#442
  - blakinio/Otheryn#298
  - blakinio/otclient#161
---

# CAN-20260801 — Agent governance v2.1

## Objective

Extend v2 with evaluated prompting, trust/context boundaries, outcome verification, complete applicable vertical slices, and mandatory PR hygiene, fresh audit, E2E, exact-head final CI, archival, and ownership release.

## Scope

Documentation and agent governance only. No runtime, production, upstream, asset, protocol, workflow, or application mutation is authorized.

## Acceptance criteria

- [x] Prompt changes are versioned and regression-evaluated with balanced positive/negative cases and multiple trials where nondeterminism matters.
- [x] Completion evidence comes from resulting environment state, not worker claims.
- [x] Untrusted retrieved content cannot redefine instructions, permissions, destinations, or tool use.
- [x] User-facing work defaults to a complete vertical slice across applicable backend and frontend layers.
- [x] Task closeout requires fresh audit, real E2E, exact-head final CI, review resolution, and terminal handling of every related PR.
- [x] Autonomous coordination archives completed tasks, releases ownership, reviews barriers, and continues with the next READY task.
- [ ] Required exact-head CI and ownership checks pass.
- [ ] This task is archived after merge.

## Context checkpoint

```yaml
checkpoint_version: 1
policy_version: 2
updated_at: 2026-08-02T00:10:00+02:00
head: 6a3546dae80e5c5b9f24383da4548ff27b87bd4e
branch: docs/agent-governance-v2-1-20260801
pr: 1052
status: validating
phase: audit_and_ci
session_id: chat-20260801-governance-v2-1
session_role: coordinator
execution_mode: chat
run_scope: autonomous_program
continuation_policy: continue_until_real_stop
task_completion_policy: finalize_archive_and_continue
user_communication: low_noise
context_routes:
  - agent-governance
owned_paths:
  - docs/agents/PROMPTING_STANDARD.md
  - docs/agents/PROMPTING_HANDOVER.md
  - docs/agents/AUTONOMOUS_PROGRAM_CONTINUATION.md
  - docs/agents/PROMPT_EVAL_STANDARD.md
  - docs/agents/TRUST_AND_CONTEXT_BOUNDARIES.md
  - docs/agents/END_TO_END_FEATURE_COMPLETENESS.md
  - docs/agents/TASK_CLOSEOUT_AUDIT_E2E.md
  - docs/agents/tasks/active/CAN-20260801-agent-governance-v2-1.md
proven:
  - Compare main...branch contains exactly eight authorized governance/task paths and no product or workflow code.
  - All referenced v2.1 contract paths exist on the branch.
  - The contracts preserve stricter repository safety, authorization, production, ownership, merge and cross-repository rules.
  - Prompt evaluation, trust boundaries, vertical-slice delivery, outcome verification, fresh audit, real E2E, exact-head CI, PR terminal states, archival and continue-to-next-READY semantics are normative.
  - Proportionate documentation audit found no missing reference, contradictory completion rule, hidden runtime authorization or material documentation defect.
  - Runtime E2E is NOT_APPLICABLE_WITH_REASON because the change modifies governance documentation only; path/content/lifecycle/CI validation remains required.
derived:
  - The v2.1 contract set directly addresses the owner-observed backend-without-frontend and stale-PR failure modes.
unknown:
  - Exact-head required workflow results after this checkpoint commit.
  - Fresh final PR diff review and review-thread state.
conflicts: []
first_failure:
  marker: none
  evidence: no exact-head failure classified yet
rejected_hypotheses:
  - encode durable rules only in chat
  - mark backend-only work as a completed user-facing feature
  - treat implementation merge as sufficient closeout
changed_paths:
  - docs/agents/AUTONOMOUS_PROGRAM_CONTINUATION.md
  - docs/agents/END_TO_END_FEATURE_COMPLETENESS.md
  - docs/agents/PROMPTING_HANDOVER.md
  - docs/agents/PROMPTING_STANDARD.md
  - docs/agents/PROMPT_EVAL_STANDARD.md
  - docs/agents/TASK_CLOSEOUT_AUDIT_E2E.md
  - docs/agents/TRUST_AND_CONTEXT_BOUNDARIES.md
  - docs/agents/tasks/active/CAN-20260801-agent-governance-v2-1.md
validation:
  - command: compare main...docs/agent-governance-v2-1-20260801
    result: PASS
    evidence: exactly eight authorized documentation/governance paths
  - command: cross-reference and contradiction audit
    result: PASS
    evidence: all seven normative contracts exist and the three entry points route to them consistently
  - command: runtime E2E applicability review
    result: NOT_APPLICABLE_WITH_REASON
    evidence: no executable product behavior changed
blockers: []
next_action: verify exact-head required checks and fresh PR diff review for PR 1052, then complete merge and lifecycle archive
```
