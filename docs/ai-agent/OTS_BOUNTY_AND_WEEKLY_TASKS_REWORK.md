# OTS Bounty and Weekly Tasks Rework

## Purpose

Durable design record for the Bounty Task, Weekly Kill Task, Weekly Delivery Task and Bounty Talisman rework discussed with the user on 2026-07-23.

This is product direction, not an implementation contract. Exact formulas, caps, probabilities, costs and level ranges remain open until the current Canary implementation and current Real Tibia behavior are audited.

Related design:

- `docs/ai-agent/OTS_DYNAMIC_SPAWN_AND_HUNTING_CAPACITY.md`
- `docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md`

## Evidence labels

- `USER-DIRECTION`: explicitly requested or approved by the user.
- `DESIGN-DIRECTION`: accepted design direction that still needs implementation analysis.
- `SOURCE-VERIFIED`: behavior checked against current external source material during the discussion.
- `OPEN`: requires source-of-truth audit, balancing, telemetry or abuse analysis.

---

# 1. Product goal

`USER-DIRECTION`

Bounty should become a strong alternative gameplay loop, especially for players with limited play time.

Desired experience:

`log in -> receive/select sensible Bounty -> quickly find a viable spawn -> complete a bounded objective -> gain normal hunt rewards + Bounty progression`

The system should reduce the frustration:

> I only have one or two hours to play, my preferred spawn is occupied, so I do not play today.

Normal hunting remains valuable for freedom and long-session optimization. Bounty should reward flexibility, variety, shorter goals and long-term Bounty progression.

Bounty must not become a mandatory daily chore or the universally best source of XP and profit.

---

# 2. Current four difficulty groups are too broad

`SOURCE-VERIFIED`

The current Bounty difficulty mapping discussed here is:

- Beginner -> Easy creatures;
- Adept -> Easy + Medium;
- Expert -> Medium + Hard;
- Master -> Hard + Challenging.

`USER-DIRECTION`

This classification is too coarse as the only basis for task generation.

Two creatures in the same Bestiary difficulty may have completely different:

- kills/hour;
- number and size of spawns;
- share in mixed spawns;
- access difficulty;
- congestion;
- recommended level/power;
- solo/party viability;
- real completion time.

The four visible tiers may remain, but the server should use a richer hidden `Task Suitability` model.

Possible internal inputs:

- Bestiary difficulty;
- recommended level/effective-power range;
- expected kills/hour;
- spawn capacity;
- number of viable spawns;
- mixed-spawn share;
- solo/party profile;
- access/travel overhead;
- congestion;
- expected completion time.

Core principle:

> Beginner/Adept/Expert/Master should describe expected difficulty and commitment for this player, not simply expose a huge static bucket of creatures.

---

# 3. Difficulty should be relative to player progression

`USER-DIRECTION`

A level 100 choosing Master should not routinely receive targets effectively intended for level 500-1000 characters.

Preferred order:

`player progression/effective power -> sensible eligible creature pool -> selected tier -> suitability filters -> offers`

Intent:

- Beginner: short/easy relative to current player;
- Adept: moderate;
- Expert: harder or longer;
- Master: the hardest sensible contract for the player, not inaccessible content.

Level should remain an understandable guide, but the hidden model may also consider vocation, equipment, access quests, charms/imbuements, party context and Bounty Talisman progression.

---

# 4. Kill counts should scale from real expected effort

`USER-DIRECTION`

Raw kill count is not a reliable measure of task difficulty.

A task should not demand 600 kills merely because it belongs to a higher tier when the creature can only be killed at roughly 100/hour on available spawns.

Preferred model:

`expected kills/hour x target task-duration range -> sensible kill target`

with minimum/maximum bounds and adjustments for:

- spawn capacity;
- number of viable spawns;
- occupancy;
- player's effective power;
- mixed-spawn share;
- solo/party context.

A low-density Master target may require fewer kills than a high-density Master target.

Core principle:

> Tier should define expected effort and reward, not a rigid kill-count bracket.

---

# 5. Why players choose Beginner

`USER-DIRECTION`

Many players choose Beginner because it is predictable, fast and easy even though they knowingly sacrifice XP and Bounty Points.

This means the higher tiers often have poor reward-to-real-effort balance or excessive variance.

Higher tiers should become attractive through:

- sensible target selection;
- more predictable completion time;
- proportionally better XP and Bounty Points;
- spawn-capacity awareness.

Higher tier should not mean:

> sometimes great, sometimes punishment for bad RNG.

---

# 6. Dynamic XP and Bounty Point rewards

`USER-DIRECTION`

Rewards should not rely mainly on rigid caps disconnected from the player and target.

Potential inputs:

- level;
- effective power;
- target difficulty relative to player;
- expected completion time;
- kills/hour;
- spawn capacity;
- solo/party profile;
- Bounty Talisman progression;
- opportunity cost versus the player's normal hunting options.

Conceptually:

`player power + target difficulty + expected effort + spawn reality + tier -> dynamic XP/Point reward`

A player should not feel strongly punished in XP for choosing a well-matched Bounty instead of camping the same optimal spawn all day.

At the same time, Bounty does not need to always beat the best possible normal hunt because it also provides Bounty Points, Talisman progression, Bestiary progress, variety and session guidance.

`OPEN`

Final formulas require telemetry and simulation across representative levels and vocations.

---

# 7. Task scaling must not cancel Talisman progression

`USER-DIRECTION`

As the Talisman becomes stronger, the system may offer stronger or more rewarding contracts, but it must not increase workload so aggressively that the player's earned power becomes meaningless.

Bad outcome:

- before upgrade: 300 kills in 2 hours;
- after major upgrade: 600 kills in 2 hours.

Desired outcome:

- stronger Talisman gives a real efficiency/power benefit;
- contracts may become somewhat harder or more rewarding;
- the player still feels that months of Bounty progression made them a better Bounty Hunter.

---

# 8. Developed Talisman may grant bounded access to harder content

`USER-DIRECTION`

A major long-term reward can be temporary access to stronger hunting grounds.

The Talisman bonus is limited by two important factors:

1. it applies only to the active Bounty target;
2. the task requires a finite number of kills.

Therefore a developed player may temporarily handle a stronger target during a Bounty without receiving unrestricted permanent power for all-day farming.

This is especially important on mixed spawns. A spot may contain 2-5 creature types, while the Talisman only boosts one active target.

Balance must therefore consider the target's real share of:

- total kills;
- combat time;
- damage taken;
- loot generation.

A +50% headline bonus against one creature does not automatically mean +50% efficiency for the whole hunt.

---

# 9. Dedicated Bounty equipment slot

`USER-DIRECTION`

Preferred direction: move the Bounty Talisman to a dedicated `Bounty Equipment Slot` rather than keep it as a normal Trinket or create a second universal ring slot.

Reasons:

- a second normal ring slot would change balance across the entire equipment system;
- a dedicated slot keeps the change scoped to Bounty;
- the Talisman can remain a permanent long-term progression item;
- future Bounty-specific artifacts can use the same slot if explicitly designed for it.

`OPEN`

Removing equipment opportunity cost makes the Talisman effectively stronger, so bonus values must be analyzed with the dedicated-slot design included.

---

# 10. Talisman bonus families

`USER-DIRECTION`

The current four core ideas are fundamentally good:

- damage;
- life leech;
- additional loot;
- doubled Bestiary progress.

The preferred redesign expands them into four clearer paths.

## Combat Mastery

Primary:

- increased damage against active Bounty target.

Possible secondary:

- reduced damage received from the active Bounty target.

The defensive effect should be target-specific and likely weaker/lower-capped than the damage effect.

## Sustain Mastery

- Life Leech;
- Mana Leech.

Adding Mana Leech may make this path more broadly useful across vocations.

Life and Mana Leech do not need identical caps or progression curves.

## Bounty Spoils

- keep additional loot against the active target.

This is an attractive long-term reward but must be monitored together with higher damage, dynamic respawn and item-generation rates.

## Bounty Knowledge

Before Bestiary completion:

- accelerated/doubled Bestiary progress.

After Bestiary completion:

- convert the otherwise dead bonus into a bounded Bounty progression reward, preferably additional Bounty Point value tied to contract completion.

It should not generate unlimited Bounty Points per kill.

---

# 11. More noticeable Knowledge progression

`USER-DIRECTION`

The Bestiary/Knowledge upgrade path may feel too granular when meaningful stages increase by roughly 1 percentage point.

Possible direction:

- use more noticeable upgrade steps, potentially around 2 percentage points;
- adjust upgrade costs and number of levels accordingly;
- final cap remains subject to balancing.

The goal is not necessarily a higher maximum. The goal is that spending Bounty Points produces a noticeable improvement.

---

# 12. Do not judge Talisman caps in isolation

`USER-DIRECTION`

Values such as high damage, leech or loot bonuses must be analyzed together with:

- one-target-only scope;
- finite task kill count;
- mixed-spawn dilution;
- dedicated Bounty slot;
- Dynamic Spawn Scaling;
- Prey/other modifiers;
- player effective power;
- economic impact.

High nominal bonuses may be appropriate as a reward for months of Bounty progression if their real scope remains bounded.

Final caps require simulation.

---

# 13. Weekly Kill Tasks must be spawn-capacity-aware

`USER-DIRECTION`

Weekly Kill target counts should consider:

- real kills/hour;
- number of available spawns;
- average occupancy;
- spawn capacity;
- player level/power;
- target share in mixed spawns;
- dynamic-spawn eligibility.

The goal is to assign a sensible amount of real play time, not an arbitrary number of kills.

---

# 14. Weekly Delivery Tasks must respect player accessibility

`USER-DIRECTION`

A player should not routinely receive delivery requirements for items sourced mainly from content far beyond their progression.

Example failure mode:

- level 500 player;
- item primarily sourced from hunting grounds intended for level 1000-2000 characters;
- required in a large quantity.

Task generation should consider:

- player level/effective power;
- access to source locations;
- source creatures;
- solo/party requirements;
- drop rate;
- realistic acquisition/hour;
- market availability.

The market may be an alternative route, but should not be the only realistic route because the assigned source content is inaccessible.

---

# 15. Weekly Delivery as an intelligent item sink

`USER-DIRECTION`

One of the best properties of Weekly Delivery is that it can remove oversupplied items from circulation instead of sending them meaninglessly to NPCs.

Desired effects:

- consume genuine oversupply;
- create player-to-player demand;
- improve market rotation;
- revive economic value of older hunting grounds;
- reduce NPC dumping.

This should become an economy-aware item sink rather than random item demand.

---

# 16. Analyze total server supply, not only market stock

`USER-DIRECTION`

Visible market supply is incomplete.

The system should consider aggregated supply in:

- market;
- player stash;
- depot/storage;
- inventory where appropriate;
- item generation rate;
- item consumption/destruction rate.

The economic controller needs aggregated totals, not player-facing information about who owns what.

Example principle:

`Total Server Supply = visible liquid supply + hidden stored supply`

---

# 17. Global Weekly Delivery Demand Controller

`USER-DIRECTION`

The system must prevent 10 or 100 players from independently receiving the same item and suddenly turning a cheap item into an artificially scarce one.

Preferred architecture:

`economy analysis -> safe weekly demand budget per item -> task assignment reservations -> monitor market reaction`

Potential signals:

- total server stock;
- market stock;
- number of holders/sellers;
- weekly volume;
- median price and trend;
- order-book depth;
- item generation rate;
- existing active Weekly demand.

When a delivery task is assigned, its required quantity should reserve part of the global item-demand budget.

This prevents independent RNG from creating impossible aggregate demand.

---

# 18. Price Shock Guard

`DESIGN-DIRECTION`

If task-generated demand causes an abnormal price jump or collapses available supply, the system should be able to:

- stop assigning new tasks for that item;
- allow already active tasks to finish;
- reduce the future demand budget;
- flag the item for analysis.

Exact thresholds remain open.

---

# 19. AI-assisted economy control with deterministic safety limits

`USER-DIRECTION`

AI may be useful for:

- forecasting supply;
- detecting oversupply;
- predicting likely price impact;
- identifying slow-moving inventory;
- recommending good item-sink candidates;
- detecting anomalies.

But deterministic rules should remain authoritative for:

- maximum generated demand;
- maximum market absorption;
- per-item concentration limits;
- price-shock stops;
- hard economy safety caps.

AI should recommend and forecast, not have unrestricted authority to create demand.

---

# 20. Delivery selection uses three filters

`DESIGN-DIRECTION`

A delivery item should ideally pass all three:

1. `Player Suitability` - player can reasonably obtain/access the source.
2. `Server Availability` - sufficient real total supply exists.
3. `Economic Usefulness` - temporary demand helps absorb oversupply rather than create scarcity.

Conceptually:

`player suitability + total server supply + market liquidity + oversupply score + global demand budget -> eligible item`

---

# 21. Preferred and Unwanted lists

`USER-DIRECTION`

Preferred/Unwanted creature lists are a good foundation, but long-term Bounty progression should provide more control.

Possible unlocks:

- more Preferred slots;
- more Unwanted slots;
- preferred region;
- preferred solo/party profile;
- preferred task-duration range.

Preferred should increase selection weight rather than guarantee one optimal creature forever.

Recently completed targets may receive temporarily reduced weight to encourage variety without overriding suitability.

---

# 22. More reroll availability

`USER-DIRECTION`

Current effective reroll availability is too restrictive for such broad creature pools.

Players should have more ways to escape bad or unsuitable offers.

However, unlimited cheap rerolls would enable endless fishing for the best XP/profit target.

Possible direction:

- more baseline rerolls;
- progression-based reroll improvements;
- several cheap/free rerolls followed by escalating cost;
- reset after task completion or another bounded cycle;
- stronger Preferred/Unwanted controls to reduce reroll dependence.

Exact token counts and costs remain open.

---

# 23. Bounty progression should improve contract quality too

`USER-DIRECTION`

Long-term progression should not only increase combat stats.

A more experienced Bounty Hunter may gradually unlock:

- stronger Talisman bonuses;
- more Preferred slots;
- more Unwanted slots;
- more reroll capacity;
- better reroll economics;
- better region/task-duration control;
- access to more challenging but still suitable contracts.

Progression fantasy:

> an experienced Bounty Hunter gets better at selecting, preparing for and completing contracts.

---

# 24. Bounty Chains and Variety Bonuses

`DESIGN-DIRECTION`

Possible optional incentives:

- bounded Bounty Chain bonus for completing several contracts in sequence;
- Variety Bonus for completing different creature families or regions.

Potential rewards:

- extra Bounty Points;
- small XP bonus;
- reroll resource;
- improved chance of special contracts.

These should not create daily-login FOMO or infinite scaling.

---

# 25. Integration with Huntfinder and Hunting Spot Availability

`USER-DIRECTION`

A Bounty offer should be useful immediately.

Potential integration:

`Bounty selected -> Huntfinder shows viable spots -> Hunting Spot Availability shows free/shareable/saturated status -> Dynamic Spawn safely increases capacity where allowed`

Future UI may also show:

- recommended level/power;
- estimated completion-time range;
- solo/party suitability;
- available hunting locations;
- current occupancy/capacity.

---

# 26. Integration with Dynamic Spawn and overleveled Bounty players

`USER-DIRECTION`

An overleveled player may legitimately return to an older spawn because the active Bounty requires that creature.

The system should distinguish:

- permanent overlevel farming;
- temporary bounded Bounty completion.

A limited Bounty Spawn Allowance may temporarily relax overlevel restrictions on dynamic spawn.

When the Bounty ends, the allowance ends.

Bounty itself should not directly force a specific target to respawn faster; normal spawn budgets, active-hunter checks and rare/boss exclusions still apply.

Detailed design lives in `OTS_DYNAMIC_SPAWN_AND_HUNTING_CAPACITY.md`.

---

# 27. Economy interaction: Bounty Spoils vs Delivery sink

`DESIGN-DIRECTION`

The broader system contains two opposing economic forces:

`Bounty Spoils + higher kill throughput -> more item generation`

`Weekly Delivery -> item removal`

This creates an opportunity for a coordinated economy controller.

The system can observe which materials are accumulating because of popular Bounty targets and later use Weekly Delivery to safely absorb genuine oversupply.

This must remain bounded by deterministic economy rules.

---

# 28. Telemetry required

`DESIGN-DIRECTION`

Bounty/Weekly telemetry should include at least:

- offers generated/selected/rerolled;
- completion and abandonment rate;
- real completion time;
- kills/hour;
- player level/effective power;
- Talisman progression;
- spawn occupancy and dynamic multiplier;
- XP/hour and profit/hour during task;
- target share in mixed spawn;
- Weekly Delivery assigned item/quantity;
- total server supply;
- market price/volume before and after assignment;
- global demand-budget usage;
- Talisman bonus contribution.

Without telemetry, dynamic balancing will be guesswork.

---

# 29. Anti-abuse concerns

`DESIGN-DIRECTION`

The design must protect against:

- reroll fishing for one best target;
- alt manipulation of dynamic spawn;
- keeping a Bounty almost complete to retain spawn allowance;
- unlimited Bounty Point farming from completed Bestiary;
- market manipulation intended to influence AI/item selection;
- excessive stacking of damage, loot, Prey and dynamic spawn;
- task-generated price shocks.

Primary protections:

- hard caps;
- global budgets;
- bounded rerolls;
- contract completion caps;
- deterministic safety rules;
- anomaly detection;
- explicit modifier-stacking contracts.

---

# 30. Source-of-truth requirement before implementation

`USER-DIRECTION`

Before implementation, agents must audit:

1. current `blakinio/canary` main;
2. current upstream `opentibiabr/canary`;
3. current authoritative Real Tibia Bounty/Weekly behavior;
4. actual implementation names and modules;
5. OTClient protocol/UI dependencies;
6. persistence/database requirements;
7. Task Board, Bestiary, Prey, loot and combat integration points.

This document records desired product direction. It is not proof of what the current server already implements.

---

# 31. Recommended workstreams

`DESIGN-DIRECTION`

1. Source-of-truth audit.
2. Creature Task Suitability model.
3. Progression-aware Bounty offer generator.
4. Preferred/Unwanted and reroll redesign.
5. Dynamic XP/Bounty Point rewards.
6. Dedicated Bounty equipment slot.
7. Talisman Combat/Sustain/Spoils/Knowledge redesign.
8. Capacity-aware Weekly Kill Tasks.
9. Economy-aware Weekly Delivery controller.
10. Market/stash/global-supply analysis and AI forecasting.
11. Huntfinder/Hunting Spot Availability/Dynamic Spawn integration.
12. Telemetry, simulation and staged rollout.

---

# 32. Final design principles

`USER-DIRECTION`

- Bounty should be an attractive gameplay loop for short sessions.
- Bounty should reduce frustration caused by occupied meta spawns.
- Four visible difficulty tiers may remain, but hidden task classification must be richer.
- Task counts should reflect real expected effort and spawn capacity.
- Higher tiers should reward proportionally better without becoming RNG traps.
- Player level/effective power should shape target eligibility.
- Weekly Delivery items should be realistically obtainable for the player's progression.
- Weekly Delivery should act as an intelligent item sink.
- Total server supply must include stash/storage, not only market listings.
- Global demand budgets must prevent dozens of players receiving the same scarce item.
- AI may forecast economy behavior, while deterministic safety caps remain authoritative.
- Bounty Talisman should preferably have a dedicated equipment slot.
- Talisman progression must produce real, felt target-specific power.
- Talisman power is bounded by one active target, mixed-spawn composition and finite task size.
- Combat Mastery may add weaker target-specific defense to damage.
- Sustain Mastery may combine Life and Mana Leech.
- Bounty Spoils should remain, with economy safeguards.
- Bounty Knowledge should remain useful after Bestiary completion through bounded Bounty Point progression.
- Knowledge upgrade steps may be made more noticeable, potentially around 2 percentage points, subject to balancing.
- Reroll availability should increase without enabling infinite target fishing.
- Preferred/Unwanted controls should improve with Bounty progression.
- Dynamic XP and Bounty Point rewards should reflect actual player/target/spawn effort.
- Task scaling must not erase Talisman progression.
- Dynamic Spawn may assist legitimate Bounty completion but must not create permanent overlevel farming abuse.
- All major formulas and caps require telemetry and simulation before finalization.

The guiding principle is:

> Bounty should turn a short or uncertain play session into a clear, rewarding adventure, while long-term Bounty progression makes the player genuinely better at fulfilling bounded contracts without creating unrestricted permanent power or economic instability.
