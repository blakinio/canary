---
task_id: CAN-20260714-cross-process-db-row-handoff
program_id: CAN-PROGRAM-MULTICHANNEL
coordination_id: ""
status: in_progress
agent: "claude"
branch: claude/canary-cross-channel-mail-fix
base_branch: main
created: 2026-07-14T08:40:00Z
updated: 2026-07-14T11:15:00Z
last_verified_commit: 4de9350e62e2ca9ddf717e16628f87084a74aa86
risk: medium
related_issue: ""
related_pr: "#308 (merged), PR 2 not yet opened"
depends_on: []
blocks:
  - "house double-ownership fix (deferred, needs this foundation)"
  - "DIRTY session recovery/admin tooling (deferred, needs this foundation)"
owned_paths:
  exclusive:
    - src/game/multichannel/cluster_pending_operation_repository.hpp
    - src/game/multichannel/db_cluster_pending_operation_repository.hpp
    - src/game/multichannel/db_cluster_pending_operation_repository.cpp
    - src/game/multichannel/cluster_record_ownership.hpp
    - src/game/multichannel/db_cluster_record_ownership_resolver.hpp
    - src/game/multichannel/db_cluster_record_ownership_resolver.cpp
    - src/game/multichannel/cluster_record_handoff.hpp
    - src/game/multichannel/cluster_record_handoff.cpp
    - data-otservbr-global/migrations/63.lua
    - tests/unit/game/multichannel/cluster_record_handoff_test.cpp
    - tests/shared/game/multichannel/fake_cluster_pending_operation_repository.hpp
    - tests/shared/game/multichannel/fake_cluster_record_ownership_resolver.hpp
    - docs/multichannel/CROSS_PROCESS_DB_ROW_HANDOFF.md
    - src/game/multichannel/cluster_handoff_runtime.hpp
    - src/game/multichannel/cluster_operation_id.hpp
    - src/game/multichannel/cluster_operation_id.cpp
    - src/game/multichannel/mail_delivery_payload.hpp
    - src/game/multichannel/mail_delivery_payload.cpp
    - src/game/multichannel/mail_delivery_operation_handler.hpp
    - src/game/multichannel/mail_delivery_operation_handler.cpp
    - tests/unit/game/multichannel/cluster_operation_id_test.cpp
    - tests/unit/game/multichannel/mail_delivery_payload_test.cpp
  shared:
    - schema.sql
    - src/items/containers/mailbox/mailbox.hpp
    - src/items/containers/mailbox/mailbox.cpp
    - src/game/game.cpp
    - src/game/CMakeLists.txt
    - vcproj/canary.vcxproj
    - docs/multichannel/ARCHITECTURE.md
    - docs/multichannel/DECISION_MATRIX.md
    - docs/multichannel/TEST_PLAN.md
    - docs/agents/MODULE_CATALOG.md
  read_only:
    - src/game/multichannel/cluster_session_lookup.hpp
    - src/game/multichannel/cluster_session_lookup.cpp
    - src/game/multichannel/cluster_runtime.hpp
    - src/game/multichannel/cluster_runtime.cpp
    - src/game/multichannel/redis_client.hpp
    - src/map/house/house.cpp
modules_touched:
  - ClusterPendingOperationStore (new)
  - ClusterRecordHandoff (new)
  - Mailbox (PR 2)
reuses:
  - cluster_sessions / findOnlineChannelForPlayer (PR #136, #292 - player ownership resolution, unchanged)
  - houses.channel_id (Phase 1 - static house ownership, unchanged)
  - IRedisClient::acquireLease/renewLease/releaseLease (Phase 1 - reused only insofar as cluster_sessions already uses it; no new Redis code)
  - economic_ledger idempotency pattern (Phase 5 - operation_id/transaction_uuid PRIMARY KEY convention)
  - channel_switch_audit consumed_at pattern (migration 61 - generalized into the new pending/applied state machine)
  - g_dispatcher().cycleEvent via Game::renewClusterSessions (Phase 2 - PR 2 will piggyback the new sweep on this, not add a second scheduler)
public_interfaces:
  - "ClusterPendingOperationStore::enqueue/markApplied/markFailed/markAbandoned/findPendingForRecord/findStalePending (new)"
  - "ClusterRecordHandoff::resolveOwnership/tryApply (new)"
cross_repo_tasks: []
---

# Goal

Design and implement one shared, safe cross-process DB-row-handoff
mechanism (per `docs/multichannel/CROSS_PROCESS_DB_ROW_HANDOFF.md`), then
use it to fix the real cross-channel mail-loss bug
(`Mailbox::sendItem` silently dropping items delivered to a recipient
online on a different channel). Explicitly do NOT implement the house
double-ownership fix or `DIRTY` session recovery tooling this session -
both are documented as migration plans (§12 of the design doc) for a
follow-up task, per the user's explicit exclusion.

# Acceptance criteria

- [x] `docs/multichannel/CROSS_PROCESS_DB_ROW_HANDOFF.md` written, comparing
      6 variants, selecting and justifying one composite mechanism.
- [x] PR 1: `cluster_pending_operations` schema (migration 63) +
      `IClusterPendingOperationRepository`/`DbClusterPendingOperationRepository` +
      `IClusterRecordOwnershipResolver`/`DbClusterRecordOwnershipResolver` +
      `ClusterRecordHandoff`, tests per design doc §14 (17/17 real gtest
      passing), no existing call site changed. Merged to `main` (squash
      commit `4de9350`) with explicit user consent ("merge i działaj
      dalej"). Full CI matrix green after two real-CI-driven fixes (Windows
      unity-build symbol collision; migration 63's expected warning firing
      on fresh installs due to a pre-existing `db_version` drift from
      migration 62) - see the CI-repair work log entries below.
- [x] PR 2 implementation complete on branch
      `claude/canary-cross-channel-mail-fix` (based directly on merged
      `main`): `ClusterHandoffRuntime` singleton, `cluster_operation_id`,
      `mail_delivery_payload` (+ shared `hexEncode`/`hexDecode`),
      `MailDeliveryOperationHandler` (`applyOwned`/`applyUnowned`,
      `applyUnowned` guarded by a real row-lock transaction, verified
      against real MariaDB including a genuine two-connection lock-
      contention test), `ClusterRecordHandoff::enqueueAndTryApplyNow` (new,
      lets the enqueuing call site apply synchronously when safe, avoiding
      sweep-interval latency for the common case), `Mailbox::sendItem`
      rewired to resolve cross-channel ownership before ever falling back
      to a local offline load, sweep wired into
      `Game::renewClusterSessions`, singleton configured at startup in
      `CanaryServer::initializeMultichannelCluster` (deliberately outside
      the `CANARY_MULTICHANNEL_REDIS` guard - this mechanism is DB-only).
      25/25 real gtest passing (17 original + 8 new). Not yet committed/
      pushed/PR-opened as of this update - next action.
- [ ] PR 2 pushed, draft PR opened, full CI matrix green.
- [ ] PR 3: `DECISION_MATRIX.md`/`TEST_PLAN.md` updated, this task record's
      Completion section filled in, house-ownership/DIRTY migration plans
      linked (already written in the design doc §12).
- [ ] Current-head GitHub checks verified for all three PRs (full matrix,
      not just fast checks).
- [ ] Module catalogue impact handled (`docs/agents/MODULE_CATALOG.md`).
- [ ] No merge without explicit user "yes, merge #NNN" (standing rule,
      repeated by the user this session).

# Confirmed context

- Verified `origin/main` @ `e94c9db085f25fbd9d76721fc86ca2d40119e676`
  (tip is PR #305, the prior task's archive commit) via `git fetch` +
  `git pull` + `git log -1`. Local `main` had been 200 commits stale before
  this pull - confirms the instruction to never trust a locally cached
  branch state without re-fetching.
- PR #292, #293, #305 are merged (confirmed via `git log --oneline` showing
  all three by title/number on `origin/main`) and must not be
  reimplemented. Their closed scope (`ChannelRuntimeRegistry` heartbeat
  loop, live login-gateway filtering, live Redis `PING`, task-record
  archival) is unrelated to this task's scope - no overlap.
- No open PR or active task record overlaps this scope (checked
  `docs/agents/tasks/active/**` - none mention multichannel/handoff/mail/
  house/DIRTY; checked all open PRs via `mcp__github__list_pull_requests` -
  none touch these files or this problem).
- `docs/multichannel/DECISION_MATRIX.md` row 2.12 and `ARCHITECTURE.md` §8
  already contain an accurate, previously-written description of the
  mail-loss bug's root cause (found while scoping a GM command in an
  earlier phase, deliberately not fixed then) - this task's audit
  independently re-confirmed it by reading the actual current
  `Mailbox::sendItem`/`Game::getPlayerByName` source, not by trusting the
  doc at face value, consistent with this program's established practice.
- **New fact this session's audit found, not previously documented**:
  `IOLoginDataSave::savePlayerInbox`/`savePlayerItem` both do
  `DELETE FROM <table> WHERE player_id = ?` then a full re-insert from the
  live in-memory tree - a *replace*, not a *merge*. This is why a direct
  DB `INSERT` into `player_inboxitems` for an online-elsewhere recipient
  cannot work as a fix on its own (the owning channel's next save deletes
  it) - the mechanism must deliver the *operation* to the *owning
  process's live memory*, not attempt a cleverer direct DB write. This
  fact directly shaped the chosen design (§0/§6.1 of the design doc).
- `cluster_sessions.status = 'DIRTY'` is confirmed (by reading
  `db_cluster_session_repository.cpp`) to never be written by any current
  code path - only `'ONLINE'` upsert or row delete. The DECISION_MATRIX's
  "state reachable and tested" claim for 5.3 is true only at the pure
  `ClusterSessionManager::isValidTransition` logic level, not the real
  engine - recorded so the DIRTY-session follow-up task doesn't assume
  more exists than does.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| `cluster_sessions` + `findOnlineChannelForPlayer` | Player record ownership resolution | `schema.sql`, `cluster_session_lookup.cpp` | Already the exact "who owns this player's live session" answer; not duplicated. |
| `houses.channel_id` | Static house ownership | `schema.sql` | Already fixed routing metadata; no new lookup needed. |
| `IRedisClient::acquireLease/renewLease/releaseLease` + Lua CAS scripts | Generic Redis lease+fencing primitive | `redis_client.hpp`, `redis_scripts/` | Already generalized once (sessions, job leadership); confirms the pattern is reusable, though this task's new mechanism turns out not to need a *new* Redis lease at all (§4.3/§4.7 of the design doc). |
| `channel_switch_audit`'s `consumed_at` column | "Pending until the right process consumes it" precedent | `channel_switch_audit_store.cpp`, migration `61.lua` | The one existing precedent for exactly this shape of problem, generalized from a single one-shot value into a typed, repeatable command inbox. |
| `economic_ledger.transaction_uuid` / `EconomicLedgerStore` | Idempotency key convention (`PRIMARY KEY`-enforced replay rejection) | `economic_ledger_store.cpp`, `economic_ledger_id.cpp` | Identical idempotency contract reused for `cluster_pending_operations.operation_id`. |
| `Item::serializeAttr`/`unserializeAttr` | Per-item attribute (de)serialization outside a whole-player save | `src/items/item.hpp`, `iologindata_save_player.cpp` | Reused for the mail payload instead of inventing a new item-serialization format. |
| `Game::renewClusterSessions` / `g_dispatcher().cycleEvent` | Existing periodic per-channel cycle | `game.cpp` | The new sweep piggybacks here in PR 2, per the explicit "reuse the existing periodic-task mechanism" requirement from this and the prior task's spec. |

# Ownership and overlap check

- Program record: none exists yet for multichannel under
  `docs/agents/programs/` (confirmed via `ls`); not created this task,
  matching the prior task record's same note - left as a possible
  follow-up, not blocking.
- Open PRs inspected: yes, via `mcp__github__list_pull_requests` (state
  open) - #306, #284, #283, #279, #245, #224, none overlapping.
- Active tasks inspected: yes, `docs/agents/tasks/active/**` - none
  overlapping (list: required-ci-gate, the-beginning-* x5,
  wheel-of-destiny-validation, achievements-validation,
  agent-program-ownership, forge-* x5, instance-arena-monster-spawn,
  otbm-storage-dependency-graph, wheel-15-25-runtime-completion).
- Ownership checker result: `tools/agents/task_ownership.py` not run this
  session (Python tool, not exercised - no conflicting claim found by
  manual inspection above; will note as a gap rather than fabricate a
  clean run).
- Exclusive claims: new files only (see `owned_paths.exclusive` above) -
  no existing file is claimed exclusively.
- Shared claims: `schema.sql`, `mailbox.*`, `game.cpp`, build registration
  files, and the multichannel docs - all edited additively, no other
  active task touches them per the check above.
- Read-only dependencies: `cluster_session_lookup.*`, `cluster_runtime.*`,
  `redis_client.hpp`, `house.cpp` - read for design, not modified in PR 1;
  `house.cpp` will need a real (but out-of-scope-for-now) edit in the
  deferred house-ownership follow-up task, not here.
- Overlaps: none found.
- Resolution: n/a.

# Current state

PR 1 (foundation) is merged to `main` (squash commit `4de9350`, user
consent given explicitly for this specific PR: "merge i działaj dalej").
Design doc renamed a few pieces during implementation for clarity/
consistency with the project's `IClusterSessionRepository`/
`DbClusterSessionRepository` split (see Decisions table):
`ClusterPendingOperationStore` became the interface
`IClusterPendingOperationRepository` + impl `DbClusterPendingOperationRepository`;
ownership resolution became its own `IClusterRecordOwnershipResolver` +
`DbClusterRecordOwnershipResolver` pair, injected into `ClusterRecordHandoff`
so the orchestration logic itself is fully unit-testable without a live
database - the design doc's intent is unchanged, only the concrete
interface split is more granular than originally sketched.

PR 2 (mail-loss fix) implementation is complete on branch
`claude/canary-cross-channel-mail-fix`, based directly on merged `main`.
Not yet committed/pushed/opened as a PR - that is the immediate next step.
See the 2026-07-14T11:15:00Z work log entry below for full detail on what
was built, the design decisions made along the way (notably
`enqueueAndTryApplyNow`, added to `ClusterRecordHandoff` itself rather than
duplicated at the call site, and the item-removal-timing analysis that
justified it), and the real-verification evidence gathered.

# Plan

1. Implement `cluster_pending_operations` schema + migration 63.
2. Implement `ClusterPendingOperationStore` (DB layer).
3. Implement `ClusterRecordHandoff` (ownership resolution + apply-or-defer
   orchestration, dispatch table with no handlers registered yet).
4. Register new files in `src/game/CMakeLists.txt` and
   `vcproj/canary.vcxproj`.
5. Write and, where standalone-compilable, actually run the test matrix
   from the design doc §14.
6. Push PR 1, open draft/ready PR, monitor CI.
7. Implement PR 2 (mail fix) on a new branch based on PR 1's foundation
   (or the same branch if splitting turns out impractical - see the design
   doc's own PR split reasoning).
8. Push PR 2, monitor CI.
9. Write PR 3 (docs-only), monitor CI.
10. Do not merge any PR without explicit user "yes, merge #NNN".

# Work log

## 2026-07-14T08:40:00Z

- Changed: created this task record; wrote
  `docs/multichannel/CROSS_PROCESS_DB_ROW_HANDOFF.md`.
- Learned: `IOLoginDataSave::savePlayerInbox`/`savePlayerItem` do a full
  delete+reinsert from live memory on every save - the key fact that rules
  out "just write directly to `player_inboxitems`" as a fix.
- Failed/blocked: none yet.
- Result: design doc complete; starting PR 1 implementation.

## 2026-07-14T09:20:00Z

- Changed: implemented PR 1 foundation - migration 63 + schema.sql,
  `IClusterPendingOperationRepository`/`DbClusterPendingOperationRepository`,
  `IClusterRecordOwnershipResolver`/`DbClusterRecordOwnershipResolver`,
  `ClusterRecordHandoff`, two test fakes, 17 gtest cases (including a real
  16-thread concurrent-apply race test), registered in
  `src/game/CMakeLists.txt`/`tests/unit/game/CMakeLists.txt`/
  `vcproj/canary.vcxproj`.
- Learned: `Database::storeQuery` cannot distinguish "zero matching rows"
  from "a real query/connection error" at the call site (confirmed by
  reading `database.cpp` directly) - every existing store in this codebase
  already accepts that ambiguity for its own "no such row" case, but for
  `DbClusterRecordOwnershipResolver`'s PLAYER_INBOX resolution this
  ambiguity is a real fail-closed correctness question (conflating
  "confirmed offline" with "DB unreachable" would let an uncertain state
  be treated as safe-to-apply-directly). Closed with a cheap `SELECT 1;`
  liveness probe that only runs when the real query returned no rows,
  distinguishing the two without changing `Database`'s own contract.
- Failed/blocked: two real, if minor, mid-implementation corrections: (1)
  `db.getUpdateRows()` does not exist on `Database` - the real method is
  `executeQueryAffectedRows(query) -> std::optional<uint64_t>`, confirmed
  by reading `database.cpp`/`database.hpp` directly and cross-checked
  against its one other real caller (`db_functions.cpp`); (2) a seed
  `players` row insert for the ownership-resolver's real-MariaDB
  verification hit `ERROR 1364 (HY000) - Field 'conditions' doesn't have a
  default value` on a hand-crafted INSERT - fixed by reusing schema.sql's
  own already-seeded sample players instead of crafting new rows (the same
  lesson Phase 12's task history already recorded once for a different
  table - reused here, not rediscovered).
- Result: PR 1 foundation complete and verified (see Validation and CI
  table below). Not yet pushed to PR #308 as of this log entry.

## 2026-07-14T10:35:00Z (CI repair)

- Changed: pushed PR 1 foundation to #308, marked ready for review (it had
  been left draft, which this repo's workflow gates the full build matrix
  behind - `Build - Linux/Windows/macOS/Docker` had all been silently
  `skipped`, not actually run, on the first push; marking ready triggered
  the real matrix).
- **Two real, independent CI failures surfaced, both root-caused:**
  1. `Build - Windows / Compile (Solution)` failed with MSVC C2084:
     `optionalIntToSql` "already has a body". Root cause: Windows' unity/
     jumbo build (MSBuild groups multiple `.cpp` files into one translation
     unit) put `db_cluster_pending_operation_repository.cpp` and the
     pre-existing `economic_ledger_store.cpp` in the same unit; both
     defined an identically-named, identically-signed anonymous-namespace
     helper `optionalIntToSql(const std::optional<int32_t>&)` - harmless
     per-file, a hard collision once unified. Linux/CMake never surfaced
     it (confirmed - only Windows failed on this). **Fixed** by renaming
     mine to `optionalChannelIdToSql`; grepped this PR's other new files
     for any other anonymous-namespace free function to rule out a second
     instance (none - `rowToRecord`/`runPendingQuery` take/return
     `ClusterPendingOperationRecord`, a type unique to this PR's own
     header).
  2. The Linux runtime smoke test failed with "Canary runtime log contains
     warning/error lines" - not a compile error, its log-scanner catching
     migration 63's own expected `logger.warn("...already exists, skipping
     creation")` idempotency-guard line on a fresh-install DB (where
     `schema.sql` already includes the table, so the migration always hits
     the "already exists" branch on first boot). **The repo owner
     (blakinio) intervened directly on this branch** while I was mid-diagnosis
     of the same issue (see below) - pushed `2d1a2b6` removing the
     `logger.warn(...)` call from `63.lua` entirely (silencing the log line
     at its source), after a first attempt (`e5c12a9`, a temporary
     `fix-pr308-migration-warning.yml` workflow) had a YAML syntax error
     (caught by `yamllint`) and was cleaned up (`d1283ef`). A merge commit
     (`84a2278`) then folded in ~10 unrelated commits that had landed on
     `main` in the meantime.
  - I had independently reached a different (also valid, more complete)
    diagnosis for the same symptom: `schema.sql`'s `server_config.
    db_version` seed was still `'61'` even though migration 62's tables
    were already present in `schema.sql` (migration 62 uses a raw `CREATE
    TABLE IF NOT EXISTS` with no explicit check, so it silently never
    triggered this; my migration follows the more explicit,
    established-since-59 `db.tableExists()` + `logger.warn(...)` style,
    which correctly, audibly surfaced the drift). I had a local, uncommitted
    fix bumping `db_version` to `'63'` prepared before discovering the
    owner had already pushed their own resolution.
  - **Reconciliation**: fetched the remote branch, found it 11 commits
    ahead of my last push (the owner's fixes plus the `main` merge).
    Stashed my uncommitted local changes for safety
    (`git stash push -u`), hard-reset my local branch to match the
    remote tip exactly (`git reset --hard origin/claude/canary-cross-process-handoff`
    - safe, since the only local state was the already-stashed diff, no
    commits were discarded), then re-applied *only* the still-unaddressed
    Windows rename fix on top of the owner's own state, **without**
    reverting or fighting their `logger.warn` removal or reintroducing my
    own `db_version` bump - the owner's fix is simpler, already live, and
    a legitimate resolution; overriding it with a competing approach after
    the fact would have been presumptuous. The stash (containing my
    superseded `db_version`/`63.lua` edits) is left untouched as a record,
    not reapplied.
  - Verified after reconciliation: `clang-format-18 --dry-run --Werror`
    clean on the renamed file; `cluster_record_handoff_test.cpp` still
    17/17 passing with real gtest after the rebase.
- Learned: (1) a draft PR on this repo's CI silently skips the full build
  matrix - green-on-draft must never be read as "CI passed," exactly the
  user's own standing instruction; (2) this repo has the owner actively
  monitoring and directly intervening on agent branches for real CI
  failures - always re-fetch before assuming local state is current when
  investigating a failure, never blindly force-push over unfetched remote
  state.
- Result: pushed the Windows fix on top of the owner's own resolution;
  awaiting the next full CI run's result on the reconciled head.

## 2026-07-14T11:15:00Z (PR 2 implementation)

- Context: PR 1 (#308) subsequently went full-CI-green and was merged to
  `main` with the user's explicit, PR-specific consent ("merge i działaj
  dalej" in response to "to wszystko?"). Started PR 2 on a fresh branch
  (`claude/canary-cross-channel-mail-fix`) based directly on the merged
  `main` tip (`4de9350`), per the task's own branch-restart convention for
  a just-merged predecessor.
- Changed (all real-verified, see Validation and CI table below):
  - `src/game/multichannel/cluster_operation_id.hpp/.cpp` - random
    UUID-shaped `operation_id` generator (no natural deterministic key for
    a mail send, unlike `economic_ledger`'s deterministic case).
  - `src/game/multichannel/mail_delivery_payload.hpp/.cpp` - pipe-
    delimited, hex-encoded (de)serialization of everything needed to
    reconstruct a mailed item on another process. `hexEncode`/`hexDecode`
    were initially private to this file; refactored to shared
    `multichannel::` functions (still declared/defined here) once it
    became clear the enqueue side (`Mailbox::sendItem`) and the apply side
    (`MailDeliveryOperationHandler`) both need the *same* byte-exact codec
    - one implementation, not three independent copies.
  - `src/game/multichannel/cluster_handoff_runtime.hpp` - production
    singleton wrapper (`getInstance()`/`configure()`), mirroring
    `ChannelRuntimeRegistry`'s exact shape.
  - `src/game/multichannel/mail_delivery_operation_handler.hpp/.cpp` - the
    `PLAYER_INBOX`/`DELIVER_MAIL_ITEM` handler from design doc §6.1.
    `applyOwned` inserts directly into the confirmed-live recipient's
    `Inbox`. `applyUnowned` wraps the offline throwaway-copy-load-and-save
    path in one explicit transaction that re-verifies (a) this pending-
    operation row is still PENDING, via `SELECT ... FOR UPDATE`, and (b) no
    login raced in since ownership resolved NoLiveOwner, via a plain
    `cluster_sessions` re-check - both immediately before committing.
    Found and fixed one real bug during hand-review before any commit:
    `Mailbox::sendItem` unconditionally transforms *every* mailed item
    (parcels too, not just letters - `ITEM_PARCEL`/`ITEM_PARCEL_STAMPED`
    are a real id pair) to its stamped id after insertion; my first draft
    only did this when a writer was present, which would have left every
    mailed parcel at the wrong item id after a cross-channel delivery -
    caught by re-reading `mailbox.cpp` line-by-line against my draft
    instead of trusting my own summary of it.
  - `src/game/multichannel/cluster_record_handoff.hpp/.cpp` - added
    `enqueueAndTryApplyNow` (new public method) and refactored `sweep`'s
    per-record dispatch into two shared private helpers (`tryApply`,
    `transitionAfterApply`) so both entry points use identical dispatch
    rules. This lets the enqueuing call site (`Mailbox::sendItem`) attempt
    delivery synchronously when it's already safe to (this process is the
    owner, or the record is confirmed NoLiveOwner), instead of always
    waiting for the next periodic sweep - avoiding a real latency
    regression for the common case, while still never calling
    `applyOwned` unless `thisChannelId` is the freshly-resolved owner.
    Returns a 3-state `ClusterRecordHandoffOutcome`
    (`NotEnqueued`/`EnqueuedButFailedDefinitively`/`EnqueuedDurably`) so
    the caller knows precisely when it's safe to treat the source item as
    consumed - see the item-removal-timing analysis below.
  - `src/items/containers/mailbox/mailbox.cpp/.hpp` - `sendItem` now tries
    the local live-player lookup (`allowOffline=false`) first when
    multichannel is enabled, and only falls back to today's
    `allowOffline=true` DB-load behavior when multichannel is *disabled*
    (byte-for-byte the original single-channel code path, otherwise
    untouched). When multichannel is enabled and the recipient isn't found
    locally, the new `sendItemAcrossCluster` resolves the recipient's guid,
    serializes the item into a `MailDeliveryPayload`, and hands it to
    `ClusterHandoffRuntime::enqueueAndTryApplyNow`.
  - `src/game/game.cpp` - sweep call site added to the existing
    `Game::renewClusterSessions` heartbeat cycle (piggybacked, no new
    scheduler), per design doc §10.
  - `src/canary_server.cpp` - `g_clusterHandoffRuntime().configure(...)`
    called at startup, deliberately *outside* the
    `#ifdef CANARY_MULTICHANNEL_REDIS` block (unlike `ClusterRuntime`) -
    this mechanism has no Redis dependency by design, so it should not be
    compiled out in a Redis-less build even though, in practice today,
    `ClusterConfigValidator` already fails closed before reaching this
    point whenever Redis isn't compiled in but multichannel is enabled.
  - Build registration: `src/game/CMakeLists.txt`,
    `tests/unit/game/CMakeLists.txt`, `vcproj/canary.vcxproj` (both
    `ClInclude`/`ClCompile` entries) for all new files.
  - 8 new unit tests added to `cluster_record_handoff_test.cpp` (6 for
    `enqueueAndTryApplyNow`'s outcome contract + 1 for a genuinely new
    concurrency scenario not covered by PR 1: two *distinct* mail
    operations - different `operation_id`, same offline recipient -
    applying concurrently must both succeed, neither lost, neither
    silently overwriting the other).
- Design decision requiring real analysis, not just implementation - **when
  is it safe to remove the physical item from the sender's mailbox?**
  Considered removing it immediately upon `enqueue()` succeeding, but
  rejected: `Mailbox::sendItem`'s original single-channel code only ever
  moves the item *after* `internalMoveItem`'s own capacity/validity check
  passes, so a "destination rejected it" failure never destroys the
  source item today. Removing it unconditionally on enqueue could destroy
  it even when a later, asynchronous apply attempt (by a different
  channel's own sweep) fails definitively - a real, if narrow, item-loss
  regression. Resolved by having `enqueueAndTryApplyNow` report a 3-state
  outcome and having `sendItemAcrossCluster` remove the item only for
  `EnqueuedDurably` (delivered synchronously, or safely deferred to a
  later owner-resolved sweep), never for `NotEnqueued` or
  `EnqueuedButFailedDefinitively`. One residual, bounded gap remains and is
  recorded here rather than hidden: if the *deferred* case (owned by
  another channel, or ownership unresolvable at send time) is later
  rejected asynchronously by that owner's own sweep (e.g. a structural
  item-reconstruction failure), the item is already gone with no return-
  to-sender path - this mirrors the *existing*, already-accepted risk
  profile of `FLAG_NOLIMIT`-bypassed rejections in the original single-
  channel code (capacity itself can never trigger this, since `FLAG_NOLIMIT`
  is passed on both the original and new code paths - confirmed by reading
  `items_definitions.hpp`), just newly reachable through an async path
  with a `FAILED` audit row for diagnosis instead of a synchronous return
  value. Return-to-sender is out of scope for this task (would require
  serializing sender identity into the payload and a second delivery
  path) - flagged as a real, small, follow-up-worthy gap, not silently
  accepted.
- Real-verification highlight: used two genuinely separate `mysql` client
  connections (not simulated) to prove `applyUnowned`'s
  `SELECT ... FOR UPDATE` lock query actually serializes at the database
  level, not just in application logic - session B's lock request measurably
  blocked (~2.5s, matching session A's `SLEEP(3)`) until session A
  committed, and then correctly observed session A's `APPLIED` status
  instead of the stale `PENDING` it saw before blocking.
- Result: PR 2 implementation complete, format-clean, 25/25 real gtest
  passing (17 original + 8 new), SQL hand-verified against real MariaDB
  including a genuine cross-connection lock-contention test. Not yet
  committed, pushed, or opened as a PR as of this log entry - next action.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Command inbox (`cluster_pending_operations`) is DB-only, no new Redis lease | Durability across a Redis outage is the mechanism's entire purpose; ownership resolution already reuses existing Redis-backed `cluster_sessions` unchanged | none yet |
| No per-operation lease/claim before applying | Exactly one process can ever be the live owner at a given instant already (via `cluster_sessions`/static `channel_id`); a lease would arbitrate a race that cannot occur | none yet |
| Reuse `cluster_sessions`/`houses.channel_id` for ownership instead of a new generic ownership table | Avoids a second source of truth for the same fact, per this program's own established "one authoritative representation" principle | none yet |
| `record_kind`/`operation_type` as strings, not DB enums | New consumer kinds (house, future ones) are data, not a schema migration | none yet |
| House double-ownership fix and DIRTY session tooling deferred to a follow-up task | Explicit user instruction this session; migration plan written now (design doc §12) so the follow-up isn't starting from zero | none yet |
| Split into `I*Repository`/`Db*` interface pairs (mirroring `IClusterSessionRepository`) instead of the design doc's original static-method sketch | Needed so `ClusterRecordHandoff`'s ownership/apply-or-defer logic is unit-testable against fakes, matching this project's own established testability pattern - decided during implementation, not a design change, just a more granular interface split | none yet |
| Tri-state `ClusterRecordOwnershipOutcome` (OwnedByChannel/NoLiveOwner/Unknown) instead of `std::optional<int32_t>` | A bool+optional pair cannot represent "cannot currently confirm" distinctly from "confirmed no owner" in one atomic call - the distinction is load-bearing for fail-closed correctness (design doc §14 test 12) | none yet |
| Added `ClusterRecordHandoff::enqueueAndTryApplyNow`, refactoring `sweep`'s dispatch into shared private helpers, instead of a sweep-only apply path | Waiting for the next periodic sweep tick for every mail send would be a real latency regression vs. today's synchronous delivery; the shared helpers guarantee both entry points use identical ownership/apply rules, so this isn't a second, divergent dispatch implementation | none yet |
| `hexEncode`/`hexDecode` promoted from `mail_delivery_payload.cpp`'s anonymous namespace to shared `multichannel::` functions | Both the enqueue side (`Mailbox::sendItem`) and the apply side (`MailDeliveryOperationHandler`) need the *same* byte-exact codec for `itemAttributesHex`; one shared implementation instead of a second/third hand-copied version reduces drift risk | none yet |
| Item removed from the sender's mailbox only on `EnqueuedDurably`, never on `NotEnqueued`/`EnqueuedButFailedDefinitively` | Matches the original single-channel code's own invariant that a rejected destination never destroys the source item; a bounded, documented residual gap remains for asynchronous rejections of a *deferred* (not synchronously-attempted) delivery - see the PR 2 work log entry | none yet |
| `ClusterHandoffRuntime::configure()` called outside the `CANARY_MULTICHANNEL_REDIS` `#ifdef` in `canary_server.cpp` | This mechanism is deliberately DB-only with no Redis dependency (design doc §4.7) - it should not be compiled out of a hypothetical future Redis-less multichannel build, even though `ClusterConfigValidator` currently always fails closed before reaching this point in that configuration | none yet |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `docs/multichannel/CROSS_PROCESS_DB_ROW_HANDOFF.md` | exclusive | Design document | done |
| `data-otservbr-global/migrations/63.lua` | exclusive | `cluster_pending_operations` schema | done, real-MariaDB verified |
| `schema.sql` | shared | Same table, fresh-install path | done, real-MariaDB verified |
| `src/game/multichannel/cluster_pending_operation_repository.hpp` | exclusive | `IClusterPendingOperationRepository` interface | done |
| `src/game/multichannel/db_cluster_pending_operation_repository.hpp/.cpp` | exclusive | Real DB-backed implementation | done, SQL hand-verified against real MariaDB (mysql wall - not standalone-compilable, same as `db_cluster_session_repository.cpp`) |
| `src/game/multichannel/cluster_record_ownership.hpp` | exclusive | `IClusterRecordOwnershipResolver` interface + tri-state outcome | done, standalone-compiled (dependency-free) |
| `src/game/multichannel/db_cluster_record_ownership_resolver.hpp/.cpp` | exclusive | Real DB-backed implementation | done, SQL hand-verified against real MariaDB (mysql wall) |
| `src/game/multichannel/cluster_record_handoff.hpp/.cpp` | exclusive | Ownership resolution + apply orchestration | done, standalone-compiled with `-Wall -Wextra` (zero warnings) |
| `tests/shared/game/multichannel/fake_cluster_pending_operation_repository.hpp` | exclusive | Test double | done |
| `tests/shared/game/multichannel/fake_cluster_record_ownership_resolver.hpp` | exclusive | Test double | done |
| `tests/unit/game/multichannel/cluster_record_handoff_test.cpp` | exclusive | Unit tests, 17 cases | done, **run with real gtest, 17/17 passed** |
| `src/game/CMakeLists.txt`, `tests/unit/game/CMakeLists.txt`, `vcproj/canary.vcxproj` | shared | Build registration (PR 1 + PR 2 files) | done |
| `src/game/multichannel/cluster_operation_id.hpp/.cpp` | exclusive | Random operation_id generator | done, standalone-compiled + 3/3 real gtest |
| `src/game/multichannel/mail_delivery_payload.hpp/.cpp` | exclusive | Payload (de)serialization + shared hex codec | done, standalone-compiled + 9/9 real gtest |
| `src/game/multichannel/cluster_handoff_runtime.hpp` | exclusive | Production singleton wrapper | done, standalone-verified via `-fsyntax-only` (header-only) |
| `src/game/multichannel/mail_delivery_operation_handler.hpp/.cpp` | exclusive | `PLAYER_INBOX`/`DELIVER_MAIL_ITEM` handler | done, hand-reviewed against exact API signatures + SQL hand-verified against real MariaDB (mysql/game.hpp wall - not standalone-compilable) |
| `src/game/multichannel/cluster_record_handoff.hpp/.cpp` | exclusive | + `enqueueAndTryApplyNow`, dispatch refactor | done, standalone-compiled, 25/25 real gtest (17 original unchanged-behavior + 8 new) |
| `src/items/containers/mailbox/mailbox.cpp/.hpp` | shared | Cross-channel `sendItem` rewrite | done, hand-reviewed against exact API signatures (not standalone-compilable) |
| `src/game/game.cpp` | shared | PR 2 sweep call site in `renewClusterSessions` | done |
| `src/canary_server.cpp` | shared | `ClusterHandoffRuntime::configure()` startup wiring | done |
| `tests/unit/game/multichannel/cluster_operation_id_test.cpp` | exclusive | Unit tests, 3 cases | done, run with real gtest |
| `tests/unit/game/multichannel/mail_delivery_payload_test.cpp` | exclusive | Unit tests, 9 cases | done, run with real gtest |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| (pre-commit) | `clang-format-18 --dry-run --Werror` on all 11 new C++ files | passed | exit 0 after one auto-`-i` fix (pointer-alignment style in `cluster_record_ownership.hpp`/test file) |
| (pre-commit) | Standalone `g++ -std=c++20 -Wall -Wextra` compile of `cluster_record_handoff.cpp` | passed | zero warnings - this file has no `database.hpp`/`game.hpp` dependency |
| (pre-commit) | Standalone compile+link+run of `cluster_record_handoff_test.cpp` against real `libgtest`/`libgtest_main` | passed | **17/17 tests passed**, including a genuine 16-thread concurrent-apply race test (`ConcurrentSweepOfNoLiveOwnerRecordHasExactlyOneWinner`), run 5x to confirm no flakiness |
| (pre-commit) | Attempted standalone compile of `db_cluster_pending_operation_repository.cpp`/`db_cluster_record_ownership_resolver.cpp` | expected failure, confirmed | hits the same pre-existing wall as `db_cluster_session_repository.cpp` (`database.hpp` → `declarations.hpp` → the full PCH-dependent engine graph) - tried with `libmariadb-dev` header shim first, per this project's "try before assuming" precedent; got past `mysql.h` but failed on `creatures_definitions.hpp`'s PCH-dependent `<array>`/`<ranges>` usage, confirming the wall is the engine graph, not just mysql.h |
| (pre-commit) | Real MariaDB 10.11 (`service mariadb start`, scratch DB `canary_handoff_test`) - fresh `schema.sql` import including the new table | passed | clean import, `SHOW CREATE TABLE cluster_pending_operations` matches the design exactly |
| (pre-commit) | Real MariaDB - exact `enqueue` SQL, replayed with a duplicate `operation_id` | passed | first INSERT succeeds; replay correctly rejected with `ERROR 1062 Duplicate entry ... for key 'PRIMARY'`, matching `economic_ledger.transaction_uuid`'s contract |
| (pre-commit) | Real MariaDB - exact `markApplied` SQL, called twice on the same row | passed | first call: 1 affected row, transitions to APPLIED; second call: 0 affected rows (guarded by `WHERE status='PENDING'`), `attempts`/`applied_at` unchanged from the first - confirms the double-transition race guard |
| (pre-commit) | Real MariaDB - `findPendingForKind`/`findPendingForRecord`/`countStalePending` exact SQL against 4 seeded rows across 2 record kinds and 3 statuses | passed | correct kind/status isolation confirmed (a HOUSE row never appears in a PLAYER_INBOX sweep query); `EXPLAIN` confirms index usage (`status_created_at`) |
| (pre-commit) | Real MariaDB - `markFailed`/`markAbandoned` exact SQL | passed | both transition correctly and record the reason in `last_error` |
| (pre-commit) | Real MariaDB - migration 63 idempotency, simulating `db.tableExists()`'s guard on a fresh pre-63 DB | passed | first run: table absent, CREATE executes; second simulated run: table present, guard would skip (matches every prior migration's convention) |
| (pre-commit) | Real MariaDB - `DbClusterRecordOwnershipResolver`'s exact SQL (houses.channel_id lookup, cluster_sessions ONLINE lookup found/not-found, `SELECT 1` liveness probe) | passed | house lookup returns the seeded `channel_id=2`; online-elsewhere lookup returns `channel_id=5` for a seeded ONLINE row; not-online lookup correctly returns empty (the NoLiveOwner case); liveness probe returns `1` |
| `4de9350` (merged) | Full CI matrix (Linux/Windows/macOS/Docker) on PR #308 | passed | Green after the Windows unity-build rename and the repo owner's `db_version`-drift fix, both described in the CI-repair log entry above; merged by explicit user consent |
| (pre-commit, PR 2) | `clang-format-18 --dry-run --Werror` on all PR 2 files (new + modified) | passed | exit 0, zero diffs |
| (pre-commit, PR 2) | Standalone compile+link+run of `mail_delivery_payload_test.cpp`/`cluster_operation_id_test.cpp` against real gtest | passed | 9/9 and 3/3 respectively |
| (pre-commit, PR 2) | Standalone compile+link+run of `cluster_record_handoff_test.cpp` (post-refactor) | passed | **25/25 tests passed** (17 original, confirming the `sweep` refactor is behavior-preserving, + 8 new for `enqueueAndTryApplyNow` and the two-distinct-concurrent-deliveries scenario); new concurrency test re-run 5x to confirm no flakiness |
| (pre-commit, PR 2) | Real MariaDB - fresh `schema.sql` import into a new scratch DB | passed | clean import |
| (pre-commit, PR 2) | Real MariaDB - `applyUnowned`'s exact `SELECT ... FOR UPDATE` lock query + `cluster_sessions` online-check query, single connection | passed | lock query correctly returns `PENDING` on a fresh row and `APPLIED`/other on an already-resolved row; online-check query correctly returns a row only when a matching `ONLINE` `cluster_sessions` row exists |
| (pre-commit, PR 2) | Real MariaDB - **two genuinely separate connections**, session A holds the row lock inside an open transaction with a 3s `SLEEP`, session B attempts the same `FOR UPDATE` concurrently | passed | session B measurably blocked (~2.5s) until session A committed, then correctly observed A's post-commit `APPLIED` status - proves the lock is real at the DB engine level, not merely an application-level check |
| | Full CI matrix (Linux/Windows/macOS/Docker) for PR 2 | not-run | Not yet pushed/opened as of this update |

Never write `passed` without verification on the stated commit.

# Failed approaches and dead ends

- Considered a direct DB `INSERT`/`UPDATE` into `player_inboxitems`/
  `houses` from the non-owning process, guarded only by a fencing-token
  check. Rejected once `savePlayerInbox`'s delete+reinsert-from-memory
  behavior was confirmed by reading the actual save code - a guarded
  direct write still loses the race against the owning process's own next
  save, which has no way to know the write happened. This is why the
  chosen mechanism delivers *operations* to the *owning process's memory*
  instead of ever writing the target table directly for an
  online-elsewhere record.
- Considered a single generic `cluster_record_ownership` table (duplicating
  `cluster_sessions`' job for players). Rejected - would be a second
  source of truth for "is this player online and where," directly against
  this program's own already-stated principle from `DECISION_MATRIX.md`'s
  `cluster_sessions` primary-key-shape reasoning.

# Risks and compatibility

- Runtime: new sweep added to an existing dispatcher cycle - additive,
  gated behind `multiChannelEnabled` (§10 of the design doc); no new
  scheduler.
- Data/migration: purely additive `CREATE TABLE IF NOT EXISTS`, no existing
  table altered, matches every migration since 59.
- Security: `payload` may carry user-authored mail text - never logged in
  full (§7 of the design doc); no credentials ever touch this table.
- Backward compatibility: inert in single-channel mode (§10).
- Cross-repo rollout: none - server-internal only.
- Rollback: revert commit(s); the new table has no other table's foreign
  key pointing into it, so dropping it is non-destructive to anything else.

# Remaining work

1. ~~Implement PR 1 (foundation)~~ - done, merged (`4de9350`).
2. ~~Implement PR 2 (mail fix)~~ - implementation done on
   `claude/canary-cross-channel-mail-fix`, based on merged `main`.
3. Commit + push PR 2, open as a PR (draft first, mark ready-for-review to
   trigger the full matrix - this repo's CI silently skips the heavy jobs
   on draft, learned the hard way during PR 1's CI repair).
4. Monitor PR 2's full CI matrix; fix any real failures the same way PR 1's
   were fixed (root-cause, minimal fix, re-run, record in this log).
5. Implement PR 3 (docs: `DECISION_MATRIX.md`/`TEST_PLAN.md` updates, this
   task record's Completion section, link the already-written house-
   ownership/DIRTY migration plans from design doc §12).
6. Do not merge PR 2 or PR 3 without a separate, specific user "yes, merge
   #NNN" for each (standing rule, repeated by the user this session).
7. Once all PRs are merged, archive this task record and fill in
   Completion.

# Handoff

## Start here

If resuming: read `docs/multichannel/CROSS_PROCESS_DB_ROW_HANDOFF.md`
first (the design is already decided and justified), then check
`git log --oneline -10` on this branch against the Plan section above.

## Do not repeat

Do not re-litigate the variant comparison in the design doc without new
evidence - it was written against a full audit of the existing lease/
fencing/session/house/mail code, not from the spec alone. Do not attempt
the house-ownership or DIRTY-session fixes in this task - both are
explicitly deferred (see design doc §12 for their migration plan).

## Required reads

- `AGENTS.md`
- `docs/multichannel/CROSS_PROCESS_DB_ROW_HANDOFF.md` (this task's own
  design doc - required, not optional)
- `docs/multichannel/ARCHITECTURE.md` §5, §7, §8 (sessions, houses,
  economy - the three existing analogs this design builds on)
- `src/game/multichannel/cluster_session_lookup.{hpp,cpp}`,
  `channel_switch_audit_store.{hpp,cpp}`, `economic_ledger_store.{hpp,cpp}`
- `src/items/containers/mailbox/mailbox.cpp`,
  `src/io/functions/iologindata_save_player.cpp`

## Open questions

None blocking; proceeding with the plan above.

# Completion

- Final status: in progress
- PR:
- Merge commit:
- Program record updated: no (none exists yet for multichannel)
- Catalogue updated: pending
- Changelog updated: pending
- Archived at: pending
