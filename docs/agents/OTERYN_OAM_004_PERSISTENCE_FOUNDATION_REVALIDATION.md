# OAM-004 Database and Persistence Foundation Revalidation

Status: **evidence matrix complete; bounded target adaptation chain active**

Program: `CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION`

Coordination: `OAM-004`

Pinned task-start baselines:

```text
legacy/governance: blakinio/canary@63e45afe684e5f923bc004a59687a5adcaac6f01
target: blakinio/Otheryn@a9c7fabc9f4b9bbeca9fed4ab73c36309cd04e2d
upstream evidence: opentibiabr/canary@a879c9312e34381e8eedf397b8ed44510698b689
```

This report is the durable evidence surface for OAM-004. It does not authorize schema execution, destructive migration, production-data mutation or bulk legacy persistence import.

# 1. Canonical modules and OAM-004 dispositions

| Module | Disposition | OAM-004 result |
|---|---|---|
| `database-connection` | `ADAPT` | Retain the target/upstream DB substrate, but make connection loss and transaction failure fail closed. OAM-004A target issue #7 / PR #11 owns this adaptation. |
| `database-migrations` | `ADAPT` | Retain ordered Lua migration infrastructure, but stop on first failed migration and advance `db_version` only for accepted successful steps. OAM-004B issue #8 owns this adaptation. |
| `player-persistence` | `ADAPT` | Retain the broad player transaction/save architecture, but audit and close unobservable sub-save failures and rely on the hardened OAM-004A DB transaction contract. OAM-004D issue #10 owns this adaptation. |
| `world-persistence` | `ADAPT` | Retain existing save owners, but fix false-callback house rollback and propagate guild/global save failures. OAM-004C issue #9 owns this adaptation. |

No module is approved for wholesale legacy import or unconditional `REUSE`.

# 2. Evidence contract

OAM-004 separates code capability from proven correctness:

```text
DBTransaction exists
!=
all higher-level save paths are atomic

ordered migration files exist
!=
migrations are reversible or partial-failure safe

save orchestration exists
!=
cross-domain crash consistency

server starts in CI
!=
persistence restart/recovery correctness
```

Evidence classification includes:

- connection ownership and reconnect behavior;
- transaction begin/commit/rollback boundaries;
- retry safety inside and outside active transactions;
- migration ordering and persisted schema-version advancement;
- migration partial-failure behavior;
- player multi-table save/load ownership;
- world/guild/house/KV save ownership;
- async save scheduling and shutdown interaction;
- restart/crash recovery assumptions;
- rollback/reconciliation boundaries;
- exact tests/runtime evidence available on the pinned target.

# 3. Source roles

## Target `blakinio/Otheryn`

Authoritative implementation candidate for OAM-004. Task-start SHA is pinned above. Every source adaptation is isolated in its own target issue/branch/PR and exact-head gate.

## Upstream `opentibiabr/canary`

Read-only implementation/evidence source. OAM-004 found the target DB/migration/player/world foundation materially inherited from the pinned upstream baseline; inherited behavior is not assumed correct merely because it is upstream-native.

## Legacy `blakinio/canary`

Evidence-only source. Legacy has the same migration-manager fail-open behavior, the same generic transaction callback-false commit semantics, the same house-save transaction helper misuse and materially the same player save transaction boundary at the pinned OAM-004 baseline. It does not provide a ready persistence fix source.

# 4. Database connection and transaction findings

PROVEN at target task-start:

- `Database::connect()` enabled `MYSQL_OPT_RECONNECT`.
- `executeQuery()` retried selected recoverable errors by resending the SQL statement.
- `storeQuery()` retried recoverable errors indefinitely with a retry loop.
- MySQL automatic reconnect can reset connection/session state and roll back an active server-side transaction, so silent statement replay is incompatible with a fail-closed local transaction contract.
- `Database::beginTransaction()` executed `BEGIN` before acquiring the long-lived recursive database lock, leaving an inter-thread window where another statement on the shared `MYSQL*` handle could enter the just-opened transaction.
- `DBTransaction::executeWithinTransaction()` committed even when its callback returned `false`.
- `DBTransaction::begin()` set local transaction state before database begin succeeded and did not restore local state on a false return.
- Legacy contains the same generic `DBTransaction` callback-false semantics and is not a ready fix source.

Decision: `database-connection` → `ADAPT`.

Bounded target package:

```text
OAM-004A / blakinio/Otheryn#7
implementation PR: blakinio/Otheryn#11
```

OAM-004A final intended contract:

- disable silent MySQL automatic reconnect;
- do not automatically resend arbitrary failed SQL statements;
- acquire transaction ownership lock before `BEGIN`;
- propagate statement failure to the owning operation;
- roll back a transaction when its callback returns `false`;
- preserve serialized shared-connection access;
- permit higher-level retries only when operation idempotence is explicitly proven.

# 5. Database migration findings

PROVEN at target/upstream and legacy task-start baselines:

`DatabaseManager::updateDatabase()`:

- loads ordered migration files;
- logs and continues after a migration file load failure;
- logs and continues after a Lua migration call failure;
- requests a return value from `onUpdateDatabase` but does not enforce a semantic success result;
- can run a later migration and persist a higher `db_version` after an earlier migration failed;
- provides no generic DDL reversibility or partial-failure recovery guarantee.

Legacy has the same migration-manager implementation and provides no stronger baseline.

Decision: `database-migrations` → `ADAPT`.

Bounded target package:

```text
OAM-004B / blakinio/Otheryn#8
```

Required contract:

- fail closed on the first migration load/runtime/explicit failure;
- define and inspect the `onUpdateDatabase` result contract;
- advance `db_version` only after the corresponding migration is successfully accepted;
- test first-failure stop and version advancement against temporary MariaDB;
- keep DDL rollback/reversibility explicitly unproven unless separately demonstrated.

# 6. Player persistence findings

PROVEN:

- `IOLoginData::savePlayer()` wraps the broad player save guard in `DBTransaction`.
- Many boolean sub-save failures are converted to exceptions, which causes the outer transaction to roll back.
- Target/upstream and legacy use materially the same outer player save transaction boundary.
- Some online-player sub-save calls expose no boolean/error result to the outer guard, so the transaction wrapper alone does not prove uniformly observable failure across every player-owned state write.
- The player transaction inherits OAM-004A DB connection/retry/transaction semantics.
- Current CI/runtime smoke does not prove complete player crash/restart recovery across every owned table and KV-backed state.

Decision: `player-persistence` → `ADAPT`.

Bounded target package:

```text
OAM-004D / blakinio/Otheryn#10
```

Required contract:

- enumerate exact player sub-save operations inside the outer transaction;
- classify whether each can fail and how failure is propagated;
- make database-backed failure observable where required without broad feature refactors;
- preserve one player-owned transaction boundary rather than inventing global cross-domain atomicity;
- retain untested crash/restart scenarios as explicit unresolved evidence.

# 7. World persistence findings

PROVEN:

- `IOMapSerialize::saveHouseItems()` uses `DBTransaction::executeWithinTransaction()`.
- `SaveHouseItemsGuard()` reports `DELETE`, batch-building and insert failures by returning `false`.
- At OAM-004 task-start, the generic transaction helper committed after a false callback. Therefore a successful `DELETE FROM tile_store` followed by a failed insert could commit the deletion instead of rolling back.
- Legacy has the same house-save transaction/helper behavior.
- `IOGuild::saveGuild()` returns `void` and ignores the database update result.
- `SaveManager::saveAll()` returns `void`; it logs player/map/KV failures and continues through later save domains without exposing an aggregate success result.
- `SaveManager::scheduleAll()` may run the global save as a detached thread-pool task.
- Existing orchestration does not prove one cross-domain transaction, crash consistency or reconciliation after partial save completion.

Decision: `world-persistence` → `ADAPT`.

Bounded target package:

```text
OAM-004C / blakinio/Otheryn#9
```

Required contract:

- house-item replacement must roll back on callback/insert failure;
- guild save failure must be observable;
- global save orchestration must expose enough aggregate status for shutdown/operations decisions;
- do not create one giant transaction across players, guilds, houses and KV;
- keep static OTBM migration and backup/restore redesign out of scope.

# 8. Evidence matrix

| Module | Target/upstream comparison | Legacy comparison | Runtime/test evidence | Transaction/recovery assessment | Disposition |
|---|---|---|---|---|---|
| `database-connection` | inherited shared connection, auto-reconnect, query replay and transaction helper behavior | no ready fix; generic transaction semantics materially same | full target CI/runtime/MariaDB gates required for OAM-004A | silent reconnect/replay and false-callback commit are incompatible with fail-closed transactions | `ADAPT` |
| `database-migrations` | ordered Lua migration manager is fail-open across failed steps | same manager behavior | clean schema import + focused migration-chain tests required | version can advance past an earlier failed step; no generic rollback proof | `ADAPT` |
| `player-persistence` | broad outer transaction exists and many failures throw/rollback | materially same outer transaction model | targeted MariaDB/player save tests required for changed paths | outer transaction is valuable but not every sub-save failure is uniformly observable; crash recovery unproven | `ADAPT` |
| `world-persistence` | existing owners and SaveManager orchestration | same house transaction misuse found | focused house/guild/save-result tests + runtime DB smoke required | known false-callback commit risk and unobservable guild/global save failure | `ADAPT` |

# 9. Boundary classification

| Boundary | State | Current evidence |
|---|---|---|
| ownership/lifecycle | applicable | shared DB connection + player/world save owners identified; adaptation split into A/B/C/D |
| build/toolchain | applicable to validation only | no DB dependency change currently required; full C++/DB matrix applies |
| configuration | applicable | auto-reconnect behavior is DB connection configuration at API level; silent reconnect rejected |
| service/API | applicable | transaction helper, migration manager and save result contracts require bounded adaptation |
| scheduling/concurrency | applicable | shared MYSQL handle transaction-lock ordering and detached save scheduling are material |
| persistence | applicable | primary OAM-004 boundary |
| protocol/session | not-applicable for current slices | no protocol/client change planned |
| identifiers/assets | not-applicable | no asset migration |
| world/map | applicable only to persisted house/world state | static OTBM migration excluded |
| runtime | applicable | exact-head temporary MariaDB/runtime smoke required for each source slice |
| tests | applicable | focused transaction, migration and failure-propagation tests plus clean schema import |
| physical-client E2E | not-applicable for foundation package unless later session-visible behavior changes | no client contract change |
| operations | applicable | migration failure, save aggregate result, restart/crash assumptions and rollback boundaries remain explicit |
| security/privacy | applicable | no credentials or sensitive player data in evidence artifacts |

# 10. Bounded target adaptation chain

Created before relevant source mutations:

```text
OAM-004A #7 — harden database transaction failure semantics
  active implementation PR #11

OAM-004B #8 — make database migration chain fail closed
  depends on final OAM-004A DB-core contract where applicable

OAM-004C #9 — make world save failures rollback and propagate
  depends on final OAM-004A transaction semantics

OAM-004D #10 — close player save failure-propagation gaps
  depends on final OAM-004A transaction semantics
```

OAM-004A PR #11 was opened before DB-core source changes. OAM-004B/C/D source work must not start before their dependency baselines are freshly re-pinned after OAM-004A merge.

# 11. Validation requirements

Shared `BUILD_TEST_MATRIX.md` requires DB/schema/migration work to include:

- clean schema import/parser validation;
- migration tests where migration behavior changes;
- rollback review;
- temporary MariaDB integration;
- exact-head C++ build and affected runtime smoke.

No historical green run substitutes for the final exact-head gate.

# 12. Explicit exclusions

- no production or user database access;
- no migration execution against real data;
- no destructive unrelated schema changes;
- no automatic generic DDL rollback claims;
- no bulk import of legacy DB/schema/migration files;
- no giant cross-domain transaction;
- no OAM-005 work;
- no protocol/client migration;
- no static map/datapack migration.

# 13. Completion gate

OAM-004 may complete only when:

1. all four dispositions remain backed by exact evidence;
2. OAM-004A/B/C/D required source adaptations are either merged with exact-head evidence or explicitly retained as blockers;
3. transaction/retry/migration-failure/restart boundaries remain explicit;
4. unresolved remains unresolved rather than inferred safe;
5. the authoritative OAM program queue records the final dependency state;
6. Canary governance PR #420 passes exact-head ownership, CI and review gates;
7. feature merge is followed by separate lifecycle-only archival before OAM-005 becomes eligible.
