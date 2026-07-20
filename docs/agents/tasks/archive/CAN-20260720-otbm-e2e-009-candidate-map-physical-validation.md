---
task_id: CAN-20260720-otbm-e2e-009-candidate-map-physical-validation
program_id: CAN-PROGRAM-OTBM-E2E-ROUTING
coordination_id: OTBM-E2E-009
status: completed
agent: "GPT-5.5 Thinking"
branch: feat/otbm-e2e-009-candidate-map-physical-validation
base_branch: main
created: 2026-07-20
updated: 2026-07-20T23:44:23Z
completed: 2026-07-20T23:44:23Z
last_verified_commit: "4aea1e43d4116976f11ee34e498b2e63155d7741"
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

Deliver OTBM-E2E-009 as the bounded candidate-map physical validation consumer over existing repair/materialization, static validation, Semantic Diff, impacted selection and Universal Physical E2E infrastructure without deploying or overwriting the source map.

# Completion

- [x] Reused approved create-new repair/materialization evidence and existing Map Quality Gate.
- [x] Reused exact Semantic OTBM Diff and OTBM-E2E-008 impacted selection.
- [x] Executed selected scenarios only through existing route preparation and Universal Physical E2E boundaries.
- [x] Kept candidate runtime state disposable under `artifacts/`; active datapacks and source/production maps are not overwritten.
- [x] Preserved exact map/index/route provenance and fail-closed stale, missing or ambiguous evidence.
- [x] Added focused tests, schema, documentation and module catalogue registration.
- [x] Passed exact-final-head and ready-state CI gates and squash-merged PR #646.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-20T23:44:23Z
head: e16c01194b2bbfc82f2e0db3cd6826c5badb16fb
branch: feat/otbm-e2e-009-candidate-map-physical-validation
pr: 646
status: ready
context_routes:
  - agent-governance
  - otbm
  - universal-e2e
owned_paths:
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/archive/CAN-20260720-otbm-e2e-009-candidate-map-physical-validation.md
  - docs/ai-agent/OTBM_CANDIDATE_PHYSICAL_VALIDATION.md
  - docs/ai-agent/OTBM_CANDIDATE_PHYSICAL_VALIDATION.schema.json
  - tests/e2e/test_otbm_candidate_physical_validation.py
  - tools/ai-agent/test_otbm_candidate_physical_validation.py
  - tools/e2e/otbm_candidate_physical_validation.py
proven:
  - OTBM-E2E-008 feature PR 643 and lifecycle PR 645 were merged and archived before OTBM-E2E-009
  - the bridge reuses approved create-new repair or materialization evidence and exact Map Quality Gate evidence without adding another OTBM writer
  - exact source candidate pipeline Semantic Diff and OTBM-E2E-008 selection hashes are validated before physical execution
  - selected scenario manifests are rehashed and only selected scenarios are delegated to the existing Physical E2E runner
  - candidate execution uses a disposable repository copy under artifacts and never overwrites an active datapack or source production map
  - existing prepare_otbm_route.py remains the route preparation path and existing run_physical_e2e.sh remains the Physical E2E runner
  - transient candidate landmark provenance requires complete non-truncated full-index diff proof of unchanged reviewed anchors or an explicit reviewed candidate registry
  - local focused candidate bridge suite passed 13 tests and representative validate-only output passed the published JSON Schema
  - exact final feature head e16c01194b2bbfc82f2e0db3cd6826c5badb16fb passed Ownership 29785447831 CI 29785447956 AI Agent Tools 29785447935 OTBM Map Tools 29785447809 and Universal Agent E2E 29785448031
  - final audit found seven bounded feature files no review submissions no review threads no comments and only unrelated Oteryn main drift
  - ready-state full CI run 29787219325 passed on unchanged exact final feature head
  - PR 646 was squash-merged as 4aea1e43d4116976f11ee34e498b2e63155d7741
  - no candidate-specific change was made to server_selection.py run_physical_e2e.sh or the Universal Agent E2E workflow
  - no specific repaired candidate artifact chain was claimed as physically gameplay-validated by this feature task

derived:
  - the smallest safe runtime injection surface is a disposable repository copy rather than an arbitrary datapack override in the existing runner
  - exact non-impact can suppress only OTBM-aware scenarios represented by OTBM-E2E-008 and never unrelated suites or general gameplay validation
unknown:
  - lifecycle archive merge SHA
conflicts: []
first_failure:
  marker: none
  evidence: no unresolved implementation or validation failure remained at feature merge
rejected_hypotheses:
  - build another OTBM parser writer World Index pathfinder Physical E2E runner or workflow: existing infrastructure is authoritative
  - add candidate runtime overrides to server_selection.py and run_physical_e2e.sh: disposable repository isolation preserves existing runner semantics with a smaller surface
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
    evidence: 13 focused candidate bridge tests passed
  - command: local jsonschema validation of representative validate-only output
    result: PASS
    evidence: representative output validated against OTBM_CANDIDATE_PHYSICAL_VALIDATION.schema.json
  - command: Agent Task Ownership run 29785447831
    result: PASS
    evidence: exact final feature head passed ownership and checkpoint governance
  - command: CI run 29785447956
    result: PASS
    evidence: exact final feature head passed repository CI
  - command: AI Agent Tools run 29785447935
    result: PASS
    evidence: exact final feature head passed AI agent tooling including focused candidate bridge discovery
  - command: OTBM Map Tools run 29785447809
    result: PASS
    evidence: exact final feature head passed OTBM schema and focused map tooling validation
  - command: Universal Agent E2E run 29785448031
    result: PASS
    evidence: exact final feature head passed existing physical E2E lifecycle regression
  - command: ready-state CI run 29787219325
    result: PASS
    evidence: unchanged exact final feature head passed full ready-state CI and Required gate
blockers: []
next_action: Confirm OTBM-E2E route integration programme completion on current main and close the programme or open a separately approved follow-up only from new live evidence.
```

## Automated lifecycle completion

- Feature PR: #646.
- Feature head: `e16c01194b2bbfc82f2e0db3cd6826c5badb16fb`.
- Merge commit: `4aea1e43d4116976f11ee34e498b2e63155d7741`.
- Merged at: `2026-07-20T23:44:23Z`.
- This record was moved from `tasks/active` by the post-merge lifecycle process.
