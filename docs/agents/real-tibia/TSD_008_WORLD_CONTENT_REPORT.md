# TSD-008 — World Content Decomposition

> Task-start main: `350739e5df12db5f3c749540a36bb7c3922cc5ee`.
> Inventory only; no map, movement, travel, instance, runtime or parity claim.

## Result

Registry grows from **49** to **52** records. Existing records remain unchanged.

Added only:

- `world-map-runtime`;
- `world-zones`;
- `instances`.

Preserved unchanged:

- `quests`;
- `npcs`;
- `houses`;
- `otbm-tooling`;
- `raids`;
- `spawns`;
- `containers`;
- `item-instances`;
- `world-persistence`;
- `physical-client-e2e`.

## Evidence inventory

### World map runtime

`Map`, `MapCache`, `Tile`, `Spectators`, map utilities and `IOMap` form one runtime boundary for loading map data, materializing tiles, spatial lookup, stack/cylinder queries, creature placement/movement, visibility, sight and pathfinding. Towns and waypoints are embedded registries inside loaded map state rather than independent lifecycles.

This runtime boundary is distinct from `otbm-tooling`, which performs read-only offline analysis, and from `world-persistence`, which owns save/serialization surfaces.

### World zones

`Zone` owns name/id/position registries, static XML and dynamic zones, area indexing, membership caches, refresh, removal destinations and bulk creature/item removal. It depends on runtime positions/tiles but has a separate registry and membership lifecycle.

### Instances

`InstanceManager` and its configured region pool own Creating → Active → Closing → Destroyed transitions, unique region reservation, stable creature-id ownership, fail-closed cross-instance relations, cleanup callbacks, region quarantine and expiration. The arena service is a bounded consumer inside the same lifecycle rather than a separate module.

## Candidate decisions

| Candidate | Decision | Reason |
|---|---|---|
| `world-map-runtime` | `ADD_NOW` | stable Map/Tile/IOMap runtime and spatial state boundary |
| `world-zones` | `ADD_NOW` | independent zone registry, indexing and membership lifecycle |
| `instances` | `ADD_NOW` | independent region allocation, state and creature-isolation lifecycle |
| `map-loading` | `MERGE_WITH_ANOTHER_MODULE` | IOMap lifecycle is inseparable from runtime map state |
| `tiles` | `MERGE_WITH_ANOTHER_MODULE` | primary runtime-map storage/cylinder implementation |
| `movement` | `MERGE_WITH_ANOTHER_MODULE` | Map/Tile/Game call sites share one runtime movement boundary |
| `pathfinding` | `MERGE_WITH_ANOTHER_MODULE` | runtime-map capability using MapCache/Tile/A* utilities |
| `visibility-spectators` | `MERGE_WITH_ANOTHER_MODULE` | runtime-map spatial capability |
| `towns` | `MERGE_WITH_ANOTHER_MODULE` | small registry embedded in Map load state |
| `waypoints` | `MERGE_WITH_ANOTHER_MODULE` | Map-owned position metadata |
| `teleports` | `DEFER` | item/tile/Lua call sites lack one independent current root |
| `floor-transitions` | `DEFER` | map/data/script findings rather than one lifecycle root |
| `npc-travel` | `ALREADY_COVERED` | NPC and quest script behavior remains in `npcs`/`quests` |
| `boats-carpet-travel` | `ALREADY_COVERED` | content entries inside NPC/quest boundaries |
| `houses` | `ALREADY_COVERED` | preserve existing house boundary |
| `quests` | `ALREADY_COVERED` | preserve existing quest/world semantics boundary |
| `spawns` | `ALREADY_COVERED` | preserve placement/dynamic creation boundary |
| `raids` | `ALREADY_COVERED` | preserve scheduling/event boundary |
| `otbm-runtime-loader` | `MERGE_WITH_ANOTHER_MODULE` | runtime IOMap inside `world-map-runtime` |
| `otbm-analysis` | `ALREADY_COVERED` | preserve `otbm-tooling` and existing canonical parser/index pipeline |
| `world-save` | `ALREADY_COVERED` | preserve `world-persistence` |
| `instance-arena` | `MERGE_WITH_ANOTHER_MODULE` | bounded consumer inside `instances` |
| individual towns/zones/maps/travel routes | `REJECT_AS_TOO_GRANULAR` | data/content entries, not durable modules |

## Dependencies

- `world-map-runtime` depends on `item-definitions` and `item-instances`.
- `world-zones` depends on `world-map-runtime`.
- `instances` depends on `world-map-runtime`.

All records begin at lifecycle/implementation/evidence `inventory`; persistence, protocol, automated tests, runtime validation and gameplay E2E remain `not-assessed`.

## Discovery expectations

```text
src/map/map.cpp
  → world-map-runtime
src/items/tile.cpp
  → world-map-runtime
src/io/iomap.cpp
  → world-map-runtime
src/game/zones/zone.cpp
  → world-zones
src/game/instance/instance_manager.cpp
  → instances
tests/unit/game/instance/instance_manager_test.cpp
  → instances
```

Server source mapping must not consume the broad client `protocol` bucket. Client `src/**` paths remain governed by the explicit client source policy and must not inherit server-only world modules. Mapping stays deterministic and discovery-only.

## Evidence limits

TSD-008 does not prove OTBM runtime load completeness, tile stack behavior, movement/pathfinding, sight/visibility, zone membership/eviction, teleport/floor-transition/NPC travel semantics, instance region isolation, cleanup, expiration, visibility/target/combat isolation, persistence, protocol compatibility, physical-client E2E, Real Tibia parity or Oteryn readiness.

## Next package

After feature merge and lifecycle archive:

```text
task: CAN-20260714-tibia-system-decomposition-social-communication-trust
package: TSD-009
branch: docs/tibia-system-decomposition-social-communication-trust
```
