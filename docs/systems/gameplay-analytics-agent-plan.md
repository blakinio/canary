# Gameplay Analytics: remaining implementation plan

This document is the execution brief for finishing the production rollout and reporting layer of Gameplay Analytics.

The core collector, lifecycle handling, persistence, retry/dead-letter handling, batching, schema migrations, hunt context, party context and optional retention framework are already implemented. New work must build on the current `main` branch rather than reconstructing earlier PR branches.

## Objectives

Finish the remaining work in six focused phases:

1. production deployment package;
2. retention scheduler;
3. spell telemetry integrations;
4. supply and loot telemetry;
5. Grafana reporting package;
6. verified named hunt-area catalogue.

Each phase must be delivered as a separate, focused pull request. Dependent phases should start from `main` only after the previous phase is merged.

## Global operating rules

1. Work from the latest `main`.
2. Use one clean branch and one focused PR per phase.
3. Do not combine unrelated changes.
4. Do not run repository-wide formatting.
5. Do not modify map, OTBM or item files unless the phase explicitly requires it.
6. Do not keep overlapping PRs for the same task open.
7. Never weaken or bypass tests to obtain a green build.
8. Keep Gameplay Analytics disabled by default.
9. Analytics failures must never prevent Canary from starting.
10. Preserve bounded queues, bounded SQL batches and idempotent retries.
11. Avoid high-cardinality Prometheus labels.
12. Do not store exact coordinate trails or party-member identity histories.
13. Do not guess item prices, market values or hunt coordinates.
14. Every PR must include scope, non-goals, test evidence and rollout notes.
15. After merge, verify the resulting files on `main`.

## Phase 1: production deployment package

Create production-safe deployment assets for Gameplay Analytics.

### Required work

- Add an example environment file without credentials.
- Add a repeatable installation script or documented command sequence that:
  - imports the baseline schema;
  - runs numbered migrations;
  - verifies the installed schema version;
  - leaves Analytics disabled if validation fails.
- Document `CANARY_SERVER_VERSION` usage.
- Document `/analytics schema` and `/analytics status` verification.
- Add startup, rollback and recovery instructions.
- Add shell and documentation validation in CI.

### Acceptance criteria

- Re-running installation does not corrupt or duplicate schema state.
- No database credentials are committed.
- A migration or connection failure leaves Analytics disabled but does not stop Canary.
- The documented rollout starts with collection disabled until schema validation succeeds.

## Phase 2: retention scheduler

Package the existing maintenance runner for production scheduling.

### Required work

- Add ready-to-use systemd service and timer examples for:
  - `tools/analytics/maintain_gameplay_analytics.sh`;
  - an external environment file;
  - a daily schedule with persistent execution after downtime.
- Keep `DELETE_RAW_SESSIONS=false` by default.
- Document installation, enablement, disablement and removal.
- Document backup requirements and rollback limits.
- Validate required service/timer fields in CI.

### Acceptance criteria

- The first production run aggregates only.
- Raw deletion requires explicit opt-in.
- Catch-up work and delete batches remain bounded.
- The scheduler uses a database account restricted to Analytics tables where practical.

## Phase 3: spell telemetry integrations

Integrate spell-level data through:

```lua
GameplayAnalytics.recordSpell(player, spellName, damage, healing, mana, targets, critical)
```

### Required work

- Audit offensive spells, healing spells and relevant rune actions.
- Record casts, targets, damage, healing, spell mana and critical counts.
- Ensure session-wide damage, healing and mana already collected by generic hooks are not counted a second time.
- Keep the integration a no-op when Analytics or spell tracking is disabled.
- Keep hot-path overhead minimal.
- Add representative Lua execution tests and static regression validators.

### Acceptance criteria

- Offensive and healing integrations have focused tests.
- Spell aggregates are persisted without changing gameplay behaviour.
- Session totals remain unchanged by the additional spell breakdown.
- A validator detects future double-counting regressions.

## Phase 4: supply and loot telemetry

Integrate domain-specific item telemetry through:

```lua
GameplayAnalytics.recordSupply(player, itemId, amount, unitValue)
GameplayAnalytics.recordLoot(player, itemId, amount, npcValue, marketValue)
```

### Required work

Cover reliable event sources for:

- potions;
- runes;
- ammunition;
- other consumable supplies;
- monster loot;
- NPC values;
- optional market values only when a trustworthy source exists.

Collection must remain disabled by default until data quality is validated.

### Data rules

- Never invent or approximate prices silently.
- Document value-source precedence.
- Missing market values must follow the documented null/zero contract.
- Aggregate in memory; never issue one SQL write per item event.
- Prevent duplicate counting when multiple callbacks observe the same action.

### Acceptance criteria

- Representative Lua tests cover supplies and loot.
- MariaDB integration tests cover persistence and retry idempotency.
- No duplicate supply or loot counting is observed.
- Price sources and fallback behaviour are documented.

## Phase 5: Grafana reporting package

Create an importable reporting package backed by MariaDB.

### Required work

- Add stable SQL views or documented dashboard queries.
- Add a Grafana dashboard JSON.
- Add a MariaDB datasource provisioning example without credentials.
- Add import, upgrade and troubleshooting instructions.

### Required panels

- EXP/h by vocation, level bracket, hunt area and server version;
- DPS, damage taken and healing rate;
- deaths per 100 sessions;
- solo versus party comparisons;
- shared-experience ratio;
- spell efficiency;
- profit and supply cost where data exists;
- session count and minimum-sample warnings;
- queue, retry, dead-letter and flush health.

### Query rules

- Use daily aggregates for long date ranges.
- Use raw sessions only for drill-down.
- Do not expose per-player dashboard variables by default.
- Avoid full-table scans where existing indexes can be used.
- Empty datasets must not break panels.

### Acceptance criteria

- Dashboard JSON is syntactically valid.
- SQL is tested against the supported MariaDB version.
- Queries provide stable results when optional supply, loot or spell data is unavailable.

## Phase 6: named hunt-area catalogue

Add a safe process for maintaining `huntAreas` configuration.

### Required work

- Add validation for:
  - malformed rectangles;
  - inverted coordinate ranges;
  - duplicate names;
  - overlapping rectangles;
  - unstable ordering where first-match behaviour matters.
- Add test fixtures.
- Document how to add and verify new areas.
- Start with a small catalogue of areas whose coordinates can be proven from an authoritative source.
- Preserve fallback grid areas for all unconfigured locations.

### Privacy and correctness rules

- Never invent coordinates.
- Do not add exact player movement history.
- Keep hunt names stable once production data groups by them.
- Treat first matching rectangle as authoritative and document intentional overlaps explicitly.

### Acceptance criteria

- The validator rejects malformed, duplicate and unintended overlapping definitions.
- The initial catalogue contains only verified areas.
- Unconfigured areas continue to use the coarse fallback grid.

## PR completion checklist

For every phase:

- [ ] branch was created from current `main`;
- [ ] scope and non-goals are documented;
- [ ] focused tests were added;
- [ ] all relevant CI jobs completed successfully;
- [ ] real failures were fixed on the same branch;
- [ ] required status checks passed;
- [ ] PR was merged using the repository's configured merge method;
- [ ] merged files were verified on `main`;
- [ ] superseded branches or PRs were removed or clearly marked.

## Recommended execution order

Execute phases in the listed order. Phase 1 establishes a repeatable production rollout. Phase 2 prevents unbounded raw-data growth. Phases 3 and 4 enrich the dataset. Phase 5 exposes the data for balancing decisions. Phase 6 should proceed only as authoritative coordinates become available.
