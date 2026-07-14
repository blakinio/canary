# Canary Engine — Project Handoff and Roadmap

> Last verified: 2026-07-12
>
> Repository: `blakinio/canary`
>
> Verified `main`: `409685766e871859775d3286fb989d9d7b0e4533`
>
> Purpose: current source of truth for agents continuing the engine architecture work.

## Goal

Harden and modularize Canary without breaking existing clients or datapacks. The active program covers portable builds, deterministic startup, strict AI-content validation and deployment, profile-driven protocol transport, secure login sessions, targeted dependency migration and instance lifecycle/isolation.

## Scope policy

- Multiworld is paused.
- Do not extend multi-channel in this workstream unless the owner explicitly reopens it.
- Existing merged multi-channel code must remain default-disabled and must not be accidentally broken.
- Open multi-channel PRs are separate work and are not dependencies of the instance/protocol roadmap below.
- Use small PRs, one concern per PR.
- Never merge failed, cancelled, stale or incomplete CI.
- Do not push production behavior directly to `main`.

## Completed and merged

### Build and startup

- PR #17 — portable CPU baseline; native optimization is opt-in.
- PR #24 — startup loader waits on a condition variable instead of polling.
- PR #59 — dispatcher latency timer refresh after long startup.

### AI content and deployment

- PR #21 — strict AI-content task schemas, dependency and identifier validation.
- PR #103 — atomic release engine with path confinement, atomic switch, process health check, rollback, audit manifest and failure-phase tests.
- PR #118 — full staging datapack assembly, real compiled Canary preflight, post-switch real-server smoke and automatic rollback.
- PR #125 — materializes a manually approved AI promotion handoff into an atomic deployment overlay with path, symlink and SHA-256 validation.

### Protocol and authentication

- PR #71 — `TransportProfile` is authoritative for framing, checksum and compression; protocol regression tests added.
- PR #77 — secure single-use `LoginSessionManager` with 256-bit tokens, TTL, hash-only storage and concurrency tests.
- PR #80 — fixes modern-client login rejection.
- PR #82 — wires secure login tokens into modern `authType == "session"` login/game handshake while preserving legacy/password paths.

### Dependency migration

- PR #117 — dependency audit and `SharedPtrManager` migration to the existing DI container.
- PR #119 — migrates `Scripts` to the DI container; no raw non-multichannel Meyers singleton remains in the audited set.

### Instance foundation

- PR #107 — `InstanceManager` lifecycle/registry foundation with strong IDs, timeout and concurrency tests.
- PR #121 — thread-safe `InstanceRegionPool` with 3D overlap validation, deterministic reservation, release/reuse and concurrency tests.
- PR #151 — integrates `InstanceRegionPool` into `InstanceManager`; each instance owns one concrete map region, close releases it only after successful cleanup, and failed cleanup quarantines the region. Full Linux, Windows, macOS and Docker CI passed. Merge commit: `95244309453e980ac0377379f8ba5605ca3aba6b`.
- PR #159 — adds lifecycle-safe creature identity ownership to `InstanceManager`: stable runtime IDs, same-owner idempotency, cross-instance rejection, cleanup-time unregister and region quarantine while owned IDs remain. Full Linux release/debug, Windows CMake/Solution, macOS, Docker, smoke and unit-test CI passed. Merge commit: `74ea517d13333248d0e0868a5b212eced5ef24dc`.
- PR #163 — defines pointer-free summon inheritance and creature interaction policy on the stable-ID registry. Normal-world pairs remain compatible; same-instance inheritance is atomic/idempotent; invalid, cross-instance, owned/unowned and Closing/Destroyed interactions fail closed. Full Linux release/debug, Windows CMake/Solution, macOS, Docker, smoke and dedicated ownership-policy tests passed. Merge commit: `dbcc809bac57bb78425ca39c2523c723cef79bb0`.
- PR #168 — adds `InstanceCreatureBinder`, a synchronous adapter from runtime objects exposing `getID()` to the authoritative stable-ID registry. It supports heterogeneous master/summon types, authoritative-owner unbind and lifetime-safe operations without retaining runtime pointers. The first Linux-debug compile exposed unconstrained templates selecting `int` as an object; the overloads were constrained to real `getID()` types and the full rerun passed. Linux debug completed 444/444 tests; Linux release, Canary/Global smoke, Windows CMake/Solution, macOS and Docker also passed. Merge commit: `2cd7ecacef872fe247833515602d670626a9ff18`.
- PR #174 — adds `InstanceCreatureBinder::inheritAndApply(...)`, a compensating transaction for master/summon ownership. It validates and inherits before the link mutation, rolls back only ownership added by the current call after a false result or exception, preserves pre-existing ownership, and detects ownership changes during rollback rather than unregistering a newer foreign owner. Tests cover success, false/exception rollback, cross-instance rejection, existing ownership, normal-world behavior and a simulated ownership race. Autofix, Fast Checks, Lua, Linux debug/release, Canary smoke, Windows CMake/Solution, macOS and Docker all passed. Merge commit: `409685766e871859775d3286fb989d9d7b0e4533`.
- PR #183 — adds `InstanceScopedEvent`, a lazy liveness check for scheduled/delayed callbacks so a callback for a Closing/Destroyed instance can detect and skip itself. Merge commit: `9441d984ecd127b16542622d6fdb72d4878b583b`.
- PR #201 — gives `Game` ownership of the runtime `InstanceManager` via `Game::getInstanceManager()`, the single manager instance every later PR consumes. Merge commit: `fbaf1951d836894a24e83a31ec43f8cc7acb1f14`.
- PR #231 — `Game::removeCreature()` automatically unregisters a removed creature's instance ownership, closing the loop the earlier registry/binder PRs opened. Merge commit: `756885fc70f30c81e5e68d53b078095f83ca64fe`.
- PR #233 — gives `closeExpiredInstances()` a real periodic owner: `Game::start()` registers a dispatcher cycle event that calls it. Merge commit: `8a0889b18acf6aa384eb5081b90f707d4febfa95`.

### Instanced Test Arena (real InstanceManager consumer)

The Instanced Test Arena program (`docs/agents/programs/INSTANCED_TEST_ARENA_PROGRAM.md`) is the first genuine production consumer of the instance foundation above — a small administrator-only vertical slice, not a generic dungeon framework.

- PR #287 — fixes a stale claim in this document's sibling `docs/architecture/instance-manager.md` and adds `docs/architecture/instanced-test-arena.md`, the OTBM-evidence-backed region plan (two disjoint 12x7 regions on `data-canary/world/canary.otbm`'s "Tps Room"). Merge commit: `47270c39f4e36568e8440cf6d2f421f5f09e6f67`.
- PR #289 — adds `InstanceArenaService`, owning the two configured regions and the create/activate/close arena lifecycle, exposed via `Game::getInstanceArenaService()`. Merge commit: `7e8f298f126fae0e2d010e25d927eb5d00c92eaf`.
- PR #295 — adds the admin-gated `/instancearena create|leave|close` talkaction and matching `Game.createInstanceArena`/`leaveInstanceArena`/`closeInstanceArena` Lua bindings, plus `InstanceArenaService`'s per-player enter/leave/close session API. Merge commit: `d9b10c322cd6bb9690c2a29fd3354082dde066f9`.
- PR #304 — `InstanceArenaService::enterArena()` spawns and registers one real monster (Cave Rat) in the reserved region, rolling the whole arena back on any spawn/registration failure; a cleanup callback empties the instance's creature registry before `close()`. `Game::getInstanceCreatureBinder()` wires the engine's one production summon-creation call site (`Monster::onThinkDefense()`) to the already-tested instance-aware `Creature::setMaster(master, binder, reload)` overload, so summons made by an instance-owned monster inherit its owner; normal-world summons are unaffected. CI caught a real compile error (a `shared_ptr<Monster>` passed where `InstanceCreatureBinder::bind()`'s template needs a dereferenced value) which was fixed before merge. Merge commit: `cb22a5063bc10c306932c407f6c02c799dfc5ba3`.
- PR #307 — every arena instance now gets a real 15-minute `InstanceDefinition::timeout` instead of running forever, so the existing periodic `closeExpiredInstances()` sweep (`Game::start()`, PR #233) actually closes idle arenas. `InstanceArenaService::reapExpiredSessions()` runs on that same tick to evacuate and forget any player session left behind by a timeout-driven close (the only prior forgetting path was the manual `closeArenaForPlayer()`). `enterArena()` schedules a one-shot closing-warning message two minutes before the timeout, guarded by `InstanceScopedEvent` (its first real production call site) so it is a no-op if the arena already closed. CI caught a real clang-format-version mismatch (local v18 vs. CI's pinned v17 disagreeing on how to wrap a 6-parameter constructor's initializer list); clang-format-17 was installed locally to match CI exactly going forward. Merge commit: `6a0cfcff5004c22bea649c8937357dc747e0619e`.

### CI reliability

- PR #132 — required `Build - Linux / Compile (linux-release)` is emitted whenever main CI runs.
- PR #141 — main CI runs for every pull request, removing the remaining path-filter deadlock for required checks.

### Already merged multi-channel phases

- PR #69 — registry/schema/config and cluster primitives.
- PR #74 — Redis-backed cluster session lifecycle.
- PR #102 — house ownership mirror.
- PR #148 — `cluster_sessions` DB dual-write defense-in-depth layer.
- PR #152 — economic-ledger idempotency for market-offer expiry.

Do not extend these phases as part of the engine architecture roadmap below.

## Current repository activity outside this roadmap

At the time of this refresh, notable separate open work includes:

- PR #136 — multi-channel runtime heartbeat and fail-closed availability; outside current scope.
- PR #155 — checksum-free transport framing correction; relevant to the later packet-level protocol E2E phase but independent from instance ownership.
- gameplay and AI/world-validation PRs continue independently and must be re-queried before every edit.

Every agent must query GitHub again before editing because this list changes quickly.

## Current engine workstream

### Instance-aware `Creature::setMaster` call-site — done

`Creature::setMaster(newMaster, InstanceCreatureBinder&, reloadCreature)` (commit `f4e395565eb86bf4df52c4c277e3192cfd66e0b3`, `src/creatures/creature.cpp`) connects the tested `inheritAndApply(...)` transaction to the real mutation exactly as originally specified below: no `InstanceManager`/binder pointer stored in `Creature`, existing `setMaster(master, reload)` unchanged for normal-world callers, cross-instance/owned-unowned/Closing/Destroyed assignments rejected before any mutation. All the "required tests" below are covered by `instance_creature_binder_test.cpp`'s `InstanceAwareSetMaster*` cases.

The one remaining piece — an actual production call site passing a real binder — is also done: PR #304 wires the engine's one summon-creation call site (`Monster::onThinkDefense()`) to this overload via `Game::getInstanceCreatureBinder()`. See "Instanced Test Arena" above for the full history.

Original design boundary (preserved for reference; already satisfied):

- forward-declare `InstanceCreatureBinder` in `creature.hpp`;
- add an explicit overload accepting `InstanceCreatureBinder &`, while preserving the existing `setMaster(master, reload)` function unchanged for normal-world callers;
- for a non-null master, call `binder.inheritAndApply(master, self, callback)` before the existing master/summon lists are mutated;
- the callback must execute the existing synchronous `setMaster(master, reload)` path and return its result;
- cross-instance, owned/unowned and Closing/Destroyed assignments must be rejected before setting `summoned`, changing `m_master`, reloading the creature or editing summon lists;
- clearing a master must preserve the summon's established instance ownership and may delegate to the existing null-master behavior;
- do not add a global `InstanceManager`, a binder field, a raw pointer or a long-lived runtime reference.

Follow-up requirements in the same phase — status:

- instance-aware monster spawn creation: done for the arena's own spawn (`InstanceArenaService::enterArena()`, PR #304); ordinary map `Spawn`/`SpawnNpc` instance-scoping remains open and out of the arena program's scope (the arena never touches ordinary spawns).
- automatic unregister when owned creatures leave the runtime: done (`Game::removeCreature()`, PR #231).
- removal of all owned creatures during close: done for the arena (`InstanceArenaService`'s cleanup callback, PR #304).
- spectator/target/combat call sites using the central relation policy: open — tracked as Instanced Test Arena program queue item 6, to be driven by concrete leaks found running two real arenas, not speculative changes.
- proof that region reuse does not expose stale entities: open — tracked as program queue item 7 (two-parallel-instances E2E).

## Remaining roadmap

### A. Creature and spawn ownership

- ~~wire the real `Creature::setMaster` mutation to the merged binder transaction~~ done (see above);
- ~~wire monsters~~ done for the arena's own spawn (PR #304); NPCs and general instance-created spawns remain open and out of the current program's scope;
- ~~automatically unregister removed owned creatures~~ done (`Game::removeCreature()`, PR #231);
- keep default/non-instanced entities unchanged — verified for every change so far (documented backward-compatibility argument per PR);
- prevent cross-instance visibility/targeting where required — open, program queue item 6;
- ~~remove owned entities during close~~ done for the arena (PR #304);
- prove no entity leaks remain after region reuse — open, program queue item 7.

### B. Scheduler and event ownership

`InstanceScopedEvent` (PR #183) and `Game::start()`'s periodic
`closeExpiredInstances()` sweep (PR #233) are merged and general-purpose.
PR #307 supplies `InstanceScopedEvent`'s first real production call site: a
one-shot closing-warning message `InstanceArenaService::enterArena()`
schedules via the dispatcher, guarded so it is a no-op if the arena already
closed by the time it fires.

- tag scheduled tasks/events with `InstanceId` — done for the arena's own
  closing-warning callback (PR #307); no *general* engine-wide mechanism
  exists for arbitrary scheduled tasks, and none is planned by this program;
- cancel or invalidate callbacks during close — done for that same callback
  (a lazy liveness check via `InstanceScopedEvent::isLive()`, not active
  cancellation - by design, see `instance_scoped_event.hpp`);
- callbacks must not run against destroyed/reused instance state — done,
  proven by a real unit test (`ClosingWarningIsANoOpAfterTheArenaAlreadyClosed`,
  `instance_arena_service_test.cpp`);
- test close racing a pending callback — done for the arena's own callback;
  a general engine-wide race test remains open and out of scope;
- preserve current behavior for unowned global events — satisfied by
  construction (`InstanceScopedEvent` is opt-in per call site).

### C. Player enter/leave API

Done for the arena's own narrow scope (PR #295/#307): `InstanceArenaService::enterArena/leaveArena/closeArenaForPlayer`, keyed by stable player id, one session per player.

- validated entry into an active instance — done;
- remember a safe return position — done;
- reject unknown, closing or destroyed instances — done (`createArena()` fails cleanly when no region is free; a player can't enter a Closing/Destroyed arena because `enterArena()` only ever creates a fresh one);
- evacuate players before releasing the region — done (`closeArenaForPlayer()` returns the saved position, then releases; `reapExpiredSessions()`, PR #307, does the same for a timeout-driven close);
- define logout, reconnect, death and timeout behavior — timeout is done (PR #307, 15-minute `InstanceArenaService::ArenaTimeout`); logout/reconnect/death remain open, tracked as program queue item 6 (once concrete gaps are found running two real arenas);
- ensure no player is stranded in a reusable region — proven only for the manual-close path so far; the two-parallel-instances E2E (queue item 7) is the full proof.

### D. Lua API

This generic `Instance.*` API below was never built, by deliberate choice: the Instanced Test Arena program (PR #295) exposes only the narrow, feature-specific `Game.createInstanceArena`/`leaveInstanceArena`/`closeInstanceArena` bindings the one admin talkaction needs, matching this codebase's existing narrow-Lua-surface convention (e.g. multichannel's `getPlayerClusterChannel`) rather than this suggested generic API. Documented bindings, stable multi-return errors, no raw pointer exposure and focused Lua tests are all satisfied for that narrower surface. Building the generic API below remains a separate, not-yet-requested later concern.

Original suggested minimal API (kept for reference, not built):

```lua
Instance.create(definition)
Instance.get(id)
Instance.enter(player, id)
Instance.leave(player)
Instance.close(id)
Instance.getState(id)
```

### E. Cleanup and recovery

Done for the arena's own scope (PR #304): its cleanup callback removes the one monster it spawns (and any summons, once inherited) before the instance closes; a failed close is quarantined by `InstanceManager`'s existing invariant rather than releasing a dirty region.

- remove temporary creatures, items, spawns and callbacks — done for the arena's own monster/summons; the arena creates no items, so item cleanup is out of scope;
- evacuate players before region release — done;
- idempotent cleanup retries — inherited from `InstanceManager`'s existing exactly-once cleanup guarantee, not re-implemented;
- explicit behavior when cleanup fails — inherited from `InstanceManager`'s existing quarantine behavior;
- metrics/logging for failed cleanup — open, not yet needed at this program's current scale;
- startup/recovery policy for referenced or interrupted instances — open, out of the current program's scope (no persistence of instance state across a server restart exists or is planned here).

### F. Two-instance end-to-end test

Prove that two simultaneous instances:

- reserve different regions;
- isolate creatures, players and scheduled events;
- can close independently;
- return players safely;
- release and reuse regions without stale state.

### G. Protocol/session end-to-end verification

The unit-level transport and token work is merged. A packet-level integration harness still needs to prove:

- login response sends a secure token for modern session auth;
- the game connection redeems it once;
- replay is rejected;
- expired, wrong-character and wrong-profile tokens fail;
- legacy and password-auth paths remain unchanged;
- Adler32, sequence checksum, no-checksum and compression profiles remain compatible;
- malformed and truncated encrypted frames are rejected.

This work can run in parallel if no active PR touches `ProtocolLogin`, `ProtocolGame`, `IOLoginData`, transport codecs or protocol profiles. PR #155 currently touches this area, so protocol E2E work must wait for it to merge or close.

## Recommended execution order

```text
instance-aware Creature::setMaster call-site
    └─> spawn/NPC ownership + automatic unregister
          └─> owned-creature cleanup + isolation call sites
                └─> scheduler/event ownership
                      └─> player enter/leave
                            └─> Lua API
                                  └─> cleanup/recovery
                                        └─> two-instance E2E

Protocol/session packet-level E2E starts after current transport PR collisions clear.
```

## CI gate

Runtime C++ PRs must pass all applicable jobs:

- autofix/formatting/static analysis;
- Lua tests;
- Linux debug tests;
- required Linux release;
- Canary and Global datapack smoke tests when affected;
- Windows CMake;
- Windows Solution/MSBuild;
- macOS;
- Docker when affected;
- dedicated feature tests.

Python/deployment PRs must additionally cover path safety, symlink escape, dry-run, failure phases, rollback and CLI smoke tests. Claims of real-server compatibility require a real Canary staging smoke test.

## Agent rules

Before editing:

1. fetch current `main` and record its SHA;
2. list open PRs and active task records;
3. inspect changed filenames for collisions;
4. declare one workstream and planned files;
5. create a fresh branch from current `main`.

When CI fails:

1. read the actual log/artifact;
2. identify the exact failing job/test;
3. fix the code or test contract, never bypass it;
4. rerun affected and full CI;
5. if the bug also exists on `main`, fix it separately.

After each merge, update this file with:

- merged PR and commit;
- tests/CI result;
- newly completed scope;
- exact remaining work;
- active blockers and known limitations.

## Definition of done

The engine architecture program is complete when:

- concrete region ownership is integrated with `InstanceManager` — completed by PR #151;
- lifecycle-safe creature identity registration is merged — completed by PR #159;
- summon inheritance and interaction policy are merged — completed by PR #163;
- runtime-ID binding is merged — completed by PR #168;
- compensating master/summon ownership transaction is merged — completed by PR #174;
- runtime creature/spawn and scheduler/event ownership are merged;
- player enter/leave and Lua APIs are merged;
- cleanup/recovery and two-instance isolation tests pass;
- protocol/session packet-level end-to-end tests pass;
- current `main` CI is green;
- obsolete PRs are closed;
- this handoff reflects the final state.
