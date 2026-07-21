# OTS Skill Progression 2.0

## Purpose

Durable design record for future active skilling, offline training, real-combat skill progression and its relationship to Tibia's existing Weapon Proficiency system in the OTS stack.

This document records product/design direction only. It does not authorize gameplay implementation. Exact formulas, thresholds and current Canary/OTClient integration points must be reverified in a separate bounded implementation task.

## Evidence labels

Use these labels consistently when reading or extending this document:

- `USER-DIRECTION`: explicitly requested or accepted by the user.
- `TIBIA-OFFICIAL`: verified behavior or direction from current official Tibia sources.
- `CANARY-CURRENT`: verified behavior present in the current `blakinio/canary` / upstream Canary code or repository documentation.
- `OTCLIENT-CURRENT`: verified behavior present in current OpenTibiaBR OTClient code/releases.
- `OTS-EXTENSION-CLAIM`: an OTS publicly claims a related custom system, but the exact mechanics may not be sufficiently documented to prove a distinct implementation.
- `DESIGN-DIRECTION`: accepted design direction whose exact balancing remains open.
- `OPEN`: requires implementation analysis, parity verification, simulation, balancing or abuse review.
- `CONFLICT`: available authoritative evidence disagrees and must be resolved before implementation.

## Core progression principle

`USER-DIRECTION`

Skill progression should reward actually playing the character. Active combat with appropriate monsters should be an efficient free way to develop weapon and defensive skills, while offline training remains a slower convenience path and exercise weapons remain a faster paid/gold-sink path.

The system should avoid making "skill training" and "playing the game" two completely separate activities.

## Real Combat Training

`DESIGN-DIRECTION`

Every qualifying weapon attack during real combat may contribute to the relevant classic skill, but the effective gain should depend on combat context rather than raw hit count alone.

Conceptual model:

`effective skill gain = base gain × threat coefficient × activity coefficient × repetition coefficient`

The exact formula is `OPEN`.

### Threat coefficient

A target's contribution should consider its threat relative to the character.

Illustrative, non-contractual ranges:

- harmless/trivial target: strongly reduced gain;
- easy target: reduced gain;
- appropriate normal hunting target: baseline gain;
- demanding target: modest bonus;
- very dangerous target: only a bounded additional bonus.

Do not create a large multiplier that encourages players to artificially tank lethal monsters purely for skill gain.

Example values discussed for simulation only:

- very weak: `0.1x`;
- easy: `0.5x`;
- normal: `1.0x`;
- demanding: `1.15x`;
- very dangerous: `1.25x`.

## Diminishing returns on one persistent target

`USER-DIRECTION`

Repeatedly attacking the same regenerating or effectively immortal monster for a long period should become less efficient than normal hunting.

`DESIGN-DIRECTION`

Apply diminishing returns when the same target is attacked continuously without meaningful encounter progression.

Illustrative example for later simulation:

- first 2 minutes: `100%`;
- 2–5 minutes: `75%`;
- 5–10 minutes: `40%`;
- above 10 minutes: `10%`.

Changing targets, killing enemies or otherwise returning to genuine active combat may restore normal efficiency under controlled anti-abuse rules.

The exact timers, reset conditions and exploit protections are `OPEN`.

## Combat Activity Score

`DESIGN-DIRECTION`

A bounded activity signal may distinguish normal active hunting from passive repetitive training.

Possible positive signals:

- defeating monsters;
- changing targets naturally during combat;
- movement and positioning;
- fighting several relevant opponents;
- using vocation-appropriate combat abilities;
- receiving meaningful incoming pressure.

Possible negative/repetition signals:

- attacking one target for an excessive period;
- no meaningful encounter progression;
- prolonged stationary repetitive loops;
- highly repetitive target/action cycles.

The activity system must not force unnatural movement or ability spam merely to maximize skill gain. Any active-combat bonus should remain modest.

Illustrative efficiency bands for simulation:

- low/repetitive activity: around `0.5x`;
- normal hunt: `1.0x`;
- highly active genuine combat: around `1.1–1.2x`.

## Shielding and defensive progression

`USER-DIRECTION`

Defensive skill progression should also reward real combat rather than trivial AFK tanking.

`DESIGN-DIRECTION`

Shielding or equivalent defensive progression should be based on qualifying defended/reduced attacks from relevant opponents.

Principles:

- attacks from monsters that are trivial relative to the character should contribute little or nothing;
- appropriate hunt-level opponents should provide normal progression;
- dangerous opponents may provide only a bounded bonus;
- long-term repetition with the same trivial set of monsters may receive diminishing returns;
- the system must not reward deliberately exposing the character to extreme lethal damage solely for faster skill gain.

Exact interaction with Canary's current shielding rules is `OPEN`.

## Relationship between progression paths

`USER-DIRECTION`

The intended hierarchy is:

1. Offline training: convenient, passive and slower.
2. Traditional low-activity monster training: available, but less efficient than genuine play.
3. Normal hunting: strong baseline free progression.
4. Highly active genuine combat: modestly better than baseline hunting.
5. Exercise weapons: fastest controlled path, functioning partly as an economy sink.

Illustrative relative values discussed for balancing simulations only:

- offline training: about `0.5x`;
- repetitive/AFK-style mob training: about `0.3–0.6x`;
- normal hunt: `1.0x`;
- highly active hunt: about `1.1–1.2x`;
- exercise weapons: about `1.5–2.0x`.

These values are not implementation contracts.

## Offline training

`DESIGN-DIRECTION`

Offline training should remain available as a catch-up/convenience mechanic for players who cannot actively play for many hours.

It should:

- progress more slowly than effective active play;
- use a bounded training-time reserve;
- avoid allowing extremely long absences to accumulate unlimited progression;
- complement active play instead of replacing it.

Exact reserve duration and vocation/skill efficiencies are `OPEN` and should be compared with current Real Tibia behavior at implementation time.

## Exercise weapons

`DESIGN-DIRECTION`

Exercise weapons should remain a faster training option and useful gold sink, but should not become the only rational route to high skills.

Principles:

- faster than free active progression;
- clear and predictable efficiency;
- controlled economic cost;
- no pay-to-win dependency for normal competitive progression;
- natural hunting must remain a meaningful source of long-term skill growth.

# Weapon Proficiency relationship — verified 2026-07-21

## Original Tibia baseline

`TIBIA-OFFICIAL`

Weapon Proficiency is already an official Tibia system and must not be described as an OTS-original concept.

Current official behavior verified from Tibia's game guide and official update announcements:

- nearly every weapon has its own Weapon Proficiency progression/tree;
- a tree has one to seven proficiency levels;
- each level can offer one to three perks, with one active perk per proficiency level;
- proficiency progress is earned by defeating monsters while the relevant weapon is equipped;
- progress follows Bestiary-like contribution rules, so characters that contributed damage can receive progress;
- progression is character-bound;
- Proficiency Catalysts can add direct progress;
- after the weapon's final proficiency level, progression can continue toward Mastery;
- Mastery is already the official end-state terminology for a mastered weapon and should not be duplicated by a second custom "Weapon Mastery" progression layer;
- since the 2026 Weapon Proficiency Update, up to two perk slots can be modified: the first after reaching Proficiency Level 3 and the second after Mastery;
- modified perks use dust-based modification and can then be refined/reshaped under the official system rules;
- official perk selection/change rules use protection-zone restrictions for already-selected or modified perks.

`CONFLICT`

Official Tibia sources are not fully consistent on exact boss proficiency progress values: the current game guide describes bosses as granting up to `1,000`, while an official 2025 release/update text describes boss rewards up to `15,000`. Exact current boss values must therefore be treated as unresolved until verified against current live data/client assets or a newer unambiguous official source.

Primary official references:

- https://www.tibia.com/gameguides/?section=combat&subtopic=manual
- https://www.tibia.com/news/?id=8421&subtopic=newsarchive
- https://www.tibia.com/news/?id=8850&subtopic=newsarchive

## Current Canary support

`CANARY-CURRENT`

The current Canary repository already contains a server-side Weapon Proficiency implementation documented for Protocol 15.11. The documented implementation includes:

- proficiency experience;
- perk selection;
- Mastery progression;
- combat perk effects;
- persistence;
- per-item proficiency assignment;
- configurable proficiency level/perk limits and gain multiplier;
- proficiency progress on monster kills;
- catalysts that add weapon proficiency experience.

The current Canary guide documents monster progress based on Bestiary stars and Bosstiary rarity and exposes concrete server-side values. This proves a working baseline implementation, but not exact parity with every current Tibia 2026 balance value or feature.

`OPEN`

The July 2026 official Weapon Proficiency perk-manipulation extension is not proven to exist in the current Canary implementation. Repository searches performed for modification-specific concepts such as Lunar Ascension Orb/refine/reshape/modified proficiency perks did not establish support. Before implementing any custom proficiency extension, first perform a bounded parity audit for the 2026 official manipulation system.

Repository reference:

- `docs/systems/weapon-proficiency.md`

## Current OTClient support

`OTCLIENT-CURRENT`

OpenTibiaBR OTClient has a dedicated `game_proficiency` module and release 4.1 includes the proficiency feature from PR #1593. This proves client-side support for the base Weapon Proficiency UI/protocol path.

Relevant paths include:

- `modules/game_proficiency/proficiency.lua`
- `modules/game_proficiency/proficiency.otui`
- `modules/game_proficiency/proficiency_data.lua`

`OPEN`

Support for the July 2026 official perk-manipulation UI/flows is not proven by the current verification and must be audited separately before claiming current-Tibia parity.

Repository reference:

- https://github.com/opentibiabr/otclient

## Other OTS comparison

`OTS-EXTENSION-CLAIM`

TibiaScape publicly announced "our own weapon proficiency" on 2026-05-20. The publicly indexed announcement does not document enough mechanics to prove which parts are genuinely distinct from Tibia's official Weapon Proficiency system.

Therefore:

- do not classify Weapon Proficiency itself as a TibiaScape/OTS-original feature;
- do not import a supposed TibiaScape extension without concrete mechanical evidence;
- if a future OTS comparison finds a documented mechanic that extends official Tibia, label only that specific mechanic as an OTS extension.

Reference:

- https://www.tibiascape.com/

# Our proposal

## Keep classic skills and Weapon Proficiency as separate systems

`USER-DIRECTION`

`DESIGN-DIRECTION`

Do not introduce another generic "Weapon Mastery" system. Tibia already uses Weapon Proficiency and Mastery for per-weapon progression.

The proposed architecture is:

### Classic skill progression

Examples: Sword Fighting, Axe Fighting, Club Fighting, Distance Fighting, Fist Fighting, Shielding and relevant magic progression.

Purpose:

- long-term character competence;
- primarily use/training based;
- affected by Real Combat Training rules;
- active hunting should be a strong free progression path;
- repetitive immortal-target training may receive diminishing returns;
- offline and exercise training remain alternative paths.

### Weapon Proficiency

Purpose:

- progression tied to a specific weapon/proficiency profile;
- kill/encounter progression rather than raw hit-count training;
- perk/build customisation;
- existing official Mastery end-state;
- should retain current-Tibia semantics as the baseline unless a deliberate, separately approved OTS extension is specified.

## How both systems work together

`DESIGN-DIRECTION`

A normal hunt should naturally advance both systems, but for different reasons:

- repeated qualifying weapon use advances the character's classic combat skill;
- defeating relevant monsters while the weapon is equipped advances that weapon's Weapon Proficiency.

This creates complementary progression without duplicating systems.

Example:

- a knight hunting with a sword develops Sword Fighting through real combat use;
- the equipped sword/proficiency profile gains Weapon Proficiency progress through qualifying monster kills;
- perk choices belong to Weapon Proficiency;
- core weapon competence remains represented by Sword Fighting.

## Interaction with Real Combat Training

`DESIGN-DIRECTION`

By default, threat/activity/repetition multipliers from Skill Progression 2.0 should apply to classic skill gain, not automatically multiply Weapon Proficiency progress.

Reasoning:

- Weapon Proficiency is already primarily kill-gated rather than raw-hit-gated;
- applying the same activity multipliers to both systems could double-reward the same behavior and distort progression;
- persistent regenerating training monsters are mainly a classic-skill exploit surface because they can generate many hits without kills;
- keeping proficiency kill-based naturally prevents infinite per-hit proficiency farming.

Any future coupling between activity score and Weapon Proficiency must be a separate, explicitly justified design change.

## Parity before extension

`DESIGN-DIRECTION`

Before designing custom Weapon Proficiency mechanics, implementation work should follow this order:

1. verify exact current official Tibia Weapon Proficiency behavior;
2. audit current Canary parity;
3. audit current OTClient UI/protocol parity;
4. close high-value official parity gaps, especially the 2026 perk-manipulation flow if missing;
5. only then evaluate documented OTS extensions;
6. add a custom OTS extension only when it solves a concrete product problem not already solved by official Tibia.

This avoids rebuilding systems that already exist in current Tibia.

## Current recommendation

`DESIGN-DIRECTION`

For the current roadmap:

- keep Weapon Proficiency as a first-class official-Tibia-derived system;
- do not add a second weapon mastery/proficiency layer;
- treat Skill Progression 2.0 as an enhancement to classic skill training and active skilling;
- let normal hunting progress both classic skills and Weapon Proficiency independently;
- prioritize a current-Tibia parity audit for the 2026 Weapon Proficiency perk-manipulation update before proposing custom proficiency features.

## Anti-abuse principles

`USER-DIRECTION`

The system should reward genuine gameplay without becoming a new botting or training exploit surface.

Future implementation analysis should cover:

- regenerating/immortal training monsters;
- summoned or player-controlled targets;
- repeatedly resetting target identity;
- multi-client or cooperative training loops;
- low-damage infinite combat setups;
- movement/activity spoofing;
- botting patterns optimized for activity-score thresholds.

Do not rely on one heuristic alone. Use bounded multipliers, diminishing returns and telemetry where appropriate.

## Product outcome

`USER-DIRECTION`

The preferred player experience is:

> The best free way to develop a combat skill over the long term is to actually play and fight with that skill.

Traditional monster training and offline training remain valid lower-intensity alternatives, while exercise weapons provide a faster controlled economy-sink option.

Weapon Proficiency remains the separate per-weapon customisation/progression layer inherited from current Tibia rather than being reinvented as an OTS-original system.

## Open implementation questions

`OPEN`

- Current Canary classic skill-advance formulas and event hooks.
- Current OTClient classic skill presentation/progress UI.
- Exact current-Tibia versus Canary Weapon Proficiency parity, including boss progress values.
- Canary support for the July 2026 Weapon Proficiency perk-manipulation system.
- OTClient support for the July 2026 Weapon Proficiency perk-manipulation UI and protocol flows.
- Threat classification source and whether it can reuse existing monster metadata.
- Exact activity and repetition windows.
- Party/shared-damage semantics.
- Summon and pet interactions.
- PvP skill-gain rules.
- Shielding-specific mechanics.
- Vocation-specific balance.
- High-skill progression curve.
- Telemetry required to detect abuse without punishing normal players.
- Simulation of offline, hunt and exercise progression over representative 100/500/1000-hour horizons.
