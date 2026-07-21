---
task_id: CAN-20260721-otbm-roadmap-all-proposals
program_id: CAN-PROGRAM-OTBM
status: implementing
agent: "GPT-5.6 Thinking"
branch: docs/otbm-roadmap-all-proposals-20260721
base_branch: main
created: 2026-07-21
updated: 2026-07-21
last_verified_commit: "92f9e68b1eb82d5a9387d3f1b7c443fa6c0f65f6"
risk: low
related_issue: ""
related_pr: "669"
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
- `PROVEN`: PR #669 changes exactly the consolidated roadmap and this active task record.
- `PROVEN`: pre-final head `92f9e68b1eb82d5a9387d3f1b7c443fa6c0f65f6` passed CI, Agent Task Ownership, OTBM Map Tools and AI Agent Tools.
- `PROVEN`: PR #669 has no inline review threads and remains mergeable.
- `DERIVED`: remaining proposals can be grouped into advanced analysis, world/domain integrity, lifecycle/provenance and downstream evidence-interface packages.
- `DERIVED`: helping E2E through compact OTBM evidence is compatible with the current ownership model only when scenario/runtime ownership remains with Universal E2E.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T12:40:00Z
head: 92f9e68b1eb82d5a9387d3f1b7c443fa6c0f65f6
branch: docs/otbm-roadmap-all-proposals-20260721
pr: 669
status: validating
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
  - Consolidated roadmap maps every OTBM proposal from the discussion into OTBM-QA-001..018 or an existing package.
  - OTBM-QA-018 explicitly limits downstream-agent/E2E support to compact read-only evidence and existing route/impact/coverage artifacts.
  - PR #669 changed-file list contains only the roadmap and this active task record.
  - Pre-final CI run 29822282257 passed on head 92f9e68b1eb82d5a9387d3f1b7c443fa6c0f65f6.
  - Pre-final Agent Task Ownership run 29822282063 passed.
  - Pre-final OTBM Map Tools run 29822282095 passed.
  - Pre-final AI Agent Tools run 29822282103 passed.
  - PR #669 has zero inline review threads.
derived:
  - Advanced proposals are grouped into dependency/blast-radius, quest/content integrity, quest-state reachability, connectivity resilience, critical/domain integrity, asset/hotspot, lifecycle/provenance, deterministic risk and evidence-gateway packages.
unknown:
  - Required exact-final-head workflow conclusions after this final checkpoint commit.
conflicts: []
first_failure:
  marker: none
  evidence: No task-specific validation failure observed.
rejected_hypotheses:
  - Giving OTBM ownership of E2E scenario generation or runtime orchestration.
  - Giving OTBM ownership of E2E replay, general runtime failure investigation or E2E NEXT_ACTION generation.
  - Creating a second pathfinder, parser, renderer, writer, E2E runner or workflow.
changed_paths:
  - docs/ai-agent/OTBM_WORLD_QUALITY_REPAIR_ROADMAP.md
  - docs/agents/tasks/active/CAN-20260721-otbm-roadmap-all-proposals.md
validation:
  - command: GitHub Actions CI run 29822282257
    result: PASS
    evidence: Repository CI passed on pre-final head 92f9e68b1eb82d5a9387d3f1b7c443fa6c0f65f6.
  - command: GitHub Actions Agent Task Ownership run 29822282063
    result: PASS
    evidence: Ownership and active checkpoint validation passed on pre-final head.
  - command: GitHub Actions OTBM Map Tools run 29822282095
    result: PASS
    evidence: Focused OTBM validation passed on pre-final head.
  - command: GitHub Actions AI Agent Tools run 29822282103
    result: PASS
    evidence: AI-agent tooling validation passed on pre-final head.
blockers:
  - Exact-final-head checks triggered by ci:final-gate must pass before readiness/merge.
next_action: Verify all required exact-final-head checks on the final checkpoint head; if green and no review blockers remain, mark PR #669 ready and squash-merge without further feature-head commits.
```
