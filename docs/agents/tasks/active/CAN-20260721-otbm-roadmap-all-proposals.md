---
task_id: CAN-20260721-otbm-roadmap-all-proposals
program_id: CAN-PROGRAM-OTBM
status: implementing
agent: "GPT-5.6 Thinking"
branch: docs/otbm-roadmap-all-proposals-20260721
base_branch: main
created: 2026-07-21
updated: 2026-07-21
last_verified_commit: "824abcfe3d39d274e8cad534fff06236085b129b"
risk: low
related_issue: ""
related_pr: ""
depends_on:
  - CAN-20260721-otbm-quality-repair-roadmap complete
blocks: []
owned_paths:
  exclusive:
    - docs/ai-agent/OTBM_WORLD_QUALITY_REPAIR_ROADMAP.md
    - docs/agents/tasks/active/CAN-20260721-otbm-roadmap-all-proposals.md
  shared: []
  read_only:
    - docs/architecture/otbm-world-quality-repair.md
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
  - OTBM repair/materialization pipeline
  - OTBM-E2E-001..009 delivered contracts
public_interfaces: []
cross_repo_tasks: []
---

# CAN-20260721 — Consolidate all OTBM roadmap proposals

## Status

ACTIVE — documentation-only roadmap expansion. No OTBM binary, runtime, E2E runner, workflow, datapack or production map changes are authorized.

## Goal

Consolidate every OTBM-focused proposal raised in the current design discussion into the durable successor roadmap, while preserving the architectural boundary that OTBM may help Universal E2E and E2E agents through exact read-only evidence but must not take ownership of E2E scenarios, fixtures, runner lifecycle, runtime assertions or general test orchestration.

## Scope

- Preserve existing `OTBM-QA-001..007` roadmap packages.
- Add the remaining proposals for dependency/blast-radius analysis, dead/orphaned content, quest completeness/state reachability, connectivity/fragility/entrapment, teleport networks, critical infrastructure, house/spawn accessibility, identifier collisions, asset consistency, static performance hotspots, release provenance, upgrade compatibility, quality history, certification freshness and deterministic change risk.
- Add one downstream-agent support package that exposes compact OTBM evidence/query surfaces without creating an E2E copilot or second runner.
- Record a proposal-to-package inventory so no idea from the discussion is lost.

## Acceptance criteria

- All OTBM proposals from the discussion are represented or explicitly mapped to an existing package.
- E2E-support capabilities remain evidence-only and reuse existing route/impact/coverage contracts.
- The roadmap explicitly excludes E2E scenario generation, runtime fixture design, client/server lifecycle control, replay, general runtime failure investigation and NEXT_ACTION ownership.
- No parallel parser, scanner, World Index, pathfinder, Script Resolution engine, renderer, mutation path, E2E runner or workflow is proposed.
- No code, map or runtime files change.

## Evidence state

- `PROVEN`: PR #665 merged the initial successor roadmap with OTBM-QA-001..007.
- `PROVEN`: PR #668 archived the completed predecessor task, so this task owns the roadmap without active-task overlap.
- `DERIVED`: remaining proposals can be grouped into advanced analysis, world/domain integrity, lifecycle/provenance and downstream evidence-interface packages.
- `DERIVED`: helping E2E through compact OTBM evidence is compatible with the current ownership model only when scenario/runtime ownership remains with Universal E2E.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T12:25:00Z
head: 824abcfe3d39d274e8cad534fff06236085b129b
branch: docs/otbm-roadmap-all-proposals-20260721
pr: null
status: implementing
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - docs/ai-agent/OTBM_WORLD_QUALITY_REPAIR_ROADMAP.md
  - docs/agents/tasks/active/CAN-20260721-otbm-roadmap-all-proposals.md
proven:
  - Initial successor roadmap OTBM-QA-001..007 merged through PR #665.
  - Predecessor task lifecycle archived through PR #668.
  - Existing OTBM-E2E route programme remains closed and is reused only through its delivered contracts.
derived:
  - The consolidated roadmap should add advanced static analysis packages and one evidence-only downstream-agent gateway.
unknown: []
conflicts: []
first_failure:
  marker: none
  evidence: No task-specific validation failure observed yet.
rejected_hypotheses:
  - Giving OTBM ownership of E2E scenario generation or runtime orchestration.
  - Creating a second pathfinder, parser, renderer, writer, E2E runner or workflow.
changed_paths:
  - docs/agents/tasks/active/CAN-20260721-otbm-roadmap-all-proposals.md
validation: []
blockers: []
next_action: Open a draft PR, then expand the OTBM successor roadmap with the consolidated proposal inventory and explicit E2E-support boundary.
```
