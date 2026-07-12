# Agent-Facing Change Log

Curated behavior/architecture log for discovery; not a replacement for Git history or release notes.

## Unreleased

- GameStore balance sequencing repair in PR #187 emits one post-mutation balance snapshot, removes the parser-level duplicate, and preserves the existing disabled-reason deduplication without changing opcodes, prices or coin arithmetic.

- Achievement trigger repair in PR #184 corrects the exact canonical names for `You Got Horse Power` and `The Professor's Nut`, with a real-source scanner contract and no registry or persistence rename.
- Achievement helper repair in PR #176 replaces sparse-table length/range iteration with a deterministic sorted list of successfully registered IDs, derives real first/last bounds, and fixes public/secret metadata lookup and invalid-input logging without changing registry definitions or player KV data.
- PR #161 extends the OTBM HD pipeline with a one-process batch external AI backend, strict source/output path confinement, independent partial-output normalization, exact source-alpha restoration, compatible override manifests, and an optional no-weights-committed TibiaSR 2x reference adapter.
- PR #154 (replacement for auto-closed #147) adds a deterministic OTBM HD-sprite artifact pipeline: bounded-region sprite export with provenance, padded nearest/external upscale backends, source-alpha restoration, hash/geometry validation, 2x renderer overrides with original-sprite fallback, and visual comparison reports without modifying OTBM or client assets.
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
