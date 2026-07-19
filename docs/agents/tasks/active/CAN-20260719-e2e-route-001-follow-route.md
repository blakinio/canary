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
last_verified_commit: "0db6289cc55069ddb0194a58758bcc97c242bf8b"
risk: medium
related_issue: ""
related_pr: ""
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
    - tools/e2e/client/agent_e2e_scenario.lua
    - tests/e2e/test_agent_e2e_scenario_plan.py
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
  - walk_edge exact movement primitive from PR #573
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

- [ ] Scenario references a logical route ID, never an arbitrary filesystem path.
- [ ] Runner validates and materializes supported `canary-otbm-e2e-route-plan-v1` data into the canonical `scenario-plan.lua` artifact.
- [ ] Unsupported interaction activation fails before physical client execution.
- [ ] Every walk edge asserts exact source, derives one movement request from coordinate delta, waits for exact destination, and fails on first timeout/divergence.
- [ ] `use-map-item` uses the verified maintained OTClient API against an exact map tile/item.
- [ ] `use-inventory-on-map` uses the verified maintained OTClient API against an exact map tile/item.
- [ ] Transition source and destination are asserted exactly with bounded timeout and deterministic first-failure diagnostics.
- [ ] Deterministic per-route-step evidence markers are emitted in the existing evidence stream.
- [ ] Existing non-route scenarios remain backward compatible.
- [ ] Existing safe logout/persistence/relog sentinel is unchanged.
- [ ] Focused tests cover success materialization, movement divergence, wrong transition destination, unsupported interaction fail-fast, and backward compatibility.
- [ ] `ci:final-gate` is applied before the final checkpoint commit.
- [ ] Exact-final-head required checks pass before squash merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19
head: 0db6289cc55069ddb0194a58758bcc97c242bf8b
branch: feat/e2e-route-001-follow-route
pr: null
status: preflight-complete
context_routes:
  - universal-e2e
  - otbm
  - cross-repo
  - agent-governance
owned_paths:
  - tools/e2e/run_agent_e2e.py
  - tools/e2e/client/agent_e2e_scenario.lua
  - tests/e2e/test_agent_e2e_scenario_plan.py
proven:
  - live main equals handover SHA 0db6289cc55069ddb0194a58758bcc97c242bf8b
  - no open PR or branch already claims E2E-ROUTE-001
  - PR #573 is merged and provides exact walk_edge source/destination synchronization
  - open PR #586 treats run_agent_e2e.py and agent_e2e_scenario.lua as read-only; its shared documentation/catalogue ownership is logically separate
  - maintained OTClient revision 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f binds g_game.use, g_game.useWith, g_game.useInventoryItem, and g_game.useInventoryItemWith to Lua
  - maintained OTClient Tile bindings expose g_map.getTile plus Tile.getItems/getTopUseThing/getTopMultiUseThing
  - implementation will reuse the canonical runner and will not add a parser, pathfinder, runner, workflow, or map asset
unknown:
  - exact focused implementation shape until current route-plan schema fields are inspected
conflicts: []
blockers: []
next_action: Open draft PR, bind related_pr, inspect exact merged route-plan schema, then implement the smallest reusable follow_route bridge and focused tests.
```
