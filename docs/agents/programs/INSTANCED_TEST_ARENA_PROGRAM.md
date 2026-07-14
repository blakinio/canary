---
program_id: CAN-PROGRAM-INSTANCED-TEST-ARENA
name: Instanced Test Arena
status: active
owner: Claude
created: 2026-07-13T20:00:00Z
updated: 2026-07-14T00:45:00Z
last_verified_commit: "6a0cfcff5004c22bea649c8937357dc747e0619e"
primary_paths:
  - src/game/instance/
  - src/game/game.hpp
  - src/game/game.cpp
  - data/talkactions/
  - docs/architecture/instanced-test-arena.md
shared_integration_paths:
  - docs/architecture/instance-manager.md
  - docs/architecture/CANARY_ENGINE_PROJECT_HANDOFF.md
  - docs/agents/MODULE_CATALOG.md
related_programs: []
cross_repo_contracts: []
---

# Mission

Deliver one small, real, administrator-only vertical-slice feature - an
Instanced Test Arena - that is a genuine production consumer of the merged
`InstanceManager` foundation (region-backed lifecycle, `Game::
getInstanceManager()`, `InstanceCreatureBinder`, automatic unregister on
removal, `InstanceScopedEvent`, periodic timeout sweep). No further
InstanceManager infrastructure PRs without a real consumer.

# Scope

- one `InstanceArenaService`-style component owning two configured map
  regions and consuming the existing manager/binder/event APIs;
- an admin-gated command (`/instancearena create|leave|close`) matching
  existing talkaction conventions;
- create -> teleport player into a reserved region -> spawn and register a
  real monster -> summons inherit ownership;
- leave -> return player to their saved position;
- close/timeout -> evacuate player, remove creatures, run cleanup, release
  region only after success;
- fix whatever concrete cross-instance leaks two real running arenas expose
  (spectator/target/combat call sites), nothing speculative;
- two-parallel-instances end-to-end proof and region reuse.

# Explicit exclusions

- no multiworld or multi-channel work;
- no generic dungeon/instance authoring framework;
- no new `InstanceManager`/registry/binder/global singleton;
- no OTBM parser/renderer duplication;
- no AI image generation;
- no `.otbm`/`items.otb` binary edits.

# Existing systems to reuse

| Module/tool/contract | Source | Required reuse rule |
|---|---|---|
| InstanceManager (region-backed) | `src/game/instance/instance_manager.{hpp,cpp}` | One manager instance via `Game::getInstanceManager()`; do not create a second. |
| InstanceRegionPool | `src/game/instance/instance_region_pool.*` | Region config is one explicit list; do not invent a second pool. |
| InstanceCreatureBinder | `src/game/instance/instance_creature_binder.hpp` | Register/unregister/inherit through this adapter only. |
| InstanceScopedEvent | `src/game/instance/instance_scoped_event.hpp` | Wrap arena-scheduled callbacks; do not build a parallel liveness check. |
| `Game::removeCreature()` auto-unregister | `src/game/game.cpp` | Already unregisters on removal; do not duplicate. |
| `Game::start()` timeout sweep | `src/game/game.cpp` | Already calls `closeExpiredInstances()` periodically; do not add a second sweep. |
| Unified OTBM world index / item audit / script resolution | `tools/ai-agent/otbm_*` | Region evidence only; never invent coordinates or hand-edit `.otbm`. |

# Active tasks

| Task ID | Branch | PR | State | Exact next action |
|---|---|---:|---|---|
| (none yet) | | | | Start PR 6: run two real arenas, fix concrete cross-instance leaks in spectator/target/combat call sites. |

# Queue

1. ~~PR 1 - fix `docs/architecture/instance-manager.md` inconsistency, add `docs/architecture/instanced-test-arena.md` region plan with OTBM evidence.~~ Done (#287).
2. ~~PR 2 - region config + `InstanceArenaService` + create/activate/close lifecycle, no player yet.~~ Done (#289).
3. ~~PR 3 - admin talkaction: create/leave/close, return-position capture, evacuation.~~ Done (#295).
4. ~~PR 4 - monster spawn + binder registration after nonzero runtime ID + summon inheritance.~~ Done (#304).
5. ~~PR 5 - instance-scoped delayed events + timeout/cleanup wiring.~~ Done (#307).
6. PR 6 - run two real arenas, fix concrete cross-instance leaks only.
7. PR 7 - two-parallel-instances E2E, region reuse proof, final docs.

# Completed work

| Task/PR | Result | Merge commit | Follow-up |
|---|---|---|---|
| CAN-20260713-instanced-test-arena / #287 | Fixed stale `instance-manager.md` paragraph; added evidence-backed region plan (`docs/architecture/instanced-test-arena.md`) | `47270c39f4e36568e8440cf6d2f421f5f09e6f67` | PR 2 consumed the region coordinates. |
| CAN-20260713-instance-arena-service / #289 | `InstanceArenaService` real consumer, `Game::getInstanceArenaService()`, two real configured regions | `7e8f298f` (squash) | PR 3 adds a player-reachable command. |
| CAN-20260713-instance-arena-talkaction / #295 | `/instancearena create\|leave\|close` talkaction, `Game.createInstanceArena/leaveInstanceArena/closeInstanceArena` Lua bindings, player-session API on `InstanceArenaService` | `d9b10c322cd6bb9690c2a29fd3354082dde066f9` (squash) | PR 4 adds the real monster spawn + binder registration. |
| CAN-20260713-instance-arena-monster-spawn / #304 | Real monster spawn + `InstanceCreatureBinder` registration in `enterArena()` with full rollback on failure; cleanup callback empties the registry before `close()`; `Game::getInstanceCreatureBinder()` wires the one production summon call site (`Monster::onThinkDefense()`) to the tested instance-aware `setMaster` overload | `cb22a5063bc10c306932c407f6c02c799dfc5ba3` (squash) | PR 5 adds instance-scoped delayed events + timeout/cleanup wiring. CI caught a real compile bug (`binder.bind()` needed a dereferenced `shared_ptr<Monster>`), fixed before merge. |
| CAN-20260714-instance-arena-timeout-events / #307 | Real 15-minute `InstanceDefinition::timeout` for every arena; `InstanceArenaService::reapExpiredSessions()` evacuates+forgets timeout-orphaned sessions on the same periodic tick as `closeExpiredInstances()`; `enterArena()` schedules an `InstanceScopedEvent`-guarded closing-warning message (its first real production call site) | `6a0cfcff5004c22bea649c8937357dc747e0619e` (squash) | PR 6 runs two real arenas and fixes concrete cross-instance leaks in spectator/target/combat call sites. CI caught a real clang-format-17-vs-18 mismatch; clang-format-17 now installed locally to match CI. |

# Dependencies and blockers

- None currently. `data-canary/world/canary.otbm` is the only complete map
  physically present in this environment (`otservbr.otbm` is downloaded at
  server startup and not committed); the region plan records this as an
  assumption the owner can redirect.

# Decisions and invariants

- Region configuration lives in exactly one place (`InstanceArenaService`'s
  region list); every later PR reads it, none duplicates it.
- Physical region separation is a defense-in-depth buffer, not the sole
  isolation mechanism - the ownership-registry relation checks
  (`getCreatureRelation()`/`canCreaturesInteract()`) are the actual
  cross-instance isolation guarantee and must keep working even if a player
  physically walks near the buffer zone.
- Every PR in this program must compile-affecting-file-check with
  `clang-format`/`cmake-format` locally (no compiler available in this
  sandbox) and rely on CI for the first real build confirmation.
- No PR in this program adds a new `g_*()` singleton or a second
  manager/registry/binder.

# Validation strategy

- Focused gtest coverage per PR where a real unit-test harness exists.
- `Game`-touching changes have no local unit-test harness (documented
  precedent from PRs #201/#231/#233); rely on full CI compile + the
  project's existing Canary/global datapack smoke jobs.
- PR 7 adds the first genuine end-to-end proof (two concurrent instances).

# Handoff

## Start here

Read `docs/architecture/instanced-test-arena.md` for the region evidence,
then `docs/architecture/instance-manager.md` for the underlying API surface,
then the active task record for exact current progress.

## Task creation protocol

1. Select the next queue item above.
2. Re-check open PRs and this program record for overlap before branching.
3. Create one task record, branch, and PR from current `main`.
4. Implement the smallest complete slice; validate what can be validated
   locally; open/update the PR; merge only after real CI is green.
5. Update this program record's Active tasks/Queue/Completed work sections
   and `docs/architecture/instance-manager.md`/
   `docs/architecture/CANARY_ENGINE_PROJECT_HANDOFF.md` after merge.

## Do not repeat

- Do not add another "safe no-op" InstanceManager adapter PR without a real
  call site behind it - that phase is over; this program's job is to be the
  real consumer.
- Do not attempt to hand-edit `data-canary/world/canary.otbm` or invent new
  rooms without RME access - reuse the existing "Tps Room" evidence instead.

## Open questions

- Is `data-canary/world/canary.otbm` actually the intended production map
  for this feature, or should the region plan be redone against the
  downloaded `otservbr.otbm` once/if that file is available in a real
  deployment? Recorded as an assumption in
  `docs/architecture/instanced-test-arena.md`, not a blocker.
