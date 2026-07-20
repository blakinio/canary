---
task_id: CAN-20260720-otbm-e2e-008-semantic-diff-selection
program_id: CAN-PROGRAM-OTBM-E2E-ROUTING
coordination_id: OTBM-E2E-008
status: validating
agent: "GPT-5.5 Thinking"
branch: feat/otbm-e2e-008-semantic-diff-selection
base_branch: main
created: 2026-07-20
updated: 2026-07-20
last_verified_commit: "2d3ff9642abbc8b004c8cf496221273f0da5cc55"
risk: medium
related_issue: ""
related_pr: "643"
depends_on:
  - merged and archived OTBM-E2E-007
  - existing canary-otbm-semantic-diff-v1
  - existing canary-otbm-e2e-route-plan-v1
  - existing Universal Physical E2E scenario manifests
blocks:
  - OTBM-E2E-009
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260720-otbm-e2e-008-semantic-diff-selection.md
    - tools/ai-agent/otbm_e2e_impacted_selection.py
    - tools/ai-agent/test_otbm_e2e_impacted_selection.py
    - docs/ai-agent/OTBM_E2E_IMPACTED_SELECTION.md
    - docs/ai-agent/OTBM_E2E_IMPACTED_SELECTION.schema.json
  shared:
    - docs/agents/MODULE_CATALOG.md
  read_only:
    - docs/agents/programs/OTBM_E2E_ROUTE_INTEGRATION_PROGRAM.md
    - docs/ai-agent/OTBM_SEMANTIC_DIFF.md
    - docs/ai-agent/OTBM_SEMANTIC_DIFF.schema.json
    - docs/ai-agent/OTBM_E2E_ROUTE_PLAN.schema.json
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/pr_scenario_selection.py
    - tests/e2e/scenarios/**
modules_touched:
  - OTBM Semantic Diff impacted Physical E2E selection
reuses:
  - canary-otbm-semantic-diff-v1
  - canary-otbm-e2e-route-plan-v1
  - Universal Physical E2E scenario manifest format
public_interfaces:
  - canary-otbm-e2e-impacted-selection-v1
cross_repo_tasks: []
---

# Goal

Deliver OTBM-E2E-008 as a deterministic fail-closed selector that consumes existing Semantic OTBM Diff evidence and baseline route-plan evidence to identify which route/mechanic Physical E2E scenarios must be rerun after a reviewed map change, without creating another parser, World Index, pathfinder, route planner, E2E runner or workflow.

# Acceptance criteria

- [x] Consume only existing `canary-otbm-semantic-diff-v1` evidence plus reviewed Universal E2E scenario manifests and canonical route-plan evidence.
- [x] Require exact full-index diff evidence before claiming a scenario is non-impacted.
- [x] Require baseline route-plan source-map and World Index provenance to match the Semantic Diff `before` provenance before allowing a skip decision.
- [x] Select a scenario when any exact diff finding position intersects its executed route positions or transition/interaction evidence.
- [x] Fail closed to selecting a scenario when diff findings are truncated, route evidence is missing/malformed/stale, or a finding lacks exact position evidence.
- [x] Keep selected versus safely-skipped decisions explicit and deterministic with bounded reasons and finding IDs.
- [x] Do not execute scenarios, parse OTBM, regenerate paths, or modify maps.
- [x] Add focused tests, schema, documentation and module catalogue entry.
- [ ] Pass exact-final-head required checks after the already-applied `ci:final-gate` label.
- [ ] Complete final review/overlap/mergeability audit, squash merge and lifecycle archive.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-20T21:27:00Z
head: 2d3ff9642abbc8b004c8cf496221273f0da5cc55
branch: feat/otbm-e2e-008-semantic-diff-selection
pr: 643
status: validating
context_routes:
  - agent-governance
  - otbm
  - universal-e2e
owned_paths:
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260720-otbm-e2e-008-semantic-diff-selection.md
  - docs/ai-agent/OTBM_E2E_IMPACTED_SELECTION.md
  - docs/ai-agent/OTBM_E2E_IMPACTED_SELECTION.schema.json
  - tools/ai-agent/otbm_e2e_impacted_selection.py
  - tools/ai-agent/test_otbm_e2e_impacted_selection.py
proven:
  - OTBM-E2E-007 feature PR 639 and lifecycle PR 640 are merged and archived
  - task branch was created from live main 99b9dec84d953d3f200284d0cf193261027650ca and draft PR 643 was opened before substantial implementation
  - no competing open PR branch or active task matching OTBM-E2E-008 was found before task claim
  - the selector consumes existing Semantic Diff scenario manifests and canonical baseline route plans without modifying the existing PR scenario selector Universal runner workflow parser World Index or Reachability pathfinder
  - exact full-index non-truncated diff plus before-map and before-World-Index-compatible complete executable baseline route evidence is required before a scenario may be safely skipped
  - bounded truncated unknown-position missing malformed blocked or stale evidence selects the scenario fail closed instead of claiming non-impact
  - exact route impact includes canonical path and edge positions plus nested reviewed transition and interaction selector positions so adjacent use-target mechanics are covered
  - local focused suite passed 15 tests and representative generated output validated against OTBM_E2E_IMPACTED_SELECTION.schema.json
  - pre-final implementation head 2d3ff9642abbc8b004c8cf496221273f0da5cc55 passed Agent Task Ownership run 29779969320 CI run 29779969506 OTBM Map Tools run 29779969340 and AI Agent Tools run 29779969291
  - MODULE_CATALOG changed by only two additions and one deletion to mark OTBM-E2E-007 merged and register the OTBM-E2E-008 reusable interface
  - current main drift is one unrelated OAM programme-document commit with no overlap against the six OTBM-E2E-008 changed paths and PR 643 is mergeable
  - ci:final-gate was applied to PR 643 before this final checkpoint commit
derived:
  - Semantic Diff can safely suppress a candidate OTBM-aware Physical E2E rerun only when exact complete evidence proves route and mechanic non-impact
  - the initial ownership failure was task metadata only because compile and focused unit tests passed before checkpoint validation failed and corrected ownership runs now pass
unknown:
  - exact live branch head created by this final checkpoint commit and its exact-final-head workflow conclusions
  - final review-ready CI conclusion after draft-to-ready transition
  - final feature and lifecycle merge SHAs
conflicts: []
first_failure:
  marker: checkpoint-pr-null
  evidence: Agent Task Ownership run 29779345222 passed compile and focused unit tests then failed changed active task checkpoint validation while the initial checkpoint still had pr null; corrected checkpoint ownership subsequently passed
rejected_hypotheses:
  - parse or rescan OTBM for impact selection: Semantic Diff is the authoritative change evidence
  - recompute routes during selection: canonical baseline route plans are evidence inputs and Reachability remains the sole pathfinder
  - modify Universal E2E runner or workflow in this task: impacted selection is a bridge evidence contract and execution ownership remains unchanged
  - treat bounded or truncated Semantic Diff as global non-impact proof: incomplete scope or samples fail closed to selection
changed_paths:
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260720-otbm-e2e-008-semantic-diff-selection.md
  - docs/ai-agent/OTBM_E2E_IMPACTED_SELECTION.md
  - docs/ai-agent/OTBM_E2E_IMPACTED_SELECTION.schema.json
  - tools/ai-agent/otbm_e2e_impacted_selection.py
  - tools/ai-agent/test_otbm_e2e_impacted_selection.py
validation:
  - command: local python -m unittest -v test_otbm_e2e_impacted_selection.py
    result: PASS
    evidence: 15 focused tests passed before repository publication
  - command: local jsonschema validation of sample selection output
    result: PASS
    evidence: representative impacted selection output validated against OTBM_E2E_IMPACTED_SELECTION.schema.json
  - command: Agent Task Ownership run 29779969320
    result: PASS
    evidence: pre-final implementation head passed ownership and checkpoint governance
  - command: CI run 29779969506
    result: PASS
    evidence: pre-final implementation head passed repository CI
  - command: OTBM Map Tools run 29779969340
    result: PASS
    evidence: pre-final implementation head passed OTBM schema validation and focused OTBM tests
  - command: AI Agent Tools run 29779969291
    result: PASS
    evidence: pre-final implementation head passed repository AI agent unit tests and tooling validation
blockers: []
next_action: Verify the exact live head created by this final checkpoint commit and all exact-final-head required workflows; if green, audit current main overlap reviews threads comments and mergeability, mark PR 643 ready, require ready-state CI success, squash-merge with expected head, then archive the task lifecycle.
```
