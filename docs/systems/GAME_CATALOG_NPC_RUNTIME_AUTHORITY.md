# Game Catalog NPC and Shop Runtime Authority

## Status

This document defines the authoritative Canary source boundary for the future `oteryn.game-catalog` schema `1.3.0` producer. It is an implementation contract for a later task; this audit does not change exporter, schema, datapack or runtime behavior.

Paired Platform contract:

- Platform PR `#338`;
- schema version `1.3.0`;
- pinned schema SHA-256 `0282c0ce4b995e4aded440b148dd4eb8a96a441e9924da182a2df2a0f2eef8a8`;
- pinned shared-fixture SHA-256 `c4fd9b187e001065f68d90f93dc67f71bb2ff745fc43c3e73110d49b23407ce7`.

## Decision

The producer must extend the existing export-only runtime loader and serializer from Canary PR `#991`. It must not parse NPC Lua or XML independently.

The authoritative static boundary is:

1. execute the existing core NPC library;
2. execute the configured datapack's existing `npc/**/*.lua` scripts through the normal Lua script interface;
3. read the resulting final `Npcs` registry;
4. read each final `NpcType` and its `NpcType::info.shopItemVector`;
5. reuse the existing final item registry and canonical item-key mapping for offered items and currencies.

No spawned `Npc`, `Player`, map, database, service port or world lifecycle is part of this boundary.

## Current runtime lifecycle

### Existing export-only loader

`CanaryServer::loadGameCatalogDefinitions()` currently loads:

- item and appearance definitions;
- core Lua and script libraries;
- the core NPC library with `g_npcs().load(true, false)`;
- events, modules, datapack libraries, monster spell scripts and monster scripts.

It deliberately does not load the complete datapack script tree. It also does not currently execute the configured datapack's `npc` directory. Therefore the current export-only path does not populate the final NPC registry and cannot yet produce schema `1.3.0` NPC records.

The producer task must add one bounded NPC-script load using the existing `Npcs::load(false, true)` behavior. It must not load migrations, actions, global events or the complete datapack script tree.

### Final NPC registry

`NpcType(name)` calls `g_npcs().getNpcType(name, true)`. The registry key is the lowercase form of the supplied name and the stored value is one shared `NpcType` instance. Later calls for the same lowercase key return the existing object.

The final registry authority is therefore the private `Npcs::npcs` map after all selected NPC scripts have completed. The producer needs a bounded const enumeration API; it must not reconstruct the registry by scanning source files.

Required entity field mapping:

| Schema field | Runtime authority |
|---|---|
| `registry_key` | exact key from `Npcs::npcs` |
| `runtime_name` | final `NpcType::name` |
| `display_name` | `null` unless a distinct reviewed runtime field is added or proven |
| `type_name` | final `NpcType::typeName` |
| `name_description` | final non-empty `NpcType::nameDescription`, otherwise `null` |
| `aliases` | empty unless a concrete runtime alias registry is identified |
| `registration_status` | `runtime_registered` |
| `currency.server_id` | final `NpcType::info.currencyId` |
| `currency.item` | existing canonical item key for that exact server ID |
| `attributes.dynamic_player_offers_included` | `false` |

The NPC canonical key must be derived deterministically from the exact registry key using the same bounded slug/collision rules used by the producer tests. A collision between distinct registry keys must fail closed; hash or ordinal fallback must not silently merge NPCs.

## Static shop authority

`NpcType:addShopItem(Shop)` calls `NpcType::loadShop`, which resolves the final item type, suppresses exact duplicate `ShopBlock` values and appends the resulting value to `NpcType::info.shopItemVector`.

A `ShopBlock` retains:

- item server ID;
- item name override;
- item subtype/count;
- player-buy price;
- player-sell price;
- storage key and storage value;
- ordered nested child shops.

The vector after NPC script execution is the authoritative static offer set.

### Direction mapping

The paired Platform contract names directions from the player's shop action:

- nonzero `ShopBlock::itemBuyPrice` produces `npc_buy_offer` — the player buys the item from the NPC;
- nonzero `ShopBlock::itemSellPrice` produces `npc_sell_offer` — the player sells the item to the NPC;
- a block with both prices produces two relations;
- a zero price produces no relation for that direction.

`priced_item_count` is always `1`; `itemSubType` remains a separate exact field.

### Runtime path and identity

Walk each `shopItemVector` recursively in stored vector order. The zero-based index sequence is the exact `runtime_path`:

- first top-level block: `[0]`;
- its second child: `[0, 1]`;
- and so on, with a maximum depth of 32 required by the paired schema.

The relation canonical key is exactly:

- `shop:<npc canonical key>:buy:<item canonical key>:<dot-joined runtime path>`; or
- `shop:<npc canonical key>:sell:<item canonical key>:<dot-joined runtime path>`.

A repeated canonical identity, an excessive depth, a missing item endpoint or a currency endpoint mismatch must reject the complete export.

### Storage requirements

`ShopBlock` has no presence bit for storage conditions. Its constructor default is `(itemStorageKey, itemStorageValue) == (0, 0)`.

Producer rule:

- `(0, 0)` maps to `storage_requirement: null` because unset and an intentional exact `(0, 0)` requirement are indistinguishable in the current runtime model;
- every other pair is emitted exactly as `{key, value}` and the relation availability is at least `conditional`;
- the producer must not infer quest names, comparison operators or player eligibility from the numeric pair.

If a future datapack proves that exact `(0, 0)` is a meaningful requirement, the runtime model must first gain an explicit presence bit; the producer must not guess.

## Dynamic behavior excluded from static snapshots

The following are not part of `NpcType::info.shopItemVector` and must not be flattened into static schema `1.3.0` offers:

- `Npc:openShopWindowTable(player, items)` tables assembled for one player;
- `Npc::shopPlayers` per-player offer vectors;
- instance-level `Npc::setCurrency` changes;
- offers computed inside dialogue callbacks from player storage, vocation, premium status, reputation, quest state, time, stock or world state;
- prices or availability calculated only when a player interacts;
- direct item exchanges implemented as arbitrary callback logic rather than registered shop blocks.

The producer records `dynamic_player_offers_included: false`. It must not execute synthetic player conversations or start a world to discover these paths. Their completeness remains `unknown` or `partial` unless a separate reviewed runtime authority is designed.

## Provenance and duplicate registration

The current `NpcType` model does not retain a source path. `LuaScriptInterface` knows the currently loading file while a chunk executes, but that path is not persisted on the registered NPC type.

The producer task must add bounded provenance capture at the existing `NpcType(name)` registration boundary:

- normalize the loading file relative to the configured datapack directory;
- reject absolute paths, traversal and paths outside the selected NPC directory;
- retain the exact normalized source path on the final runtime object;
- fail closed when one registry key is registered by different source files unless a reviewed explicit override rule is added.

This also prevents filesystem traversal order from silently deciding which conflicting NPC definition becomes authoritative. Output ordering remains canonical-key sorted; offer ordering remains the final vector order within one registered NPC.

## Required producer interfaces

The later implementation should add the smallest interfaces necessary:

1. a const, deterministic enumeration view of the final `Npcs` registry;
2. bounded registration-source provenance on `NpcType`;
3. `buildSnapshotDocument` support for the final NPC registry while preserving schemas `1.0.0` through `1.2.0` byte behavior;
4. schema `1.3.0` manifest/validator dispatch using the exact Platform-pinned contract;
5. no new parser and no normal server startup.

The collector must reuse the existing item canonical-key table for:

- offered item targets;
- NPC currency endpoints;
- relation currency endpoints.

Unknown item or currency IDs fail the entire export rather than producing dangling fallback keys.

## Validation contract for the producer task

### Focused C++ tests

Use synthetic final runtime objects to prove:

- registry-key normalization and deterministic NPC ordering;
- distinct runtime name, type name and nullable description mapping;
- default and custom currency mapping;
- one block with buy, sell or both directions;
- exact subtype, price and item name preservation;
- `(0, 0)` versus nondefault storage mapping;
- nested `runtime_path` construction;
- exact duplicate suppression inherited from `NpcType::loadShop`;
- canonical-key collision, duplicate relation, excessive depth, dangling item and dangling currency rejection;
- per-player vectors are not accepted by the collector;
- old schema documents remain unchanged for identical old inputs.

### Export-only runtime smoke

Extend the isolated runtime datapack with deterministic NPC scripts that register:

- at least one NPC;
- gold and custom-currency shops;
- buy and sell directions;
- one conditional storage pair;
- one nested child shop.

Run export twice with controlled timestamps and require:

- exact schema `1.3.0` validation;
- identical normalized bytes and valid lowercase SHA-256 sidecars;
- nonzero typed NPC and shop counts;
- no `connect`, `bind`, `listen`, `accept` or database-backed shutdown activity;
- no complete datapack script-tree load.

### Cross-repository compatibility

A generated Canary artifact must then pass the Platform PR `#338` contract validator and MariaDB inactive-import lifecycle against the exact pinned schema hash. This proof does not authorize activation, staging deployment or production import.

## Failure policy

Fail the complete export and preserve any prior published snapshot when:

- NPC scripts cannot execute in export-only mode;
- duplicate registry provenance is ambiguous;
- canonical keys collide;
- an item or currency endpoint is absent or mismatched;
- prices, paths, counts or integer fields exceed the schema bounds;
- child nesting exceeds the bounded depth;
- the produced document fails the exact pinned schema or semantic validator;
- any database or network endpoint activity is observed.

## Explicitly deferred

- per-player or world-dependent offers;
- dialogue-only exchanges;
- historical introduced/removed evidence;
- map/spawn reachability and encounterability;
- public Platform NPC/shop projection;
- staging activation, production import, production activation and deployment.
