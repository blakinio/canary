# Canary Engine — Project Handoff and Roadmap

> Last verified: 2026-07-12
>
> Repository: `blakinio/canary`
>
> Purpose: current source of truth for agents continuing the engine architecture work.

## Goal

Harden and modularize Canary without breaking existing clients or datapacks. The active program covers portable builds, deterministic startup, strict AI-content validation, profile-driven protocol transport, secure login sessions, atomic content deployment, targeted dependency migration and instance lifecycle/isolation.

## Scope policy

- Multiworld is paused.
- Do not add another multi-channel phase unless the owner explicitly reopens it.
- Existing merged multi-channel code must remain default-disabled and must not be accidentally broken.
- Use small PRs, one concern per PR.
- Never merge failed, cancelled, stale or incomplete CI.
- Do not push production changes directly to `main`.

## Completed and merged

- PR #17 — portable CPU baseline; native optimization is opt-in.
- PR #21 — strict AI-content task schemas, dependency and identifier validation.
- PR #24 — startup loader waits on a condition variable instead of polling.
- PR #59 — dispatcher latency timer refresh after long startup.
- PR #71 — `TransportProfile` is authoritative for framing, checksum and compression; protocol regression tests added.
- PR #77 — secure single-use `LoginSessionManager` with 256-bit tokens, TTL, hash-only storage and concurrency tests.
- PR #80 — fixes modern-client login rejection.
- PR #82 — wires secure login tokens into the modern `authType == "session"` handshake while preserving legacy/password paths.
- PR #107 — `InstanceManager` lifecycle/registry foundation with strong IDs, slot pool, timeout and concurrency tests.

Additional merged multi-channel phases already present in `main`:

- PR #69 — registry/schema/config and cluster primitives.
- PR #74 — Redis-backed cluster session lifecycle.
- PR #102 — house ownership mirror.

Do not extend these phases in the current workstream.

## Current work

### PR #103 — atomic content deployment engine

Status at last verification:

- open and mergeable;
- deployment workflow green;
- full CI green on its current head;
- branch was created from an older `main` and must be refreshed/rebuilt on current `main` before final merge.

Provides:

- deployment-root confinement;
- traversal and symlink-escape rejection;
- hidden staging directory;
- atomic release publication and `active` switch;
- process health check;
- automatic and idempotent rollback;
- SHA-256 manifest;
- production confirmation gate;
- dry-run;
- failure-phase tests.

Still required after merge:

1. build a full staging datapack from reviewed AI output;
2. run the real compiled `canary_server`;
3. reuse `.github/scripts/smoke_test_canary.py`;
4. verify Lua/datapack loading and startup logs;
5. stop staging cleanly;
6. switch only after successful staging validation;
7. run post-switch health check and rollback on failure.

### PR #106 — dependency migration audit and `SharedPtrManager` DI migration

Status at last verification:

- open and mergeable;
- Linux debug test fails.

Exact blocker:

```text
SharedPtrManagerTest.StoreAndCleanDoesNotCrashOnLiveOrExpiredPointers
runtime_provider.hpp: assertion failed: Type not bound! [T = Logger]
```

Cause: the test installs an isolated DI container and calls `countAllReferencesAndClean()`, which reaches logging without a `Logger` binding.

Required fix:

- bind a test logger, or run the behavior test under the normal test container and keep isolation testing separate;
- restore the previous test container through RAII;
- update/rebuild on current `main`;
- rerun full CI;
- merge only when green.

Audit result: most `g_*()` accessors already use the existing DI container. After #106, migrate `Scripts` in a separate PR. Do not perform a global-accessor mega-refactor.

## Remaining roadmap

### A. Atomic deployment integration

1. merge refreshed #103;
2. real staging Canary integration;
3. production approval/runbook;
4. end-to-end rollback test.

### B. Dependency migration

1. fix and merge #106;
2. migrate `Scripts` to DI with isolated-container tests;
3. introduce constructor injection only where instance isolation or testing requires it.

### C. InstanceManager integration

The lifecycle foundation is merged. Continue in this order:

1. **Map region pool** — physically separated regions, overlap validation, reserve/release, no full-map copy.
2. **Creature/spawn ownership** — creatures, summons, NPCs and spawns associated with `InstanceId`; cleanup and leak tests.
3. **Scheduler/event ownership** — tag and cancel instance-owned callbacks safely during close.
4. **Player enter/leave** — validated entry, safe return position, logout/death/reconnect/closing behavior.
5. **Lua API** — create/get/enter/leave/close/state with documented bindings and stable errors.
6. **Cleanup/recovery** — remove temporary state, cancel timers, evacuate players, return slots only after cleanup.
7. **Two-instance E2E** — prove map, creature, player and timer isolation and slot reuse.

### D. Protocol/session end-to-end verification

Add a packet-level integration harness proving:

- login response sends a secure token for modern session auth;
- the game connection redeems it once;
- replay is rejected;
- expired/wrong-character/wrong-profile tokens fail;
- legacy and password-auth paths remain unchanged;
- Adler32, sequence checksum, no-checksum and compression profiles remain compatible;
- malformed and truncated encrypted frames are rejected.

## Recommended execution order

```text
refresh + merge #103 ──> real staging-server deployment
fix + merge #106 ──────> Scripts DI migration
                            └─> map region pool
                                  └─> creature/spawn ownership
                                        └─> scheduler/event ownership
                                              └─> player API
                                                    └─> Lua API
                                                          └─> cleanup/recovery
                                                                └─> two-instance E2E

Protocol/session E2E may run in parallel if no active PR touches the same protocol files.
```

## CI gate

Runtime C++ PRs must pass all applicable jobs:

- autofix/formatting/static analysis;
- Lua tests;
- Linux debug tests;
- Linux release;
- Canary and Global datapack smoke tests;
- Windows CMake;
- Windows Solution/MSBuild;
- macOS;
- Docker;
- dedicated feature tests.

Python/deployment PRs must additionally cover path safety, symlink escape, dry-run, every failure phase, rollback and CLI smoke tests. Claims of real-server compatibility require a real Canary staging smoke test.

## Agent rules

Before editing:

1. fetch current `main` and record its SHA;
2. list open PRs;
3. inspect changed filenames for collisions;
4. declare one workstream and planned files;
5. create a fresh branch from current `main`.

When CI fails:

1. read the actual log/artifact;
2. identify the exact failing test;
3. fix the code/test contract, never bypass it;
4. rerun affected and full CI;
5. if the bug also exists on `main`, fix it in a separate PR.

After each merge, update this file with:

- merged PR and commit;
- tests/CI result;
- newly completed scope;
- exact remaining work;
- known limitations and active blockers.

## Definition of done

The architecture program is complete when:

- atomic deployment uses a real staging Canary server and rollback is verified;
- #106 and the `Scripts` DI migration are merged;
- all InstanceManager integration phases and two-instance isolation tests are merged;
- protocol/session end-to-end tests pass;
- current `main` CI is green;
- obsolete PRs are closed;
- this handoff reflects the final state.
