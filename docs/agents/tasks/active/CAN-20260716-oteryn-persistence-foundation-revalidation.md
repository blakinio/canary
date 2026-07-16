---
task_id: CAN-20260716-oteryn-persistence-foundation-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: "OAM-004"
status: blocked
agent: oteryn-architecture-migration-agent
branch: docs/oam-004-persistence-foundation-revalidation
base_branch: main
created: 2026-07-16T10:20:00+02:00
updated: 2026-07-16T15:28:00+02:00
last_verified_commit: "63e45afe684e5f923bc004a59687a5adcaac6f01"
risk: high
related_issue: ""
related_pr: "420"
depends_on:
  - OAM-003
blocks:
  - OAM-005
  - OAM-006
  - OAM-007
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260716-oteryn-persistence-foundation-revalidation.md
    - docs/agents/OTERYN_OAM_004_PERSISTENCE_FOUNDATION_REVALIDATION.md
  shared:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
  read_only:
    - docs/architecture/oteryn-target-server-architecture.md
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/real-tibia/registry/modules/database-connection.yaml
    - docs/agents/real-tibia/registry/modules/database-migrations.yaml
    - docs/agents/real-tibia/registry/modules/player-persistence.yaml
    - docs/agents/real-tibia/registry/modules/world-persistence.yaml
    - docs/agents/real-tibia/TSD_002B_PERSISTENCE_TRANSACTIONS_REPORT.md
    - blakinio/Otheryn@4b5b94eced0f3c5d88b9a4293e849d888333e0cb
    - blakinio/canary@63e45afe684e5f923bc004a59687a5adcaac6f01
    - opentibiabr/canary@a879c9312e34381e8eedf397b8ed44510698b689
modules_touched:
  - database-connection
  - database-migrations
  - player-persistence
  - world-persistence
reuses:
  - docs/agents/real-tibia/TSD_002B_PERSISTENCE_TRANSACTIONS_REPORT.md
  - docs/agents/BUILD_TEST_MATRIX.md
  - docs/agents/KNOWN_RISKS.md
  - docs/agents/MODULE_CATALOG.md
public_interfaces:
  - OAM-004 persistence foundation migration dispositions
cross_repo_tasks:
  - blakinio/Otheryn#7
  - blakinio/Otheryn#8
  - blakinio/Otheryn#9
  - blakinio/Otheryn#10
  - blakinio/Otheryn#11
  - blakinio/Otheryn#12
  - blakinio/Otheryn#13
  - blakinio/Otheryn#14
---

# Goal

Revalidate the four canonical Oteryn database/persistence foundation modules against exact target, legacy and upstream baselines; assign evidence-backed dispositions; deliver bounded target adaptations required by those dispositions; and stop before OAM-005.

# Current dispositions

| Module | Disposition | Reason |
|---|---|---|
| `database-connection` | `ADAPT` | task-start DB core allowed silent reconnect/replay, callback-false commit and unsafe BEGIN/lock ordering |
| `database-migrations` | `ADAPT` | task-start migration chain was fail-open and could advance version after earlier failure |
| `world-persistence` | `ADAPT` | task-start house rollback and aggregate save failure visibility were insufficient |
| `player-persistence` | `ADAPT` | player SQL transaction existed, but wheel KV staging crossed the SQL transaction boundary and failure propagation was not uniform |

# PROVEN completed target work

## OAM-004A — database transaction integrity

- Target PR `blakinio/Otheryn#11` merged as `45ffe6afb915746c69125c9e74f5513c0cecdec4`.
- Disabled silent MySQL auto-reconnect and arbitrary SQL statement resend.
- Transaction lock is acquired before `BEGIN`.
- Generic transaction callback `false` rolls back instead of committing.
- Failed transaction begin restores local transaction state.
- Full exact-head cross-platform/runtime/database validation passed before merge.

## OAM-004B — fail-closed database migrations

- Target PR `blakinio/Otheryn#12` merged as `1fe44d165fd8637e29ece62b261b7caa33895c65`.
- Migration chain stops at first load/call/runtime/result/persistence failure.
- `db_version` advances only after accepted migration and durable version write.
- Compatibility contract: historical `nil` = success, `true` = success, `false` = explicit failure, other result types = failure.
- Normal server startup aborts when migration update fails.
- Migration metadata lookup uses the active connection schema via `DATABASE()` rather than a potentially divergent configured DB name.
- Startup migration Lua state does not expose async DB APIs.
- Focused unit and MariaDB integration tests passed on final exact head.

## OAM-004C — world-save failure propagation

- Target PR `blakinio/Otheryn#13` merged as `4b5b94eced0f3c5d88b9a4293e849d888333e0cb`.
- `IOGuild::saveGuild()` now exposes DB write success/failure.
- `SaveManager::saveGuild()`, `saveMap()` and `saveKV()` propagate status.
- Synchronous `SaveManager::saveAll()` returns an aggregate result while preserving best-effort continuation across independent save domains.
- Scheduled asynchronous save logs aggregate failure.
- Player save transaction ownership was intentionally not changed by OAM-004C.
- MariaDB integration regression proof verifies `DBTransaction` false-callback rollback; `IOMapSerialize::saveHouseItems()` directly uses that helper and returns its guard result, so failed replacement inherits the proven rollback contract.
- Final exact head `79cda51b8ad8ecbff224110377e4b2c8e689807e` passed autofix, Fast Checks, Lua Tests, full cross-platform CI #69, Linux debug runtime/schema/full tests and Required #69 before merge.

# ACTIVE target work

## OAM-004D — player SQL / wheel KV save boundary

Target PR: `blakinio/Otheryn#14`

Issue: `blakinio/Otheryn#10`

Task-start target:

```text
blakinio/Otheryn@4b5b94eced0f3c5d88b9a4293e849d888333e0cb
```

Current exact PR head:

```text
079a69e606896040739103638bc1f87aa07607a7
```

PROVEN implementation boundary:

- main `IOLoginData::savePlayer()` path owns one player SQL transaction;
- SQL-backed online-player save sequence was separated from wheel KV cache staging;
- transaction-owned save guard executes only SQL-backed persistence;
- after successful SQL commit, four Wheel of Destiny KV cache mutations are staged;
- SQL transaction failure prevents wheel KV staging;
- post-commit wheel KV staging exceptions make `savePlayer()` return false;
- public `saveOnlyDataForOnlinePlayer()` preserves its historical SQL + KV behavior because complete direct-call-site absence was not proven;
- durable KV persistence remains `KVSQL::saveAll()` and OAM-004C already propagates its boolean result through aggregate server save.

Explicit unresolved limitations:

- player SQL commit and later KV durable flush are not atomic; crash between them can still lose staged wheel KV changes;
- `KVStore::processEvictions()` may persist evicted entries while ignoring backend `save()` failure; this is a generic KV subsystem reliability gap outside OAM-004D scope;
- no deterministic test seam currently forces a late player SQL sub-save failure while inspecting private wheel KV cache without a broad mock/injection refactor, so no stronger test claim is made.

LIVE merge gate verified for PR #14:

- PR state: open, ready, mergeable=true;
- exact head: `079a69e606896040739103638bc1f87aa07607a7`;
- ready-triggered `CI #73`: PASS;
- `Required #73`: PASS;
- `autofix.ci #66`: PASS;
- comments: none;
- submitted reviews: none;
- unresolved review threads: none.

The exact next target action is therefore to re-check that PR #14 head is still `079a69e606896040739103638bc1f87aa07607a7`, then squash-merge with exact-head guard if mergeable/review state remains clean. After merge, close issue #10 and pin the resulting `Otheryn:main` SHA.

# Remaining OAM-004 governance work

Canary governance PR: `blakinio/canary#420`

Current live state observed during this handoff:

```text
state: open
draft: true
mergeable: true
head branch: docs/oam-004-persistence-foundation-revalidation
head SHA before this handoff update: 2e45743a5101aa28b378190e0c2288e1acddfb4b
changed files before this handoff update: 2
```

PR #420 durable content is stale relative to completed A/B/C and active D; this task checkpoint is the handoff source of truth until the report/program are refreshed.

After OAM-004D merge:

1. Pin final `Otheryn:main` SHA after PR #14.
2. Update `docs/agents/OTERYN_OAM_004_PERSISTENCE_FOUNDATION_REVALIDATION.md` with final A/B/C/D results and exact merge SHAs.
3. Update `docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md` so OAM-004 is ready for feature merge; keep OAM-005 inactive until OAM-004 feature merge plus lifecycle archive.
4. Update this task from `blocked` to repository-valid `ready` once all target slices are merged and exact final target SHA is pinned.
5. Verify final PR #420 changed files, ownership, exact-head CI, comments, reviews and unresolved threads.
6. Mark PR #420 ready and use the latest ready-triggered exact-head CI as the merge gate.
7. Squash-merge PR #420 with exact-head guard.
8. Create a separate lifecycle-only PR moving this task from `tasks/active` to `tasks/archive` and marking OAM-004 completed in the program queue.
9. Do not start OAM-005 until that lifecycle PR merges.

# Do not repeat / rejected hypotheses

- Do not infer ACID/retry/crash safety from presence of `DBTransaction`.
- Do not re-enable MySQL auto-reconnect or arbitrary statement replay.
- Do not redesign OAM-004B migration semantics; they are already merged and validated.
- Do not duplicate the OAM-004A house rollback fix inside world serializers; OAM-004C added regression evidence for the shared transaction contract.
- Do not invent one giant transaction across players, guilds, houses, map and KV.
- Do not broaden OAM-004D into generic KV subsystem redesign.
- Do not claim SQL + KV atomicity; it remains explicitly unresolved.
- Do not start OAM-005 mechanically after target PR #14; Canary OAM-004 governance merge and lifecycle archive must complete first.
- GitHub code search was unreliable for some known symbols; negative search results are not absence proof.

# UNKNOWN / residual risk

- Complete crash/restart recovery semantics for untouched persistence paths remain unresolved.
- SQL commit followed by later KV flush remains a non-atomic durability boundary.
- Generic KV eviction persistence failure handling remains outside OAM-004D.
- Final OAM-004 governance merge SHA and lifecycle merge SHA are not yet known.

# Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T15:28:00+02:00
branch: docs/oam-004-persistence-foundation-revalidation
pr: 420
status: blocked
context_routes:
  - agent-governance
  - database-persistence
proven:
  - OAM-004A PR 11 merged as 45ffe6afb915746c69125c9e74f5513c0cecdec4
  - OAM-004B PR 12 merged as 1fe44d165fd8637e29ece62b261b7caa33895c65
  - OAM-004C PR 13 merged as 4b5b94eced0f3c5d88b9a4293e849d888333e0cb
  - OAM-004D PR 14 exact head is 079a69e606896040739103638bc1f87aa07607a7
  - OAM-004D CI 73 PASS
  - OAM-004D Required 73 PASS
  - OAM-004D autofix 66 PASS
  - OAM-004D review threads reviews and comments are empty
  - all four OAM-004 canonical modules have disposition ADAPT
  - OAM-005 remains blocked until OAM-004 feature and lifecycle completion
derived:
  - PR 14 is ready for final exact-head merge check and squash merge
  - after PR 14 merge the remaining work is Canary governance finalization and lifecycle archive
unknown:
  - final OAM-004D merge SHA
  - final Otheryn main SHA after OAM-004D
  - final Canary OAM-004 feature merge SHA
  - OAM-004 lifecycle merge SHA
conflicts: []
first_failure:
  marker: none active
  evidence: OAM-004D exact-head CI and Required are green
rejected_hypotheses:
  - DBTransaction presence proves persistence safety
  - legacy or upstream baseline can be reused without adaptation
  - world persistence needs one giant cross-domain transaction
  - player SQL and KV persistence are fully atomic after OAM-004D
next_action: Re-verify PR 14 exact head 079a69e606896040739103638bc1f87aa07607a7, mergeability and review state; squash-merge with exact-head guard if unchanged, then close issue 10 and pin final Otheryn main SHA.
```
