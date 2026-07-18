# OTS OTBM tooling roadmap

> Repository: `blakinio/canary`  
> Coordination: `OTS-OTBM-VALIDATION`  
> Last refreshed: 2026-07-18  
> Evidence rule: static source/map evidence is not live gameplay proof

## Mission

Maintain one deterministic, evidence-based OTBM analysis stack that agents can reuse for quests, teleportation, reachability, NPCs, spawns, storage progression, semantic diffs, bounded geometry audits and—only after explicit safety gates—bounded map patching.

The stack reuses the existing native OTBM scanner, World Index, script resolver, Quest Map Validator, appearances parser, Phase 3 reachability, Phase 4 spawn/NPC evidence, Phase 5 storage evidence, Phase 6 semantic diff, Phase 7 geometry evidence and factual renderer. It must not create competing OTBM parsers/pathfinders/renderers or use AI-generated imagery as map evidence.

## Programme status

| Phase | Scope | State | Delivery |
|---:|---|---|---|
| 1 | Unified OTBM World Index | merged and archived | #219 / #223 |
| 2 | Quest Map Validator | merged and archived | #225 / #236 |
| 3 | Teleports, floor transitions and reachability | merged and archived | #274 / #277 |
| 4 | Spawns, bosses and NPCs | merged and archived | #286 / #290 |
| 5 | Storage dependency graph | merged and archived | #299 / #309 |
| 6 | Semantic OTBM diff and visual evidence | merged and archived | #311 / #315 |
| 7 | Geometry and consistency audit | merged and archived | #322 / #323 |
| 8 | Safe bounded OTBM patch writer | merged and archived | #325 / #333 |

Every numbered phase is a separate bounded task, branch and PR. Later structural materialization and finalization work extends the completed Phase 8 safety architecture without inventing a new numbered phase.

## Shared evidence boundaries

- Dynamic Lua is not executed.
- Dynamic expressions remain `unresolved`.
- `unresolved` is never promoted to handled without direct evidence.
- `map-only`, source-only and selected-scope findings are review candidates, not automatic proof of a defect.
- AID/UID presence, creature definitions, storage edges and handler resolution do not prove player reachability or successful execution.
- A source/map match can still be blocked by doors, quest state, walkability, direction, account state, protocol or runtime conditions.
- Green CI proves only the checks executed at that commit; it does not prove live gameplay.
- Coordinates, item IDs, AID, UID, storage values, spawn radii/times and transition offsets must never be invented.
- World Index, Quest Map Validator, reachability, spawn/NPC validation, storage dependency analysis, semantic diff and geometry audit are read-only.
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

Static storage evidence is an inventory. Phase 5 consumes the exact selected and hashed Phase 2 source set to derive conservative operation and transition evidence.

## Phase 3 — Teleports, floor transitions and reachability

### Delivery

Merged PR #274 delivered:

- report `canary-otbm-reachability-v1`;
- reviewed transition manifest `canary-otbm-transition-manifest-v1`;
- public facade and CLI `tools/ai-agent/otbm_reachability*.py`;
- focused evidence, transition, graph and analysis modules;
- schemas `OTBM_REACHABILITY.schema.json` and `OTBM_TRANSITIONS.schema.json`;
- documentation, evidence-boundary ADR and dedicated workflow.

Final feature head: `230237188cf8beed738e96923b6346948dc70d20`.  
Squash merge: `0a9afe2821e249a15c9402419483675a2842f5a8`.  
Lifecycle cleanup: #277, merge `5fe0b307f73d992e604dc490eb3da2a5cc67df21`.

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
- public facade, implementation and CLI `tools/ai-agent/otbm_spawn_npc*.py`;
- source and validation JSON Schemas;
- `docs/ai-agent/OTBM_SPAWN_NPC_VALIDATION.md`;
- evidence-boundary ADR;
- dedicated workflow `.github/workflows/otbm-spawn-npc-validation.yml`.

Final feature head: `40ce55b791e11b2344a7c9662675ab4e3e15f31f`.  
Squash merge: `360d79ebad5802edd4d89e99d0f210ab19b36b60`.  
Lifecycle cleanup: #290, merge `91d04b854495d827d7b896d5778dff3a701bdde5`.

### Active-datapack and runtime-source policy

- one explicit datapack root;
- explicit companion monster/NPC XML files only;
- globs and source paths confined below that root;
- no mixing of `data-otservbr-global` with `data-canary`;
- symlink/path escapes and DTD/entity XML fail closed;
- optional/custom/event XML is excluded unless its active load path is proven and selected explicitly.

The current C++ loaders resolve static positions as:

```text
x = centerx + child x
y = centery + child y
z = centerz
```

A differing child `z` is evidence of an ignored source attribute, not a different runtime floor. Radius is an inclusive square. NPC intervals outside `1..86400` seconds are rejected by the runtime. Monster missing/non-positive intervals use the configured default; intervals above one day remain rate-dependent until runtime rate scaling and final clamping.

Names resolve case-insensitively against active literal `Game.createMonsterType` / `Game.createNpcType` registrations. Missing and duplicate definitions remain explicit. `rewardBoss` and runtime spawn-boss evidence stay separate; a literal non-empty Bosstiary class is the only static `spawnBossLiteral` proof.

Only literal `Game.createMonster` / `Game.createNpc` names with literal positions are resolved. Other calls remain `unresolved`; Lua is never executed. Bounded map validation reuses World Index and a non-truncated Phase 3 report rather than creating another parser/pathfinder.

### Active global datapack scan

The final read-only scan observed:

- 2 spawn XML files;
- 2,692 definition files and 2,688 resolved definitions;
- 52,903 spawn groups;
- 84,294 static placements: 83,286 monsters and 1,008 NPCs;
- 1,781 dynamic-source files;
- 461 dynamic creation calls: 151 literal and 310 unresolved;
- 318 findings: 2 errors and 316 warnings;
- 356 literal reward-boss definitions;
- 0 literal non-empty Bosstiary-class spawn-boss definitions in selected sources.

The two errors are one underlying duplicate active NPC type: canonical `harlow` is defined by `npc/harlow.lua` and `npc/harlow_trade.lua`, so the static Harlow placement at `32836,31364,7` resolves ambiguously. This is review evidence, not automatic authorization to delete or rewrite either source.

One exact static/dynamic overlap was recorded for `bone capsule` at `33485,32333,14`; nonliteral dynamic calls remain unresolved.

### Final validation evidence

Head `40ce55b791e11b2344a7c9662675ab4e3e15f31f`:

- OTBM Spawn and NPC Validation `29283580455`: success;
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

## Phase 5 — Storage dependency graph

### Delivery

Merged PR #299 delivered:

- report `canary-otbm-storage-graph-v1`;
- public facade and focused internal modules `tools/ai-agent/otbm_storage_graph*.py`;
- CLI `tools/ai-agent/otbm_storage_graph_tool.py`;
- schema `docs/ai-agent/OTBM_STORAGE_GRAPH.schema.json`;
- documentation `docs/ai-agent/OTBM_STORAGE_GRAPH.md`;
- evidence-boundary ADR;
- dedicated workflow `.github/workflows/otbm-storage-graph.yml`.

Final feature head: `b1e19e179eb32199cc6e14e68becd9cc99c91fca`.  
Squash merge: `c7ecb321681d6c4dd80b23b380bd211062f52c90`.  
Lifecycle cleanup: #309, merge `f4e5371906d3b4a33229db2dce6b25d44fb813f0`.

### Source-selection and namespace policy

The required input is `canary-quest-map-evidence-v1`. Phase 5 reads only its selected source paths, confines them below the supplied repository root, rejects symlinks/path escapes and verifies each current SHA-256 against Phase 2 before reading it.

Optional correlation inputs are Phase 2 validation, Phase 3 reachability and Phase 4 spawn/NPC evidence/validation. They add handler, map, actor or geometry context but never prove runtime progression.

Namespaces remain separate:

- `player-storage`;
- `account-storage`;
- `player-kv`;
- `account-kv`;
- `global-storage`;
- `global-kv`;
- narrow literal `database` storage evidence.

### Transition proof rule

An explicit edge requires one enclosing source branch that proves exactly one same-key equality prerequisite and one literal, delete or exact same-key delta result.

The tool does not create exact edges from:

- inequalities;
- `else` negation;
- dynamic keys or values;
- nearby reads/writes;
- operations in different functions or files;
- unproven callback order.

Nested explicit branches may retain exact outer prerequisites. Source proximity and lexical/file order never imply runtime order.

### Conservative findings

- read without a selected writer means `external-or-unproven`, not broken;
- write without a selected read means `write-only-in-selected-scope`, not globally unused;
- a consumed prerequisite without a selected producer is informational selected-scope evidence;
- a numeric decrease is warned only for one proven same-key transition;
- writer conflict requires the same exact namespace/key/prerequisite with incompatible literal outputs;
- dynamic expressions remain `unresolved`.

Output is bounded and deterministic. Core graph limits fail closed; sampled findings/unresolved lists retain exact totals. Writes are atomic, existing output requires explicit overwrite and symlink outputs are rejected.

### Final workflow smoke

The dedicated-workflow smoke on The Beginning/Zirella selected source evidence produced:

```text
files: 1
operations: 23
nodes: 2
transitions: 0
unresolved: 0
findings: 1 informational write-only-in-selected-scope
ok: true
complete: true
sourceDigest: e995eeaa2916ffb6aee8f8867d97674d8812fe83b77f9f0e77e69b127bfa3d7c
```

This is a representative contract smoke, not a full-world quest-progression audit.

## Private-map provenance retained from Phases 1–4

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
- Phase 3 found seven indexed map teleports targeting `0,0,0` at `32822,31373,7`, `32830,31374,7`, `32830,31375,7`, `32834,31364,7`, `32850,31367,7`, `32850,31368,7` and `32850,31369,7`;
- none of these findings was modified or treated as proof of intended behavior.

Bone Capsule region `33470,32320,14` through `33500,32350,14`:

- static `Bone Capsule` at `33485,32333,14` is confirmed;
- literal quest-side dynamic creation at the same position is confirmed;
- the target tile exists and is strict/optimistic walkable;
- the bounded Phase 3 report has no transition or mechanic errors.

Earlier Phase 1/2 builds of the same map observed 32.72 seconds / 419,140 KiB and 40.21 seconds / 418,956 KiB. A Phase 3 rebuild attempt exceeded its execution window and was abandoned without using a partial index.

No private map, WIDX, appearances binary, client asset package or generated full report was committed.

## Factual rendering

Entrypoints:

- `tools/ai-agent/otbm_render_tool.py`;
- `tools/ai-agent/otbm_renderer.py`.

The renderer requires the real OTBM and compatible client assets, hashes its inputs and uses real appearance/sprite/stack/displacement data. One render is produced per floor. Visual context does not prove runtime behavior.

## Phase 6 — Semantic OTBM diff

### Delivery

Merged PR #311 delivered:

- report `canary-otbm-semantic-diff-v1`;
- factual render manifest `canary-otbm-semantic-diff-render-v1`;
- modular facade, analysis, types, render integration and CLI in `tools/ai-agent/otbm_semantic_diff*.py`;
- schema `docs/ai-agent/OTBM_SEMANTIC_DIFF.schema.json`;
- documentation `docs/ai-agent/OTBM_SEMANTIC_DIFF.md`;
- evidence-boundary ADR;
- 30 focused tests;
- dedicated workflow `.github/workflows/otbm-semantic-diff.yml`.

Final feature head: `5ae3141d6809b7a046b95922b304f905f7c636b2`.  
Squash merge: `4ab2dd2d72e3f55badfd45d76dd9f59d65c22f5a`.  
Lifecycle cleanup: #315, merge `e71630db609e03417ac61725fc5695dbe04d92b6`.

### Comparison contract

Phase 6 consumes two compatible canonical World Index binaries and manifests. It does not parse OTBM. Optional source maps are hash-verified only.

- tiles are matched only by exact `x,y,z`;
- item base identity is exact `(itemId,itemDepth,source)`;
- exact-multiset reorder is reported separately without false add/remove;
- other stack edits use a deterministic minimum edit script with fixed `replace`, `remove`, `add` tie order;
- AID, UID, house-door and teleport source/destination changes remain separate findings;
- full-index and inclusive bounded 3D scopes preserve exact counts while samples are bounded and explicitly truncated;
- stable finding IDs do not change when optional correlation is added.

No fuzzy item matching, neighboring-position inference or gameplay-intent inference is allowed.

### Walkability and correlation

The implementation calls the existing Phase 3 `otbm_reachability_transition._classify_tile` classifier. It does not copy the ground/static-blocker/conditional-blocker/unknown-appearance/strict/optimistic rules.

Optional format-validated Phase 2, script-resolution, Phase 3, Phase 4 and Phase 5 reports attach only exact selected-scope position/mechanic evidence. Absence from a supplied report never means global absence or non-use. `unresolved` is never promoted to handled.

### Factual visual evidence and safety

Before/after/context requests call `otbm_renderer.render_region` or record exact `otbm_render_tool.py` commands. No AI image generation, stylization, invented sprite or competing renderer is used. Private maps, indexes, assets and PNGs remain external.

Inputs and outputs are artifact-root confined and size-bounded. Direct symlinks and accidental overwrite are rejected. JSON writes are atomic. Corrupt/incompatible indexes or mismatched provenance fail closed. Maps are never modified.

### Final validation evidence

Final head `5ae3141d6809b7a046b95922b304f905f7c636b2`:

- OTBM Semantic Diff run `29316215755`: success;
- Validate semantic map evidence job `87030733453`: success;
- OTBM Map Tools run `29316215784`: success;
- Agent Task Ownership run `29316215791`: success;
- Agent Task Ownership job `87030730336`: success;
- autofix.ci run `29316215749`: success;
- AI Agent Tools run `29316215787`: success;
- repository CI run `29316215995`: success;
- Fast Checks job `87030777614`: success;
- Lua Tests job `87030777654`: success;
- Linux Release job `87031009052`: success;
- Required job `87032170628`: success;
- all 30 focused tests: success;
- review threads: zero;
- auto-merge: enabled and completed the squash merge.

The synthetic workflow validates the tested contract and safety checks; it is not real-map or gameplay proof. Only one private map was available historically, so no real two-map comparison was fabricated or produced.

## Phase 7 — Geometry and consistency audit

### Delivery

Merged PR #322 delivered:

- report `canary-otbm-geometry-audit-v1`;
- reviewed adjacency rules `canary-otbm-geometry-rules-v1`;
- factual render request manifest `canary-otbm-geometry-audit-render-v1`;
- facade, bounded analysis, types, render integration and CLI in `tools/ai-agent/otbm_geometry_audit*.py`;
- schemas `OTBM_GEOMETRY_AUDIT.schema.json` and `OTBM_GEOMETRY_RULES.schema.json`;
- documentation `docs/ai-agent/OTBM_GEOMETRY_AUDIT.md`;
- evidence-boundary ADR;
- 21 focused tests;
- dedicated workflow `.github/workflows/otbm-geometry-audit.yml`.

Final feature head: `67a7774a2cfba98613ea415802063218c951afba`.  
Squash merge: `0d1eb94c8e8e3033d95fd73f56711b830624540f`.  
Lifecycle cleanup: #323, merge `9b04ab3ef3dfbc9440274d63e15e6102c5501d85`.

### Bounded evidence contract

Phase 7 requires one explicit inclusive 3D region containing at most 1,000,000 coordinates. It consumes the canonical World Index and its exact hash/size/OTBM/summary manifest, plus compatible appearances evidence. The implementation uses World Index area postings to enumerate only the selected scope and calls the existing Phase 3 tile classifier.

The report preserves exact positions and classifies:

- tile/item evidence without confirmed ground;
- multiple confirmed ground placements as review warnings, not automatic defects;
- unknown appearances;
- small cardinal tile components with scope-boundary uncertainty;
- disconnected exact house-ID components;
- mixed PZ state inside one house component;
- isolated PZ tiles and PZ-enclosed gaps;
- low-confidence invisible-blocker candidates;
- reviewed wall/border adjacency mismatches.

### Evidence boundaries

- Only verified OTBM protection-zone bit `0x0001` is interpreted; every other raw tile flag remains opaque.
- Wall and border findings require an explicit reviewed rule manifest. Names, sprite shape, proximity and visual memory do not create rules.
- An invisible-blocker candidate requires direct `unpassable` appearance evidence and absence of any nonzero decoded sprite ID. Sprite pixels and runtime state are not inspected, so confidence remains low.
- Small or disconnected components are review candidates because scripts, reviewed floor transitions and runtime teleportation may provide connectivity.
- Factual render requests use the existing renderer and real external map/client assets only. No map image is generated by AI.
- Maps, indexes, appearances binaries, client assets, reports and renders remain external artifacts and are never modified by the audit.

### Final validation evidence

Final feature head `67a7774a2cfba98613ea415802063218c951afba`:

- all 21 focused tests: success;
- Python compilation: success;
- both schema syntax checks and representative `jsonschema`: success;
- deterministic synthetic map/index/report and reviewed-rules validation: success;
- forbidden generated-artifact publication check: success;
- OTBM Geometry Audit: success;
- Agent Task Ownership: success;
- OTBM Map Tools: success;
- AI Agent Tools: success;
- repository ready-state CI run `29321550957`: success;
- Fast Checks job `87047811522`: success;
- Lua Tests job `87047811551`: success;
- Linux Release job `87048054021`: success;
- Required job `87049366021`: success;
- review threads: zero;
- auto-merge completed the feature squash merge.

The first dedicated runs exposed only the known synthetic fixture `maxItemDepth=-1` versus binary `0` edge for maps without node-items. Fixtures were repaired by retaining one neutral known nested item; no production validation was weakened. Original draft #320 was closed without merge after its stale merge-base produced unrelated shared-document diff noise; clean replacement #322 started from current main and delivered the exact reviewed 15-file scope.

## Phase 8 — Safe bounded OTBM patch writer

### Delivery

Phase 8 is complete, merged, validated and archived.

Bounded existing-attribute patcher:

- feature PR: #325;
- final reviewed feature head: `132fa913bbd1607928d9bd70a080c6b27f5ce669`;
- squash merge: `9350f2fb7420f9af2ecf79ea7085ca4e094a3891`;
- lifecycle PR: #333;
- lifecycle squash merge: `85c706ce79baa63e9cd4d8d2622b026c6a4826a7`.

Public contracts:

- `canary-otbm-patch-anchors-v1`;
- `canary-otbm-bounded-patch-plan-v1`;
- `canary-otbm-bounded-patch-result-v1`.

Phase 8 intentionally supports only already-existing fixed-width mechanic attributes:

- action ID;
- unique ID;
- house-door ID;
- teleport destination.

Every reviewed operation must pin exact source identity and expected prior state, operate only on a distinct copy, preserve file length and escape framing, prove byte equality outside declared payload offsets, fully reparse the candidate, rebuild canonical World Index evidence, require an exact bounded Semantic OTBM Diff, and retain rollback evidence. Factual render requests use the existing renderer and real map/client assets only.

Phase 8 does not insert or remove attributes, items, tiles or nodes; change item IDs, counts, stack order, tile type, ground, geometry, house ID or tile flags; serialize a full map; write a source map in place; execute a production-map deployment; or treat structural success as proof of player intent or gameplay correctness.

The durable completion handoff is `docs/agents/OTBM_PHASE8_FINAL_HANDOFF.md`.

## Post-Phase-8 bounded repair and materialization extensions

After Phase 8 completed, later bounded tasks extended the existing safety architecture without creating a new numbered roadmap phase or a generic/full-map serializer:

- #406 — read-only real-map repair preflight over existing item/mechanic audit, Phase 8 patch anchors and script resolution;
- #419 — static Map Quality Gate over compatible Geometry, Reachability and Script Resolution evidence;
- #422 — repair sandbox verifier that reuses the existing Phase 8 patcher on a distinct artifact copy;
- #424 — read-only donor/region merge planner with explicit translation and `writerReady: false`;
- #426 — approved zero-translation complete `OTBM_TILE_AREA` materialization;
- #456 — canonical repair/materialization finalization pipeline over the existing attribute and TILE_AREA paths;
- #467 — bounded same-coordinate complete raw tile replacement;
- #482 — bounded same-coordinate complete raw tile insertion into an already-existing parent `TILE_AREA`;
- #488 — bounded complete raw tile deletion while retaining the parent `TILE_AREA`;
- #498 — bounded same-coordinate complete `OTBM_TILE ↔ OTBM_HOUSETILE` donor-subtree conversion;
- #506 — integration of replacement, insertion, deletion and tile-type conversion into the canonical repair/materialization pipeline; lifecycle cleanup #508 is merged.

The canonical finalization pipeline now supports exactly one mutation mode per run: `attribute`, `tile-area`, `tile-replacement`, `tile-insertion`, `tile-deletion`, or `tile-type-conversion`. It reuses existing materializers and Map Quality evidence and publishes only a verified create-new final map. It does not add a second parser, scanner, World Index, Semantic Diff, script resolver, renderer, E2E runner or deployment path.

Still explicitly out of scope are non-zero coordinate translation in the finalizer, automatic teleport-destination rewriting caused by translation, partial `TILE_AREA` import, arbitrary independent item insertion/deletion or stack reordering, generic OTBM node serialization, a full-map serializer, in-place writes and direct production-map execution.

## Programme handoff

Phases 1–8 are merged and archived. The bounded Phase 8 writer itself has no remaining implementation work, and the later bounded structural materializers plus canonical repair/materialization integration through PR #506 are merged.

Do not reopen historical OTBM PRs or continue their branches. Future real-map repair work must start as a new bounded task from then-current `main`, reuse the existing item/mechanic audit and script resolution first, prove the exact target and expected old state, use the already-merged reviewed patch/materialization contracts, create a new copy only, and require full reparse, World Index, Semantic Diff, confinement evidence and rollback instructions. Physical-client E2E remains a separate proof layer when runtime behavior must be demonstrated.

Do not combine future real-map repair with Harlow cleanup, `0,0,0` teleport repair, Bone Capsule repair, Targuna donor-map remediation or unrelated gameplay fixes unless a separately reviewed task explicitly owns that scope. Non-zero translation, generic serialization and broader item-stack editing remain separate architecture boundaries rather than unfinished acceptance criteria for the completed roadmap.
