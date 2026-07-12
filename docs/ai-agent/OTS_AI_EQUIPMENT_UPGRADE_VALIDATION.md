# OTS AI Equipment Upgrade Validation — status, findings and handoff

> **Status date:** 2026-07-12  
> **Repository:** `blakinio/canary`  
> **Working branch:** `validation/equipment-upgrade`  
> **Current pull request:** `#177`  
> **Primary comparison page:** `https://tibia.fandom.com/wiki/Equipment_Upgrade`  
> **Parent methodology:** `docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md`  
> **Current phase:** static and semantic validation; remediation and runtime evidence remain open  
> **Rule:** every implementation change made during this validation must be recorded in this file in the same commit or immediately following commit.

---

## 1. Goal

Validate Canary's complete Equipment Upgrade / Exaltation Forge implementation against documented Tibia behaviour, without treating code presence, a successful build or a client-side list as proof of gameplay parity.

The validation covers:

1. upgrade classifications and tier limits;
2. upgradable-item metadata and imbuement restrictions;
3. Dust capacity, acquisition and conversions;
4. Slivers and Exalted Cores;
5. influenced and fiendish creature spawning, scaling, rewards and restrictions;
6. regular Fusion and all bonus outcomes;
7. Convergence Fusion;
8. regular and Convergence Transfer;
9. Onslaught, Ruse, Momentum, Transcendence and Amplification;
10. client protocol data and server authority;
11. persistence, Forge history and resource accounting;
12. malformed or stale packet rejection and transaction safety;
13. focused unit, integration, runtime and gameplay tests.

---

## 2. Evidence levels

The project-wide validation layers from `OTS_AI_WORLD_VALIDATION_PROJECT.md` are applied here as follows:

- **A — structural:** relevant files and configurations load and compile;
- **B — static references:** classifications, tiers, config keys, metadata and protocol handlers resolve;
- **C — semantic parity:** formulas, eligibility, costs, outcomes and side effects match the reference behaviour;
- **D — runtime:** the server starts and Forge systems register without critical errors;
- **E — gameplay:** test characters execute each flow and receive the exact expected result;
- **F — regression:** automated tests preserve confirmed behaviour and reject malformed requests.

A lower layer must not be reported as proof of a higher layer.

---

## 3. Safety and scope rules

- Do not modify maps, client assets or binary item files for an unproven hypothesis.
- Do not change prices, probabilities or formulas without evidence.
- Do not infer official behaviour solely from variable names, UI filtering or existing tests.
- Treat item IDs, tiers, action flags and convergence flags received from the client as untrusted.
- Validate before removing items, Dust, cores or gold.
- Prefer the smallest independently testable correction.
- Preserve unrelated work already merged to `main`.
- Record unresolved questions rather than guessing.

---

## 4. Existing baseline work that must be preserved

### PR #89 — normal Transfer rules, costs and history

Already merged before this validation. It introduced or corrected:

- compatibility based on matching upgrade classification rather than equipment slot;
- server-side validation of matching classifications and valid donor tiers;
- donor-tier-based price and core lookup;
- correct resulting tier calculation;
- actual Dust, core and gold values in history;
- correct donor and receiver rendering;
- focused Transfer policy and integration tests.

### PR #110 — Forge history item identity

Already merged before this validation. It introduced or corrected:

- storing both item IDs in in-memory Forge history;
- resolving item types by ID instead of ambiguous name-only lookup;
- fallback name lookup for older call sites.

### Upstream same-object removal correction

The current baseline also contains the upstream guard against removing the same item object twice during Forge operations. This must remain intact when Fusion and Convergence validation is changed.

These changes are baseline evidence, not proof that the complete Equipment Upgrade system is correct.

---

## 5. Reference behaviour inventory and current evidence

| Area | Reference behaviour | Current evidence/status |
|---|---|---|
| Classification | Class 1/2/3/4 tier caps are 1/2/3/10 | **confirmed statically** in the registered tier table; runtime loading still pending |
| Imbuements | Equipment cannot be used in Forge while imbued | **confirmed statically** in both Forge-window filtering and server item lookup |
| Dust initial limit | Characters start with capacity 100 | **confirmed statically** in database schema |
| Dust capacity upgrade | Cost is current limit minus 75; maximum 325 | formula confirmed; **mismatch F-001:** configured and fallback maximum are 225 |
| Dust conversion | 60 Dust creates 3 Slivers | **confirmed statically**; mutation/failure tests pending |
| Core conversion | 50 Slivers creates 1 Exalted Core | **confirmed statically**; mutation/failure tests pending |
| Influenced creatures | 1–5 stacks with stack-dependent HP, damage, XP and Dust | stack range and HP/damage/XP multipliers **confirmed statically**; reward eligibility mismatches F-006/F-007 remain |
| Fiendish creatures | Strength equivalent to 15 stacks; maximum four alive; replacement/lifetime rules | stack 15, HP/damage/XP, configured cap 4, 270-second replacement and one-hour default lifetime confirmed; **mismatch F-002** and Sliver mismatch F-009 remain |
| Premium restriction | No Dust reward without Premium | **mismatch F-006:** current reward script has no Premium check |
| Party Dust eligibility | Shared-experience members must meet combat/range/floor eligibility | **mismatch F-007:** all leader/members are rewarded when shared experience is enabled |
| Regular Fusion eligibility | Two identical items of equal tier | equal tier/item availability checked; **mismatch F-003:** identical item ID is not revalidated server-side |
| Fusion success | Base 50%; optional core raises to 65% | configuration and server-side random outcome path confirmed statically; statistical/runtime test pending |
| Fusion failure | Optional core changes the tier-loss/destruction risk | implementation located; exact outcome matrix and boundary tests pending |
| Fusion costs | Class/tier gold table plus Dust and optional cores | **confirmed statically** against the documented tables; accounting tests pending |
| Fusion bonuses | Eight documented bonus outcomes | **not yet validated** |
| Convergence Fusion | Class 4 only; different items, same normalized body slot and equal tier; guaranteed; no bonus | client list filters class/slot; **mismatch F-004:** these restrictions are not fully revalidated server-side |
| Regular Transfer | Same classification; receiver tier 0; source destroyed; result donor tier minus one | partially confirmed by PR #89 and focused tests; full gameplay test pending |
| Convergence Transfer | Class 4 only; no tier loss; may cross body slots; source destroyed | result/cost path located; **mismatch F-005:** class 4 is not enforced server-side |
| Onslaught | Weapon chance table; triggered basic attack gains 60% damage | formula coefficients and combat application **confirmed statically**; AoE and runtime sampling pending |
| Ruse | Armor dodge chance table | formula path confirmed; **precision risk F-010:** probability is truncated to integer basis points rather than rounded |
| Momentum | Helmet chance table; reduce eligible cooldowns by two seconds | formula and two-second reduction confirmed statically; **semantic risk F-012:** visual trigger can occur without an eligible cooldown being changed |
| Transcendence | Legs chance table; check after offensive action; seven-second Avatar; cannot overlap Avatar spell | formula, two-second action window and duration confirmed; **mismatch F-011:** only the Forge timer is checked |
| Amplification | Boots multiplicatively increase other Forge effect chances | base table and multiplicative use for Ruse, Onslaught, Momentum and Transcendence confirmed; event-bonus ordering/runtime tests pending |
| History | Exact partners, result, costs, bonus and success state | partially covered by PRs #89 and #110; Fusion/Convergence cases pending |
| Transaction safety | Rejected or failed operations cannot partially consume resources | **not yet proven**; malformed-packet integration tests required |

---

## 6. Confirmed implementation paths

### Configuration and tier data

- `config.lua.dist`
- `src/config/configmanager.cpp`
- `data/scripts/systems/item_tiers.lua`
- `src/items/items_classification.hpp`
- `src/lua/functions/items/item_classification_functions.cpp`
- `data/libs/functions/register_item_tier.lua`

### Protocol and operation handling

- `src/server/network/protocol/protocolgame.cpp`
- `src/creatures/players/player.cpp`
- `src/game/game.cpp`
- `src/game/functions/forge_transfer_policy.hpp`

### Creature scaling, rewards and lifecycle

- `src/creatures/monsters/monster.cpp`
- `src/creatures/monsters/monster.hpp`
- `data/libs/systems/exaltation_forge.lua`
- `data/scripts/creaturescripts/monster/forge_kill.lua`
- Forge creature-event and datapack registration paths

### Equipment effects

- `src/items/item.cpp`
- `src/creatures/combat/combat.cpp`
- `src/creatures/players/player.cpp`
- `data/scripts/spells/support/avatar_of_*.lua`
- Lua binding for `Player:avatarTimer`

### Persistence and tests

- `schema.sql`
- player load/save paths for Forge resources
- `tests/unit/players/forge_test.cpp`
- `tests/integration/game/forge_it.cpp`

---

## 7. Open findings

### F-001 — maximum Dust capacity remains 225

**Severity:** medium gameplay mismatch  
**Evidence level:** B–C  
**Observed:**

- `config.lua.dist` sets `forgeMaxDust = 225`;
- `ConfigManager` also falls back to 225;
- the protocol sends this configured value to the client;
- the documented post-February-2023 maximum is 325.

**Required correction:** change both the distributed configuration and engine fallback to 325, then test capacity 324 → 325 and rejection above 325.

### F-002 — Fiendish fallback limit differs from configured limit

**Severity:** low/medium configuration inconsistency  
**Evidence level:** B  
**Observed:** distributed configuration uses 4 while the engine fallback uses 3. The Lua helper also retains an unused legacy `maxFiendish = 3` value.

**Required correction:** align active fallback/default sources with the selected Tibia version, remove or document stale dead configuration, then test startup without the Lua key and population refresh.

### F-003 — regular Fusion identity relies on the client list

**Severity:** high server-authority issue  
**Evidence level:** C  
**Observed:** the Forge window only lists pairs of identical item IDs, but the operation handler does not independently require `firstItemId == secondItemId` before mutation. An existing integration test currently uses two different item IDs for a successful regular Fusion, which codifies the wrong eligibility rule.

**Risk:** a crafted packet may request a regular Fusion using two different item types that otherwise satisfy tier and availability checks.

**Required correction:** add a pure server-side Fusion eligibility policy, reject the request before mutation and replace the permissive integration case.

### F-004 — Convergence Fusion restrictions are incomplete server-side

**Severity:** high server-authority issue  
**Evidence level:** C  
**Observed:** class 4, different item IDs and same normalized slot are enforced when constructing the client list, but are not all repeated in the operation handler.

**Risk:** a crafted request may bypass client-side class, identity or slot filtering.

**Required correction:** enforce class 4 on both items, different item IDs, equal tier and matching normalized slot before mutation. Two-handed hand items must use the same normalization as the protocol list.

### F-005 — Convergence Transfer does not enforce class 4

**Severity:** high server-authority issue  
**Evidence level:** C  
**Observed:** the Transfer handler validates matching classifications and donor tier, but the convergence flag does not additionally require classification 4.

**Risk:** a crafted request may use Convergence Transfer for classes 1–3.

**Required correction:** extend the Transfer policy with an explicit convergence classification rule and add focused regression tests.

### F-006 — Dust is awarded without Premium

**Severity:** high gameplay/economy mismatch  
**Evidence level:** C  
**Observed:** `ForgeMonster:onDeath` calculates and credits Dust without checking the recipient's Premium status in either the solo or party path.

**Required correction:** centralize recipient eligibility and reject Dust credit for non-Premium players while leaving Fiendish Sliver drops independent of Premium.

### F-007 — party Dust eligibility is broader than the reference rule

**Severity:** high gameplay/economy mismatch  
**Evidence level:** C  
**Observed:** when shared experience is enabled, the script adds the party leader and every party member to the reward list. It does not verify logout/combat participation state, distance, floor difference or the normal experience-sharing range for each recipient.

**Required correction:** calculate eligible recipients from the actual shared-experience participation/range rules and add boundary tests for 30/31 tiles and adjacent floors.

### F-008 — Dust cap message reports the requested amount, not the credited amount

**Severity:** low feedback mismatch  
**Evidence level:** C  
**Observed:** when a reward would exceed the player's Dust limit, the script credits only the remaining capacity but still reports the original random amount as received.

**Required correction:** compute `creditedAmount` once, use it for mutation and messaging, and test a reward at `limit - 1`.

### F-009 — Fiendish Sliver quantity ignores creature difficulty

**Severity:** medium reward mismatch  
**Evidence level:** C  
**Observed:** every Fiendish corpse receives a uniform random amount between global `forgeMinSlivers` and `forgeMaxSlivers`; no creature difficulty input is used.

**Required correction:** determine the exact versioned difficulty-to-Sliver rule from an authoritative reference before implementation. Do not invent a formula.

### F-010 — Ruse runtime chance truncates fractional basis points

**Severity:** low probability precision risk  
**Evidence level:** B–C, authoritative runtime confirmation required  
**Observed:** the item formula returns a floating-point percentage, but `Player::getDodgeChance()` converts `percentage * 100` directly to `uint16_t`, truncating rather than rounding. Amplification is truncated again when added.

**Required action:** confirm whether the intended server probability is the displayed two-decimal table or a hidden higher-precision formula. If the documented two-decimal values are authoritative, use explicit rounding and add all-tier tests.

### F-011 — Transcendence can overlap the Avatar spell

**Severity:** medium/high effect-rule mismatch  
**Evidence level:** C  
**Observed:** Avatar spells set `WheelOnThink_t::AVATAR_SPELL`, but `Player::triggerTranscendence()` only blocks while `AVATAR_FORGE` is active. It never checks the active Avatar-spell timer before creating the seven-second Forge Avatar condition.

**Required correction:** block Transcendence while either Avatar timer is active and add tests for spell→Forge, Forge→Forge and post-expiry transitions.

### F-012 — Momentum can show a false-positive trigger

**Severity:** low feedback/semantic risk  
**Evidence level:** C  
**Observed:** `triggered` is set for every condition visited before checking whether that condition is an eligible spell or offensive group cooldown. The hourglass/message may therefore appear even when no cooldown was reduced.

**Required correction:** set `triggered = true` only after an eligible cooldown is changed; test players with only `CONDITION_INFIGHT` and with support-only group cooldowns.

---

## 8. Required regression scenarios

1. regular Fusion accepts identical item IDs and rejects different IDs;
2. regular Fusion rejects mismatched tiers, imbued items and missing quantities without consuming resources;
3. Convergence Fusion accepts only two different class-4 items of equal tier in the same normalized slot;
4. Convergence Fusion rejects classes 1–3 and cross-slot requests without consuming resources;
5. normal Transfer preserves PR #89 behaviour;
6. Convergence Transfer rejects classes 1–3 and accepts valid class-4 donors from tier 1;
7. every rejected packet leaves both items, Dust, cores and bank balance unchanged;
8. Dust capacity stops at 325 and uses the current-limit-minus-75 price;
9. conversions reject insufficient Dust/items without partial mutation;
10. non-Premium characters receive no Dust but can still loot valid Fiendish Slivers;
11. party Dust recipients satisfy shared-experience combat/range/floor rules;
12. Dust cap messaging reports the amount actually credited;
13. Fiendish Slivers follow the confirmed difficulty rule;
14. Transcendence cannot activate during an Avatar spell and expires after seven seconds;
15. Momentum reports a trigger only when at least one eligible cooldown changed;
16. effect chance tables and Amplification are tested for tiers 1–10;
17. history stores exact item IDs, tiers, costs, result, bonus and success state.

---

## 9. Work log

### 2026-07-12 — validation initialized

- Read the parent methodology and adopted its layered evidence model.
- Created branch `validation/equipment-upgrade`.
- Created this dedicated validation/handoff document beside the parent project file.
- Identified merged baseline fixes in PRs #89 and #110.
- Began source inventory and external behaviour extraction.

No production code was changed in this step.

### 2026-07-12 — static and semantic audit pass 1

- Reconstructed classification, price, core and Dust tables used by the protocol and operation handlers.
- Confirmed the database starting Dust capacity and both conversion ratios.
- Confirmed imbuement rejection in the client list and server item lookup.
- Traced packet-controlled fields through regular and Convergence Fusion/Transfer.
- Confirmed that success and bonus rolls are generated by the server, not accepted from the client.
- Confirmed influenced/fiendish stack assignment and HP/damage multipliers.
- Recorded findings F-001 through F-005.

No production-code correction is claimed in this pass.

### 2026-07-12 — static and semantic audit pass 2

- Used a temporary read-only CI exporter to capture the current branch versions of Forge-related C++, Lua, SQL and test sources; the exporter was removed immediately after the audit.
- Confirmed influenced/fiendish XP multipliers, Fiendish replacement delay and default lifetime.
- Traced solo and party Dust credit paths and found missing Premium and recipient-range validation.
- Traced Fiendish Sliver creation and confirmed it uses only global minimum/maximum values.
- Reconstructed all tier 1–10 chance tables from the configured quadratic formulas.
- Confirmed static Onslaught damage, Momentum cooldown reduction, Transcendence duration/action window and multiplicative Amplification paths.
- Confirmed Avatar spells and Transcendence use separate timers and found the missing overlap guard.
- Recorded findings F-006 through F-012.
- Removed all temporary exporter/scaffolding files; the intended pull-request diff remains this validation document only.

No production-code correction is claimed in this pass. Static evidence now reaches B–C for the explicitly marked rows; runtime/gameplay evidence remains absent.

---

## 10. Next actions

1. implement high-severity server-authority fixes F-003 through F-005 before resource mutation;
2. implement Dust eligibility/accounting fixes F-006 through F-008 with shared-recipient tests;
3. implement configuration corrections F-001/F-002;
4. establish the authoritative Fiendish difficulty-to-Sliver rule before addressing F-009;
5. fix the confirmed Transcendence and Momentum control-flow issues F-011/F-012;
6. resolve Ruse precision only after confirming the intended probability representation;
7. add focused unit and malformed-request integration tests;
8. run the normal build/test matrix and inspect all Forge-related failures;
9. validate all eight Fusion bonus outcomes and Forge history packets;
10. perform runtime and gameplay validation before declaring parity.

---

## 11. Handoff

Continue on `validation/equipment-upgrade` and read this document plus `OTS_AI_WORLD_VALIDATION_PROJECT.md` first. Preserve the behaviour already merged in PRs #89 and #110. Do not describe F-001 through F-012 as fixed until production code and regression tests are present in the branch. Static evidence currently reaches levels B–C for the explicitly marked rows; runtime, gameplay and complete regression evidence remain open. Full Equipment Upgrade parity has not been established.