# OTS AI Equipment Upgrade Validation — status, findings and handoff

> **Status date:** 2026-07-12  
> **Repository:** `blakinio/canary`  
> **Working branch:** `validation/equipment-upgrade`  
> **Current pull request:** `#177`  
> **Primary comparison page:** `https://tibia.fandom.com/wiki/Equipment_Upgrade`  
> **Parent methodology:** `docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md`  
> **Current phase:** static/semantic validation plus first evidence-backed remediation; runtime and gameplay evidence remain open  
> **Rule:** every implementation change made during this validation must be recorded in this file in the same commit or immediately following commit.

---

## 1. Goal and scope

Validate Canary's complete Equipment Upgrade / Exaltation Forge implementation against documented Tibia behaviour. Code presence, a successful build or client-side filtering is not accepted as gameplay proof.

Scope:

1. classifications, tier caps and item eligibility;
2. Dust, Slivers and Exalted Cores;
3. influenced/fiendish spawn, scaling, rewards and lifecycle;
4. regular and Convergence Fusion;
5. regular and Convergence Transfer;
6. Fusion bonuses and Forge history;
7. Onslaught, Ruse, Momentum, Transcendence and Amplification;
8. protocol/server authority, persistence and transaction safety;
9. Canary ↔ OTClient result-packet compatibility;
10. unit, integration, runtime and gameplay evidence.

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
- Treat item IDs, tiers, action flags and convergence flags from the client as untrusted.
- Validate before removing items, Dust, cores or gold.
- Preserve merged behaviour from PRs #89 and #110 and the same-object removal guard.
- Prefer the smallest independently testable correction.
- Keep server-mechanic and OTClient-presentation findings separate.
- Record unresolved questions instead of guessing.

---

## 4. Existing baseline that must be preserved

### PR #89 — normal Transfer

Already merged:

- matching upgrade classification instead of matching equipment slot;
- donor-tier and classification validation;
- correct regular Transfer price/core lookup and resulting tier;
- real Dust/core/gold values in history;
- corrected donor/receiver rendering;
- focused policy and integration tests.

### PR #110 — Forge history identity

Already merged:

- both item IDs stored in in-memory history;
- item resolution by ID instead of ambiguous name-only lookup;
- name fallback for older call sites.

These are baseline evidence, not proof of complete Equipment Upgrade parity.

---

## 5. Validation matrix

| Area | Reference behaviour | Current result |
|---|---|---|
| Classification | Class 1/2/3/4 caps: 1/2/3/10 | **confirmed statically**; runtime loading pending |
| Imbuements | Imbued equipment cannot enter Forge | **confirmed statically** in list and server item lookup |
| Initial Dust limit | 100 | **confirmed statically** in schema |
| Dust limit upgrade | Cost = current limit − 75; maximum 325 | formula confirmed; **F-001 open:** configured/fallback maximum 225 |
| Dust conversion | 60 Dust → 3 Slivers | **confirmed statically**; failure tests pending |
| Core conversion | 50 Slivers → 1 Core | **confirmed statically**; failure tests pending |
| Influenced scaling | 1–5 stacks; HP/damage/XP and 1–3 Dust per stack | HP/damage/XP confirmed statically; Dust reward remediation present, runtime pending |
| Fiendish scaling/lifecycle | strength of 15 stacks; four alive; 270 s replacement; one-hour lifetime | default path confirmed statically; **F-002/F-009 open** |
| Premium Dust | no Dust without Premium | **F-006 remediated in branch**; runtime test pending |
| Party Dust | one amount for eligible shared-experience members with logout block | **F-007/F-013 remediated in branch**; range/logout runtime boundaries pending |
| Dust cap feedback | report actual credited amount | **F-008 remediated in branch**; runtime test pending |
| Regular Fusion eligibility | identical item IDs and equal tier | **F-003 open:** item identity not revalidated server-side |
| Fusion success | 50%; optional core raises to 65% | confirmed statically; statistical test pending |
| Fusion failure | optional core modifies tier-loss/destruction chance | implementation located; complete outcome matrix pending |
| Fusion costs | class/tier gold + Dust + optional cores | **confirmed statically**; accounting tests pending |
| Fusion bonuses | eight documented success bonuses | **F-014–F-016 open:** eighth bonus absent, +2 tier cap wrong, rolls not tier-aware |
| Fusion history | exact result for each bonus and both partner IDs | **F-017 open:** several bonus/Convergence outcomes are described incorrectly |
| Forge result protocol/client | payload and OTClient must represent every result exactly | **F-018/F-019 open:** OTClient omits bonus types 5–8 and decreased-tier payload displays wrong tier |
| Convergence Fusion | class 4; different IDs; same normalized slot/tier; guaranteed; no bonus | **F-004 open:** restrictions incomplete server-side |
| Regular Transfer | same class; receiver tier 0; result donor tier − 1 | partially confirmed by PR #89; gameplay test pending |
| Convergence Transfer | class 4; no tier loss; source destroyed; cross-slot allowed | **F-005 open:** class 4 not enforced server-side |
| Onslaught | tier chance; triggered basic attack +60% damage | formula/combat path confirmed statically; runtime/AoE pending |
| Ruse | tier dodge chance | formula path confirmed; **F-010 precision risk** |
| Momentum | tier chance; eligible cooldowns −2 s | formula/reduction confirmed; **F-012 open** |
| Transcendence | offensive-action check; seven-second Avatar; no overlap with Avatar spell | formula/window/duration confirmed; **F-011 open** |
| Amplification | multiplicative increase to Forge effect chances | base table and four paths confirmed; event ordering/runtime pending |
| Transaction safety | rejected operations consume nothing | not proven; malformed-request integration tests required |

---

## 6. Confirmed implementation paths

### Configuration and tier data

- `config.lua.dist`
- `src/config/configmanager.cpp`
- `data/scripts/systems/item_tiers.lua`
- `src/items/items_classification.hpp`
- `data/libs/functions/register_item_tier.lua`

### Forge operations and protocol

- `src/game/game.cpp`
- `src/creatures/players/player.cpp`
- `src/server/network/protocol/protocolgame.cpp`
- `src/utils/tools.cpp`
- `src/game/functions/forge_transfer_policy.hpp`

### Creatures and rewards

- `src/creatures/monsters/monster.cpp`
- `src/creatures/monsters/monster.hpp`
- `data/libs/systems/exaltation_forge.lua`
- `data/scripts/creaturescripts/monster/forge_kill.lua`
- `src/creatures/players/grouping/party.cpp`

### Equipment effects

- `src/items/item.cpp`
- `src/creatures/combat/combat.cpp`
- `src/creatures/players/player.cpp`
- `data/scripts/spells/support/avatar_of_*.lua`
- Lua binding for `Player:avatarTimer`

### Client result presentation

- `opentibiabr/otclient/modules/game_forge/game_forge.lua`
- `opentibiabr/otclient/modules/game_forge/game_forge_helpers.lua`
- `opentibiabr/otclient/src/client/protocolgameparse.cpp`

### Persistence and tests

- `schema.sql`
- Forge player load/save paths
- `tests/unit/players/forge_test.cpp`
- `tests/integration/game/forge_it.cpp`

---

## 7. Findings and remediation status

### F-001 — maximum Dust capacity remains 225

**Severity:** medium. **Status:** open. **Evidence:** B–C.

`config.lua.dist` and the `ConfigManager` fallback use 225, while the selected post-February-2023 behaviour uses 325.

**Required:** update both sources and test 324 → 325 plus rejection above 325.

### F-002 — Fiendish limit defaults are inconsistent

**Severity:** low/medium. **Status:** open. **Evidence:** B.

Distributed configuration uses 4; engine fallback and an unused legacy Lua value use 3.

**Required:** align active defaults with 4, remove/document dead legacy state, test startup without the key.

### F-003 — regular Fusion identity relies on client filtering

**Severity:** high. **Status:** open. **Evidence:** C.

The handler does not independently require `firstItemId == secondItemId`. An integration test currently accepts two different item IDs for regular Fusion.

**Required:** add a pure server-side policy before mutation and replace the permissive test.

### F-004 — Convergence Fusion restrictions are incomplete server-side

**Severity:** high. **Status:** open. **Evidence:** C.

Class 4, different item IDs and same normalized slot are enforced in the client list but not fully repeated in the operation handler.

**Required:** enforce class 4 on both items, different IDs, equal tier and normalized slot before mutation.

### F-005 — Convergence Transfer does not enforce class 4

**Severity:** high. **Status:** open. **Evidence:** C.

Matching classifications and donor tier are checked, but convergence does not additionally require classification 4.

**Required:** extend the Transfer policy and add malformed-request tests.

### F-006 — Dust was awarded without Premium

**Severity:** high. **Status:** remediated; runtime test pending. **Evidence:** C.

The former solo and party paths credited Dust without checking Premium.

**Change:** centralized `ForgeMonster:creditDust()` now requires `player:getPremiumDays() > 0`. Fiendish Sliver creation remains independent of Premium.

### F-007 — party Dust eligibility lacked an explicit current logout-block check

**Severity:** high. **Status:** remediated statically; boundary tests pending. **Evidence:** C.

The shared-experience engine controls activity, level and 30×30×1 range. The reward path now additionally requires `CONDITION_INFIGHT` for every recipient.

**Tests required:** active/inactive member, 30/31 fields, same floor and ±1/±2 floors, leader and summon kill.

### F-008 — Dust cap message reported the requested amount

**Severity:** low. **Status:** remediated; runtime test pending. **Evidence:** C.

When a reward crossed capacity, less Dust was credited than reported.

**Change:** `creditedAmount = min(amount, limit - total)` is used for mutation and success messaging.

### F-009 — Fiendish Slivers ignore creature difficulty

**Severity:** medium. **Status:** open. **Evidence:** C.

Every Fiendish corpse receives a uniform random value between global minimum and maximum; creature difficulty is not used.

**Required:** obtain the exact versioned difficulty mapping from an authoritative source before implementation. Do not invent a formula.

### F-010 — Ruse truncates fractional basis points

**Severity:** low. **Status:** open precision question. **Evidence:** B–C.

The floating-point percentage is multiplied by 100 and cast to `uint16_t`, truncating instead of rounding; Amplification is truncated again.

**Required:** confirm whether displayed two-decimal values or hidden formula precision is authoritative before changing it.

### F-011 — Transcendence can overlap the Avatar spell

**Severity:** medium/high. **Status:** open. **Evidence:** C.

Avatar spells set `AVATAR_SPELL`, but `triggerTranscendence()` checks only `AVATAR_FORGE` before creating the seven-second Forge Avatar.

**Required:** block while either timer is active; test spell→Forge, Forge→Forge and post-expiry transitions.

### F-012 — Momentum can display a false trigger

**Severity:** low. **Status:** open. **Evidence:** C.

`triggered` is set for every condition before confirming it is an eligible spell/offensive group cooldown. The effect/message can appear when no cooldown changed.

**Required:** set `triggered` only after an eligible cooldown is reduced.

### F-013 — party members received independently randomized Dust

**Severity:** medium/high. **Status:** remediated; runtime test pending. **Evidence:** C.

The old loop called `math.random()` separately per recipient.

**Change:** one amount is rolled per creature death and passed to every eligible recipient.

### F-014 — the Dust-refill success bonus is not implemented

**Severity:** high gameplay/economy mismatch. **Status:** open. **Evidence:** C.

The documented eighth success bonus refills Dust to the character's maximum. `forgeBonus()` generates only values 0–7 and no successful path refills Dust. Value 8 is instead assigned after a failed Fusion when the second item keeps its tier.

**Required:** separate the failed-Fusion retained-tier outcome from the eighth success bonus, implement the Dust refill, define an unambiguous protocol representation and add deterministic tests.

### F-015 — the +2-tier bonus uses classification ID as the tier cap

**Severity:** high gameplay mismatch. **Status:** open. **Evidence:** C.

The application condition is `tier + 2 <= firstForgedItem->getClassification()`. That accidentally matches caps of classes 1–3 but treats class 4 as if its maximum tier were 4 instead of 10. A class-4 item at tier 3 or above can be reported as receiving bonus 7 while receiving only the normal +1 result.

**Required:** resolve the actual `ItemClassification` tier table/cap and reject or reroll the bonus when +2 would exceed that cap.

### F-016 — Fusion bonus selection is not tier-aware

**Severity:** medium/high semantic mismatch. **Status:** open. **Evidence:** C.

The bonus is rolled before item eligibility and current tier are known to the bonus selector. A decreased-tier retained item can therefore be selected at tier 0, and +2 tiers can be selected where the class cap prevents the documented result.

**Required:** select from outcomes valid for the concrete item/class/tier or explicitly map impossible outcomes to the documented fallback; cover every boundary tier.

### F-017 — Fusion history misreports Convergence and bonus results

**Severity:** high audit/history mismatch. **Status:** open. **Evidence:** C.

The Fusion history renderer resolves only the first item type and uses it for both partners. Successful history always says the first item gained one tier and treats the second item as consumed except when `bonus == 8`. This is wrong for Convergence with different IDs and for retained/decreased/increased second-item bonuses and +2 tiers.

**Required:** derive history from explicit result item IDs/tiers rather than reinterpreting the bonus code. Add one history assertion per outcome.

### F-018 — OTClient renders only bonus types 1–4

**Severity:** medium/high client mismatch. **Status:** open in `opentibiabr/otclient`. **Evidence:** C.

The current Forge result UI provides labels/details only for bonus values 1, 2, 3 and 4. Values 5–8 still open the bonus step but have no complete result presentation.

**Required:** define shared bonus semantics with Canary and render all supported outcomes with the actual returned item/tier and Dust result.

### F-019 — decreased-tier bonus payload/UI reports the wrong tier

**Severity:** medium client/protocol mismatch. **Status:** open. **Evidence:** C.

For bonus 4 the server changes the retained second item from tier `t` to `t−1`, but `sendForgeResult()` sends the original left tier as the bonus-item tier. OTClient derives its displayed tier from the normal result tier (`t+1−1 = t`), so the UI displays tier `t` while the retained item is tier `t−1`.

**Required:** send explicit result-item ID/tier values and make OTClient display those values directly. Add protocol round-trip tests.

---

## 8. Required regression scenarios

1. regular Fusion accepts identical IDs and rejects different IDs;
2. rejected Fusion/Transfer requests leave items, Dust, cores and gold unchanged;
3. Convergence Fusion accepts only different class-4 items of equal tier in the same normalized slot;
4. Convergence Transfer rejects classes 1–3 and preserves PR #89 normal Transfer behaviour;
5. Dust capacity stops at 325 with the current-limit-minus-75 price;
6. 60 Dust → 3 Slivers and 50 Slivers → 1 Core fail atomically when resources are insufficient;
7. non-Premium characters receive no Dust but can loot valid Fiendish Slivers;
8. one Dust roll is shared by all eligible party recipients;
9. party recipients satisfy shared-experience range plus current `CONDITION_INFIGHT`;
10. Dust cap messaging reports the credited amount;
11. Fiendish Slivers follow the confirmed difficulty rule;
12. Transcendence cannot activate during Avatar spell and lasts seven seconds;
13. Momentum reports a trigger only when an eligible cooldown changed;
14. tier 1–10 chance tables and Amplification are tested;
15. every Fusion success bonus is forced deterministically and checked for item tiers/resources/history/protocol;
16. impossible boundary bonuses are never reported without their documented effect;
17. OTClient displays all server bonus outcomes from a captured packet fixture.

---

## 9. Work log

### 2026-07-12 — initialization

- Read the parent methodology.
- Created `validation/equipment-upgrade` and this dedicated document.
- Identified PRs #89/#110 and the same-object removal guard as baseline.

No production code changed.

### 2026-07-12 — audit pass 1: operations and protocol

- Reconstructed tier, price, core and Dust tables.
- Confirmed schema default, conversions and imbuement rejection.
- Traced packet-controlled fields through Fusion and Transfer.
- Confirmed server-generated success/bonus rolls.
- Recorded F-001 through F-005.

No production code changed.

### 2026-07-12 — audit pass 2: creatures and effects

- Captured current Forge-related C++, Lua, SQL and test sources through a temporary read-only CI artifact; removed the exporter afterward.
- Confirmed stack, HP, damage, XP, Fiendish replacement and lifetime paths.
- Traced Dust/Sliver rewards and all five item-effect formulas.
- Confirmed separate Avatar spell/Forge timers.
- Recorded F-006 through F-012.

No production code changed.

### 2026-07-12 — remediation pass 1: Dust rewards

Changed `data/libs/systems/exaltation_forge.lua`:

- added a single player-killer resolver for direct and summon kills;
- centralized Premium, capacity, mutation and messaging in `creditDust`;
- generated one Dust amount per kill instead of per recipient;
- retained the engine's shared-experience eligibility/range gate;
- added explicit `CONDITION_INFIGHT` validation for each party recipient;
- reported the amount actually credited at the Dust cap.

Updated F-006, F-007, F-008 and F-013. Formatter and repository agent-tool workflows passed; the superseded full CI run was cancelled by workflow concurrency after later documentation commits. Runtime/gameplay evidence is still pending.

### 2026-07-12 — audit pass 3: Fusion bonuses, history and OTClient

- Traced the bonus roll from `Game::playerForgeFuseItems()` through `forgeBonus()`, item mutation, history, packet serialization and OTClient rendering.
- Confirmed that the successful bonus generator has only seven outcomes and does not refill Dust.
- Found the class-4 +2-tier cap bug and tier-unaware bonus selection.
- Found incorrect Fusion history rendering for Convergence and retained/+2 outcomes.
- Found incomplete OTClient presentation for bonus values 5–8 and a tier mismatch for the decreased-tier result.
- Confirmed existing Forge integration tests do not cover the complete bonus matrix.
- Recorded F-014 through F-019.

No production code changed in this pass.

---

## 10. Next actions

1. add focused runtime/integration coverage for the Dust reward change;
2. implement high-severity server-authority fixes F-003 through F-005 before resource mutation;
3. redesign bonus result data and implement F-014 through F-019 jointly across Canary and OTClient;
4. implement configuration corrections F-001/F-002;
5. establish the authoritative Fiendish difficulty-to-Sliver rule for F-009;
6. fix F-011/F-012 and add effect tests;
7. resolve F-010 only after confirming intended precision;
8. run the normal build/test matrix;
9. perform runtime and gameplay validation before declaring parity.

---

## 11. Handoff

Continue on `validation/equipment-upgrade` and read this file plus `OTS_AI_WORLD_VALIDATION_PROJECT.md` first. Preserve PR #89/#110 behaviour. F-006/F-007/F-008/F-013 have code changes but still require runtime evidence. F-001–F-005 and F-009–F-012 remain open. F-014–F-019 require a coordinated Canary/OTClient result model; do not patch only the labels. Static evidence reaches B–C for explicitly marked rows; full Equipment Upgrade parity has not been established.