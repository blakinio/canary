---
task_id: CAN-20260731-rtec-006-refresh-drift-planner
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-006
status: ready
agent: "GPT-5.6 Thinking"
branch: feat/rtec-006-refresh-drift-planner-20260731
base_branch: main
created: 2026-07-31T00:17:45+02:00
updated: 2026-07-31T00:41:30+02:00
last_verified_commit: "4b6903840a7b06275d14c45296678bbe95f21096"
risk: medium
related_issue: ""
related_pr: "1038"
depends_on:
  - RTEC-001
  - populated Real Tibia evidence dossiers
blocks:
  - RTEC-007
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260731-rtec-006-refresh-drift-planner.md
    - tools/agents/real_tibia_refresh_plan.py
    - tools/agents/test_real_tibia_refresh_plan.py
    - docs/agents/real-tibia/REFRESH_OPERATION.md
  shared: []
  read_only:
    - AGENTS.md
    - docs/agents/AGENTS.md
    - docs/agents/REPOSITORY_MAP.md
    - docs/agents/CONTEXT_HANDOFF.md
    - docs/agents/CONTEXT_ROUTING.md
    - docs/agents/PROJECT_STATE.md
    - docs/agents/ACTIVE_WORK.md
    - docs/agents/BUILD_TEST_MATRIX.md
    - docs/agents/programs/README.md
    - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
    - docs/agents/prompts/RTEC_COMMON_AGENT_RULES.md
    - docs/agents/real-tibia/evidence/**
    - docs/agents/real-tibia/registry/modules/**
    - tools/agents/real_tibia_evidence.py
    - tools/agents/real_tibia_evidence_lib.py
    - tools/agents/real_tibia_evidence_test_support.py
    - .github/workflows/real-tibia-evidence.yml
modules_touched:
  - real-tibia-evidence-collection
  - platform-tooling
reuses:
  - canary-real-tibia-evidence-record-v1
  - Corpus publication validation
  - deterministic freshness diagnostics
public_interfaces:
  - read-only deterministic Real Tibia refresh/drift planner CLI
cross_repo_tasks: []
---

# Goal

Implement the bounded RTEC-006 read-only planner that deterministically selects published Real Tibia evidence records requiring re-verification because of freshness windows, explicit stale state, exact version-baseline deltas, changed Canary paths, changed source identifiers or an explicit module selector.

# Acceptance criteria

- [x] Add a Python 3.12 standard-library CLI with an explicit `--as-of` date and deterministic JSON output.
- [x] Reuse the validated publication view; never publish or act on prepublication records.
- [x] Select inclusive freshness warning/invalidation boundaries and explicit `STALE` state without mutating records.
- [x] Select exact target-version deltas across the canonical version axes while preserving historical-version records as historical evidence.
- [x] Select changed repository paths and source identifiers from exact evidence provenance.
- [x] Produce stable priorities, reasons, input identity and plan digest independent of argument order.
- [x] Fail closed on malformed selectors, invalid corpus state, unsafe paths and duplicate/conflicting target axes.
- [x] Exclude rejected and superseded evidence from actionable output.
- [x] Add focused positive, negative, determinism, CLI and no-mutation tests.
- [x] Document the operator workflow, output contract, priority rules and nonclaims.
- [x] Change no global evidence index, owner request, dossier module or RTEC programme file.
- [ ] Pass the final-gate checks on the final source head and squash-merge the source PR.
- [ ] Archive this task in a separate lifecycle PR and merge it.

# Scope boundaries

This task only plans future review work. It does not refresh evidence, change evidence state, accept owner results, regenerate shared indexes, edit dossiers, infer Real Tibia behavior, claim a defect, claim parity drift or execute owner-programme work.

`docs/agents/PROJECT_STATE.md` and `docs/agents/prompts/RTEC_COMMON_AGENT_RULES.md` are absent from current `main@dcc09b1d012cbf4462aecc9970ae8540353ea8e3`. Their contents remain `UNKNOWN`; no historical or invented substitute is used. The explicit user-owned paths, current root/nested governance and current RTEC programme boundary remain authoritative for this bounded implementation.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-31T00:41:30+02:00
head: 4b6903840a7b06275d14c45296678bbe95f21096
branch: feat/rtec-006-refresh-drift-planner-20260731
pr: 1038
status: ready
context_routes:
  - agent-governance
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260731-rtec-006-refresh-drift-planner.md
  - tools/agents/real_tibia_refresh_plan.py
  - tools/agents/test_real_tibia_refresh_plan.py
  - docs/agents/real-tibia/REFRESH_OPERATION.md
proven:
  - PR 1038 targets blakinio/canary main from the dedicated RTEC-006 branch
  - the exact PR diff contains only the four declared exclusive paths
  - planner uses explicit as_of, validated publication filtering, exact version anchors and exact provenance selectors
  - planner emits stable priorities, normalized selectors, input SHA-256 and plan SHA-256 identities
  - planner performs no corpus writes and excludes prepublication, rejected and superseded records from actionable output
  - historical-version evidence is not selected solely because a newer target version is supplied
  - malformed selectors, unsafe paths and blocking corpus errors fail closed
  - Python bytecode compilation passed for the source and repository test file
  - seven focused planner and CLI tests passed in the deterministic isolated harness
  - Agent Task Ownership, Real Tibia Module Registry, Upstream Intelligence and draft CI passed on 2f336c8a86b4b1bb028b778d790fb59240d98309
  - ready-for-review CI was started on 83c34da246fd71533bd111692643ccd84f2904ec
  - ci:final-gate was applied before the final task/checkpoint commits
  - global evidence indexes, owner requests, dossier modules, workflow files and the RTEC programme remain unchanged
  - docs/agents/PROJECT_STATE.md is absent on current main
  - docs/agents/prompts/RTEC_COMMON_AGENT_RULES.md is absent on current main
  - the dedicated Real Tibia evidence workflow does not currently include the new planner paths in its path filter
derived:
  - focused planner behavior is validated locally while repository-wide final checks remain authoritative for merge
unknown:
  - final-gate conclusion on the final source head is pending this checkpoint commit
  - missing RTEC common rules cannot be evaluated because the current repository has no such file
  - missing project state cannot be evaluated because the current repository has no such file
conflicts: []
first_failure:
  marker: none
  evidence: all implementation failures were corrected task-checkpoint metadata; no open code failure remains
rejected_hypotheses:
  - planner code caused the ownership failures: each failure rejected only task checkpoint metadata
  - the planner should edit evidence or shared indexes: user scope and programme boundaries forbid those writes
  - historical evidence should become stale solely because a newer target version exists: historical-version records preserve bounded historical facts
changed_paths:
  - docs/agents/real-tibia/REFRESH_OPERATION.md
  - docs/agents/tasks/active/CAN-20260731-rtec-006-refresh-drift-planner.md
  - tools/agents/real_tibia_refresh_plan.py
  - tools/agents/test_real_tibia_refresh_plan.py
validation:
  - command: python -m py_compile real_tibia_refresh_plan.py test_real_tibia_refresh_plan.py
    result: PASS
    evidence: Python bytecode compilation completed without diagnostics
  - command: deterministic isolated planner test harness
    result: PASS
    evidence: 7 tests passed for freshness, versions, selectors, ordering, digests, CLI, publication filtering and no mutation
  - command: GitHub Actions on 2f336c8a86b4b1bb028b778d790fb59240d98309
    result: PASS
    evidence: CI, Agent Task Ownership, Real Tibia Module Registry and Upstream Intelligence succeeded
  - command: source PR final gate
    result: NOT_RUN
    evidence: ci:final-gate is applied and this final task commit must trigger the exact-head run
blockers: []
next_action: Confirm all required final-gate checks on the resulting exact source head, then squash-merge PR 1038 without further source-branch commits.
```
