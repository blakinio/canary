# Real Tibia Vocation Adjustments Forum Analysis

> Status: community-feedback evidence, not gameplay parity proof
>
> Primary release corpus collected: 2026-07-22
>
> Foundational Dev Note, General Changes, Sorcerer, Monk, and supplemental Druid design threads reviewed: 2026-07-23
>
> Target use: bounded design and validation input for `blakinio/canary`

## Executive summary

Six official Tibia forum corpora provide a vision-to-release view of the 2026 vocation adjustments:

1. **Dev Note: Vocation Balancing** records the foundational reaction to CipSoft's role, innovation, and input-reduction goals and the first stance, Barrier, and Mentor Other examples.
2. **General Changes** records the reaction to the later system-wide proposal: charm and AoE scaling, Energy Ring, UH/IH support, combat mode, mitigation, and mana potions.
3. **Sorcerer** adds the vocation-specific design expectations and objections that preceded testing.
4. **Monk** adds the vocation-specific support, ranged, chain-targeting, solo, bossing, and progression questions that preceded testing.
5. **Release State** records expectations, unresolved test concerns, and official clarifications before the live release.
6. **Release** records live-server bugs, balance experience, subsequent numerical nerfs, and the community response through the thread's closure.

The strongest cross-thread conclusion is not that one vocation simply needs more power. Players repeatedly ask for a legible relationship between mechanical difficulty, risk, Wheel investment, role specialization, and practical reward.

The complete foundational **Dev Note: Vocation Balancing** thread adds 1,625 unique posts across all 82 pages. Its 1,620 community posts show that players broadly connected the announced goals to concrete rotation, role, solo/team, Wheel, targeting, sustain, and quality-of-life problems rather than evaluating the four teaser mechanics in isolation.

The complete **Vocation Balancing Monk** thread adds 206 unique posts across all 11 pages. Its 203 community posts strongly connect Monk balance to damage after repeated nerfs, support identity, ranged completeness, solo performance, bossing, chain targeting, harmony, and Wheel access.

A supplemental review of the first page of **Vocation Balancing Druid** adds design-stage evidence for Elder Druid. It is not included in the 6,592-post primary accessible corpus because only 20 of the thread's 393 displayed results were accessible in that collection. Within the 17 deduplicated community contributions on that page, the clearest concerns were the doubled healing cooldown in the group stance, weak solo hunting, and insufficiently specified Forked Spells.

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
| Foundational vision | [Dev Note: Vocation Balancing](https://www.tibia.com/forum/?action=thread&threadid=4989637&pagenumber=1) | `4989637` | 1,625 | 1,625 | 2025-11-12–2025-11-19 |
| Proposal | [Vocation Balancing General Changes](https://www.tibia.com/forum/?action=thread&threadid=4992263&pagenumber=1) | `4992263` | 765 | 765 | 2026-01-22–2026-01-29 |
| Pre-release | [Vocation Adjustments Release State](https://www.tibia.com/forum/?action=thread&threadid=4996962&pagenumber=1) | `4996962` | 606 | 600 | 2026-06-02–2026-06-11 |
| Post-release | [Vocation Adjustments Release](https://www.tibia.com/forum/?action=thread&threadid=4997270&pagenumber=1) | `4997270` | 2,863 | 2,863 | 2026-06-16–2026-07-21 |

### Supplemental sources (excluded from primary-corpus totals)

| Phase | Official thread | Thread ID | Displayed results | Accessible unique posts | Coverage | Observed dates |
|---|---|---:|---:|---:|---|---|
| Early design feedback | [Vocation Balancing Druid](https://www.tibia.com/forum/?action=thread&threadid=4992268&pagenumber=1) | `4992268` | 393 | 20 | page 1 only | 2026-01-22 |
| Early design feedback | [Vocation Balancing Monk](https://www.tibia.com/forum/?action=thread&threadid=4992269&pagenumber=1) | `4992269` | 206 | 206 | all 11 pages | 2026-01-22-2026-01-29 |

The Druid source remains a page-one sample because direct requests for the remaining pages were rejected by Tibia.com with HTTP 403 during that collection. The Monk thread was collected from rendered public pages with isolated headless Chrome profiles after direct HTTP requests encountered the same protection. No account, cookies, or authenticated browser state were used.

Collection facts:

- Post identifiers were used for uniqueness checks.
- All 1,625 displayed results in thread `4989637` were collected from pages 1–82 without duplicate identifiers. Pages 1–81 contain 20 posts each and page 82 contains 5.
- The thread `4989637` snapshot contains 5 official-marker posts and 1,620 community posts from 1,400 community author names. Of those names, 1,247 posted once; the 10 most active names contributed 50 posts, or 3.1% of community posts.
- The thread `4989637` HTML snapshot was retrieved on 2026-07-23 as 82 rendered page documents totalling 14,608,900 bytes and retained outside Git. A canonical manifest of `filename<TAB>size<TAB>SHA-256<LF>` rows has SHA-256 `39cea2336a84b1621fdc52a19fc52763087660d492c5cb74cbe7467121c711af`.
- All 765 displayed results in thread `4992263` were collected from pages 1–39 without duplicate identifiers. The corpus contains 666 author names and three posts carrying the official-post marker.
- The thread `4992263` HTML snapshot was retrieved on 2026-07-23 as 39 page responses totalling 6,392,541 bytes and retained outside Git. A canonical manifest of `filename<TAB>size<TAB>SHA-256<LF>` rows has SHA-256 `5e175301a56477fa7bdedc9b88e39449e83045878f98eeefd8ae8738f8579553`.
- All 2,863 displayed results in thread `4997270` were collected without duplicate identifiers.
- Active content in thread `4997270` ended on page 144 even though navigation exposed pages through 147; pages 145–147 returned no posts.
- Thread `4996962` yielded 600 unique posts on pages 1–30. Its linked page 31 repeatedly returned HTTP 403, so six displayed results were not accessible and are not inferred.
- The two later corpora contain 3,463 unique posts, 1,825 unique author names, and 33 official-marker posts. Two hundred author names appear in both later corpora.
- Thread `4992269` yielded exactly 206 unique post identifiers: 20 posts on each page 1-10 and 6 posts on page 11.
- The Monk thread contains 3 community-manager posts and 203 community posts from 175 distinct author names.
- Across the six primary corpora, the accessible corpus contains 6,592 unique post identifiers and 48 official-marker posts. A six-corpus unique-author total was not recomputed from the separately retained aggregates, so per-thread author counts are reported instead.

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

Rendered quotations remain in many replies in the primary corpus. A quoted issue can therefore increase the number of primary-corpus posts associated with a theme. This is useful as an engagement measure but must not be interpreted as an equal number of independent reports.

For the foundational Dev Note analysis, 137 `blockquote.QuoteText` elements from 100 posts were removed before keyword-family matching. A post can still belong to several themes, and repeated posts by one author remain separate contributions. Theme breadth is therefore an engagement measure, not a vote count or a count of distinct reports.

For the supplemental Monk analysis, `blockquote.QuoteText` content was removed before keyword-family and structured-answer counting. A Monk post can still belong to several overlapping themes, and repeated posts by one author remain separate contributions; distinct-author counts are therefore reported beside post counts.

Forum posts may be edited or deleted after collection. Release-phase counts are a snapshot from 2026-07-22; the foundational Dev Note, January design-thread collections, and supplemental Druid page-one sample are snapshots from 2026-07-23.

## Foundational feedback: Dev Note Vocation Balancing

This section analyzes every displayed result in thread `4989637`. It captures reaction to an early design direction, before the later vocation-specific proposals, test-server iterations, or release changes. Proposed mechanics and values below describe the November 2025 note; they are not evidence of current Real Tibia or Canary behavior.

### Official goals and examples

The opening post framed the project around three pillars:

1. strengthen each vocation's role;
2. add gameplay innovation rather than only numerical changes;
3. reduce unnecessary inputs and improve quality of life.

It then used four early examples:

- permanent Blood Rage and Protector stances for Elite Knight;
- permanent Sharpshooter and Swift Foot stances for Royal Paladin;
- a mage Barrier that would intercept lethal damage and remove eight times the overkill from mana, with death when the remaining mana was insufficient;
- merging Virtue of Justice with Mentor Other and turning the latter into a party bonus for Monk.

The note also signalled Wheel revisions, replacement of outdated mechanics, and new spells. The accompanying official questions asked about the overall direction, examples of meaningful innovation, and each vocation's must-have changes. These questions produced feedback about complete roles and rotations, not just the four previewed mechanics.

### Full-thread composition

| Metric | Count |
|---|---:|
| Displayed and collected posts | 1,625 |
| Pages | 82 |
| Unique post identifiers | 1,625 |
| Duplicate identifiers | 0 |
| Official-marker posts | 5 |
| Community posts | 1,620 |
| Community author names | 1,400 |
| Community author names posting once | 1,247 |
| Community posts by the 10 most active names | 50 (3.1%) |
| Community posts with a displayed level | 1,395 |
| Displayed community level range | 2–3,076 |
| Median displayed community level | 580 |

The low concentration matters: the most active 10 names produced only 3.1% of community posts, while 89.1% of community author names posted once. Recurring themes therefore came from a broad author base, although author names are not verified unique people and repeated posts remain separate contributions.

| Displayed vocation family | Community posts | Share |
|---|---:|---:|
| Knight | 420 | 25.9% |
| Sorcerer | 363 | 22.4% |
| Paladin | 291 | 18.0% |
| None or missing | 239 | 14.8% |
| Druid | 214 | 13.2% |
| Monk | 93 | 5.7% |

The discussion was front-loaded: 901 posts appeared on November 12 and 314 on November 13. Those first two observed days account for 1,215 posts, or 74.8% of the corpus. This is rapid reaction to a high-level direction, not long-run evaluation of a stable implementation.

### Quote-free theme breadth

The following keyword families were matched after removing rendered quotation blocks. Counts overlap and measure how many community posts engaged with a topic; they are not approval totals, distinct-author counts, or verified defect reports.

| Theme family | Community posts | Share |
|---|---:|---:|
| Requests for exact mechanics, numbers, or implementation details | 892 | 55.1% |
| Vocation role or identity | 724 | 44.7% |
| Quality of life, inputs, or rotation | 684 | 42.2% |
| Stances | 650 | 40.1% |
| Team or party play | 616 | 38.0% |
| Solo play | 527 | 32.5% |
| Wheel of Destiny | 319 | 19.7% |
| Barrier | 276 | 17.0% |

More than half the community posts matched the request-for-details family. This is the clearest evidence boundary in the thread: many contributors could not judge balance from direction alone because state transitions, interaction rules, ranges, areas, cooldowns, coefficients, Wheel placement, and compensation were not yet specified.

### Vocation-specific problem signals

Narrower keyword families show which existing pain points contributors used to test the announced goals. They remain engagement signals rather than validated mechanics.

| Problem signal | Community posts | Share |
|---|---:|---:|
| Mage wand/rod basic attacks or autoattacks | 464 | 28.6% |
| Sorcerer beams or waves | 283 | 17.5% |
| Sorcerer Ultimate Healing Rune support | 254 | 15.7% |
| Knight challenge/exeta reliability | 220 | 13.6% |
| Knight mana or potion input | 183 | 11.3% |
| Druid earth, ice, or AoE tools | 144 | 8.9% |
| Paladin charm multi-proc behavior | 106 | 6.5% |
| Barrier interactions and boundary cases | 104 | 6.4% |
| Paladin stance safety, cancellation, or mobility | 64 | 4.0% |
| Monk Mentor Other or virtues | 54 | 3.3% |
| Elemental ammunition or weapons | 45 | 2.8% |

The examples reveal five distinct validation clusters:

- **Elite Knight:** reduce mana-potion input and improve challenge reliability without breaking existing taunt, sustain, or Blood Rage behavior.
- **Royal Paladin:** define stance cancellation, healing, attack, movement, and debuff rules; preserve charm and elemental-ammunition interactions.
- **Master Sorcerer:** make beam/wave execution and damage identity coherent while resolving awkward support and low-value wand attacks.
- **Elder Druid:** preserve healing identity while addressing solo AoE, earth/ice coverage, and practical rotation constraints.
- **Exalted Monk:** ensure Mentor Other and virtue changes do not remove value without compensation, and make the role and Wheel path legible in both solo and team play.

### Design implications

#### 1. The vision was easier to support than the previewed implementation

Many posts welcomed clearer roles and fewer unnecessary inputs while questioning whether permanent stances and passive replacements qualified as gameplay innovation. For Canary, a feature should be evaluated against the stated pillar it is meant to satisfy: role clarity, a genuinely new decision, or reduced input burden. A passive or toggle can be useful without proving the innovation pillar.

#### 2. Permanent stances require an operational contract before coefficient tuning

Stance validation must specify:

- activation and toggle cooldowns;
- which actions cancel or suppress the stance;
- whether healing, attacks, movement, death, dispels, or debuffs change its state;
- persistence across login, vocation promotion, arena, and PvP boundaries;
- interaction with existing spells and Wheel perks;
- migration or replacement of old augments.

Without those rules, reports about uptime and power mix state-machine defects with balance.

#### 3. Barrier is a tail-risk system, not a flat effective-health bonus

The opening post presented an approximate 73% effective-health interpretation, but the actual proposal depended on lethal overkill, remaining mana, and the eight-times conversion. Deterministic tests must cover exact lethal damage, one point of overkill, sufficient/exactly sufficient/insufficient mana, multiple same-tick hits, and subsequent damage. Interactions with Magic Shield, Mana Shield, Energy Ring, Gift of Life, death prevention, and PvP rules must be established before average effective health is used.

#### 4. Solo and team outcomes need separate matrices

Team or party play appeared in 616 posts and solo play in 527. A change can improve a formal party role while weakening solo access, duo utility, bossing, or general hunting. Each vocation therefore needs separate solo, duo, four-player hunt, and boss scenarios across representative level and Wheel-investment bands.

#### 5. Reliability and input gaps should be resolved before interpreting damage

Challenge reliability, mana-potion repetition, beam geometry, wand/rod attacks, UH support, charm processing, and elemental access are functional parts of the rotation. If they are unreliable or disproportionately laborious, raw damage telemetry will not isolate the balance question.

#### 6. Broad participation strengthens prioritization, not correctness

The corpus is not dominated by a handful of prolific accounts, which makes repeated themes useful for choosing validation work. It still does not make any requested mechanic or number correct. Current authoritative behavior, Canary source inspection, deterministic tests, and controlled measurements remain required.

### Official chronology

| Date and time | Post | Official action |
|---|---|---|
| 2025-11-12 10:59 | `#39551414` | Liamas opened the Dev Note with the three pillars and the stance, Barrier, and Mentor Other examples. |
| 2025-11-12 10:59 | `#39551416` | Liamas asked for feedback on direction, innovation, and must-have vocation changes; the thread was scheduled to remain open until November 19 at 10:00 CET. |
| 2025-11-12 15:27 | `#39551906` | Liamas thanked participants, said details could not yet be answered because work was in progress, requested on-topic replies, and stated that all feedback was being read. |
| 2025-11-13 09:14 | `#39552606` | Niadus described the response as chaotic but insightful, said it was shaping both shown and unrevealed proposals, and reiterated that every post was being read. |
| 2025-11-19 10:00 | `#39554066` | Liamas closed the thread and said engagement had exceeded expectations. |

The official replies confirm intake and influence on work in progress, but they do not validate individual requests, commit to values, or establish final behavior.

### Bounded Canary validation matrix

| Priority | Question | Minimum evidence before a code change |
|---:|---|---|
| 1 | Are stance transitions and cancellation rules deterministic? | Current authoritative behavior or specification plus tests for every activation, cancellation, persistence, and Wheel interaction. |
| 2 | Does Barrier resolve lethal boundaries and other defensive systems consistently? | Exact-damage fixtures covering mana thresholds, same-tick hits, death prevention, shields, rings, and PvE/PvP differences. |
| 3 | Does each vocation meet its intended role in both solo and team contexts? | A documented role matrix and controlled comparisons across level, equipment, Wheel, party, boss, and target-layout bands. |
| 4 | Do the changes reduce unnecessary inputs without hiding resource or timing costs? | Input-per-minute, mana/supply, cooldown, idle-time, and complete-rotation telemetry. |
| 5 | Are targeting, area, and reliability correct before raw coefficients are compared? | Deterministic geometry, range, retargeting, movement, line-of-sight, and multi-target tests. |
| 6 | Does the complete mechanic arrive at the intended progression point? | Wheel and equipment path audit with functional breakpoints and migration checks. |

### Foundational-source conclusion

The complete thread supports a bounded hypothesis:

> Players broadly supported clearer vocation roles and lower unnecessary input, but expected innovation to be demonstrated through complete, reliable rotations and explicit interaction rules—not inferred from high-level stances or isolated numerical examples.

That hypothesis prioritizes state-machine, boundary, targeting, rotation, and role tests. It does not prescribe coefficients or prove a Canary parity gap.

## Supplemental design-stage evidence: Vocation Balancing Druid

This section analyzes only page one of thread `4992268`. It is a bounded design-stage sample, not a complete-thread sentiment result and not part of either the 6,592-post primary accessible corpus or its 3,463-post later-thread subset.

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

## Supplemental design-stage evidence: Vocation Balancing Monk

This section analyzes all 206 unique posts in thread `4992269`. It is a complete-thread design-stage corpus, but it remains separate from the later 3,463-post Release State/Release corpus.

### Official proposal

The opening community-manager post proposed:

- Mass Spirit Mend without harmony consumption, with adjusted cooldown and higher base healing;
- Virtue of Justice and Mentor Other bonuses for nearby allies: 3% damage reduction for Knight, 6% auto-attack damage for Paladin, 9% spell/rune damage for Sorcerer, 12% healing for Druid, and 15% fist fighting for Monk;
- Thousand Fist Blows as a ranged builder with an area described as similar to diamond arrows;
- Mystic Repulse cooldown reduced from 20 to 12 seconds;
- Guiding Presence sharing 100% of mantra;
- Sanctuary adding 10% damage and healing against adjacent targets;
- Augmented Mystic Repulse I reducing cooldown by six seconds;
- the Augmented Sweeping Takedown slot becoming Augmented Thousand Fist Blows;
- Augmented Flurry of Blows I increasing area instead of granting life leech.

These are January 2026 proposal-state descriptions, not current authoritative Real Tibia values.

### Full-thread composition

| Metric | Count |
|---|---:|
| Unique posts | 206 |
| Pages collected | 11 of 11 |
| Community-manager posts | 3 |
| Community posts | 203 |
| Distinct community author names | 175 |
| Community posts with a displayed level | 163 |
| Displayed community level range | 3-3,076 |
| Median displayed community level | 592 |
| Monk/Exalted Monk community posts | 129 |
| Median displayed level among Monk/Exalted Monk posts | 610 |

| Displayed author vocation | Community posts | Share |
|---|---:|---:|
| Exalted Monk / Monk | 129 | 63.5% |
| Elite Knight / Knight | 11 | 5.4% |
| Royal Paladin / Paladin | 11 | 5.4% |
| Elder Druid / Druid | 8 | 3.9% |
| Master Sorcerer / Sorcerer | 4 | 2.0% |
| Missing or traded character | 40 | 19.7% |

The 129 posts carrying a displayed Monk vocation cover a broad but high-level-skewed range:

| Displayed Monk level band | Posts | Share of displayed Monk posts |
|---|---:|---:|
| 1-300 | 19 | 14.7% |
| 301-600 | 44 | 34.1% |
| 601-900 | 43 | 33.3% |
| 901+ | 23 | 17.8% |

Displayed forum levels are snapshot metadata, not proof of experience with every mechanic discussed. Counts are by post, so a repeat author can appear more than once.

### Attention to proposed components

The table below counts quote-free community posts that name each proposed component. It measures attention, not approval.

| Proposed component | Posts | Distinct authors |
|---|---:|---:|
| Virtue of Justice / VoJ | 62 | 59 |
| Thousand Fist Blows | 35 | 34 |
| Mass Spirit Mend | 32 | 32 |
| Flurry of Blows | 32 | 32 |
| Mystic Repulse | 24 | 24 |
| Sweeping Takedown replacement or takedown | 21 | 19 |
| Guiding Presence | 16 | 16 |
| Sanctuary | 13 | 13 |

Ninety-six community posts contained a parseable numbered answer to question 1. Within those answer-1 segments, the following changes were named:

| Change named in answer 1 | Answers | Share of parseable answer-1 segments |
|---|---:|---:|
| Virtue of Justice, Mentor Other, or party support | 29 | 30.2% |
| Thousand Fist Blows or ranged builder/gameplay | 28 | 29.2% |
| Mass Spirit Mend or healing | 19 | 19.8% |
| Flurry area change | 14 | 14.6% |
| Mystic Repulse | 6 | 6.3% |
| Guiding Presence or Sanctuary | 6 | 6.3% |

Because question 1 explicitly asks what is most exciting, this is stronger directional evidence than raw mentions. It is still not a clean approval poll: some replies copied the question text, named several features, or answered critically.

### Full-thread theme breadth

The following post-level keyword families were evaluated after removing rendered quote blocks. Families overlap.

| Theme family | Community posts | Distinct authors | Share of community posts |
|---|---:|---:|---:|
| Damage, DPS, nerfs, or burst | 129 | 119 | 63.5% |
| Support package or party buffs | 96 | 91 | 47.3% |
| Ranged package | 83 | 80 | 40.9% |
| Solo play | 76 | 72 | 37.4% |
| Bossing, single target, or PvP | 68 | 65 | 33.5% |
| Chain, bounce, or jump mechanics | 66 | 64 | 32.5% |
| Harmony or builder/spender loop | 66 | 61 | 32.5% |
| Wheel, gems, augments, Sanctuary, or Guiding Presence | 63 | 60 | 31.0% |
| Healing, Sio, or Mend | 62 | 61 | 30.5% |
| Elements, holy damage, or imbuements | 43 | 39 | 21.2% |
| Survivability, defence, Energy Ring, or tanking | 41 | 39 | 20.2% |
| Single-target Exeta, off-tanking, or trapped-player rescue | 14 | 14 | 6.9% |

Concrete subtopic counts help separate broad theme families:

- Chained Penance appeared in 30 posts, Spiritual Outburst in 35, and jump/bounce wording in 27.
- Boss wording appeared in 61 posts; PvP appeared in 5.
- Energy Ring appeared in 12 posts.
- Serene or Serene Stance appeared in 20 posts.
- Element, holy, or imbuement wording appeared in 40 posts.
- Exact Exeta wording appeared in 11 posts.

These counts show discussion breadth, not independent bug reproduction or agreement with a specific fix.

### Additional changes requested in structured answers

One hundred and two posts contained a parseable numbered answer 3. Their answer-3 segments produced the following overlapping request families:

| Request family in answer 3 | Answers | Share of parseable answer-3 segments |
|---|---:|---:|
| Solo play, damage, DPS, nerfs, or burst | 69 | 67.6% |
| Bossing, single target, or PvP | 40 | 39.2% |
| Chain, bounce, or jump mechanics | 39 | 38.2% |
| Wheel, gems, or augments | 27 | 26.5% |
| Elements, holy damage, or imbuements | 26 | 25.5% |
| Survivability or defence | 23 | 22.5% |
| Healing | 23 | 22.5% |
| Single-target Exeta, off-tanking, or rescue | 9 | 8.8% |
| Serene stance | 9 | 8.8% |

### Design implications

#### 1. Support identity was welcomed, but uptime and party value need proof

Virtue of Justice and party support led the parseable excitement answers. At the same time, authors questioned:

- whether Serene/proximity conditions make the bonuses unreliable in overlure or split-frontline hunts;
- whether a Monk becomes a mandatory buffer, a luxury fifth slot, or still loses to another damage vocation;
- whether Virtue of Harmony and Virtue of Sustain retain meaningful identities;
- how several nearby vocation bonuses stack on the Monk itself;
- whether Mass Spirit Mend can replace or only supplement a dedicated healer.

For Canary, nominal buff percentages are not enough. Tests need realistic party layouts, movement, off-tanking, proximity loss, buff uptime, stacking, effective healing, and total team damage.

#### 2. A ranged builder is useful only if the ranged loop is coherent

Thousand Fist Blows and the ranged direction were frequently welcomed, especially for mechanics that prevent adjacent attacks. The recurring qualification was that one ranged builder does not establish a complete ranged identity.

Validation should establish:

- target count, area, range, cooldown, damage, and harmony generation;
- whether Monk has an appropriate ranged spender or only a builder;
- auto-attack, weapon-proficiency, and gem interactions;
- how Mystic Repulse fits the rotation;
- whether ranged play is an emergency fallback, boss tool, or sustained alternative;
- hotkey and rotation complexity compared with practical reward.

#### 3. Chain reliability should be resolved before chain damage

Chained Penance and Spiritual Outburst were the most concrete unplanned mechanic family. Authors repeatedly described chains selecting a low-health or out-of-cluster creature, stopping early, or failing to cover a box.

A deterministic contract should define:

- initial cast range and distance between jumps;
- target priority;
- maximum targets;
- whether maximizing targets takes precedence over health;
- tie-breaking and repeat-target rules;
- behavior at walls, line of sight, changing health, and dispersed packs;
- damage progression across the chain.

Until those rules are proven, lower hit counts can be mistaken for a damage-scaling defect.

#### 4. Solo, team, and bossing performance are separate balance questions

The most common answer-3 family combined solo play and damage, while boss/single-target concerns appeared in 40 of 102 parseable answer-3 segments. Players also disagreed on direction: some wanted stronger solo burst, some wanted a clearer support slot, and some wanted rescue/off-tank utility.

A useful Canary comparison must separate:

- solo AoE hunting;
- optimized four- and five-vocation team hunting;
- bosses with adjacency restrictions or target-switch mechanics;
- single-target and PvP pressure;
- experience, profit, supplies, incoming turns, and leech;
- Monk contribution as damage, healing, mitigation, rescue, or control.

The forum does not establish that one global damage multiplier can solve these modes.

#### 5. Harmony and Wheel changes must preserve existing build value

Several replies welcomed a stronger builder/spender identity. Others argued that spenders no longer feel materially stronger, Harmony is under-rewarded, and replacing Augmented Sweeping Takedown removes a useful solo/Ascetic interaction.

Canary validation should compare complete builds rather than isolated nodes:

- base and harmony-scaled builder/spender rotations;
- existing Sweeping Takedown critical or proficiency interactions;
- the new Thousand Fist Blows augment;
- Flurry area versus removed life leech;
- Guiding Presence and Sanctuary opportunity cost;
- access to core-spell gems and the level at which the complete rotation exists.

#### 6. Survivability and elemental access affect viable content

Survivability discussion linked melee exposure, weaker defensive equipment, Energy Ring efficiency, and reduced damage/leech. Elemental proposals focused on making weapons affect spell damage, adding holy access, or avoiding content where physical damage is heavily resisted.

These are separate investigations. Element conversion requires authoritative spell/weapon/imbuement semantics; survivability requires full incoming-damage, kill-time, leech, mana, equipment, and emergency-tool accounting.

### Official clarifications and chronology

- **January 22, post `39563969`:** the community manager published the proposal and requested numbered answers about excitement, fit, and missing changes.
- **January 23, post `39565886`:** the leading developer clarified that Sanctuary's adjacent-target bonus would be permanently active once unlocked. Virtue of Justice would grant a Serene Monk the listed bonuses for nearby party vocations; the Monk counts as being in a party with itself for the fist-fighting bonus.
- **January 29, post `39568241`:** the community manager stated that developers were analyzing the input and would provide updates.

The thread was then closed. These posts clarify proposal intent and feedback handling; they do not prove later release behavior.

### Bounded Canary validation matrix

| Priority | Question | Minimum evidence before a code change |
|---:|---|---|
| 1 | Do Chained Penance and Spiritual Outburst select and reach targets deterministically? | Current Canary path, authoritative target-selection rules, and fixtures for boxes, dispersed packs, health order, walls, ties, and maximum targets. |
| 2 | Does Monk have a coherent ranged builder/spender rotation? | Full spell, harmony, cooldown, range, weapon, proficiency, gem, and boss-scenario comparison. |
| 3 | What measurable party value does Monk add at realistic buff uptime? | Proximity/Serene simulation plus total team damage, mitigation, healing, rescue, and slot-replacement comparisons. |
| 4 | Which mode is underperforming: solo AoE, team hunt, bossing, or single target? | Repeatable level-banded simulations with equipment, targets, supplies, leech, and rotation held constant. |
| 5 | Do harmony spenders justify their setup and Wheel cost? | Complete build comparisons at representative Wheel totals, including the displaced Sweeping Takedown path. |
| 6 | Is a single-target Exeta/rescue tool compatible with Monk's intended role? | Authoritative role evidence, exact target/control rules, abuse cases, cooldown tests, and party scenarios. |
| 7 | Is survivability limited by equipment, damage/leech, Energy Ring, or melee exposure? | Incoming-damage and kill-time decomposition across representative content and level bands. |
| 8 | Should elemental weapons or imbuements affect Monk spells? | Current server path, authoritative element-conversion behavior, protocol/client constraints, and deterministic spell/weapon tests. |

### Supplemental-source conclusion

The complete Monk thread does not support a simple "buff Monk" conclusion. It supports a more specific design hypothesis:

> Players welcomed a clearer support role and a ranged builder, but repeatedly tied Monk viability to reliable chain targeting, a complete builder/spender loop, measurable party-slot value, and separate solo, bossing, survivability, and elemental-access outcomes.

That hypothesis can prioritize bounded tests. It cannot set damage, healing, cooldown, range, target-count, Wheel, or buff values.

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

## What the multi-stage comparison adds

Analyzing only the post-release thread can make the July reaction look like resistance to any nerf. The foundational, proposal, and pre-release threads show a more nuanced sequence:

1. Players welcomed stronger vocation identity, lower unnecessary input, and the promise of new gameplay while immediately requesting complete mechanics and role definitions.
2. The later proposals made potion access, simplification, mitigation, stances, targeting, and vocation-specific trade-offs concrete.
3. Players asked how compensation would preserve AoE scaling, emergency support, survivability, solo access, and practical role identity.
4. Release State narrowed those concerns to specific mechanics, targeting, accessibility, Wheel cost, and role performance.
5. CipSoft intentionally moved to live observation to obtain better data.
6. Live play expanded the concerns into sustain, hunting efficiency, team composition, and economy effects.
7. Numerical corrections on July 7 sharply increased criticism because players perceived cumulative reductions without an equally concrete explanation of targets or trade-offs.

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

## Sorcerer design-thread supplement: January 2026

This supplement adds the complete vocation-specific design discussion that preceded the release-state and release threads:

| Official thread | Thread ID | Displayed results | Collected unique posts | Pages | Observed dates |
|---|---:|---:|---:|---:|---|
| [Vocation Balancing Sorcerer](https://www.tibia.com/forum/?action=thread&threadid=4992267&pagenumber=1) | `4992267` | 533 | 533 | 27 | 2026-01-22–2026-01-29 |

The January corpus is kept separate from the 3,463-post release-phase corpus above. It represents design feedback before test-server and live-server observation, so combining its counts with the later threads would obscure the change in context.

### Collection and composition

- All pages 1–27 returned successfully on 2026-07-23.
- All 533 displayed results were collected with 533 unique post identifiers.
- The corpus contains 450 unique displayed author names and four posts by community manager Liamas.
- Of 529 non-official posts, 389 (73.5%) display a Sorcerer or Master Sorcerer vocation.
- The discussion was broad rather than controlled by a small group: 394 of 449 non-official author names posted once; the ten most active non-official authors contributed 42 posts, or 7.9%.
- Activity was front-loaded: 279 posts (52.3%) appeared on January 22, and 375 (70.4%) appeared during the first two days.

| Displayed author vocation | Posts | Share |
|---|---:|---:|
| Master Sorcerer / Sorcerer | 389 | 73.0% |
| Elite Knight / Knight | 44 | 8.3% |
| Royal Paladin / Paladin | 36 | 6.8% |
| Elder Druid / Druid | 26 | 4.9% |
| Exalted Monk / Monk | 9 | 1.7% |
| None, missing, or other | 29 | 5.4% |

Displayed vocation and level are profile metadata at collection time, not verified posting-time identity or experience. They are useful for describing the corpus, not for weighting an argument.

### Theme breadth

The same post-level keyword-family method used above was applied to the 529 non-official posts. Themes overlap: one post can discuss beams, solo hunting, targeting, and chain spells. Rendered quotations remain in the text and can increase a theme count when a proposal is repeated or challenged; counts therefore measure discussion breadth and engagement, not independent votes.

| Theme family | Posts | Share of non-official posts |
|---|---:|---:|
| Damage, DPS, or spell power | 283 | 53.5% |
| Solo versus team hunting | 226 | 42.7% |
| Beam spells and Beam Mastery | 216 | 40.8% |
| UH/IH and healing allies | 189 | 35.7% |
| Elemental stances and conversion | 158 | 29.9% |
| Targeting, aiming, latency, or positioning | 133 | 25.1% |
| Wands and mana generation | 126 | 23.8% |
| Chain-spell requests | 121 | 22.9% |
| Barrier, mana shield, or survivability | 120 | 22.7% |
| Ultimate-spell or group cooldown | 116 | 21.9% |
| Utility stances and debuffs | 107 | 20.2% |
| Lightning and strike spells | 98 | 18.5% |
| Wheel of Destiny and augments | 94 | 17.8% |
| PvP utility | 72 | 13.6% |
| Repeated blast | 68 | 12.9% |
| Exclusive death/area-rune requests | 32 | 6.0% |

A coarse critical-language marker matched 223 of 529 non-official posts (42.2%). This does not mean that 42.2% opposed the package. Praise and criticism frequently coexist in the same post: players often welcomed the direction of elemental and utility stances while objecting to beam execution, party-role losses, or insufficient information.

### What players broadly welcomed

#### Elemental identity

Elemental stances were the clearest identity success. Players liked the ability to use a fuller spell rotation where the natural elements of existing spells would otherwise be resisted. The recurring questions were operational rather than a rejection of the concept:

- whether elemental and utility stances could coexist;
- whether a stance could be disabled or changed without penalty;
- which spell triggers conversion and how long conversion persists;
- whether runes, ultimate spells, Wheel bonuses, Momentum, and equipment interact with conversion;
- whether death had enough native spells to make a death stance practical;
- how much matching-element power a stance actually grants.

For Canary, elemental conversion should be treated as a deterministic state machine, not only as a damage modifier.

#### Lower input load

Turning Sap Strength and Expose Weakness into automatically applied utility stances was repeatedly praised for removing maintenance inputs. The remaining design question was whether the debuff values and party contribution would be strong enough to preserve a meaningful Sorcerer slot after UH removal.

#### A survivability mechanism that preserves fragility

Many players welcomed a barrier that mitigates one-shots without turning a mage into a tank. The official concept converts lethal overkill into mana loss at an 8:1 multiplier and still kills the player when mana is insufficient. A smaller but important counter-theme warned that an always-available effect could become a zero-cooldown Gift of Life for very large mana pools.

The disagreement was therefore mainly about trigger rules, repeatability, and scaling—not the need to address mage one-shots.

### Main unresolved design conflicts

#### 1. Beam execution versus solo accessibility

Beams were the strongest concrete objection. Of the 529 non-official posts:

- 216 discussed beams;
- 119 discussed both beams and solo/team hunting;
- 82 discussed both beams and targeting, latency, aiming, or positioning;
- 88 discussed both beams and chain spells.

Players did not uniformly demand that beams disappear. Some defended them as a skill-rewarding spell shape. The common acceptance condition was that correct positioning and tracking must produce an observable advantage over a rune turn.

The dominant alternative was a chain spell, especially chain lightning or a death chain. Chain behavior was framed as:

- more reliable while kiting;
- less sensitive to latency and rapid target movement;
- usable without an EK holding a stable box;
- a way to give Lightning a distinct purpose;
- a bridge between solo and team play.

This creates a testable design question: **what measurable performance premium compensates for beam miss risk, limited geometry, and positional cost?**

#### 2. UH removal and party-role compensation

UH/IH or healing allies appeared in 189 posts. The discussion was polarized:

- identity-focused players welcomed removing a healing obligation from the destructive mage;
- party-focused players described UH as necessary sustain in high-level hunts, boss rooms, duos, three-vocation teams, and teams without an Elder Druid;
- several players feared that Monk healing and utility would make the Sorcerer easier to replace;
- compromise proposals included party-only UH, boss-room UH, a long-cooldown Sorcerer heal, or stronger offensive/debuff compensation.

The corpus does not support treating UH removal as an isolated rune permission. It changes viable team compositions and the value proposition of the Sorcerer slot. Validation needs three-, four-, and five-vocation scenarios plus boss encounters—not only a full standard party.

#### 3. Numerical buffs to unused spells

Lightning and strong/ultimate strikes appeared in 98 posts. A repeated objection was that higher base power and range do not correct the reasons these spells are skipped:

- they compete with AoE turns;
- they lack a distinct tactical purpose;
- their damage may not cover target-count loss;
- Lightning overlaps conceptually with strike spells;
- ultimate spells retain a long group cooldown.

Targeted lexical checks found at least 27 posts explicitly calling Lightning or strike spells useless, obsolete, never used, or otherwise irrelevant, and 35 posts explicitly linking ultimate spells to a four-second/global/group-cooldown complaint. These are lower-bound phrase matches, not exhaustive vote counts.

#### 4. Repeated blast must work with moving combat

Repeated blast appeared in 68 posts. Players asked for its element, area, range, targeting mode, cooldown, Wheel location, damage split, charm behavior, and interaction with stances. The most important gameplay concern was that a second hit two seconds later may land behind a solo mage who is continuously kiting.

The January 23 official clarification stated that:

- the first blast carries most of the damage;
- the second blast deals reduced damage;
- the second blast cannot trigger charms;
- the second hit is intended to reward skillful use.

That clarification defines an implementation constraint but not a complete behavior contract. Position anchoring, target anchoring, retargeting, floor/door behavior, and cast-mode semantics still require proof.

#### 5. Wand changes were viewed as useful but too generic

Wands appeared in 126 posts. Players generally accepted removing their mana cost and adding mana generation/range, but many considered the result too small or too similar to Druid rods. Forty-eight lower-bound phrase matches explicitly connected wands/rods with AoE, area damage, Explosion, or GFB-like behavior.

Other proposals included stance-dependent elements, debuff stacks, proficiency effects, and different role-specific wand/rod identities. These are design requests, not Real Tibia parity evidence.

#### 6. PvP identity remained unresolved

PvP utility appeared in 72 posts. Recurring requests included:

- Sorcerer-exclusive Sudden Death or a death-area rune;
- a control effect comparable in role value, but not necessarily identical, to Paralyze or Wild Growth;
- push/repel, anti-heal, or other offensive utility;
- burst tools that reinforce the destructive-mage identity.

The forum establishes demand for a legible PvP role. It does not establish which mechanic or value is balanced.

### Official clarifications in the thread

The four community-manager posts form a short official chronology:

1. **January 22, opening post:** proposed elemental and utility stances, repeated blast, spell and Wheel changes, the lethal-overkill barrier, wand mana generation/range, and loss of UH-on-allies.
2. **January 22, amendment:** confirmed that the barrier remained in the plan and restated the 8:1 overkill-to-mana rule.
3. **January 23, developer clarification:** stated that repeated blast is front-loaded; its reduced second hit cannot trigger charms; Beam Mastery makes beams three squares wide with reduced damage on the outer squares.
4. **January 29, closure response:** said that developers had begun analysing the feedback.

These statements describe the proposal at that date. They are not proof of current live values or Canary behavior.

### Cross-thread warning-to-outcome map

| January design concern | Later release-phase feedback documented above |
|---|---|
| Beam positioning needs a visible skill premium | Players later described outer beams as too weak for their positional effort and objected to the combined Beam Mastery/base-damage reductions. |
| Repeated blast needs clear targeting and moving-combat behavior | Death Echo was later considered interesting but execution-heavy, with cursor/crosshair and position issues. |
| Elemental conversion needs explicit cooldown and rotation rules | Live feedback later reported unintuitive interactions between desired element, Momentum, and cooldown reductions. |
| Barrier must balance one-shot protection against large mana pools | The live system appeared as Mana Buffer, and its multiplier was later increased from 8 to 10 during numerical corrections. |
| Core functionality should not depend on deep Wheel investment | Mid-level Sorcerers later described the Wheel cost of the intended beam/elemental playstyle as excessive. |

The January thread therefore strengthens the release-phase conclusion: several live controversies were identifiable as design-contract questions before testing, not only as reactions to later nerfs.

### Sorcerer validation contract for Canary

Before implementing any Sorcerer adjustment inspired by these threads:

1. **Elemental conversion:** specify activation, exclusivity, trigger spell, consumed spell, duration, logout/death behavior, rune behavior, cooldown interaction, Wheel interaction, and damage-element attribution.
2. **Beams:** compare expected damage and hit rate with rune/wave alternatives in solo kiting, stable team boxes, dispersed targets, and latency-sensitive movement.
3. **Repeated blast / Death Echo:** test first/second-hit damage, area growth, anchor behavior, cast modes, target loss, movement between hits, charm eligibility, doors/floors, and cooldown.
4. **Barrier / Mana Buffer:** test the exact lethal threshold, overkill calculation, exact and insufficient mana, consecutive lethal hits, cooldown/rearm rules, mana-shield interaction, PvP, and very large mana pools.
5. **UH removal:** model duos, three-vocation teams, standard four-vocation teams, five-vocation teams, and boss rooms; measure both survivability and the opportunity cost of losing a damage turn.
6. **Wands:** separate verified Real Tibia behavior from community AoE/proficiency proposals.
7. **PvP utility:** treat any exclusive rune or control mechanic as a deliberate Canary design decision unless current authoritative Real Tibia evidence is pinned.
8. **Difficulty premium:** define the expected benefit of correct beam/stance/blast execution over a simpler fallback and add a deterministic test or simulation that can falsify it.

The forum should prioritize these investigations. It should not determine formulas or authorize copying a proposed value.

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

Across 6,592 accessible posts in six primary official corpora, plus the bounded Druid page-one sample, the community consistently supports stronger vocation identity, new rotations, useful defensive choice, and lower unnecessary input complexity. The main rejection concerns incomplete functional access, unclear role trade-offs, late Wheel availability, and numerical packages whose combined risk or complexity appears greater than their practical reward.

For Canary, the durable lesson is methodological: use the forum to identify high-value validation questions, then prove each mechanic independently. Community volume can prioritize investigation; it cannot replace authoritative values, current source inspection, or runtime evidence.
