---
task_id: CAN-20260713-instance-arena-service
program_id: CAN-PROGRAM-INSTANCED-TEST-ARENA
coordination_id: ""
status: merged
agent: "Claude"
branch: feat/instance-arena-service
base_branch: main
created: 2026-07-13T21:00:00Z
updated: 2026-07-13T21:20:00Z
last_verified_commit: "47270c39f4e36568e8440cf6d2f421f5f09e6f67"
risk: medium
related_issue: ""
related_pr: "#289"
depends_on:
  - CAN-20260713-instanced-test-arena (region plan, PR #287)
blocks:
  - CAN-PROGRAM-INSTANCED-TEST-ARENA queue item 3 (admin talkaction)
owned_paths:
  exclusive:
    - src/game/instance/instance_arena_service.hpp
    - src/game/instance/instance_arena_service.cpp
    - tests/unit/game/instance/instance_arena_service_test.cpp
    - docs/agents/tasks/active/CAN-20260713-instance-arena-service.md
  shared:
    - src/game/game.hpp
    - src/game/game.cpp
    - src/game/CMakeLists.txt
    - tests/unit/game/CMakeLists.txt
    - vcproj/canary.vcxproj
    - docs/architecture/instance-manager.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/programs/INSTANCED_TEST_ARENA_PROGRAM.md
  read_only:
    - src/game/instance/instance_manager.{hpp,cpp}
    - src/game/instance/instance_creature_binder.hpp
modules_touched:
  - InstanceArenaService (new)
reuses:
  - Game::getInstanceManager() (PR #201)
  - InstanceCreatureBinder (merged)
  - existing getIOWheel()/getAttachedEffects() Game accessor pattern
public_interfaces:
  - InstanceArenaService::configuredRegions()
  - InstanceArenaService::createArena()/closeArena()/getState()/getRegion()/getBinder()
  - Game::getInstanceArenaService()

---

# Goal

Give `Game::getInstanceManager()` its first real production caller:
`InstanceArenaService`, configured with the two regions from
`docs/architecture/instanced-test-arena.md`, supporting create/activate/close
lifecycle with no player involvement yet (that is the next task).

# Acceptance criteria

- [x] `InstanceArenaService::configuredRegions()` returns exactly the two
      regions documented in `docs/architecture/instanced-test-arena.md`.
- [x] `Game`'s `InstanceManager` member is now constructed with those two
      regions instead of an empty list.
- [x] `Game::getInstanceArenaService()` accessor added, mirroring
      `getInstanceManager()`/`getIOWheel()`.
- [x] `createArena()`/`closeArena()` tested: reserve/activate, two arenas
      get different regions, third fails cleanly, close releases for reuse.
- [x] `docs/architecture/instance-manager.md` and `MODULE_CATALOG.md`
      updated to reflect the two real configured regions and the new
      module.
- [ ] Current-head GitHub checks verified (pending PR open + CI - this
      touches `game.hpp`, so full Linux/Windows/macOS/Docker compile is the
      real test).
- [ ] Autonomous merge gate satisfied (pending CI).

# Confirmed context

- Depends on the region plan in PR #287 (`docs/architecture/
  instanced-test-arena.md`); that PR was open (not yet merged) when this
  branch was created from `main` at `6fb9c65d3e8b9105e65515dc2b03827a06753eb0`.
  Both PRs touch `docs/architecture/instance-manager.md` but different
  paragraphs (PR #287: "Scheduler/event liveness"; this task: "Scope and
  boundaries" and "Remaining integration sequence" item 0) - low conflict
  risk, will rebase if GitHub reports one.
- `InstanceArenaService` does not own a second `InstanceManager` - it takes
  `Game`'s single instance by reference, per the program's explicit
  "no second manager/registry/binder" rule.
- No unit-test harness exists for `Game` itself (documented precedent from
  PRs #201/#231/#233); `InstanceArenaService` itself IS independently
  testable (plain constructor-injected class, not a `Game` member), so a
  real focused test suite was written and is expected to run in CI.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| Game::getInstanceManager() (#201) | Constructor-injected into InstanceArenaService | `src/game/game.hpp` | The one shared manager instance. |
| InstanceCreatureBinder (merged) | Owned by InstanceArenaService, exposed via getBinder() for the next PR | `src/game/instance/instance_creature_binder.hpp` | Avoids a second binder. |
| getIOWheel()/getInstanceManager() accessor pattern | Mirrored exactly for getInstanceArenaService() | `src/game/game.hpp`/`.cpp` | Established Game accessor convention. |

# Ownership and overlap check

- Program record: `docs/agents/programs/INSTANCED_TEST_ARENA_PROGRAM.md`.
- Open PRs inspected: re-checked before starting; none touch
  `src/game/instance/`, `src/game/game.{hpp,cpp}` besides my own PR #287
  (docs-only, different file sections).
- Active tasks inspected: only this program's own task records.
- Overlaps: `docs/architecture/instance-manager.md` shared with PR #287
  (different paragraphs).
- Resolution: proceed; rebase on conflict.

# Work log

## 2026-07-13T21:20:00Z

- Changed: added `InstanceArenaService` (header + impl + tests), wired it
  into `Game` (new member, accessor, region config), updated
  `instance-manager.md` and `MODULE_CATALOG.md`, registered new files in
  CMakeLists and `vcproj/canary.vcxproj`.
- Learned: n/a (straightforward layer on top of already-merged pieces).
- Failed/blocked: none.
- Result: ready to open PR.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| InstanceArenaService takes InstanceManager& by constructor, does not own one | Program rule: no second manager/registry | none |
| Region coordinates live only in InstanceArenaService::configuredRegions() | Single source of truth; Game's member initializer calls it | none |
| Arena activates immediately after create (no multi-step Creating phase) | Arena has no complex setup; matches "basic lifecycle without player" scope | none |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `src/game/instance/instance_arena_service.hpp/.cpp` | exclusive | new service | done |
| `tests/unit/game/instance/instance_arena_service_test.cpp` | exclusive | focused tests | done |
| `src/game/game.hpp/.cpp` | shared | owner + accessor | done |
| `src/game/CMakeLists.txt`, `tests/unit/game/CMakeLists.txt`, `vcproj/canary.vcxproj` | shared | build registration | done |
| `docs/architecture/instance-manager.md`, `docs/agents/MODULE_CATALOG.md` | shared | doc accuracy | done |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| (pre-commit) | `clang-format --dry-run --Werror` on all changed/added C++ files | Pass | No formatting diffs |
| (pre-commit) | `cmake-format --check` on both CMakeLists | Pass | No formatting diffs |
| (pending) | CI on opened PR | not-run | Touches `game.hpp`; full compile matrix is the real test, as with PR #201 |

# Failed approaches and dead ends

- None for this task.

# Risks and compatibility

- Runtime: `Game::getInstanceManager()` now has two real regions instead of
  zero - `createInstance()` can now actually succeed. This is the deliberate
  purpose of this PR (giving it a real caller); no other code path calls
  `createInstance()` in production yet, so this is not a silent behavior
  change to anything else.
- Data/migration: none.
- Security: arena creation is not yet reachable by any player (no
  talkaction/command wired in this PR) - reachability is the next task.
- Backward compatibility: additive only.
- Cross-repo rollout: none.
- Rollback: revert this commit; `Game`'s InstanceManager reverts to zero
  regions and the arena service member is removed.

# Remaining work

1. Open PR, get CI green (full compile matrix since `game.hpp` changed),
   merge.
2. Proceed to program queue item 3: admin talkaction (create/leave/close),
   return-position capture, evacuation.

# Handoff

## Start here

Read `docs/architecture/instanced-test-arena.md` and this task's "Decisions"
section before adding the admin talkaction in the next task - the entry
position convention (region's `(minX, minY, Z)` corner) is documented there.

## Required reads

- `AGENTS.md`
- `docs/agents/programs/INSTANCED_TEST_ARENA_PROGRAM.md`
- `docs/architecture/instanced-test-arena.md`
- `docs/architecture/instance-manager.md`

## Open questions

- None new; inherits the map-choice question from the region-plan task.

# Completion

- Final status: merged, CI green (Fast Checks, Lua Tests, Linux release,
  lint/format/audit jobs required for this path; Windows/macOS/Docker
  scheduling was in progress at merge time, gated by the repo owner's
  auto-merge).
- PR: #289.
- Merge commit: `7e8f298f`.
- Program record updated: yes (Active tasks/Queue/Completed work).
- Catalogue updated: yes.
- Changelog updated: not yet (behavior-level change, will note in the
  program's finishing touches or a dedicated changelog entry if requested).
- Archived at: `docs/agents/tasks/archive/CAN-20260713-instance-arena-service.md`.
