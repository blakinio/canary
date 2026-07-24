# OTS Forge Slot, Item Enhancement, and Equipment Proficiency

Status: design concept / future gameplay system

## Purpose

This document records the proposed redesign of long-term equipment progression discussed for the OTS roadmap.

The core design goal is to separate three concerns that are often conflated in a single upgrade system:

1. permanent character progression associated with an equipment slot;
2. numerical strengthening of a concrete item instance;
3. build-oriented perk selection that changes how a concrete item behaves.

The proposed architecture is:

- **Forge Slot Mastery** for permanent slot-tier progression and the existing Forge-style special effects;
- **Item Enhancement** for upgrading the base statistics of an individual item;
- **Equipment Proficiency** for choosing perks and specialisations for that item, with maximum progression constrained by item classification.

This is a design record only. Final values, costs, rates, caps, supported item classes, migration rules, and balancing must be validated against current server economy, combat telemetry, vocation balance, and upstream/current Tibia behaviour before implementation.

---

## 1. Problem statement

The current item-tier model has a structural weakness: long-term investment is attached primarily to a particular item instance.

When a stronger new best-in-slot item appears, the player may face an undesirable choice:

- keep using the old high-tier item despite owning a better base item;
- abandon months of Forge investment;
- pay an extremely high transfer cost;
- repeat a large part of the progression.

This can make acquiring new equipment feel like a penalty rather than a reward.

At the same time, simply moving all progression to the equipment slot would weaken item sinks and remove part of the value of upgrading individual items.

The preferred solution is therefore a layered model rather than a single replacement mechanic.

---

# 2. Three-layer equipment progression model

## 2.1 Forge Slot Mastery

Forge tier belongs to the **equipment slot / character progression**, not to the physical item.

Examples:

- Weapon Slot Tier -> Onslaught-style effect
- Armor Slot Tier -> Ruse-style effect
- Helmet Slot Tier -> Momentum-style effect
- Legs Slot Tier -> Transcendence-style effect
- Boots Slot Tier -> Amplification-style effect

Illustrative state:

```text
Character
├── Weapon Slot T7
├── Armor Slot T6
├── Helmet Slot T4
├── Legs Slot T3
└── Boots Slot T2
```

Replacing the equipped item does not reset the slot tier.

Example:

```text
Old armor equipped
Armor Slot T6 -> Ruse T6

replace armor

New armor equipped
Armor Slot T6 -> still Ruse T6
```

This makes Forge Slot Mastery a durable long-term achievement of the character.

### Design principle

> A new item should not invalidate months or years of slot progression.

---

## 2.2 Item Enhancement

A concrete item instance receives a separate enhancement level.

Example:

```text
Soulgarb +0
Soulgarb +1
...
Soulgarb +10
```

Enhancement improves the intrinsic statistics of that specific item.

Potential upgrade targets include, depending on item type:

### Weapons
- attack;
- elemental attack component;
- existing skill or magic modifiers;
- other bounded base-stat improvements.

### Armor
- armor value;
- existing protection values;
- small improvements to existing defensive attributes.

### Other slots
- only statistics appropriate to the item category.

Enhancement should not automatically add every possible bonus to every item.

The system should avoid excessive multiplicative power growth when combined with:

- Forge Slot Mastery;
- Equipment Proficiency;
- Charms;
- Prey;
- Bounty Talisman;
- imbuements;
- vocation systems.

### Design principle

> Enhancement makes the item numerically stronger; it does not define the player's build.

---

# 3. Item Classification as maximum development potential

Existing item classification can become the central limiter of how far an item may be developed.

Classification would represent not only a Forge category but the item's **maximum progression potential**.

Illustrative example only:

| Classification | Maximum Enhancement | Maximum Equipment Proficiency |
|---|---:|---:|
| Class 1 | +3 | Lv1 |
| Class 2 | +5 | Lv2 |
| Class 3 | +7 | Lv3 |
| Class 4 | +10 | Lv4 |

These numbers are placeholders, not final balance values.

This creates a clear hierarchy:

```text
higher classification
-> higher maximum enhancement
-> deeper proficiency tree
-> greater customisation potential
```

However, lower-class items should remain useful during progression because they are cheaper and faster to maximise.

A Class 2 item at its maximum may be an attractive temporary or budget option while the player is still developing a Class 4 item.

### Design principle

> Higher classification means greater ceiling, not automatic immediate superiority in every real player state.

---

# 4. Equipment Proficiency

Equipment Proficiency determines **how the item behaves**.

It is inspired by the general idea of the modern Weapon Proficiency model: progression unlocks increasingly advanced perk choices and additional specialisation depth.

It should not be a direct copy of any specific current interface or perk table.

The concept should be generalised to equipment categories.

Possible systems:

- Weapon Proficiency;
- Armor Proficiency;
- Helmet Proficiency;
- Legs Proficiency;
- Boots Proficiency.

Not every slot needs an equally large tree.

Weapon may have the deepest system, while armor and boots may use smaller, clearer perk structures.

---

# 5. Armor Proficiency example

Armor is the clearest example of how the system can create build diversity.

Instead of every enhanced armor automatically receiving reflect damage, sustain, resistance, and additional defense, the player chooses a path.

Possible branches:

## Fortification
Focus:

- physical mitigation;
- elemental resilience;
- emergency defense;
- bounded incoming-damage reduction.

## Retaliation
Focus:

- reflect/thorns-style mechanics;
- controlled retaliation procs;
- counterattack effects.

## Sustain
Focus:

- healing received;
- life sustain;
- mana sustain where appropriate;
- defensive recovery effects.

The player should not receive all branches at full strength simultaneously.

Choosing one direction should involve opportunity cost.

Example:

```text
Want stronger Retaliation?
-> give up part of maximum Fortification.

Want maximum Sustain?
-> do not also receive the strongest Retaliation package.
```

This produces real equipment builds instead of pure vertical stat stacking.

---

# 6. Reflect / Retaliation design

Reflect damage can be a valid armor specialisation, but unrestricted percentage reflection is dangerous in Tibia-style combat.

A player surrounded by many monsters receives many hits per second. A simple permanent percentage reflect can therefore create excessive passive DPS.

Potential controls:

- proc chance rather than reflection on every hit;
- internal cooldown;
- damage-per-second cap;
- diminishing returns when many attackers hit simultaneously;
- calculation from post-mitigation damage instead of raw incoming damage;
- different PvP rules;
- limited area retaliation instead of direct proportional reflect.

A preferred pattern may be **Retaliation** rather than unlimited classical reflect:

```text
When hit
-> X% chance to trigger Retaliation
-> controlled damage to attacker or limited nearby targets
-> internal cooldown / output cap
```

This is easier to balance than unconditional percentage reflection.

---

# 7. Proficiency level structure

A general progression could be:

## Lv1 - Foundation
Basic perk choice.

## Lv2 - Specialisation
The player's intended direction becomes clearer.

## Lv3 - Mastery
A stronger qualitative improvement and/or first major build-defining perk.

## Lv4 - Grandmaster / Classification 4 capstone
Reserved for the highest-potential items.

Lv4 should not simply be another linear percentage increase.

It should be a bounded qualitative capstone.

Examples:

- improved Retaliation behaviour;
- conditional defensive interaction;
- improved synergy with the chosen branch;
- a new mechanic with strict limits.

### Design principle

> Higher proficiency levels should increase specialisation depth, not merely stack more raw stats.

---

# 8. Example: Soulgarb for Monk

The following is a conceptual example of how a Class 4 Monk armor could participate in the system.

The exact current base statistics and final implementation must be verified from authoritative game/server data before coding.

Conceptual model:

```text
CHARACTER
│
├── Armor Forge Slot T6
│   └── Ruse T6
│
└── SOULGARB
    │
    ├── Classification 4
    │
    ├── Item Enhancement +10
    │   └── bounded improvements to intrinsic armor statistics
    │
    ├── Imbuements
    │
    └── Armor Proficiency Lv4
        ├── Lv1: Fortified Weave
        ├── Lv2: Retaliation
        ├── Lv3: Retaliation Mastery
        └── Lv4: Harmony of Retaliation
```

The names above are placeholders illustrating the architecture, not final perk names.

A second Monk using the same Soulgarb could instead select a sustain-oriented path.

Example:

```text
Soulgarb +10
Armor Proficiency Lv4
├── Meditative foundation
├── Inner Balance
├── Sustain Mastery
└── Sustain-oriented capstone
```

A third Monk could choose a defensive Fortification build.

Therefore:

> Two players can own the same base item and the same enhancement level while still using meaningfully different builds.

---

# 9. Separation of responsibilities

The three systems must remain conceptually distinct.

## Forge Slot Mastery
Answers:

> How developed is this equipment slot on the character?

Provides:

- permanent tier progression;
- Forge-style slot effect.

## Item Enhancement
Answers:

> How numerically developed is this concrete item instance?

Provides:

- bounded improvement to intrinsic item statistics.

## Equipment Proficiency
Answers:

> How does this item behave and what build does the player want?

Provides:

- perk selection;
- specialisation;
- capstones;
- playstyle differentiation.

This separation is the core of the proposal.

---

# 10. Enhancement materials

The Item Enhancement system may use a material-based model conceptually inspired by classic MMO upgrade systems such as Bless/Soul-style progression, without copying them directly.

Possible resource roles:

## Enhancement Crystal
General low/mid-tier upgrade material.

## Refined Crystal
Higher enhancement levels.

## Stabilization Core
Protects against degradation or reduces upgrade risk.

## Exalted Catalyst
Endgame enhancement material.

Names are placeholders.

The material economy should be integrated with the server's existing loot, economy, Forge, boss, Bounty, Drome, or dynamic encounter systems only after economy analysis.

---

# 11. Controlled RNG instead of unlimited punishment

RNG may make upgrades exciting, but the system should avoid unlimited destructive failure loops.

Preferred principles:

- early enhancement levels may be deterministic;
- higher levels may use controlled RNG;
- failure builds pity/stability progress;
- repeated failure increases future success probability or eventually guarantees success;
- protection items may prevent degradation;
- catastrophic destruction of extremely valuable items should generally be avoided.

Illustrative progression:

```text
+0 -> +3
mostly or fully deterministic

+4 -> +6
high success probability

+7 -> +9
controlled RNG + pity

+10
expensive endgame target with bounded failure
```

This is illustrative only.

### Design principle

> Luck may accelerate progression, but extreme bad luck must have a ceiling.

---

# 12. Item sink and duplicate items

Moving Forge tiers to slots reduces one source of item consumption, so Item Enhancement may preserve an item sink in a more controlled way.

Duplicate items could:

- increase enhancement success probability;
- replace a rare catalyst;
- reduce material cost;
- be required only for the highest enhancement milestone;
- contribute to an enhancement stability meter.

Example concept:

```text
Class 4 item +9 -> +10
may optionally or conditionally consume:
- endgame catalyst;
- duplicate item;
- large gold fee.
```

The design should avoid requiring repeated destruction of many identical ultra-rare best-in-slot items as the default progression path.

---

# 13. Salvage and replacement of old best-in-slot items

A new best-in-slot item should not erase all investment in the previous item.

Forge Slot Mastery already survives because it belongs to the slot.

Item Enhancement remains item-specific, but the player should be able to recover part of the investment.

Possible **Enhancement Salvage**:

```text
Old item +10
-> salvage
-> recover a bounded percentage of enhancement resources
```

Recovery should not be 100%, because changing equipment should remain an economic sink.

The goal is:

> changing to a new item has a cost, but does not delete all previous progress.

---

# 14. Interaction with Weapon Proficiency

The existing/current concept of Weapon Proficiency provides a useful model for item-specific build progression.

The proposal extends the same broad design philosophy beyond weapons while avoiding a literal copy.

Potential structure:

```text
Weapon
-> offensive / elemental / utility / mastery choices

Armor
-> fortification / retaliation / sustain choices

Helmet
-> cooldown / mana / utility choices

Legs
-> resistance / mobility / reactive defense choices

Boots
-> movement / positioning / dodge / amplification choices
```

The exact categories must be designed per slot and vocation.

---

# 15. Interaction with item classification

Classification determines maximum depth.

Example:

```text
Class 1 armor
-> basic proficiency only

Class 2 armor
-> first meaningful specialisation

Class 3 armor
-> mastery depth

Class 4 armor
-> full tree and Lv4 capstone
```

This gives classification a clear player-facing purpose:

> it defines how far the item can ultimately be developed.

---

# 16. Interaction with imbuements

Imbuements should remain a separate system.

Possible conceptual distinction:

- Forge Slot Mastery = permanent slot progression;
- Item Enhancement = intrinsic stat growth;
- Equipment Proficiency = build identity;
- Imbuements = temporary or replaceable utility/combat modifiers.

The systems should not duplicate the exact same bonuses excessively.

For example, if an armor proficiency branch heavily improves sustain, the interaction with life/mana leech imbuements must be simulated.

---

# 17. Interaction with other long-term systems

The full power budget must consider:

- Forge Slot effects;
- Item Enhancement;
- Equipment Proficiency;
- Weapon Proficiency;
- imbuements;
- Wheel/vocation systems;
- Charms;
- Prey;
- Bounty Talisman;
- consumables;
- party buffs;
- future systems.

No single subsystem can be balanced in isolation.

Particularly dangerous combinations include:

```text
high Item Enhancement
+ high Forge Slot tier
+ offensive proficiency
+ Charm damage
+ Bounty target bonus
+ Prey damage
```

Similarly defensive stacking must be examined for effective immortality or excessive sustain.

---

# 18. Economy goals

The system should support several economic functions:

## Gold sink
Enhancement, proficiency reconfiguration, or high-end progression may consume gold.

## Material sink
Upgrade resources leave circulation.

## Item sink
Duplicates may have value in high-end enhancement without being universally mandatory.

## Long-term demand
Older relevant Class 3/4 items may retain economic value as enhancement inputs, alternative builds, or transitional equipment.

Economy telemetry is required to prevent:

- runaway scarcity;
- excessive destruction of rare items;
- impossible entry costs for new players;
- uncontrolled inflation of upgrade materials.

---

# 19. Migration considerations

If a live server already contains tiered items, migration requires a separate design.

Possible questions:

- Does the highest owned/equipped item tier seed Slot Mastery?
- How are multiple tiered items handled?
- Are existing tiers converted into slot progression, materials, or compensation?
- How are tradable tiered items migrated?
- Can migration duplicate permanent power across multiple characters?

No migration rule should be chosen without auditing existing player inventories and economy state.

---

# 20. UI concept

The equipment UI should clearly separate the three systems.

Example item detail panel:

```text
SOULGARB
Classification: 4

BASE ITEM
- normal item statistics

FORGE SLOT
- Armor Slot Tier: T6
- Effect: Ruse T6

ITEM ENHANCEMENT
- Enhancement: +10
- Maximum: +10 (Class 4)

ARMOR PROFICIENCY
- Level: Lv4
- selected perk path
- active capstone
```

The Equipment Proficiency view may use a progression-tree interface conceptually similar to Weapon Proficiency, with:

- progression levels;
- perk nodes;
- branches;
- one or more perk-selection slots;
- clear lock/unlock requirements;
- classification ceiling shown visibly.

The UI must make it obvious which power comes from:

- the character's slot;
- the physical item;
- selected perks.

---

# 21. Recommended implementation posture

Do not implement the full system in one step.

Suggested sequence:

1. audit current Forge and Weapon Proficiency implementation/state;
2. catalogue all equipment classifications and supported slots;
3. build telemetry/simulation model;
4. prototype Slot Forge progression independently;
5. prototype Item Enhancement with one equipment category;
6. prototype Armor Proficiency on a small representative set;
7. test vocation balance and multi-system stacking;
8. model economy and item-sink effects;
9. design migration only after the target model is stable;
10. expand to other equipment slots incrementally.

A high-class armor such as Soulgarb can serve as a design example, but implementation should begin with a controlled test matrix rather than balancing around one item.

---

# 22. Open design questions

The following remain intentionally unresolved:

- exact maximum enhancement per classification;
- exact number of proficiency levels;
- whether proficiency belongs to the item type, item instance, item family, or character-item relationship;
- whether selected perks are freely respecable, gold-costed, cooldown-limited, or use another resource;
- exact effect and caps of Retaliation/Reflect;
- whether duplicate items are required or only optional accelerators;
- exact pity/stability formula;
- salvage percentage;
- exact migration from existing item tiers;
- which current Forge resources remain relevant;
- how Weapon Proficiency and broader Equipment Proficiency share or separate resources;
- whether Class 4 Lv4 capstones are universal or item-specific;
- which systems may modify base stats versus derived combat stats.

These must be answered through source-of-truth audit, combat simulation, economy modelling, and playtesting.

---

# 23. Final design principle

The preferred equipment progression model is:

```text
FORGE SLOT MASTERY
permanent character/slot progression
special Forge effects

+

ITEM ENHANCEMENT
concrete item numerical development
bounded +0...+N progression

+

EQUIPMENT PROFICIENCY
perk selection and build identity
maximum depth based on item classification
```

In one sentence:

> **Forge defines how developed the slot is, Enhancement defines how strong the item is, and Proficiency defines how the item plays.**

This separation preserves long-term progression when equipment changes while retaining item investment, gold/material sinks, and meaningful build diversity.
