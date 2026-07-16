# TSD-006 — Creatures, Hunting, Raids and Bosses Decomposition

> Task-start main: `f68f826915882b0b20081b8fca5ed975ce303f45`.
> Inventory only. No gameplay, runtime, parity, reward, scheduling or E2E claim.

## Result

Registry records grow from **41** to **45**. Existing records are unchanged.

Added only:

- `creature-definitions`;
- `creature-ai`;
- `boss-encounters`;
- `raids`.

Preserved unchanged:

- `spawns`;
- `prey`;
- `bestiary`;
- `bosstiary`;
- `cyclopedia`;
- `combat`;
- `combat-conditions`;
- `weapons`;
- `player-persistence`.

## Evidence inventory

### Creature definitions

`MonsterType` and `Monsters` form a stable registry for names, combat traits, spells, loot, summons, immunities, Bestiary/Bosstiary metadata, targeting strategies and creature flags. Active monster definitions live under `data-otservbr-global/monster/**` and `data-canary/monster/**`.

This boundary owns definition discovery only. It does not prove that a creature is spawnable, reachable, correctly scripted, correctly balanced or equivalent to official Tibia.

### Creature AI

`Monster` has an independent runtime state machine for think ticks, target/friend lists, target selection, follow/flee/path steps, movement refresh, attacking, spawn/despawn and summon ownership interactions.

These paths are separate from definition loading, static spawn placement and generic combat formulas. Async refresh and weak-reference handling are implementation inventory, not thread-safety proof.

### Boss encounters

`data/libs/systems/reward_boss.lua` and `data/scripts/systems/reward_chest.lua` implement reward-boss encounter participation, damage/healing contribution tracking, target-list reconciliation, boss-death scoring, reward generation and reward-container persistence handoff.

This boundary excludes Bosstiary points/slots, generic boss definitions and AI, spawn scheduling, quest access/cooldowns and encounter-specific levers. It does not prove participant eligibility, score arithmetic, loot distribution or transactional safety.

### Raids

`Raids` and `Raid` define a separate load/start/check/run/reset/reload state machine. The subsystem schedules periodic raid selection and ordered announce, single-spawn, area-spawn and script events through the shared dispatcher.

Static placement and general dynamic creation remain in `spawns`. Individual raid definitions remain data entries, not modules.

## Candidate decisions

| Candidate | Decision | Reason |
|---|---|---|
| `creature-definitions` | `ADD_NOW` | independent MonsterType/Monsters registry and stable data roots |
| `creature-ai` | `ADD_NOW` | independent Monster runtime think/target/movement/attack state machine |
| `boss-encounters` | `ADD_NOW` | durable participation/scoring/reward lifecycle |
| `raids` | `ADD_NOW` | independent registry, scheduling and ordered-event state machine |
| `monster-types` | `MERGE_WITH_ANOTHER_MODULE` | implementation inside `creature-definitions` |
| `monster-spells` | `MERGE_WITH_ANOTHER_MODULE` | definition capability interacting with combat/spells |
| `monster-loot` | `MERGE_WITH_ANOTHER_MODULE` | definition/encounter capability, not a separate registry root |
| `monster-summons` | `MERGE_WITH_ANOTHER_MODULE` | definition and AI capability |
| `target-selection` | `MERGE_WITH_ANOTHER_MODULE` | `creature-ai` capability |
| `pathfinding-fleeing` | `MERGE_WITH_ANOTHER_MODULE` | `creature-ai` capability |
| `spawn-placement` | `ALREADY_COVERED` | preserve `spawns` |
| `dynamic-creation` | `ALREADY_COVERED` | preserve `spawns` inventory |
| `hunting-tasks` | `ALREADY_COVERED` | preserve `prey` |
| `prey` | `ALREADY_COVERED` | preserve `prey` |
| `bestiary-credit` | `ALREADY_COVERED` | preserve `bestiary` |
| `bosstiary-credit` | `ALREADY_COVERED` | preserve `bosstiary` |
| `boss-definitions` | `MERGE_WITH_ANOTHER_MODULE` | boss entries inside `creature-definitions` |
| `boss-ai` | `MERGE_WITH_ANOTHER_MODULE` | runtime behavior inside `creature-ai` |
| `boss-reward-eligibility` | `MERGE_WITH_ANOTHER_MODULE` | finding inside `boss-encounters` |
| `boss-score` | `MERGE_WITH_ANOTHER_MODULE` | finding inside `boss-encounters` |
| `boss-loot` | `MERGE_WITH_ANOTHER_MODULE` | reward generation inside `boss-encounters` |
| `boss-cooldowns` | `DEFER_TO_NEXT_PACKAGE` | encounter/quest-specific access state lacks one generic root |
| `raid-scheduling` | `MERGE_WITH_ANOTHER_MODULE` | lifecycle inside `raids` |
| `raid-announcements` | `MERGE_WITH_ANOTHER_MODULE` | raid event type |
| `raid-spawns` | `MERGE_WITH_ANOTHER_MODULE` | raid event type interacting with `spawns` |
| individual creature/boss/raid names | `REJECT_AS_TOO_GRANULAR` | data entries, not durable module boundaries |

## Relationships

- `creature-ai` depends on `creature-definitions`.
- `boss-encounters` depends on `creature-definitions` and `player-persistence`.
- `raids` depends on `creature-definitions` and `engine-scheduler`.
- `creature-definitions` has no fundamental dependency edge.

All new records start at lifecycle/implementation/evidence `inventory`; persistence, protocol, automated tests, runtime validation and gameplay E2E remain `not-assessed`.

## Discovery expectations

```text
src/creatures/monsters/monsters.cpp
  → creature-definitions

src/creatures/monsters/monster.cpp
  → creature-ai

data-otservbr-global/monster/bosses/example.lua
  → creature-definitions

data/scripts/systems/reward_chest.lua
  → boss-encounters

src/lua/creature/raids.cpp
  → raids

data/raids/raids.xml
  → raids
```

Server source mapping must not apply the broad client `protocol` bucket. Client-source `src/**` behavior remains governed by the existing explicit client policy. Mapping remains deterministic and discovery-only.

## Evidence limits

This package does not prove AI correctness, pathfinding, target choice, spawn timing, boss eligibility/scoring/reward formulas, raid probability/order/timing, Bestiary/Bosstiary/Prey credit, persistence safety, protocol compatibility, runtime behavior, physical-client E2E, Real Tibia parity or Oteryn readiness.

## Next package

After feature merge and lifecycle archive:

```text
task: CAN-20260714-tibia-system-decomposition-items-economy
package: TSD-007
branch: docs/tibia-system-decomposition-items-economy
```
