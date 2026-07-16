# OAM-004 Database and Persistence Foundation Revalidation

Status: **target delivery complete; Canary feature governance ready for final gate**

Program: `CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION`

Coordination: `OAM-004`

Pinned task-start baselines:

```text
legacy/governance: blakinio/canary@63e45afe684e5f923bc004a59687a5adcaac6f01
target: blakinio/Otheryn@a9c7fabc9f4b9bbeca9fed4ab73c36309cd04e2d
upstream evidence: opentibiabr/canary@a879c9312e34381e8eedf397b8ed44510698b689
```

Final target head after OAM-004 delivery:

```text
blakinio/Otheryn@67212530b03c10175da2c0d9eabcee8991a05924
```

This report is the durable evidence surface for OAM-004. It does not authorize schema execution, destructive migration, production-data mutation, bulk legacy persistence import or OAM-005 implementation.

# 1. Canonical modules and final dispositions

| Module | Disposition | Final OAM-004 result |
|---|---|---|
| `database-connection` | `ADAPT` | Retained the target DB substrate while removing silent reconnect/replay behavior and hardening transaction ownership/failure semantics. |
| `database-migrations` | `ADAPT` | Retained ordered Lua migrations while making migration failure and schema-version advancement fail closed. |
| `world-persistence` | `ADAPT` | Retained existing save owners while propagating guild/map/KV status and aggregate save failure; house rollback inherits the hardened shared transaction contract. |
| `player-persistence` | `ADAPT` | Retained the player SQL transaction while moving Wheel of Destiny KV staging outside that transaction and only after successful SQL commit. |

No module is approved for wholesale legacy import or unconditional `REUSE`.

# 2. Delivered target adaptation chain

## OAM-004A — database transaction integrity

Target issue/PR:

```text
blakinio/Otheryn#7
blakinio/Otheryn#11
```

Merged target SHA:

```text
45ffe6afb915746c69125c9e74f5513c0cecdec4
```

Delivered:

- disabled silent MySQL automatic reconnect;
- removed arbitrary SQL statement replay;
- acquired the transaction lock before `BEGIN`;
- made callback `false` roll back rather than commit;
- restored local transaction state when transaction begin fails.

Result: the shared DB transaction helper now fails closed for the proven transaction failure cases covered by this slice.

## OAM-004B — fail-closed database migrations

Target issue/PR:

```text
blakinio/Otheryn#8
blakinio/Otheryn#12
```

Merged target SHA:

```text
1fe44d165fd8637e29ece62b261b7caa33895c65
```

Delivered:

- migration chain stops on the first load/call/runtime/result/version-persistence failure;
- `db_version` advances only after an accepted migration and durable version persistence;
- historical `nil` migration return remains compatible as success;
- `true` means success;
- `false` means failure;
- invalid result types fail closed;
- normal startup aborts when migration update fails;
- metadata lookup uses active `DATABASE()`;
- startup migration Lua does not expose async DB APIs;
- focused unit and MariaDB integration tests cover the changed contract.

Generic DDL rollback/reversibility remains unproven and is not claimed.

## OAM-004C — world-save failure propagation

Target issue/PR:

```text
blakinio/Otheryn#9
blakinio/Otheryn#13
```

Merged target SHA:

```text
4b5b94eced0f3c5d88b9a4293e849d888333e0cb
```

Delivered:

- `IOGuild::saveGuild()` exposes DB write success/failure;
- `SaveManager::saveGuild()`, `saveMap()` and `saveKV()` propagate status;
- synchronous `SaveManager::saveAll()` returns aggregate success/failure;
- independent save domains continue best-effort after another domain fails;
- asynchronous scheduled save logs aggregate failure;
- MariaDB integration regression proof verifies callback-`false` rollback in `DBTransaction::executeWithinTransaction()`.

`IOMapSerialize::saveHouseItems()` directly uses that same transaction callback contract, so failed house replacement inherits the proven rollback semantics. No duplicate serializer-local transaction fix was introduced.

## OAM-004D — player SQL / wheel KV save boundary

Target issue/PR:

```text
blakinio/Otheryn#10
blakinio/Otheryn#14
```

Task-start target:

```text
4b5b94eced0f3c5d88b9a4293e849d888333e0cb
```

Final PR head before merge:

```text
079a69e606896040739103638bc1f87aa07607a7
```

Merged target SHA:

```text
67212530b03c10175da2c0d9eabcee8991a05924
```

Delivered:

- player SQL-backed save operations remain inside the player-owned SQL transaction;
- Wheel of Destiny KV cache mutations occur only after successful SQL commit;
- failed SQL transaction prevents wheel KV staging;
- post-commit KV staging exceptions make `savePlayer()` return `false`;
- public `saveOnlyDataForOnlinePlayer()` preserves historical SQL + KV behavior because absence of external callers was not proven;
- durable KV persistence remains independently owned by `KVSQL::saveAll()`;
- OAM-004C propagates durable KV save failure through the aggregate server-save result.

Final exact-head merge gate for PR #14:

```text
head: 079a69e606896040739103638bc1f87aa07607a7
mergeable: true
CI #73: PASS
Required #73: PASS
autofix.ci #66: PASS
comments: none
submitted reviews: none
unresolved review threads: none
```

PR #14 was squash-merged with exact-head guard. Issue #10 was closed as completed. `Otheryn:main` was then verified identical to `67212530b03c10175da2c0d9eabcee8991a05924`.

# 3. Final evidence matrix

| Module | Task-start risk | Delivered evidence | Final disposition |
|---|---|---|---|
| `database-connection` | silent reconnect/replay, unsafe transaction ownership ordering, callback-false commit | OAM-004A merged and exact-head validated | `ADAPT` |
| `database-migrations` | fail-open migration chain and unsafe version advancement | OAM-004B merged with focused unit/MariaDB coverage | `ADAPT` |
| `world-persistence` | house rollback dependency plus unobservable guild/global save failures | OAM-004A shared rollback contract + OAM-004C result propagation | `ADAPT` |
| `player-persistence` | KV cache staging occurred inside SQL transaction boundary | OAM-004D separates SQL commit from post-commit KV staging | `ADAPT` |

# 4. Explicit unresolved limitations

The following remain unresolved and must not be represented as solved by OAM-004:

- player SQL commit and later durable KV flush are not atomic; a crash between them can lose staged wheel KV changes;
- `KVStore::processEvictions()` may persist evicted entries while ignoring backend save failure;
- complete crash/restart recovery semantics for untouched persistence paths are not proven;
- generic DDL reversibility is not proven;
- OAM-004 does not create one cross-domain transaction across players, guilds, houses, map and KV.

# 5. Governance completion boundary

Target delivery for OAM-004 is complete at:

```text
blakinio/Otheryn@67212530b03c10175da2c0d9eabcee8991a05924
```

Remaining governance sequence:

1. update the active OAM-004 task to repository-valid `ready`;
2. update the authoritative OAM program queue to record target delivery complete while keeping OAM-005 inactive;
3. verify Canary PR #420 exact changed files, ownership, exact-head CI, comments, reviews and unresolved review threads;
4. mark PR #420 ready;
5. use the latest ready-triggered exact-head CI as the final merge gate;
6. squash-merge PR #420 with exact-head guard;
7. create a separate lifecycle-only PR that moves the OAM-004 task from `active` to `archive` and marks OAM-004 completed in the program queue;
8. make OAM-005 only the next eligible bounded task after that lifecycle PR merges.

OAM-005 must remain inactive until both the OAM-004 feature-governance merge and the separate lifecycle archive merge are complete.

# 6. Do not repeat

- Do not re-enable MySQL automatic reconnect.
- Do not restore arbitrary SQL statement replay.
- Do not infer persistence safety merely from `DBTransaction` existence.
- Do not redesign the already merged OAM-004B migration semantics.
- Do not duplicate the DB-core rollback fix inside house serializers.
- Do not create one giant transaction across players, guilds, houses, map and KV.
- Do not claim player SQL + KV atomicity.
- Do not broaden OAM-004D into generic KV subsystem redesign.
- Do not trust negative GitHub code-search results as proof of absence.
- Do not start OAM-005 before OAM-004 feature merge and lifecycle archive.
