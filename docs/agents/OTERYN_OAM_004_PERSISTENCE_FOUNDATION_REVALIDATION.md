# OAM-004 Database and Persistence Foundation Revalidation

Status: **active evidence revalidation; target implementation not authorized**

Program: `CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION`

Coordination: `OAM-004`

Pinned task-start baselines:

```text
legacy/governance: blakinio/canary@63e45afe684e5f923bc004a59687a5adcaac6f01
target: blakinio/Otheryn@a9c7fabc9f4b9bbeca9fed4ab73c36309cd04e2d
upstream evidence: opentibiabr/canary@a879c9312e34381e8eedf397b8ed44510698b689
```

This report is the durable evidence surface for OAM-004. It does not authorize schema execution, destructive migration, production-data mutation or bulk legacy persistence import.

# 1. Canonical modules

| Module | Initial state | OAM-004 question |
|---|---|---|
| `database-connection` | `REVALIDATE` | Is the target/upstream low-level DB core safe to retain, and what retry/transaction guarantees are actually proven? |
| `database-migrations` | `REVALIDATE` | Is ordered migration discovery/version advancement sufficiently safe, or does Oteryn require adaptation for failure/rollback semantics? |
| `player-persistence` | `REVALIDATE` | Are player save/load boundaries transactionally complete and restart/crash-safe for the target architecture? |
| `world-persistence` | `REVALIDATE` | Are guild/house/map/KV save flows and orchestration sufficiently consistent, or is bounded adaptation required? |

No disposition is assigned until exact source and runtime/test evidence is refreshed.

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

Evidence must classify, where applicable:

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

Authoritative implementation candidate for OAM-004. Task-start SHA is pinned above. No target source change is permitted until dispositions and a separate bounded target task/PR exist.

## Upstream `opentibiabr/canary`

Read-only implementation/evidence source. Target began from upstream, but exact persistence-path equality must be verified rather than assumed after OAM-003 target adaptations.

## Legacy `blakinio/canary`

Evidence-only source for persistence changes, tests and possible candidate fixes. A newer or larger legacy diff does not authorize migration.

# 4. Initial canonical-record constraints

PROVEN from canonical records:

- `database-connection` inventories low-level transaction capability but explicitly does not prove isolation, retry safety or rollback completeness.
- `database-migrations` inventories ordered migration execution and version state but explicitly does not prove reversibility or partial-failure recovery.
- `player-persistence` is a broad mapped umbrella over player save/load and DB-backed state; path inventory alone is insufficient for reuse.
- `world-persistence` inventories non-player save orchestration but explicitly does not prove cross-domain atomicity, crash consistency or restart/reconciliation safety.

# 5. Evidence matrix

| Module | Target/upstream comparison | Legacy comparison | Tests/runtime evidence | Transaction/recovery assessment | Disposition |
|---|---|---|---|---|---|
| `database-connection` | pending | pending | pending | pending | `REVALIDATE` |
| `database-migrations` | pending | pending | pending | pending | `REVALIDATE` |
| `player-persistence` | pending | pending | pending | pending | `REVALIDATE` |
| `world-persistence` | pending | pending | pending | pending | `REVALIDATE` |

# 6. Boundary classification

| Boundary | State | Current evidence |
|---|---|---|
| ownership/lifecycle | unresolved | exact DB/save ownership review pending |
| build/toolchain | not-applicable unless DB dependency changes are found | no target change planned |
| configuration | applicable | DB configuration/reconnect inputs pending review |
| service/API | applicable | DB core and persistence interfaces pending review |
| scheduling/concurrency | applicable | async save/shutdown ordering pending review |
| persistence | applicable | primary OAM-004 boundary |
| protocol/session | not-applicable unless player login/session persistence coupling is found | no protocol change planned |
| identifiers/assets | not-applicable | no asset migration |
| world/map | applicable only to persisted house/map state | static OTBM migration excluded |
| runtime | applicable | startup/save/restart evidence pending |
| tests | applicable | targeted DB/IO/integration matrix pending |
| physical-client E2E | likely not-applicable for foundation package | revisit only if session-visible behavior changes |
| operations | applicable | migration/recovery/rollback boundaries pending |
| security/privacy | applicable | no sensitive DB/player data may enter evidence artifacts |

# 7. Required comparison slices

1. `src/database/database.*` — connection, query/result lifetime, retry and transaction primitives.
2. `src/database/databasemanager.*`, `schema.sql`, migration directories — schema version and migration lifecycle.
3. Player persistence owner paths discovered from `src/io/**` and relevant player/database call sites — save/load and multi-table transaction boundaries.
4. `src/game/scheduling/save_manager.*`, `src/io/iomapserialize.*`, `src/io/ioguild.*`, `src/kv/**` — non-player persistence and save orchestration.

Repository-wide diff is discovery only and cannot decide a disposition.

# 8. Explicit exclusions

- no production or user database access;
- no migration execution against real data;
- no destructive schema changes;
- no automatic rollback claims;
- no bulk import of legacy DB/schema/migration files;
- no OAM-005 work;
- no protocol/client migration;
- no static map/datapack migration.

# 9. Completion gate

OAM-004 may advance only when:

1. all four canonical modules have exact evidence-backed dispositions;
2. transaction/retry/migration-failure/restart boundaries are explicitly classified;
3. unresolved remains unresolved rather than inferred safe;
4. any required target adaptation is split into separate bounded Otheryn work before source mutation;
5. Canary governance PR passes exact-head ownership, CI and review gates;
6. feature merge is followed by separate lifecycle-only archival before OAM-005 becomes eligible.
