# OTS Vocation/Class Identity, Roles and Balance Framework

## Purpose

Durable design direction for defining the identity, role expectations and balance model of every playable vocation/class before later gameplay, itemization, party, encounter and progression systems are tuned around them.

This document is a product/design framework, not proof of current Tibia, Canary or OTClient behavior. Exact current-vocation mechanics and parity must be reverified before implementation work.

## Evidence labels

- `USER-DIRECTION`: explicitly requested or approved by the user.
- `DESIGN-DIRECTION`: concrete direction selected as useful, but not yet an implementation contract.
- `OPEN`: requires current-baseline analysis, telemetry, simulation, balance testing or technical validation.

---

# 1. Core direction

`USER-DIRECTION`

Create an explicit definition for every supported vocation/class covering:

- class fantasy and identity;
- primary role;
- secondary roles;
- intended solo-play profile;
- intended party-play profile;
- strengths;
- weaknesses;
- damage profile;
- defensive profile;
- sustain/resource profile;
- mobility;
- support/utility;
- expected skill ceiling;
- intended interaction with equipment, Skill Wheel, classic skills, Weapon Proficiency, Imbuements and Build Presets.

The purpose is to prevent balance from becoming a sequence of isolated item/spell buffs and nerfs without a stable definition of what each vocation/class is supposed to be good or bad at.

---

# 2. Vocation/Class Identity Contract

`DESIGN-DIRECTION`

Every vocation/class should receive a durable identity contract with the following fields.

## 2.1 Primary identity

A concise statement describing what the class is fundamentally expected to do in combat.

Examples of identity dimensions, without assigning them to a specific vocation before analysis:

- front-line durability;
- sustained single-target pressure;
- burst damage;
- area damage;
- ranged pressure;
- healing;
- party support;
- battlefield control;
- mobility;
- resource efficiency.

## 2.2 Primary and secondary roles

Each class should have:

- one or more clearly defined primary strengths;
- optional secondary contributions;
- explicit areas where another class is expected to outperform it.

A class should not become best-in-class simultaneously at damage, survival, healing, mobility and utility without a meaningful tradeoff.

## 2.3 Strengths and weaknesses

Each class definition should explicitly state:

- what situations reward the class;
- what situations pressure the class;
- what resources or positioning it depends on;
- what other party members can complement it;
- what tradeoffs appear when moving from a defensive to offensive build or vice versa.

Weaknesses should create meaningful gameplay decisions, not arbitrary frustration.

---

# 3. Role taxonomy

`DESIGN-DIRECTION`

Use a shared role vocabulary across Party System 2.0, Party Finder 2.0, Build Presets, Training Arena and balance telemetry.

Candidate role tags include:

- `Frontliner`;
- `Tank`;
- `Damage`;
- `Burst Damage`;
- `Sustained Damage`;
- `AoE Damage`;
- `Single-Target Damage`;
- `Healer`;
- `Support`;
- `Control`;
- `Mobility`;
- `Hybrid`.

Role tags are descriptive, not necessarily rigid queue requirements.

## 3.1 Avoid a forced hard trinity

`USER-DIRECTION`

The system should not automatically force every activity into a rigid tank/healer/DPS composition if Tibia-style gameplay works better with more flexible group structures.

Preferred direction:

- every vocation/class remains capable of meaningful solo play;
- party play makes specialization and cooperation valuable;
- no class becomes mandatory for every piece of content solely because the system hard-codes one composition;
- encounters may strongly reward certain roles without permanently excluding alternative viable strategies.

`OPEN`

- exact role vocabulary;
- whether role tags are manually selected, inferred from build, or both;
- how role tags interact with flexible boss-party-size design.

---

# 4. Solo versus party balance

`USER-DIRECTION`

Balance should explicitly evaluate both solo and group gameplay.

A vocation/class may be stronger in one context than another, but the difference should be intentional and bounded.

## 4.1 Solo viability

Every supported class should have viable paths for:

- ordinary progression;
- hunting;
- completing reasonable solo content;
- testing and improving builds;
- earning enough resources to sustain normal play.

Solo viability does not require identical XP/hour, profit/hour or difficulty across classes.

## 4.2 Party value

Party value should include more than raw damage.

The balance model should be capable of recognizing:

- damage dealt;
- damage prevented/mitigated;
- effective healing;
- resource support;
- control;
- positioning assistance;
- survival contribution;
- other future support mechanics.

This is important for Party System 2.0 so shared-EXP/bonus design does not accidentally reward only direct damage while undervaluing tanking, healing or support.

---

# 5. Balance dimensions

`DESIGN-DIRECTION`

Each vocation/class should be evaluated across multiple dimensions rather than one aggregate power score.

## 5.1 Offense

- sustained DPS;
- burst DPS;
- single-target damage;
- AoE damage;
- damage uptime;
- range;
- target-switching cost;
- elemental/access flexibility.

## 5.2 Defense

- raw survivability;
- physical mitigation;
- elemental mitigation;
- recovery after burst damage;
- vulnerability while disabled or resource-starved;
- dependence on positioning.

## 5.3 Sustain and economy

- mana/resource consumption;
- potion/rune/ammunition usage;
- life/mana leech dependence;
- supply cost per hour;
- recovery downtime;
- profit sensitivity.

## 5.4 Support and utility

- healing;
- buffs;
- debuffs;
- control;
- protection of party members;
- mobility assistance;
- encounter-specific utility.

## 5.5 Mobility and execution

- movement freedom;
- positioning requirements;
- rotation complexity;
- reaction demands;
- punishment for mistakes;
- skill ceiling.

---

# 6. Balance target bands instead of forced equality

`DESIGN-DIRECTION`

Do not attempt to make every class numerically identical.

Use bounded target bands appropriate to role and context.

Examples:

- a highly defensive build may intentionally deal less damage;
- a high-burst build may have weaker sustain;
- a strong healer may contribute less direct damage but high party survival value;
- a mobile ranged build may trade raw durability for positioning freedom.

The balance question should be:

`Is the class/build within an acceptable role-appropriate performance band?`

not:

`Does every class produce exactly the same DPS?`

Exact bands remain `OPEN` until supported by telemetry and simulation.

---

# 7. Progression-band balance

`USER-DIRECTION`

Do not balance only around one level range or only around top-end players.

Evaluate at least:

- early progression;
- mid progression;
- high level;
- endgame;
- highly optimized endgame builds.

A formula that is acceptable at low level must not create disproportionate scaling problems at very high level.

This principle should align with the broader roadmap goal that long-term progression remains viable without punishing high-level players because of legacy formulas designed for much lower progression ceilings.

---

# 8. PvE, boss and PvP contexts

`DESIGN-DIRECTION`

Balance should be measured separately for:

- ordinary solo PvE;
- ordinary party PvE;
- high-density hunting;
- boss encounters;
- structured PvP;
- open-world PvP where applicable.

A class can be healthy in PvE but overpowered in PvP, or vice versa.

Preferred direction:

- preserve one understandable core kit where practical;
- allow context-specific coefficients/rules only when necessary and transparent;
- avoid repeatedly damaging PvE balance solely to solve a PvP-only problem.

`OPEN`

- exact separation mechanisms;
- whether some effects need PvP-specific coefficients;
- interaction with future PvP System 2.0.

---

# 9. Build diversity inside each class

`USER-DIRECTION`

The vocation/class definition should describe a stable core identity while allowing multiple viable builds.

Potential build axes:

- offensive versus defensive;
- burst versus sustain;
- solo versus party specialization;
- single-target versus AoE;
- elemental specialization;
- healing/support emphasis;
- mobility/utility emphasis.

Build diversity must not erase class identity.

Preferred relationship:

`Vocation/Class Identity`

-> defines the durable gameplay boundaries

`Skill Wheel + Equipment + Imbuements + Itemization`

-> selects a build inside those boundaries

`Build Presets`

-> stores the configuration

`Build Impact Calculator + Training Arena`

-> measures the consequences.

---

# 10. Itemization and Imbuement dependency

`DERIVED`

Itemization cannot be balanced correctly without role definitions.

Examples:

- class-role definitions determine what offensive, defensive and support tradeoffs an item should enable;
- Imbuement active channels should complement roles without allowing one class to erase all intended weaknesses;
- Elemental Attunement should improve preparation/flexibility without turning every build into a universal all-resistance configuration;
- item classification/Forge progression should not cause one class to scale disproportionately because its role converts item power more efficiently than others.

Therefore `Itemization & Build System 2.0` and `Imbuement System 2.0` should consume the vocation/class balance framework rather than define class identity indirectly.

---

# 11. Party System 2.0 dependency

`DERIVED`

Party roles and party bonuses should use the same class/role framework.

Potential integrations:

- Party Finder can display desired roles without forcing one exact composition;
- Party UI can display role markers;
- shared-EXP/bonus analysis can measure meaningful contribution beyond damage;
- party combat visibility can prioritize tanks, healers/support or manually pinned members;
- Party Hunt Accounting can report role-relevant metrics without turning them into mandatory performance scores.

---

# 12. Build Impact Calculator and Training Arena dependency

`DERIVED`

The balance framework should define standardized test profiles.

Possible outputs by class/build:

- damage;
- healing;
- mitigation;
- sustain;
- resource efficiency;
- mobility/execution-sensitive performance where measurable.

Training Arena scenarios can include:

- standardized single-target pressure;
- AoE density;
- incoming burst;
- sustained incoming damage;
- healing/support scenarios;
- movement/mechanics scenarios.

The purpose is to compare builds and understand class performance, not create a public mandatory DPS ranking that removes all contextual nuance.

---

# 13. Balance telemetry framework

`DESIGN-DIRECTION`

Balance decisions should use aggregate telemetry and controlled tests instead of Discord anecdotes alone.

Candidate signals:

## Solo PvE

- XP/hour distributions;
- profit/hour distributions;
- supply cost/hour;
- death rate;
- hunt abandonment rate;
- damage taken;
- healing/resource consumption.

## Party PvE

- party composition;
- effective damage;
- effective healing;
- damage taken/mitigated;
- resource support;
- death/wipe rate;
- encounter completion time;
- contribution distribution.

## Bosses

- completion rate;
- party composition diversity;
- clear time;
- deaths;
- class representation by difficulty tier.

## PvP

- win/loss and objective outcomes;
- class/build representation;
- burst lethality;
- survivability;
- repeated matchup imbalance.

Telemetry should be normalized where practical by relevant progression context such as level, skills, equipment/build quality and encounter difficulty.

`OPEN`

- privacy and retention;
- exact normalization model;
- sample-size thresholds;
- protection against balancing around bot/abuse data;
- distinction between player skill and class power.

---

# 14. Balance governance

`DESIGN-DIRECTION`

Use a repeatable balance loop:

1. define the class identity and expected roles;
2. define measurable target bands by context;
3. gather telemetry and controlled Training Arena results;
4. identify deviations;
5. determine whether the cause is class kit, itemization, Imbuement, encounter design, level scaling or player-skill distribution;
6. apply the smallest targeted adjustment;
7. validate again before broad follow-up changes.

Avoid:

- balancing from one viral clip;
- balancing only from the top 1% or only from inexperienced players;
- fixing class weakness exclusively by continuous item power creep;
- forcing every class into identical damage output;
- changing multiple unrelated systems simultaneously without attribution.

---

# 15. Required per-class specification

`USER-DIRECTION`

Before a class/vocation is considered balance-defined, create a separate specification containing at least:

- identity statement;
- primary role(s);
- secondary role(s);
- intended solo profile;
- intended party profile;
- offensive strengths/weaknesses;
- defensive strengths/weaknesses;
- sustain/resource model;
- mobility;
- support/utility;
- early/mid/high/endgame scaling expectations;
- PvE/boss/PvP considerations;
- intended build archetypes;
- itemization/Imbuement interaction;
- Skill Wheel/skills/Weapon Proficiency interaction;
- measurable balance target bands;
- known risks and open questions.

Do not invent final class-specific values before the current vocation implementations and combat formulas are audited.

---

# 16. Implementation policy

1. Treat this framework as product direction, not a completed class balance pass.
2. Audit every currently supported vocation/class and its current Canary/OTClient behavior before assigning final roles or changing numbers.
3. Reverify current Tibia behavior when making parity claims.
4. Define role identity before tuning individual spells/items whenever practical.
5. Keep solo viability and party value as separate measured concerns.
6. Keep PvE, boss and PvP balance contexts separately observable.
7. Use telemetry and standardized simulations before final numeric tuning.
8. Integrate with Party System 2.0, Itemization & Build System 2.0, Imbuement System 2.0, Build Impact Calculator and Training Arena.
9. Preserve meaningful class asymmetry; balance means viable tradeoffs, not identical kits.
10. Exact numeric balance remains `OPEN` until a bounded implementation/research task establishes evidence.