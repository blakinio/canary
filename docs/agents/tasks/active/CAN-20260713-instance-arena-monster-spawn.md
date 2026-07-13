---
task_id: CAN-20260713-instance-arena-monster-spawn
program_id: CAN-PROGRAM-INSTANCED-TEST-ARENA
coordination_id: ""
status: ready_for_pr
agent: "Claude"
branch: feat/instance-arena-monster-spawn
base_branch: main
created: 2026-07-13T22:00:00Z
updated: 2026-07-13T22:35:00Z
last_verified_commit: "d9b10c322cd6bb9690c2a29fd3354082dde066f9"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - CAN-20260713-instance-arena-talkaction (player session API, PR #295)
blocks:
  - CAN-PROGRAM-INSTANCED-TEST-ARENA queue item 5 (instance-scoped delayed events + timeout/cleanup)
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260713-instance-arena-monster-spawn.md
  shared:
    - src/game/instance/instance_arena_service.hpp
    - src/game/instance/instance_arena_service.cpp
    - tests/unit/game/instance/instance_arena_service_test.cpp
    - src/game/game.hpp
    - src/game/game.cpp
    - src/creatures/monsters/monster.cpp
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/programs/INSTANCED_TEST_ARENA_PROGRAM.md
    - docs/architecture/instance-manager.md
    - docs/architecture/CANARY_ENGINE_PROJECT_HANDOFF.md
modules_touched:
  - InstanceArenaService (monster spawn + registration + rollback)
  - Game::getInstanceCreatureBinder() (new narrow accessor)
  - Monster::onThinkDefense() summon call site (now instance-aware)
reuses:
  - InstanceCreatureBinder::bind()/getRegisteredCreatureIds() (existing)
  - InstanceManager::setCleanupCallback() (existing)
  - Creature::setMaster(master, InstanceCreatureBinder&, reload) (existing, tested overload - PR #174/earlier)
  - Game::removeCreature() auto-unregister hook (existing, PR #231)
public_interfaces:
  - InstanceArenaService::EnterResult::monsterId
  - InstanceArenaService::MonsterName
  - InstanceArenaService(manager, MonsterFactory, CreatureRemover) (test-only DI constructor)
  - Game::getInstanceCreatureBinder()
---

# Goal

Make the arena a real gameplay scenario, not just an empty reserved box: spawn
and register one real monster per arena instance, and make the engine's one
summon-creation call site instance-aware so any summon that monster makes
inherits its owner through the existing binder.

# Acceptance criteria

- [x] `enterArena()` spawns one real monster (`Cave Rat`, chosen for
      datapack consistency with `data-canary/world/canary.otbm`) inside the
      reserved region and registers it with `InstanceCreatureBinder` only
      after it has a real nonzero runtime id.
- [x] Any failure in the spawn/register step (factory returns null, or
      `binder.bind()` fails) rolls back the whole arena: no session is
      created, the instance is closed, the region is freed.
- [x] `InstanceManager::close()` no longer throws
      `"instance cleanup left registered creatures"` when a player's arena
      is closed - `enterArena()` registers a cleanup callback
      (`InstanceManager::setCleanupCallback`) that removes every creature id
      still registered to the instance before `close()`'s invariant check
      runs.
- [x] The single real summon-creation call site
      (`Monster::onThinkDefense()`, `src/creatures/monsters/monster.cpp`)
      now calls the already-tested instance-aware
      `Creature::setMaster(master, InstanceCreatureBinder&, reload)` overload
      instead of the plain one, via a new narrow
      `Game::getInstanceCreatureBinder()` accessor that delegates to the one
      binder `InstanceArenaService` already owns (no second binder created).
- [x] Verified backward-compatible for every normal-world monster: an
      unregistered master makes `InstanceManager::inheritCreatureOwnership()`
      a no-op, so the call is a transparent pass-through to the previous
      plain `setMaster(master, reload)` behavior when the master isn't an
      instance-owned creature (which is every monster today, since nothing in
      production creates an instance except this same feature).
- [x] `InstanceArenaService`'s monster spawn/removal are behind an
      constructor-injected `MonsterFactory`/`CreatureRemover` seam (production
      defaults call real `Monster::createMonster()` +
      `Game::placeCreature()`/`Game::removeCreature()`; tests inject
      synthetic doubles), matching this codebase's established pattern for
      keeping `Game`-touching logic unit-testable without a live server
      bootstrap.
- [x] Focused C++ unit tests added/updated: monster registered with the
      binder after `enterArena()` succeeds; monster-factory failure rolls
      the whole arena back; `closeArenaForPlayer()` drives the injected
      remover and empties the registry so `manager.close()` succeeds without
      throwing.
- [ ] Current-head GitHub checks verified (pending PR open + CI).
- [ ] Module catalogue and architecture docs updated with the merge SHA
      (pending merge).
- [ ] Autonomous merge gate satisfied (pending CI).

# Confirmed context

- `data-canary/monster/mammals/cave_rat.lua` registers `Game.createMonsterType("Cave Rat")`
  in the same datapack (`data-canary`) already selected for the region plan
  in `docs/architecture/instanced-test-arena.md` - a plain, harmless monster
  with no scripted summon behavior of its own, appropriate for a test arena.
- `Monster::onThinkDefense()` (`src/creatures/monsters/monster.cpp`, around
  line 1501) is the only production call site in the entire engine that
  creates a summon and calls `setMaster` on it - confirmed by searching the
  whole `src/` tree for summon-creation patterns paired with `setMaster(`.
- `Creature::setMaster(newMaster, InstanceCreatureBinder&, reloadCreature)`
  (`src/creatures/creature.cpp`) and `InstanceManager::inheritCreatureOwnership()`
  are already merged and already extensively unit-tested
  (`instance_creature_binder_test.cpp`); this task only had to wire the one
  real call site to the existing, tested function - no new binder logic was
  written.
- `InstanceManager::close()` has a hard invariant
  (`instance_manager.cpp`): it throws if any creature id is still registered
  to the instance when cleanup finishes. `enterArena()` now registers a
  cleanup callback via `manager.setCleanupCallback(id, ...)` that enumerates
  `manager.getRegisteredCreatureIds(id)` and calls the injectable
  `creatureRemover` for each - this is what makes `closeArenaForPlayer()`
  safe to call `manager.close()` unconditionally.
- No local build is available in this sandbox (no vcpkg/CMake configure has
  been run; establishing one from scratch is out of scope for this task).
  As with every prior PR in this program, `clang-format --dry-run --Werror`
  was run on every changed/added file (all clean) and correctness was
  verified by close reading and by mirroring already-merged, already-tested
  patterns (`instance_creature_binder_test.cpp`'s `makeRuntimeMonster()`
  helper for the new synthetic test doubles). CI's full compile matrix is
  the first real build/link/test-run confirmation, exactly as documented for
  PRs #201/#231/#233/#289.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| InstanceCreatureBinder / InstanceManager registry | `bind()`, `getRegisteredCreatureIds()`, `setCleanupCallback()` | `src/game/instance/instance_creature_binder.hpp`, `instance_manager.{hpp,cpp}` | Single existing ownership registry; no second one created. |
| `Creature::setMaster(master, binder, reload)` | Called unchanged at the one real summon call site | `src/creatures/creature.cpp`, `src/creatures/monsters/monster.cpp` | Already tested; this task only adds the real caller. |
| `Game::removeCreature()` auto-unregister (#231) | Production `CreatureRemover` default calls `Game::removeCreature()`, which already unregisters | `src/game/game.cpp` | No duplicate unregister logic added. |
| `instance_creature_binder_test.cpp`'s `makeRuntimeMonster()` pattern | Mirrored for the new synthetic-monster test harness | `tests/unit/game/instance/instance_creature_binder_test.cpp` | Established precedent for building real `Monster` objects without a live `Game`. |

# Ownership and overlap check

- Program record: `docs/agents/programs/INSTANCED_TEST_ARENA_PROGRAM.md`.
- Open PRs re-checked before starting: none touch
  `src/game/instance/instance_arena_service.*`, `src/creatures/monsters/monster.cpp`
  (the one summon call site), or `Game::getInstanceCreatureBinder()`.
- Overlaps: none found.

# Work log

## 2026-07-13T22:35:00Z

- Changed: `InstanceArenaService` monster spawn/registration/rollback logic
  with constructor-injected `MonsterFactory`/`CreatureRemover`;
  `Game::getInstanceCreatureBinder()`; the one summon call site in
  `monster.cpp`; rewrote the unit test file to use the new DI constructor and
  added tests for binder registration, factory-failure rollback, and
  cleanup-driven creature removal.
- Learned: the production `CreatureRemover`/`MonsterFactory` defaults are
  only ever invoked through `enterArena()`/the cleanup callback - tests that
  never call `enterArena()` (e.g. `createArena()`-only tests) can keep using
  the single-argument `InstanceArenaService(manager)` constructor safely,
  since the production factory functions are stored but never called
  without a live `Game`.
- Failed/blocked: none.
- Result: ready to open PR.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| `Cave Rat` as the arena's monster | Same datapack already selected for the region plan; harmless, no scripted summon side effects | none |
| Constructor-injected `MonsterFactory`/`CreatureRemover` instead of a virtual interface or a global test hook | Matches this codebase's plain-function/`std::function` DI style used elsewhere; keeps the class trivially testable without mocking frameworks | none |
| `Game::getInstanceCreatureBinder()` exposed generally, not only through `InstanceArenaService` | Summon-ownership inheritance at real call sites is a general instance concern; avoids threading `InstanceArenaService` itself into `monster.cpp` for an unrelated concern | none |
| Cleanup callback removes creatures before `close()`'s invariant check, rather than changing the invariant | The invariant ("no owned creatures at close") is a correctness guarantee from earlier PRs; the arena must satisfy it, not weaken it | none |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `src/game/instance/instance_arena_service.hpp/.cpp` | shared | monster spawn/registration/rollback, DI seam | done |
| `src/game/game.hpp/.cpp` | shared | `getInstanceCreatureBinder()` accessor | done |
| `src/creatures/monsters/monster.cpp` | shared | instance-aware summon call site | done |
| `tests/unit/game/instance/instance_arena_service_test.cpp` | shared | rewritten + new tests | done |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| (pre-commit) | `clang-format --dry-run --Werror` on all changed C++ files (`instance_arena_service.{hpp,cpp}`, `game.hpp`, `game.cpp`, `monster.cpp`, the test file) | Pass | No formatting diffs |
| (pending) | CI (full Linux/Windows/macOS/Docker compile matrix, unit tests, Canary/Global smoke) | not-run | First real build/link/test-run confirmation |

# Risks and compatibility

- Runtime: normal-world monster summon behavior is unchanged (verified by
  tracing `InstanceManager::inheritCreatureOwnership()`'s no-op path for an
  unregistered master, which is every monster outside this one feature).
- Concurrency: the cleanup callback registered in `enterArena()` only
  touches `InstanceManager` and `Game`/the injected remover - it never
  acquires `InstanceArenaService`'s own `sessionMutex`, avoiding the
  previously-documented lock-ordering hazard.
- Rollback: revert this commit; the arena instance goes back to spawning no
  monster and `InstanceManager::close()` behaves as it did before (no
  registered creatures to clean up, since none were ever created).

# Remaining work

1. Open PR, get CI green, merge.
2. Proceed to program queue item 5: instance-scoped delayed events +
   timeout/cleanup wiring (`InstanceScopedEvent`).

# Handoff

## Required reads

- `docs/architecture/instanced-test-arena.md`
- `docs/agents/programs/INSTANCED_TEST_ARENA_PROGRAM.md`
- `docs/architecture/instance-manager.md` (Remaining integration sequence,
  item 1 - now done by this task)

## Open questions

- None new.

# Completion

- Final status: pending PR/CI.
- PR: (to be filled after opening).
- Merge commit: (to be filled after merge).
