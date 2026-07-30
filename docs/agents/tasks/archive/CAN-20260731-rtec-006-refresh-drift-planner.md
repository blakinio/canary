---
task_id: CAN-20260731-rtec-006-refresh-drift-planner
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-006
agent: "GPT-5.6 Thinking"
status: completed
related_pr: 1038
lifecycle_pr: pending
created: 2026-07-31T00:17:45+02:00
completed: 2026-07-31T00:58:02+02:00
risk: medium
---

# CAN-20260731-rtec-006-refresh-drift-planner

## Goal

Implement the bounded RTEC-006 read-only planner that deterministically selects published Real Tibia evidence records requiring re-verification because of freshness windows, explicit stale state, exact version-baseline deltas, changed Canary paths, changed source identifiers or explicit module selection.

## Result

- Source PR #1038 added `tools/agents/real_tibia_refresh_plan.py`, focused tests and `docs/agents/real-tibia/REFRESH_OPERATION.md`.
- The CLI requires explicit `--as-of`; it has no wall-clock dependency.
- Planning reuses the validated publication view and existing stale diagnostics.
- Prepublication, rejected and superseded evidence is non-actionable.
- Exact target-version, Canary-path, source-ID and module selectors are normalized and deterministic.
- Historical-version records are not selected solely because a newer target version is supplied.
- Output carries deterministic priority/reason ordering, input SHA-256 and plan SHA-256 identities.
- Malformed selectors, unsafe paths and blocking corpus errors fail closed.
- The operation performs no evidence, dossier, owner-request, generated-index or programme mutation.
- Seven focused planner/CLI tests and Python bytecode compilation passed.
- Exact source head `c3cca39807cdf79750913cbce91cf747a88fed0c` passed Agent Task Ownership, Real Tibia Module Registry, Upstream Intelligence and full final-gate CI.
- Source PR #1038 squash-merged as `da84057b43f9a3451c70fe06eb52c6e589715959`.
- This lifecycle change only moves the task record from `active` to `archive` and releases RTEC-006 ownership.

## Final checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-31T00:58:30+02:00
head: da84057b43f9a3451c70fe06eb52c6e589715959
branch: docs/archive-rtec-006-refresh-drift-planner-20260731
pr: pending
merge_sha: da84057b43f9a3451c70fe06eb52c6e589715959
status: implementing
context_routes:
  - agent-governance
  - real-tibia-parity
proven:
  - PR 1038 changed only the three owned implementation paths and its own active task record.
  - The planner uses explicit as_of, validated publication filtering, exact version anchors and exact provenance selectors.
  - The planner emits stable priorities, normalized selectors, input SHA-256 and plan SHA-256 identities.
  - The planner performs no corpus writes and excludes prepublication, rejected and superseded records from actionable output.
  - Historical-version evidence is not selected solely because a newer target version is supplied.
  - Malformed selectors, unsafe paths and blocking corpus errors fail closed.
  - Seven focused planner and CLI tests passed in the deterministic isolated harness.
  - Agent Task Ownership, Real Tibia Module Registry, Upstream Intelligence and full CI passed on exact source head c3cca39807cdf79750913cbce91cf747a88fed0c.
  - PR 1038 merged as da84057b43f9a3451c70fe06eb52c6e589715959 without unresolved review threads or repository rule bypass.
  - Global evidence indexes, owner requests, dossier modules, workflow files and the RTEC programme remained unchanged.
  - docs/agents/PROJECT_STATE.md and docs/agents/prompts/RTEC_COMMON_AGENT_RULES.md were absent from the verified source base and remained UNKNOWN.
derived:
  - The lifecycle PR can release ownership by an exact active-to-archive move with no implementation changes.
unknown:
  - Lifecycle PR number and exact-head validation are pending creation of the lifecycle PR.
conflicts: []
first_failure:
  marker: none
  evidence: Source implementation, final gate and squash merge completed successfully.
rejected_hypotheses:
  - The lifecycle PR should modify implementation or evidence files.
  - Missing governance files should be reconstructed from historical copies.
changed_paths:
  - docs/agents/tasks/active/CAN-20260731-rtec-006-refresh-drift-planner.md
  - docs/agents/tasks/archive/CAN-20260731-rtec-006-refresh-drift-planner.md
validation:
  - command: deterministic isolated planner test harness
    result: PASS
    evidence: 7 tests passed for freshness, versions, selectors, ordering, digests, CLI, publication filtering and no mutation.
  - command: source exact-head final gate
    result: PASS
    evidence: Agent Task Ownership, Real Tibia Module Registry, Upstream Intelligence and CI succeeded on c3cca39807cdf79750913cbce91cf747a88fed0c.
  - command: source squash merge
    result: PASS
    evidence: PR 1038 merged as da84057b43f9a3451c70fe06eb52c6e589715959.
  - command: lifecycle exact-head checks
    result: NOT_RUN
    evidence: Lifecycle PR has not yet been created.
blockers: []
next_action: Delete the matching active task record, open the lifecycle PR, bind its number and run exact-head lifecycle checks.
```
