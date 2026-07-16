# TSD-005 — Combat, Weapons and Vocations Decomposition

> Status: bounded inventory for `blakinio/canary`.
> Task-start main: `f163ed8e3b3d51e65c7fef1bc03830b12b2e6bfa`.
> This report is decision evidence for the canonical registry. It does not prove combat formulas, targeting legality, condition behavior, weapon parity, runtime correctness or client compatibility.

## Result

TSD-005 preserves the existing broad combat and progression records and adds only two independent boundaries with stable source roots.

- Registry records before: **39**.
- New records: **2**.
- Registry records after: **41**.
- Existing module records modified: **0**.
- Category/schema/generator/mapper/workflow changes: **none**.
- Runtime/gameplay/protocol/database/client/map/asset changes: **none**.

Records added:

1. `combat-conditions`;
2. `weapons`.

Stable records preserved unchanged:

- `combat`;
- `spells`;
- `vocations`;
- `weapon-proficiency`;
- `character-progression`;
- `player-persistence`;
- `protocol`.

## Preflight and concurrent work

Open PRs at task start:

| PR | Area | TSD-005 treatment |
|---|---|---|
| #360 | received leave-game dispatch/session cleanup | read-only; currently only its task record is changed and any later protocol/runtime expansion remains outside TSD-005 |
| #316 | Targuna donor map/content audit | read-only; no map, OTBM or content change |
| #245 | shared physical-client E2E platform | read-only; no scenario or orchestrator change |

No open PR claims `docs/agents/real-tibia/**` or the new TSD-005 report/module/test paths. `ACTIVE_WORK.md` remains read-only.

## Current-main evidence inventory

### Existing combat umbrella

`src/creatures/combat/combat.*` combines:

- area and chain target selection;
- callback-driven value calculation;
- health and mana combat dispatch;
- condition/dispel application;
- PvP-zone, protection and target permission checks;
- armor/shield blocking flags;
- damage/healing extension and ordering hooks;
- combat effects and origin handling.

Those responsibilities share one central class and source root. TSD-005 therefore preserves `combat` as the compatibility/discovery umbrella rather than inventing helper-level modules for each function family.

### Combat conditions

`src/creatures/combat/condition.*` defines an independent condition lifecycle:

- factory creation from condition type or serialized state;
- start, timed execution, refresh/merge and end hooks;
- clone and parameter configuration;
- persistent-condition and removable-on-death state;
- serialization/unserialization;
- generic, attribute, regeneration, mana-shield, damage-over-time and vocation-specific condition subclasses.

The condition hierarchy has its own state machine and serialization boundary, so it receives a narrow `combat-conditions` record. Individual condition classes remain implementations inside that lifecycle.

### Weapons

`src/items/weapons/weapons.*` defines an independent weapon subsystem:

- registry and Lua/XML event registration;
- item-to-weapon resolution;
- wield, level, magic-level, premium and vocation checks;
- melee, distance and wand implementations;
- damage/element calculation surfaces;
- mana, health, soul, charges, break chance and item-count consumption;
- combat and chain handoff;
- Weapon Proficiency integration.

`data/scripts/weapons/**` provides weapon script definitions and is a verified current data root. The subsystem therefore receives a narrow `weapons` record.

### Existing spells, vocations and Weapon Proficiency

`spells` already owns spell/rune registration, cooldowns, areas, vocation restrictions and runtime execution.

`vocations` already owns the vocation registry, promotion relation and growth/regeneration configuration.

`weapon-proficiency` already owns proficiency definitions, experience, perks, mastery, KV persistence and achievement interaction.

TSD-005 does not duplicate or rewrite those identities.

## Candidate decisions

| Candidate | Decision | Result / reason |
|---|---|---|
| `combat` | `ALREADY_COVERED` | preserve the existing broad combat engine record |
| `combat-targeting` | `MERGE_WITH_ANOTHER_MODULE` | area, chain and target selection share `combat.*` |
| `combat-permissions` | `MERGE_WITH_ANOTHER_MODULE` | PvP/protection/can-target/can-combat checks share `combat.*` |
| `combat-formulas` | `MERGE_WITH_ANOTHER_MODULE` | value callbacks and damage/healing calculation remain combat capabilities |
| `damage-healing` | `MERGE_WITH_ANOTHER_MODULE` | health/mana dispatch is part of the combat pipeline |
| `combat-mitigation` | `MERGE_WITH_ANOTHER_MODULE` | armor, shield, resistance and absorption ordering span combat/creature/player call sites; no stable independent root |
| `combat-ordering` | `MERGE_WITH_ANOTHER_MODULE` | pipeline property of `combat`, not a standalone lifecycle |
| `combat-areas` | `MERGE_WITH_ANOTHER_MODULE` | `MatrixArea` and `AreaCombat` are implementations inside `combat.*` |
| `combat-chains` | `MERGE_WITH_ANOTHER_MODULE` | chain callbacks/selection remain combat capabilities |
| `critical-leech` | `MERGE_WITH_ANOTHER_MODULE` | combat modifier capability spanning combat/player/equipment, not a stable root |
| `combat-conditions` | `ADD_NOW` | independent condition state machine, subclasses and serialization lifecycle |
| `buffs-debuffs` | `MERGE_WITH_ANOTHER_MODULE` | condition instances/types inside `combat-conditions` |
| `damage-over-time` | `MERGE_WITH_ANOTHER_MODULE` | `ConditionDamage` capability |
| `regeneration` | `MERGE_WITH_ANOTHER_MODULE` | `ConditionRegeneration` capability |
| `mana-shield` | `MERGE_WITH_ANOTHER_MODULE` | condition subtype/capability |
| `condition-persistence` | `MERGE_WITH_ANOTHER_MODULE` | serialization capability of `combat-conditions` and player persistence |
| `weapons` | `ADD_NOW` | independent registry, use/wield/resource/formula lifecycle and stable source/data roots |
| `melee-weapons` | `MERGE_WITH_ANOTHER_MODULE` | implementation class inside `weapons` |
| `distance-weapons` | `MERGE_WITH_ANOTHER_MODULE` | implementation class inside `weapons` |
| `wands` | `MERGE_WITH_ANOTHER_MODULE` | implementation class inside `weapons` |
| `weapon-permissions` | `MERGE_WITH_ANOTHER_MODULE` | wield/use checks inside `weapons`, interacting with vocations |
| `weapon-formulas` | `MERGE_WITH_ANOTHER_MODULE` | calculation capability inside `weapons` and `combat` |
| `weapon-resource-consumption` | `MERGE_WITH_ANOTHER_MODULE` | use lifecycle capability inside `weapons` |
| `runes` | `ALREADY_COVERED` | spell/rune registration remains in `spells`; item-use details remain shared with weapons/items |
| `spells` | `ALREADY_COVERED` | preserve existing spell system record |
| `vocations` | `ALREADY_COVERED` | preserve existing vocation registry record |
| `weapon-proficiency` | `ALREADY_COVERED` | preserve existing independent proficiency record |
| `vocation-combat-modifiers` | `MERGE_WITH_ANOTHER_MODULE` | interaction between `vocations` and `combat`; no new lifecycle |
| `monk-harmony` | `MERGE_WITH_ANOTHER_MODULE` | vocation/combat/condition capability, not a separate subsystem |
| `monk-virtues` | `MERGE_WITH_ANOTHER_MODULE` | vocation/combat capability, not a separate subsystem |

## Relationships

Only fundamental dependencies are encoded:

- `combat-conditions` depends on `combat`;
- `weapons` depends on `combat`.

All other relationships are descriptive interactions. The existing records remain unchanged and the dependency graph remains acyclic.

## Maturity

Both new records start with:

```text
lifecycle: inventory
implementation: inventory
evidence: inventory
persistence: not-assessed
protocol: not-assessed
automated_tests: not-assessed
runtime_validation: not-assessed
gameplay_e2e: not-assessed
```

Existing tests or source structure are evidence pointers only and do not promote maturity.

## Discovery boundaries

Representative expected server lookups:

```text
src/creatures/combat/condition.cpp
  → combat
  → combat-conditions

src/items/weapons/weapons.cpp
  → weapons

data/scripts/weapons/example.lua
  → weapons

src/creatures/combat/combat.cpp
  → combat only

src/creatures/combat/spells/spell.cpp
  → combat
  → spells
```

Source-role-aware mapping requirements:

- server sources may discover `combat`, `combat-conditions`, `weapons`, `spells`, `vocations` and `weapon-proficiency` through server/data/test/doc buckets;
- client sources must not receive these server-only records through broad client patterns;
- `triage_status` and reviewed decision state remain unchanged;
- module IDs and mapped paths remain deterministic;
- path matches remain discovery hints, not ownership.

## Evidence limits

TSD-005 does **not** prove:

- target legality or PvP/protection correctness;
- damage, healing, critical, leech, mitigation, armor or shield formulas;
- combat ordering and callback correctness;
- condition timing, stacking, dispel, serialization or persistence correctness;
- weapon hit chance, damage, elemental, resource, charge or break formulas;
- vocation restrictions or promotion behavior;
- spell/rune behavior;
- Weapon Proficiency integration correctness;
- protocol or maintained-client compatibility;
- production runtime behavior;
- physical-client E2E;
- Real Tibia parity;
- Oteryn readiness.

## Next package

After feature merge and a separate lifecycle archive, TSD-006 must start from then-current `main`:

```text
task: CAN-20260714-tibia-system-decomposition-creatures-hunting-raids-bosses
package: TSD-006
branch: docs/tibia-system-decomposition-creatures-hunting-raids-bosses
```

TSD-006 should preserve `spawns`, `prey`, `bestiary`, `bosstiary`, `cyclopedia` and the TSD-005 combat boundaries while evaluating creature definitions, AI, hunting/credit, boss encounters, raids and scheduling.