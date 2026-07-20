---
task_id: CAN-20260720-otbm-e2e-009-candidate-map-physical-validation
program_id: CAN-PROGRAM-OTBM-E2E-ROUTING
coordination_id: OTBM-E2E-009
status: review
agent: "GPT-5.5 Thinking"
branch: feat/otbm-e2e-009-candidate-map-physical-validation
base_branch: main
created: 2026-07-20
updated: 2026-07-21
last_verified_commit: "394238eb1ee7a810d8893a5489c30851e51d3720"
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
- [ ] Pass exact-final-head checks after the already-applied `ci:final-gate`, squash merge and lifecycle archive.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T00:58:00Z
head: 394238eb1ee7a810d8893a5489c30851e51d3720
branch: feat/otbm-e2e-009-candidate-map-physical-validation
pr: 646
status: validating
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
  - OTBM-E2E-008 feature PR 643 and lifecycle PR 645 are merged and archived before OTBM-E2E-009
  - the canonical repair materialization pipeline supplies create-new candidate and exact Map Quality Gate evidence while preserving the source map
  - the bridge validates exact source candidate pipeline Semantic Diff and OTBM-E2E-008 selection hashes before physical execution
  - selected scenario manifests are rehashed against OTBM-E2E-008 and only selected scenarios are delegated to the existing Physical E2E runner
  - candidate execution uses a disposable repository copy under artifacts and never overwrites an active datapack or source production map
  - existing prepare_otbm_route.py rebuilds candidate World Index evidence and remains the only route preparation pathfinder consumer
  - transient candidate landmark provenance requires complete non-truncated full-index diff evidence proving selected reviewed anchors unchanged otherwise an exact reviewed candidate registry is required
  - existing run_physical_e2e.sh is reused unchanged from the disposable repository and retained map.sha256 must equal the candidate SHA
  - local focused candidate bridge suite passed 13 tests and representative validate-only output passed the new JSON Schema
  - pre-final head 394238eb1ee7a810d8893a5489c30851e51d3720 passed Agent Task Ownership run 29785240009 CI run 29785240117 OTBM Map Tools run 29785240003 and AI Agent Tools run 29785239965
  - AI Agent Tools current-head unit-test discovery executes the focused candidate bridge suite through one thin wrapper without duplicating test logic
  - PR 646 changes exactly seven bounded files and its MODULE_CATALOG diff contains only the review date OTBM-E2E-008 merged status and OTBM-E2E-009 registration
  - current main drift before final checkpoint consists of three unrelated Oteryn documentation files with no overlap against the seven OTBM-E2E-009 paths
  - PR 646 has no submitted reviews review threads or comments at the pre-final audit point
  - ci:final-gate was applied before this final checkpoint commit
  - no candidate-specific change was made to server_selection.py run_physical_e2e.sh or the Universal Agent E2E workflow

derived:
  - the smallest safe runtime injection surface is a disposable repository copy rather than an arbitrary datapack override in the existing runner
  - exact non-impact can suppress only OTBM-aware scenarios represented by OTBM-E2E-008 and never unrelated suites or general gameplay validation
unknown:
  - exact live branch head created by this final checkpoint commit and its exact-final-head workflow conclusions
  - final ready-state CI conclusion
  - final feature and lifecycle merge SHAs
conflicts: []
first_failure:
  marker: none
  evidence: no unresolved implementation or validation failure remains before exact-final-head validation
rejected_hypotheses:
  - build another OTBM parser writer World Index pathfinder Physical E2E runner or workflow: existing infrastructure is authoritative
  - add candidate runtime overrides to server_selection.py and run_physical_e2e.sh: the disposable repository copy preserves existing runner semantics with a smaller surface
  - deploy or overwrite the source map or active datapack: candidate execution remains isolated under artifacts and is removed after execution
  - run every Physical E2E scenario unconditionally: OTBM-E2E-008 impacted selection is the required selection bridge
changed_paths:
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260720-otbm-e2e-009-candidate-map-physical-validation.md
  - docs/ai-agent/OTBM_CANDIDATE_PHYSICAL_VALIDATION.md
  - docs/ai-agent/OTBM_CANDIDATE_PHYSICAL_VALIDATION.schema.json
  - tests/e2e/test_otbm_candidate_physical_validation.py
  - tools/ai-agent/test_otbm_candidate_physical_validation.py
  - tools/e2e/otbm_candidate_physical_validation.py
validation:
  - command: local python -m unittest -v tests/e2e/test_otbm_candidate_physical_validation.py
    result: PASS
    evidence: 13 focused tests cover exact evidence chain mismatch fail-closed selection completeness and disposable runtime copy confinement
  - command: local jsonschema validation of representative validate-only output
    result: PASS
    evidence: representative canary-otbm-candidate-physical-validation-v1 output validated against the published schema
  - command: Agent Task Ownership run 29785240009
    result: PASS
    evidence: pre-final head passed ownership and checkpoint governance
  - command: CI run 29785240117
    result: PASS
    evidence: pre-final head passed repository CI
  - command: OTBM Map Tools run 29785240003
    result: PASS
    evidence: pre-final head passed OTBM schema and focused tooling workflow
  - command: AI Agent Tools run 29785239965
    result: PASS
    evidence: pre-final head passed AI agent tools including focused candidate bridge discovery
blockers: []
next_action: Verify the exact live head created by this final checkpoint commit and exact-head Ownership CI AI Agent Tools OTBM Map Tools and Universal Agent E2E; if green audit main overlap and review state, mark PR 646 ready, require ready-state CI success, squash merge with expected head, then archive lifecycle.
```
