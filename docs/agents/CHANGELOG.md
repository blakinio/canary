# Agent-Facing Change Log

Curated behavior/architecture log for discovery; not a replacement for Git history or release notes.

## Unreleased

- Gameplay Analytics correctness hardening merged in PR #135: UTC day rollover, combat/death persistence eligibility, retention of short death sessions, truthful dead-letter reporting, rune-charge-aware supply costs, configurable maintenance `LEVEL_BRACKETS`, dimension-safe Grafana series, and focused Lua/Python/shell/MariaDB regression coverage.
- Added persistent multi-agent coordination, autonomous PR/CI/merge rules, active-work discovery, module catalogue, task/handoff templates, ADRs, and cross-repository contracts.

## 2026-07-12 bootstrap inventory

- InstanceManager and InstanceRegionPool are available under `src/game/instance/**`.
- OTBM script-resolution audit tooling is available under `tools/ai-agent/**` with schemas/review rules under `docs/ai-agent/**`.
- Gameplay Analytics and hunt-area tooling are available; production enabling remains an operator decision.
- Account-wide quest access exists with active hardening in PR #124.
- AI overlay materialization remains active in PR #125; the real staging/deployment pipeline merged in PR #118.
- DI migrations for `SharedPtrManager` and `Scripts` are merged.
- Forge history resolution uses item IDs with name fallback.
