# Cyclopedia Fix Log

Last updated: 2026-07-12 22:30 Europe/Warsaw

This file records every implementation batch derived from the read-only Cyclopedia audit. Each batch must update this log together with the affected source, validation status and compatibility decision.

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
