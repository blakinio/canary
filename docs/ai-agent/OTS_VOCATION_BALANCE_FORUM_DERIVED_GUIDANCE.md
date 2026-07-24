# OTS Vocation Balance — Forum-Derived Design Guidance

## Purpose

This document converts the recurring problem statements captured in `docs/ai-agent/REAL_TIBIA_VOCATION_ADJUSTMENTS_FORUM_ANALYSIS.md` into implementation-neutral guidance for future vocation balance work in `blakinio/canary`.

It is a design and validation input, not a balance patch specification.

The source report is community-feedback evidence. It can prioritize questions, scenarios and risks, but it does not establish current Real Tibia formulas, current Canary behavior or numeric values to copy.

## Source baseline and dependencies

Primary source:

- `docs/ai-agent/REAL_TIBIA_VOCATION_ADJUSTMENTS_FORUM_ANALYSIS.md`
- observed source blob SHA: `1a4a9df2515b9ea128efefa2907af6ba808f540a`
- source scope at this baseline: seven complete official Tibia forum threads containing 7,187 accessible unique posts, plus a bounded Druid page-one sample

Related design framework:

- PR #799 proposes `docs/ai-agent/OTS_VOCATION_ROLE_AND_BALANCE_FRAMEWORK.md`.
- That framework defines class identity contracts, role taxonomy, solo/party viability, target bands, progression-band analysis, telemetry and balance governance.
- This document does not modify or duplicate the paths owned by PR #799. It adds a forum-derived layer that can later feed per-vocation specifications and controlled balance investigations.

Known source evolution:

- PR #823 is preparing a bounded Paladin design-thread supplement.
- The current Druid design-stage evidence remains a page-one sample rather than a complete-thread corpus.
- Any later per-vocation specification must re-read the current source report and incorporate newer supplements before treating this document as complete evidence coverage.

## Evidence labels

- `SOURCE-DERIVED` — directly supported as a recurring problem statement or design concern by the forum analysis.
- `DESIGN-DERIVED` — a product or validation principle inferred from multiple source findings.
- `OPEN` — requires current Canary source/runtime audit, current Real Tibia evidence when parity matters, simulation, telemetry or implementation design.
- `NO-NUMERIC-AUTHORITY` — no coefficient, cooldown, area, target count, Wheel cost or other gameplay value is authorized by forum frequency alone.

---

# 1. Central balance thesis

`DESIGN-DERIVED`

The strongest cross-vocation lesson is that future balance should not begin with the question:

> Which vocation needs more or less damage?

It should begin with:

> What role, risk, execution difficulty, progression investment and practical reward is this vocation or build supposed to have in this context?

The forum analysis repeatedly connects player acceptance of difficult or risky mechanics with whether those mechanics provide a visible practical advantage.

Examples include:

- positional beam execution;
- permanent offensive or defensive stance tradeoffs;
- chained or forked targeting;
- high Wheel investment;
- narrow spell geometry;
- reduced defensive safety;
- higher input or aiming burden;
- melee exposure;
- dependence on party positioning.

A future OTS balance model should therefore evaluate **reward relative to difficulty, risk and investment**, not only raw output.

`NO-NUMERIC-AUTHORITY`

This does not define how large the reward premium should be. That remains a measured target-band decision.

---

# 2. Balance package principle

`SOURCE-DERIVED`

Players repeatedly evaluated combined packages rather than isolated coefficients.

A damage reduction can also change:

- life leech;
- mana leech;
- creature kill time;
- number of incoming attack turns;
- potion and rune consumption;
- profit per hour;
- viable hunting grounds;
- experience per hour;
- party composition value.

Likewise, a stronger heal may not compensate for a longer healing interval if the practical failure mode is a lethal gap between casts.

`DESIGN-DERIVED`

Every future balance change should have a **compensation ledger** covering at least:

1. direct offense;
2. effective target coverage;
3. defense and survival;
4. sustain and leech;
5. resource economy;
6. rotation cadence;
7. positional or execution cost;
8. progression/Wheel cost;
9. party contribution;
10. PvE, boss and PvP side effects.

A change should not be described as a simple `+X%` or `-X%` adjustment when its meaningful effect is multidimensional.

---

# 3. Functional correctness before balance tuning

`SOURCE-DERIVED`

Across vocations, targeting, geometry, range, state transitions, movement behavior and augment/Wheel access repeatedly contaminated balance discussion.

Examples include:

- Monk chain target selection and early termination;
- Druid forked target selection;
- Sorcerer beam geometry and delayed/repeated-hit behavior;
- Knight challenge/aggro selection and Front Sweep geometry;
- Paladin spell area and charm behavior;
- stance activation, cancellation and switching rules.

`DESIGN-DERIVED`

Use the following order:

1. prove the mechanic definition;
2. prove registration and runtime path;
3. define a deterministic behavior contract;
4. test targeting, geometry, range, timing and state transitions;
5. resolve confirmed defects;
6. only then measure balance output.

A mechanic that misses targets because of a targeting defect must not be "balanced" by increasing damage.

A mechanic that is unusable because its geometry is wrong must not be treated as a coefficient problem.

---

# 4. Difficulty premium

`SOURCE-DERIVED`

A recurring rule in the forum analysis is that a correctly executed difficult option should provide a visible advantage over a simpler fallback.

Relevant dimensions include:

- aiming difficulty;
- movement constraints;
- latency sensitivity;
- narrow geometry;
- target-distribution sensitivity;
- stance penalties;
- setup time;
- Wheel investment;
- rotation complexity;
- punishment for a missed turn.

`DESIGN-DERIVED`

Every advanced rotation or mechanic should declare:

- the simpler fallback being compared;
- the additional execution/risk/investment cost;
- the intended benefit category;
- the scenario where that benefit should be visible;
- the measurable failure condition when the premium is absent.

The premium does not have to be raw DPS. It may be:

- better target coverage;
- higher burst;
- better sustain;
- lower supply cost;
- stronger boss contribution;
- safer positioning;
- better party utility;
- improved control.

`OPEN`

Exact acceptable premiums remain target-band decisions and should be calibrated with controlled scenarios and telemetry.

---

# 5. Core rotation before endgame amplification

`SOURCE-DERIVED`

Wheel criticism repeatedly focused on functional completeness, not merely total power. Players objected when the mechanic presented as a vocation's new identity required very high progression investment before the rotation became coherent.

`DESIGN-DERIVED`

Preferred progression model:

- the **core gameplay loop** becomes functional at a reasonable progression point;
- later Wheel or equivalent progression improves power, flexibility, specialization or efficiency;
- endgame investment deepens a coherent rotation rather than repairing an incomplete base kit.

For every vocation/build, record two separate thresholds:

1. **functional breakpoint** — the minimum progression at which the intended loop works coherently;
2. **scaling breakpoint** — later progression where the loop becomes stronger or more specialized.

A balance review should flag cases where the functional breakpoint is effectively endgame-only.

---

# 6. Separate contexts instead of one global balance verdict

`SOURCE-DERIVED`

The forum analysis consistently distinguishes:

- solo hunting;
- duo play;
- standard party hunting;
- high-density hunting;
- bossing;
- PvP.

A vocation may be healthy in one context and structurally weak or excessive in another.

`DESIGN-DERIVED`

No future task should conclude that a vocation is globally "balanced" from one benchmark.

Minimum scenario matrix:

| Context | Minimum questions |
|---|---|
| Solo PvE | XP/h, profit/h, supplies, survival, realistic target count, rotation completeness |
| Duo | role complementarity, rescue/healing availability, aggro/control, combined sustain |
| Four-player party | slot value, damage, mitigation, healing, utility, movement and uptime |
| High-density hunt | target scaling, AoE geometry, leech feedback, incoming-turn amplification |
| Boss | single-target contribution, burst windows, mechanics uptime, rescue/control value |
| PvP | burst lethality, cleanse/recovery, control, mobility, resource pressure, abuse cases |

Each scenario should be repeated across progression bands rather than only at maximum level.

---

# 7. Human execution and input burden are balance variables

`SOURCE-DERIVED`

The original vocation-balancing direction explicitly included reducing unnecessary inputs, and forum feedback repeatedly connected practical power with input repetition, hotkey burden, aiming and movement.

`DESIGN-DERIVED`

Track human execution costs alongside combat results:

- actions per minute;
- repeated potion inputs;
- number of required hotkeys;
- target-selection actions;
- facing changes;
- crosshair/cursor actions;
- movement interruptions;
- missed-turn penalty;
- latency sensitivity;
- cognitive state tracking.

A rotation that wins only in a theoretical perfect-input model may be practically weaker than a simpler rotation.

The balance target should distinguish:

- theoretical ceiling;
- realistic skilled execution;
- ordinary competent execution.

This avoids balancing every vocation around either perfect play or low-skill play alone.

---

# 8. Reliability budget

`DESIGN-DERIVED`

For mechanics dependent on targeting, chains, forks, delayed hits, beams or stance state, introduce a **reliability budget** before coefficient tuning.

Measure at least:

- intended targets available;
- intended targets actually hit;
- failure reason;
- target-layout sensitivity;
- movement sensitivity;
- line-of-sight sensitivity;
- retargeting behavior;
- tie-breaking behavior;
- latency/input sensitivity where relevant.

A vocation should not need excessive nominal damage merely to compensate for unreliable mechanics unless unreliability is itself an explicit, intentional risk/reward property.

---

# 9. Balance debt

`DESIGN-DERIVED`

Create the concept of **balance debt** for features that are live or planned but cannot yet be interpreted cleanly because one of the following is unresolved:

- targeting contract;
- geometry;
- state machine;
- progression access;
- broken augment;
- missing client behavior;
- missing telemetry;
- unclear role expectation;
- unresolved parity question.

A balance-debt item should not automatically trigger a buff or nerf.

It should first nominate the missing proof that prevents trustworthy interpretation.

This helps prevent repeated numerical compensation for functional design problems.

---

# 10. Vocation-specific investigation priorities

These are hypotheses and validation priorities derived from the forum analysis. They are not final role assignments or numeric balance decisions.

## 10.1 Elite Knight

`SOURCE-DERIVED`

Primary recurring questions:

- whether stance rewards match permanent or persistent penalties;
- whether longer healing cadence creates dangerous survival gaps despite higher per-cast healing;
- whether lower damage indirectly reduces survivability through lower leech and longer kill time;
- whether solo and AoE target-count limits are appropriate;
- whether tank specialization remains a meaningful choice rather than a forced identity;
- whether aggro-control tools select and position targets reliably;
- whether Front Sweep/Exori Min geometry is useful before its coefficient is considered;
- whether shielding produces visible marginal value;
- whether the complete offensive/defensive loop arrives at an appropriate progression point.

`DESIGN-DERIVED`

Future EK balance should separately model:

- offensive stance;
- defensive stance;
- neutral/no-stance behavior if supported;
- solo box hunting;
- party blocking;
- boss tanking;
- PvP front-line play.

The key EK metric is not only damage dealt. It is the combined loop:

`damage -> kill time -> incoming turns -> leech -> healing/resource pressure -> survival`.

## 10.2 Master Sorcerer

`SOURCE-DERIVED`

Primary recurring questions:

- whether elemental identity is mechanically coherent;
- whether beam positioning and execution receive a visible reward;
- whether outer/secondary beam effects justify their practical difficulty;
- whether delayed/repeated-hit mechanics work during movement;
- whether losing off-vocation rescue/healing utility changes party-slot value;
- whether unused single-target spells are weak because of numbers or because they do not fit the combat loop;
- whether the intended playstyle requires excessive Wheel investment;
- whether Barrier/Mana Buffer-like protection remains a one-shot protection mechanic rather than a generic effective-health pool.

`DESIGN-DERIVED`

Future MS testing should compare:

- simple rune fallback;
- beam/stance rotation;
- moving solo combat;
- stable party-box combat;
- dispersed targets;
- boss single-target play;
- party utility with and without rescue/healing tools.

A difficult beam rotation should have an explicitly defined benefit category over the simpler fallback.

## 10.3 Exalted Monk

`SOURCE-DERIVED`

Primary recurring questions:

- deterministic chain targeting;
- complete ranged builder/spender identity;
- high-density scaling;
- boss and single-target contribution;
- party-slot justification;
- support uptime and proximity dependence;
- harmony/spender reward;
- Wheel opportunity cost;
- survivability under melee exposure;
- elemental access and content restrictions.

`DESIGN-DERIVED`

Monk should be evaluated as several contribution channels rather than one damage score:

- direct damage;
- healing;
- mitigation/support;
- rescue/off-tank potential;
- control;
- ranged fallback or ranged specialization.

A future role decision should explicitly answer why a party chooses a Monk in relevant content without requiring the Monk to outperform every pure damage vocation in raw DPS.

## 10.4 Royal Paladin

`SOURCE-DERIVED`

Primary recurring questions from the current source baseline:

- whether signature RP spells remain preferable to simpler legacy alternatives;
- whether charm-processing changes are compensated across the complete damage package;
- whether Sharpshooter/stance tradeoffs account for strong physical-damage dependency;
- whether Divine Defiance-like tradeoffs alter emergency healing and survivability appropriately;
- whether Holy Grenade and other signature mechanics retain a meaningful purpose after bug corrections or numerical changes;
- whether the rotation preserves ranged identity rather than collapsing into a narrow close-range pattern;
- whether smoother rotation and lower rune dependence can be preserved while tuning power.

`OPEN`

PR #823 is preparing additional bounded Paladin design-stage evidence. Re-read the current forum analysis after that supplement lands before finalizing an RP-specific design contract.

## 10.5 Elder Druid

`SOURCE-DERIVED`

Primary recurring questions:

- whether group-healing stance design improves survival or merely trades burst healing for dangerous cadence gaps;
- whether solo compensation addresses damage/AoE limitations rather than only self-healing;
- whether forked targeting is deterministic and practically useful;
- whether solo-damage functionality requires excessive investment in party-healing branches;
- whether the complete rotation arrives too late in the Wheel;
- whether runes remain an alternative or stay dominant even after investing in vocation-specific damage mechanics;
- whether duo play receives a coherent stance/role answer.

`OPEN`

The current Druid design-stage source is incomplete. Treat ED conclusions as lower-confidence prioritization until broader design-stage evidence or current authoritative behavior is available.

---

# 11. Standard per-vocation balance worksheet

`DESIGN-DERIVED`

Every future vocation balance task should fill this worksheet before proposing numeric changes.

## Identity

- vocation/class identity statement;
- primary role(s);
- secondary role(s);
- explicit intended weaknesses;
- solo identity;
- duo identity;
- party identity;
- boss identity;
- PvP identity.

## Functional contract

- core rotation;
- fallback rotation;
- state machines;
- target-selection rules;
- geometry;
- range;
- cooldown groups;
- resource costs;
- interaction with leech;
- interaction with equipment;
- interaction with Wheel/gems/proficiency/imbuements;
- client/protocol coupling.

## Progression

- functional breakpoint;
- scaling breakpoints;
- early/mid/high/endgame expectations;
- minimum Wheel or equivalent investment;
- opportunity cost versus alternative branches.

## Performance

- single-target sustained output;
- single-target burst;
- realistic AoE target coverage;
- high-density scaling;
- damage uptime;
- effective healing;
- damage prevented/mitigated;
- control/support contribution;
- mobility;
- survival;
- resource efficiency;
- supply cost;
- profit sensitivity.

## Execution

- input rate;
- aiming/facing requirement;
- movement restriction;
- latency sensitivity;
- missed-turn penalty;
- skill ceiling;
- reliability rate.

## Comparison

- simpler fallback;
- same-vocation alternative build;
- cross-vocation role comparison;
- intended advantage;
- intended disadvantage;
- measurable success band.

---

# 12. Proposed balance decision pipeline

`DESIGN-DERIVED`

1. **Identity decision** — define what the vocation/build should do.
2. **Current Canary audit** — prove definitions, registrations, runtime paths and current tests.
3. **Parity decision** — when Real Tibia parity matters, pin authoritative evidence separately from OTS-specific design.
4. **Functional validation** — target selection, geometry, state transitions, progression access and client interaction.
5. **Scenario simulation** — run standardized solo, duo, party, density, boss and PvP scenarios as applicable.
6. **Telemetry review** — compare controlled results with aggregate real-server data where available.
7. **Cause classification** — determine whether the issue is kit, coefficient, itemization, Wheel/progression, encounter design, reliability, economy or execution burden.
8. **Smallest targeted adjustment** — change one attributable package where practical.
9. **Regression matrix** — re-run every materially affected context and progression band.
10. **Observation window** — monitor outcome before stacking another broad change.

---

# 13. Change communication contract

`DESIGN-DERIVED`

Every meaningful balance change should state:

- the observed problem;
- the affected role/context/progression band;
- the intended outcome;
- the mechanic or coefficient being changed;
- the expected tradeoff;
- the metrics that should improve;
- the metrics that must not regress beyond the accepted band;
- the rollback or follow-up trigger.

This directly addresses the recurring community concern that combined numerical packages are difficult to judge when their intended total outcome is not explained.

---

# 14. What should be preserved

`SOURCE-DERIVED`

The source analysis records several outcomes that received meaningful positive feedback and should not be casually lost during future tuning:

- clearer vocation identity;
- lower unnecessary input repetition;
- smoother RP spell rotation and reduced rune dependence;
- stronger Ice Wave identity for Druid;
- elemental identity for Sorcerer;
- improved Knight healing direction;
- Monk support/ranged identity concepts where they become mechanically complete and reliable.

`DESIGN-DERIVED`

Future balance should prefer targeted correction over reverting an entire successful direction because one part of the package is overtuned, undertuned or functionally incomplete.

---

# 15. Recommended future research packages

These are documentation/research packages, not implementation authorization.

## Package A — Per-vocation identity specifications

Create one bounded specification for each supported vocation using the worksheet in this document and the framework proposed by PR #799.

Suggested order:

1. Elite Knight;
2. Master Sorcerer;
3. Exalted Monk;
4. Royal Paladin;
5. Elder Druid.

The order is prioritization only, based on the density and maturity of currently available forum-derived questions. It is not a statement that one vocation is more imbalanced than another.

## Package B — Standardized combat scenario suite

Define deterministic and simulation-friendly scenarios for:

- single target;
- stable eight-target or representative full-box combat where applicable;
- dispersed targets;
- moving/kiting combat;
- sustained incoming damage;
- burst incoming damage;
- healing cadence;
- rescue/support;
- boss single-target;
- PvP burst/control.

## Package C — Progression breakpoint audit

For every vocation:

- locate the functional core rotation;
- record exact progression/Wheel requirements;
- compare early, mid, high and endgame access;
- identify cross-path taxes;
- separate core functionality from scaling bonuses.

## Package D — Balance telemetry contract

Define privacy-safe aggregate telemetry and normalization for:

- level/progression;
- skills;
- equipment quality;
- Wheel/build;
- party composition;
- hunt/encounter difficulty;
- player activity quality and bot/abuse filtering.

## Package E — Balance change ledger

Create a machine-readable or reviewable record for every balance patch containing:

- baseline;
- hypothesis;
- changed package;
- affected dimensions;
- expected benefit;
- expected cost;
- validation scenarios;
- observed outcome;
- follow-up decision.

---

# 16. Non-goals

This document does not:

- declare any vocation overpowered or underpowered in current Canary;
- establish current Real Tibia formulas or values;
- authorize copying 2026 proposal values from forum posts;
- assign final role target bands;
- define final Wheel costs;
- define final spell areas, target counts, cooldowns or coefficients;
- prove that any reported live Tibia issue exists in Canary;
- replace the Real Tibia parity playbook;
- replace deterministic runtime or physical-client validation.

---

# 17. Durable conclusion

`DESIGN-DERIVED`

The forum analysis should influence **how we balance**, not directly **what number we set**.

The durable OTS balance model should:

1. define vocation identity and role first;
2. treat difficulty, risk and progression investment as costs that require visible reward;
3. evaluate complete packages rather than isolated coefficients;
4. fix functional reliability before tuning output;
5. make core rotations available before extreme endgame progression;
6. measure solo, duo, party, density, boss and PvP contexts separately;
7. include sustain, economy and human execution in the balance model;
8. preserve successful gameplay directions while correcting bounded problems;
9. make each balance change attributable, measurable and reversible;
10. use forum feedback to prioritize investigations, never as numeric authority.

This document should be revalidated whenever the underlying forum analysis receives material new vocation-specific evidence or when the upstream vocation/class framework changes.
