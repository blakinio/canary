# OTS OTBM tooling roadmap

> Repository: `blakinio/canary`  
> Coordination: `OTS-OTBM-VALIDATION`  
> Last refreshed: 2026-07-13  
> Evidence rule: static source/map evidence is not live gameplay proof

## Mission

Maintain one deterministic, evidence-based OTBM analysis stack that agents can reuse for quests, teleportation, reachability, NPCs, spawns, storage progression, semantic diffs and—only after explicit safety gates—bounded map patching.

The stack reuses the existing native OTBM scanner, World Index, script resolver, Quest Map Validator, appearances parser, Phase 3 reachability and factual renderer. It must not create competing OTBM parsers/pathfinders or use AI-generated imagery as map evidence.

## Programme status

| Phase | Scope | State | Delivery |
|---:|---|---|---|
| 1 | Unified OTBM World Index | merged and archived | #219 / #223 |
| 2 | Quest Map Validator | merged and archived | #225 / #236 |
| 3 | Teleports, floor transitions and reachability | merged and archived | #274 / #277 |
| 4 | Spawns, bosses and NPCs | merged and archived | #286 / #290 |
| 5 | Storage dependency graph | not started | separate future task |
| 6 | Semantic OTBM diff and visual evidence | not started | separate future task |
| 7 | Geometry and consistency audit | not started | separate future task |
| 8 | Safe bounded OTBM patch writer | blocked by Phases 6–7 safety gates | separate future task |

Every phase is a separate bounded task, branch and PR. Do not combine phases.

## Shared evidence boundaries

- Dynamic Lua is not executed.
- Dynamic expressions remain `unresolved`.
- `unresolved` is never promoted to handled without direct evidence.
- `map-only` or source-only evidence is a review candidate, not automatic proof of a defect.
- AID/UID presence, creature definitions and handler resolution do not prove player reachability or successful execution.
- A source/map match can still be blocked by doors, quest state, walkability, direction, account state, protocol or runtime conditions.
- Green CI proves only the checks executed at that commit; it does not prove live gameplay.
- Coordinates, item IDs, AID, UID, storage values, spawn radii/times and transition offsets must never be invented.
- World Index, Quest Map Validator, reachability and spawn/NPC validation are read-only.
- `.otbm`, `.widx`, `items.otb`, appearances binaries, client packages, generated large reports and renders stay outside Git.
- Map images must come from the real OTBM, compatible client assets and the factual renderer.
- Do not use AI image generation to visualize or modify the map.
- Upstream `opentibiabr/*` repositories are read-only for this programme.

## Phase 1 — Unified OTBM World Index

### Contracts and entrypoints

- binary magic `OTSWIDX1`, version `1`;
- provenance manifest `canary-otbm-world-index-v1`;
- query response `canary-otbm-world-query-v1`;
- native build report `canary-otbm-world-index-build-v1`;
- `tools/ai-agent/otbm_item_audit_scan.cpp`;
- `tools/ai-agent/otbm_world_index.py`;
- `tools/ai-agent/otbm_world_index_tool.py`.

The existing native scanner is reused. No second OTBM parser exists.

### Indexed evidence

- exact tile positions and stacks;
- item IDs, action IDs and unique IDs;
- house-door IDs;
- teleport source placements and destinations;
- inclusive 3D regions;
- tile flags, house IDs and exact counts.

### Safety

- deterministic binary sections and postings;
- duplicate exact tile positions and corrupt/incompatible headers fail closed;
- bounded query output with exact total counts;
- source map, scanner and index hashes;
- source stability check during build;
- atomic output and symlink rejection;
- source map is never modified.

## Phase 2 — Quest Map Validator

### Contracts and entrypoints

- source evidence `canary-quest-map-evidence-v1`;
- correlated report `canary-quest-map-validation-v1`;
- schema `docs/ai-agent/QUEST_MAP_VALIDATION.schema.json`;
- `tools/ai-agent/quest_map_validation.py`;
- `tools/ai-agent/quest_map_validation_tool.py`.

### Capabilities

- explicit include/exclude source selection;
- per-source SHA-256, line and bounded context;
- static AID/UID/item/position/teleport/storage evidence;
- direct `Storage...` alias canonicalization;
- World Index and script-resolution correlation;
- classifications `confirmed`, `map-only`, `script-only`, `unresolved`, `conflicting`;
- bounded samples, exact counts, atomic output and symlink rejection.

Storage facts remain inventory only until Phase 5. A missing static item is not automatically `script-only` because rewards and dynamic creation may not require an OTBM placement.

## Phase 3 — Teleports, floor transitions and reachability

### Delivery

Merged PR #274 delivered:

- report `canary-otbm-reachability-v1`;
- reviewed transition manifest `canary-otbm-transition-manifest-v1`;
- public facade `tools/ai-agent/otbm_reachability.py`;
- CLI `tools/ai-agent/otbm_reachability_tool.py`;
- focused evidence, transition, graph and analysis modules;
- `docs/ai-agent/OTBM_REACHABILITY.schema.json`;
- `docs/ai-agent/OTBM_TRANSITIONS.schema.json`;
- `docs/ai-agent/OTBM_REACHABILITY.md`;
- evidence-boundary ADR and dedicated workflow.

Final feature head: `230237188cf8beed738e96923b6346948dc70d20`.  
Squash merge: `0a9afe2821e249a15c9402419483675a2842f5a8`.

### Geometry and transition policy

The validator consumes actual appearance flags and emits:

- **strict** — confirmed ground, no static blocker, no conditional blocker and no unknown appearance;
- **optimistic** — confirmed ground and no static blocker, with conditional/unknown runtime state retained.

Default movement is four-directional. Optional diagonals require both orthogonal corner tiles. Indexed teleports are consumed automatically. Stairs, ladders, holes, rope spots and other floor changes require a reviewed manifest; offsets are never guessed from names, sprites or visual memory.

Routes and reachable map mechanics are classified as `confirmed`, `conditional`, `unreachable` or `invalid` inside one explicit bounded region. This does not model live storage/account state, creatures, players or movable blockers.

### Final validation evidence

Head `230237188cf8beed738e96923b6346948dc70d20`:

- OTBM Reachability `29271057597`: success;
- Agent Task Ownership `29271057936`: success;
- AI Agent Tools `29271058098`: success;
- OTBM Map Tools `29271057570`: success;
- autofix.ci `29271058771`: success;
- repository CI `29271058469`: success;
- Linux Release `86888848766`: success;
- Required `86890150987`: success;
- review threads: zero.

## Phase 4 — Spawns, bosses and NPCs

### Delivery

Merged PR #286 delivered:

- source evidence `canary-otbm-spawn-npc-evidence-v1`;
- bounded correlation report `canary-otbm-spawn-npc-validation-v1`;
- public facade `tools/ai-agent/otbm_spawn_npc.py`;
- implementation `tools/ai-agent/otbm_spawn_npc_validation.py`;
- CLI `tools/ai-agent/otbm_spawn_npc_tool.py`;
- source and validation JSON Schemas;
- `docs/ai-agent/OTBM_SPAWN_NPC_VALIDATION.md`;
- evidence-boundary ADR;
- dedicated workflow `.github/workflows/otbm-spawn-npc-validation.yml`.

Final feature head: `40ce55b791e11b2344a7c9662675ab4e3e15f31f`.  
Squash merge: `360d79ebad5802edd4d89e99d0f210ab19b36b60`.

### Active-datapack policy

- one explicit datapack root;
- explicit companion monster/NPC XML files only;
- globs and source paths confined below that root;
- no mixing of `data-otservbr-global` with `data-canary`;
- symlink/path escapes and DTD/entity XML fail closed;
- optional/custom/event XML is excluded unless its active load path is proven and selected explicitly.

### Runtime source semantics

The current C++ loaders resolve static positions as:

```text
x = centerx + child x
y = centery + child y
z = centerz
```

A differing child `z` is evidence of an ignored source attribute, not a different runtime floor. Radius is an inclusive square. NPC intervals outside `1..86400` seconds are rejected by the runtime. Monster missing/non-positive intervals use the configured default; intervals above one day remain rate-dependent until runtime rate scaling and final clamping.

Names resolve case-insensitively against active literal `Game.createMonsterType` / `Game.createNpcType` registrations. Missing and duplicate definitions remain explicit.

`rewardBoss` and runtime spawn-boss evidence are separate. `MonsterType::isBoss()` currently checks a non-empty Bosstiary class, so Phase 4 promotes only a literal non-empty Bosstiary `class` to `spawnBossLiteral`. It does not treat `rewardBoss = true` as runtime spawn-block boss proof.

### Dynamic creation policy

Only literal `Game.createMonster` / `Game.createNpc` names with literal `Position(x,y,z)` or literal position tables are resolved. Other calls remain `unresolved`; Lua is never executed. Exact literal static/dynamic overlaps and quest-source locations are reported.

Literal dynamic positions are bounded by the selected validation region. Calls without a statically resolved position cannot be assigned to a coordinate region and are reported separately as selected-active-datapack-global evidence.

### World Index and Phase 3 reuse

Bounded map validation requires:

1. Phase 4 source evidence;
2. the canonical `OTSWIDX1` World Index;
3. a non-truncated `canary-otbm-reachability-v1` report fully covering the selected region.

World Index proves tile existence. Phase 3 supplies strict/optimistic geometry. Phase 4 does not create another OTBM parser or pathfinder. Truncated Phase 3 tile diagnostics fail closed.

### Active global datapack scan

The final read-only scan of explicit `data-otservbr-global` companion files observed:

- 2 spawn XML files;
- 2,692 definition files and 2,688 resolved definitions;
- 52,903 spawn groups;
- 84,294 static placements: 83,286 monsters and 1,008 NPCs;
- 1,781 dynamic-source files;
- 461 dynamic creation calls: 151 literal and 310 unresolved;
- 318 findings: 2 errors and 316 warnings;
- 356 literal reward-boss definitions;
- 0 literal non-empty Bosstiary-class spawn-boss definitions in the selected sources.

The two errors are one underlying duplicate active NPC type:

- canonical `harlow` is defined by `npc/harlow.lua` and `npc/harlow_trade.lua`;
- static Harlow at `32836,31364,7` resolves to both definitions.

This is review evidence, not automatic authorization to delete or rewrite either NPC. One exact static/dynamic overlap was also recorded for `bone capsule` at `33485,32333,14`; nonliteral dynamic calls remain unresolved.

### Final validation evidence

Head `40ce55b791e11b2344a7c9662675ab4e3e15f31f`:

- OTBM Spawn and NPC Validation `29283580455`: success; job `86930499868` succeeded;
- Agent Task Ownership `29283580606`: success;
- AI Agent Tools `29283580631`: success;
- OTBM Map Tools `29283580582`: success;
- ready-state autofix.ci `29283719806`: success;
- ready-state repository CI `29283719990`: success;
- Fast Checks `86930966539`: success;
- Lua Tests `86930966552`: success;
- Linux Release `86931249627`: success;
- Required `86932589537`: success;
- review threads: zero.

The dedicated workflow ran 18 focused tests, Python compilation, schema validation, the real source scan, contract assertions and toolkit packaging. This is source/static evidence; it does not prove live gameplay.

### Private-map bounded smoke

The supplied private map was indexed with the existing native scanner and World Index:

```text
map SHA-256: a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2
WIDX SHA-256: 6c22cd26d4414aa094af1d00be7f62190a441e270ee7a478b55449bf92e55e7a
WIDX size: 842,280,592 bytes
tiles: 17,972,761
placements: 23,359,571
mechanic placements: 9,339
build wall time: 31.65 seconds
peak RSS: 417,512 KiB
```

Harlow region `32820,31350,7` through `32850,31380,7`:

- exact Harlow tile exists and is strict/optimistic walkable;
- Harlow remains `conflicting-definition` because both active Harlow source files resolve;
- nine other static placements in the region were confirmed;
- Phase 3 separately found seven indexed map teleports targeting `0,0,0` at `32822,31373,7`, `32830,31374,7`, `32830,31375,7`, `32834,31364,7`, `32850,31367,7`, `32850,31368,7` and `32850,31369,7`;
- these map-mechanic findings were not modified or treated as proof of intended behavior.

Bone Capsule region `33470,32320,14` through `33500,32350,14`:

- static `Bone Capsule` at `33485,32333,14` is confirmed;
- literal quest-side `Game.createMonster` evidence at the same position is confirmed;
- the target tile exists and is strict/optimistic walkable;
- the bounded Phase 3 report has no transition or mechanic errors.

The OTBM, WIDX, appearances binary, client assets and generated reports remain external and uncommitted.

## Real-map provenance retained from Phases 1–4

The current private map evidence is the Phase 4 build above. Earlier Phase 1/2 builds of the same map observed 32.72 seconds / 419,140 KiB and 40.21 seconds / 418,956 KiB respectively. A Phase 3 rebuild attempt exceeded its execution window and was abandoned without using a partial index.

No private map, WIDX, appearances binary or client asset package was committed.

## Factual rendering

Entrypoints:

- `tools/ai-agent/otbm_render_tool.py`;
- `tools/ai-agent/otbm_renderer.py`.

The renderer requires the real OTBM and compatible client assets, hashes its inputs and uses real appearance/sprite/stack/displacement data. One render is produced per floor. Visual context does not prove runtime behavior.

## Phase 5 — Storage dependency graph

Planned deliverables:

- inventory reads, writes, comparisons and increments;
- build explicit stage transitions;
- identify unreachable values and conflicting writers;
- separate player, account, KV and database namespaces;
- preserve dynamic expressions as unresolved;
- link transitions to NPC dialogue, Actions, MoveEvents, kills and rewards only where proven;
- never infer execution order from source proximity alone.

Phase 5 must consume Phase 2 quest evidence and Phase 4 creature/source evidence rather than create another source scanner.

## Phase 6 — Semantic OTBM diff

Planned deliverables:

- tiles and item stacks added/removed;
- AID/UID/house/teleport changes;
- walkability-relevant changes using Phase 3 semantics;
- affected handlers, quest and spawn/NPC evidence;
- bounded factual before/after/context renders;
- maps, indexes and generated images remain external artifacts.

## Phase 7 — Geometry and consistency audit

Planned deliverables:

- item without floor;
- broken or inconsistent walls/borders;
- invisible blockers;
- isolated/orphan tiles;
- suspicious duplicate ground;
- house/PZ continuity issues;
- exact positions, confidence levels and bounded factual renders.

Visual-style rules remain warnings unless backed by deterministic contracts.

## Phase 8 — Safe bounded OTBM patch writer

Phase 8 remains blocked until semantic-diff and geometry gates are complete. Every future approved operation must:

- work on a copy, never the source map in place;
- require exact expected previous state;
- pin source hash and format/version;
- use a bounded region and operation allowlist;
- create a machine-readable manifest;
- generate a semantic diff;
- reparse and fully validate the result;
- prove equality outside the intended change;
- render the affected region using real map/client assets;
- write atomically;
- provide backup and rollback instructions.

Existing older patch surfaces do not authorize production-map edits.

## Programme handoff

Phases 1–4 are merged and archived. The next bounded programme task is Phase 5, but it may start only from current `main` after a fresh PR/task ownership search.

Phase 5 must reuse:

1. `canary-quest-map-evidence-v1` and `canary-quest-map-validation-v1` from Phase 2;
2. `canary-otbm-reachability-v1` from Phase 3 where coordinate/geometry evidence is required;
3. `canary-otbm-spawn-npc-evidence-v1` and `canary-otbm-spawn-npc-validation-v1` from Phase 4.

Do not combine Phase 5 with Harlow cleanup, `0,0,0` teleport repair, semantic map diff, geometry audit or map writing. Those findings remain separate evidence-backed tasks.
