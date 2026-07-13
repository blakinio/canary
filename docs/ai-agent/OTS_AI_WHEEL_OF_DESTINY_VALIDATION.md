# OTS AI Wheel of Destiny Validation — plan, evidence, findings and handoff

> **Status:** validation phase complete; confirmed fixes in PR #220; missing systems and runtime proofs explicitly tracked
> **Started:** 2026-07-12
> **Last updated:** 2026-07-12
> **Repository:** `blakinio/canary`
> **Integrated via:** PR #220 into `main` (`35ff51ac022e36d215db9d0fa86053b326a0bdf0`)
> **Reference process:** `docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md`
> **Primary gameplay reference:** `https://tibia.fandom.com/wiki/Wheel_of_Destiny`
> **Rule:** update this file whenever Wheel of Destiny code, data, tests, or validation conclusions change.

---

## 1. Goal

Validate the complete Wheel of Destiny implementation in Canary against the currently documented Tibia mechanics, without assuming that code presence proves gameplay correctness.

The validation covers:

- eligibility and promotion-point sources;
- wheel topology, slice costs, adjacency, domain totals, and Revelation thresholds;
- Dedication, Conviction, Revelation, and vocation-specific effects;
- Wheel presets and temple-only reset/reallocation rules;
- protocol serialization and client interaction;
- database/KV persistence and migration safety;
- Gem Atelier, gem capacity, affinity, vessels, resonances, mod activation, grades, fragments, and costs;
- spell, combat, stat, resistance, leech, cooldown, and passive-effect integration;
- reload/login/death/vocation-change consistency;
- automated static, unit, integration, and gameplay regression tests.

This document is intentionally separate from the world/map validation log because Wheel of Destiny is primarily a player-state, protocol, persistence, and combat subsystem.

---

## 2. Validation method

Each mechanic receives one of these evidence levels:

1. **Definition found** — enum/config/table exists.
2. **Runtime path found** — value is consumed by active production code.
3. **Persistence proven** — save/load and migration behavior are traced.
4. **Protocol proven** — server/client message path and validation are traced.
5. **Behavior proven** — deterministic automated test confirms the effect.
6. **Gameplay proven** — end-to-end scenario confirms observable behavior.

A mechanic is not marked compliant from levels 1–2 alone.

Disposition labels:

- `confirmed`
- `partial`
- `missing`
- `incorrect`
- `unverified`
- `blocked-by-reference`
- `needs-runtime-test`

---

## 3. External baseline captured on 2026-07-12

The referenced TibiaWiki page currently states:

- one promotion point per level after level 50;
- additional sources include up to 50 Promotion Scroll points, 10 Way of the Monk points, 50 Hunting Task Shop points, and 69 points from fully upgraded Basic/Supreme Mods;
- the Wheel has four domains and 36 slices;
- the strongest outer benefit requires a 575-point branch path;
- Revelation stages unlock at 250, 500, and 1000 points invested in a domain;
- point reallocation is free but restricted to temples;
- Wheel use requires a promoted character on a Premium account;
- revealed-gem capacity is 225;
- Lesser/Regular/Greater gems have 1/2/3 mod slots respectively;
- matching enabled Vessel Resonances activate subsequent gem slots;
- full resonance grants +1/+1/+2 damage and healing for Lesser/Regular/Greater gems;
- reveal costs are 125,000 / 1,000,000 / 6,000,000 gold;
- affinity rotation costs are 125,000 / 250,000 / 500,000 gold;
- Grade II/III/IV require 5/15/30 fragments;
- Basic upgrade gold costs are 2,000,000 / 5,000,000 / 30,000,000;
- Supreme upgrade gold costs are 5,000,000 / 12,500,000 / 75,000,000;
- each mod upgraded fully to Grade IV grants one permanent promotion point.

These values are a working comparison baseline, not yet a declaration that every detail is authoritative or unchanged. Official CipSoft sources and captured protocol behavior supersede community documentation when available.

### 3.1. Current 15.25 balance baseline

The June 16, 2026 update additionally requires:

- Gift of Life to restore 20/25/30% maximum mana as well as health;
- Dedication mitigation to grant 0.075% per Promotion Point;
- Gem mitigation to scale as 20/22/24/30% at Grades I/II/III/IV;
- Ballistic Mastery bow attacks/spells to gain 4% physical and holy pierce;
- Healing Link to transfer 25% healing;
- Battle Healing to increase healing spells by 10%, tripled while a shield is equipped, with no challenge-triggered heal;
- Blessing of the Grove to add 5/7.5/10% below 60% health, doubled below 30%, and to enable critical healing;
- multiple existing augments to use new values/order/area/cooldown behavior;
- new vocation stances and replacement spells that do not currently exist in Canary.

The missing new spells/stances are tracked separately instead of being emulated by renaming old Wheel entries.

---

## 4. Repository surface discovered

Active subsystem files located so far:

- `src/io/io_wheel.hpp`
- `src/io/io_wheel.cpp`
- `src/creatures/players/components/wheel/player_wheel.hpp`
- `src/creatures/players/components/wheel/player_wheel.cpp`
- `src/creatures/players/components/wheel/wheel_definitions.hpp`
- `src/creatures/players/components/wheel/wheel_gems.hpp`
- `src/creatures/players/components/wheel/wheel_gems.cpp`
- `src/creatures/players/components/wheel/wheel_spells.hpp`
- `src/enums/player_wheel.hpp`
- `src/server/network/protocol/protocolgame.hpp`
- `src/server/network/protocol/protocolgame.cpp`
- `data/scripts/actions/items/wheel_scrolls.lua`
- `data/modules/scripts/taskboard/taskboard.lua`
- `data-otservbr-global/migrations/32.lua`
- `data-otservbr-global/migrations/33.lua`
- `schema.sql`
- login-data, vocation, combat, spell, Lua binding, and player integration files.

Confirmed definitions and active paths:

- 36 wheel slots are enumerated;
- Revelation thresholds are represented as 250, 500, and 1000;
- Knight, Paladin, Druid, Sorcerer, and Monk Revelation effects are represented;
- Wheel bonuses include stats, skills, leech, mitigation, damage/healing, instant effects, stages, avatars, Vessel Resonances, momentum, and spell unlocks/boosts;
- five Promotion Scroll definitions provide 3 + 5 + 9 + 13 + 20 = 50 points;
- level points use `(level - 50) * pointsPerLevel` with the default one point per level;
- server-side eligibility requires level 51+, Premium, promotion, and a non-zero vocation;
- slot allocation is persisted in `player_wheeldata`; migration 33 and `schema.sql` provide a primary key on `player_id`;
- scrolls, gems, active gems, and mod grades are persisted through the player KV tree.

---

## 5. Validation matrix

| Area | Status | Current evidence | Next proof required |
|---|---|---|---|
| Promotion points from levels | partial | formula handles levels 1–50 without unsigned wrap; unit coverage and PR #220 CI passed | runtime login test |
| Promotion Scroll points | confirmed | five unique scrolls total 50; KV persistence traced | Lua/runtime use test |
| Way of the Monk points | partial | storage/config path exists and is included in extra points | quest completion and protocol test |
| Hunting Task Shop points | missing | current Taskboard module explicitly sends an empty shop shim | implement Taskboard reward/shop persistence |
| Grade IV permanent points | partial | accounting consolidated into `getExtraPoints()`; load order fixed; PR #220 CI passed | protocol capture and Grade IV round trip |
| 36-slice topology | partial | duplicated green edge corrected by quadrant symmetry; complete allocation is validated before commit | exhaustive topology matrix test |
| Revelation thresholds | partial | 250/500/1000 definitions and runtime stages exist | domain totals and effect tests |
| Temple-only reallocation | partial | proposed decreases are now rejected server-side unless `getOptions()` confirms temple access | forged-packet integration test |
| Premium/promoted eligibility | confirmed | `canOpenWheel()` rejects unpromoted, non-Premium, level <= 50, and vocation-none players | protocol rejection test |
| Vocation wheels | partial | effects for five vocations are represented | verify every slice/effect/value per vocation |
| Dedication perks | partial | current 15.25 mitigation is now 0.075% per Promotion Point; remaining values require matrix/runtime proof | complete per-vocation value matrix and gameplay tests |
| Conviction perks | partial | supported 15.25 augment values were corrected where an existing runtime spell path is present | implement missing replacement spells/stances and test every augment |
| Revelation perks | partial | Blue spell grades corrected; Gift of Life now restores health and mana; Battle Healing and Blessing values updated | implement remaining 15.25 Revelation reworks and verify death/relogin state |
| Presets | unverified | no complete preset path proved yet | save/load/switch validation and limits |
| Client protocol | partial | raw modifier reachability proved; save plus current/legacy Gem Atelier payloads now validate required bytes, enum ranges, flags, indexes, and affinities | parser integration tests and official captures |
| Slot persistence | partial | blob records now reject malformed size, duplicate/out-of-range slots, per-slot overflow, disconnected and over-budget state | DB round-trip integration test |
| KV persistence | partial | scroll/gem/active/grade paths traced | round-trip and stale-reference tests |
| Gem reveal and capacity | partial | server-side 225 cap added; initial gems are inserted into the in-memory list immediately | cap and first-open integration tests |
| Gem reveal transaction | partial | item is reserved first, money prechecked, and item restored if the money mutation unexpectedly fails | failure-injection integration test |
| Affinity rotation | partial | active copies are removed by UUID, stale KV is cleared, gem is persisted, and bonuses reload | rotation/login round-trip test |
| Vessel resonance | partial | activation thresholds, effective Grade chaining, +1/+1/+2 full-resonance bonus, and current mitigation scaling are implemented | deterministic runtime effect test |
| Gem mod generation | partial | allowed pools exist; effective Grade is now capped by every preceding gem slot | verify pools, slot restrictions, vocation rules, duplicates, and runtime values |
| Fragment Workshop | partial | 12,500,000 cost applied; type/range/vocation allow-list validation added before indexing; payment rollback added | forged-packet and failure-injection tests |
| Grade persistence | partial | arrays and max-grade count reset; only grades 0..3 are accepted; upgrades persist immediately | KV round-trip test |
| Unused-points accounting | confirmed | spent points use `uint32_t`; overspent state returns zero; allocation validator rejects it; focused test and PR #220 CI passed | runtime malformed-state test remains defense-in-depth |
| Combat/stat integration | partial | 15.25 mitigation, Gift mana, Ballistic pierce, Healing Link, Battle Healing, and low-health Grove scaling are wired into runtime | critical-healing, missing stance/spell, and deterministic effect tests |
| Monk support | partial | Monk stages/avatar and quest bonus represented | full wheel/perk validation |
| Security/anti-cheat | partial | network reachability confirmed; atomic slot/gem proposal, temple enforcement, current/legacy packet length and enum checks, and modifier allow-lists implemented | integration fuzz/forged-packet tests |

---

## 6. Confirmed findings

### WOD-001 — server does not enforce temple-only decreases

**Disposition:** `incorrect`
**Severity:** high

`getOptions()` tells the client whether decreases are allowed, but `saveSlotPointsOnPressSaveButton()` only checks `canOpenWheel()` and per-slot topology/maximum values. A modified client can submit lower allocations outside a temple.

Required correction:

- compare the complete proposed allocation with the current allocation;
- reject any decrease unless the player is in an eligible temple area;
- do not rely on the client-provided UI state.

### WOD-002 — Wheel save is not atomic

**Disposition:** `incorrect`
**Severity:** high

The save handler clears and writes slots sequentially. Invalid entries are retried, and after retry exhaustion earlier accepted changes remain applied. The handler then still loads bonuses and sends the resulting Wheel state.

Required correction:

- parse into a temporary 36-slot structure;
- validate maximums, total budget, topology, decrease rules, and gem references without mutating the player;
- commit all slots and active gems only after the complete proposal passes.

### WOD-003 — Grade IV permanent points are not serialized as extra points

**Disposition:** `incorrect`
**Severity:** high

`getUnusedPoints()` adds `m_modsMaxGrade`, but `getExtraPoints()` and the Wheel-open payload only report scroll and Monk quest points. The server and client can therefore disagree about the available permanent-point total.

Required correction:

- include validated max-grade modifier count in the authoritative extra-point total;
- remove the separate addition from `getUnusedPoints()`;
- use one source of truth for gameplay and protocol.

### WOD-004 — Hunting Task Shop source is absent

**Disposition:** `missing`
**Severity:** medium

The current Taskboard module explicitly implements empty, structurally valid windows and an empty shop. No Wheel point reward/purchase path was found. This blocks the documented additional 50 points.

Required correction is a Taskboard subsystem implementation, not a fabricated Wheel-only storage shortcut.

### WOD-005 — malformed stored/allocation state can underflow unused points

**Disposition:** `incorrect`
**Severity:** high

The unused-point accumulator is unsigned and subtracts each allocated slot without first proving that the allocation total is within the available budget. Invalid persisted or partially applied state can wrap to a large value.

Required correction:

- sum allocations in a wider unsigned type;
- return zero/reject state when spent exceeds available;
- validate loaded slot IDs, per-slot maxima, topology, and total budget before activation.

### WOD-006 — green topology prerequisite contains a duplicated check

**Disposition:** `incorrect`
**Severity:** medium

The `SLOT_GREEN_TOP_100` prerequisite expression checks `SLOT_GREEN_MIDDLE_100` twice. The second occurrence should be verified against the intended adjacent upper branch; current code does not express two distinct paths.

Required correction: derive the expected graph from the 36-slot layout and test every edge before changing the duplicated token.

### WOD-007 — Supreme modifier upgrade cost mismatch

**Disposition:** `incorrect`
**Severity:** medium

The current Grade III Supreme upgrade cost is 12,000,000 gold. The captured gameplay baseline states 12,500,000.

Required correction: change the value only after a second authoritative/captured confirmation, then add a deterministic cost test.

### WOD-008 — modifier position is used before validation

**Disposition:** `incorrect`
**Severity:** critical

`getGemGrade()` and `improveGemGrade()` index fixed arrays using the supplied modifier position without a range/allow-list check. Protocol tracing confirmed that the current and legacy Gem Atelier packet paths pass the client-supplied modifier position directly to this API. The unsafe array access was therefore network-reachable.

Required correction:

- reject positions outside the relevant array;
- require membership in the allowed Basic or vocation-specific Supreme modifier list;
- reject invalid fragment type before reading an array;
- add boundary and forged-packet tests.

### WOD-009 — no revealed-gem capacity enforcement

**Disposition:** `incorrect`
**Severity:** medium

The reveal path appends a generated gem without enforcing the documented limit of 225 revealed gems.

### WOD-010 — affinity rotation can leave stale active bonuses

**Disposition:** `incorrect`
**Severity:** high

Active gems are stored as values. Rotating the affinity of the revealed-gem object does not update/remove the active copy and does not reload Wheel bonus data. The active state can therefore disagree with the revealed gem.

### WOD-011 — reveal payment order is failure-unsafe

**Disposition:** `incorrect`
**Severity:** medium

Gold is removed before the required gem item. If item removal fails after the money operation, the operation returns without refunding the gold.

### WOD-012 — original DB-primary-key suspicion disproved

**Disposition:** `confirmed-correct`

Migration 32 creates `player_wheeldata` with a non-unique index, but migration 33 adds `PRIMARY KEY (player_id)`, and the current `schema.sql` contains the same primary key. No new deduplication migration is required for a fully migrated installation.

The remaining persistence risk is semantic validation of the blob, not row uniqueness.

### WOD-013 — levels below 50 wrap in the point formula

**Disposition:** `incorrect` → correction implemented; PR #220 CI passed
**Severity:** high

The previous formula subtracted 50 from an unsigned level before applying `std::max`, so levels 1–49 wrapped to a large value. Wheel opening blocked these characters, but the public point API still returned invalid values. The formula now branches before subtraction and clamps the final protocol-sized result.

### WOD-014 — initial gems are not visible during the first Wheel open

**Disposition:** `incorrect` → correction implemented; PR #220 CI passed
**Severity:** medium

`addInitialGems()` wrote starter gems only to KV after revealed gems had already been loaded. The same first-open payload therefore omitted the newly created gems. New starter gems are now persisted and inserted into the in-memory revealed list before serialization.

### WOD-015 — permanent point sources were loaded after slot allocation

**Disposition:** `incorrect` → correction implemented; PR #220 CI passed
**Severity:** high

The login sequence loaded the DB allocation before scroll and Grade IV point sources. A semantic allocation validator would therefore reject a valid configuration that spends those points. KV grades and scrolls now load before the persisted allocation is validated.

### WOD-016 — gem modifier Grade ignored preceding-slot limits

**Disposition:** `incorrect` → correction implemented; PR #220 CI passed
**Severity:** high

The runtime applied each globally upgraded modifier Grade independently. Officially documented Gem Atelier behavior limits the second Basic Mod to the effective Grade of the first Basic Mod, and the Supreme Mod to the effective Grades of both preceding Basic Mods. A deterministic helper now calculates effective Grades in slot order before any modifier strategy is executed.

### WOD-017 — full Vessel Resonance damage/healing bonus was absent

**Disposition:** `missing` → correction implemented; PR #220 CI passed
**Severity:** high

The engine unlocked gem modifier slots from Vessel Resonance but did not add the documented full-resonance damage/healing bonus. Runtime loading now adds +1 for a fully enabled Lesser gem, +1 for a fully enabled Regular gem, and +2 for a fully enabled Greater gem.

### WOD-018 — two Blue Revelation spell grades were one stage too high

**Disposition:** `incorrect` → correction implemented; PR #220 CI passed
**Severity:** high

`Drain_Body_Spells` and `Divine Empowerment` were inserted `stage + 1` times because their loops used `i <= stageValue`. One insertion maps to Regular, two to Upgraded, and three to Max, so Revelation Stage I incorrectly produced Grade II. Both loops now perform exactly `stageValue` insertions, matching the other vocation Revelation paths.

### WOD-019 — truncated Gem Atelier packets could execute default actions

**Disposition:** `incorrect` → correction implemented; PR #220 CI passed
**Severity:** critical

Both current and legacy packet paths read action parameters without first proving that the bytes existed. A truncated packet could therefore supply zero-valued defaults and reach destructive or mutating operations, including gem index zero. Both parsers now reject missing action/index/quality/fragment bytes and out-of-range quality or fragment enums before updating UI exhaustion or calling Wheel methods.

### WOD-020 — Dedication mitigation used the pre-15.25 value

**Disposition:** `incorrect` → correction implemented; PR #220 CI passed
**Severity:** high

The Wheel used 0.03% mitigation per Promotion Point. The current 15.25 value is 0.075%. The value is now centralized in `WheelBalance::DEDICATION_MITIGATION_PER_POINT` and used by slot loading.

### WOD-021 — Gem mitigation used obsolete Grade values

**Disposition:** `incorrect` → correction implemented; PR #220 CI passed
**Severity:** high

The base value of 500 produced 5/5.5/6/7.5%. The current values are 20/22/24/30%, so the Grade multiplier now starts from 2000.

### WOD-022 — Gift of Life restored health but not mana

**Disposition:** `missing` → correction implemented; PR #220 CI passed
**Severity:** high

The runtime health effect existed, but no mana restoration path was present. Gift of Life now restores the same stage percentage of maximum mana after the health effect.

### WOD-023 — Ballistic Mastery bow pierce remained at 2%

**Disposition:** `incorrect` → correction implemented; PR #220 CI passed
**Severity:** medium

Bow attacks/spells granted 2% physical and holy pierce. Both values now use the current 4% baseline. Crossbow critical extra damage already matched 10%.

### WOD-024 — Healing Link remained at 10%

**Disposition:** `incorrect` → correction implemented; PR #220 CI passed
**Severity:** high

The linked-healing value now uses 25%.

### WOD-025 — Battle Healing still used challenge-triggered healing

**Disposition:** `incorrect` → correction implemented; PR #220 CI passed
**Severity:** high

The old implementation healed when a monster challenge succeeded and scaled from shield skill and missing health. The challenge hook was removed. Healing spells now receive +10% healing, or +30% while a shield is equipped.

### WOD-026 — Blessing of the Grove low-health values were obsolete

**Disposition:** `incorrect` → percentage correction implemented; critical healing still missing
**Severity:** high

The engine used 6/9/12%. It now uses 5/7.5/10% below 60% health and doubles the value at or below 30%. The newly required critical-healing capability remains a separate unimplemented combat feature.

### WOD-027 — supported existing augment values/order were outdated

**Disposition:** `incorrect` → partial correction implemented; PR #220 CI passed
**Severity:** high

Existing runtime paths were updated for Front Sweep, Groundshaker, Divine Dazzle, Energy Wave, Heal Friend, Terra Wave, Strong Ice Wave metadata, Mass Spirit Mend, Mystic Repulse, and Flurry of Blows. Front Sweep and Flurry now execute their larger Wheel areas. Strong Ice Wave's exact current base/augmented tile layouts remain blocked pending authoritative area evidence.

### WOD-028 — current replacement spells and vocation stances are absent

**Disposition:** `missing`
**Severity:** critical for 15.25 parity

No implementation was found for Shield Bash, Shield Slam, Divine Barrage, Ethereal Barrage, Death Echo, Forked Glacier, Forked Thorns, Thousand Fist Blows, or the new vocation stance framework. Old augment targets such as Chivalrous Challenge, Swift Foot, Sharpshooter, Sap Strength, Magic Shield, Nature's Embrace, and Sweeping Takedown must not be silently treated as equivalent.

### WOD-029 — several 15.25 Revelation/passive reworks remain absent

**Disposition:** `missing`
**Severity:** critical for 15.25 parity

Combat Mastery still follows its old behavior; Beam Mastery does not implement adjacent-target scaling; Lord of Destruction is absent; Focus Mastery lacks the current group-cooldown reduction; Blessing critical healing is absent; and the latest Guiding Presence, Sanctuary, and other vocation reworks still require dedicated runtime implementation.

---

## 7. Change log

### 2026-07-12 — validation initialized

- Created the dedicated branch and durable validation log.
- Read the main AI world-validation methodology and adopted its evidence-based, no-guessing rule.
- Captured the current community gameplay baseline.
- Located the principal Wheel of Destiny implementation surface.
- Confirmed explicit 36-slot and 250/500/1000 Revelation-stage definitions.

### 2026-07-12 — points, persistence, Gem Atelier, and security audit

- Traced level points, Promotion Scroll points, Monk quest points, Grade IV points, and the absent Hunting Task Shop source.
- Confirmed server-side Premium/promotion/level/vocation eligibility.
- Traced DB and KV persistence and corrected the initial suspicion about a missing `player_wheeldata` primary key after finding migration 33.
- Confirmed non-atomic save behavior and missing server-side temple decrease enforcement.
- Confirmed unsigned unused-point underflow risk.
- Located a duplicated green topology prerequisite.
- Confirmed the missing 225 revealed-gem cap, stale active-gem rotation behavior, and failure-unsafe reveal payment order.
- Confirmed the 12,000,000 versus 12,500,000 Supreme cost mismatch against the captured baseline.
- Confirmed unsafe modifier-position array indexing and proved reachability from both current and legacy Gem Atelier packet paths.
- Identified the below-level unsigned wrap, first-open starter-gem omission, and login load-order dependency.


### 2026-07-12 — first hardening implementation

- Added an atomic 36-slot proposal validator: invalid topology, over-budget state, malformed gem references, or truncated packets leave the previous Wheel unchanged.
- Enforced temple-only decreases on the server instead of trusting the client option byte.
- Added semantic validation for persisted Wheel blobs and moved permanent point-source loading before allocation validation.
- Consolidated Grade IV points into `getExtraPoints()` and replaced subtractive unsigned accounting with a saturating spent/available calculation.
- Fixed the unsigned point formula for levels 1–50.
- Added modifier type, bounds, and vocation allow-list checks before any grade-array access.
- Corrected the Supreme Grade III gold cost to 12,500,000 and persisted successful upgrades immediately.
- Added the 225-gem reveal cap, first-open starter-gem synchronization, stale active-gem cleanup, and active-bonus reload on destruction/rotation.
- Reordered reveal/upgrade transactions so consumed items are restored if the later money mutation unexpectedly fails.
- Added focused unit tests for level thresholds, overspent-state saturation, Supreme costs, and invalid grades.
- Applied the SHA-256-verified patch to the clean review branch and removed every temporary patch/export workflow before opening the clean review PR.

### 2026-07-12 — Gem Atelier grade/resonance and parser follow-up

- Confirmed that active gem runtime ignored the preceding-slot Grade cap documented by the Gem Atelier.
- Added deterministic effective-Grade calculation for Lesser, Regular, and Greater gems.
- Added the missing +1/+1/+2 full Vessel Resonance damage/healing bonuses.
- Corrected `Drain_Body_Spells` and `Divine Empowerment` from `stage + 1` to exactly one spell-grade insertion per Revelation stage.
- Proved that both current and legacy Gem Atelier parsers could read truncated payloads as zero-valued actions or parameters.
- Added byte-length and enum-range validation before every current/legacy Gem Atelier mutation.
- Added focused unit tests for Grade chaining and full-resonance thresholds.
- Standard repository CI for clean PR #209 completed successfully, including the dedicated Wheel validation workflow and repository build matrix.

### 2026-07-12 — current 15.25 balance and augment follow-up

- Captured the June 16, 2026 Wheel balance baseline and separated implementable numeric/runtime corrections from missing spell/stance systems.
- Updated Dedication and Gem mitigation scaling.
- Added Gift of Life mana restoration, 4% Ballistic Mastery pierce, and 25% Healing Link.
- Replaced challenge-triggered Battle Healing with +10% healing-spell output, or +30% with a shield.
- Corrected Blessing of the Grove low-health percentages while leaving critical healing explicitly unresolved.
- Updated supported existing augment values/order and added runtime area variants for Front Sweep and Flurry of Blows.
- Recorded missing current spells, stances, and major passive/Revelation reworks instead of mapping them onto obsolete mechanics.
- Clean PR #220 completed the repository CI build matrix, dedicated Wheel validation, and AI codebase checks successfully.
- Added centralized balance constants and focused regression assertions.
- Status: merged to `main` via PR #220; remaining Tibia 15.25 gaps are explicitly tracked below.

---

## 8. Validation conclusion

The evidence-based validation phase is complete for the currently implemented Wheel subsystem. PR #220 contains the confirmed, non-speculative corrections and passed the repository CI build matrix plus dedicated Wheel validation.

The Wheel is **not fully feature-complete for Tibia 15.25**. The following are explicit implementation gaps rather than unresolved audit ambiguity:

1. the new vocation stance framework and replacement spells/augments absent from Canary;
2. Blessing of the Grove critical-healing support;
3. Strong Ice Wave expanded tile layout pending authoritative geometry;
4. remaining major 15.25 passive/Revelation reworks listed in WOD-029;
5. Hunting Task Shop promotion points, blocked by the empty Taskboard shop subsystem;
6. end-to-end protocol, DB/KV round-trip, failure-injection, and gameplay scenario tests.

These gaps must not be represented as compatible until their runtime behavior and client protocol are implemented and tested. They are suitable for separate focused PRs because they require new gameplay systems or authoritative data, not small corrections to the existing Wheel implementation.

---

## 9. Handoff rule

A later agent must begin by reading this file and `OTS_AI_WORLD_VALIDATION_PROJECT.md`, then inspect the latest branch diff and continue from the first unresolved finding or matrix item. Do not repeat completed evidence gathering, do not silently change baseline values, and do not mark a subsystem `confirmed` without a reproducible test or an explicitly documented reason why runtime proof is unavailable.
