---
task_id: CAN-20260721-otbm-quality-repair-roadmap
program_id: CAN-PROGRAM-OTBM
status: implementing
agent: "GPT-5.6 Thinking"
branch: docs/otbm-quality-repair-roadmap-20260721
base_branch: main
created: 2026-07-21
updated: 2026-07-21
last_verified_commit: "994d1ffdfd6828688b1acc6cd7c0c519eab052ba"
risk: low
related_issue: ""
related_pr: ""
depends_on:
  - CAN-PROGRAM-OTBM-E2E-ROUTING completed
blocks: []
owned_paths:
  exclusive:
    - docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md
    - docs/ai-agent/OTBM_E2E_ROUTE_INTEGRATION.md
    - docs/agents/tasks/active/CAN-20260721-otbm-quality-repair-roadmap.md
  shared:
    - docs/agents/CHANGELOG.md
  read_only:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/programs/OTBM_E2E_ROUTE_INTEGRATION_PROGRAM.md
modules_touched: []
reuses:
  - Unified OTBM World Index
  - OTBM Script Resolution
  - OTBM Reachability
  - Semantic OTBM Diff
  - OTBM Geometry Audit
  - OTBM Map Quality Gate
  - OTBM repair preflight and repair/materialization pipeline
  - OTBM-E2E-001..009 delivered contracts
public_interfaces: []
cross_repo_tasks: []
---

# CAN-20260721 — OTBM quality, repair and regression roadmap reconciliation

## Status

ACTIVE — documentation/architecture reconciliation only. No OTBM binary, datapack, runtime or production map changes are authorized by this task.

## Goal

Update the authoritative OTBM tooling roadmap and route-integration architecture to current live state after completion of OTBM-E2E-001..009, then define the next bounded architecture for world health auditing, regression protection, reviewed repair orchestration, coverage reporting and region/quest certification.

## Scope

- Preserve the completed `CAN-PROGRAM-OTBM-E2E-ROUTING` programme as closed.
- Record OTBM-E2E-008 Semantic Diff impacted selection and OTBM-E2E-009 candidate-map Physical E2E validation as delivered.
- Reconcile stale architecture text that still describes already-delivered bridge capabilities as missing.
- Define successor work as composition over existing OTBM audit, quality, repair/materialization and Physical E2E contracts.
- Keep automatic mutation fail-closed and review/approval gated; no second parser, pathfinder, renderer, writer, E2E runner or workflow.

## Acceptance criteria

- `OTS_OTBM_TOOLING_ROADMAP.md` reflects current completed routing/E2E state and a dependency-ordered future queue.
- `OTBM_E2E_ROUTE_INTEGRATION.md` reflects delivered v1 instead of an implementation queue and documents the successor quality/repair architecture boundary.
- Future roadmap distinguishes read-only health/certification from approval-gated candidate mutation and from Physical E2E proof.
- Existing repair/materialization contracts are reused rather than replaced.
- No binary/map/runtime implementation files change.

## Evidence state

- `PROVEN`: OTBM-E2E-001..009 are merged/archived and the route integration programme is formally closed.
- `PROVEN`: existing Map Quality, repair preflight, sandbox/materialization and candidate Physical E2E contracts already provide bounded building blocks.
- `DERIVED`: the next roadmap can be organized around world health, regression guard, repair orchestration, coverage dashboard and certification by composing those delivered contracts.
- `UNKNOWN`: exact future task numbering, implementation sequencing and CI workflow placement until each bounded implementation task performs fresh live ownership/preflight.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T11:00:00Z
head: 994d1ffdfd6828688b1acc6cd7c0c519eab052ba
branch: docs/otbm-quality-repair-roadmap-20260721
pr: null
status: implementing
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md
  - docs/ai-agent/OTBM_E2E_ROUTE_INTEGRATION.md
  - docs/agents/CHANGELOG.md
  - docs/agents/tasks/active/CAN-20260721-otbm-quality-repair-roadmap.md
proven:
  - CAN-PROGRAM-OTBM-E2E-ROUTING was closed after OTBM-E2E-001..009 merged and archived.
  - OTBM-E2E-008 selects impacted Physical E2E scenarios from Semantic OTBM Diff evidence.
  - OTBM-E2E-009 validates approved candidate maps with selected Physical E2E while preserving exact candidate provenance.
  - Existing OTBM repair/materialization tooling already provides bounded attribute and structural mutation paths on distinct copies.
derived:
  - Successor architecture should compose existing evidence and mutation boundaries rather than create a new parser, writer, pathfinder or E2E runner.
unknown:
  - Exact implementation package IDs after this documentation reconciliation.
conflicts: []
first_failure: null
rejected_hypotheses:
  - Building a new automatic repair engine from scratch; existing repair/materialization pipeline must be reused.
changed_paths:
  - docs/agents/tasks/active/CAN-20260721-otbm-quality-repair-roadmap.md
validation: []
blockers: []
next_action: Open the draft PR, then update the OTBM tooling roadmap and route-integration architecture with the successor quality/repair/regression model.
```
