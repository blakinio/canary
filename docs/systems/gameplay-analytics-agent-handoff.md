# Gameplay Analytics — final agent handoff

Last verified: **2026-07-12**  
Repository: `blakinio/canary`  
Primary branch: `main`

This document is the source of truth for any agent continuing Gameplay
Analytics work. It replaces the earlier work-in-progress handoff with the
post-audit state of the module.

## 1. Current status

### Repository implementation

The required repository-side implementation is complete on `main`. Final
hardening was merged in PR #122 as commit
`97954d5d468190aeb46f223e87309396e2bfc3fa` after all dedicated Analytics,
hunt-area, Lua, Fast Checks, autofix and Linux CI completed successfully.

Implemented and tested:

- opt-in runtime collection;
- session lifecycle handling;
- damage, healing, mana, experience, kill and death aggregation;
- bounded in-memory queues;
- idempotent MariaDB persistence;
- bounded multi-row batching;
- retries with exponential backoff;
- dead-letter persistence and health counters;
- schema migrations and runtime schema guard;
- hunt-area fallback grid and dynamic party context;
- representative spell telemetry;
- representative supply and loot telemetry;
- recursive loot collection from nested corpse containers;
- daily long-range aggregates;
- correct separate solo/party daily aggregates;
- shared-experience values capped to combat time;
- bounded rolling reaggregation for late and corrected sessions;
- optional bounded raw-session retention;
- production installer and systemd scheduler examples;
- Grafana SQL views, dashboard and provisioning examples;
- named hunt-area generation and validation tooling;
- strict rejection of unfinished deployment and hunt-area placeholders;
- focused Lua, Python, shell and MariaDB integration tests.

There are no known unresolved correctness defects from the 2026-07-12 audit.
Do not reopen superseded branches merely because they still exist in GitHub.
Always inspect the current `main` branch.

### Production deployment

A repository merge does not prove that a live server has been configured.
Production rollout remains an operator task because it requires credentials,
host access, a database backup and in-game verification.

Until those steps are performed, do not claim that Analytics is active on the
production server.

## 2. Product goal

Gameplay Analytics collects low-overhead aggregate data for vocation, hunt,
spell, supply and loot balancing without recording exact player movement
trails and without issuing one SQL write per gameplay event.

The intended flow is:

```text
Canary runtime hooks
        |
        v
bounded in-memory session aggregates
        |
        v
bounded, retry-safe MariaDB persistence
        |
        +--> recent raw session/detail tables
        |
        v
external daily maintenance
        |
        +--> long-range daily balance aggregates
        +--> separate solo/party aggregates
        +--> optional bounded raw deletion
        |
        v
Grafana / SQL reporting
```

The module must remain optional. Analytics or database failures must never
prevent Canary from starting or normal gameplay from continuing.

## 3. Non-negotiable safety rules

- Keep `enabled = false` by default.
- Keep `trackSupplies = false` and `trackLoot = false` by default.
- Keep `DELETE_RAW_SESSIONS=false` by default.
- Never commit database credentials.
- Never invent item prices or hunt coordinates.
- Never persist exact coordinate trails.
- Never add one SQL statement per hit, spell, potion or loot item.
- Never remove queue, SQL-batch, retry or maintenance bounds.
- Never bypass failing tests or weaken validators to obtain green CI.
- Never edit an already-applied migration; add the next migration instead.
- Never enable Analytics automatically from an installer.

## 4. Runtime architecture

Load order:

```text
data-otservbr-global/scripts/lib/gameplay_analytics.lua
    -> gameplay_analytics_context.lua
    -> gameplay_analytics_schema.lua
    -> gameplay_analytics_batching.lua
    -> gameplay_analytics_reliability.lua
```

Registration:

```text
data-otservbr-global/scripts/systems/gameplay_analytics.lua
```

Configuration:

```text
data-otservbr-global/scripts/config/gameplay_analytics.lua
```

Shared spell, rune, action and callback scripts must resolve the live
`GameplayAnalytics` global at event time. They must not `dofile` the core
library again. Re-executing the core can replace wrapped functions while
installation flags remain set, silently removing context, batching or
reliability layers.

## 5. Database and operations files

Core schema and migrations:

```text
schema/gameplay_analytics.sql
schema/gameplay_analytics_migrations/
```

Retention and reporting:

```text
schema/gameplay_analytics_retention.sql
schema/gameplay_analytics_views.sql
```

Operational scripts:

```text
tools/analytics/install_gameplay_analytics.sh
tools/analytics/migrate_gameplay_analytics.sh
tools/analytics/maintain_gameplay_analytics.sh
tools/analytics/systemd/
```

Reporting:

```text
grafana/gameplay-analytics-dashboard.json
grafana/provisioning/
docs/systems/gameplay-analytics-dashboards.md
```

## 6. Correctness decisions

### Solo versus party

Raw sessions are classified before grouping into
`analytics_daily_party_balance`.

Current rule:

```text
party_size_avg <= 1  -> solo
party_size_avg > 1   -> party
```

A session that changes mode during the same hunt is assigned one dominant mode
from its time-weighted average. Exact segment-level splitting would require a
new privacy and schema design because EXP, damage and loot are not retained per
party-state segment.

### Shared experience

At runtime and during maintenance:

```text
shared_experience_seconds <= combat_seconds
shared_experience_ratio <= 1.0
```

The reporting view also caps the percentage defensively at 100%.

### Rolling daily rebuild

`REAGGREGATE_DAYS=7` rebuilds a bounded recent window on every maintenance run.
Each day is replaced transactionally in both daily aggregate tables. This
captures delayed flushes and corrected dimensions and removes stale groups.

When raw deletion is enabled:

```text
RAW_RETENTION_DAYS > REAGGREGATE_DAYS + AGGREGATION_LAG_DAYS
```

### Hunt areas

The shipped named catalogue remains empty because no authoritative rectangle
source exists in the repository. Fallback grid areas remain enabled.

The exact placeholder name `REPLACE_WITH_REAL_HUNT_NAME` and the example-only
`_comment` marker are rejected. Real coordinates must be verified in-game or
in the map editor before they are committed.

### Prices and market values

Only documented NPC prices may be recorded. Missing prices remain zero under
the documented contract. Market value remains zero until a trustworthy source
is implemented.

## 7. Final hardening completed

PR #122 added these protections:

1. `install_gameplay_analytics.sh` rejects empty, whitespace-only and
   `CHANGE_ME` database passwords before SQL access.
2. The installer rejects empty, whitespace-only and `CHANGE_ME`
   `CANARY_SERVER_VERSION` values before SQL access.
3. A shell regression test proves invalid values cannot invoke MariaDB and
   valid values pass the guard stage.
4. Hunt-area parsing rejects the shipped placeholder name in both candidate
   JSON and the Lua catalogue.
5. Candidate JSON containing the example-only `_comment` marker is rejected.
6. CI expects the example template to fail and separately verifies successful
   generation from a valid synthetic fixture.

## 8. Production rollout checklist

Perform these steps on the actual server, not in an unrelated code PR.

1. Back up MariaDB.
2. Copy `tools/analytics/gameplay-analytics.env.example` to a protected host
   path such as `/etc/canary/gameplay-analytics.env`.
3. Set a real `DB_PASSWORD` and stable `CANARY_SERVER_VERSION`.
4. Run:

   ```bash
   set -a
   source /etc/canary/gameplay-analytics.env
   set +a
   bash tools/analytics/install_gameplay_analytics.sh
   ```

5. Apply `schema/gameplay_analytics_retention.sql` and
   `schema/gameplay_analytics_views.sql` if they are not already present.
6. Start Canary with Analytics still disabled.
7. Run `/analytics schema`; require `ready=true`, current and required schema
   versions equal, and no error.
8. Run `/analytics status`; require `schemaReady=true` and no schema error.
9. Enable Analytics deliberately and restart Canary.
10. Confirm startup logs and `/analytics status` show a running collector.
11. Install the systemd maintenance service, timer and protected environment
    file.
12. Keep `DELETE_RAW_SESSIONS=false` for the first several days.
13. Compare raw sessions with both daily aggregate tables.
14. Import/provision the Grafana dashboard and verify panels against real data.
15. Enable raw deletion only after aggregate validation and backup review.

## 9. Required verification commands

Repository checks:

```bash
python tools/analytics/validate_gameplay_analytics.py
python tools/analytics/validate_gameplay_analytics_context.py
python tools/analytics/validate_gameplay_analytics_batching.py
python tools/analytics/validate_gameplay_analytics_reliability.py
python tools/analytics/validate_gameplay_analytics_migrations.py
python tools/analytics/validate_gameplay_analytics_deployment.py
python tools/analytics/validate_gameplay_analytics_hunt_areas.py
python -m unittest discover -s tools/analytics -p "test_*.py" -v
bash tools/analytics/test_install_gameplay_analytics_guards.sh
```

The dedicated GitHub workflows also run Lua tests and real MariaDB integration
tests. Required repository CI must remain green before merge.

## 10. Implementation history

Major merged PRs:

| PR | Contribution |
|---:|---|
| #30 | Initial opt-in subsystem and MariaDB schema. |
| #52 | Persistence API shadowing fix. |
| #54 | Session lifecycle and metric accuracy hardening. |
| #55 | Idempotent retry-safe persistence. |
| #58 | Bounded retry, backoff and dead-letter handling. |
| #61 | Real MariaDB persistence tests. |
| #62 | Multi-row bounded batching. |
| #63 | Migrations and runtime schema guard. |
| #65 | Daily aggregate and retention framework. |
| #67 | Hunt-area and dynamic party context. |
| #72 | Production deployment package. |
| #73 | systemd maintenance scheduler. |
| #76 | Representative spell telemetry. |
| #79 | Representative supply and loot telemetry. |
| #83 | Grafana reporting package. |
| #105 | Named hunt-area tooling. |
| #108 | Runtime load-order hardening and recursive loot. |
| #109 | First comprehensive agent handoff. |
| #114 | Correct solo/party aggregates, shared EXP and rolling rebuilds. |
| #115 | Remaining implementation execution brief. |
| #122 | Final deployment and hunt-area hardening; implementation plan closed. |

Closed/superseded PRs and their branches are historical references only. Do not
merge them or rebuild current work on top of them.

## 11. Optional future expansion

These are product enhancements, not blockers for the completed base module:

- expand spell coverage beyond the representative integrations;
- add accurate AoE target counts after an engine-supported signal exists;
- add critical-hit attribution after an engine-supported signal exists;
- add ammunition tracking after the consumed item ID is reliably exposed;
- expand the verified NPC price catalogue;
- integrate market prices only from a trustworthy documented source;
- add real named hunt rectangles after operator verification;
- persist additional pipeline health history if Grafana time-series monitoring
  is required beyond `/analytics status`.

Each enhancement requires its own focused PR, tests and explicit data
semantics.

## 12. Quick start for the next agent

1. Read this file and the focused subsystem document relevant to the task.
2. Fetch the latest `main` and inspect recent merged PRs.
3. Treat repository implementation as complete unless a reproducible defect is
   demonstrated.
4. Do not resurrect old Analytics branches.
5. For production work, ask for or use actual host access; repository access
   alone cannot verify deployment.
6. Preserve all conservative defaults and failure isolation.
7. Record any new verified production state in this document with a date,
   commands executed and observable results.
