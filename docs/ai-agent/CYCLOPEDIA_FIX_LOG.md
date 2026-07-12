# Cyclopedia Fix Log

Last updated: 2026-07-12 22:15 Europe/Warsaw

This file records every implementation batch derived from the read-only Cyclopedia audit. Each batch must update this log together with the affected source, validation status and compatibility decision.

## 2026-07-12 22:15 — PR-event execution trigger

- PR #188 is open against `main`.
- The one-shot workflow now accepts both branch pushes and same-repository pull-request synchronization.
- Checkout and push explicitly target the PR head branch; the temporary workflow and applicator must disappear in the generated source commit.

## 2026-07-12 22:12 — execution trigger

- PR #188 was created from current `main`.
- The initial push trigger did not yet produce a source commit visible on the PR head, so execution was widened to the PR event without changing the fix scope.

## 2026-07-12 22:05 — runtime batch bootstrap

- Branch: `fix/cyclopedia-runtime-correctness`.
- Base: current `main` with merged audit #170.
- Scope reserved: difficulty arithmetic, reset cost, Bestiary null guard, Charm category guard, recent-PvP count window and empty boosted-boss row recovery.
- One-shot automation performs exact precondition-checked replacements, runs focused tests, updates all project logs and removes itself before committing.
- Data IDs, protocol, schema, maps, assets and player-state migration are outside this batch.
