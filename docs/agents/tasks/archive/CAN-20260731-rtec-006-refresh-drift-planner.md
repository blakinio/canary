---
task_id: CAN-20260731-rtec-006-refresh-drift-planner
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-006
agent: "GPT-5.6 Thinking"
status: completed
related_pr: 1038
lifecycle_pr: 1041
created: 2026-07-31T00:17:45+02:00
completed: 2026-07-31T01:02:30+02:00
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
- Lifecycle PR #1041 only moves this record from `active` to `archive` and releases RTEC-006 ownership.

## Final checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-31T01:02:30+02:00
head: 40cbc8f17fd39044f9b4ee399528ddabb6834856
branch: docs/archive-rtec-006-refresh-drift-planner-20260731
pr: 1041
merge_sha: da84057b43f9a3451c70fe06eb52c6e589715959
status: completed
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
  - Lifecycle PR 1041 changes only the archived task addition and matching active task deletion.
  - Lifecycle Agent Task Ownership run 30589123523 and CI run 30589123770 passed on reviewed lifecycle head 40cbc8f17fd39044f9b4ee399528ddabb6834856.
  - The ci:final-gate label was applied to PR 1041 before this final checkpoint commit.
  - Global evidence indexes, owner requests, dossier modules, workflow files and the RTEC programme remained unchanged.
  - docs/agents/PROJECT_STATE.md and docs/agents/prompts/RTEC_COMMON_AGENT_RULES.md were absent from the verified source base and remained UNKNOWN.
derived:
  - The lifecycle PR releases ownership through an exact active-to-archive move with no implementation changes.
unknown:
  - Lifecycle exact-head final-gate conclusion is pending this final checkpoint commit.
conflicts: []
first_failure:
  marker: none
  evidence: Source implementation, source final gate, source merge and reviewed lifecycle checks completed successfully.
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
  - command: lifecycle reviewed-head checks
    result: PASS
    evidence: Agent Task Ownership run 30589123523 and CI run 30589123770 succeeded on 40cbc8f17fd39044f9b4ee399528ddabb6834856.
  - command: lifecycle exact-head final gate after this checkpoint commit
    result: NOT_RUN
    evidence: The synchronize event from this final checkpoint commit must complete before PR 1041 is merged.
blockers: []
next_action: Merge PR 1041 only after its exact final checkpoint head passes Agent Task Ownership and CI without further lifecycle-branch commits.
```
