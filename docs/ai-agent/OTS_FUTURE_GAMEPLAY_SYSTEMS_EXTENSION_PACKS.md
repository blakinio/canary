# OTS Future Gameplay Systems — Integrated Extension Packs

Status: approved future-design integration record

This document promotes three already-merged detailed design packages into the future-gameplay roadmap without replacing their full specifications. It is a concise product index, not implementation proof.

## Practical change-kind labels

- `FEATURE`: a new capability, progression layer or service.
- `UPGRADE`: an extension or redesign of an existing Tibia/Canary/OTClient foundation.
- `FIX`: a safeguard, migration rule, anti-abuse control or correction of an identified progression/UX failure.

The authoritative provenance classification remains `ORIGIN` + `TYPE` in `docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md`.

---

# 36. Charm, Bestiary and Drome Mastery

`USER-DIRECTION`

Detailed design:

`docs/ai-agent/OTS_CHARM_BESTIARY_AND_DROME_MASTERY.md`

Promoted proposal entries:

- **95 — Bestiary staged Charm Point rewards — `UPGRADE`**: distribute the existing total Charm Point reward across Bestiary milestones while preserving full completion as the largest and most valuable milestone.
- **96 — Bestiary knowledge-gated effective Charm levels — `UPGRADE`**: a globally owned Charm may be stronger, but its effective level against one creature is capped by the player's knowledge of that creature.
- **97 — Charm Level 3 Mastery and Level 4 Grandmaster — `UPGRADE`**: create bounded qualitative capstones instead of unlimited percentage growth; Level 4 remains optional endgame specialization.
- **98 — Creature Family Mastery — `FEATURE`**: full Bestiary completion contributes to stable family-level mastery and Level 4 eligibility for fully learned members of that family.
- **99 — Persistent Charm assignments and loadouts — `UPGRADE`**: remember preferred creature assignments and allow bounded hunting-ground loadouts instead of repetitive manual reassignment.
- **100 — Drome Charm amplifiers and optional Grandmaster catalysts — `UPGRADE`**: Drome rewards amplify legitimately unlocked Charm power and must not bypass Bestiary or family-mastery gates.

Required boundaries:

- do not create unlimited vertical Charm growth;
- do not allow potions to bypass creature knowledge;
- do not revoke earned family mastery merely because future updates add creatures;
- preserve strategic limits on active assignments;
- exact Charm effects, costs, thresholds and rollout levels remain `OPEN`.

---

# 37. Quest Journal, Quest Progression, Postal Network and Market Logistics

`USER-DIRECTION`

Detailed design:

`docs/ai-agent/OTS_QUEST_JOURNAL_POSTAL_AND_MARKET_LOGISTICS.md`

Promoted proposal entries:

- **101 — Quest Journal 2.0 and dependency graph — `UPGRADE`**: represent campaigns, chains, quests, missions and objectives as a searchable dependency graph rather than only a flat legacy list.
- **102 — Current Objective and blocker explanation — `FIX`**: show the exact current step and explain missing prerequisite quests, accesses, items, NPC interactions or party incompatibilities.
- **103 — Party Quest Sync — `FEATURE`**: show party-stage compatibility and the earliest missing prerequisite without granting skipped quest progress.
- **104 — Quest Renown / Adventure Points — `FEATURE`**: add long-term exploration and completion progression focused on convenience, identity, titles, cosmetics and world services rather than unrestricted combat power.
- **105 — Region Mastery — `FEATURE`**: connect related regional quest lines to durable exploration progress and bounded regional rewards.
- **106 — Legacy quest reward modernization and bounded XP scaling — `UPGRADE`**: preserve iconic physical rewards while adding modern progression value and carefully bounded one-time XP where old fixed rewards became irrelevant.
- **107 — Postman Quest modernization pilot — `UPGRADE`**: use the Postman chain as a representative pilot where long quest effort unlocks meaningful postal rank and service privileges.
- **108 — Postal Network 2.0 — `FEATURE`**: support item delivery, own-character transfers, COD, insurance, tracking, service tiers, guild/house mailboxes and depot delivery under explicit safety rules.
- **109 — Global Market plus Local Logistics — `UPGRADE`**: preserve one searchable liquid market while retaining stock origin, optional pickup and postal delivery between locations.
- **110 — Consolidated market delivery — `FEATURE`**: combine purchases from several locations into one bounded delivery to a selected depot or mailbox.

Existing proposal reused rather than duplicated:

- account-wide quest progression remains classification entry **4**; this package provides quest-by-quest classification and UX around that direction, not a second account-quest system.

Required boundaries:

- do not make every quest account-wide;
- do not grant skipped progression through Party Quest Sync;
- do not delete iconic legacy rewards by default;
- do not fully fragment the market into low-liquidity city markets by default;
- exact delivery timing, insurance, fees, limits and quest classifications remain `OPEN`.

---

# 38. Forge Slot Mastery, Item Enhancement and Equipment Proficiency

`USER-DIRECTION`

Detailed design:

`docs/ai-agent/OTS_FORGE_SLOT_ITEM_ENHANCEMENT_AND_EQUIPMENT_PROFICIENCY.md`

The architecture deliberately separates permanent slot progression, numerical item development and build-oriented perk selection.

Promoted proposal entries:

- **111 — Forge Slot Mastery — `UPGRADE`**: move durable Forge-style tier progression to the character's equipment slot so replacing an item does not erase months or years of slot investment.
- **112 — Item Enhancement `+N` — `FEATURE`**: improve bounded intrinsic statistics of one concrete item instance without defining the whole build or granting every possible bonus.
- **113 — Equipment Proficiency — `FEATURE`**: add item/category-specific perk and specialization choices beyond weapons while keeping official Weapon Proficiency separate and authoritative for its own domain.
- **114 — Item Classification as progression ceiling — `UPGRADE`**: use existing item classification to constrain maximum enhancement and proficiency depth instead of inventing a parallel rarity system.
- **115 — Equipment proficiency branches and qualitative capstones — `FEATURE`**: support opportunity-cost paths such as Fortification, Retaliation or Sustain, with bounded mastery effects rather than unrestricted stat stacking.
- **116 — Controlled Enhancement RNG and pity — `FIX`**: allow bounded randomness at higher levels while guaranteeing that extreme bad luck has a ceiling and avoiding catastrophic item destruction.
- **117 — Controlled duplicate-item sink — `UPGRADE`**: let duplicates contribute to selected high-end progression without requiring repeated destruction of many ultra-rare best-in-slot items.
- **118 — Enhancement Salvage and equipment-replacement protection — `FIX`**: allow partial recovery of item-specific investment when a stronger replacement arrives; changing equipment has a cost but does not delete all progress.
- **119 — Existing tier migration contract — `FIX`**: audit and migrate live tiered items without duplicating permanent power, silently deleting investment or creating cross-character exploits.
- **120 — Controlled Retaliation / reflect safety — `FIX`**: prefer proc, cooldown and output-cap models over unrestricted percentage reflection that scales dangerously with attacker count.

Required boundaries:

- Forge Slot Mastery, Item Enhancement, Equipment Proficiency and Imbuements remain distinct responsibilities;
- Equipment Proficiency must not be described as a replacement for official Weapon Proficiency;
- all illustrative level caps, success rates, materials, costs and branch values remain non-final;
- total power must be simulated together with Forge effects, Weapon Proficiency, Imbuements, Wheel, Charms, Prey, Bounty and vocation balance;
- migration requires a separate inventory/economy audit before implementation.

---

## Integration status

- entries **95-100** map to the Charm/Bestiary/Drome design;
- entries **101-110** map to the Quest/Postal/Market Logistics design;
- entries **111-120** map to the Forge Slot/Enhancement/Equipment Proficiency design;
- all three full design files remain authoritative for detailed requirements and open questions;
- the classification index remains the authoritative source for `ORIGIN` and `TYPE`.
