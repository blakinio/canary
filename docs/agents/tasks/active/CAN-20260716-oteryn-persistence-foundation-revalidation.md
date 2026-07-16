---
task_id: CAN-20260716-oteryn-persistence-foundation-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: "OAM-004"
status: ready
agent: oteryn-architecture-migration-agent
branch: docs/oam-004-persistence-foundation-revalidation
base_branch: main
created: 2026-07-16T10:20:00+02:00
updated: 2026-07-16T18:06:17+02:00
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
    - blakinio/Otheryn@67212530b03c10175da2c0d9eabcee8991a05924
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

# Final dispositions

| Module | Disposition | Result |
|---|---|---|
| `database-connection` | `ADAPT` | transaction/reconnect failure semantics hardened by OAM-004A |
| `database-migrations` | `ADAPT` | migration chain and version advancement made fail closed by OAM-004B |
| `world-persistence` | `ADAPT` | save result propagation delivered by OAM-004C; house rollback inherits shared DB transaction fix |
| `player-persistence` | `ADAPT` | player SQL and post-commit wheel KV staging boundary separated by OAM-004D |

# PROVEN completed target work

## OAM-004A — database transaction integrity

- PR `blakinio/Otheryn#11` merged as `45ffe6afb915746c69125c9e74f5513c0cecdec4`.
- Silent MySQL auto-reconnect disabled.
- Arbitrary SQL statement replay removed.
- Transaction lock acquired before `BEGIN`.
- Callback `false` rolls back rather than commits.
- Failed transaction begin restores local transaction state.

## OAM-004B — fail-closed database migrations

- PR `blakinio/Otheryn#12` merged as `1fe44d165fd8637e29ece62b261b7caa33895c65`.
- Migration chain stops on first failure.
- `db_version` advances only after accepted migration and durable version persistence.
- Historical `nil` and explicit `true` remain success; `false` and invalid result types fail.
- Startup aborts when migration update fails.
- Metadata lookup uses active `DATABASE()`.
- Migration Lua does not expose async DB APIs.
- Focused unit and MariaDB integration tests cover the changed semantics.

## OAM-004C — world-save failure propagation

- PR `blakinio/Otheryn#13` merged as `4b5b94eced0f3c5d88b9a4293e849d888333e0cb`.
- `IOGuild::saveGuild()` exposes DB write result.
- `SaveManager` propagates guild/map/KV status.
- Synchronous `saveAll()` returns aggregate success/failure while preserving best-effort continuation across independent domains.
- Scheduled save logs aggregate failure.
- MariaDB integration regression proof verifies callback-`false` rollback in the shared transaction helper used by house replacement.

## OAM-004D — player SQL / wheel KV save boundary

- PR `blakinio/Otheryn#14` final head was `079a69e606896040739103638bc1f87aa07607a7`.
- Final gate was clean: mergeable=true, CI #73 PASS, Required #73 PASS, autofix.ci #66 PASS, no comments, no submitted reviews, no unresolved review threads.
- PR #14 squash-merged with exact-head guard as `67212530b03c10175da2c0d9eabcee8991a05924`.
- Issue `blakinio/Otheryn#10` closed as completed.
- `Otheryn:main` verified identical to `67212530b03c10175da2c0d9eabcee8991a05924`.
- SQL-backed player save operations remain in the player SQL transaction.
- Wheel of Destiny KV cache staging runs only after successful SQL commit.
- Failed SQL transaction prevents wheel KV staging.
- Post-commit KV staging exceptions make `savePlayer()` return false.
- Public `saveOnlyDataForOnlinePlayer()` preserves historical SQL + KV behavior because absence of external callers was not proven.
- Durable KV persistence remains independently owned by `KVSQL::saveAll()` and its failure is propagated by OAM-004C aggregate save handling.

# Explicit unresolved limitations

- Player SQL commit and later durable KV flush are not atomic; a crash between them can lose staged wheel KV changes.
- `KVStore::processEvictions()` may persist evicted entries while ignoring backend save failure.
- Complete crash/restart recovery semantics for untouched persistence paths remain unproven.
- Generic DDL rollback/reversibility remains unproven.
- No cross-domain transaction across players, guilds, houses, map and KV is claimed or required.

# Remaining OAM-004 governance work

Canary governance PR: `blakinio/canary#420`.

This task is now repository-valid `ready` because all bounded target adaptations A/B/C/D are merged and final target `main` is pinned.

Required sequence:

1. Refresh this task, the durable OAM-004 report and the authoritative OAM program record with final target delivery state.
2. Keep OAM-005 inactive.
3. Verify PR #420 exact changed files and ownership.
4. Verify exact-head CI, comments, submitted reviews and unresolved review threads.
5. Mark PR #420 ready.
6. Use the latest ready-triggered exact-head CI as the final merge gate.
7. Squash-merge PR #420 with exact-head guard.
8. Create a separate lifecycle-only PR that moves this task from `tasks/active` to `tasks/archive` and marks OAM-004 completed in the program queue.
9. Make OAM-005 only the next eligible bounded task after the lifecycle PR merges.

# Do not repeat / rejected hypotheses

- Do not infer ACID/retry/crash safety from presence of `DBTransaction`.
- Do not re-enable MySQL auto-reconnect or arbitrary statement replay.
- Do not redesign OAM-004B migration semantics.
- Do not duplicate the DB-core rollback fix inside house serializers.
- Do not invent one giant transaction across players, guilds, houses, map and KV.
- Do not broaden OAM-004D into generic KV subsystem redesign.
- Do not claim SQL + KV atomicity.
- Do not trust negative GitHub code-search results as absence proof.
- Do not start OAM-005 before the OAM-004 feature merge and lifecycle archive both complete.

# Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T18:06:17+02:00
branch: docs/oam-004-persistence-foundation-revalidation
pr: 420
status: ready
context_routes:
  - agent-governance
  - database-persistence
proven:
  - OAM-004A PR 11 merged as 45ffe6afb915746c69125c9e74f5513c0cecdec4
  - OAM-004B PR 12 merged as 1fe44d165fd8637e29ece62b261b7caa33895c65
  - OAM-004C PR 13 merged as 4b5b94eced0f3c5d88b9a4293e849d888333e0cb
  - OAM-004D PR 14 final head 079a69e606896040739103638bc1f87aa07607a7 passed CI 73 Required 73 and autofix 66 with a clean review gate
  - OAM-004D PR 14 merged as 67212530b03c10175da2c0d9eabcee8991a05924
  - Otheryn main is identical to 67212530b03c10175da2c0d9eabcee8991a05924
  - Otheryn issue 10 is closed as completed
  - all four OAM-004 canonical modules have disposition ADAPT
  - OAM-005 remains blocked until OAM-004 feature and lifecycle completion
derived:
  - target delivery for OAM-004 is complete
  - remaining work is Canary governance feature merge followed by separate lifecycle archive
unknown:
  - final Canary OAM-004 feature merge SHA
  - OAM-004 lifecycle merge SHA
conflicts: []
first_failure:
  marker: none active
  evidence: all target slices are merged; Canary PR 420 still requires final exact-head ready-triggered gate
rejected_hypotheses:
  - DBTransaction presence proves persistence safety
  - legacy or upstream baseline can be reused without adaptation
  - world persistence needs one giant cross-domain transaction
  - player SQL and KV persistence are fully atomic after OAM-004D
next_action: Verify Canary PR 420 changed files and ownership, mark it ready, use the latest ready-triggered exact-head CI and clean review gate, then squash-merge with exact-head guard.
```
