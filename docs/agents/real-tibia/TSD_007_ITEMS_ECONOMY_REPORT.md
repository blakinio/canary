# TSD-007 — Items and Economy Decomposition

> Task-start main: `821f213038770d68cd95b1b22afa78937b974210`.
> Inventory only; no item, economy, persistence, runtime, protocol or parity claim.

## Result

Registry grows from **45** to **49** records. Existing records remain unchanged.

Added only:

- `item-definitions`;
- `item-instances`;
- `containers`;
- `item-decay`.

Preserved unchanged:

- `market`;
- `imbuements`;
- `exaltation-forge`;
- `weapons`;
- `boss-encounters`;
- `player-persistence`;
- `world-persistence`;
- `protocol`.

## Evidence inventory

### Item definitions

`Items`/`ItemType` load and reload appearance protobuf and items XML, map static categories/flags/abilities/market metadata, and provide ID/name lookup. This is a durable registry boundary distinct from runtime Item objects.

### Item instances

`Item` owns factory/subtype creation, attributes, custom attributes, clone/equality/transform state and serialization boundaries. Attribute/serializer presence is not proof of persistence completeness or move safety.

### Containers

`Container`/`Cylinder` own nested item membership, capacity, query/add/remove/update operations, traversal depth/cycle handling, depots, inboxes, mailboxes and reward containers. Those subclasses share one lifecycle.

### Item decay

`Decay` has an independent scheduler-backed start/stop/check/transform lifecycle over ordered duration buckets.

## Candidate decisions

| Candidate | Decision | Reason |
|---|---|---|
| `item-definitions` | `ADD_NOW` | independent ItemType registry and load/reload lifecycle |
| `item-instances` | `ADD_NOW` | runtime factory, attributes, transforms and serializer boundary |
| `containers` | `ADD_NOW` | independent nested cylinder/container lifecycle and subtype family |
| `item-decay` | `ADD_NOW` | independent scheduled duration/transform state machine |
| `item-movement` | `MERGE_WITH_ANOTHER_MODULE` | orchestration spans Game/Cylinder/Container; no one narrow root |
| `item-stacking` | `MERGE_WITH_ANOTHER_MODULE` | item/container capability |
| `item-attributes` | `MERGE_WITH_ANOTHER_MODULE` | capability inside `item-instances` |
| `item-serialization` | `MERGE_WITH_ANOTHER_MODULE` | item/container/persistence capability |
| `depots` | `MERGE_WITH_ANOTHER_MODULE` | container subtype |
| `inbox-mailbox` | `MERGE_WITH_ANOTHER_MODULE` | container subtypes |
| `reward-containers` | `MERGE_WITH_ANOTHER_MODULE` | container subtype interacting with `boss-encounters` |
| `stash-managed-containers` | `MERGE_WITH_ANOTHER_MODULE` | cross-cutting container/player/game capability |
| `weapons` | `ALREADY_COVERED` | preserve TSD-005 record |
| `market` | `ALREADY_COVERED` | preserve market listing/trade record |
| `imbuements` | `ALREADY_COVERED` | preserve independent system |
| `exaltation-forge` | `ALREADY_COVERED` | preserve independent system |
| `boss-rewards` | `ALREADY_COVERED` | encounter scoring/rewards remain `boss-encounters` |
| `account-coins` | `DEFER_TO_NEXT_PACKAGE` | account/store/payment economy needs a dedicated bounded source inventory |
| `npc-trade` | `DEFER_TO_NEXT_PACKAGE` | NPC shop surface spans NPC/Lua/item economy and lacks a single narrow root here |
| individual item/container types | `REJECT_AS_TOO_GRANULAR` | entries/subclasses inside shared lifecycles |

## Dependencies

- `item-instances` depends on `item-definitions`.
- `containers` depends on `item-instances`.
- `item-decay` depends on `engine-scheduler` and `item-instances`.
- `item-definitions` has no fundamental dependency edge.

All records begin at lifecycle/implementation/evidence `inventory`; all other maturity dimensions remain `not-assessed`.

## Discovery expectations

```text
src/items/items.cpp
  → item-definitions
src/items/item.cpp
  → item-instances
src/items/containers/container.cpp
  → containers
src/items/decay/decay.cpp
  → item-decay
data/items/items.xml
  → item-definitions
```

Source-role-aware mapping must include these through server/data buckets and must not apply server modules to client sources. Client `src/**` continues to map only through the configured client policy.

## Evidence limits

TSD-007 does not prove item metadata, appearance, price or category parity; movement/stacking/transfer atomicity; duplication/loss safety; container cycle/capacity correctness; serializer completeness; decay timing/restart behavior; market/Forge/Imbuement/weapon/boss-reward correctness; protocol compatibility; runtime behavior; physical-client E2E; Real Tibia parity or Oteryn readiness.

## Next package

After feature merge and lifecycle archive:

```text
task: CAN-20260714-tibia-system-decomposition-world-content
package: TSD-008
branch: docs/tibia-system-decomposition-world-content
```
