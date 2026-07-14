---
task_id: CAN-20260714-cross-process-db-row-handoff
program_id: CAN-PROGRAM-MULTICHANNEL
coordination_id: ""
status: in_progress
agent: "claude"
branch: claude/canary-cross-process-handoff
base_branch: main
created: 2026-07-14T08:40:00Z
updated: 2026-07-14T08:40:00Z
last_verified_commit: e94c9db085f25fbd9d76721fc86ca2d40119e676
risk: medium
related_issue: ""
related_pr: ""
depends_on: []
blocks:
  - "house double-ownership fix (deferred, needs this foundation)"
  - "DIRTY session recovery/admin tooling (deferred, needs this foundation)"
owned_paths:
  exclusive:
    - src/game/multichannel/cluster_pending_operation_store.hpp
    - src/game/multichannel/cluster_pending_operation_store.cpp
    - src/game/multichannel/cluster_record_handoff.hpp
    - src/game/multichannel/cluster_record_handoff.cpp
    - data-otservbr-global/migrations/63.lua
    - tests/unit/game/multichannel/cluster_pending_operation_store_test.cpp
    - tests/unit/game/multichannel/cluster_record_handoff_test.cpp
    - docs/multichannel/CROSS_PROCESS_DB_ROW_HANDOFF.md
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
- [ ] PR 1: `cluster_pending_operations` schema (migration 63) +
      `ClusterPendingOperationStore` + `ClusterRecordHandoff`, tests per
      design doc §14, no existing call site changed.
- [ ] PR 2: `Mailbox::sendItem` cross-channel fix using PR 1's foundation,
      tests per the design doc's mail-specific list.
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

Design doc complete (`docs/multichannel/CROSS_PROCESS_DB_ROW_HANDOFF.md`).
Implementation of PR 1 (foundation) starting next.

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

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Command inbox (`cluster_pending_operations`) is DB-only, no new Redis lease | Durability across a Redis outage is the mechanism's entire purpose; ownership resolution already reuses existing Redis-backed `cluster_sessions` unchanged | none yet |
| No per-operation lease/claim before applying | Exactly one process can ever be the live owner at a given instant already (via `cluster_sessions`/static `channel_id`); a lease would arbitrate a race that cannot occur | none yet |
| Reuse `cluster_sessions`/`houses.channel_id` for ownership instead of a new generic ownership table | Avoids a second source of truth for the same fact, per this program's own established "one authoritative representation" principle | none yet |
| `record_kind`/`operation_type` as strings, not DB enums | New consumer kinds (house, future ones) are data, not a schema migration | none yet |
| House double-ownership fix and DIRTY session tooling deferred to a follow-up task | Explicit user instruction this session; migration plan written now (design doc §12) so the follow-up isn't starting from zero | none yet |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `docs/multichannel/CROSS_PROCESS_DB_ROW_HANDOFF.md` | exclusive | Design document | done |
| `data-otservbr-global/migrations/63.lua` | exclusive | `cluster_pending_operations` schema | planned |
| `schema.sql` | shared | Same table, fresh-install path | planned |
| `src/game/multichannel/cluster_pending_operation_store.hpp/.cpp` | exclusive | DB layer | planned |
| `src/game/multichannel/cluster_record_handoff.hpp/.cpp` | exclusive | Ownership resolution + apply orchestration | planned |
| `tests/unit/game/multichannel/cluster_pending_operation_store_test.cpp` | exclusive | Unit tests | planned |
| `tests/unit/game/multichannel/cluster_record_handoff_test.cpp` | exclusive | Unit tests | planned |
| `src/items/containers/mailbox/mailbox.cpp` | shared | PR 2 fix | planned |
| `src/game/game.cpp` | shared | PR 2 sweep call site | planned |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| | | not-run | PR 1 not yet implemented as of this record's creation |

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

1. Implement PR 1 (foundation) per the Plan section above.
2. Implement PR 2 (mail fix).
3. Implement PR 3 (docs).
4. Monitor full CI matrix on all three; fix real failures.
5. Do not merge without explicit user "yes, merge #NNN".
6. Once all three are merged, archive this task record and fill in
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
