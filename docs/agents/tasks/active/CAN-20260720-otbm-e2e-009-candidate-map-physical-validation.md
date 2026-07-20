---
task_id: CAN-20260720-otbm-e2e-009-candidate-map-physical-validation
program_id: CAN-PROGRAM-OTBM-E2E-ROUTING
coordination_id: OTBM-E2E-009
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/otbm-e2e-009-candidate-map-physical-validation
base_branch: main
created: 2026-07-20
updated: 2026-07-21
last_verified_commit: "6ebcce5605227cd9c7af7e5ad5ef9c2082a58d8b"
risk: high
related_issue: ""
related_pr: "646"
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
    - tools/e2e/otbm_candidate_physical_validation.py
    - tests/e2e/test_otbm_candidate_physical_validation.py
    - tools/ai-agent/test_otbm_candidate_physical_validation.py
    - docs/ai-agent/OTBM_CANDIDATE_PHYSICAL_VALIDATION.md
    - docs/ai-agent/OTBM_CANDIDATE_PHYSICAL_VALIDATION.schema.json
  shared:
    - docs/agents/MODULE_CATALOG.md
  read_only:
    - docs/agents/programs/OTBM_E2E_ROUTE_INTEGRATION_PROGRAM.md
    - docs/ai-agent/OTBM_REPAIR_MATERIALIZATION_PIPELINE.md
    - docs/ai-agent/OTBM_SEMANTIC_DIFF.md
    - docs/ai-agent/OTBM_E2E_IMPACTED_SELECTION.md
    - docs/ai-agent/OTBM_SEMANTIC_LANDMARKS.json
    - tools/e2e/prepare_otbm_route.py
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/server_selection.py
    - tools/e2e/run_physical_e2e.sh
    - .github/workflows/universal-agent-e2e.yml
modules_touched:
  - OTBM candidate-map Physical E2E validation bridge
reuses:
  - canary-otbm-repair-materialization-pipeline-v1
  - canary-otbm-map-quality-v1
  - canary-otbm-semantic-diff-v1
  - canary-otbm-e2e-impacted-selection-v1
  - existing exact-map route preparation and preflight
  - existing Universal Physical E2E runner
public_interfaces:
  - canary-otbm-candidate-physical-validation-v1
cross_repo_tasks: []
---

# Goal

Deliver OTBM-E2E-009 as the bounded candidate-map physical validation consumer: approved repair/materialization output to candidate map copy, full static validation, Semantic OTBM Diff, impacted route selection, disposable Canary on the candidate map, and only the selected existing Physical E2E scenarios. Never deploy or overwrite the source/production map.

# Acceptance criteria

- [x] Reuse existing approved bounded repair/materialization output; do not add another map writer.
- [x] Validate the candidate map through existing static validation contracts before physical execution.
- [x] Produce or consume exact Semantic OTBM Diff between source and candidate maps.
- [x] Reuse OTBM-E2E-008 impacted selection; do not run all physical scenarios when exact non-impact is proven.
- [x] Run selected scenarios only through the existing disposable Universal Physical E2E lifecycle.
- [x] Keep source and candidate maps distinct and never deploy or overwrite production/source map state.
- [x] Preserve exact map/index/route provenance and fail closed on stale, missing or ambiguous evidence.
- [x] Determine the smallest dependency-safe implementation surface from live repository evidence before claiming additional owned paths.
- [x] Add focused validation and documentation only where a new reusable interface is actually required.
- [ ] Apply `ci:final-gate` before final checkpoint commit, pass exact-final-head checks, squash merge and lifecycle archive.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T00:35:00Z
head: 6ebcce5605227cd9c7af7e5ad5ef9c2082a58d8b
branch: feat/otbm-e2e-009-candidate-map-physical-validation
pr: 646
status: implementing
context_routes:
  - agent-governance
  - otbm
  - universal-e2e
owned_paths:
  - docs/agents/tasks/active/CAN-20260720-otbm-e2e-009-candidate-map-physical-validation.md
  - tools/e2e/otbm_candidate_physical_validation.py
  - tests/e2e/test_otbm_candidate_physical_validation.py
  - tools/ai-agent/test_otbm_candidate_physical_validation.py
  - docs/ai-agent/OTBM_CANDIDATE_PHYSICAL_VALIDATION.md
  - docs/ai-agent/OTBM_CANDIDATE_PHYSICAL_VALIDATION.schema.json
  - docs/agents/MODULE_CATALOG.md
proven:
  - OTBM-E2E-008 feature PR 643 merged as 944c2af02b0aa6619c78fcaf412d773d9aa6feb1 and lifecycle PR 645 merged as 6b1bbadf5c9fdc9c4b5831dcfbdef9c9ed894b3d before this task was claimed
  - initial checkpoint head c2c5317eb7c3f76f558e41f56c4e6a0aa7ee79ab passed Agent Task Ownership run 29781959334 and CI run 29781959514
  - the canonical repair materialization pipeline already supplies create-new candidate and exact Map Quality Gate evidence while preserving the source map
  - the implemented bridge pins source candidate pipeline Semantic Diff and OTBM-E2E-008 selection hashes before any physical execution
  - selected scenario manifests are rehashed against OTBM-E2E-008 and only selected scenarios are delegated to the existing Physical E2E runner
  - candidate execution uses a disposable repository copy under artifacts and replaces only the logical map in that copy so active datapacks and source maps remain untouched
  - existing prepare_otbm_route.py rebuilds candidate World Index evidence and remains the only route preparation pathfinder consumer
  - transient candidate landmark provenance is allowed only from complete non-truncated full-index diff evidence proving selected reviewed anchors unchanged otherwise an exact reviewed candidate registry is required
  - existing run_physical_e2e.sh is reused unchanged from the disposable repository and retained map.sha256 must equal the candidate SHA
  - local focused candidate bridge suite passed 13 tests and representative validate-only output passed the new JSON Schema
  - implementation head a9c9281fa8ac8f350ac2d8a0a98caf7c9875fb85 passed CI run 29784480701 Agent Task Ownership run 29784480574 OTBM Map Tools run 29784480520 and AI Agent Tools run 29784480467 while Universal Agent E2E remained in progress
  - a thin AI Agent Tools discovery wrapper now executes the focused tests in repository CI without duplicating test logic
derived:
  - no change to server_selection.py run_physical_e2e.sh or Universal workflow is required because the unchanged runner can execute inside a disposable repository copy
  - candidate runtime isolation is stronger than an arbitrary datapack override because existing runner selection semantics stay unchanged and no active datapack receives the candidate
unknown:
  - exact workflow conclusions on the current checkpoint head after adding focused-test discovery
  - final main synchronization and review state before final gate
  - exact final feature and lifecycle merge SHAs
conflicts: []
first_failure:
  marker: none
  evidence: no implementation failure has been observed; the preflight-only runtime override hypothesis was rejected before modifying existing runner surfaces
rejected_hypotheses:
  - build another OTBM parser writer World Index pathfinder or E2E runner: existing infrastructure is authoritative
  - create another Physical E2E workflow: existing Universal workflow and runner remain the execution boundary
  - add candidate runtime overrides to server_selection.py and run_physical_e2e.sh: a disposable repository copy preserves existing runner semantics with a smaller implementation surface
  - deploy or overwrite the source map or active datapack: candidate execution is isolated under artifacts and deleted after execution
  - run every Physical E2E scenario unconditionally: OTBM-E2E-008 impacted selection is the required selection bridge
changed_paths:
  - docs/agents/tasks/active/CAN-20260720-otbm-e2e-009-candidate-map-physical-validation.md
  - tools/e2e/otbm_candidate_physical_validation.py
  - tests/e2e/test_otbm_candidate_physical_validation.py
  - tools/ai-agent/test_otbm_candidate_physical_validation.py
  - docs/ai-agent/OTBM_CANDIDATE_PHYSICAL_VALIDATION.md
  - docs/ai-agent/OTBM_CANDIDATE_PHYSICAL_VALIDATION.schema.json
validation:
  - command: local python -m unittest -v tests/e2e/test_otbm_candidate_physical_validation.py
    result: PASS
    evidence: 13 focused tests cover exact evidence-chain mismatch fail-closed selection completeness and disposable runtime copy confinement
  - command: local jsonschema validation of representative validate-only output
    result: PASS
    evidence: generated canary-otbm-candidate-physical-validation-v1 output validated against OTBM_CANDIDATE_PHYSICAL_VALIDATION.schema.json
  - command: CI run 29784480701
    result: PASS
    evidence: implementation head passed repository CI
  - command: Agent Task Ownership run 29784480574
    result: PASS
    evidence: implementation head passed ownership and checkpoint governance before focused-test wrapper claim
  - command: OTBM Map Tools run 29784480520
    result: PASS
    evidence: implementation head passed OTBM schema and focused tooling validation
  - command: AI Agent Tools run 29784480467
    result: PASS
    evidence: implementation head passed AI agent tooling validation before focused-test discovery wrapper was added
blockers: []
next_action: Update MODULE_CATALOG for the merged OTBM-E2E-008 selector and active OTBM-E2E-009 bridge, then verify current-head Ownership CI AI Agent Tools OTBM Map Tools and Universal Agent E2E before final-gate checkpointing.
```
