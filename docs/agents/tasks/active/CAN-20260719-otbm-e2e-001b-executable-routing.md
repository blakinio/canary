---
task_id: CAN-20260719-otbm-e2e-001b-executable-routing
program_id: CAN-PROGRAM-OTBM-E2E-ROUTING
coordination_id: OTBM-E2E-001B
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/otbm-e2e-001b-executable-routing
base_branch: main
created: 2026-07-19T11:58:00+02:00
updated: 2026-07-19T12:22:00+02:00
last_verified_commit: "7b3818fada2f998f25d2b2675a44531079784b6a"
risk: medium
related_issue: ""
related_pr: "580"
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
    - .github/workflows/otbm-reachability.yml
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

- [x] Reuse the existing `_bfs()` traversal; do not add another pathfinder.
- [x] Preserve existing strict and optimistic Reachability report behavior when executable interaction routing is not requested.
- [x] Add an executable movement/edge policy equivalent to strict walkability OR an exact conditional crossing with supported reviewed interaction evidence.
- [x] Keep unknown appearances, unresolved quest/dynamic state, conflicting Script Resolution and unsupported interactions blocked.
- [x] Require reviewed interaction semantics for transition edges used by an executable route.
- [x] Emit exact resolved interaction evidence on the route-plan edge where the conditional crossing/transition is used.
- [x] Pin the exact interaction-registry SHA-256 in route-plan provenance when it influences executability.
- [x] Provide the programme fixture: strict route unavailable, optimistic route can cross an unknown barrier or a reviewed door, executable BFS selects only a fully reviewed path, and removing interaction evidence makes the route non-executable.
- [x] Keep existing route-plan deterministic/full-path fail-closed behavior.
- [ ] Update the route-plan schema/docs plus catalogue/changelog for the changed reusable interface.
- [ ] Apply `ci:final-gate` before the final checkpoint commit and merge only on green exact-final-head checks.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19T12:22:00+02:00
head: 7b3818fada2f998f25d2b2675a44531079784b6a
branch: feat/otbm-e2e-001b-executable-routing
pr: 580
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
  - .github/workflows/otbm-reachability.yml
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - OTBM-E2E-001 merged as PR #567 and publishes canary-otbm-e2e-route-plan-v1 from the existing Reachability BFS/predecessor graph
  - OTBM-E2E-003 merged as PR #572 and publishes canary-otbm-route-interactions-v1 with deterministic fail-closed resolution
  - programme requires executable routing to reuse the same existing _bfs() and forbids treating plain optimistic walkability as executable
  - PR #580 is the same-repository draft PR for this task with base main and head feat/otbm-e2e-001b-executable-routing
  - _bfs() remains the only traversal and now accepts an optional movement-edge predicate without changing default strict/optimistic behavior
  - validated transition edges accept an optional directional executable predicate while preserving existing strict/optimistic eligibility
  - interaction-aware routing builds a narrower executable edge set and reruns the same _bfs() rather than introducing another pathfinder
  - unknown appearances are rejected before registry lookup and therefore cannot be promoted by a reviewed selector
  - exact conditional blocker placements must all resolve executable; AID/UID barriers additionally require an explicit safe Script Resolution status
  - transition edges require exact reviewed transition-ID semantics and fail closed on unresolved dynamic/script uncertainty
  - executable route-plan edges retain exact interaction-resolution evidence and interaction-registry provenance
  - focused fixtures cover a shorter unsafe optimistic path versus a longer reviewed-door path, missing door evidence, unknown appearance fail-closed behavior, reviewed/unreviewed teleports, unresolved AID state and determinism
  - route-plan CLI accepts optional --interactions and validates the reviewed registry against exact source-map and World Index provenance before executable routing
  - route-plan schema/docs now describe executable routing mode, executableDistance and edge-level interaction evidence
  - existing OTBM Reachability workflow now executes and compiles test_otbm_reachability*.py, validates the route-plan schema and packages the route-interaction runtime dependency instead of leaving the new fixtures unexecuted
  - no open PR was found claiming OTBM-E2E-001B or otbm_reachability paths at task start
  - repository writes are restricted to blakinio/canary
  - lifecycle cleanup PR #579 for merged PR #572 is separate; auto-merge is enabled and this task does not manually archive that record
  - no OTBM, WIDX, items.otb, client assets or tools/e2e changes are in scope
unknown:
  - focused workflow results for the current implementation head are queued
  - final shared catalogue/changelog update and exact final implementation head
conflicts: []
blockers: []
first_failure: {}
rejected_hypotheses:
  - add another BFS/A*/Dijkstra implementation
  - treat optimistic unknown appearances as executable
  - infer door or transition behavior from sprite/item names
  - modify Universal Physical E2E execution in this work package
changed_paths:
  - .github/workflows/otbm-reachability.yml
  - docs/agents/tasks/active/CAN-20260719-otbm-e2e-001b-executable-routing.md
  - docs/ai-agent/OTBM_E2E_ROUTE_PLAN.md
  - docs/ai-agent/OTBM_E2E_ROUTE_PLAN.schema.json
  - tools/ai-agent/otbm_reachability.py
  - tools/ai-agent/otbm_reachability_analysis.py
  - tools/ai-agent/otbm_reachability_graph.py
  - tools/ai-agent/otbm_reachability_tool.py
  - tools/ai-agent/test_otbm_reachability_executable.py
validation:
  - command: live programme/dependency/ownership preflight
    result: PASS
    evidence: PR #567 and PR #572 are merged; no open overlapping OTBM-E2E-001B/reachability PR found
  - command: changed-file scope review on PR #580 before CI workflow update
    result: PASS
    evidence: implementation changes stayed inside task/Reachability/route-plan paths with no tools/e2e, OTBM, WIDX, items.otb or asset paths
  - command: OTBM Reachability workflow coverage review
    result: PASS
    evidence: existing workflow was extended in place to execute the new focused fixture file, validate route-plan schema syntax and package otbm_route_interactions.py; no second workflow was created
next_action: Read focused workflow results, repair any exact failures, then update shared catalogue/changelog, apply ci:final-gate and create the final task checkpoint commit.
```
