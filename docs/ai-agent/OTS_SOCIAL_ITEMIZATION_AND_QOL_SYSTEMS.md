# OTS Social, Itemization and Quality-of-Life Systems

## Purpose

Durable design record for the user-approved future OTS directions discussed on 2026-07-23. This document expands the central `OTS_FUTURE_GAMEPLAY_SYSTEMS.md` roadmap without turning the roadmap itself into a very large implementation specification.

The systems here are product/design directions, not proof of current Canary, OTClient or current-Tibia behavior.

## Evidence labels

- `USER-DIRECTION`: explicitly requested, corrected or approved by the user.
- `DESIGN-DIRECTION`: a concrete design direction proposed during discussion and accepted as useful, but not yet an implementation contract.
- `OPEN`: requires balancing, technical validation, privacy/abuse analysis, economy simulation or current-parity verification.

---

# 1. World Map, Discovery and Live Social Map

## 1.1 Interactive World Map 2.0

`USER-DIRECTION`

Expand the full-world/minimap experience into a useful discovery and navigation surface rather than a mostly passive map.

Candidate map layers:

- NPCs;
- banks;
- depots;
- temples;
- mailboxes;
- trainers;
- transport NPCs and destinations;
- hunting-ground entrances;
- boss/event locations where disclosure is appropriate;
- quest-related POIs where disclosure does not destroy exploration;
- houses/guild-related locations where appropriate;
- player-created markers.

Expected UX:

- category filters;
- text search;
- marker details;
- optional navigation/target selection;
- route guidance where the required travel graph is known;
- discovery/fog-of-war rules where full disclosure would trivialize exploration.

`DESIGN-DIRECTION`

Map information should be layered. Static public POIs, player-discovered POIs, social/live markers and time-sensitive world-event markers should not be treated as one undifferentiated marker set.

`OPEN`

- exact authoritative source for NPC/transport/hunt/quest marker data;
- discovery and spoiler policy;
- route-planning graph and cross-floor/transport semantics;
- current OTClient full-map/minimap architecture and protocol requirements.

## 1.2 Live Social Map

`USER-DIRECTION`

Allow optional live map visibility for trusted social relationships.

Candidate scopes:

- current party;
- guild members;
- accepted friends/VIP contacts;
- explicitly selected/whitelisted players.

Each scope should be independently configurable.

Possible marker information:

- character name;
- position;
- vocation/role;
- distance;
- online/dead/unreachable state;
- last-known position where appropriate.

`DESIGN-DIRECTION`

Party tracking can be temporary and automatically end when the party ends. Guild/friend tracking should require explicit permission rather than being inferred merely from guild membership or unilateral VIP addition.

`OPEN`

- update frequency and bandwidth;
- cross-floor and cross-region visibility;
- PvP information-leak rules;
- invisible/privacy modes;
- last-known-position expiry;
- server-authoritative permission enforcement.

## 1.3 Shared Discovery Markers

`USER-DIRECTION`

When a player discovers a time-sensitive event or target such as an Echo Raid or Fiendish creature, the player should be able to create/share a map marker so selected social groups can see it.

Candidate share scopes:

- party;
- guild;
- accepted friends/VIP contacts;
- selected players;
- optional broader/public scope only if deliberately supported.

Candidate marker fields:

- event/target type;
- exact or approximate position;
- reporting player;
- report timestamp;
- status such as `active`, `cleared`, `unknown`;
- optional expiry;
- navigation action.

Other possible shared discoveries:

- rare bosses;
- world events;
- unusual raid activity;
- manually defined rally points.

`DESIGN-DIRECTION`

A report flow such as `Report Fiendish`, `Report Echo Raid` or a generic contextual map-marker action should reduce chat/Discord friction while preserving player discovery.

`OPEN`

- whether the server ever supplies exact positions automatically;
- whether markers are purely player-reported;
- anti-spam and false-report handling;
- event-specific expiry rules;
- exact current behavior and disclosure expectations for official Echo/Fiendish systems before implementation.

---

# 2. Friends/VIP, Consent and Social Privacy 2.0

## 2.1 Mutual contact relationship

`USER-DIRECTION`

A player must not gain tracking privileges merely by adding another player to a VIP list.

Preferred model:

`contact request -> accept / reject / block`

Only an accepted relationship may become eligible for additional social permissions.

## 2.2 Fine-grained permissions

`USER-DIRECTION`

Permissions should be separable, including at least:

- may see online status;
- may see live map position;
- may see shared discovery markers;
- may send party/group invitations;
- other future social-presence permissions.

Consent must be revocable.

Guild membership alone should not necessarily grant precise live position access.

`DESIGN-DIRECTION`

The legacy `VIP List` concept may be presented as a broader Friends/Contacts model while retaining compatibility terminology where needed.

`OPEN`

- account-wide versus character-level relationships;
- blocking semantics;
- privacy defaults;
- migration of existing VIP entries;
- protocol and persistence model;
- interaction with invisible status and PvP worlds.

---

# 3. Party System 2.0

## 3.1 Rebuild the party experience, not only Party Finder

`USER-DIRECTION`

The future party redesign should include the active party itself, not only the existing `Party Finder 2.0` roadmap direction.

Areas to review:

- party UI;
- party member visibility;
- roles;
- shared-experience/bonus rules;
- contribution recognition;
- hunt accounting;
- social-map integration;
- shared objectives and discoveries.

`OPEN`

The exact shared-EXP and party-bonus formulas require a separate balance review. Do not promote speculative formulas into implementation contracts without simulation and current-baseline verification.

## 3.2 Party Combat Visibility

`USER-DIRECTION`

During high-intensity hunts, party members become difficult to track among monsters, effects, health bars and other visual noise. The client should make party information much easier to parse.

Candidate improvements:

- strong optional outline/highlight for party members;
- distinct leader marker;
- role markers such as tank/support where roles exist;
- clearer name/HP presentation;
- low-HP emphasis;
- status/debuff indicators;
- off-screen direction indicators;
- priority/pinned party members;
- compact party panel with HP/mana/status;
- optional reduction/simplification of nonessential visual effects;
- a high-intensity-hunt presentation preset.

Core usability goal:

`where is my party -> who is in danger -> who needs healing/support -> who is the leader/priority -> who left the visible screen`

`OPEN`

- accessibility/color policy;
- PvP implications;
- screen clutter thresholds;
- exact data already exposed to OTClient versus new protocol state.

## 3.3 Shared Hunt Accounting / Party Loot Ledger

`USER-DIRECTION`

Remove the painful manual end-of-hunt workflow where one person collects/sells loot, players calculate supplies separately, and somebody later calculates and transfers every player's share.

The party session should be able to record:

- total loot acquired;
- who physically picked up each item where useful;
- loot valuation source;
- supplies consumed per player;
- total waste;
- gross and net profit;
- configured split rule;
- final amount owed to/from each player.

Candidate split policies:

- equal net split;
- equal split after individual supply reimbursement;
- percentage split;
- manually adjusted split before final confirmation.

`DESIGN-DIRECTION`

A `Party Treasury` or settlement flow may either:

1. calculate the exact transfers while players execute them manually; or
2. perform bounded automatic settlement if the economy/bank architecture safely supports it.

The calculation layer should be designed independently from the decision to automate money movement.

`OPEN`

- authoritative loot valuation;
- market versus NPC price choice;
- handling unsold rare items;
- TC/alternate-currency loot;
- automatic-transfer safety;
- disconnect/party-change edge cases;
- abuse and audit history.

---

# 4. Itemization & Build System 2.0

## 4.1 Goal

`USER-DIRECTION`

Make equipment and build decisions easier to understand and test without reducing the game to one mandatory meta build or forcing players to ask external communities for basic quantitative comparisons.

The system should connect existing/future concepts instead of inventing duplicate progression layers:

- equipment;
- existing item classification/Forge foundations;
- imbuements;
- Skill Wheel;
- classic skills;
- Weapon Proficiency;
- Equipment/Build Presets;
- Huntfinder/Boss preparation.

## 4.2 Build Impact & Comparison System

`USER-DIRECTION`

Players frequently need to ask questions such as:

- how much more damage does this weapon actually give?;
- how much more healing does this perk/item give?;
- what percentage improvement does this build change provide?;
- what is the defensive cost of switching to an offensive item?

The client should provide an authoritative comparison surface using the same underlying server formulas/contracts where practical.

Candidate output:

### Offense

- estimated average damage;
- spell-specific damage ranges;
- auto-attack contribution;
- critical contribution;
- total estimated DPS change.

### Healing

- average heal;
- expected healing change;
- spell-specific comparison;
- healing-per-resource where useful.

### Defense

- physical mitigation;
- elemental damage taken;
- resistance deltas;
- expected incoming-damage change for a selected profile.

### Sustain

- life leech;
- mana leech;
- regeneration;
- resource consumption;
- damage/healing per mana/resource.

Preferred comparison modes:

- current item versus candidate item;
- perk before/after;
- full Build A versus Build B;
- optional target/monster profile where authoritative resistance data is available.

`OPEN`

- formula ownership and anti-desync strategy;
- exact definition of estimated DPS/healing;
- random/conditional effects;
- server versus client calculation boundary;
- avoiding misleading precision.

## 4.3 Build Preset integration

`DESIGN-DIRECTION`

A build preset may eventually coordinate:

- equipment;
- Skill Wheel preset;
- imbuement configuration;
- action bars/hotkeys;
- optional summon/role configuration where supported.

Preset switching must obey combat/PZ restrictions defined by the corresponding systems.

## 4.4 Training Arena / Combat Simulation

`USER-DIRECTION`

Provide a controlled arena where players can test real combat builds against training monsters instead of relying only on a static dummy.

Training monsters must provide no normal progression or farmable value:

- `0 EXP`;
- `0 loot`;
- `0 Bestiary/Bosstiary progress`;
- `0 Bounty/Task progress`;
- `0 Weapon Proficiency progress`;
- `0 classic skill gain`;
- no other normal progression/reward unless a future explicit training-only contract says otherwise.

Candidate modes:

- single-target;
- AoE density test;
- survival test;
- sustain/resource test;
- healing/support test;
- movement/mechanics practice;
- standardized hunt-style scenarios;
- controlled boss-style practice profiles.

Candidate metrics:

- total damage;
- average DPS;
- peak DPS;
- average/maximum hit;
- healing and HPS;
- damage received;
- mana/resource usage;
- potion/rune/ammunition usage;
- life/mana leech contribution;
- time survived;
- kills in fixed time;
- A/B comparison against saved previous tests.

`DESIGN-DIRECTION`

The ideal model combines:

`Build Impact Calculator -> theoretical/formula comparison`

with

`Training Arena -> practical player-executed comparison`.

`OPEN`

- whether consumed supplies are virtual, refunded or genuinely consumed;
- exact monster-profile creation rules;
- whether real monster AI can be reused safely without progression hooks;
- instance architecture;
- server load and anti-exploit boundaries.

---

# 5. Inventory, Depot and Stash 2.0

## 5.1 Goal

`USER-DIRECTION`

Reduce the legacy friction created by large trees of backpacks/containers, fragmented storage, weak filtering, manual post-hunt cleanup and non-stackable/high-volume items.

Preserve the physical backpack/container identity where it creates gameplay, but do not require depot/storage management to remain a maze of nested containers.

Preferred distinction:

`backpacks in active field gameplay = physical inventory gameplay`

`depot/stash/storage = modern searchable storage UX`

## 5.2 Global Item Search

`USER-DIRECTION`

Provide a search surface across appropriate owned storage scopes, potentially including:

- inventory;
- open/closed containers where server permissions allow;
- depot;
- stash;
- inbox;
- account/character storage scopes where supported;
- house storage only if the ownership/security model supports it.

Results should show:

- item;
- quantity;
- location/container/storage scope.

## 5.3 Smart containers and sorting

`USER-DIRECTION`

Support category/rule-based organization such as:

- potions;
- runes;
- creature products;
- valuables;
- equipment;
- quest/task items;
- custom user categories.

Candidate actions:

- auto-sort;
- smart destination containers;
- post-hunt deposit;
- merge stacks;
- move sellable loot while excluding protected/reserved items.

## 5.4 Item Reservation & Protection

`USER-DIRECTION`

The system should understand that some owned items are required for active goals and should not be accidentally sold, traded, dropped or consumed.

Reservation sources may include:

- active Bounty Tasks;
- Weekly Delivery Tasks;
- quests;
- saved build/loadout items;
- manually locked/favorited items;
- future crafting/objective reservations.

Expected behavior example:

`Owned: 84`

`Reserved for active objective: 50`

`Safe to sell: 34`

Protection should be quantity-aware rather than always locking the entire stack.

Candidate protected actions:

- NPC sale;
- Market listing;
- player trade;
- dropping/destroying;
- auto-sell;
- auto-sort into sellable-loot destinations.

`DESIGN-DIRECTION`

Useful item tags include:

- `Do not sell`;
- `Reserved`;
- `Quest`;
- `Bounty/Weekly`;
- `Build`;
- `Favorite`;
- custom user tag.

`OPEN`

- authoritative task/quest item reservation sources;
- account versus character storage;
- item stacks with charges/subtypes;
- transaction atomicity when reserved quantities change;
- UI performance for very large stores.

## 5.5 Stackability review

`USER-DIRECTION`

Review item categories that create entire backpacks of objects because they are not stackable or have unnecessarily low stack limits.

Do not globally make every item stackable. Separate:

- unique/equipment/stateful physical items;
- commodities/materials/creature products that can safely behave as quantities.

`OPEN`

Every stackability change needs item-state, market, depot/stash, protocol and migration review.

---

# 6. Market & Trade System 2.0 additions

## 6.1 Sale-only commission

`USER-DIRECTION`

Preferred fee model:

- no fee merely for listing an offer;
- commission is charged only when a sale successfully completes.

Expected confirmation should show:

- sale price;
- commission;
- net proceeds.

`DESIGN-DIRECTION`

Free listing must be protected from offer spam through non-monetary controls where needed, such as bounded active-offer limits, expiry and anti-automation controls.

`OPEN`

- exact commission formula;
- offer limits;
- cancellation/expiry semantics;
- economy impact versus the current fee model.

## 6.2 Multi-Currency Market & Trade

`USER-DIRECTION`

Support legitimate high-value trading in currencies other than gold, specifically including Tibia Coins where the server/account ecosystem supports them.

Candidate transaction forms:

- item for gold;
- item for TC;
- item for item;
- item plus gold;
- item plus TC;
- potentially mixed settlement only if UX/audit rules remain unambiguous.

Market offers should clearly identify the settlement currency and support currency-specific filtering/history.

Do not silently convert between gold and TC unless a separate explicit exchange system is designed.

High-value item support should reduce the need to move rare-item trading to Discord/forum/private-message channels merely because the normal Market cannot express the desired currency.

`DESIGN-DIRECTION`

Possible future rare-item flow:

- fixed price in chosen currency;
- buy offer in chosen currency;
- optional `open to offers` negotiation model.

`OPEN`

- exact TC/account balance authority;
- premium-currency legal/accounting constraints;
- trade rollback and audit;
- commission currency;
- cross-account abuse/RMT implications;
- whether mixed-currency transactions are worth the complexity.

---

# 7. Imbuement System 2.0

## 7.1 Problem statement

`USER-DIRECTION`

The current item-bound timed Imbuement experience creates several forms of friction:

- players must monitor remaining time;
- a resistance imbue can keep losing time while the player is temporarily fighting content where that resistance is irrelevant;
- many hunting spots combine multiple damage elements;
- players can end up owning/juggling multiple copies of similar equipment mainly to maintain different resistance/imbuement configurations;
- the growing number of spots/elements makes inventory/configuration management increasingly painful.

The redesign should preserve meaningful preparation and economic sinks without requiring needless duplicate-item juggling.

## 7.2 Slot-based Imbuement library

`USER-DIRECTION`

Move the stored/charged Imbuement concept from one physical item toward an equipment-slot-level library/profile system.

Example:

`Armor equipment slot library`

- Fire protection charged/available;
- Ice protection charged/available;
- Energy protection charged/available;
- Earth protection charged/available;
- Death protection charged/available;
- other compatible future effects.

The currently equipped item remains important because it defines how many active Imbuement channels and which Imbuement categories are legal.

Core model:

`equipment slot = stores unlocked/charged Imbuement options`

`equipped item = defines active channel capacity and compatibility`

`build preset = selects the active configuration`

This avoids permanently binding every paid/charged configuration to one physical copy of an item.

## 7.3 Active channels

`USER-DIRECTION`

An item may support up to its allowed number of simultaneously active non-elemental channels.

Example for a compatible three-channel weapon:

- Critical;
- Life Leech;
- Mana Leech.

The redesign should not force elemental protection to consume the same limited active-channel budget if doing so recreates the original conflict between core sustain/offense effects and the need to prepare for increasingly mixed-element content.

`DESIGN-DIRECTION`

Each equipment category should retain a role/compatibility matrix. For example, weapons should not become universal defensive-resistance carriers merely because the slot library contains resistance charges.

`OPEN`

- exact channel counts per current item;
- whether current item Imbuement slots map 1:1 to active channels;
- item-category compatibility rules;
- handling items with unusual official slot contracts.

## 7.4 Elemental Attunement as a separate layer

`USER-DIRECTION`

Elemental protections should be considered as a separate equipment-slot attunement layer rather than competing directly with `Crit + Life Leech + Mana Leech` style active channels.

A slot can have multiple elemental protections charged/unlocked, while its attunement capability determines what can be used automatically or simultaneously.

Example concept:

`Armor attunement library`

- Ice charged;
- Death charged;
- Energy charged.

On a mixed-element hunting spot the system can apply the appropriate protection to the corresponding incoming damage type, subject to the slot/item's attunement limits.

This does **not** mean granting every elemental resistance at full strength without cost or limits.

## 7.5 Slot progression / attunement level

`USER-DIRECTION`

Consider progression of the equipment-slot Imbuement/Attunement capability itself, potentially through bounded levels such as a future Level 1-10 model.

Possible progression dimensions:

- number of elemental types that can be stored/charged;
- number of types available to automatic attunement;
- convenience/automation;
- recharge efficiency or other bounded utility.

`DESIGN-DIRECTION`

A possible milestone model, for later balancing only:

- early levels: one/few manually selected elemental options;
- mid levels: more stored elemental options;
- high level: automatic matching of a charged protection to incoming elemental damage;
- highest level: maximum supported convenience/flexibility, not unlimited free resistance.

Exact `1-10` progression is a design placeholder, not an approved numeric contract.

## 7.6 Item Classification integration

`USER-DIRECTION`

Use the existing item-classification foundation rather than inventing a parallel `Common/Rare/Epic/Legendary` rarity system.

Potential relationship:

- Item Classification constrains the maximum flexibility/potential of the equipped item;
- the concrete item defines exact active-channel/compatibility rules;
- Forge Tier remains a separate progression/power axis;
- Imbuement/Attunement remains the build-specialization axis.

Do not define `Classification 4 = automatically strongest at everything`.

The goal is to use classification as one input into available flexibility while keeping item identity meaningful.

`OPEN`

- exact current classification coverage and Forge interaction;
- whether classification should cap slot level, active channels, attunement options or none of these;
- legacy item compatibility;
- current official restrictions that must be preserved.

## 7.7 Effective-use lifecycle

`USER-DIRECTION`

The current fixed-duration concept should be reviewed so a specialized defensive Imbuement does not waste its duration while the player is temporarily doing unrelated elemental content.

Preferred direction to evaluate:

`effective usage time`

For a defensive elemental effect, one minute of relevant active combat consumes one minute regardless of whether the player is fighting weak or extremely strong monsters.

This avoids a damage-proportional charge model where difficult content drains the Imbuement dramatically faster merely because incoming numbers are larger.

Possible semantics:

- relevant elemental protection is being used -> timer runs normally;
- content has no relevant damage source -> that elemental timer does not run;
- outside relevant combat -> timer does not run.

`OPEN`

Different Imbuement categories need separate contracts. The trigger semantics for Crit, Life Leech, Mana Leech, skill effects and elemental resistance are not necessarily identical.

## 7.8 Build Preset integration

`USER-DIRECTION`

A build preset should be able to select:

- equipment;
- active non-elemental Imbuement channels;
- elemental attunement configuration;
- Skill Wheel preset where allowed;
- related build UI/action configuration.

Changing presets/configurations must not become an in-combat instant-resistance exploit. Combat/PZ restrictions remain required.

## 7.9 Economy / gold-sink model

`USER-DIRECTION`

The redesign should ideally improve the economy sink rather than remove Imbuement costs.

Use two complementary sink classes:

### Progression sink

Potential one-time/long-term costs for:

- raising equipment-slot Imbuement/Attunement level;
- unlocking additional elemental capacity/automation;
- other bounded slot progression.

### Maintenance sink

Recurring costs for:

- recharging elemental protections;
- renewing active Crit/Leech/Skill-style effects;
- convenient `Recharge All` operations where appropriate.

`DESIGN-DIRECTION`

Higher progression should grant flexibility and convenience, not permanently free Imbuements. A mature slot should still consume charged effects/resources according to the final lifecycle contract.

`OPEN`

- exact gold/material split;
- recharge frequency;
- whether materials remain mandatory at every stage;
- impact on creature-product demand;
- impact on inflation compared with current Imbuement spending;
- interaction with existing Economy Sink Framework and Weekly Delivery demand controls.

---

# 8. System integration map

`DERIVED`

## Social/discovery cluster

World Map 2.0
+ Live Social Map
+ Friends/VIP Consent & Privacy
+ Shared Discovery Markers
+ Party System 2.0
+ Party Finder 2.0
+ Huntfinder
+ Hunting Spot Availability

## Party hunt cluster

Party System 2.0
+ Party Combat Visibility
+ Shared Hunt Accounting
+ Loot System Rework
+ Bank/Transaction History
+ Social Map

## Item/build cluster

Itemization & Build System 2.0
+ Equipment/Build Presets
+ Build Impact & Comparison
+ Imbuement System 2.0
+ Skill Wheel
+ Classic Skills
+ Weapon Proficiency
+ Training Arena
+ Huntfinder/Boss preparation

## Storage/task cluster

Inventory/Depot/Stash 2.0
+ Global Item Search
+ Smart Containers/Sorting
+ Item Reservation & Protection
+ Bounty Tasks
+ Weekly Delivery Tasks
+ Loot System Rework

## Market/economy cluster

Market System 2.0
+ Trade System 2.0
+ Bank/Transaction History
+ Multi-Currency Transactions
+ sale-only commission
+ Economy Sink Framework

## Imbuement/economy cluster

Slot-Based Imbuement Library
+ Active Channels
+ Elemental Attunement
+ Slot Progression
+ Item Classification
+ Build Presets
+ Effective-Use Lifecycle
+ Progression Sink
+ Maintenance Sink

---

# 9. Implementation policy

1. Treat every section as roadmap/product direction until promoted into a bounded implementation task.
2. Reverify current Canary, OTClient and current-Tibia behavior before implementation, especially for Party, Market, item classification/Forge and Imbuement contracts.
3. Do not create a second parallel Party Finder, Loot System or minimap-marker implementation when the existing roadmap concept can be extended.
4. Run privacy/PvP abuse analysis before enabling live social tracking or shared location data.
5. Run economy simulation before changing Market fees, premium-currency settlement, Imbuement maintenance costs or slot progression sinks.
6. Keep Training Arena targets non-farmable and explicitly excluded from all normal progression/value paths.
7. Prefer transparent calculators that expose assumptions over false precision.
8. Preserve meaningful preparation while removing repetitive inventory/configuration friction.
9. Keep user consent authoritative for friend/VIP tracking permissions.
10. Quantitative examples in this document are placeholders unless later promoted into explicit contracts.
