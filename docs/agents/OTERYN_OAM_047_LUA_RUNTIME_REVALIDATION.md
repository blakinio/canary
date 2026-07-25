# OAM-047 Lua Runtime revalidation

## Final disposition

`lua-runtime → ADAPT`

## Exact baselines and delivery

- Canary preflight merge: `bc8d7827f652b8b8b3200f7ef81818e8d5d149f5`
- Otheryn task-start main: `415f559f829c83d79d9c609e7f421d2449e59d74`
- reviewed upstream: `7323503b3dc61ed86bf1f04a611b2d0aec64b35a`
- Otheryn feature final head: `a7349190a51d627e4668af56912337ff8cadec46`
- Otheryn feature merge: `5b3bee0dd6eedf8c2f9578c686ca85c0fde519cf`
- Otheryn lifecycle merge: `68e2b233b02356a79a03422ed51d757b85915bc5`
- Canary governance task-start main: `124b029d1a2498a64fa6612b16efa386b8786a83`

## Canonical responsibility

Canonical `lua-runtime` owns the shared Lua state/environment lifecycle, script-interface initialization and teardown, callback ownership boundaries, and reload/shutdown safety. It does not own individual gameplay scripts, feature-specific registration families, analytics policy, persistent gameplay state, protocol/client behavior or generic concurrent orchestration.

## Isolated target defect

Ordinary `LuaScriptInterface::initState()` retained the shared main `lua_State*` and event-table registry references. `LuaEnvironment::reInitState()` closed that state and created a replacement without inventorying, invalidating or reinitializing attached child interfaces. The inherited source retained an explicit child reload TODO. Child interfaces could therefore keep pointers and registry IDs belonging to the closed state until a separate subsystem happened to reinitialize them.

## Bounded adaptation

The target now keeps a process-local lifetime registry for `LuaScriptInterface` objects. The main environment snapshots only registered children whose base `luaState` equals the current shared state, closes their event-table references before `lua_close()`, creates the replacement main state, and reinitializes the same children against it. A rebind failure closes the replacement state and already rebound children. Dormant, destroyed and independently overridden test interfaces are excluded from the snapshot.

The registry implementation was folded into the existing `lua_environment.cpp` translation unit so CMake and the maintained Visual Studio Solution consume the same implementation without expanding build-system ownership.

## Focused proof

The target fixture proves:

- two active child interfaces bind to the replacement main state;
- stale registry IDs fail closed after reset;
- rebound children register and resolve new events;
- an uninitialized interface is not attached merely because its object exists;
- a destroyed interface is removed before a later reset;
- the shared test interface follows the bounded child lifecycle.

## Exact-head gates

Otheryn final head `a7349190a51d627e4668af56912337ff8cadec46` passed:

- Autofix `30167797667`;
- CI `30167797744`;
- Required `30167797642`.

The first final-head CI isolated a build-registration defect because a separated registry translation unit was CMake-only. The corrected head passed Windows CMake, Windows Solution, Linux release/debug, macOS, Docker, Lua tests, focused unit tests and runtime smokes. One unrelated `PartyTest.GetPlayersAndDisbandHandleNullEntries` process exited with a post-test segmentation fault after GoogleTest reported the test passed; the exact same head passed a clean Linux-debug rerun. No feature code was changed for that unrelated flake.

PR #107 had no comments, reviews or review threads and target main had zero drift before expected-head squash merge. Lifecycle PR #108 changed only the task active/archive path, passed Required `30169112582`, had clean discussions and merged as `68e2b233b02356a79a03422ed51d757b85915bc5`.

## Rejected hypotheses

- infer `REUSE` from byte-identical interface roots or successful compilation;
- reload all gameplay scripts inside the main-state lifecycle primitive;
- expand into feature bindings, userdata redesign or generic concurrent reload orchestration;
- edit the Visual Studio project when the implementation can use an existing supported translation unit;
- claim concurrent, physical-client or production gameplay safety from the focused lifecycle proof.

## Final conclusion

OAM-047 is `lua-runtime → ADAPT`. The shared Lua architecture remains suitable, but state replacement required one bounded child-interface lifecycle correction. Focused tests and all maintained build paths prove the corrected boundary without importing feature-specific reload policy.

## Nonclaims

OAM-047 does not claim complete production subsystem reload ordering; callback timing during operator-triggered reloads; concurrent reload/read/callback safety, lock freedom or race freedom; exhaustive userdata, timer parameter or external C++ wrapper lifetime safety; persistence, crash recovery or distributed behavior; automatic gameplay script reload; physical-client behavior; protocol/client compatibility; production gameplay parity; or full server readiness.
