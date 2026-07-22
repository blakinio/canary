---
task_id: CAN-20260722-otbm-qa-013-identifier-selector-integrity
program_id: CAN-PROGRAM-OTBM
status: ready
agent: "GPT-5.6 Thinking"
branch: feat/otbm-qa-013-identifier-integrity-20260722
base_branch: main
created: 2026-07-22
updated: 2026-07-22
last_verified_commit: "6ceb02385c8c7609b1b32c9073dad419f22f3f89"
risk: medium
related_issue: ""
related_pr: "724"
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

READY — bounded QA-013 feature implementation is complete on draft PR #724. `ci:final-gate` was applied before this final checkpoint commit; no further feature-branch commits are permitted. Merge and lifecycle closure remain pending exact-final evidence.

## Goal

Provide deterministic read-only evidence for identifier and selector conflicts without treating ordinary repeated AIDs/item IDs as defects and without rebuilding canonical map, script, transition or route-interaction logic.

## Delivered

- Added reviewed `canary-otbm-identifier-integrity-policy-v1` and deterministic `canary-otbm-identifier-integrity-v1` contracts.
- Reused canonical World Index mechanic placements for exact AID/UID/house-door inventory and house scope; no OTBM parser or scanner was added.
- Reused existing Script Resolution aggregate evidence; `conflicting` remains conflict while `unresolved`, `partially-resolved` and `referenced-only` remain unresolved evidence.
- Reused the existing transition parser contract and reports duplicate transition IDs without creating a second transition validator.
- Reused the reviewed Route Interaction Registry and identifies non-identical reviewed mechanic selectors that can match the same exact witness query.
- Added reviewed `unique` versus `reviewed-reuse` policy; repetition without reviewed intent or exact conflict evidence remains `review-required`.
- Added exact reviewed placement-role compatibility evidence for incompatible-role conflicts without inferring roles from names, sprites, proximity or source location.
- House-door uniqueness/reuse expectations require exact `houseId + houseDoorId` scope.
- Added stable-input, exact-provenance, create-new/no-clobber CLI with symlink/input-output/hard-link protections and atomic overwrite.
- Hardened Route Interaction Registry consumption so its internal source-map, World Index and optional transition/script provenance must match the same evidence set.
- Added focused semantic, schema and output-safety tests plus dedicated documentation.

## Explicit proof boundary

- Repeated AIDs or item IDs are not automatically defects.
- Static identifier/selector evidence does not prove runtime behavior, player intent or global uniqueness outside the reviewed scope.
- No Lua/runtime execution, map/datapack mutation, repair recommendation or automatic identifier renumbering is performed.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T18:10:00+02:00
head: 6ceb02385c8c7609b1b32c9073dad419f22f3f89
branch: feat/otbm-qa-013-identifier-integrity-20260722
pr: 724
status: ready
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
  - docs/agents/tasks/active/CAN-20260722-otbm-qa-013-identifier-selector-integrity.md
proven:
  - QA-012 feature PR 717 and lifecycle PR 721 are merged and complete; lifecycle squash merge is f3d850109e075368f04330b67230563c5332dc46.
  - Fresh QA-013 searches found no existing QA-013 task and no competing open identifier/selector collision PR.
  - World Index is reused as the canonical exact placement/mechanic source; QA-013 adds no OTBM parser or scanner.
  - Script Resolution conflicting evidence is preserved as conflict while unresolved/partially-resolved/referenced-only evidence remains unresolved.
  - Existing transition parsing is reused for exact transition ID/source/destination semantics; duplicate IDs are reported without a second transition resolver.
  - Route Interaction Registry validation is reused; QA-013 additionally proves non-identical mechanic-selector overlap only through an exact witness query compatible with both selectors.
  - Reviewed unique expectations fail on multiple exact in-scope placements; reviewed-reuse remains non-conflicting; unreviewed repetition remains review-required.
  - House-door expectations are scoped by exact houseId plus houseDoorId.
  - Reviewed incompatible mechanic-role evidence requires exact placementOrdinal and namespace/value bindings.
  - CLI pins exact source-map and World Index provenance plus optional evidence-file hashes and validates internal Route Interaction Registry provenance against the same evidence set.
  - Pre-final CI 29935481525, Agent Task Ownership 29935481231, OTBM Map Tools 29935483454 and AI Agent Tools 29935483455 passed on provenance-hardened head 6ceb02385c8c7609b1b32c9073dad419f22f3f89.
  - PR 724 pre-final review audit found zero inline review threads and zero review submissions; main remained f3d850109e075368f04330b67230563c5332dc46.
  - ci:final-gate was applied to PR 724 before this final checkpoint commit.
derived:
  - QA-013 is ready for immutable exact-final-head validation and merge without further feature changes.
unknown:
  - Intentional identifier reuse cannot be inferred from repetition alone; unreviewed reuse remains review-required unless exact conflict evidence or reviewed policy closes it.
  - MODULE_CATALOG.md and CHANGELOG.md shared-path entries were not modified in the bounded feature branch; delivered public contracts are documented in OTBM_IDENTIFIER_INTEGRITY.md, the two JSON schemas and task metadata.
conflicts: []
first_failure:
  marker: none
  evidence: No unresolved feature, provenance, ownership, focused-test or pre-final validation failure remains.
rejected_hypotheses:
  - Treating every repeated AID or itemId as a defect.
  - Rebuilding Script Resolution, transition parsing or Route Interaction resolution inside QA-013.
  - Inferring incompatible mechanic roles from names, sprites, proximity or source location.
changed_paths:
  - docs/agents/tasks/active/CAN-20260722-otbm-qa-013-identifier-selector-integrity.md
  - docs/ai-agent/OTBM_IDENTIFIER_INTEGRITY.md
  - docs/ai-agent/OTBM_IDENTIFIER_INTEGRITY.schema.json
  - docs/ai-agent/OTBM_IDENTIFIER_INTEGRITY_POLICY.schema.json
  - tools/ai-agent/otbm_identifier_integrity.py
  - tools/ai-agent/otbm_identifier_integrity_tool.py
  - tools/ai-agent/test_otbm_identifier_integrity.py
  - tools/ai-agent/test_otbm_identifier_integrity_output_safety.py
  - tools/ai-agent/test_otbm_identifier_integrity_schema.py
validation:
  - command: GitHub Actions CI run 29935481525
    result: PASS
    evidence: pre-final repository CI passed on provenance-hardened head 6ceb02385c8c7609b1b32c9073dad419f22f3f89.
  - command: GitHub Actions Agent Task Ownership run 29935481231
    result: PASS
    evidence: pre-final ownership validation passed.
  - command: GitHub Actions OTBM Map Tools run 29935483454
    result: PASS
    evidence: schema JSON validation and focused OTBM tests passed.
  - command: GitHub Actions AI Agent Tools run 29935483455
    result: PASS
    evidence: AI-agent unit tests and repository audit pipeline passed.
blockers: []
next_action: Make no further commits; verify exact-final-head CI, Ownership, OTBM Map Tools and AI Agent Tools plus review/mergeability on PR 724, then mark ready, enable auto-merge, confirm squash merge and complete lifecycle-only active-to-archive closure before QA-014 preflight.
```
