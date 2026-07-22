# Real Tibia Vocation Adjustments Forum Analysis

> Status: community-feedback evidence, not gameplay parity proof
>
> Collected: 2026-07-22
>
> Target use: bounded design and validation input for `blakinio/canary`

## Executive summary

Two official Tibia forum threads provide a useful before-and-after view of the 2026 vocation adjustments:

1. **Release State** records expectations, unresolved test concerns, and official clarifications before the live release.
2. **Release** records live-server bugs, balance experience, subsequent numerical nerfs, and the community response through the thread's closure.

The strongest cross-thread conclusion is not that one vocation simply needs more power. Players repeatedly ask for a legible relationship between mechanical difficulty, risk, Wheel investment, role specialization, and practical reward.

Pre-release discussion was mixed and often constructive. A lexical indicator marked 43.5% of accessible non-official Release State posts as critical. The same indicator reached 70.3% across the post-release thread and 80.0% during July 7–8, immediately after numerical corrections. The discussion therefore moved from *clarify and finish the mechanics* toward *justify the balance model and its combined effects*.

Several pre-release warnings later became major live topics:

- Elite Knight healing cooldown and stance trade-offs;
- Master Sorcerer targeting, beam execution, and elemental-rotation complexity;
- Exalted Monk high-density scaling, bossing, targeting, and incomplete functionality;
- Royal Paladin charm behavior, spell area, Swift Foot, and Sharpshooter;
- Elder Druid Wheel placement and the cost of obtaining the complete solo rotation.

This report does not establish official formulas, live values, or Canary defects. It identifies recurring community-observed problem statements that require independent source, code, and runtime validation before implementation.

## Sources and provenance

| Phase | Official thread | Thread ID | Displayed results | Accessible unique posts | Observed dates |
|---|---|---:|---:|---:|---|
| Pre-release | [Vocation Adjustments Release State](https://www.tibia.com/forum/?action=thread&threadid=4996962&pagenumber=1) | `4996962` | 606 | 600 | 2026-06-02–2026-06-11 |
| Post-release | [Vocation Adjustments Release](https://www.tibia.com/forum/?action=thread&threadid=4997270&pagenumber=1) | `4997270` | 2,863 | 2,863 | 2026-06-16–2026-07-21 |

Collection facts:

- Post identifiers were used for uniqueness checks.
- All 2,863 displayed results in thread `4997270` were collected without duplicate identifiers.
- Active content in thread `4997270` ended on page 144 even though navigation exposed pages through 147; pages 145–147 returned no posts.
- Thread `4996962` yielded 600 unique posts on pages 1–30. Its linked page 31 repeatedly returned HTTP 403, so six displayed results were not accessible and are not inferred.
- The combined accessible corpus contains 3,463 unique posts, 1,825 unique author names, and 33 posts carrying the forum's official-post marker.
- Two hundred author names appear in both corpora, derived from the separate and combined unique-author counts.

## Evidence boundary

The official forum is strong evidence for:

- what players publicly reported and proposed;
- the frequency and timing of recurring discussion themes;
- statements made by posts carrying the official community-manager marker;
- the change in discussion focus before and after release.

It is not sufficient evidence for:

- exact spell, damage, healing, cooldown, or scaling formulas;
- whether a reported behavior was reproducible or intended;
- current Real Tibia behavior after the observation date;
- current Canary implementation behavior or parity;
- a specific balance value to encode in Canary.

Any implementation proposal derived from this report must follow `docs/agents/REAL_TIBIA_PARITY_PLAYBOOK.md`, prove the current Canary path, pin an authoritative behavior/value source, and add deterministic validation.

## Method

Each accessible post was projected into:

- thread phase and page;
- unique post identifier;
- author name;
- displayed vocation and level;
- timestamp;
- official-post marker;
- rendered post text.

The analysis used post-level keyword families rather than raw word occurrence counts. A post could belong to multiple themes. This intentionally measures the breadth of discussion, not mutually exclusive issue counts.

The critical-language indicator matched words and phrases such as `nerf`, `broken`, `weak`, `problem`, `bug`, `unfair`, and `disappoint`. It is a coarse lexical indicator, not a trained sentiment classifier. Positive and critical language can coexist in one constructive post.

Rendered quotations remain in many replies. A quoted issue can therefore increase the number of posts associated with a theme. This is useful as an engagement measure but must not be interpreted as an equal number of independent reports.

Forum posts may be edited or deleted after collection. Counts are a snapshot from 2026-07-22.

## Corpus composition

### Combined accessible corpus

| Displayed author vocation | Posts | Share |
|---|---:|---:|
| Master Sorcerer / Sorcerer | 948 | 27.4% |
| Elite Knight / Knight | 920 | 26.6% |
| Exalted Monk / Monk | 531 | 15.3% |
| Royal Paladin / Paladin | 487 | 14.1% |
| Elder Druid / Druid | 444 | 12.8% |
| None, missing, or other | 133 | 3.8% |

### Phase comparison

| Metric | Release State | Release |
|---|---:|---:|
| Accessible posts | 600 | 2,863 |
| Unique author names | 440 | 1,585 |
| Official-marker posts | 11 | 22 |
| Accessible non-official posts | 589 | 2,841 |
| Posts matching critical-language indicator | 256 | 1,996 |
| Critical-language share | 43.5% | 70.3% |

The post-release thread was broad rather than dominated by a small group: it contained 1,585 author names, had a median of one post per author, and 1,094 authors posted only once. The ten most active authors contributed 221 posts, or 7.7% of the thread.

## How the discussion changed after release

| Theme family | Release State posts | Share of pre-release non-official posts | Release posts | Share of post-release non-official posts | Change |
|---|---:|---:|---:|---:|---:|
| Nerfs, balance, and damage | 333 | 56.5% | 2,054 | 72.3% | +15.8 pp |
| Bugs or unintended behavior | 72 | 12.2% | 672 | 23.7% | +11.4 pp |
| Solo versus team hunting | 120 | 20.4% | 899 | 31.6% | +11.3 pp |
| Healing and cooldowns | 242 | 41.1% | 867 | 30.5% | −10.6 pp |
| Monk rotation, fist blows, and stance | 121 | 20.5% | 818 | 28.8% | +8.2 pp |
| Mana, potions, and mana shield/buffer | 96 | 16.3% | 691 | 24.3% | +8.0 pp |
| RP barrage, grenade, and Divine mechanics | 162 | 27.5% | 561 | 19.7% | −7.8 pp |
| Runes, elements, and imbuements | 174 | 29.5% | 628 | 22.1% | −7.4 pp |

The decrease in healing's relative share does not mean healing was resolved. It means the live discussion expanded sharply into bugs, damage outcomes, mana sustainability, solo/team performance, and cumulative nerf effects.

### July 7 inflection point

The post-release corpus has a clear temporal break:

| Period | All posts | Non-official posts | Critical-language posts | Critical-language share |
|---|---:|---:|---:|---:|
| June 16–July 6 | 1,216 | 1,200 | 699 | 58.3% |
| July 7–8 | 1,017 | 1,015 | 812 | 80.0% |
| July 9–21 | 630 | 626 | 485 | 77.5% |

July 7–8 alone produced 35.5% of all posts in the release thread. Posts concerning nerfs, balance, or damage rose from 60.0% before July 7 to 81.8% on July 7–8 and remained at 80.5% afterward.

The community-manager response on July 7 described numerical adjustments as the next necessary step after testing the mechanics in practice. The July 8 response acknowledged disappointment with the nerfs, called them necessary for overall balance, and declined to discuss individual adjustments in more detail at that time.

## Cross-vocation findings

### 1. Difficulty and risk need a visible reward

The most consistent principle across professions is that mechanical difficulty, positional requirements, or defensive risk should produce an observable advantage over simpler alternatives.

Examples raised by players include:

- positioning beams and maintaining elemental rotations as MS;
- accepting Blood Rage's incoming-damage penalty as EK;
- directing wave-like and chained Monk abilities across dispersed targets;
- investing deeply in Wheel paths before ED's forked rotation becomes complete;
- using RP signature spells when simpler legacy options remain more efficient.

### 2. Damage changes also change sustain and economy

Players repeatedly reject analysis that treats a damage coefficient as an isolated offensive value. Lower damage can also mean:

- less life and mana leech;
- more incoming attack turns before a creature dies;
- higher potion use;
- lower profit;
- reduced survivability;
- different viable hunting grounds;
- altered team composition and experience per hour.

This systems-level effect is especially prominent in EK discussion but appears across all professions.

### 3. The core mechanic should arrive before endgame scaling

Wheel criticism is not limited to the total strength of perks. Many players want the functional core of a new rotation at a moderate level and later points to improve its power. They object when the complete mechanic requires a very high level while lower-level players receive an incomplete rotation.

### 4. Solo and party identity must both remain legible

Players generally accept that professions should have different strengths. They resist designs that make one profession structurally uncompetitive in a primary mode without a compensating role:

- EK damage and target-count limits;
- Monk justification for a team slot;
- ED access to solo-damage paths;
- MS execution cost versus rune alternatives;
- RP ranged identity versus close-range repetitive play.

### 5. Numerical changes need combined-effect explanations

After July 7, many complaints focused on stacked changes rather than one coefficient. The community repeatedly asked for the rationale and expected outcome of the entire package: base power, mastery percentages, Wheel investment, cooldown, mana cost, area, and defensive penalties together.

## Findings by vocation

### Elite Knight

#### Pre-release expectations and warnings

- The two-second shared cooldown for Knight healing spells was immediately described as a nerf.
- Players questioned why both stances combined a benefit with a punishment while other professions appeared to choose between benefits.
- Questions about Groundshaker, Shield Slam/Chivalrous Challenge placement, healing augments, and Blood Rage already exposed uncertainty about EK's intended offensive and defensive identity.

#### Live-server feedback

- Blood Rage became the clearest risk/reward example: players argued that the offensive bonus was reduced while the incoming-damage penalty remained.
- Lower damage was linked to lower leech and therefore lower practical survivability.
- Team-hunt feedback described EK as the lowest damage contributor even when continuously attacking full boxes.
- Solo feedback emphasized target-count limits, experience per hour, and equipment dependency.
- Improved healing and some quality-of-life changes were acknowledged positively, but many players felt the design pushed EK toward mandatory tank specialization rather than a meaningful stance choice.

#### Validation questions for Canary

- What explicit offensive, defensive, solo, and team roles does Canary intend EK to occupy?
- Does each stance's total reward match its penalty after accounting for leech and kill-time effects?
- At what level ranges is the complete intended rotation available?

### Master Sorcerer

#### Pre-release expectations and warnings

- Elemental stances and spell conversion were broadly recognized as a stronger identity.
- Players were already concerned about fire-versus-energy rotation quality, Death Echo area and targeting, Beam Mastery geometry, and the value of mana buffer.
- Official replies clarified Death Echo's three targeting modes and several Beam Mastery details, showing that control and calculation semantics were major concerns before launch.

#### Live-server feedback

- Players argued that the combined reduction of Beam Mastery and beam base damage was stronger than necessary.
- Side beams were described as too weak for the positional effort and cooldown.
- Maintaining the desired element could conflict with Momentum or cooldown reductions, making optimization less intuitive.
- Death Echo was considered interesting but execution-heavy and affected by cursor/crosshair and position issues.
- Mid-level players frequently described the Wheel investment needed for the intended playstyle as excessive.
- A repeated design rule was that a correctly executed beam rotation should outperform a simpler rune rotation.

#### Validation questions for Canary

- Does added positional and rotational difficulty produce measurable benefit at low, mid, and high levels?
- Are elemental-conversion rules, cooldown interactions, and target modes explainable and testable?
- Is core beam gameplay accessible before late-endgame Wheel totals?

### Exalted Monk

#### Pre-release expectations and warnings

- Players described Monk changes as underwhelming before release.
- High-density damage, dispersed targets, bossing, Guiding Presence, Thousand Fist Blows cooldown, and the lack of a clear high-level scaling path were already central concerns.

#### Live-server feedback

- Early posts reported functional issues with Mentor, Chained Penance range, Executioner's Throw, physical melee hits, and target acquisition.
- Later posts broadened the problem to multi-target scaling, boss contribution, sustain, spell shapes, and the absence of a complete ranged builder/spender rotation.
- Chained Penance remained the signature topic: target count, decreasing damage across chains, initial range, and its importance to Monk identity.
- Optimized team-hunt feedback questioned when Monk justifies replacing an MS or RP.
- Many proposals focused on functionality and targeting rather than a flat global damage increase.

#### Validation questions for Canary

- Which reported problems are defects, which are intended trade-offs, and which are scaling-design gaps?
- Does Monk have a distinct, measurable team contribution and boss role?
- Can the full builder/spender identity function across realistic target distributions?

### Royal Paladin

#### Pre-release expectations and warnings

- New spell rotations were generally anticipated positively.
- Players requested exact spell areas and questioned the effect of restricting AoE ammunition charm triggers to the main target.
- Swift Foot's damage reduction, cooldown, and speed value were questioned.
- Sharpshooter's total-skill scaling was immediately compared with other vocation power budgets.

#### Live-server feedback

- Divine Barrage was often compared unfavorably with Divine Caldera or Ethereal Barrage after nerfs, considering area, mana cost, and damage together.
- Sharpshooter reductions were viewed as especially costly because RP remains strongly tied to physical damage.
- Charm-proc changes were described as a major DPS loss without enough baseline compensation.
- Divine Defiance feedback connected reduced magic level to emergency healing and survivability.
- The smoother spell rotation and reduced rune dependence were repeatedly praised.
- Holy Grenade was often considered too weak after the unintended boss interaction was removed.

#### Validation questions for Canary

- Do signature RP spells remain preferable in the situations they are designed for?
- Is the physical-damage dependency accounted for in stance and Sharpshooter values?
- Does the rotation preserve ranged identity rather than returning to a narrow close-range pattern?

### Elder Druid

#### Pre-release expectations and warnings

- Release State contained an acknowledged copy/paste mistake in the Druid Wheel description.
- Strong Ice Wave augment placement, Forked Spells, Heal Friend, and the relationship between solo and party paths were already recurring topics.
- Players welcomed improved Ice Wave and the prospect of less rune-dependent solo play.

#### Live-server feedback

- The central complaint was the placement and cost of Forked Spells relative to Heal Friend and Strong Ice Wave.
- Player examples claimed that obtaining large Ice Wave and both fork augments required hundreds more Wheel points than a late test configuration.
- Without the additional fork target, players often considered runes more efficient, undermining the intended rotation change.
- Solo ED players objected to investing deeply in a party-healing branch to reach useful damage functionality.

#### Validation questions for Canary

- Can solo-damage and party-healing identities be selected without excessive cross-path tax?
- At what level does the full forked rotation become functional?
- Do runes remain an alternative rather than the dominant answer after investing in the new rotation?

## Official-response chronology

### Release State thread

The official-marker posts were comparatively specific and operational:

- **June 2:** corrected the Druid copy/paste error; clarified Swift Foot cooldowns, charm scope, RP spell area, Groundshaker/Shield Slam placement, Death Echo placement and targeting, Monk auto-attack questions, Chivalrous Challenge cooldown, and Strong Ice Wave augments.
- **June 3:** stated that release would not end the balancing process; answered questions about Divine Defiance, IH/UH emergency healing, Death Echo's second hit, Beam Mastery, Forked Spells, charms, rune prices, healing, gems, and Wheel timing.
- **June 5:** rejected a single fixed “buff to strongest” or “nerf to weakest” philosophy and emphasized concrete gameplay situations, data, level range, and content.
- **June 8:** confirmed three Death Echo targeting modes.
- **June 9:** discussed launch timing and elemental-mechanic questions.

The key official pre-release position was that some important information could only be obtained from live servers.

### Release thread

The official response evolved in three stages:

1. **Immediate bug triage:** Druid Wheel layout, Death Echo, imbuement restrictions, Stone Shower, RP Grenade, healing scaling, Forked Thorns, target selection, and Monk issues were acknowledged or forwarded.
2. **Factual clarification:** daily rewards, converted-spell element semantics, and Strike imbuement restrictions received direct answers.
3. **General monitoring after numerical changes:** later posts emphasized collected data, long-term game health, respectful criticism, and the absence of promises or timelines. On July 13, the community manager stated that no decision had been made on whether or when further action would be taken. On July 21, the thread was closed and feedback was redirected to a new thread.

The response pattern suggests that discrete defects and factual questions were easier to address than the community's demand for a transparent multidimensional balance model.

## What the two-thread comparison adds

Analyzing only the post-release thread can make the July reaction look like resistance to any nerf. The pre-release thread shows a more nuanced sequence:

1. Players welcomed several identity and quality-of-life directions.
2. They identified specific mechanical, targeting, accessibility, and role concerns before launch.
3. CipSoft intentionally moved to live observation to obtain better data.
4. Live play expanded those concerns into sustain, hunting efficiency, team composition, and economy effects.
5. Numerical corrections on July 7 sharply increased criticism because players perceived cumulative reductions without an equally concrete explanation of targets or trade-offs.

The strongest interpretation is therefore not “players rejected balancing.” It is:

> Players accepted the need for iteration but expected hard mechanics, deep Wheel investment, and explicit risk to produce a visible, explainable reward across relevant level ranges and play modes.

## Implementation-neutral recommendations

These recommendations define questions and evidence, not values to copy:

1. **Publish or document a role matrix.** For each vocation, define intended relative strength in AoE, single target, sustain, solo, team, bossing, input difficulty, positional difficulty, and equipment dependency.
2. **Evaluate packages, not isolated coefficients.** Include base power, cooldown, area, mana, Wheel cost, leech, defensive penalty, target count, and rotation constraints in one impact model.
3. **Separate functional access from endgame scaling.** Unlock the complete mechanic earlier and use later investment to scale it where appropriate.
4. **Test multiple level bands.** A design that works above level 1,000 may still provide an incomplete or frustrating experience at levels 200–800.
5. **Prove difficulty premiums.** A correctly executed difficult rotation should have an explicit expected benefit over a simpler fallback, or the difficulty should be reduced.
6. **Close functional defects before interpreting balance data.** Targeting, range, placement, and broken augment behavior contaminate performance measurements.
7. **Keep positive outcomes.** Preserve smoother RP rotation, stronger Ice Wave identity, elemental MS identity, improved EK healing, and the overall move away from unnecessary inputs.
8. **Communicate expected outcomes.** Future changes should state what behavior is being corrected and what observable result would indicate success.

## Canary follow-up contract

This report may nominate a future investigation but cannot authorize a gameplay change. A bounded follow-up must:

1. select one exact mechanic and level/content range;
2. prove current `blakinio/canary` definition, registration, runtime path, and tests;
3. pin current official behavior or retain the value as `UNVERIFIED`;
4. separate Real Tibia parity from a deliberate Canary-specific design decision;
5. define one failing deterministic test or measurable simulation;
6. account for client/protocol coupling where relevant;
7. avoid importing values from forum consensus alone.

## Conclusion

Across 3,463 accessible posts, the community consistently supports stronger vocation identity, new rotations, and lower unnecessary input complexity. The main rejection concerns incomplete functional access, unclear role trade-offs, late Wheel availability, and numerical packages whose combined risk or complexity appears greater than their practical reward.

For Canary, the durable lesson is methodological: use the forum to identify high-value validation questions, then prove each mechanic independently. Community volume can prioritize investigation; it cannot replace authoritative values, current source inspection, or runtime evidence.
