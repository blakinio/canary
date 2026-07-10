# Gameplay Analytics retention and daily aggregates

Raw hunt sessions are useful for investigation but should not grow forever. Migration `004_daily_retention.sql` adds:

- `analytics_daily_balance` — long-lived daily aggregates;
- `analytics_maintenance_state` — checkpoints and maintenance counters;
- `(started_at, id)` on `analytics_sessions` for ordered batch deletion.

The maintenance process is external to the game server. A slow report or cleanup therefore cannot block combat processing.

## Safety defaults

Raw deletion is disabled by default:

```bash
DELETE_RAW_SESSIONS=false
```

The first production runs should only aggregate. Review the resulting rows and query totals before enabling deletion.

The runner never deletes a session newer than the configured retention cutoff and never deletes beyond the `daily_aggregate_through` checkpoint. Detail tables are removed by their existing `ON DELETE CASCADE` foreign keys.

## Manual run

```bash
DB_HOST=127.0.0.1 \
DB_PORT=3306 \
DB_USER=canary \
DB_PASSWORD='your-password' \
DB_NAME=canary \
AGGREGATION_LAG_DAYS=1 \
MAX_DAYS_PER_RUN=31 \
RAW_RETENTION_DAYS=180 \
DELETE_RAW_SESSIONS=false \
bash tools/analytics/maintain_gameplay_analytics.sh
```

The script requires migration version `4`. It processes dates sequentially and records `daily_aggregate_through` after every successful day, so interruption resumes from the next date.

## Configuration

| Variable | Default | Purpose |
|---|---:|---|
| `AGGREGATION_LAG_DAYS` | `1` | Do not aggregate the newest incomplete days. |
| `MAX_DAYS_PER_RUN` | `31` | Bound catch-up work per invocation. |
| `RAW_RETENTION_DAYS` | `180` | Raw sessions older than this may be deleted after aggregation. |
| `DELETE_RAW_SESSIONS` | `false` | Explicit deletion switch. |
| `DELETE_BATCH_SIZE` | `5000` | Maximum sessions removed by one SQL delete. |
| `DELETE_MAX_BATCHES` | `20` | Maximum delete batches per invocation. |

A large historical backlog is intentionally processed over several runs. This avoids one maintenance execution monopolizing MariaDB.

## Aggregation dimensions

Each `analytics_daily_balance` row is grouped by:

```text
session_date
server_version
hunt_area
vocation_id
level_bracket
```

It stores session count, combat time, experience, damage, healing, mana, deaths, loot, supplies, weighted party size and shared-experience seconds.

Average party size is derived as:

```sql
party_size_weighted / NULLIF(party_weight_seconds, 0)
```

The daily upsert replaces the full aggregate for a dimension. Re-running the same day does not add counters twice.

## Recommended schedule

Run once per day after the aggregation lag. Example systemd service:

```ini
[Unit]
Description=Gameplay Analytics maintenance
After=network-online.target mariadb.service

[Service]
Type=oneshot
EnvironmentFile=/etc/canary/gameplay-analytics-maintenance.env
WorkingDirectory=/opt/canary
ExecStart=/usr/bin/bash tools/analytics/maintain_gameplay_analytics.sh
```

Example systemd timer:

```ini
[Unit]
Description=Run Gameplay Analytics maintenance daily

[Timer]
OnCalendar=*-*-* 04:30:00
Persistent=true
RandomizedDelaySec=900

[Install]
WantedBy=timers.target
```

Use a database account restricted to the Analytics tables.

## Rollout procedure

1. Back up the MariaDB database.
2. Apply migration `004_daily_retention.sql` through the migration runner.
3. Run for at least several days with `DELETE_RAW_SESSIONS=false`.
4. Compare daily aggregates with raw queries for several dates and vocations.
5. Enable deletion with a conservative `RAW_RETENTION_DAYS`, such as `180`.
6. Monitor runtime, deleted-row counters, MariaDB load and table size.

## Recovery

Deleting an aggregate row is recoverable while its raw sessions still exist: move the `daily_aggregate_through` checkpoint backward or remove it, then rerun maintenance.

Deleting raw sessions is not reversible without a backup. The script deliberately requires an explicit deletion flag and a completed aggregate checkpoint, but these safeguards do not replace database backups.
