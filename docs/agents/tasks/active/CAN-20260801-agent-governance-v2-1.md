---
task_id: CAN-20260801-agent-governance-v2-1
program_id: CAN-PROGRAM-AGENT-GOVERNANCE
coordination_id: AGENT-GOVERNANCE-V2-1
status: implementing
agent: "GPT-5.6 Thinking"
branch: docs/agent-governance-v2-1-20260801
base_branch: main
created: 2026-08-01T23:46:00+02:00
updated: 2026-08-01T23:46:00+02:00
last_verified_commit: "UNKNOWN"
risk: low
related_issue: ""
related_pr: ""
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
  - blakinio/freqtrade
  - blakinio/Oteryn-Platform
  - blakinio/Otheryn
  - blakinio/otclient
---

# CAN-20260801 — Agent governance v2.1

## Objective

Extend the v2 agent contracts with eval-driven prompting, explicit trust/context boundaries, outcome-based acceptance, complete frontend/backend vertical slices, and mandatory PR hygiene, fresh audit, E2E, final CI, archival, and ownership release.

## Scope

Documentation and agent-governance contracts only. No runtime, production, upstream, asset, protocol, workflow, or application mutation is authorized.

## Acceptance criteria

- [ ] Prompt changes are versioned and regression-evaluated with balanced positive/negative cases and multiple trials where nondeterminism matters.
- [ ] Completion evidence comes from resulting environment state, not worker claims.
- [ ] Untrusted retrieved content cannot redefine instructions, permissions, destinations, or tool use.
- [ ] User-facing work defaults to a complete vertical slice across applicable backend and frontend layers.
- [ ] Task closeout requires fresh audit, real E2E, exact-head final CI, review-thread resolution, and terminal handling of every related PR.
- [ ] Autonomous coordination archives completed tasks, releases ownership, reviews barriers, and continues with the next READY task.
- [ ] Required exact-head CI and ownership checks pass.
- [ ] This task is archived after merge.

## Context checkpoint

```yaml
checkpoint_version: 1
policy_version: 2
updated_at: 2026-08-01T23:46:00+02:00
head: UNKNOWN
branch: docs/agent-governance-v2-1-20260801
pr: UNKNOWN
status: implementing
phase: implement
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
  - The merged v2 contract already supports long low-noise owner invocations and task archival.
  - The owner explicitly authorized this cross-repository governance update.
derived:
  - The safest extension is a small set of normative contracts referenced by the existing prompting entry points.
unknown:
  - Exact PR number and exact-head workflow results until the draft PR is opened.
conflicts: []
first_failure:
  marker: none
  evidence: no exact-head failure classified yet
rejected_hypotheses:
  - encode all new rules only in chat
  - mark backend-only work as a completed user-facing feature
  - treat an implementation PR merge as sufficient task closeout
changed_paths:
  - docs/agents/tasks/active/CAN-20260801-agent-governance-v2-1.md
validation: []
blockers: []
next_action: add the v2.1 normative contracts and update the prompting entry points
```
