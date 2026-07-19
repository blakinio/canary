---
task_id: CAN-20260719-e2e-route-001-follow-route
program_id: CAN-PROGRAM-OTBM-E2E-ROUTING
coordination_id: E2E-ROUTE-001
status: ready
agent: "GPT-5.5 Thinking"
branch: feat/e2e-route-001-follow-route
base_branch: main
created: 2026-07-19
updated: 2026-07-19
last_verified_commit: "bb9e5334cee9a4e1e53857073ff7e8d82cdd91f7"
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
- [x] Existing non-route scenarios remain backward compatible.
- [x] Existing safe logout/persistence/relog sentinel is unchanged.
- [x] Focused tests cover success materialization, movement divergence, wrong transition destination, unsupported interaction fail-fast, and backward compatibility.
- [x] `ci:final-gate` is applied before the final checkpoint commit.
- [ ] Exact-final-head required checks pass before squash merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19
head: bb9e5334cee9a4e1e53857073ff7e8d82cdd91f7
branch: feat/e2e-route-001-follow-route
pr: 589
status: ready
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
  - live main equaled handover SHA 0db6289cc55069ddb0194a58758bcc97c242bf8b at work-package preflight and remained unchanged through pre-final validation
  - no pre-existing open PR or branch claimed E2E-ROUTE-001 at work-package preflight
  - PR #589 owns feat/e2e-route-001-follow-route
  - PR #573 exact walk_edge and follow_route delegate to one shared exact movement-edge executor
  - canonical route selection derives route-<logical-id>.json only from the runner-owned artifact directory
  - route plan hash, provenance hashes, executable status, blockers, path continuity, edge semantics, and interaction activation are validated fail-closed before client execution
  - plain optimistic routing is rejected for physical execution
  - deterministic Lua route fixtures exercise exact movement success, divergence, bounded timeout, wrong transition destination, use-map-item, and use-inventory-on-map
  - existing Lua Tests job executes the focused Python E2E route contract suites without introducing a new workflow
  - maintained OTClient revision 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f binds g_game.use and g_game.useInventoryItemWith and exposes exact tile/item lookup primitives
  - step-on transitions preserve the exact-edge contract by requiring the movement destination/transition source to be observed before waiting for automatic relocation
  - pre-final head bb9e5334cee9a4e1e53857073ff7e8d82cdd91f7 passed Agent Task Ownership, full CI/Required, focused Lua/Python route tests, and Universal Agent E2E
  - no parser, World Index, pathfinder, runner, workflow, map, widx, items.otb, or client asset was added or modified
derived:
  - the controlled client executes only the normalized route runtime contract emitted after host-side validation, not arbitrary manifest paths or unvalidated route JSON
  - standalone walk_edge and follow_route cannot diverge into separate movement semantics because both call the same Lua exact-edge executor
unknown:
  - exact-final-head CI, Required, ownership, and Universal Agent E2E results are pending on the final checkpoint commit
conflicts: []
rejected_hypotheses:
  - arbitrary route file paths were rejected in favor of the documented route-<logical-id>.json canonical evidence layout
  - a second movement primitive was rejected; follow_route reuses the same exact-edge executor as walk_edge
  - workflow modification was rejected; focused route tests run through the existing Lua Tests workflow
  - bypassing exact movement destination observation for immediate step-on transitions was rejected because it would violate the required P0-to-P1 synchronization contract
changed_paths:
  - docs/agents/tasks/active/CAN-20260719-e2e-route-001-follow-route.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
  - tools/e2e/run_agent_e2e.py
  - tools/e2e/route_plan_execution.py
  - tools/e2e/client/agent_e2e_scenario.lua
  - tools/e2e/client/agent_e2e_route.lua
  - tests/e2e/test_agent_e2e_scenario_plan.py
  - tests/e2e/test_exact_movement_edges.py
  - tests/e2e/test_follow_route_execution.py
  - tests/lua/test_agent_e2e_route.lua
blockers: []
first_failure:
  marker: Agent Task Ownership / Validate changed active task checkpoints
  evidence: Run 29687894902 failed because the task checkpoint did not yet contain the complete required checkpoint schema; the checkpoint schema was completed without weakening the validator and subsequent ownership validation passed.
validation:
  - command: Agent Task Ownership on head bb9e5334cee9a4e1e53857073ff7e8d82cdd91f7
    result: PASS
    evidence: Workflow run 29688305177 completed successfully.
  - command: CI / Required on head bb9e5334cee9a4e1e53857073ff7e8d82cdd91f7
    result: PASS
    evidence: Workflow run 29688305256 completed successfully, including full required platform builds and Lua Tests.
  - command: CI / Lua Tests / Run Lua Tests on head bb9e5334cee9a4e1e53857073ff7e8d82cdd91f7
    result: PASS
    evidence: The existing Lua Tests job passed deterministic route fixtures and the three focused Python E2E route contract suites.
  - command: Universal Agent E2E on head bb9e5334cee9a4e1e53857073ff7e8d82cdd91f7
    result: PASS
    evidence: Workflow run 29688305269 completed the controlled Canary/MariaDB/OTClient physical login-safe-logout-persistence-relog lifecycle successfully.
next_action: Wait for exact-final-head Agent Task Ownership, CI/Required, focused Lua/Python route tests, and Universal Agent E2E on this final checkpoint commit; if all remain green and no review blocker appears, squash merge PR #589 with no further feature-branch commit.
```
