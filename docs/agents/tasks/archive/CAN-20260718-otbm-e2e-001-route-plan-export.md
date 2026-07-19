---
task_id: CAN-20260718-otbm-e2e-001-route-plan-export
program_id: CAN-PROGRAM-OTBM-E2E-ROUTING
coordination_id: OTBM-E2E-001
status: completed
agent: "GPT-5.5 Thinking"
branch: feat/otbm-e2e-001-route-plan-export
base_branch: main
created: 2026-07-18T23:45:00+02:00
updated: 2026-07-19T07:37:09Z
last_verified_commit: "f962d7b606e29965fe091ea79ba154c27b22fe34"
risk: medium
related_issue: ""
related_pr: "567"
depends_on:
  - CAN-PROGRAM-OTBM-E2E-ROUTING merged planning programme PR #562
blocks:
  - E2E-ROUTE-001
  - OTBM-E2E-004
  - OTBM-E2E-005
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260718-otbm-e2e-001-route-plan-export.md
    - tools/ai-agent/otbm_reachability_graph.py
    - tools/ai-agent/otbm_reachability_analysis.py
    - tools/ai-agent/otbm_reachability.py
    - tools/ai-agent/otbm_reachability_tool.py
    - tools/ai-agent/test_otbm_reachability.py
    - docs/ai-agent/OTBM_E2E_ROUTE_PLAN.schema.json
    - docs/ai-agent/OTBM_E2E_ROUTE_PLAN.md
  shared:
    - docs/ai-agent/OTBM_REACHABILITY.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - docs/agents/programs/OTBM_E2E_ROUTE_INTEGRATION_PROGRAM.md
    - docs/ai-agent/OTBM_E2E_ROUTE_INTEGRATION.md
    - docs/ai-agent/OTBM_WORLD_INDEX.md
    - docs/ai-agent/OTBM_TRANSITIONS.schema.json
    - docs/agents/TASK_LIFECYCLE.md
    - tools/e2e/**
modules_touched:
  - OTBM Reachability executable route-plan export
reuses:
  - tools/ai-agent/otbm_reachability_graph.py::_bfs
  - existing predecessor map previous[position] = (parent, transition_id)
  - tools/ai-agent/otbm_reachability_graph.py::_movement_neighbors
  - existing strict/optimistic tile classification
  - existing validated transition states and transition edges
  - Unified OTBM World Index provenance
public_interfaces:
  - canary-otbm-e2e-route-plan-v1
cross_repo_tasks: []
completed: 2026-07-19T07:37:09Z
---

# Goal

Implement `OTBM-E2E-001 — Reachability executable route export` as a bounded extension of the existing OTBM Reachability graph/BFS. The output must preserve the existing route decision, expose the complete ordered path and exact edge sequence, attach transition evidence to the exact edge where it is used, and fail closed when a route cannot be safely published as executable.

# Acceptance criteria

- [x] Route planning is derived from the existing `_bfs` predecessor graph; no second pathfinder or graph builder is introduced.
- [x] Add versioned `canary-otbm-e2e-route-plan-v1` schema and human-readable contract.
- [x] Export exact map, World Index, appearances, bounds, origin, destination and routing-policy provenance.
- [x] Export the complete ordered path and complete ordered edge list for supported routes.
- [x] Distinguish ordinary movement edges from transition edges.
- [x] Attach `transition_id` and validated existing transition evidence to the exact transition edge.
- [x] Preserve `confirmed`, `conditional`, `unreachable` and `invalid` Reachability semantics.
- [x] Never mark unresolved `conditional`, `unreachable` or `invalid` routes executable.
- [x] Fail closed with a machine-readable blocker when the full route exceeds the supported executable bound; never publish a truncated route as executable.
- [x] Add focused tests for ordinary movement, movement plus transition, exact transition-edge placement, non-executable statuses, full-route bound and deterministic output/hash.
- [x] Prove route-plan status/distance matches the existing Reachability decision for the same BFS/predecessor graph.
- [x] Update the reusable interface catalogue/changelog only for the delivered public contract.
- [x] Apply `ci:final-gate` before the final checkpoint commit.
- [ ] Verify required checks and review/merge blockers on the exact final head before merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19T00:13:00+02:00
head: cd6cb40609844b112a0b352b16c38bd8b056cdc0
branch: feat/otbm-e2e-001-route-plan-export
pr: 567
status: implementing
context_routes:
  - agent-governance
  - otbm
owned_paths:
  - docs/agents/tasks/active/CAN-20260718-otbm-e2e-001-route-plan-export.md
  - tools/ai-agent/otbm_reachability_graph.py
  - tools/ai-agent/otbm_reachability_analysis.py
  - tools/ai-agent/otbm_reachability.py
  - tools/ai-agent/otbm_reachability_tool.py
  - tools/ai-agent/test_otbm_reachability.py
  - docs/ai-agent/OTBM_E2E_ROUTE_PLAN.schema.json
  - docs/ai-agent/OTBM_E2E_ROUTE_PLAN.md
  - docs/ai-agent/OTBM_REACHABILITY.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - task branch was created from live main at c1c0d10ed1e758cb72728be5fe22458cd9d9e61a
  - draft PR 567 is the early same-repository PR for this task with base main and head feat/otbm-e2e-001-route-plan-export
  - merged programme PR #562 defines OTBM-E2E-001 and requires reuse of the existing Reachability BFS/predecessor graph
  - existing _bfs stores previous[destination] = (parent, transition_id)
  - full route reconstruction now walks only the selected existing BFS predecessor map and does not perform another search
  - normal Reachability analyze output remains opt-in unchanged because routePlan is added only when route_plan_max_positions is explicitly requested
  - route plan export preserves the selected Reachability status and BFS distance and attaches transition_id to the exact predecessor edge
  - full-route output is reconstructed independently of the existing head/tail public report sample
  - route-plan over-limit handling emits no partial path or edges and blocks execution with route-exceeds-supported-bound
  - conditional routes remain blocked and unreachable or invalid routes remain non-executable
  - selected routes containing validated transitions preserve exact edge evidence but remain blocked until later interaction semantics are explicitly defined
  - route-plan input and full-plan hashes are deterministic over canonical JSON inputs and output
  - focused OTBM Reachability workflow passed with the six requested route-plan coverage areas
  - Agent Task Ownership passed after repairing the checkpoint first_failure field to the required YAML mapping
  - live open-PR review immediately before final gate found no other owner of tools/ai-agent/otbm_reachability*.py or the route-plan contract paths
  - PR #565 explicitly excludes OTBM parser, pathfinder and route-consumption changes; tools/e2e remains untouched by this task
  - live main remained c1c0d10ed1e758cb72728be5fe22458cd9d9e61a immediately before final gate
  - complete PR diff was reviewed before final gate; no OTBM, WIDX, items.otb, client assets, generated route reports or tools/e2e paths are present
  - ci:final-gate was applied before the final checkpoint commit and explicitly removed/reapplied before this governance-only follow-up checkpoint fix
  - repository writes are restricted to blakinio/canary
  - no local Git checkout is available in the execution sandbox; GitHub connector state is authoritative for branch, PR and workflow operations
  - direct git clone is unavailable because the sandbox cannot resolve github.com
  - OTBM World Index map source SHA-256 is available through worldIndexManifest.source.sha256 when a validated world manifest is supplied
  - executable route provenance fails closed when required map, World Index or appearances identity is unavailable
derived:
  - pure confirmed movement can be executable when required provenance is present; conditional geometry and unresolved physical transition activation remain blocked
  - route-plan input and plan hashes provide deterministic stale-plan identity for later runtime preflight
unknown:
  - exact final-head workflow conclusions are pending this checkpoint commit and must be verified before merge
conflicts: []
blockers: []
first_failure:
  marker: repaired
  evidence: initial changed-task validation rejected first_failure as null on 2ffccff2b0f8a8add4e612fd641a791005206130; the checkpoint was changed to a mapping and Agent Task Ownership subsequently passed on c0aafb64b28ba17874cc62577ac20b98452a6029
rejected_hypotheses:
  - add an E2E-owned BFS, A*, Dijkstra or graph builder
  - infer stairs, ladders, holes, rope, doors or dynamic Lua behavior
  - treat optimistic reachability as physical executability
  - reuse the existing truncated head/tail path sample as executable output
changed_paths:
  - docs/agents/tasks/active/CAN-20260718-otbm-e2e-001-route-plan-export.md
  - tools/ai-agent/otbm_reachability_graph.py
  - tools/ai-agent/otbm_reachability_analysis.py
  - tools/ai-agent/otbm_reachability.py
  - tools/ai-agent/otbm_reachability_tool.py
  - tools/ai-agent/test_otbm_reachability.py
  - docs/ai-agent/OTBM_E2E_ROUTE_PLAN.schema.json
  - docs/ai-agent/OTBM_E2E_ROUTE_PLAN.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
validation:
  - command: live repository, programme, routed OTBM docs, open PR and ownership preflight
    result: PASS
    evidence: main c1c0d10ed1e758cb72728be5fe22458cd9d9e61a; PR #562 merged; PR #563 merged; no overlapping Reachability route-plan owner found
  - command: OTBM Reachability workflow on 2ffccff2b0f8a8add4e612fd641a791005206130
    result: PASS
    evidence: workflow run 29662423170 completed successfully with focused route-plan tests included
  - command: Agent Task Ownership workflow on 2ffccff2b0f8a8add4e612fd641a791005206130
    result: FAIL
    evidence: changed-task checkpoint validation required first_failure to be a YAML mapping instead of null; implementation tests were not the failure
  - command: Agent Task Ownership workflow on c0aafb64b28ba17874cc62577ac20b98452a6029
    result: PASS
    evidence: checkpoint schema repair accepted
  - command: current-head workflows on 0a4ff423403352d0986d8a68e1df1f2e6ed2d3ee before final checkpoint
    result: PASS
    evidence: CI, OTBM Reachability, OTBM Spawn and NPC Validation, OTBM Semantic Diff, OTBM Geometry Audit, Agent Task Ownership and OTBM Map Tools all completed successfully; AI Agent Tools unit-test and generation/validation steps completed successfully while the workflow status was still finalizing
  - command: full PR diff and live ownership/main pre-merge review
    result: PASS
    evidence: main unchanged at c1c0d10ed1e758cb72728be5fe22458cd9d9e61a; no competing Reachability route-plan PR; no tools/e2e or forbidden binary/generated artifact paths in the diff
  - command: ci:final-gate label application
    result: PASS
    evidence: label applied before final checkpoint and reapplied before the governance-only follow-up checkpoint fix
  - command: Agent Task Ownership workflow on cd6cb40609844b112a0b352b16c38bd8b056cdc0
    result: FAIL
    evidence: active task records require an active lifecycle status; status validating was rejected, so this checkpoint restores implementing and leaves archival to lifecycle automation after merge
next_action: Verify every required workflow on the exact final head, inspect review threads and merge blockers, then mark PR ready and squash-merge only if the full merge gate is green.
```

## Automated lifecycle completion

- Feature PR: #567.
- Feature head: `bc81c6ae1ef3c0b7b2854dc6debe1d7771429ba1`.
- Merge commit: `f962d7b606e29965fe091ea79ba154c27b22fe34`.
- Merged at: `2026-07-19T07:37:09Z`.
- This record was moved from `tasks/active` by the post-merge lifecycle automation.
