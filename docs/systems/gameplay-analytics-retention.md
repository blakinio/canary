# Gameplay Analytics retention and daily aggregates

Raw hunt sessions are useful for investigation but should not grow forever. The optional schema `schema/gameplay_analytics_retention.sql` adds:

- `analytics_daily_balance` — long-lived daily balance aggregates;
- `analytics_daily_party_balance` — separate daily solo/party aggregates;
- `analytics_maintenance_state` — checkpoints and maintenance counters;
- `(started_at, id)` on `analytics_sessions` for ordered batch deletion.

Apply it only after the main Gameplay Analytics schema and migrations. The maintenance process is external to the game server, so a slow report or cleanup cannot block combat processing.

## Safety defaults

Raw deletion is disabled by default:

```bash
DELETE_RAW_SESSIONS=false
```

The first production runs should only aggregate. Review both daily tables and compare their totals with raw queries before enabling deletion.

The runner never deletes a session newer than the configured retention cutoff and never deletes beyond the `daily_aggregate_through` checkpoint. Detail tables are removed through their existing `ON DELETE CASCADE` foreign keys.

A rolling correction window is also enabled by default:

```bash
REAGGREGATE_DAYS=7
```

Every run deletes and rebuilds each complete day in that recent window inside a transaction. This picks up delayed session flushes and corrected raw dimensions without leaving stale aggregate groups. When raw deletion is enabled, `RAW_RETENTION_DAYS` must be greater than `REAGGREGATE_DAYS + AGGREGATION_LAG_DAYS`, so the rolling rebuild never reaches data already removed by retention.

## Install the optional schema

```bash
mariadb -u canary -p canary < schema/gameplay_analytics_retention.sql
```

The file is repeatable on MariaDB 11.4+. It does not change the schema version required by the game runtime; retention can be enabled or disabled independently.

## Manual run

```bash
DB_HOST=127.0.0.1 \
DB_PORT=3306 \
DB_USER=canary \
DB_PASSWORD='your-password' \
DB_NAME=canary \
AGGREGATION_LAG_DAYS=1 \
MAX_DAYS_PER_RUN=31 \
REAGGREGATE_DAYS=7 \
LEVEL_BRACKETS=50,100,200,300,400,600,800,1000 \
RAW_RETENTION_DAYS=180 \
DELETE_RAW_SESSIONS=false \
bash tools/analytics/maintain_gameplay_analytics.sh
```

The runner requires the main Analytics schema version `3` and all three optional retention tables. It processes historical dates sequentially and writes `daily_aggregate_through` after every successful day, so an interrupted catch-up resumes from the next date. It then rebuilds the bounded recent window independently of that checkpoint.

## Configuration

| Variable | Default | Purpose |
|---|---:|---|
| `AGGREGATION_LAG_DAYS` | `1` | Do not aggregate the newest incomplete days. |
| `MAX_DAYS_PER_RUN` | `31` | Bound historical catch-up work per invocation. |
| `REAGGREGATE_DAYS` | `7` | Rebuild this many recent complete days on every run. |
| `LEVEL_BRACKETS` | `50,100,200,300,400,600,800,1000` | Strictly ascending lower-bound transitions used to classify `level_start`. |
| `RAW_RETENTION_DAYS` | `180` | Raw sessions older than this may be deleted after aggregation. |
| `DELETE_RAW_SESSIONS` | `false` | Explicit deletion switch. |
| `DELETE_BATCH_SIZE` | `5000` | Maximum sessions removed by one SQL delete. |
| `DELETE_MAX_BATCHES` | `20` | Maximum delete batches per invocation. |

A large historical backlog is intentionally processed over several runs. This avoids one maintenance execution monopolizing MariaDB.

### Level-bracket contract

`LEVEL_BRACKETS` must be a comma-separated, strictly ascending list of positive integers. Malformed, duplicate or descending input is rejected before any MariaDB access.

The default list produces these buckets:

```text
0-49      -> 0
50-99     -> 50
100-199   -> 100
200-299   -> 200
300-399   -> 300
400-599   -> 400
600-799   -> 600
800-999   -> 800
1000+     -> 1000
```

The stored `level_bracket` is the lower bound shown on the right. This setting belongs to the maintenance process because daily aggregation assigns the bracket; the runtime Lua configuration does not duplicate it.

Changing `LEVEL_BRACKETS` changes reporting dimensions. Keep raw deletion disabled, use a new `CANARY_SERVER_VERSION`, and rebuild the required dates before comparing old and new data. Existing daily rows are replaced when their dates are reaggregated.

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

`analytics_daily_party_balance` uses the same dimensions plus:

```text
party_mode = solo | party
```

The mode is assigned to each raw session before grouping, using its time-weighted average party size: values at or below `1` are `solo`, and values above `1` are `party`. Therefore separate solo and party sessions can never be merged into one daily mode. A single session that itself changes between solo and party is classified by its dominant time-weighted result; exact within-session metric splitting would require segment-level telemetry that the current raw schema intentionally does not store.

Average party size is derived as:

```sql
party_size_weighted / NULLIF(party_weight_seconds, 0)
```

Party weighting uses combat seconds only. Shared-experience seconds are clamped per raw session to that session's combat time before summing, so the resulting dashboard percentage cannot be inflated by context sampling outside combat or exceed `100%`.

The runtime closes a session before recording the first metric on a later UTC day. Maintenance still groups by `started_at`, but post-midnight events now belong to the newly created session rather than the previous day's row.

For every rebuilt date, the runner deletes the old daily rows and inserts their complete replacements in one transaction. Re-running the same day does not add counters twice, delayed rows appear on the next run, and corrected dimensions remove stale groups.

## Recommended schedule

Run once per day after the aggregation lag using the ready-to-use systemd units in `tools/analytics/systemd/`:

- `gameplay-analytics-maintenance.service` — a oneshot service that loads `/etc/canary/gameplay-analytics-maintenance.env` and runs `maintain_gameplay_analytics.sh`;
- `gameplay-analytics-maintenance.timer` — a systemd timer that schedules the service daily at 04:30 UTC with `Persistent=true` and a randomized delay;
- `gameplay-analytics-maintenance.env.example` — the environment template, with safe aggregation and deletion defaults.

Use a database account restricted to the Analytics tables.

### Install

```bash
sudo cp tools/analytics/systemd/gameplay-analytics-maintenance.env.example /etc/canary/gameplay-analytics-maintenance.env
sudo chmod 600 /etc/canary/gameplay-analytics-maintenance.env
# Edit the copy with the real DB_PASSWORD and intended LEVEL_BRACKETS.

sudo cp tools/analytics/systemd/gameplay-analytics-maintenance.service /etc/systemd/system/
sudo cp tools/analytics/systemd/gameplay-analytics-maintenance.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now gameplay-analytics-maintenance.timer
```

The unit's `WorkingDirectory` and `ExecStart` assume Canary is deployed at `/opt/canary`; adjust both paths in the copied unit file if your deployment uses a different path. Run the first several executions with `DELETE_RAW_SESSIONS=false` so only aggregation happens.

Check the result with:

```bash
systemctl status gameplay-analytics-maintenance.timer
sudo journalctl -u gameplay-analytics-maintenance.service
```

### Uninstall

```bash
sudo systemctl disable --now gameplay-analytics-maintenance.timer
sudo rm /etc/systemd/system/gameplay-analytics-maintenance.service /etc/systemd/system/gameplay-analytics-maintenance.timer
sudo systemctl daemon-reload
```

This stops future scheduled runs. It does not modify or delete data already written to the aggregate or maintenance tables.

## Rollout procedure

1. Back up the MariaDB database.
2. Apply the main Analytics migrations and `gameplay_analytics_retention.sql`.
3. Set and record the intended `LEVEL_BRACKETS` and `CANARY_SERVER_VERSION`.
4. Run for at least several days with `DELETE_RAW_SESSIONS=false`.
5. Compare both daily aggregate tables with raw queries for several dates, vocations, brackets, hunts and solo/party modes.
6. Confirm the rolling rebuild picks up a deliberately delayed test session in a non-production environment.
7. Enable deletion only with a conservative `RAW_RETENTION_DAYS` outside the lag plus rebuild window.
8. Monitor runtime, deleted-row counters, MariaDB load and table size.

## Recovery

A wrong or missing aggregate remains recoverable while its raw sessions still exist. Recent dates are rebuilt automatically. For an older date, move the `daily_aggregate_through` checkpoint backward or remove it, then rerun maintenance with enough `MAX_DAYS_PER_RUN` capacity to reach that date.

Deleting raw sessions is not reversible without a backup. The script deliberately requires an explicit deletion flag, a completed aggregate checkpoint and a retention margin outside the rolling rebuild window, but these safeguards do not replace database backups.
