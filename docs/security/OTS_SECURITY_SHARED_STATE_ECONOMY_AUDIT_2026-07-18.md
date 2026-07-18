# OTS Security Audit Continuation — Multichannel Shared State and Exactly-Once Economy

Date: 2026-07-18

Task: `CAN-20260718-ots-security-shared-state-economy-audit`

Draft PR: #526

## Scope and baseline

This document continues the durable OTS security audit from:

- `docs/security/MYAAC_CANARY_SECURITY_AUDIT_2026-07-17.md`
- `docs/security/OTS_SECURITY_AUDIT_HANDOVER_2026-07-18.md`

It does not restart completed MyAAC/login-stack work and does not reopen previously rejected hypotheses without new evidence.

Writable repository: `blakinio/canary`.

Evidence-only/read-only repositories remain `opentibiabr/canary`, `opentibiabr/login-server`, `slawkens/myaac`, `opentibiabr/otclient`, `opentibiabr/remeres-map-editor`, and `opentibiabr/client-editor`.

Exact source baseline for source findings in this pass:

- `blakinio/canary@d9c967d6e9b778da11a206d134d559f38ec1b8c8`

Local shell Git preflight could not be completed because the disposable shell had no existing checkout and could not resolve `github.com`. Live GitHub state and source content were revalidated through the authenticated GitHub connector. No public or third-party deployment was scanned or tested.

## Evidence-state contract

- `PROVEN` — directly confirmed in current code or deterministic source-level proof.
- `DYNAMICALLY CONFIRMED` — reproduced in an isolated runtime/harness.
- `DERIVED` — strongly follows from code composition but lacks complete runtime proof.
- `CONFIGURATION-DEPENDENT` — impact depends on deployment/configuration behavior.
- `CANDIDATE` — suspicious path still requiring call-chain or runtime proof.
- `UNKNOWN` — insufficient evidence.
- `REJECTED` / `FALSE POSITIVE` — hypothesis tested and rejected.

---

## Shared/global state inventory — continuation checkpoint

| Surface | Scope | Writer/coordination state | Audit state |
|---|---|---|---|
| `players_online` | global, keyed only by `player_id` | every channel rebuilds/prunes from process-local players | `PROVEN` — OTS-MC-SS-001 |
| `cluster_sessions` | cluster-global account/player ownership | Redis lease + DB mirror | prior fencing/stale-writer findings preserved |
| `channel_runtime_status` | per-channel row | keyed by `channel_id` | no new finding in this slice |
| `market_offers` / `market_history` | global economy state | accept has no transactional row claim; expiry leader-gated | `PROVEN` partial-fill race — OTS-ECO-MKT-001 |
| `economic_ledger` | global idempotency/audit | wired for selected market paths | overlap-leader duplicate rejected; prior crash wedge remains |
| `guilds.balance` | global per-guild balance | copied into process-local Guild and saved absolutely | `PROVEN` — OTS-ECO-GUILD-001 |
| `players.balance` | global per-player bank balance | direct SQL increments coexist with process-local absolute full saves | `PROVEN` house-refund lost update — OTS-ECO-HOUSE-001 |
| house auction bid state | per-channel world object persisted in `houses` | value effects happen before later `Map::save()` persistence | `PROVEN` crash window — OTS-ECO-HOUSE-002 |
| player inventory ownership | per-player durable rows | trade moves both sides in memory; players save independently | `PROVEN` asymmetric trade persistence — OTS-ECO-TRADE-001 |
| `accounts.coins*` | global per-account balances | single-type add/remove are SELECT -> absolute UPDATE; dual-type remove uses row lock transaction | prior RMW finding narrowed/revalidated |
| `global_storage` | global key/value | daily reward individually leader-gated | wider writers still open |
| `kv_store` | global `key_name` PK | namespace/call-site dependent | raid-reset candidate open |
| boosted creature/boss | global rows | leader gates wired | no new finding in this slice |
| house rows/lists/items | intended per-channel world state | schema/query/save paths remain inconsistently partitioned | prior house-isolation finding revalidated |
| global event framework | starts in every process | only selected jobs individually gated | candidate by concrete event |
| cleanup/highscores/DB optimization/global record | intended singleton where truly global | current runbook still marks wiring incomplete | concrete call-site proof pending |

This is a checkpoint, not a claim that every shared table/KV writer is already exhaustively classified.

---

# Qualified findings

## OTS-MC-SS-001 — `players_online` is destructively rebuilt from process-local state by every channel

- Severity: **MEDIUM**
- Repository/component: `blakinio/canary` / multichannel shared persistence
- Evidence state: **PROVEN**
- Source baseline: `d9c967d6e9b778da11a206d134d559f38ec1b8c8`
- Paths/functions: `src/game/game.cpp` (`Game::start`, `Game::updatePlayersOnline`), `schema.sql` (`players_online`)
- Status: open; remediation not implemented

### Trace and deterministic timeline

Each process schedules `Game::updatePlayersOnline()` and derives IDs only from its local `Game::players`. It inserts local IDs and then deletes every row not in that local set; an empty local set can delete the whole table. The schema has no `channel_id`, writer identity, ownership predicate, or fencing token. The transaction makes one process's rebuild atomic but does not compose channel-local views into a cluster union.

With A local `{A1}` and B local `{B1}`, A can prune B1 and B can then prune A1. Durable state is last-writer-wins rather than `{A1,B1}`.

### Qualification / impact

The table-integrity failure is proven. Current `ProtocolStatus` uses local `Game` statistics rather than this table, so downstream impact depends on external consumers. Any consumer treating `players_online` as cluster authority can falsely classify live characters as offline.

### Remediation direction

Partition by `(channel_id, player_id)` and let each channel prune only its rows, or replace this table as authority with cluster session/runtime state. Add a two-process regression including the zero-local-player case.

### Overlap

Deepens the prior handover's global presence/shared-state finding.

---

## OTS-ECO-MKT-001 — concurrent partial market fills can over-consume one stale offer snapshot

- Severity: **HIGH**
- Repository/component: `blakinio/canary` / market economy
- Evidence state: **PROVEN**
- Source baseline: `d9c967d6e9b778da11a206d134d559f38ec1b8c8`
- Paths/functions: `src/game/game.cpp::Game::playerAcceptMarketOffer`, `src/io/iomarket.cpp::{getOfferByCounter,acceptOffer,deleteOffer}`, `schema.sql::market_offers`
- Status: open; priority dynamic proof recommended

### Trace and deterministic timeline

`getOfferByCounter()` performs a plain read; no row claim/lock is acquired. `playerAcceptMarketOffer()` validates against the local `offer.amount`, performs BUY/SELL value effects and history work, and only then mutates the offer. Partial acceptance executes `UPDATE market_offers SET amount = amount - ? WHERE id = ?`, without `amount >= ?`, affected-row ownership proof, or a transaction coupling the claim with effects.

Offer amount `100`: A reads `100` and accepts `60`; B reads `100` and also accepts `60`; both perform value effects before final durable decrements. Thus `120` units can be processed from a `100`-unit offer before the second persistence result can reject or reconcile anything. Exact unsigned-underflow DB behavior is configuration-dependent; the over-consumption window is not.

A related exact-fill race exists when two channels each accept `50` from a `100` snapshot: both local copies can choose the partial-update branch rather than deleting an exhausted offer.

### Impact

Economy duplication/overpayment or unreconciled market state, potentially involving items, coins, or gold-equivalent credit.

### Remediation direction

Durably claim quantity before irreversible effects, using a conditional atomic decrement requiring exactly one affected row or a row-locked transaction with durable operation identity and explicit recovery. Add deterministic two-process partial-fill coverage.

### Overlap

Concrete partial-fill specialization of the prior market double-accept class.

---

## OTS-ECO-GUILD-001 — process-local guild balances plus absolute saves permit multichannel double-spend

- Severity: **HIGH**
- Repository/component: `blakinio/canary` / guild bank
- Evidence state: **PROVEN**
- Source baseline: `d9c967d6e9b778da11a206d134d559f38ec1b8c8`
- Paths/functions: `schema.sql::guilds.balance`, `src/io/ioguild.cpp::{loadGuild,saveGuild}`, `Guild::bankBalance`, `src/game/bank/bank.cpp`
- Status: revalidated/deepened existing finding

### Trace and deterministic timeline

One global `guilds.balance` is loaded into process-local `Guild::bankBalance`. `Bank::hasBalance()` / `debit()` authorize against that snapshot, while `IOGuild::saveGuild()` later writes an absolute balance. No CAS/version/conditional decrement/fencing protects the global value.

Durable balance `100`: A loads `100`, B loads `100`, each spends `80`, each local balance becomes `20`, both effects are accepted, and later both save `20`. Durable balance is `20` although `160` was paid out.

### Remediation direction

Authorize/debit at the durable DB boundary with conditional atomic mutation and transactionally couple the corresponding effect. Prevent stale absolute guild-balance saves from overwriting newer global state.

---

## OTS-ECO-HOUSE-001 — cross-channel house-auction refund can be erased by the remote bidder's later full save

- Severity: **HIGH**
- Repository/component: `blakinio/canary` / house auction + player bank persistence
- Evidence state: **PROVEN**
- Source baseline: `d9c967d6e9b778da11a206d134d559f38ec1b8c8`
- Paths/functions: `Game::playerCyclopediaHouseBid`, `Game::processBankAuction`, `IOLoginData::increaseBankBalance`, `IOLoginDataSave::savePlayerFirst`
- Status: open; concrete specialization of prior cross-process stale-save class

### Trace and deterministic timeline

When refunding a previous bidder, `processBankAuction()` checks only the current process with `g_game().getPlayerByName()`. A bidder online on another channel is treated as non-local/offline and refunded by durable `balance = balance + refund`. The bidder's actual owning process retains the pre-refund in-memory balance. A later full player save writes `players.balance = player->bankBalance` absolutely, with no CAS/version/fencing check.

V is online on B with local/DB balance `100`. A refunds `50` by direct SQL, making DB `150`; B still holds `100`; B later performs a normal full save and writes `100`, erasing the refund.

### Impact

Normal cross-channel house-auction activity can destroy refunded bank value.

### Remediation direction

Route the mutation to the current record owner through a durable addressed operation, or make bank balance DB-authoritative and exclude it from stale full-save overwrite. Require idempotent identity and ownership/fencing checks.

---

## OTS-ECO-HOUSE-002 — auction money/refund effects precede durable house bid-state persistence

- Severity: **HIGH**
- Repository/component: `blakinio/canary` / house auction crash consistency
- Evidence state: **PROVEN**
- Source baseline: `d9c967d6e9b778da11a206d134d559f38ec1b8c8`
- Paths/functions: `Game::playerCyclopediaHouseBid`, `Game::processBankAuction`, house bid setters in `src/map/house/house.hpp`, `IOMapSerialize::{loadHouseInfo,saveHouseInfo,SaveHouseInfoGuard}`, `Map::save`, `IOLoginData::increaseBankBalance`
- Status: open

### Trace and deterministic timeline

`playerCyclopediaHouseBid()` calls `processBankAuction()` before updating the House object's bidder/bid fields. `processBankAuction()` immediately mutates the new bidder's local bank balance and may immediately persist the previous bidder's refund. House bid setters are only in-memory. Durable house state is written later by `SaveHouseInfoGuard()` when `Map::save()` runs.

DB still records previous bidder P. New bidder N bids; P is durably refunded; in-memory House switches to N; process crashes before a successful `Map::save()`. Restart reloads P as bidder while P's refund remains durable. A later outbid can refund the same hold again, or stale auction settlement can treat P as winner although the hold was already refunded.

### Qualification

The effect-before-house-persistence crash window is proven. Exact new-bidder debit persistence depends on whether that player's state was saved separately before the crash; this finding does not require that assumption.

### Remediation direction

Treat bid transition, reserve/debit, previous-bidder refund, and durable bidder state as one recoverable operation with durable identity and transaction/state-machine or idempotent PENDING/COMMITTED semantics.

---

## OTS-ECO-TRADE-001 — completed two-player trade has no atomic persistence boundary across both inventories

- Severity: **HIGH**
- Repository/component: `blakinio/canary` / player-to-player trade persistence
- Evidence state: **PROVEN**
- Source baseline: `d9c967d6e9b778da11a206d134d559f38ec1b8c8`
- Paths/functions:
  - `src/game/game.cpp` — `Game::playerAcceptTrade`
  - `src/game/scheduling/save_manager.cpp` — `SaveManager::saveAll`, `schedulePlayer`, `doSavePlayer`
  - `src/io/iologindata.cpp` — `IOLoginData::savePlayer`, `savePlayerGuard`
  - `src/io/functions/iologindata_save_player.cpp` — `IOLoginDataSave::savePlayerItem`
- Status: open; isolated crash-injection proof recommended

### Source -> validation -> authorization -> state transition -> persistence -> retry/crash -> impact

1. Once both players accept, `playerAcceptTrade()` moves trade item 1 to the partner and trade item 2 to the player in memory.
2. It marks transfer success and closes trade state, but does not synchronously persist both players as one operation.
3. `IOLoginData::savePlayer()` provides a DB transaction for one player's complete save only.
4. Inventory persistence for one player deletes that player's `player_items` rows and reinserts the current in-memory inventory inside that one-player transaction.
5. `SaveManager::saveAll()` iterates players independently and may save them in parallel; `schedulePlayer()` can also persist one player independently.
6. There is no transaction or durable trade operation spanning both player inventories.

### Deterministic failure timelines

Before trade, item X is durably owned by A and item Y by B. In-memory trade completes: A receives Y and B receives X.

Variant A — duplication:

1. B's post-trade player save commits first, persisting X in B's inventory.
2. A has not yet saved, so durable A inventory still contains X.
3. Process/server crashes.
4. Restart loads X for both A and B.

Variant B — loss:

1. A's post-trade save commits first, removing X from A and adding Y.
2. B has not yet saved, so durable B inventory still contains Y and does not contain X.
3. Process/server crashes.
4. Restart can leave X absent from both durable inventories while Y appears on both sides, depending on which side committed first and which item is traced.

The core invariant failure is that one logical bilateral exchange is persisted as two independently committing player snapshots.

### Qualification / limitations

Trade itself is local to one Canary process because both parties are represented by live `Player` objects in the same trade state. The finding is crash consistency, not a cross-channel concurrent-trade claim. No crash-injection runtime proof was executed in this pass.

### Impact

A crash during asymmetric persistence can duplicate or destroy high-value traded items.

### Remediation direction

Persist completed trade as one durable operation: either transactionally save the affected inventory ownership changes for both players together, or introduce a durable trade ledger/state machine with idempotent replay and recovery. A regression harness should force a crash after exactly one side's save commits.

---

# Current-source revalidation of previously preserved findings

## House isolation failures remain current

Evidence state: **PROVEN — existing finding revalidated/deepened**.

Current schema comments intend physical house identity `(channel_id, id)`, but `houses` simultaneously defines `PRIMARY KEY (channel_id, id)` and `UNIQUE(id)`, preventing the same map house ID from existing independently per channel. `IOMapSerialize::loadHouseInfo()` selects all house rows without a channel predicate and resolves only by `houseId`; `SaveHouseInfoGuard()` inserts/upserts house rows without `channel_id`, therefore relying on default channel `1`. `house_lists` has a `channel_id` column but its primary key omits it, save inserts omit it, and cleanup deletes by version without channel partitioning.

This exactly revalidates the prior handover class: schema identity conflicts with intended channel-scoped identity and house/list persistence is not consistently partitioned. It is not assigned a new finding ID here.

`SaveHouseItemsGuard()` also begins by deleting all `tile_store` rows before rebuilding from the current process map. The broader tile-store channel impact remains part of the existing house-isolation class; this continuation does not promote a separate finding without re-tracing the complete current `tile_store` schema/migration contract.

## Single-type account coin RMW remains current; dual-type debit is transactionally guarded

Evidence state: **PROVEN — existing single-type finding revalidated and narrowed**.

`Account::addCoins(type, amount)` and `Account::removeCoins(type, amount)` call `getCoins()`, then `setCoins()` with an absolute new value. `AccountRepositoryDB::getCoins()` is a plain SELECT and `setCoins()` is an absolute UPDATE. Two concurrent single-type mutations can therefore read the same balance and overwrite one another.

Examples:

- balance `100`, concurrent `+50` and `+50` can both write `150`, losing one credit;
- balance `100`, two concurrent single-type `-80` checks can both pass and both write `20`, allowing two logical debits/effects against one starting balance.

Coin transaction history is registered after the balance UPDATE in these single-type methods and registration failure is only logged by the void helper, so balance/history can diverge.

By contrast, `Account::removeCoins(primaryType, secondaryType, ...)` delegates to `AccountRepositoryDB::removeCoins()`, which uses a rollback-on-failure DB transaction, `SELECT ... FOR UPDATE`, one combined balance check, one update, and transaction-history inserts inside that transaction. The hypothesis that this dual-type path has the same unlocked RMW race is rejected below.

## Bank transfer crash consistency remains current

Evidence state: **PROVEN — existing finding revalidated**.

`Bank::transferTo()` applies source debit and destination credit to process-local bankable objects. Player persistence remains one transaction per player, and SaveManager can save players independently/parallel. Therefore a bilateral transfer still lacks one durable atomic boundary across both player balances; asymmetric commit before a crash can persist only the debit or only the credit. This is the previously preserved bank-transfer crash-consistency class, not a new finding ID.

## GameStore effect/delivery before final coin debit

Evidence state: **PROVEN — existing finding revalidated**.

`data/libs/gamestore/parsers.lua` performs `GameStore.process*Purchase(...)` effects before `player:makeCoinTransaction(offer)`. `data/libs/gamestore/player.lua` removes coins and writes history afterward; EXP-boost count KV is also mutated before coin removal. The prior effect-before-debit crash/failure window remains current.

## Transferable coin transfer credits receiver before checked sender debit

Evidence state: **PROVEN — existing finding revalidated**.

`parseTransferableCoins` checks sender balance, directly increments receiver `accounts.coins_transferable`, then calls sender removal. Receiver credit is not transactionally coupled to a proven sender debit.

## Market expiry PENDING crash-recovery wedge

Evidence state: **PROVEN — existing finding revalidated**.

Expiry inserts a deterministic `economic_ledger` PENDING row, moves/removes the active offer, then performs refund/delivery and commits the ledger. A crash after the offer transition can leave PENDING with no active offer; retry reuses the same UUID and duplicate insertion fails closed, so automatic effect replay does not occur.

---

# Rejected hypotheses

## OTS-MC-JOB-RJ-001 — `market.expire` leader loss mid-run alone duplicates the same expiry effect

- Evidence state: **REJECTED**

The leader check is not fenced through asynchronous result mutation, so overlapping old/new leaders are possible in principle. However each offer expiry derives the same deterministic `economic_ledger.transaction_uuid`; it is the primary key and `beginPending()` fails closed on the second insert. Two workers cannot both pass the per-offer ledger gate and both apply the effect.

This rejection is narrow and does not reject the separate PENDING crash-recovery wedge.

## OTS-ECO-COIN-RJ-001 — dual-type `Account::removeCoins(primary, secondary)` has the same unlocked RMW race as single-type coin removal

- Evidence state: **REJECTED / FALSE POSITIVE**
- Source baseline: `d9c967d6e9b778da11a206d134d559f38ec1b8c8`

The current dual-type repository path executes inside `DBTransaction::executeWithinTransactionRollbackOnFailure`, obtains the account row with `SELECT ... FOR UPDATE`, checks the combined balance after taking the row lock, updates both coin columns, and records non-empty-detail transaction entries before commit. Concurrent calls serialize on the row lock.

This does not make all account-coin mutations safe: single-type add/remove still use unlocked read -> absolute write and remain in scope.

---

# Candidates / unknowns requiring continuation

## OTS-MC-SS-C01 — global server record writer race

Evidence state: **CANDIDATE**.

Known: `server_config` has one global `players_record`; every process loads a process-local record cache; the multichannel runbook still classifies global server record handling as unwired singleton work.

Missing: exact current `Game::loadPlayersRecord()` / `Game::checkPlayersRecord()` implementation and persistence predicate, and proof whether writers can lower/overwrite a record or merely compute a per-channel rather than cluster-wide peak.

## OTS-MC-SS-C02 — raid daily-counter KV reset from every channel global-server-save event

Evidence state: **CANDIDATE**.

Known: daily-reward reset is individually leader-gated; the same global-server-save function resets each `Raid.registry` `checks-today` / `last-check-date` KV without that gate; the global-event framework starts in every process.

Missing: exact `raid.kv` namespace/backing persistence and a concrete reset/increment race impact.

## OTS-MC-SS-C03 — remaining unwired global-event / cleanup / highscore / DB-optimization jobs

Evidence state: **UNKNOWN / CANDIDATE by individual job**.

The runbook warning is not enough to manufacture findings. Each concrete scheduler still needs classification by data scope, writer count, ownership, fencing, transactions, retries and stale-writer behavior.

## Exactly-once flows still open

- depot/inbox/stash handoff beyond already preserved mail findings;
- additional house transfer/settlement ordering;
- remaining account-coin call sites beyond the core Account API;
- MyAAC premium-point paid-operation races not re-traced in this slice.

---

# Evidence-state index

## PROVEN

- `OTS-MC-SS-001` — destructive multiwriter rebuild of global `players_online`.
- `OTS-ECO-MKT-001` — concurrent partial market over-consumption from stale offer snapshots.
- `OTS-ECO-GUILD-001` — guild-bank stale snapshot/absolute-save double spend; existing class revalidated.
- `OTS-ECO-HOUSE-001` — cross-channel house-auction refund can be erased by remote bidder's stale full save.
- `OTS-ECO-HOUSE-002` — auction money/refund effects precede durable house bid-state persistence.
- `OTS-ECO-TRADE-001` — bilateral trade is persisted as independently committing player snapshots, enabling crash-time duplication/loss.
- Existing house-isolation class revalidated with current schema/load/save/list paths.
- Existing single-type account coin RMW class revalidated and narrowed.
- Existing bank-transfer crash-consistency class revalidated.
- Existing GameStore effect-before-debit path revalidated.
- Existing transferable-coin receiver-credit-before-sender-debit path revalidated.
- Existing market-expiry PENDING crash-recovery wedge revalidated.

## DYNAMICALLY CONFIRMED

- None added in this pass.

## DERIVED

- No standalone finding promoted solely from framework/runbook composition.

## CONFIGURATION-DEPENDENT

- Exact DB outcome of a market partial-fill decrement that would underflow an unsigned column; over-consumption does not depend on it.
- Downstream operational impact of corrupted `players_online` depends on table consumers.

## CANDIDATE

- `OTS-MC-SS-C01` — global server record writer behavior.
- `OTS-MC-SS-C02` — raid daily-counter KV reset.
- `OTS-MC-SS-C03` — concrete cleanup/highscore/DB-optimization/global-event jobs pending source proof.

## UNKNOWN

- Exhaustive repository-wide shared-state writer inventory is not complete.
- Remaining depot/inbox/stash and house-transfer/settlement exactly-once flows are not fully traced.

## REJECTED / FALSE POSITIVE

- `OTS-MC-JOB-RJ-001` — overlapping `market.expire` leaders alone cannot both apply the same expiry effect because deterministic ledger-PK insertion rejects the second execution.
- `OTS-ECO-COIN-RJ-001` — dual-type coin debit is not affected by the same unlocked RMW race as single-type coin add/remove; it is row-locked and transactional at the current baseline.
- Prior durable handover rejected hypotheses remain closed absent new evidence.

---

# Dynamic validation status

No dynamic race/crash proof was executed in this slice.

Reason:

- no existing local checkout was available in the disposable shell;
- the shell could not resolve `github.com`, preventing a fresh local clone/fetch;
- public/third-party deployment testing is explicitly out of scope.

Priority isolated harness scenarios:

1. two-process market partial overfill;
2. cancel-versus-accept;
3. mail retry duplication;
4. stale persistent save after ownership loss;
5. guild-bank double spend;
6. cross-channel house-auction refund lost update;
7. crash after persisted previous-bidder refund but before house `Map::save()`;
8. crash after exactly one side of a completed player trade is saved;
9. broader cross-channel house persistence corruption.

Target harness: minimum two Canary processes, shared MariaDB, Redis, deterministic synchronization/crash injection, disposable local/container environment.

# Remediation workflow

PR #526 remains evidence-only. No runtime remediation is mixed into this audit continuation.

Each future fix must be a separate bounded task with exact ownership, overlap review, source provenance, narrow design and regression proof.

# Next continuation checkpoint

Continue in this order unless stronger evidence changes priority:

1. finish concrete shared-state writer inventory:
   - `Game::loadPlayersRecord()` / `Game::checkPlayersRecord()`;
   - raid KV backing/reset semantics;
   - cleanup jobs;
   - highscore persistent/shared cache behavior;
   - DB optimization scheduler;
2. continue exactly-once tracing:
   - depot/inbox/stash persistence beyond preserved mail handoff;
   - remaining house transfer/settlement transitions;
   - remaining account coin mutation call sites;
   - MyAAC premium-point paid operations;
3. build isolated two-process race/crash proofs when a local disposable runtime is available.
