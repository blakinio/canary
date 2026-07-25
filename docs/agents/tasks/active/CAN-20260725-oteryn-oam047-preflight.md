---
task_id: CAN-20260725-oteryn-oam047-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-047
status: review
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-047-lua-runtime-preflight
base_branch: main
created: 2026-07-25
updated: 2026-07-25
last_verified_commit: "8838a3ff743cdc4879c6652d60251ce92032fccd"
risk: high
related_issue: ""
related_pr: "922"
depends_on:
  - OAM-046 durably completed as 2b09ef1acfe23d1ef4027c85f44b0093420d7434
blocks:
  - OAM-047 Otheryn target proof
  - OAM-048 start
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260725-oteryn-oam047-preflight.md
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/real-tibia/registry/modules/lua-runtime.yaml
modules_touched:
  - oteryn-architecture-migration
  - lua-runtime
cross_repo_tasks: []
---

# OAM-047 fresh preflight: Lua Runtime

## Selection

Canonical package: `lua-runtime`

Initial disposition: `REVALIDATE`

The package has no canonical dependencies, owns the shared `src/lua/**` runtime boundary and is narrower than the dependency-valid `build-system` package. Completing it also unblocks the separate `gameplay-analytics` dependency. This preflight does not infer `REUSE` from source identity or successful unrelated gameplay tests.

## Fresh live-state preflight

- Canary task-start main: `c468be4c34039b4b3e9f4e320c4b125cb6998d77`.
- Otheryn target main: `415f559f829c83d79d9c609e7f421d2449e59d74`.
- reviewed current upstream: `opentibiabr/canary@7323503b3dc61ed86bf1f04a611b2d0aec64b35a`.
- OAM-046 durable completion: `2b09ef1acfe23d1ef4027c85f44b0093420d7434`.
- Otheryn has no open pull request.
- Open Canary PRs do not own `src/lua/**` or this checkpoint. In particular PR `#514` owns security workflow/runtime fixtures, PR `#921` owns Real Tibia owner-request tooling, and the active E2E/map/docs PRs remain outside the Lua runtime paths.

## Candidate evaluation

- `network-transport` remains collision-blocked by open Canary PR `#514`.
- `login-protocol` remains dependency-invalid because it depends on `network-transport`.
- `physical-client-e2e` remains active under the separate E2E Automation Program.
- `gameplay-analytics` is dependency-invalid until `lua-runtime` completes.
- `deployment-operations` is dependency-invalid until `build-system` completes.
- `build-system` has no dependencies but owns broad CMake, vcpkg, Visual Studio and CI entry points. `lua-runtime` is selected first as the narrower runtime package and the direct prerequisite for gameplay analytics.

## Exact reviewed roots

- canonical registry blob: `10040d899de61dd0f0e6aa80d68d040c34f92847`.
- target/upstream/live-legacy `src/lua/CMakeLists.txt`: `6c4ca0fb88057c4760d118e61f416a987338b17e`.
- target/upstream/live-legacy `src/lua/scripts/CMakeLists.txt`: `d7c8525af3fd29a01e0cbb6fc04a1371eea6e90c`.
- target/upstream/live-legacy `src/lua/scripts/luascript.hpp`: `e65ac8fab062491a8d60a951d38ff6b57e025f4a`.
- target/upstream/live-legacy `src/lua/scripts/luascript.cpp`: `2bbfed787aaa39f63f11a69165e9d47fca8aa067`.
- target `src/lua/scripts/lua_environment.hpp`: `9e5d8d8b5224eed6f23da01d99bd9f2f419aaeda`; reviewed upstream header: `4ce01411f23f120040d5bfd4fdb4bc39929be401`.
- target `src/lua/scripts/lua_environment.cpp`: `060a735293a5b89abe98e58a40000d9b264818f9`; reviewed upstream and live legacy implementation: `c28c3a77824fc7fc997940921b039a3eeca1a6ce`.

The target-specific Lua environment variant adds shutdown guards, `reloadCore()` and an idempotent `shutdown()` path. It nevertheless retains the inherited `LuaEnvironment::reInitState()` TODO to discover and reload child interfaces.

## First bounded failure candidate

Every ordinary `LuaScriptInterface::initState()` stores the shared main `lua_State*` and creates a registry event table. `LuaEnvironment::reInitState()` currently closes that shared state and creates a new one without inventorying, invalidating or reinitializing child interfaces. The explicit source TODO is therefore a real ownership/lifetime gap candidate, not proof of a crash in every reload path.

Marker: `untracked-child-interface-reset`.

## Canonical boundary

Includes:

- shared Lua state and environment lifecycle;
- script-interface initialization and teardown;
- runtime callback ownership boundaries;
- reload and shutdown safety inventory.

Excludes:

- individual gameplay scripts;
- feature-specific Lua registration families;
- a separate package for every binding family;
- arbitrary Lua execution by analytics or AI systems;
- object-lifetime, serialization, race-freedom or reload-safety claims without focused evidence.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T15:46:00+02:00
head: 8838a3ff743cdc4879c6652d60251ce92032fccd
branch: dudantas/oam-047-lua-runtime-preflight
pr: 922
status: validating
context_routes:
  - agent-governance
  - cross-repo
  - lua-runtime
owned_paths:
  - docs/agents/tasks/active/CAN-20260725-oteryn-oam047-preflight.md
proven:
  - OAM-046 is durably complete as 2b09ef1acfe23d1ef4027c85f44b0093420d7434.
  - The canonical lua-runtime record has no dependencies and owns src/lua/** while excluding individual gameplay scripts and feature-specific registration families.
  - Otheryn has no open pull request and current open Canary PRs do not own src/lua/**.
  - The compiled Lua and scripts CMake roots plus LuaScriptInterface header/implementation are byte-identical across target, reviewed upstream and live legacy.
  - The target LuaEnvironment variant has additional shutdown/reloadCore guards but retains the inherited child-interface reload TODO.
  - Child LuaScriptInterface instances store the shared main lua_State pointer and registry references, while the main reInitState closes and replaces the state without child inventory.
derived:
  - lua-runtime is the next narrower dependency-valid canonical package.
  - The child-interface reset boundary requires focused target proof before final REUSE, ADAPT or DO_NOT_MIGRATE disposition.
unknown:
  - Which production reload sequences reinitialize every child interface after the main state changes.
  - Whether any child callback can execute between main-state replacement and subsystem-specific reload.
  - Complete userdata, callback and registry-reference lifetime safety across reload and shutdown.
  - Concurrent reload/callback behavior, thread safety and race freedom.
  - Exhaustive runtime behavior of feature-specific binding families outside this package.
conflicts: []
first_failure:
  marker: untracked-child-interface-reset
  evidence: LuaEnvironment::reInitState closes and recreates the shared state while source retains an explicit TODO to get/reload children; child interfaces retain shared-state pointers and registry refs unless separately reinitialized.
rejected_hypotheses:
  - Select network-transport while PR 514 owns related validation surfaces.
  - Select login-protocol before network-transport is dependency-complete.
  - Select gameplay-analytics before lua-runtime is complete.
  - Infer Lua runtime reuse from byte-identical interface roots, compilation or unrelated gameplay tests.
  - Expand the preflight into every feature-specific Lua registration or individual gameplay script.
changed_paths:
  - docs/agents/tasks/active/CAN-20260725-oteryn-oam047-preflight.md
validation:
  - command: fresh live main, open-PR and ownership review
    result: PASS
    evidence: Exact live baselines and active PR path ownership were reviewed after durable OAM-046 closure.
  - command: canonical dependency and scope review
    result: PASS
    evidence: lua-runtime has no dependencies, is narrower than build-system and directly unblocks gameplay-analytics.
  - command: exact compiled-root and lifecycle-source review
    result: PASS
    evidence: CMake, LuaScriptInterface and LuaEnvironment blobs plus the child-reset TODO are pinned above.
blockers:
  - Canary preflight exact-head gates and merge
next_action: Mark PR 922 ready, require exact-head Ownership and CI, audit discussions and main drift, then squash-merge before target work starts.
```
