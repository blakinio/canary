---
task_id: CAN-20260716-oteryn-persistence-foundation-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: "OAM-004"
status: completed
agent: oteryn-architecture-migration-agent
branch: docs/oam-004-persistence-foundation-revalidation
base_branch: main
created: 2026-07-16T10:20:00+02:00
updated: 2026-07-16T18:22:26+02:00
completed: 2026-07-16T18:22:26+02:00
last_verified_commit: "0507fc5de8049d712345f43db0b05a23a6577a8a"
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
    - docs/agents/tasks/archive/CAN-20260716-oteryn-persistence-foundation-revalidation.md
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
    - blakinio/canary@0507fc5de8049d712345f43db0b05a23a6577a8a
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

# Governance completion

- Canary feature-governance PR `blakinio/canary#420` passed exact-head Agent Task Ownership #1659 and CI #2798 on head `c83517b66e5a51951445e8303fdc050a58917a52`.
- PR #420 had no comments, submitted reviews or unresolved review threads at the final merge gate.
- PR #420 was squash-merged with exact-head guard as `0507fc5de8049d712345f43db0b05a23a6577a8a`.
- `canary:main` was verified identical to `0507fc5de8049d712345f43db0b05a23a6577a8a` immediately after the feature merge.
- This lifecycle package archives OAM-004 and marks it completed in the authoritative program queue.
- OAM-005 becomes only the next eligible bounded package after this lifecycle package merges; it is not created or started here.

# Do not repeat / rejected hypotheses

- Do not infer ACID/retry/crash safety from presence of `DBTransaction`.
- Do not re-enable MySQL auto-reconnect or arbitrary statement replay.
- Do not redesign OAM-004B migration semantics.
- Do not duplicate the DB-core rollback fix inside house serializers.
- Do not invent one giant transaction across players, guilds, houses, map and KV.
- Do not broaden OAM-004D into generic KV subsystem redesign.
- Do not claim SQL + KV atomicity.
- Do not trust negative GitHub code-search results as absence proof.
- Do not start OAM-005 as part of OAM-004 lifecycle completion.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T18:22:26+02:00
head: 0507fc5de8049d712345f43db0b05a23a6577a8a
branch: docs/oam-004-lifecycle-archive
pr: pending
status: completed
context_routes:
  - agent-governance
  - database-persistence
owned_paths:
  - docs/agents/tasks/archive/CAN-20260716-oteryn-persistence-foundation-revalidation.md
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
proven:
  - OAM-004A PR 11 merged as 45ffe6afb915746c69125c9e74f5513c0cecdec4
  - OAM-004B PR 12 merged as 1fe44d165fd8637e29ece62b261b7caa33895c65
  - OAM-004C PR 13 merged as 4b5b94eced0f3c5d88b9a4293e849d888333e0cb
  - OAM-004D PR 14 merged as 67212530b03c10175da2c0d9eabcee8991a05924
  - Otheryn main is identical to 67212530b03c10175da2c0d9eabcee8991a05924
  - Otheryn issue 10 is closed as completed
  - all four OAM-004 canonical modules have disposition ADAPT
  - Canary PR 420 exact head c83517b66e5a51951445e8303fdc050a58917a52 passed Agent Task Ownership 1659 and CI 2798
  - Canary PR 420 merged as 0507fc5de8049d712345f43db0b05a23a6577a8a
  - Canary main is identical to 0507fc5de8049d712345f43db0b05a23a6577a8a after feature merge
derived:
  - OAM-004 feature delivery and feature governance are complete
  - this lifecycle-only package is the remaining completion boundary
  - OAM-005 may become next eligible only after this lifecycle package merges
unknown:
  - final lifecycle PR number
  - final lifecycle merge SHA
conflicts: []
first_failure:
  marker: none active
  evidence: feature target and governance gates are complete; lifecycle-only validation remains
rejected_hypotheses:
  - DBTransaction presence proves persistence safety
  - legacy or upstream baseline can be reused without adaptation
  - world persistence needs one giant cross-domain transaction
  - player SQL and KV persistence are fully atomic after OAM-004D
changed_paths:
  - docs/agents/tasks/active/CAN-20260716-oteryn-persistence-foundation-revalidation.md
  - docs/agents/tasks/archive/CAN-20260716-oteryn-persistence-foundation-revalidation.md
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
validation:
  - command: Otheryn PR 14 exact-head CI 73 / Required 73 / autofix.ci 66
    result: PASS
    evidence: completed success on head 079a69e606896040739103638bc1f87aa07607a7
  - command: Canary PR 420 Agent Task Ownership 1659
    result: PASS
    evidence: completed success on head c83517b66e5a51951445e8303fdc050a58917a52
  - command: Canary PR 420 CI 2798
    result: PASS
    evidence: completed success on head c83517b66e5a51951445e8303fdc050a58917a52
blockers: []
next_action: Merge this lifecycle-only package after its exact-head ownership CI and clean review gates pass; then OAM-005 is merely the next eligible bounded task and remains not started.
```

# Completion

- Final task status: completed.
- Final Otheryn target head: `67212530b03c10175da2c0d9eabcee8991a05924`.
- Canary feature PR: #420.
- Canary feature head: `c83517b66e5a51951445e8303fdc050a58917a52`.
- Canary feature merge: `0507fc5de8049d712345f43db0b05a23a6577a8a`.
- Lifecycle archive: this separate lifecycle-only package.
- OAM-005 implementation: not started.
