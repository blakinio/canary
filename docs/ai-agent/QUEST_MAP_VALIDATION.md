# Quest Map Validator

## Purpose

`tools/ai-agent/quest_map_validation_tool.py` connects explicitly selected quest Lua/XML sources with factual map evidence from the Unified OTBM World Index.

The workflow is split deliberately:

```text
public repository sources
  -> canary-quest-map-evidence-v1
  -> CI artifact

private/local OTBM world index (.widx)
  + optional OTBM script-resolution report
  + source evidence artifact
  -> canary-quest-map-validation-v1
```

This separation lets CI inspect public source code without requiring a private or very large map artifact. Local agents can then correlate the deterministic evidence artifact with the approved map snapshot.

The validator is read-only. It does not execute Lua, modify the OTBM, edit scripts, invent identifiers or generate gameplay fixes.

## Source scan

Select source roots and explicit include globs:

```bash
python tools/ai-agent/quest_map_validation_tool.py scan \
  --repository-root . \
  --source-root data \
  --source-root data-otservbr-global \
  --include 'data-otservbr-global/scripts/quests/*.lua' \
  --include 'data-otservbr-global/scripts/quests/**/*.lua' \
  --include 'data-otservbr-global/npc/*.lua' \
  --include 'data-otservbr-global/npc/**/*.lua' \
  --exclude '**/test/**' \
  --output artifacts/QUEST_MAP_EVIDENCE.json
```

At least one `--include` is required. The validator never guesses that every Lua file belongs to the same quest.

The source-only report is `canary-quest-map-evidence-v1` and contains:

- selected file paths and SHA-256 values;
- exact source line and context for every entry;
- static action IDs and unique IDs;
- item IDs used by creation, reward, consumption, type and condition expressions;
- exact `Position(x, y, z)` references;
- statically resolved teleport destinations;
- storage read/write inventory;
- unresolved dynamic expressions.

Action, MoveEvent and XML registrations are obtained through the existing OTBM script-resolution scanner rather than a competing registration parser.

## Static resolution boundary

Supported examples include:

```lua
local reward = 7772
local exitPosition = Position(33300, 31700, 7)

local action = Action()
action:aid(45001)
action:register()

player:addItem(reward, 1)
player:removeItem(3031, 100)
player:teleportTo(exitPosition)
player:getStorageValue(Storage.Quest.Example)
player:setStorageValue(Storage.Quest.Example, 1)
```

Comments and strings are masked before supplementary extraction, so text such as `"Position(1, 2, 3)"` is not treated as map evidence.

Dynamic expressions remain explicit:

```lua
action:aid(config.actionId)
player:addItem(config.reward, 1)
player:teleportTo(config.destination)
```

They appear under `unresolved`; they are never evaluated or guessed.

## Correlate with the map

```bash
python tools/ai-agent/quest_map_validation_tool.py validate \
  artifacts/QUEST_MAP_EVIDENCE.json \
  --world-index /outside/repository/world.widx \
  --script-resolution /outside/repository/OTBM_SCRIPT_RESOLUTION.json \
  --region-from 33200,31800,7 \
  --region-to 33250,31850,8 \
  --sample-limit 20 \
  --output artifacts/QUEST_MAP_VALIDATION.json \
  --fail-on conflicting
```

`--script-resolution` is optional. When supplied, AID/UID handler status comes from the merged script-resolution contract. A reviewed unresolved identifier remains unresolved and is not promoted to handled.

The optional region is inclusive. It adds map mechanics located inside the selected region but not referenced by the selected source set. Regions are bounded to one million coordinate positions.

Placement samples are bounded, while every finding retains its exact map count.

## Classifications

- `confirmed` — selected source evidence and the required map placement both exist; AID/UID handler evidence is confirmed when script-resolution is available.
- `map-only` — a map placement exists, but the selected sources do not establish a confirmed matching handler/reference.
- `script-only` — selected source evidence expects an item, identifier or tile absent from the indexed map.
- `unresolved` — evidence is insufficient or belongs to a later semantic phase, such as storage progression.
- `conflicting` — script-resolution found competing handlers for the same runtime event.

`ok` is false only for confirmed conflicts. `complete` requires no map-only, script-only, unresolved or conflicting result and no unresolved source expressions.

## Storage evidence

This phase inventories storage reads and writes only. It preserves numeric storage keys and symbolic paths such as `Storage.Quest.Example`.

It does not infer stage order, account-vs-player scope, reachable values or transition graphs. Those checks belong to the dedicated Storage Dependency Graph phase.

## Region map-only findings

When a bounded region is supplied, the validator enumerates indexed mechanics and reports unreferenced:

- action IDs;
- unique IDs;
- teleport destinations.

This is useful for identifying a chest, lever or teleport near a selected quest area that was omitted from the reviewed source set. It is not proof that the mechanic is broken; dynamic or shared handlers may require manual review.

## CI artifact

`.github/workflows/quest-map-validation.yml`:

1. runs focused tests;
2. compiles the Python modules;
3. scans selected active source families without an OTBM;
4. validates the JSON shape and invariants;
5. uploads `QUEST_MAP_EVIDENCE.json` for local correlation.

The workflow does not upload `.otbm`, `.widx`, client assets or generated map renders.

## Safety and failure behavior

- repository-relative source paths are recorded; local absolute paths are not required for evidence identity;
- include/exclude selection is deterministic;
- source files receive SHA-256 provenance;
- malformed evidence, script-resolution formats or corrupt world indexes fail closed;
- query sample limits and region volumes are bounded;
- generated JSON reports remain artifacts and are not committed;
- no map-writing API exists.

## Current limitations

- arbitrary Lua execution, generated registrations, database-dependent states and runtime-loaded tables remain unresolved;
- item references are conservative lexical patterns and require semantic review before gameplay changes;
- storage progression, NPC dialogue state machines, spawn validation and pathfinding are separate roadmap phases;
- a map placement does not prove that the player can reach or use it;
- visual rendering is optional review evidence, not a substitute for identifiers and code.

## Focused validation

```bash
PYTHONPATH=tools/ai-agent \
  python -m unittest -v tools/ai-agent/test_quest_map_validation.py

python -m py_compile \
  tools/ai-agent/quest_map_validation.py \
  tools/ai-agent/quest_map_validation_tool.py \
  tools/ai-agent/test_quest_map_validation.py
```
