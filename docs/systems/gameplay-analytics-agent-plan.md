# Gameplay Analytics: completed implementation plan

Status: **complete in the repository**  
Last verified: **2026-07-12**

This file originally described the remaining implementation plan for Gameplay
Analytics. All six planned phases and the post-implementation correctness audit
have now been completed in the repository.

The current operational handoff is:

```text
docs/systems/gameplay-analytics-agent-handoff.md
```

Use that document as the source of truth. Do not use old task branches or this
historical phase list to infer that repository work is still missing.

## Completed phases

1. **Production deployment package**
   - environment template;
   - repeatable schema installer and migration runner;
   - schema/status verification procedure;
   - rollback and failure-isolation documentation;
   - strict empty/placeholder value rejection before SQL access.

2. **Retention scheduler**
   - systemd service and timer examples;
   - bounded catch-up and rolling rebuild;
   - raw deletion disabled by default;
   - transactional rebuild of both daily aggregate tables.

3. **Spell telemetry**
   - safe representative offensive, healing and rune integrations;
   - no-double-counting helper and regression tests.

4. **Supply and loot telemetry**
   - representative potions and runes;
   - verified NPC price precedence;
   - recursive nested-container corpse loot;
   - no guessed market values.

5. **Grafana reporting**
   - MariaDB views;
   - dashboard JSON and provisioning examples;
   - corrected solo/party reporting;
   - shared-experience cap;
   - long-range aggregate and short-range drill-down separation.

6. **Named hunt-area tooling**
   - generator and validator;
   - coordinate, overlap and duplicate checks;
   - rejection of unfinished example placeholders;
   - fallback grid retained while real rectangles remain unverified.

## Post-plan audit fixes

The audit additionally corrected:

- runtime library re-execution from shared scripts;
- nested loot omission;
- mixed solo/party daily rows;
- shared-experience clock mismatch;
- missed late/corrected sessions after the maintenance checkpoint;
- stale daily dimension groups;
- incomplete deployment environment validation;
- accidental generation from the hunt-area example template.

## What is not proven by repository completion

Production deployment still requires access to the actual host and database.
The operator must:

- create a database backup;
- install/apply schemas and migrations;
- set real credentials and `CANARY_SERVER_VERSION`;
- verify `/analytics schema` and `/analytics status`;
- enable Analytics deliberately;
- install the retention timer;
- import/provision Grafana;
- validate real data before enabling raw deletion.

Repository access alone cannot prove that these steps were performed.

## Future enhancements

Expanding spell coverage, ammunition support, verified item prices, real named
hunt rectangles or persisted pipeline-health history are optional product
extensions. They are not unfinished work from this implementation plan and
must be handled as separate focused changes.
