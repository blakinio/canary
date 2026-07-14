# TSD-002B Persistence and Transactions Classification Report

> Task-start baseline: `blakinio/canary@709693b4cca42214c52e63ea15a1a22b93f9a113`.
> PR #308 is included only because its squash merge `4de9350e62e2ca9ddf717e16628f87084a74aa86` is part of this baseline. Inventory does not inherit PR claims of atomicity, idempotency or runtime safety.

## Candidate decisions

| Candidate | Decision | Reason | Registry action |
|---|---|---|---|
| `database-connection` | `ADD_NOW` | `Database`, `DBResult`, `DBInsert` and retry/connection/query primitives form one durable MariaDB access and result-lifetime boundary used across the server. | Add one conservative inventory record. |
| `database-migrations` | `ADD_NOW` | `DatabaseManager`, `schema.sql` and versioned Lua migrations form a distinct startup schema/version lifecycle with an independent failure and validation queue. | Add one conservative inventory record. |
| `transaction-boundaries` | `MERGE_WITH_ANOTHER_MODULE` | `DBTransaction` is a DB-core capability and transaction use is owned by each functional persistence path. A separate record would turn one helper class into a false domain boundary. | Keep inside `database-connection` and module-specific findings. |
| `world-persistence` | `ADD_NOW` | `SaveManager` coordinates non-player server state, guilds, house/map serialization and KV persistence through a stable save lifecycle distinct from player serialization. | Add one conservative inventory record. |
| `database-reconciliation` | `DEFER` | Current code contains feature-specific recovery, pending-operation and consistency mechanisms, but no generic reconciliation subsystem or stable implementation root. | No record until a durable cross-domain subsystem and validation queue exist. |
| `save-restart-reload` | `MERGE_WITH_ANOTHER_MODULE` | Save orchestration belongs to `world-persistence`/`player-persistence`; startup and shutdown belong to `engine-runtime-lifecycle`; reload belongs to each functional/Lua domain. The combined phrase is a proof package, not one implementation subsystem. | No standalone record. |

## Existing umbrella decision

`player-persistence` remains `KEEP_AS_UMBRELLA` for compatibility and broad discovery. Its current paths continue to overlap narrower DB records. TSD-002B does not rewrite the existing record, narrow its paths or promote its maturity.

## Evidence inventory

### `database-connection`

Verified implementation root:

```text
src/database/database.*
```

The root owns:

- MySQL handle initialization and connection configuration;
- reconnect option and max-packet discovery;
- escaped strings/blobs;
- query execution, affected-row and stored-result lifetimes;
- bounded retry of selected connection errors;
- batched insert support;
- the low-level `DBTransaction` begin/commit/rollback wrapper.

Explicit exclusions:

- schema and migration ordering;
- player/world serializers;
- query correctness in functional modules;
- proofs of isolation, atomicity, deadlock freedom, retry safety, rollback completeness or production MariaDB compatibility;
- external Redis connections and protocol network connections.

### `database-migrations`

Verified implementation/data roots:

```text
src/database/databasemanager.*
schema.sql
data-otservbr-global/migrations/**
```

The lifecycle reads `server_config.db_version`, discovers numeric Lua migration files from the configured data directory, sorts them, executes `onUpdateDatabase`, advances the recorded version and is called from startup after database connection/setup checks.

Explicit exclusions:

- proof that every migration is reversible, idempotent, transactional or safe against partial failure;
- destructive migration execution by this task;
- runtime schema compatibility with every deployment;
- ownership of feature-specific tables after migration.

Migration 63 from merged PR #308 is current evidence of one additive migration and one feature-specific state table. It does not establish a generic reconciliation or exactly-once guarantee.

### `world-persistence`

Verified implementation roots:

```text
src/game/scheduling/save_manager.*
src/io/iomapserialize.*
src/io/ioguild.*
src/kv/**
```

`SaveManager` coordinates save-all and scheduled saves, including guild state, house/map state and the KV store. `IOMapSerialize` owns house information/item serialization and uses DB transactions around house saves. Player serialization is invoked by the manager but remains owned by the existing `player-persistence` umbrella.

Explicit exclusions:

- player/account serialization details;
- static OTBM map content;
- feature-specific tables and formulas;
- guarantees of cross-domain atomicity across players, guilds, houses, map state and KV;
- crash consistency, backup/restore, restart/reload correctness or reconciliation;
- physical-client E2E proof.

## Why `transaction-boundaries` is not a module

The database layer exposes one `DBTransaction` helper and functional modules invoke it around selected operations. That is a reusable capability, but transaction scope and correctness remain properties of each call site. A separate record would imply one central transaction owner and hide missing or partial boundaries.

Future findings should state the exact operation, tables, begin/commit/rollback path, retry semantics and observed failure behavior. No transaction is considered correct merely because it uses `DBTransaction`.

## Why `database-reconciliation` is deferred

Merged PR #308 adds a feature-specific pending-operation state machine and ownership resolver under `src/game/multichannel/**`. Other domains have their own repair or reconciliation logic. There is no one generic scheduler, registry, state machine or operator workflow shared across these domains.

Reconsider only if current-main later contains a durable cross-domain reconciliation service with explicit ownership, state transitions, idempotency keys and focused validation.

## Why `save-restart-reload` is not a module

The phrase combines several owners:

- scheduled and global save orchestration — `world-persistence` and `player-persistence`;
- startup/shutdown state — `engine-runtime-lifecycle`;
- database schema startup — `database-migrations`;
- Lua reload — `lua-runtime`;
- feature reloads — their functional modules;
- physical relog/restart proof — the shared `physical-client-e2e` platform.

It remains a future cross-module validation package. TSD-002B records no claim that restart, reload or crash recovery is safe.

## Relationships

- `database-connection` interacts with `configuration`, `engine-runtime-lifecycle` and `engine-service-container`.
- `database-migrations` depends on `database-connection` and interacts with `configuration`, `engine-runtime-lifecycle` and `lua-runtime`.
- `world-persistence` depends on `database-connection` and interacts with `engine-runtime-lifecycle`, `engine-scheduler` and `player-persistence`.
- `player-persistence` remains the compatibility umbrella and is not modified.

## Maturity baseline

All three records begin conservatively:

```text
lifecycle: inventory
implementation: inventory
evidence: inventory
persistence: not-assessed
protocol: not-assessed
automated_tests: not-assessed
runtime_validation: not-assessed
gameplay_e2e: not-assessed
```

The presence of unit/integration tests, migration scripts, SQL schema, retries or transaction helpers remains inventory evidence only.

## Source-aware discovery expectations

For the configured upstream-server policy:

- `src/database/database.cpp` maps to `database-connection` and may also map to the broad `player-persistence` umbrella;
- `src/database/databasemanager.cpp`, `schema.sql` and migration paths map to `database-migrations` where the registered bucket permits the path;
- `src/game/scheduling/save_manager.cpp` maps to `world-persistence`;
- client-only `protocol` globs are excluded;
- module IDs and mapped rows remain deterministic;
- triage and decision state remain unchanged.

## Safety and evidence limits

TSD-002B changes no database or runtime implementation. It does not prove:

- ACID behavior or transaction isolation;
- rollback completeness;
- deadlock, retry or reconnect safety;
- migration reversibility or partial-failure recovery;
- idempotency or exactly-once processing;
- crash consistency or backup restoration;
- player/world save completeness;
- restart/reload safety;
- production MariaDB compatibility;
- Real Tibia parity, E2E behavior or Oteryn readiness.

## Exact next package

After TSD-002B feature and lifecycle PRs merge, create from then-current `main`:

```text
task: CAN-20260714-tibia-system-decomposition-account-character-progression
package: TSD-003
branch: docs/tibia-system-decomposition-account-character-progression
```

Reclassify durable account, authentication/entitlement, character lifecycle, vocation/skill/level progression and account-wide state boundaries without duplicating `player-persistence` or protocol domains.
