# OTS Security Audit Continuation Addendum — Raid Shared State and GameStore XP Boost

Date: 2026-07-18

Task: `CAN-20260718-ots-security-shared-state-economy-audit`

Program: `CAN-PROGRAM-SECURITY-VALIDATION`

Draft PR: #526

Source baseline for the code paths qualified in this addendum: `blakinio/canary@d9c967d6e9b778da11a206d134d559f38ec1b8c8`.

This addendum continues `docs/security/OTS_SECURITY_SHARED_STATE_ECONOMY_AUDIT_2026-07-18.md`. It does not reopen or duplicate the findings and rejected hypotheses already preserved there or in `docs/security/OTS_SECURITY_AUDIT_HANDOVER_2026-07-18.md`.

Allowed evidence classifications used here are `PROVEN`, `DYNAMICALLY CONFIRMED`, `DERIVED`, `HIGH-CONFIDENCE CANDIDATE`, `CANDIDATE`, `REJECTED`, and `FALSE POSITIVE`.

No public or third-party deployment was tested. No dynamic two-process or packet E2E was executed in this continuation because the disposable shell could not resolve `github.com` and no local multichannel Canary runtime was available. All new qualifications below are source-level.

---

# OTS-MC-SS-002 — global raid scheduling and raid KV decisions are process-local in multichannel mode

- ID: `OTS-MC-SS-002`
- Severity: **MEDIUM**
- Affected repository/component: `blakinio/canary` / raid scheduler, KV persistence, multichannel global jobs
- Evidence state: **PROVEN**
- Status: open; evidence only, no remediation in PR #526
- Affected paths/functions:
  - `data/scripts/globalevents/raids.lua`
  - `data/scripts/globalevents/global_server_save.lua`
  - `data/libs/systems/raids.lua` — `Raid:canStart`, `Raid:tryStart`
  - `data/libs/systems/encounters.lua` — `Encounter:start`, process-local `currentStage`
  - `src/kv/kv.cpp` — `KVStore::get`, `KVStore::set`
  - `src/kv/kv.hpp` — `KVStore`, `ScopedKV`
  - `src/kv/kv_sql.cpp` — SQL-backed load/save/upsert
  - `src/game/scheduling/save_manager.cpp` — later KV persistence

## Attacker/source-to-impact trace

The triggering source is ordinary global raid scheduling rather than a direct unauthenticated request. A player can benefit from the resulting duplicated world event, but no claim is made that a player directly controls the scheduler clock or random roll.

1. `data/scripts/globalevents/raids.lua` registers a periodic global event in every Canary process and iterates `Raid.registry`, calling `raid:tryStart()`.
2. There is no multichannel leader check, fencing token, DB ownership claim, or Redis lease in that scheduling path.
3. `Raid` uses a shared logical namespace built from `kv.scoped("raids"):scoped(name)` for `checks-today`, `failed-attempts`, `last-occurrence`, and related values.
4. `ScopedKV` delegates to the root `KVStore`, but `KVStore::get()` first serves the process-local in-memory cache and `KVStore::set()` mutates that local cache.
5. A normal `set()` does not synchronously make the new value authoritative across processes. Persistence occurs later through eviction/flush/save-all paths.
6. The SQL persistence layer upserts by key. It does not attach a process owner, fencing token, version predicate, compare-and-swap condition, or atomic increment to these raid values.
7. `Raid:canStart()` performs scheduling checks and increments against the process's local cached view.
8. `Raid:tryStart()` updates last-occurrence state and starts the encounter after those local checks pass.
9. `Encounter:start()` protects only the process-local encounter state (`currentStage`). A second channel has an independent `Encounter` object and independent stage guard.
10. Therefore two channels can independently authorize and start the same intended global raid while each believes its local raid state permits execution.
11. Later KV persistence can also write stale absolute snapshots of the same logical keys, producing lost updates to counters or last-occurrence state.
12. `global_server_save.lua` additionally resets raid day-check state without the daily-reward leader gate used elsewhere in that file, reinforcing that raid state is not treated as a fenced cluster singleton.

## Deterministic two-process timeline

Assume channels A and B share MariaDB and run the same raid definition.

1. A and B each run the one-minute raid global event.
2. Each reads its own cached `checks-today` and `last-occurrence` view for the same logical raid keys.
3. Both independently pass `canStart()`.
4. Both update only their local cached raid state.
5. A starts its local encounter because A's `currentStage` is free.
6. B also starts its local encounter because B's separate `currentStage` is free.
7. Each channel executes the raid on its own local world/map process.
8. When cached KV state is later persisted, the final durable values can reflect whichever stale snapshot writes last rather than the union of both executions.

No physical two-process reproduction was performed, so this timeline is a deterministic source-level proof rather than `DYNAMICALLY CONFIRMED` evidence.

## Retry, restart, and crash behavior

- A restart discards one process's local KV cache and reloads whatever durable snapshot survived the competing delayed writes.
- Another still-running channel can continue making decisions from an older cached value.
- There is no durable per-raid execution identity that makes a second process's start idempotent.
- There is no fencing token attached to the spawn/effect execution, so a stale process is not prevented from executing after a newer process has acted.

## Impact

- One raid intended to be globally scheduled can execute independently on multiple channels.
- Daily/max-check and minimum-gap semantics are not cluster-authoritative.
- Durable raid counters and last-occurrence metadata can lose updates.

Duplicated reward or economy amplification from a specific raid is **DERIVED** from duplicate encounter execution; no individual raid reward call chain was traced in this continuation, so that narrower impact is not promoted to `PROVEN` here.

## Remediation direction

Use one cluster-authoritative execution claim per raid occurrence. Suitable designs include a leader/fenced scheduler or an atomic durable per-raid lease/claim with monotonic fencing. Scheduling counters and last-occurrence updates must use authoritative atomic mutations rather than process-local read/modify/write cache decisions. The actual raid start/effect path must validate the same fencing/claim identity so a stale process cannot execute after supersession.

Regression coverage should run at least two Canary processes against one shared DB/Redis set, synchronize both at the same eligibility decision, and prove that exactly one process obtains the execution claim and exactly one encounter starts.

---

# OTS-ECO-STORE-001 — direct XP Boost purchase packets bypass the server's daily-limit and active-boost eligibility guards

- ID: `OTS-ECO-STORE-001`
- Severity: **MEDIUM**
- Affected repository/component: `blakinio/canary` / GameStore XP Boost purchase authorization and pricing
- Evidence state: **PROVEN**
- Status: open; evidence only, no remediation in PR #526
- Affected paths/functions:
  - `data/libs/gamestore/constants.lua`
  - `data/libs/gamestore/senders.lua` — offer presentation
  - `data/libs/gamestore/player.lua` — `canBuyOffer`, `makeCoinTransaction`
  - `data/libs/gamestore/parsers.lua` — `onRecvbyte`, `parseBuyStoreOffer`
  - `data/libs/gamestore/purchases.lua` — `processExpBoostPurchase`
  - `src/io/functions/iologindata_save_player.cpp` — XP boost persistence

## Attacker-controlled source

An authenticated game client controls the incoming GameStore packet and offer ID. `GameStore.RecivedPackets.C_BuyStoreOffer` is routed to `parseBuyStoreOffer()`.

This finding does not require bypassing account authentication. The attacker is a normal authenticated player who sends a syntactically valid direct purchase packet instead of relying on the client UI's disabled-state presentation.

## Validation and routing

1. `constants.lua` defines XP Boost as `OFFER_TYPE_EXPBOOST`, defines `C_BuyStoreOffer`, the `exp-boost-count` KV key, tier prices, and an XP Boost item limit.
2. `player.lua::canBuyOffer()` contains two relevant eligibility checks:
   - it disables XP Boost when the purchase counter reaches the configured daily terminal value;
   - it disables XP Boost when `getXpBoostTime() > 0`, reporting that an XP boost is already active.
3. `senders.lua::sendShowStoreOffers()` calls `player:canBuyOffer(offer)` while constructing the client-visible offer list and disabled reason.
4. The packet receive path in `parsers.lua::onRecvbyte()` routes a direct `C_BuyStoreOffer` packet to `parseBuyStoreOffer()`.
5. `parseBuyStoreOffer()` validates the offer shape and payment capacity, but it does not call `player:canBuyOffer()` and does not independently enforce either the daily terminal count or the already-active XP Boost condition.
6. XP Boost is explicitly included among offer types allowed through the parser's generic guard.

The authoritative server-side purchase path therefore treats the UI-disabled state as presentation rather than an enforced authorization condition.

## Business logic and side effect

1. After the parser accepts the packet, the XP Boost branch calls `GameStore.processExpBoostPurchase(player)`.
2. `processExpBoostPurchase()` does not recheck the daily count or active-boost restriction.
3. It sets the boost percent and changes boost time to `currentXpBoostTime + 3600`.
4. Therefore a direct valid purchase packet can add another hour even when an XP Boost is already active.
5. The resulting `xpboost_value` and `xpboost_stamina` fields are included in player persistence, so the accumulated effect can become durable on normal save.

## Counter and pricing behavior

`player.lua::makeCoinTransaction()` handles XP Boost pricing after the purchase effect path:

1. It reads `exp-boost-count`.
2. When the count is `<= 0` or `> 5`, it replaces the pricing index with `1`.
3. It selects the corresponding tier price.
4. It stores `expBoostCount + 1`.
5. It then attempts coin removal and records history on successful debit.

The normal UI disables the offer at the terminal counter state, but a direct purchase packet is not subject to that guard. Once the direct path reaches a value above the defined pricing range, `makeCoinTransaction()` resets the pricing index to tier 1 and continues. Serialized direct purchases can therefore continue cycling through the pricing schedule rather than being rejected at the intended daily cap.

The existing, separately documented GameStore effect-before-final-debit problem is not duplicated as a new finding here. This finding is specifically the missing authoritative eligibility enforcement that permits purchases the server UI says are disallowed.

## Retry and rate behavior

`parseBuyStoreOffer()` uses a short purchase cooldown. That throttles rapid repeated requests but does not restore the missing daily/active eligibility check. An attacker can serialize requests after each cooldown and continue extending boost time.

## Deterministic request timeline

1. Player has a currently active XP Boost or has reached the UI-disabled daily terminal counter.
2. Client UI would present the XP Boost as disabled through `canBuyOffer()`.
3. Player sends a direct `C_BuyStoreOffer` packet containing the valid XP Boost offer ID.
4. `parseBuyStoreOffer()` resolves the valid offer and never invokes the eligibility predicate that disabled it in the UI.
5. `processExpBoostPurchase()` adds 3600 seconds to the existing boost time.
6. `makeCoinTransaction()` charges according to its own counter normalization and advances the counter.
7. After the counter falls outside the defined pricing tier range, the transaction path normalizes it back to tier 1 instead of rejecting the purchase.
8. Repeating the serialized request extends the active boost beyond the intended one-active/daily-limit policy.

## Impact

A normal authenticated player with sufficient store currency can bypass the intended XP Boost purchase policy, stack additional boost duration while a boost is active, and continue purchasing past the UI-enforced daily terminal count. The price state can cycle back to the first tier after the counter exceeds the defined range.

## Remediation direction

Move XP Boost eligibility into the authoritative purchase transaction path and evaluate it immediately before any effect:

- reject when an XP Boost is already active if that is the intended policy;
- reject at the daily terminal count rather than normalizing an out-of-range counter back to the first tier;
- compute one immutable server-side price from the validated counter;
- couple counter reservation, debit, history, and effect through one atomic or recoverable idempotent operation;
- do not treat client-visible disabled state as authorization.

Regression coverage should send direct purchase packets rather than using only the normal UI:

1. active boost present -> request rejected; no time, counter, balance, or history change;
2. daily terminal counter reached -> request rejected with no mutation;
3. final permitted purchase -> exactly one increment/debit/effect;
4. next direct packet -> rejected;
5. debit/history failure -> no lasting effect or counter advancement.

---

# Candidate status updates

## OTS-MC-SS-C01 — global `players_record` writer

Evidence state: **HIGH-CONFIDENCE CANDIDATE**.

The previously missing implementation is now traced:

- `Game::loadPlayersRecord()` loads the single global `server_config.players_record` into process-local `Game::playersRecord`.
- `Game::getPlayersOnline()` reflects the process-local player collection.
- `Game::checkPlayersRecord()` compares that local count with the process-local cached record.
- when the local count is larger than the cached value, it assigns the local value and calls `updatePlayersRecord()`;
- `updatePlayersRecord()` performs an unconditional absolute `UPDATE server_config SET value = <local playersRecord>` with no `GREATEST`, compare-and-swap, ownership predicate, leader election, or fencing token.

If two processes both invoke this path after loading the same older value, a stale channel can lower the durable record. Example: A and B load `100`; A reaches local `150` and writes `150`; B still caches `100`, later reaches local `120`, sees `120 > 100`, and writes `120`.

Promotion to `PROVEN` is withheld because the exact current invocation point of `checkPlayersRecord()` was not resolved in the available current-source search. The writer semantics are proven; reachability of the writer in the current runtime remains the missing call-chain link.

## OTS-MC-SS-C03 — startup cleanup, migration, optimization, and highscore work

Evidence state: **CANDIDATE**.

Newly traced facts:

- `CanaryServer` runs database setup/update and optional `DatabaseManager::optimizeTables()` before `initializeMultichannelCluster()`.
- Therefore Redis leader election/fencing initialized by the multichannel runtime cannot protect those earlier database jobs.
- `DatabaseManager::updateDatabase()` reads one `db_version`, runs migration scripts, and advances the version after a successful Lua call.
- It does not inspect a migration's returned boolean result before advancing the version.
- Some migrations use DDL sequences whose individual `db.query()` results are not transactionally coupled or are not propagated back to `updateDatabase()`.
- `server_initialization.lua` runs global cleanup in every process and directly deletes `kv_store` rows matching `player%.exp-boost-count`.
- That SQL deletion does not invalidate another process's already-cached `KVStore` value, so a still-running process can continue from or later persist stale cached state.

No isolated concurrent-start or migration-failure reproduction was executed, so no standalone startup-migration vulnerability is promoted from this evidence in this addendum.

No persistent/shared highscore rebuild writer was proven in the searched current-source paths. That does not establish an exhaustive `REJECTED` result for all highscore behavior; it remains part of the unfinished shared-writer inventory.

---

# Dynamic validation status

## DYNAMICALLY CONFIRMED

None added in this continuation.

Tests not executed:

- two-process simultaneous raid eligibility/start;
- stale/lost raid KV update after competing process saves;
- direct XP Boost packet against active-boost state;
- direct XP Boost packet at the daily terminal counter;
- repeated XP Boost packet sequence through counter wrap;
- concurrent multichannel startup migration/optimization;
- `players_record` stale rollback through the unresolved current invocation point.

Reason: no local checkout/runtime was available in the disposable shell because `github.com` DNS resolution failed. Testing public or third-party deployments is explicitly out of scope.

---

# Rejected hypotheses status

No previously rejected hypothesis was reopened.

The following remain closed:

- `OTS-MC-JOB-RJ-001` — overlapping market expiry leaders alone do not both apply the same expiry effect because the deterministic ledger transaction identity rejects the second worker.
- `OTS-ECO-COIN-RJ-001` — dual-type account coin debit does not share the unlocked single-type RMW race because it uses a row-locked transaction.
- all rejected/false-positive hypotheses preserved by the durable July 18 handover remain closed absent new evidence.

No new `REJECTED` or `FALSE POSITIVE` classification is added by this addendum.

---

# Handover checkpoint

## Repository / branch / PR

- repository: `blakinio/canary`
- branch: `docs/ots-security-shared-state-economy-audit-20260718`
- PR: `#526` — `docs(security): continue shared-state and economy audit`
- PR state at handover preparation: open, draft
- branch head before this addendum commit: `6f9cee00b35d882df9d11bece9e3d3ff36ed0138`
- task-start source baseline: `d9c967d6e9b778da11a206d134d559f38ec1b8c8`

## Task / program / ownership

- task ID: `CAN-20260718-ots-security-shared-state-economy-audit`
- program ID: `CAN-PROGRAM-SECURITY-VALIDATION`
- owned write paths:
  - `docs/agents/tasks/active/CAN-20260718-ots-security-shared-state-economy-audit.md`
  - `docs/security/OTS_SECURITY_SHARED_STATE_ECONOMY_AUDIT_2026-07-18.md`
  - `docs/security/OTS_SECURITY_SHARED_STATE_ECONOMY_AUDIT_2026-07-18_ADDENDUM.md`
- source/runtime paths remain read-only evidence in this task.

## Read before continuation

- root `AGENTS.md`
- `docs/agents/AGENTS.md`
- `docs/agents/REPOSITORY_MAP.md`
- `docs/agents/CONTEXT_ROUTING.md`
- active task record for `CAN-20260718-ots-security-shared-state-economy-audit`
- `docs/security/MYAAC_CANARY_SECURITY_AUDIT_2026-07-17.md`
- `docs/security/OTS_SECURITY_AUDIT_HANDOVER_2026-07-18.md`
- `docs/security/OTS_SECURITY_SHARED_STATE_ECONOMY_AUDIT_2026-07-18.md`
- multichannel operations/current source paths relevant to leader election, KV, raids, GameStore, database startup, and persistence.

The external File Library did not provide a separate `OTS_security_audit_matrix.xlsx` during this continuation. No claim is made that an unavailable matrix was checked.

## Checked in this continuation

- live PR #526 state and current head before writes;
- task ownership and existing evidence scope;
- current-source raid global-event registration and `tryStart` chain;
- raid KV namespace and process-local cache behavior;
- delayed SQL persistence and absence of fencing/CAS on raid KV decisions;
- process-local encounter stage guard;
- GameStore XP Boost UI eligibility checks;
- direct `C_BuyStoreOffer` routing and parser authorization path;
- XP Boost side effect, counter normalization, coin transaction ordering, and player persistence;
- global `players_record` load/check/update implementation;
- startup database update/optimization ordering relative to multichannel initialization;
- selected migration return/error handling;
- startup cleanup mutation of XP Boost KV rows;
- highscore search for a concrete persistent/shared rebuild writer;
- overlap with existing findings and rejected hypotheses before assigning new IDs.

## New findings

- `OTS-MC-SS-002` — **PROVEN** — global raid scheduling/KV decisions are process-local and unfenced across channels, permitting independent duplicate raid execution and stale/lost raid-state updates.
- `OTS-ECO-STORE-001` — **PROVEN** — direct XP Boost purchase packets bypass daily-limit and active-boost eligibility checks that exist only in offer presentation; repeated direct purchases can stack boost time and cycle pricing state.

## Candidate updates

- `OTS-MC-SS-C01` — **HIGH-CONFIDENCE CANDIDATE** — unsafe absolute multiwriter implementation proven; current invocation point still unresolved.
- `OTS-MC-SS-C03` — **CANDIDATE** — DB migrations/optimization execute before multichannel coordination and migration result handling is unsafe, but no isolated failure reproduction supports standalone promotion yet.

## Rejected hypotheses

No new rejected hypothesis. Previously preserved `REJECTED` / `FALSE POSITIVE` items remain closed.

## Dynamic tests

- executed: none
- failed: none claimed
- not executable in this environment: two-process raid race, direct packet E2E, crash injection, concurrent startup migration tests

## CI / validation

- last previously verified Agent Task Ownership pass: head `421fbe5a21ee49f7b797bab3f56ee864dd6545fb`, workflow run `29637804392`
- last previously verified CI pass: head `421fbe5a21ee49f7b797bab3f56ee864dd6545fb`, workflow run `29637804516`
- the new checkpoint/addendum head requires fresh exact-head checks before PR readiness or merge
- no final gate is claimed for the new head

## Merge status

- PR #526 remains open and draft during this handover.
- no merge was performed.
- no branch-protection bypass or admin merge was attempted.

## Exact next action

Continue Priority B exactly-once review from the current task branch, starting with remaining depot/inbox/stash cross-process mutation paths and final house settlement/ownership transitions. In parallel, resolve the current `checkPlayersRecord()` invocation point before promoting `OTS-MC-SS-C01`. When a disposable local two-process stack becomes available, prioritize dynamic confirmation of `OTS-MC-SS-002` and direct-packet regression proof for `OTS-ECO-STORE-001`. Do not open remediation PRs until each remediation receives its own bounded task/ownership scope and overlap check.
