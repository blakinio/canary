# OTS AI Equipment Upgrade Validation — current state and durable handoff

> **Status date:** 2026-07-13  
> **Repository:** `blakinio/canary`  
> **Current documentation branch:** `fix/equipment-upgrade-validation-2`  
> **Current documentation PR:** `#241`  
> **Task record:** `docs/agents/tasks/active/CAN-20260713-equipment-upgrade-handoff-refresh.md`  
> **Primary comparison page:** `https://tibia.fandom.com/wiki/Equipment_Upgrade`  
> **Parent methodology:** `docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md`  
> **Current phase:** current-main static/semantic reverification and handoff only; no gameplay remediation in this PR  
> **Parity claim:** full Equipment Upgrade / Exaltation Forge parity is **not** established.

---

## 1. Goal and scope

This document is the durable evidence and handoff for Canary's Equipment Upgrade / Exaltation Forge validation. It separates structural, static, semantic, compiled-regression, runtime, gameplay and physical-client E2E evidence. A lower evidence level must never be presented as proof of a higher one.

Validated areas:

1. classifications, tier caps and item eligibility;
2. Dust, Slivers and Exalted Cores;
3. influenced/fiendish spawn, rewards and lifecycle;
4. regular and Convergence Fusion/Transfer;
5. Fusion bonuses, history, result packets and transaction safety;
6. Onslaught, Ruse, Momentum, Transcendence and Amplification;
7. Canary ↔ maintained `blakinio/otclient` compatibility;
8. unit, integration, runtime, gameplay and E2E proof boundaries.

This refresh changes documentation only. It does not fix a finding, change runtime behavior, add E2E infrastructure or modify either OTClient repository.

---

## 2. Evidence levels

| Level | Meaning | Examples |
|---|---|---|
| A — structural | File/configuration/schema can be parsed or built. | syntax, load, compile |
| B — static | Identifiers, metadata, registrations and call paths resolve. | config key, function, packet field, handler |
| C — semantic | Current code can be compared with a stated rule or invariant. | eligibility, formula, mutation order, displayed result |
| D — compiled regression | An automated compiled test exercises the claimed behavior. | focused C++ unit/integration test |
| E — runtime | Canary starts and the relevant systems register/run without critical errors. | server/runtime smoke |
| F — gameplay | A test character executes the real feature flow and state is verified. | real Fusion/Transfer/Dust scenario |
| G — physical-client E2E | Maintained OTClient and Canary execute the full user flow. | login, UI action, packet/result, persistence |

No focused Forge gameplay or physical-client E2E proof is recorded for the current main in this document.

---

## Current repository state

| Field | Current value |
|---|---|
| Repository | `blakinio/canary` |
| Current main SHA at refresh start | `d4eeab3db322f26ee72d7f0ad958d35dc9bd007d` |
| Updated | 2026-07-13 |
| Open Forge implementation PRs | none found |
| Open Forge documentation PR | `#241`, branch `fix/equipment-upgrade-validation-2` |
| Active Forge task | `CAN-20260713-equipment-upgrade-handoff-refresh` |
| Last merged Forge PR | `#177`, merge `f1d217c43e8e302978f533212e6aa9d1ce2b77c8` |
| Historical validation branch | `validation/equipment-upgrade`; no current branch match; do not continue or recreate it |
| Current validation state | 21 findings remain open or version-decision-gated; F-007/F-008/F-013 retain partial production remediation but remain runtime-untested |
| Maintained client target | `blakinio/otclient` |
| Reference-only client | `opentibiabr/otclient`; never write to it |

The report previously presented `validation/equipment-upgrade` and PR #177 as active. That state was historical. PR #177 is merged and its old branch is not a continuation target.

### Current open-work review

- Repository open-PR review found no active Forge gameplay implementation PR.
- PR #222 establishes universal E2E ownership for future feature suites; it does not test or remediate Forge.
- `docs/agents/ACTIVE_WORK.md` was read as a potentially stale convenience index and was not edited. It contained no Forge row before this task.
- This documentation task owns only this report and its task record.

---

## 3. Historical baseline that must be preserved

### PR #89 — normal Transfer rules, costs and history

- merged: 2026-07-12;
- merge commit: `209289d38e64aafe7ce3e036867bb632cd0363b8`;
- head: `570d6e077c02107eb712a4ff214cf4442d6c91d8`.

Preserved behavior:

- normal Transfer compatibility uses upgrade classification, not equipment slot;
- donor-tier and matching-classification rules are checked server-side;
- configured cost resources use the donor tier;
- result tier is calculated separately;
- actual Dust/core/gold values are stored in history;
- donor/receiver/result rendering and focused tests were corrected.

Relevant current paths:

- `src/game/functions/forge_transfer_policy.hpp`;
- `src/creatures/players/player.cpp` — `Player::forgeTransferItemTier`;
- `src/server/network/protocol/protocolgame.cpp` — Forge list/result payloads;
- `tests/unit/players/forge_test.cpp`;
- `tests/integration/game/forge_it.cpp`.

### PR #110 — Forge history item identity

- merged: 2026-07-12;
- merge commit: `84f5c09263f459d726fbc7b9f79557b2cbb0801d`;
- head: `78e10449f9c9c8401bf576f5751998f0fa7da655`.

Preserved behavior:

- in-memory Forge history carries both item IDs;
- Fusion and Transfer populate those IDs;
- history resolves item types by ID first;
- name lookup remains only as a fallback for older call sites.

### PR #177 — Equipment Upgrade audit and Dust reward remediation

- merged: 2026-07-12 19:37:41Z;
- merge commit: `f1d217c43e8e302978f533212e6aa9d1ce2b77c8`;
- head: `05134a4c96083c9b21e5e86a5e51dcfc3f53bee6`.

Retained production changes in `data/libs/systems/exaltation_forge.lua`:

- direct-player and summon-master killer resolution;
- one Dust amount rolled once per creature death;
- the same amount passed to every eligible shared-experience recipient;
- explicit `CONDITION_INFIGHT` recipient check;
- actual capped credited amount used for mutation and success messaging.

PR #177 explicitly did not implement exact Premium eligibility and did not claim full Forge parity.

---

## 4. Post-#177 drift review

Current `main` is 77 commits ahead of the PR #177 merge. The combined comparison includes later edits to broad shared surfaces such as `src/game/game.cpp`, `src/server/network/protocol/protocolgame.cpp` and `src/creatures/monsters/monster.cpp`. It does not include later edits to the principal finding-bearing Forge paths:

- `src/creatures/players/player.cpp`;
- `src/game/functions/forge_transfer_policy.hpp`;
- `src/config/configmanager.cpp`;
- `config.lua.dist`;
- `data/libs/systems/exaltation_forge.lua`;
- `src/utils/tools.cpp`;
- `tests/integration/game/forge_it.cpp`;
- `tests/unit/players/forge_test.cpp`.

Relevant later overlaps reviewed:

| PR | Overlap | Current-main conclusion |
|---:|---|---|
| #220 | Wheel of Destiny, `monster.cpp`, `game.cpp`, `protocolgame.cpp` | Did not change `Player::forgeFuseItems`, `forgeTransferItemTier`, conversions, Forge configuration, Dust Lua or Forge tests. Current F-011/F-012 paths still exhibit the recorded conditions. |
| #231 | `Game::removeCreature` instance ownership cleanup in `game.cpp` | No Forge request/transaction behavior change. |
| #233 | periodic instance timeout owner in `game.cpp`/`game.hpp` | No Forge request/transaction behavior change. |
| #195/#212 | weapon-proficiency audit/mastery state and monster death overlap | No change to Forge Dust event or Forge player transaction functions. |
| #188/#192 and related Cyclopedia work | broad protocol/data validation overlap | No evidence that Forge result bonus semantics, history or transaction safety changed. Current maintained-client and server paths still reproduce F-018/F-019. |
| #222 | universal E2E ownership | Defines future platform ownership only; no Forge gameplay proof. |
| #232 | read-only multichannel Game/Lua bindings | No Forge request/result change. |
| #239/#240 | Imbuement Vibrancy mapping and task lifecycle | No Forge behavior change. |

A broad-file overlap is not treated as remediation. Each finding below is classified from the current function/configuration/client path.

---

## 5. Current-main finding table

Status vocabulary used below: `still-open`, `partially-remediated`, `remediated`, `superseded`, `conflicting`, `target-version-decision-required`, `runtime-untested`, `no-longer-applicable`.

| Finding | Historical status | Current-main status | Evidence | Remediation PR | Remaining proof | Recommended next scope |
|---|---|---|---|---|---|---|
| F-001 — maximum Dust capacity 225 | open | **still-open** | B–C: `config.lua.dist` `forgeMaxDust = 225`; `ConfigManager::load` fallback `FORGE_MAX_DUST = 225`; `Player::forgeResourceConversion` compares against that value; maintained client fallback is also 225. | none | Confirm target version requires 325; compiled boundary tests 324→325 and rejection above cap; runtime/client display. | Isolated configuration-limit PR with F-002 only as separately reviewed config scope. |
| F-002 — Fiendish limit defaults inconsistent | open | **still-open** | B: distributed config `forgeFiendishLimit = 4`; `ConfigManager::load` fallback is 3; legacy `ForgeMonster.maxFiendish = 3`. | none | Prove which fields are live, test omitted-config startup and actual Fiendish count/lifecycle. | Configuration defaults PR; do not mix with Fiendish reward formulas. |
| F-003 — regular Fusion accepts different IDs server-side | open | **still-open** | C: `Player::forgeFuseItems` resolves `firstItemId` and arbitrary `secondItemId` at equal tier but does not require equality; historical integration success test uses two different IDs, while a later same-ID test only protects distinct-object removal. | none | Negative compiled regression proving crafted different-ID request leaves items, Dust, cores, gold, chest and history unchanged. | First bounded follow-up together with F-004/F-005, validation before mutation. |
| F-004 — Convergence Fusion restrictions incomplete | open | **still-open** | C: `ProtocolGame::sendOpenForge` filters class 4 and normalized slot for offered items; `Player::forgeFuseItems` does not independently require class 4, different IDs or equal normalized slot. | none | Negative tests for non-class-4, same ID, different normalized slot, imbued/stale candidates and no mutation. | Same server-authority PR as F-003/F-005. |
| F-005 — Convergence Transfer class 4 not enforced | open | **still-open** | C: `Player::forgeTransferItemTier` checks donor tier and matching nonzero classifications through `ForgeTransferPolicy`, but has no `convergence => class == 4` condition. | none | Crafted-packet negative tests with class 1–3; resource/inventory/history invariance. | Same server-authority PR as F-003/F-004. |
| F-006 — Premium Dust eligibility absent | open | **still-open** | C: `ForgeMonster:onDeath`/`creditDust` never call a Premium predicate. C++ exposes full `Player::isPremium()`, while current Lua player API exposes days-oriented access rather than a verified exact eligibility binding. | none | Implement exact semantics and test normal Premium, active final partial day, `FREE_PREMIUM`, `IsAlwaysPremium` and free account. Runtime Dust proof required. | Dedicated Premium/Dust PR after transaction/history scopes; do not use `getPremiumDays() > 0` as a substitute. |
| F-007 — party recipient logout block | remediated statically; runtime pending | **partially-remediated; runtime-untested** | C: PR #177 retained `recipient:hasCondition(CONDITION_INFIGHT)` and shared-experience recipient enumeration in `ForgeMonster:onDeath`. | #177 | Runtime boundaries for leader/member, active/inactive, range/floor, logged-out transition, summon killer and party changes. | Dedicated Dust runtime-proof scope with F-008/F-013; no new E2E platform. |
| F-008 — Dust cap message used requested amount | remediated statically; runtime pending | **partially-remediated; runtime-untested** | C: `ForgeMonster:creditDust` computes `math.min(amount, limit - current)`, adds and reports `creditedAmount`. | #177 | Runtime test near cap, at cap, zero credit and concurrent/state-change boundary. | Same Dust runtime-proof PR as F-007/F-013. |
| F-009 — Fiendish Slivers ignore creature difficulty | open | **target-version-decision-required** | B–C: current reward path uses global stack-based random amount/configuration; no current difficulty→Sliver mapping was found in Forge Lua, monster death or configuration. | none | Authoritative versioned rule/data source and deterministic tests for each difficulty bracket; then runtime corpse/reward proof. | Only after versioned evidence; do not invent mapping. |
| F-010 — Ruse precision truncation | open precision question | **target-version-decision-required** | B–C: item chance is floating-point, while downstream basis-point conversion/casts can truncate fractional precision; Amplification compounds before the cast. | none | Authoritative precision and rounding rule for the target client/server version plus boundary tests. | Isolated evidence-first precision task after higher-risk findings. |
| F-011 — Transcendence can overlap Avatar spell | open | **still-open** | C: `Player::triggerTranscendence` guards only `WheelOnThink_t::AVATAR_FORGE` and sets that timer; Avatar spell state uses the separate spell timer/condition path. | none | Focused compiled timer/state test and runtime cast/trigger overlap in both orders. | Small effects PR with F-012, after Dust proof. |
| F-012 — Momentum false trigger feedback | open | **still-open** | C: `Player::triggerMomentum` sets `triggered = true` while iterating before confirming the condition is an eligible cooldown actually changed. | none | Compiled tests with no cooldown, ineligible cooldowns, eligible spell/group cooldown and message/effect assertion. | Same effects PR as F-011. |
| F-013 — party members received independent Dust rolls | remediated statically; runtime pending | **partially-remediated; runtime-untested** | C: PR #177 computes `amount` once before party enumeration and passes the same value to each eligible recipient. | #177 | Runtime multi-member assertion that balances increase by the same roll under eligibility boundaries. | Same Dust runtime-proof PR as F-007/F-008. |
| F-014 — Dust-refill success bonus absent | open | **still-open** | C: `forgeBonus()` returns only 0–7; current value 8 is reused by failed Fusion for retained tier. No distinct success outcome refills Dust. | none | Versioned server/client result model, deterministic bonus selection, resource mutation, history and packet/UI tests. | Coordinated Canary + `blakinio/otclient` program with F-015–F-019. |
| F-015 — +2 tier cap uses classification ID | open | **still-open** | C: `Player::forgeFuseItems` uses `tier + 2 <= firstForgedItem->getClassification()`, incorrectly treating class ID as tier cap; class 4 can reach configured tier 10. | none | Tier-aware helper and deterministic tests at each classification cap, especially class-4 tiers 8/9/10. | Coordinated bonus/result scope F-014–F-019. |
| F-016 — bonus selection not tier-aware | open | **still-open** | C: `Game::playerForgeFuseItems` calls global `forgeBonus(chance)` before item/tier-specific validation; impossible decrease/+2 outcomes may be selected then have no documented effect. | none | Explicit eligible-bonus set per current item/tier and forced deterministic tests. | Coordinated bonus/result scope F-014–F-019. |
| F-017 — Fusion history misreports results | open | **still-open** | C: `registerForgeHistoryDescription` uses the first item type for both Fusion partners, always describes first result as `tier + 1`, and only recognizes overloaded bonus 8 as retained. PR #110 fixes ID resolution infrastructure but not outcome semantics. | #110 only provides baseline identity plumbing | Exact history assertions for Convergence and every success/failure bonus using both IDs and actual resulting tiers/states. | Coordinated bonus/history/protocol scope F-014–F-019. |
| F-018 — maintained OTClient renders only bonus 1–4 | open in upstream-named client path | **still-open** | C: current `blakinio/otclient/modules/game_forge/game_forge.lua::forgeResultData` has branches only for bonuses 1–4. Values 5–8 have no complete presentation. | none | Define contract IDs/meaning, update maintained client only, test every result and supported one-sided rollout behavior. | Atomic-required Canary + `blakinio/otclient` coordination; never modify `opentibiabr/otclient`. |
| F-019 — decreased-tier packet/UI tier mismatch | open | **still-open** | C: server `sendForgeResult` call uses right tier `tier + 1` for Fusion; retained bonus 4 mutates second item to `tier - 1`; client derives bonus tier from received `rightTier - 1`, yielding the wrong state. | none | Versioned packet contract, server serialization test, client parse/UI test and physical-client proof when platform exists. | Same coordinated program as F-014–F-018. |
| F-020 — Fusion/Transfer not atomic after mutation begins | open | **still-open** | C: both functions add a chest/remove inputs before all output creation, insertion, resource removal and money removal complete; later errors return without rollback. Existing prechecks reduce early failures but do not make the operation atomic. | prechecks exist from earlier work; no rollback PR | Fault-injection compiled tests at every mutation boundary; restore inventory, tiers, Dust, cores, money, chest and history. | Second bounded follow-up after F-003–F-005. |
| F-021 — Sliver→Core can consume Slivers without Core | open | **still-open** | C: `Player::forgeResourceConversion` removes Slivers before Core creation/insertion; null creation does not set a failure code and insertion failure does not restore Slivers. | none | Preflight output insertion or transactional rollback; injected creation/add failure tests and history invariance. | Same atomicity program as F-020, separate from Fusion bonus work. |
| F-022 — failed Fusion history hardcodes 100 Dust | open | **still-open** | C: failed branch mutates configured `dustCost`, but `registerForgeHistoryDescription` prints literal `100 dust`. | none | Config-variation compiled history test and actual stored cost assertion. | Small history-correctness PR with F-023/F-024. |
| F-023 — conversion history action types overwritten | open | **still-open** | C: `registerForgeHistoryDescription` rewrites `SLIVERSTOCORES` and `INCREASELIMIT` to `DUSTTOSLIVERS` before storing history. | none | Round-trip tests for all three conversion action types and persistence/page output. | Same history-correctness PR as F-022/F-024. |
| F-024 — Dust→Slivers history hardcodes gained 3 | open | **still-open** | C: created count uses `FORGE_SLIVER_AMOUNT`, while `history.gained = 3` is literal. | none | Config-variation test proving created quantity and history remain equal. | Same history-correctness PR as F-022/F-023. |

### Classification summary

- `still-open`: F-001–F-006, F-011–F-012, F-014–F-024 except the entries listed below;
- `partially-remediated; runtime-untested`: F-007, F-008, F-013;
- `target-version-decision-required`: F-009, F-010;
- `remediated`: none at the full required evidence level;
- `superseded`: none;
- `conflicting`: none currently proven;
- `no-longer-applicable`: none.

---

## 6. Current implementation and test paths

### Server/configuration

- `config.lua.dist` — Forge defaults;
- `src/config/configmanager.cpp` — fallback loading;
- `data/scripts/systems/item_tiers.lua` — tier/classification data loading;
- `src/items/items_classification.hpp` — tier price/cap structure;
- `src/game/game.cpp` — `Game::playerForgeFuseItems`, `playerForgeTransferItemTier`, `playerForgeResourceConversion`;
- `src/creatures/players/player.cpp` — `triggerMomentum`, `triggerTranscendence`, `forgeFuseItems`, `forgeTransferItemTier`, `forgeResourceConversion`, `registerForgeHistoryDescription`;
- `src/game/functions/forge_transfer_policy.hpp` — preserved normal Transfer policy;
- `src/server/network/protocol/protocolgame.cpp` — `sendForgingData`, `sendOpenForge`, Forge result/history packet paths;
- `src/utils/tools.cpp` — `forgeBonus`.

### Creature rewards/effects

- `data/libs/systems/exaltation_forge.lua` — Dust reward selection/credit and legacy defaults;
- `data/scripts/creaturescripts/monster/forge_kill.lua` — death event delegation;
- `src/creatures/monsters/monster.cpp` — Forge classification/lifecycle overlap;
- `src/creatures/players/grouping/party.cpp` — shared-experience eligibility/range/activity;
- `src/items/item.cpp` — Forge effect chances;
- `src/creatures/combat/combat.cpp` — Onslaught/Ruse interaction paths;
- `data/scripts/spells/support/avatar_of_*.lua` — Avatar spell state.

### Tests

- `tests/unit/players/forge_test.cpp` — Dust state and Transfer policy helpers;
- `tests/integration/game/forge_it.cpp` — normal success paths, same-object distinct-removal guards and limited resource/history assertions.

Current gaps in compiled regression coverage:

- no negative authority matrix for F-003–F-005;
- no failure-injection rollback matrix for F-020/F-021;
- no configurable conversion/history matrix for F-022–F-024;
- no exact Premium matrix;
- no deterministic all-bonus server/client matrix;
- no focused Dust party runtime proof.

### Maintained client

- `blakinio/otclient/modules/game_forge/game_forge.lua` — selection, result and bonus UI;
- maintained client default branch at review: `main`;
- reviewed file blob at refresh: `60e3fd76a1f893665990f2f04519b79f476bee3f`.

`opentibiabr/otclient` is not an authorized write target.

---

## 7. Test and evidence record

### Historical evidence

- PR #110 reported full CI, including Linux debug/release, all 383 C++ tests, Windows/macOS builds and Docker quickstart smoke on its historical head.
- PR #177 retained Lua remediation and recorded successful Lua/format/static checks on its historical head; focused Dust gameplay remained pending.
- Historical checks prove only their stated commits and scenarios. They are not current-main gameplay proof.

### Current handoff environment

Attempted command:

```text
git clone --filter=blob:none --no-checkout https://github.com/blakinio/canary.git canary-handoff
```

Result:

```text
fatal: unable to access 'https://github.com/blakinio/canary.git/': Could not resolve host: github.com
```

Therefore, for this refresh:

- local checkout: unavailable;
- `git fetch`, `git pull`, local checkout and full-repository local tests: unavailable;
- `python tools/agents/task_ownership.py`: not run;
- local Markdown/path review and `git diff --check`: not run;
- local build, C++ tests, Lua tests, runtime and gameplay: not run.

GitHub API reads/writes are used. Concrete current-head workflow run IDs, job names, results and evidence boundaries are recorded in the task and PR before readiness/merge. A green aggregate `Required` result is not accepted without inspecting its concrete jobs.

---

## 8. Work performed in the 2026-07-13 handoff refresh

### Read and compared

- repository coordination and safety documents listed in the task record;
- current report and parent methodology;
- current configuration, C++ Forge functions, Dust Lua, monster death overlap, protocol list/result paths, Forge tests and maintained-client Forge module;
- PRs #89, #110 and #177 metadata/merge commits;
- current open PRs and active-work index;
- PR #177 merge versus current main;
- relevant later overlapping PRs, especially #220, #231, #233, #195/#212, #222 and #232.

### Confirmed

- PR #89, #110 and #177 fixes remain part of the baseline;
- F-007/F-008/F-013 retain production code from #177 but have no focused current runtime proof;
- all other findings retain current source evidence or require versioned target evidence as classified above;
- no open Forge implementation PR supersedes this report;
- no full Forge parity, gameplay or E2E proof exists in the reviewed state.

### Discarded incomplete work

Before the task was narrowed to documentation-only handoff, the branch temporarily contained two experimental scaffolding files:

- `.github/workflows/equipment-upgrade-phase1.yml`;
- `tools/ai-agent/apply_equipment_upgrade_phase1.py`.

They were never submitted in a PR, were not accepted evidence and were removed by resetting `fix/equipment-upgrade-validation-2` to current main through the GitHub API. They must not be recreated as a substitute for proper bounded implementation work.

### Files changed by this handoff PR

- `docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_VALIDATION.md`;
- `docs/agents/tasks/active/CAN-20260713-equipment-upgrade-handoff-refresh.md`.

Explicitly unchanged:

- `docs/agents/ACTIVE_WORK.md`;
- all runtime/gameplay/config/protocol/test paths;
- both OTClient repositories.

---

## 9. Recommended bounded follow-up sequence

After starting from the then-current `main` and repeating overlap checks:

1. **F-003–F-005 — server authority before mutation**  
   Reject crafted/stale Fusion and Convergence requests before chest creation or any resource/item mutation. First read `Player::forgeFuseItems` and `Player::forgeTransferItemTier` in `src/creatures/players/player.cpp`, then `tests/integration/game/forge_it.cpp`.
2. **F-020–F-021 — atomicity and rollback**  
   Introduce a bounded transaction/preflight design and injected-failure regression tests.
3. **F-022–F-024 — history action types and configurable amounts**  
   Correct only history values/types and add config-variation tests.
4. **F-006 — exact Premium semantics**  
   Reuse `Player::isPremium()` semantics; never replace them with days-only logic.
5. **Runtime proof for F-007/F-008/F-013**  
   Add feature-owned scenarios to the shared E2E/runtime platform when available; do not duplicate its orchestration.
6. **F-011/F-012 — Transcendence/Momentum effects**  
   Add focused timer/cooldown tests and bounded runtime proof.
7. **F-014–F-019 — explicit Canary + `blakinio/otclient` program**  
   Define a versioned result contract, compatibility/rollout matrix and tests in both repositories.
8. **F-009/F-010 — evidence-first version decisions**  
   Implement only after authoritative versioned Fiendish reward and precision/rounding evidence exists.

Do not combine these groups into one PR:

- F-001/F-002 configuration limits;
- F-003–F-005 authority;
- F-006 plus runtime proof F-007/F-008/F-013;
- F-009–F-012 Fiendish/effects;
- F-014–F-019 bonus/history/protocol/client;
- F-020/F-021 atomicity;
- F-022–F-024 history amounts/action types.

---

## 10. Handoff

| Field | Value at documentation-PR creation |
|---|---|
| Repository | `blakinio/canary` |
| Main SHA used for branch base | `d4eeab3db322f26ee72d7f0ad958d35dc9bd007d` |
| Branch | `fix/equipment-upgrade-validation-2` |
| PR | `#241` |
| PR state | draft while this report/task/CI evidence is finalized |
| Task record | `docs/agents/tasks/active/CAN-20260713-equipment-upgrade-handoff-refresh.md` |
| Branch exists | yes |
| Auto-merge | not enabled at report-write time |
| Review threads | none at PR creation; recheck before merge |
| Changed files | this report and task record only after finalization |
| Runtime/gameplay changes | none |
| Local tests | none; checkout unavailable due `Could not resolve host: github.com` |
| Current findings | table in section 5 |
| First bounded follow-up | F-003–F-005 authority validation before any mutation |
| First source to read | `src/creatures/players/player.cpp`: `Player::forgeFuseItems`, then `Player::forgeTransferItemTier` |
| First tests to read | `tests/integration/game/forge_it.cpp`, then `tests/unit/players/forge_test.cpp` |

Suggested first local commands for the next implementation agent, when DNS/local checkout is available:

```sh
git fetch origin main
git switch main
git pull --ff-only origin main
python tools/agents/task_ownership.py
rg -n "forgeFuseItems|forgeTransferItemTier|forgeResourceConversion|registerForgeHistoryDescription" src tests
cmake --preset linux-debug
cmake --build --preset linux-debug --target canary_test
ctest --preset linux-debug --output-on-failure -R "Forge"
```

The exact presets/targets must be checked against the then-current `CMakePresets.json`; do not report these commands as passed until executed on a recorded commit.

### Required warnings

- **DO NOT REOPEN PR #177.**
- **DO NOT CONTINUE A DELETED HISTORICAL BRANCH.**
- **DO NOT EDIT `docs/agents/ACTIVE_WORK.md`.**
- **DO NOT CLAIM FULL FORGE PARITY.**
- **DO NOT CLAIM GAMEPLAY OR E2E PROOF WITHOUT EXECUTION.**
- **DO NOT MODIFY `opentibiabr/otclient`.**
- **DO NOT FIX ALL FINDINGS IN ONE PR.**
- Start from current `main` unless a later active task/branch explicitly and validly owns the chosen bounded scope.

---

## 11. Completion state of this documentation refresh

The current PR is complete only after:

1. the task record contains the actual PR/head/check data;
2. changed files are confirmed to exclude `ACTIVE_WORK.md` and all runtime paths;
3. the draft is marked ready;
4. concrete current-head jobs are inspected;
5. documentation-scope failures are repaired;
6. `last_verified_commit` is set to the verified head;
7. auto-merge/squash merge completes or an exact blocker is recorded;
8. the task is moved from `tasks/active` to `tasks/archive` through a follow-up lifecycle PR.
