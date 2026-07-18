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
| `accounts.coins*` | global per-account balances | multiple RMW paths | prior race findings revalidated |
| `global_storage` | global key/value | daily reward individually leader-gated | wider writers still open |
| `kv_store` | global `key_name` PK | namespace/call-site dependent | raid-reset candidate open |
| boosted creature/boss | global rows | leader gates wired | no new finding in this slice |
| house rows | intended per-channel world state | rent/auction jobs per-channel | prior house-isolation findings preserved |
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
- Paths/functions:
  - `src/game/game.cpp` — `Game::start`, `Game::updatePlayersOnline`
  - `schema.sql` — `players_online`
- Status: open; remediation not implemented

### Trace

1. Each Canary process owns only its local `Game::players` map.
2. `Game::start()` schedules `Game::updatePlayersOnline()` in every process.
3. No leader/ownership check protects this job.
4. `updatePlayersOnline()` derives IDs only from the local process.
5. It inserts local IDs, then deletes every row not in that local set.
6. If the local set is empty it executes a table-wide delete.
7. `players_online` has no `channel_id`, writer identity, or fencing field.
8. The DB transaction makes one channel's rebuild atomic but does not compose multiple channel-local rebuilds into a cluster union.

### Deterministic failure timeline

- A local set: `{A1}`.
- B local set: `{B1}`.
- A inserts A1 and prunes B1.
- B inserts B1 and prunes A1.
- Durable state becomes whichever channel wrote last, not `{A1,B1}`.
- A channel with zero local players can erase all rows.

### Qualification

The table-integrity failure is proven. Current `ProtocolStatus` uses local `Game` statistics, not this table, so downstream impact depends on which external components consume `players_online`.

### Impact

Cluster-wide presence stored in `players_online` is last-writer-wins and can falsely report live characters as offline.

### Remediation direction

Partition by `(channel_id, player_id)` and allow each channel to prune only its own rows, or replace this table as authority with cluster session/runtime state. Add a two-process regression covering normal and zero-local-player writers.

### Overlap

Deepens the prior handover's global presence/shared-state finding. No remediation is mixed into PR #526.

---

## OTS-ECO-MKT-001 — concurrent partial market fills can over-consume one stale offer snapshot

- Severity: **HIGH**
- Repository/component: `blakinio/canary` / market economy
- Evidence state: **PROVEN**
- Source baseline: `d9c967d6e9b778da11a206d134d559f38ec1b8c8`
- Paths/functions:
  - `src/game/game.cpp` — `Game::playerAcceptMarketOffer`
  - `src/io/iomarket.cpp` — `IOMarket::getOfferByCounter`, `acceptOffer`, `deleteOffer`
  - `schema.sql` — `market_offers`
- Status: open; priority dynamic proof recommended

### Trace

1. `getOfferByCounter()` performs a plain read; no row claim/lock is acquired.
2. `playerAcceptMarketOffer()` validates requested amount against the locally read `offer.amount`.
3. BUY and SELL branches perform item/coin/gold effects before final durable offer mutation.
4. History is appended after those effects.
5. Only then does the local snapshot subtract the accepted amount.
6. Partial acceptance executes `UPDATE market_offers SET amount = amount - ? WHERE id = ?`.
7. There is no `amount >= ?` predicate, affected-row ownership proof, or transaction coupling the claim with effects.

### Deterministic failure timeline

Offer amount is `100`.

1. Channel A reads `100`, requests `60`, passes validation.
2. Channel B reads `100`, requests `60`, also passes.
3. A performs value effects for `60`.
4. B performs value effects for `60`.
5. Only afterward do both attempt durable amount decrements.

`120` units of value can therefore be processed from a `100`-unit offer before the second persistence outcome can reject/reconcile anything. The exact DB result of an unsigned underflow is configuration-dependent; the over-consumption window is not.

A related exact-fill race exists when two channels each accept `50` from a `100` snapshot: both local copies remain nonzero and can choose the partial-update branch rather than deleting an exhausted offer.

### Impact

Economy duplication/overpayment or unreconciled market state; manifestation depends on offer direction and can include items, coins, or gold-equivalent credit.

### Remediation direction

Durably claim quantity before irreversible effects, e.g. conditional atomic decrement requiring exactly one affected row, or row-locked transaction with durable operation identity and explicit recovery. Add deterministic two-process partial-fill coverage.

### Overlap

Concrete partial-fill specialization of the prior market double-accept class; not a restart of completed audit work.

---

## OTS-ECO-GUILD-001 — process-local guild balances plus absolute saves permit multichannel double-spend

- Severity: **HIGH**
- Repository/component: `blakinio/canary` / guild bank
- Evidence state: **PROVEN**
- Source baseline: `d9c967d6e9b778da11a206d134d559f38ec1b8c8`
- Paths/functions:
  - `schema.sql` — `guilds.balance`
  - `src/io/ioguild.cpp` — `IOGuild::loadGuild`, `saveGuild`
  - `src/creatures/players/grouping/guild.hpp` — `Guild::bankBalance`
  - `src/game/bank/bank.cpp` — `Bank::credit`, `debit`, `transferTo`
- Status: revalidated/deepened existing finding

### Trace

1. One global `guilds.balance` is loaded into a process-local `Guild::bankBalance`.
2. `Bank::hasBalance()` / `debit()` authorize against that local snapshot.
3. Different channel processes can hold the same starting balance.
4. `IOGuild::saveGuild()` later writes an absolute balance value.
5. No CAS/version/conditional decrement/fencing protects the global balance.
6. `Bank::transferTo()` composes source debit and destination credit in memory, not one durable DB transaction.

### Deterministic failure timeline

Durable guild balance is `100`.

1. A loads `100`.
2. B loads `100`.
3. A spends `80`, local balance `20`.
4. B independently spends `80`, local balance `20`.
5. Both effects are accepted.
6. A saves `20`; B later saves `20`.
7. Durable balance is `20` although `160` was paid out.

### Impact

Cross-channel guild-bank double spend and hidden lost updates.

### Remediation direction

Authorize/debit at the durable DB boundary with a conditional atomic mutation and transactionally couple the corresponding credit/effect. Prevent stale absolute guild-balance saves from overwriting newer global state.

### Overlap

Existing handover finding revalidated with exact current load/debit/save chain.

---

## OTS-ECO-HOUSE-001 — house-auction refund to a bidder online on another channel can be lost by that bidder's later full save

- Severity: **HIGH**
- Repository/component: `blakinio/canary` / house auction + player bank persistence
- Evidence state: **PROVEN**
- Source baseline: `d9c967d6e9b778da11a206d134d559f38ec1b8c8`
- Paths/functions:
  - `src/game/game.cpp` — `Game::playerCyclopediaHouseBid`, `Game::processBankAuction`
  - `src/io/iologindata.cpp` — `IOLoginData::increaseBankBalance`
  - `src/io/functions/iologindata_save_player.cpp` — `IOLoginDataSave::savePlayerFirst`
- Status: open; concrete house-payment specialization of prior cross-process stale-save class

### Source -> validation -> authorization -> state transition -> persistence -> retry/crash -> impact

1. A previous house bidder may later be online on a different channel process.
2. When another player outbids them, the house-owning channel calls `Game::processBankAuction()`.
3. Refund routing checks only `g_game().getPlayerByName(house->getBidderName())`, which sees players local to the current process.
4. A bidder online on another channel is therefore treated as non-local/offline.
5. The current channel refunds them through `IOLoginData::increaseBankBalance()`, which executes a durable relative SQL increment: `balance = balance + refund`.
6. The bidder's real owning channel still holds the pre-refund process-local `Player::bankBalance` snapshot.
7. A later normal full player save executes `IOLoginDataSave::savePlayerFirst()` and writes `players.balance = player->bankBalance` as an absolute value.
8. There is no CAS/fencing/version check protecting that bank column from the stale writer.
9. The stale full save can overwrite and permanently erase the cross-channel auction refund.

### Deterministic failure timeline

Assume bidder V has durable/local bank balance `100` while online on channel B.

1. V previously placed a bid for a house on channel A, then is online on B.
2. Another bidder on A triggers a refund of `50` to V.
3. A cannot find V in its local player map and executes `UPDATE players SET balance = balance + 50`, making durable balance `150`.
4. V's in-memory balance on B remains `100`.
5. B later saves V for an unrelated normal lifecycle event.
6. `savePlayerFirst()` writes absolute `balance = 100`.
7. The `50` refund is lost.

### Qualification / limitations

The stale-write sequence is directly proven. It requires the prior bidder to be online in another channel while the refund is issued and then to perform a later full save from that stale in-memory state. No runtime E2E was executed in this pass.

### Impact

Normal cross-channel house-auction activity can destroy refunded bank value. The same routing pattern is relevant anywhere a process treats a remotely online player as offline and directly mutates DB state later covered by an absolute player save.

### Remediation direction

Do not apply bank mutations directly to a row that may be owned by another live process and later overwritten by a full save. Route the mutation to the current record owner through a durable addressed operation (`cluster_pending_operations`-style handoff), or make bank balance itself a DB-authoritative atomic value excluded from stale full-save overwrite. Require idempotent operation identity and ownership/fencing checks.

### Overlap

This is a concrete house-auction/payment call-site for the prior cross-process offline-player/stale-full-save class. It adds a specific normal-economy failure timeline and affected functions; it does not duplicate the generic finding mechanically.

---

# Current-source revalidation of previously preserved findings

## GameStore effect/delivery before final coin debit

Evidence state: **PROVEN — existing finding revalidated**.

`data/libs/gamestore/parsers.lua` performs `GameStore.process*Purchase(...)` effects inside the purchase `pcall`; only after those effects return does it call `player:makeCoinTransaction(offer)`. `data/libs/gamestore/player.lua` removes coins and then writes history, and mutates EXP-boost count KV before coin removal. The prior effect-before-debit crash/failure window remains current.

## Transferable coin transfer credits receiver before checked sender debit

Evidence state: **PROVEN — existing finding revalidated**.

`parseTransferableCoins` checks sender balance, directly increments receiver `accounts.coins_transferable`, then calls sender removal. Receiver credit is not transactionally coupled to a proven sender debit.

## Market expiry PENDING crash-recovery wedge

Evidence state: **PROVEN — existing finding revalidated**.

Expiry inserts a deterministic `economic_ledger` PENDING row, moves/removes the active offer, then performs refund/delivery and commits the ledger. A crash after the offer transition can leave PENDING with no active offer; retry reuses the same UUID and the duplicate insert fails closed, so automatic effect replay does not occur.

---

# Rejected hypotheses

## OTS-MC-JOB-RJ-001 — `market.expire` leader loss mid-run alone duplicates the same expiry effect

- Evidence state: **REJECTED**
- Source baseline: `d9c967d6e9b778da11a206d134d559f38ec1b8c8`

The leader check is not fenced through the asynchronous result mutation, so overlapping old/new leaders are possible in principle. However each offer expiry derives the same deterministic `economic_ledger.transaction_uuid`; that column is the primary key and `beginPending()` fails closed on the second insert. Two workers cannot both pass the per-offer ledger gate and both apply the effect.

This rejection is narrow: it does not reject the separate PENDING crash-recovery wedge.

---

# Candidates / unknowns requiring continuation

## OTS-MC-SS-C01 — global server record writer race

Evidence state: **CANDIDATE**.

Known:

- `server_config` has one global `players_record` row;
- every process calls `Game::loadPlayersRecord()` during initialization;
- `Game` holds a process-local `playersRecord` cache;
- the current multichannel runbook still classifies global server record handling as unwired singleton work.

Missing before promotion:

- exact current implementation of `Game::loadPlayersRecord()` / `Game::checkPlayersRecord()`;
- exact persistence/update predicate;
- proof whether writers can lower/overwrite a record or merely compute a per-channel rather than cluster-wide peak.

## OTS-MC-SS-C02 — raid daily-counter KV reset from every channel global-server-save event

Evidence state: **CANDIDATE**.

Known:

- daily-reward reset is individually leader-gated;
- the same global-server-save function resets every `Raid.registry` entry's `raid.kv` `checks-today` and `last-check-date` without that gate;
- the global-event framework starts in every process.

Missing before promotion:

- exact `raid.kv` namespace/backing persistence;
- whether the keys are intentionally global or channel-scoped by convention;
- concrete increment/reset race impact.

## OTS-MC-SS-C03 — remaining unwired global-event / cleanup / highscore / DB-optimization jobs

Evidence state: **UNKNOWN / CANDIDATE by individual job**.

The runbook warning is not sufficient to manufacture findings. Each concrete scheduler must still be classified by data scope, writer count, ownership, fencing, transactions, retries and stale-writer behavior.

## Exactly-once flows still open

- remaining bank transfer combinations;
- depot/inbox/stash handoff beyond already preserved mail findings;
- trade completion persistence ordering;
- additional house auction/payment transitions, including bid debit/state crash windows;
- remaining account-coin mutation call sites;
- MyAAC premium-point paid-operation races not yet re-traced in this slice.

---

# Evidence-state index

## PROVEN

- `OTS-MC-SS-001` — destructive multiwriter rebuild of global `players_online`.
- `OTS-ECO-MKT-001` — concurrent partial market over-consumption from stale offer snapshots.
- `OTS-ECO-GUILD-001` — guild-bank stale snapshot/absolute-save double spend; existing class revalidated.
- `OTS-ECO-HOUSE-001` — cross-channel house-auction refund can be erased by remote bidder's stale full save.
- Existing GameStore effect-before-debit path revalidated.
- Existing transferable-coin receiver-credit-before-sender-debit path revalidated.
- Existing market-expiry PENDING crash-recovery wedge revalidated.

## DYNAMICALLY CONFIRMED

- None added in this pass.

## DERIVED

- No standalone finding promoted solely from framework/runbook composition.

## CONFIGURATION-DEPENDENT

- Exact DB outcome of a market partial-fill decrement that would underflow an unsigned column; the over-consumption finding itself does not depend on it.
- Downstream operational impact of corrupted `players_online` depends on table consumers.

## CANDIDATE

- `OTS-MC-SS-C01` — global server record writer behavior.
- `OTS-MC-SS-C02` — raid daily-counter KV reset.
- `OTS-MC-SS-C03` — concrete cleanup/highscore/DB-optimization/global-event jobs pending source proof.

## UNKNOWN

- Exhaustive repository-wide shared-state writer inventory is not complete.
- Remaining bank/trade/stash/house-payment exactly-once flows are not fully traced.

## REJECTED / FALSE POSITIVE

- `OTS-MC-JOB-RJ-001` — overlapping `market.expire` leaders alone cannot both apply the same expiry effect because deterministic ledger-PK insertion rejects the second execution.
- Prior durable handover rejected hypotheses remain closed absent new evidence.

---

# Dynamic validation status

No dynamic race proof was executed in this slice.

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
7. broader cross-channel house persistence corruption.

Target harness: minimum two Canary processes, shared MariaDB, Redis, deterministic synchronization, disposable local/container environment.

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
   - bank transfer combinations;
   - trade completion;
   - depot/inbox/stash persistence;
   - remaining house auction/payment transitions;
   - remaining account coin mutations;
3. build isolated two-process race proofs when a local disposable runtime is available.
