# Gameplay Analytics: runtime, dry-run validation and Oteryn handoff

This document is the evidence-qualified state reference for the current Canary Gameplay Analytics implementation and its no-server/no-database validation path. It replaces the previous short dry-run invocation note.

It does **not** claim that Gameplay Analytics has been proven on a production or staging Canary runtime. Runtime event ordering, real database behaviour under load, concurrency, memory stability and gameplay-data completeness remain separate validation gates.

## Scope and evidence vocabulary

The statements below use four evidence classes:

- **CURRENT SOURCE** — confirmed directly in the implementation on the audited `main` baseline.
- **CURRENT TEST** — exercised by a test or workflow on the current PR evidence head recorded in [Current verification record](#current-verification-record).
- **HISTORICAL EVIDENCE** — recorded by an earlier merged PR/task, but not treated as a current-head execution result by itself.
- **NOT PROVEN** — outside the deterministic dry-run boundary or not executed in the recorded environment.

Historical PRs #135 and #140 are useful provenance, not substitutes for current source and current-PR CI. Comparing merge commit `86f553c15cbabf2234243f11584cdc6ed8008029` from PR #140 with the audited current `main` found no later changes to Gameplay Analytics runtime, schema, tests or workflows; unrelated repository work advanced substantially.

## Executive state

- Gameplay Analytics is an optional Lua subsystem and is **disabled by default**.
- It runs inside Canary only when enabled and, when database persistence is enabled, only after schema version `3` passes the runtime guard.
- It collects session-level combat and context metrics. Spell, monster and damage-type details are enabled by default; supplies and loot integrations exist but are disabled by default.
- Completed sessions are buffered in bounded memory queues, written with idempotent upserts and retried with bounded exponential backoff.
- Sessions exhausting retries enter a bounded in-memory dead-letter queue and may be persisted as terminal history. Persisted dead-letter rows are not an automatic database replay queue.
- The dry-run path starts no Canary process, loads no map, starts no network service and requires no real MariaDB.
- MariaDB-backed workflows separately verify schema import, migrations, upserts, retention, reporting views and selected query plans.
- Production or staging runtime behaviour is **not proven** by the dry-run suite.

## Runtime and dry-run boundary

### Runtime Gameplay Analytics

The live runtime consists of:

1. `data-otservbr-global/scripts/config/gameplay_analytics.lua` — operator configuration and safe defaults.
2. `data-otservbr-global/scripts/lib/gameplay_analytics.lua` — session model, core record APIs, base queue, base flush and lifecycle.
3. `gameplay_analytics_context.lua` — hunt-area, party and server-version context.
4. `gameplay_analytics_schema.lua` — schema-version startup guard.
5. `gameplay_analytics_batching.lua` — bounded detail-row batching and the context-aware session upsert.
6. `gameplay_analytics_reliability.lua` — retry scheduling, health metrics and dead letters.
7. `gameplay_analytics_correctness.lua` — UTC rollover, non-combat eligibility and short death/rollover handling.
8. `data-otservbr-global/scripts/systems/gameplay_analytics.lua` — Canary event hooks, startup/shutdown integration and `/analytics` administration.
9. Shared spell, supply, price and loot helpers under `data/scripts/**`.
10. MariaDB baseline schema, migrations, optional retention schema, reporting views, maintenance runner and Grafana assets.

The wrapper load order is deliberate:

```text
core
  -> context
  -> schema guard
  -> batching
  -> reliability
  -> correctness
```

Every wrapper has an installation flag and returns the already wrapped table when loaded again. The core must not be reloaded after wrappers have been installed.

### Dry-run only

The dry-run path consists of validators and test harnesses under `tools/analytics/**` plus `.github/workflows/gameplay-analytics-dry-run.yml`.

It uses:

- Python source/contract validators and mutation tests;
- LuaJIT with mock Analytics objects, mock players and deterministic clocks;
- direct invocation of registered mock event hooks;
- shell syntax and configuration validation;
- a fake `mariadb` executable that fails if configuration-only mode tries to access the database;
- JSON and SQL asset parsing.

Dry-run code is test infrastructure. It is not loaded by the live server and does not collect production data.

## Configuration and safe defaults

| Setting | Current default | Behaviour |
| --- | ---: | --- |
| `enabled` | `false` | No collection until an operator enables it. |
| `databaseEnabled` | `true` | Completed eligible sessions are intended for MariaDB when Analytics is enabled. |
| `flushIntervalSeconds` | `300` | Periodic queue processing; runtime clamps the lower bound. |
| `minimumSessionSeconds` | `60` | Normal short sessions are not persisted; death and UTC-rollover fragments are exceptions. |
| `combatTimeoutSeconds` | `120` | Inactive combat and utility-only sessions expire; runtime clamps to at least 10 seconds. |
| `includeStaff` | `false` | Staff accounts are excluded by default. |
| `trackPvP` | `false` | Player and player-owned-summon PvP damage is excluded by default. |
| `trackSpells` | `true` | Per-spell detail rows may be collected. |
| `trackMonsters` | `true` | Per-monster detail rows may be collected. |
| `trackDamageTypes` | `true` | Per-damage-type detail rows may be collected. |
| `trackSupplies` | `false` | Supply integrations are inactive by default. |
| `trackLoot` | `false` | Loot integration is inactive by default. |
| `anonymizePlayers` | `false` | Player names are stored by default; player IDs are always part of the current relational model. |
| `queueLimit` | `10000` | Bounded completed-session queue. |
| `detailBatchSize` | `250` | Detail rows per SQL batch, clamped to `1..1000`. |
| `maxRetryAttempts` | `5` | Bounded retry attempts before dead-lettering. |
| `retryBaseDelaySeconds` | `30` | Initial retry delay. |
| `retryMaxDelaySeconds` | `900` | Maximum retry delay. |
| `deadLetterQueueLimit` | `1000` | Bounded in-memory terminal-failure queue. |
| `serverVersion` | environment or empty | `CANARY_SERVER_VERSION` is copied into finalized sessions. The production installer rejects an empty placeholder, but direct runtime configuration does not independently reject an empty value. |
| `trackFallbackGridAreas` | `true` | Unknown positions use a bounded grid label when no named hunt area matches. |
| `huntAreas` | empty | No named catalogue is shipped in the default config. |

The installer prepares the database only. It validates a real database password and a non-empty stable `CANARY_SERVER_VERSION`, but never edits the Lua configuration and never enables Analytics.

## Collected data

### Session identity and lifecycle

Each active player session contains:

- generated session UUID;
- database player ID and current runtime ID;
- optional player name;
- vocation and starting/ending level;
- start/end timestamps and finish reason;
- combat-window timestamps and accumulated combat seconds;
- retry scheduling state when persistence fails.

The session UUID has a unique database key and is the idempotency key for retries.

### Core totals

The runtime can collect:

- raw and final experience;
- damage dealt and received;
- self-healing and healing of others;
- overhealing;
- negative mana changes recorded as `mana_spent`;
- monster kills;
- deaths;
- NPC-valued and market-valued loot totals;
- supply value.

`mana_spent` is currently the sum of negative primary and secondary values observed by the registered mana-change hook. It is not a semantic guarantee that every negative mana change is a spell cost.

### Detail dimensions

When enabled by configuration, session details include:

- monster name, kills, dealt/received damage and raw experience;
- spell name, casts, target count, damage, healing, configured mana and critical count;
- damage type with dealt/received totals;
- supply item ID, amount, unit value and total value;
- loot item ID, amount, verified NPC value and market value.

The engine does not expose a Lua market-price source to this integration. Current loot market value is therefore recorded as `0`, rather than guessed.

### Party, hunt and version context

The context wrapper samples:

- current party members and leader without duplicate GUIDs;
- party-size minimum, maximum and time-weighted average;
- shared-experience seconds and ratio;
- a sorted vocation-composition string;
- named hunt area or fallback grid area;
- `server_version` from `CANARY_SERVER_VERSION`.

Context sample gaps are bounded so a delayed callback does not invent an unbounded amount of party or area time.

### Identifiers, anonymization and exclusions

- `anonymizePlayers=true` suppresses `player_name` in new sessions.
- It does not remove `player_id`; the current schema uses a foreign key to `players(id)`.
- `includeStaff=false` excludes account types above normal.
- `excludedAccountTypes` and case-insensitive `excludedPlayerNames` provide additional exclusions.
- Grafana validation forbids per-player dashboard variables, so standard reporting is aggregate-oriented even when raw rows retain identifiers.

For Oteryn, player identity handling requires an explicit privacy and retention decision; it is not a drop-in anonymous telemetry model.

## Event sources and attribution

The live system registers:

- startup and shutdown global events;
- login, logout, health, mana, death and kill creature events;
- player experience and engine-wide drain-health callbacks;
- the `/analytics` gamemaster talk action.

Current source behaviour:

- outgoing damage to non-player creatures is recorded through the engine-wide drain-health callback;
- a summon is attributed to its player master;
- damage to a player-owned summon is treated as PvP for the `trackPvP` gate;
- incoming damage to a player from a monster is recorded;
- direct or summon-owned player damage is excluded when `trackPvP=false`;
- healing records effective healing and overhealing based on missing health at callback time;
- raw/final experience keeps the source creature for per-monster attribution;
- login registers player creature events but does not create an empty session;
- death closes the session immediately;
- logout finishes an active session;
- shutdown finishes online sessions, finalizes remaining offline sessions and forces queue/dead-letter processing.

The no-server runtime-hook test invokes these registered mock callbacks directly. That proves the Lua callback logic for its synthetic inputs, not that the real engine emits callbacks once or in a particular order.

## Spell, supply and loot integrations

### Spell telemetry

The shared spell helper takes session combat totals before and after a successful cast and stores only the cast delta in the spell detail bucket. It passes the configured spell mana cost into the spell row but does **not** call `recordManaSpent`; the generic mana-change hook remains the source of the session-wide mana total.

Current explicit integrations include selected spells and the fireball and intense-healing runes. Failed casts do not create spell detail records.

### Supplies

- Supply tracking is disabled by default.
- Potions report one consumed unit only when `REMOVE_POTION_CHARGES` is enabled and the item is actually removed.
- Fireball and intense-healing runes report one unit only when `REMOVE_RUNE_CHARGES` is enabled and the cast succeeds.
- Unit values come from a small source-reviewed NPC-price table. Missing values resolve to `0`.

This is selective integration, not proof that every consumable in the datapack is covered.

### Loot

- Loot tracking is disabled by default.
- The post-drop callback reads the final recursive corpse contents.
- Loot is credited once to the corpse owner, not once per party member.
- NPC values come only from the reviewed price table; market values remain `0`.

This is physical-corpse attribution, not a full economy or item-provenance ledger.

## Session correctness rules

### UTC rollover

Before the first metric access on a later UTC day, the correctness wrapper closes the old active session with `utc-day-rollover` and starts one replacement session. A multi-day gap produces one close and one new session; it does not synthesize empty sessions for skipped days.

Short rollover fragments bypass the normal minimum-duration filter but still must contain combat or death to pass persistence eligibility.

### Non-combat eligibility

Mana, spell, supply or loot activity can create an in-memory session through the shared `get()` path. Such a session:

- receives `lastActivityAt` updates;
- expires after the inactivity timeout;
- is discarded before persistence unless it has combat or death evidence;
- is counted in correctness health metrics.

This prevents utility-only sessions from inflating reporting session counts.

### Death and normal short sessions

- A death increments `deaths` and closes the session.
- A death fragment shorter than `minimumSessionSeconds` is retained.
- The temporary minimum override is restored even if the wrapped finish raises an error.
- Other short sessions remain subject to the normal minimum duration.

## Buffering, persistence and failure behaviour

### Queues

Completed eligible sessions enter a bounded in-memory queue. The configured limit is clamped to at least `100`. Queue overflow is logged, increments a dropped-session health counter and attempts to move the session into the bounded dead-letter queue.

No queue is durable until a MariaDB write succeeds. A process crash can therefore lose in-memory sessions and dead letters.

### Session and detail writes

The batching layer writes:

1. one session row by `session_uuid`;
2. sorted detail rows in batches;
3. each table with `ON DUPLICATE KEY UPDATE`.

A detail failure makes the whole session persistence attempt fail for retry purposes. The session row may already exist, but retry remains safe because all writes are idempotent upserts.

The writes are not wrapped in one database transaction across the session row and every detail table. Idempotency repairs partial writes on a later successful retry; it does not provide all-or-nothing visibility during a failed attempt.

### Retry and exponential backoff

On a failed flush:

- retry count increases;
- next retry time is `base * 2^(attempt-1)`, capped at the configured maximum;
- delayed sessions stay queued but are skipped by non-forced flushes;
- a forced flush ignores `nextRetryAt`;
- retry count is bounded before terminal dead-lettering.

Health status exposes ready/delayed queue information, flush success/failure counters, processed/failed counts, oldest queued age and flush duration.

### Dead letters

After retries are exhausted, or when queue pressure cannot accept a session, the reliability wrapper attempts to place it in a bounded in-memory dead-letter queue.

`persistDeadLetters()` writes terminal failure snapshots with an idempotent `session_uuid` upsert. Failed dead-letter writes are requeued only while the in-memory dead-letter limit permits.

Persisted rows are terminal failure history. The current code has no automatic database replay state machine, resolution status or operator replay command.

### Database-disabled mode

When `databaseEnabled=false`:

- the schema guard bypasses MariaDB;
- completed sessions are not retained for later writes;
- flush drains the normal queue;
- reliability flush clears the in-memory dead-letter queue;
- Analytics may still execute collection logic while enabled, but persistence is intentionally discarded.

### Missing or incompatible database

When database persistence is enabled, runtime startup checks the maximum applied migration version:

- missing/unreadable migration table blocks startup;
- schema version below `3` blocks startup;
- Analytics is disabled and the server continues;
- the error is exposed through status and `/analytics schema`.

This guard proves fail-closed collection startup for detectable schema incompatibility. It does not prove production credentials, network latency or database behaviour after startup.

### Shutdown

`stopRuntime()`:

- stops future ticks;
- finishes online sessions;
- closes remaining sessions using last combat time or current time;
- flushes the queue;
- the reliability wrapper then forces another retry pass and persists dead letters.

Dry-run tests exercise wrapper delegation and forced failure handling. Real shutdown scheduling and process-exit timing are not proven.

## Database schema and migrations

The baseline schema creates eight InnoDB tables:

1. `analytics_sessions`;
2. `analytics_session_monsters`;
3. `analytics_session_spells`;
4. `analytics_session_damage_types`;
5. `analytics_session_supplies`;
6. `analytics_session_loot`;
7. `analytics_dead_letters`;
8. `analytics_schema_migrations`.

The baseline records schema version `1`. Numbered migrations are contiguous from version `2`; current runtime requires version `3`.

The migration runner:

- discovers ordered `NNN_*.sql` files;
- computes SHA-256 for each migration;
- refuses a checksum mismatch for an already recorded version;
- applies only missing migrations;
- records version, filename and checksum;
- is intended to be repeatable.

Migration `002` adds server-version indexing. Migration `003` adds hunt/party context fields and hunt-area indexing. Current migration validators verify repeatable DDL contracts.

## Maintenance, aggregation and retention

The optional retention schema adds:

- `analytics_daily_balance` grouped by date, server version, hunt area, vocation and level bracket;
- `analytics_daily_party_balance` with the additional party-mode dimension;
- `analytics_maintenance_state` checkpoints;
- a `(started_at, id)` raw-session index.

The maintenance runner:

- validates all numeric and boolean configuration first;
- validates a strictly ascending positive `LEVEL_BRACKETS` list;
- rejects duplicate, descending, zero, nonnumeric and values above `2147483647` before Bash arithmetic;
- requires schema version `3` and all retention tables in database-backed mode;
- deletes and rebuilds a complete day in one transaction;
- preserves `server_version`, `hunt_area`, `vocation_id`, configured `level_bracket` and party mode;
- advances a catch-up checkpoint;
- rebuilds a bounded recent window to include late/corrected rows;
- leaves raw deletion disabled by default;
- deletes raw sessions only in bounded batches and only when covered by the aggregate checkpoint;
- requires `RAW_RETENTION_DAYS > REAGGREGATE_DAYS + AGGREGATION_LAG_DAYS` before deletion is enabled.

Party mode is currently classified as `solo` when `party_size_avg <= 1`, otherwise `party`.

### Configuration-only dry-run

```bash
VALIDATE_CONFIG_ONLY=true \
LEVEL_BRACKETS=50,100,200,300,400,600,800,1000 \
DELETE_RAW_SESSIONS=false \
bash tools/analytics/maintain_gameplay_analytics.sh
```

This mode prints the derived SQL `CASE` expression and exits before constructing or invoking a MariaDB command. Do not set `VALIDATE_CONFIG_ONLY=true` in the production systemd service.

## Reporting and Grafana

Reporting views are repeatable `CREATE OR REPLACE VIEW` definitions.

Long-range views read daily aggregate tables. Recent drill-down views read raw sessions/details and are intended for bounded ranges.

Current preserved reporting dimensions are:

- vocation;
- level bracket;
- hunt area;
- party mode in the dedicated party aggregate;
- server version.

Dashboard validation requires these dimensions in series identity and requires hunt-area/server-version filters. It rejects per-player variables. Ratio views use `NULLIF` for zero denominators, cap shared-experience percentage at `100%`, and label persisted dead letters as terminal history.

The dashboard is a reporting asset. Passing JSON/SQL validation does not prove correct Grafana provisioning, permissions, datasource latency or production query cost.

## Administrative commands

The gamemaster-only `/analytics` command supports:

- `/analytics` — current health/status;
- `/analytics flush` — forced queue retry pass;
- `/analytics deadletters` — attempts to persist in-memory dead letters;
- `/analytics schema` — schema readiness check;
- `/analytics enable` — enables until restart only if the schema guard passes, then registers already-online players;
- `/analytics disable` — stops runtime and disables until restart.

The commands do not replay persisted dead-letter records and do not perform production deployment.

## Tests that run without Canary and without MariaDB

The dedicated `Gameplay Analytics Dry Run` workflow defines no service container and no database connection.

| Test group | What it exercises | Important boundary |
| --- | --- | --- |
| Python contract validators | Config defaults, APIs, source wiring, wrapper order, migrations, retention, dashboards, deployment and supply/loot contracts | Source-shape evidence, not engine execution. |
| Python mutation tests | Validators reject deliberately broken source/contracts | Proves validator sensitivity only for included mutations. |
| `test_gameplay_analytics_context.lua` | Context sampling/finalization with mock players/parties/positions | No real map or party engine. |
| `test_gameplay_analytics_batching.lua` | SQL generation, sorted details and bounded batches with mock DB APIs | Does not execute SQL. |
| `test_gameplay_analytics_reliability.lua` | Retry delay, forced retries, dead-letter transition/persistence and database-disabled drain | Uses synthetic write success/failure. |
| `test_gameplay_analytics_correctness.lua` | Main non-combat, death and rollover behaviour | Synthetic clock/session core. |
| `test_gameplay_analytics_correctness_edge_cases.lua` | Exact UTC boundary, multi-day gap, same-day access, online/offline utility expiry, timeout clamp, short death, wrapper idempotency and finish exception restoration | Synthetic clock and players. |
| `test_gameplay_analytics_runtime_hooks.lua` | Direct mock invocation of registered damage, summon, PvP, mana, healing, EXP, kill, death, login, startup and shutdown callbacks | Does not prove real event order or uniqueness. |
| `test_gameplay_analytics_schema.lua` | Missing/old/current schema response and database-disabled bypass using mock DB handles | Does not connect to MariaDB. |
| Spell integration Lua test | Successful/failed cast behaviour and per-cast delta without adding to session totals | Does not execute a real combat object. |
| Supply/loot Lua tests | Price fallback, charge guards, corpse-owner attribution and optional feature gates | Selective integrations only. |
| Maintenance configuration shell test | Valid/invalid brackets, deletion safety and proof that config-only mode never invokes a fake `mariadb` | Does not validate SQL against a server. |
| Reporting asset parse | Grafana JSON and view SQL presence/parse checks | Does not provision Grafana. |

The deterministic dry-run does not load an OTBM map, sprites, monsters, NPCs or a network protocol.

## Tests that require MariaDB

| Test/workflow | Database evidence |
| --- | --- |
| Main Analytics MariaDB integration | Repeatable baseline import, eight InnoDB tables, foreign keys, session/detail/dead-letter idempotent upserts and cascades. |
| Schema migration integration | Ordered version application, version `3`, repeatability and checksum-mismatch refusal. |
| Retention MariaDB integration | Configured brackets, all reporting dimensions, weighted party/shared metrics, late-row rebuild, stale-group removal, bounded raw deletion and cascade cleanup. |
| Dashboard MariaDB integration | Repeatable views, correct sample ratios, solo/party separation, dimension preservation, zero denominators, terminal dead-letter semantics and representative index usage. |
| Supply/loot MariaDB integration | Persistence of reviewed supply/loot values through the real schema. |

These tests use an ephemeral MariaDB `11.4` service in GitHub Actions. They do not reproduce production users, permissions, topology, latency, backups, replication or dataset size.

## Audited correctness matrix

| Case | Current implementation evidence | Executable evidence | Conclusion |
| --- | --- | --- | --- |
| Exact UTC midnight | Correctness wrapper compares integer UTC days before `get()` | Edge-case Lua test | Deterministic logic verified. |
| Multi-day active gap | One old session is closed and one replacement starts | Edge-case Lua test | Deterministic logic verified; skipped days are not synthesized. |
| Same UTC day | Existing session is reused | Edge-case Lua test | Verified. |
| Utility/non-combat-only session | Final enqueue requires combat or death | Correctness tests, online/offline expiry tests | Discard behaviour verified. |
| Online/offline expiry | Online uses normal finish path; offline removes directly | Edge-case Lua test | Verified with mocks. |
| Exact timeout boundary | Timeout is clamped and applies at `>=` | Edge-case Lua test | Verified with deterministic clock. |
| Short death | Minimum temporarily becomes zero | Correctness tests | Verified with mocks. |
| Short UTC rollover fragment | Same minimum override as death | Correctness tests | Verified with mocks. |
| Wrapper idempotency | Installation flags | Context/batching/reliability/correctness tests | Verified for tested wrappers. |
| Exception during finish | `pcall` restores minimum before rethrow | Edge-case Lua test | Verified. |
| Direct non-player combat | Drain-health callback calls dealt recorder | Static validator plus runtime-hook mock | Lua callback logic verified. |
| Summon attribution | `ownerPlayer()` resolves player master | Static validator plus runtime-hook mock | Lua callback logic verified; engine master relationship not runtime-proven here. |
| PvP disabled | Both direct-player and player-summon paths use `trackPvP` | Static validator plus runtime-hook mock | Lua callback logic verified. |
| Mana accounting | Negative primary/secondary deltas are summed once per callback | Runtime-hook mock | Callback arithmetic verified; semantic source and real callback multiplicity not proven. |
| Spell mana double count | Spell helper never calls `recordManaSpent` | Static validator and spell Lua test | Deterministic integration verified. |
| Rune charges | Supply record is guarded by `REMOVE_RUNE_CHARGES` | Source validator and supply Lua test | Verified for the two integrated runes. |
| Supplies/loot default | Both config flags are false | Config validator | Verified default. |
| Queue limits | Normal and dead-letter queues are bounded | Reliability source/tests | Core transitions verified; sustained real pressure not proven. |
| Retry/backoff | Exponential delay with maximum cap | Reliability Lua test | Representative sequence verified. |
| Dead-letter lifecycle | In-memory terminal transition and idempotent DB snapshot | Reliability Lua + MariaDB upsert test | Verified within current design; no DB replay exists. |
| Idempotent writes | UUID/composite keys and upserts | MariaDB integration | Verified against ephemeral MariaDB. |
| Missing/old schema | Startup disables Analytics without stopping server | Schema Lua test | Wrapper behaviour verified; real startup log/order not proven. |
| Missing database after startup | Writes fail into bounded retry/dead-letter paths | Reliability mocks | Failure policy verified synthetically; real transport failure not proven. |
| Database-disabled mode | Schema bypass and queue/dead-letter drain | Schema/reliability Lua tests | Verified. |
| Shutdown/forced flush | Reliability wraps core stop and forces flush/dead letters | Source and runtime/reliability mocks | Delegation verified; process-exit timing not proven. |
| Invalid brackets | Duplicate, descending, zero, nonnumeric and overflow rejected | Shell dry-run test | Verified without database. |
| Raw deletion safety | Retention-window guard and checkpoint-covered bounded delete | Shell dry-run + MariaDB retention test | Verified against ephemeral MariaDB. |
| Reporting dimensions | Aggregate PK/grouping, views and dashboard series preserve all five dimensions | Validators + retention/dashboard MariaDB tests | Verified for synthetic rows. |

## What dry-run cannot prove

Dry-run does not prove:

- actual event-hook order in Canary;
- absence of duplicate engine callback delivery;
- that all real gameplay actions reach the intended hooks;
- performance on a real server;
- production MariaDB permissions, latency, failover or connection-pool behaviour;
- thread/concurrency safety;
- absence of memory leaks;
- stability across long uptime and restart cycles;
- behaviour at real player and queue volume;
- completeness or statistical representativeness of collected gameplay data;
- correct real-map hunt-area attribution;
- Grafana provisioning and production query performance;
- safe production retention without operator reconciliation;
- that an empty `server_version` cannot be introduced by bypassing the installer.

No conclusion about production readiness may be derived solely from green dry-run CI.

## Current source versus historical claims

| Claim | Current status |
| --- | --- |
| PR #135 corrected UTC rollover, non-combat eligibility, short deaths, rune-charge accounting, brackets, dashboard dimensions and dead-letter wording | Confirmed in current source and current tests where listed above. |
| PR #140 added no-server/no-database validation and fixed counter/bracket edge cases | Confirmed in current source/test files and re-executed by current-PR workflows. |
| Earlier PR CI was green | Historical evidence only. It is not a current-PR result. |
| Analytics is production-proven | False/not proven. No production or staging runtime evidence is recorded here. |
| Analytics detects bots, exploits or item duplication | False. Those capabilities do not exist in the current module. |
| Persisted dead letters are automatically replayed | False. They are terminal failure history. |
| Current reporting is anonymous | Not strictly. Dashboard surfaces are aggregate-only, but raw sessions keep player IDs and names unless name anonymization is enabled. |

## Current verification record

- Audited base before task branch: `3a390c9d892c5b737d32711a71dbdf7fff1f06fe`.
- Pull request: `#330`.
- Complete implementation/test evidence head: `34d16130d5e18653b69e1fa949b578436e92e046`.
- The commit containing this record is documentation-only relative to that test head. The same workflow families are configured to run again because this document is included in their path filters.
- Local checkout: **not executed** — the tool sandbox could not resolve GitHub for a repository clone; no local pass is claimed.

| Test/workflow | Commit | Result | Evidence |
| --- | --- | --- | --- |
| Agent Task Ownership | `34d16130d5e18653b69e1fa949b578436e92e046` | passed | GitHub Actions run `29328811829`. |
| Gameplay Analytics Dry Run — No server or database | `34d16130d5e18653b69e1fa949b578436e92e046` | passed | Run `29328811882`; static validators, Python tests, configuration-only shell checks, all mocked Lua tests including runtime hooks, and reporting parse passed. |
| Gameplay Analytics — validators/Lua | `34d16130d5e18653b69e1fa949b578436e92e046` | passed | Run `29328811876`, job `validate`, including the new runtime-hook dry-run. |
| Gameplay Analytics — MariaDB integration | `34d16130d5e18653b69e1fa949b578436e92e046` | passed | Run `29328811876`, job `mariadb-integration`; schema, persistence and migrations passed. |
| Gameplay Analytics Retention | `34d16130d5e18653b69e1fa949b578436e92e046` | passed | Run `29328811871`; validator/systemd and MariaDB aggregation/retention jobs passed. |
| Gameplay Analytics Dashboards | `34d16130d5e18653b69e1fa949b578436e92e046` | passed | Run `29328811920`; validator and MariaDB reporting-view jobs passed. |
| Gameplay Analytics Spell Telemetry | `34d16130d5e18653b69e1fa949b578436e92e046` | passed | Run `29328811918`. |
| Gameplay Analytics Supply and Loot Telemetry | `34d16130d5e18653b69e1fa949b578436e92e046` | passed | Run `29328811868`; Lua/validator and MariaDB jobs passed. |
| Gameplay Analytics Hunt Areas | `34d16130d5e18653b69e1fa949b578436e92e046` | passed | Run `29328811914`. |
| General CI | `34d16130d5e18653b69e1fa949b578436e92e046` | passed | Run `29328812062`. |

## Production/staging gate

Before production enablement:

1. Install and migrate a disposable or staging MariaDB with production-like permissions.
2. Export a stable non-empty `CANARY_SERVER_VERSION` to the Canary process.
3. Start a staging Canary with Analytics still disabled and run `/analytics schema` and `/analytics status`.
4. Enable deliberately and exercise real login, combat, summon, healing, mana, spell, death, logout and shutdown paths.
5. Compare raw rows, daily aggregates and dashboard values across several complete UTC days.
6. Simulate database interruption and recovery while observing bounded queues, retries, dead letters and server responsiveness.
7. Run load/soak tests for memory, queue pressure, flush latency and long-term stability.
8. Keep `DELETE_RAW_SESSIONS=false` until aggregates have been reconciled against raw sessions.

## Oteryn migration and future analytics handoff

This section is architecture and migration planning only. It does not implement Oteryn, Security Analytics or a live AI agent.

### Target architecture

```text
Oteryn Engine
    ↓
Common Event / Telemetry Collector
    ├── Gameplay Analytics
    └── Security Analytics
            ↓
       AI Investigation Layer
```

### 1. Common event / telemetry foundation

Oteryn should provide one lightweight event collector shared by Gameplay Analytics and future Security Analytics.

The collector should:

- run inside the engine process;
- emit explicit, versioned event records;
- buffer rather than synchronously persist or analyse every hit;
- remain fail-open for gameplay;
- never block combat on analytics storage;
- use bounded queues and observable drop/failure counters;
- carry `event_id`, `transaction_id`, `correlation_id` and `server_version` where applicable;
- separate event capture from aggregation and investigation;
- avoid sending every hit directly to AI;
- give no AI component permission to mutate runtime state;
- support deterministic replay into test consumers without replaying effects into gameplay.

The current Canary session wrapper stack is useful design evidence, but Oteryn should not copy the Lua wrappers as the engine-level event contract. Define the event schema first, then build adapters/aggregators.

### 2. Gameplay Analytics

The Oteryn Gameplay Analytics consumer should calculate or aggregate:

- experience per hour;
- damage dealt/received;
- healing and overhealing;
- deaths;
- spell efficiency;
- supplies and loot;
- vocation balance;
- solo versus party performance;
- comparisons across engine/server versions;
- gameplay regression indicators.

It should primarily use aggregates and privacy-preserving identifiers. Raw player-linked data should have a documented purpose, access policy and retention window.

Gameplay Analytics must remain observational. It must not change combat outcomes or balance automatically.

### 3. Security Analytics

Security Analytics does not exist in the current Canary Gameplay Analytics module and must not be inferred from it. It is a future separate consumer.

Future Security Analytics may detect or investigate:

- bots and automation patterns;
- exploits and hidden bug abuse;
- item duplication;
- unnatural transfers;
- repeated rewards;
- cooldown violations;
- market, trade, mail and depot inconsistencies;
- provenance of items and currency;
- transaction-invariant violations.

It requires finer-grained authoritative events than Gameplay Analytics, including:

- item create and destroy;
- split and merge;
- move;
- trade;
- market;
- mail;
- depot;
- quest reward;
- currency change;
- rollback and retry;
- transaction commit;
- session ownership;
- storage transition.

These events should be correlated by transaction identifiers and checked by deterministic invariants. Do not overload aggregate combat sessions to serve as an economy ledger.

### 4. AI Investigation Layer

AI must stay outside the game process and outside the authoritative transaction path.

An investigation agent should:

- use read-only data, replicas or restricted views;
- run periodically or after a deterministic alert;
- correlate anomalies into hypotheses;
- identify likely modules and affected versions;
- prepare an evidence package for a human reviewer;
- never ban solely from an anomaly score;
- never change balance;
- never mutate production data;
- never make automatic commits or deployments;
- never receive runtime mutation capabilities.

Hard invariants, idempotency, authorization and transaction safety must be deterministic without AI. AI is an investigation layer, not an enforcement or gameplay-control layer.

### Migration classification

| Element | Status | Decision for Oteryn | Required evidence |
| --- | --- | --- | --- |
| Session model | ADAPT | Preserve aggregate-session concepts but derive them from versioned engine events. | Event-schema review and replay tests. |
| UTC rollover | REUSE | Reuse the UTC-day split rule for daily reporting. | Boundary unit tests in Oteryn time abstraction. |
| Non-combat eligibility | REUSE | Keep combat/death eligibility for gameplay session counts. | Event-replay tests including utility-only activity. |
| Short-death retention | REUSE | Preserve deaths even below normal duration. | Boundary tests and metric reconciliation. |
| Bounded queues | REUSE | Mandatory for all in-process collectors. | Load tests, drop counters and fail-open proof. |
| Retry | ADAPT | Retain bounded exponential backoff in an asynchronous persistence component. | Transport-failure and restart tests. |
| Dead letters | ADAPT | Add explicit lifecycle/status, operator replay and resolution audit if replay is required. | Replay idempotency and access-control tests. |
| Idempotent writes | REUSE | Keep stable event/session IDs and upserts or deduplicating inserts. | Duplicate-delivery integration tests. |
| Schema versioning | REUSE | Version both event and storage schemas. | Compatibility and downgrade/upgrade matrix. |
| Migration checksums | REUSE | Preserve immutable ordered migration checksums. | Clean/upgrade/modified-migration tests. |
| Maintenance | ADAPT | Move SQL maintenance behind an Oteryn-owned operational component. | Backlog, interruption and late-data tests. |
| Retention | REVALIDATE | Set policy from privacy, investigation and rollback requirements. | Data-classification and deletion/reconciliation review. |
| Dashboards | ADAPT | Reuse metric definitions, rebuild datasource/provisioning for Oteryn. | Query reconciliation on Oteryn synthetic and staging data. |
| Lua tests | DO_NOT_MIGRATE | Keep as Canary regression evidence; rewrite in Oteryn's test language. | Equivalent Oteryn unit/replay coverage. |
| Python validators | ADAPT | Reuse contract-validation ideas against Oteryn schemas/config/assets. | Mutation tests for new validators. |
| Shell tests | ADAPT | Reuse configuration-safety scenarios where shell operations remain. | Platform-specific CI and failure tests. |
| MariaDB integration | REVALIDATE | Reuse only if Oteryn retains MariaDB and compatible schema semantics. | Real target database integration and migration tests. |
| Runtime hooks | REWRITE | Replace Lua callback interception with explicit engine event emission. | Engine unit/integration and real-client staging tests. |
| Summon attribution | ADAPT | Emit authoritative owner identity in the event instead of resolving later where possible. | Summon ownership lifecycle tests. |
| Spell telemetry | ADAPT | Emit cast IDs and correlate damage/healing outcomes without double counting. | Multi-target, delayed-effect and failed-cast tests. |
| Supply telemetry | REWRITE | Generalize from selected script hooks to authoritative consumption events. | Coverage inventory and charge/removal transaction tests. |
| Loot telemetry | REWRITE | Emit authoritative loot/item creation and ownership events. | Corpse, party-rights and item-provenance tests. |
| Player identifiers | REWRITE | Use privacy-scoped pseudonymous analytics IDs; separate operational identity access. | Privacy model, rotation/linkability and access-control review. |
| Anonymization | ADAPT | Replace name-only suppression with a documented pseudonymization policy. | Re-identification and retention review. |
| Admin commands | ADAPT | Keep read-only health/flush/schema controls with audited authorization. | Permission, misuse and operational runbook tests. |
| CI workflows | ADAPT | Preserve layered dry-run/database/runtime gates using Oteryn tooling. | Required-check emission and final-head workflow proof. |
| Common telemetry collector | REWRITE | Build as a new Oteryn engine subsystem; do not embed the Canary Lua stack. | Performance, queue, ordering and fail-open tests. |
| Security Analytics | FUTURE_SECURITY_MODULE | Implement separately after authoritative transaction events exist. | Threat model, invariant catalogue and labelled incident evidence. |
| Live AI in engine | DO_NOT_MIGRATE | Keep AI outside runtime and transaction paths. | Architecture/security review. |
| AI investigation layer | FUTURE_SECURITY_MODULE | Read-only, alert-driven evidence correlation only. | Access-control, auditability and human-review workflow. |

### Oteryn reuse summary

Ready to reuse as rules or patterns:

- UTC daily split;
- combat/death session eligibility;
- short-death retention;
- bounded queues;
- idempotency keys and writes;
- schema versions and migration checksums;
- layered deterministic dry-run and database integration tests.

Requires adaptation:

- session model;
- retries and dead-letter operations;
- maintenance, retention and dashboards;
- spell/summon attribution;
- validators, shell tooling, administration and CI.

Requires revalidation:

- target database integration;
- privacy/retention policy;
- performance, concurrency and long-running behaviour;
- all real engine hook/event semantics.

Should not be migrated directly:

- Canary Lua wrapper implementation as the Oteryn engine collector;
- any assumption that current player IDs/names are sufficiently anonymous;
- live AI in the engine;
- claims that aggregate Gameplay Analytics can detect item duplication or transaction exploits.

Reserved for future Security Analytics:

- transaction and item/currency ledgers;
- deterministic economy invariants;
- anomaly investigation;
- read-only AI evidence correlation.

## Remaining limitations

Even after all repository checks pass, the following remain open until staging/production-like evidence exists:

- real event ordering and exactly-once assumptions;
- real coverage of gameplay actions;
- database interruption/recovery with actual Canary callbacks;
- queue and memory behaviour under load;
- concurrency safety;
- long-running stability;
- production privacy and retention approval;
- statistical validity of balance conclusions;
- complete supply, loot and spell integration inventory;
- Oteryn event schema and engine implementation;
- all Security Analytics and AI Investigation functionality.
