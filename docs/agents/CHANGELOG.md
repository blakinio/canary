# Agent-Facing Change Log

Curated behavior/architecture log for discovery; not a replacement for Git history or release notes.

## Unreleased

- The Beginning Carlos repair in PR #157 removes the stage-1 `outfit` completion bypass, gates trade to the accepted stage-6 task, sends tutorial `13` when that trade is first opened, and advances to stage 7 only after an actual meat/ham sale while preserving the existing shop transaction and prices.
- The Beginning Zirella reward-room repair in PR #156 seals UID `50085` until Zirella stage 8 and remaps shovel/rope tutorials to current reward UIDs `50093/50094`; it remains open and requires refresh against the advanced `main` branch.
- PR #154 (replacement for auto-closed #147) adds a deterministic OTBM HD-sprite artifact pipeline: bounded-region sprite export with provenance, padded nearest/external upscale backends, source-alpha restoration, hash/geometry validation, 2x renderer overrides with original-sprite fallback, and visual comparison reports without modifying OTBM or client assets.
- The Beginning Collecting Wood restoration in PR #149 adds exact-position Actions for the five tutorial dead trees and Zirella's cart, creating branch `7772` on the ground and advancing both Zirella storages from stage 6 to 7 after one authentic branch delivery without changing the OTBM.
- PR #145 was closed without merge after historical tutorial MoveEvents were judged broader than the proven current-game contract; no gameplay from that PR landed, while PR #144's evidence classification remains available for semantic review.
- Gameplay Analytics dry-run audit merged in PR #140: a no-server/no-database workflow now tests lifecycle boundaries and maintenance configuration; it fixed false short-session persistence counters, undercounted non-combat discards, and overflowing `LEVEL_BRACKETS` input.
- Gameplay Analytics correctness hardening merged in PR #135: UTC day rollover, combat/death persistence eligibility, retention of short death sessions, truthful dead-letter reporting, rune-charge-aware supply costs, configurable maintenance `LEVEL_BRACKETS`, dimension-safe Grafana series, and focused Lua/Python/shell/MariaDB regression coverage.
- Added persistent multi-agent coordination, autonomous PR/CI/merge rules, active-work discovery, module catalogue, task/handoff templates, ADRs, and cross-repository contracts.

## 2026-07-12 bootstrap inventory

- InstanceManager and InstanceRegionPool are available under `src/game/instance/**`.
- OTBM script-resolution audit tooling is available under `tools/ai-agent/**` with schemas/review rules under `docs/ai-agent/**`.
- Gameplay Analytics and hunt-area tooling are available; production enabling remains an operator decision.
- Account-wide quest access exists with active hardening in PR #124.
- AI overlay materialization and real staging/deployment merged in PRs #125 and #118.
- DI migrations for `SharedPtrManager` and `Scripts` are merged.
- Forge history resolution uses item IDs with name fallback.
