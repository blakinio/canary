# Agent-Facing Change Log

Curated behavior/architecture log for discovery; not a replacement for Git history or release notes.

## Unreleased

- The Beginning Zirella reward-room restoration in PR #156 seals UID `50085` until Zirella stage 8, preserves standard open/close door behavior, and remaps shovel/rope tutorials to current reward UIDs `50093/50094` without changing reward contents or the OTBM.
- The Beginning Collecting Wood restoration in PR #149 adds exact-position Actions for the five tutorial dead trees and Zirella's cart, creating branch `7772` on the ground and advancing both Zirella storages from stage 6 to 7 after one authentic branch delivery without changing the OTBM.
- The Beginning tutorial restoration in PR #145 adds current-API MoveEvents for the 24 map AIDs classified by PR #144, restoring one-shot guidance, map marks, effects and Santiago/Zirella/cave progression gates without changing the OTBM.
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
