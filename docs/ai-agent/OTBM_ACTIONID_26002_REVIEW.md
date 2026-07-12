# Manual review — OTBM `actionId 26002`

## Decision

```text
ID: 26002
namespace: actionId
decision: legacy-unused
confidence: high
underlying mechanic: handled by active position-registered MoveEvent
map change: none
gameplay change: none
```

The `actionId` value itself is not consumed by the active datapack or engine. The related Soul War Ebb and Flow boat transitions are implemented by the active `ebbAndFlowBoatTeleports` `MoveEvent`, registered directly on positions from `SoulWarQuest.ebbAndFlowBoatTeleportPositions`.

This classification does **not** authorize removing the map attributes. Preserve them until a separate map-cleanup decision is explicitly approved and validated.

## Audited baseline

```text
base commit: 7d8b5c1b54121f309614ecdfafbb445b00f8606b
canonical resolver merge: 0b355669ebe66c9d9c604c2a9221f47280699581
source map SHA-256: a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2
source map size: 184,776,037 bytes
mechanic placements: 9,339
runtime-resolved placements: 8,964
runtime-unresolved/partial placements: 375
runtime-unresolved identifiers before this decision: 151
conflicting placements: 0
normal report: ok = true
strict runtime: exit 2, expected
```

The mechanics scan is exact. The current session did not contain the original client 15.25 `appearances.dat`; the resolver input was rebuilt with a clearly labelled appearance surrogate containing every scanned item ID except the previously verified missing item `2141`. Appearance metadata does not affect mechanic placement extraction or handler correlation.

## Map evidence

```text
placements: 71
floor: z = 8
bounds: 33896,31019,8 .. 33945,31117,8
connected marker strips: 14
house IDs: none
teleport destination on marked items: none
item IDs: 4394..4410
item name: rock soil
```

Every placement is an item node carrying `actionId 26002`; none is an inline tile item.

### Item distribution

| Item ID | Placements | Item ID | Placements |
|---:|---:|---:|---:|
| 4394 | 7 | 4403 | 2 |
| 4395 | 5 | 4404 | 3 |
| 4396 | 2 | 4405 | 2 |
| 4397 | 4 | 4406 | 6 |
| 4398 | 4 | 4407 | 11 |
| 4399 | 2 | 4408 | 3 |
| 4400 | 5 | 4409 | 4 |
| 4401 | 5 | 4410 | 5 |
| 4402 | 1 | | |

### Complete position set

Each range below is inclusive and represents one contiguous horizontal or vertical strip; together they contain all 71 placements.

```text
x=33919, y=31019..31022, z=8
x=33919, y=31046..31049, z=8
x=33929, y=31046..31049, z=8
x=33896..33902, y=31055, z=8
x=33940..33944, y=31055, z=8
x=33940..33944, y=31064, z=8
x=33934..33939, y=31087, z=8
x=33934..33939, y=31098, z=8
x=33899..33904, y=31099, z=8
x=33899..33904, y=31108, z=8
x=33934, y=31108..31112, z=8
x=33945, y=31108..31112, z=8
x=33913, y=31114..31117, z=8
x=33921, y=31114..31117, z=8
```

## Area and quest identification

The group belongs to **Soul War — Ebb and Flow**, the Bony Sea Devil hunting ground.

Evidence:

- `data-otservbr-global/scripts/quests/soul_war/moveevent-soul_war_entrances.lua` registers hub position `33621,31422,10` to destination `33894,31019,8` with the comment `hunt bony sea devil`;
- same-floor spawns around the markers include `Turbulent Elemental`, `Hazardous Phantom`, and `Bony Sea Devil`;
- a nearby map teleport at `33891,31020,8` leads back to `33621,31427,10`;
- `SoulWarQuest.areaZones.ebbAndFlow` covers this region and subtracts the entrance room;
- `SoulWarQuest.ebbAndFlowBoatTeleportPositions` contains the matching boat-transition lines.

The coordinates overlap an annual-event island on other layers. Winterlight/Percht files were checked and rejected as the source because the exact floor, spawns, entrance and runtime table identify Soul War Ebb and Flow.

## Active execution path

1. `data-otservbr-global/lib/quests/soul_war.lua` defines `SoulWarQuest.ebbAndFlowBoatTeleportPositions`.
2. The table contains 173 direct `register` position to `teleportTo` position mappings.
3. `data-otservbr-global/scripts/quests/soul_war/soul_war_mechanics.lua` creates `ebbAndFlowBoatTeleports = MoveEvent()`.
4. `onStepIn` requires `SoulWarQuest.ebbAndFlow.isActive()`, finds the matching position, teleports the player and emits a teleport effect.
5. Every table entry is registered with `ebbAndFlowBoatTeleports:position(pos.register)`, followed by `ebbAndFlowBoatTeleports:register()`.

### Position coverage

```text
actionId 26002 positions matching active position handlers: 64 / 71
active Ebb and Flow position handlers without actionId 26002: 109
actionId 26002 positions without an exact position handler: 7
```

The 109 active position registrations without this action ID establish that `26002` is not the runtime registration key.

The seven unmatched map attributes are adjacent endpoints of marker strips and remain preserved as legacy map metadata:

```text
33902,31055,8
33913,31117,8
33919,31049,8
33921,31117,8
33929,31049,8
33934,31087,8
33935,31087,8
```

## Repository search

- Active roots `data` and `data-otservbr-global`: no `Action` or `MoveEvent` registration by `actionId 26002`.
- Inactive `data-canary`: no handler for `actionId 26002`.
- C++ engine sources: no hard-coded handling for `26002`.
- Text occurrences are limited to the unrelated item ID `26002` (`valuable mayhem bow`), review metadata and handoff documentation.
- The resolver surfaces `ebbAndFlowBoatTeleports:position(pos.register)` as a dynamic position registration. It intentionally does not guess the cross-file table values.

## Classification record

```text
ID: 26002
namespace: actionId
liczba wystąpień: 71
pozycje: 14 pełnych zakresów powyżej, wszystkie na z=8
itemy: 4394..4410, rock soil
obszar: Soul War — Ebb and Flow / Bony Sea Devil hunting ground
prawdopodobna funkcja: historyczne markery linii teleportów łodzi
aktywny handler: ebbAndFlowBoatTeleports, rejestracja po pozycjach
źródło potwierdzenia: aktywny SoulWarQuest table, aktywny RevScriptSys MoveEvent, zgodność 64 pozycji
decyzja: legacy-unused
confidence: high
dalsza akcja: zachować mapę; ewentualne rozszerzenie resolvera wykonać osobno z testem
```

## Validation

```text
python -m unittest tools/ai-agent/test_otbm_script_resolution.py -v
result: 4 passed

python -m unittest discover -s tools/ai-agent -p 'test_*.py' -v
result: 139 passed

normal resolver after classification:
ok = true
review dispositions: legacy-unused = 1, needs-manual-review = 150
conflicts = 0

strict resolver after classification:
exit code = 2
runtime-unresolved identifiers = 151
```

Strict runtime intentionally remains non-green because review dispositions do not claim a runtime handler for an unused map identifier.

No map, client asset, generated multi-megabyte report, active datapack, resolver source or gameplay file is committed by this review.
