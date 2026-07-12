# Canary Engine — Project Handoff and Roadmap

> Last verified: 2026-07-12
>
> Repository: `blakinio/canary`
>
> Verified `main` at refresh start: `17a392cad0e25ad20765c1bc428fca744a691cc6`
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

- PR #107 — `InstanceManager` lifecycle/registry foundation with strong IDs, fixed slot capacity, timeout and concurrency tests.
- PR #121 — thread-safe `MapRegionPool` with 3D overlap validation, deterministic reservation, release/reuse and concurrency tests.

### CI reliability

- PR #132 — required `Build - Linux / Compile (linux-release)` is emitted whenever main CI runs.
- PR #141 — main CI runs for every pull request, removing the remaining path-filter deadlock for required checks.

### Already merged multi-channel phases

- PR #69 — registry/schema/config and cluster primitives.
- PR #74 — Redis-backed cluster session lifecycle.
- PR #102 — house ownership mirror.

Do not extend these phases as part of the engine architecture roadmap below.

## Current repository activity outside this roadmap

At the time of this refresh, notable separate open work includes:

- PR #136 — multi-channel runtime heartbeat and fail-closed availability; outside current scope and previously had real cross-platform compile failures.
- PR #148 — multi-channel `cluster_sessions` DB dual-write; outside current scope.
- PR #147 — draft OTBM HD sprite pipeline; separate AI/map tooling work.
- PR #149 — draft The Beginning/Zirella quest repair; separate gameplay work.

Every agent must query GitHub again before editing because this list changes quickly.

## Remaining roadmap

### A. Connect `MapRegionPool` to `InstanceManager`

This is the next engine-architecture PR.

Requirements:

- `InstanceManager` reserves a concrete `MapRegion` when creating an instance;
- the instance record exposes its reserved region read-only;
- creation fails atomically when no region is available;
- close releases the region only after cleanup succeeds or the defined failure policy completes;
- repeated close/release remains idempotent;
- timeout close uses the same path as explicit close;
- no full map copy;
- no global singleton;
- no multiworld or channel identifier.

Tests:

- successful create binds exactly one region;
- capacity is determined by region availability;
- close returns the same region to the pool;
- concurrent create never double-reserves a region;
- concurrent/repeated close releases once;
- cleanup failure cannot silently expose a dirty region for reuse;
- timeout close releases through the same lifecycle.

### B. Creature and spawn ownership

After the region integration merges:

- associate monsters, summons, NPCs and instance-created spawns with `InstanceId`;
- default/non-instanced entities retain current behavior;
- prevent cross-instance visibility/targeting where required by the map model;
- remove owned entities during close;
- prove no entity leaks remain after region reuse.

### C. Scheduler and event ownership

- tag scheduled tasks/events with `InstanceId`;
- cancel or invalidate callbacks during close;
- callbacks must not run against destroyed/reused instance state;
- test close racing a pending callback;
- preserve current behavior for unowned global events.

### D. Player enter/leave API

- validated entry into an active instance;
- remember a safe return position;
- reject unknown, closing or destroyed instances;
- evacuate players before releasing the region;
- define logout, reconnect, death and timeout behavior;
- ensure no player is stranded in a reusable region.

### E. Lua API

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

### F. Cleanup and recovery

- remove temporary creatures, items, spawns and callbacks;
- evacuate players before region release;
- idempotent cleanup retries;
- explicit behavior when cleanup fails;
- metrics/logging for failed cleanup;
- startup/recovery policy for referenced or interrupted instances.

### G. Two-instance end-to-end test

Prove that two simultaneous instances:

- reserve different regions;
- isolate creatures, players and scheduled events;
- can close independently;
- return players safely;
- release and reuse regions without stale state.

### H. Protocol/session end-to-end verification

The unit-level transport and token work is merged. A packet-level integration harness still needs to prove:

- login response sends a secure token for modern session auth;
- the game connection redeems it once;
- replay is rejected;
- expired, wrong-character and wrong-profile tokens fail;
- legacy and password-auth paths remain unchanged;
- Adler32, sequence checksum, no-checksum and compression profiles remain compatible;
- malformed and truncated encrypted frames are rejected.

This work can run in parallel if no active PR touches `ProtocolLogin`, `ProtocolGame`, `IOLoginData`, transport codecs or protocol profiles.

## Recommended execution order

```text
MapRegionPool ↔ InstanceManager integration
    └─> creature/spawn ownership
          └─> scheduler/event ownership
                └─> player enter/leave
                      └─> Lua API
                            └─> cleanup/recovery
                                  └─> two-instance E2E

Protocol/session packet-level E2E may run in parallel when file ownership is clear.
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

- `MapRegionPool` is integrated with `InstanceManager`;
- creature/spawn and scheduler/event ownership are merged;
- player enter/leave and Lua APIs are merged;
- cleanup/recovery and two-instance isolation tests pass;
- protocol/session packet-level end-to-end tests pass;
- current `main` CI is green;
- obsolete PRs are closed;
- this handoff reflects the final state.
