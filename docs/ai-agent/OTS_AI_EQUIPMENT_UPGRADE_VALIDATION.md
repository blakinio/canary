# OTS AI Equipment Upgrade Validation — status, findings and handoff

> **Status date:** 2026-07-12  
> **Repository:** `blakinio/canary`  
> **Working branch:** `validation/equipment-upgrade`  
> **Current pull request:** `#177`  
> **Primary comparison page:** `https://tibia.fandom.com/wiki/Equipment_Upgrade`  
> **Parent methodology:** `docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md`  
> **Current phase:** static/semantic validation plus limited evidence-backed remediation; runtime and gameplay evidence remain open  
> **Rule:** every implementation change made during this validation must be recorded in this file in the same commit or immediately following commit.

---

## 1. Goal and scope

Validate Canary's complete Equipment Upgrade / Exaltation Forge implementation against documented Tibia behaviour. Code presence, a successful build or client-side filtering is not accepted as gameplay proof.

Scope:

1. classifications, tier caps and item eligibility;
2. Dust, Slivers and Exalted Cores;
3. influenced/fiendish spawn, scaling, rewards and lifecycle;
4. regular and Convergence Fusion/Transfer;
5. Fusion bonuses, history and transaction safety;
6. Onslaught, Ruse, Momentum, Transcendence and Amplification;
7. Canary ↔ OTClient result compatibility;
8. unit, integration, runtime and gameplay evidence.

---

## 2. Evidence levels

- **A — structural:** relevant files/configuration load and compile.
- **B — static:** identifiers, metadata, tables and handlers resolve.
- **C — semantic:** formulas, eligibility, costs and outcomes match the reference.
- **D — runtime:** the server starts and Forge systems register without critical errors.
- **E — gameplay:** test characters execute the complete scenarios correctly.
- **F — regression:** automated tests preserve confirmed behaviour and reject malformed requests.

A lower level is never reported as proof of a higher level.

---

## 3. Safety rules

- Do not change prices, probabilities or formulas without evidence.
- Treat all client-supplied item IDs, tiers and action flags as untrusted.
- Validate before removing items, Dust, cores or gold.
- Preserve merged behaviour from PRs #89 and #110 and the same-object removal guard.
- Prefer the smallest independently testable correction.
- Keep server-mechanic and OTClient-presentation findings separate.
- Record unresolved questions instead of guessing.

---

## 4. Existing baseline that must be preserved

### PR #89 — normal Transfer

Already merged:

- compatibility based on upgrade classification rather than equipment slot;
- donor-tier and classification validation;
- correct regular Transfer costs and resulting tier;
- actual Dust/core/gold values in history;
- corrected donor/receiver rendering;
- focused policy and integration tests.

### PR #110 — Forge history identity

Already merged:

- both item IDs stored in in-memory history;
- item resolution by ID instead of ambiguous name-only lookup;
- name fallback for older call sites.

These are baseline evidence, not proof of complete parity.

---

## 5. Validation matrix

| Area | Reference behaviour | Current result |
|---|---|---|
| Classification | Class 1/2/3/4 caps: 1/2/3/10 | **confirmed statically**; runtime loading pending |
| Imbuements | Imbued equipment cannot enter Forge | **confirmed statically** in list and server item lookup |
| Initial Dust limit | 100 | **confirmed statically** in schema |
| Dust limit upgrade | Cost = current limit − 75; maximum 325 | formula confirmed; **F-001 open:** configured/fallback maximum 225 |
| Dust conversion | 60 Dust → 3 Slivers | success path confirmed; **F-024:** history is config-insensitive |
| Core conversion | 50 Slivers → 1 Core | **F-021 open:** removal precedes result creation |
| Influenced scaling | 1–5 stacks; HP/damage/XP and 1–3 Dust per stack | HP/damage/XP confirmed statically; reward tests pending |
| Fiendish scaling/lifecycle | strength of 15 stacks; four alive; replacement/lifetime rules | default path confirmed statically; **F-002/F-009 open** |
| Premium Dust | no Dust without Premium | **F-006 open:** Lua has no binding matching full `Player::isPremium()` semantics |
| Party Dust | one amount for eligible shared-experience members with logout block | **F-007/F-013 remediated in branch**; runtime boundaries pending |
| Dust cap feedback | report actual credited amount | **F-008 remediated in branch**; runtime test pending |
| Regular Fusion eligibility | identical item IDs and equal tier | **F-003 open:** identity not revalidated server-side |
| Fusion success/failure | documented probabilities and loss rules | static path located; deterministic outcome tests pending |
| Fusion costs | class/tier gold + Dust + optional cores | table confirmed; **F-022:** failed history hardcodes 100 Dust |
| Fusion bonuses | eight documented success bonuses | **F-014–F-016 open:** eighth bonus absent, +2 cap wrong, selection not tier-aware |
| Fusion history | exact result for each bonus and both IDs | **F-017/F-022 open** |
| Forge result protocol/client | every result represented exactly | **F-018/F-019 open** |
| Convergence Fusion | class 4; different IDs; same normalized slot/tier | **F-004 open:** restrictions incomplete server-side |
| Regular Transfer | same class; receiver tier 0; result donor tier − 1 | partially confirmed by PR #89; gameplay test pending |
| Convergence Transfer | class 4; no tier loss; cross-slot allowed | **F-005 open:** class 4 not enforced server-side |
| Atomicity | failed operation leaves no partial mutation | **F-020/F-021 open** |
| Conversion history type | preserve executed action type and actual amounts | **F-023/F-024 open** |
| Onslaught | tier chance; triggered basic attack +60% damage | formula/combat path confirmed statically; runtime/AoE pending |
| Ruse | tier dodge chance | formula path confirmed; **F-010 precision risk** |
| Momentum | eligible cooldowns −2 s | formula/reduction confirmed; **F-012 open** |
| Transcendence | seven-second Avatar; cannot overlap Avatar spell | formula/window/duration confirmed; **F-011 open** |
| Amplification | multiplicatively increases other Forge chances | four paths confirmed statically; runtime/event ordering pending |

---

## 6. Confirmed implementation paths

### Server/configuration

- `config.lua.dist`
- `src/config/configmanager.cpp`
- `data/scripts/systems/item_tiers.lua`
- `src/items/items_classification.hpp`
- `src/game/game.cpp`
- `src/creatures/players/player.cpp`
- `src/server/network/protocol/protocolgame.cpp`
- `src/utils/tools.cpp`
- `src/game/functions/forge_transfer_policy.hpp`

### Creatures/rewards/effects

- `src/creatures/monsters/monster.cpp`
- `data/libs/systems/exaltation_forge.lua`
- `data/scripts/creaturescripts/monster/forge_kill.lua`
- `src/creatures/players/grouping/party.cpp`
- `src/items/item.cpp`
- `src/creatures/combat/combat.cpp`
- `data/scripts/spells/support/avatar_of_*.lua`

### Client/tests

- `opentibiabr/otclient/modules/game_forge/game_forge.lua`
- `opentibiabr/otclient/src/client/protocolgameparse.cpp`
- `tests/unit/players/forge_test.cpp`
- `tests/integration/game/forge_it.cpp`

---

## 7. Findings and remediation status

### F-001 — maximum Dust capacity remains 225

**Severity:** medium. **Status:** open. **Evidence:** B–C.

`config.lua.dist` and the `ConfigManager` fallback use 225; the selected post-February-2023 behaviour uses 325.

**Required:** update both sources and test 324 → 325 plus rejection above 325.

### F-002 — Fiendish limit defaults are inconsistent

**Severity:** low/medium. **Status:** open. **Evidence:** B.

Distributed configuration uses 4; engine fallback and an unused legacy Lua value use 3.

### F-003 — regular Fusion identity relies on client filtering

**Severity:** high. **Status:** open. **Evidence:** C.

The handler does not independently require identical item IDs. An integration test currently permits two different IDs.

### F-004 — Convergence Fusion restrictions are incomplete server-side

**Severity:** high. **Status:** open. **Evidence:** C.

Class 4, different IDs and same normalized slot are filtered for the UI but not fully revalidated before mutation.

### F-005 — Convergence Transfer does not enforce class 4

**Severity:** high. **Status:** open. **Evidence:** C.

Matching classifications and donor tier are checked; convergence does not additionally require classification 4.

### F-006 — Premium Dust eligibility is not enforced

**Severity:** high. **Status:** open. **Evidence:** C.

The reward path has no Premium check. A temporary `getPremiumDays() > 0` check was removed because it did not match `Player::isPremium()`, which also recognizes global free Premium, `IsAlwaysPremium` and an active `premiumLastDay`.

**Required:** expose `Player::isPremium()` to Lua or move reward eligibility to C++; test normal, final partial day, free-Premium and always-Premium cases.

### F-007 — party Dust needed an explicit current logout block

**Severity:** high. **Status:** remediated statically; runtime boundaries pending. **Evidence:** C.

Shared experience controls activity, level and 30×30×1 range. The reward path now also requires `CONDITION_INFIGHT` for every recipient.

### F-008 — Dust cap message reported the requested amount

**Severity:** low. **Status:** remediated; runtime test pending. **Evidence:** C.

The reward helper now uses `min(amount, limit − current)` for mutation and success messaging.

### F-009 — Fiendish Slivers ignore creature difficulty

**Severity:** medium. **Status:** open. **Evidence:** C.

Every Fiendish corpse uses a global random minimum/maximum; creature difficulty is unused. The exact versioned mapping must be sourced before implementation.

### F-010 — Ruse truncates fractional basis points

**Severity:** low. **Status:** open precision question. **Evidence:** B–C.

Floating-point percentages and Amplification are cast to integer basis points by truncation. Confirm authoritative precision before changing.

### F-011 — Transcendence can overlap the Avatar spell

**Severity:** medium/high. **Status:** open. **Evidence:** C.

Avatar spells set `AVATAR_SPELL`; Transcendence checks only `AVATAR_FORGE`.

### F-012 — Momentum can display a false trigger

**Severity:** low. **Status:** open. **Evidence:** C.

The trigger flag can be set before any eligible cooldown is reduced.

### F-013 — party members received independently randomized Dust

**Severity:** medium/high. **Status:** remediated; runtime test pending. **Evidence:** C.

One amount is now rolled per death and passed to every eligible recipient.

### F-014 — the Dust-refill success bonus is not implemented

**Severity:** high. **Status:** open. **Evidence:** C.

The documented eighth success bonus refills Dust. `forgeBonus()` generates only values 0–7; value 8 is overloaded for a failed-Fusion retained-tier outcome.

### F-015 — +2 tiers uses classification ID as the cap

**Severity:** high. **Status:** open. **Evidence:** C.

`tier + 2` is compared with classification ID. Class 4 is therefore treated as if capped at tier 4 instead of 10.

### F-016 — Fusion bonus selection is not tier-aware

**Severity:** medium/high. **Status:** open. **Evidence:** C.

Impossible decreased-tier or +2 outcomes can be selected and reported without their documented effect.

### F-017 — Fusion history misreports Convergence and bonus results

**Severity:** high. **Status:** open. **Evidence:** C.

Fusion history resolves only the first item type, always reports +1 on success and marks retained items consumed except for overloaded bonus 8.

### F-018 — OTClient renders only bonus types 1–4

**Severity:** medium/high. **Status:** open in `opentibiabr/otclient`. **Evidence:** C.

Values 5–8 have no complete result presentation.

### F-019 — decreased-tier payload/UI reports the wrong tier

**Severity:** medium. **Status:** open. **Evidence:** C.

The server retains the item at `t−1`, but the packet/UI represents tier `t`.

### F-020 — Fusion and Transfer are not atomic after mutation starts

**Severity:** high. **Status:** open. **Evidence:** C.

The chest and input removals occur before all output/resource mutations succeed. Later failures return without rollback.

### F-021 — Sliver→Core can consume Slivers without granting a Core

**Severity:** high. **Status:** open. **Evidence:** C.

Slivers are removed before Core creation/insertion. Null creation can still lead to success history; insertion failure does not restore Slivers.

### F-022 — failed Fusion history hardcodes 100 Dust

**Severity:** low/medium. **Status:** open. **Evidence:** C.

History ignores the actual stored/configured Dust cost.

### F-023 — conversion history rewrites action types

**Severity:** medium. **Status:** open. **Evidence:** C.

`SLIVERSTOCORES` and `INCREASELIMIT` are stored as `DUSTTOSLIVERS`.

### F-024 — Dust→Slivers history hardcodes gained amount 3

**Severity:** low. **Status:** open. **Evidence:** C.

Created quantity uses configuration; history always says 3.

---

## 8. Required regression scenarios

1. regular Fusion accepts identical IDs and rejects different IDs;
2. all rejected/failed operations preserve items, Dust, cores and gold;
3. Convergence Fusion/Transfer enforce class 4 and their exact slot/tier rules;
4. Dust capacity stops at 325 and conversions are atomic;
5. Premium eligibility matches `Player::isPremium()` in every account/configuration case;
6. party recipients share one Dust roll and satisfy range/activity/logout rules;
7. Dust cap messaging reports the credited amount;
8. Fiendish Slivers follow the confirmed difficulty rule;
9. Transcendence cannot overlap Avatar and Momentum triggers only after a real reduction;
10. every bonus is forced deterministically and checked across item state, resources, history, packet and OTClient;
11. every mutation boundary has an injected-failure rollback test;
12. all conversion history action types and configurable amounts round-trip correctly.

---

## 9. Work log

### 2026-07-12 — initialization

- Read the parent methodology.
- Created `validation/equipment-upgrade` and this document.
- Identified PRs #89/#110 and the same-object removal guard as baseline.

### 2026-07-12 — audit passes 1–4

- Reconstructed classifications, costs, probabilities, conversions and protocol flows.
- Traced influenced/fiendish scaling, rewards and lifecycle.
- Traced all five item effects.
- Traced every Fusion bonus through mutation, history, packet and OTClient.
- Traced mutation ordering in Fusion, Transfer and conversion.
- Recorded F-001 through F-024.

### 2026-07-12 — remediation pass 1: Dust accounting and party delivery

Changed `data/libs/systems/exaltation_forge.lua`:

- centralized player/summon killer resolution;
- generated one Dust amount per kill;
- reused that amount for eligible shared-experience recipients;
- added explicit `CONDITION_INFIGHT` validation;
- used the actual capped amount for mutation and messaging.

The initial Premium-days check was deliberately removed after proving it did not match full server Premium semantics. F-006 remains open; F-007/F-008/F-013 retain code remediation.

### CI evidence

For the Lua remediation and current document state:

- Lua tests passed;
- clang-format, StyLua and cmake-format checks passed without generated changes;
- Lua API documentation checks, analysis and yamllint passed;
- the current Linux compile/runtime/test job was still running at the time of this update.

No focused Forge gameplay test has been executed. Full parity is not claimed.

---

## 10. Next actions

1. expose exact `Player::isPremium()` semantics and test F-006;
2. implement server-authority fixes F-003–F-005 before mutation;
3. introduce atomic transaction/rollback handling for F-020/F-021;
4. redesign bonus result data and resolve F-014–F-019 jointly across Canary/OTClient;
5. correct F-001/F-002 and history F-022–F-024;
6. source the Fiendish difficulty→Sliver mapping for F-009;
7. fix F-011/F-012; resolve F-010 only after precision confirmation;
8. complete build, runtime and gameplay validation.

---

## 11. Handoff

Continue on `validation/equipment-upgrade` and read this file plus `OTS_AI_WORLD_VALIDATION_PROJECT.md` first. Preserve PR #89/#110. Only F-007/F-008/F-013 currently have retained production-code remediation, and they still need runtime evidence. All other findings remain open. Static evidence reaches B–C for explicitly marked rows; full Equipment Upgrade parity has not been established.