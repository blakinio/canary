---
task_id: CAN-20260720-otbm-e2e-008-semantic-diff-selection
program_id: CAN-PROGRAM-OTBM-E2E-ROUTING
coordination_id: OTBM-E2E-008
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/otbm-e2e-008-semantic-diff-selection
base_branch: main
created: 2026-07-20
updated: 2026-07-20
last_verified_commit: "99b9dec84d953d3f200284d0cf193261027650ca"
risk: medium
related_issue: ""
related_pr: ""
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

- [ ] Consume only existing `canary-otbm-semantic-diff-v1` evidence plus reviewed Universal E2E scenario manifests and canonical route-plan evidence.
- [ ] Require exact full-index diff evidence before claiming a scenario is non-impacted.
- [ ] Require baseline route-plan source-map and World Index provenance to match the Semantic Diff `before` provenance before allowing a skip decision.
- [ ] Select a scenario when any exact diff finding position intersects its executed route positions or transition/interaction evidence.
- [ ] Fail closed to selecting a scenario when diff findings are truncated, route evidence is missing/malformed/stale, or a finding lacks exact position evidence.
- [ ] Keep selected versus safely-skipped decisions explicit and deterministic with bounded reasons and finding IDs.
- [ ] Do not execute scenarios, parse OTBM, regenerate paths, or modify maps.
- [ ] Add focused tests, schema, documentation and module catalogue entry.
- [ ] Apply `ci:final-gate` before final checkpoint commit and pass exact-final-head required checks.
- [ ] Complete final review/overlap/mergeability audit, squash merge and lifecycle archive.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-20
head: 99b9dec84d953d3f200284d0cf193261027650ca
branch: feat/otbm-e2e-008-semantic-diff-selection
pr: null
status: implementing
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
  - current task branch was created from live main 99b9dec84d953d3f200284d0cf193261027650ca
  - no open PR or branch matching OTBM-E2E-008 was found before task claim
  - existing Semantic Diff emits exact stable finding IDs and exact positions but samples may be truncated
  - existing Universal E2E scenario manifests identify follow_route logical route IDs while canonical route plans carry ordered path and provenance
  - existing PR scenario selector remains the execution owner and is read-only for this task
derived:
  - exact non-impact proof must fail closed when Semantic Diff samples are truncated or baseline route provenance does not match the diff before-map evidence
unknown:
  - final implementation head and workflow conclusions
  - final feature and lifecycle merge SHAs
conflicts: []
first_failure:
  marker: none
  evidence: no implementation failure recorded yet
rejected_hypotheses:
  - parse or rescan OTBM for impact selection: Semantic Diff is the authoritative change evidence
  - recompute routes during selection: canonical baseline route plans are evidence inputs and Reachability remains the sole pathfinder
  - modify Universal E2E runner in this bounded task: selector output is a bridge contract and runner remains unchanged
changed_paths:
  - docs/agents/tasks/active/CAN-20260720-otbm-e2e-008-semantic-diff-selection.md
validation: []
blockers: []
next_action: Open the draft PR, then implement the bounded Semantic Diff impacted-scenario selector with focused fail-closed tests.
```
