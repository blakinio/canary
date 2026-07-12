# Gameplay Analytics — complete project handoff and PR audit

Last verified: **2026-07-12**  
Repository: `blakinio/canary`  
Primary branch: `main`  
Module status: **repository implementation complete; live production rollout not yet verified**

This document is the authoritative handoff for every agent or operator who
continues work on Gameplay Analytics. Read it before opening a new branch.
It explains why the module exists, what was implemented, how the pieces fit
together, which decisions are intentional, what every relevant pull request
delivered, which historical PRs were superseded, what remains an operator task,
and which future additions are optional rather than unfinished work.

---

## 1. Executive summary

Gameplay Analytics is an opt-in, low-overhead telemetry and reporting subsystem
for balancing vocations, hunts, spells, supplies and loot in Canary.

Its purpose is to replace balance decisions based only on anecdotes with
repeatable data such as:

- experience per hour by vocation, level bracket, hunt and server build;
- outgoing damage, incoming damage and effective healing;
- deaths per sample group;
- solo versus party performance;
- shared-experience participation;
- spell-level damage/healing/mana efficiency for integrated casts;
- supply costs, loot values and NPC profit where trustworthy prices exist;
- pipeline reliability, queue, retry and dead-letter health.

The repository-side implementation is complete on `main`. The final functional
hardening was merged in PR #122 and the previous final status update was merged
in PR #123. A full audit of Analytics-related PRs found no open functional
Analytics PR and no known unresolved correctness defect from the 2026-07-12
audit.

A repository merge is not proof of a live deployment. The following still
requires access to the real host, MariaDB credentials, a backup, the Canary
process configuration, Grafana and a GM account:

- apply/verify production schema and migrations;
- export a stable `CANARY_SERVER_VERSION`;
- enable Analytics deliberately;
- install the maintenance timer;
- observe real data and compare raw versus daily aggregates;
- provision Grafana;
- enable raw deletion only after validation.

Do not claim that Analytics is active in production until those steps have
observable evidence.

---

## 2. Why we built this

### 2.1 Problem being solved

Without structured telemetry, balancing an OTS commonly depends on isolated
hunt screenshots, subjective player reports and short test sessions. Those are
useful signals, but they do not reliably answer questions such as:

- Is one vocation consistently outperforming another at the same level range?
- Did a balance update improve one hunt while accidentally breaking another?
- Is a party composition stronger because of higher damage, lower deaths,
  better shared experience or lower supply consumption?
- Which spell is efficient in practice rather than only on paper?
- Does a change affect new characters and endgame characters differently?
- Are apparently profitable hunts still profitable after verified supply costs?

### 2.2 Expected value

The module is intended to provide:

1. **Evidence-based balancing** — compare real aggregates instead of guessing.
2. **Before/after comparisons** — group data by `server_version` or balance
   build identifier.
3. **Hunt-specific analysis** — distinguish map areas rather than mixing all
   sessions together.
4. **Safer changes** — monitor deaths, damage taken and healing, not only EXP/h.
5. **Operational visibility** — know when persistence is retrying, dropping or
   dead-lettering data.
6. **Privacy-conscious aggregation** — collect useful balance context without
   retaining exact movement trails or party-member identity histories.
7. **Bounded server impact** — no SQL write for each hit, cast or item event.

### 2.3 What this module is not

Gameplay Analytics is not:

- an anti-cheat system;
- a complete player-surveillance system;
- a replacement for gameplay logs or crash diagnostics;
- a real-time exact path recorder;
- a market-price oracle;
- an automatic balance-changing agent;
- proof that a balance change is correct without human interpretation;
- production-enabled by default.

---

## 3. Current status

### 3.1 Repository implementation

The required implementation is complete on `main`.

Implemented and tested:

- opt-in runtime collection;
- lazy hunt-session lifecycle;
- raw/final experience collection;
- outgoing and incoming damage;
- primary and secondary combat-type separation;
- effective healing and overhealing;
- mana usage;
- monster kills, deaths and combat duration;
- per-monster, spell, damage-type, supply and loot detail aggregates;
- PvP and player-owned-summon exclusions;
- account-type exclusions;
- bounded in-memory queues;
- idempotent MariaDB upserts;
- bounded multi-row detail batching;
- bounded retries with exponential backoff;
- persisted dead letters and operational counters;
- migration checksums and runtime schema guard;
- coarse named/fallback hunt context;
- dynamic party size, composition and shared-experience context;
- representative spell integrations;
- representative supply and loot integrations;
- recursive corpse loot collection from nested containers;
- daily long-range balance aggregates;
- separate solo/party daily aggregates;
- shared-experience clamping to combat time;
- rolling reaggregation for late or corrected sessions;
- optional bounded raw retention;
- deployment installer and environment examples;
- systemd maintenance service/timer examples;
- SQL reporting views, Grafana dashboard and provisioning examples;
- named hunt-area generation and validation tooling;
- strict rejection of unfinished placeholders;
- Lua, Python, shell and real MariaDB test coverage.

### 3.2 PR audit result

At the time of this audit:

- all previous Gameplay Analytics PRs were closed;
- every accepted implementation PR was merged;
- superseded Analytics PRs were closed without merge and explicitly replaced;
- there was no open functional Analytics PR;
- no historical Analytics branch should be used as a base for new work;
- `main` is the only valid source of truth.

This documentation update is intentionally a documentation-only PR. After it
merges, there should again be no open Analytics PR unless a new verified task is
started.

### 3.3 Production status

Production status is **unknown/not verified from repository access**.

The repository still intentionally ships conservative defaults. Until an
operator performs and records the rollout, do not assume:

- the schema exists in the live database;
- migrations have been applied;
- the collector is enabled;
- the maintenance timer is installed;
- Grafana is provisioned;
- live data quality has been checked;
- raw deletion is enabled or should be enabled.

---

## 4. System architecture

### 4.1 End-to-end data flow

```text
Canary gameplay/runtime hooks
        |
        v
per-player in-memory hunt session
        |
        | aggregate events in Lua
        | no SQL per hit/cast/item
        v
bounded completed-session queue
        |
        v
schema guard + bounded batched persistence
        |
        +--> success: analytics_sessions + detail tables
        |
        +--> failure: retry with backoff
                         |
                         +--> exhausted: analytics_dead_letters
        |
        v
external maintenance job
        |
        +--> analytics_daily_balance
        +--> analytics_daily_party_balance
        +--> rolling correction window
        +--> optional bounded raw deletion
        |
        v
SQL views + Grafana dashboard + manual analysis
```

### 4.2 Runtime load order

The wrapper order matters:

```text
data-otservbr-global/scripts/lib/gameplay_analytics.lua
    -> gameplay_analytics_context.lua
    -> gameplay_analytics_schema.lua
    -> gameplay_analytics_batching.lua
    -> gameplay_analytics_reliability.lua
```

Runtime registration lives in:

```text
data-otservbr-global/scripts/systems/gameplay_analytics.lua
```

Configuration lives in:

```text
data-otservbr-global/scripts/config/gameplay_analytics.lua
```

Shared spell, rune, action and callback files must resolve the live
`GameplayAnalytics` global at event time. They must not execute the core again
with `dofile`. Re-executing the core after wrappers are installed can replace
wrapped functions while installation flags remain set, silently removing
context, batching or reliability behavior. PR #108 added validators against
this regression.

### 4.3 Main database files

```text
schema/gameplay_analytics.sql
schema/gameplay_analytics_migrations/
schema/gameplay_analytics_retention.sql
schema/gameplay_analytics_views.sql
```

### 4.4 Main operational files

```text
tools/analytics/install_gameplay_analytics.sh
tools/analytics/migrate_gameplay_analytics.sh
tools/analytics/maintain_gameplay_analytics.sh
tools/analytics/gameplay-analytics.env.example
tools/analytics/systemd/
```

### 4.5 Reporting files

```text
grafana/gameplay-analytics-dashboard.json
grafana/provisioning/
docs/systems/gameplay-analytics-dashboards.md
```

### 4.6 Focused documentation

```text
docs/systems/gameplay-analytics.md
docs/systems/gameplay-analytics-persistence.md
docs/systems/gameplay-analytics-migrations.md
docs/systems/gameplay-analytics-context.md
docs/systems/gameplay-analytics-context-rollout.md
docs/systems/gameplay-analytics-retention.md
docs/systems/gameplay-analytics-deployment.md
docs/systems/gameplay-analytics-spells.md
docs/systems/gameplay-analytics-supply-loot.md
docs/systems/gameplay-analytics-dashboards.md
docs/systems/gameplay-analytics-hunt-areas.md
```

---

## 5. Data and correctness semantics

### 5.1 Session lifecycle

Sessions are created lazily on the first meaningful metric rather than at login.
This avoids empty rows for players who log in but do not hunt.

Combat duration ends at the last recorded combat event rather than including
the entire inactivity timeout. Completed sessions are queued only when
persistence is enabled; otherwise they are discarded instead of building an
undrainable queue.

### 5.2 Experience

Both raw and final experience are retained where available. Per-monster raw
experience is attributed using the retained source. Balance reports should
state which measure they use.

### 5.3 Damage and healing

- outgoing and incoming damage are separated;
- primary and secondary combat types are recorded independently;
- player-versus-player events and player-owned summons follow the configured
  exclusion policy;
- healing distinguishes effective healing from overhealing;
- spell detail aggregates do not add damage/healing/mana to the session totals
  again.

### 5.4 Spell telemetry

Representative offensive/healing spells and runes are integrated through a
helper that snapshots session totals before and after the existing cast. The
spell row receives only the cast delta.

Current intentional limitations:

- only representative casts are wired;
- accurate AoE target counts need an engine-supported signal;
- critical-hit attribution is not guessed and remains unavailable from the
  current Lua surface;
- rune mana cost is zero where use consumes no mana.

### 5.5 Supply and loot telemetry

- potions and representative runes record one supply event per successful
  consumption;
- corpse loot is attributed once to the corpse owner, not multiplied across
  party members;
- nested bags/backpacks are scanned recursively with `getItems(true)`;
- prices come only from documented NPC sources;
- missing values remain zero according to the documented contract;
- market value remains zero until a trustworthy source exists;
- ammunition is deferred until the exact consumed item ID is reliably exposed.

### 5.6 Hunt areas

The shipped named catalogue remains empty because the repository contains no
authoritative list of hunt rectangles. Fallback grid grouping remains enabled,
so data is still grouped geographically without invented names.

The tooling rejects:

- malformed or inverted coordinates;
- out-of-range coordinates;
- case-insensitive duplicate names;
- overlapping rectangles;
- `REPLACE_WITH_REAL_HUNT_NAME`;
- candidate entries that retain the example-only `_comment` marker.

Real named rectangles must be confirmed in-game or in the map editor.

### 5.7 Party classification

Raw sessions are classified before aggregation into
`analytics_daily_party_balance`:

```text
party_size_avg <= 1  -> solo
party_size_avg > 1   -> party
```

A session that switches between solo and party is assigned one dominant mode
from its time-weighted average. Exact within-session splitting would require a
new segment-level schema and privacy review because EXP, damage and loot are not
currently retained per party-state segment.

### 5.8 Shared experience

The invariant is enforced at runtime, during maintenance and defensively in the
reporting view:

```text
shared_experience_seconds <= combat_seconds
shared_experience_ratio <= 1.0
reported percentage <= 100%
```

### 5.9 Daily aggregates and corrections

`REAGGREGATE_DAYS=7` rebuilds a bounded recent window on every maintenance run.
Each completed day is replaced transactionally in both daily aggregate tables.
This captures delayed flushes and corrected raw dimensions and removes stale
groups.

If raw deletion is enabled, the required relation is:

```text
RAW_RETENTION_DAYS > REAGGREGATE_DAYS + AGGREGATION_LAG_DAYS
```

### 5.10 Idempotency

Persistence retries must be safe after a partial write:

- the session row is upserted by `session_uuid`;
- every detail category is upserted by its stable key;
- detail failures propagate to the session flush result;
- the complete session is requeued within configured bounds;
- dead letters are persisted idempotently after retries are exhausted.

---

## 6. Safety and performance invariants

These rules are non-negotiable unless a new design explicitly replaces them
with stronger guarantees:

- `enabled = false` remains the shipped default;
- `trackSupplies = false` remains the shipped default;
- `trackLoot = false` remains the shipped default;
- `DELETE_RAW_SESSIONS=false` remains the shipped default;
- the installer never enables Analytics;
- database/schema failures never prevent normal Canary startup;
- gameplay events never perform one SQL write per hit, cast, potion or loot item;
- queues, SQL batches, retries, dead letters, catch-up days and delete batches
  remain bounded;
- credentials are never committed;
- prices and hunt coordinates are never invented;
- exact movement trails are never persisted;
- party-member identity histories are not introduced casually;
- applied migrations are immutable; add the next numbered migration;
- validators and tests are not weakened to make CI green;
- a failed optional subsystem must fail isolated from normal gameplay.

---

## 7. Configuration defaults and operational controls

The exact current configuration should always be read from:

```text
data-otservbr-global/scripts/config/gameplay_analytics.lua
```

Important conservative controls include:

- global `enabled` switch;
- database persistence switch;
- spell/supply/loot tracking switches;
- excluded account types and PvP behavior;
- queue sizes and flush interval;
- detail batch size;
- retry/backoff limits;
- dead-letter capacity;
- context sampling interval and gap cap;
- fallback grid size;
- named hunt-area table;
- server/balance version from `CANARY_SERVER_VERSION`.

Runtime GM commands include status, schema readiness, enable/disable, forced
flush and dead-letter inspection/handling according to the focused docs.

---

## 8. Deployment and rollback playbook

Perform these steps only on the real server with a current backup.

### 8.1 Prepare

1. Fetch the exact intended `main` revision.
2. Back up MariaDB and record the backup identifier.
3. Keep Analytics disabled.
4. Copy the example environment file to a protected host path:

   ```bash
   cp tools/analytics/gameplay-analytics.env.example \
      /etc/canary/gameplay-analytics.env
   chmod 600 /etc/canary/gameplay-analytics.env
   ```

5. Set real values for `DB_PASSWORD` and a stable
   `CANARY_SERVER_VERSION`, for example a release or balance identifier.

The installer rejects empty, whitespace-only and `CHANGE_ME` values before any
SQL access.

### 8.2 Install and migrate

```bash
set -a
source /etc/canary/gameplay-analytics.env
set +a
bash tools/analytics/install_gameplay_analytics.sh
```

Apply the optional retention and reporting schemas if not already installed:

```bash
mariadb ... < schema/gameplay_analytics_retention.sql
mariadb ... < schema/gameplay_analytics_views.sql
```

### 8.3 Verify while disabled

1. Start/restart Canary with the environment exported to the process.
2. Run `/analytics schema` as GM.
3. Require `ready=true`, matching current/required schema version and no error.
4. Run `/analytics status`.
5. Require `schemaReady=true`, no schema error and clean startup queue state.

Do not enable the collector if either command fails.

### 8.4 Enable deliberately

Set the intended configuration flags, restart Canary and verify:

- startup contains the Analytics enabled message;
- `/analytics status` reports enabled/running;
- queue depth remains controlled;
- successful sessions reach MariaDB;
- retry and dead-letter counts remain healthy.

### 8.5 Install maintenance

Use the unit/environment examples in:

```text
tools/analytics/systemd/
```

Install and enable the timer, not the oneshot service directly. Keep:

```text
DELETE_RAW_SESSIONS=false
```

for the first several days.

### 8.6 Validate real data

Compare for the same complete days:

- raw session counts and totals;
- `analytics_daily_balance`;
- `analytics_daily_party_balance`;
- solo/party separation;
- shared-experience percentage range;
- server-version and hunt-area dimensions;
- supply/loot values where tracking is enabled;
- dead-letter and retry health.

### 8.7 Grafana

Provision the MariaDB datasource without committing credentials, apply the SQL
views and import/provision:

```text
grafana/gameplay-analytics-dashboard.json
```

Verify every panel against direct SQL before trusting it for balance decisions.

### 8.8 Raw retention

Enable raw deletion only after:

- multiple successful maintenance runs;
- raw/daily reconciliation;
- backup review;
- confirmation that the rebuild window cannot overlap deleted data;
- documented operator approval.

### 8.9 Rollback

Before enabling, rollback normally means fixing the database/environment and
rerunning the idempotent installer while collection stays disabled.

After enabling:

- immediate: `/analytics disable`;
- persistent: set `enabled = false` and restart;
- database: restore the pre-install backup if schema rollback is required;
- do not edit an applied migration to simulate rollback.

---

## 9. Reporting interpretation

### 9.1 Long-range versus drill-down

Long ranges must use daily aggregate views. Raw session and spell tables are for
short-range drill-down only.

### 9.2 Sample size

A mathematically valid ratio is not automatically statistically useful. Reports
must show session counts and use a meaningful minimum-sample threshold before
comparing groups.

### 9.3 Server version

`CANARY_SERVER_VERSION` is a balance-analysis dimension, not decoration. Change
it deliberately when deploying a balance release so before/after comparisons
are possible.

### 9.4 Hunt fallback grids

A fallback cell is a coarse area, not a named hunting ground. Do not present a
grid key as a verified hunt name.

### 9.5 Profit

NPC profit is meaningful only for items with documented values. Zero can mean
"no trustworthy value available", not necessarily "worthless". Market profit
must not be fabricated while market values remain unavailable.

---

## 10. Test and CI surface

### 10.1 Local/static commands

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
bash -n tools/analytics/install_gameplay_analytics.sh
bash -n tools/analytics/maintain_gameplay_analytics.sh
```

Focused Lua tests under `tools/analytics/` cover context, batching, schema,
reliability, spell integration and supply/loot behavior.

### 10.2 Dedicated workflows

Analytics work may trigger dedicated workflows for:

- core Gameplay Analytics;
- retention;
- spell telemetry;
- supply/loot telemetry;
- dashboards;
- hunt-area tooling;
- general repository CI/autofix.

Real MariaDB 11.4 service tests validate schemas, migrations, idempotent upserts,
foreign keys, cascades, retention, daily aggregates and reporting views.

### 10.3 Merge rule

A PR is not complete because code was pushed. It is complete only when:

- its scope is focused and reviewed;
- dedicated Analytics checks pass;
- general Fast Checks and Lua tests pass;
- required Linux/build checks pass when emitted;
- no unresolved review thread remains;
- the PR is merged or explicitly closed as superseded;
- the resulting files are verified on `main`.

---

## 11. Complete Analytics PR audit

### 11.1 Merged implementation and documentation PRs

All PRs in this table are closed and merged.

| PR | Area | What it contributed |
|---:|---|---|
| #30 | Foundation | Initial opt-in collector, session aggregates, schema, runtime command and static validation. |
| #46 | Validation | Required monster health registration inside a spawn callback. |
| #47 | Validation | Structured Lua callback validation and focused tests. |
| #48 | Validation/runtime support | Improved spawn-registration parser and tests; also contained a separate account-quest permission change. |
| #49 | Runtime registration | Named Analytics spawn callback; also contained account-quest robustness/formatting work. |
| #52 | Persistence correctness | Removed `result` API shadowing and added a regression validator. |
| #54 | Metric correctness | Lazy sessions, accurate combat time, PvP/summon filtering, damage types, raw EXP source, online enable and account exclusions. |
| #55 | Retry correctness | Idempotent session/detail upserts, failure propagation and complete-session requeue. |
| #58 | Reliability | Bounded retry/backoff, dead letters, counters and runtime health commands. |
| #61 | Database verification | Real MariaDB integration tests for schema, upserts and cascades. |
| #62 | Performance | Bounded multi-row detail batching and batch counters. |
| #63 | Deployment safety | Versioned migrations, checksums, runtime schema guard and `/analytics schema`. |
| #65 | Retention foundation | Daily aggregates, checkpoints and opt-in bounded raw deletion. |
| #67 | Context | Clean hunt-area, party, shared EXP, composition and server-version implementation. |
| #72 | Deployment package | Environment example, repeatable installer, rollback/verification docs. |
| #73 | Scheduler | systemd service/timer/environment examples and validation. |
| #76 | Spells | Representative offensive/healing spell and rune telemetry without double counting. |
| #79 | Supply/loot | Representative potions/runes, corpse loot, verified NPC price table and tests. |
| #83 | Reporting | SQL views, Grafana dashboard, provisioning examples and MariaDB view tests. |
| #105 | Hunt tooling | Candidate parser/generator, overlap/duplicate checks and operator process. |
| #108 | Runtime integration hardening | Live-global resolution and recursive nested loot collection. |
| #109 | Handoff | First comprehensive Analytics agent handoff. |
| #114 | Aggregate correctness | Separate solo/party table, shared EXP cap and rolling correction window. |
| #115 | Execution plan | Six-phase remaining-work plan, later marked complete. |
| #122 | Final hardening | Strict installer guards, placeholder rejection, focused regression tests and final implementation closeout. |
| #123 | Final status | Recorded repository completion after #122 merged. |

### 11.2 Closed, intentionally unmerged Analytics PRs

These PRs are closed historical references and must not be reopened or merged.

| PR | Status | Replacement/current resolution |
|---:|---|---|
| #34 | Closed, unmerged | Mixed/stale runtime-hook branch; superseded by later clean/runtime work. |
| #38 | Closed, unmerged | Clean runtime-hook attempt that was not merged; current runtime behavior is delivered by later merged PRs and validated on `main`. |
| #50 | Closed, unmerged | Duplicate persistence override; explicitly replaced by direct-library fix #52. |
| #64 | Closed, unmerged | Conflicted hunt/party context branch; replaced by clean merged PR #67. |

### 11.3 Supporting repository work

The following changes were not primary Analytics features but materially helped
the Analytics program:

- #44 formatted unrelated Lua files so formatter noise would not contaminate
  Analytics branches;
- #51 changed AI CI repair to read-only/manual patch output, preventing automatic
  unrelated writes to failed PR branches;
- the branch-protection required checks were aligned with checks that are
  actually emitted for conditional workflows.

### 11.4 Audit conclusion

Before this documentation-only audit PR was opened:

- open functional Analytics PRs: **0**;
- merged accepted Analytics PRs: **all listed in 11.1**;
- closed superseded Analytics PRs: **#34, #38, #50, #64**;
- known untracked functional branch requiring merge: **none**;
- known unresolved audit defect: **none**.

Old branches may still exist on GitHub after their PR closes. Branch existence
is not unfinished work. Do not build on them.

---

## 12. Changelog by project phase

### Phase A — Initial collector

PR #30 established the opt-in configuration, in-memory session model, MariaDB
schema, basic hooks and operator command. This proved the concept but still
needed substantial production hardening.

### Phase B — Runtime and validator stabilization

PRs #46, #47, #48 and #49 made monster health-event registration explicit and
verifiable. PR #52 fixed a real persistence bug caused by a local query handle
shadowing Canary's global `result` API.

### Phase C — Metric and lifecycle correctness

PR #54 corrected empty sessions, combat duration, disabled-persistence queue
behavior, spell mana double counting, PvP/summon filtering, secondary damage
types, per-monster raw EXP, online-player enable and account exclusions.

### Phase D — Reliable persistence

PR #55 made retries idempotent after partial writes. PR #58 added bounded
backoff and dead-letter handling. PR #61 added real MariaDB verification. PR
#62 replaced per-detail statements with bounded multi-row upserts.

### Phase E — Schema lifecycle and context

PR #63 introduced numbered checksum-protected migrations and a non-fatal schema
guard. PR #67 added hunt, dynamic party, shared EXP, vocation composition and
server-version context after superseding conflicted PR #64.

### Phase F — Retention and operations

PR #65 added daily aggregate maintenance and optional retention. PR #72 created
the production installer package. PR #73 supplied validated systemd units.

### Phase G — Domain detail integrations

PR #76 integrated representative spell telemetry. PR #79 integrated
representative supplies and loot with documented prices. PR #108 later fixed
runtime load-order safety and recursive nested loot scanning.

### Phase H — Reporting and hunt tooling

PR #83 added MariaDB views, Grafana dashboard/provisioning and query tests. PR
#105 added named hunt-area tooling while honestly leaving the production
catalogue empty until coordinates are verified.

### Phase I — Post-rollout correctness audit

PR #114 fixed mixed solo/party aggregation, shared-experience time semantics,
late/corrected session handling and raw-deletion overlap.

### Phase J — Final hardening and handoff

PRs #109 and #115 documented the work and execution plan. PR #122 closed the
last installer and hunt-placeholder gaps and marked the repository plan
complete. PR #123 recorded the completed status on `main`.

---

## 13. Known limitations and optional future expansion

The following are enhancements, not blockers for the completed base module:

- integrate more spells beyond the representative set;
- expose and record accurate AoE target counts;
- expose and record critical-hit attribution;
- expose exact ammunition consumption IDs and integrate ammo costs;
- expand the verified NPC price catalogue;
- add a trustworthy market-value provider with provenance and update policy;
- add real named hunt rectangles after map/in-game verification;
- persist queue/retry/flush time series to Prometheus or another metrics backend;
- add more advanced statistical confidence or cohort comparison tooling;
- add automated production smoke/reconciliation tooling once host access exists.

Every enhancement should be a focused PR with explicit data semantics,
performance bounds, privacy review and tests. Do not relabel optional expansion
as an unfinished defect.

---

## 14. Instructions for the next agent

### 14.1 First actions

1. Read this document.
2. Fetch the latest `main`.
3. Inspect the focused subsystem document for the task.
4. Check open PRs before creating a branch.
5. Treat repository implementation as complete unless a reproducible defect is
   demonstrated.
6. Never resurrect old Analytics branches.

### 14.2 For a production rollout session

Ask for or use actual access to:

- the Canary host and service manager;
- the live MariaDB database and backup process;
- the Canary environment/service configuration;
- a GM account for `/analytics schema` and `/analytics status`;
- Grafana and its datasource configuration.

Record in this file or a dated rollout record:

- deployed commit SHA;
- database backup identifier;
- schema/migration output;
- configured `CANARY_SERVER_VERSION`;
- GM command outputs;
- systemd timer status;
- first successful raw and aggregate counts;
- Grafana validation results;
- whether raw deletion remains disabled;
- any rollback performed.

### 14.3 For a defect

Before coding:

- reproduce it on current `main`;
- identify whether it is runtime, persistence, maintenance, reporting or
  operational configuration;
- check whether the behavior is an intentional documented limitation;
- add the smallest regression test that proves the defect;
- avoid unrelated formatting or project changes.

### 14.4 For an enhancement

Document:

- the balance question it answers;
- the exact data and dimensions required;
- event frequency and worst-case overhead;
- queue/SQL batching implications;
- privacy implications;
- data-source provenance for values such as prices;
- compatibility with existing raw/daily schemas;
- dashboard and retention impact.

---

## 15. Definition of done

### Repository implementation

The base module is complete when all of the following remain true:

- accepted implementation is on `main`;
- no accepted change exists only on a stale branch;
- superseded PRs are closed and clearly identified;
- dedicated and required CI is green;
- safe defaults are unchanged;
- documentation matches runtime/schema behavior;
- no known correctness defect from the completed audit remains.

This condition is currently satisfied.

### Production rollout

Production rollout is complete only after:

- backup exists;
- schema and migrations are verified;
- stable server version is exported;
- GM schema/status checks pass;
- collector is deliberately enabled and running;
- maintenance timer runs successfully;
- raw and daily data reconcile for several days;
- Grafana panels are validated against direct SQL;
- raw deletion is either deliberately kept disabled or enabled only after
  documented validation.

This condition has not been verified from repository access.

---

## 16. New-session starter prompt

```text
Work in https://github.com/blakinio/canary.
Read docs/systems/gameplay-analytics-agent-handoff.md first.
Gameplay Analytics repository implementation is complete; do not rebuild old
branches. Verify current main and open PRs before acting. Continue either with
an evidence-backed defect, an explicitly scoped optional enhancement, or the
operator-only production rollout. Preserve disabled-by-default behavior,
bounded queues/batches/retries/maintenance, idempotent persistence, privacy
constraints and failure isolation. Never claim production deployment without
host/database/GM evidence.
```
