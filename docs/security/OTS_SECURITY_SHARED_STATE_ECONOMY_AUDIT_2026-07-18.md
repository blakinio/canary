# OTS Security Audit Continuation — Multichannel Shared State and Exactly-Once Economy

Date: 2026-07-18

Task: `CAN-20260718-ots-security-shared-state-economy-audit`

Draft PR: #526

## Scope and baseline

This document continues:

- `docs/security/MYAAC_CANARY_SECURITY_AUDIT_2026-07-17.md`
- `docs/security/OTS_SECURITY_AUDIT_HANDOVER_2026-07-18.md`

It does not restart completed MyAAC/login-stack work and does not reopen previously rejected hypotheses without new evidence.

Writable repository: `blakinio/canary` only.

Evidence-only/read-only repositories remain:

- `opentibiabr/canary`
- `opentibiabr/login-server`
- `slawkens/myaac`
- `opentibiabr/otclient`
- `opentibiabr/remeres-map-editor`
- `opentibiabr/client-editor`

Exact source baseline for source findings in this pass:

- `blakinio/canary@d9c967d6e9b778da11a206d134d559f38ec1b8c8`

The disposable shell had no existing checkout and could not resolve `github.com`, so local `git status/branch/remote/worktree/fetch` preflight and physical runtime harness work were unavailable. Live GitHub state and source were revalidated through the authenticated GitHub connector. No public or third-party deployment was scanned or tested.

## Evidence-state contract

- `PROVEN` — directly confirmed in current code or deterministic source-level proof.
- `DYNAMICALLY CONFIRMED` — reproduced in an isolated runtime/harness.
- `DERIVED` — strongly follows from code composition but lacks complete E2E proof.
- `CONFIGURATION-DEPENDENT` — impact depends on deployment/configuration behavior.
- `CANDIDATE` — suspicious path still requiring call-chain or runtime proof.
- `UNKNOWN` — insufficient evidence.
- `REJECTED` / `FALSE POSITIVE` — hypothesis checked and rejected.

---

# Shared/global state inventory — continuation checkpoint

| Surface | Data scope | Writer/coordination state | Audit state |
|---|---|---|---|
| `players_online` | global | every channel rebuilds/prunes from process-local players | `PROVEN` — OTS-MC-SS-001 |
| `cluster_sessions` | cluster-global ownership | Redis lease + DB mirror | prior fencing/stale-writer findings preserved |
| `channel_runtime_status` | per-channel | keyed by `channel_id` | no new finding |
| `market_offers` / `market_history` | global economy | accept has no transactional row claim | `PROVEN` — OTS-ECO-MKT-001 |
| market counterparty Player snapshot | global player persistence | `getPlayerByGUID(..., true)` can load stale DB copy of remotely online counterparty | `PROVEN` — OTS-ECO-MKT-002 |
| `economic_ledger` | global idempotency/audit | wired for selected market paths | overlap-leader duplicate rejected; prior crash wedge remains |
| `guilds.balance` | global per-guild balance | process-local snapshot + absolute save | `PROVEN` — OTS-ECO-GUILD-001 |
| `players.balance` | global per-player balance | direct SQL increments coexist with process-local absolute full saves | `PROVEN` — OTS-ECO-HOUSE-001 |
| house auction bid state | per-channel-intended world state | money/refund effects precede later `Map::save()` | `PROVEN` — OTS-ECO-HOUSE-002 |
| house transfer state | per-channel-intended world state | payment/refund and House persistence are separate | `PROVEN` — OTS-ECO-HOUSE-003 |
| bilateral trade inventory | per-player persistent inventory | both sides move in memory; players save independently | `PROVEN` — OTS-ECO-TRADE-001 |
| mail handoff | cluster-global operation + player inbox | source removal, owned delivery, offline delivery and operation status are not one atomic operation | existing `PROVEN` class revalidated |
| `accounts.coins*` | global per-account balance | single-type RMW unlocked; dual-type debit row-locked | existing finding narrowed/revalidated |
| house rows/lists/items | intended per-channel world state | schema/query/save paths inconsistently partitioned | existing house-isolation finding revalidated |
| `global_storage` | global KV | daily reward individually leader-gated | wider writers still open |
| `kv_store` | global `key_name` PK | namespace/call-site dependent | raid-reset candidate open |
| boosted creature/boss | global | leader gates wired | no new finding |
| highscore/query caches | process-local `Game` members observed | persistent/shared writer not proven | `UNKNOWN` shared-state impact |
| global server record | one global DB record + process-local cache | implementation of writer still unresolved | `CANDIDATE` |
| cleanup/DB optimization/global events | mixed | runbook says singleton wiring incomplete | classify concrete jobs before promotion |

This is a continuation checkpoint, not a claim that every shared writer is already exhaustively inventoried.

---

# Qualified findings

## OTS-MC-SS-001 — `players_online` is destructively rebuilt from process-local state by every channel

- ID: `OTS-MC-SS-001`
- Severity: **MEDIUM**
- Affected repository/component: `blakinio/canary` / multichannel shared persistence
- Evidence state: **PROVEN**
- Exact source baseline: `d9c967d6e9b778da11a206d134d559f38ec1b8c8`
- Affected paths/functions:
  - `src/game/game.cpp` — `Game::start`, `Game::updatePlayersOnline`
  - `schema.sql` — `players_online`
- Status: open; evidence only, no remediation in PR #526

### Source-to-impact trace

1. Every process schedules `Game::updatePlayersOnline()`.
2. The function derives IDs only from that process's local `Game::players`.
3. It inserts local IDs and deletes every row not in the local set.
4. A process with zero local players can delete the entire table.
5. `players_online` has no `channel_id`, writer identity, ownership predicate, or fencing token.
6. The transaction makes one local rebuild atomic but does not compose channel-local views into a cluster union.

### Deterministic failure timeline

- A local set: `{A1}`.
- B local set: `{B1}`.
- A inserts A1 and prunes B1.
- B inserts B1 and prunes A1.
- Durable state becomes whichever channel writes last, not `{A1,B1}`.

### Qualification / limitations

Current `ProtocolStatus` uses local `Game` statistics rather than `players_online`; exact downstream impact depends on external consumers.

### Impact

Any component treating `players_online` as cluster authority can falsely report live characters as offline.

### Remediation direction

Partition by `(channel_id, player_id)` and let each channel prune only its own rows, or replace this table as cluster authority with session/runtime ownership state. Regression: two processes, including a channel with zero local players.

### Conflicts / overlap

Deepens the prior handover's global presence/shared-state finding. No remediation overlap introduced.

---

## OTS-ECO-MKT-001 — concurrent partial market fills can over-consume one stale offer snapshot

- ID: `OTS-ECO-MKT-001`
- Severity: **HIGH**
- Affected repository/component: `blakinio/canary` / market economy
- Evidence state: **PROVEN**
- Exact source baseline: `d9c967d6e9b778da11a206d134d559f38ec1b8c8`
- Affected paths/functions:
  - `src/game/game.cpp` — `Game::playerAcceptMarketOffer`
  - `src/io/iomarket.cpp` — `IOMarket::getOfferByCounter`, `acceptOffer`, `deleteOffer`
  - `schema.sql` — `market_offers`
- Status: open; priority dynamic race proof recommended

### Source-to-impact trace

1. `getOfferByCounter()` performs a plain read; no row claim/lock is acquired.
2. Acceptance validates requested amount against local `offer.amount`.
3. BUY/SELL branches perform item/coin/gold effects before final offer mutation.
4. Partial acceptance executes `UPDATE market_offers SET amount = amount - ? WHERE id = ?`.
5. There is no `amount >= ?` predicate, affected-row ownership proof, or transaction coupling claim and effects.

### Deterministic failure timeline

Offer amount = `100`.

1. A reads `100`, accepts `60`.
2. B reads `100`, accepts `60`.
3. A performs value effects for `60`.
4. B performs value effects for `60`.
5. Only afterward do both attempt durable decrements.

Thus `120` units of value can be processed from a `100`-unit offer before the second persistence outcome can reject or reconcile anything.

### Qualification / limitations

Exact DB behavior if an unsigned decrement would underflow is configuration-dependent. The over-consumption window does not depend on that behavior. No physical two-process reproduction was executed in this pass.

### Impact

Economy duplication/overpayment or unreconciled market state involving items, coins, or gold-equivalent credit.

### Remediation direction

Durably claim quantity before irreversible effects: conditional atomic decrement requiring one affected row, or row-locked transaction with durable operation identity and recovery semantics.

### Conflicts / overlap

Concrete partial-fill specialization of the previously preserved market double-accept class.

---

## OTS-ECO-MKT-002 — market acceptance can load and full-save a stale DB copy of a counterparty who is online on another channel

- ID: `OTS-ECO-MKT-002`
- Severity: **HIGH**
- Affected repository/component: `blakinio/canary` / market + multichannel player persistence
- Evidence state: **PROVEN**
- Exact source baseline: `d9c967d6e9b778da11a206d134d559f38ec1b8c8`
- Affected paths/functions:
  - `src/game/game.cpp` — `Game::getPlayerByGUID`
  - `src/game/game.cpp` — `Game::playerAcceptMarketOffer`
  - `src/io/iologindata.cpp` / `src/io/functions/iologindata_save_player.cpp` — full player save
- Status: open; concrete market call-site of the prior cross-process offline-load/stale-save class

### Source-to-impact trace

1. `Game::getPlayerByGUID(guid, true)` searches only the current process's local player set.
2. If not found locally, it loads the player from DB and marks the object offline; it does not consult multichannel live ownership.
3. In market BUY-offer acceptance, the accepting channel calls `getPlayerByGUID(offer.playerId, true)` for the offer owner/buyer, inserts purchased items into that object's inbox, and saves it when `isOffline()` is true.
4. In market SELL-offer acceptance, the accepting channel uses the same offline-load path for the seller, credits its bank balance, and saves the object when `isOffline()` is true.
5. If the counterparty is actually online on another channel, this object is a stale snapshot of a record owned by another live process.
6. The accepting channel can full-save that stale snapshot while the true owner continues mutating its live Player state.
7. The remote owner can later full-save its own older inbox/balance snapshot and erase the market delivery/credit, or the stale market-side save can overwrite unrelated newer live state.

### Deterministic failure timelines

BUY-offer item delivery:

1. Buyer B is online on channel 2; durable snapshot is older than B's live state.
2. Seller A on channel 1 accepts B's buy offer.
3. Channel 1 does not see B locally and loads B from DB with `allowOffline=true`.
4. Channel 1 inserts the purchased item into stale B's inbox and full-saves B.
5. B's real channel 2 process later full-saves its live state whose inbox did not contain that item.
6. The market-delivered item can be erased.

SELL-offer gold credit:

1. Seller S is online on channel 2.
2. Buyer A on channel 1 accepts S's sell offer.
3. Channel 1 loads stale S as offline, credits its bank balance, and full-saves it.
4. S's owning channel later saves its live pre-credit balance.
5. The market sale credit can be erased; conversely the stale save can overwrite other newer S state.

### Qualification / limitations

This is a concrete current-source market specialization of an already known generic stale offline-player load/full-save class. No runtime E2E was executed. The exact set of overwritten fields follows the full player save surface.

### Impact

Normal cross-channel market activity can lose purchased items or sale proceeds and can overwrite unrelated live player state.

### Remediation direction

Do not use `allowOffline=true` for a record that can have a live owner on another channel. Resolve cluster ownership first and route mutation to the owning process through durable addressed operations; only perform offline direct apply after proving no live owner, with transactionally safe persistence.

### Conflicts / overlap

Deepens prior cross-process offline-player/stale-full-save evidence and market multichannel findings; no duplicate generic finding is opened.

---

## OTS-ECO-GUILD-001 — process-local guild balances plus absolute saves permit multichannel double-spend

- ID: `OTS-ECO-GUILD-001`
- Severity: **HIGH**
- Affected repository/component: `blakinio/canary` / guild bank
- Evidence state: **PROVEN**
- Exact source baseline: `d9c967d6e9b778da11a206d134d559f38ec1b8c8`
- Affected paths/functions:
  - `schema.sql` — `guilds.balance`
  - `src/io/ioguild.cpp` — `loadGuild`, `saveGuild`
  - `Guild::bankBalance`
  - `src/game/bank/bank.cpp`
- Status: revalidated/deepened existing finding

### Trace and deterministic reasoning

One global `guilds.balance` is loaded into process-local `Guild::bankBalance`. Authorization/debit uses the local snapshot; save later writes an absolute balance. No CAS/version/conditional decrement/fencing protects the global value.

Balance `100`: A and B each load `100`, each spend `80`, both effects succeed, each local balance becomes `20`, and both later save `20`. Durable balance is `20` although `160` was paid out.

### Impact

Cross-channel guild-bank double-spend and hidden lost updates.

### Remediation direction

Authorize/debit at the durable DB boundary with conditional atomic mutation and transactionally coupled effect. Eliminate stale absolute balance overwrite.

### Conflicts / overlap

Existing handover class revalidated with exact current load/debit/save chain.

---

## OTS-ECO-HOUSE-001 — cross-channel house-auction refund can be erased by the remote bidder's later full save

- ID: `OTS-ECO-HOUSE-001`
- Severity: **HIGH**
- Affected repository/component: `blakinio/canary` / house auction + player bank persistence
- Evidence state: **PROVEN**
- Exact source baseline: `d9c967d6e9b778da11a206d134d559f38ec1b8c8`
- Affected paths/functions:
  - `Game::playerCyclopediaHouseBid`
  - `Game::processBankAuction`
  - `IOLoginData::increaseBankBalance`
  - `IOLoginDataSave::savePlayerFirst`
- Status: open; concrete specialization of prior stale-save class

### Trace and timeline

`processBankAuction()` looks up the previous bidder only in the current process. A bidder online on another channel is treated as non-local/offline and receives a direct durable `balance = balance + refund`. The true owner process keeps its pre-refund in-memory balance and can later full-save an absolute value.

V is online on B with local/DB balance `100`. A refunds `50` directly in DB, producing `150`. B still holds `100`; B later full-saves and writes `100`, erasing the refund.

### Impact

Normal cross-channel house-auction activity can destroy refunded bank value.

### Remediation direction

Route mutation to the current record owner through a durable addressed operation, or make bank balance DB-authoritative and exclude it from stale full-save overwrite.

### Conflicts / overlap

Concrete house-auction call-site of the previously preserved cross-process stale-save class.

---

## OTS-ECO-HOUSE-002 — auction money/refund effects precede durable house bid-state persistence

- ID: `OTS-ECO-HOUSE-002`
- Severity: **HIGH**
- Affected repository/component: `blakinio/canary` / house auction crash consistency
- Evidence state: **PROVEN**
- Exact source baseline: `d9c967d6e9b778da11a206d134d559f38ec1b8c8`
- Affected paths/functions:
  - `Game::playerCyclopediaHouseBid`
  - `Game::processBankAuction`
  - House bid setters
  - `IOMapSerialize::{loadHouseInfo,saveHouseInfo,SaveHouseInfoGuard}`
  - `Map::save`
- Status: open

### Trace and timeline

Bid processing can durably refund the previous bidder before the new bidder/bid state, which exists only in memory, reaches a later `Map::save()`.

1. Durable House state still names previous bidder P.
2. New bidder N outbids P.
3. P is durably refunded.
4. House object switches to N only in memory.
5. Crash occurs before successful `Map::save()`.
6. Restart reloads P as bidder while P's refund remains durable.
7. A later outbid can refund the same hold again, or stale settlement can treat P as winner despite the hold having been returned.

### Qualification / limitations

The crash window is proven. Exact new-bidder debit persistence depends on independent player-save timing; duplicate-refund/unbacked-state branches do not require that assumption.

### Impact

Duplicate refunds, unbacked winning-bid state, or inconsistent bidder balances.

### Remediation direction

Treat bid state, reserve/debit and refund as one recoverable operation with durable identity and transactional or idempotent state-machine semantics.

---

## OTS-ECO-HOUSE-003 — house-transfer payment/refund state is persisted independently from transfer state

- ID: `OTS-ECO-HOUSE-003`
- Severity: **HIGH**
- Affected repository/component: `blakinio/canary` / house transfer economy
- Evidence state: **PROVEN**
- Exact source baseline: `d9c967d6e9b778da11a206d134d559f38ec1b8c8`
- Affected paths/functions:
  - `Game::playerCyclopediaHouseTransfer`
  - `Game::playerCyclopediaHouseAcceptTransfer`
  - `Game::playerCyclopediaHouseCancelTransfer`
  - `Game::playerCyclopediaHouseRejectTransfer`
  - `Game::processBankAuction`
  - per-player save path
  - `IOMapSerialize::SaveHouseInfoGuard` / `Map::save`
- Status: open

### Source-to-impact trace

1. Transfer creation changes House bidder/bid/end/state only in memory.
2. Accept calls `processBankAuction()`, reducing buyer bank balance in Player state, then sets `transferStatus=true` only in memory.
3. Player persistence and House persistence have separate commit boundaries.
4. Cancel/reject can refund the paid amount, including a direct durable DB increment for a non-local target, before clearing House transfer state in memory.
5. House state is persisted later by `Map::save()`.

### Deterministic failure timelines

Acceptance/debit branch:

1. Durable House transfer has `transferStatus=false`.
2. Buyer accepts; local bank is reduced; in-memory `transferStatus=true`.
3. Buyer save commits the reduced bank balance.
4. Crash occurs before House save.
5. Restart reloads `transferStatus=false` although the debit remains.
6. Re-accept can cause a repeated debit or the first payment becomes stranded.

Cancel/reject/refund branch:

1. Durable House transfer has `transferStatus=true`.
2. Cancel/reject refunds the buyer.
3. House fields are cleared only in memory.
4. Crash occurs before House save.
5. Restart reloads the still-accepted transfer.
6. Repeated cancel/reject can refund the same payment again.

### Qualification / limitations

The split persistence boundaries are proven. Exact UI/action availability after restart depends on transfer-state handling. No crash-injection runtime proof was executed.

### Impact

Repeated debit, stranded payment, duplicate refund, or inconsistent transfer ownership state.

### Remediation direction

Persist transfer acceptance/payment/refund through one durable idempotent operation or recoverable state machine. Cross-channel refunds must also respect live record ownership.

---

## OTS-ECO-TRADE-001 — completed bilateral trade has no atomic persistence boundary across both inventories

- ID: `OTS-ECO-TRADE-001`
- Severity: **HIGH**
- Affected repository/component: `blakinio/canary` / player trade persistence
- Evidence state: **PROVEN**
- Exact source baseline: `d9c967d6e9b778da11a206d134d559f38ec1b8c8`
- Affected paths/functions:
  - `Game::playerAcceptTrade`
  - `SaveManager::{saveAll,schedulePlayer,doSavePlayer}`
  - `IOLoginData::{savePlayer,savePlayerGuard}`
  - `IOLoginDataSave::savePlayerItem`
- Status: open; crash-injection proof recommended

### Source-to-impact trace

1. Once both players accept, both item transfers complete in memory.
2. Trade closes without synchronously persisting both players as one operation.
3. `IOLoginData::savePlayer()` gives one DB transaction per player.
4. SaveManager can persist players independently or in parallel.
5. No transaction or durable trade operation spans both inventories.

### Deterministic failure timelines

Before trade: X belongs durably to A, Y to B. In-memory trade: A receives Y, B receives X.

Duplication:

1. B's post-trade save commits X into B's inventory.
2. A has not saved, so durable A still contains X.
3. Crash.
4. Restart loads X for both A and B.

Loss/asymmetry:

1. A's post-trade save commits, removing X and adding Y.
2. B has not saved, so durable B still contains Y and lacks X.
3. Crash.
4. Restart can leave X absent from both and Y present on both, depending on the side/item traced.

### Qualification / limitations

Trade itself is local to one Canary process. This is crash consistency, not a cross-channel concurrent-trade claim.

### Impact

High-value item duplication or destruction.

### Remediation direction

Persist both ownership changes in one durable operation or use a durable trade ledger/state machine with idempotent recovery.

---

# Current-source revalidation of previously preserved findings

## Mail handoff exactly-once failures remain current

Evidence state: **PROVEN — existing finding revalidated/deepened**.

Affected paths/functions:

- `src/items/containers/mailbox/mailbox.cpp` — `Mailbox::sendItemAcrossCluster`
- `src/game/multichannel/mail_delivery_operation_handler.cpp` — `applyOwned`, `applyUnowned`
- `src/game/multichannel/cluster_record_handoff.cpp` — `tryApply`, `transitionAfterApply`, `enqueueAndTryApplyNow`

Current exact failure windows:

### Durable enqueue vs source-item removal persistence — duplication

1. `sendItemAcrossCluster()` serializes the mail item and durably enqueues a random operation ID.
2. Once the operation is durably captured, the source item is removed only from current in-memory state with `internalRemoveItem()`.
3. Enqueue and persistence of the sender/map source removal are not one transaction.
4. Crash after durable enqueue but before source-side persistence can restore the original source item after restart while the durable pending operation still delivers the serialized copy.
5. Result: source item + delivered mail item can both survive.

### Owned recipient apply vs operation `APPLIED` — loss

1. `applyOwned()` inserts the reconstructed item into the live recipient's in-memory inbox and returns `Applied`.
2. It does not save the Player.
3. `ClusterRecordHandoff::transitionAfterApply()` then independently marks the operation applied.
4. Crash after `markApplied` but before the recipient's next durable player save loses the in-memory inbox item while the operation is no longer pending.
5. Result: permanent mail loss.

### Offline apply commit vs operation `APPLIED` — duplication

1. `applyUnowned()` locks the operation row, proves no live owner, loads an offline Player, inserts the item, and saves that Player inside its explicit DB transaction.
2. The handler transaction commits before `ClusterRecordHandoff::transitionAfterApply()` marks the operation applied.
3. Crash after offline player save commit but before `markApplied` leaves the operation pending although the first delivery is already durable.
4. Retry can reconstruct and save the same mail item again.
5. Result: duplicate mail delivery.

These timelines directly revalidate the handover's existing mail handoff exactly-once class. No new generic ID is opened here.

### Remediation direction

Source consume, recipient delivery, and operation state need one recoverable idempotent protocol. For live-owned records, an `APPLIED` transition must not precede durable recipient persistence. For offline apply, player mutation and operation status must commit atomically or carry a recipient-side dedupe identity. Source removal also requires durable handoff identity that prevents the original item from reappearing as a second valid value after crash.

## House isolation failures remain current

Evidence state: **PROVEN — existing finding revalidated/deepened**.

Current schema comments intend physical house identity `(channel_id, id)`, but `houses` simultaneously defines `PRIMARY KEY (channel_id, id)` and `UNIQUE(id)`. `IOMapSerialize::loadHouseInfo()` reads house rows without a channel predicate and resolves by `houseId`; `SaveHouseInfoGuard()` inserts/upserts without `channel_id`, relying on default channel `1`. `house_lists` has `channel_id`, but its primary key omits it, save inserts omit it, and cleanup deletes by version without channel partitioning.

This revalidates the prior house-isolation class. `SaveHouseItemsGuard()` also starts by deleting all `tile_store` rows before rebuilding from the current process map; the broader tile-store impact remains within the existing class pending full schema/migration re-trace.

## Single-type account coin RMW remains current; dual-type debit is transactionally guarded

Evidence state: **PROVEN — existing single-type finding revalidated and narrowed**.

Single-type `Account::addCoins` / `removeCoins` perform plain read then absolute write. Concurrent `+50/+50` from `100` can both write `150`; concurrent `-80/-80` can both pass and both write `20`. Transaction history is registered after the balance update, so history failure can diverge from balance state.

Dual-type `removeCoins(primary, secondary)` instead uses a rollback transaction, `SELECT ... FOR UPDATE`, combined balance check, update and history writes. The hypothesis that it has the same unlocked RMW race is rejected below.

## Bank transfer crash consistency remains current

Evidence state: **PROVEN — existing finding revalidated**.

`Bank::transferTo()` mutates source and destination process-local bankable objects. Player saves are separate per-player transactions. A crash after only one player's save commits can persist only debit or only credit.

## GameStore effect/delivery before final coin debit remains current

Evidence state: **PROVEN — existing finding revalidated**.

Purchase effects run before `makeCoinTransaction`; coin removal/history occur afterward. EXP-boost count KV is also mutated before coin removal.

## Transferable coin receiver credit before sender debit remains current

Evidence state: **PROVEN — existing finding revalidated**.

The receiver DB balance is incremented before sender transferable-coin removal, without one transaction coupling both sides.

## Market expiry PENDING crash-recovery wedge remains current

Evidence state: **PROVEN — existing finding revalidated**.

Expiry creates deterministic `economic_ledger` PENDING, moves/removes the active offer, then performs refund/delivery and commits the ledger. Crash after offer transition can leave PENDING with no active offer; retry reuses the UUID and duplicate insertion fails closed, so automatic effect replay does not occur.

---

# Rejected hypotheses

## OTS-MC-JOB-RJ-001 — overlapping `market.expire` leaders alone duplicate one expiry effect

- Evidence state: **REJECTED**

Each offer expiry derives the same deterministic `economic_ledger.transaction_uuid`, which is unique/primary-key protected. The second worker cannot pass the same per-offer ledger insertion and apply the same effect. This does not reject the separate PENDING crash-recovery wedge.

## OTS-ECO-COIN-RJ-001 — dual-type `Account::removeCoins(primary, secondary)` has the single-type unlocked RMW race

- Evidence state: **REJECTED / FALSE POSITIVE**
- Baseline: `d9c967d6e9b778da11a206d134d559f38ec1b8c8`

The dual-type path uses a rollback-on-failure transaction and `SELECT ... FOR UPDATE`; concurrent calls serialize on the account row. Single-type add/remove remain unsafe.

All rejected hypotheses from the prior durable handover remain closed absent new evidence.

---

# Candidates / unknowns requiring continuation

## OTS-MC-SS-C01 — global server record writer behavior

Evidence state: **CANDIDATE**.

Known:

- `server_config` has one global `players_record` row;
- every process calls `Game::loadPlayersRecord()` during `GAME_STATE_INIT`;
- `Game` holds process-local `playersRecord` and declares `checkPlayersRecord()` / `updatePlayersRecord()`;
- the multichannel runbook classifies global server record handling as unwired singleton work.

Missing before promotion:

- exact current `loadPlayersRecord` / `checkPlayersRecord` / `updatePlayersRecord` implementation and persistence predicate;
- proof whether writers can lower/overwrite a record or merely compute a per-channel instead of cluster-wide peak.

## OTS-MC-SS-C02 — raid daily-counter KV reset from every channel global-server-save event

Evidence state: **CANDIDATE**.

Known:

- daily-reward reset is individually leader-gated;
- the same `global_server_save.lua` resets every `Raid.registry` `checks-today` / `last-check-date` KV without that gate;
- the global-event framework starts in every process.

Missing:

- exact `raid.kv` backing/namespace;
- concrete reset-versus-increment race impact.

## OTS-MC-SS-C03 — cleanup/highscore/DB-optimization/global-event jobs

Evidence state: **UNKNOWN / CANDIDATE by concrete job**.

The runbook warning is insufficient to manufacture findings. `Game` visibly owns process-local highscore/query cache maps, so a persistent/shared conflict must be proven at an actual global writer. Each scheduler still needs data-scope, writer-count, ownership, fencing, transaction, retry and stale-writer tracing.

## Remaining exactly-once scope

- depot/inbox/stash paths beyond the now revalidated mail and market call-sites;
- final house settlement/ownership transitions beyond bid/transfer findings;
- remaining account-coin call-sites beyond the core Account API;
- MyAAC premium-point paid-operation races not re-traced in this slice.

---

# Evidence-state index

## PROVEN

- `OTS-MC-SS-001` — destructive multiwriter rebuild of global `players_online`.
- `OTS-ECO-MKT-001` — concurrent partial market over-consumption from stale offer snapshots.
- `OTS-ECO-MKT-002` — market acceptance can mutate/full-save stale DB copies of counterparties online on another channel.
- `OTS-ECO-GUILD-001` — guild-bank stale snapshot/absolute-save double-spend.
- `OTS-ECO-HOUSE-001` — cross-channel house-auction refund can be erased by remote stale full save.
- `OTS-ECO-HOUSE-002` — auction money/refund effects precede durable bid-state persistence.
- `OTS-ECO-HOUSE-003` — house-transfer payment/refund and transfer-state persistence have separate crash boundaries.
- `OTS-ECO-TRADE-001` — bilateral trade persists as independently committing player snapshots.
- Existing mail handoff exactly-once class revalidated with source-consume, owned-apply and offline-apply crash windows.
- Existing house-isolation class revalidated.
- Existing single-type account coin RMW class revalidated and narrowed.
- Existing bank-transfer crash-consistency class revalidated.
- Existing GameStore effect-before-debit class revalidated.
- Existing transferable-coin credit-before-debit class revalidated.
- Existing market-expiry PENDING crash-recovery wedge revalidated.

## DYNAMICALLY CONFIRMED

- None added in this pass.

## DERIVED

- No standalone finding promoted solely from framework/runbook composition.

## CONFIGURATION-DEPENDENT

- Exact DB outcome of market amount underflow; `OTS-ECO-MKT-001` does not depend on it.
- Downstream impact of corrupt `players_online` depends on consumers.

## CANDIDATE

- `OTS-MC-SS-C01` — global server record writer behavior.
- `OTS-MC-SS-C02` — raid daily-counter KV reset.
- `OTS-MC-SS-C03` — concrete cleanup/highscore/DB-optimization/global-event jobs.

## UNKNOWN

- Exhaustive repository-wide shared-state writer inventory is not complete.
- Remaining depot/inbox/stash and final house-settlement exactly-once paths are not fully traced.

## REJECTED / FALSE POSITIVE

- `OTS-MC-JOB-RJ-001` — overlapping expiry leaders alone do not duplicate one expiry effect because deterministic ledger identity rejects the second execution.
- `OTS-ECO-COIN-RJ-001` — dual-type coin debit is row-locked/transactional and does not share the single-type unlocked RMW race.
- Prior durable handover rejected hypotheses remain closed absent new evidence.

---

# Dynamic validation status

No dynamic race/crash proof was executed in this slice.

Reason:

- no existing local checkout in the disposable shell;
- shell DNS could not resolve `github.com` for a fresh clone/fetch;
- public/third-party deployment testing is explicitly out of scope.

Priority isolated harness scenarios:

1. two-process market partial overfill;
2. market accept against counterparty live on another channel;
3. cancel-versus-accept;
4. mail source-removal crash after durable enqueue;
5. mail owned-delivery crash after `markApplied` but before recipient save;
6. mail offline-delivery crash after player commit but before `markApplied`;
7. stale persistent save after ownership loss;
8. guild-bank double spend;
9. cross-channel house-auction refund lost update;
10. house auction crash after refund but before `Map::save()`;
11. house-transfer acceptance crash after debit save but before House save;
12. house-transfer cancel/reject crash after refund but before House save;
13. crash after exactly one side of completed trade is saved;
14. broader cross-channel house persistence corruption.

Target harness: at least two Canary processes, shared MariaDB, Redis, deterministic barriers/crash injection, disposable local/container environment.

# Remediation workflow

PR #526 remains evidence-only. No runtime remediation is mixed into this continuation.

Each confirmed problem must move to a separate bounded remediation task with exact ownership, overlap review, source provenance, narrow implementation strategy and regression proof.

# Next continuation checkpoint

Continue in this order unless stronger evidence changes priority:

1. finish shared-state writer inventory:
   - global player record implementation;
   - raid KV backing/reset semantics;
   - concrete cleanup jobs;
   - concrete persistent/shared highscore behavior;
   - DB optimization scheduler;
2. continue exactly-once review:
   - remaining depot/inbox/stash mutation paths;
   - final house settlement/ownership transitions;
   - remaining account-coin mutations;
   - MyAAC premium-point paid operations;
3. run isolated two-process race/crash proofs when a local disposable runtime is available.
