# Cross-process DB-row handoff

Design document for a shared, safe mechanism to transfer responsibility for
a persistent record or operation between channel processes, without
concurrent ownership, stale-owner writes, lost updates, silent overwrites,
double execution, or dependence on another channel's local memory.

Audited against `origin/main` @ `e94c9db085f25fbd9d76721fc86ca2d40119e676`
(the tip immediately after PR #305 merged).

## 0. Why this document exists

Two real, independently-discovered bugs in this codebase are the same bug:

- **Mail loss** (`docs/multichannel/ARCHITECTURE.md` §8, `DECISION_MATRIX.md`
  row 2.12): `Mailbox::sendItem` resolves the recipient via
  `g_game().getPlayerByName(receiver, true)`, which only ever checks *this
  process's* in-memory `mappedPlayerNames`. If the recipient is online on a
  different channel, this process has no visibility into that and silently
  falls back to loading a throwaway offline `Player` copy from the DB,
  delivers the item into it, and saves it. The real owning channel's next
  save (`IOLoginDataSave::savePlayerInbox`, confirmed below) does a
  wholesale `DELETE FROM player_inboxitems WHERE player_id = ?` followed by
  re-inserting *only what is currently in that process's live in-memory
  tree* — which never learned about the mail item — silently erasing it.
- **House double ownership** (`ARCHITECTURE.md` §7): `House::setOwner`
  correctly moves the `account_house_ownership` mirror row to the new house,
  but never revokes the *actual* `houses.owner` column of whatever other
  house the account previously owned, if that house lives on a different
  channel. The owning channel's own in-memory `House` object and DB row are
  never touched — genuine double ownership, not just a stale mirror.

Both bugs have the identical shape: **a process wants to mutate a record
that a *different, live* process currently has cached in memory and is
responsible for persisting.** A direct DB write from the wrong process
either gets silently reverted by the right process's next save (mail), or
desyncs the right process's cache from the DB until its next reload
(house). Building three independent local patches for mail, house, and the
future `DIRTY`-session admin tool would produce three variations of the
same race with three different edge cases — the explicit reason this
document exists before any of those three are touched again.

## 1. Audit: what already exists and what is reused

Confirmed by reading current source, not assumed from documentation:

| Concern | Existing mechanism | File | Reused as-is? |
|---|---|---|---|
| Redis atomic lease + monotonic fencing token, keyed by an arbitrary string | `IRedisClient::acquireLease/renewLease/releaseLease/peekFencingToken` + `acquire.lua`/`renew.lua`/`release.lua` | `src/game/multichannel/redis_client.hpp`, `redis_scripts/` | **Yes** — already generalized once (`ClusterSessionManager` keys by `cluster:session:<accountId>`, `ClusterLeaderElection` keys by `cluster:job:<jobName>` — same primitive, different key namespace). No new Redis script needed. |
| "Which channel currently has this player's live session" | `cluster_sessions` DB table (`PRIMARY KEY(account_id)`, `UNIQUE(player_id)`, `fencing_token`, `status`) + `multichannel::findOnlineChannelForPlayer(playerId)` | `schema.sql`, `cluster_session_lookup.hpp/.cpp` | **Yes** — this is exactly "who owns this player record right now," already correct, already tested (Phase 8, real MariaDB). Not duplicated. |
| "Which channel currently has this house's live representation" | `houses.channel_id` (static, part of the composite `(channel_id, id)` identity, §2.2) | `schema.sql` | **Yes** — a house's owning channel is fixed routing metadata, not a lease; no new lookup needed, just read the column. |
| Is the owning channel's process actually alive right now | `ChannelRuntimeRegistry` heartbeat (fail-closed, local staleness cutoff) | `channel_runtime_registry.hpp` | **Yes** — used to decide whether a pending operation can be expected to drain soon or should surface as a stuck/needs-attention condition. |
| "Pending until the right process consumes it" pattern | `channel_switch_audit` with nullable `consumed_at` (added migration 61): the origin channel writes a row, the *target* channel's own login flow finds the still-unconsumed row and calls `markConsumed` | `channel_switch_audit_store.hpp/.cpp` | **Generalized**, not copied — this is the one PR in this codebase's history that already solved "handoff to whichever process is about to become responsible," but only for a single one-shot value (a position) consumed by a single known future event (a login to a known target channel). Mail/house need a *repeatable*, *typed*, *addressed-by-current-owner* version of the same idea — see §5. |
| Idempotency key / replay rejection via a `CHAR(36)` primary key | `economic_ledger.transaction_uuid`, `mail_delivery_audit.transaction_uuid` | `schema.sql`, `economic_ledger_store.*`, `economic_ledger_id.*` | **Yes** — `multichannel::computeDeterministicLedgerUuid` is pure/dependency-free and already proven; the new mechanism's idempotency key follows the identical shape and, where a natural one-shot key exists, the identical deterministic-derivation approach. |
| Periodic per-channel background cycle | `g_dispatcher().cycleEvent(...)`, already driving `Game::renewClusterSessions()` (session lease renewal + heartbeat publish) | `game.cpp` (`Game::init`) | **Yes** — the new mechanism's "check my own pending inbox" sweep is added to the *same* existing cycle, not a second scheduler. |
| A record's item-level attribute serialization, independent of a whole-player save | `Item::serializeAttr(PropWriteStream&)` / `Item::unserializeAttr(PropStream&)`, already used per-item inside `IOLoginDataSave::saveItems` | `src/items/item.hpp`, `src/io/functions/iologindata_save_player.cpp` | **Yes** — reused to serialize a single mailed item's attributes into the pending-operation payload; not a new serialization format. |

**What does not already exist and is genuinely new:** a durable,
typed, addressed, retry-safe **command inbox** that lets one process
enqueue an operation targeting a record it does not currently own, and
lets whichever process *does* currently own that record apply it safely
through its own live in-memory state and its own existing save pipeline —
never through a blind cross-process DB write. This is the one new piece
built by this design (§5).

**A precondition confirmed by direct source reading, not assumption:**
`IOLoginDataSave::savePlayerInbox` and `savePlayerItem` both do
`DELETE FROM <table> WHERE player_id = ?` followed by a full re-insert of
whatever is currently in the live in-memory tree. This is a *replace*, not
a *merge* — which is exactly why a direct DB `INSERT` into
`player_inboxitems` for a player who is online on another channel does not
work as a fix: that channel's own very next save deletes it. **The mailed
item can only durably reach the recipient by being physically present in
that recipient's own process's in-memory `Inbox` container at the moment
that process next saves them.** This single fact is why the chosen
mechanism (§4) must deliver the *operation* to the right *process*, not
attempt a cleverer direct DB write.

## 2. Requirements recap (binding)

- No concurrent ownership of a record.
- No write by a process that is no longer the current owner.
- No lost update, no silent overwrite.
- No double execution of the same operation on retry/crash/reconnect.
- No process may act as if it owns a record just because it is the one
  that happens to be running the code right now.
- Fail-closed on any uncertainty about current ownership.
- Recoverable after crash, distinguishing not-started / started /
  committed / committed-but-unconfirmed / abandoned / needs-admin.
- Does not break single-channel mode; can be no-op there.

## 3. Variant comparison

| # | Variant | Pros | Risks | Crash behavior | Partition behavior | Testability | Impact on existing code |
|---|---|---|---|---|---|---|---|
| 1 | **DB-only row lease** (a `lease_owner`/`lease_expires_at` column, acquired via `UPDATE ... WHERE lease_expires_at < NOW()`) | No Redis dependency; simple; DB is already the durability floor | Racy without `SELECT ... FOR UPDATE` or a CAS-shaped `UPDATE`; polling-based renewal is chatty; no delivery mechanism — only tells you who owns something, not how to get an operation to them | Survives crash (DB persists); but a crashed owner's lease just sits until TTL expiry — no way to know if it crashed mid-write | Survives partition (single source of truth); but during a DB-only partition from the true owner, nothing can proceed | High — trivial to unit test against a real or in-memory DB | None — read-only building block only |
| 2 | **Redis lease + DB fencing token** | Already implemented, tested, and running in production for sessions and job leadership (`ClusterSessionManager`, `ClusterLeaderElection`); fast; monotonic fencing survives Redis restarts (`INCR`-backed) | Redis outage stops new acquisitions (already an accepted, documented fail-closed behavior elsewhere in this codebase); still only an ownership primitive, not a delivery mechanism | Fail-closed already proven (§10 of `ARCHITECTURE.md`) | Fail-closed already proven | High — `FakeRedisClient` + real `redis-server` harnesses already exist and are reused, not rebuilt | None if reused as-is for the ownership question it already answers (player sessions); zero new Redis code needed |
| 3 | **DB advisory lock** (`GET_LOCK`/`SELECT ... FOR UPDATE`) | Strong, DB-native mutual exclusion for a short critical section | Connection-scoped (MySQL `GET_LOCK` ties the lock to the *connection*, not the logical process — this project's `Database` wrapper does not guarantee one persistent connection per logical actor); not durable across a connection drop; no cross-process addressing | A dropped connection silently releases the lock — cannot distinguish "still working" from "crashed" | Behaves unpredictably under partition (depends on which side keeps the connection) | Medium — needs a real MySQL/MariaDB connection to test meaningfully, not just logic | Would require auditing every DB connection-pooling assumption in `Database` — out of proportion to the problem |
| 4 | **Optimistic concurrency via version/CAS** (`UPDATE ... SET ... WHERE version = ?`) | Simple, well-understood, no separate lock table; naturally rejects a stale writer (`affected_rows = 0` disambiguates "stale" from "gone") | On its own, does not tell a process *whether* to attempt the write in the first place, nor deliver the write to the correct process — only guards a write already decided to happen | Crash before the `UPDATE` leaves the previous, still-consistent state; crash after is durable | Survives partition at the DB layer; a partitioned stale writer's `UPDATE` simply affects 0 rows once connectivity returns | High | Complements, does not replace, an ownership/routing layer |
| 5 | **Dedicated ownership/handoff table** (generalization of `cluster_sessions`) | Single authoritative place to answer "who owns record X right now"; already the *exact* shape of `cluster_sessions` for players and `houses.channel_id` for houses | A brand-new generic table duplicating `cluster_sessions`' job for players would be a second source of truth for the same fact — explicitly against this project's own "one authoritative representation" precedent (`DECISION_MATRIX.md`'s own reasoning for *not* building two session-lock tables) | N/A on its own (ownership state, not operation state) | N/A on its own | High | None if *reused* (players via `cluster_sessions`, houses via `houses.channel_id`) rather than duplicated |
| 6 | **Transactional outbox/inbox for inter-process operations** | The only variant that actually *delivers* an operation to the correct owning process, rather than just answering who owns what; naturally idempotent via a `PRIMARY KEY` idempotency column (exact precedent: `economic_ledger.transaction_uuid`); naturally recoverable (row status *is* the recovery state); already has a proven, narrower precedent in this codebase (`channel_switch_audit`'s `consumed_at`) | Adds one new table and one new sweep loop; requires every consumer to define an "apply" handler | A stuck/never-owned record (crashed channel with no heartcoming heartbeat) leaves rows `PENDING` indefinitely unless surfaced — must be observable (§11), not silently ignored | The failure mode *is* "stays `PENDING`, retried automatically once the true owner is running again" — this is the correct, intended crash behavior, not a bug | The failure mode *is* "stays `PENDING`, retried once connectivity returns" — same reasoning | High — pure DB logic, a `record_kind` → handler dispatch, and idempotency; fully unit-testable against `FakeClusterSessionRepository`-style fakes and a real MariaDB, same methodology as every prior phase | New table, new sweep call site in the existing `renewClusterSessions` cycle, new per-consumer "apply" function — additive, no existing call site changed |

### Why not "just" any single variant

- **Not #1/#3 alone**: neither actually gets an operation to the process
  that needs to run it — they only ever answer "who owns X," never "how do
  I make X happen once the right process is available." Building the mail
  fix on top of #1/#3 alone would still need a second mechanism for
  delivery, which is exactly variant #6.
- **Not #2 alone**: already reused (unchanged) as the *fast, live* answer
  to "who owns this player's session right now" — but Redis TTL-based
  leases are the wrong tool for "this operation must eventually be applied
  exactly once, even if Redis is down for hours." A pending mail item must
  not be lost just because Redis is unreachable; it must sit safely in the
  DB and wait. Making the new command inbox Redis-*independent* is a
  deliberate design choice (§4), not an oversight.
- **Not #4/#5 alone**: necessary building blocks (idempotency guard,
  ownership lookup) but neither, alone, moves an operation to the correct
  process.
- **#6, built on top of the *already-existing* #2 (session ownership) and
  #5 (house's static `channel_id`)**, using #4-style idempotent,
  fencing-checked application: this is the chosen mechanism. It is
  presented as one coherent design in §4-§9, not three independent pieces,
  because its only genuinely new component is the command inbox itself —
  everything it needs to know about *current ownership* already exists and
  is reused unmodified.

## 4. Chosen mechanism: `ClusterRecordHandoff`

One new DB table (`cluster_pending_operations`), one new store class pair
(`ClusterPendingOperationStore` for the DB layer,
`ClusterRecordHandoff` for the ownership-resolution + apply-or-defer
orchestration), reusing `cluster_sessions`/`findOnlineChannelForPlayer` and
`houses.channel_id` for ownership, and the existing `g_dispatcher()
.cycleEvent` cycle for the sweep.

### 4.1 Ownership model

Ownership of a record is **resolved on demand**, never stored redundantly
by the new mechanism itself:

```cpp
enum class ClusterRecordKind : uint8_t {
    PlayerInbox, // owner = whichever channel currently has this player's
                 // live session, per cluster_sessions.status = 'ONLINE'
    House,       // owner = houses.channel_id (static routing, always known)
};

struct ClusterRecordOwnership {
    bool ownedByAnyChannel = false; // false only for PlayerInbox: a fully
                                     // offline player has no live owner at all
    int32_t ownerChannelId = 0;     // valid only when ownedByAnyChannel
    bool ownerChannelIsThisProcess = false;
};
```

- `PlayerInbox` resolves via the already-existing
  `multichannel::findOnlineChannelForPlayer(playerId)`. `std::nullopt` means
  "not owned by any live process right now" (safe for direct application by
  whichever process picks the operation up, guarded per §6.3).
- `House` resolves via a plain `SELECT channel_id FROM houses WHERE id = ?`
  (or, if this process already has the house loaded, its own in-memory
  `House::getChannelId()` accessor — to be added, trivial). Always has a
  value; the only question is whether that channel's process is currently
  running (§4.4).

No new "owner" column is added to `cluster_sessions` or `houses` — this
reuses the columns that already answer the question.

### 4.2 Identifier fields

| Field | Meaning |
|---|---|
| `operation_id` | `CHAR(36)`, the idempotency key. Random UUID-shaped for one-shot player-initiated actions (mail send); deterministic (`multichannel::computeDeterministicLedgerUuid`-style) for anything with a natural one-shot source key. |
| `record_kind` | `'PLAYER_INBOX'` \| `'HOUSE'` (string, not a closed DB enum, so a future kind is a data value, not a migration — see §12). |
| `record_id` | The target's own id (`player_id` for `PLAYER_INBOX`, `house.id` for `HOUSE`). |
| `record_channel_id` | `NULL` for dynamically-owned kinds (`PLAYER_INBOX`, resolved live); the house's `channel_id` for statically-owned kinds (`HOUSE`) — carried on the row so applying does not require a second lookup and so a row is self-describing for recovery/inspection. |
| `enqueued_by_channel_id` | Which channel created this row — diagnostic, not authoritative. |

There is no separate "instanceId" field on the operation row itself: the
*owner*'s identity for `PLAYER_INBOX` is already carried by
`cluster_sessions.instance_id`/`session_id`/`fencing_token` (read live at
apply time, §4.5), and for `HOUSE` there is exactly one process per
`channel_id` by construction (§3.1 of `ARCHITECTURE.md`), so
`record_channel_id` alone is unambiguous.

### 4.3 Lease and TTL

**Deliberately none, at the operation level.** A `PENDING` row is not
leased or claimed by a would-be applier ahead of time — a process either
(a) determines it is the current owner right now and applies immediately
in the same step, or (b) is not the owner and leaves the row untouched for
the real owner's own next sweep. There is no "I am working on this, don't
touch it" intermediate claim, because:

- Application is a single, fast, in-process operation (mutate an
  in-memory container, no network call) — not a long-running task that
  could benefit from a lease against a competing worker.
- Exactly one process can ever legitimately be the current owner at a
  given instant (guaranteed transitively by `cluster_sessions`' own
  `PRIMARY KEY(account_id)` for players, and by construction for houses) —
  so there is no genuine multi-worker race to arbitrate with a lease.

This is why the mechanism does not need a new Redis lease: the *existing*
session lease (players) or static partitioning (houses) already prevents
two processes from both believing they are the current owner
simultaneously. A TTL exists only at the **staleness/attention** level
(§11): a row `PENDING` for longer than a configurable threshold is surfaced
as needing attention, not auto-expired or auto-abandoned.

### 4.4 Fencing / monotonic version

- **`PLAYER_INBOX`**: fencing is not reimplemented — it is the *existing*
  `cluster_sessions.fencing_token`, issued by the *existing* Redis
  `acquireLease` path. The apply-time check (§4.5) is: "is this player
  still present in `ClusterRuntime`'s own tracked-sessions map right now" —
  `ClusterRuntime::getTrackedSessionInfo(accountId)` already exists and
  already reflects exactly this, because a relog/channel-switch on another
  process removes the player from *this* process's `players` map (existing,
  unrelated-to-this-design behavior) before any other process could
  legitimately take over. No new token is minted; the existing one is
  read.
- **`HOUSE`**: fencing is structural, not token-based — only the process
  whose own `ChannelContext::getChannelId()` equals the row's
  `record_channel_id` will ever attempt to apply it, and that process's
  main dispatcher thread is already the sole writer of its own in-memory
  `House` objects (existing, unrelated-to-this-design invariant). A stale
  writer cannot exist because no other process ever attempts to apply a
  `HOUSE` row that is not addressed to its own channel id.
- **Rejection of a stale attempt**: encoded as "the apply-time ownership
  check in §4.5 returns not-owner," not as a separate DB comparison — the
  row simply stays `PENDING` and is picked up by whichever process the
  *next* ownership check identifies as current.

### 4.5 Acquire / renew / transfer / release, mapped to this mechanism's actual verbs

The spec's generic lifecycle maps onto this mechanism as:

- **Acquire** ≈ *enqueue*: `ClusterPendingOperationStore::enqueue(...)`
  inserts a `PENDING` row. Always succeeds for a fresh `operation_id`;
  replays with the same `operation_id` are rejected by the `PRIMARY KEY`
  (idempotent no-op, matching `economic_ledger.beginPending`'s contract
  exactly).
- **Renew** ≈ *no-op by design* (§4.3) — there is nothing to renew because
  nothing is leased ahead of time.
- **Transfer** ≈ *re-resolution*: the next sweep (this process's or the new
  owner's, after a relog/channel-switch) simply re-resolves current
  ownership (§4.1) and either applies or continues deferring. No explicit
  "transfer" call exists or is needed — the row is passive; only the
  *reader's* conclusion about who owns the target changes.
- **Release** ≈ *terminal status write*: `markApplied`/`markFailed`/
  `markAbandoned`, each a single `UPDATE ... WHERE operation_id = ? AND
  status = 'PENDING'` (guards against a double-apply race between this
  process's own two sweep passes, belt-and-suspenders alongside the
  ownership check already preventing two *different* processes from both
  applying).

### 4.6 Crash behavior

| Crash point | Resulting row state | Recovery |
|---|---|---|
| After `enqueue`, before any apply attempt | `PENDING` | Normal — next sweep (any process) picks it up. |
| Applier crashes after mutating in-memory state, before `markApplied` commits | `PENDING`, but the in-memory mutation is lost with the crashed process (never saved) | Row is still `PENDING` — the *next* time a process determines it owns the record (could be the same process after restart, since a restart makes it re-acquire the session/still own the house), it re-applies from scratch. Idempotent because the row's own `operation_id` guards the *store*-level effect (§4.7 — the mutation itself must be re-derivable from the row, not from transient state), not because the in-memory mutation itself is retried blindly. |
| Applier crashes after `markApplied` commits, before the record's own next natural save | Row is `APPLIED`; the in-memory mutation may or may not have been part of a save yet | This is the one honestly-accepted residual window, identical in shape to the market-expiry `PENDING`→`COMMITTED` gap already documented in `ARCHITECTURE.md` §8 ("makes a crash mid-expiry detectable and auditable... does not yet make the sequence atomic") — see §11 for how this is made *observable* rather than silently swallowed. |
| Enqueuing process crashes before its own transaction commits | No row exists at all | Nothing was promised yet — safe. The original triggering action (e.g. a `sendItem` call) is not retried automatically; this matches existing behavior (a crash mid-`sendItem` today already has no retry either). |

### 4.7 Redis outage

**No effect on this mechanism.** `cluster_pending_operations` is pure DB
state; enqueue and apply are pure DB operations. The only place Redis
enters at all is the pre-existing `PLAYER_INBOX` ownership question via
`cluster_sessions`, and that table is itself the DB-layer defense-in-depth
that already keeps working when Redis is down (per `ARCHITECTURE.md` §5's
existing, unchanged fail-closed design) — a Redis outage degrades new
*session acquisition*, not the ability to read who is *already* recorded
online, which is all this mechanism needs.

### 4.8 DB outage

Fail-closed by construction: no DB, no `enqueue`, no `apply`, no sweep
progress. Nothing is lost (nothing was durably promised), and nothing is
double-applied (nothing could have been marked `APPLIED` without the DB).
This matches every other DB-dependent mechanism already in this codebase.

### 4.9 Network partition

A partition between two channel processes (both DB- and Redis-reachable
from each independently, but not from each other in any way that matters —
they only ever communicate *through* the shared DB/Redis, never directly)
is not a distinguished case: the mechanism has no direct process-to-process
communication to partition. The only meaningful partition is
process-to-DB or process-to-Redis, both covered above.

### 4.10 Retry resilience / idempotency key

`operation_id` is the idempotency key end to end, in the exact tradition of
`economic_ledger.transaction_uuid` and `mail_delivery_audit.transaction_uuid`:

- A caller retrying the *same logical* operation (e.g. the client resending
  a mail-send request after a timeout) must derive the *same*
  `operation_id` for the retry to be safely idempotent. Where a natural
  one-shot source key exists (e.g. `channel_switch_audit`'s row id for a
  house-revoke triggered by a specific ownership grant), the deterministic
  derivation is used, matching `EconomicLedgerStore::deterministicUuid`.
  Where no natural one-shot key exists (mail send has no pre-existing
  unique id at the moment of sending — the same gap already identified and
  accepted for `Game::playerCreateMarketOffer` in `ARCHITECTURE.md` §8), a
  fresh random UUID is generated once at the point of the user-initiated
  action and is not regenerated on retry within that same request — i.e.
  idempotency here matches the same boundary as market offer creation, not
  a stronger guarantee that does not exist for it either.

### 4.11 Atomicity

Two DB statements need atomicity guarantees, both narrow and both
achievable with this project's existing `Database` wrapper (no new
transaction infrastructure required, confirmed by reading `database.hpp`):

1. **Enqueue** is a single `INSERT` — atomic by construction (either the
   row exists with `PENDING` status, or it does not exist at all).
2. **Apply for the "no live owner" (`PLAYER_INBOX`, offline) case** needs
   the check-then-apply-then-mark sequence to be atomic against a login
   racing in between the check and the mark. This is the one place this
   design uses variant #3 (DB advisory/row lock) deliberately and
   narrowly: `SELECT status FROM cluster_sessions WHERE player_id = ? FOR
   UPDATE` inside an explicit transaction, re-confirming still not
   `ONLINE` immediately before the direct-apply write, committing the
   in-memory-equivalent DB write (§6.3) and `markApplied` together, then
   releasing the row lock at commit. If the row-lock read shows `ONLINE`
   (a login raced in after the outer ownership check but before this
   transaction), the transaction aborts without applying, and the
   operation stays `PENDING` for the now-online owning channel's own
   sweep to pick up instead — no double-delivery, no loss.
3. **Apply for the "live owner is this process" case** (`PLAYER_INBOX`
   online-here, or `HOUSE` on this channel) does not need a DB transaction
   at all for the mutation itself: it is a single in-process, main-
   dispatcher-thread, in-memory mutation (already inherently atomic — the
   dispatcher is single-threaded for game-state mutation), followed by a
   single `markApplied` `UPDATE`. The *durability* of the mutation itself
   is deferred to that record's own existing, unmodified, already-correct
   save pipeline (§0) — this mechanism's job ends at getting the mutation
   into the right process's memory, exactly once.

### 4.12 Stale-owner detection

Covered by §4.4: a process only ever attempts to apply a row it has *just*
freshly determined, via the live ownership resolution (§4.1), that it
currently owns. There is no cached/stale belief about ownership carried
across sweep cycles — every sweep re-resolves from scratch. A process that
*was* the owner and no longer is simply stops being selected by §4.1 on its
very next sweep; it does not need to be told it lost ownership, because it
never assumed continuity in the first place.

### 4.13 Recovery procedure

Row `status` **is** the recovery state machine (mirrors §11 GM
observability):

| Status | Meaning | Action |
|---|---|---|
| `PENDING` | Not yet applied by anyone | Automatic — every sweep re-attempts ownership resolution and applies if now possible. |
| `APPLIED` | Applied successfully by the identified owner | Terminal, informational only. |
| `FAILED` | The owner attempted to apply and the operation-specific handler reported a definitive failure (e.g. mailbox full) | Terminal — will **not** be retried automatically (retrying a definitively-failed business operation is not safe to assume idempotent at the business level, only at the row level); surfaced for GM/operator visibility (§11). |
| `ABANDONED` | Manually marked by an operator/GM tool (not implemented this PR — see §12) after investigation concluded the operation should not be applied | Terminal, audit trail only. |

A row `PENDING` for longer than `pendingStaleWarningMs` (config, §9) is a
metric/log signal (§11), never an automatic transition to `FAILED` or
`ABANDONED` — silently giving up on a real business operation (an item a
player is owed) is exactly the "don't fix blind" failure mode this whole
document exists to avoid.

## 5. Required DB indexes and constraints

```sql
CREATE TABLE IF NOT EXISTS `cluster_pending_operations` (
    `operation_id` char(36) NOT NULL,
    `record_kind` varchar(32) NOT NULL,
    `record_id` int(11) NOT NULL,
    `record_channel_id` int(11) DEFAULT NULL,
    `operation_type` varchar(64) NOT NULL,
    `payload` mediumtext NOT NULL,
    `status` enum('PENDING','APPLIED','FAILED','ABANDONED') NOT NULL DEFAULT 'PENDING',
    `attempts` int(11) NOT NULL DEFAULT '0',
    `last_error` varchar(255) NOT NULL DEFAULT '',
    `enqueued_by_channel_id` int(11) NOT NULL,
    `created_at` bigint(20) NOT NULL,
    `applied_at` bigint(20) DEFAULT NULL,
    CONSTRAINT `cluster_pending_operations_pk` PRIMARY KEY (`operation_id`),
    INDEX `record_lookup` (`record_kind`, `record_id`, `status`),
    INDEX `status_created_at` (`status`, `created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

- `PRIMARY KEY(operation_id)` is the idempotency constraint — a retried
  `enqueue` with the same id fails the `INSERT` (same contract as
  `economic_ledger.transaction_uuid`), the caller must treat that as
  "already enqueued," not as an error.
- `record_lookup (record_kind, record_id, status)` is the sweep query's
  index: "give me every `PENDING` row for records this process might now
  own." Composite, leftmost-prefix-usable for both "all pending for a
  kind" and "all pending for one specific record."
- `status_created_at (status, created_at)` backs the staleness metric
  (§11) and any future admin listing, without a full table scan as the
  table grows.
- No foreign key to `players`/`houses`: `record_id`'s meaning depends on
  `record_kind` (a polymorphic reference cannot carry a single FK target),
  matching the existing precedent of `channels.temple_town_id` deliberately
  omitting an FK for the same structural reason (see the comment already in
  `schema.sql` next to that column).
- `utf8mb4`, not the `utf8` most other multichannel tables use: `payload`
  may carry a mailed letter's free-text body, which can legitimately
  contain characters outside the `utf8` (3-byte) subset.
- No unbounded scan at startup: this table is never read in bulk at boot
  (unlike, say, a full-table migration); the sweep query is always
  index-bound by `(record_kind, record_id, status)` or `(status,
  created_at)`, never a full scan.

## 6. `record_kind` → apply handler contracts

### 6.1 `PLAYER_INBOX` / `DELIVER_MAIL_ITEM`

`payload` carries: item type id, count, the serialized attribute blob
(`Item::serializeAttr`, hex- or base64-encoded into the `mediumtext`
column — reusing the exact primitive `saveItems` already uses per-item,
not a new format), and, for a written letter, writer/date/text (mirroring
the existing fields `Mailbox::sendItem` already extracts).

Apply, when this process is confirmed to be the current owner (§4.1/§4.5):

1. Reconstruct the `Item` via `Item::CreateItem(itemId, count)` +
   `unserializeAttr`.
2. `internalMoveItem`/direct insertion into the live recipient `Player`'s
   `Inbox` container — the *same* call the already-correct same-channel
   path uses today.
3. If the recipient is online in this process right now, call the existing
   `player->onReceiveMail()` notification (unchanged behavior).
4. `markApplied`.

Apply, when no channel currently owns the record (fully offline recipient),
under the row-lock transaction from §4.11.2:

1. Load a throwaway `Player` copy exactly as `Mailbox::sendItem` does
   today (this part of today's code is *not* buggy for the genuinely-
   offline case).
2. Insert the reconstructed item into its `Inbox`.
3. `g_saveManager().savePlayer(tmpPlayer)`.
4. `markApplied`, all before the row lock (§4.11.2) is released.

### 6.2 `HOUSE` / `REVOKE_HOUSE_OWNER`

`payload` carries: the house id being revoked, the account id the
revocation is scoped to (a defensive check — only revoke if the house's
*current* owner is still that account, since time may have passed between
enqueue and apply and a further, unrelated ownership change may have
already occurred), and the `operation_id` of the *grant* that triggered
this revoke (for audit traceability).

Apply, when this process's `ChannelContext::getChannelId()` matches
`record_channel_id`:

1. Look up the live in-memory `House` object for `record_id` (guaranteed
   present — every channel loads all of its own houses at map load).
2. If `house->getOwnerAccountId()` no longer equals the payload's account
   id, this revoke is stale (something else already changed this house's
   ownership) — `markApplied` anyway (the *goal state* — "this account no
   longer double-owns" — is already true) with a note in `last_error` for
   traceability, not a `FAILED`.
3. Otherwise, call the *existing*, unmodified `house->setOwner(0)` —
   reusing the one real chokepoint every other ownership change already
   goes through (§7 of `ARCHITECTURE.md`), not a parallel write path.
4. `markApplied`.

**Not implemented this PR** (§12 has the migration plan): the *enqueue*
side of `HOUSE`/`REVOKE_HOUSE_OWNER` — i.e. actually detecting at grant
time that the account previously owned a different-channel house and
calling `enqueue` for it. This document's Stage 3 scope is the foundation
only; wiring `House::setOwner` to *produce* this operation is explicitly
deferred (§12), consistent with the task's own "do not implement the house
fix yet" instruction.

### 6.3 Handler registration

A small, closed dispatch table inside `ClusterRecordHandoff`
(`record_kind` + `operation_type` string pair → function pointer/
`std::function`), not a virtual-class-per-kind hierarchy — this project's
established style favors small free functions and explicit dispatch over
speculative polymorphism (see `redisPingFailureError`'s plain `switch` in
`cluster_config_validator.cpp` for the same taste applied to a smaller
case). Adding a new kind/type is a new `case`, not a new inheritance
layer.

## 7. Logging and metrics

No secrets or full item/mail contents in logs (a mailed letter's free-text
body is user content, `payload`'s raw bytes are never logged — only
`operation_id`, `record_kind`, `record_id`, `status`, and error
*categories*, matching the existing project-wide rule already followed by
`RedisPingResult` — the raw hiredis string is logged, but no credential
ever is).

Required diagnostics (per the task's explicit list):

| Diagnostic | Source |
|---|---|
| Current owner of a record | §4.1 resolution, exposed read-only (mirrors `findSessionLockInfo`'s existing GM-command shape) |
| Fencing token / equivalent | For `PLAYER_INBOX`, the live `cluster_sessions.fencing_token` (already exposed via `Game.getPlayerSessionLockInfo`, unchanged); `HOUSE` has none by design (§4.4) |
| Lease age | N/A (§4.3 — no lease); "row age" (`now - created_at`) is the analogous, actually-relevant number, exposed as the staleness metric below |
| Last operation | `operation_type`, `created_at`, `status`, `applied_at` per row — queryable by `record_kind`+`record_id` |
| Idempotency key | `operation_id`, always logged (never sensitive) |
| Recovery state | `status` column value, directly |
| Write-rejection reason | `last_error`, populated on the `FAILED` path and on the stale-revoke `markApplied`-with-note path (§6.2 step 2) |
| Ownership-conflict count | New counter, incremented whenever §4.1 resolves a record to a channel other than this one for a row this process's sweep considered (i.e. "how often do I defer") |
| Post-crash takeover count | New counter, incremented whenever `applied_at IS NULL AND status = 'PENDING'` for a row whose `created_at` predates this process's own startup — a proxy for "how many operations did I inherit from a predecessor" |
| Undelivered/incomplete count | Gauge: `SELECT COUNT(*) FROM cluster_pending_operations WHERE status = 'PENDING' AND created_at < ?` (the staleness threshold), sampled by the same periodic sweep, logged at `warn` when non-zero |

## 8. Error model

No new exception types. Every store method returns a plain `bool`/
`std::optional` success signal, matching every other multichannel DB store
in this codebase (`EconomicLedgerStore`, `ChannelSwitchAuditStore`,
`DbClusterSessionRepository`) — a real DB error and "the operation cannot
proceed right now" are handled identically by the caller (retry on next
sweep), since distinguishing "duplicate key" from "connection lost" at the
call site has never been needed by any existing store in this codebase and
adding it here would be new, untested surface for no behavioral gain.

## 9. Transaction boundaries

- `enqueue`: one `INSERT`, no explicit transaction needed (auto-commit,
  matching every existing store in this codebase).
- Apply when this process is the live owner: no DB transaction around the
  in-memory mutation itself (§4.11.3); `markApplied` is its own
  auto-commit `UPDATE`, executed *after* the in-memory mutation succeeds,
  guarded by `WHERE status = 'PENDING'` so a duplicate sweep pass within
  the same process cannot double-count it.
- Apply when no live owner exists (`PLAYER_INBOX` offline path): one
  explicit transaction spanning the row-lock read, the direct-apply write,
  and `markApplied` together (§4.11.2) — the only place this design uses
  an explicit multi-statement transaction, and narrowly, matching this
  project's existing preference for single-statement auto-commit
  everywhere else (see `House::setOwner`'s own comment explaining why its
  writes are *not* wrapped in a transaction, for the established taste
  this follows).

## 10. Compatibility

- New table only; no existing table's shape changes.
- Entirely inert when `multiChannelEnabled = false`: nothing enqueues a
  `cluster_pending_operations` row in single-channel mode, since
  `findOnlineChannelForPlayer`/the whole multichannel session model does
  not run there — `Mailbox::sendItem`'s existing single-process behavior
  is completely unaffected (§13, PR 2 scope, keeps the existing
  fast-path branch for "recipient found in local `mappedPlayerNames`"
  first, exactly as today).
- The sweep is added to the existing `multiChannelEnabled`-gated
  `renewClusterSessions` cycle (`Game::init`), so it costs nothing and
  runs nothing in single-channel mode.
- Migration (`63.lua`) is purely additive (`CREATE TABLE IF NOT EXISTS`),
  guarded the same way as every migration since `59.lua`.

## 11. Observability / GM surface (design only this PR — see §12)

Mirrors the existing four read-only GM commands (Phase 8/10/12) in shape:
a future `Game.getPendingClusterOperations(recordKind, recordId)` and
`Game.getStalePendingOperationCount()` binding, backed by plain
`SELECT`s against the indexes in §5 — not implemented this PR (no GM
command is requested by this task's scope), but the schema and store
methods are written so that adding them later is call-site wiring only,
the same "primitive now, call site later" split already used successfully
for every prior GM command in this project's history.

## 12. What this PR does NOT implement (migration plan for the deferred consumers)

Per the task's explicit instructions, this document and its accompanying
foundation PR do **not** wire:

- **House double-ownership fix**: the `enqueue` side of §6.2. Migration
  plan: add a check in `House::setOwner`'s grant path (after resolving the
  new owner's `account_id`, before/alongside the existing
  `account_house_ownership` mirror `DELETE`+`INSERT`) that looks up
  whether that account previously held a *different* `(channel_id,
  house_id)` via the mirror row being replaced; if that previous
  `channel_id` differs from this process's own, call
  `ClusterRecordHandoff::enqueue(House, previousHouseId, "REVOKE_HOUSE_OWNER",
  ...)` instead of leaving the other channel's `houses.owner` untouched.
  If the previous house is on *this* channel, no handoff is needed at all —
  call `setOwner(0)` on it directly, exactly as any other same-process
  ownership change already does.
- **`DIRTY` session recovery/admin tooling**: `cluster_sessions.status =
  'DIRTY'` is currently never written by any code path at all (confirmed
  by reading `db_cluster_session_repository.cpp` — it only ever writes
  `'ONLINE'` or deletes the row). Migration plan: (1) wire the *write*
  side first — `ClusterRuntime` should transition a session to `DIRTY`
  (instead of the current silent delete) when it detects a fencing
  conflict or an ungraceful loss it cannot cleanly attribute to a clean
  logout, giving operators something to actually find; (2) build the GM
  recovery tool on top of the *same* `ClusterRecordHandoff` primitive:
  "force-clear a `DIRTY` session" is itself a cross-process operation if
  the session's `channel_id` in the dirty row refers to a *different*,
  possibly-crashed process — the admin action should `enqueue` a
  `PLAYER_SESSION`/`FORCE_CLEAR_DIRTY` operation rather than directly
  `DELETE`-ing the row out from under a process that might still believe
  it owns it, for exactly the same reason direct writes are unsafe
  everywhere else in this document. This needs its own design pass on top
  of this foundation, not a blind extension — left for a follow-up task.
- **Other future consumers** the task names as "potentially other
  operations requiring persistent data ownership transfer" (e.g. bank/
  currency operations, guild leadership transfer) are not scoped or
  designed here; §6.3's dispatch table is built to accept them without
  a schema change, which is the concrete promise this document makes to
  them, not a specific implementation.

## 13. This PR's actual scope (Stage 3 + Stage 4)

- **PR 1 (foundation)**: `cluster_pending_operations` schema (migration
  63), `ClusterPendingOperationStore` (DB layer: `enqueue`/`markApplied`/
  `markFailed`/`markAbandoned`/`findPendingForRecord`/
  `findStalePending`), `ClusterRecordHandoff` (ownership resolution +
  apply-or-defer orchestration + the dispatch table from §6.3, with
  *zero* handlers registered yet — the mail handler is PR 2's job), unit
  and integration tests per §14 below. No existing call site changed.
- **PR 2 (mail-loss fix)**: registers the `PLAYER_INBOX`/
  `DELIVER_MAIL_ITEM` handler (§6.1), changes `Mailbox::sendItem` to
  resolve cross-channel ownership before falling back to the throwaway-
  copy path, adds the sweep call site (piggybacked on
  `Game::renewClusterSessions`'s existing cycle).
- **PR 3 (docs)**: `DECISION_MATRIX.md`/`TEST_PLAN.md` updates, task
  record, the house-ownership and `DIRTY`-session migration plans (§12,
  already written above so PR 3 only needs to *link* to this document,
  not re-derive the plan).

## 14. Test matrix (implemented in PR 1 unless noted)

| # | Scenario | Layer |
|---|---|---|
| 1 | First enqueue of a fresh `operation_id` succeeds | `ClusterPendingOperationStore` unit |
| 2 | Re-`enqueue` of the same `operation_id` is rejected (idempotent no-op) | unit |
| 3 | Ownership resolution: `PLAYER_INBOX` online here / online elsewhere / offline everywhere | `ClusterRecordHandoff` unit against `FakeClusterSessionRepository`-style fake |
| 4 | Ownership resolution: `HOUSE` on this channel / on another channel | unit |
| 5 | Apply succeeds when this process is the resolved owner; row becomes `APPLIED` | unit |
| 6 | Apply is skipped (row stays `PENDING`) when another process is the resolved owner | unit |
| 7 | Two processes' sweeps both consider the same row; exactly one applies (simulated via two `ClusterRecordHandoff` instances against the same fake DB/session state) | unit — mirrors the existing 16-thread `ClusterLeaderElection` race test's spirit, adapted since this mechanism's exclusivity comes from `cluster_sessions`, not a Redis lease |
| 8 | Stale fencing/ownership: a process that believed it owned a `PLAYER_INBOX` record but has since lost the session (per `ClusterRuntime::getTrackedSessionInfo`) refuses to apply | unit |
| 9 | Crash before commit: an `enqueue` that never completes leaves no row (nothing to recover — documents the accepted gap from §4.6) | unit (simulated failure injection) |
| 10 | Crash after commit, before confirmation: a row `APPLIED` with no further mutation is left as-is, not retried, not double-counted | unit |
| 11 | Retry of the same operation after the row is already `APPLIED` is a safe no-op | unit |
| 12 | Redis outage: `PLAYER_INBOX` ownership resolution correctly reports "cannot confirm" (not "offline") when `cluster_sessions`' own Redis-backed fast path is unavailable but the DB table itself is reachable — fail-closed, does not apply | unit, mirrors the existing `RedisOutageClearsPreviouslyFreshSnapshot`-style tests already in this codebase |
| 13 | DB outage: `enqueue`/`apply`/sweep all no-op cleanly, no crash, no partial state | unit (fake returns failure) |
| 14 | Partial Redis/DB failure: Redis says one thing, DB (defense-in-depth) says another — DB wins per the existing, unchanged `cluster_sessions` precedence | unit |
| 15 | Network partition (modeled as: this process cannot reach the DB at all for N sweep cycles, then reconnects) — no operation is lost or double-applied across the gap | unit + real-MariaDB scenario (start/stop a real connection) |
| 16 | Delayed request from a stale owner: a sweep pass that started before a takeover completes its ownership check *after* the takeover — must resolve to "not owner" using the fresh, not cached, state | unit |
| 17 | Clock skew: `created_at`/staleness comparisons use DB-observed or dispatcher-observed monotonic-enough wall time consistently (never a per-process `steady_clock`), matching the existing `multichannel::wallClockMs()` convention audited in the prior phase — explicitly *not* relying on Redis TTL expiry for this mechanism's own correctness (§4.7) | unit + code review |
| 18 | Manual recovery: `markAbandoned` moves a row out of the sweep's consideration set (`record_lookup` index excludes non-`PENDING`) | unit |
| 19 | Single-channel compatibility: with `multiChannelEnabled = false`, no row is ever created and the sweep is never scheduled | unit + code review of the `Game::init` gate |
| 20 | Real MariaDB: `cluster_pending_operations` schema imports cleanly from a fresh `schema.sql`, migration `63.lua` is idempotent (a second run no-ops, matching every prior migration's guard-query convention) | integration, real MariaDB 10.11, same methodology as every prior migration in this series |

PR 2 additionally covers the mail-specific scenarios from the task's own
list (offline→offline, same-channel online, cross-channel online, switch
mid-send, logout mid-send, concurrent sends, retry after timeout,
idempotency-key replay, sender crash, recipient crash, stale-owner
rejection, no loss, no duplication, full mailbox, incomplete-delivery
recovery) — see PR 2's own task record section once implemented.
