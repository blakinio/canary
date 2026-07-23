# Real Tibia Vocation Adjustments Forum Analysis

> Status: community-feedback evidence, not gameplay parity proof
>
> Primary release corpus collected: 2026-07-22
>
> General Changes and supplemental Druid design threads reviewed: 2026-07-23
>
> Target use: bounded design and validation input for `blakinio/canary`

## Executive summary

Three official Tibia forum threads provide a proposal-to-release view of the 2026 vocation adjustments:

1. **General Changes** records the first reaction to the system-wide proposal: charm and AoE scaling, Energy Ring, UH/IH support, combat mode, mitigation, and mana potions.
2. **Release State** records expectations, unresolved test concerns, and official clarifications before the live release.
3. **Release** records live-server bugs, balance experience, subsequent numerical nerfs, and the community response through the thread's closure.

The strongest cross-thread conclusion is not that one vocation simply needs more power. Players repeatedly ask for a legible relationship between mechanical difficulty, risk, Wheel investment, role specialization, and practical reward.

A supplemental review of the first page of the earlier official **Vocation Balancing Druid** thread adds design-stage evidence for Elder Druid. It is not included in the 4,228-post primary-corpus statistics because only 20 of the thread's 393 displayed results were accessible in that collection. Within the 17 deduplicated community contributions on that page, the clearest concerns were the doubled healing cooldown in the group stance, weak solo hunting, and insufficiently specified Forked Spells.

The January General Changes discussion was broad and exploratory: all 765 displayed posts were accessible, representing 666 author names. A coarse critical-language indicator matched 29.5% of its non-official posts. The same indicator rose to 43.5% in Release State and 70.3% across the post-release thread, reaching 80.0% during July 7–8 immediately after numerical corrections. The discussion therefore moved from *define the compensation and preserve useful roles*, through *clarify and finish the mechanics*, toward *justify the balance model and its combined effects*.

Several proposal-stage and pre-release warnings later became major live topics:

- Elite Knight healing cooldown and stance trade-offs;
- Master Sorcerer targeting, beam execution, and elemental-rotation complexity;
- Exalted Monk high-density scaling, bossing, targeting, and incomplete functionality;
- Royal Paladin charm behavior, spell area, Swift Foot, and Sharpshooter;
- Elder Druid Wheel placement and the cost of obtaining the complete solo rotation.

This report does not establish official formulas, live values, or Canary defects. It identifies recurring community-observed problem statements that require independent source, code, and runtime validation before implementation.

## Sources and provenance

| Phase | Official thread | Thread ID | Displayed results | Accessible unique posts | Observed dates |
|---|---|---:|---:|---:|---|
| Proposal | [Vocation Balancing General Changes](https://www.tibia.com/forum/?action=thread&threadid=4992263&pagenumber=1) | `4992263` | 765 | 765 | 2026-01-22–2026-01-29 |
| Pre-release | [Vocation Adjustments Release State](https://www.tibia.com/forum/?action=thread&threadid=4996962&pagenumber=1) | `4996962` | 606 | 600 | 2026-06-02–2026-06-11 |
| Post-release | [Vocation Adjustments Release](https://www.tibia.com/forum/?action=thread&threadid=4997270&pagenumber=1) | `4997270` | 2,863 | 2,863 | 2026-06-16–2026-07-21 |

### Supplemental source (excluded from primary-corpus totals)

| Phase | Official thread | Thread ID | Displayed results | Accessible page-one posts | Observed date |
|---|---|---:|---:|---:|---|
| Early design feedback | [Vocation Balancing Druid](https://www.tibia.com/forum/?action=thread&threadid=4992268&pagenumber=1) | `4992268` | 393 | 20 | 2026-01-22 |

The supplemental source is reported separately because Chrome exposed the selected first page, while direct requests for the remaining pages were rejected by Tibia.com with HTTP 403 during this collection. No values or opinions from inaccessible pages are inferred.

Collection facts:

- Post identifiers were used for uniqueness checks.
- All 765 displayed results in thread `4992263` were collected from pages 1–39 without duplicate identifiers. The corpus contains 666 author names and three posts carrying the official-post marker.
- All 2,863 displayed results in thread `4997270` were collected without duplicate identifiers.
- Active content in thread `4997270` ended on page 144 even though navigation exposed pages through 147; pages 145–147 returned no posts.
- Thread `4996962` yielded 600 unique posts on pages 1–30. Its linked page 31 repeatedly returned HTTP 403, so six displayed results were not accessible and are not inferred.
- The two later corpora contain 3,463 unique posts, 1,825 unique author names, and 33 official-marker posts. Two hundred author names appear in both later corpora.
- Across all three threads, the accessible corpus contains 4,228 unique post identifiers and 36 official-marker posts. A three-thread unique-author total was not recomputed from the earlier retained aggregates, so per-thread author counts are reported instead.

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

Forum posts may be edited or deleted after collection. Primary-corpus counts are a snapshot from 2026-07-22; the supplemental page-one sample is a snapshot from 2026-07-23.

## Supplemental design-stage evidence: Vocation Balancing Druid

This section analyzes only page one of thread `4992268`. It is a bounded design-stage sample, not a complete-thread sentiment result and not part of either the 4,228-post primary corpus or its 3,463-post later-thread subset.

### Official proposal represented on the page

The opening community-manager post proposed:

- a group-healing stance with doubled cooldowns for Heal Friend and Mass Healing and 110% increased ally healing;
- a solo stance with 10% increased self-healing;
- a distributed stance that sends 30% of Heal Friend or Nature's Embrace healing to a second nearby lowest-health ally;
- more reliable healing and damage spells, Nature's Embrace base power of 2,000, and stronger/range-seven Strike spells;
- earth and ice Forked Spells;
- Wheel changes for Healing Link, critical healing, Terra Wave life leech, and Strong Ice Wave;
- a lethal-damage Barrier that converts overkill into eight times as much mana loss;
- mana-generating, longer-range rods with intentionally modest damage.

The Barrier was reiterated in a second official post after being restored to the opening note.

These are proposal-state values from January 22, 2026. They are not evidence of current Real Tibia behavior and must not be copied into Canary without current authoritative and runtime validation.

### Page-one composition

| Metric | Count |
|---|---:|
| Visible posts | 20 |
| Official posts | 2 |
| Community posts | 18 |
| Deduplicated community contributions | 17 |
| Distinct community authors | 17 |
| Authors with a displayed level | 14 |
| Displayed level range | 470–1,604 |
| Median displayed level | 656 |

One author posted the same response twice. The thematic counts below remove that duplicate and ignore text reproduced inside quotation blocks where the author's own surrounding text does not independently raise the issue.

| Displayed author vocation | Deduplicated contributions | Share |
|---|---:|---:|
| Elder Druid | 11 | 64.7% |
| Elite Knight | 2 | 11.8% |
| Master Sorcerer | 1 | 5.9% |
| Missing or traded character | 3 | 17.6% |

This is a high-level, Druid-heavy convenience sample. It cannot represent low-level players or the full thread.

### Recurring page-one themes

| Theme | Deduplicated contributions | Share | Interpretation boundary |
|---|---:|---:|---|
| Group stance or doubled healing cooldown concern | 11 | 64.7% | Ten were clearly negative; one reconsidered the stance after editing the post but retained downtime concerns. |
| Solo, duo, damage, or experience-rate weakness | 10 | 58.8% | Mostly claims about practical hunting performance; no logs or controlled benchmarks were supplied on this page. |
| Forked Spell targeting, geometry, or specification concern | 5 | 29.4% | Authors wanted automatic secondary targeting or enough detail to judge real rotations. |
| Rune area or wave-area concern | 4 | 23.5% | Connected to mobile AoE hunting and compensation for a referenced rune-area reduction. |
| Positive interest in distributed healing | 3 | 17.6% | Support included the automatic lowest-health target; one author expected it to dominate party choices. |
| Positive interest in Wheel or critical-healing changes | 3 | 17.6% | These were among the few repeatedly praised support changes. |
| Rod/mana-generation interest | 2 | 11.8% | A third author questioned whether rod damage would matter. |
| Strong/Ultimate Strike relevance concern | 2 | 11.8% | Both argued that single-target Strike spells do not address the AoE gameplay loop. |
| Heal variance or weak minimum-heal concern | 2 | 11.8% | Authors asked for more reliable base healing rather than longer cooldowns. |

Counts overlap because one contribution can raise several issues.

### Design implications

#### 1. The group stance is primarily a burst-versus-gap trade

Using only the proposal's headline multipliers, a baseline heal of `H` every `C` seconds becomes `2.10H` every `2C` seconds:

`2.10H / 2C = 1.05H / C`

The nominal sustained-healing increase is therefore only 5% before overhealing, missed timing, shared cooldowns, critical heals, and encounter damage cadence. The stance can still create a much larger single-heal rescue window, but it also doubles the interval in which a target may receive no Heal Friend or Mass Healing.

For Canary, average healing per second is not enough. Validation should compare:

- effective, non-overheal throughput;
- maximum time without an ally heal;
- target death probability during burst sequences;
- the effect of low and high heal rolls;
- duo, four-player hunt, and boss compositions;
- interaction with cooldown resets and other healers.

#### 2. The solo stance does not answer the dominant solo complaint

A 10% self-healing increase improves sustain, but the sampled complaints mostly concern experience per hour, AoE coverage, damage rotation, and restricted hunting-ground choice. Treating self-healing as the complete solo compensation risks solving a different variable than the one players reported.

Any Canary investigation should separate at least:

- survival-limited solo performance;
- damage-limited solo performance;
- AoE geometry and pull size;
- experience and profit across level bands;
- dependence on runes versus vocation spells.

#### 3. Forked Spells need a deterministic targeting contract

The page did not give enough information to evaluate the new targeting mode. Before values are tuned, a parity investigation needs to establish:

- maximum secondary-target count;
- search radius and shape;
- whether secondary targets are automatic;
- tie-breaking and lowest-distance rules;
- damage falloff, if any;
- behavior when moving, changing target, or losing line of sight;
- Wheel unlock point and the level at which the complete rotation is available.

Without that contract, balance measurements mix targeting defects, execution difficulty, and raw damage.

#### 4. AoE compensation should match the actual Druid loop

Several authors connected solo weakness to narrow waves, rune-area changes, and the difficulty of aiming while kiting. Buffing Strong and Ultimate Strike spells does not automatically compensate an AoE-oriented rotation if those spells remain outside realistic hunt usage.

The relevant comparison is not spell-sheet power. It is damage and sustain over complete rotations against representative target counts and layouts.

#### 5. Barrier requires tail-risk tests, not only average sustain tests

The proposed eight-times overkill conversion is intentionally severe: 500 overkill damage would consume 4,000 mana and 1,000 overkill would consume 8,000 mana. Deterministic tests should cover:

- exact-lethal and one-point-over-lethal hits;
- sufficient, exactly sufficient, and insufficient mana;
- simultaneous or same-tick damage sources;
- existing mana-shield interactions;
- PvE and PvP rule differences;
- whether the character remains at one hit point and how subsequent damage resolves.

#### 6. Duo play needs its own stance analysis

One Elite Knight author explicitly asked which stance fits an EK + ED duo. The distributed stance refers to a second ally, the group stance increases healing gaps, and the solo stance may not improve ally healing. Whether the caster can be the distributed secondary target is not established by this page and must be verified rather than assumed.

### Bounded Canary validation matrix

| Priority | Question | Minimum evidence before a code change |
|---:|---|---|
| 1 | Does the group stance reduce or increase ally deaths despite nominally higher healing? | Current Canary path, current authoritative behavior, deterministic cadence simulation, and duo/team fixtures. |
| 2 | Is Druid solo performance damage-limited, survival-limited, or both by level band? | Repeatable hunt simulations or controlled telemetry with target layouts, full rotations, supplies, and equipment held constant. |
| 3 | Are Forked Spells mechanically reliable before damage tuning? | Target-selection specification plus tests for count, range, ties, movement, and line of sight. |
| 4 | Does the complete Druid rotation arrive at an appropriate Wheel investment? | Wheel-path audit and functional breakpoints across representative levels. |
| 5 | Does Barrier prevent isolated one-shots without becoming a general-purpose extra health pool? | Exact boundary tests and representative mana-pool/overkill distributions. |
| 6 | Do rods materially improve sustain without becoming the primary damage source? | Mana-per-turn, range, hit-rate, rotation, and leech accounting. |

### Supplemental-source conclusion

The first page does not support a flat “buff Druid” conclusion. It supports a more specific hypothesis:

> The proposed Druid package may improve support flexibility while leaving solo damage and AoE constraints under-addressed, and the group-healing stance may exchange safer burst heals for dangerous cadence gaps with only a small nominal throughput gain.

That hypothesis is actionable for prioritizing tests, but the sample is too small and incomplete to set values or prove parity.

## Corpus composition

### General Changes proposal corpus

| Displayed author vocation | Posts | Share |
|---|---:|---:|
| Royal Paladin / Paladin | 214 | 28.0% |
| Elite Knight / Knight | 182 | 23.8% |
| Master Sorcerer / Sorcerer | 166 | 21.7% |
| Elder Druid / Druid | 93 | 12.2% |
| None, missing, or other | 69 | 9.0% |
| Exalted Monk / Monk | 41 | 5.4% |

Displayed levels were available for 698 posts and ranged from 2 to 3,076, with a median of 601. This is author-character context, not proof of the player's main vocation, experience, or the level at which the reported behavior occurred.

### Combined accessible corpus

| Displayed author vocation | Posts | Share |
|---|---:|---:|
| Master Sorcerer / Sorcerer | 1,114 | 26.3% |
| Elite Knight / Knight | 1,102 | 26.1% |
| Royal Paladin / Paladin | 701 | 16.6% |
| Exalted Monk / Monk | 572 | 13.5% |
| Elder Druid / Druid | 537 | 12.7% |
| None, missing, or other | 202 | 4.8% |

### Phase comparison

| Metric | General Changes | Release State | Release |
|---|---:|---:|---:|
| Accessible posts | 765 | 600 | 2,863 |
| Unique author names | 666 | 440 | 1,585 |
| Official-marker posts | 3 | 11 | 22 |
| Accessible non-official posts | 762 | 589 | 2,841 |
| Posts matching critical-language indicator | 225 | 256 | 1,996 |
| Critical-language share | 29.5% | 43.5% | 70.3% |

The post-release thread was broad rather than dominated by a small group: it contained 1,585 author names, had a median of one post per author, and 1,094 authors posted only once. The ten most active authors contributed 221 posts, or 7.7% of the thread.

## January General Changes findings

The proposal thread was unusually broad: 585 of its 666 author names posted only once, and the ten most active names contributed 32 posts, or 4.2% of the corpus. This limits the risk that the headline counts merely reflect a few highly active accounts.

### Topic engagement

| Proposed system-wide change | Non-official posts mentioning theme | Share of 762 non-official posts |
|---|---:|---:|
| Potion access, tiers, or mana restoration | 248 | 32.5% |
| UH/IH use on other characters | 236 | 31.0% |
| Energy Ring or mana shield | 218 | 28.6% |
| AoE rune area or affected runes | 211 | 27.7% |
| Autoattacks, charms, or diamond arrows | 203 | 26.6% |
| Combat mode or battle stances | 93 | 12.2% |
| Mitigation, dedication perks, or lesser gems | 90 | 11.8% |

A post can match multiple themes. These are post-level engagement counts, not votes. Rendered quotations can carry a theme into a reply and therefore measure discussion propagation as well as independent reports.

### Role and vocation signals

- **Autoattacks and charms:** 106 of 203 matching posts displayed Paladin, making RP the source of 52.2% of engagement. Repeated concerns involved Diamond Arrow multi-target identity, Low Blow, Fatal Hold, and whether unspecified new spells and stances would fully compensate the loss.
- **AoE runes:** Sorcerer and Druid authors contributed 111 of 211 matching posts, or 52.6%. The dominant uncertainty was not merely lower damage; it was the interaction among reduced area, target density, charms, level scaling, positioning, and the still-unknown damage increase.
- **Energy Ring:** 109 of 218 matching posts displayed Paladin. The proposed 3 mana per absorbed damage point was frequently treated as a survivability and mana-pool question, with alternatives such as a lower ratio, cooldown, charge limit, or emergency-only barrier.
- **UH/IH on others:** this was cross-vocation rather than an MS-only topic. The 236 matching posts included 75 Sorcerer, 57 Paladin, 50 Knight, and 29 Druid posts. Players linked external UH use to EK+MS duos, boss mechanics, quests, PvP, emergency saves, and the risk of making a Druid mandatory. Common alternatives preserved a short rescue action without enabling full-time off-vocation healing.
- **Potions:** discussion was broad across RP (80 posts), EK (62), MS (50), and ED (24). Better access was often welcomed, while replies also questioned the Knight exception, the 50% universal-potion premium, how “next tier” applied to each vocation, and whether more potion throughput merely increased repetitive input.
- **Combat mode and mitigation:** these generated fewer posts than the controversial survival and AoE changes. Many replies welcomed simplification, permanent attack compensation, better shield/spellbook defence, and stronger mitigation choices, while asking for exact formulas, caps, and vocation-specific consequences.

### Official clarification and unresolved boundary

On January 23, the official follow-up stated that Intense Healing Rune would be treated like Ultimate Healing Rune, while the team considered another way for non-healer vocations to save a player briefly without becoming full-time healers. It also clarified the new superior mana-potion tier and stated that vocation stances would behave like persistent Monk Virtues. On January 29, the thread closed with confirmation that developers were analysing the feedback.

The thread therefore established problem statements and compensation requirements, not final values. For Canary, its most useful output is a scenario matrix:

1. compare single-target and increasing-density outcomes for charm, rune, and signature-spell rotations;
2. test emergency rescue separately from sustained healing throughput;
3. model Energy Ring against realistic mana pools and incoming burst at several level bands;
4. evaluate potion sustain, cost, and input rate together;
5. test combat-mode removal and mitigation as complete offensive/defensive packages rather than isolated percentages.

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

### General Changes thread

- **January 22:** proposed main-target-only charm triggering for autoattacks, smaller but stronger AoE runes, a 3:1 Energy Ring mana cost, removal of external UH use, removal of combat mode with permanent attack compensation, stronger mitigation, and broader mana-potion access.
- **January 23:** clarified that IH would follow UH, an emergency rescue alternative for non-healers was under consideration, superior mana potion would sit between Great and Ultimate and exclude Knights, and stances would persist like Monk Virtues.
- **January 29:** closed the feedback cycle by stating that developers were analysing the input.

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

## What the three-stage comparison adds

Analyzing only the post-release thread can make the July reaction look like resistance to any nerf. The proposal and pre-release threads show a more nuanced sequence:

1. Players welcomed potion access, simplification, mitigation improvements, stronger vocation identity, and several quality-of-life directions.
2. They immediately asked how compensation would preserve AoE scaling, emergency support, survivability, and practical role identity.
3. Release State narrowed those concerns to specific mechanics, targeting, accessibility, Wheel cost, and role performance.
4. CipSoft intentionally moved to live observation to obtain better data.
5. Live play expanded the concerns into sustain, hunting efficiency, team composition, and economy effects.
6. Numerical corrections on July 7 sharply increased criticism because players perceived cumulative reductions without an equally concrete explanation of targets or trade-offs.

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

Across 4,228 accessible posts in three official threads, the community consistently supports stronger vocation identity, new rotations, useful defensive choice, and lower unnecessary input complexity. The main rejection concerns incomplete functional access, unclear role trade-offs, late Wheel availability, and numerical packages whose combined risk or complexity appears greater than their practical reward.

For Canary, the durable lesson is methodological: use the forum to identify high-value validation questions, then prove each mechanic independently. Community volume can prioritize investigation; it cannot replace authoritative values, current source inspection, or runtime evidence.
