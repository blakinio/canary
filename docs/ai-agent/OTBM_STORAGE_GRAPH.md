# OTBM storage dependency graph

## Purpose

Phase 5 converts the already selected and hashed source set from the Quest Map Validator into a deterministic storage-operation graph. It does not discover a wider source tree, execute Lua, modify the OTBM, or claim that lexical source order is runtime order.

Public report format:

```text
canary-otbm-storage-graph-v1
```

Entrypoints:

- `tools/ai-agent/otbm_storage_graph.py`
- `tools/ai-agent/otbm_storage_graph_tool.py`
- `docs/ai-agent/OTBM_STORAGE_GRAPH.schema.json`

## Required input

The required input is a Phase 2 source-evidence report:

```text
canary-quest-map-evidence-v1
```

Every source path is taken from that report. The tool resolves the path below the supplied repository root, rejects symlinks/path escapes, and verifies the current SHA-256 against Phase 2 before reading it. This is how Phase 5 reuses Phase 2 source selection instead of becoming another broad scanner.

Optional correlation inputs are:

- `canary-quest-map-validation-v1`;
- `canary-otbm-spawn-npc-evidence-v1`;
- `canary-otbm-spawn-npc-validation-v1`;
- `canary-otbm-reachability-v1`.

Optional inputs add handler, actor, map or geometry context. They do not promote a storage transition to live gameplay proof.

## Supported namespaces

The graph keeps storage systems separate:

| Namespace | Static forms |
|---|---|
| `player-storage` | `player:getStorageValue(key)`, `player:setStorageValue(key, value)` |
| `account-storage` | `player:getAccountStorage(key)`, `player:getUpdatedAccountStorage(key)` |
| `player-kv` | `player:kv():get/set/remove`, literal `scoped(scope)` form |
| `account-kv` | `player:accountKV():get/set/remove` when present in selected sources |
| `global-storage` | `Game.getStorageValue`, `Game.setStorageValue` |
| `global-kv` | literal `GlobalKV` / `KV` get/set/remove forms |
| `database` | narrow literal SQL statements touching a storage table |

A key can be an integer, a literal string, or a canonical `Storage...` symbol. Dynamic keys remain unresolved.

## Operations

The report inventories:

- reads;
- literal writes;
- deletes;
- exact same-key increments and decrements;
- comparisons inside explicit `if`/`elseif` branches.

A dynamic write value is unresolved unless it is a direct same-key expression such as:

```lua
player:setStorageValue(key, player:getStorageValue(key) + 1)
```

or a uniquely bound read variable:

```lua
local current = player:getStorageValue(key)
player:setStorageValue(key, current - 1)
```

## Transition proof rule

An explicit graph edge is emitted only when one enclosing source branch proves exactly one same-key equality prerequisite and one literal/delete/delta result:

```lua
if player:getStorageValue(Storage.Quest.Example.Stage) == 2 then
    player:setStorageValue(Storage.Quest.Example.Stage, 3)
end
```

This becomes:

```text
player-storage / Storage.Quest.Example.Stage
2 -> 3
```

The following do **not** become exact stage edges:

- inequalities such as `>= 2`;
- `else` branches, because negation is not converted into a guessed exact value;
- dynamic keys or values;
- writes merely located near a read;
- operations in a different function or file;
- callbacks whose execution relationship is not proven by the selected source construct.

Nested explicit branches retain exact outer prerequisites. Source proximity and line order are never used as runtime ordering evidence.

## Findings

Findings are deliberately conservative:

- `storage_read_without_selected_writer` means no writer was found in the **selected Phase 2 source set**. External initialization, another quest, migration or runtime system may still provide it.
- `storage_write_without_selected_read` means the selected set writes the key but does not prove a selected-scope consumer.
- `storage_prerequisite_unproven_in_selected_scope` means an exact prerequisite is consumed but no selected explicit transition produces it.
- `storage_backward_literal_transition` reports a proven same-key numeric decrease.
- `storage_conflicting_literal_writers` requires the same exact prerequisite with incompatible literal results.
- `storage_expression_unresolved` preserves dynamic syntax instead of guessing.

These are review findings, not automatic repair authorization.

## Example

First create Phase 2 evidence using explicit source globs:

```bash
PYTHONPATH=tools/ai-agent \
python tools/ai-agent/quest_map_validation_tool.py scan \
  --repository-root . \
  --source-root data-otservbr-global \
  --include 'data-otservbr-global/scripts/quests/the_beginning/**/*.lua' \
  --include 'data-otservbr-global/npc/zirella.lua' \
  --output /tmp/QUEST_MAP_EVIDENCE.json
```

Then build the graph:

```bash
PYTHONPATH=tools/ai-agent \
python tools/ai-agent/otbm_storage_graph_tool.py \
  --repository-root . \
  --quest-evidence /tmp/QUEST_MAP_EVIDENCE.json \
  --output /tmp/OTBM_STORAGE_GRAPH.json
```

Optional correlation reports can be supplied with `--quest-validation`, `--spawn-npc-evidence`, `--spawn-npc-validation`, and `--reachability`.

Existing output is rejected unless `--overwrite` is passed. Symlink outputs are rejected and successful writes are atomic.

## Bounds

- selected files: 10,000;
- selected source bytes: 128 MiB;
- operations: 250,000;
- nodes: 100,000;
- transitions: 250,000;
- unresolved expressions: 250,000;
- finding/unresolved output samples: configurable `1..10,000`.

Core graph arrays fail closed at hard limits. Finding and unresolved arrays may be sampled while exact totals remain in `summary`.

## Evidence boundary

The graph is static evidence only. It does not model:

- Lua execution or callback order;
- current player/account/KV/database values;
- transaction boundaries or concurrent writers;
- external migrations and manual database changes;
- runtime branch reachability;
- client behavior;
- successful gameplay completion.

No `.otbm`, `.widx`, `items.otb`, appearances binary, client asset or active datapack file is modified.
