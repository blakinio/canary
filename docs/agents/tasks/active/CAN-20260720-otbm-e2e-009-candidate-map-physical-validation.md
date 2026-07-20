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
last_verified_commit: "c2c5317eb7c3f76f558e41f56c4e6a0aa7ee79ab"
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
    - tools/e2e/server_selection.py
    - tools/e2e/run_physical_e2e.sh
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

- [ ] Reuse existing approved bounded repair/materialization output; do not add another map writer.
- [ ] Validate the candidate map through existing static validation contracts before physical execution.
- [ ] Produce or consume exact Semantic OTBM Diff between source and candidate maps.
- [ ] Reuse OTBM-E2E-008 impacted selection; do not run all physical scenarios when exact non-impact is proven.
- [ ] Run selected scenarios only through the existing disposable Universal Physical E2E lifecycle.
- [ ] Keep source and candidate maps distinct and never deploy or overwrite production/source map state.
- [ ] Preserve exact map/index/route provenance and fail closed on stale, missing or ambiguous evidence.
- [x] Determine the smallest dependency-safe implementation surface from live repository evidence before claiming additional owned paths.
- [ ] Add focused validation and documentation only where a new reusable interface is actually required.
- [ ] Apply `ci:final-gate` before final checkpoint commit, pass exact-final-head checks, squash merge and lifecycle archive.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T00:05:00Z
head: c2c5317eb7c3f76f558e41f56c4e6a0aa7ee79ab
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
  - tools/e2e/server_selection.py
  - tools/e2e/run_physical_e2e.sh
  - docs/ai-agent/OTBM_CANDIDATE_PHYSICAL_VALIDATION.md
  - docs/ai-agent/OTBM_CANDIDATE_PHYSICAL_VALIDATION.schema.json
  - docs/agents/MODULE_CATALOG.md
proven:
  - OTBM-E2E-008 feature PR 643 merged as 944c2af02b0aa6619c78fcaf412d773d9aa6feb1 and lifecycle PR 645 merged as 6b1bbadf5c9fdc9c4b5831dcfbdef9c9ed894b3d before this task was claimed
  - branch feat/otbm-e2e-009-candidate-map-physical-validation was created from post-lifecycle main and draft PR 646 was opened before implementation
  - initial checkpoint head c2c5317eb7c3f76f558e41f56c4e6a0aa7ee79ab passed Agent Task Ownership run 29781959334 and CI run 29781959514
  - canonical repair materialization pipeline already publishes a create-new byte-identical candidate only after exact candidate SHA compatible Map Quality Gate success while preserving the source unchanged
  - OTBM-E2E-008 already provides fail-closed exact Semantic Diff to selected or safely-skipped Physical E2E scenario evidence
  - existing Universal Physical E2E already resolves scenarios prepares exact-map OTBM routes starts disposable Canary and controlled OTClient and records runtime map SHA and persistence evidence
  - the missing bridge is candidate-map runtime injection plus exact evidence-chain validation and selected-scenario orchestration rather than another parser writer pathfinder runner or workflow
  - disposable runtime map state can live under repository artifacts with useAnyDatapackFolder enabled so no active datapack or production map must be overwritten
  - candidate follow_route preparation must reuse prepare_otbm_route.py and a transient exact candidate landmark-registry provenance copy only when full-index non-truncated Semantic Diff proves referenced reviewed anchors unchanged
  - if candidate landmark provenance cannot be safely derived an explicitly reviewed candidate registry is required and execution fails closed otherwise
derived:
  - server_selection.py needs a narrow explicit runtime datapack and map override seam while preserving existing scenario behavior by default
  - run_physical_e2e.sh needs only candidate runtime override plumbing and expected map SHA enforcement before server startup
  - the new bridge can validate pipeline diff and impacted-selection pins then execute only selected scenarios through the existing route preparer and physical runner
unknown:
  - whether focused implementation validation will expose additional bounded integration defects
  - exact final feature and lifecycle merge SHAs
conflicts: []
first_failure:
  marker: none
  evidence: no implementation failure has been observed; live preflight identified the missing candidate runtime injection seam
rejected_hypotheses:
  - build another OTBM parser writer World Index pathfinder or E2E runner: existing infrastructure is authoritative
  - create another Physical E2E workflow: existing Universal workflow and runner remain the execution boundary
  - deploy or overwrite the source map during candidate validation: candidate execution must remain disposable and isolated
  - copy candidate OTBM into an active datapack: runtime candidate state belongs under disposable artifacts
  - run every Physical E2E scenario unconditionally: OTBM-E2E-008 impacted selection is the required selection bridge
changed_paths:
  - docs/agents/tasks/active/CAN-20260720-otbm-e2e-009-candidate-map-physical-validation.md
validation:
  - command: Agent Task Ownership run 29781959334
    result: PASS
    evidence: initial active task checkpoint passed ownership governance
  - command: CI run 29781959514
    result: PASS
    evidence: initial active task checkpoint passed repository CI
blockers: []
next_action: Implement and focused-test the bounded candidate-map evidence and runtime-injection bridge on the claimed paths without adding a parser writer pathfinder runner or workflow.
```
