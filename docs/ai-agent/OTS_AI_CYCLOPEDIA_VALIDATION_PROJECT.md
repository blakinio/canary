# OTS AI Cyclopedia Validation — project state and handoff

> **Updated:** 2026-07-12 21:00 Europe/Warsaw  
> **Parent methodology:** `docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md`  
> **Repository:** `blakinio/canary`  
> **Branch:** `feat/cyclopedia-validation-audit`  
> **PR:** [#170](https://github.com/blakinio/canary/pull/170) — draft  
> **Task:** `docs/agents/tasks/active/CAN-20260712-cyclopedia-validation.md`  
> **Current stage:** static audit complete and verified; focused gameplay/data fixes and disposable runtime scenarios remain  
> **Safety:** #170 is read-only and does not change gameplay, protocol, DB schema, map, assets or OTClient.

## 1. Goal

Validate Canary Cyclopedia across seven domains while keeping definition, runtime, persistence and Canary ↔ OTClient evidence separate:

1. Items;
2. Bestiary;
3. Charms;
4. Bosstiary;
5. Map;
6. Character/Titles;
7. Houses.

Reference requested by the user: `https://tibia.fandom.com/wiki/Cyclopedia`. It is a comparison source, not unconditional truth. Large wiki tables and spoilers are not copied into the repository.

## 2. Evidence layers

- **Structure:** IDs, fields, enums, thresholds, tier arrays and sparse registries.
- **References:** monster→Bestiary, Charm→handler, boss→monster, title→unlock, area→trigger, house→world/DB/protocol.
- **Semantics:** progression, costs, reset state, rarity stages, pagination and legal house actions.
- **Runtime/protocol:** loading, request→handler→response, fields/counts/gates and invalid-data handling.
- **Persistence/gameplay:** initial state, action, packet, saved state, relog, idempotency and cleanup.
- **Regression:** focused static checks on every relevant change; disposable DB/client scenarios when required.

Dispositions are independent from confidence. Main values: `definition-invalid`, `definition-needs-review`, `display-metadata-defect`, `latent-helper-defect`, `confirmed-runtime-defect`, `protocol-contract-defect`, `persistence-defect`, `needs-evidence`, with `high`/`medium`/`low` confidence.

## 3. Active sources and boundaries

Scanner roots:

```text
data/monster
data-otservbr-global/monster
```

`data-canary` is excluded to avoid mixing an alternate datapack with active global data.

Primary sources:

```text
data/scripts/systems/bestiary_charms.lua
data/scripts/lib/register_bestiary_charm.lua
src/io/iobestiary.*
src/io/io_bosstiary.*
src/creatures/players/components/player_cyclopedia.*
src/creatures/players/components/player_title.*
src/server/network/protocol/protocolgame.*
src/enums/player_cyclopedia.hpp
src/map/house/**
schema.sql
```

A future protocol fix must identify Canary producer, OTClient consumer, field order/width/signedness, counts, optional fields and version gates, then update `CROSS_REPO_CONTRACTS.md`. #170 only performs read-only OTClient inventory.

## 4. Implemented artifacts

```text
tools/ai-agent/cyclopedia_validation.py
tools/ai-agent/test_cyclopedia_validation.py
.github/workflows/cyclopedia-validation.yml
docs/ai-agent/CYCLOPEDIA_VALIDATION_REPORT.md
docs/ai-agent/CYCLOPEDIA_RUNTIME_TEST_PLAN.json
```

CLI:

```bash
python tools/ai-agent/cyclopedia_validation.py \
  --repository-root . \
  --otclient-root otclient \
  --output artifacts/CYCLOPEDIA_VALIDATION.json \
  --fail-on none
```

The JSON report is uploaded by CI rather than committed.

## 5. Final verified scan

Verified audit code head: `741ffed81275d37fd700cacdb05cbae05a0a1356`, directly based on current `main` `ab0ca005625ca4f80fc5931d86a3f8d0b0304299`.

Workflow run `29204136200` succeeded. Repository CI run `29204136318` and AI Agent Tools run `29204136186` also succeeded on the same code head.

- 7 domains;
- 1,656 active monster files;
- 749 Bestiary definitions;
- 249 Bosstiary definitions;
- 25 Charms;
- 18 scanner findings: 3 errors and 15 warnings;
- no scanned server/client declaration-definition gaps;
- artifact `8263239684`;
- JSON digest `sha256:e3fad997b2c1104e221807a596e48638a4a3992ea0f85d75d4bb72bc61b8574f`.

All Cyclopedia workflow steps passed: Canary/OTClient checkout, 9 tests, compilation, scan, JSON validation, invariants, summary and artifact upload. At verification the branch was one commit ahead of `main`, zero behind, and PR #170 was mergeable.

## 6. Confirmed defects

### Runtime/data — high confidence

- integer division collapses a Bestiary difficulty band;
- recent PvP rows use a 70-day filter but pagination count does not;
- Crypt Warrior has Bestiary data but no positive `raceId`;
- Druid's Apparition and Monk's Apparition are distinct Bestiary creatures sharing race ID `1946`, so progress/Charm assignment collides;
- Eradicator and Rupture are distinct Bosstiary bosses sharing boss ID `1225`, so progress/boss-slot state collides.

Correct replacement IDs are not guessed. These fixes belong in separate small PRs.

### Display metadata — high confidence

Missing numeric `Bestiary.race` metadata affects race filters/unlocked counts for:

- Agrestic Chicken `1979`;
- Terrified Elephant `771`;
- Haunted Dragon `1376`;
- Crypt Warrior.

### Latent helper/resilience — high confidence

- Charm category registration is guarded by `mask.type` instead of `mask.category`;
- `addBestiaryKill` dereferences `mtype` before the null guard;
- boosted-boss empty-result fallback is unreachable after an earlier return.

### Needs evidence — medium confidence

- full Charm reset formula requires an authoritative current rule and boundary tests at levels 100/101/102.

### Likely intentional shared forms

Kept visible as review warnings: Bestiary `213`, `227`; Bosstiary `1406`, `1811`, `1969`.

Full details: `docs/ai-agent/CYCLOPEDIA_VALIDATION_REPORT.md`.

## 7. Runtime plan

`CYCLOPEDIA_RUNTIME_TEST_PLAN.json` contains 10 disposable scenarios:

- Bestiary difficulty boundaries;
- full Charm reset boundaries;
- Charm assignment/persistence;
- null-safe kill attribution;
- Bestiary progression/relog;
- missing boosted-boss row recovery;
- Bosstiary stages/slots/relog;
- recent PvP pagination;
- seven-domain Canary ↔ OTClient packet smoke;
- Houses state/action matrix.

Production DB, production characters, production map and upstream writes are forbidden.

## 8. Completion checklist

- [x] dedicated project document and task record;
- [x] branch, draft PR and ACTIVE_WORK entry;
- [x] seven-domain scanner;
- [x] active Charm/Bestiary/Bosstiary parsing;
- [x] Canary/OTClient static protocol inventory;
- [x] evidence report and runtime plan;
- [x] module catalogue entry;
- [x] final alignment with current `main` and Achievement task archival;
- [x] corrected full-checkout CI/artifact;
- [x] reference review of duplicate IDs `1946` and `1225`;
- [x] mergeability verified on the audit code head;
- [ ] focused fix PRs for confirmed defects;
- [ ] disposable runtime/DB/packet scenarios;
- [ ] authoritative replacement IDs for `1946` and `1225`.

## 9. Changelog

### 2026-07-12 21:00 — final verified static audit

- realigned #170 onto current main `ab0ca005...` after Achievement Validation archival;
- preserved the merged Achievement module and removed its closed task from Active Work;
- verified PR mergeability and clean one-commit diff;
- Cyclopedia Validation, repository CI and AI Agent Tools passed on `741ffed812...`;
- final artifact confirms 1,656 monster files, 749 Bestiary, 249 Bosstiary, 25 Charms and 18 findings;
- updated this project file, report, task and PR body;
- no gameplay/protocol/data/client fix was added to #170.

### 2026-07-12 20:31 — scanner correction

- corrected optional `Bestiary.race` classification;
- corrected recent PvP detection to `loadRecentKills`;
- expanded tests from 8 to 9.

### 2026-07-12 20:10 — implementation batch

- added scanner, tests, workflow, report, runtime plan and catalogue entry.

### 2026-07-12 19:41 — start

- created branch, task, dedicated project document and draft PR #170 in `blakinio/canary` only.

## 10. Handoff

Read `AGENTS.md`, agent indexes, this document, task record, evidence report, runtime plan, PR #170 and workflow runs `29204136200`, `29204136318`, `29204136186`.

Next actions:

1. source correct replacement IDs for Bestiary `1946` and Bosstiary `1225` from authoritative client/server data;
2. open separate focused PRs for the five confirmed defects;
3. execute P0 disposable runtime scenarios;
4. packet-smoke all seven domains with the maintained OTClient;
5. update this file, task and report after every implementation/test/CI/review batch.

Do not edit gameplay, protocol, DB schema, map or assets in #170. Do not write to `opentibiabr/*`. Do not duplicate merged Achievement Validation #165. Do not invent missing IDs or rules.

### 2026-07-12 22:20 Europe/Warsaw — runtime correctness batch

- corrected Bestiary difficulty arithmetic to preserve fractional thresholds;
- corrected the all-Charm reset formula to charge 11,000 gold only for levels above 100;
- made Bestiary kill attribution null-safe before reading the monster type;
- corrected the Charm category guard;
- aligned recent-PvP pagination count with the 70-day row window;
- restored boosted-boss initialization when the table has no row;
- added four source-contract regression tests covering all six corrections;
- no protocol, schema, map, asset or player-data migration was added in this batch.
