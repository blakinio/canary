---
task_id: CAN-20260713-instance-arena-talkaction
program_id: CAN-PROGRAM-INSTANCED-TEST-ARENA
coordination_id: ""
status: ready_for_pr
agent: "Claude"
branch: feat/instance-arena-talkaction
base_branch: main
created: 2026-07-13T21:30:00Z
updated: 2026-07-13T21:50:00Z
last_verified_commit: "7e8f298f"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - CAN-20260713-instance-arena-service (InstanceArenaService, PR #289)
blocks:
  - CAN-PROGRAM-INSTANCED-TEST-ARENA queue item 4 (monster spawn)
owned_paths:
  exclusive:
    - src/lua/functions/core/game/game_functions.hpp
    - src/lua/functions/core/game/game_functions.cpp
    - data/scripts/talkactions/gm/instance_arena.lua
    - docs/agents/tasks/active/CAN-20260713-instance-arena-talkaction.md
  shared:
    - src/game/instance/instance_arena_service.hpp
    - src/game/instance/instance_arena_service.cpp
    - tests/unit/game/instance/instance_arena_service_test.cpp
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/programs/INSTANCED_TEST_ARENA_PROGRAM.md
  read_only:
    - src/game/game.hpp
    - src/game/game.cpp
modules_touched:
  - InstanceArenaService (player session API)
  - Game Lua bindings (createInstanceArena/leaveInstanceArena/closeInstanceArena)
reuses:
  - existing TalkAction/groupType("gamemaster") convention (data/scripts/talkactions/gm/*)
  - existing Game Lua-method registration pattern (game_functions.cpp)
  - Lua::getPlayer/pushPosition/pushString helpers
public_interfaces:
  - InstanceArenaService::enterArena()/leaveArena()/closeArenaForPlayer()/hasActiveSession()
  - Game.createInstanceArena(player)/leaveInstanceArena(player)/closeInstanceArena(player) (Lua)
  - "/instancearena create|leave|close" talkaction
---

# Goal

Make the arena reachable: an admin-only `/instancearena create|leave|close`
talkaction, backed by a minimal, feature-specific Lua binding on `Game`, and
a per-player session API on `InstanceArenaService` (enter/leave/close),
matching existing repository conventions exactly.

# Acceptance criteria

- [x] `InstanceArenaService::enterArena/leaveArena/closeArenaForPlayer/
      hasActiveSession` added, keyed by stable player id, one active arena
      per player, own mutex (documented lock-ordering note for the future
      cleanup-callback PR).
- [x] `Game.createInstanceArena`/`leaveInstanceArena`/`closeInstanceArena`
      Lua bindings added with `@function` docblocks (matches
      `tools/check_lua_api_binding_docs.py`'s requirement).
- [x] `/instancearena create|leave|close` talkaction added under
      `data/scripts/talkactions/gm/`, `groupType("gamemaster")` (same tier
      as the bulk of existing admin commands in that directory),
      `logCommand` call matching every sibling script.
- [x] `create` teleports into the reserved region's entry corner; `leave`
      returns to the saved position without closing the instance; `close`
      evacuates (same saved position) and releases the region.
- [x] Focused C++ unit tests for the new `InstanceArenaService` methods
      (independent sessions, region exhaustion, close-then-reuse, leave
      does not release).
- [ ] Current-head GitHub checks verified (pending PR open + CI, including
      `luac`/`luacheck` for the new Lua file and the Lua-API-binding-docs
      check).
- [x] Module catalogue updated.
- [ ] Autonomous merge gate satisfied (pending CI).

# Confirmed context

- `data/scripts/talkactions/gm/*.lua` is the exact existing convention for
  admin commands (`TalkAction(...)`, `onSay(player, words, param)`,
  `logCommand(player, words, param)`, `:separator(" ")`,
  `:groupType("gamemaster")`, `:register()`) - no manifest/index file is
  needed, the directory is auto-scanned.
- `Game` already exposes a rich, narrow-feature-specific Lua method surface
  (e.g. `getPlayerClusterChannel`, `getPlayerSessionLockInfo` for
  multichannel) - the same pattern was used here rather than building the
  broader generic `Instance.*` Lua API from the original roadmap (that
  remains a separate, later concern if ever pursued; this PR only exposes
  exactly what the arena talkaction needs).
- `tools/check_lua_api_binding_docs.py --base main` run locally after
  committing: reports the new bindings and requires (already satisfied)
  explicit `@function` docblocks since the bindings take a typed `Player`
  parameter rather than a weak `any`/`arg1` pattern.
- No local Lua interpreter/luac/luacheck available in this sandbox; the new
  `.lua` file was hand-verified against multiple existing sibling scripts
  for exact syntax/indentation/API-call correctness. CI's `luac`/`luacheck`
  reviewdog runners are the first real syntax check.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| InstanceArenaService (#289) | Extended with session API | `src/game/instance/instance_arena_service.{hpp,cpp}` | Single existing arena consumer; no second manager/service. |
| Game Lua binding pattern | Three new narrow methods added the same way | `src/lua/functions/core/game/game_functions.cpp` | Matches `getPlayerClusterChannel` etc. exactly. |
| GM talkaction convention | New script matches sibling files exactly | `data/scripts/talkactions/gm/position.lua`, `teleport_to_town.lua` | Established admin-command pattern. |

# Ownership and overlap check

- Program record: `docs/agents/programs/INSTANCED_TEST_ARENA_PROGRAM.md`.
- Open PRs inspected: re-checked before starting; none touch
  `src/lua/functions/core/game/`, `data/scripts/talkactions/`, or
  `src/game/instance/instance_arena_service.*`.
- Overlaps: none found.

# Work log

## 2026-07-13T21:50:00Z

- Changed: added `InstanceArenaService` player-session methods, three
  `Game.*InstanceArena*` Lua bindings, the `/instancearena` talkaction
  script, focused C++ tests, module catalogue update.
- Learned: `lua_api.json` is a checked-in doc file validated for internal
  quality metrics (`check_lua_api_quality.py`) but not regenerated from
  source automatically; the binding-docs check
  (`check_lua_api_binding_docs.py`) only requires the inline `@function`
  docblock in the C++ source, which was already added - no further doc
  file edit needed.
- Failed/blocked: none.
- Result: ready to open PR.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Player sessions keyed by stable player id (uint32_t), not shared_ptr<Player> | Matches every other piece of this subsystem's "stable IDs only, no retained pointers" discipline | none |
| "leave" does not release the region; only "close" does | Matches the task's literal distinction between the two commands | none |
| Narrow `Game.*InstanceArena*` Lua methods instead of a generic `Instance.*` API | Task explicitly scopes this PR to "what the talkaction needs"; the broader Lua API was a separate later roadmap item, not requested here | none |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `src/game/instance/instance_arena_service.hpp/.cpp` | shared | session API | done |
| `src/lua/functions/core/game/game_functions.hpp/.cpp` | exclusive | Lua bindings | done |
| `data/scripts/talkactions/gm/instance_arena.lua` | exclusive | talkaction | done |
| `tests/unit/game/instance/instance_arena_service_test.cpp` | shared | new tests | done |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| (pre-commit) | `clang-format --dry-run --Werror` on all changed/added C++ files | Pass | No formatting diffs |
| (pre-commit) | `python3 tools/check_lua_api_binding_docs.py --base main` | Pass (post-commit) | New bindings have required docblocks |
| (pending) | CI (`luac`/`luacheck`/`xmllint` reviewdog runners, full compile matrix, Lua Tests) | not-run | First real Lua syntax check happens here |

# Risks and compatibility

- Runtime: adds a reachable admin-only capability (previously
  `InstanceArenaService` existed but nothing could call it). Gated behind
  `groupType("gamemaster")`.
- Security: `groupType("gamemaster")` matches the existing tier used by the
  bulk of admin commands in the same directory; not exposed to regular
  players.
- Concurrency: documented lock-ordering hazard for the future
  cleanup-callback PR (a synchronous callback must not re-acquire
  `sessionMutex` while `closeArenaForPlayer()` holds it).
- Rollback: revert this commit; the talkaction and Lua bindings disappear,
  `InstanceArenaService`'s session methods become unreachable again (same
  end state as after PR #289).

# Remaining work

1. Open PR, get CI green (first real Lua syntax check via `luac`/
   `luacheck`), merge.
2. Proceed to program queue item 4: monster spawn + binder registration
   after nonzero runtime ID + summon inheritance.

# Handoff

## Required reads

- `docs/architecture/instanced-test-arena.md`
- `docs/agents/programs/INSTANCED_TEST_ARENA_PROGRAM.md`

## Open questions

- None new.

# Completion

- Final status: pending PR/CI.
- PR: (to be filled after opening).
- Merge commit: (to be filled after merge).
