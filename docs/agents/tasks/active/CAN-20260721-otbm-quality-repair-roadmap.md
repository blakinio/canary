---
task_id: CAN-20260721-otbm-quality-repair-roadmap
program_id: CAN-PROGRAM-OTBM
status: implementing
agent: "GPT-5.6 Thinking"
branch: docs/otbm-quality-repair-roadmap-20260721
base_branch: main
created: 2026-07-21
updated: 2026-07-21
last_verified_commit: "d4e347f7d9f5da28d948cba23121aa7a8ded3d18"
risk: low
related_issue: ""
related_pr: "665"
depends_on:
  - CAN-PROGRAM-OTBM-E2E-ROUTING completed
blocks: []
owned_paths:
  exclusive:
    - docs/ai-agent/OTBM_WORLD_QUALITY_REPAIR_ROADMAP.md
    - docs/architecture/otbm-world-quality-repair.md
    - docs/agents/tasks/active/CAN-20260721-otbm-quality-repair-roadmap.md
  shared: []
  read_only:
    - docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md
    - docs/ai-agent/OTBM_E2E_ROUTE_INTEGRATION.md
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

Persist a successor OTBM roadmap and architecture after completion of OTBM-E2E-001..009, covering world health auditing, regression protection, reviewed repair orchestration, coverage reporting and region/quest certification without reopening the completed validation or route-integration programmes.

## Scope

- Preserve the completed `OTS-OTBM-VALIDATION` and `CAN-PROGRAM-OTBM-E2E-ROUTING` records as historical delivered state.
- Record OTBM-E2E-008 Semantic Diff impacted selection and OTBM-E2E-009 candidate-map Physical E2E validation as delivered baseline capabilities.
- Define successor work as composition over existing OTBM audit, quality, repair/materialization and Physical E2E contracts.
- Separate read-only health/certification, repair recommendation, explicit approval, candidate mutation, static validation and Physical E2E proof.
- Keep mutation fail-closed and approval gated; no second parser, pathfinder, renderer, writer, E2E runner or workflow.

## Acceptance criteria

- `OTBM_WORLD_QUALITY_REPAIR_ROADMAP.md` defines a dependency-ordered successor queue grounded in delivered contracts.
- `docs/architecture/otbm-world-quality-repair.md` defines the end-to-end evidence/mutation/candidate/certification layer model and ownership boundaries.
- Future roadmap distinguishes read-only health/certification from approval-gated candidate mutation and from Physical E2E proof.
- Existing repair/materialization and OTBM-E2E-001..009 contracts are reused rather than replaced.
- Completed historical programmes remain closed.
- No binary/map/runtime implementation files change.

## Evidence state

- `PROVEN`: OTBM-E2E-001..009 are merged/archived and the route integration programme is formally closed.
- `PROVEN`: OTBM-E2E-008 provides Semantic Diff impacted Physical E2E selection.
- `PROVEN`: OTBM-E2E-009 provides approved candidate-map selected Physical E2E validation with exact candidate provenance.
- `PROVEN`: existing Map Quality, repair preflight, sandbox/materialization and repair/materialization pipeline contracts already provide bounded building blocks.
- `DERIVED`: the next roadmap can be organized around world health, regression guard, repair recommendations, reviewed candidate orchestration, coverage/certification and continuous assurance by composing those delivered contracts.
- `UNKNOWN`: exact future implementation task ownership and CI workflow placement until each bounded package performs fresh live preflight.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T12:00:00Z
head: d4e347f7d9f5da28d948cba23121aa7a8ded3d18
branch: docs/otbm-quality-repair-roadmap-20260721
pr: 665
status: implementing
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - docs/ai-agent/OTBM_WORLD_QUALITY_REPAIR_ROADMAP.md
  - docs/architecture/otbm-world-quality-repair.md
  - docs/agents/tasks/active/CAN-20260721-otbm-quality-repair-roadmap.md
proven:
  - CAN-PROGRAM-OTBM-E2E-ROUTING was closed after OTBM-E2E-001..009 merged and archived.
  - OTBM-E2E-008 selects impacted Physical E2E scenarios from Semantic OTBM Diff evidence.
  - OTBM-E2E-009 validates approved candidate maps with selected Physical E2E while preserving exact candidate provenance.
  - Existing OTBM repair/materialization tooling provides bounded attribute, TILE_AREA and raw-tile mutation paths on distinct copies.
  - PR #665 is the draft documentation-only delivery branch for this reconciliation.
derived:
  - Successor architecture should compose existing evidence and mutation boundaries rather than create a new parser, writer, pathfinder or E2E runner.
  - Completed historical roadmap/programme records should remain closed and the new work should be expressed as a successor roadmap.
unknown:
  - Exact implementation owners and CI placement for future OTBM-QA packages.
conflicts: []
first_failure:
  marker: Agent Task Ownership / Validate changed active task checkpoints
  evidence: Run 29820096255 rejected first_failure because it was null instead of a YAML mapping; this checkpoint repairs that contract.
rejected_hypotheses:
  - Building a new automatic repair engine from scratch; existing repair/materialization pipeline must be reused.
  - Reopening the completed OTBM-E2E route programme for successor quality/certification work.
changed_paths:
  - docs/ai-agent/OTBM_WORLD_QUALITY_REPAIR_ROADMAP.md
  - docs/architecture/otbm-world-quality-repair.md
  - docs/agents/tasks/active/CAN-20260721-otbm-quality-repair-roadmap.md
validation:
  - command: GitHub Actions CI run 29820096710
    result: PASS
    evidence: Repository CI passed on head d4e347f7d9f5da28d948cba23121aa7a8ded3d18.
  - command: GitHub Actions Agent Task Ownership run 29820096255
    result: FAIL
    evidence: Checkpoint contract required first_failure to be a YAML mapping; repaired in the next commit.
blockers: []
next_action: Verify current-head Agent Task Ownership, AI Agent Tools and OTBM Map Tools after the checkpoint-contract repair; then apply the exact-final-head gate if required.
```
