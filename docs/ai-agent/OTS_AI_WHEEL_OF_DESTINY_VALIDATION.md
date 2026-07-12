# OTS AI Wheel of Destiny Validation — plan, evidence, findings and handoff

> **Status:** active validation
> **Started:** 2026-07-12
> **Repository:** `blakinio/canary`
> **Working branch:** `validation/wheel-of-destiny`
> **Reference process:** `docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md`
> **Primary gameplay reference:** `https://tibia.fandom.com/wiki/Wheel_of_Destiny`
> **Rule:** update this file in the same change set whenever Wheel of Destiny code, data, tests, or validation conclusions change.

---

## 1. Goal

Validate the complete Wheel of Destiny implementation in Canary against the currently documented Tibia mechanics, without assuming that code presence proves gameplay correctness.

The validation covers:

- eligibility and promotion-point sources;
- wheel topology, slice costs, adjacency, domain totals, and revelation thresholds;
- dedication, conviction, revelation, and vocation-specific effects;
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

These values are a working comparison baseline, not yet a declaration that every detail is authoritative or unchanged. Official CipSoft sources and protocol behavior should supersede community documentation when available.

---

## 4. Repository surface discovered

Initial code search identified these active subsystem files:

- `src/io/io_wheel.hpp`
- `src/io/io_wheel.cpp`
- `src/creatures/players/components/wheel/player_wheel.hpp`
- `src/creatures/players/components/wheel/player_wheel.cpp`
- `src/creatures/players/components/wheel/wheel_definitions.hpp`
- `src/creatures/players/components/wheel/wheel_gems.hpp`
- `src/creatures/players/components/wheel/wheel_gems.cpp`
- `src/creatures/players/components/wheel/wheel_spells.hpp`
- `src/enums/player_wheel.hpp`
- `data/scripts/actions/items/wheel_scrolls.lua`
- `data-otservbr-global/migrations/32.lua`
- protocol, login-data, vocation, combat, spell, and player integration files.

Initial confirmed definitions:

- 36 wheel slots are enumerated;
- Revelation thresholds are represented as 250, 500, and 1000;
- Knight, Paladin, Druid, Sorcerer, and Monk revelation effects are represented;
- Wheel bonuses include stats, skills, leech, mitigation, damage/healing, instant effects, stages, avatars, vessel resonances, momentum, and spell unlocks/boosts.

Current disposition: `partial`. Definitions exist, but calculation correctness, validation security, persistence, protocol handling, and gameplay behavior are not yet proven.

---

## 5. Validation matrix

| Area | Status | Current evidence | Next proof required |
|---|---|---|---|
| Promotion points from levels | unverified | subsystem present | trace formula, eligibility, caps, tests |
| Extra permanent points | unverified | scroll action discovered | trace all four sources and persistence |
| 36-slice topology | partial | 36 slots enumerated | verify adjacency, costs, legal allocation |
| Revelation thresholds | partial | 250/500/1000 enum values | verify domain calculation and activation |
| Temple-only reallocation | unverified | none reviewed | trace request validation and map/zone check |
| Premium/promoted eligibility | unverified | none reviewed | trace protocol and server-side rejection |
| Vocation wheels | partial | vocation effects represented | verify every slice/effect/value per vocation |
| Dedication perks | unverified | stats structures present | map each slot to exact scaling and tests |
| Conviction perks | unverified | spell/passive hooks present | map each perk and stacking behavior |
| Revelation perks | partial | stages/avatars represented | verify stages, cooldowns, death/relogin state |
| Presets | unverified | none reviewed | save/load/switch validation and limits |
| Client protocol | unverified | protocol integration discovered | parse/send paths, malformed request tests |
| Persistence | unverified | IO layer discovered | schema/KV/load/save/migration round-trip tests |
| Gem reveal and capacity | unverified | gem subsystem discovered | verify 225 cap, destruction/binding, costs |
| Affinity rotation | unverified | gem subsystem discovered | verify direction, costs, overflow, persistence |
| Vessel resonance | partial | four resonance values represented | verify activation order and full-resonance bonus |
| Gem mod generation | unverified | allowed modifier tables present | verify pools, slot restrictions, vocation rules |
| Fragment Workshop | unverified | none fully traced | verify fragments, gold, grades, dependencies |
| Combat/stat integration | partial | bonus structures and hooks present | deterministic effect tests |
| Monk support | partial | Monk stages/avatar represented | full wheel and extra-point source validation |
| Security/anti-cheat | unverified | none reviewed | invalid points, disconnected slices, forged packets |

---

## 6. Findings log

### 2026-07-12 — validation initialized

- Created dedicated branch and durable validation log.
- Read the main AI world-validation methodology and adopted its evidence-based, no-guessing rule.
- Captured the current community gameplay baseline.
- Located the principal Wheel of Destiny implementation surface.
- Confirmed that the repository contains explicit 36-slot and 250/500/1000 Revelation-stage definitions.
- No production code change has been made yet.

---

## 7. Immediate next tasks

1. Trace `PlayerWheel` allocation validation from inbound protocol to applied bonuses.
2. Prove promotion-point calculation and every permanent-point source.
3. Audit save/load and migration behavior, including malformed or legacy state.
4. Build a machine-readable vocation/slice/perk matrix from production tables.
5. Compare every numeric value and activation condition with reliable gameplay references.
6. Add focused tests before making behavior changes.
7. For every code correction, update this document in the same branch commit.

---

## 8. Handoff rule

A later agent must begin by reading this file and `OTS_AI_WORLD_VALIDATION_PROJECT.md`, then inspect the latest branch diff and continue from the first `unverified`, `partial`, or `needs-runtime-test` item. Do not repeat completed evidence gathering, do not silently change baseline values, and do not mark a subsystem `confirmed` without a reproducible test or an explicitly documented reason why runtime proof is unavailable.
