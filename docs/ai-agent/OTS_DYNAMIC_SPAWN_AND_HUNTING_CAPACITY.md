# OTS Dynamic Spawn and Hunting Capacity

## Purpose

Durable design record for a future dynamic monster-respawn and hunting-capacity system.

The goal is to let existing open-world hunting grounds support more players when the physical layout has enough space, but static respawn timers become the real bottleneck. The system should reduce unnecessary pressure to create instanced copies of hunting areas while avoiding a situation where high-level players can turn lower-level spawns into unlimited XP, loot, bestiary or rare-monster farms.

This document records product direction only. Exact formulas, thresholds, balancing values and implementation details remain open until the current Canary spawn system, monster metadata, hunting-area definitions and telemetry capabilities are audited.

## Evidence labels

- `USER-DIRECTION`: explicitly requested or approved by the user.
- `DESIGN-DIRECTION`: proposed design direction accepted as useful, but not yet specified as an implementation contract.
- `OPEN`: requires technical validation, balancing, gameplay analysis or abuse review.

---

# 1. Product intent

`USER-DIRECTION`

Many hunting grounds are physically large enough to accommodate more players, but their practical capacity is limited by static monster respawn timers.

A representative example is a large circular hunting route where one sufficiently strong player can clear the full loop in roughly two or three minutes and repeatedly arrive at empty rooms because the monsters have not respawned yet. In such a case, the map itself may have enough space for more activity, but the spawn throughput effectively limits the hunting ground to one player.

The desired system should:

- increase the effective capacity of suitable open-world hunting grounds;
- allow multiple players or parties to share a large location more naturally;
- reduce the need to solve population pressure by creating instanced copies of existing hunting grounds;
- reduce time spent running through empty spawn sections caused purely by static timers;
- preserve the open-world character of the game;
- avoid turning dynamic respawn into a universal XP or loot multiplier;
- preserve meaningful progression between lower-, mid- and high-level hunting grounds.

The core principle is:

> Dynamic respawn should scale for legitimate hunting-ground population pressure and unused physical capacity, not endlessly scale to match the farming power of one overleveled character.

---

# 2. Dynamic Spawn Scaling

`USER-DIRECTION`

A hunting ground may temporarily respawn monsters faster when real player activity shows that the area can support more simultaneous hunting than the base spawn timer currently allows.

The system must not use a naive rule such as:

> more characters present = faster respawn.

Instead it should evaluate real hunting pressure.

Potential signals include:

- number of actively hunting players;
- number of active parties;
- monster kill rate;
- percentage of the local monster population currently dead;
- average time monsters remain dead before respawning;
- frequency with which active hunters reach empty sections of the route;
- sustained combat activity;
- XP gain associated with real hunting activity;
- loot activity;
- time spent actively moving and fighting inside the hunting area.

`DESIGN-DIRECTION`

Scaling should be gradual rather than instant. A temporary spike in player count should not immediately multiply the spawn rate.

The system should increase respawn capacity only after sustained evidence that the area is genuinely under-respawned for its current active population. It should also return gradually toward the baseline when pressure disappears.

---

# 3. Hunting-ground capacity, not individual monster acceleration

`USER-DIRECTION`

The system should primarily reason about the capacity of a defined hunting ground or sector, not reward a player for repeatedly killing one specific monster.

Desired behavior:

- a player or group consistently clears most of a hunting sector faster than it refills -> the sector may receive limited additional respawn capacity;
- several active players occupy different parts of a large hunting ground -> relevant sectors may scale within configured limits;
- one player repeatedly farms one valuable monster -> that specific monster should not automatically respawn faster because it is being killed efficiently.

This distinction is a core anti-abuse requirement.

Dynamic scaling should normally apply to the ordinary population that forms the intended hunting loop.

The following categories should default to separate or stricter policies:

- rare monsters;
- bosses;
- quest-only monsters;
- event monsters;
- monsters with unusually valuable unique drops;
- monsters whose spawn frequency is itself part of progression or rarity;
- special bestiary targets where accelerated respawn would undermine intended scarcity.

Possible policy values include:

- dynamic respawn disabled;
- dynamic respawn enabled with a low cap;
- dynamic respawn controlled by a separate encounter-specific rule.

---

# 4. Sector-based scaling

`DESIGN-DIRECTION`

Large hunting grounds should be divisible into logical sectors or spawn regions.

This allows the system to distinguish between:

- several players legitimately using different parts of a large location;
- one extremely strong player rapidly clearing only a subset of the location;
- one party occupying the whole route;
- players merely passing through the area.

Sector-based scaling prevents one highly efficient player from forcing every monster in a large location to respawn at the maximum dynamic rate.

Each sector may evaluate its own local hunting pressure while still respecting a hunting-ground-wide capacity budget.

---

# 5. Hard respawn limits

`USER-DIRECTION`

Every dynamic hunting ground must have a configured upper bound.

The system must never attempt to keep up indefinitely with an arbitrarily powerful player.

A conceptual example:

- normal spawn capacity: `1.0x`;
- legitimate multi-player pressure: gradual scaling above baseline;
- configured maximum for the hunting ground: for example `1.5x` or `1.6x`;
- a very powerful character still clearing faster than the cap: the character eventually encounters empty spawn and should move to a more suitable hunting ground if efficiency is the goal.

Exact numbers are `OPEN` and must be balanced per hunting ground.

The important rule is that the dynamic system improves capacity, but does not guarantee infinite monster availability.

---

# 6. Recommended level and effective-power range

`USER-DIRECTION`

Each managed hunting ground should have a target progression profile so that dynamic respawn does not make lower-tier locations disproportionately attractive to much stronger characters.

Potential metadata:

- recommended minimum level;
- recommended maximum level;
- target effective-power range;
- expected solo/party profile;
- target party size;
- expected kill-rate range;
- expected route-clear time;
- base spawn capacity;
- maximum dynamic spawn multiplier.

Level alone may not be sufficient because equipment, vocation, charms, imbuements and other progression systems can significantly change actual hunting power.

`DESIGN-DIRECTION`

The final system should therefore consider an effective hunting-power model where practical, while preserving level ranges as understandable player-facing guidance.

The purpose is not to prevent an overleveled player from entering an older hunting ground.

The purpose is to decide how much the dynamic-respawn system should help that player.

---

# 7. Soft limits instead of hard level gates

`USER-DIRECTION`

The preferred model is open-world access with soft scaling rules, not hard doors that block players purely because their level is too high.

A higher-level player should still be able to:

- visit an older location;
- help another player;
- complete a quest;
- complete bestiary goals;
- complete a bounty or task;
- travel through the area;
- hunt there for personal reasons.

However, a character far above the intended power range should not automatically receive the full benefit of dynamic respawn when farming the location for XP or profit.

Possible behavior:

- player within target range -> eligible for normal dynamic scaling;
- several legitimate hunters within target range -> higher population-driven scaling within the hunting-ground cap;
- moderately overleveled player -> reduced influence on scaling;
- heavily overleveled player -> little or no additional scaling caused by that player's farming pressure.

This preserves freedom of movement while protecting progression balance.

---

# 8. Population pressure versus individual farming power

`USER-DIRECTION`

The system should explicitly distinguish these two cases.

## Case A: several appropriately powered players

Example:

Three players around the intended level range hunt different parts of a large cave.

The system observes:

- sustained combat from all three players;
- broad use of the hunting area;
- ordinary monsters dying across several sectors;
- hunters repeatedly encountering depleted spawn;
- no evidence that the pressure comes from one repeatedly farmed monster.

Result:

The hunting ground may scale meaningfully within its configured cap so the players can divide the area more effectively.

## Case B: one extremely strong player

Example:

A level 1000 character enters a hunting ground designed for much lower levels and clears the route several times faster than its intended population.

Result:

The system must not continue accelerating the spawn until it matches that character's power.

The player may receive little or no additional scaling beyond a limited allowance, depending on the hunting-ground policy.

The fact that one character can destroy the entire population extremely quickly is not, by itself, sufficient justification for unlimited dynamic respawn.

---

# 9. Spawn Budget

`DESIGN-DIRECTION`

A hunting ground or sector should have a bounded additional spawn budget.

The budget controls how much extra monster throughput may be created above the static baseline over a given period.

Goals:

- prevent one player from forcing unlimited additional monsters into existence;
- prevent farming loops that continually increase their own spawn rate;
- keep total XP and loot generation within expected bounds;
- make scaling predictable enough to balance and monitor;
- allow multiple legitimate hunters to benefit without making one high-power farmer infinitely efficient.

The budget may be defined per:

- hunting ground;
- sector;
- monster population group;
- time window.

Exact implementation is `OPEN`.

---

# 10. Active Hunter Score and anti-alt abuse

`DESIGN-DIRECTION`

Characters should not influence dynamic respawn merely by being present in the area.

Potential signals for an `Active Hunter Score` include:

- recent combat participation;
- damage dealt to ordinary hunting-ground monsters;
- legitimate kill participation;
- XP gain;
- loot interaction;
- active movement through the hunting route;
- sustained time participating in the hunt.

The system should discount or ignore:

- AFK characters;
- characters standing at the entrance;
- characters that are only passing through;
- inactive alts placed in the area to inflate population;
- very short visits;
- accounts repeatedly cycling characters into the area to manipulate scaling.

Additional anti-abuse signals may include:

- account correlation;
- device/session correlation where privacy and architecture permit;
- repeated synchronized entry/exit patterns;
- abnormal player-count spikes followed by rare-monster kills;
- repeated farming of one high-value monster while the rest of the area remains unused.

Enforcement should prefer bounded system behavior and telemetry over attempting to perfectly classify every individual case in real time.

---

# 11. Bounty and task exception for overleveled players

`USER-DIRECTION`

A high-level player may legitimately return to a lower-tier hunting ground because a bounty or task explicitly requires monsters from that location.

A level 500 or level 1000 character completing a bounty is not necessarily trying to use the hunting ground as a permanent XP or profit farm.

The system should therefore support a bounded `Bounty Spawn Allowance`.

Desired behavior:

- the player may enter the location normally;
- an active eligible bounty/task may grant limited temporary eligibility for dynamic respawn assistance;
- the assistance exists to reduce artificial waiting for required ordinary monsters;
- the allowance should be related to legitimate task progress, not become a permanent farming entitlement;
- once the bounty requirement is completed, the special allowance ends;
- remaining in the area after completion returns the character to normal overlevel rules;
- rare, boss, quest-gated and specially valuable monsters remain governed by separate policies.

The core principle is:

> A bounty may temporarily extend access to the dynamic capacity of an older hunting ground, but it must not turn that hunting ground into a permanent high-level farm.

`OPEN`

The exact contract needs abuse analysis, including:

- whether the allowance is tied to remaining required kills;
- whether only kills that advance the bounty count toward scaling eligibility;
- how repeatable bounties interact with cooldowns;
- how to prevent players from keeping an almost-complete bounty open indefinitely;
- whether party members without the bounty may benefit indirectly;
- how shared task credit should interact with dynamic spawn;
- whether bounty-specific additional spawn budget is required.

---

# 12. Bounty must not directly accelerate a specific monster

`USER-DIRECTION`

Possessing a bounty should not directly mean:

> this player's target monster respawns faster.

That model would be easy to exploit and could distort rare-monster, bestiary and loot economies.

Instead:

- the bounty may affect the overlevel eligibility of the player;
- actual respawn scaling should still depend on real hunting-ground activity;
- scaling should normally affect the intended ordinary population or sector capacity;
- all normal hard caps and spawn budgets still apply.

This keeps the bounty exception as a usability mechanism rather than a direct spawn-generation command.

---

# 13. Economic and progression safeguards

`DESIGN-DIRECTION`

Dynamic respawn changes monster throughput, which can change:

- XP generation;
- loot supply;
- gold generation;
- creature-product supply;
- imbuement-material supply;
- bestiary completion speed;
- charm progression;
- bounty/task completion speed.

Therefore every hunting ground considered for dynamic scaling should be evaluated for economic and progression impact.

Possible controls:

- per-ground maximum spawn multiplier;
- per-sector spawn budget;
- monster-class exclusions;
- rare-drop exclusions;
- lower cap for solo overlevel pressure;
- higher cap for legitimate multi-player population pressure;
- telemetry-based anomaly detection;
- post-release balancing using observed XP/hour and loot/hour distributions.

The preferred strategy is to constrain additional monster creation directly rather than secretly reduce player rewards after the fact.

---

# 14. Integration with Hunting Spot Availability

`DESIGN-DIRECTION`

Dynamic Spawn Scaling should integrate with the existing planned Hunting Spot Availability System.

The combined system can distinguish:

- free location;
- lightly occupied location with substantial unused capacity;
- occupied but shareable location;
- near-capacity location;
- fully saturated location despite dynamic scaling.

This is more useful than a simple binary free/occupied flag.

A hunting ground may be physically occupied but still have available dynamic capacity for another suitable player or party.

Conversely, a location may already be at its safe dynamic-spawn cap and should be shown as effectively full.

---

# 15. Integration with Huntfinder

`DESIGN-DIRECTION`

Huntfinder may use hunting-capacity metadata to recommend locations based on:

- player level;
- effective power;
- vocation/party composition;
- target XP or profit profile;
- current occupancy;
- current dynamic capacity;
- whether the location is already near its safe spawn cap.

This allows the game to guide an overleveled player toward more appropriate content instead of silently scaling an old hunting ground forever.

A future player-facing model could show concepts such as:

- recommended level range;
- recommended party size;
- current occupancy;
- estimated remaining capacity;
- whether the player's current bounty makes the location relevant.

Exact UI is `OPEN`.

---

# 16. Integration with Party Finder

`DESIGN-DIRECTION`

Party Finder may use the same hunting-ground capacity model.

Examples:

- advertise a party for a hunting ground that currently has safe capacity;
- warn that the location is saturated;
- suggest another sector or alternative hunting ground;
- prefer parties whose combined effective power fits the intended range;
- avoid directing multiple parties into a location already at its dynamic cap.

---

# 17. Telemetry and tuning

`DESIGN-DIRECTION`

Dynamic respawn should be designed with telemetry from the start.

Useful metrics include:

- baseline versus dynamic respawn time;
- active hunters per sector;
- effective-power distribution;
- route-clear time;
- empty-spawn encounter rate;
- monster uptime/dead-time ratio;
- kills per minute;
- XP/hour distribution;
- loot/hour distribution;
- dynamic spawn budget consumption;
- number of players benefiting from scaling;
- number of overleveled players influencing scaling;
- bounty allowance usage;
- suspicious repeated activity patterns.

The system should make it possible to identify:

- permanently overcrowded hunting grounds;
- locations whose base respawn is clearly too slow;
- locations whose dynamic cap is too generous;
- hunting grounds being exploited by overleveled characters;
- rare-monster or high-value farming anomalies;
- locations that are physically large but underutilized due to poor static respawn configuration.

---

# 18. Example policy model

`DESIGN-DIRECTION`

A future hunting-ground configuration could conceptually contain:

```yaml
hunting_area:
  id: example_area
  recommended_level_min: 300
  recommended_level_max: 600
  target_party_size: 1-3
  base_spawn_multiplier: 1.0
  dynamic_spawn_multiplier_max: 1.6
  solo_overlevel_multiplier_max: 1.15
  bounty_overlevel_multiplier_max: 1.30
  sector_scaling: true
  spawn_budget_enabled: true
  rare_monster_dynamic_respawn: false
```

These values are illustrative only and are not an implementation contract.

The important architectural concept is that each hunting ground may have its own balancing profile instead of using one global dynamic-respawn formula for the whole game.

---

# 19. Example scenarios

## Scenario A: three appropriately leveled players in a cave

`USER-DIRECTION`

Three characters around the intended progression range use different parts of the cave.

The system sees sustained legitimate hunting pressure across multiple sectors.

Expected result:

- dynamic respawn gradually increases;
- players can divide the hunting ground more effectively;
- scaling remains below the configured maximum;
- rare and excluded monsters keep their separate rules.

## Scenario B: one level 400 character enters the same cave

Expected result:

- the character may hunt normally;
- the system evaluates whether the player is still within or moderately above the intended power range;
- individual clear speed alone does not justify unlimited scaling;
- the configured solo/overlevel cap limits additional throughput.

## Scenario C: one level 1000 character clears the entire cave extremely quickly

`USER-DIRECTION`

Expected result:

- the system does not attempt to match the player's full farming power;
- the character has little influence on dynamic scaling if far above the target range;
- the player may still encounter empty spawn;
- the natural incentive is to move to content appropriate for that power level.

## Scenario D: level 1000 character has an active bounty in the cave

`USER-DIRECTION`

Expected result:

- the bounty may grant a limited temporary spawn allowance;
- the allowance reduces pointless waiting while completing the legitimate task;
- the hunting-ground hard cap and spawn budget still apply;
- completion of the bounty removes the special allowance;
- continued farming after completion follows normal overlevel rules.

---

# 20. Non-goals

`USER-DIRECTION`

The system is not intended to:

- guarantee every player a private hunting ground;
- replace the open world with instances;
- make every occupied hunting ground infinitely shareable;
- guarantee maximum XP/hour to overleveled players;
- accelerate rare monsters merely because someone wants to farm them;
- allow player count to be manipulated with inactive alts;
- remove competition from the game entirely;
- eliminate the need to create new hunting grounds in future content.

---

# 21. Open design questions

`OPEN`

Before implementation, determine:

1. How hunting areas and sectors are defined and owned in the data model.
2. Whether current Canary spawn structures can support per-area dynamic timing safely.
3. Whether spawn acceleration should modify timers, population budgets or both.
4. How to calculate active hunting pressure without expensive runtime queries.
5. How to define effective player power without creating an opaque or easily gamed score.
6. How to configure target level/power ranges for legacy and current hunting grounds.
7. How to handle parties containing both appropriately leveled and heavily overleveled players.
8. How bounty/task ownership and shared kill credit affect the allowance.
9. How to exclude rare, boss and progression-sensitive monsters reliably.
10. How dynamic spawn interacts with rapid respawn events or global spawn-rate modifiers.
11. How to prevent multiplicative stacking between global rapid respawn and local dynamic scaling.
12. What telemetry is required before enabling the feature broadly.
13. Whether rollout should begin with a small allowlist of suitable hunting grounds.
14. How Huntfinder and Hunting Spot Availability expose capacity without enabling player tracking.

---

# 22. Recommended implementation posture

`DESIGN-DIRECTION`

Treat this as a bounded, telemetry-driven open-world capacity system.

Recommended sequence:

1. Audit the current Canary spawn implementation and existing spawn-rate modifiers.
2. Define hunting-area and sector metadata.
3. Classify monster populations into dynamically scalable and excluded groups.
4. Establish target progression profiles for selected hunting grounds.
5. Implement telemetry before aggressive automatic scaling.
6. Prototype on a small allowlist of ordinary hunting grounds.
7. Add hard caps and spawn budgets before enabling any player-driven scaling.
8. Validate solo, multi-player, party, overlevel and bounty scenarios independently.
9. Measure XP, loot and economy impact.
10. Integrate capacity signals with Huntfinder and Hunting Spot Availability only after server-side behavior is proven stable.

The system should fail safely: if classification, telemetry or area state is uncertain, fall back toward the normal static respawn rather than granting extra monster throughput.
