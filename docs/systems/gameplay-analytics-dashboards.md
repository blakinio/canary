# Gameplay Analytics Grafana reporting package

This document covers the SQL reporting views, the Grafana dashboard, and how to install both. It does not change Analytics collection behavior; it reads tables created by the main schema, migrations and retention package.

## Files

- `schema/gameplay_analytics_views.sql` — repeatable reporting views.
- `grafana/gameplay-analytics-dashboard.json` — the dashboard.
- `grafana/provisioning/datasources/mariadb.yaml.example` — datasource provisioning example without credentials.
- `grafana/provisioning/dashboards/gameplay-analytics.yaml.example` — dashboard provisioning example.

## Prerequisites

1. Apply `schema/gameplay_analytics.sql` and its migrations.
2. Apply `schema/gameplay_analytics_retention.sql`.
3. Run `tools/analytics/maintain_gameplay_analytics.sh` at least once.
4. Apply the reporting views:

   ```bash
   mariadb -u canary -p canary < schema/gameplay_analytics_views.sql
   ```

Every view uses `CREATE OR REPLACE VIEW`, so the step is repeatable.

## Views and what backs each panel

| View | Reads | Used for |
|---|---|---|
| `analytics_daily_vocation_metrics` | `analytics_daily_balance` | EXP/h, DPS, damage taken/s, healing/s, deaths, profit, supplies, shared EXP and session counts |
| `analytics_daily_party_mode_metrics` | `analytics_daily_party_balance` | Solo versus party without combining modes into one daily row |
| `analytics_dead_letter_health` | `analytics_dead_letters` | Persisted terminal failure count and oldest/newest failure |
| `analytics_session_drilldown` | `analytics_sessions` | Short-range ad-hoc drill-down |
| `analytics_spell_efficiency_drilldown` | spell details plus sessions | Short-range spell efficiency |

The first two views read daily aggregates and are suitable for long ranges. Raw-session views must stay bounded to hours or a few days.

## Daily aggregates versus drill-down

`analytics_daily_balance` is written once per day per vocation, configured level bracket, hunt area and server version. `analytics_daily_party_balance` adds the `solo`/`party` dimension. Maintenance rebuilds a rolling correction window so delayed sessions and corrected raw dimensions replace stale rows.

The shipped dashboard:

- uses daily views for every long-range chart;
- uses the spell drill-down only in a panel explicitly labelled as short-range;
- never queries raw sessions for a long-range trend.

Keep the same split in custom panels.

## Series identity

Every long-range time-series metric label includes all dimensions that can produce more than one row at the same timestamp:

```text
vocation_id
level_bracket
hunt_area
server_version
```

The solo/party panel additionally includes `mode`. Its query applies the same `vocation_id`, `hunt_area`, `server_version` and minimum-sample filters as the other long-range panels.

Omitting one of these dimensions can make distinct rows share the same Grafana series name and timestamp. Depending on panel processing, that produces duplicate points, visually merged lines or misleading comparisons. The dashboard validator rejects ambiguous labels and missing hunt/server filters.

## Solo versus party semantics

Maintenance classifies each raw session before grouping it into `analytics_daily_party_balance`. A time-weighted average party size at or below `1` is `solo`; a value above `1` is `party`.

A single session that changes mode receives one dominant classification because the privacy-conscious raw schema does not retain segment-level EXP, damage and loot.

## Shared-experience percentage

Maintenance clamps each session's shared-experience seconds to combat seconds before summing. The reporting view caps the final percentage at `100`, protecting reports from malformed or historical values.

## Minimum sample size

The dashboard exposes a `Minimum sample size` variable with default `20`. Trend panels apply `sessions >= $min_sessions`. The session-count warning table intentionally remains unfiltered so low-volume groups stay visible.

## No per-player variables

Template variables are limited to vocation, hunt area, server version and sample threshold. There is no default player or character selector. Per-player investigation should be a separate, explicitly access-controlled tool.

## Queue, retry, dead-letter and flush health

Queue depth, retry-in-progress count and flush duration are process-local counters and reset on restart. They are available through `/analytics status`, not MariaDB.

Rows in `analytics_dead_letters` are **terminal failure records** created after a session exhausts its bounded in-memory retry policy. They are retained for investigation and are not an active database replay queue. The view exposes `dead_letter_records`; `pending_dead_letters` remains only as a compatibility alias for older external consumers. The shipped dashboard queries `dead_letter_records` and labels the panel “Persisted dead-letter sessions”.

`/analytics deadletters` retries persistence of entries still in the current process-local dead-letter queue. It does not automatically replay rows already stored in MariaDB.

## Profit and market value

`npc_profit_per_hour` and `supply_cost_per_hour` use verified NPC values. `market_loot_per_hour` exists in the view, but the dashboard does not chart it because no trustworthy Lua-accessible market price provider currently exists.

## Import

1. In Grafana, open **Dashboards → New → Import**.
2. Upload `grafana/gameplay-analytics-dashboard.json`.
3. Select a MySQL-type datasource pointing at Canary's MariaDB database.
4. Import and verify the available filter values.

## Provisioning

1. Copy `grafana/provisioning/datasources/mariadb.yaml.example` into the Grafana provisioning directory.
2. Fill connection data and provide the password through the deployment secret mechanism; never commit it.
3. Copy the dashboard JSON into the path referenced by the dashboard provisioning example.
4. Restart Grafana or wait for the configured reload interval.

## Upgrade

1. Re-apply `schema/gameplay_analytics_retention.sql`.
2. Run maintenance with `DELETE_RAW_SESSIONS=false` to build/rebuild daily rows.
3. Re-apply `schema/gameplay_analytics_views.sql`.
4. Replace or re-import the dashboard JSON because the corrected query labels, filters and dead-letter panel are stored in that file.
5. Compare local Grafana edits before replacing a provisioned dashboard.

## Empty datasets

Every ratio uses `NULLIF(..., 0)`. Zero denominators return `NULL`; empty tables return zero rows. Panels show “No data” or blank ratio cells rather than failing.

## Indexes and query cost

- vocation/date filters can use `analytics_daily_balance_vocation_date`;
- party vocation/date filters can use `analytics_daily_party_vocation_date`;
- mode/date filters can use `analytics_daily_party_mode_date`;
- raw drill-down filters use `analytics_sessions_started_id`;
- spell joins use existing primary keys.

`tools/analytics/test_gameplay_analytics_dashboard_views.sh` verifies the views against MariaDB, including empty data, corrected ratios, separate party modes, terminal dead-letter counts and representative index use.
