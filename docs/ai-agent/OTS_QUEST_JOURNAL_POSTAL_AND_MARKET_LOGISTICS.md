# OTS Quest Journal, Quest Progression, Postal Network, and Market Logistics

Status: design record / future gameplay proposal

This document preserves product ideas developed for the OTS future-gameplay roadmap. It is a design proposal, not a claim that current Tibia or Canary already behaves this way.

## 1. Problem statement

Many legacy quests are experienced as mandatory access gates rather than attractive gameplay. Players often complete only the quests they must complete because:

- the quest log is difficult to navigate;
- players frequently do not know their exact current objective;
- missions may be nested under a larger quest or campaign and therefore cannot be found by the name the player remembers;
- prerequisite quests and access dependencies are poorly exposed;
- long quest chains are difficult to resume after a break;
- party members can be on incompatible quest stages without a clear explanation;
- old physical rewards may have little practical value after many years;
- large legacy quests can require significant time while rewarding mostly access, a nostalgic item, or a minor discount;
- some world systems unlocked by old quests, especially postal services, no longer provide enough practical value to justify the effort.

The desired direction is to preserve the identity and history of old quests while adding a modern progression, navigation, and service layer.

## 2. Core product principles

1. A quest should be content, not merely a time tax before the real content.
2. The game should be able to tell the player what they are doing, where they are in the chain, what they already completed, and what currently blocks them.
3. Legacy physical rewards should usually be preserved rather than replaced.
4. Old quests can receive new permanent value through modern progression and thematic service unlocks.
5. Long-term quest progression should favor account convenience, exploration, identity, prestige, and world mastery rather than unrestricted vertical combat power.
6. A player should not need an external wiki merely to determine their current quest state.

## 3. Quest Journal 2.0

The current list-oriented mental model should be replaced by a structured quest-progress model.

### 3.1 Hierarchy

Recommended hierarchy:

```text
Campaign
  -> Quest Chain
      -> Quest
          -> Mission / Chapter
              -> Objective
```

A quest can also depend on another quest, access, reputation, item, boss completion, or world state.

Therefore the underlying data model should support a dependency graph rather than only a flat list.

### 3.2 Quest dependency graph

The journal should explicitly model dependencies such as:

```text
Quest A
  -> requires Quest B, Mission 4
  -> requires Access C
  -> requires Item D
  -> unlocks Quest E
```

When a prerequisite belongs to a different campaign or quest chain, the relationship should still be visible and clickable.

### 3.3 Current Objective

Every active quest should expose one primary current objective.

Example:

```text
Current Objective
Return to NPC X in Y.
```

Optional layers of assistance can include:

- immersive quest text only;
- a general hint;
- a more direct navigation hint;
- an optional map marker.

This allows players to choose between exploration and guided progression without forcing either style.

### 3.4 Completed-step history

The journal should preserve a human-readable history:

```text
Completed
- Spoke with NPC X
- Delivered Item Y
- Defeated Boss Z

Current
- Return to NPC X

Next
- Unknown / locked
```

A player returning after weeks or months should be able to understand their state immediately.

### 3.5 Why can I not continue?

Blocked steps should explain the blocker directly.

Examples:

- Missing prerequisite: Quest X, Mission 4.
- Required access: Y.
- Speak with NPC Z first.
- Required item: A.
- Party member B is missing prerequisite C.

This should be treated as a first-class UX requirement.

### 3.6 Search

Search should index more than top-level quest names.

Searchable concepts should include:

- campaign names;
- quest names;
- mission names;
- objective text;
- NPC names;
- regions;
- bosses;
- access names;
- major rewards;
- common aliases where maintained by content data.

A player searching for the name of a subquest should find the parent campaign and the exact nested mission that contains it.

### 3.7 Breadcrumbs

The player should always see structural context, for example:

```text
Quests > Zao > Wrath of the Emperor > Mission 7
```

Every level should be navigable.

### 3.8 Continue Playing view

The journal home screen should prioritize current play rather than the full archive.

Suggested sections:

- Active Quest;
- Current Objective;
- Blocked Quest and reason;
- Recently Completed;
- Recommended quests appropriate for current progression;
- Region or campaign progress.

### 3.9 Party Quest Sync

The system should expose party quest compatibility.

Example:

```text
3/4 players ready.
Player X is missing: Quest Y, Mission 5.
```

The system should never grant skipped quest progress merely for joining a party.

However, it should help the party identify the earliest compatible checkpoint and the exact missing prerequisites.

## 4. Account-wide access versus character progression

Not every quest should become account-wide.

A useful distinction is:

### Account-wide unlock candidates

- basic city or region access;
- major transport unlocks;
- portals and shortcuts;
- convenience services;
- postal-network privileges;
- selected repeated access prerequisites.

### Character-specific progression candidates

- individual story decisions;
- personal boss completions where repetition is meaningful;
- character-specific rewards;
- progression intended to be replayed for gameplay value.

The exact split requires quest-by-quest classification.

The objective is to remove repetitive access friction for alts without deleting meaningful character progression.

## 5. Quest Renown / Adventure Points

Completing quests should contribute to a persistent progression layer.

Working names:

- Quest Renown;
- Adventure Points.

The system should primarily reward exploration and completion, not raw combat power.

Possible rewards include:

- travel convenience;
- additional waypoints or service access;
- quest-journal features;
- additional tracker or loadout slots;
- titles;
- cosmetics;
- account prestige;
- improved access to selected world services;
- integration with Huntfinder or other discovery systems.

Quest Renown should not become an unrestricted source of permanent damage scaling.

## 6. Region Mastery

Completing related quest lines in a region can contribute to Region Mastery.

Example:

```text
Yalahar storyline complete
Oramond storyline complete
Kilmaresh storyline complete
```

Possible mastery rewards:

- title;
- cosmetic;
- travel perk;
- shortcut;
- service unlock;
- additional Quest Renown;
- Huntfinder or discovery quality-of-life for the region.

This turns quest completion into a broader exploration goal rather than an isolated checklist.

## 7. Modernizing quest rewards without deleting legacy identity

Legacy physical rewards should normally remain.

Preferred model:

```text
Legacy Physical Reward
+ Modern Progression Reward
+ Thematic Permanent Perk
+ Quest Renown
+ Region Mastery Progress
+ Appropriate One-Time XP Reward
```

### 7.1 Preserve iconic rewards

Recognizable quest items, outfits, access items, trophies, and historical rewards should usually remain because they are part of the identity of the world.

### 7.2 Add value around obsolete rewards

If a large old quest gives an item that no longer has meaningful economic or combat value, the quest can still become worthwhile by adding:

- Quest Renown;
- thematic service privileges;
- account progression;
- titles or cosmetics;
- region mastery;
- a carefully bounded one-time XP reward.

### 7.3 Do not level-scale tradeable physical items by default

A legacy item should not usually become a different power tier based on the level of the character who completes the quest.

This would complicate:

- item identity;
- trading;
- economy;
- balance;
- replay expectations.

Dynamic scaling is safer for one-time XP or non-tradeable progression rewards than for legacy tradeable equipment.

## 8. Quest XP reward scaling

Very old fixed XP rewards can become irrelevant to high-level characters.

A future model may consider:

```text
Base Quest Reward
+ Quest Effort / Difficulty
+ Character Progression Bracket
+ One-Time Completion Scaling
```

This must be bounded and simulated.

The objective is not to make quests the universally best XP source. The objective is to prevent large one-time quests from feeling completely unrewarding solely because the character is old or high level.

## 9. Postman Quest as a pilot candidate

A long legacy quest such as Postman is a strong candidate for a pilot rework because it combines:

- many missions;
- travel across the world;
- ranks and organizational identity;
- legacy physical rewards;
- access and service privileges;
- rewards whose practical value may be much lower today than when the quest was created.

The correct direction is not to delete the historic rewards.

Instead:

```text
Historic Postman Rewards
+ Quest Renown
+ Postal Rank Progression
+ Permanent Postal Privileges
+ Account/Character Service Unlocks
```

The player should feel that completing a long quest for the postal organization actually makes them a privileged member of that organization.

## 10. Postal Network rework

The broader problem is that postal gameplay can become functionally dead even if the old quest remains available.

The proposal is to evolve mail into a modern Postal and Logistics Network.

### 10.1 Core postal services

Potential services:

- sending items to another player;
- sending items between the player's own characters;
- COD / payment on delivery;
- insured parcels;
- parcel tracking;
- standard delivery;
- express delivery;
- delivery to a selected depot or mailbox;
- guild mailbox and guild logistics;
- house mailboxes and delivery boxes.

Not every feature must be implemented in the first version.

### 10.2 Postman progression

Quest progress can unlock service tiers.

Conceptually:

```text
No or early Postman progress
- basic postal service

Mid progression
- lower fees
- larger limits
- additional delivery options

Full Postman completion
- express services
- better insurance terms
- cross-city delivery privileges
- consolidation services
- additional mailbox access
```

The exact privileges must be balanced so that they do not bypass important quest access or world-travel rules.

### 10.3 Thematic reward principle

A postal quest should primarily reward postal and logistical privilege.

It should not simply be modernized by adding unrelated combat equipment.

## 11. Market architecture: do not copy fully separated Albion-style markets by default

Completely separate markets for every city could fragment liquidity on a server with a smaller population.

Potential failure mode:

```text
Thais -> highly liquid
Carlin -> moderate liquidity
Edron -> low liquidity
Small city -> nearly empty
```

The result could be additional friction rather than meaningful regional economy.

Therefore the preferred direction is a hybrid model.

## 12. Hybrid Global Market + Local Logistics

### 12.1 Global Marketplace

All offers remain discoverable through one global market interface.

This preserves liquidity and avoids forcing players to visit a dominant trade city simply to find an item.

### 12.2 Local warehousing / origin

Items or offers may retain a city/depot of origin.

Example:

```text
Seller stock: Thais
Buyer location: Darashia
```

The buyer can choose:

- local pickup at origin;
- postal delivery to another city;
- express delivery at a higher cost.

### 12.3 Postal delivery as the logistics layer

The Postal Network becomes the mechanism that moves purchased goods between locations.

Possible options:

```text
Pickup at origin
- immediate
- no delivery fee

Standard delivery
- lower fee
- normal delay or service rules

Express delivery
- higher fee
- faster service
```

Exact timing rules remain an open design question.

### 12.4 Consolidated delivery

A player buying multiple offers from different cities can request a consolidated delivery to one selected depot or mailbox.

Example:

```text
40 items in Thais
30 items in Carlin
30 items in Edron
-> consolidate to Darashia
```

Postman progression may reduce fees, improve limits, or unlock faster consolidation.

### 12.5 Local stock information

The market UI can expose both global pricing and regional stock information.

Example:

```text
Global median price: 10,000 gp
Thais stock: 540
Carlin stock: 22
Edron stock: 0
```

This gives location economic meaning without fragmenting the searchable marketplace.

### 12.6 City trade specialization

Cities may optionally provide small category-specific economic benefits.

Examples could include lower listing or logistics fees for thematic item groups.

These bonuses should be modest and optional.

The objective is to create regional identity, not force every player into mandatory trade routes.

## 13. Optional trade and logistics contracts

A future extension may introduce optional contracts such as:

```text
Deliver a quantity of goods from region A to region B.
```

This should remain optional side gameplay.

The game should not require manual hauling for normal market use.

The Postal Network should handle standard logistics automatically so that the system remains suitable for Tibia-style gameplay rather than becoming a mandatory trade-hauling simulator.

## 14. Economy and analytics integration

The hybrid market model can integrate with broader economy telemetry.

Useful aggregate signals include:

- global market supply;
- regional market supply;
- warehouse/depot distribution;
- player stash supply;
- item generation rate;
- regional generation source;
- regional consumption;
- postal delivery demand;
- price and liquidity differences between regions.

AI may assist with forecasting and anomaly detection, but deterministic safety controls should govern fees, caps, and economy-impacting behavior.

## 15. Relationship to other planned systems

### Bounty and Weekly Tasks

Quest access and region knowledge can improve task eligibility and explain why a target is currently unavailable.

### Huntfinder

Quest Journal and Huntfinder can share:

- access state;
- region unlocks;
- recommended progression;
- current quest blockers.

### Account-wide progression

Selected access unlocks and postal privileges can be account-wide while story progress remains character-specific where appropriate.

### Future gameplay roadmap

Quest Renown, Region Mastery, Postal Network, and hybrid market logistics should be treated as separate but connected systems.

## 16. Non-goals

This proposal does not require:

- deleting classic quest rewards;
- converting every quest reward into scaled equipment;
- making all quests account-wide;
- granting skipped quest progress to party members;
- making quests the best universal XP farm;
- fully splitting the market into isolated city markets;
- forcing players to physically haul every purchased item;
- turning postal progression into unrestricted combat power.

## 17. Open design questions

Before implementation, the following require explicit analysis:

1. Which quest unlocks should become account-wide?
2. Which quest rewards are iconic and must remain untouched?
3. Which legacy quests deserve modern thematic perks?
4. How should Quest Renown be earned and spent?
5. How should Region Mastery thresholds work?
6. How should one-time XP scaling be bounded?
7. Which Postman privileges are valuable without becoming mandatory?
8. Should postal delivery be instant, delayed, or tiered by service?
9. How should delivery fees scale with item count, weight, value, or distance?
10. Which market data remains global and which is regional?
11. Should local pickup materially reduce fees?
12. How should house and guild mailboxes interact with depots?
13. Which quest chains are best pilot candidates for Quest Journal 2.0?
14. How should quest dependency data be authored and validated in the datapack?

## 18. Recommended implementation posture

Do not begin by rewriting every quest.

Recommended staged approach:

1. define the quest graph and dependency contract;
2. build Quest Journal 2.0 against a small representative quest set;
3. pilot with one long legacy chain such as Postman;
4. classify legacy rewards into preserve / augment / rework;
5. define Quest Renown and Region Mastery contracts;
6. prototype Postal Network privileges;
7. prototype hybrid Global Market + Local Logistics independently of full market fragmentation;
8. add telemetry;
9. expand quest coverage incrementally after validation.

The design should preserve Tibia's historical world while making questing, exploration, and old world services worth engaging with in modern long-term play.
