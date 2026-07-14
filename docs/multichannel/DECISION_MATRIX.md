# Decision Matrix

Every binding decision from the originating spec, the concrete choice made
(the spec's decisions are binding as written; where the spec left a choice
open, the safest-for-integrity variant was picked, per the spec's own
tie-breaking rule), and its implementation status in this PR.

Status legend: ✅ shipped and tested · 📐 designed/schema-ready, not wired ·
🔭 documented roadmap only.

| # | Decision | Choice made | Status |
|---|---|---|---|
| 2.1 | Global vs per-account state scope | Preserved existing Canary ownership boundaries exactly (player-owned stays player-owned, account-owned stays account-owned); house ownership is the only new cluster-wide constraint | ✅ (see §2 of ARCHITECTURE.md) |
| 2.1 | No bank/depot/inventory `player_id`→`account_id` migration | Confirmed not required by current model; not done | ✅ (no-op is the correct outcome) |
| 2.2 | Per-channel physical/runtime state | `houses`, `house_lists`, `tile_store` get `channel_id`; everything else in the list is already per-process in-memory by construction | ✅ schema / 📐 runtime wiring for instances |
| 2.3 | Market global, no `channel_id` in offer identity | `source_channel_id` added as nullable audit column only | ✅ schema / 📐 write call sites |
| 2.3 | Market operations transactional + idempotent | `economic_ledger.transaction_uuid` PK contract; wired into `IOMarket::processExpiredOffers` (expiry job) and `Game::playerCancelMarketOffer` (deterministic key off the cancelled offer's own id, safe since an offer can only be cancelled once), verified against a real MariaDB incl. the duplicate-`transaction_uuid` rejection | ✅ expiry job + cancel / 📐 create (no pre-existing key) + accept (needs a compound key for partial acceptance) |
| 2.4 | Position resolution order: same → nearest bounded → last-safe → temple | Implemented exactly, radius+cost bounded BFS; `EnginePositionLegality` wires it to the live Map/Tile/House (Zone-name convention for the 3 checks with no dedicated schema); `Game::playerRequestChannelSwitch` calls it for real | ✅ algorithm+tests+engine hook+switch command / 📐 `players.last_safe_position` (step 3) still not added |
| 2.4 | Persistent "last safe public position" | New `players.last_safe_position` intent documented; column not added to schema.sql in this PR (would require touching the very large `players` load/save path blind) | 📐 documented in MIGRATION.md as the exact ALTER + call sites needed |
| 2.5 | Composite house identity `(channel_id, house_id)` | Implemented on `houses`/`house_lists`/`tile_store` | ✅ schema / 📐 house ids still not independently reusable per channel (`houses_id_unique`) |
| 2.5 | One house per account, DB-enforced | `account_house_ownership` with `PRIMARY KEY(account_id)`; `House::setOwner` (the one real chokepoint for every ownership change) now mirrors every grant/revoke into it, verified against a real MariaDB (grant, re-grant moves the row, revoke deletes it) | ✅ schema+engine hook / 📐 no gate yet at bid/trade-*acceptance* time / 🐛 a grant only revokes the account's *previous house's mirror row*, not that other house's actual `houses.owner` if it lives on a different channel - see ARCHITECTURE.md §7 |
| 2.5 | Extend `houseOwnedByAccount`, no second model | Confirmed `House::ownerAccountId` stays the runtime cache resolved from `players.account_id`; `account_house_ownership` is the new cross-channel authority, not a competing cache | ✅ |
| 2.6 | Boss cooldowns/quest progress stay global | No schema change needed — already keyed by `player_id`/account, not per-channel | ✅ (no-op is correct) |
| 2.6 | Per-channel vs cluster-singleton event flag | Documented enum `EventClusterScope { PerChannel, ClusterSingleton }` and leader-election contract | 📐 (design in OPERATIONS.md §11) |
| 2.7 | Party is local-only, default policy `deny` | `channelSwitchPartyPolicy` config, default `"deny"`, `"leave"` supported | ✅ policy engine / 📐 party subsystem hook |
| 2.8 | Guilds fully global, no `channel_id` | Confirmed, no schema change to `guilds*` tables | ✅ (no-op is correct) |
| 2.8 | Guild hall = house, same per-channel/one-per-guild rule as houses | Documented; `account_house_ownership` model generalizes but a guild-hall-specific table is not added since no guild hall feature exists in current schema to extend | 🔭 |
| 2.9 | War kills global definition, combat only on PvP channels | `guildwar_kills.channel_id` audit column added | ✅ schema / 📐 combat-check call site |
| 2.10 | Per-channel `pvp_type`, kept compatible with existing `worldType` values | `channels.pvp_type` enum reuses exactly `no-pvp`/`pvp`/`pvp-enforced` | ✅ |
| 2.10 | `pvpChannelExitPolicy` default `combat-or-skull` | Config default set exactly as specified | ✅ |
| 2.11 | One online character per account, cluster-wide, defense in depth | `cluster_sessions` DB table (`PRIMARY KEY(account_id)` + `UNIQUE(player_id)`) + Redis lease/fencing; `ClusterRuntime` wires both into real login (acquire)/logout (release)/heartbeat (renew, outage handling) via `IClusterSessionRepository`/`DbClusterSessionRepository`, verified against a real MariaDB (a real upsert-corruption edge case was found and fixed - see TEST_PLAN.md) | ✅ schema+algorithm+Redis+DB engine hooks / 📐 admin tool for orphaned `DIRTY` sessions still not implemented |
| 2.12 | Mail/parcel exactly-once across channels | `mail_delivery_audit` table + `transaction_uuid` contract; a real cross-channel **loss** race (not just a missing idempotency guard) was found while scoping GM commands - `Mailbox::sendItem` writes to a throwaway offline copy of the recipient when they're actually online on a different channel, which that channel's own next save silently overwrites - see MIGRATION.md "Phase 12" | 📐 schema / 🐛 real gap found, not fixed |
| 2.13 | VIP/ignore/block global, no `channel_id` | Confirmed, no schema change | ✅ (no-op is correct) |
| 2.14 | Chat scope `local`/`cluster`, Pub/Sub for ephemeral only | `ChatChannelScope` enum documented; Redis Pub/Sub not used as source of truth for anything persistent | 📐 |
| 2.15 | Trade same-channel only, blocked during switch | Documented constraint; no code change needed since trade already only operates on locally-visible players | ✅ (already true by construction) / 📐 explicit switch-time guard |
| 2.16 | Exiva cross-channel policy | Documented: same-channel only by default, safe non-revealing message otherwise, GM override tool | 🔭 |
| 3.1 | Channel id resolution priority CLI > env > fallback | `ChannelContext` implements exactly this order, called from `main()` before anything else runs | ✅ tested and wired |
| 3.2 | Login gateway via existing multi-world protocol structure | Extended `ProtocolLogin::getCharacterList` (modern + legacy layouts) | ✅ |
| 3.3 | `channels` registry table, exact column set | Implemented as specified plus `login_gateway`, `map_hash` | ✅ |
| 3.4 | Runtime heartbeat table | `channel_runtime_status` schema + `ChannelRuntimeRegistry` Redis-backed fail-closed cache, driven every cycle by `ClusterRuntime::renewAllAndCollectExpired` via the existing `g_dispatcher().cycleEvent` mechanism; `ChannelRegistry::getLoginListChannels`/`ChannelSwitchService::evaluate` both consult it live when enabled; graceful shutdown publishes a final `OFFLINE` status | ✅ schema+heartbeat loop+login-filter+switch-check+graceful-shutdown / 📐 `DRAINING` status has no trigger (no drain command exists) |
| 3.5 | Map/data hash compatibility check, refuse on mismatch | `ChannelRegistry::computeFileHash` (the doc previously called it `computeMapHash`, a name never actually used in code) + comparison against every `channels.map_hash` row, wired into `CanaryServer::initializeMultichannelCluster()` before `loadMaps()` runs, verified against a real MariaDB (first-boot seed, cross-channel match, mismatch detection) | ✅ algorithm+tests+boot-sequence hook / 📐 narrow simultaneous-first-boot race, not Redis-CAS-protected (see ARCHITECTURE.md §3.5) |
| 4.1 | `config.lua.dist` keys exactly as specified | Added verbatim | ✅ |
| 4.3 | No unsafe disable-safety toggles | Confirmed none added | ✅ |
| 4.4 | Fail-closed startup validator | `ClusterConfigValidator`, called from `CanaryServer::initializeMultichannelCluster()`; `IRedisClient::ping()` (Hiredis + Fake) performs a real live PING, classified into 6 outcome categories, verified against a real local `redis-server` for all 5 failure categories plus success | ✅ config-shape checks incl. single-login-gateway, wired into real startup and aborts via `FailedToInitializeCanary` / ✅ live Redis ping / 📐 live cross-process "other login gateway still alive" heartbeat check |
| 5.1 | Atomic acquire/renew/release, fencing token, DB defense-in-depth | `ClusterSessionManager` + Lua CAS scripts + `cluster_sessions` | ✅ algorithm+tests, Redis-script-validated / 📐 engine hook |
| 5.2 | Clean logout ordering (block → SAVING → save → commit → OFFLINE → release) | State machine implements the exact ordering as transitions | ✅ state machine / 📐 wired to real save pipeline |
| 5.3 | Dirty session recovery, no blind TTL-based reuse | `DIRTY` state + admin inspection contract documented | ✅ state reachable and tested / 📐 admin tool, recovery validation logic |
| 5.4 | Optimistic state version, reject stale writes | `state_version` column documented for `cluster_sessions`-guarded saves | 🔭 (needs the real save pipeline from 5.2 first) |
| 6 | Channel switch requirements list | `ChannelSwitchService` implements cooldown/session/PZ/skull/party/position/capacity checks and audit write | ✅ policy engine+tests / 📐 engine hook |
| 7 | Guild war kills channel-restricted, combat blocked cross-channel appropriately | Documented; `guildwar_kills.channel_id` ready | 📐 |
| 8.1–8.4 | Transactions, idempotency, ledger, item UID | `economic_ledger` schema, wired into the market-offer-expiry job (`IOMarket::processExpiredOffers`) and `Game::playerCancelMarketOffer` via `EconomicLedgerStore`; item UID explicitly *not* added (see rationale below) | ✅ expiry job + cancel offer / 📐 remaining call sites (create/accept offer, mail, house) / 🔭 item UID |
| 9 | Redis: keys/scripts vs Pub/Sub vs Streams, no economic ops over Pub/Sub | Documented split; only the lease/fencing Lua scripts are implemented | ✅ scripts / 📐 Pub/Sub, Streams |
| 10.1–10.3 | Fail-closed Redis/DB loss, isolated channel crash doesn't affect others | State machine + documented operator runbook | ✅ state machine / 📐 live wiring |
| 11 | Leader election for singleton jobs | `EventClusterScope` enum + job inventory table in OPERATIONS.md; `ClusterLeaderElection` primitive (reuses `ClusterSessionManager`'s Redis lease/fencing mechanism, keyed by job name) + `ClusterJobLeadershipRegistry` cache, wired into `IOMarket::checkExpiredOffers` (recurring job), `Game::loadBoostedCreature`/`IOBosstiary::loadBoostedBoss` (one-shot startup jobs, a one-shot leader-election race), and `global_server_save.lua`'s daily reward reset (Lua-side, via a new `Game.tryClaimClusterJobLeadership(jobName)` binding). House rent charging/auction settlement, previously misclassified here as cluster-singleton, corrected to `per-channel` after tracing that houses are already disjoint per channel — see OPERATIONS.md | ✅ primitive+tests+4 jobs wired / 📐 remaining genuinely-global jobs unwired |
| 12 | Status/admin/metrics | Documented command and metric list, tagged by channel/instance; `Game.getPlayerClusterChannel`, `Game.getClusterOnlinePlayers`, `Game.getPlayerChannelSwitchHistory`, `Game.getPlayerSessionLockInfo` implemented (all read-only, `cluster_sessions`/`channel_switch_audit` DB lookups) | ✅ four GM commands / 🔭 the rest + metrics |
| 13 | Migrations idempotent, backward compatible, default off | `59.lua`/`60.lua`, guarded by `tableExists`/`columnExists` checks like existing migrations; `multiChannelEnabled=false` by default | ✅ |
| 14 | Table scope matrix | This document + ARCHITECTURE.md §2 | ✅ |
| 15 | Tests | See TEST_PLAN.md for per-scenario status | ✅ unit / 📐-🔭 integration+race (see TEST_PLAN.md) |
| 16 | CI green | See final report; only the changes actually in this PR were pushed for real CI evaluation | honest, not fabricated |
| 20 | MyAAC | `blakinio/myaac` not in this session's repo allowlist | 🔭 contract-only, see MYAAC_INTEGRATION.md |

## Notable "safest variant" calls made where the spec left room

- **Item UID (§8.4):** not added. The spec explicitly says not to rebuild
  the storage model just to add a UID if it risks compatibility, and to add
  anomaly detection instead if skipped. Given this session cannot compile
  or test the item serialization path end-to-end, adding a persistent
  64-bit item instance ID was judged higher risk than value for Phase 1.
  Anti-dupe here instead rests on the already-shipped layers: one session
  per account (DB constraint), transactional ledger contract, and
  idempotency keys — exactly the stack the spec says must exist *before*
  UID is even considered.
- **`cluster_sessions` primary key shape:** spec asks for "global lock on
  `account_id`" *and* "global lock on `player_id`" as two requirements.
  Modeled as one table with both a `PRIMARY KEY` and a `UNIQUE` constraint
  rather than two separate lock tables, since a single account can only
  ever have one online player at a time by game rules anyway — two tables
  would be two sources of truth for the same fact, which §2.5's
  "one authoritative representation" principle argues against generalizing
  to sessions too.
- **`houses.id` losing `AUTO_INCREMENT`:** existing house rows are always
  inserted with an explicit id from the map data
  (`iomapserialize.cpp:407`), never relying on MySQL-generated ids, so
  dropping `AUTO_INCREMENT` in favor of the composite `(channel_id, id)`
  primary key does not change any existing code path's behavior.
