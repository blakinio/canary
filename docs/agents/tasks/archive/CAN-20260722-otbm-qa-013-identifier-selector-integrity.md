---
task_id: CAN-20260722-otbm-qa-013-identifier-selector-integrity
program_id: CAN-PROGRAM-OTBM
status: complete
agent: "GPT-5.6 Thinking"
branch: docs/archive-otbm-qa-013-identifier-selector-integrity-724
base_branch: main
created: 2026-07-22
updated: 2026-07-22
last_verified_commit: "1cba80be50116cb936e805784e5c1abcdd98bc7e"
risk: medium
related_issue: ""
related_pr: "731"
depends_on:
  - CAN-20260722-otbm-qa-012-critical-access-integrity complete
  - Unified OTBM World Index available
  - OTBM script-resolution audit available
  - OTBM Reachability transition contract available
  - OTBM Route Interaction Registry available
blocks:
  - OTBM-QA-017 deterministic change risk
owned_paths:
  exclusive: []
  shared: []
  read_only:
    - tools/ai-agent/otbm_identifier_integrity.py
    - tools/ai-agent/otbm_identifier_integrity_tool.py
    - docs/ai-agent/OTBM_IDENTIFIER_INTEGRITY.md
    - docs/ai-agent/OTBM_IDENTIFIER_INTEGRITY_POLICY.schema.json
    - docs/ai-agent/OTBM_IDENTIFIER_INTEGRITY.schema.json
modules_touched:
  - otbm-identifier-integrity
reuses:
  - Unified OTBM World Index exact placement and mechanic evidence
  - OTBM Script Resolution identifier and handler evidence
  - OTBM Reachability transition manifest validation
  - OTBM Route Interaction Registry selector semantics
public_interfaces:
  - canary-otbm-identifier-integrity-policy-v1
  - canary-otbm-identifier-integrity-v1
cross_repo_tasks: []
---

# CAN-20260722 — OTBM-QA-013 Identifier, Selector and Collision Integrity

## Status

COMPLETE — bounded QA-013 implementation merged through feature PR #724, required shared-doc governance merged through PR #727, and lifecycle PR #731 contains only the active-to-archive task-record move.

## Goal

Provide deterministic read-only evidence for identifier and selector conflicts without treating ordinary repeated AIDs/item IDs as defects and without rebuilding canonical map, script, transition or route-interaction logic.

## Delivered

- Added reviewed `canary-otbm-identifier-integrity-policy-v1` and deterministic `canary-otbm-identifier-integrity-v1` contracts.
- Reused canonical World Index mechanic placements for exact AID/UID/house-door inventory and house scope; no OTBM parser or scanner was added.
- Preserved existing Script Resolution `conflicting` evidence while unresolved/partial/referenced-only evidence remains unresolved.
- Reused the existing transition parser contract and reviewed Route Interaction Registry; no second resolver or pathfinder was added.
- Added reviewed `unique` versus `reviewed-reuse` policy; unreviewed repetition remains `review-required`.
- Added exact house-door `houseId + houseDoorId` scope and exact reviewed placement-role compatibility evidence.
- Added stable-input, exact-provenance, create-new/no-clobber output safety and internal Route Interaction provenance compatibility.
- Added focused semantic, schema and output-safety tests and dedicated documentation.
- Registered the reusable public surface in `MODULE_CATALOG.md` and recorded the delivered behavior in `CHANGELOG.md` through governance PR #727.

## Proof boundary

- Repeated AIDs or item IDs are not automatically defects.
- Static identifier/selector evidence does not prove runtime behavior, player intent or global uniqueness outside reviewed scope.
- No Lua/runtime execution, map/datapack mutation, repair recommendation or automatic identifier renumbering is performed.

## Merge evidence

- Feature PR: #724 — `feat(otbm): add identifier and selector integrity analysis`.
- Final feature head: `b9e4c954a4e9a2f2f5b13c2f593c0e47c3956e2b`.
- Feature squash merge: `09e0324894f011b95e3fe132e0634d7fe40b0116`.
- Exact-final CI `29935892154`: success.
- Exact-final Agent Task Ownership `29935891991`: success.
- Exact-final OTBM Map Tools `29935892966`: success.
- Exact-final AI Agent Tools `29935891913`: success.
- Ready-for-review full CI `29936130293`: success after exactly one failed-job rerun of the transient Docker `Build and export (PR)` job; no feature commit changed.
- Final feature review audit found zero inline review threads and zero review submissions.
- Feature PR changed exactly nine bounded feature/test/docs/task paths.
- Governance PR #727 changed exactly two shared-doc paths with two additions and zero deletions.
- Governance PR #727 squash merged as `0d5f1be451b97e96add2066ee40d1ebca0e753a9` after pre-final CI `29945742703`, Ownership `29945742844` and full final-gate CI `29945834682` all succeeded.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T20:42:00+02:00
head: 1cba80be50116cb936e805784e5c1abcdd98bc7e
branch: docs/archive-otbm-qa-013-identifier-selector-integrity-724
pr: 731
status: complete
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/CAN-20260722-otbm-qa-013-identifier-selector-integrity.md
  - docs/agents/tasks/archive/CAN-20260722-otbm-qa-013-identifier-selector-integrity.md
proven:
  - QA-013 feature PR 724 merged as 09e0324894f011b95e3fe132e0634d7fe40b0116 from immutable final head b9e4c954a4e9a2f2f5b13c2f593c0e47c3956e2b.
  - Exact-final CI 29935892154, Ownership 29935891991, OTBM Map Tools 29935892966 and AI Agent Tools 29935891913 passed on the immutable feature head.
  - Ready-for-review full CI 29936130293 passed on the same immutable feature head after exactly one failed-job rerun for a Docker build/export failure; all non-Docker matrix jobs were already green and no feature commit changed.
  - Feature PR 724 changed exactly nine bounded paths and final review audit found zero review threads and zero review submissions.
  - Governance PR 727 merged as 0d5f1be451b97e96add2066ee40d1ebca0e753a9 with exactly one MODULE_CATALOG row and one CHANGELOG bullet, zero deletions and no unrelated modifications.
  - Governance pre-final CI 29945742703, Ownership 29945742844 and full final-gate CI 29945834682 all passed on immutable governance head f26ca429def377f2dcf2dca742134cdb92110e20.
  - Lifecycle PR 731 changes exactly the active and archive QA-013 task-record paths.
  - Lifecycle pre-final CI 29947390152 and Agent Task Ownership 29947389890 passed on head 1cba80be50116cb936e805784e5c1abcdd98bc7e.
  - ci:final-gate was applied to lifecycle PR 731 before this final checkpoint commit.
derived:
  - QA-014 may begin only after lifecycle PR 731 merges, followed by a fresh live-state and ownership preflight.
unknown:
  - Intentional identifier reuse cannot be inferred from repetition alone; unreviewed reuse remains review-required unless exact conflict evidence or reviewed policy closes it.
conflicts: []
first_failure:
  marker: docker-build-export-transient
  evidence: Ready-for-review CI 29936130293 initially failed only Docker Build and export (PR); one failed-job rerun passed without any feature code change.
rejected_hypotheses:
  - Treating every repeated AID or itemId as a defect.
  - Rebuilding Script Resolution, transition parsing or Route Interaction resolution inside QA-013.
  - Inferring incompatible mechanic roles from names, sprites, proximity or source location.
changed_paths:
  - docs/agents/tasks/active/CAN-20260722-otbm-qa-013-identifier-selector-integrity.md
  - docs/agents/tasks/archive/CAN-20260722-otbm-qa-013-identifier-selector-integrity.md
validation:
  - command: GitHub Actions CI run 29935892154
    result: PASS
    evidence: exact-final-head repository CI passed before feature merge.
  - command: GitHub Actions Agent Task Ownership run 29935891991
    result: PASS
    evidence: exact-final-head ownership validation passed.
  - command: GitHub Actions OTBM Map Tools run 29935892966
    result: PASS
    evidence: exact-final-head focused OTBM validation passed.
  - command: GitHub Actions AI Agent Tools run 29935891913
    result: PASS
    evidence: exact-final-head AI-agent validation passed.
  - command: GitHub Actions CI run 29936130293
    result: PASS
    evidence: ready-for-review full final-gate matrix passed after one failed-job Docker rerun with no feature commit change.
  - command: GitHub Actions CI run 29945834682
    result: PASS
    evidence: governance full final-gate matrix passed before PR 727 auto-merge.
  - command: GitHub Actions CI run 29947390152
    result: PASS
    evidence: lifecycle pre-final repository CI passed before final checkpoint.
  - command: GitHub Actions Agent Task Ownership run 29947389890
    result: PASS
    evidence: lifecycle pre-final ownership validation passed before final checkpoint.
blockers: []
next_action: Verify exact-final lifecycle CI and Ownership plus review/mergeability on the immutable lifecycle head, mark PR 731 ready with auto-merge, confirm its squash merge, then perform a fresh QA-014 live-state/overlap preflight and create the active QA-014 checkpoint for resume.py.
```
