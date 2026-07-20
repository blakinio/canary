---
task_id: CAN-20260720-otbm-e2e-009-candidate-map-physical-validation
program_id: CAN-PROGRAM-OTBM-E2E-ROUTING
coordination_id: OTBM-E2E-009
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/otbm-e2e-009-candidate-map-physical-validation
base_branch: main
created: 2026-07-20
updated: 2026-07-20
last_verified_commit: "6b1bbadf5c9fdc9c4b5831dcfbdef9c9ed894b3d"
risk: high
related_issue: ""
related_pr: ""
depends_on:
  - merged and archived OTBM-E2E-008
  - existing approved bounded repair or materialization pipeline
  - existing static map validation and Semantic OTBM Diff
  - existing canary-otbm-e2e-impacted-selection-v1
  - existing Universal Physical E2E lifecycle
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260720-otbm-e2e-009-candidate-map-physical-validation.md
  shared: []
  read_only:
    - docs/agents/programs/OTBM_E2E_ROUTE_INTEGRATION_PROGRAM.md
    - docs/ai-agent/OTBM_REPAIR_MATERIALIZATION_PIPELINE.md
    - docs/ai-agent/OTBM_SEMANTIC_DIFF.md
    - docs/ai-agent/OTBM_E2E_IMPACTED_SELECTION.md
    - tools/e2e/**
modules_touched: []
reuses:
  - approved bounded repair/materialization outputs
  - static map validation
  - canary-otbm-semantic-diff-v1
  - canary-otbm-e2e-impacted-selection-v1
  - Universal Physical E2E
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Deliver OTBM-E2E-009 as the bounded candidate-map physical validation consumer: approved repair/materialization output to candidate map copy, full static validation, Semantic OTBM Diff, impacted route selection, disposable Canary on the candidate map, and only the selected existing Physical E2E scenarios. Never deploy or overwrite the source/production map.

# Acceptance criteria

- [ ] Reuse existing approved bounded repair/materialization output; do not add another map writer.
- [ ] Validate the candidate map through existing static validation contracts before physical execution.
- [ ] Produce or consume exact Semantic OTBM Diff between source and candidate maps.
- [ ] Reuse OTBM-E2E-008 impacted selection; do not run all physical scenarios when exact non-impact is proven.
- [ ] Run selected scenarios only through the existing disposable Universal Physical E2E lifecycle.
- [ ] Keep source and candidate maps distinct and never deploy or overwrite production/source map state.
- [ ] Preserve exact map/index/route provenance and fail closed on stale, missing or ambiguous evidence.
- [ ] Determine the smallest dependency-safe implementation surface from live repository evidence before claiming additional owned paths.
- [ ] Add focused validation and documentation only where a new reusable interface is actually required.
- [ ] Apply `ci:final-gate` before final checkpoint commit, pass exact-final-head checks, squash merge and lifecycle archive.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-20T21:55:00Z
head: 6b1bbadf5c9fdc9c4b5831dcfbdef9c9ed894b3d
branch: feat/otbm-e2e-009-candidate-map-physical-validation
pr: 0
status: investigating
context_routes:
  - agent-governance
  - otbm
  - universal-e2e
owned_paths:
  - docs/agents/tasks/active/CAN-20260720-otbm-e2e-009-candidate-map-physical-validation.md
proven:
  - OTBM-E2E-008 feature PR 643 merged as 944c2af02b0aa6619c78fcaf412d773d9aa6feb1 and lifecycle PR 645 merged as 6b1bbadf5c9fdc9c4b5831dcfbdef9c9ed894b3d before this task was claimed
  - no existing branch open PR or indexed active task matching OTBM-E2E-009 was found before task claim
  - OTBM-E2E-009 must reuse the approved bounded repair or materialization pipeline static validation Semantic Diff OTBM-E2E-008 impacted selection and Universal Physical E2E
  - source and candidate maps must remain distinct and production or source maps must never be overwritten or deployed by this flow
derived:
  - the first implementation step must be a live dependency and ownership preflight that identifies the smallest missing bridge instead of creating a second orchestration stack
unknown:
  - final draft PR number
  - exact smallest implementation surface and additional owned paths
  - candidate-map fixture or approved artifact suitable for focused validation
  - final feature and lifecycle merge SHAs
conflicts: []
first_failure:
  marker: none
  evidence: no OTBM-E2E-009 implementation has started
rejected_hypotheses:
  - build another OTBM parser writer World Index pathfinder or E2E runner: existing infrastructure is authoritative
  - deploy or overwrite the source map during candidate validation: candidate execution must remain disposable and isolated
  - run every Physical E2E scenario unconditionally: OTBM-E2E-008 impacted selection is the required selection bridge
changed_paths:
  - docs/agents/tasks/active/CAN-20260720-otbm-e2e-009-candidate-map-physical-validation.md
validation: []
blockers: []
next_action: Open the draft PR, update this checkpoint with its exact PR number, validate the checkpoint, then perform the live dependency and ownership preflight to identify the smallest missing candidate-map validation bridge.
```
