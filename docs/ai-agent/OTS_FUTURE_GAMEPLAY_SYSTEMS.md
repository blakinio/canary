# OTS Future Gameplay Systems Roadmap

## Purpose

Durable design record for future OTS gameplay, client, economy, security, PvP, bossing and quality-of-life work discussed with the user on 2026-07-21.

This document is intentionally broader than one implementation task. It preserves product direction so future agents do not have to reconstruct it from chat history.

## Evidence labels

- `USER-DIRECTION`: explicitly requested or approved by the user.
- `DESIGN-DIRECTION`: proposed design direction accepted as useful, but not yet specified as an implementation contract.
- `OPEN`: requires analysis, balancing, technical validation or abuse review.

## Core product philosophy

`USER-DIRECTION`

- The game must remain challenging, risky and rewarding.
- Remove legacy friction that is mostly irritating rather than meaningful.
- Do not make the game trivial in the process of improving quality of life.
- Player progression should remain viable over the long term; systems should not punish high-level players disproportionately because of formulas designed for an era when level 100 was near endgame.
- Convenience should often be earned by first engaging with the original content.
- Where possible, replace arbitrary frustration with meaningful temporary cost, risk, progression, mastery or preparation.
- Systems that can be abused should be designed around telemetry, bounded rewards, diminishing returns and anomaly detection from the start.

---

# 1. RubinOT research context

## Classification model

The RubinOT feature audit should be kept in four buckets rather than calling everything "custom":

1. Real Tibia feature improved or modified.
2. Hybrid system built on a Real Tibia foundation.
3. Fully custom system.
4. External/web/client tooling or custom content.

All RubinOT behavior must be reverified against the current RubinOT wiki before implementation work.

## Real Tibia -> improved/modified

- Boosted Exercise.
- World Transfer with custom rules and convenience.
- Map/client UX improvements.

## Hybrid systems

- Huntfinder: recommendations, filters, XP/profit context, equipment/imbuement suggestions, charms and route guidance.
- Linked Tasks: chained/repeatable task progression layered over task/quest concepts.
- Equipment Presets: whole-set switching integrated with client/action bar behavior.
- Obelisk/Mini Obelisk: custom handling around boss cooldowns and crash compensation.

## Fully custom systems

- Cosmetic Card.
- Castle battleground/event.
- Prestige Arena ranked PvP.
- Battle Pass.
- Drop/Roulette system.

## Tools/content

- Skill Calculator.
- Outfitter.
- Interactive Map: exact behavior remains `OPEN` and must be inspected directly.
- Custom outfits and mounts are mainly content unless tied to new mechanics.
- House items are mostly content/variants unless a specific item has unique behavior.
- Annual events can include custom bosses, mechanics and rewards.

## High-interest ideas for our stack

`DESIGN-DIRECTION`

Priority candidates from the RubinOT review:

1. Huntfinder.
2. Equipment Presets.
3. Crash-aware boss-cooldown compensation/Obelisk concept.
4. Linked Tasks.
5. Better map UX.
6. Castle.
7. Prestige Arena.

Target stack context: Canary + OTClient + RME + client-editor.

---

# 2. Account-wide quest progression

`USER-DIRECTION`

Quest completion/progression should be considered for account-level storage rather than always character-level storage.

Goals:

- Reduce repeated mandatory questing on alts.
- Preserve account progression.
- Define which quests are truly account-wide versus character-specific.

`OPEN`

- Migration semantics for existing characters.
- Reward duplication rules.
- Quest-state compatibility with scripts that assume per-character storage.

---

# 3. Independent auto attack and spell casting

`USER-DIRECTION`

Auto attack should operate independently from spell usage:

- casting a spell should not cancel auto attack;
- casting should not reset the auto-attack timer;
- casting should not cause the next weapon attack turn to be skipped merely because a spell was used.

`OPEN`

- Exact timing contract per vocation and weapon type.
- PvP balance impact.
- Compatibility with current Canary combat scheduling.

---

# 4. Character markers on minimap

`USER-DIRECTION`

Add character markers on the minimap.

Possible visibility scopes to evaluate:

- party;
- guild;
- friends;
- selected/whitelisted players.

`OPEN`

- Privacy and PvP visibility rules.
- Server-authoritative versus client-local information.

---

# 5. Hunting Spot Availability System

`USER-DIRECTION`

Players should be able to see whether a defined hunting spot such as Cobra Basement or Falcon Eagle is actively occupied.

Preferred status model:

- available/free;
- probably occupied;
- occupied;
- unknown.

Detection should use real activity rather than mere presence when possible:

- players inside a defined region;
- time spent there;
- monster kills;
- XP gain;
- loot activity;
- party size/activity.

Do not expose player names by default; the goal is spot availability, not player tracking.

Potential integration:

- Huntfinder shows live availability.
- "Notify when free" for a selected spot.

`OPEN`

- Region definitions and ownership of hunt-area data.
- Anti-grief/anti-reservation abuse.
- False positives from players passing through.

---

# 6. Party Finder 2.0

`USER-DIRECTION`

Rebuild the existing Party Finder rather than creating a separate parallel system.

Core capabilities:

- search by hunt;
- search by boss;
- search by Soul Core/Soulpit;
- required level range;
- required vocations/roles;
- current party composition;
- status: looking / ready / full / in progress;
- join requests;
- ready check;
- matching/notifications.

## Hunt mode

Integrate with:

- Huntfinder;
- Hunting Spot Availability;
- chosen hunting spot.

## Boss mode

Integrate with Boss System 2.0 and Boss Hub.

## Soul Core / Soulpit mode

Players should be able to advertise/search for a specific Soul Core/Soulpit activity.

Possible filters:

- I have this Soul Core;
- I need this Soul Core;
- I want to help;
- required party composition;
- queue several Soul Cores.

`OPEN`

- Exact Soul Core ownership/progression checks.
- How account-wide versus character-wide completion should interact with finder results.

---

# 7. Loot System Rework

`USER-DIRECTION`

Current corpse-by-corpse clicking is considered tiring and frustrating.

Potential layers:

- Loot Nearby / Loot All hotkey.
- Optional Auto Loot.
- Loot queue for multiple corpses.
- Loot filters/lists.
- Destination containers by category.
- Party loot rights.
- Clear feedback such as number of corpses looted.
- Manual loot remains available.

## Summon Loot Assistant

`DESIGN-DIRECTION`

The existing summon system may be extended so a summon can collect loot.

Possible modes:

- Combat;
- Loot;
- Follow.

Constraints to consider:

- limited radius;
- respects loot rights;
- respects loot filters and destination containers;
- limited speed so it is not equivalent to instant global auto-loot.

`OPEN`

Current summon implementation must be audited before choosing the integration model.

---

# 8. Bank System Rework

`USER-DIRECTION`

Replace chat-command-heavy banking flows with a dedicated UI.

## Transfer UI

- select recipient;
- enter amount;
- show current balance;
- show resulting balance;
- explicit confirmation;
- validation of recipient and funds;
- large-transfer warning;
- protection against duplicate submission.

## Transaction History

Record at least:

- incoming transfers;
- outgoing transfers;
- deposits;
- withdrawals;
- system fees/transactions;
- timestamp;
- sender/recipient;
- amount;
- resulting balance;
- transaction identifier or description where useful.

Legacy chat commands may remain for compatibility, but should not be the primary UX.

---

# 9. Trade System Rework / Financial & Trading System 2.0

`USER-DIRECTION`

Trade should be able to use bank balance directly instead of requiring physical coin withdrawal into backpacks.

Supported forms:

- item for bank gold;
- item for item;
- item + bank gold for item;
- multiple items + bank gold.

UX goals:

- seller proposes amount;
- buyer can accept or counteroffer;
- amount can be entered directly or adjusted with a convenient control;
- both parties must accept the exact same final transaction state;
- any item/amount change resets acceptance;
- high-value trade may require final confirmation;
- show balance before/after;
- validate capacity/inventory/tradeability/funds.

Trade history should integrate with bank transaction history for support and audit.

---

# 10. Death System 2.0

`USER-DIRECTION`

Current death loss is considered too harsh and based on a legacy model that scales from total accumulated experience. The new system must preserve frequent meaningful death and risk without causing high-level players to lose disproportionate amounts of long-term progression.

## Design goals

- Death must still matter.
- The game must not become easy.
- A player should fear dying but should not fear attempting challenging content.
- Avoid a death costing many hours solely because lifetime XP is enormous.
- Progression should remain sustainable.

## Level-relative XP loss

`DESIGN-DIRECTION`

Prefer loss based on current progression scale, e.g. a fraction of experience associated with the current level/progression band, not a percentage of lifetime XP.

Exact percentages remain `OPEN`.

## Blessings

Blessings should remain meaningful and may reduce:

- XP loss;
- skill loss;
- item-loss risk;
- possibly post-death fatigue duration.

## Recovery Pool

Part of lost XP may become recoverable through continued active play.

Intent:

- death still creates real loss;
- part of the loss can be recovered by continuing to play;
- reduce the "I lost the whole evening, I quit" effect.

## Consecutive-death handling

Consider protection against catastrophic death spirals while avoiding exploitability.

Possible direction:

- diminishing additional permanent loss for repeated deaths in a short period;
- temporary penalties may increase instead.

## Death Fatigue / Post-Death Weakness

`USER-DIRECTION`

Use temporary stat reduction after death as part of the cost, similar in spirit to systems in other MMOs.

Potential effects:

- reduced damage;
- reduced healing;
- reduced defense;
- optional movement or resource penalties.

Intent:

- player cannot instantly rush back at full power;
- shift part of the punishment from permanent progression loss to temporary consequence.

Avoid making the player effectively unable to play for a long time.

## Different death contexts

Evaluate separate tuning for:

- open-world PvE;
- boss/instance/Soulpit;
- PvP;
- confirmed server failures.

Confirmed infrastructure failures may justify full or near-full compensation.

---

# 11. Connection Loss Protection

`USER-DIRECTION`

Create protection for genuine Internet loss/client crash while preventing combat-logout abuse.

Important conclusion:

A server cannot reliably prove from one disconnect whether it was genuine or intentional. A deliberate network cut can look like a real failure.

Therefore do not base the whole system on "perfect disconnect classification".

Possible signals:

- explicit logout request versus abrupt socket loss;
- in-fight state;
- HP/mana;
- incoming DPS;
- nearby attackers;
- ping/RTT/timeout history if telemetry is added;
- reconnect delay;
- repeated disconnect history;
- simultaneous incidents affecting multiple players.

Possible protection behavior:

- character remains in world during combat according to controlled rules;
- fast reconnect restores control;
- reduced death penalty for eligible incidents;
- full compensation for proven server-side failures.

`OPEN`

Any server-side autopilot, auto-healing or defensive control during disconnect must be evaluated extremely carefully because it can create powerful abuse paths.

---

# 12. Disconnect Abuse Detection Agent

`USER-DIRECTION`

Extend the gameplay-analysis agent to detect repeated abuse patterns rather than trying to judge one disconnect.

Potential features:

- long-term pattern analysis;
- suspicion/risk score;
- detect disconnects disproportionately occurring at low HP or lethal combat moments;
- compare combat disconnects with normal non-combat disconnect frequency;
- correlate reconnect times;
- correlate server-wide/network-wide events;
- report repeated suspicious behavior.

Recommended response model:

- low risk: no action;
- medium risk: observation;
- high risk: report/review;
- repeated high risk: eligibility restrictions or manual investigation.

Do not automatically ban based on one model output.

---

# 13. AI Anti-Bot / Anti-Cheat Platform

`USER-DIRECTION`

Build a stronger anti-bot/anti-cheat system inspired by systems such as BattlEye but designed around modern AI-assisted and external vision bots.

## Threat model from current bot research

Modern bots may operate as:

- classic macros/taskers;
- pixel/computer-vision bots;
- full cavebot loops with navigation, targeting, healing, loot and refill;
- external systems observing video and emulating keyboard/mouse input;
- future visual AI agents with more adaptive behavior.

The most important design conclusion is that client-only anti-cheat is insufficient against bots whose logic runs outside the game process or even on another device.

## Multi-layer architecture

### Client integrity

- detect client modification;
- detect injection/hooks where feasible;
- verify important client assets/modules.

### Server-side behavioral telemetry

Potential signals:

- extremely repeated routes;
- unusually low timing variance;
- highly consistent healing thresholds;
- repeated identical target-selection patterns;
- long uninterrupted sessions with invariant behavior;
- repeated refill loops;
- machine-like response consistency.

### AI behavioral analysis

Compare:

- player versus own historical behavior;
- player versus peer distributions;
- player versus known bot patterns;
- correlated behavior across accounts.

### Cross-account graph detection

Detect:

- bot farms;
- mule funnels;
- coordinated repetitive behavior;
- suspicious economic transfers.

## Enforcement principle

`USER-DIRECTION`

Do not use `AI says bot -> automatic ban` as the primary policy.

Prefer:

signals + evidence + correlation + risk score + review/challenge/escalation.

The same platform may also analyze:

- macro abuse;
- disconnect abuse;
- exploit abuse;
- kill farming;
- win trading;
- suspicious economic activity;
- multibox abuse.

---

# 14. PvP System 2.0

`USER-DIRECTION`

Current PvP is considered both boring and irritating. Rework should make combat more interesting while reducing grief-driven frustration.

Goals:

- more skill expression;
- more meaningful positioning/timing;
- clearer combat state/effects;
- more structured PvP;
- less open-world griefing/power abuse;
- separate rules for open world, arena, guild wars and events where appropriate;
- integrate with Death System 2.0.

## PvP rewards

`USER-DIRECTION`

PvP should be rewarding enough to encourage participation without becoming an abuseable gold/XP farm.

Preferred reward types:

- rating/prestige;
- seasonal ranking;
- cosmetics;
- titles;
- achievements;
- PvP currency with controlled utility;
- objective-based rewards.

Prefer rewards for meaningful objectives rather than every kill:

- ranked wins;
- guild-war objectives;
- Castle objectives;
- bounty objectives;
- tournament outcomes.

Use diminishing returns for repeated kills of the same victim.

Use account-level/cross-account anti-farming analysis where appropriate.

## Victim loss and recoverability

`USER-DIRECTION`

Directly transferring large amounts of victim gold or XP to the killer is considered too abuseable.

Preferred direction:

- victim can lose meaningful progress;
- part of that loss may become recoverable;
- killer receives prestige/ranking/objective rewards rather than the victim's full economic value.

Possible PvP-specific Recovery Pool or revenge/recovery objective.

## High-risk PvP zones

`DESIGN-DIRECTION`

Opt-in high-risk zones may be the appropriate place for stronger loot-drop rules because players knowingly accept the risk.

`OPEN`

- exact PvP combat mechanics;
- anti-grief rules;
- bounty design;
- structured versus open-world reward weighting.

---

# 15. Adaptive Game View & Scalable UI 2.0

`USER-DIRECTION`

Modernize the client for large monitors, ultrawide, high DPI, 1440p and 4K.

The user specifically highlighted large 34-inch displays and modern resolutions.

Goals:

- resolution-independent rendering;
- dynamic game viewport;
- independent UI scaling;
- independent font scaling;
- scalable minimap;
- scalable action bars, inventory, battle list, chat and tooltips;
- responsive panel layout;
- dockable/movable/resizable panels;
- layout presets for hunting, bosses, PvP, trading;
- proper 21:9 and potentially 32:9 support.

## Competitive visibility constraint

A wider monitor must not automatically create unfair PvP information advantage.

Evaluate:

- server-controlled gameplay visibility range;
- larger visual viewport without unlimited dynamic entity visibility;
- fixed competitive visibility rules where needed.

`OPEN`

- OTClient renderer/protocol limits;
- exact distinction between rendered terrain and authoritative visible entities.

---

# 16. Boss System 2.0

`USER-DIRECTION`

Current bossing is considered highly frustrating because of:

- long group search time;
- repeated travel time;
- rigid five-player expectations;
- large time cost;
- extreme loot RNG where one player can kill a boss many times with nothing while another gets repeated drops.

Summer Update 2026 boss-system ideas were discussed as useful inspiration, especially difficulty scaling/practice concepts and bad-luck protection. Reverify current official behavior before implementation.

## Adventure Guild Boss Hub

`USER-DIRECTION`

Adventure Guild is the preferred physical location for the Boss Hub.

The hub should not trivialize exploration.

Fast access should be earned.

Possible unlock conditions:

- access quest completed;
- boss physically discovered/reached;
- boss killed at least N times;
- Bosstiary milestone;
- relevant Bestiary/region progression.

Possible mastery states:

- Discovered;
- Accessed;
- Experienced;
- Mastered.

Rewards can unlock convenience such as fast travel and advanced difficulty access.

Core principle:

First engage with and learn the content; repeated travel becomes optional after mastery/unlock.

## Boss Finder integration

Use Party Finder 2.0 rather than chat spam.

Potential flow:

boss selection -> difficulty -> desired party -> join requests -> ready check -> Boss Lobby.

## Flexible party size

`USER-DIRECTION`

Remove rigid dependence on exactly five players where feasible.

Target concept:

- 2–5 players;
- scale encounter mechanics, not only HP;
- avoid a simple linear HP formula that creates one optimal exploitable group size.

## Boss Lobby

After party assembly:

- teleport to lobby;
- equipment preparation;
- difficulty selection;
- ready check;
- start encounter;
- retry/next difficulty/leave options after completion.

## Difficulty system

Potential modes:

- Training/Practice: reduced risk, no or minimal rewards;
- Normal;
- scalable difficulty tiers.

Higher levels should introduce meaningful mechanics, not merely HP/damage inflation.

## Personal loot

Consider personal loot rolls to reduce party conflict.

## Bad Luck Protection / pity

`USER-DIRECTION`

Avoid unlimited bad luck.

Preferred structure:

- base RNG remains exciting;
- failed attempts increment personal bad-luck protection;
- visible progress where practical;
- soft pity;
- optional hard pity or guaranteed progression endpoint.

## Boss Essence / guaranteed progression currency

`DESIGN-DIRECTION`

Each successful kill may provide bounded progression currency/fragments so a no-drop evening still advances the player toward a target.

Core formula:

RNG drop + pity + guaranteed progression.

## Leaderboards/mastery

Potential prestige for highest difficulty cleared and boss mastery.

`OPEN`

- loot economy impact;
- cooldown model;
- exact unlock counts;
- difficulty scaling math;
- party-size scaling rules.

---

# 17. Monster Collision & Movement Rework

`USER-DIRECTION`

Current hard body blocking is useful for danger/positioning but becomes frustrating when trivial monsters block movement or when a player is fully surrounded with almost no recovery option.

## Threat-Based Monster Collision

Use monster difficulty/threat category plus relative player power.

Potential behavior:

- harmless relative to player: no hard block;
- trivial: automatic pass-through/push/swap;
- low threat: soft collision;
- normal threat: standard body block;
- elite/boss/special blockers: full body block.

This is preferable to a universal "players can walk through all monsters" rule.

Examples motivating the design:

- high-level player stopped repeatedly by Bugs or Goblins in one-SQM corridors;
- weak legacy monsters creating travel friction with no meaningful gameplay decision.

## Break Free / Emergency Breakthrough

`DESIGN-DIRECTION`

For genuine dangerous surrounds, consider an active limited escape mechanic:

- cooldown;
- resource cost or temporary debuff;
- pass through one occupied tile;
- boss/special exceptions;
- PvP-specific rules.

Purpose:

Preserve risk from poor positioning while giving a limited emergency response instead of guaranteed helpless death.

## Vocation differences

`OPEN`

Different escape styles by vocation may be considered, but are not yet a requirement.

---

# 18. Transition, Ladder, Hole & Teleport Safety Rework

`USER-DIRECTION`

Current holes, ladders, stairs, teleports and similar transitions create several frustration points:

- exits/holes can be difficult to see on the floor;
- corpses and items can visually cover them;
- items/corpses can interfere with interaction;
- destination points can be trapped by monsters;
- players can arrive already fully surrounded with no meaningful reaction window.

Screenshots shown during discussion illustrated transition destinations densely surrounded by monsters.

## Visibility and interaction priority

- highlight transitions more clearly;
- optional transition markers;
- higher interaction priority than corpses/decorations;
- corpse/item on top should not make the transition unusable;
- optional dedicated "use transition" action/hotkey;
- possible minimap markers.

## Safe landing rules

Transition destination should provide a bounded minimum safety guarantee without becoming a permanent safe zone.

Potential rules:

- transition tile cannot be occupied by a monster;
- nearby protected landing tiles do not allow a full instant surround;
- brief transition protection;
- protection ends on offensive action;
- monsters on required escape tiles may be displaced under controlled rules;
- no hostile spawn directly on protected transition tiles.

## Guaranteed Escape Path / Safe Transition Corridor

`USER-DIRECTION`

After a forced transition, the player should have at least one legal immediate route out of the landing area.

Core distinction:

- being boxed during combat is valid danger;
- spawning into a pre-existing unavoidable box is a transition-design failure.

## PvP anti-abuse

Do not let players repeatedly cycle a ladder/teleport to reset protection indefinitely.

Combat lock and transition cooldown rules must prevent this becoming a free combat reset.

---

# 19. Fishing System 2.0

`USER-DIRECTION`

Fishing is considered underdeveloped and a large source of unused gameplay potential.

Potential system:

- Fishing Mastery/skill;
- different water biomes;
- fishing hotspots;
- bait types;
- active bite/reel interaction;
- common/rare/epic/legendary fish;
- size/weight records;
- Fishing Codex;
- treasure fishing;
- fishing contracts/tasks;
- tournaments and social events.

Avoid turning fishing into a passive AFK gold farm.

Anti-bot telemetry should be considered from the start.

---

# 20. Cooking, Fish Food and Buff Consumables

`USER-DIRECTION`

Fishing should feed into a useful cooking/consumable ecosystem.

Potential outputs:

- normal food;
- long-duration preparation food;
- stews/soups;
- resistance-oriented food;
- utility food;
- limited offensive/defensive buffs;
- rare recipes using rare fish.

Design distinction:

- potions remain immediate combat consumables;
- food is longer-duration preparation/build support.

Avoid making one food buff mandatory for every hunt.

Possible rule:

- only one major food buff active at a time.

Exact buff strength remains `OPEN`.

---

# 21. House Chef / Cooking 2.0

`USER-DIRECTION`

The existing idea of a house cook/hireling should be expanded rather than ignored.

Potential loop:

Fishing -> ingredients -> recipes -> House Chef -> prepared food -> hunt/boss preparation.

Possible behavior:

- player supplies ingredients;
- pays cooking fee;
- chooses recipe;
- advanced recipes require unlocks/quests/mastery;
- house chef may be cheaper or more convenient than a public cook;
- public cooking remains available so houses do not become mandatory for core progression.

This is also a natural economy sink.

---

# 22. Economy Sink Framework

`USER-DIRECTION`

Create intentional money sinks to control inflation, but prefer sinks players want to use.

## Preferred categories

### Houses

- rent;
- upgrades;
- storage;
- servants/hirelings;
- chef;
- other convenience services;
- premium decorations/luxury upgrades.

### Cooking/Fishing

- cooking service fees;
- bait;
- rare bait;
- processing;
- fishing travel/license/event fees where appropriate.

### Boss convenience

- fast travel fees;
- optional convenience services;
- advanced challenge/crafting fees.

Do not make basic boss access prohibitively expensive.

### Market/Bank/Trade

- small controlled market fees;
- optional premium listing/service fees;
- carefully designed transfer/trade fees only if they do not push players to bypass the system.

### PvP

- arena/tournament/guild-war entry fees;
- cosmetic/prestige sinks.

### Luxury sinks

Very expensive cosmetics, house upgrades, visual prestige and other nonessential goals can remove large amounts of gold from wealthy players.

## Sink philosophy

Three useful levels:

- small mandatory sinks;
- medium optional convenience sinks;
- large luxury sinks.

Avoid relying primarily on:

- harsh death costs;
- expensive basic consumables;
- punitive travel costs;
- frequent mandatory repair chores.

---

# 23. Equipment Durability & Maintenance

`USER-DIRECTION`

Item repair may be useful as a money sink only if designed as soft, infrequent maintenance rather than constant annoyance.

Preferred rules:

- no permanent item destruction;
- slow durability decay;
- no sudden weapon shutdown during combat;
- clear low-durability warnings;
- 0% may mean reduced effectiveness rather than total unusability;
- Repair All;
- optional Auto Repair at appropriate service points;
- predictable cost shown before repair;
- no requirement to manually remove every item.

Possible service locations:

- city blacksmith;
- Adventure Guild;
- house blacksmith/hireling;
- portable repair with a convenience premium.

Cost should depend on controlled game data such as item tier/class/durability lost, not volatile player-market price.

Preferred player experience:

"repair once every several sessions" rather than "repair every hunt".

`OPEN`

- whether durability is needed at all after broader economy simulation;
- decay rate;
- endgame versus beginner cost curve;
- interaction with Forge and imbuements.

---

# 24. System dependency map

`DERIVED`

These systems should be designed together where practical:

## Discovery/social cluster

Huntfinder
+ Hunting Spot Availability
+ Party Finder 2.0
+ Boss Finder
+ Soul Core Finder

## Boss cluster

Adventure Guild Boss Hub
+ Boss Mastery
+ Party Finder 2.0
+ Boss Lobby
+ Difficulty System
+ Personal Loot
+ Pity
+ Boss Essence

## Death/security cluster

Death System 2.0
+ Death Fatigue
+ Recovery Pool
+ Connection Loss Protection
+ Disconnect Abuse Detection
+ AI Gameplay Security Platform

## Economy cluster

Bank UI
+ Trade System
+ Transaction History
+ Cooking/Fishing
+ House services
+ Money Sink Framework
+ optional Durability

## Client UX cluster

Adaptive UI
+ scalable viewport
+ minimap character markers
+ transition highlighting
+ Huntfinder/Party Finder panels

## Movement/safety cluster

Threat-Based Collision
+ Break Free
+ transition safety
+ guaranteed escape path

---

# 25. Implementation policy for future agents

1. Treat this roadmap as product direction, not implementation proof.
2. Before implementing one system, create a separate bounded task record.
3. Reverify current Canary/OTClient architecture and reusable modules.
4. For Real Tibia parity or inspiration claims, use current evidence at implementation time.
5. Quantitative values in this document are examples only unless later promoted into an explicit contract.
6. Run abuse analysis for any system that creates transferable value, PvP rewards, disconnect protection, teleport convenience, personal loot or automated actions.
7. Prefer incremental rollout and telemetry before irreversible balance decisions.
8. Keep the game challenging; remove meaningless friction, not meaningful danger.

---

# 26. Skill Wheel Change Access

`USER-DIRECTION`

The skill wheel should be changeable outside the temple; being physically in a temple should not be a mandatory requirement for changing the wheel.

Required restriction:

- the character must have no PZ/combat lock;
- changing the skill wheel while PZ/combat locked must be blocked.

`OPEN`

- Exact server/client enforcement and the current Canary/OTClient skill-wheel implementation must be reverified before implementation.
