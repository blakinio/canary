# Instanced Test Arena

## Purpose

A small, administrator-only vertical slice that is a real consumer of the
existing `InstanceManager` foundation (`Game::getInstanceManager()`,
region-backed lifecycle, `InstanceCreatureBinder`, automatic unregister on
removal, `InstanceScopedEvent`, periodic timeout sweep). It is not a generic
dungeon framework and does not implement multiworld or multi-channel
features.

One authorized player creates a real instance, is teleported into a reserved
map region, a real monster is spawned and registered to that instance, and
the player can leave or close the instance, returning to their prior
position while the region is cleaned up and released for reuse.

## Map selection

`config.lua.dist` defaults to `mapName = "otservbr"`, `dataPackDirectory =
"data-otservbr-global"`. That map file (`otservbr.otbm`) is **not present in
this checkout** - `src/map/map_download.hpp`/`.cpp` and
`tests/unit/utils/map_download_test.cpp` confirm it is fetched from a GitHub
release asset at server startup, not committed to the repository.

The only complete, physically present world map in this checkout is
`data-canary/world/canary.otbm` (19,718,948 bytes, confirmed by
`otbm_map_tool.py inspect`):

```text
sha256: a3a1389bc7e8ba63080858023fba0eaded5253b6f6bd3d66b0f3c5112c987361
width/height: 40000 x 40000
tileCount: 1940292
tileAreaCount: 115541
description: "Map developed by Eduardo Dantas for Canary project of the
             OpenTibiaBR organization."
```

This is the project's own named "Canary" world (matching the fork's name),
not a throwaway fixture, and it is the only map this sandbox can actually
scan end-to-end. The arena's region configuration therefore targets
`data-canary/world/canary.otbm`. **This is a recorded assumption, not a
unilateral final decision** - if the intended production map for this
feature is the downloaded `otservbr.otbm` instead, the owner should say so;
the region-selection methodology below applies identically to any map, and
`InstanceArenaService`'s region list (added in the next PR) is a single,
explicit configuration point that can be repointed at different coordinates
without any other code change.

## Candidate area: "Tps Room"

`otbm_map_tool.py world-index` lists 8 towns. Seven cluster inside
roughly `x:1900-6000, y:1300-5550` (Montag, Tihamah, Nahag Village,
Alexandria, Thalom, Katorga, Strongarm). The eighth, **"Tps Room"**
(`townId 3`, temple at `19992,19992,7`), sits alone near the map's
geometric center, over 14,000 tiles away from every other town. The map's
only house (`houseId 1`, name `"NPC"`, size 17, entry `19977,19988,7`) is
inside this same area.

A bounded export (`otbm_map_tool.py export --from 19960,19965,7 --to
20015,20010,7 --items-xml data/items/items.xml`) plus a full-map audit
(`otbm_item_audit_scan` + `otbm_item_audit_tool.py` +
`otbm_script_resolution_tool.py`, see "Verification evidence" below)
identify exactly what this area is: a single walled GM/developer
teleport-testing hall, not active gameplay content.

Layout (`#`=wall, `H`=house, `D`=door, `T`=teleport, `.`=plain floor):

```text
      1997199719971997199719971998199819981998199819981999199919991999199920002000200020002000
      567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234
19982 ####################################
19983 #HHHH#.............................#
19984 #HHHH#TTTT.TTTTTTTT.TTT...T........#     <- 16 magic-forcefield "windows" to other towns
19985 #HHHH#.............................#
19986 #HHHH#.............................#
19987 ###D##.............................#     <- house door (houseDoorId 2)
19988 #..................................#  \
19989 #..................................#   \
19990 #..................................#    \  clean band, zero mechanics,
19991 #..................................#     >  y = 19988..19994, x = 19975..20008
19992 #..................................#    /
19993 #..................................#   /
19994 #..................................#  /
19995 #.................T...T.T.T.T......#     <- more forcefield windows
19996 #..................................#
19997 #..................................#
19998 #..................................#
19999 #..................................#
20000 #.........T.T.T.TTT.T.....T.T.T.T.T#     <- forcefield windows + 2 real crystal
20001 #..................................#        teleporters (destination [0,0,0], unset)
20002 #.........................T........#
20003 #..................................#
20004 ####################################
```

(column header reads vertically; interior wall box is
`x:19974-20009, y:19982-20004`.)

## Selected regions

Both regions sit inside the clean `y:19988-19994` band, which the audit
below proves is free of every mechanic in the area (all teleports live at
`y=19984`, `19995`, `20000`, `20002`; the only door is at `19977,19987`;
the house occupies `x:19974-19979, y:19982-19987`). An 8-tile buffer
(`x:19988-19995`) separates the two regions so neither a spawned monster's
normal aggro/wander range nor a careless walk crosses from one into the
other; cross-instance interaction itself is enforced logically by the
existing ownership registry (`getCreatureRelation()`/
`canCreaturesInteract()`), not by this physical gap alone - this is
belt-and-suspenders, not the sole isolation mechanism.

| Region | minX | maxX | minY | maxY | Z | Size |
|---|---:|---:|---:|---:|---:|---|
| `InstanceTestArenaSlotOne` | 19976 | 19987 | 19988 | 19994 | 7 | 12 x 7 (84 tiles) |
| `InstanceTestArenaSlotTwo` | 19996 | 20007 | 19988 | 19994 | 7 | 12 x 7 (84 tiles) |

Both regions are strict subsets of plain floor tiles already confirmed
walkable (non-void ground, `stone tile`/`cobbled pavement`/`wooden floor`)
by the bounded export. Neither overlaps the house, the door, or any
teleport tile. Same dimensions, same floor, non-overlapping, evidence-backed
- no invented coordinates.

## Verification evidence

Full-map audit (native scanner + item audit + script resolution, run
against `data-canary/world/canary.otbm` in its entirety, not just the
candidate area):

```text
otbm_item_audit_scan (compiled from tools/ai-agent/otbm_item_audit_scan.cpp)
otbm_appearances_tool.py data/items/appearances.dat
otbm_item_audit_tool.py data-canary/world/canary.otbm \
  --scanner <built scanner> --appearances-index <built index> \
  --items-xml data/items/items.xml --allow-errors
  -> ok: true, mapMechanicItemIds: 15, mapMechanicPlacements: 271

otbm_script_resolution_tool.py <item audit output> \
  --script-root data --script-root data-otservbr-global
  -> ok: true, strictRuntimeOk: true
  -> mechanicPlacements: 271, resolvedPlacements: 271
  -> runtimeUnresolvedPlacements: 0, conflictingPlacements: 0
  -> identifierCounts: {"actionId": 1, "uniqueId": 0} (elsewhere on the map,
     not in either selected region)
```

Cross-referencing all 271 real mechanic placements against both region
boxes: **zero placements fall inside `InstanceTestArenaSlotOne` or
`InstanceTestArenaSlotTwo`**. Every mechanic in the wider "Tps Room" area
is `handled-by-engine` (teleport destinations, the one house door) - none
are dynamic Lua, none carry an `actionId`/`uniqueId`, so there is nothing
here for a future spawn/creature/event to collide with.

No `.otbm` file was modified. No new room was authored - RME is not
available in this environment, and both selected regions are existing,
already-walkable floor tiles inside an existing walled hall, so the
"add two new rooms" fallback was not needed.

## Player entry, return position, and arena entities

- **Return position**: the player's exact position at the moment
  `/instancearena create` is issued (captured by the future
  `InstanceArenaService`, not a hardcoded town coordinate). This is
  necessarily safe - the player is already standing there - and needs no
  new map evidence.
- **Entry position**: the region's `(minX, minY, Z)` corner
  (`19976,19988,7` for slot one, `19996,19988,7` for slot two), one tile in
  from both interior edges.
- **Monster spawn position**: offset a few tiles from the entry corner,
  well inside the region's bounds (exact tile decided in the PR that adds
  spawning, once the concrete monster type is chosen).

## Architecture for the next PRs

`InstanceArenaService` (added in the next PR) is the real consumer:

- owns the two-region `std::vector<InstanceMapRegion>` above as its single,
  explicit configuration point;
- takes `InstanceManager &` (from `Game::getInstanceManager()`) and
  `InstanceCreatureBinder` by constructor injection - no new `g_*()`
  singleton;
- identifies players, monsters, and events by stable IDs only, matching
  every existing piece of this subsystem;
- is reachable only through an administrator-gated command; ordinary
  players cannot invoke it.

## Current status (updated through PR 5)

The plan above was written before implementation; this section tracks what
actually exists on `main` so the two don't drift apart silently.

- **PR #289**: `InstanceArenaService` exists, owns the two regions above,
  and provides create/activate/close arena lifecycle via
  `Game::getInstanceArenaService()`.
- **PR #295**: `/instancearena create|leave|close` (admin-gated,
  `groupType("gamemaster")`) and matching `Game.createInstanceArena/
  leaveInstanceArena/closeInstanceArena` Lua bindings. `create` teleports to
  the region's entry corner using the player's real position at command time
  as the saved return position; `leave` returns there without releasing the
  region; `close` evacuates to the same position and releases it.
- **PR #304**: `create`/enter spawns and registers one real `Cave Rat`
  (chosen for datapack consistency with `data-canary/world/canary.otbm`) a
  few tiles from the entry corner, registered with `InstanceCreatureBinder`
  only after it has a real runtime id; any spawn/registration failure rolls
  the whole arena back. The engine's one production summon-creation call
  site (`Monster::onThinkDefense()`) is wired to the instance-aware
  `Creature::setMaster(..., binder, ...)` overload via
  `Game::getInstanceCreatureBinder()`, so a summon inherits its master's
  arena ownership.
- **PR 5 (this one)**: every arena now has a real 15-minute timeout
  (`InstanceArenaService::ArenaTimeout`) instead of running forever; a
  one-shot closing-warning message is scheduled 2 minutes before that,
  guarded by `InstanceScopedEvent` so it is a no-op if the arena already
  closed; `InstanceArenaService::reapExpiredSessions()` runs on the same
  periodic tick as `closeExpiredInstances()` (`Game::start()`) to evacuate
  and forget any player session left behind by a timeout-driven close.

Still open, tracked by the program queue in
`docs/agents/programs/INSTANCED_TEST_ARENA_PROGRAM.md`: cross-instance
isolation fixes for spectator/target/combat call sites (item 6) and the
two-parallel-instances end-to-end proof plus region-reuse evidence (item 7).

## Non-goals

- no generic dungeon/instance framework beyond this one vertical slice;
- no multiworld or multi-channel work;
- no new OTBM parser or renderer - existing `tools/ai-agent/otbm_*` tooling
  was reused throughout;
- no AI image generation for the visualization above (a deterministic
  tool-generated SVG preview and the ASCII diagram above, both derived
  directly from the real export, are the only visualizations produced);
- no `.otbm`/`items.otb` modification.
