---
task_id: CAN-20260722-otbm-qa-013-identifier-selector-integrity
program_id: CAN-PROGRAM-OTBM
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/otbm-qa-013-identifier-integrity-20260722
base_branch: main
created: 2026-07-22
updated: 2026-07-22
last_verified_commit: "f3d850109e075368f04330b67230563c5332dc46"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - CAN-20260722-otbm-qa-012-critical-access-integrity complete
  - Unified OTBM World Index available
  - OTBM script-resolution audit available
  - OTBM Reachability transition contract available
  - OTBM Route Interaction Registry available
blocks:
  - OTBM-QA-017 deterministic change risk
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_identifier_integrity.py
    - tools/ai-agent/otbm_identifier_integrity_tool.py
    - tools/ai-agent/test_otbm_identifier_integrity.py
    - tools/ai-agent/test_otbm_identifier_integrity_output_safety.py
    - tools/ai-agent/test_otbm_identifier_integrity_schema.py
    - docs/ai-agent/OTBM_IDENTIFIER_INTEGRITY.md
    - docs/ai-agent/OTBM_IDENTIFIER_INTEGRITY_POLICY.schema.json
    - docs/ai-agent/OTBM_IDENTIFIER_INTEGRITY.schema.json
    - docs/agents/tasks/active/CAN-20260722-otbm-qa-013-identifier-selector-integrity.md
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/ai-agent/otbm_world_index.py
    - tools/ai-agent/otbm_script_resolution.py
    - tools/ai-agent/otbm_reachability_types.py
    - tools/ai-agent/otbm_reachability_transition.py
    - tools/ai-agent/otbm_route_interactions.py
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

IMPLEMENTING — QA-012 feature and lifecycle are complete; fresh QA-013 live-state and overlap preflight passed on `main` `f3d850109e075368f04330b67230563c5332dc46`.

## Goal

Provide deterministic read-only evidence for identifier and selector conflicts without treating ordinary repeated AIDs/item IDs as defects and without rebuilding canonical map, script, transition or route-interaction logic.

## Bounded slice

- Reuse the canonical World Index for exact mechanic placements and house/tile scope.
- Reuse existing Script Resolution aggregate/placement statuses for handler conflicts; do not rescan Lua/XML.
- Reuse the existing transition-manifest parser contract for duplicate/incompatible transition evidence; do not create a second transition validator.
- Reuse the reviewed Route Interaction Registry validation contract and detect selector overlap that may match more than one reviewed entry.
- Add an explicit reviewed policy for selected uniqueness/reuse expectations. Repetition without exact conflict evidence or reviewed uniqueness intent remains `review-required`.
- Support exact reviewed role/compatibility evidence only when a caller needs to prove that one reused selector spans incompatible mechanic roles.
- Preserve source-map, World Index and optional Script Resolution/transition/interaction evidence provenance and fail closed on stale or incompatible inputs.

## Explicit non-goals

- No OTBM parser/scanner, World Index, Script Resolution engine, transition resolver, route planner or E2E runner.
- No inference that repeated AIDs or item IDs are defects.
- No guessing intentional reuse, mechanic roles, handler compatibility or house semantics.
- No runtime execution, Lua execution, map mutation, repair recommendation or automatic identifier renumbering.
- No global uniqueness claim when the reviewed policy is bounded to a selected namespace/value/scope.

## Acceptance criteria

- Duplicate/reused World Index identifiers are inventory evidence, not automatic errors.
- A reviewed `unique` expectation violated by multiple exact matching placements is classified as conflicting.
- A reviewed reusable selector remains explicitly reviewed reuse rather than conflict.
- Existing Script Resolution `conflicting` evidence is preserved as conflict; unresolved/partial evidence is not promoted to conflict without other proof.
- Duplicate transition IDs and incompatible duplicate transition definitions are reported using the existing transition contract.
- Route Interaction selectors that can both match the same exact query are reported as ambiguous even when they are not byte-identical duplicate selectors.
- House-door analysis is scoped by exact `houseId` plus `houseDoorId` where house semantics are required.
- All outputs are deterministic, provenance-pinned, create-new/no-clobber and fail closed on truncated/missing/stale required evidence.
- Focused semantic, schema and output-safety tests plus relevant OTBM/AI Agent workflows pass.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T17:35:00+02:00
head: f3d850109e075368f04330b67230563c5332dc46
branch: feat/otbm-qa-013-identifier-integrity-20260722
pr: none
status: implementing
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - tools/ai-agent/otbm_identifier_integrity.py
  - tools/ai-agent/otbm_identifier_integrity_tool.py
  - tools/ai-agent/test_otbm_identifier_integrity.py
  - tools/ai-agent/test_otbm_identifier_integrity_output_safety.py
  - tools/ai-agent/test_otbm_identifier_integrity_schema.py
  - docs/ai-agent/OTBM_IDENTIFIER_INTEGRITY.md
  - docs/ai-agent/OTBM_IDENTIFIER_INTEGRITY_POLICY.schema.json
  - docs/ai-agent/OTBM_IDENTIFIER_INTEGRITY.schema.json
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
  - docs/agents/tasks/active/CAN-20260722-otbm-qa-013-identifier-selector-integrity.md
proven:
  - QA-012 feature PR 717 and lifecycle PR 721 are merged and complete; lifecycle squash merge is f3d850109e075368f04330b67230563c5332dc46.
  - Fresh QA-013 searches found no existing QA-013 task and no open identifier/selector collision PR.
  - World Index is the canonical exact placement/mechanic source and exposes actionId, uniqueId, houseDoorId, teleport destination, position, tileIndex and houseId without reparsing OTBM.
  - Script Resolution already preserves conflicting, unresolved, partially-resolved and referenced-only identifier/placement evidence and must be consumed rather than reimplemented.
  - Reachability transition parsing already rejects duplicate transition IDs and validates exact source/destination semantics.
  - Route Interaction Registry rejects exact duplicate selectors, while its resolver may still match multiple non-identical overlapping selectors; such overlap is valid QA-013 ambiguity evidence.
derived:
  - QA-013 can be implemented as a fail-closed evidence composer plus reviewed uniqueness/reuse policy rather than a new scanner or resolver.
unknown:
  - Intentional identifier reuse cannot be inferred from repetition alone; unreviewed reuse remains review-required unless exact conflict evidence or reviewed policy closes it.
conflicts: []
first_failure:
  marker: none
  evidence: No live-state, overlap or ownership blocker was found during fresh QA-013 preflight.
rejected_hypotheses:
  - Treating every repeated AID or itemId as a defect.
  - Rebuilding Script Resolution or transition parsing inside QA-013.
  - Inferring incompatible mechanic roles from names, proximity or source location.
changed_paths:
  - docs/agents/tasks/active/CAN-20260722-otbm-qa-013-identifier-selector-integrity.md
validation:
  - command: post-QA-012 live main and overlap preflight
    result: PASS
    evidence: main f3d850109e075368f04330b67230563c5332dc46; no competing QA-013 task/PR; canonical reuse boundaries confirmed.
blockers: []
next_action: Open the draft QA-013 PR, bind this task record to it, then implement the smallest deterministic policy and evidence-composition contract with focused tests before shared-doc updates.
```
