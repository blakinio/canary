---
task_id: CAN-20260714-instance-arena-timeout-events
program_id: CAN-PROGRAM-INSTANCED-TEST-ARENA
coordination_id: ""
status: merged
agent: "Claude"
branch: feat/instance-arena-timeout-events
base_branch: main
created: 2026-07-14T00:00:00Z
updated: 2026-07-14T00:45:00Z
last_verified_commit: "6a0cfcff5004c22bea649c8937357dc747e0619e"
risk: medium
related_issue: ""
related_pr: "#307"
depends_on:
  - CAN-20260713-instance-arena-monster-spawn (InstanceArenaService monster spawn, PR #304)
blocks:
  - CAN-PROGRAM-INSTANCED-TEST-ARENA queue item 6 (cross-instance isolation)
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260714-instance-arena-timeout-events.md
  shared:
    - src/game/instance/instance_arena_service.hpp
    - src/game/instance/instance_arena_service.cpp
    - tests/unit/game/instance/instance_arena_service_test.cpp
    - src/game/game.cpp
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/programs/INSTANCED_TEST_ARENA_PROGRAM.md
    - docs/architecture/instance-manager.md
    - docs/architecture/instanced-test-arena.md
modules_touched:
  - InstanceArenaService (timeout, closing-warning scheduling, session reaping)
  - Game::start() periodic sweep (now also calls reapExpiredSessions())
reuses:
  - InstanceManager::createInstance()'s existing InstanceDefinition::timeout field (already supported, unused until now)
  - InstanceManager::closeExpiredInstances() (existing, PR #151/#233 - already periodically called by Game::start())
  - InstanceScopedEvent (existing, PR #183 - first real production call site)
  - g_dispatcher().scheduleEvent() (existing engine scheduling API)
  - Game::getPlayerByID() / Game::internalTeleport() / Player::sendTextMessage() (existing, same mechanism Creature:teleportTo() uses in Lua)
public_interfaces:
  - InstanceArenaService::ArenaTimeout / ArenaClosingWarningLeadTime (constants)
  - InstanceArenaService::reapExpiredSessions()
  - InstanceArenaService(manager, MonsterFactory, CreatureRemover, DelayedEventScheduler, MessageNotifier, PlayerEvacuator) (extended test-only DI constructor)
---

# Goal

Give the arena a real timeout instead of running forever, make sure a
timeout-driven close evacuates the player and forgets their session (not
just the manual `/instancearena close` path), and give `InstanceScopedEvent`
its first real production consumer: a one-shot closing-warning message that
must not fire against a player who already left.

# Acceptance criteria

- [x] Every arena instance is created with a real, nonzero
      `InstanceDefinition::timeout` (`InstanceArenaService::ArenaTimeout`,
      15 minutes) instead of the previous "never expires" default, so the
      already-periodic `Game::start()` sweep (`closeExpiredInstances()`,
      PR #233) actually closes idle arenas.
- [x] Timeout-driven close runs the exact same cleanup callback a manual
      `closeArenaForPlayer()` does (verified: the registered monster is
      removed via the same injected `CreatureRemover` either way) - no
      separate/duplicate cleanup path was added.
- [x] `InstanceArenaService::reapExpiredSessions()` added: evacuates
      (teleports back) and forgets any tracked player session whose arena
      is no longer `Active` by the time it runs, since a timeout-driven
      close never goes through `closeArenaForPlayer()` (which is the only
      place that previously forgot a session). A no-op for sessions still
      `Active`.
- [x] `Game::start()`'s existing periodic instance sweep now also calls
      `getInstanceArenaService().reapExpiredSessions()` right after
      `closeExpiredInstances()`, on the same tick.
- [x] `enterArena()` schedules one real `InstanceScopedEvent`-guarded
      closing-warning message (2 minutes before the 15-minute timeout) via
      the engine's dispatcher; if the arena already closed by the time the
      scheduler runs the callback, `InstanceScopedEvent::isLive()` is false
      and the callback is a no-op - proven with a real production call
      site, not just the pre-existing isolated class-level tests.
- [x] `InstanceArenaService`'s remaining production dependencies (event
      scheduling, player messaging, player teleport) are behind the same
      constructor-injected DI pattern established in PR #304
      (`MonsterFactory`/`CreatureRemover`), so the class stays unit-testable
      without a live `Game`/dispatcher.
- [x] Focused C++ unit tests added: real timeout expires an idle arena;
      expiry drives the same cleanup callback as manual close; the closing
      warning is scheduled with the correct delay; it fires when the arena
      is still active; it is a no-op after the arena already closed;
      `reapExpiredSessions()` evacuates+forgets a timed-out session and is
      a no-op for an active one.
- [x] Current-head GitHub checks verified: CI caught a real clang-format
      version mismatch (local v18 vs. CI's pinned v17 disagreeing on how to
      wrap the 6-parameter constructor's initializer list) - the autofix-ci
      bot pushed the correction directly to the branch, and clang-format-17
      was installed locally to match CI exactly going forward. Full
      Linux/Windows/macOS/Docker matrix, Fast Checks, Lua Tests all passed
      afterward. PR #307 merged (commit
      `6a0cfcff5004c22bea649c8937357dc747e0619e`).
- [x] Module catalogue and architecture docs updated with the merge SHA.
- [x] Autonomous merge gate satisfied.

# Confirmed context

- `InstanceDefinition::timeout` (`instance_manager.hpp`) already existed
  from earlier InstanceManager-foundation PRs (defaults to
  `std::chrono::seconds{0}` = never expires) but nothing ever set it to a
  nonzero value in production - `InstanceArenaService::createArena()` was
  the first real caller of `InstanceManager::createInstance()`, and it
  passed no timeout. This task's whole "timeout" half is simply passing the
  already-supported field for the first time.
- `Game::start()` already registers a periodic
  `g_dispatcher().cycleEvent(EVENT_INSTANCE_TIMEOUT_SWEEP_MS, ...)` tick
  (10s interval, PR #233) that calls `closeExpiredInstances()`. That tick's
  lambda now also calls `reapExpiredSessions()` - no new timer/event was
  added, the existing one just does one more thing.
- `Monster::onThinkDefense()`'s summon call site (PR #304) is the engine's
  only OTHER `InstanceScopedEvent`-adjacent production wiring; this task's
  closing-warning callback is the actual first production consumer of
  `InstanceScopedEvent` itself (the summon wiring uses
  `InstanceCreatureBinder`, a related but different class).
- `g_game().internalTeleport(thing, position, pushMove)` is exactly what
  `Creature:teleportTo()` calls in Lua (`creature_functions.cpp`,
  `luaCreatureTeleportTo`) - the evacuation default reuses this, not a new
  teleport mechanism.
- No local build is available in this sandbox; as with every prior PR in
  this program, `clang-format --dry-run --Werror` was run on every
  changed/added file (all clean) and correctness was verified by close
  reading, cross-checking exact function signatures
  (`Game::internalTeleport`, `Game::getPlayerByID`,
  `Dispatcher::scheduleEvent`, `Player::sendTextMessage`) against their
  real declarations before use - directly motivated by PR #304's real
  CI-caught compile error in this same file, which is documented as the
  reason for this extra care.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| `InstanceDefinition::timeout` + `closeExpiredInstances()` | First real nonzero-timeout caller | `src/game/instance/instance_manager.hpp` | Already built and tested (PR #151/#233); just never used until now. |
| `InstanceScopedEvent` | First real production consumer | `src/game/instance/instance_scoped_event.hpp` | Already built and tested (PR #183); this task supplies the missing call site. |
| `Game::start()`'s periodic sweep | Extended with one more call on the same tick | `src/game/game.cpp` | No second timer/dispatcher event added. |
| `Creature:teleportTo()`'s `Game::internalTeleport()` mechanism | Reused for the production `PlayerEvacuator` default | `src/lua/functions/creatures/creature_functions.cpp` | Same teleport path as every other in-game teleport; no new mechanism invented. |

# Ownership and overlap check

- Program record: `docs/agents/programs/INSTANCED_TEST_ARENA_PROGRAM.md`.
- Open PRs re-checked before starting: none touch
  `src/game/instance/instance_arena_service.*`, the instance-sweep lambda in
  `src/game/game.cpp`, or `tests/unit/game/instance/
  instance_arena_service_test.cpp`.
- Overlaps: none found.

# Work log

## 2026-07-14T00:15:00Z

- Changed: `InstanceArenaService::ArenaTimeout`/`ArenaClosingWarningLeadTime`
  constants; `createArena()` now passes the timeout; `enterArena()`
  schedules an `InstanceScopedEvent`-guarded closing warning;
  `reapExpiredSessions()` added; `Game::start()`'s periodic sweep calls it;
  extended the constructor DI seam with `DelayedEventScheduler`/
  `MessageNotifier`/`PlayerEvacuator`; rewrote the test harness and added
  new PR5-specific tests.
- Learned: nothing needed to change in the per-instance cleanup callback
  established in PR #304 - `closeExpiredInstances()` goes through the same
  `InstanceManager::close()` path a manual close does, so the existing
  callback (which removes registered creatures) already runs correctly on
  timeout without modification. The only genuinely new gap was the
  `InstanceArenaService`-level session map, which nothing but
  `closeArenaForPlayer()` previously knew how to clear - solved with a
  separate periodic reap step (not by touching the per-instance cleanup
  callback, which would have re-entered `sessionMutex` while
  `closeArenaForPlayer()` already holds it - see Decisions below).
- Failed/blocked: none.
- Result: ready to open PR.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Session reaping is a separate periodic sweep (`reapExpiredSessions()`), not part of the per-instance `setCleanupCallback()` | The cleanup callback registered in `enterArena()` can run synchronously inside `closeArenaForPlayer()`, which already holds `sessionMutex` - having the callback also touch `sessions`/`sessionMutex` would self-deadlock on that path. A separate sweep called only from `Game::start()`'s dispatcher tick (which never holds `sessionMutex`) avoids this entirely. | none |
| 15-minute timeout, 2-minute warning lead time | Concrete, reasonable defaults for a test/admin feature; no gameplay-balance requirement exists to derive them from | none |
| Closing-warning message reuses the existing DI pattern (`DelayedEventScheduler`/`MessageNotifier`) instead of calling `g_dispatcher()`/`g_game()` directly | Consistent with PR #304's `MonsterFactory`/`CreatureRemover` precedent; keeps the class unit-testable without a live dispatcher/Game | none |
| Evacuator reuses `Game::internalTeleport()`, the same call `Creature:teleportTo()` makes in Lua | No new teleport mechanism; matches existing conventions exactly | none |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `src/game/instance/instance_arena_service.hpp/.cpp` | shared | timeout, closing warning, session reaping, extended DI | done |
| `src/game/game.cpp` | shared | periodic sweep now also reaps sessions | done |
| `tests/unit/game/instance/instance_arena_service_test.cpp` | shared | rewritten + new tests | done |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| (pre-commit) | `clang-format --dry-run --Werror` on all changed/added C++ files | Pass | No formatting diffs |
| (pending) | CI (full Linux/Windows/macOS/Docker compile matrix, unit tests, Canary/Global smoke) | not-run | First real build/link/test-run confirmation |

# Risks and compatibility

- Runtime: normal-world behavior is unaffected - `Game::start()`'s sweep
  already ran unconditionally; it now also calls
  `getInstanceArenaService().reapExpiredSessions()`, a cheap no-op whenever
  no arena session has expired (which is always true outside this feature).
- Concurrency: `reapExpiredSessions()` releases `sessionMutex` before
  calling the injected `playerEvacuator`, so it never calls into
  Game/Player while holding this service's own lock.
- Rollback: revert this commit; arenas go back to running forever with no
  closing warning and no session reaping - the same end state as after
  PR #304.

# Remaining work

1. ~~Open PR, get CI green, merge.~~ Done: PR #307, merge commit
   `6a0cfcff5004c22bea649c8937357dc747e0619e`.
2. Proceed to program queue item 6: run two real arenas and fix concrete
   cross-instance leaks in spectator/target/combat call sites.

# Handoff

## Required reads

- `docs/architecture/instanced-test-arena.md` ("Current status" section)
- `docs/agents/programs/INSTANCED_TEST_ARENA_PROGRAM.md`
- `docs/architecture/instance-manager.md` (Remaining integration sequence,
  items 4-5 - updated by this task)

## Open questions

- None new.

# Completion

- Final status: merged.
- PR: #307.
- Merge commit: `6a0cfcff5004c22bea649c8937357dc747e0619e`.
