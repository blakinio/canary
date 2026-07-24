# OTS Charm, Bestiary and Drome Mastery Design

Status: design record / future gameplay direction

This document preserves the current product direction for a deeper Charm and Bestiary progression system and its integration with Tibiadrome rewards. It is intentionally a design contract, not an implementation specification. Exact formulas, costs, caps and balance values require telemetry and simulation before implementation.

## 1. Product intent

The goal is to evolve Bestiary and Charms from a mostly binary completion-and-assignment loop into a long-term creature knowledge and mastery system.

The design should:

- reward partial Bestiary progress instead of placing all value at full completion;
- make the player's knowledge of a specific creature matter to the Charm level usable against that creature;
- create a meaningful endgame Charm mastery layer without turning it into unlimited vertical power creep;
- remove repetitive manual Charm reassignment when changing hunting grounds;
- preserve strategic choice through active loadouts and limited simultaneous assignments;
- give full creature-family completion a durable purpose;
- integrate existing Drome Charm boost rewards as temporary amplifiers rather than progression shortcuts;
- keep Charm progression understandable at the UI level while allowing deeper rules underneath.

## 2. Bestiary stages should award partial Charm Points

A Bestiary entry may have several kill milestones before full completion. The current design direction is that Charm Points should not be withheld entirely until the final kill threshold.

Instead, the total Charm Point value of a creature should be distributed across its Bestiary milestones.

Illustrative model only:

- Stage 1: first portion of total Charm Points;
- Stage 2: second portion;
- Full Bestiary: largest remaining portion.

A possible starting distribution for balancing analysis is 20% / 30% / 50%, but these numbers are not final.

The total Charm Points available from the creature should remain unchanged unless a separate rebalance explicitly changes it. The primary change is when the reward is delivered.

This removes the hard reward cliff where a player can make substantial progress toward a long Bestiary entry while receiving no Charm Point progression until the final milestone.

Full completion must still remain the most valuable milestone.

## 3. Bestiary knowledge gates effective Charm level on a creature

Charm ownership and Charm effectiveness against a creature should be treated as separate concepts.

A player may globally own or upgrade a Charm to a high level, but the effective level usable against a specific creature is capped by the player's Bestiary knowledge of that creature.

Proposed mapping:

- Bestiary Stage 1 -> maximum effective Charm Level 1 against that creature;
- Bestiary Stage 2 -> maximum effective Charm Level 2;
- Full Bestiary -> maximum effective Charm Level 3 / Mastery;
- Full Bestiary plus qualifying Creature Family Mastery -> eligibility for Charm Level 4 / Grandmaster against that creature.

Example:

A player owns Freeze Level 4 globally.

- Creature A is only at Stage 1: Freeze works as Level 1.
- Creature B is at Stage 2: Freeze works as Level 2.
- Creature C has Full Bestiary: Freeze works as Level 3.
- Creature D has Full Bestiary and the player has mastered its qualifying creature family: Freeze may work as Level 4.

This creates the core rule:

> The player cannot be a Grandmaster against a creature they have not personally learned in depth.

Family Mastery must therefore not bypass the Full Bestiary requirement of the specific target creature.

## 4. Charm progression levels

The preferred progression model is four conceptual levels.

### Level 1 - Unlock

The base Charm effect.

### Level 2 - Improved

A stronger version of the same core effect.

### Level 3 - Mastery

The full standard version of the Charm plus a meaningful qualitative capstone where appropriate.

Level 3 should feel more important than another small linear percentage increase.

### Level 4 - Grandmaster / Ascended

A rare endgame specialization tier.

Level 4 should not simply mean "more percentage". It should provide a carefully bounded qualitative enhancement, synergy or specialized behavior.

Level 4 should be expensive and optional. It should reward long-term specialization without making every Charm Level 4 mandatory.

The technical design should support Level 4 even if initial gameplay rollout keeps only Levels 1-3 active until the balance model is validated.

## 5. Creature Family Mastery

Full Bestiary completion should contribute to mastery of broader creature families or classes, for example Demon, Undead or another taxonomy supported by the game's authoritative data model.

The intended relationship is:

- Full Bestiary of the specific creature -> Level 3 eligibility on that creature;
- qualifying mastery of the creature's family -> Level 4 eligibility on fully completed members of that family.

Family Mastery should provide a durable achievement and a reason to complete related Bestiary entries beyond immediate Charm Point needs.

The exact requirement should not necessarily be literal 100% completion of every creature that ever belongs to the family. Event-only, inaccessible, newly added or exceptional creatures can otherwise make the system brittle.

Preferred direction:

- define a stable qualifying family pool or weighted completion threshold;
- once earned, Family Mastery should not be revoked merely because a future update adds a new creature;
- new creatures may extend optional progression without invalidating previously earned mastery.

## 6. Charm Points and Bestiary Effort

The existing broad creature difficulty labels are not necessarily sufficient to represent the real effort required to complete Bestiary.

Future analysis should consider a Bestiary Effort Score using signals such as:

- required kills;
- realistic kills per hour;
- spawn density and capacity;
- number of viable hunting grounds;
- access requirements;
- mixed-spawn share of the target creature;
- rarity or time restrictions.

This can be used to audit whether Charm Point rewards are reasonably aligned with actual completion effort.

It should not be used to dynamically rewrite rewards in an opaque or unstable way without a clear balance policy.

## 7. Persistent creature assignments and Charm loadouts

Players should not need to manually rebuild Charm assignments every time they change hunting grounds.

Preferred model:

### Persistent creature preference

The game remembers the player's preferred Major and Minor Charm configuration for a creature.

Returning to that creature later should not require rebuilding the configuration from scratch.

### Active Charm loadouts

Strategic limitations remain through a limited number of simultaneously active assignments or an active hunting-ground loadout.

Example loadouts:

- Asuras;
- Library;
- Demons;
- Bounty;
- custom player-defined hunting spots.

Changing hunting grounds should require at most switching one loadout, not individually reassigning every creature.

Potential safety rules:

- loadout switching only outside combat;
- optionally only in a Protection Zone;
- optional cooldown where necessary;
- Huntfinder or Hunting Spot systems may recommend a loadout, but should not silently remove player agency.

This preserves meaningful Charm choices while removing repetitive administrative friction.

## 8. Major and Minor Charm philosophy

The Major / Minor split is a useful foundation and should be preserved.

Preferred high-level roles:

- Major Charms: meaningful combat or hunt-efficiency effects;
- Minor Charms: utility, sustain, movement, control or supporting effects.

Minor Charms should generally not become a second unrestricted major-DPS layer.

Level 3 Mastery and Level 4 Grandmaster effects may introduce bounded Major-Minor synergies, but these should be designed to avoid one mandatory spreadsheet-optimal combination.

## 9. Level 3 should have a capstone identity

Level 3 should provide more than a routine linear stat increase.

Design principle:

- Level 1 establishes the Charm;
- Level 2 improves its core value;
- Level 3 completes standard mastery and may add a bounded qualitative capstone.

Examples of possible capstone categories, not final effects:

- an offensive Charm gains a small conditional secondary interaction;
- a sustain Charm gains a bounded efficiency behavior;
- a defensive Charm gains a small follow-up effect after a successful proc;
- a Minor Charm gains a controlled interaction with the active Major Charm.

Each Charm requires separate design and balance review. Capstones must not invalidate vocation balance or create mandatory combinations.

## 10. Level 4 should represent Grandmaster specialization

Level 4 should be a long-term endgame objective gated by both Charm progression and creature knowledge.

Baseline eligibility concept:

- the player owns the Charm at Level 4;
- the target creature has Full Bestiary;
- the relevant Creature Family Mastery is unlocked.

Additional endgame requirements may be considered, but should not make lower-level Charm progression dependent on unrelated content.

Level 4 should emphasize horizontal specialization and qualitative identity rather than unlimited percentage scaling.

## 11. Tibiadrome Charm potions as temporary amplifiers

Existing Drome rewards that boost Charms should be integrated into the mastery system rather than removed.

Core rule:

> A Drome Charm potion amplifies the Charm power the player has legitimately unlocked; it does not bypass Bestiary or Family Mastery gates.

Examples:

- if a Charm is globally Level 3 but the creature is only at Bestiary Stage 2, a potion must not make it behave as Level 3 or Level 4 against that creature;
- if the creature permits Level 3, the potion may temporarily enhance the Level 3 effect within defined caps;
- if the player legitimately has Level 4 eligibility, a potion may enhance that Grandmaster configuration without creating a Level 5 progression tier.

The potion is therefore an amplifier, not a shortcut.

## 12. Potential Drome potion categories

Future balancing may consider more specialized Charm boosters instead of one generic effect.

Possible categories:

### Charm Power Potion

Temporarily enhances supported offensive Major Charms.

### Charm Guard Potion

Temporarily enhances supported defensive Charm effects.

### Charm Echo Potion

Temporarily enhances supported Minor Charms.

### Charm Mastery Potion

A rarer booster for Mastery / Grandmaster configurations that strengthens an already unlocked effect without bypassing the player's creature-knowledge ceiling.

These are design possibilities, not committed item definitions.

## 13. Optional Drome role in Level 4 progression

A future option is to make Drome contribute a rare Grandmaster progression component, for example a catalyst.

Possible eligibility stack:

- Charm Points -> primary Charm progression currency;
- Full Bestiary -> creature-specific knowledge;
- Creature Family Mastery -> Grandmaster eligibility;
- optional Drome Grandmaster Catalyst -> endgame specialization component.

Important constraint:

Drome should not be mandatory for normal Charm Levels 1-3.

If Drome participates in Level 4, it should do so as an endgame specialization layer rather than blocking ordinary players from the core Charm system.

## 14. Relationship with Bounty

This Charm design is compatible with the separate Bounty redesign.

Relevant interaction:

- Bounty may send players back to creatures whose Bestiary is already complete;
- completed Bestiary should therefore retain value through Bounty progression or other bounded post-completion systems;
- Bounty should not become an unlimited alternative source that trivializes Bestiary or Charm Point acquisition;
- the Bounty Talisman Bestiary-related bonus can convert to a bounded Bounty-progress benefit after the target's Bestiary is complete, as described in the Bounty design document.

The systems should reinforce each other without collapsing their progression currencies into one unrestricted farm loop.

## 15. Relationship with Huntfinder and hunting-ground intelligence

Future Huntfinder integration may show:

- which creatures dominate a hunting ground;
- the player's Bestiary stage for each creature;
- the maximum effective Charm level currently usable on each creature;
- recommended Charm loadouts;
- expected benefit of available Major and Minor combinations.

Recommendations should remain advisory. Players should retain control over final Charm choices.

## 16. Telemetry and balance requirements

Before finalizing values, collect or simulate:

- Charm usage rate by vocation and level bracket;
- assignment frequency;
- contribution to damage, sustain and hunt efficiency;
- proc rate and effective value per hour;
- popularity of Level 3 capstones;
- progression time to Levels 1-4;
- Bestiary completion time by creature;
- Family Mastery completion distribution;
- Drome potion usage and resulting power increase.

Telemetry should identify dead Charms and dominant mandatory choices.

AI may assist with anomaly detection and balance analysis, but live gameplay rules, caps and progression costs should remain deterministic and reviewable.

## 17. Non-goals

This design does not propose:

- unlimited Charm power growth;
- automatic Level 4 access on newly discovered creatures;
- potions that bypass Bestiary progression;
- permanent loss of Family Mastery when new creatures are added;
- making Drome mandatory for basic Charm progression;
- removing strategic limits on simultaneous active Charm assignments;
- forcing players to manually rebuild assignments whenever they change a hunting ground.

## 18. Preferred progression loop

The intended player journey is:

1. Hunt a creature and reach Bestiary Stage 1.
2. Receive part of its Charm Point reward and unlock Level 1 effectiveness against it.
3. Reach Stage 2, receive further Charm Points and unlock Level 2 effectiveness.
4. Complete the creature's Bestiary, receive the largest remaining Charm Point reward and unlock Level 3 Mastery effectiveness.
5. Complete enough qualifying creatures in the relevant family to earn Creature Family Mastery.
6. If the player also owns the Charm at Level 4, unlock Grandmaster effectiveness against fully completed creatures in that mastered family.
7. Use Drome Charm potions as temporary amplifiers of legitimate unlocked power.
8. Use persistent assignments and loadouts to switch hunting grounds without repetitive manual Charm administration.

The resulting system connects Bestiary knowledge, Charm Points, Charm mastery, creature-family completion, Drome rewards and hunting-ground planning into one coherent long-term progression loop.

## 19. Implementation posture

Before implementation:

1. audit the authoritative current Canary/OTClient Charm, Bestiary and Drome data model;
2. inventory all current Major and Minor Charms and their actual formulas;
3. inventory current Bestiary stage thresholds and Charm Point rewards;
4. inventory existing Drome Charm-boosting consumables and exact supported effects;
5. define the creature-family taxonomy and migration rules;
6. simulate Charm Point availability and progression time under staged rewards;
7. design Level 3 capstones Charm-by-Charm;
8. decide whether Level 4 ships immediately or remains a supported future tier;
9. validate loadout UX and protocol/storage compatibility;
10. test balance separately for each vocation and representative hunting-ground composition.

No concrete numerical capstone, potion, Level 4 or Charm Point rebalance should be treated as final until this audit is complete.
