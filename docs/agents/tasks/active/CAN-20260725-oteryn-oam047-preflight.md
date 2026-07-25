---
task_id: CAN-20260725-oteryn-oam047-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-047
status: review
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-047-lua-runtime-governance
base_branch: main
created: 2026-07-25
updated: 2026-07-25
last_verified_commit: "9ca36f79483e9ade00fae0fc407e7b68f29bf00e"
risk: high
related_issue: ""
related_pr: "928"
depends_on:
  - OAM-046 durably completed as 2b09ef1acfe23d1ef4027c85f44b0093420d7434
blocks:
  - OAM-047 Canary governance and lifecycle
  - OAM-047 durable program reconciliation
  - OAM-048 start
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260725-oteryn-oam047-preflight.md
    - docs/agents/OTERYN_OAM_047_LUA_RUNTIME_REVALIDATION.md
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/real-tibia/registry/modules/lua-runtime.yaml
modules_touched:
  - oteryn-architecture-migration
  - lua-runtime
cross_repo_tasks:
  - Otheryn PR 107 feature merge 5b3bee0dd6eedf8c2f9578c686ca85c0fde519cf
  - Otheryn PR 108 lifecycle merge 68e2b233b02356a79a03422ed51d757b85915bc5
---

# OAM-047 Lua Runtime governance

## Final disposition

`lua-runtime → ADAPT`

The shared Lua architecture remains suitable. Main-state replacement required one bounded adaptation so attached child script interfaces no longer retain pointers and registry references belonging to the closed state.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T20:18:00+02:00
head: 9ca36f79483e9ade00fae0fc407e7b68f29bf00e
branch: dudantas/oam-047-lua-runtime-governance
pr: 928
status: validating
context_routes:
  - agent-governance
  - cross-repo
  - lua-runtime
owned_paths:
  - docs/agents/tasks/active/CAN-20260725-oteryn-oam047-preflight.md
  - docs/agents/OTERYN_OAM_047_LUA_RUNTIME_REVALIDATION.md
proven:
  - OAM-046 durable reconciliation merged as 2b09ef1acfe23d1ef4027c85f44b0093420d7434 before OAM-047.
  - Canary preflight PR 922 selected dependency-valid lua-runtime and merged as bc8d7827f652b8b8b3200f7ef81818e8d5d149f5.
  - Otheryn task-start main was 415f559f829c83d79d9c609e7f421d2449e59d74 and reviewed upstream was 7323503b3dc61ed86bf1f04a611b2d0aec64b35a.
  - Child LuaScriptInterface objects retained the shared main lua_State and event-table references while reInitState closed and replaced that state without child inventory.
  - The adaptation inventories only registered children attached to the old state, closes their registry tables and rebinds them after replacement-state creation.
  - Focused fixtures cover active children, stale registry IDs, new event registration, dormant interfaces, destroyed interfaces and the shared test interface.
  - The first final-head CI isolated a CMake-only translation-unit registration defect in the maintained Visual Studio Solution path.
  - Folding the registry into existing lua_environment.cpp preserved one implementation across CMake and Visual Studio without expanding build-system ownership.
  - Final Otheryn head a7349190a51d627e4668af56912337ff8cadec46 passed Autofix 30167797667, CI 30167797744 and Required 30167797642.
  - Windows CMake/Solution, Linux release/debug, macOS, Docker, Lua tests, focused tests and runtime smokes passed on the final attempt.
  - PR 107 had clean discussions and zero target-main drift and merged as 5b3bee0dd6eedf8c2f9578c686ca85c0fde519cf.
  - Otheryn lifecycle PR 108 passed Required 30169112582, had clean discussions and merged as 68e2b233b02356a79a03422ed51d757b85915bc5.
  - Canary governance PR 928 opened from task-start main 124b029d1a2498a64fa6612b16efa386b8786a83 with exactly the task and package report paths.
derived:
  - lua-runtime requires ADAPT rather than REUSE because main-state replacement did not preserve attached child-interface validity.
  - The correction remains inside shared Lua lifecycle and does not own feature-specific script reload policy.
unknown:
  - Complete production subsystem reload ordering and callback timing.
  - Concurrent reload/read/callback safety and race freedom.
  - Exhaustive userdata, timer parameter and external wrapper lifetime safety.
  - Physical-client, protocol and production gameplay effects.
conflicts: []
first_failure:
  marker: untracked-child-interface-reset
  evidence: LuaEnvironment::reInitState closed the main state while attached child interfaces retained pointers and registry IDs unless separately reinitialized.
rejected_hypotheses:
  - Finalize REUSE from source identity or compilation alone.
  - Reload all gameplay scripts inside the main-state primitive.
  - Expand into feature bindings, userdata redesign or concurrent reload orchestration.
  - Edit Visual Studio project ownership when an existing supported translation unit is sufficient.
  - Claim physical-client or production safety from focused lifecycle proof.
changed_paths:
  - docs/agents/tasks/active/CAN-20260725-oteryn-oam047-preflight.md
  - docs/agents/OTERYN_OAM_047_LUA_RUNTIME_REVALIDATION.md
validation:
  - command: exact target/upstream/legacy lifecycle review
    result: PASS
    evidence: Task-start roots, child-interface state ownership and target-specific LuaEnvironment deltas are recorded in the governance report.
  - command: focused child-interface lifecycle contract
    result: PASS
    evidence: Final CI 30167797744 compiled and executed the OAM-047 fixtures.
  - command: maintained cross-platform builds and runtime smokes
    result: PASS
    evidence: Final CI passed Windows CMake/Solution, Linux release/debug, macOS, Docker and runtime smokes.
  - command: Otheryn exact-head gates, audit and lifecycle
    result: PASS
    evidence: Feature and lifecycle PRs passed their required gates, had clean discussions and merged as recorded above.
  - command: Canary governance exact-head gates
    result: NOT_RUN
    evidence: PR 928 must pass on the synchronized exact head.
blockers:
  - Canary governance exact-head Ownership and CI
  - clean discussion and Canary-main drift audit
  - governance merge, Canary lifecycle archive and durable program reconciliation
next_action: Require exact-head Ownership and CI on PR 928, audit discussions and Canary-main drift, then merge and finish lifecycle plus durable reconciliation before OAM-048.
```
