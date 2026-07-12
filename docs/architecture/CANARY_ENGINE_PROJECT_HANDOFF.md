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

### Instance-aware `Creature::setMaster` call-site

The manager registry, ownership policy, runtime-ID binder and rollback transaction are complete in PRs #159, #163, #168 and #174. The next focused PR must connect the tested transaction to the real `Creature::setMaster` mutation without storing an `InstanceManager` or binder pointer in `Creature`.

Preferred boundary:

- forward-declare `InstanceCreatureBinder` in `creature.hpp`;
- add an explicit overload accepting `InstanceCreatureBinder &`, while preserving the existing `setMaster(master, reload)` function unchanged for normal-world callers;
- for a non-null master, call `binder.inheritAndApply(master, self, callback)` before the existing master/summon lists are mutated;
- the callback must execute the existing synchronous `setMaster(master, reload)` path and return its result;
- cross-instance, owned/unowned and Closing/Destroyed assignments must be rejected before setting `summoned`, changing `m_master`, reloading the creature or editing summon lists;
- clearing a master must preserve the summon's established instance ownership and may delegate to the existing null-master behavior;
- do not add a global `InstanceManager`, a binder field, a raw pointer or a long-lived runtime reference;
- do not yet mix spawn/NPC creation, automatic unregister, spectator filtering, combat, players or Lua into this PR.

Required tests using real runtime creatures where practical:

- normal-world assignment through the legacy overload remains unchanged;
- owned master registers an unowned summon and commits only after successful linking;
- same-instance assignment/reassignment remains valid and does not duplicate ownership;
- cross-instance assignment leaves ownership, `m_master`, summon lists and `summoned` state unchanged;
- an unowned master cannot take an owned summon;
- clearing the master preserves the summon's instance boundary;
- no binder or manager pointer is retained by `Creature`;
- existing rollback-transaction tests remain green.

Follow-up requirements in the same phase:

- instance-aware monster and NPC spawn creation;
- automatic unregister when owned creatures leave the runtime;
- removal of all owned creatures during close;
- spectator/target/combat call sites using the central relation policy;
- proof that region reuse does not expose stale entities.

## Remaining roadmap

### A. Creature and spawn ownership

- wire the real `Creature::setMaster` mutation to the merged binder transaction;
- wire monsters, NPCs and instance-created spawns;
- automatically unregister removed owned creatures;
- keep default/non-instanced entities unchanged;
- prevent cross-instance visibility/targeting where required;
- remove owned entities during close;
- prove no entity leaks remain after region reuse.

### B. Scheduler and event ownership

- tag scheduled tasks/events with `InstanceId`;
- cancel or invalidate callbacks during close;
- callbacks must not run against destroyed/reused instance state;
- test close racing a pending callback;
- preserve current behavior for unowned global events.

### C. Player enter/leave API

- validated entry into an active instance;
- remember a safe return position;
- reject unknown, closing or destroyed instances;
- evacuate players before releasing the region;
- define logout, reconnect, death and timeout behavior;
- ensure no player is stranded in a reusable region.

### D. Lua API

Suggested minimal API:

```lua
Instance.create(definition)
Instance.get(id)
Instance.enter(player, id)
Instance.leave(player)
Instance.close(id)
Instance.getState(id)
```

Requirements:

- documented bindings and stable errors;
- no raw pointer exposure;
- validation and permission rules;
- focused Lua tests.

### E. Cleanup and recovery

- remove temporary creatures, items, spawns and callbacks;
- evacuate players before region release;
- idempotent cleanup retries;
- explicit behavior when cleanup fails;
- metrics/logging for failed cleanup;
- startup/recovery policy for referenced or interrupted instances.

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
