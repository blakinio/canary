# OTS Prey System 2.0

## Purpose

Durable future-design record for rebuilding the Prey system around real target use, flexible hunting plans and sustainable in-game maintenance.

This is product direction, not implementation proof. Exact costs, caps, time buckets, cooldowns, percentages, protocol fields and migration code remain open until implementation-time simulation and client/server contract work.

Related design:

- `docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS_EXTENSION_PACKS.md`
- `docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md`
- `docs/ai-agent/OTS_BOUNTY_AND_WEEKLY_TASKS_REWORK.md`
- `docs/ai-agent/OTS_DYNAMIC_SPAWN_AND_HUNTING_CAPACITY.md`

## Evidence labels

- `TIBIA-OFFICIAL`: verified current official Tibia behavior.
- `CANARY-CURRENT`: verified current behavior in this Canary fork.
- `OTCLIENT-CURRENT`: verified current behavior in upstream OTClient.
- `USER-DIRECTION`: explicitly requested by the user.
- `DESIGN-DIRECTION`: selected future product behavior.
- `OPEN`: requires implementation audit, simulation, telemetry or protocol design.
- `CONFLICT`: sources disagree or current behavior conflicts with intended semantics.

---

# 1. Problem statement

`USER-DIRECTION`

The current system creates two linked frustrations:

1. a player receives only a limited free opportunity to reroll the offered creature list, so choosing a creature creates pressure to hunt it immediately;
2. once a creature and good bonus are selected, preserving them for future sessions is expensive.

The most important failure is that active Prey time can be consumed while the player hunts something else. A player who changes spawn, helps a party, completes a quest or hunts a different monster can lose valuable Prey time without receiving the selected-target benefit.

Desired experience:

`choose or reserve a useful target -> activate the bonus when actually hunting it -> pause automatically away from that target -> return later without paying repeatedly merely to keep the creature`

Prey should encourage variety and planning, not punish a player for changing plans.

---

# 2. Current official Tibia baseline

`TIBIA-OFFICIAL`

Current official documentation states:

- a slot offers 9 creatures;
- one free list reroll becomes available every 20 hours;
- additional list rerolls cost gold based on character level;
- direct selection of a creature costs 5 Prey Wildcards;
- the available bonuses are damage boost, damage reduction, bonus XP and improved loot;
- a Prey lasts for 2 hours of hunting time;
- bonus reroll consumes 1 Prey Wildcard and resets the time;
- Automatic Bonus Reroll consumes 1 Prey Wildcard when the timer expires;
- Lock Prey preserves the selected creature and bonus and consumes 5 Prey Wildcards for each 2-hour renewal;
- up to 3 slots can exist depending on account status and permanent slot purchases.

`OPEN`

The exact current official server trigger that decrements hunting time is not proven by the public manual. The manual says the timer decreases while hunting, but that wording alone does not prove selected-creature-only consumption.

Therefore target-specific consumption in this document is an OTS design extension, not an official-parity claim.

---

# 3. Current Canary behavior

`CANARY-CURRENT`

The fork preserves the official-style slot model, bonuses, 2-hour duration, free reroll timestamp, gold rerolls, wildcard direct selection, automatic reroll and lock behavior.

Current time consumption is coupled to the generic stamina/experience path:

1. gaining experience from a non-player target calls the generic stamina function;
2. that function calls `player:removePreyStamina(60 or 120)`;
3. only afterwards does the XP path inspect the target race and apply the selected Prey XP percentage.

`CONFLICT`

This ordering means current Canary can consume active Prey time while the player gains experience from a creature that is not selected in any active Prey slot.

Current Lock Prey renewal also couples two different player needs:

- preserve the selected creature;
- preserve the exact bonus and its grade.

The implementation renews both together using the direct-selection price. A player cannot cheaply reserve the creature while allowing the bonus to expire.

---

# 4. Current OTClient boundary

`OTCLIENT-CURRENT`

The current `game_prey` module mirrors the official-style contract:

- list reroll;
- bonus reroll;
- creature selection;
- request/select from all creatures;
- one generic option action;
- option states `None`, `Automatic Reroll` and `Lock Prey`.

The UI explicitly describes:

- 2 hours of hunting time;
- 1 wildcard for automatic bonus reroll;
- 5 wildcards for Lock Prey.

`OPEN`

Prey System 2.0 requires an implementation-time client/server contract for new state and actions. The current client does not expose dormant target reservation, banked charges, selective renewal or active-use consumption status.

No OTClient change is included in this documentation task.

---

# 5. Core redesign: target-specific active-use time

`USER-DIRECTION`

`DESIGN-DIRECTION`

Prey time should decrease only when the player is meaningfully participating in combat against the selected creature for that slot.

The timer must not decrease because the player:

- kills unrelated creatures;
- changes hunting ground;
- travels, quests, trades or stays in protection zone;
- helps a party against another target;
- completes Bounty or Bestiary work on another creature;
- remains online while not fighting the selected creature.

Preferred server-authoritative rule:

> A Prey slot consumes active-use time only from eligible combat activity involving its selected race ID.

Possible eligible signals:

- qualifying damage or healing contribution against the selected creature;
- experience entitlement from the selected creature;
- loot eligibility from the selected creature;
- valid summon/familiar contribution attributed to the owning player.

The implementation should use a bounded activity bucket rather than subtracting time for every packet or hit. For example, selected-target activity may activate one server-side consumption interval with a small grace period.

`OPEN`

The exact bucket size and grace window require testing. They must avoid both:

- wasting time during normal pauses between pulls;
- allowing a player to receive long continuous value while consuming almost no time.

---

# 6. Mixed-spawn and party behavior

`DESIGN-DIRECTION`

Mixed spawns must remain practical.

If the selected creature is only part of a pull:

- the Prey bonus applies only to the selected race;
- the slot consumes time while the player has eligible activity against that race;
- killing other creatures in the same pull does not independently consume additional Prey time.

Party rules:

- a player who receives legitimate party experience/loot contribution for the selected race may consume the normal activity bucket;
- merely standing nearby without valid contribution must not consume time;
- party members use their own selected races and timers independently;
- one player's Prey state never changes another player's slot.

Summons and familiars:

- valid owner-attributed participation may count;
- unattended or non-rewarding summons must not create free activity or drain the owner's Prey without meaningful participation.

---

# 7. Dormant Prey target reservation

`USER-DIRECTION`

`DESIGN-DIRECTION`

Selected creature identity and active bonus time become separate state.

When active time reaches zero, the default state should be:

- the bonus becomes inactive/dormant;
- the selected creature remains reserved in the slot;
- no further time or currency is consumed;
- the player may reactivate, reroll the bonus, release the target or replace it.

Keeping the creature reserved should not require a recurring wildcard payment.

This solves the core planning problem:

> The player can keep a useful creature for a future hunt without paying every two hours simply to prevent the target from disappearing.

A reserved target grants no combat benefit until the bonus is reactivated.

`OPEN`

A bounded reservation limit or inactivity expiry may be considered only if telemetry proves permanent reservations harm target variety or economy. The default product direction is no recurring reservation fee.

---

# 8. Separate target lock, bonus lock and renewal

`DESIGN-DIRECTION`

The existing combined Lock Prey action should be separated into three responsibilities.

## 8.1 Reserve Target

- preserves the selected creature;
- does not preserve active time;
- does not guarantee the current bonus type or grade after reactivation;
- has no recurring wildcard cost.

## 8.2 Preserve Bonus

- preserves the current bonus type and grade while dormant;
- may require a bounded in-game cost, charge or optional wildcard;
- does not automatically spend anything unless the player explicitly enables renewal.

## 8.3 Reactivate / Renew Time

- adds a bounded amount of active-use time;
- consumes one selected payment source shown before confirmation;
- never silently consumes a more valuable currency when a cheaper configured source is available.

Automatic renewal remains optional and must display:

- selected payment source;
- cost per renewal;
- number of renewals currently affordable;
- estimated active-use time available.

---

# 9. Bankable free Prey charges

`USER-DIRECTION`

`DESIGN-DIRECTION`

The free reroll cadence should become a bankable resource instead of a use-it-now opportunity.

Proposed model:

- each eligible slot generates a free Prey Charge on the normal cadence;
- unused charges accumulate to a bounded cap;
- a charge may be used for either a list reroll or reactivation of a reserved target;
- the UI shows current charges, next charge time and cap;
- reaching the cap stops generation but does not delete stored charges.

This lets occasional players save several free decisions and use them when they actually have time to hunt.

`OPEN`

The exact cap remains open. A preliminary evaluation range is 3-7 charges per slot, but no value is approved as an implementation constant.

Direct selection of any creature may remain a stronger action with a different cost.

---

# 10. Sustainable maintenance paths

`USER-DIRECTION`

`DESIGN-DIRECTION`

Prey System 2.0 should preserve useful economy sinks without making Store-linked wildcards the practical requirement for maintaining normal gameplay.

Possible payment sources:

1. banked free Prey Charges;
2. gold;
3. gameplay-earned Prey Marks or another non-tradeable hunt resource;
4. Prey Wildcards as an optional convenience/fallback.

Preferred principles:

- reserving a target costs nothing recurring;
- reactivation has a clear bounded cost;
- gold cost should use level/power bands or controlled daily escalation rather than unbounded punishment for high level alone;
- gameplay-earned currency should come from genuine eligible hunting, not AFK loops;
- wildcards may remain useful for direct selection, instant high-grade preservation or convenience, but should not be the only practical maintenance path;
- no hidden automatic conversion between gold, marks and wildcards.

`OPEN`

Exact prices and earning rates require economy simulation. The redesign must be evaluated together with Bounty, Weekly Tasks, Bestiary, Charms, Dynamic Spawn and server inflation controls.

---

# 11. Prey loadouts and hunt planning

`DESIGN-DIRECTION`

The client may support bounded Prey profiles such as:

- solo hunt;
- party hunt;
- boss access route;
- Bestiary session;
- Bounty session.

A profile may remember:

- preferred target per slot;
- preferred bonus type priority;
- automatic renewal preference;
- allowed payment sources and priority;
- maximum spend per session/day.

Profiles do not grant targets or bonuses. They only reduce repetitive configuration and must respect server-authoritative availability, costs, cooldowns and slot rules.

---

# 12. Switching safeguards

`DESIGN-DIRECTION`

Target-specific time must not enable rapid tactical abuse.

Required safeguards:

- target replacement and bonus-state changes are blocked during combat lock;
- switching may require protection zone or another safe state;
- no retroactive application to creatures already defeated;
- the server validates selected race, state, balance and payment atomically;
- repeated activate/deactivate requests are rate-limited;
- active-use time is stored server-side and cannot be client-controlled;
- logout, crash and reconnect preserve the last authoritative state without double charging;
- no active Prey benefit in explicitly excluded training, test or non-reward encounters.

`OPEN`

Whether reactivation requires protection zone or only absence of combat lock is an implementation-time UX/balance decision.

---

# 13. Relationship to Bounty and Weekly Tasks

`DESIGN-DIRECTION`

Prey, Bounty and Weekly Tasks remain separate systems:

- Prey modifies combat rewards against a selected race;
- Bounty provides a bounded kill contract and Bounty progression;
- Weekly Tasks provide scheduled objectives and rewards.

Possible synergy may be evaluated later, but must not be implicit.

Examples that require separate approval:

- one discounted Prey reactivation for the active Bounty target;
- limited Prey Marks from completed Bounty contracts;
- target recommendations shared between Huntfinder, Bounty and Prey.

The default redesign does not automatically assign a Bounty target as Prey, bypass selection costs or multiply every reward layer without caps.

---

# 14. UI and transparency requirements

`DESIGN-DIRECTION`

Each slot should clearly show:

- selected creature;
- state: available, active, dormant/reserved, selection or locked slot;
- bonus type and grade;
- active-use time remaining;
- whether time is currently being consumed and why;
- banked free charges and next charge time;
- reservation status;
- bonus-preservation status;
- automatic-renewal source and cost;
- estimated renewals affordable;
- explicit buttons for reactivate, release target, change target, reroll bonus and configure renewal.

The player should never have to guess whether hunting another creature is draining Prey time.

---

# 15. Migration contract

`DESIGN-DIRECTION`

Implementation must migrate existing slots without deleting legitimate player value.

For each existing active slot preserve:

- selected race ID;
- bonus type;
- bonus percentage/grade;
- remaining time;
- slot ownership/unlock state;
- free reroll timestamp;
- wildcard balance.

Suggested option migration:

- current `None` -> active until expiry, then dormant target reservation;
- current `Automatic Reroll` -> automatic renewal enabled with the closest compatible source, but no new source may be charged without explicit player confirmation;
- current `Lock Prey` -> reserve target + preserve bonus preference, with automatic spending disabled until the player confirms the new cost/source policy.

Migration must not:

- charge wildcards during deployment;
- duplicate remaining time;
- reset a good bonus;
- unlock paid slots for free;
- remove stored wildcards or free-reroll progress.

---

# 16. Telemetry and balance review

`OPEN`

Before final values are selected, measure:

- percentage of Prey time currently consumed off-target;
- average active time used before players abandon a target;
- wildcard spend by action;
- gold reroll spend by level band;
- frequency of Lock Prey renewal;
- time between selecting a target and actually hunting it;
- dormant reservation duration;
- free-charge generation and cap saturation;
- target diversity and concentration;
- stacking impact with Charms, Bounty Talisman, boosted creatures and hunting events.

Success criteria:

- substantially less off-target waste;
- more players use Prey without feeling forced into one spawn;
- selected targets can be saved for later without recurring payment;
- high-value bonus preservation remains a meaningful decision;
- economy sinks remain useful but understandable and non-punitive;
- no material exploit from rapid switching or near-zero timer consumption.

---

# 17. Proposed implementation phases

## Phase 1 — correctness and state separation

- selected-race activity consumption;
- dormant target reservation;
- separate server states for target, bonus and active time;
- migration of existing slots.

## Phase 2 — sustainable renewal

- bankable free charges;
- explicit gold/gameplay/wildcard payment sources;
- atomic renewal and spend limits;
- telemetry.

## Phase 3 — client UX and profiles

- new OTClient state/actions;
- consumption indicator;
- renewal-cost forecast;
- bounded Prey profiles.

Each phase requires a new implementation task with current official Tibia, Canary and OTClient parity rechecked at that time.

---

# 18. Final product direction

`USER-DIRECTION`

`DESIGN-DIRECTION`

Prey System 2.0 should follow these rules:

1. unrelated hunting does not consume selected Prey time;
2. the selected creature may remain reserved after the bonus expires;
3. reserving a creature has no recurring wildcard fee;
4. preserving a maximum bonus is separate from preserving the target;
5. free decisions can be banked within a bounded cap;
6. reactivation supports transparent in-game payment paths;
7. wildcards remain optional convenience, not the only practical maintenance method;
8. mixed spawns and party hunts consume time only through legitimate selected-race activity;
9. switching is server-authoritative and combat-safe;
10. exact constants remain `OPEN` until simulation and implementation-time review.
