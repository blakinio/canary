# OTS Skill Progression 2.0

## Purpose

Durable design record for future active skilling, offline training and real-combat skill progression in the OTS stack.

This document records product/design direction only. It does not authorize gameplay implementation. Exact formulas, thresholds and current Canary/OTClient integration points must be reverified in a separate bounded implementation task.

## Evidence labels

- `USER-DIRECTION`: explicitly requested or accepted by the user.
- `DESIGN-DIRECTION`: accepted design direction whose exact balancing remains open.
- `OPEN`: requires implementation analysis, simulation, balancing or abuse review.

## Core progression principle

`USER-DIRECTION`

Skill progression should reward actually playing the character. Active combat with appropriate monsters should be an efficient free way to develop weapon and defensive skills, while offline training remains a slower convenience path and exercise weapons remain a faster paid/gold-sink path.

The system should avoid making "skill training" and "playing the game" two completely separate activities.

## Real Combat Training

`DESIGN-DIRECTION`

Every qualifying weapon attack during real combat may contribute to the relevant skill, but the effective gain should depend on combat context rather than raw hit count alone.

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

## Open implementation questions

`OPEN`

- Current Canary skill-advance formulas and event hooks.
- Current OTClient presentation/progress UI.
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
