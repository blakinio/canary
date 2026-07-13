# Agent-Facing Change Log

Curated behavior/architecture log for discovery; not a replacement for Git history or release notes.

## Unreleased

- PR #286 adds Phase 4 read-only spawn, boss and NPC validation: explicit active companion XML and definition evidence, current loader coordinate/radius/interval semantics, separate reward-boss and Bosstiary spawn-boss classification, conservative literal dynamic-creation inventory, exact static/dynamic overlap findings, and bounded World Index plus Phase 3 geometry correlation without executing Lua or modifying map/gameplay data. Its first active global datapack scan observed 52,903 groups, 84,294 placements, 2,688 definitions and 461 dynamic creation calls; duplicate active Harlow definitions and the resulting ambiguous placement remain review evidence rather than automatic repair.
- PR #274 adds the read-only Phase 3 OTBM teleport and reachability validator: bounded strict/optimistic walkability from World Index plus real appearance flags, automatic indexed teleport checks, reviewed non-teleport floor-transition manifests, no-corner-cut pathfinding, route/mechanic reachability, one-way/dead-end/cycle findings, optional script-resolution evidence, atomic reports and a local toolkit workflow without committing maps, indexes or client assets.
- Added bounded Forge server-authority policies and regressions in PR #250 so crafted normal Fusion, Convergence Fusion and Convergence Transfer requests are rejected before item/resource/history mutation; full Forge parity remains tracked by `CAN-PROGRAM-EQUIPMENT-UPGRADE-PARITY`.
- PR #251 aligns the Imbuement registry with the selected current live Tibia mechanics: fixed application fees of 7,500/60,000/250,000 gold at 100% success with no protection surcharge, Strike at 5% chance and +5%/+15%/+40% damage, and Basic Punch using item 10281 x25; existing Forgotten Knowledge and Vibrancy scroll repairs remain preserved.

- PR #225 adds the read-only Quest Map Validator on top of the merged World Index and script-resolution contracts: explicit quest source globs produce hashed AID/UID/item/position/teleport/storage evidence, bounded local `.widx` correlation classifies confirmed/map-only/script-only/unresolved/conflicting results, dynamic Lua remains unresolved, static item absence and generic missing positions are treated conservatively, JSON output is atomic, and CI publishes source evidence plus a local correlation toolkit without committing map artifacts.
- PR #219 implements the unified read-only OTBM world index planned by #190 and supersedes conflicted #211: the existing native scanner emits a deterministic binary postings cache, while a memory-mapped Python library and CLI provide bounded item/AID/UID/house-door/teleport/position/region queries with hashes, duplicate detection, atomic output and real-map validation without committing map or index artifacts.
- Raid startup repair in PR #205 splits active Draptor and Yeti monster bursts into progressive waves, enforces spawn-before-stage-advance timing, and separates the Undead Cavebear encounter identity without changing populations, broadcasts, maps or assets.

- The Beginning Carlos repair in PR #157 removes the stage-1 `outfit` completion bypass, gates trade to the accepted stage-6 task, sends tutorial `13` when that trade is first opened, and advances to stage 7 only after an actual meat/ham sale while preserving the existing shop transaction and prices.
- The Beginning Zirella reward-room repair in PR #156 seals UID `50085` until Zirella stage 8 and remaps shovel/rope tutorials to current reward UIDs `50093/50094`; it remains open and requires refresh against the advanced `main` branch.
- GameStore balance sequencing repair in PR #187 emits one post-mutation balance snapshot, removes the parser-level duplicate, and preserves the existing disabled-reason deduplication without changing opcodes, prices or coin arithmetic.

- Achievement trigger repair in PR #184 corrects the exact canonical names for `You Got Horse Power` and `The Professor's Nut`, with a real-source scanner contract and no registry or persistence rename.
- Achievement helper repair in PR #176 replaces sparse-table length/range iteration with a deterministic sorted list of successfully registered IDs, derives real first/last bounds, and fixes public/secret metadata lookup and invalid-input logging without changing registry definitions or player KV data.
- PR #161 extends the OTBM HD pipeline with a one-process batch external AI backend, strict source/output path confinement, independent partial-output normalization, exact source-alpha restoration, compatible override manifests, and an optional no-weights-committed TibiaSR 2x reference adapter.
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
