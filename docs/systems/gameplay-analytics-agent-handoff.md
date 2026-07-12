# Gameplay Analytics — agent handoff, status and remaining work

Last verified: **2026-07-12**  
Repository: `blakinio/canary`  
Primary branch: `main`

This document is the operational source of truth for agents continuing work on
Gameplay Analytics. It describes the product goal, shipped architecture,
completed changes, current work in progress, known defects, required follow-up,
testing surface and repository rules.

It covers **Gameplay Analytics only**. Other active projects in the repository
(multichannel, instances, OTBM tooling, deployment tooling, Forge fixes and so
on) are intentionally outside this handoff unless they directly affect an
Analytics branch or CI run.

---

## 1. Product goal

Gameplay Analytics exists to collect reliable, low-overhead, aggregated data
that can be used to balance vocations, hunting grounds, spells, supplies and
loot without recording player movement trails or issuing one database query per
game event.

The intended production flow is:

```text
Canary runtime events
        |
        v
bounded in-memory session aggregates
        |
        v
bounded batched + idempotent MariaDB persistence
        |
        +--> raw session/detail tables for recent drill-down
        |
        v
external daily maintenance
        |
        +--> daily long-range balance aggregates
        +--> optional bounded deletion of old raw sessions
        |
        v
Grafana / SQL reporting
```

The system must remain **opt-in**. Analytics or database failures must never
prevent the game server from starting or normal gameplay from continuing.

### Primary reporting questions

The implementation is meant to answer questions such as:

- How much EXP/h, DPS, healing, damage taken and profit does each vocation
  produce at a given level range and hunt?
- Did a balance patch improve or reduce performance for a vocation?
- How do solo and party sessions differ?
- Which spells are mana-efficient?
- Which hunting grounds have high death rates or poor profit?
- Is the Analytics pipeline healthy, retrying or dropping data?

### Explicit non-goals

- no exact coordinate trail or movement history;
- no per-event SQL write for hits, spells, potions or loot;
- no guessed item prices;
- no player identity variable in the default Grafana dashboard;
- no server-start failure merely because Analytics is unavailable;
- no automatic activation on production;
- no raw-data deletion without explicit operator opt-in and verified aggregates.

---

## 2. Current high-level status

### Shipped on `main`

The following layers are implemented and merged:

- opt-in Lua runtime and session aggregation;
- damage, healing, mana, experience, kill and death hooks;
- idempotent session/detail persistence;
- bounded retry, exponential backoff and dead-letter handling;
- multi-row detail batching;
- schema migrations and runtime schema guard;
- hunt-area and dynamic party context;
- optional daily retention schema and maintenance runner;
- production deployment package;
- systemd service/timer examples;
- representative spell telemetry;
- representative supply and loot telemetry;
- Grafana SQL views, dashboard JSON and provisioning examples;
- named hunt-area generator and validator;
- real MariaDB integration workflows;
- runtime integration hardening from PR #108.

### Still disabled by default

The shipped config intentionally remains conservative:

```lua
enabled = false
trackSupplies = false
trackLoot = false
huntAreas = {}
```

Do not change those defaults in a cleanup PR.

### Production state is not proven

Repository code and CI are present, but this repository alone does **not** prove
that a production host has:

- imported all schemas and migrations;
- enabled Analytics in Lua configuration;
- configured `CANARY_SERVER_VERSION`;
- installed and enabled the systemd timer;
- imported the Grafana dashboard;
- produced and reviewed real hunt data.

Treat production rollout as a separate operator task with backup, verification
and rollback steps.

---

## 3. Runtime architecture and important files

### Runtime load order

The intended layer order is:

```text
data-otservbr-global/scripts/lib/gameplay_analytics.lua
    -> gameplay_analytics_context.lua
    -> gameplay_analytics_schema.lua
    -> gameplay_analytics_batching.lua
    -> gameplay_analytics_reliability.lua
```

The system registration lives in:

```text
data-otservbr-global/scripts/systems/gameplay_analytics.lua
```

Do not re-execute the core library from shared spell, rune, action or callback
scripts. PR #108 established the required contract: those scripts resolve the
live `GameplayAnalytics` global at event time.

Re-running the core with `dofile(...)` after wrapper layers were installed can
replace wrapped functions while installation flags remain set, silently
removing context, batching or reliability behavior.

### Configuration

```text
data-otservbr-global/scripts/config/gameplay_analytics.lua
```

Important settings include:

- `enabled`;
- `databaseEnabled`;
- `trackSpells`;
- `trackSupplies`;
- `trackLoot`;
- queue/retry/dead-letter limits;
- detail batch size;
- context sampling interval and maximum gap;
- fallback hunt grid size;
- named `huntAreas`;
- server/balance version identifier.

### Main database files

```text
schema/gameplay_analytics.sql
schema/gameplay_analytics_migrations/
schema/gameplay_analytics_retention.sql
schema/gameplay_analytics_views.sql
```

### Operations

```text
tools/analytics/install_gameplay_analytics.sh
tools/analytics/migrate_gameplay_analytics.sh
tools/analytics/maintain_gameplay_analytics.sh
tools/analytics/systemd/
```

### Reporting

```text
grafana/gameplay-analytics-dashboard.json
grafana/provisioning/
docs/systems/gameplay-analytics-dashboards.md
```

### Focused integrations

```text
data/scripts/lib/gameplay_analytics_spell.lua
data/scripts/lib/gameplay_analytics_loot.lua
data/scripts/lib/gameplay_analytics_prices.lua

data/scripts/spells/attack/ethereal_spear.lua
data/scripts/spells/healing/ultimate_healing.lua
data/scripts/runes/fireball.lua
data/scripts/runes/intense_healing_rune.lua
data/scripts/actions/items/potions.lua
data/scripts/eventcallbacks/monster/postdroploot_gameplay_analytics.lua
```

### Named hunt-area tooling

```text
tools/analytics/gameplay_analytics_hunt_areas_lib.py
tools/analytics/validate_gameplay_analytics_hunt_areas.py
tools/analytics/generate_gameplay_analytics_hunt_areas.py
tools/analytics/gameplay_analytics_hunt_area_candidates.example.json
```

---

## 4. Changelog of major Analytics work

This is a condensed implementation history. Inspect the merged PR and current
`main` before relying on an old branch.

| PR | State | Main contribution |
|---:|---|---|
| #30 | merged | Initial opt-in Gameplay Analytics subsystem and MariaDB schema. |
| #34 | closed, superseded | First runtime-hook repair attempt; contained unrelated changes. Do not reuse. |
| #38 | closed, superseded | Clean replacement attempt for runtime hooks. |
| #46–#49 | merged | Runtime registration/validator corrections, especially monster spawn health registration. Some PRs also contained unrelated account-quest cleanup; inspect scope carefully. |
| #50 | closed, superseded | Valid root cause but unacceptable duplicated persistence override. Replaced by #52. |
| #52 | merged | Direct fix for `result` API shadowing in persistence plus regression validation. |
| #54 | merged | Session lifecycle and metric-accuracy hardening. |
| #55 | merged | Idempotent retry-safe session and detail persistence. |
| #58 | merged | Bounded retries, exponential backoff, dead-letter queue and health counters. |
| #61 | merged | Real MariaDB persistence integration tests. |
| #62 | merged | Multi-row detail batching with bounded statement size. |
| #63 | merged | Schema migrations, checksums and runtime schema guard. |
| #64 | closed, superseded | Conflict-heavy first hunt/party context PR. Replaced by #67. |
| #65 | merged | Optional daily aggregate/retention maintenance. |
| #67 | merged | Clean hunt-area and dynamic party context implementation; schema v3. |
| #72 | merged | Production deployment package and validation. |
| #73 | merged | systemd maintenance service/timer and env example. |
| #76 | merged | Representative spell telemetry and no-double-counting tests. |
| #79 | merged | Representative supply/loot telemetry and verified NPC price table. |
| #83 | merged | Grafana dashboard, MariaDB views and dashboard tests. |
| #105 | merged | Named hunt-area generation/validation tooling. |
| #108 | merged | Runtime load-order hardening and recursive nested-container loot. |

### PR #108 details

PR #108 is merged. It fixed two important post-rollout audit findings:

1. shared spell/rune/action/callback scripts no longer `dofile` the Analytics
   core; they use the live global at event time;
2. corpse loot now uses `corpse:getItems(true)`, so nested bag/backpack contents
   are included.

Validators and tests now reject future regressions of both patterns.

---

## 5. Known correctness gaps still requiring work

The items in this section are not optional polish. They affect data quality or
safe operation and should be completed before trusting production reports.

### 5.1 Solo versus party is currently aggregated incorrectly

Current long-range daily aggregation groups sessions by:

```text
session_date
server_version
hunt_area
vocation_id
level_bracket
```

Solo and party sessions can therefore be merged into the same daily row. The
existing reporting view later labels that combined row from its average party
size. This can make solo sessions disappear into a row labelled `party`.

#### Required correction

Create a separate daily aggregate whose primary key includes an explicit
`party_mode`, or store separate solo/party counters. Classify each raw session
**before** grouping.

Recommended table:

```text
analytics_daily_party_balance
```

Recommended key:

```text
(session_date, server_version, hunt_area, vocation_id, level_bracket, party_mode)
```

The exact session classification must be documented. A conservative rule is:

```text
party_size_max <= 1  -> solo
otherwise            -> party
```

Using only `party_size_avg` is simpler but classifies a session that briefly
joined a party as party based on an average threshold. Do not leave this
semantic choice implicit.

### 5.2 Shared-experience percentage uses mismatched clocks

`shared_experience_seconds` comes from context sampling while dashboard ratios
use `combat_seconds` as the denominator. Those clocks can diverge, producing an
inflated ratio or a value above 100%.

#### Preferred correction

At context finalization, cap persisted shared-experience seconds to the
session's finalized combat time:

```text
sharedExperienceSeconds = min(sharedExperienceSeconds, combatSeconds)
```

Also cap the reporting expression defensively. Add a Lua runtime test proving
that context sampling outside combat cannot produce a persisted ratio above
1.0.

An alternative is to persist a dedicated `context_seconds` denominator, but
that requires a schema migration and dashboard semantic change. Do not mix both
approaches without an explicit decision.

### 5.3 Retention misses late or corrected sessions

The current maintenance runner advances from `daily_aggregate_through + 1 day`.
Once a day is behind the checkpoint, a session flushed late or corrected later
may never be included in daily aggregates.

#### Required correction

Rebuild a bounded recent window on every maintenance run, for example:

```text
REAGGREGATE_DAYS=7
```

For each rebuilt day, replace the complete day in a transaction rather than
only upserting current groups. An upsert-only rebuild cannot remove a stale
old dimension when a raw session changes hunt, vocation grouping or another
key.

Safety requirements:

- sequential catch-up remains bounded by `MAX_DAYS_PER_RUN`;
- rolling rebuild remains bounded by `REAGGREGATE_DAYS`;
- raw deletion remains disabled by default;
- when deletion is enabled, `RAW_RETENTION_DAYS` must be greater than the
  rebuild window plus aggregation lag;
- the runner must never rebuild a date whose raw data may already have been
  deleted;
- both aggregate tables must be rebuilt in one transaction per day;
- late-arrival, corrected-dimension and stale-group-removal tests are required.

### 5.4 Deployment validation does not fully enforce its documented contract

The installer/validator currently focuses on placeholder values but needs
stricter rejection of empty or unresolved production values.

Required checks:

- `DB_PASSWORD` must not be empty and must not equal `CHANGE_ME`;
- `CANARY_SERVER_VERSION` must not be empty and must not equal `CHANGE_ME`;
- no secret is committed;
- installation still leaves Analytics disabled;
- failure must not edit the Lua config or partially claim successful rollout.

### 5.5 Hunt-area example placeholders are accepted as real candidates

The example candidate contains obvious placeholders such as:

```text
REPLACE_WITH_REAL_HUNT_NAME
x=0, y=0
_comment=EXAMPLE ONLY ...
```

The generator currently demonstrates its output against that example. A future
operator could accidentally treat it as a real area.

Required behavior:

- reject the exact placeholder name;
- reject candidates that still contain the example-only `_comment` marker;
- keep synthetic test fixtures usable;
- update CI so it tests expected rejection or uses a separate valid synthetic
  candidate fixture;
- never invent real hunt coordinates.

### 5.6 Telemetry coverage is intentionally partial

Current spell telemetry covers four representative casts only. Supply covers
potions and two runes. Loot pricing uses a small verified NPC catalogue and
market value remains zero.

This is not a correctness bug in the implemented paths, but reports must not be
presented as complete coverage.

Future work may include:

- more fixed-target spells and runes;
- accurate AoE target counts only after an engine-supported target-count hook;
- real critical-hit attribution only after an engine-supported signal;
- ammunition only after the consumed item ID is reliably exposed;
- a broader NPC price catalogue with a source comment for every entry;
- market values only from a trustworthy, documented source.

Never infer or guess missing values.

### 5.7 Dashboard pipeline health is partial

Persisted dead letters can be graphed. Queue depth, retry-in-progress counts and
flush duration are currently process-local values available through
`/analytics status`, not historical MariaDB series.

A future instrumentation PR may export these through an existing metrics
backend, but it must avoid high-cardinality labels and must not fabricate SQL
history from values that are not persisted.

---

## 6. Work currently in progress

### WIP branch

```text
fix/analytics-aggregation-correctness
```

This branch contains an **unmerged draft** of:

- `analytics_daily_party_balance`;
- rolling recent-day reaggregation;
- full-day aggregate replacement inside transactions;
- defensive shared-experience capping in SQL;
- updated retention integration tests;
- updated systemd env validation;
- initial reporting-view changes.

### Critical branch warning

The branch was created before PR #108 merged and is now divergent from `main`.
Do **not** open it directly as a pull request and do not force-merge its full
history.

The next agent must:

1. fetch the newest `main`;
2. create a fresh branch from that exact `main`;
3. copy/reimplement only the intended aggregation changes;
4. compare the resulting diff against `main`;
5. confirm that no PR #108 files appear as unrelated changes;
6. keep the final PR focused on aggregation/retention/reporting correctness.

Suggested clean branch name:

```text
fix/analytics-aggregation-correctness-clean
```

### WIP is not yet complete

Before a clean PR can be opened, the draft still needs:

- a final party-mode semantic decision (`party_size_max` versus average);
- runtime shared-experience capping and Lua tests, not SQL-only protection;
- updates to `docs/systems/gameplay-analytics-retention.md`;
- updates to `docs/systems/gameplay-analytics-dashboards.md`;
- updates to Grafana dashboard validator expectations;
- updates to `test_gameplay_analytics_dashboard_views.sh`;
- repeatable import tests for the new party aggregate table;
- checks that an existing retention installation can add the new table safely;
- full dedicated MariaDB workflow execution;
- general CI and Linux build verification;
- a clean one-purpose PR description and rollback notes.

---

## 7. Recommended execution order

Finish work sequentially. Do not open several dependent Analytics PRs at once.

### PR A — aggregation, shared-EXP and retention correctness

Scope:

- dedicated solo/party daily aggregate;
- documented session classification;
- runtime cap for shared-experience seconds;
- defensive SQL ratio cap;
- bounded recent-day rebuild;
- complete-day transactional replacement;
- dashboard view migration to the party aggregate;
- MariaDB/Lua/Python regression coverage;
- retention/dashboard documentation.

Do not include deployment-placeholder or hunt-area-placeholder changes here.

### PR B — deployment contract hardening

Scope:

- reject empty and placeholder DB password;
- reject empty and placeholder server version;
- update validator tests and deployment documentation;
- keep Analytics disabled and do not edit config automatically.

### PR C — hunt-area placeholder rejection

Scope:

- reject example placeholder name and example-only comment;
- add dedicated valid synthetic candidate fixture for generator CI;
- update unit tests and hunt-area documentation.

### PR D — optional telemetry expansion

Only after the correctness PRs are merged:

- add more verified spells, runes, supplies or prices in small batches;
- each batch must have focused tests and source attribution;
- do not mix engine API changes with a large content sweep.

### Production rollout

After PRs A–C are merged and verified:

1. back up MariaDB;
2. apply baseline schema, migrations and optional retention schema;
3. apply reporting views;
4. run `/analytics schema` and `/analytics status`;
5. set a real `CANARY_SERVER_VERSION`;
6. enable core Analytics only;
7. leave supply/loot and raw deletion disabled initially;
8. collect several days of data;
9. compare raw sessions to daily aggregates;
10. import Grafana dashboard and verify empty/low-sample behavior;
11. enable supply/loot only after confirming desired coverage;
12. enable raw deletion only after backup and aggregate verification.

---

## 8. Required testing surface

### Core validators and unit tests

```bash
python tools/analytics/validate_gameplay_analytics.py
python -m unittest discover -s tools/analytics -p "test_*.py" -v
```

### Lua tests

Run the focused scripts used by the Analytics workflows, including:

```text
test_gameplay_analytics_batching.lua
test_gameplay_analytics_context.lua
test_gameplay_analytics_reliability.lua
test_gameplay_analytics_schema.lua
test_gameplay_analytics_spell_integration.lua
test_gameplay_analytics_supply_loot_integration.lua
```

### Shell syntax

```bash
bash -n tools/analytics/install_gameplay_analytics.sh
bash -n tools/analytics/migrate_gameplay_analytics.sh
bash -n tools/analytics/maintain_gameplay_analytics.sh
bash -n tools/analytics/test_retention_maintenance.sh
```

### MariaDB

The dedicated workflows must verify at least:

- baseline schema import;
- migration runner;
- repeated optional-schema import;
- idempotent session/detail upserts;
- detail foreign-key cascade;
- daily aggregate values;
- solo and party separation;
- shared-experience percentage never above 100%;
- late session included by rolling rebuild;
- corrected dimension removes stale aggregate group;
- raw deletion remains opt-in and bounded;
- aggregates survive deletion of eligible raw rows;
- dashboard views apply repeatedly and work on empty data;
- indexed drill-down plans remain index-friendly.

### GitHub checks

Current repository protection has been configured around stable checks such as:

```text
Fast Checks / run-checks
Build - Linux / Compile (linux-release)
```

Do not add a permanently required check that is conditionally skipped, such as
a Windows build that only runs for engine changes.

A green subsystem workflow does not replace the required general checks.

---

## 9. Agent operating rules

1. Start every task from the newest `main`.
2. One focused branch and one focused PR per independent task.
3. Merge one dependent PR before opening the next dependent PR.
4. Never reuse conflict-heavy or superseded PR history.
5. Never disable, weaken or bypass a failing test to obtain green CI.
6. Fix the root cause on the same branch and rerun the relevant workflow.
7. Do not perform repository-wide formatting.
8. Do not modify `.otbm`, `items.otb` or unrelated datapack content.
9. Keep Analytics disabled by default.
10. Keep raw deletion disabled by default.
11. Preserve bounded queues, retries, batches, catch-up and cleanup loops.
12. Preserve idempotent persistence and retry behavior.
13. Never issue one SQL statement per gameplay event.
14. Never guess prices, target counts, critical hits or hunt coordinates.
15. Never add exact movement history or party-member identity history.
16. Avoid high-cardinality metrics labels.
17. Shared scripts must use the live `GameplayAnalytics` global and must never
    `dofile` the core Analytics library.
18. Database/Analytics failure must not stop Canary startup.
19. After merge, verify the resulting files on `main`, not only the PR branch.
20. Close or clearly mark superseded branches/PRs.

---

## 10. Review checklist for every future Analytics PR

### Scope

- [ ] The PR has one coherent goal.
- [ ] Non-goals are explicitly listed.
- [ ] No unrelated account-quest, map, multichannel or engine cleanup appears.
- [ ] Diff is based on current `main`.

### Runtime safety

- [ ] Analytics remains opt-in.
- [ ] Gameplay behavior is unchanged when Analytics is disabled.
- [ ] No core library re-execution from shared scripts.
- [ ] No unbounded queue, retry, batch or maintenance loop.
- [ ] No synchronous database write added to a hot event path.

### Data correctness

- [ ] Counters cannot double-count generic combat hooks.
- [ ] Retry is idempotent.
- [ ] Dimension changes cannot leave stale aggregate rows.
- [ ] Ratios use matching clocks and safe denominators.
- [ ] Missing values remain zero/null according to the documented contract.

### Database safety

- [ ] Schema operation is repeatable.
- [ ] Existing installations have a safe upgrade path.
- [ ] Backup and rollback behavior is documented.
- [ ] Raw deletion remains explicitly gated.
- [ ] MariaDB integration tests cover the real SQL.

### CI

- [ ] Python validators pass.
- [ ] Lua tests pass.
- [ ] Shell syntax passes.
- [ ] MariaDB integration passes.
- [ ] General required checks pass.
- [ ] Autofix output is reviewed rather than blindly accepted.

### Post-merge

- [ ] Files are re-read from `main`.
- [ ] No superseded PR remains misleadingly open.
- [ ] This handoff document is updated when architecture, status or priorities
      materially change.

---

## 11. Quick start for the next agent

Use this exact sequence:

```text
1. Read this file.
2. Inspect current main and all open Analytics PRs.
3. Confirm PR #108 is present on main.
4. Inspect fix/analytics-aggregation-correctness only as a WIP reference.
5. Create fix/analytics-aggregation-correctness-clean from current main.
6. Implement PR A from section 7 without copying unrelated history.
7. Run validators, Lua tests, MariaDB tests and general CI.
8. Fix failures on the same branch.
9. Merge only after required checks pass.
10. Verify main and update this handoff.
```

Do not assume old summaries, branch names or PR descriptions are authoritative
when they conflict with current `main`.
