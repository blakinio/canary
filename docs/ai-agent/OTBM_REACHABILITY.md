# OTBM Teleport and Reachability Validation

## Purpose

Phase 3 adds deterministic, read-only movement analysis on top of the existing OTBM World Index. It answers bounded questions such as:

- does a teleport destination tile exist;
- does the destination contain confirmed floor evidence;
- is the tile statically blocked, conditionally blocked or unresolved;
- is there an exact reverse transition;
- is a transition one-way, self-referential or aimed at a dead end;
- can a player-shaped path be found between two explicit positions inside a bounded region;
- does the only possible path depend on doors, dynamic mechanics or incomplete appearance evidence.

The tool does not parse OTBM independently. It consumes the `.widx` contract from `otbm_world_index.py` and movement flags from an existing `canary-appearances-index-v1` report.

## Entrypoints

```text
tools/ai-agent/otbm_reachability.py
tools/ai-agent/otbm_reachability_tool.py
```

Report contract:

```text
canary-otbm-reachability-v1
```

Schema:

```text
docs/ai-agent/OTBM_REACHABILITY.schema.json
```

## Movement evidence model

Every indexed tile is conservatively classified:

| Classification | Meaning |
|---|---|
| `walkable` | tile exists, confirmed ground/floor appearance exists and no blocker/unknown appearance was found |
| `blocked` | tile is absent, has no confirmed floor when all appearances are known, or contains a static `unpassable` item |
| `conditional` | movement may depend on a mechanic-controlled blocker or an `avoid` appearance |
| `unresolved` | an appearance needed to establish floor/blocking evidence is missing |

An `unpassable` placement carrying `actionId`, `uniqueId` or `houseDoorId` is not treated as permanently blocked. It is `conditional`, because a door or scripted object may change state at runtime.

This is deliberately conservative. Client appearance flags are useful evidence, but they are not proof of all server runtime rules.

## Teleport audit

```bash
PYTHONPATH=tools/ai-agent \
python tools/ai-agent/otbm_reachability_tool.py audit \
  /path/to/world.widx \
  /path/to/APPEARANCES_INDEX.json \
  --sample-limit 500 \
  --output /tmp/OTBM_REACHABILITY.json
```

Optional bounded source selection:

```bash
  --region-from 32000,32000,7 \
  --region-to 32100,32100,9
```

The audit reports:

- destination tile/floor/walkability evidence;
- `zero-destination`;
- `self-loop`;
- `missing-destination-tile`;
- `missing-destination-floor`;
- `blocked-destination`;
- `destination-dead-end`;
- exact reverse pairing;
- one-way transitions.

A one-way transition is descriptive, not automatically a defect. Many valid quest entrances and exits are intentionally asymmetric.

## Bounded route validation

Route validation always requires explicit bounds:

```bash
PYTHONPATH=tools/ai-agent \
python tools/ai-agent/otbm_reachability_tool.py route \
  /path/to/world.widx \
  /path/to/APPEARANCES_INDEX.json \
  --region-from 32000,32000,6 \
  --region-to 32100,32100,9 \
  --start 32010,32010,7 \
  --goal 32080,32075,8 \
  --max-nodes 250000 \
  --output /tmp/OTBM_ROUTE.json
```

The validator builds two graphs:

1. **definite graph** — only tiles classified `walkable`;
2. **permissive graph** — `walkable`, `conditional` and `unresolved` tiles.

Results:

| Status | Meaning |
|---|---|
| `confirmed` | a path exists using only definite walkable evidence |
| `unresolved` | no definite path exists, but a permissive path exists through conditional or unresolved tiles |
| `unreachable` | no path exists in either graph inside the supplied bounds |

Cardinal movement is four-directional on one floor. Indexed teleport edges are added when both endpoints are inside the explicit bounds.

The output contains the selected path, path length and any conditional/unresolved positions used. Path samples are capped at 10,000 positions.

## Stairs, ladders, holes and reviewed floor changes

The tool never guesses an item's movement role. Cross-floor item semantics must come from a reviewed catalogue:

```json
{
  "format": "canary-otbm-movement-catalog-v1",
  "rules": [
    {
      "itemId": 1386,
      "role": "ladder",
      "offset": [0, 0, -1],
      "bidirectional": false
    }
  ]
}
```

Allowed roles:

- `stairs`;
- `ladder`;
- `hole`;
- `rope`;
- `floor-change`;
- `custom`.

Rules use a bounded relative `[dx,dy,dz]` offset. They should be added only after item behavior and direction are proven from active server/client contracts or reviewed fixtures. No production catalogue is bundled by default.

Use it with:

```bash
--movement-catalog /path/to/reviewed-movement-catalog.json
```

## Tile inspection

```bash
PYTHONPATH=tools/ai-agent \
python tools/ai-agent/otbm_reachability_tool.py tile \
  /path/to/world.widx \
  /path/to/APPEARANCES_INDEX.json \
  32062,32271,7
```

The response contains exact placements, floor item IDs, static blockers, mechanic-controlled blockers, avoid items and missing appearance IDs.

## Bounds and safety

- route bounds may cover at most 1,000,000 coordinate positions;
- default indexed-node limit is 250,000;
- transition samples default to 100 and may not exceed 10,000;
- report output is atomic;
- symlink output targets are rejected;
- existing output requires `--overwrite`;
- source `.widx` and appearance-index hashes are recorded;
- maps, WIDX files, appearances binaries, client assets and generated reports stay outside Git;
- the tool never modifies the map or executes Lua.

## Evidence limitations

The following remain outside static proof:

- runtime door state;
- creature/player occupancy;
- dynamic item movement;
- script-created or removed blockers;
- quest/account/storage conditions;
- directional use requirements;
- path costs and diagonal movement rules beyond this explicit model;
- full physical-client gameplay.

A green report proves only the recorded bounded static evidence. It must not be presented as complete live quest execution proof.
