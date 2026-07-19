---
task_id: CAN-20260719-otbm-e2e-001b-executable-routing
program_id: CAN-PROGRAM-OTBM-E2E-ROUTING
coordination_id: OTBM-E2E-001B
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/otbm-e2e-001b-executable-routing
base_branch: main
created: 2026-07-19T11:58:00+02:00
updated: 2026-07-19T11:58:00+02:00
last_verified_commit: ""
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - OTBM-E2E-001 route-plan contract merged as PR #567
  - OTBM-E2E-003 route interaction registry merged as PR #572
blocks:
  - robust door/use routing in OTBM-E2E-005
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260719-otbm-e2e-001b-executable-routing.md
    - tools/ai-agent/otbm_reachability_graph.py
    - tools/ai-agent/otbm_reachability_analysis.py
    - tools/ai-agent/otbm_reachability.py
    - tools/ai-agent/otbm_reachability_tool.py
    - tools/ai-agent/test_otbm_reachability_executable.py
    - docs/ai-agent/OTBM_E2E_ROUTE_PLAN.md
    - docs/ai-agent/OTBM_E2E_ROUTE_PLAN.schema.json
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - docs/agents/programs/OTBM_E2E_ROUTE_INTEGRATION_PROGRAM.md
    - docs/ai-agent/OTBM_E2E_ROUTE_INTEGRATION.md
    - docs/ai-agent/OTBM_ROUTE_INTERACTIONS.md
    - docs/ai-agent/OTBM_ROUTE_INTERACTIONS.schema.json
    - docs/ai-agent/OTBM_ROUTE_INTERACTIONS.json
    - tools/ai-agent/otbm_route_interactions.py
    - tools/e2e/**
modules_touched:
  - OTBM Reachability
  - OTBM E2E Route Plan
reuses:
  - existing otbm_reachability_graph.py::_bfs traversal and predecessor map
  - existing strict and optimistic tile classification
  - existing validated transition states and transition IDs
  - canary-otbm-route-interactions-v1 resolver and provenance gate
public_interfaces:
  - canary-otbm-e2e-route-plan-v1 executable routing mode
cross_repo_tasks: []
---

# Goal

Implement `OTBM-E2E-001B — Executable interaction-aware routing mode` by rerunning the existing Reachability `_bfs()` with a fail-closed executable edge policy. Strictly walkable edges remain usable; conditional crossings are usable only when their exact reviewed interaction resolves as executable. Plain optimistic/unknown reachability must never become physical executability.

# Acceptance criteria

- [ ] Reuse the existing `_bfs()` traversal; do not add another pathfinder.
- [ ] Preserve existing strict and optimistic Reachability report behavior when executable interaction routing is not requested.
- [ ] Add an executable movement/edge policy equivalent to strict walkability OR an exact conditional crossing with supported reviewed interaction evidence.
- [ ] Keep unknown appearances, unresolved quest/dynamic state, conflicting Script Resolution and unsupported interactions blocked.
- [ ] Require reviewed interaction semantics for transition edges used by an executable route.
- [ ] Emit exact resolved interaction evidence on the route-plan edge where the conditional crossing/transition is used.
- [ ] Pin the exact interaction-registry SHA-256 in route-plan provenance when it influences executability.
- [ ] Provide the programme fixture: strict route unavailable, optimistic route can cross an unknown barrier or a reviewed door, executable BFS selects only a fully reviewed path, and removing interaction evidence makes the route non-executable.
- [ ] Keep existing route-plan deterministic/full-path fail-closed behavior.
- [ ] Update the route-plan schema/docs plus catalogue/changelog for the changed reusable interface.
- [ ] Apply `ci:final-gate` before the final checkpoint commit and merge only on green exact-final-head checks.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19T11:58:00+02:00
head: ""
branch: feat/otbm-e2e-001b-executable-routing
pr: null
status: implementing
context_routes:
  - agent-governance
  - otbm
owned_paths:
  - docs/agents/tasks/active/CAN-20260719-otbm-e2e-001b-executable-routing.md
  - tools/ai-agent/otbm_reachability_graph.py
  - tools/ai-agent/otbm_reachability_analysis.py
  - tools/ai-agent/otbm_reachability.py
  - tools/ai-agent/otbm_reachability_tool.py
  - tools/ai-agent/test_otbm_reachability_executable.py
  - docs/ai-agent/OTBM_E2E_ROUTE_PLAN.md
  - docs/ai-agent/OTBM_E2E_ROUTE_PLAN.schema.json
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - OTBM-E2E-001 merged as PR #567 and publishes canary-otbm-e2e-route-plan-v1 from the existing Reachability BFS/predecessor graph
  - OTBM-E2E-003 merged as PR #572 and publishes canary-otbm-route-interactions-v1 with deterministic fail-closed resolution
  - programme requires executable routing to reuse the same existing _bfs() and forbids treating plain optimistic walkability as executable
  - current _bfs() chooses strict versus optimistic TileState predicates and retains transition_id on predecessor edges
  - current route-plan exporter blocks all conditional routes and all routes containing unresolved transition interaction semantics
  - no open PR was found claiming OTBM-E2E-001B or otbm_reachability paths at task start
  - repository writes are restricted to blakinio/canary
  - lifecycle cleanup PR #579 for merged PR #572 is separate; auto-merge is enabled and this task does not manually archive that record
  - no OTBM, WIDX, items.otb, client assets or tools/e2e changes are in scope
unknown:
  - exact final implementation head and CI evidence
conflicts: []
blockers: []
first_failure: null
rejected_hypotheses:
  - add another BFS/A*/Dijkstra implementation
  - treat optimistic unknown appearances as executable
  - infer door or transition behavior from sprite/item names
  - modify Universal Physical E2E execution in this work package
changed_paths:
  - docs/agents/tasks/active/CAN-20260719-otbm-e2e-001b-executable-routing.md
validation:
  - command: live programme/dependency/ownership preflight
    result: PASS
    evidence: PR #567 and PR #572 are merged; no open overlapping OTBM-E2E-001B/reachability PR found
next_action: Open the draft PR, then implement the smallest executable edge-policy extension around the existing Reachability _bfs() and add focused fixtures.
```
