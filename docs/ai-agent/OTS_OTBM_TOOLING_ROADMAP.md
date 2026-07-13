# OTS OTBM tooling roadmap

## Goal

Build one deterministic, evidence-based map-analysis stack that agents can reuse for quests, NPCs, spawns, teleportation, geometry, regression review and—only after strict safety gates—bounded map patching.

This roadmap extends existing Canary tooling. It does not authorize committing or modifying `.otbm`, `items.otb`, appearances binaries, sprite sheets, generated reports or production datapacks.

## Existing foundation

The project already has:

- a native OTBM item/mechanic scan and item audit;
- a script-resolution audit for `actionId`, `uniqueId`, item-ID and position handlers;
- a factual region renderer using the supplied client assets;
- provenance, hash and deterministic fallback conventions from the HD rendering pipeline;
- the active Phase 1 implementation in PR #211: a deterministic binary `.widx` cache, JSON provenance manifest, memory-mapped query library and CLI.

New phases must reuse those contracts instead of creating competing parsers.

## Delivery model

The programme is intentionally split into independently testable PRs. Each phase must be merged and documented before downstream phases depend on it.

### Phase 1 — Unified OTBM World Index — implemented in PR #211, validating

Delivered interfaces:

- `OTSWIDX1` deterministic binary postings index;
- `canary-otbm-world-index-v1` JSON provenance/summary manifest;
- `canary-otbm-world-query-v1` bounded query responses;
- indexes for position, region, item ID, action ID, unique ID, house door and teleport destination;
- pagination with exact total counts;
- source, scanner and index SHA-256 provenance;
- reusable memory-mapped query library and CLI;
- focused tests, schema and dedicated CI.

The implementation extends the existing native scanner instead of creating a second OTBM parser. Full-world generated `.widx` files remain local/workflow artifacts and are never committed.

Safety boundary: read-only; no map, item or asset write path.

### Phase 2 — Quest Map Validator

Deliverables:

- correlate quest Lua/XML/NPC references with world-index placements and script-resolution evidence;
- classify each requirement as `confirmed`, `map-only`, `script-only`, `unresolved` or `conflicting`;
- report storages, item IDs, AID/UID, positions, reward containers, doors, levers and teleport requirements;
- produce machine-readable per-quest evidence bundles.

Safety boundary: static evidence is not runtime proof; dynamic expressions remain unresolved.

### Phase 3 — Teleport, stairs and walkability validation

Deliverables:

- validate source and destination tiles;
- detect destinations without floor, destinations blocked by map geometry, invalid floor transitions, loops and dead ends;
- bounded pathfinding for explicitly selected regions and start/goal pairs;
- distinguish definite geometry failures from unknown engine/script conditions.

Safety boundary: no assumption that every blocking item is permanent; door, quest and dynamic states must be represented explicitly.

### Phase 4 — Spawn and NPC index

Deliverables:

- parse active spawn/NPC definitions and dynamic `Game.createMonster`/NPC placement references where statically resolvable;
- validate spawn centers and NPC positions against indexed map tiles;
- detect missing creature/NPC definitions, blocked positions, suspicious radius overlap and quest boss gaps;
- preserve active/inactive datapack separation.

Safety boundary: never invent missing creature names, positions or spawn times.

### Phase 5 — Storage dependency graph

Deliverables:

- inventory storage reads, writes, comparisons and transitions in active Lua/NPC scripts;
- build per-quest graphs linking NPC dialogue, Actions, MoveEvents, kills, rewards and completion;
- detect read-only storages, write-only storages, unreachable stages, backwards transitions and conflicting writers;
- keep account/player/KV/database state namespaces separate.

Safety boundary: dynamic storage calculations remain explicit unknowns.

### Phase 6 — Semantic OTBM diff and visual evidence

Deliverables:

- compare two world indexes/manifests without requiring binary map files in Git;
- report added/removed/changed tiles, item stacks, AID/UID, teleport destinations, house flags and walkability-relevant changes;
- determine affected script registrations and quest evidence;
- render bounded before/after/difference views from local approved artifacts.

Safety boundary: generated indexes, images and reports remain workflow/local artifacts, not repository data.

### Phase 7 — Geometry and consistency audit

Deliverables:

- detect item-without-floor, isolated tiles, suspicious duplicate ground, broken wall/border patterns, invalid house transitions and hidden blocking items;
- use conservative confidence levels and configurable rule packs;
- produce exact positions and bounded renders for review.

Safety boundary: visual style rules are warnings unless backed by deterministic item/flag contracts.

### Phase 8 — Safe bounded OTBM patch writer

This phase stays disabled until all prerequisites pass.

Mandatory prerequisites:

- explicit map-format/version detection;
- verified backup/copy-only operation;
- exact expected-old-state preconditions;
- bounded region and operation allowlist;
- no unknown attribute tails in the target nodes;
- round-trip parse equality outside the intended change;
- semantic diff and factual before/after render;
- atomic output write and rollback instructions;
- focused fixtures plus real-map dry-run evidence.

Allowed initial operations should be narrow attribute edits such as setting an existing item `actionId`, `uniqueId` or teleport destination. Adding/removing tiles or arbitrary item stacks requires a later safety review.

## CI integration

The final CI stack should select checks by changed paths and available local artifacts:

- source-only PRs: validators and synthetic fixtures;
- map-change review workflows: externally supplied map/index artifacts, semantic diff and bounded renders;
- no private or proprietary map/client binary is committed to the repository or uploaded without explicit retention and access review.

Blocking findings should initially be limited to structural corruption, provenance mismatch, duplicate/conflicting identifiers introduced by the change, invalid accepted outputs and explicit new teleport-to-empty-tile defects. Existing unresolved findings remain reported without silently becoming merge blockers.

## Cross-repository boundary

Phases 1–7 are Canary offline tooling and do not require OTClient changes. Renderer output can be reviewed with the maintained client assets, but no protocol contract changes.

Direct editor integration with Remere's Map Editor or client-editor is a future separate task. Any write/plugin integration must have its own repository authorization and cross-repository coordination record.

## Programme success criteria

The roadmap is complete when an agent can select a quest or region and obtain one reproducible evidence bundle containing:

- exact map placements and identifiers;
- active script/NPC/spawn/storage relationships;
- teleport and reachability findings;
- semantic changes from a baseline;
- factual visual context;
- explicit confidence and unresolved cases;
- a safe patch plan or a proven no-change conclusion.
