# OTS OTBM tooling roadmap

> Repository: `blakinio/canary`  
> Coordination: `OTS-OTBM-VALIDATION`  
> Last refreshed: 2026-07-13  
> Evidence rule: static source/map evidence is not live gameplay proof

## Mission

Maintain one deterministic, evidence-based OTBM analysis stack that agents can reuse for quests, teleportation, reachability, NPCs, spawns, storage progression, semantic diffs and—only after explicit safety gates—bounded map patching.

The stack reuses the existing native OTBM scanner, World Index, script resolver, Quest Map Validator, appearances parser and factual renderer. It must not create competing parsers or use AI-generated imagery as map evidence.

## Programme status

| Phase | Scope | State | Delivery |
|---:|---|---|---|
| 1 | Unified OTBM World Index | merged and archived | #219 / #223 |
| 2 | Quest Map Validator | merged and archived | #225 / #236 |
| 3 | Teleports, floor transitions and reachability | merged and archived | #274 / lifecycle cleanup |
| 4 | Spawns, bosses and NPCs | not started | separate future task |
| 5 | Storage dependency graph | not started | separate future task |
| 6 | Semantic OTBM diff and visual evidence | not started | separate future task |
| 7 | Geometry and consistency audit | not started | separate future task |
| 8 | Safe bounded OTBM patch writer | blocked by Phases 6–7 safety gates | separate future task |

Every phase is a separate bounded task, branch and PR. Do not combine phases.

## Shared evidence boundaries

- Dynamic Lua is not executed.
- Dynamic expressions remain `unresolved`.
- `unresolved` is never promoted to handled without direct evidence.
- `map-only` is a review candidate, not automatic proof of a defect.
- AID/UID presence and handler resolution do not prove player reachability or successful execution.
- A source/map match can still be blocked by doors, quest state, walkability, direction, account state, protocol or runtime conditions.
- Green CI proves only the checks executed at that commit; it does not prove live gameplay.
- Coordinates, item IDs, AID, UID, storage values and transition offsets must never be invented.
- The World Index, Quest Map Validator and reachability validator are read-only.
- `.otbm`, `.widx`, `items.otb`, appearances binaries, client packages, generated large reports and renders stay outside Git.
- Map images must come from the real OTBM, compatible client assets and the factual renderer.
- Do not use AI image generation to visualize or modify the map.
- Upstream `opentibiabr/*` repositories are read-only for this programme.

## Phase 1 — Unified OTBM World Index

### Contract and entrypoints

- binary magic `OTSWIDX1`, version `1`;
- provenance manifest `canary-otbm-world-index-v1`;
- query response `canary-otbm-world-query-v1`;
- native build report `canary-otbm-world-index-build-v1`;
- `tools/ai-agent/otbm_item_audit_scan.cpp`;
- `tools/ai-agent/otbm_world_index.py`;
- `tools/ai-agent/otbm_world_index_tool.py`.

The existing native scanner is reused. No second OTBM parser exists.

### Indexed dimensions

- exact tile positions and stacks;
- item IDs;
- action IDs;
- unique IDs;
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

### Example

```bash
python tools/ai-agent/otbm_world_index_tool.py build \
  /path/to/world.otbm \
  --scanner /tmp/otbm_item_audit_scan \
  --output /path/to/world.widx \
  --manifest /path/to/world.widx.json

python tools/ai-agent/otbm_world_index_tool.py action world.widx 50999 --limit 20
python tools/ai-agent/otbm_world_index_tool.py position world.widx 32062,32271,7
```

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
- bounded samples and exact counts;
- atomic output and symlink rejection.

Storage facts are inventory only until Phase 5. A missing static item is not automatically `script-only` because rewards and dynamic creation may not require an OTBM placement.

### Example

```bash
PYTHONPATH=tools/ai-agent \
python tools/ai-agent/quest_map_validation_tool.py scan \
  --repository-root . \
  --source-root data-otservbr-global \
  --include 'data-otservbr-global/scripts/quests/the_beginning/**/*.lua' \
  --output /tmp/QUEST_MAP_EVIDENCE.json

PYTHONPATH=tools/ai-agent \
python tools/ai-agent/quest_map_validation_tool.py validate \
  /tmp/QUEST_MAP_EVIDENCE.json \
  --world-index /path/to/world.widx \
  --script-resolution /path/to/OTBM_SCRIPT_RESOLUTION.json \
  --region-from 32055,32265,7 \
  --region-to 32090,32295,7 \
  --output /tmp/QUEST_MAP_VALIDATION.json
```

## Phase 3 — Teleports, floor transitions and reachability

### Delivery

Merged PR #274 delivered:

- report `canary-otbm-reachability-v1`;
- reviewed transition manifest `canary-otbm-transition-manifest-v1`;
- CLI `tools/ai-agent/otbm_reachability_tool.py`;
- public facade `tools/ai-agent/otbm_reachability.py`;
- focused modules for evidence types, transition validation, graph traversal and report orchestration;
- schemas:
  - `docs/ai-agent/OTBM_REACHABILITY.schema.json`;
  - `docs/ai-agent/OTBM_TRANSITIONS.schema.json`;
- documentation `docs/ai-agent/OTBM_REACHABILITY.md`;
- evidence-boundary ADR;
- dedicated workflow `.github/workflows/otbm-reachability.yml`.

Final feature head: `230237188cf8beed738e96923b6346948dc70d20`.  
Squash merge: `0a9afe2821e249a15c9402419483675a2842f5a8`.

### Geometry policy

The validator consumes actual object appearance flags:

- `bank` confirms ground;
- `unpassable` confirms blocking geometry;
- `avoid` is reported but remains geometrically traversable;
- `usable`, `multiUse`, `forceUse`, AID/UID and house-door evidence identify potentially conditional barriers.

It emits two graphs:

- **strict** — confirmed ground, no static blocker, no conditional blocker and no unknown appearance;
- **optimistic** — confirmed ground and no static blocker, while conditional/unknown runtime state remains explicit.

Default movement is four-directional. Optional diagonals require both orthogonal corner tiles, so corner cutting is impossible.

### Transition policy

Indexed teleport destinations are consumed automatically and checked for:

- source/destination tile existence;
- confirmed ground;
- static/conditional blockers;
- optional script-resolution status;
- one-way edges;
- dead-end destinations;
- transition cycles.

Stairs, ladders, holes, rope spots and other non-teleport floor changes are never guessed from sprites, item names or visual memory. They require a reviewed manifest with an explicit destination or delta and optional expected source item IDs.

### Reachability classifications

Routes:

- `confirmed` — strict path exists;
- `conditional` — only optimistic path exists;
- `unreachable` — neither path exists inside the explicit region;
- `invalid` — malformed or out-of-region request.

Map mechanics reachable from supplied origins are classified as `confirmed`, `conditional` or `unreachable`.

This is bounded geometry evidence, not gameplay proof. It does not model current quest/storage/account state, creatures, players, movable blockers or physical-client behavior.

### Bounds and output safety

- region coordinate volume: 1,000,000;
- distinct origins/route starts: 16;
- routes: 32;
- transitions: 10,000;
- sample output: 10,000;
- path sample: 10,000 positions;
- exact summary counts retained when samples truncate;
- atomic output;
- existing output requires explicit overwrite;
- symlink output targets rejected;
- map and index remain unchanged.

### Example

```bash
PYTHONPATH=tools/ai-agent \
python tools/ai-agent/otbm_reachability_tool.py analyze \
  /path/to/world.widx \
  --world-manifest /path/to/world.widx.json \
  --appearances /path/to/appearances.dat \
  --script-resolution /path/to/OTBM_SCRIPT_RESOLUTION.json \
  --transitions /path/to/OTBM_TRANSITIONS.json \
  --from 32055,32265,7 \
  --to 32090,32295,8 \
  --origin 32062,32271,7 \
  --route 32062,32271,7:32070,32280,8 \
  --output /tmp/OTBM_REACHABILITY.json
```

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

The dedicated workflow compiled the existing native scanner, ran the focused suite including real World Index fixture integration, compiled the Python modules, validated schema syntax and uploaded a local toolkit without maps or client assets.

Runtime/database/C++ test execution was skipped by repository path scope, so this evidence does not claim live gameplay.

## Real-map provenance retained from Phases 1–2

The validated private local map used by the earlier phases:

```text
map SHA-256: a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2
source size: 184,776,037 bytes
index size: 842,280,592 bytes
tiles: 17,972,761
placements: 23,359,571
used item IDs: 23,852
mechanic placements: 9,339
unknown attribute tails: 0
```

Observed Phase 1 build:

```text
wall time: 32.72 s
peak RSS: 419,140 KiB
canonical areas: 1,171
raw OTBM tile-area nodes: 1,175,983
maximum item depth: 2
```

A later Phase 2 rebuild of the same map observed 40.21 s and 418,956 KiB peak RSS. These are separate measured runs, not conflicting format values.

A Phase 3 attempt to rebuild the complete private-map WIDX exceeded the available execution window and was aborted. No partial output was used as evidence. No private map, WIDX or asset package was committed.

## Factual rendering

Entrypoints:

- `tools/ai-agent/otbm_render_tool.py`;
- `tools/ai-agent/otbm_renderer.py`.

The renderer requires the real OTBM and compatible client assets, hashes its inputs, uses real appearance/sprite/stack/displacement data and emits `canary-otbm-render-report-v1`.

Run one render per floor. A render provides visual context only; it does not prove runtime behavior.

## Phase 4 — Spawns, bosses and NPCs

Planned deliverables:

- parse active companion XML/spawn/NPC definitions without mixing inactive datapacks;
- validate spawn/NPC centers against indexed tiles and Phase 3 walkability evidence;
- resolve monster/NPC definitions;
- detect blocked/missing positions and suspicious radius relationships;
- record statically resolvable dynamic `Game.createMonster`/NPC placement evidence;
- compare quest expectations with static and dynamic creation;
- never invent names, positions, radii or spawn times.

Phase 4 must consume `canary-otbm-reachability-v1` rather than create another geometry engine.

## Phase 5 — Storage dependency graph

Planned deliverables:

- inventory reads, writes, comparisons and increments;
- build explicit stage transitions;
- identify unreachable values and conflicting writers;
- separate player, account, KV and database namespaces;
- preserve dynamic expressions as unresolved;
- link transitions to NPC dialogue, Actions, MoveEvents, kills and rewards only where proven;
- never infer execution order from source proximity alone.

## Phase 6 — Semantic OTBM diff

Planned deliverables:

- tiles and item stacks added/removed;
- AID/UID/house/teleport changes;
- walkability-relevant changes using Phase 3 semantics;
- affected script handlers and quest evidence;
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

Phase 8 remains blocked until semantic-diff and geometry gates are complete.

Every approved future operation must:

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

Phase 3 is complete. The next programme agent may begin Phase 4 only from current `main` after a fresh open-PR and structured ownership check.

The Phase 4 implementation must:

1. reuse the World Index, Quest Map Validator and `canary-otbm-reachability-v1`;
2. keep active and inactive datapacks separate;
3. avoid another parser/pathfinder/renderer;
4. keep maps, indexes, client assets and generated reports outside Git;
5. preserve runtime/dynamic uncertainty instead of guessing.

Gameplay-specific quest repairs remain separate from this tooling programme and must follow their own evidence/task records.
