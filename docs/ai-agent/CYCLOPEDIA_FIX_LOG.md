# Cyclopedia Fix Log

Last updated: 2026-07-12 22:52 Europe/Warsaw

This file records every implementation batch derived from the read-only Cyclopedia audit. Each batch must update this log together with the affected source, validation status and compatibility decision.

## 2026-07-12 22:52 — data source batch committed

- Atomic data/validator commit: `f89993e464b54f2dd3ba5b93b0fad10a62a23af2`.
- The temporary applicator and workflow are absent from the final PR diff.
- Commit creation was gated behind all Cyclopedia tests and `findingCount == 0`.
- This connector-authored commit triggers normal PR workflows because workflows created by the bot source commit require separate approval.

## 2026-07-12 22:48 — validator CLI correction

- Workflow run `29207895586` applied every reviewed data/validator replacement and passed all Cyclopedia tests.
- The zero-finding step stopped before scanning because the temporary workflow used obsolete `--markdown` and `--allow-findings` CLI flags.
- Those flags are removed; the source scope and hard `findingCount == 0` assertion are unchanged.

## 2026-07-12 22:42 — zero-finding data execution trigger

- PR #192 is rebased directly on current `main` commit `f4ee347c7f9d40e9ea800514fad9f5117259031d` and is mergeable.
- This logged push triggers the exact-match data applicator and mandatory zero-finding assertion.
- The generated source commit must remove the temporary applicator/workflow and preserve only gameplay data, validator, tests and durable logs.

## 2026-07-12 22:40 — Bestiary/Bosstiary data batch bootstrap

- Branch: `fix/cyclopedia-bestiary-data` from merged runtime fix `f105c8b44603d4ad640263a8971ebf2b71b06df2`.
- Reserved corrections: Monk's Apparition `2636`, Crypt Warrior `1995`, four numeric race metadata entries, and alternate Eradicator form `1226`.
- Validator will suppress a duplicate only when the complete active path set exactly equals a reviewed shared-form allowlist.
- Full acceptance target: all Cyclopedia tests pass and the complete active scan reports zero findings.
- No protocol, DB schema, map, asset or ambiguous counter-copy migration is included.

## 2026-07-12 22:30 — source batch committed

- Atomic source commit: `ce2151877d0d4d9ce0a638d1f5357d369137d3c2`.
- All six source corrections and four source-contract tests are present on PR #188.
- The temporary applicator and workflow are absent from the PR diff.
- Branch state before final CI: ahead of `main`, zero behind, mergeable.
- This connector-authored log commit intentionally retriggers all normal PR workflows after the bot-authored source commit required action approval.

## 2026-07-12 22:20 — regression-test correction

- The exact source replacement phase completed successfully in workflow run `29207302573`.
- The generated commit was intentionally blocked because the first synthetic scanner test was too coupled to its fixture text.
- The source scope remained unchanged.
- The replacement workflow created four direct source-contract tests against the modified repository files before committing.

## 2026-07-12 22:15 — PR-event execution trigger

- PR #188 is open against `main`.
- The one-shot workflow accepted both branch pushes and same-repository pull-request synchronization.
- Checkout and push explicitly targeted the PR head branch; the temporary workflow and applicator disappeared in the generated source commit.

## 2026-07-12 22:12 — execution trigger

- PR #188 was created from current `main`.
- The initial push trigger did not yet produce a source commit visible on the PR head, so execution was widened to the PR event without changing the fix scope.

## 2026-07-12 22:05 — runtime batch bootstrap

- Branch: `fix/cyclopedia-runtime-correctness`.
- Base: current `main` with merged audit #170.
- Scope reserved: difficulty arithmetic, reset cost, Bestiary null guard, Charm category guard, recent-PvP count window and empty boosted-boss row recovery.
- One-shot automation performed exact precondition-checked replacements, ran focused tests, updated all project logs and removed itself before committing.
- Data IDs, protocol, schema, maps, assets and player-state migration are outside this batch.

## Applied batch

### 2026-07-12 22:20 Europe/Warsaw — runtime correctness batch

- corrected Bestiary difficulty arithmetic to preserve fractional thresholds;
- corrected the all-Charm reset formula to charge 11,000 gold only for levels above 100;
- made Bestiary kill attribution null-safe before reading the monster type;
- corrected the Charm category guard;
- aligned recent-PvP pagination count with the 70-day row window;
- restored boosted-boss initialization when the table has no row;
- added four source-contract regression tests covering all six corrections;
- no protocol, schema, map, asset or player-data migration was added in this batch.

## Applied data batch

### 2026-07-12 22:45 Europe/Warsaw — Bestiary/Bosstiary data batch

- assigned Monk's Apparition Bestiary ID `2636`;
- assigned Crypt Warrior Bestiary ID `1995` and Undead race metadata;
- added Bird, Mammal and Dragon numeric race metadata to the three affected definitions;
- moved the alternate Eradicator form from Rupture ID `1225` to Eradicator ID `1226`;
- added exact path-set allowlists for intentional shared forms; unexpected extra or missing forms still fail validation;
- added full active-monster inventory and source-contract regression tests;
- target result: zero Cyclopedia scanner findings.

Evidence used before changing technical IDs:

- Crypt Warrior uses Bestiary ID `1995` in an independent complete Bestiary registry; `1674` is already occupied by Skeleton Elite Warrior.
- Monk's Apparition uses `2636` in two independent modern server datasets, while Druid's Apparition remains `1946`.
- `eradicator2.lua` exposes the display name Eradicator and is an alternate Eradicator form; it now shares `1226` with `eradicator.lua` instead of colliding with Rupture `1225`.
- Existing ambiguous historical counters are not copied or duplicated: `1946` remains Druid's Apparition, `1225` remains Rupture, and Eradicator forms use `1226`.
