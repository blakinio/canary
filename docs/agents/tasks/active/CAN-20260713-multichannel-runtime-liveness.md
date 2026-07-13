---
task_id: CAN-20260713-multichannel-runtime-liveness
program_id: CAN-PROGRAM-MULTICHANNEL
coordination_id: ""
status: in_review
agent: "claude"
branch: claude/canary-multichannel-cluster-e1jhrr (Part A); claude/canary-multichannel-redis-ping (Part B)
base_branch: main
created: 2026-07-13T20:39:00Z
updated: 2026-07-13T21:20:00Z
last_verified_commit: 6fb9c65d3e8b9105e65515dc2b03827a06753eb0
risk: medium
related_issue: ""
related_pr: ""
depends_on: []
blocks: []
owned_paths:
  exclusive:
    - src/game/multichannel/cluster_runtime.hpp
    - src/game/multichannel/cluster_runtime.cpp
    - src/game/multichannel/redis_client.hpp
    - src/game/multichannel/hiredis_redis_client.hpp
    - src/game/multichannel/hiredis_redis_client.cpp
    - src/game/multichannel/cluster_config_validator.hpp
    - src/game/multichannel/cluster_config_validator.cpp
    - tests/unit/game/multichannel/cluster_runtime_test.cpp
    - tests/unit/game/multichannel/channel_registry_test.cpp
    - tests/unit/game/multichannel/channel_switch_service_test.cpp
    - tests/unit/game/multichannel/cluster_config_validator_test.cpp
    - tests/shared/game/multichannel/fake_redis_client.hpp
  shared:
    - src/game/game.cpp
    - src/canary_server.cpp
    - docs/multichannel/ARCHITECTURE.md
    - docs/multichannel/DECISION_MATRIX.md
    - docs/multichannel/MIGRATION.md
    - docs/multichannel/OPERATIONS.md
    - docs/multichannel/TEST_PLAN.md
  read_only:
    - src/game/multichannel/channel_runtime_registry.hpp
    - src/game/multichannel/channel_runtime_status.hpp
    - src/game/multichannel/channel_switch_service.cpp
    - src/game/multichannel/channel_registry.cpp
modules_touched:
  - ClusterRuntime
  - IRedisClient / HiredisRedisClient / FakeRedisClient
  - ClusterConfigValidator
reuses:
  - ChannelRuntimeRegistry (PR #136, already merged - heartbeat cache/TTL/fail-closed logic reused unchanged)
  - ChannelRegistry::getLoginListChannels live-filter delegation (PR #136, already merged)
  - ChannelSwitchService live-availability branch (PR #136, already merged)
public_interfaces:
  - "IRedisClient::ping() (new)"
  - "ClusterRuntime: new graceful-shutdown publish method (name TBD during implementation)"
  - "ClusterConfigValidationInput::redisPingOutcome (new)"
cross_repo_tasks: []
---

# Goal

User-requested scope (verbatim intent, translated from Polish instructions):
1. `ChannelRuntimeRegistry` — verify/complete a real heartbeat cycle.
2. Login gateway — verify/complete live runtime-based channel filtering.
3. `ClusterConfigValidator` — add a real live Redis `PING` check, distinguishing
   no-config / DNS failure / connection refused / timeout / auth failure /
   unexpected response, fail-closed only when clustering actually requires Redis.

Explicitly out of scope this task: house double-ownership fix, DIRTY-session
admin tooling (both need a shared cross-process DB-row-handoff design first -
see `docs/multichannel/ARCHITECTURE.md` §7/§5.3).

# Acceptance criteria

- [x] Verified current `origin/main` (not stale docs) for what's actually shipped.
- [x] Real, previously-undiscovered gaps in heartbeat/login-filtering fixed and tested (graceful-shutdown OFFLINE publish; cross-cutting/reconnect/empty-list/live-switch test coverage).
- [x] `IRedisClient::ping()` implemented (Hiredis + Fake) and wired into `ClusterConfigValidator`, fail-closed only when Redis is actually required.
- [x] New/extended unit tests for every scenario in the user's checklist that wasn't already covered.
- [ ] Current-head GitHub checks verified (not just fast checks - full build matrix) - **pending, PRs about to be opened**.
- [x] Module catalogue, docs (`ARCHITECTURE.md`/`DECISION_MATRIX.md`/`MIGRATION.md`/`AGENT_HANDOFF.md`) updated to reflect true current state, correcting the stale P0.4 claim found along the way.
- [ ] Two PRs opened (heartbeat+login-filter completeness; Redis ping validator), not merged without explicit user approval - **about to open**.

# Confirmed context

**Critical finding, contradicts `docs/multichannel/AGENT_HANDOFF.md`:** that handoff
document (dated 2026-07-12, audited against a *different* `main` SHA
`97954d5d468190aeb46f223e87309396e2bfc3fa` than this task's verified
`6fb9c65`) describes only PR #69/#74/#75/#102 as merged and lists P0.4
("realny runtime heartbeat kanałów") as an open gap. That is **stale**.
`git log` on the actual current `origin/main` shows PR #136
(`feat/multichannel-runtime-heartbeat`, merged, and the same PR this agent's
own earlier session fixed CI on) already delivered:

- `ChannelRuntimeRegistry` (`channel_runtime_registry.hpp`) - Redis-backed
  heartbeat cache with TTL, local staleness cutoff independent of Redis TTL,
  fail-closed clearing on any Redis failure. Already has 5 gtest cases
  (`channel_runtime_registry_test.cpp`) covering fresh/full/maintenance/
  crash-via-TTL/Redis-outage/local-staleness.
- `ClusterRuntime::renewAllAndCollectExpired` (`cluster_runtime.cpp:167`)
  already builds a full `ChannelRuntimeStatus` (channelId, instanceId,
  nodeId from `CANARY_NODE_ID` env or `external_host`, startedAtMs,
  lastHeartbeatMs, status ONLINE/MAINTENANCE from the `channels.maintenance`
  flag, playersOnline from tracked-session count, buildSha/mapHash/dataHash
  from env vars or `channels.map_hash`) and calls
  `g_channelRuntimeRegistry().publishAndRefresh(...)` every cycle, plus
  queues a best-effort `channel_runtime_status` DB diagnostic mirror write.
  Scheduled via the existing `g_dispatcher().cycleEvent(heartbeatIntervalMs,
  ...)` pattern from `Game::init` (`game.cpp:864`) - the same dispatcher
  every other periodic game job uses, gated behind
  `MULTICHANNEL_ENABLED`.
- `ChannelRegistry::getLoginListChannels()` (`channel_registry.cpp:91`)
  already delegates to `g_channelRuntimeRegistry().getLoginListChannels(...)`
  when the runtime registry is enabled, falling back to static
  `isSelectable()` filtering otherwise (single-channel-compatible).
- `ProtocolLogin::getCharacterList` (`protocollogin.cpp:41`) already calls
  this live-filtered list on **both** the legacy (`LegacyCharacterList`,
  line 98) and modern (line 185) paths, and on an empty result calls
  `disconnectClient(...)` with a clear message instead of fabricating a
  fallback single-world endpoint - verified by direct code read, not
  assumed.
- `ChannelSwitchService::evaluate` (`channel_switch_service.cpp:107`)
  already overrides `targetChannelOnline`/`targetChannelFull` with live
  `g_channelRuntimeRegistry().getAvailability(...)` data when enabled.
- `multichannel::wallClockMs()` (`wall_clock.hpp`) and `OTSYS_TIME()`
  (`utils/tools.cpp:1626`) both use `std::chrono::system_clock` - confirmed
  **not** mixed with a monotonic clock anywhere in this path.

**Real gaps found (not already covered), this is what this task actually
delivers:**

1. Graceful shutdown does not publish `OFFLINE` or otherwise proactively
   invalidate this channel's heartbeat key - `Game::setGameState`'s
   `GAME_STATE_SHUTDOWN` case (`game.cpp:943`) has zero multichannel-aware
   code. A clean shutdown is currently indistinguishable from a crash to
   every other channel/the login gateway until the heartbeat TTL elapses.
2. No test exercises the *cross-cutting* path: that `ClusterRuntime::
   renewAllAndCollectExpired` actually reaches `ChannelRuntimeRegistry`
   (existing tests cover session-lease renewal and `ChannelRuntimeRegistry`
   in isolation, never both through the real call chain), including
   reconnect-after-outage recovery.
3. No test exercises `ChannelRegistry::getLoginListChannels()`'s
   *delegation* branch (only the static fallback is tested at that layer)
   or the fully-empty-result scenario through that integration boundary.
4. No test exercises `ChannelSwitchService`'s live-availability branch at
   all (0 references to `ChannelRuntimeRegistry`/`getAvailability` in
   `channel_switch_service_test.cpp`).
5. `DRAINING` status is designed (`ChannelRuntimeStatus::hasValidState()`
   accepts it) but no code path ever publishes it - the GM "drain a
   channel" command does not exist yet (confirmed, matches this session's
   own earlier finding). **Decision: document as an explicit, honest
   limitation, do not half-implement** - draining needs an admin-command
   trigger mechanism that is out of scope here.
6. Both session-lease renewal (`ClusterSessionManager::renew`, one call per
   tracked account) and heartbeat publish/refresh (one call per known
   channel) run as **synchronous Redis I/O on the main game dispatcher
   thread** (`Game::renewClusterSessions` → `g_dispatcher().cycleEvent`).
   This is a pre-existing characteristic from Phase 2 (PR #74) and PR #136,
   not something introduced here. Redis client connect/command timeouts
   (`HiredisRedisClient::Options::connectTimeoutMs`, default 2000ms) bound
   the worst case per stalled call, but a full redesign to move this off
   the main thread is out of scope for this task (would touch already-
   shipped, already-tested core session-safety code) - documented
   precisely rather than fixed blind, per this project's established
   discipline.
7. `ClusterConfigValidator::validate` is a pure function; nothing in the
   current codebase ever performs a live `PING`. `IRedisClient` has no
   `ping()` method. The Redis client in `canary_server.cpp` is constructed
   *after* `validate()` already ran, so wiring a live check in requires
   reordering that construction earlier (reusing the same client instance,
   not opening a second connection).

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| `ChannelRuntimeRegistry` | Reuse unchanged | `channel_runtime_registry.hpp` | Already correct fail-closed cache; only the *publisher* side (shutdown) and *test coverage* have gaps. |
| `FakeRedisClient` | Extend with `ping()` | `tests/shared/game/multichannel/fake_redis_client.hpp` | Only existing `IRedisClient` implementer besides Hiredis; must stay instantiable. |
| `HiredisRedisClient::ensureConnected` | Extend to capture classified error detail | `hiredis_redis_client.cpp:114` | Already has the connect/AUTH/SELECT sequence; reuse its control flow rather than a second connect path. |

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Do not implement DRAINING status | No trigger mechanism (GM drain command) exists; would be dead code | none - documented in ARCHITECTURE.md instead |
| Do not move Redis I/O off the main dispatcher thread | Pre-existing since Phase 2/PR #74; redesign is large, high-risk, touches already-shipped session-safety code; timeouts bound the damage | none - documented as a known limitation |
| `ClusterConfigValidationInput.redisPingOutcome` stays a caller-supplied field, not live I/O inside `validate()` | Preserves the validator's existing "pure function, fully unit-testable" contract | none |
| `std::nullopt` ping outcome is treated as a hard failure when Redis is required | Fail-closed default; "never attempted" must not silently pass as "succeeded" | none |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `src/game/multichannel/cluster_runtime.{hpp,cpp}` | exclusive | Graceful-shutdown OFFLINE publish | planned |
| `src/game/game.cpp` | shared | Wire shutdown publish into `GAME_STATE_SHUTDOWN` | planned |
| `src/game/multichannel/redis_client.hpp` | exclusive | `RedisPingOutcome`/`RedisPingResult`/`IRedisClient::ping()` | planned |
| `src/game/multichannel/hiredis_redis_client.{hpp,cpp}` | exclusive | Real `ping()` with error classification | planned |
| `tests/shared/game/multichannel/fake_redis_client.hpp` | exclusive | Fake `ping()` for tests | planned |
| `src/game/multichannel/cluster_config_validator.{hpp,cpp}` | exclusive | New input field, error values, validation logic | planned |
| `src/canary_server.cpp` | shared | Reorder Redis client construction before `validate()`, perform ping | planned |
| various `tests/unit/game/multichannel/*_test.cpp` | exclusive/shared | New coverage per gap list above | planned |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| (pre-commit, Part A) | `clang-format-18 --dry-run --Werror` on all changed files | passed | |
| (pre-commit, Part B) | `clang-format-18 --dry-run --Werror` on all changed files | passed | |
| (pre-commit, Part B) | `g++ -Wall -Wextra -DCANARY_MULTICHANNEL_REDIS` standalone compile of `hiredis_redis_client.cpp` against real system `hiredis` | passed, 0 warnings | |
| (pre-commit, Part B) | Real local `redis-server`, 5-scenario `ping()` harness | passed | all 5 `RedisPingOutcome` categories + success matched real conditions exactly - see TEST_PLAN.md |
| (pre-commit, Part B) | `cluster_config_validator_test.cpp` standalone-linked against real gtest | 25/25 passed | 8 pre-existing + 9 new |
| (pending) | GitHub Actions full matrix (Linux/Windows/macOS/Docker) on both PR heads | not-run | pending push |

Never write `passed` without verification on the stated commit.

# Failed approaches and dead ends

- First draft of the new `channel_registry_test.cpp`/`channel_switch_service_test.cpp`
  live-availability tests published heartbeats at a fixed logical timestamp
  (`lastHeartbeatMs = 100000`), not realizing `ChannelRegistry::
  getLoginListChannels()`/`ChannelSwitchService::evaluate()` both call
  `multichannel::wallClockMs()` (real wall-clock time) internally rather
  than accepting a caller-supplied clock - the published heartbeat would
  already read as ancient/stale by the time the assertion ran. Fixed by
  capturing `multichannel::wallClockMs()` once per test and using it
  consistently.

# Risks and compatibility

- Runtime: touches the main dispatcher thread's periodic cluster job; kept additive (new method, new call site) rather than altering existing renewal logic.
- Data/migration: none - no schema change.
- Security: `ping()` must not log credentials; only classify/log the hiredis `errstr`.
- Backward compatibility: every new check gated behind `MULTICHANNEL_ENABLED`; single-channel boot path untouched.
- Cross-repo rollout: none - server-internal only.
- Rollback: revert commit(s); no schema/data migration to unwind.

# Remaining work

1. ~~Implement graceful-shutdown OFFLINE publish + wire into `Game::setGameState`.~~ done
2. ~~Add the cross-cutting/integration/empty-list/live-switch tests listed above.~~ done
3. ~~Implement `IRedisClient::ping()` (Hiredis real + Fake), wire into `ClusterConfigValidator`, reorder `canary_server.cpp`.~~ done
4. ~~Update docs with corrected current-state facts and honestly-documented limitations.~~ done
5. ~~Update `docs/agents/MODULE_CATALOG.md`'s multichannel row.~~ done
6. ~~Push both branches, open both PRs.~~ done - PR #292 (`claude/canary-multichannel-cluster-e1jhrr`, Part A: shutdown OFFLINE + test gaps) and PR #293 (`claude/canary-multichannel-redis-ping`, Part B: live Redis PING) are both open against `main`. Monitoring the full CI matrix on both is in progress; no CI results or review comments yet as of this update. Do not merge without explicit user "yes, merge #NNN" per this branch's standing rule.
7. Once both PRs are known-good (green CI), move this task record to `docs/agents/tasks/archive/` and fill in the Completion section below.

# Handoff

## Start here

If resuming: check `git log --oneline -10` on this branch and compare
against the "Remaining work" list above; the code changes are additive and
independently testable per numbered item.

## Do not repeat

Do not re-investigate whether PR #136 already covers heartbeat/login-
filtering - it does, extensively; re-reading `docs/multichannel/
AGENT_HANDOFF.md`'s P0.4 claim at face value is the trap this task's
"Confirmed context" section exists to prevent.

## Required reads

- `AGENTS.md`
- `docs/agents/README.md`
- `docs/multichannel/ARCHITECTURE.md`, `AGENT_HANDOFF.md` (read critically, cross-checked against code - not taken at face value)
- `src/game/multichannel/cluster_runtime.cpp`, `channel_runtime_registry.hpp`, `channel_switch_service.cpp`, `channel_registry.cpp`
- `src/server/network/protocol/protocollogin.cpp`
- `src/game/multichannel/cluster_config_validator.{hpp,cpp}`, `redis_client.hpp`, `hiredis_redis_client.{hpp,cpp}`

## Open questions

None blocking; proceeding with the plan above.

# Completion

- Final status: in progress - both PRs open, CI running, awaiting green matrix and explicit user merge approval
- PR: #292 (Part A - heartbeat/login-filter completeness), #293 (Part B - live Redis PING)
- Merge commit: none yet - not merged
- Program record updated: no (no long-lived program record exists yet for multichannel under `docs/agents/programs/`; could be created as a follow-up)
- Catalogue updated: yes (`docs/agents/MODULE_CATALOG.md`, in PR #292)
- Changelog updated: pending
- Archived at: pending - will move to `docs/agents/tasks/archive/` once both PRs are green and merged
