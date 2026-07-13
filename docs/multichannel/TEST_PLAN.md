# Test Plan

Honest status of every test category the spec asks for. "Run" means
actually executed in this session and its result observed; "not run"
means the scenario requires infrastructure that was not available in this
development sandbox and is left for CI / a follow-up session to execute.
A real MariaDB 10.11 server and real gtest turned out to be installable
here (`apt-get install mariadb-server`/`libgtest-dev`) even though a
working Docker daemon and a bootstrapped vcpkg toolchain were not — so the
database and unit-test layers got substantially more real execution than
originally expected; the remaining gap is specifically a compiled,
running three-process Canary cluster.

## 15.1 Unit tests — ✅ implemented, added to `tests/unit`, 5 of 7 files actually compiled and run with real gtest

| Test | File | Status |
|---|---|---|
| Config validation (lease TTL vs heartbeat, pvp_type, party/exit policy enums) | `tests/unit/game/multichannel/cluster_config_validator_test.cpp` | ✅ **run**, 12/12 passed |
| Channel registry parsing/lookup/enabled-filtering | `tests/unit/game/multichannel/channel_registry_test.cpp` | ✅ written, not run locally (see below) |
| Channel id resolution priority (CLI > env > fallback) | `tests/unit/game/multichannel/channel_context_test.cpp` | ✅ written, not run locally (see below) |
| Position resolver: same-tile accept, radius-bounded search, house-access denial, restricted-zone denial, temple fallback | `tests/unit/game/multichannel/position_resolver_test.cpp` | ✅ **run**, 10/10 passed |
| Session lock acquire/renew/release against `FakeRedisClient` | `tests/unit/game/multichannel/cluster_session_manager_test.cpp` | ✅ **run**, 18/18 passed |
| Fencing token monotonicity + rejection of stale token | same file | ✅ **run** (included in the 18 above) |
| Channel switch policy: cooldown, PZ-lock block, skull policy variants, party deny/leave | `tests/unit/game/multichannel/channel_switch_service_test.cpp` | ✅ **run**, 18/18 passed |
| Idempotency: `economic_ledger` replay contract (pure logic model) | `tests/unit/game/multichannel/idempotency_test.cpp` | ✅ **run**, 5/5 passed |

**These compile against the project's real gtest-based unit test target**
(`canary_ut`, `CANARY_BUILD_TESTS=ON` with the vcpkg `tests` feature) in the
normal CMake build, which is what CI actually exercises. Separately, and in
addition to that, **5 of the 7 test files above were compiled and run in
this sandbox with a real `g++ -std=c++20` + the real `libgtest`/
`libgtest_main` (installed via `apt-get install libgtest-dev` for this
purpose) linked against each module's actual `.cpp`** — not a mock, not a
rewritten copy: `cluster_config_validator_test.cpp`,
`position_resolver_test.cpp`, `cluster_session_manager_test.cpp`,
`channel_switch_service_test.cpp`, and `idempotency_test.cpp`, totaling
**63 test cases, all passing**. `position_resolver_test.cpp` and
`cluster_session_manager_test.cpp` needed a small local shim (pre-included
standard headers, and a stub `operator<<(ostream&, Position)`) to stand in
for this project's precompiled header, which is unavailable without the
real CMake/vcpkg build; the module code under test was compiled unmodified
except for one real fix this exercise found (see below).

`channel_context_test.cpp` and `channel_registry_test.cpp` could **not** be
run locally: both modules use `inject<T>()` (this project's boost.di-based
DI container, `lib/di/container.hpp`), which requires `boost/di.hpp`
(vcpkg's `bext-di` package) - not installable via `apt`, and fetching the
single-header library from its upstream GitHub source was blocked by this
session's own external-code-fetch safety policy (an unvetted third-party
source, correctly refused). These two files are written to the same
conventions as the five that were run and will be compiled for real by CI;
their pure/static logic (`ChannelContext::resolveFrom`,
`ChannelInfo::isValidPvpType`, `ChannelRegistry::hashBytes`) was reviewed
carefully but not independently executed outside of the code review.

**A real bug this exercise found and fixed:** `position_resolver.hpp`
included `"game/movement/position.hpp"` *before* its own `<optional>`
include. In this project's real build that's harmless (the precompiled
header brings in `<optional>`/`<functional>` before any project header is
processed, regardless of local include order), but it is a latent
include-order hazard for any future non-PCH build, and it broke the
standalone compile immediately. Fixed by reordering the includes (system
headers before the local `position.hpp` include) - a one-line, zero-risk
correction, kept in the shipped header, not just the test harness.

A second, purely test-side bug was also found and fixed: an early
standalone assertion for `cluster_session_manager` accidentally renewed a
lease before asserting that a *different* renew call should fail due to
expiry, which had silently extended the expiry past the test's own
"expired" timestamp. Fixed in the test, not the production code - see the
relevant commit message for detail. Both of these are exactly the kind of
findings this level of real, executed verification is supposed to surface,
and both were caught and corrected in this session, not left for CI to
discover.

### Phase 2 additions

| Test | File | Status |
|---|---|---|
| `ClusterRuntime`: conflict rejection, clean release+reacquire, healthy renewal, legitimate supersession (no grace period), outage blocks new logins immediately, outage forces disconnect before lease could be stolen, `getTrackedSessionInfo` reflects the acquired handle | `tests/unit/game/multichannel/cluster_runtime_test.cpp` | ✅ **run**, 8/8 passed |
| `HiredisRedisClient` against a **real local `redis-server`** (not `FakeRedisClient`): acquire/conflict/renew/non-holder-renew/release/re-acquire/real-wall-clock-expiry/unreachable-connection | ad hoc standalone harness (not part of the gtest suite - a production networked client isn't something the project's own unit-test target exercises against a live server either) | ✅ **run**, 19/19 assertions passed |
| `multichannel::formatPosition`/`parsePosition`: round-trip, boundary values, malformed/negative/out-of-range/trailing-garbage rejection | `tests/unit/game/multichannel/position_serialization_test.cpp` | ✅ **run**, 10/10 passed |
| `describeChannelSwitchDenyReason` returns a non-empty string for every `ChannelSwitchDenyReason` | `tests/unit/game/multichannel/channel_switch_service_test.cpp` | ✅ **run** (included in that file's 19/19) |

`ChannelSwitchAuditStore`'s pure position (de)serialization was
deliberately split into its own `position_serialization.*` (no `database.hpp`
dependency) specifically so it could get the same real-gtest treatment as
everything else, rather than being untestable-by-construction inside a
class that also does live DB I/O - the same reasoning that split
`channel_info.hpp` out of `channel_registry.hpp` in Phase 1.

**A real bug this exercise found and fixed, in code from *this* PR, before
it ever reached CI:** `Game::renewClusterSessions()` was first declared
`const` (it only reads `ClusterRuntime` state, calling
`renewAllAndCollectExpired`), but its body also calls the existing,
non-const `Game::kickPlayer()` to force-disconnect an expired account -
`this` inside a `const` member function is `const Game*`, which cannot
bind to `kickPlayer`'s non-const `this`. Real compilers on every platform
caught this immediately and identically (GCC: "passing 'const Game' as
'this' argument discards qualifiers"; MSVC: "C2662: cannot convert 'this'
pointer from 'const Game' to 'Game &'") the moment this reached CI - fixed
by dropping the erroneous `const` from both the declaration and the
definition. Left in this document instead of quietly amended away, per
this repo's established practice of recording every real bug CI (not just
local review) actually caught.

`libhiredis-dev` (1.2.0, matching the vcpkg package's typical version) was
installable via `apt-get` in this sandbox, same as `libgtest-dev` and
`mariadb-server` before it - unexpected again, and used for real: the
production `IRedisClient` implementation Phase 1 explicitly declined to
write blind was compiled against the actual header/lib and driven against
an actual running Redis server, including letting a real lease actually
expire on the wall clock rather than only simulating time.

**A real test-driven bug found and fixed here:** `FakeRedisClient`'s new
`isHealthy()`/`setHealthyForTesting()` were added so `ClusterRuntime`'s
outage-handling logic could be tested, but the fake's existing
`acquireLease`/`renewLease`/`releaseLease` methods didn't originally
consult the simulated-outage flag at all - a test asserting "this account
survives a brief Redis outage, then gets force-expired once its lease
nears real expiry" would have passed for the wrong reason (every renew
kept silently succeeding, so the account's tracked expiry kept advancing
forever and the "about to expire" branch was never actually exercised).
Fixed by making the fake's CAS methods fail cleanly while marked
unhealthy, matching what an actually-unreachable Redis would do. The bug
was entirely in the test double, not in `cluster_runtime.cpp` itself - but
without the fix, the outage test would have been asserting the wrong
thing and passing for the wrong reason, which is exactly the kind of gap
this level of real, executed verification exists to catch.

**What was reviewed but could not be compiled or run in this sandbox:**
the actual engine call sites - `ProtocolGame::login`'s acquire gate and
switch-audit consumption, `Player::onRemoveCreature`'s release call,
`Game::renewClusterSessions`, `Game::playerRequestChannelSwitch` and its
`player:requestChannelSwitch` Lua binding, and
`CanaryServer::initializeMultichannelCluster`'s `HiredisRedisClient`
construction - and `EnginePositionLegality` (`tileExists`/
`isInaccessibleHouse` against `Tile`/`House`, and the `Zone`-name
convention for the other three checks). Each of these files transitively
includes the project's full engine header graph (`game/game.hpp` pulls in
Lua, the database layer, and eventually protobuf/Abseil/opentelemetry via
`src/pch.hpp`'s own dependency list), which requires the real vcpkg-
managed toolchain to compile; this sandbox does not have one bootstrapped
(confirmed again this session: `mysql/mysql.h` was reachable after
installing `libmariadb-dev` and shimming the include path, but the very
next missing header was `absl/numeric/int128.h`, at which point chasing
the rest of vcpkg's dependency tree one `apt-get` at a time stopped being
a reasonable use of the time available). Each was instead reviewed by hand
against the exact surrounding code (matching existing patterns for
per-account checks, `cycleEvent` registration, `queryAdd`-based tile
legality, etc.) - **CI is the first real compiler for these**, per this
repo's established CI-repair policy from #69.

### Phase 3: house ownership mirror

`House::setOwner`'s new `account_house_ownership` sync (ARCHITECTURE.md
§7) is DB-write glue inside a `.cpp` that transitively pulls in the full
engine (`game/game.hpp`), so it hits the same standalone-compile wall as
every other engine call site in this document. What was verified instead,
against a real MariaDB 10.11 (fresh `schema.sql` install, two real
accounts, two real houses on channel 1):

- **Grant**: the exact `UPDATE houses` + `DELETE ... WHERE channel_id=?
  AND house_id=?` + `SELECT ... FROM players` + `DELETE ... WHERE
  account_id=?` + `INSERT` sequence the new code issues, run in order,
  produces exactly one `account_house_ownership` row for the new owner.
- **Re-grant**: the same account "buying" a second house on the same
  channel moves the row (the old house's row disappears, a new one
  appears for the new house) rather than leaving two - confirms the
  `PRIMARY KEY(account_id)` semantics work as the one-house-per-account
  invariant this table exists to hold, even without any new application-
  level gate.
- **Revoke**: `guid = 0` deletes the row and leaves none behind.
- **Cross-channel collision**: attempting to give two different channels
  a house with the same numeric id (to check `(channel_id, house_id)`
  scoping in isolation) hit `houses_id_unique` first - a real, pre-
  existing Phase 1 constraint (see MIGRATION.md's "Known limitation"),
  confirming this is not a new gap the mirror introduces; today every
  `house_id` the mirror will ever see is already globally unique on its
  own, so the `channel_id` scoping is inert until that separate,
  documented limitation is lifted.

### Phase 4: cluster_sessions DB defense-in-depth

`ClusterRuntime`'s new `IClusterSessionRepository`/`DbClusterSessionRepository`
wiring got two levels of real verification:

- **13 gtest cases** (up from 7) against `FakeClusterSessionRepository`
  (`tests/shared/game/multichannel/fake_cluster_session_repository.hpp`, an
  in-memory model of the real table's `PRIMARY KEY(account_id)` +
  `UNIQUE(player_id)` constraints): acquire writes a row, clean logout
  deletes it, a healthy renew updates its heartbeat, an outage-forced
  disconnect deletes it, and - the interesting one - a simulated
  repository write failure on acquire rolls back the Redis lease it had
  just taken (verified a subsequent acquire then succeeds cleanly). All
  13/13 passing.
- **Real MariaDB 10.11**, the exact SQL the code issues: a fresh acquire
  produces one row; a second acquire for the same account (relogin/switch)
  moves that same row in place rather than duplicating it; heartbeat and
  release both behave as expected. **A real bug found and fixed here**: a
  naive single `INSERT ... ON DUPLICATE KEY UPDATE` silently corrupted a
  row when an INSERT collided on `cluster_sessions_player_unique` (a
  *different* account's existing row) rather than the `account_id` primary
  key - MySQL updated that other row's session/channel columns via
  `VALUES()` but left its `account_id` untouched, since `account_id` was
  never itself in the `UPDATE` clause. The result was one row whose
  `account_id` belonged to the old holder but whose `session_id`/
  `channel_id`/etc. described the new one - an internally inconsistent
  record, not a clean rejection. This exact scenario is realistically
  unreachable through the real call path (`player_id` is permanently tied
  to one `account_id` in this engine, and `ProtocolGame::login` only ever
  calls this with a `(accountId, playerId)` pair `IOLoginData` already
  verified belong together) - but it was worth fixing anyway, since it's
  precisely the kind of anomaly this defense-in-depth layer exists to
  catch cleanly rather than silently mishandle. Fixed with an explicit
  `DELETE FROM cluster_sessions WHERE player_id = ? AND account_id != ?`
  before the upsert (mirroring the same "explicit multi-step over one
  clever multi-key statement" choice already made for
  `account_house_ownership` in Phase 3); re-verified against the real
  database that both the normal re-acquire case and the anomaly case now
  behave correctly.
- `db_cluster_session_repository.cpp` itself is not standalone-compilable
  (transitively pulls in `database/database.hpp`'s full dependency chain,
  same wall as `channel_switch_audit_store.cpp`/`house.cpp`) - reviewed by
  hand, verified at the SQL level for real as above.

### Phase 5: economic ledger idempotency (market-offer-expiry job)

`IOMarket::processExpiredOffers`'s new `EconomicLedgerStore` wiring
(`beginPending`/`markCommitted`/`markFailed`) got the same two-level
treatment:

- **5 new gtest cases** (`tests/unit/game/multichannel/
  economic_ledger_id_test.cpp`) against the pure, dependency-free
  `multichannel::computeDeterministicLedgerUuid` (`economic_ledger_id.hpp`/
  `.cpp`, split out of `EconomicLedgerStore` the same way
  `position_serialization.hpp` was split out of `channel_switch_audit_store`
  in Phase 2, purely so it can be compiled and tested standalone without
  pulling in `database.hpp`): produces a 36-char, 8-4-4-4-12-shaped string;
  deterministic for the same inputs; differs for different natural keys;
  differs for different namespace tags sharing the same natural key; and
  no collisions across a sequential range of 10,000 natural keys. Compiled
  standalone with real `g++ -std=c++20` + real `libgtest`/`libgtest_main`
  and run - **5/5 passing**.
- **Real MariaDB 10.11**, the exact SQL `EconomicLedgerStore` issues,
  imported against the real `schema.sql`'s `economic_ledger` table:
  `beginPending`'s `INSERT` followed by `markCommitted`'s `UPDATE`
  produces the expected `COMMITTED` row; **a second `beginPending` INSERT
  for the same `transaction_uuid` (the replay scenario) is rejected with a
  real `ERROR 1062 Duplicate entry ... for key 'PRIMARY'`** - this is the
  core idempotency guarantee the whole mechanism exists to provide, and it
  was verified against the actual constraint, not assumed. Also verified:
  the item-delivery ledger record shape (`amount = 0`, `item_id`/
  `item_count` populated) reaching `FAILED` via `markFailed`, and the
  currency-refund shape (`amount` populated, no item fields) reaching
  `COMMITTED` via `markCommitted`.
- `economic_ledger_store.cpp` itself is not standalone-compilable (same
  `database.hpp` wall as `db_cluster_session_repository.cpp`/
  `channel_switch_audit_store.cpp`) - reviewed by hand, verified at the SQL
  level for real as above.
- **Not covered by this phase**: the three live market call sites
  (`Game::playerCreateMarketOffer`/`...CancelMarketOffer`/
  `...AcceptMarketOffer`) do not write to `economic_ledger` yet - only the
  expiry background job does. No integration test exercises
  `IOMarket::checkExpiredOffers`'s actual scheduling/dispatch path (that
  requires the full engine + `g_databaseTasks()`, unavailable in this
  sandbox); only the SQL `EconomicLedgerStore` issues was verified
  directly.

### Phase 6: cluster leader election primitive

`ClusterLeaderElection` (`src/game/multichannel/cluster_leader_election.hpp`/
`.cpp`) got the same standalone-gtest treatment as `ClusterSessionManager`
in Phase 1, since it has the same zero-engine-dependency property (it only
depends on `redis_client.hpp` and reuses `ClusterSessionManager::
generateSessionId()`):

- **13 new gtest cases** (`tests/unit/game/multichannel/
  cluster_leader_election_test.cpp`) against `FakeRedisClient`: first
  acquire gets fencing token 1; a second acquire while held is rejected and
  correctly reports the current holder; different job names don't
  contend; renew by owner succeeds and preserves the token; renew by a
  non-owner session id fails; renew past expiry does not resurrect
  leadership; release by owner succeeds and immediately frees the lock for
  a new acquire; release by non-owner fails; the fencing token is
  monotonic across release/reacquire cycles; an expired, never-released
  lease can be reacquired with a strictly higher token; a stale token
  correctly reads as no-longer-current after a takeover; a 16-thread
  concurrent-acquire race has exactly one winner and exactly one fencing
  token issued; and lock keys are correctly scoped per job name. Compiled
  standalone with real `g++ -std=c++20` + real `libgtest`/`libgtest_main`
  and run - **13/13 passing**.
- No new Redis Lua scripts were needed: `acquire.lua`/`renew.lua`/
  `release.lua` (already validated against a real `redis-server` in Phase
  1/2 - see 15.1b below) only ever operate on an opaque lock key/session
  id/TTL and have no player-session-specific semantics, so they apply
  unchanged to a leader-election lock keyed by job name.
- **Not covered by this phase**: no actual background job calls
  `ClusterLeaderElection::acquire`/`renew`/`isFencingTokenCurrent` yet -
  this phase implements and verifies the primitive only. No integration
  test exercises a real job (e.g. `IOMarket::checkExpiredOffers`) actually
  contending for leadership across two simulated processes, since that
  requires the full engine + scheduler, unavailable in this sandbox.

### Phase 7: wiring the leader election primitive into the market-expiry job

`ClusterJobLeadershipRegistry` (`src/game/multichannel/
cluster_job_leadership_registry.hpp`) got the same standalone-gtest
treatment as `ClusterLeaderElection` in Phase 6, since it's also header-only
with zero engine dependency:

- **8 new gtest cases** (`tests/unit/game/multichannel/
  cluster_job_leadership_registry_test.cpp`) against `FakeRedisClient`:
  disabled-by-default never claims leadership; first `renewOrAcquire` claims
  it; different job names are independent; a second instance cannot steal
  an already-held, unexpired job lease; repeated `renewOrAcquire` calls keep
  leadership across cycles; losing the lease during a simulated Redis outage
  correctly stops claiming leadership; **leadership correctly recovers once
  the outage ends**; `resetForTesting` clears everything. Compiled
  standalone with real `g++ -std=c++20` + real `libgtest`/`libgtest_main`
  and run - **8/8 passing**.
- **A real bug found and fixed here**: the first version of
  `renewOrAcquire` discarded the remembered lease id the moment a renew
  call failed, before falling back to a fresh `acquire`. During a
  transient Redis outage this was actively harmful: the fallback `acquire`
  attempt correctly failed too (Redis still unreachable), but by the time
  Redis became reachable again, the id needed for a clean `renew` was
  already gone — the `acquire.lua` script unconditionally rejects an
  `acquire` against a lease that has not yet expired on Redis's own clock,
  *even from the lease's own rightful holder* (only `renew` checks session
  id ownership), so this process would incorrectly abstain from leadership
  until the full TTL elapsed, even though nothing else ever contended for
  the job. Caught by the `RecoversLeadershipAfterOutageEnds` test failing
  on the first implementation. Fixed by keeping the remembered id across a
  failed renew and only replacing it once a fallback `acquire` actually
  succeeds; re-verified all 8 cases pass afterward.
- `IOMarket::checkExpiredOffers`'s new leadership gate (`src/io/
  iomarket.cpp`) itself is not standalone-compilable (transitively pulls in
  `game/game.hpp`/`database/database.hpp`'s full dependency chain, the same
  wall as every other engine-glue file this session) — reviewed by hand;
  the gate is a single cheap boolean check (`isEnabled() ` short-circuits
  to "always run" when multichannel is off, exactly preserving today's
  single-node behavior) wrapped around the pre-existing query, not a change
  to the query or refund logic itself.
- **Not covered by this phase**: no other job in OPERATIONS.md's inventory
  table (house rent, daily reward reset, highscores rebuild, ...) is wired
  to leadership yet — only `market.expire`. No integration test exercises
  two simulated channel processes actually contending for the same job
  lease end-to-end (would require the full engine + scheduler running
  twice, unavailable in this sandbox); the contention semantics themselves
  are covered at the `ClusterLeaderElection`/`ClusterJobLeadershipRegistry`
  unit level instead.

### Phase 8: GM command to locate a player's cluster channel

`multichannel::findOnlineChannelForPlayer` (`src/game/multichannel/
cluster_session_lookup.hpp`/`.cpp`), backing the new
`Game.getPlayerClusterChannel(name)` Lua global, was verified against a real
MariaDB 10.11, importing the real `schema.sql`:

- A player with an `ONLINE` row in `cluster_sessions` is found and its
  `channel_id` returned correctly.
- A player with no row at all (unknown to the cluster) correctly returns
  nothing, matching the function's `std::nullopt` contract.
- **The important defensive case**: after transitioning that same row's
  `status` to `DIRTY` (simulating an orphaned session per
  ARCHITECTURE.md §5.3), the exact same query correctly returns nothing -
  confirming the `status = 'ONLINE'` filter actually matters and isn't a
  no-op, since a naive "does a row exist for this player_id" query would
  have wrongly reported a dirty session as a live location.
- `IOLoginData::getGuidByName`'s existing name-to-id resolution was
  exercised alongside it (a known player name resolves; an unknown name
  returns no row), since the Lua binding chains both lookups.

`game_functions.cpp`'s new binding itself is not standalone-compilable
(transitively pulls in the full engine, same wall as every other Lua
binding file) - reviewed by hand against the verified SQL above; it is a
thin two-call chain (name → guid → channel id) with no additional logic of
its own. `check_lua_api_binding_docs.py`/`check_lua_api_quality.py` both
pass against the hand-written `docs/lua-api/lua_api.json` entry (mirrors
Phase 2's `Player:requestChannelSwitch` precedent: this repo's own CI is
the first real compiler for the actual `.cpp`, and its
`--generate-lua-api-docs-only` step - made more robust by the Phase 6/7 CI
fix - will auto-correct the doc entry if the hand-written version drifts
from a real regeneration).

### Phase 9: leader election for boosted creature/boss, and a corrected misclassification

While scoping "wire the next cluster-singleton job" as a follow-up to
Phase 7, house rent charging (`Houses::payHouses`) was investigated first
as the next candidate. Tracing its actual data access (iterates the
in-memory `houseMap`, itself populated per-channel from each channel's own
OTBM map) revealed it - and house auction settlement, which shares the same
per-channel `houseMap` - are **not** cluster-singleton at all: each channel
already only ever touches its own disjoint houses. Gating either behind
`ClusterJobLeadershipRegistry` would have caused non-leader channels to
silently stop charging rent/settling auctions for their own houses - a real
regression, not a fix. No code change was made for these two; OPERATIONS.md
and ARCHITECTURE.md were corrected instead (`per-channel`, not
`cluster-singleton`).

Two other candidates - `Game::loadBoostedCreature` (`src/game/game.cpp`)
and `IOBosstiary::loadBoostedBoss` (`src/io/io_bosstiary.cpp`) - were
checked the same way and confirmed genuinely global: `boosted_creature`/
`boosted_boss` are both `PRIMARY KEY(date)` with no `channel_id` column, and
`schema.sql` grep-confirmed this directly (not just trusting the existing
OPERATIONS.md claim, having just been burned by a wrong one). Both are now
wired:

- Each function, upon finding its row's `date` is stale, now calls
  `ClusterJobLeadershipRegistry::renewOrAcquire("boosted.creature"/
  "boosted.boss", SESSION_LEASE_TTL, OTSYS_TIME())` directly (a one-shot
  acquire race, not a sustained per-cycle check, since both are one-shot
  startup calls with no periodic heartbeat cycle running yet at this point
  in `CanaryServer::loadModules()`) and checks `isLeader(...)` immediately
  after. The winner proceeds with the existing reroll+persist logic
  unchanged; every other process falls back to reading whatever is
  currently on record instead.
- Neither new call site is standalone-compilable (both transitively pull in
  `game/game.hpp`/`database/database.hpp`'s full dependency chain, the same
  wall as every engine-glue file in this series) - reviewed by hand. The
  underlying `ClusterLeaderElection`/`ClusterJobLeadershipRegistry`
  primitives being called were already thoroughly verified with real gtest
  in Phase 6 (13 cases, including a 16-thread concurrent-acquire race with
  exactly one winner) and Phase 7 (8 cases, including outage/recovery); this
  phase's changes are thin, mechanical call sites invoking already-proven
  logic, not new logic of their own.
- `schema.sql` was checked directly to confirm `boosted_creature`/
  `boosted_boss` each already seed a default row
  (`INSERT INTO boosted_boss (...) VALUES ('default', 0, 0);` and the
  `boosted_creature` equivalent), meaning `IOBosstiary::loadBoostedBoss`'s
  `if (!result)` "no row exists" branch is dead code on any server
  initialized from this schema - a pre-existing quirk, not something this
  phase's gate needed to specially handle (the gate still runs correctly on
  either branch).

### Phase 10: two more read-only GM commands

`multichannel::listOnlinePlayers()` (`cluster_session_lookup.hpp`/`.cpp`)
and `ChannelSwitchAuditStore::getRecentHistory` (`channel_switch_audit_store
.hpp`/`.cpp`) were both verified against a real MariaDB 10.11, mirroring
Phase 8's methodology exactly:

- **`listOnlinePlayers`**: seeded two players on two different channels
  (both `ONLINE` in `cluster_sessions`); the `cluster_sessions` ⋈ `players`
  join correctly returned both, correctly ordered by `channel_id` then
  `name` (the lower-channel-id player first, regardless of insertion
  order).
- **`getRecentHistory`**: seeded three `channel_switch_audit` rows for one
  player - a first-ever-login row (`source_channel_id IS NULL`), a normal
  `SUCCESS` switch, and a `DENIED` switch - and one player with no rows at
  all. Verified: all three rows returned newest-first when queried with a
  generous limit; `LIMIT 2` correctly truncated to the two newest; the
  `NULL` source channel correctly read back as `0` via
  `COALESCE(source_channel_id, 0)` and correctly translated to
  `std::nullopt` in C++ (0 is confirmed never a valid channel id -
  `ChannelContext::DefaultSingleChannelId = 1`); and the player with no
  history correctly produced an empty result set, not an error.
- **A real, if minor, mistake was caught and fixed before committing**:
  the first attempt to add the two new `lua_api.json` entries used
  Python's `json.dump(..., indent=2, sort_keys=True)` to rewrite the whole
  file, which reformatted ~50 unrelated lines across the file (whitespace/
  key-ordering differences from whatever originally generated it) - a
  needlessly large, noisy diff for a two-entry addition. Reverted and redid
  it as two precise text edits instead (15 lines changed, matching every
  other `lua_api.json` edit in this series).
- **A real Lua API quality regression was also caught and fixed**: the
  first version of both new bindings' return type was the literal string
  `"table"`, which `tools/check_lua_api_quality.py` tracks as the
  `return_plain_table` metric against a baseline - two new plain-`table`
  returns would have pushed it from 22 to 24, failing the check. Fixed by
  using the more accurate `table[]` (both functions return an array of
  records, not a single flat table) in both the EmmyLua docblocks and the
  hand-written JSON entries; re-ran `check_lua_api_quality.py` and
  confirmed the metric stayed at 22.
- Neither new Lua binding is standalone-compilable (same engine-glue wall
  as every other Lua binding file in this series) - reviewed by hand
  against the SQL verified above.

### Phase 11: economic_ledger wired into `playerCancelMarketOffer`

`Game::playerCancelMarketOffer` (`src/game/game.cpp`) is not standalone-
compilable (same `game/game.hpp` → `mysql.h` → `absl` wall as every other
engine-glue file in this series), so it was reviewed by hand against a real
MariaDB 10.11 instance (scratch database `canary_phase11_test`, imported
from the real `schema.sql`, dropped after):

- Computed the real deterministic UUIDs the new code path produces via a
  standalone compile of the already-merged, dependency-free
  `economic_ledger_id.cpp` from Phase 5:
  `multichannel::computeDeterministicLedgerUuid("market.cancel", 42)` =
  `fe49ddeb-4440-2e43-0000-00000000002a`, and the same for offer 43 =
  `...002b` - confirming the namespace tag actually changes the derived UUID
  (as opposed to accidentally colliding with `"market.expire"`'s keyspace
  for the same offer id).
- Replayed the buy-offer cancel sequence by hand: `INSERT` a `PENDING` row
  with the computed UUID and the currency `amount` populated (no item
  fields), then `UPDATE ... SET status = 'COMMITTED'` - both statements
  succeeded exactly as `EconomicLedgerStore::beginPending`/`markCommitted`
  would issue them.
- Replayed the sell-offer cancel sequence: `INSERT` a `PENDING` row with
  `item_id`/`item_count` populated and no `amount`, then `UPDATE ... SET
  status = 'FAILED'` - confirming the shape `markFailed` writes for an
  inbox-insertion-failure early exit.
- Replayed a duplicate cancel of the same offer: a second `INSERT` using
  the identical offer-42 UUID was correctly rejected with `ERROR 1062
  (23000): Duplicate entry ... for key 'PRIMARY'` on `transaction_uuid` -
  the exact replay-protection guarantee the whole design depends on.
- Hand-traced the store-coin exclusion: confirmed `ITEM_STORE_COIN` is
  `22118` (`src/utils/utils_definitions.hpp:604`) and that the
  `isStoreCoinOffer` check is evaluated once, before either the ledger
  bracket or the `it.id == 0`/`it.id == ITEM_STORE_COIN` branches inside
  the sell path - so the unconditional `EconomicLedgerStore::markFailed`
  call inside the `it.id == 0` early-exit branch can never fire when
  `beginPending` was skipped (`it.id == 0` and `it.id == ITEM_STORE_COIN`
  are mutually exclusive by construction), ruling out a call to
  `markFailed` on a transaction that was never begun.
- `clang-format-18 --dry-run --Werror src/game/game.cpp` passed cleanly.
- No Lua bindings touched this phase, so `tools/
  check_lua_api_binding_docs.py`/`check_lua_api_quality.py` are unaffected
  (confirmed 0 new findings from both).

### Phase 12: fourth GM command (session lock/fencing inspection)

`multichannel::findSessionLockInfo` (`cluster_session_lookup.hpp`/`.cpp`)
and its Lua binding `Game.getPlayerSessionLockInfo` were verified against a
real MariaDB 10.11 (scratch database `canary_phase12_test`, imported from
the real `schema.sql`, dropped after), mirroring Phase 8's methodology:

- Reused the sample seed rows `schema.sql` itself inserts (`players.id = 1`,
  `"Rook Sample"`, `account_id = 1`) rather than hand-crafting new
  account/player rows, after an initial attempt to `INSERT` synthetic ones
  failed on a stale guessed column list (`accounts.premium_ends_at` doesn't
  exist in this schema) - a reminder to check the real seeded seed data
  before writing throwaway fixture rows.
- Inserted a `cluster_sessions` row with `status = 'DIRTY'` and
  `fencing_token = 18446744073709551615` (`UINT64_MAX`) and ran the exact
  projection query the new code issues: confirmed it returns the row
  **unfiltered by status** (the defining difference from
  `findOnlineChannelForPlayer`, which does filter to `ONLINE`) and that the
  `UINT64_MAX` fencing token round-trips through MariaDB's `bigint(20)
  unsigned` column intact.
- Confirmed a query for a `player_id` with no `cluster_sessions` row at all
  returns an empty result set, which the C++ layer maps to `std::nullopt`
  (existing, already-verified `storeQuery` → `nullptr` convention).
- Traced `DBResult::getNumber<uint64_t>`'s implementation
  (`src/database/database.hpp`) to confirm it parses via `std::stoull` for
  unsigned types, and confirmed the existing `Lua::setField(lua_State*,
  const char*, lua_Number)` overload (`lua_Number` is `double`,
  `src/lua/functions/lua_functions_loader.hpp:55`) is the same pattern
  already used for every other 64-bit field this series has exposed to Lua
  (e.g. `createdAt` in Phase 10's channel-switch-history command) - not a
  new risk introduced by this field.
- `clang-format-18 --dry-run --Werror` on all four changed files passed
  cleanly; `tools/check_lua_api_binding_docs.py --base origin/main` and
  `tools/check_lua_api_quality.py` both passed, the latter confirming the
  new binding's `"table|nil"` return type does not exact-string-match
  `RETURN_METRICS`' `"table"` key and so does not regress
  `return_plain_table` (stayed at 22).
- Neither new C++ file nor the Lua binding file is standalone-compilable
  (same engine-glue wall as every other file in this series) - reviewed by
  hand against the SQL verified above.

**A real bug was found while scoping this command, not fixed** (documented
in ARCHITECTURE.md §8, DECISION_MATRIX.md row 2.12, and MIGRATION.md "Phase
12"): `Mailbox::sendItem` silently writes mail into a throwaway offline
copy of a recipient who is actually online on a *different* channel, which
that channel's own next save can silently overwrite - a genuine
cross-channel data-loss race, not just a missing idempotency guard. Not
attempted this phase: the fix needs the same DB-row-handoff design already
used for channel switching (§6), which is materially larger than a bounded
GM-command addition.

## 15.1b Redis Lua CAS script validation — ✅ run against a real `redis-server`

The acquire/renew/release Lua scripts in
`src/game/multichannel/redis_scripts/` were loaded into a real local
`redis-server` (available in this sandbox) via `redis-cli --eval` and
exercised directly:

- acquire on an empty key succeeds, returns session id + fencing token 1
- second acquire attempt while a lease is held and unexpired is rejected
- renew by the owning session id succeeds and does not change the fencing
  token
- renew by a non-owning session id is rejected
- release by the owning session id succeeds and clears the key
- a fresh acquire after release/expiry issues fencing token 2, never
  reusing 1
- 8 concurrent `redis-cli --eval acquire.lua` processes fired at the same
  key at once (via shell background jobs): exactly one acquired, and
  exactly one fencing token (1) was ever issued, confirmed by inspecting
  every process's raw output plus the key's final `HGETALL` state

This is real integration proof that the compare-and-swap semantics the
whole anti-split-brain design depends on (THREAT_MODEL T1/T2) are correct
Lua, not just a description. See the PR commit for the exact `redis-cli`
transcript.

## 15.2 Integration tests (3-process, MySQL+Redis) — not run

Requires a bootstrapped vcpkg toolchain to produce three actual Canary
binaries; that specific piece was not available in this sandbox (no
`vcpkg`). A real MariaDB server *was* obtained and used extensively (see
§15.4 and MIGRATION.md's "What was actually verified" section) - the
remaining gap is specifically the compiled engine, not the database. The
30 scenarios from the spec are captured as concrete, numbered acceptance
criteria in `docker/multichannel/SCENARIOS.md` so they can be executed
against the Compose stack in this PR by CI or by an operator with Docker
access, once Phase 2 wires the engine call sites these scenarios exercise
(most of them — login races, session takeover, position fallback — depend
on code marked 📐 in ARCHITECTURE.md).

## 15.3 Anti-dupe race tests — run at every level this PR's code actually reaches

- **Redis CAS script race:** 8 concurrent `redis-cli --eval` acquire
  calls fired at the same key at once — confirmed exactly one succeeds
  and exactly one fencing token is ever issued (✅ run, see 15.1b).
- **`FakeRedisClient` concurrent acquire:** unit test spins 16-32 threads
  calling `acquire()` on the same account/player key concurrently, asserts
  exactly one succeeds and the fencing token sequence has no gaps or
  repeats (✅ run, both via the real gtest suite and a standalone g++
  harness).
- **DB constraint enforcement** (`cluster_sessions.PRIMARY KEY(account_id)`,
  `cluster_sessions_player_unique`, `account_house_ownership.PRIMARY
  KEY(account_id)`, `account_house_ownership_house_unique`): ✅ **run**
  against a real MariaDB 10.11 instance installed in this sandbox
  (`apt-get install mariadb-server` worked, even though a Docker daemon
  did not). Confirmed each constraint actually rejects the specific
  duplicate it exists to prevent — a second house for one account, a
  second account claiming one physical house, a second online session for
  one account, and a second session for one player under a different
  account. This is sequential constraint-violation testing (one `INSERT`
  after another observing the rejection), not literally two concurrent
  connections racing in the same millisecond — but a UNIQUE/PRIMARY KEY
  constraint is exactly the mechanism that makes concurrent races
  irrelevant (MySQL/MariaDB serializes conflicting writes at the storage
  engine regardless of arrival timing), so confirming the constraint
  itself is real and correctly shaped is the meaningful thing to verify
  here, and it was.

## 15.4 Compatibility — schema/migration path run against a real database; engine boot not run

- **Single-channel mode unaffected:** verified by inspection — every new
  code path added in Phase 1 is gated by `multiChannelEnabled` (which
  defaults `false`) or is purely additive schema (migrations are
  `CREATE TABLE IF NOT EXISTS` / guarded `ALTER`). Not verified by an
  actual full-engine build+boot in this sandbox (no vcpkg toolchain).
- **Migration idempotency and upgrade correctness: ✅ run for real**, not
  just reviewed. This session installed a real MariaDB 10.11 server,
  imported the pre-PR `schema.sql` (a genuine "v58" baseline, via `git
  show`), applied `59.lua` and `60.lua`'s actual SQL bodies in their real
  file order as a live upgrade, diffed the result against a fresh-install
  `schema.sql` import (identical modulo column order), and confirmed every
  guard query used by the Lua idempotency checks
  (`SHOW COLUMNS ... LIKE`, `SHOW KEYS ... WHERE Column_name = ...`,
  `information_schema` existence checks) returns exactly what the
  migration script expects to see post-migration - i.e. a second run
  would correctly no-op. The documented rollback SQL in MIGRATION.md was
  also executed against the upgraded database and confirmed to restore
  the exact pre-migration `houses` shape. **This process found and fixed
  a real bug**: `account_id` columns on four new tables were declared as
  plain signed `int(11)` instead of `int(11) UNSIGNED` to match
  `accounts.id`, which MariaDB rejected outright as a malformed foreign
  key the moment `schema.sql` was imported for real - see MIGRATION.md
  for detail. What's still not run: three actual compiled Canary
  processes reading/writing through this schema end-to-end (needs the
  vcpkg toolchain this sandbox doesn't have).
- **Legacy protocol layout:** `ProtocolLogin` change was written to
  preserve the exact existing single-world output when
  `multiChannelEnabled = false` (early-return keeps the original code
  path completely untouched), and to extend, not replace, the multi-world
  encoding when enabled. Not run against a real client.
- **Windows/macOS build:** not attempted (no cross-toolchain in this
  sandbox); nothing in this PR is platform-specific (no OS-specific
  syscalls added), so no reason to expect divergence, but this is an
  expectation, not a verified fact.

## What CI is expected to actually prove

Because this session cannot run the project's own build, **CI is the
first real compiler** for every C++ file in this PR. The PR is pushed and
CI is watched for real; any compile error, lint failure, or test failure
CI reports against the code in this PR is treated as a real bug and fixed
with a real commit, per the repo's own CI-repair policy. This document
will not claim a CI status that wasn't actually observed — see the PR
description / final report for the true, current CI state at hand-off
time.

One failure observed during this PR's CI runs was **not** a code bug:
`Build - Docker / Image Build` failed with
`Error response from daemon: ... registry-1.docker.io ... 502 Bad Gateway`
while the `docker/setup-buildx-action` step was pulling the
`moby/buildkit` builder image itself, before this PR's `Dockerfile` was
even reached. That is a transient upstream Docker Hub registry error, not
something a source change can fix. The automation account pushing this
PR does not hold `actions:write` (re-running a specific failed job via
the API returns `403 Resource not accessible by integration`), so the
only retry lever available here is a new commit, which starts a fresh
workflow run and gives the same job a new attempt.
