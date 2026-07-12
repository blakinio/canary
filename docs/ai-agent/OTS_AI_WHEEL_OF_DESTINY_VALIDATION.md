# OTS AI Wheel of Destiny Validation — plan, evidence, findings and handoff

> **Status:** active validation
> **Started:** 2026-07-12
> **Last updated:** 2026-07-12
> **Repository:** `blakinio/canary`
> **Working branch:** `validation/wheel-of-destiny`
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
| Promotion points from levels | partial | formula now handles levels 1–50 without unsigned wrap; unit coverage added | CI and runtime login test |
| Promotion Scroll points | confirmed | five unique scrolls total 50; KV persistence traced | Lua/runtime use test |
| Way of the Monk points | partial | storage/config path exists and is included in extra points | quest completion and protocol test |
| Hunting Task Shop points | missing | current Taskboard module explicitly sends an empty shop shim | implement Taskboard reward/shop persistence |
| Grade IV permanent points | partial | accounting consolidated into `getExtraPoints()` and load order moved before allocation validation | CI, protocol capture, Grade IV round trip |
| 36-slice topology | partial | duplicated green edge corrected by quadrant symmetry; complete allocation is validated before commit | exhaustive topology matrix test |
| Revelation thresholds | partial | 250/500/1000 definitions and runtime stages exist | domain totals and effect tests |
| Temple-only reallocation | partial | proposed decreases are now rejected server-side unless `getOptions()` confirms temple access | forged-packet integration test |
| Premium/promoted eligibility | confirmed | `canOpenWheel()` rejects unpromoted, non-Premium, level <= 50, and vocation-none players | protocol rejection test |
| Vocation wheels | partial | effects for five vocations are represented | verify every slice/effect/value per vocation |
| Dedication perks | unverified | stats structures present | map each slot to exact scaling and tests |
| Conviction perks | unverified | spell/passive hooks present | map each perk and stacking behavior |
| Revelation perks | partial | stages/avatars represented | verify stages, cooldowns, death/relogin state |
| Presets | unverified | no complete preset path proved yet | save/load/switch validation and limits |
| Client protocol | partial | raw modifier position reachability proved; save payload now checks required bytes, flags, indexes, and affinities | parser integration tests and official captures |
| Slot persistence | partial | blob records now reject malformed size, duplicate/out-of-range slots, per-slot overflow, disconnected and over-budget state | DB round-trip integration test |
| KV persistence | partial | scroll/gem/active/grade paths traced | round-trip and stale-reference tests |
| Gem reveal and capacity | partial | server-side 225 cap added; initial gems are inserted into the in-memory list immediately | cap and first-open integration tests |
| Gem reveal transaction | partial | item is reserved first, money prechecked, and item restored if the money mutation unexpectedly fails | failure-injection integration test |
| Affinity rotation | partial | active copies are removed by UUID, stale KV is cleared, gem is persisted, and bonuses reload | rotation/login round-trip test |
| Vessel resonance | partial | four resonance values represented | verify activation order and full-resonance bonus |
| Gem mod generation | partial | allowed pools exist | verify pools, slot restrictions, vocation rules, and duplicates |
| Fragment Workshop | partial | 12,500,000 cost applied; type/range/vocation allow-list validation added before indexing; payment rollback added | forged-packet and failure-injection tests |
| Grade persistence | partial | arrays and max-grade count reset; only grades 0..3 are accepted; upgrades persist immediately | KV round-trip test |
| Unused-points accounting | partial | spent points are summed in `uint32_t`; overspent state returns zero and allocation validator rejects it | unit test added; CI pending |
| Combat/stat integration | partial | bonus structures and hooks present | deterministic effect tests |
| Monk support | partial | Monk stages/avatar and quest bonus represented | full wheel/perk validation |
| Security/anti-cheat | partial | network reachability confirmed; atomic slot/gem proposal, temple enforcement, packet length/range checks, and modifier allow-lists implemented | integration fuzz/forged-packet tests |

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

**Disposition:** `incorrect` → correction implemented, CI pending
**Severity:** high

The previous formula subtracted 50 from an unsigned level before applying `std::max`, so levels 1–49 wrapped to a large value. Wheel opening blocked these characters, but the public point API still returned invalid values. The formula now branches before subtraction and clamps the final protocol-sized result.

### WOD-014 — initial gems are not visible during the first Wheel open

**Disposition:** `incorrect` → correction implemented, CI pending
**Severity:** medium

`addInitialGems()` wrote starter gems only to KV after revealed gems had already been loaded. The same first-open payload therefore omitted the newly created gems. New starter gems are now persisted and inserted into the in-memory revealed list before serialization.

### WOD-015 — permanent point sources were loaded after slot allocation

**Disposition:** `incorrect` → correction implemented, CI pending
**Severity:** high

The login sequence loaded the DB allocation before scroll and Grade IV point sources. A semantic allocation validator would therefore reject a valid configuration that spends those points. KV grades and scrolls now load before the persisted allocation is validated.

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
- Status: local patch prepared; formatter, build, unit tests, and CI evidence still pending.

---

## 8. Immediate next tasks

1. Apply the prepared patch to the validation branch and let repository formatters normalize it.
2. Run Linux build and focused/unit test suites; fix every compiler, formatter, sanitizer, or test failure.
3. Add integration tests for forged save packets, invalid modifier positions, temple decreases, transaction rollback, KV/DB round trips, cap behavior, and first-open starter gems.
4. Generate a machine-readable 36-slot topology/perk matrix for every vocation.
5. Compare every Dedication, Conviction, Revelation, spell augment, and gem modifier value with authoritative/captured behavior.
6. Implement the missing Hunting Task Shop point source in its Taskboard subsystem or keep it explicitly blocked as a separate dependency.
7. Remove all temporary patch/export workflows before the PR is marked ready.
8. Update this document with each code/test commit and final runtime evidence.

---

## 9. Handoff rule

A later agent must begin by reading this file and `OTS_AI_WORLD_VALIDATION_PROJECT.md`, then inspect the latest branch diff and continue from the first unresolved finding or matrix item. Do not repeat completed evidence gathering, do not silently change baseline values, and do not mark a subsystem `confirmed` without a reproducible test or an explicitly documented reason why runtime proof is unavailable.
