# Multi-Channel Cluster Architecture

## Status legend

Every component below is tagged so reviewers and operators know exactly what
they are getting in this PR:

- ✅ **Shipped** — implemented, compiled/tested in this PR, safe behind
  `multiChannelEnabled = false` (default off).
- 📐 **Designed, schema-ready** — the data model, contracts and interfaces
  exist and are documented, but the gameplay engine call sites are not yet
  wired. Turning `multiChannelEnabled` on does **not** activate these; they
  require a follow-up PR ("Phase 2").
- 🔭 **Roadmap** — described for completeness, no code in this PR.

This PR is **Phase 1** of the multi-channel cluster effort described in the
originating spec. It intentionally does not claim to be the entire spec —
see [DECISION_MATRIX.md](DECISION_MATRIX.md) for the section-by-section
mapping and honest status of each binding decision, and the "Why Phase 1"
note at the bottom of this document for the reasoning.

## 1. Goal

One game, one economy, N parallel realtime channels (worlds) sharing the
same character roster, the same account, and the same persistent economy.
Channels differ in population, PvP ruleset and map instance state, not in
"who the player is". A player picks a channel by picking the same character
under a different world entry on the classic character list — no client
patch required (§3.2).

Seed configuration (configurable, not hardcoded):

| Channel | Name      | PvP type | 
|---------|-----------|----------|
| 1       | Channel 1 | no-pvp   |
| 2       | Channel 2 | no-pvp   |
| 3       | Channel 3 | pvp      |

## 2. Data ownership matrix

This is the authoritative table. Any code review question of "should this
have a `channel_id`" is answered by finding the row here first.

### 2.1 Global (identical across every channel, single row per entity)

| Domain | Tables (existing unless noted) | Notes |
|---|---|---|
| Account / character identity | `accounts`, `players` | unchanged, no duplication |
| Level/XP/skills/vocation | `players` | unchanged |
| Inventory / equipped items | `player_items` | unchanged, stays keyed by `player_id` |
| Depot | `player_depotitems` | unchanged |
| Inbox / store inbox | `player_inboxitems` | unchanged |
| Stash | `player_stash` | unchanged |
| Storage / quest state | `player_storage`, `global_storage` | unchanged |
| Charms, prey, task hunt, bosstiary, wheel data | `player_charms`, `player_prey`, `player_taskhunt`, `player_bosstiary`, `player_wheeldata` | unchanged |
| Boss cooldowns | `player_bosstiary` / boss cooldown storages | unchanged — see §2.6 |
| Bank balance | `players.balance` (existing column) | unchanged |
| Market | `market_offers`, `market_history` | unchanged identity; `source_channel_id` added as **audit only**, see §2.3 |
| Mail / parcels / rewards | `player_inboxitems`, `player_rewards`, `daily_reward_history` | unchanged; new `mail_delivery_audit` table added for exactly-once tracing (📐 not yet wired into the send call site) |
| Guilds | `guilds`, `guild_ranks`, `guild_membership`, `guild_invites`, `guild_wars` | unchanged, no `channel_id` added to any of these |
| VIP | `account_viplist`, `account_vipgroups`, `account_vipgrouplist` | unchanged, no `channel_id` |
| Bans | `account_bans`, `account_ban_history`, `ip_bans` | unchanged |
| Highscores | derived from `players` | unchanged, cluster-wide by construction since players are global |
| PvP skull / frags / PZ lock | `players` columns (`skull`, `lastAttack`, etc.) | unchanged, global |
| New: channel registry | `channels` ✅ | see §3.3 |
| New: cluster session lock | `cluster_sessions` ✅ | see §5 |
| New: channel switch audit | `channel_switch_audit` ✅ | see §6 |
| New: economic ledger | `economic_ledger` ✅ (schema only, 📐 write call sites) | see §8 |
| New: one-house-per-account authority | `account_house_ownership` ✅ | see §2.5 |

### 2.2 Per-channel (physically separate per channel)

| Domain | Tables | Notes |
|---|---|---|
| Houses | `houses` | `channel_id` added ✅, composite identity `(channel_id, id)` |
| House lists (access) | `house_lists` | `channel_id` added ✅, FK now composite |
| Physical map item state | `tile_store` | `channel_id` added ✅, FK now composite |
| Beds, doors, house access | in-map house state driven by the above | per-channel by construction once houses are |
| Runtime online players, monsters, NPCs, spawns, corpses | in-memory game state, not persisted globally | per-process by construction |
| Local party / shared XP | in-memory | per-channel by construction (§2.7) |
| Direct trade | in-memory | per-channel by construction (§2.15) |
| say/whisper/yell/NPC channel | in-memory speech | per-channel by construction |
| Instances, boss rooms, local events | in-memory / per-process | per-channel unless declared `cluster-singleton` (§2.6, §11) |
| Channel runtime presence | `channel_runtime_status` ✅ (persisted diagnostics) + Redis (fast path, 📐) | see §3.4 |

### 2.3 Audited, globally-identified (has `channel_id`/`source_channel_id` for traceability, identity stays global)

| Table | Column added | Purpose |
|---|---|---|
| `market_offers`, `market_history` | `source_channel_id` (nullable) ✅ | which channel an offer/trade originated from; never part of the offer's identity |
| `guildwar_kills` | `channel_id` ✅ | war kills only ever occur on PvP channels (§2.9); enforced at the call site in Phase 2 |
| `channel_switch_audit` | full audit row ✅ | see §6 |
| `economic_ledger` | `source_channel_id`, `target_channel_id` ✅ | see §8 |
| `mail_delivery_audit` | `source_channel_id` ✅ (📐) | see §2.12 |

No table in 2.1 gets a `channel_id` added to its primary/business key. This
is the single hard rule this PR enforces at the schema level.

## 3. Process model

### 3.1 One process per channel

Each channel is an independent OS process running the existing Canary
binary, pointed at the same MariaDB/MySQL database and the same Redis
instance, loading the same map/datapack. Channel identity is resolved with
this priority (✅ implemented in `ChannelContext`, see
`src/game/multichannel/channel_context.hpp`):

1. `--channel-id=<N>` CLI argument
2. `CANARY_CHANNEL_ID` environment variable
3. fallback `1` (single-channel / legacy behavior — this is what makes
   existing single-process deployments keep working untouched)

This is intentionally **not** read from `config.lua` alone, because
`config.lua` is shared by every process in the cluster (§3.1 of the spec) —
baking a process-specific id into a shared file would make every process
believe it is the same channel.

### 3.2 Login gateway

Canary's login protocol already supports a "world list" concept (see
`ProtocolLogin::getCharacterList`, modern layout): it sends a count of
worlds, then `(worldId, name, ip, port)` per world, then a character list
where every character row also carries a `worldId` byte. That is exactly
the "same character name under a different world" mechanism the product
spec calls for in §3.2 — no client protocol change is required.

✅ Shipped in this PR, gated by `multiChannelEnabled`:
- `ChannelRegistry` loads enabled+online, non-maintenance channels from the
  `channels` table.
- `ProtocolLogin::getCharacterList` (modern layout) emits one world entry
  per channel instead of the single hardcoded world, and repeats each
  character's row once per channel with that channel's `worldId`, without
  creating a second `players` row.
- The legacy 8.60 layout (which encodes `serverName/worldIp/worldPort`
  directly per character row, with no separate world table) is extended
  the same way: one row per `(character, channel)` pair, each pointing at
  that channel's own IP/port.

Exactly one process should have `loginProtocolEnabled = true` in the
`channels` table (see `login_gateway` column) — the startup validator
(§4.4, ✅) refuses to boot a second gateway. This mirrors the "dedicated
login-gateway role" option from the spec rather than inventing a new
service, since Canary's login protocol is already handled by a distinct
`ProtocolLogin` class separate from the game protocol.

### 3.3 Channel registry (`channels` table)

Authoritative source for every channel's configuration. Columns exactly
match the spec: `id`, `name`, `pvp_type`, `external_host`, `game_port`,
`status_port`, `max_players`, `enabled`, `sort_order`, `temple_town_id`,
`maintenance`, `maintenance_message`, `created_at`, `updated_at`, plus two
implementation columns: `login_gateway` (bool) and `map_hash` (populated at
boot, §3.5). See `data-otservbr-global/migrations/59.lua`.

Changing `pvp_type`, map, port or `login_gateway` requires a process
restart — nothing in this PR hot-swaps a running channel's ruleset.

### 3.4 Runtime registry / heartbeat

📐 Schema-ready (`channel_runtime_status`), not yet wired to a live
heartbeat loop. The design: each process upserts its row every
`sessionHeartbeatInterval` (also mirrored into Redis as the fast path for
the login gateway and session manager to consult without hitting MySQL on
every login). A channel whose `last_heartbeat` is older than
`sessionLeaseTtl` is treated as offline and dropped from the login list.
Wiring this into the game's existing scheduler loop is Phase 2 work — the
table, the `IRuntimeHeartbeat` interface, and the failure semantics are
specified in [OPERATIONS.md](OPERATIONS.md).

### 3.5 Map/datapack compatibility

✅ Wired: at startup, when `multiChannelEnabled = true`,
`CanaryServer::initializeMultichannelCluster()` computes a hash of the raw
OTBM file at `<dataDirectory>/world/<mapName>.otbm`
(`ChannelRegistry::computeFileHash`, an FNV-1a hash over the file bytes, ✅
implemented and unit-tested since Phase 1 - the doc previously referred to
this as `computeMapHash`, a name that was never actually used in code) and
compares it against every other row's `channels.map_hash` in the cluster
(`SELECT map_hash FROM channels WHERE map_hash != '' LIMIT 1`), not just
its own row - correct because house/tile identity (`(channel_id, house_id)`
/`(channel_id, position)`, §2.2/§2.5) is positionally derived from the map
file, so every channel must run byte-identical map data for that identity
scheme to mean the same thing across channels; the multichannel Docker
Compose example (`docker/multichannel/`) confirms this design intent -
all three channels share the same `mapName`/`dataDirectory` config, only
`CANARY_CHANNEL_ID` differs. The first channel to ever record a non-empty
hash seeds it for the whole cluster (no existing row has one yet); every
later boot of any channel, including a restart of the seeding channel
itself, must match that hash exactly or the process refuses to start
(`FailedToInitializeCanary`, fail-closed). Runs *before* `loadMaps()`, so a
mismatch is caught before any game state loads - it only needs the raw
file bytes, not a parsed `Map`. `pvp_type` is explicitly exempt from this
check (channels are allowed to diverge there) - not touched by this code
at all. Full datapack-file hashing beyond the map is listed as 🔭
roadmap - the OTBM hash is the integrity-critical piece since it is what
determines house/tile geometry compatibility across channels.

**📐 Known, narrow gap, stated honestly:** this check is a plain
`SELECT`/`UPDATE` pair, not an atomic Redis CAS like the session/leader
election primitives - if two channels boot for the very first time
*simultaneously* (an empty `channels` table, genuinely concurrent cluster
bootstrap) with *different* map files, both could see an empty result set
and both seed their own row without ever comparing against each other,
since neither observes the other's write in time. This is strictly better
than the status quo (no check ever existed before this phase) and is a
narrow, one-time bootstrap-only race rather than a routine-operation risk -
every subsequent boot of either channel, including their very next
restart, would then correctly detect and refuse the mismatch. Closing it
fully would mean routing this specific check through the same Redis
lease/fencing mechanism as leader election, which is more machinery than
this narrow bootstrap-only race justifies for now.

## 4. Configuration

### 4.1 `config.lua.dist` additions (✅ shipped)

See the actual file for the authoritative list; summarized:

```lua
multiChannelEnabled = false

channelSwitchCooldown = 60 * 1000
channelSwitchPositionPolicy = "same-nearest-public-last-safe-temple"
channelSwitchSearchRadius = 10
channelSwitchPartyPolicy = "deny"        -- "deny" | "leave"
pvpChannelExitPolicy = "combat-or-skull" -- "combat-only" | "combat-or-skull"

clusterChatEnabled = true
showChannelTagInClusterChat = true

redisHost = "127.0.0.1"
redisPort = 6379
redisDatabase = 0
redisUsername = ""
redisPassword = ""
redisUseTls = false

sessionLeaseTtl = 30 * 1000
sessionHeartbeatInterval = 5 * 1000
redisFailureGracePeriod = 10 * 1000
databaseFailureGracePeriod = 5 * 1000

loginProtocolEnabled = true
statusProtocolAggregateChannels = true
```

All keys are booleans/ints/strings — no ad-hoc list parsing was
introduced; `ConfigManager` does not currently support Lua-table config
values, so nothing in this PR requires adding that capability.

### 4.2 Database as source of truth

`channels` is the only place per-channel operational config lives. The
Lua config file is deliberately *not* used to declare the channel list,
since (§3.1 of the spec) multiple processes share one `config.lua`.

### 4.3 No unsafe toggles

Per the spec's hard-invariant list, this PR does not introduce any of:
`enableSessionLocks=false`, `disableTransactionSafety=true`,
`allowLoginWithoutRedis=true`, or equivalents. When `multiChannelEnabled`
is `true`, the session manager, fencing tokens and fail-closed Redis/DB
policies (§10) are not optional.

### 4.4 Startup validator (✅ shipped, `ClusterConfigValidator`)

Runs only when `multiChannelEnabled = true`. Checks, in order, and aborts
startup (fail-closed) on the first failure:

1. `sessionLeaseTtl` is strictly greater than `sessionHeartbeatInterval`
   (at least 2x, logged as a warning below that but not a hard failure
   above 1x — hard failure only if `leaseTtl <= heartbeatInterval`, which
   would guarantee spurious lease expiry).
2. The resolved `channelId` (§3.1) exists in the `channels` table and is
   `enabled`.
3. `pvp_type` for this channel is one of `no-pvp`, `pvp`, `pvp-enforced`.
4. `channelSwitchPartyPolicy` ∈ `{deny, leave}`.
5. `pvpChannelExitPolicy` ∈ `{combat-only, combat-or-skull}`.
6. Redis connectivity (best-effort ping) — see §10.1 for what happens if
   this fails *after* startup instead.

Redis connectivity ping (#6) is 📐 (not implemented - see item 6 above,
which today only fails closed if the binary wasn't *compiled* with the
Redis client, not if Redis is unreachable at boot). The config-shape
validations (1–5), plus a 7th check added alongside them - at most one
*enabled* row in the whole `channels` table may have `login_gateway = true`
(`ClusterConfigValidationError::MultipleLoginGatewaysEnabled`) - are ✅ and
wired into real server startup (`CanaryServer::initializeMultichannelCluster`,
called from `initializeDatabase()`): it reloads the registry, runs every
check above, logs every warning/error, and throws `FailedToInitializeCanary`
to abort the process on any hard failure. This 7th check is a static,
single-snapshot check (every process reads the same table) - it is
**not** the live, cross-process "is that other login gateway actually
still alive" check, which still needs the runtime heartbeat table from
§3.4 and remains 📐.

## 5. Sessions, locks, anti-split-brain (✅ core algorithm and engine call sites)

`ClusterSessionManager` (`src/game/multichannel/cluster_session_manager.*`)
implements the lease/fencing state machine from spec §5.1:

- States: `ACQUIRING → ONLINE → SAVING → OFFLINE`, with `DIRTY` reachable
  from any state on a detected fencing conflict or lease loss.
- `session_id`: random 128-bit token, generated per acquire.
- `fencing_token`: monotonically increasing 64-bit integer, issued by
  Redis (`INCR` under the same key namespace as the lease) so it survives
  process restarts and can never go backwards for a given
  `(account_id, player_id)` pair.
- Acquire/renew/release are single atomic Redis Lua scripts (`EVAL`), not
  a read-then-write pair, so two processes racing to acquire the same
  account/player cannot both win. The scripts are in
  `src/game/multichannel/redis_scripts/`. See
  [THREAT_MODEL.md](THREAT_MODEL.md) for exactly why plain `SET NX` is not
  enough here (renewal-by-owner-only + fencing both require compare logic
  server-side, in Redis, not in the client).
- `cluster_sessions` (§2.1) is the DB-backed defense-in-depth layer: it has
  `PRIMARY KEY(account_id)` **and** `UNIQUE(player_id)`, so even a total
  Redis loss (§10.1) cannot let two DB rows exist for the same account or
  the same player — a second `INSERT` fails on the constraint, not on
  application logic. **Not yet dual-written by the engine call sites below**
  (📐 — see "Known gap" at the end of this section).
- The abstraction is `IRedisClient`; production uses `HiredisRedisClient`
  (✅ `src/game/multichannel/hiredis_redis_client.*`, built only when the
  optional vcpkg feature is enabled — see §9), compiled standalone against
  the real `hiredis` header/lib and run end-to-end against a real local
  `redis-server` (acquire/renew/release/expiry/conflict/unreachable-
  connection). Tests use `FakeRedisClient`, an in-memory model of the exact
  same CAS semantics, so the state machine is fully unit-tested without a
  live Redis dependency too.

**✅ Engine call sites (Phase 2):**

- `ClusterRuntime` (`src/game/multichannel/cluster_runtime.*`) orchestrates
  `ClusterSessionManager` against the accounts this process currently
  believes are online. It is the seam between the pure state machine above
  and the live engine, and implements the Redis-outage policy from §10/
  OPERATIONS.md itself (see there for the exact rules).
- `ProtocolGame::login` calls `ClusterRuntime::acquireForLogin` as the very
  last gate before `placeCreature`, so every earlier rejection (ban,
  waiting list, per-account PZ limit) still returns before a lease is ever
  acquired that the function would then have to remember to release; a
  `placeCreature` failure after a successful acquire releases it again
  immediately rather than leaving it to expire on its own TTL.
- `Player::onRemoveCreature` calls `ClusterRuntime::releaseForLogout` right
  after the existing save-on-logout call — the one place a player's own
  creature is actually removed from the world, regardless of why.
- `Game::renewClusterSessions()`, cycled at `sessionHeartbeatInterval`,
  renews every tracked account and force-disconnects (best-effort save,
  then kick, via the existing `Game::kickPlayer`) whichever ones
  `ClusterRuntime` reports expired — either a legitimate supersession
  (no grace period) or a Redis outage whose grace period or lease margin
  has run out (see §10).

**✅ `cluster_sessions` DB dual-write (Phase 4):** `IClusterSessionRepository`
(`src/game/multichannel/cluster_session_repository.hpp`) is the abstraction,
`DbClusterSessionRepository` the real implementation, wired into
`ClusterRuntime` at the exact same three events as the Redis side:

- **Acquire**: `INSERT ... ON DUPLICATE KEY UPDATE`, matching the "latest
  acquire wins" semantics `account_house_ownership` already uses (§7) - a
  relogin or channel switch moves the account's one row rather than
  leaving two. If the DB write fails, the just-acquired Redis lease is
  released and the login is rejected — the defense-in-depth layer failing
  to persist is treated the same as Redis refusing the lease outright.
  Verified against a real MariaDB: a naive single-statement upsert
  silently corrupted a row when a (realistically unreachable, since
  player_id→account_id never changes in this engine) `player_id` collision
  hit a *different* account's row than the one colliding on the
  `account_id` primary key — `ON DUPLICATE KEY UPDATE` updated that other
  row's columns without updating its `account_id`, producing an internally
  inconsistent record instead of an error. Fixed with an explicit
  `DELETE ... WHERE player_id = ? AND account_id != ?` before the upsert,
  re-verified clean afterward.
- **Heartbeat**: a plain `UPDATE` alongside every successful Redis renew -
  best-effort (a transient DB hiccup during a routine heartbeat must not
  force-disconnect a player whose Redis lease, the fast path, is fine).
- **Release**: a plain `DELETE`, both on a clean logout and when
  `ClusterRuntime` force-expires an account after a Redis outage (the
  legitimate-supersession case needs no separate delete here - the new
  holder's own acquire already overwrote the row).

Not yet wired: the admin tool to inspect/clear orphaned `DIRTY` sessions
(§5.3, §12.2) - this dual-write only ever deletes or upserts a row as
`ONLINE`, it never writes `DIRTY` itself.

## 6. Channel switch (✅ policy engine and position resolver, 📐 switch command)

`ChannelSwitchService` orchestrates, in order:

1. Reject if `target_channel_id == player.last_channel_id` (plain relog,
   not a switch — no cooldown, no audit row beyond the normal login).
2. Reject if `now - last_channel_switch_at < channelSwitchCooldown`.
3. Reject if the account/player has any cluster session in a state other
   than `OFFLINE` (no login while online elsewhere, no parallel switch
   races — this is the same lock as §5, not a second one).
4. Reject if PZ-locked/in combat (always, unconditionally).
5. Apply `pvpChannelExitPolicy` when the target is `no-pvp`: block if
   skulled (`combat-or-skull`, default) or allow if unskulled and not in
   combat (`combat-only`).
6. Apply `channelSwitchPartyPolicy`: `deny` blocks the switch outright
   while in an active party; `leave` removes the player from the party
   first, then proceeds.
7. Resolve target position via `PositionResolver` (§ below).
8. Reject if the target channel is disabled, in maintenance, offline
   (stale heartbeat) or at `max_players`.
9. Write one row to `channel_switch_audit` regardless of outcome.

`PositionResolver` implements the exact fallback chain from spec §2.4:

1. Same `(x, y, z)` if the tile exists, is not blocked, not inside a house
   the account/player cannot access on the target channel, not inside an
   instance/boss-room/quest-room flagged no-switch, and not inside a
   `NO_CHANNEL_SWITCH` zone.
2. Bounded breadth-first search outward from that tile, capped by
   `channelSwitchSearchRadius` (Chebyshev radius) and a hard node-visit
   budget, for the nearest tile passing the same legality checks — **never**
   an unbounded map scan.
3. The player's last persisted "safe public position"
   (`player.lastSafePosition`, 📐 new column, updated whenever the player
   is on a legal public tile and periodically like the existing position
   save, not on every step).
4. The target channel's configured temple (`channels.temple_town_id`).

Both classes are pure logic over an injected map/legality interface, so
they are fully unit-tested (radius bound, house-access denial, instance
denial, tie-breaking) without needing a live game world.

**✅ `EnginePositionLegality`** (`src/game/multichannel/
engine_position_legality.*`) is the real, engine-backed `IPositionLegality`
`PositionResolver` needs to actually run against a live map instead of a
test fake:

- `tileExists`: `Tile::queryAdd(0, arrivingPlayer, 1, 0) ==
  RETURNVALUE_NOERROR` — the exact same legality check the normal
  movement/teleport path already uses, reused rather than reimplemented so
  it can never silently disagree with the engine's own definition of
  "walkable".
- `isInaccessibleHouse`: `Tile::getHouse()` + `House::isInvited(player)` —
  the existing house-access model, unchanged.
- `isRestrictedInstance` / `isNoChannelSwitchZone` /
  `requiresSpecialEntryCondition`: there is no dedicated schema or
  authoring convention anywhere in this project for these three concepts,
  so they are answered via an explicit, **opt-in naming convention**: a
  `Zone` (existing `game/zones/zone.hpp` mechanism) covering the position
  whose name starts with `restrictedinstance` / `nochannelswitch` /
  `specialentry` respectively (case-insensitive). An operator who wants a
  boss room or quest instance excluded from channel-switch arrivals names
  (or renames) its zone accordingly — no code change needed, but nothing
  is excluded by default. This is honestly a convention bolted onto the
  existing generic zone system, not a first-class feature; a real
  dedicated flag is tracked as Phase 3 work in DECISION_MATRIX.md.

`EnginePositionLegality` is only correct for a target channel that shares
this channel's `mapHash` (`ChannelRegistry`/`channels.map_hash`, §3.5) —
it answers every check against *this* process's own already-loaded map,
which is only meaningful if the target channel loaded the same one. A
caller resolving a switch to a channel with a **different** `mapHash` must
not use it and should fall back to the temple-only step of the chain
instead — `Game::playerRequestChannelSwitch` (below) checks this itself.

**✅ The switch command is wired**, using exactly the DB-row handoff
design above, chosen specifically so a switch never requires cross-process
signaling (which this sandbox has no way to integration-test):

- `Game::playerRequestChannelSwitch(playerId, targetChannelId)` runs on the
  **origin** channel. It gathers the player's live state (position, combat/
  PZ-lock via the same tile-flag check `ProtocolGame::logout` already uses,
  skull, party, and `ChannelSwitchAuditStore::getLastSwitchAtMs` for the
  cooldown clock), calls `ChannelSwitchService::evaluate()`, and on success
  resolves the arrival position (`PositionResolver`/`EnginePositionLegality`
  if `mapHash` matches, otherwise straight to the target's temple), writes
  one `channel_switch_audit` row either way, then calls
  `player->removePlayer(true)` — a perfectly normal, already-safe clean
  disconnect (§5's real `ClusterRuntime::releaseForLogout` path fires from
  the same `Player::onRemoveCreature` hook a plain logout uses; no new
  release mechanism was needed). `decision.mustLeavePartyFirst` needs no
  separate action, since that same disconnect path already unconditionally
  leaves any active party.
- The only new trigger surface is `player:requestChannelSwitch(channelId)`,
  a Lua method (`src/lua/functions/creatures/player/player_functions.cpp`)
  an operator wires into a talkaction/command of their choosing — there is
  still no new client protocol packet.
- `ProtocolGame::login`'s existing acquire gate (§5) now also calls
  `ChannelSwitchAuditStore::findPending` for this account/channel; a match
  overrides the stale `loginPosition` for that one login and is marked
  consumed only after `placeCreature` actually succeeds (a failed
  placement leaves it pending, so the *next* attempt gets the same
  resolved position instead of silently falling back).

**📐 Known gaps, stated honestly:** `targetChannelOnline`/`targetChannelFull`
are optimistic placeholders (`true`/`false`) since no heartbeat loop exists
yet to check them for real (§3.4). `players.last_safe_position` still
doesn't exist, so step 3 of the resolver chain is never reached in
practice. The `cluster_sessions` DB table is still not dual-written by any
of this (§5's gap). And the admin-facing side of this — an operator
inspecting `channel_switch_audit` for a stuck/failed switch — has no
tooling beyond direct SQL.

## 7. Houses (✅ schema and purchase/transfer call site)

Composite identity `(channel_id, id)` on `houses`, propagated to
`house_lists` and `tile_store` (§2.2). `account_house_ownership` is the
single authoritative table for "one house per account, cluster-wide"
(§2.5) — `PRIMARY KEY(account_id)` makes a second house for the same
account a constraint violation, not an application-level check that can
race. This directly extends `houseOwnedByAccount` /
`House::getOwnerAccountId()` rather than inventing a second ownership
model: `ownerAccountId` continues to be resolved from `players.account_id`
for the owning `player_id` at load time; `account_house_ownership` is the
new piece that makes the *cross-channel* constraint real instead of an
in-memory check.

**✅ `House::setOwner`** (`src/map/house/house.cpp`) is the one real
chokepoint every ownership change in this codebase funnels through —
auction settlement, trade-based sale, rent/inactivity repossession, and
the deferred "transfer on next restart" path (`IOMapSerialize::
loadHouseInfo`, `Houses::payHouses`) all call it, directly or via
`setNewOwnerGuid`. It now also mirrors every change into
`account_house_ownership`:

- Whenever the existing `UPDATE houses SET owner = ...` write actually
  runs (i.e. `updateDatabase && owner != guid`), a
  `DELETE FROM account_house_ownership WHERE channel_id = ? AND house_id = ?`
  clears whatever row was there — keyed by
  `account_house_ownership_house_unique(channel_id, house_id)`, not by the
  previous owner's account, so it works even when that account can no
  longer be resolved. For a revoke (`guid == 0`) this is the whole job.
- For a grant (`guid != 0`), once the new owner's `account_id` is resolved
  (the same `SELECT ... FROM players` the function already ran), a
  `DELETE FROM account_house_ownership WHERE account_id = ?` clears
  whatever house that account held anywhere else in the cluster (the
  `PRIMARY KEY(account_id)` only allows one row), then a plain `INSERT`
  adds the new one.
- Neither write is wrapped in a new explicit transaction — matching every
  other write already in this function (the `UPDATE houses` and the
  `SELECT ... FROM players` are two independent statements today too);
  see TEST_PLAN.md for what was verified against a real MariaDB instead
  (grant, re-grant to a different house for the same account, revoke).

**📐 Known gap, stated honestly:** this makes the *mirror* accurate, it
does not add a new *gate*. Nothing yet stops an account from bidding on
or trading for a second house before an already-in-flight purchase for a
different house settles — that would mean touching the auction/bid/trade
acceptance code (`Game::playerCyclopediaHouseBid`/...`Transfer`/
...`MoveOut` and the trade-accept path), which only stage pending state
today and don't call `setOwner` until the next `IOMapSerialize::
loadHouseInfo()` pass (i.e. next restart/map reload) - a materially larger
and riskier change than mirroring an already-decided outcome, left for a
follow-up. Also unresolved from Phase 1: house ids still aren't
independently reusable per channel (`houses_id_unique`, see
MIGRATION.md's "Known limitation").

**🐛 A deeper mechanism behind this gap was traced while scoping a possible
fix, not fixed:** even when `House::setOwner` *does* eventually run for a
grant, it only clears and reinserts the `account_house_ownership` **mirror**
row for the account - it does not revoke the *actual* `houses.owner` column
of whatever *other* house that account previously owned. If that other
house physically lives on a different channel (a different `houses` table
partition, per §2.2's composite `(channel_id, id)` identity), the owning
channel's own in-memory `House` object and DB row are simply never touched
by this grant at all. The account ends up genuinely, concretely owning two
houses at once (full in-game access, rent billed on both) even though the
cluster-wide mirror - by construction of its own `PRIMARY KEY(account_id)`
- can only ever show one. A correct fix would need to find and revoke the
account's previous house *before or during* the grant, which for a
different-channel house means either a blind cross-channel DB `UPDATE`
(desyncs that channel's in-memory `House` object from its own DB row until
its next reload - arguably worse than today's gap) or the same DB-row-handoff
signaling pattern already needed for §6 (channel switch) and the mail-loss
bug (§8) - i.e. a pending-revocation row the *owning* channel's own process
picks up and applies to its own live `House` object. This is genuinely more
design work than a bounded gate-the-bid-call-site change, and a partial fix
(e.g. blocking *new* bids when `account_house_ownership` already has a row)
would not close the underlying gap and could give a false sense of safety -
so, per this project's established "don't fix blind" discipline (see the
house-rent misclassification correction above, and MIGRATION.md's mail-loss
finding), nothing was changed here this phase; this refines the gap
description for whoever picks it up next.

## 8. Economy (✅ market-offer-expiry job + cancel-offer wired, 📐 create/accept not wired)

`economic_ledger.transaction_uuid` is a `CHAR(36)` primary key: a retried
operation `INSERT`s the same UUID and gets a duplicate-key error instead of
a second effect, which the caller treats as "already applied, look up the
existing row's `status`". This is the idempotency mechanism the spec
requires for market/mail/bank/house operations (§8.2).

**✅ `IOMarket::processExpiredOffers`** (`src/io/iomarket.cpp`), the
background job `IOMarket::checkExpiredOffers` schedules periodically, is
the first (and so far only) engine call site wired to this table. The
pre-existing bug this closes: `moveOfferToHistory` does a synchronous
`DELETE FROM market_offers` for the expiring offer *before*
`processExpiredOffers` credits the refund (gold to bank balance) or
delivers the item to the player's inbox; a crash between that `DELETE` and
the credit/delivery silently and permanently drops the refund or item —
there is no second attempt (the row that would have driven a retry is
already gone) and, before this change, no durable trace that it ever
happened.

`EconomicLedgerStore` (`src/game/multichannel/economic_ledger_store.hpp`/
`.cpp`) now brackets each expiring offer:

- `beginPending` inserts a `PENDING` row keyed by a **deterministic** UUID
  derived from the offer's own `id` (`EconomicLedgerStore::deterministicUuid
  ("market.expire", offerId)`, via the pure, dependency-free
  `multichannel::computeDeterministicLedgerUuid` in
  `economic_ledger_id.hpp`/`.cpp`) — deterministic rather than random
  because this is a scheduled job with no per-attempt nonce to rely on; the
  same offer id must always retry into the same row rather than creating a
  fresh one. If this `INSERT` fails (duplicate key = this exact offer was
  already attempted; any other DB error = fail closed), the offer is
  skipped for this run rather than risking a second effect.
- `moveOfferToHistory` runs as before (deleting the offer, appending
  history); if it fails, the ledger row is marked `FAILED` and the offer is
  skipped.
- Once the refund/delivery branch actually completes (item(s) placed in
  the inbox, or the bank balance/`increaseBankBalance` credit applied), the
  row is marked `COMMITTED`. The two early-exit checks inside the
  item-delivery branch (`itemType.id == 0`, player not resolvable) mark the
  row `FAILED` instead, since no delivery occurred.

This makes a crash mid-expiry **detectable and auditable** (a `PENDING`
row with no matching `COMMITTED` is exactly the offer that needs manual
reconciliation) even though it does not yet make the DELETE-then-credit
sequence atomic — see TEST_PLAN.md for what was verified against a real
MariaDB instance (the core duplicate-`transaction_uuid` rejection, plus
both the item-delivery and currency-refund ledger record shapes).

**✅ `Game::playerCancelMarketOffer`** (`src/game/game.cpp`) is now the
second call site wired to `economic_ledger`, using the same deterministic-UUID
pattern as the expiry job, but keyed off namespace `"market.cancel"` and the
cancelled offer's own `id`
(`EconomicLedgerStore::deterministicUuid("market.cancel", offer.id)`). This
key is safe specifically *because* a given `market_offers` row can be
cancelled at most once — `IOMarket::moveOfferToHistory` deletes the row as
part of cancellation, so the same `(namespace, offer.id)` pair can never
legitimately recur; a retried/duplicated cancel request replays into the
same `PENDING`/`COMMITTED` row and is rejected by the `transaction_uuid`
primary key exactly like the expiry job's replay case. The ledger bracket
follows the same shape: `beginPending` before the refund/delivery attempt,
`markCommitted` right after `moveOfferToHistory` succeeds, `markFailed` on
every early-exit error path (unknown item type, inbox insertion failure).
Store-coin cancellations (`it.id == ITEM_STORE_COIN`) are deliberately
excluded from the ledger entirely, matching this function's pre-existing
"do not register a transaction for coins" comment — that path already goes
through the account's own coin-transaction system, which is a different
ledger than the gold/item economy `economic_ledger` tracks. Verified against
a real MariaDB instance: a buy-offer cancel's `PENDING → COMMITTED`
transition (currency `amount` populated, no item fields), a sell-offer
cancel's `PENDING → FAILED` transition (item fields populated, `amount`
unset), and a replay `INSERT` against an already-used offer-id key correctly
rejected with `ERROR 1062` on the `transaction_uuid` primary key — see
TEST_PLAN.md.

**📐 Known gap, stated honestly:** `Game::playerCreateMarketOffer` and
`Game::playerAcceptMarketOffer` remain unwired, for two different reasons
rather than one:

- **Create** has no natural, pre-existing single-use key to derive a
  deterministic UUID from — unlike expiry/cancel, there is no offer `id` yet
  at the point a new offer is created (the DB assigns it during the same
  `INSERT` this would need to guard). Reusing the deterministic pattern here
  would require inventing a client-supplied nonce, a materially different
  design than "key off an entity that can only be consumed once," and worth
  its own follow-up rather than forcing the existing pattern where it
  doesn't fit.
- **Accept** cannot safely use `offer.id` alone as a key: a single offer can
  legitimately be *partially* accepted multiple times by different
  counter-parties for different `amount`s until it is exhausted, so
  `(namespace, offer.id)` is not single-use the way it is for expiry/cancel —
  a second, legitimate partial accept would collide with the first and be
  wrongly rejected as a replay. This needs a compound key (offer id plus
  something that distinguishes each accept attempt, e.g. acceptor account id
  and amount) worked out deliberately rather than reusing cancel's key shape
  by analogy.

Mail delivery and house purchase/transfer are also still unwired — see
DECISION_MATRIX.md for the precise list of functions that still need it and
why wiring all of transactional economy code in one pass, in an environment
with no compiler to verify most of it, would be irresponsible.

**🐛 Real bug found while scoping GM commands, not fixed this phase:** mail
delivery has a correctness gap that goes beyond "no idempotency guard yet."
`Mailbox::sendItem` (`src/items/containers/mailbox/mailbox.cpp`) resolves
the recipient via `g_game().getPlayerByName(receiver, true)`, which only
checks this process's own in-memory online-player map; if the recipient
isn't found there — which is exactly what happens when they're online on a
*different* channel, not just when they're genuinely offline — it silently
falls back to loading a throwaway offline `Player` copy from the DB,
delivers the item into that copy's inbox, and saves it. The recipient's own
channel process, holding the real live `Player` object, has no idea this
happened; its own next periodic or logout save overwrites the DB row,
silently discarding the item. A correct fix needs the same DB-row-handoff
pattern §6 already uses for channel switching (a pending-delivery row the
owning channel's own process picks up and applies to its own live player
object), which is materially more design work than call-site wiring — see
MIGRATION.md "Phase 12" and DECISION_MATRIX.md row 2.12.

## 9. Redis client dependency

New optional vcpkg feature `multichannel` (mirrors the existing `metrics`
feature pattern) adds a Redis client. Default build (`CANARY_BUILD_TESTS`
off, no extra `VCPKG_MANIFEST_FEATURES`) is completely unaffected — Redis
is not linked, not required, and `multiChannelEnabled` cannot be turned on
in a binary built without the feature (checked at config-load time: if the
flag is on and the client type resolves to a stub, startup fails closed).

## 10. Failure policy

Implemented as documented state transitions in `ClusterSessionManager`
(Redis loss → grace period → freeze → drain) and specified in detail,
including exact operator actions, in [OPERATIONS.md](OPERATIONS.md) §Redis
outage / §DB outage. The state machine transitions themselves are unit
tested; the "freeze new logins" and "disconnect before another process can
steal the lease" actions require the Phase 2 game-loop wiring to execute
for real.

## 10a. Leader election primitive (✅ module, ✅ wired to 4 jobs, 📐 others unwired)

Several background jobs must run exactly once cluster-wide rather than once
per channel process (`OPERATIONS.md`'s "Leader election / cluster-singleton
jobs" table: house rent charging, house auction settlement, market offer
expiration, daily reward reset, global boosted creature/boss selection,
table cleanup jobs, highscores cache rebuild, ...). `ClusterLeaderElection`
(`src/game/multichannel/cluster_leader_election.hpp`/`.cpp`) is the
primitive that will let exactly one process win each of those jobs: it
reuses the *exact same* atomic Redis lease/fencing mechanism as
`ClusterSessionManager` (§5) - the same `IRedisClient` seam, the same
`redis_scripts/{acquire,renew,release}.lua` (already validated against a
real `redis-server`, see TEST_PLAN.md; these scripts only ever operate on
an opaque lock key/session id/TTL, so they needed no changes to serve
leader election too), just keyed by a job name string (`cluster:leader:
<jobName>`) instead of an account id. A job leader has no multi-state
lifecycle the way a player session does (no Acquiring/Saving/Dirty) -
either this process currently holds the lease for that job or it doesn't;
a job run is expected to call `isFencingTokenCurrent` immediately before
any effect that must not run twice, mirroring the anti-zombie check
THREAT_MODEL.md T2 already requires for session saves.

**✅ Verified**: 13 new gtest cases (`tests/unit/game/multichannel/
cluster_leader_election_test.cpp`), compiled standalone with real `g++
-std=c++20` + real `libgtest`/`libgtest_main` (this module has zero engine
dependency, same as `ClusterSessionManager`, so it needed no MariaDB
verification and no hand-review substitute) - acquire/reject-while-held,
independent job names don't contend, renew by owner/non-owner, renew past
expiry doesn't resurrect, release by owner/non-owner, fencing token
monotonicity across release/reacquire cycles, reacquire-after-expiry gets
a higher token, stale token correctly reads as not-current after a
takeover, and a 16-thread concurrent-acquire race with exactly one winner.
**13/13 passing.**

**✅ `ClusterJobLeadershipRegistry`** (`src/game/multichannel/
cluster_job_leadership_registry.hpp`, header-only like
`ChannelRuntimeRegistry`) is the Redis-backed cache that sits between the
primitive and a job call site: `renewOrAcquire(jobName, ttlMs, nowMs)` does
the actual Redis work once per heartbeat cycle (called from
`Game::renewClusterSessions`, right alongside the existing session-lease
renewal, reusing `SESSION_LEASE_TTL` rather than adding a dedicated job-lease
config key for this one wired example); `isLeader(jobName)` is a cheap,
I/O-free read any job call site can check. A failed renew keeps the
remembered lease id instead of discarding it, so a merely-transient Redis
outage recovers cleanly on the very next cycle once reachable again (the
lease was never actually touched on the Redis side while unreachable) - a
real takeover by another process is, correctly, not reversible this way. Set
up once in `CanaryServer::initializeMultichannelCluster()` alongside
`ClusterRuntime`, sharing the same Redis client and instance id.

**✅ `IOMarket::checkExpiredOffers`** (`src/io/iomarket.cpp`) is the first
(and so far only) job wired to it, matching OPERATIONS.md's own listing of
market offer expiration as `cluster-singleton`: before running its query, it
checks `isLeader("market.expire")` - if the registry is disabled (single-node,
or `multiChannelEnabled=false`), the check is skipped entirely and behavior
is unchanged; if enabled and this process is not the current leader, the
query is skipped for this cycle (the function still reschedules itself
normally, so it keeps checking every cycle). This is a **cheap in-memory
check gating a whole DB query**, not a change to the query or the
expiry/refund logic itself.

**✅ `Game::loadBoostedCreature`/`IOBosstiary::loadBoostedBoss`**
(`src/game/game.cpp`/`src/io/io_bosstiary.cpp`) are the second and third
jobs wired, and structurally different from market expiry: both are
**one-shot startup calls** (`CanaryServer::loadModules()`), not recurring
dispatcher events, so there is no periodic heartbeat cycle available yet at
the point they run to have kept leadership "warm." Each calls
`ClusterJobLeadershipRegistry::renewOrAcquire("boosted.creature"/
"boosted.boss", ...)` directly, once, as a one-shot leader-election *race*
rather than a sustained leadership check: whichever channel process reaches
this line first wins the lease and proceeds to reroll+persist a new
selection; every other process reads whatever is currently on record
(possibly stale-by-one-day) instead of independently rolling and persisting
a *different* value. `boosted_creature`/`boosted_boss` are both
`PRIMARY KEY(date)` with no `channel_id` - genuinely one shared row each,
unlike houses (see below) - and `loadBoostedBoss`'s reroll additionally
resets *global* `player_bosstiary` slot state tied to the old boss id,
making an uncoordinated race actively corrupting, not just cosmetically
inconsistent.

**✅ Daily reward reset** (`data/scripts/globalevents/global_server_save.lua`)
is the fourth job wired, and the first one whose scheduling lives in Lua
(a `GlobalEvent`) rather than the C++ engine - `DailyReward.storages.
lastServerSave` is a single shared `global_storage` row with no
`channel_id`, written on each channel's own `GlobalServerSave` schedule
(OPERATIONS.md), so an unguarded write from every channel would race the
same way market expiry did before Phase 7. Since there was no existing
Lua-side leadership check to call, a new one-shot wrapper was added:
`Game.tryClaimClusterJobLeadership(jobName)` (`src/lua/functions/core/game/
game_functions.cpp`) mirrors the exact gating shape already used by
`loadBoostedCreature`/`loadBoostedBoss` above - `true` unconditionally when
clustering is disabled (so single-node deployments are never gated), else a
one-shot `renewOrAcquire` + `isLeader` check. Only the `
UpdateDailyRewardGlobalStorage` line inside `ServerSave()` is gated - the
same function's `cleanMap()`, `Game.setGameState(...)`, and the per-raid
daily-counter reset are deliberately left unguarded, since those act on
this channel's own in-memory map/game-state/raid registry and must keep
running on every process (the same "don't over-gate a genuinely per-channel
effect" lesson as the house-rent correction below).

**📐 Known gap, stated honestly:** every *other* job in OPERATIONS.md's
table (table cleanup jobs, highscores cache rebuild, database optimization,
global server record, global event scheduling) still runs unconditionally
on every channel process. Wiring each remaining job individually (deciding
what "lost leadership mid-run" should mean for that specific job) is real
per-job design work left for a follow-up, not something safe to do blind in
one broad pass across the rest.

**Correction, found while scoping this phase:** house rent charging and
house auction settlement were previously listed here (and in OPERATIONS.md)
as `cluster-singleton` - this was wrong. `Houses::payHouses`
(`src/map/house/house.cpp`) iterates the in-memory `houseMap`, populated
per-channel from each channel's own OTBM map at startup; since houses
already have composite `(channel_id, house_id)` identity (§2.5), each
channel's `houseMap` only ever contains its own disjoint houses. Gating
this behind cluster-wide leader election would have been a **regression**
(every non-leader channel would simply stop charging rent for its own
houses), not a fix - it is a genuine `per-channel` job needing no
coordination. See OPERATIONS.md's job table for the corrected
classification and full reasoning.

## 10b. GM/admin commands (✅ four read-only lookups, 📐 the rest)

`OPERATIONS.md`'s "GM / admin commands" list was previously a contract only.
**"Locate a player's current channel"** is now implemented as
`Game.getPlayerClusterChannel(name)` (`src/lua/functions/core/game/
game_functions.cpp`): a read-only Lua global that resolves a player name to
a guid (`IOLoginData::getGuidByName`, existing), then queries
`multichannel::findOnlineChannelForPlayer` (`src/game/multichannel/
cluster_session_lookup.hpp`/`.cpp`) - a new, tiny DB-glue module, styled
after `ChannelSwitchAuditStore`'s existing query pattern - against the
`cluster_sessions` table for a row with that `player_id` and
`status = 'ONLINE'`. Returns the channel id, or `nil` if the player is
unknown or has no such row.

This deliberately reads the **DB mirror, not Redis**: unlike every other
multichannel fast path in this codebase, a GM issuing this command from one
channel process is very likely asking about a player logged into a
*different* one, so Redis's per-process caching advantage doesn't apply -
the DB table is the one thing every process can equally query regardless of
which one currently holds the player's session.

Following this codebase's own existing convention (verified: no
`Game.*`/`Player:*` Lua binding checks GM group access internally - e.g.
`luaGameReload`, `luaGameSetGameState` have zero access checks; the one real
enforcement point is `TalkAction:groupType(...)` at the framework/dispatch
layer, `src/lua/creature/talkaction.cpp`), this new function does not check
permissions itself - that is left to whatever talkaction/script exposes it
to GMs, exactly like every other admin-oriented Lua function already in this
engine.

**✅ Verified** against a real MariaDB 10.11: a player with an `ONLINE`
`cluster_sessions` row is correctly found and its `channel_id` returned; an
unknown player (no row at all) correctly returns nothing; and - the
important defensive case - a row that has been transitioned to `DIRTY`
(simulating an orphaned session, docs/multichannel/ARCHITECTURE.md §5.3) is
correctly **not** reported as a live channel location, since the query
filters on `status = 'ONLINE'` rather than merely "a row exists for this
player_id".

**✅ `Game.getClusterOnlinePlayers()`** (`src/lua/functions/core/game/
game_functions.cpp`) implements **"Cluster-wide online list"**: a read-only
Lua global returning an array of `{accountId, playerId, name, channelId}`
for every player currently recorded `ONLINE` anywhere in the cluster, via a
new `multichannel::listOnlinePlayers()` (`cluster_session_lookup.hpp`/
`.cpp`, a sibling of `findOnlineChannelForPlayer` above) - a single
`cluster_sessions` ⋈ `players` join, ordered by channel then name. Same
no-access-check convention as the previous command; same DB-mirror
rationale (a GM's own process only knows about players logged into itself).

**✅ `Game.getPlayerChannelSwitchHistory(name[, limit = 10])`** implements
**"Inspect the last N channel-switch audit rows for a player"**: resolves
the name to a guid the same way, then calls a new `ChannelSwitchAuditStore::
getRecentHistory(playerId, limit)` (`channel_switch_audit_store.hpp`/`.cpp`,
alongside the store's existing `findPending`/`getLastSwitchAtMs`) against
the `channel_switch_audit` table (§6), returning an array of
`{sourceChannelId (nil on first-ever login), targetChannelId, result,
denyReason, createdAt}`, newest first. `source_channel_id` is a nullable DB
column with no `isNull()` accessor available on this codebase's `DBResult`
type, so the query reads `COALESCE(source_channel_id, 0)` and treats `0` as
"unset" in C++ - safe because channel ids start at `1`
(`ChannelContext::DefaultSingleChannelId`), the same convention
`ChannelRegistry`'s existing `optionalIntColumn` helper already uses for a
different nullable int column.

**✅ Verified** against a real MariaDB 10.11 (both new queries, alongside
the existing one for this phase): the online-list join correctly returns
and orders multiple players across different channels; the history query
correctly returns rows newest-first, correctly honors `LIMIT`, correctly
represents a `NULL` `source_channel_id` (first-ever login) as absent in the
result, and correctly returns an empty list for a player with no audit
history at all.

**✅ `Game.getPlayerSessionLockInfo(name)`** implements **"Inspect a
session's current lock owner and fencing token"**: resolves the name to a
guid the same way, then calls a new `multichannel::findSessionLockInfo(
playerId)` (`cluster_session_lookup.hpp`/`.cpp`) returning the raw
`cluster_sessions` row - `{accountId, playerId, channelId, instanceId,
sessionId, fencingToken, status, acquiredAt, lastHeartbeat, expiresAt}` - or
`nil` if no lease has ever been acquired for that player. This lookup is
deliberately **not** filtered to `status = 'ONLINE'`, unlike
`getPlayerClusterChannel` - inspecting a stale/`DIRTY` session (the row left
behind by §5.3's dirty-session-recovery scenario) is the primary reason a
GM would reach for this command, so filtering it out would defeat the
command's purpose. `fencingToken` is a `bigint(20) unsigned` column read via
`DBResult::getNumber<uint64_t>`, verified to round-trip a token value of
`UINT64_MAX` correctly through both the DB layer's `std::stoull` parsing and
the existing `Lua::setField(lua_State*, const char*, lua_Number)` overload
(`lua_Number` is `double`; verified this is the same established pattern
already used for every other 64-bit field this series exposes to Lua, e.g.
`createdAt` in the channel-switch-history command above).

**✅ Verified** against a real MariaDB 10.11: inserted a `DIRTY` session row
with `fencing_token = 18446744073709551615` (`UINT64_MAX`) and confirmed the
exact projection query returns it unfiltered by status; confirmed a
nonexistent `player_id` correctly yields an empty result set (`nullopt` in
C++).

**📐 Known gap, stated honestly:** every other command in OPERATIONS.md's
list (kick a player on another channel, cross-channel broadcast,
force-save/drain/maintenance a channel, DIRTY session recovery) remains
contract-only - notably, every command implemented so far is read-only;
none of the remaining ones are (they all either mutate cluster state or
need cross-process signaling to a *different* channel process, which no
mechanism in this codebase currently provides).

## 11. Why Phase 1 and not the whole spec

The full spec (all 23 sections) describes cluster-wide leader election for
a dozen singleton jobs, a 3-process MySQL+Redis integration harness with 30
scenarios plus dedicated race tests, deep transactional rewrites of
market/mail/house/bank code, protocol-level login gateway routing for every
supported client version, and a green multi-platform CI matrix — after
each of those is actually implemented and verified. That is a genuinely
large distributed-systems project; this sandboxed session has no vcpkg
toolchain bootstrap and no multi-hour CI budget to iterate against (a
live MariaDB server, it turns out, *was* obtainable here via `apt-get`,
and got used heavily — see MIGRATION.md/TEST_PLAN.md). Claiming all of
that was built and verified here would be false. What *is* real in this
PR: the schema (imported and upgrade-tested against a real database, one
real bug found and fixed in the process), the config
surface, the core algorithms (position resolution, session fencing) with
unit tests and — for the Redis compare-and-swap logic specifically — a
real local `redis-server` integration check, the login-list wiring (which
the existing protocol already supports structurally), and a complete,
precise contract for every piece that is not yet wired, so Phase 2 has no
ambiguity about where to plug in. See TEST_PLAN.md for the exact test
matrix status.
