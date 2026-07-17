# OAM-007 — Item and World Runtime Foundation Revalidation

Status: investigating

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

## Principal exact-blob matrix — current findings

| Path | Otheryn vs upstream | Legacy relation | Interpretation |
|---|---|---|---|
| `src/items/items.cpp` | identical | identical | strong reusable core registry evidence |
| `src/items/item.cpp` | identical | identical | strong reusable runtime item core evidence |
| `src/io/iomap.cpp` | identical | identical | reusable runtime map loader core evidence |
| `src/map/spectators.cpp` | identical | identical | reusable spectator lookup core evidence |
| `src/map/map.cpp` | identical | legacy differs | legacy delta requires necessity/provenance proof; no automatic port |
| `src/map/map.hpp` | identical | legacy differs | same bounded legacy map-runtime divergence |
| `src/items/tile.cpp` | identical | legacy differs | legacy tile delta requires proof before target adaptation |
| `src/items/tile.hpp` | identical | legacy differs | same bounded legacy tile divergence |
| `src/map/mapcache.cpp` | identical | legacy differs | legacy cache implementation delta requires proof |
| `src/map/mapcache.hpp` | identical | identical | public cache header remains aligned |
| `src/items/functions/item/item_parse.cpp` | identical | legacy differs | legacy parser delta requires proof; static registry core itself is aligned |

Exact remaining attribute/parser/header/util paths are still being checked before final disposition.

## Legacy-delta decision rule

Otheryn and the pinned upstream are aligned across every principal path checked so far. Therefore a legacy-only delta is not a target defect by definition. It may enter OAM-007 only when all of the following are established:

1. a concrete target requirement falls inside one of the three canonical modules;
2. target/upstream behavior demonstrably fails that requirement or lacks the necessary invariant;
3. the legacy delta actually addresses that requirement;
4. focused tests and applicable runtime proof can be attached to the bounded target change.

Absent that evidence, preserve the upstream-aligned target and record the legacy delta as non-migrated evidence.

## Working dispositions

| Module | Working disposition | Gate still open |
|---|---|---|
| `item-definitions` | `REUSE` candidate | complete parser/header matrix and review legacy parser delta necessity |
| `item-instances` | `REUSE` candidate | complete attribute/custom-attribute/serialization matrix |
| `world-map-runtime` | `REUSE` candidate | complete remaining map runtime matrix and establish that legacy Map/Tile/MapCache deltas are not required target fixes |

## Validation plan

- exact SHA/blob matrix over canonical registry paths;
- focused review of every legacy-only divergence that intersects the bounded modules;
- target build/test evidence at exact target head if no code changes are required;
- use existing Universal Agent E2E/runtime capabilities for a bounded exact-target proof when the scenario can exercise the foundation without inventing unverified fixtures;
- if adaptation becomes necessary, implement one bounded Otheryn PR and require exact-head CI before governance completion.

## Safety and known limits

- No module is declared Real Tibia parity-complete.
- No claim of exhaustive map completeness, pathfinding correctness, tile-stack correctness or every movement edge case.
- No item price/value/appearance parity claim.
- Item serialization review does not change or strengthen OAM-004 SQL/KV atomicity claims.
- No legacy map/item code is copied wholesale.
- No second E2E orchestrator is created.
