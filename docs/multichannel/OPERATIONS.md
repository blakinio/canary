# Operations Runbook

## Redis outage

**Policy: fail closed.**

1. Detection: `ClusterSessionManager` heartbeat/renew calls start failing.
2. Immediately: block new logins and channel switches cluster-wide (every
   process independently fails closed — no coordination needed to *stop*
   doing things), disable global/guild chat and PM delivery with a clear
   in-game message, refuse new session acquisition.
3. Players already `ONLINE` get a grace period of `redisFailureGracePeriod`
   during which the process keeps trying to renew its lease. Local
   gameplay (say, movement, combat on that channel) may continue during
   the grace period since it does not depend on cross-channel
   coordination — but nothing that touches another channel's data
   (switch, cluster chat, market) is allowed.
4. If renewal keeps failing as the lease TTL approaches expiry: enter
   emergency freeze — stop mutating actions, attempt a best-effort DB
   save, and disconnect affected players **before** another process could
   legally acquire their lease. A process must never keep a player's
   session "logically online" past the point another process is entitled
   to take over.
5. Recovery: once Redis is reachable again, re-establish heartbeat, verify
   this process's sessions are still the ones Redis has on record (they
   may have been reassigned during the outage — if so, this process must
   not resume for that player), rebuild presence, then re-enable
   logins/switches last.

## Database outage

**Policy: fail closed, more restrictive than Redis.**

1. Block logins, channel switches, and *all* economic mutations
   immediately (market, mail, bank, house, depot, trade-completion).
2. Enter emergency freeze/maintenance for mutating actions — reads of
   already-loaded in-memory state may continue locally, but nothing may be
   persisted.
3. Reconnect with bounded exponential backoff (mirrors the pattern used
   for Redis reconnect; do not busy-loop).
4. If the DB returns within grace period (`databaseFailureGracePeriod`):
   verify pending transactions, reconcile, then resume — only after full
   validation, not immediately on TCP reconnect.
5. If the DB does not return: controlled disconnect/shutdown, mark
   in-flight sessions `DIRTY`, require recovery validation at next login
   (§5.3 of ARCHITECTURE.md).

## Single channel crash

The other channels are unaffected by construction (independent processes,
independent game state). Requirements for the login gateway and any
cluster-aware tooling:

- Stop offering the dead channel once its heartbeat is stale
  (`> sessionLeaseTtl` since `last_heartbeat`).
- Do **not** touch `players_online`/session rows belonging to *other*
  channels.
- Do **not** reset any global table (guilds, market, VIP, etc.) — a single
  channel's crash is a local event only.
- A dirty session left behind by the crashed channel's players requires
  recovery (§5.3), not automatic reassignment.

## Leader election / cluster-singleton jobs

Inventory of periodic/global jobs that must not run N times in an
N-channel cluster:

| Job | Scope | Notes | Wired? |
|---|---|---|---|
| House rent charging | `per-channel` (corrected — see below) | touches global bank balance, but each channel's houses are already disjoint | n/a |
| House auction settlement | `per-channel` (corrected — see below) | touches `account_house_ownership`, but each channel's houses are already disjoint | n/a |
| Market offer expiration | `cluster-singleton` | market is global | ✅ `IOMarket::checkExpiredOffers` checks `ClusterJobLeadershipRegistry::isLeader("market.expire")` |
| Daily reward reset | `cluster-singleton` | the actual shared state is one `global_storage` row (`DailyReward.storages.lastServerSave`, no `channel_id`), written by each channel's own `global_server_save.lua` `GlobalEvent` on its own schedule | ✅ `global_server_save.lua` checks `Game.tryClaimClusterJobLeadership("daily.reward.reset")`, a new Lua-exposed wrapper around `ClusterJobLeadershipRegistry` |
| Global boosted creature/boss selection | `cluster-singleton` | `boosted_creature`/`boosted_boss` are both `PRIMARY KEY(date)`, no `channel_id` — genuinely one shared row each | ✅ `Game::loadBoostedCreature`/`IOBosstiary::loadBoostedBoss` check `ClusterJobLeadershipRegistry::isLeader("boosted.creature"/"boosted.boss")` |
| Global event scheduling | `cluster-singleton` unless the event is explicitly declared `per-channel` | | 📐 |
| Table cleanup jobs (e.g. expired bans, stale storages) | `cluster-singleton` | | 📐 |
| Highscores cache rebuild | `cluster-singleton` | | 📐 |
| Database optimization | `cluster-singleton` | | 📐 |
| Global server record | `cluster-singleton` | | 📐 |
| Local map/server save | `per-channel` | this is the one job type that *should* run once per process | n/a |
| Monster/NPC spawn cycles | `per-channel` | | n/a |
| Local instance/boss-room timers | `per-channel` unless the boss is declared `cluster-singleton` | | n/a |

**Correction (this phase):** house rent charging and house auction
settlement were previously misclassified as `cluster-singleton`. On closer
inspection: `Houses::payHouses` (`src/map/house/house.cpp`) iterates the
in-memory `houseMap`, populated per-channel from each channel's own OTBM map
file at startup (`src/canary_server.cpp`'s `setupHousesRent()`, a one-shot
call, not a recurring job) — since houses already have composite
`(channel_id, house_id)` identity (§2.5), each channel's `houseMap` only
ever contains *its own* disjoint set of houses. Gating this behind
cluster-wide leader election would have been an actual **regression**: every
non-leader channel would simply never charge rent for (or settle auctions
on) its own houses, since the call would be skipped entirely rather than
raced. This is a genuine `per-channel` job, correctly requiring no
coordination — the original classification was written before house
partitioning's implications were fully traced through.

The leader election mechanism itself is implemented: `ClusterLeaderElection`
(lock key `cluster:leader:<job-name>`, same fencing-token pattern as session
leases, docs/multichannel/ARCHITECTURE.md §10a) plus
`ClusterJobLeadershipRegistry`, the Redis-backed cache that renews/acquires
on the existing session heartbeat cycle (for recurring jobs) or via a direct
one-shot acquire call (for startup-only jobs like the boosted
creature/boss selections) and exposes a cheap `isLeader(name)` check to job
call sites. Market offer expiration, the two boosted-X selections, and now
daily reward reset are wired; the last of these is scheduled from Lua
(`global_server_save.lua`'s `GlobalEvent`, not C++), so a new Lua-exposed
wrapper, `Game.tryClaimClusterJobLeadership(jobName)`, was added for it —
same one-shot-race gating shape as the boosted-X jobs, callable from any
future Lua-scheduled cluster-singleton job without needing its own bespoke
binding. Every other genuinely `cluster-singleton` job above still runs
unconditionally on every channel process and needs its own follow-up wiring
(deciding what "lost leadership mid-run" means for that specific job before
gating it) — and, per the correction above, every future candidate must
first be checked for hidden per-channel partitioning before assuming it
needs gating at all.

## GM / admin commands (✅ four implemented, 📐 the rest still contract-only)

- ✅ **Cluster-wide online list** — `Game.getClusterOnlinePlayers()`
  (`src/lua/functions/core/game/game_functions.cpp`), a read-only Lua global
  returning an array of `{accountId, playerId, name, channelId}` for every
  `cluster_sessions` row currently `ONLINE`, via a new
  `multichannel::listOnlinePlayers()` (`src/game/multichannel/
  cluster_session_lookup.hpp`/`.cpp`).
- Kick a player who is on a different channel.
- ✅ **Locate a player's current channel** — `Game.getPlayerClusterChannel(name)`
  (`src/lua/functions/core/game/game_functions.cpp`), a read-only Lua global
  reading the `cluster_sessions` DB defense-in-depth layer (not Redis, since
  a GM issuing this from one channel process needs to find a player who may
  be logged into a *different* one) via
  `multichannel::findOnlineChannelForPlayer` (`src/game/multichannel/
  cluster_session_lookup.hpp`/`.cpp`). Returns the channel id, or `nil` if
  the player is unknown or not currently tracked online anywhere in the
  cluster. No access check inside the binding - permission gating is left to
  the calling script/talkaction, matching this codebase's existing
  convention (verified: no other `Game.*`/`Player:*` binding checks GM group
  access internally either).
- Broadcast: cluster-wide vs. this-channel-only variants.
- Force-save a specific channel.
- Drain a channel (stop accepting new logins/switches, let existing
  players finish naturally).
- Set a channel to maintenance with a message.
- Inspect and, with explicit confirmation + audit log entry, clear an
  orphaned `DIRTY` session.
- ✅ **Inspect a session's current lock owner and fencing token** —
  `Game.getPlayerSessionLockInfo(name)` (`src/lua/functions/core/game/
  game_functions.cpp`), a read-only Lua global returning the raw
  `cluster_sessions` row - `{accountId, playerId, channelId, instanceId,
  sessionId, fencingToken, status, acquiredAt, lastHeartbeat, expiresAt}` -
  or `nil` if no lease has ever been acquired for that player, via a new
  `multichannel::findSessionLockInfo` (`src/game/multichannel/
  cluster_session_lookup.hpp`/`.cpp`). Deliberately **not** filtered to
  `status = 'ONLINE'` (unlike `getPlayerClusterChannel`) - inspecting a
  stale/`DIRTY` session is the primary reason a GM would call this, so an
  `ONLINE`-only filter would hide exactly the sessions this command exists
  to surface. Reads the DB defense-in-depth row, not Redis, for the same
  reason as the other lookups: the GM issuing the command and the session
  being inspected may be on different channel processes, and the DB table
  is the one source both can always read.
- ✅ **Inspect the last N channel-switch audit rows for a player** —
  `Game.getPlayerChannelSwitchHistory(name[, limit = 10])`, a read-only Lua
  global returning an array of `{sourceChannelId (nil on first-ever login),
  targetChannelId, result, denyReason, createdAt}`, newest first, via a new
  `ChannelSwitchAuditStore::getRecentHistory(playerId, limit)`
  (`src/game/multichannel/channel_switch_audit_store.hpp`/`.cpp`).

All four implemented commands are **read-only**; every remaining
command either mutates cluster state or needs cross-process signaling to a
*different* channel process, neither of which this codebase currently has a
mechanism for - the live channel switch (§6 of ARCHITECTURE.md) is the one
existing precedent for "coordinate an effect on a different channel," and it
was deliberately built as a DB-row handoff rather than any direct
process-to-process call specifically to avoid needing cross-process
signaling at all; the same reasoning applies here rather than building
ad hoc signaling for one admin command.

All cross-node commands must be authorized (existing GM permission checks)
and written to an audit trail — no new unauthenticated control surface.

## Metrics (📐 contract, not implemented)

Tag every metric with `channel_id`, `instance_id`, `node_id`. Minimum set:
active sessions, login lock failures, lease renewal failures, dirty
sessions, channel switch success/failure/latency, version conflicts,
idempotency duplicates (economic_ledger replay hits), DB transaction
failures, Redis disconnects, chat publish failures, channel heartbeat age,
economic operation latency. The existing `metrics/` (OpenTelemetry/
Prometheus) integration is the intended sink — no new metrics backend.

## Logs

Every cluster-related log line should carry `channel_id` and `instance_id`
(via the existing `spdlog` structured logging conventions) so operators can
`grep` a single channel's activity out of aggregated log storage.

## Running three channels locally

See `docker/multichannel/` for a Compose example: MariaDB, Redis, and
three Canary processes (`CANARY_CHANNEL_ID=1/2/3`) sharing the DB/Redis
and a common map volume, with Channel 1 acting as the login gateway
(`login_gateway = true` in its seeded `channels` row).
