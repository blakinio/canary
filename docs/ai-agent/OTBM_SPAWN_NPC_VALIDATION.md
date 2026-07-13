# OTBM spawn, boss and NPC validation

Phase 4 adds deterministic, read-only evidence for static spawn XML, creature definitions, literal runtime creation calls and bounded OTBM placement validation.

## Contracts

- source evidence: `canary-otbm-spawn-npc-evidence-v1`;
- correlated validation: `canary-otbm-spawn-npc-validation-v1`;
- source schema: `docs/ai-agent/OTBM_SPAWN_NPC_EVIDENCE.schema.json`;
- validation schema: `docs/ai-agent/OTBM_SPAWN_NPC_VALIDATION.schema.json`.

Entrypoints:

- public facade: `tools/ai-agent/otbm_spawn_npc.py`;
- implementation: `tools/ai-agent/otbm_spawn_npc_validation.py`;
- `tools/ai-agent/otbm_spawn_npc_tool.py`.

## Evidence boundary

The scanner accepts one explicit active datapack root and explicit companion spawn XML files. All globs are resolved below that root and symlink/path escapes fail closed. It does not infer the active datapack from neighboring directories and never combines `data-canary` with `data-otservbr-global`.

Dynamic Lua is never executed. Only literal `Game.createMonster` and `Game.createNpc` calls with literal names and literal `Position(x, y, z)` or literal position tables are resolved. Other calls remain `unresolved` with source and line evidence.

Static evidence and green CI are not live gameplay proof. The validator does not model current players, creatures, events, storage/account/database state, runtime zone variants, rate scaling or scheduler timing.

## Runtime coordinate semantics

The current Canary loaders in:

- `src/creatures/monsters/spawns/spawn_monster.cpp`;
- `src/creatures/npcs/spawns/spawn_npc.cpp`;

construct runtime positions as:

```text
x = centerx + child x
y = centery + child y
z = centerz
```

A child `z` attribute is therefore recorded as source evidence but is not used as the runtime floor. A differing child `z` produces `child_z_ignored` rather than silently changing the position.

The runtime spawn zone is an inclusive square around the center. Radius `-1` is unbounded. An offset outside the declared square is reported.

## Definition resolution

Monster definitions are indexed from literal:

```lua
Game.createMonsterType("Name")
```

NPC definitions support both a literal call and the standard local-name form:

```lua
local internalNpcName = "Name"
Game.createNpcType(internalNpcName)
```

Names are correlated case-insensitively. Zero matches are `missing`; more than one active match is `conflicting`. A literal `rewardBoss = true` is recorded as reward-system evidence. Runtime spawn-block boss exclusivity is based on `MonsterType::isBoss()`, which currently means a non-empty Bosstiary class; therefore a literal `monster.Bosstiary = { ... }` assignment is tracked separately as `spawnBossLiteral`. A literal Bosstiary boss sharing the same runtime spawn position with another entry is rejected.

## Phase 3 reuse

Validation requires:

1. a `canary-otbm-spawn-npc-evidence-v1` document;
2. the existing `OTSWIDX1` World Index;
3. a `canary-otbm-reachability-v1` report that fully covers the explicit Phase 4 region.

No second OTBM parser or walkability engine is created.

The World Index proves exact tile existence. Phase 3 diagnostics provide strict and optimistic walkability:

- `confirmed`: tile exists and is strictly walkable;
- `conditional`: only optimistic walkability is available;
- `blocked`: the tile is not optimistically walkable;
- `missing-tile`: no indexed tile exists;
- `unresolved`: Phase 3 diagnostics were truncated or evidence is otherwise incomplete.

Phase 3 normally emits diagnostics only for problematic tiles. Absence from an untruncated diagnostic list therefore means strict walkability. If `tileDiagnosticsTruncated` is true, Phase 4 fails closed and does not assume omitted tiles are walkable.

## Source scan

```bash
PYTHONPATH=tools/ai-agent \
python tools/ai-agent/otbm_spawn_npc_tool.py scan \
  --datapack-root data-otservbr-global \
  --monster-spawn world/otservbr-monster.xml \
  --npc-spawn world/otservbr-npc.xml \
  --monster-definition-glob 'monster/**/*.lua' \
  --npc-definition-glob 'npc/**/*.lua' \
  --dynamic-glob 'scripts/**/*.lua' \
  --output /tmp/OTBM_SPAWN_NPC_EVIDENCE.json
```

Only explicitly supplied spawn XML files are active evidence. Optional/custom/event companion XML must be added explicitly after proving that the selected server configuration loads it.

## Bounded OTBM validation

```bash
PYTHONPATH=tools/ai-agent \
python tools/ai-agent/otbm_spawn_npc_tool.py validate \
  /tmp/OTBM_SPAWN_NPC_EVIDENCE.json \
  --world-index /path/to/world.widx \
  --reachability /tmp/OTBM_REACHABILITY.json \
  --from 33370,32620,0 \
  --to 33420,32690,15 \
  --output /tmp/OTBM_SPAWN_NPC_VALIDATION.json
```

The validation region must be fully contained in the Phase 3 report region. Static groups/placements and literal dynamic creations outside the requested region are not included in the bounded result. Dynamic calls without a statically resolved position cannot be assigned to a coordinate region; they remain explicitly counted as selected-active-datapack-global evidence under `unpositionedDynamicCreations` and `unpositionedDynamicEvidenceScope`.

## Findings

The scanner reports, among others:

- missing/conflicting definitions;
- invalid/missing spawn attributes;
- offsets outside the runtime radius square;
- child `z` values ignored by the loader;
- NPC intervals rejected by the runtime;
- monster intervals defaulted or rate-dependent before the runtime clamp;
- duplicate static placements and overlapping groups;
- literal Bosstiary bosses mixed with another entry at one runtime spawn position;
- unresolved dynamic creation calls;
- exact static/dynamic overlaps.

The correlated validator adds:

- missing group-center or placement tiles;
- blocked or conditional group centers and creature positions;
- literal dynamic creation positions missing or blocked in the map;
- fail-closed Phase 3 diagnostic truncation.

## Safety and output

- no `.otbm`, `.widx`, client asset, generated report or render is committed;
- map and gameplay data are never modified;
- output is deterministic JSON written atomically;
- existing output requires `--overwrite`;
- output symlinks are rejected;
- DTD/entity declarations in spawn XML are rejected;
- source counts, file sizes, placements, dynamic calls and samples are bounded;
- factual rendering remains a separate review step using the existing renderer and real client assets.
