# OAM-007 — Item and World Runtime Foundation Revalidation

Status: implementing

## Bounded scope

Canonical modules, in dependency order:

1. `item-definitions`
2. `item-instances`
3. `world-map-runtime`

Out of scope: `world-zones`, `instances`, houses, spawns, raids, quests, offline OTBM tooling, datapack/map-content migration, protocol/client mutation and OAM-008 implementation.

## Exact task-start baselines

- governance/legacy: `blakinio/canary@c2e181f892ce2f094e887f1da5c6c7df207629c9`
- target: `blakinio/Otheryn@c547d8ad70ef1252624c255476e6cb83fa125e14`
- upstream evidence: `opentibiabr/canary@e0ac98e399d0f7e483f3668f57b78fcc45b6e53f`
- maintained client, only when applicable to runtime proof: `blakinio/otclient@2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`

## Canonical boundaries

### item-definitions

Static `Items` / `ItemType` registry, appearance/XML parsing, categories, abilities, market metadata, static attributes and lookup/reload lifecycle.

### item-instances

Runtime item factory/subtypes, instance attributes, clone/transform state and item serialization/unserialization boundaries. This does not claim database transaction atomicity.

### world-map-runtime

Runtime `Map`/`MapCache`/`Tile`/`Spectators`/`IOMap` boundary for map loading, tile materialization, spatial lookup, placement/movement, visibility and pathfinding. `world-zones` and `instances` remain separate downstream modules.

## Exact-blob matrix and disposition evidence

### item-definitions

- `src/items/items.cpp` and `src/items/items.hpp` are identical across target, legacy and upstream.
- `src/items/functions/item/item_parse.hpp` was identical at task start.
- `src/items/functions/item/item_parse.cpp` was target/upstream-identical, while legacy differed.
- The legacy difference has concrete provenance: merged Canary PR #81 (`a3406fe3d0cb1df32406c9e1292f43b5d90462a7`) fixed verified upstream issue #3584, where a newly placed magic field failed to affect a creature already standing on the target tile.
- The bounded fix registers the existing add-item-on-tile handler in addition to the existing step-in handler only for magic-field step-in definitions; non-field events remain unchanged.
- PR #81 provided a pure three-case policy test. Its unrelated manual healing-rune fix is excluded from OAM-007.
- Otheryn PR #23 implements only this item-definition adaptation on top of exact task-start target `c547d8ad70ef1252624c255476e6cb83fa125e14`.

Disposition candidate: `ADAPT`.

### item-instances

Checked principal runtime instance paths are content-identical across target, legacy and upstream:

- `src/items/item.cpp`
- `src/items/item.hpp`
- `src/items/functions/item/attribute.cpp`
- `src/items/functions/item/custom_attribute.cpp`

No target incompatibility or required legacy-only behavior was identified in the bounded runtime item instance boundary.

Disposition candidate: `REUSE`.

### world-map-runtime

Target and upstream are aligned across the checked principal runtime boundary, including:

- `src/io/iomap.cpp/.hpp`
- `src/map/spectators.cpp/.hpp`
- `src/map/map.cpp/.hpp`
- `src/items/tile.cpp/.hpp`
- `src/map/mapcache.cpp/.hpp`
- `src/map/utils/astarnodes.cpp`
- `src/map/utils/mapsector.cpp`
- `src/map/navigation_snapshot.cpp`

Legacy Canary diverges in `Map`, `Tile`, `MapCache` and `MapSector`, while the upstream-aligned target contains the separately built `navigation_snapshot` runtime source that is absent from the legacy tree. This is evidence of a different legacy runtime fork, not evidence that the target is missing a required fix. No focused failing target test or target requirement was found that justifies importing the legacy fork.

Disposition candidate: `REUSE`.

## Legacy-delta decision rule

A legacy-only delta enters OAM-007 only when all of the following are established:

1. a concrete target requirement falls inside one of the three canonical modules;
2. target/upstream behavior demonstrably fails that requirement or lacks the necessary invariant;
3. the legacy delta actually addresses that requirement;
4. focused tests and applicable runtime proof can be attached to the bounded target change.

PR #81 satisfies this rule for the magic-field item-definition behavior. The legacy Map/Tile/MapCache/MapSector fork does not currently satisfy it and is not migrated.

## Current target delivery

Otheryn draft PR #23, branch `fix/oam-007-magic-field-add-item-event`:

- adds the PR #81 policy helper and focused unit test;
- routes existing three-argument parser script registration through a bounded overload;
- preserves the four-argument weapon-registration path;
- registers `MOVE_EVENT_ADD_ITEM_ITEMTILE` only for `MOVE_EVENT_STEP_IN + magic field`;
- registers the new translation unit in both CMake and the existing Windows MSBuild bridge;
- does not modify Map/Tile/MapCache, datapacks, protocol or client code.

Exact-head CI and review gates are still pending before target merge.

## Working dispositions

| Module | Working disposition | Remaining gate |
|---|---|---|
| `item-definitions` | `ADAPT` | Otheryn PR #23 exact-head CI/review/merge plus exact final-target runtime proof |
| `item-instances` | `REUSE` | final bounded validation and governance gate |
| `world-map-runtime` | `REUSE` | final bounded validation and exact final-target runtime proof; no legacy fork port |

## Validation plan

- exact SHA/blob matrix over canonical registry paths;
- focused review of every legacy-only divergence that intersects the bounded modules;
- Otheryn PR #23 focused policy unit test and full exact-head target CI;
- exact controlled-server runtime/physical proof against the final Otheryn merge using the existing Universal Agent E2E platform;
- final Canary ownership/CI/review gates after recording exact target evidence.

## Safety and known limits

- No module is declared Real Tibia parity-complete.
- No claim of exhaustive map completeness, pathfinding correctness, tile-stack correctness or every movement edge case.
- No item price/value/appearance parity claim.
- Item serialization review does not change or strengthen OAM-004 SQL/KV atomicity claims.
- No legacy map/item code is copied wholesale.
- No second E2E orchestrator is created.
