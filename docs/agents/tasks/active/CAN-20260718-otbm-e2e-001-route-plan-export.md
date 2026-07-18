---
task_id: CAN-20260718-otbm-e2e-001-route-plan-export
program_id: CAN-PROGRAM-OTBM-E2E-ROUTING
coordination_id: OTBM-E2E-001
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/otbm-e2e-001-route-plan-export
base_branch: main
created: 2026-07-18T23:45:00+02:00
updated: 2026-07-18T23:45:00+02:00
last_verified_commit: "c1c0d10ed1e758cb72728be5fe22458cd9d9e61a"
risk: medium
related_issue: ""
related_pr: ""
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
---

# Goal

Implement `OTBM-E2E-001 — Reachability executable route export` as a bounded extension of the existing OTBM Reachability graph/BFS. The output must preserve the existing route decision, expose the complete ordered path and exact edge sequence, attach transition evidence to the exact edge where it is used, and fail closed when a route cannot be safely published as executable.

# Acceptance criteria

- [ ] Route planning is derived from the existing `_bfs` predecessor graph; no second pathfinder or graph builder is introduced.
- [ ] Add versioned `canary-otbm-e2e-route-plan-v1` schema and human-readable contract.
- [ ] Export exact map, World Index, appearances, bounds, origin, destination and routing-policy provenance.
- [ ] Export the complete ordered path and complete ordered edge list for supported routes.
- [ ] Distinguish ordinary movement edges from transition edges.
- [ ] Attach `transition_id` and validated existing transition evidence to the exact transition edge.
- [ ] Preserve `confirmed`, `conditional`, `unreachable` and `invalid` Reachability semantics.
- [ ] Never mark unresolved `conditional`, `unreachable` or `invalid` routes executable.
- [ ] Fail closed with a machine-readable blocker when the full route exceeds the supported executable bound; never publish a truncated route as executable.
- [ ] Add focused tests for ordinary movement, movement plus transition, exact transition-edge placement, non-executable statuses, full-route bound and deterministic output/hash.
- [ ] Prove route-plan status/distance matches the existing Reachability decision for the same BFS/predecessor graph.
- [ ] Update the reusable interface catalogue/changelog only for the delivered public contract.
- [ ] Apply `ci:final-gate` before the final checkpoint commit and verify required checks on the exact final head.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-18T23:45:00+02:00
head: c1c0d10ed1e758cb72728be5fe22458cd9d9e61a
branch: feat/otbm-e2e-001-route-plan-export
pr: null
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
  - merged programme PR #562 defines OTBM-E2E-001 and requires reuse of the existing Reachability BFS/predecessor graph
  - existing _bfs stores previous[destination] = (parent, transition_id)
  - existing _reconstruct_path truncates long public-report paths and therefore cannot itself be used as an executable full-route contract
  - existing Reachability separates confirmed, conditional, unreachable and invalid geometry states
  - existing reviewed transition state retains stable transition IDs, validation state, uncertainties and evidence
  - live open-PR review found no owner of tools/ai-agent/otbm_reachability*.py or the planned route-plan contract paths
  - PR #565 explicitly excludes OTBM parser/pathfinder/routing changes and tools/e2e remains out of scope here
  - repository writes are restricted to blakinio/canary
  - no local Git checkout is available in the execution sandbox; GitHub connector state is authoritative for branch/PR operations
  - direct git clone is unavailable because the sandbox cannot resolve github.com
  - OTBM World Index map source SHA-256 is available through worldIndexManifest.source.sha256 when a validated world manifest is supplied
  - executable route provenance must fail closed when required map or World Index identity is unavailable

derived:
  - a full edge-aware reconstruction helper can walk the same predecessor map without running any new search
  - pure confirmed movement can be executable when required provenance is present; conditional geometry and unresolved physical transition activation remain blocked
unknown:
  - exact final GitHub required-check set for the future final head; verify from live workflow runs before merge
conflicts: []
blockers: []
first_failure: null
rejected_hypotheses:
  - add an E2E-owned BFS, A*, Dijkstra or graph builder
  - infer stairs, ladders, holes, rope, doors or dynamic Lua behavior
  - treat optimistic reachability as physical executability
  - reuse the existing truncated head/tail path sample as executable output
changed_paths:
  - docs/agents/tasks/active/CAN-20260718-otbm-e2e-001-route-plan-export.md
validation:
  - command: live repository, programme, routed OTBM docs, open PR and ownership preflight
    result: PASS
    evidence: main c1c0d10ed1e758cb72728be5fe22458cd9d9e61a; PR #562 merged; PR #563 merged; open PRs reviewed; no overlapping Reachability route-plan owner found
next_action: Open the early draft PR, bind the task record to its PR number, then implement full predecessor-derived route reconstruction and deterministic route-plan export with focused tests.
```
