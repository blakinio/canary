# Gameplay Analytics

Gameplay Analytics collects aggregated hunt data for vocation balancing. The subsystem is disabled by default and is configured in:

```text
data-otservbr-global/scripts/config/gameplay_analytics.lua
```

## Installation

1. Apply `schema/gameplay_analytics.sql` to the Canary MariaDB database.
2. Run `tools/analytics/migrate_gameplay_analytics.sh` with the production database connection variables.
3. Run `/analytics schema` as a gamemaster and confirm that the current version matches the required version.
4. Set `enabled = true` in the Lua configuration.
5. Restart Canary.
6. Verify startup logs contain `[GameplayAnalytics] Enabled`.
7. Run `/analytics status` as a gamemaster.

For a repeatable production rollout with an example environment file, an installation script and rollback guidance, see `docs/systems/gameplay-analytics-deployment.md`.

The feature does not issue SQL writes for individual hits. Data is accumulated in memory and flushed as completed sessions. A retry writes the complete in-memory session snapshot and upserts every aggregate by its natural key.

## Configuration

| Setting | Default | Purpose |
|---|---:|---|
| `enabled` | `false` | Master switch. |
| `databaseEnabled` | `true` | Persist completed sessions. When disabled, completed sessions are discarded instead of retained in memory. |
| `flushIntervalSeconds` | `300` | Queue flush interval; minimum runtime value is 30 seconds. |
| `minimumSessionSeconds` | `60` | Discard shorter ordinary sessions. Death and UTC day rollover fragments are preserved so deaths and cross-day combat are not lost. |
| `combatTimeoutSeconds` | `120` | Split hunts after inactivity. It also bounds non-combat activity sessions. Idle timeout time is not added to `combat_seconds`. |
| `includeStaff` | `false` | Allow staff characters to be considered. Account types listed in `excludedAccountTypes` remain excluded. |
| `trackPvP` | `false` | Include player-versus-player and player-summon damage. |
| `trackSpells` | `true` | Store spell aggregates reported through the API. |
| `trackMonsters` | `true` | Store per-monster aggregates. |
| `trackDamageTypes` | `true` | Store primary and secondary combat damage under their own combat types. |
| `trackSupplies` | `false` | Store supply use reported through the API. |
| `trackLoot` | `false` | Store loot reported through the API. |
| `anonymizePlayers` | `false` | Do not persist character names. Player IDs remain for relational integrity. |
| `queueLimit` | `10000` | Maximum completed sessions awaiting persistence. |
| `detailBatchSize` | `250` | Maximum detail rows per multi-row upsert; runtime range is 1–1000. |
| `maxRetryAttempts` | `5` | Maximum retries after the initial failed persistence attempt. |
| `retryBaseDelaySeconds` | `30` | Initial retry delay. |
| `retryMaxDelaySeconds` | `900` | Maximum retry delay after exponential backoff. |
| `deadLetterQueueLimit` | `1000` | Maximum failed sessions waiting to be written to `analytics_dead_letters`. |
| `detailLevel` | `1` | Reserved detail tier from 0 to 2. |
| `excludedPlayerNames` | `{}` | Character names excluded from collection. |
| `excludedAccountTypes` | GM/God | Account types excluded even when staff collection is allowed. |

Level brackets are not a runtime Lua option. They are an external maintenance aggregation setting named `LEVEL_BRACKETS`; see `docs/systems/gameplay-analytics-retention.md`.

## Automatically collected data

The runtime hooks collect:

- raw and final experience, including per-monster raw experience;
- outgoing and incoming damage after combat calculation;
- effective self-healing, healing of others and overhealing;
- negative mana changes;
- monster kills and deaths;
- vocation, level, party size and shared-experience state;
- damage grouped by primary and secondary combat type;
- combat and session duration.

Outgoing damage to monsters is collected through the engine-wide drain-health callback, including damage caused by player-owned summons. Damage involving another player or a player-owned summon is excluded unless `trackPvP = true`.

## Session lifecycle and data eligibility

Sessions are created lazily on the first recorded metric. Merely logging in and remaining online does not create an empty database row.

A session is eligible for persistence only when it contains combat or a death. **Non-combat sessions** created by utility mana use, a spell-detail callback, supply use or loot-only activity expire after `combatTimeoutSeconds` and are discarded instead of increasing hunt-session counts.

When a combat timeout closes a session, `combat_seconds` ends at the last recorded combat event rather than when the timeout worker runs.

### UTC day rollover

Before recording the first metric on a later UTC date, the runtime closes the previous session with the reason `utc-day-rollover` and creates a new session. A short rollover fragment is retained even below `minimumSessionSeconds`. This keeps daily maintenance from assigning post-midnight events to the previous day merely because the player remained online.

### Deaths shorter than the normal minimum

**Short death sessions** are retained even when they last less than `minimumSessionSeconds`. The ordinary minimum still removes short, non-death noise, but it cannot suppress a real death from the balance statistics.

The status command exposes `dayRollovers`, `discardedNonCombatSessions`, `expiredNonCombatSessions`, `shortDeathSessionsPersisted` and `shortRolloverSessionsPersisted` for rollout verification.

The `mana_spent` aggregate represents all negative mana changes observed by the mana-change event. Depending on server mechanics, this can include mana shield damage in addition to spell and rune costs. Mana-only sessions are not persisted as hunts unless combat or a death also occurs.

## Reliability and retry behaviour

A failed session or detail write is retried with exponential backoff. The delay starts at `retryBaseDelaySeconds` and is capped at `retryMaxDelaySeconds`. Manual `/analytics flush` and server shutdown force delayed entries to make one immediate attempt.

After `maxRetryAttempts` retries, the session leaves the normal queue and enters a bounded in-memory dead-letter queue. The runtime then tries to upsert a compact terminal failure record into `analytics_dead_letters`. The record contains the session UUID, player reference, retry count, last error and the main aggregate counters. Dead-letter writes are idempotent by `session_uuid`.

Persisted dead-letter rows are an investigation history, not an automatic database replay queue. `/analytics deadletters` retries persistence of records still waiting in the process-local dead-letter queue; it does not replay rows already stored in MariaDB.

A database outage therefore does not block gameplay. Normal sessions remain bounded by `queueLimit`, dead letters remain bounded by `deadLetterQueueLimit`, and all overflows are logged and counted.

## Schema compatibility

The runtime checks `analytics_schema_migrations` before starting database-backed collection. Analytics remains stopped when the migration table is missing or its version is lower than the code requires. The game server itself continues to run normally.

Run the migration command before enabling a newer runtime:

```bash
DB_HOST=127.0.0.1 \
DB_PORT=3306 \
DB_USER=canary \
DB_PASSWORD='your-password' \
DB_NAME=canary \
bash tools/analytics/migrate_gameplay_analytics.sh
```

Applied migration files are protected by SHA-256 checksums. Add a new numbered migration instead of editing a migration that has already been deployed.

## Optional integration API

Scripts can report domain-specific data that cannot be inferred reliably from generic combat events:

```lua
GameplayAnalytics.recordSpell(player, spellName, damage, healing, mana, targets, critical)
GameplayAnalytics.recordSupply(player, itemId, amount, unitValue)
GameplayAnalytics.recordLoot(player, itemId, amount, npcValue, marketValue)
```

`recordSpell` stores the spell's own mana aggregate but does not add it again to the session-wide `mana_spent` value, because generic mana-change events already collect that value.

Supply and loot collection remain disabled until enabled in the configuration. Integrated runes record their supply cost only when `configKeys.REMOVE_RUNE_CHARGES` is enabled, matching the server's `REMOVE_RUNE_CHARGES` behavior. Infinite-charge rune configurations therefore do not create fictional supply expenses.

## Administrative commands

```text
/analytics status
/analytics flush
/analytics deadletters
/analytics schema
/analytics enable
/analytics disable
```

`/analytics flush` forces normal and delayed retry entries to run immediately. `/analytics deadletters` retries persistence of the current process-local dead-letter queue. `/analytics schema` rechecks the installed database version and reports the current and required versions. Runtime enable/disable does not edit the Lua configuration and resets after restart. Runtime enable registers the required creature events for players who are already online.

The status output includes:

- schema readiness and version fields;
- active, queued, retrying and process-local dead-letter counts;
- successful/failed flush and persistence counters;
- retry, drop, batching and queue-age counters;
- context sampling/finalization counters;
- UTC rollover, non-combat discard and short-death/rollover counters.

These counters intentionally have no per-player, per-spell or per-monster labels.

## Recommended rollout

Start with:

```lua
enabled = true
databaseEnabled = true
trackMonsters = true
trackDamageTypes = true
trackSpells = false
trackSupplies = false
trackLoot = false
detailLevel = 1
```

After validating schema readiness, CPU, memory, queue depth, retry counters, lifecycle counters and data quality, enable explicit spell, supply and loot reporting. Use a new `CANARY_SERVER_VERSION` when deploying changed collection or aggregation semantics.

## Example balance queries

### Vocation performance by configured daily level bracket

Long-range analysis should read the maintained view rather than reproduce bracket logic in ad hoc SQL:

```sql
SELECT
    vocation_id,
    level_bracket,
    hunt_area,
    server_version,
    SUM(sessions) AS sessions,
    ROUND(SUM(exp_per_hour * combat_seconds) / NULLIF(SUM(combat_seconds), 0)) AS weighted_exp_per_hour
FROM analytics_daily_vocation_metrics
WHERE session_date BETWEEN '2026-07-01' AND '2026-07-31'
GROUP BY vocation_id, level_bracket, hunt_area, server_version
HAVING SUM(sessions) >= 20;
```

### Solo versus party

```sql
SELECT
    vocation_id,
    level_bracket,
    hunt_area,
    server_version,
    mode,
    SUM(sessions) AS sessions,
    ROUND(SUM(exp_per_hour * combat_seconds) / NULLIF(SUM(combat_seconds), 0)) AS weighted_exp_per_hour
FROM analytics_daily_party_mode_metrics
GROUP BY vocation_id, level_bracket, hunt_area, server_version, mode;
```

### Spell efficiency

```sql
SELECT
    s.vocation_id,
    p.spell_name,
    SUM(p.casts) AS casts,
    ROUND(SUM(p.damage) / NULLIF(SUM(p.casts), 0)) AS damage_per_cast,
    ROUND(SUM(p.healing) / NULLIF(SUM(p.casts), 0)) AS healing_per_cast,
    ROUND((SUM(p.damage) + SUM(p.healing)) / NULLIF(SUM(p.mana_spent), 0), 2) AS output_per_mana
FROM analytics_session_spells p
JOIN analytics_sessions s ON s.id = p.session_id
GROUP BY s.vocation_id, p.spell_name
HAVING SUM(p.casts) >= 100;
```

## Operational safeguards

- Disabled mode returns before creating sessions.
- Sessions are created only after a metric is recorded.
- Persistence rejects sessions without combat or death.
- Ordinary short sessions are filtered, but real deaths and UTC rollover fragments are retained.
- Staff characters, PvP and player-summon combat are excluded by default.
- Database-backed Analytics does not start against an incompatible schema.
- Completed sessions, detail SQL batches, retries and dead letters are bounded.
- Database-disabled mode does not accumulate an undrainable queue.
- Session, detail and dead-letter writes use idempotent upserts.
- Database failures do not stop the game server.
- Player names can be omitted from analytics records.
- Prometheus labels are intentionally not added per player, spell or monster to avoid cardinality problems.
