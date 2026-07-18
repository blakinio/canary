# OTS Security Audit Continuation — Multichannel Shared State and Exactly-Once Economy

Date: 2026-07-18

Task: `CAN-20260718-ots-security-shared-state-economy-audit`

Draft PR: #526

## Scope and baseline

This document continues the durable OTS security audit from:

- `docs/security/MYAAC_CANARY_SECURITY_AUDIT_2026-07-17.md`
- `docs/security/OTS_SECURITY_AUDIT_HANDOVER_2026-07-18.md`

It does not restart the completed MyAAC/login-stack review and does not reopen previously rejected hypotheses without new evidence.

Writable repository:

- `blakinio/canary`

Evidence-only/read-only repositories remain:

- `opentibiabr/canary`
- `opentibiabr/login-server`
- `slawkens/myaac`
- `opentibiabr/otclient`
- `opentibiabr/remeres-map-editor`
- `opentibiabr/client-editor`

Exact source baseline for this continuation pass:

- `blakinio/canary@d9c967d6e9b778da11a206d134d559f38ec1b8c8`

Local shell Git preflight could not be completed because the disposable shell had no existing checkout and could not resolve `github.com`. Live GitHub state and source content were therefore revalidated through the authenticated GitHub connector. No public or third-party deployment was scanned or tested.

## Evidence-state contract

- `PROVEN` — directly confirmed in current code or deterministic source-level proof.
- `DYNAMICALLY CONFIRMED` — reproduced in an isolated runtime/harness.
- `DERIVED` — strongly follows from code composition but lacks a complete runtime proof.
- `CONFIGURATION-DEPENDENT` — impact depends on deployment/configuration behavior.
- `CANDIDATE` — suspicious path still requiring call-chain or runtime proof.
- `UNKNOWN` — insufficient evidence.
- `REJECTED` / `FALSE POSITIVE` — hypothesis tested and rejected.

No finding below is promoted solely because a sink looks dangerous. Each qualified item traces the relevant state transition and persistence boundary.

---

## Shared/global state inventory — current continuation checkpoint

| Surface | Scope observed at current baseline | Current writer/coordination state | Audit state |
|---|---|---|---|
| `players_online` | global table keyed only by `player_id` | every channel periodically rebuilds/prunes from its own local player map | `PROVEN` destructive multiwriter conflict — OTS-MC-SS-001 |
| `cluster_sessions` | cluster-global account/player ownership table | Redis lease + DB mirror; separate stale-writer/fencing findings already preserved in the prior handover | previously audited; not reopened here |
| `channel_runtime_status` | per-channel row keyed by `channel_id` | channel-partitioned | no new finding in this slice |
| `market_offers` / `market_history` | global economy state | acceptance has no transactional row claim; expiry is leader-gated | `PROVEN` partial-fill race — OTS-ECO-MKT-001; prior expiry crash finding revalidated |
| `economic_ledger` | global idempotency/audit table keyed by deterministic `transaction_uuid` | wired for selected market paths only | duplicate-expiry-on-leader-loss hypothesis rejected; crash-recovery gap remains previously known |
| `guilds.balance` | global per-guild balance | copied into process-local `Guild`, later saved by absolute value | `PROVEN` stale snapshot / multichannel double-spend — OTS-ECO-GUILD-001 |
| `accounts.coins*` | global per-account balances | multiple RMW paths; prior account-coin race finding preserved | prior finding revalidated through GameStore/transfer paths |
| `global_storage` | global key/value rows with no channel partition | daily reward reset individually leader-gated | broader writers still require call-site inventory |
| `kv_store` | global `key_name` primary key with no channel partition | namespace/call-site dependent | `CANDIDATE` for unguarded global-event writers |
| boosted creature/boss | global rows | one-shot leader-election gates wired | no new finding in this slice |
| house rows | intended per-channel physical identity | house rent/auction correctly treated as per-channel by current runbook | prior house isolation findings remain; not mechanically reopened |
| global event scheduling | framework starts in every process | only specific jobs are individually gated | `CANDIDATE` until each event is classified per-channel vs cluster-singleton |
| table cleanup jobs | expected cluster-singleton where operating on global rows | current runbook marks wiring contract-only | `UNKNOWN` exact live call sites |
| highscores cache rebuild | expected cluster-singleton if shared persistent cache exists | current runbook marks wiring contract-only | `UNKNOWN` exact live persistent writer |
| database optimization | cluster-singleton administrative work | current runbook marks wiring contract-only | `UNKNOWN` exact live scheduler/call site |
| global server record | global `server_config.players_record`; per-process cached `Game::playersRecord` | current runbook marks singleton wiring contract-only | `CANDIDATE`; exact writer implementation still to trace |

The inventory above is a continuation checkpoint, not a claim that every repository-global table has already been exhaustively classified. Items without a complete source-to-impact trace remain `CANDIDATE` or `UNKNOWN`.

---

# Qualified findings

## OTS-MC-SS-001 — `players_online` is destructively rebuilt from process-local state by every channel

- Severity: **MEDIUM**
- Affected component/repository: Canary multichannel shared persistence — `blakinio/canary`
- Evidence state: **PROVEN**
- Exact source baseline: `d9c967d6e9b778da11a206d134d559f38ec1b8c8`
- Affected paths/functions:
  - `src/game/game.cpp` — `Game::start`
  - `src/game/game.cpp` — `Game::updatePlayersOnline`
  - `schema.sql` — `players_online`
- Status: open; durable evidence captured; bounded remediation task not yet created

### Source -> validation -> authorization -> state transition -> persistence -> retry/crash -> impact

1. Each Canary process owns only its own in-memory `Game::players` map.
2. `Game::start()` schedules `Game::updatePlayersOnline()` on every process at `UPDATE_PLAYERS_ONLINE_DB` intervals.
3. There is no multichannel ownership or leader check around this periodic job.
4. `Game::updatePlayersOnline()` derives `onlinePlayerIds` only from the current process's local players.
5. It inserts those local IDs into global `players_online`.
6. It then executes:
   - `DELETE FROM players_online` when the local process has zero players; or
   - `DELETE FROM players_online WHERE player_id NOT IN (<this process local ids>)` otherwise.
7. The table schema contains only `player_id`; there is no `channel_id`, writer identity, fencing token, or ownership predicate.
8. The enclosing DB transaction makes each local rebuild atomic, but does not make concurrent channel rebuilds compositionally correct.
9. Repeated execution does not converge on cluster union; it converges on whichever channel wrote last.

### Deterministic failure timeline

Assume:

- Channel A local online set = `{A1}`.
- Channel B local online set = `{B1}`.
- Both share one `players_online` table.

Timeline:

1. A inserts `A1`.
2. A deletes every row not equal to `A1`; `B1` is removed if present.
3. B inserts `B1`.
4. B deletes every row not equal to `B1`; `A1` is removed.
5. Final durable table represents B's local set, not `{A1, B1}`.

A channel with zero local players executes an unconditional table-wide delete and can erase the presence rows of every other channel.

### Qualification / limitations

- The integrity failure in `players_online` is directly proven.
- This pass did **not** prove that current `ProtocolStatus` reads `players_online`; current `ProtocolStatus` uses local `Game` statistics instead.
- Exact downstream impact therefore depends on which external/web/account components consume `players_online` in a given deployment.

### Impact

Cluster-wide presence data becomes last-writer-wins and can report live characters as offline. Any consumer treating `players_online` as authoritative can make incorrect presence-dependent decisions.

### Remediation direction

Use one of these bounded designs:

1. make presence channel-partitioned, e.g. `(channel_id, player_id)`, and allow each channel to prune only its own rows; or
2. retire this table as cluster authority and derive cluster presence from the already partitioned/owned multichannel session/runtime state.

Regression proof should run at least two Canary processes sharing one DB and verify that one channel cannot delete another channel's presence rows, including the zero-local-player case.

### Conflicts / overlap

- Deepens the prior handover's generic global presence/shared-state interference finding with a concrete current-source writer and deterministic failure timeline.
- No overlap with lifecycle-only PR #522.
- No exclusive-path overlap with authenticated-session transport PR #514.

---

## OTS-ECO-MKT-001 — concurrent partial market fills can over-consume one offer after both channels perform value effects

- Severity: **HIGH**
- Affected component/repository: Canary market / multichannel economy — `blakinio/canary`
- Evidence state: **PROVEN**
- Exact source baseline: `d9c967d6e9b778da11a206d134d559f38ec1b8c8`
- Affected paths/functions:
  - `src/game/game.cpp` — `Game::playerAcceptMarketOffer`
  - `src/io/iomarket.cpp` — `IOMarket::getOfferByCounter`
  - `src/io/iomarket.cpp` — `IOMarket::acceptOffer`
  - `src/io/iomarket.cpp` — `IOMarket::deleteOffer`
  - `schema.sql` — `market_offers`
- Status: open; durable evidence captured; high-priority isolated two-process dynamic proof recommended

### Source -> validation -> authorization -> state transition -> persistence -> retry/crash -> impact

1. A channel reads an offer through `IOMarket::getOfferByCounter()` with a plain `SELECT`; no row lock or durable claim is acquired.
2. `Game::playerAcceptMarketOffer()` validates the requested amount against the locally read `offer.amount` snapshot.
3. The function performs value-moving effects before the final offer mutation:
   - BUY-offer branch: item/coin delivery/removal and seller bank credit;
   - SELL-offer branch: buyer debit, item/coin delivery, seller bank credit.
4. Market history is appended after those effects.
5. Only then does the local snapshot execute `offer.amount -= amount`.
6. If the local snapshot is nonzero, `IOMarket::acceptOffer()` executes:
   `UPDATE market_offers SET amount = amount - <requested> WHERE id = <offerId>`.
7. The update has no `amount >= requested` predicate and no transactionally coupled claim.
8. The caller does not check an affected-row count or otherwise prove that this acceptance owned sufficient remaining quantity.
9. Different channel processes can therefore validate against the same stale amount and each complete value effects before either final DB decrement prevents the other.

### Deterministic partial-fill failure timeline

Assume one offer has durable `amount = 100`.

1. Channel A reads amount `100` and requests `60`; validation passes.
2. Channel B reads amount `100` and requests `60`; validation also passes.
3. A performs its economic effects for `60`.
4. B independently performs its economic effects for `60`.
5. A decrements the DB row by `60`.
6. B attempts a second decrement by `60` after its economic effects already completed.

At this point `120` units of offer value have been processed from an offer that represented only `100` units. The exact final database result of the second unsigned decrement can vary with SQL behavior/configuration, but the over-consumption window exists before that final persistence result and the return path does not reconcile the already-applied effects.

A related exact-quantity variant also exists: two concurrent `50`-unit acceptances can each keep a local `offer.amount = 50` and both choose the partial-update branch, potentially leaving a durable zero-amount row instead of deleting the exhausted offer.

### Qualification / limitations

- The stale-snapshot/no-claim race and effect-before-final-amount-mutation sequence are directly proven in current source.
- The exact SQL result when an unsigned amount would underflow is configuration-dependent; the finding does not depend on assuming a specific underflow behavior because both value effects can already have occurred.
- No physical two-process runtime reproduction was executed in this pass.

### Impact

Concurrent channel acceptance can process more value than the offer's remaining quantity, creating an economy duplication/overpayment condition or an unreconciled partial state. Depending on offer direction, the duplicated value can manifest as extra items, coins, or gold-equivalent credit.

### Remediation direction

The offer quantity must be durably claimed before irreversible effects, for example:

- one transactionally checked update such as `UPDATE ... SET amount = amount - ? WHERE id = ? AND amount >= ?`, requiring exactly one affected row;
- row locking/transaction scope that couples the claim, histories, debit/credit/delivery state, and exhausted-offer deletion;
- deterministic idempotency identity for each acceptance/retry;
- explicit recovery for a claimed-but-not-fully-applied operation.

A two-Canary shared-DB harness should deterministically synchronize two partial accepts against the same offer and assert total delivered/credited value never exceeds the original amount.

### Conflicts / overlap

- This is a concrete partial-fill specialization of the previously preserved market double-accept class, not a restart of that audit.
- It adds the exact stale-snapshot partial-fill timeline and the final `amount` update weakness.
- No overlap with PR #522 lifecycle work.

---

## OTS-ECO-GUILD-001 — process-local guild balances plus absolute saves permit multichannel double-spend and lost updates

- Severity: **HIGH**
- Affected component/repository: Canary guild bank / multichannel economy — `blakinio/canary`
- Evidence state: **PROVEN**
- Exact source baseline: `d9c967d6e9b778da11a206d134d559f38ec1b8c8`
- Affected paths/functions:
  - `schema.sql` — `guilds.balance`
  - `src/io/ioguild.cpp` — `IOGuild::loadGuild`, `IOGuild::saveGuild`
  - `src/creatures/players/grouping/guild.hpp` — process-local `Guild::bankBalance`
  - `src/game/bank/bank.cpp` — `Bank::credit`, `Bank::debit`, `Bank::transferTo`
- Status: revalidated/deepened existing finding; durable current-source trace captured

### Source -> validation -> authorization -> state transition -> persistence -> retry/crash -> impact

1. `guilds.balance` is one global durable value per guild.
2. `IOGuild::loadGuild()` loads that balance into a process-local `Guild::bankBalance`.
3. `Bank::hasBalance()` and `Bank::debit()` operate only on that local in-memory value.
4. Multiple Canary channel processes can therefore each hold the same stale starting balance for the same guild.
5. `IOGuild::saveGuild()` later persists an absolute value with `UPDATE guilds SET balance = <localBalance>`.
6. There is no compare-and-swap version, conditional decrement, row lock, fencing token, or transaction spanning multiple channel processes.
7. `Bank::transferTo()` composes source debit and destination credit in memory rather than as one durable DB transaction.
8. Subsequent absolute saves can collapse multiple independently spent snapshots into one final balance.

### Deterministic failure timeline

Assume durable guild balance = `100`.

1. Channel A loads guild balance `100`.
2. Channel B loads the same guild balance `100`.
3. A authorizes and spends/transfers `80`; local A balance becomes `20`.
4. B independently authorizes and spends/transfers `80`; local B balance becomes `20`.
5. Both value effects are accepted by their respective process-local checks.
6. A saves absolute guild balance `20`.
7. B later saves absolute guild balance `20`.
8. Durable balance is `20` although `160` of value was authorized from an initial `100`.

### Qualification / limitations

This pass revalidates and deepens a finding already preserved in the prior handover. It is not claimed as a newly discovered class.

### Impact

A shared guild balance can be double-spent across channels and later persisted as a plausible-looking lower balance, hiding the fact that more value was paid out than existed.

### Remediation direction

Use durable atomic balance mutation rather than process-local authorization, e.g. a conditional decrement at the DB boundary with affected-row verification, and transactionally couple the corresponding credit/effect. Cross-channel retries need a stable idempotency key. Absolute stale balance saves must not overwrite a newer global guild balance.

### Conflicts / overlap

- Directly overlaps the existing handover's guild-bank multichannel double-spend class and supplies the current exact load/debit/save chain.
- No remediation is included in PR #526.

---

# Current-source revalidation of previously preserved findings

## GameStore effect/delivery occurs before final coin debit

Evidence state: **PROVEN — existing finding revalidated**

Current `data/libs/gamestore/parsers.lua` performs the selected `GameStore.process*Purchase(...)` effect inside the purchase `pcall` and only after the effect returns successfully calls `player:makeCoinTransaction(offer)`. The transaction call removes the coins and writes history afterward. Selected transaction-summary state is also emitted before the final coin debit.

`data/libs/gamestore/player.lua` additionally mutates the EXP-boost purchase-count KV before coin removal inside `makeCoinTransaction()`.

The prior handover's effect-before-debit crash/failure window therefore remains valid at the current baseline. This document does not create a duplicate finding ID for it.

## Transferable coin transfer credits the receiver before checked sender debit

Evidence state: **PROVEN — existing finding revalidated**

Current `data/libs/gamestore/parsers.lua::parseTransferableCoins`:

1. checks the sender's process-visible transferable balance;
2. resolves the receiver account;
3. executes a direct DB increment on the receiver's `accounts.coins_transferable`;
4. only then calls `player:removeTransferableCoinsBalance(amount)` on the sender;
5. does not condition receiver credit on a transactionally coupled successful sender debit.

The existing credit-before-debit finding remains current.

## Market expiry retains the previously documented PENDING crash-recovery wedge

Evidence state: **PROVEN — existing finding revalidated**

`IOMarket::processExpiredOffers()` creates a deterministic `economic_ledger` `PENDING` row, moves the offer to history/removes it from active offers, and only afterward performs the refund/delivery and marks the ledger `COMMITTED`.

A crash after the active-offer transition but before the effect/commit can leave a durable `PENDING` key while the offer is no longer active. A retry reuses the same deterministic UUID, and `EconomicLedgerStore::beginPending()` treats the duplicate-key insert failure as fail-closed, so no automatic effect replay occurs. This is the previously preserved crash-consistency finding, not a new one.

---

# Rejected hypotheses

## OTS-MC-JOB-RJ-001 — losing `market.expire` leadership mid-run does not by itself create a duplicate expiry refund/delivery

- Evidence state: **REJECTED** for the duplicate-effect hypothesis
- Exact baseline: `d9c967d6e9b778da11a206d134d559f38ec1b8c8`
- Paths:
  - `src/io/iomarket.cpp`
  - `src/game/multichannel/cluster_job_leadership_registry.hpp`
  - `src/game/multichannel/economic_ledger_store.cpp`
  - `schema.sql`

### Reasoning

The leader check occurs before the asynchronous expiry query and no fencing token is carried into each result mutation. That initially suggests that an old leader and a replacement leader could overlap.

However, each expiry operation derives one deterministic ledger UUID from `("market.expire", offerId)`. `economic_ledger.transaction_uuid` is the primary key, and `beginPending()` uses a plain insert and fails closed if that insert fails. Therefore two overlapping workers targeting the same offer cannot both pass the per-offer ledger insert and both apply the expiry effect.

### Important limitation

This rejection is narrow. It rejects **duplicate expiry effect caused solely by overlapping leaders**. It does **not** reject the separate, already proven PENDING crash-recovery wedge described above.

Status: closed unless new evidence bypasses or removes the deterministic ledger gate.

---

# Candidates / unknowns requiring continuation

## OTS-MC-SS-C01 — global server record writer race

Evidence state: **CANDIDATE**

Known evidence:

- `server_config` has one global `players_record` row.
- every process calls `Game::loadPlayersRecord()` during `GAME_STATE_INIT`;
- `Game` maintains a process-local `playersRecord` cache;
- current multichannel operations documentation classifies global server record handling as cluster-singleton and still contract-only/unwired.

Missing proof before promotion:

- current implementation of `Game::loadPlayersRecord()` / `Game::checkPlayersRecord()`;
- exact persistence statement and update predicate;
- whether concurrent channels can lower/overwrite the record or only redundantly increase it.

## OTS-MC-SS-C02 — raid daily counters are reset from every channel's global server-save event

Evidence state: **CANDIDATE**

Known evidence:

- daily-reward shared storage is individually protected by `Game.tryClaimClusterJobLeadership("daily.reward.reset")`;
- the same `global_server_save.lua` function then resets each `Raid.registry` entry's `raid.kv` `checks-today` and `last-check-date` without a leader gate;
- the generic global-event framework is started in every Canary process.

Missing proof before promotion:

- exact `raid.kv` backing namespace and persistence implementation;
- whether those keys are intentionally cluster-global or map/channel-local by convention;
- whether duplicate resets can race with increments and lose same-window raid progress.

## OTS-MC-SS-C03 — unwired global event scheduling / cleanup / highscores / DB optimization jobs

Evidence state: **UNKNOWN / CANDIDATE by individual job**

The current operations runbook explicitly marks global event scheduling, cleanup jobs, highscores cache rebuild, database optimization and global server record handling as not yet wired to cluster-singleton execution. This is not sufficient by itself to create five security findings.

Required continuation:

1. enumerate each concrete scheduler/call site;
2. classify its data as per-channel or global;
3. identify all writers;
4. trace locking/fencing/transactions;
5. promote only concrete conflicting global writers.

## Exactly-once flows still open in this continuation task

- bank transfer combinations beyond the already preserved crash-consistency class;
- inbox/depot/stash handoff outside the already preserved mail-handoff findings;
- trade completion persistence ordering;
- house auction/payment effects beyond the prior house-isolation and per-channel job classification;
- remaining account-coin mutation call sites;
- MyAAC premium-point paid-operation races not yet re-traced in this slice.

---

# Evidence-state index

## PROVEN

- `OTS-MC-SS-001` — global `players_online` destructive multiwriter rebuild from local channel state.
- `OTS-ECO-MKT-001` — concurrent partial market fills can over-consume one stale offer snapshot after value effects.
- `OTS-ECO-GUILD-001` — process-local guild balances plus absolute persistence permit multichannel double-spend/lost update; existing handover finding revalidated and deepened.
- Existing GameStore effect-before-debit path revalidated.
- Existing transferable-coin receiver-credit-before-sender-debit path revalidated.
- Existing market-expiry PENDING crash-recovery wedge revalidated.

## DYNAMICALLY CONFIRMED

- None added in this pass.

## DERIVED

- None promoted as standalone findings in this pass. Broad framework-level shared-job concerns remain candidates until concrete call sites are traced.

## CONFIGURATION-DEPENDENT

- Exact database outcome of the second partial-fill decrement when the arithmetic would underflow an unsigned column. The over-consumption finding itself does not depend on this outcome.
- Downstream operational impact of corrupted `players_online` depends on which external components consume that table.

## CANDIDATE

- `OTS-MC-SS-C01` — global server record writer race.
- `OTS-MC-SS-C02` — unguarded raid daily-counter KV reset from each channel's global server-save event.
- `OTS-MC-SS-C03` — individual global-event/cleanup/highscore/DB-optimization jobs pending concrete call-site proof.

## UNKNOWN

- Exhaustive repository-wide global/shared table and KV writer inventory is not yet complete.
- Remaining bank/trade/stash/house-payment exactly-once flows are not yet fully re-traced on the current baseline.

## REJECTED / FALSE POSITIVE

- `OTS-MC-JOB-RJ-001` — overlapping `market.expire` leaders alone do not duplicate the same expiry effect because the deterministic per-offer economic-ledger primary key rejects the second execution. The separate crash-recovery wedge remains valid.
- All rejected hypotheses listed in the prior durable handover remain closed unless new evidence appears.

---

# Dynamic validation status

No dynamic race proof was executed in this continuation slice.

Reason:

- no existing local checkout was available in the disposable shell;
- the shell could not resolve `github.com`, so a fresh local clone/fetch could not be created;
- testing public or third-party deployments is explicitly out of scope.

Priority isolated harness scenarios remain:

1. two-process market partial overfill;
2. cancel-versus-accept;
3. mail retry duplication;
4. stale persistent save after ownership loss;
5. guild-bank double spend;
6. cross-channel house persistence corruption.

The intended harness remains two or more Canary processes with shared MariaDB and Redis in a disposable local/container environment.

# Remediation workflow

This PR is evidence-only. No runtime fix is mixed into this audit continuation.

For each confirmed problem, the next remediation step must be a separate bounded task that records:

- exact affected component and ownership;
- overlap with open PRs/tasks;
- source provenance;
- one narrowly scoped implementation strategy;
- regression proof, preferably deterministic concurrent integration coverage for race findings.

# Next continuation checkpoint

Continue in this order unless stronger evidence changes priority:

1. finish concrete global/shared-state writer inventory, beginning with:
   - `Game::loadPlayersRecord()` / `Game::checkPlayersRecord()`;
   - raid KV backing and reset/increment semantics;
   - cleanup jobs;
   - highscores persistent/shared cache behavior;
   - DB optimization scheduler;
2. continue exactly-once tracing for:
   - bank transfer combinations;
   - trade completion;
   - depot/inbox/stash persistence;
   - house payments/auctions;
   - remaining account coin mutations;
3. build the isolated two-process race harness when a local disposable runtime is available.
