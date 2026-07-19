---
task_id: CAN-20260719-e2e-route-001-follow-route
program_id: CAN-PROGRAM-OTBM-E2E-ROUTING
coordination_id: E2E-ROUTE-001
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/e2e-route-001-follow-route
base_branch: main
created: 2026-07-19
updated: 2026-07-19
last_verified_commit: "3ba5e990aa7d3834c6605d347f7a19f7f0188077"
risk: medium
related_issue: ""
related_pr: "589"
depends_on:
  - merged PR #567 canary-otbm-e2e-route-plan-v1
  - merged PR #572 canary-otbm-route-interactions-v1
  - merged PR #573 exact walk_edge movement primitive
  - merged PR #580 executable interaction-aware routing
blocks:
  - OTBM-E2E-005 reference physical route integration
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260719-e2e-route-001-follow-route.md
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/route_plan_execution.py
    - tools/e2e/client/agent_e2e_scenario.lua
    - tools/e2e/client/agent_e2e_route.lua
    - tests/e2e/test_agent_e2e_scenario_plan.py
    - tests/e2e/test_exact_movement_edges.py
    - tests/e2e/test_follow_route_execution.py
    - tests/lua/test_agent_e2e_route.lua
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
    - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
  read_only:
    - .github/workflows/**
    - tools/e2e/run_physical_e2e.sh
    - tools/ai-agent/otbm_reachability*.py
    - docs/ai-agent/OTBM_E2E_ROUTE_PLAN.schema.json
    - docs/ai-agent/OTBM_ROUTE_INTERACTIONS.schema.json
modules_touched:
  - Universal OTS E2E physical gameplay action execution
reuses:
  - tools/e2e/run_agent_e2e.py canonical scenario validation/materialization
  - tools/e2e/client/agent_e2e_scenario.lua controlled-client driver
  - one shared exact movement-edge executor used by walk_edge and follow_route
  - existing evidence marker stream and safe logout/persistence/relog lifecycle
  - canary-otbm-e2e-route-plan-v1
  - canary-otbm-route-interactions-v1
public_interfaces:
  - follow_route physical action
cross_repo_tasks: []
---

# Goal

Add one reusable `follow_route` action to the existing Universal Physical E2E action layer. It consumes only a validated generated route-plan artifact materialized by the canonical runner lifecycle, executes exact movement edges and supported reviewed interactions through the controlled OTClient, and preserves the existing two-session logout/persistence/relog lifecycle.

# Acceptance criteria

- [x] Scenario references a logical route ID, never an arbitrary filesystem path.
- [x] Runner validates and materializes supported `canary-otbm-e2e-route-plan-v1` data into the canonical `scenario-plan.lua` artifact.
- [x] Unsupported interaction activation fails before physical client execution.
- [x] Every walk edge asserts exact source, derives one movement request from coordinate delta, waits for exact destination, and fails on first timeout/divergence.
- [x] `use-map-item` uses the verified maintained OTClient API against an exact map tile/item.
- [x] `use-inventory-on-map` uses the verified maintained OTClient API against an exact map tile/item.
- [x] Transition source and destination are asserted exactly with bounded timeout and deterministic first-failure diagnostics.
- [x] Deterministic per-route-step evidence markers are emitted in the existing evidence stream.
- [ ] Existing non-route scenarios remain backward compatible.
- [x] Existing safe logout/persistence/relog sentinel is unchanged.
- [ ] Focused tests cover success materialization, movement divergence, wrong transition destination, unsupported interaction fail-fast, and backward compatibility.
- [ ] `ci:final-gate` is applied before the final checkpoint commit.
- [ ] Exact-final-head required checks pass before squash merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19
head: 3ba5e990aa7d3834c6605d347f7a19f7f0188077
branch: feat/e2e-route-001-follow-route
pr: 589
status: validating
context_routes:
  - universal-e2e
  - otbm
  - cross-repo
  - agent-governance
owned_paths:
  - tools/e2e/run_agent_e2e.py
  - tools/e2e/route_plan_execution.py
  - tools/e2e/client/agent_e2e_scenario.lua
  - tools/e2e/client/agent_e2e_route.lua
  - tests/e2e/test_agent_e2e_scenario_plan.py
  - tests/e2e/test_exact_movement_edges.py
  - tests/e2e/test_follow_route_execution.py
  - tests/lua/test_agent_e2e_route.lua
proven:
  - live main equals handover SHA 0db6289cc55069ddb0194a58758bcc97c242bf8b
  - no pre-existing open PR or branch claimed E2E-ROUTE-001
  - PR #589 owns feat/e2e-route-001-follow-route
  - PR #573 exact walk_edge and follow_route now delegate to one shared exact movement-edge executor
  - canonical route selection derives route-<logical-id>.json only from the runner-owned artifact directory
  - route plan hash, provenance hashes, executable status, blockers, path continuity, edge semantics, and interaction activation are validated fail-closed before client execution
  - plain optimistic routing is rejected for physical execution
  - deterministic Lua route fixtures exercise exact movement success, divergence, bounded timeout, wrong transition destination, use-map-item, and use-inventory-on-map
  - existing Lua Tests job also executes the focused Python E2E route contract suites without introducing a new workflow
  - maintained OTClient revision 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f binds g_game.use and g_game.useInventoryItemWith and exposes exact tile/item lookup primitives
  - no parser, World Index, pathfinder, runner, workflow, map, widx, items.otb, or client asset was added or modified
unknown: []
conflicts: []
blockers: []
next_action: Run live CI and focused tests, repair actual failures, then update shared module/changelog records, apply ci:final-gate, and create the final checkpoint commit.
```
