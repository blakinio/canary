# OTS Gem Atelier and Gem Progression Review

## Purpose

Durable review direction for the official Tibia Gem Atelier, Fragment Workshop and gem progression systems, and for deciding how those systems should interact with the future OTS vocation/class balance, itemization, build, Wheel of Destiny and economy layers.

This document records a required audit/review scope. It is not proof that the current Canary fork or OTClient already implements every official mechanic described below.

## Evidence labels

- `USER-DIRECTION`: explicitly requested or approved by the user.
- `OFFICIAL-BASELINE`: verified from current official Tibia Game Guides and official Tibia news history during the 2026-07-23 review.
- `DESIGN-DIRECTION`: integration direction selected as useful, but not yet an implementation contract.
- `OPEN`: requires repository audit, current parity verification, simulation or balance analysis.

---

# 1. Review mandate

`USER-DIRECTION`

The full gem system must be reviewed as one connected progression/build system, not only as individual gem bonuses.

The audit must cover at least:

- Gem Atelier;
- gem acquisition;
- vocation-specific gem families;
- Lesser, Regular and Greater gems;
- revealing and character binding;
- Basic and Supreme Mods;
- random mod assignment;
- Wheel domains and domain affinity;
- domain switching and its gold cost;
- Wheel vessels;
- Vessel Resonance;
- gem placement/removal;
- gem locking;
- dismantling;
- Fragment Workshop;
- lesser and greater fragments;
- mod Grade I-IV progression;
- gold/resource costs;
- interaction with Revelation Perks / Revelation Mastery;
- interaction with vocation/class identity and balance;
- interaction with Build Presets, Build Impact Calculator and Training Arena;
- economy, RNG, progression and long-term sink behavior.

The objective is to decide what should remain parity-compatible, what should be rebalanced, and what should be integrated with our broader OTS progression architecture.

---

# 2. Current official baseline to preserve during analysis

`OFFICIAL-BASELINE`

Current official Tibia documentation describes Gem Atelier as a Wheel of Destiny subsystem.

## 2.1 Gem acquisition and vocation ownership

The current official baseline includes gems obtainable from fiendish creatures and selected bosses, with official release history also documenting influenced/fiendish creatures and Archfoe boss sources.

Gems are vocation-linked. Current official Game Guides list five families:

- Guardian gems for knights;
- Marksman gems for paladins;
- Spiritualist gems for monks;
- Sage gems for sorcerers;
- Mystic gems for druids.

Characters can reveal only gems belonging to their vocation.

Unrevealed gems can be traded. Revealing binds the resulting gem progression to the character and removes normal tradeability.

`OPEN`

Exact current drop-source tables and probabilities must be reverified immediately before implementation or parity work.

## 2.2 Gem sizes and mods

The current system uses:

- Lesser gems;
- Regular gems;
- Greater gems.

Current official documentation describes one, two or three mods respectively, while release documentation distinguishes Basic Mods from the Supreme Mod available on Greater gems.

Mods can affect areas such as:

- character stats;
- elemental or other defensive properties;
- specific spell augments;
- Revelation-related progression;
- other vocation-specific build effects.

The exact current mod catalogue and values are intentionally not frozen in this roadmap because official balancing has continued to change them.

## 2.3 Domains

A revealed gem belongs to one of the four Wheel domains.

Official behavior includes the ability to change domain affinity by moving the gem to the next domain in clockwise order for a gold fee.

This makes domain compatibility part of the build-selection cost and not merely a visual property.

## 2.4 Vessels and Vessel Resonance

Gems are placed into Wheel vessels.

The number of active mods depends on Vessel Resonance progression in the relevant domain.

The current official model allows progressive activation of gem mods as corresponding Vessel Resonance capability is unlocked.

A Greater gem therefore does not automatically imply that every contained mod is active in every vessel configuration.

## 2.5 Locking and dismantling

The current Gem Atelier supports locking gems to protect them from destructive or configuration-changing actions.

Unneeded gems can be dismantled into fragments subject to the system's restrictions.

## 2.6 Fragment Workshop

`OFFICIAL-BASELINE`

The Fragment Workshop complements Gem Atelier and upgrades gem mods from Grade I through Grade IV.

The official system uses:

- lesser fragments for Basic Mods;
- greater fragments for Supreme Mods;
- gold plus fragments as upgrade costs.

Fragments can be obtained through smashing unrevealed gems or dismantling revealed gems, and official documentation states that fragments are tradeable and may also be obtained from jewelry-shop NPCs.

Official 2024 documentation also describes grade progression as a mod-level progression that can affect the same mod wherever it appears, subject to ordering/activation constraints on the gem and Vessel Resonance.

This is important for our audit because the Fragment Workshop is not merely an item-upgrade screen; it creates account/character-wide progression effects for repeated mod types and therefore has major balance and economy consequences.

## 2.7 Ongoing balance surface

`OFFICIAL-BASELINE`

Gem Atelier and Fragment Workshop remain actively maintained systems. Official 2025-2026 fixes and balance changes include Gem Atelier UI fixes, vocation-specific gem/workshop corrections and further changes to gem-related mitigation values.

Therefore exact gem values must be treated as time-sensitive and reverified from current official sources before parity or balance implementation.

---

# 3. Required Canary / OTClient audit

`USER-DIRECTION`

Before designing changes, perform a focused current-fork audit answering:

1. Does Canary currently implement Gem Atelier state at all?
2. Does it implement Wheel vessels and Vessel Resonance?
3. Are gem objects, revealed-gem records and mod definitions persisted?
4. Are vocation-specific gem families represented, including Monk/Spiritualist gems?
5. Is domain affinity persisted and switchable?
6. Are reveal costs and domain-switch costs implemented?
7. Is locking supported?
8. Is dismantling supported?
9. Does Fragment Workshop exist?
10. Are fragment item types, acquisition and tradeability implemented?
11. Are Grade I-IV mod upgrades implemented?
12. Is mod-grade progression character-wide or gem-instance-specific in the current fork?
13. Are Vessel Resonance and mod-grade activation constraints enforced server-side?
14. Are Gem Atelier actions exposed through protocol/client support?
15. Does the maintained OTClient have the necessary UI/protocol implementation?
16. Are current official 2026 gem and Monk changes represented?

`OPEN`

A narrow repository code search performed during this design pass did not return direct Gem Atelier/Wheel matches. This is insufficient evidence to claim the system is absent. A dedicated implementation audit remains required.

---

# 4. Balance review

`USER-DIRECTION`

Gem balance must become part of the Vocation/Class Identity, Roles and Balance Framework.

The review should measure how gems alter:

- sustained damage;
- burst damage;
- healing;
- survivability;
- mitigation;
- elemental resistance;
- resource efficiency;
- mobility;
- utility/control;
- Revelation Perk access/effectiveness;
- individual spell performance.

A vocation must not be balanced only from base spells/items while Gem Atelier creates a substantially different endgame power profile.

## 4.1 Class identity guardrail

`DESIGN-DIRECTION`

Gem choices should reinforce or diversify a vocation's identity without allowing every vocation to erase all intended weaknesses simultaneously.

Examples of questions to answer:

- Does one gem combination become mandatory for a vocation?
- Can one class gain excessive damage, sustain and defense at the same time?
- Do Supreme Mods create one dominant spell/build path?
- Are some domains effectively dead because their gem combinations are inferior?
- Does Revelation Mastery create mandatory domain routing?
- Does a gem disproportionately improve one vocation relative to another?

## 4.2 Context-separated analysis

Measure gem impact separately for:

- ordinary PvE hunts;
- high-density AoE hunts;
- bosses;
- solo play;
- party play;
- PvP where relevant.

Do not use one global DPS metric as the only balancing criterion.

---

# 5. Build-system integration

`DESIGN-DIRECTION`

Gem Atelier should integrate with the future Itemization & Build System 2.0 rather than remain an opaque separate screen.

## 5.1 Build Impact Calculator

A saved or candidate build should expose the contribution of:

- equipped items;
- Forge/item progression;
- Imbuements;
- Skill Wheel;
- active gems;
- active gem mods and grades;
- Revelation Perks;
- classic skills;
- Weapon/Equipment Proficiency where applicable.

The UI should distinguish:

`base build`
+
`gem contribution`
+
`Wheel/Revelation contribution`
+
`other progression layers`

so players can understand what a gem actually changes.

## 5.2 Build Presets

Evaluate whether Build Presets should save/reference:

- gem placement;
- Wheel domain configuration;
- active vessel configuration;
- other legal Gem Atelier state.

Preset switching must respect any server-authoritative restrictions and must not duplicate or destroy character-bound gem state.

## 5.3 Training Arena

Training Arena should allow A/B testing of gem builds.

Example:

`Build A: current Wheel + gems`

versus

`Build B: alternate gem/domain configuration`

with metrics for damage, healing, mitigation, resource use and survival.

This gives practical proof of gem impact instead of relying only on tooltip interpretation.

---

# 6. RNG and progression quality review

`USER-DIRECTION`

The audit must explicitly evaluate whether the random reveal model creates healthy long-term progression or excessive frustration.

Questions:

- How many gem drops/reveals are typically required to reach a competitive configuration?
- How much bad-roll waste is produced?
- Does binding after reveal create meaningful commitment or merely inventory/progression frustration?
- Are duplicate/unwanted gems sufficiently useful through dismantling?
- Is domain switching a healthy gold sink or repetitive friction?
- Does mod upgrading reduce RNG frustration enough?
- Does the system disproportionately punish new/returning players?
- Does endgame competition require an unrealistic number of random reveals?

`DESIGN-DIRECTION`

Do not automatically remove RNG. Prefer to identify whether a bounded improvement mechanism, reroll/protection path, targeted progression or stronger dismantle value is needed only after economy and acquisition data are measured.

No pity/reroll mechanic is approved by this document yet.

---

# 7. Economy review

`USER-DIRECTION`

Gem Atelier and Fragment Workshop must be included in the Economy Sink Framework.

Measure at least:

- gold removed by gem reveals;
- gold removed by domain switching;
- gold removed by Grade II-IV upgrades;
- fragment generation and consumption;
- market value and liquidity of unrevealed gems;
- market value and liquidity of fragments;
- impact of NPC fragment supply;
- effect of fiendish/boss farming on gem supply;
- value destruction/creation through dismantling;
- whether the system concentrates excessive wealth advantages.

The system can be a strong gold/material sink, but sink strength must not be achieved by making basic build participation unreasonably inaccessible.

---

# 8. Interaction with proposed equipment progression

`OPEN`

Open PR #794 currently proposes a separate Forge-slot / Item Enhancement / Equipment Proficiency architecture.

Gem Atelier review must not silently duplicate or conflict with that proposal.

Before implementation, explicitly map responsibilities:

- Forge/slot mastery -> equipment progression/effects;
- Item Enhancement -> bounded intrinsic item growth;
- Equipment Proficiency -> item/slot specialization;
- Imbuement System 2.0 -> charged active channels and elemental attunement;
- Gem Atelier -> Wheel/vocation-oriented build modifiers;
- Fragment Workshop -> gem-mod progression;
- Skill Wheel/Revelation -> vocation build architecture.

The final architecture should avoid five parallel systems all granting interchangeable generic damage/defense bonuses with no distinct purpose.

---

# 9. Recommended audit output

A later bounded Gem Atelier audit should produce:

1. current official 2026 behavior matrix;
2. current Canary support matrix;
3. current OTClient support matrix;
4. persistence/data model map;
5. protocol/UI dependency map;
6. gem/mod/vessel/domain/fragment lifecycle diagram;
7. per-vocation gem/mod catalogue;
8. economy flow and sink analysis;
9. RNG acquisition/frustration analysis;
10. build-impact and class-balance analysis;
11. compatibility analysis with Wheel, Imbuement 2.0 and PR #794 equipment progression;
12. recommended preserve/change/remove/add decisions;
13. phased implementation plan only after the evidence above is complete.

---

# 10. Classification and implementation policy

The underlying Gem Atelier, Fragment Workshop, gem sizes, vocation gem families, domains, vessels, Vessel Resonance, fragments and Grade I-IV mod progression are official Tibia foundations verified from current official documentation.

Our current proposal is therefore primarily a **parity and design audit**, not a claim that we invented the gem system.

Any later custom changes must be classified separately and must not be described as official Tibia behavior.

Quantitative values are time-sensitive and must be reverified before implementation.
