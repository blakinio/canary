# Gameplay Analytics supply and loot telemetry

`GameplayAnalytics.recordSupply(player, itemId, amount, unitValue)` and `GameplayAnalytics.recordLoot(player, itemId, amount, npcValue, marketValue)` store per-item aggregates in `analytics_session_supplies` and `analytics_session_loot`. Both remain disabled until `trackSupplies` / `trackLoot` are set to `true`; both default to `false`.

## Value-source precedence

Every price used by this integration comes from `data/scripts/lib/gameplay_analytics_prices.lua`, a small table copied directly from real NPC shop scripts.

1. A verified `buy` value is used for supplies.
2. A verified `sell` value is used for loot.
3. A missing side or item reports `0`.

Prices are **never guessed, estimated, or derived** from unrelated data. Every entry contains a source comment. `marketValue` is always `0` because the current Lua surface has no trustworthy market-price provider.

## Runtime access and script load order

Shared action, rune and event-callback scripts resolve the live `GameplayAnalytics` global when the event occurs. They do not reload the core with `dofile`. Reloading the core after context, batching, reliability and correctness wrappers are installed could silently replace wrapped functions while leaving installation flags set.

When the active data pack does not provide Analytics, the global is `nil` and integrations remain no-ops.

## Supply telemetry

### Potions

`data/scripts/actions/items/potions.lua` records supply use at the existing `player:updateSupplyTracker(item)` site immediately before the item is removed. This gives one recording point per consumed potion.

Items without a verified NPC buy price still record their amount with `unitValue = 0` rather than inventing a value.

### Runes

`data/scripts/runes/fireball.lua` and `data/scripts/runes/intense_healing_rune.lua` record one supply unit after a successful cast only when:

```lua
configManager.getBoolean(configKeys.REMOVE_RUNE_CHARGES)
```

This matches the server's `REMOVE_RUNE_CHARGES` setting. When rune charges are disabled, a successful cast still records spell telemetry, but it does not create fictional supply consumption or cost.

Rune supply rows use the configured rune item ID and verified NPC buy prices. Spell telemetry and supply telemetry remain separate aggregates and do not double-count one another.

### Ammunition

Ammunition is intentionally not integrated because some weapon scripts register multiple item IDs while the current callback does not reliably expose which exact item was consumed. Recording one of those IDs would be a guess.

## Loot telemetry

`data/scripts/eventcallbacks/monster/postdroploot_gameplay_analytics.lua` runs after the corpse has received generated loot. It reads the final contents with `Container:getItems(true)` so items in **nested containers** are included.

Loot is attributed only to the **corpse owner**, never to every party member. A corpse contains one physical set of items; assigning it to the whole party would multiply loot value by party size.

The helper `GameplayAnalyticsLoot.recordCorpseLoot` lives in `data/scripts/lib/gameplay_analytics_loot.lua` so this behavior can be tested without a running game engine.

## No duplicate counting

- Potions: one call immediately before actual removal.
- Runes: one call after a successful cast and only when `REMOVE_RUNE_CHARGES` is active.
- Loot: one call per physical item in the recursively enumerated corpse, attributed to one owner.

## Disabled by default

`trackSupplies` and `trackLoot` both default to `false`. Every call site goes through `recordSupply` / `recordLoot`, which no-op when tracking or Analytics is disabled.

## Aggregated, not per-event, writes

Supply and loot functions accumulate into the in-memory session. They do not issue SQL per potion, rune cast or item. Persistence remains bounded, batched and idempotent when a completed combat/death session is flushed.
