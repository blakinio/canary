# Gameplay Analytics — agent handoff and implementation status

## Purpose

This document is the authoritative handoff for agents continuing work on Gameplay Analytics in:

```text
https://github.com/blakinio/canary
```

Related project repositories:

```text
https://github.com/opentibiabr/otclient
https://github.com/opentibiabr/canary
https://github.com/opentibiabr/remeres-map-editor
https://github.com/opentibiabr/client-editor
```

Always inspect the latest `main` before making assumptions. Earlier PR branches may contain superseded or duplicated code.

---

## Main objective

Build a production-safe Gameplay Analytics platform for Canary that can:

- collect combat, experience, healing, mana, deaths and monster statistics;
- compare vocations, level brackets, hunts, party modes and server versions;
- collect optional spell, supply and loot telemetry;
- persist data without per-hit SQL writes;
- survive MariaDB outages without affecting gameplay;
- expose operational health and dead-letter state;
- retain long-term daily aggregates while safely deleting old raw sessions;
- provide Grafana-ready SQL views and dashboards;
- avoid exact coordinate trails, party-member identity history and high-cardinality monitoring labels.

The Analytics subsystem must never prevent Canary from starting or running.

---

## Current implementation status

### Completed and merged

The following major layers are already implemented on `main`:

1. Core Gameplay Analytics runtime.
2. Automatic collection of:
   - experience;
   - outgoing and incoming damage;
   - healing and overhealing;
   - mana spent;
   - kills and deaths;
   - monster and damage-type aggregates;
   - session and combat duration.
3. Lazy session creation.
4. Bounded in-memory queue.
5. Idempotent session and detail upserts.
6. Batched detail persistence.
7. Retry with exponential backoff.
8. Dead-letter queue and dead-letter persistence.
9. Runtime and queue health counters.
10. MariaDB integration tests.
11. Explicit schema migrations with checksums.
12. Runtime schema guard.
13. Hunt-area and dynamic party context.
14. Optional daily aggregate and retention subsystem.
15. Spell telemetry helper and representative integrations.
16. Supply and loot telemetry for selected items and events.
17. Grafana views and dashboard package.
18. Hunt-area generator, validator and fixtures.
19. Production deployment scripts and documentation.
20. systemd service/timer examples for retention maintenance.

### Important merged PR lineage

Relevant historical PRs include:

```text
#30  initial gameplay analytics
#52  reliability foundation
#54  MariaDB integration
#55  idempotent persistence
#58  observability and dead letters
#61  retry reliability
#62  detail batching
#63  schema migrations and runtime guard
#65  optional daily retention
#67  hunt and dynamic party context
```

Later PRs added production deployment assets, spell telemetry, supply/loot telemetry, Grafana and hunt-area tooling. Always verify their current implementation on `main` instead of relying on PR descriptions alone.

---

## Current branch and active audit

Active repair branch:

```text
fix/gameplay-analytics-production-audit
```

The branch was created from the latest `main` to address issues found during a full implementation audit.

### Problems found in the audit

1. Daily solo and party sessions were merged before classification.
2. Shared-experience percentage could use incompatible time bases.
3. Nested loot inside containers was not collected.
4. Retention maintenance did not rebuild recently closed days.
5. Deployment installer accepted empty credentials or server version.
6. Hunt-area example placeholders could be generated as production Lua.

---

## Changes already made on the active audit branch

### 1. Separate solo and party daily aggregates

Updated:

```text
schema/gameplay_analytics_retention.sql
```

Added:

```text
analytics_daily_party_mode
```

This table preserves `solo` and `party` as an explicit dimension before aggregation.

Do not infer solo/party from an average after unlike sessions have already been combined.

### 2. Correct reporting views

Updated:

```text
schema/gameplay_analytics_views.sql
```

Changes:

- `analytics_daily_party_mode_metrics` now reads from `analytics_daily_party_mode`;
- `shared_experience_percent` is bounded against combat time;
- comments document the correct aggregation semantics.

### 3. Rebuild recent closed days

Updated:

```text
tools/analytics/maintain_gameplay_analytics.sh
```

Added:

```text
REAGGREGATE_DAYS=3
```

Behavior:

- while behind, maintenance processes dates sequentially from the checkpoint;
- once caught up, every run rebuilds a recent closed window;
- daily slices are deleted before reinsertion so removed or reclassified groups do not remain stale;
- shared-experience seconds are capped to combat seconds;
- solo and party aggregates are written separately.

### 4. Recursive corpse loot

Updated:

```text
data/scripts/eventcallbacks/monster/postdroploot_gameplay_analytics.lua
```

Changed:

```lua
corpse:getItems(false)
```

to:

```lua
corpse:getItems(true)
```

This includes items inside bags, backpacks and other nested containers.

### 5. Hardened production installer

Updated:

```text
tools/analytics/install_gameplay_analytics.sh
```

The installer now rejects:

- empty `DB_PASSWORD`;
- `DB_PASSWORD=CHANGE_ME`;
- empty `CANARY_SERVER_VERSION`;
- `CANARY_SERVER_VERSION=CHANGE_ME`;
- invalid `DB_PORT`;
- empty `DB_USER` or `DB_NAME`.

It still never enables Analytics automatically and never edits the Lua configuration.

### 6. Stronger deployment validator

Updated:

```text
tools/analytics/validate_gameplay_analytics_deployment.py
```

The validator now enforces all installer input checks listed above.

### 7. Reject hunt-area placeholders

Updated:

```text
tools/analytics/generate_gameplay_analytics_hunt_areas.py
.github/workflows/gameplay-analytics-hunt-areas.yml
```

The generator rejects names such as:

```text
REPLACE_WITH_REAL_HUNT_NAME
replace_with_...
example
placeholder
```

The workflow now expects the shipped example placeholder file to fail generation.

### 8. Retention environment example

Updated:

```text
tools/analytics/systemd/gameplay-analytics-maintenance.env.example
```

Added:

```text
REAGGREGATE_DAYS=3
```

---

## Work still required on the active audit branch

The following tasks are not yet complete and must be finished before merge.

### A. Finish retention validators

Update:

```text
tools/analytics/validate_gameplay_analytics_retention.py
tools/analytics/validate_gameplay_analytics_retention_systemd.py
tools/analytics/test_validate_gameplay_analytics_retention.py
```

Required checks:

- `analytics_daily_party_mode` exists;
- `REAGGREGATE_DAYS` exists and is positive;
- recent-window rebuild logic exists;
- date slices are deleted before reinsertion;
- shared experience uses `LEAST(shared_experience_seconds, combat_seconds)`;
- deletion remains behind the aggregate checkpoint;
- raw deletion remains disabled by default.

### B. Update MariaDB retention integration test

Update:

```text
tools/analytics/test_retention_maintenance.sh
```

Add coverage for:

1. separate solo and party aggregate rows;
2. late-arriving session added after the first maintenance run;
3. recent-window reaggregation picks up the delayed session;
4. no duplicate totals after repeated runs;
5. shared-experience percentage cannot exceed 100%;
6. raw deletion preserves both long-term aggregate tables;
7. nested detail rows still cascade on raw deletion.

### C. Update Grafana integration tests

Inspect and update as needed:

```text
tools/analytics/test_gameplay_analytics_grafana.sh
tools/analytics/validate_gameplay_analytics_grafana.py
tools/analytics/test_validate_gameplay_analytics_grafana.py
grafana/gameplay-analytics-dashboard.json
```

The dashboard must continue to query the stable view:

```text
analytics_daily_party_mode_metrics
```

SQL plans should use the new party-mode table indexes.

### D. Add nested loot runtime test

Inspect:

```text
data/scripts/lib/gameplay_analytics_loot.lua
tools/analytics/test_gameplay_analytics_supply_loot.lua
```

Add a fixture or mock representing a nested container hierarchy and verify each nested item is counted exactly once.

### E. Update hunt-area unit tests

Update:

```text
tools/analytics/test_gameplay_analytics_hunt_areas.py
```

Add tests asserting:

- placeholder candidate names are rejected;
- ordinary verified names still generate correctly;
- duplicate names and overlapping rectangles remain rejected.

### F. Update deployment tests

Update:

```text
tools/analytics/test_validate_gameplay_analytics_deployment.py
```

Add regression cases for:

- empty password;
- placeholder password;
- empty server version;
- placeholder server version;
- invalid database port.

### G. Update documentation

Update:

```text
docs/systems/gameplay-analytics-retention.md
docs/systems/gameplay-analytics-deployment.md
docs/systems/gameplay-analytics-hunt-areas.md
docs/systems/gameplay-analytics-grafana.md
```

Document:

- the new party-mode aggregate table;
- `REAGGREGATE_DAYS`;
- late-arriving session handling;
- shared-experience time semantics;
- stricter installer requirements;
- placeholder rejection in hunt-area tooling.

### H. Update workflow path filters if necessary

Verify these workflows include every changed file:

```text
.github/workflows/gameplay-analytics.yml
.github/workflows/gameplay-analytics-retention.yml
.github/workflows/gameplay-analytics-deployment.yml
.github/workflows/gameplay-analytics-grafana.yml
.github/workflows/gameplay-analytics-hunt-areas.yml
.github/workflows/gameplay-analytics-supply-loot.yml
```

---

## Required verification before merge

The repair PR must not be merged until all of the following pass.

### Static validation

```bash
python tools/analytics/validate_gameplay_analytics.py
python tools/analytics/validate_gameplay_analytics_context.py
python tools/analytics/validate_gameplay_analytics_batching.py
python tools/analytics/validate_gameplay_analytics_reliability.py
python tools/analytics/validate_gameplay_analytics_migrations.py
python tools/analytics/validate_gameplay_analytics_retention.py
python tools/analytics/validate_gameplay_analytics_retention_systemd.py
python tools/analytics/validate_gameplay_analytics_deployment.py
python tools/analytics/validate_gameplay_analytics_grafana.py
python tools/analytics/validate_gameplay_analytics_hunt_areas.py
```

### Python tests

```bash
python -m unittest discover -s tools/analytics -p "test_*.py" -v
```

### Lua tests

At minimum:

```bash
luajit tools/analytics/test_gameplay_analytics_context.lua
luajit tools/analytics/test_gameplay_analytics_batching.lua
luajit tools/analytics/test_gameplay_analytics_reliability.lua
luajit tools/analytics/test_gameplay_analytics_schema.lua
luajit tools/analytics/test_gameplay_analytics_supply_loot.lua
```

Run every additional Analytics Lua test present on `main`.

### MariaDB integration

At minimum:

```bash
bash tools/analytics/test_mariadb_integration.sh
bash tools/analytics/test_schema_migrations.sh
bash tools/analytics/test_retention_maintenance.sh
bash tools/analytics/test_gameplay_analytics_grafana.sh
```

### Shell syntax

```bash
bash -n tools/analytics/install_gameplay_analytics.sh
bash -n tools/analytics/maintain_gameplay_analytics.sh
bash -n tools/analytics/test_retention_maintenance.sh
```

### Full repository checks

Required checks currently expected for ordinary PRs:

```text
Fast Checks / run-checks
Build - Linux / Compile (linux-release)
```

Windows builds are conditional and should not be a required check for Analytics-only changes.

Do not merge while any relevant Analytics workflow is red or missing.

---

## Operating rules for future agents

1. Always branch from the latest `main`.
2. One focused PR at a time.
3. Do not create overlapping PRs for dependent Analytics work.
4. Do not merge a branch with conflicts or outdated duplicated history.
5. Do not weaken tests to make CI green.
6. Do not disable schema checks, retry limits, queue bounds or dead-letter handling.
7. Keep Analytics disabled by default.
8. Keep raw deletion disabled by default.
9. Never commit credentials.
10. Never invent hunt coordinates or market prices.
11. Do not add per-player, per-spell, per-monster or per-hunt Prometheus labels.
12. Do not store exact coordinate trails or party-member history.
13. Do not perform one SQL write per hit, loot item or movement event.
14. Verify the resulting files on `main` after merge.
15. Close or clearly mark superseded PRs and branches.

---

## Production rollout state

Repository implementation and CI do not prove production deployment.

Before claiming the system is live, confirm on the actual server:

1. main schema imported;
2. migrations applied;
3. retention schema imported;
4. reporting views imported;
5. `/analytics schema` reports ready and current;
6. `/analytics status` reports no schema error;
7. `CANARY_SERVER_VERSION` is set;
8. Analytics is explicitly enabled;
9. systemd maintenance timer is active;
10. Grafana datasource and dashboard are imported;
11. raw deletion remains disabled during the validation period;
12. real sessions appear and match expected hunt data.

Current repository defaults may still include:

```lua
enabled = false
trackSupplies = false
trackLoot = false
huntAreas = {}
```

These defaults are intentional until production validation is complete.

---

## Remaining broader roadmap after the audit repair

After the active repair PR is merged and production data is validated, future work may include:

1. broader spell coverage;
2. ammunition telemetry;
3. larger verified NPC price catalogue;
4. trustworthy optional market-price source;
5. historical queue/retry/flush metrics for Grafana;
6. verified named hunt-area catalogue from authoritative map coordinates;
7. separate item provenance and anti-duplication history subsystem.

The item provenance/anti-duplication system is a separate project and must not be mixed into the current Gameplay Analytics repair PR.

---

## Changelog summary

### Existing system

```text
Added core runtime, persistence, batching, retries, dead letters, schema migrations,
hunt context, retention, spell/supply/loot telemetry, Grafana and deployment tooling.
```

### Active production-audit repair

```text
Fixed solo/party aggregation semantics.
Fixed shared-experience percentage bounds.
Fixed nested corpse loot collection.
Added recent-day reaggregation for delayed sessions.
Hardened deployment installer inputs.
Rejected hunt-area placeholders.
Added operator configuration for recent reaggregation.
```

### Pending in the same repair

```text
Complete validators and regression tests.
Update MariaDB retention and Grafana integration tests.
Add nested loot and placeholder unit tests.
Update documentation and workflow path coverage.
Run full CI and merge only when green.
```
