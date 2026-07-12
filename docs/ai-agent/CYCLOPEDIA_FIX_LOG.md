# Cyclopedia Fix Log

Last updated: 2026-07-12 22:12 Europe/Warsaw

This file records every implementation batch derived from the read-only Cyclopedia audit. Each batch must update this log together with the affected source, validation status and compatibility decision.

## 2026-07-12 22:12 — execution trigger

- PR #188 was created from current `main`.
- The one-shot workflow is triggered by this logged push; its resulting commit must remove the temporary applicator and workflow.

## 2026-07-12 22:05 — runtime batch bootstrap

- Branch: `fix/cyclopedia-runtime-correctness`.
- Base: current `main` with merged audit #170.
- Scope reserved: difficulty arithmetic, reset cost, Bestiary null guard, Charm category guard, recent-PvP count window and empty boosted-boss row recovery.
- One-shot automation performs exact precondition-checked replacements, runs focused tests, updates all project logs and removes itself before committing.
- Data IDs, protocol, schema, maps, assets and player-state migration are outside this batch.
