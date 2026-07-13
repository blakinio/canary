# OTS AI Equipment Upgrade Validation — current status and handoff

> **Updated:** 2026-07-13  
> **Repository:** `blakinio/canary`  
> **Current main at refresh start:** `d4eeab3db322f26ee72d7f0ad958d35dc9bd007d`  
> **Documentation branch:** `docs/equipment-upgrade-handoff-refresh`  
> **Documentation PR:** `#242`  
> **Historical validation PR:** `#177` — merged; do not reopen  
> **Primary comparison page:** `https://tibia.fandom.com/wiki/Equipment_Upgrade`  
> **Parent methodology:** `docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md`  
> **Evidence boundary:** structural/static/semantic and compiled-regression evidence exist; full runtime, gameplay and physical-client E2E parity do not.

---

## 1. Purpose

Validate Canary's Equipment Upgrade / Exaltation Forge implementation and preserve a trustworthy handoff. This refresh does not change gameplay. It rechecks historical findings F-001–F-024 against current `main`, records merged remediation, separates evidence levels and defines small follow-up scopes.

A successful build, client-side filtering or an aggregate `Required` job is not gameplay proof. Evidence levels remain separate:

- **structural:** files/configuration load or compile;
- **static:** identifiers, handlers and tables resolve;
- **semantic:** formulas, validation and mutation ordering match the selected target;
- **compiled regression:** automated unit/integration assertions execute;
- **runtime:** server starts and the relevant system registers/executes without critical failure;
- **gameplay:** a player executes the scenario through the game protocol;
- **physical-client E2E:** a real supported client completes the scenario.

---

## Current repository state

| Item | Current state |
|---|---|
| Current `blakinio/canary` main | `d4eeab3db322f26ee72d7f0ad958d35dc9bd007d` at refresh start |
| Open Forge PRs | none found |
| Active Forge tasks | none found in open PR/task searches or the read-only coordination snapshot |
| Last merged Forge PR | #177, merge `f1d217c43e8e302978f533212e6aa9d1ce2b77c8` |
| Historical branch | `validation/equipment-upgrade` is not present; it is historical and must not be continued |
| Current validation state | F-001–F-024 rechecked against current source history; no later Forge implementation PR found |
| Maintained client | `blakinio/otclient` main `2fcfa2b61f4cd2e47beb49ec036a01152979dd79` |
| Upstream client | `opentibiabr/otclient` is reference-only and must not be modified |
| Current handoff task | `docs/agents/tasks/active/CAN-20260713-equipment-upgrade-handoff-refresh.md` |
| Current documentation PR | #242, documentation-only |

Comparison of PR #177's merge commit with current `main` shows 77 later commits. None changes Forge configuration, item-tier tables, `Player` Forge functions, Forge reward Lua, Forge item/combat effects, Forge tests or this report. Later generic changes in `protocolgame.cpp`, Player/Wheel and creature/instance lifecycle were reviewed and do not modify the audited Forge functions or packet contract.

No current open PR or active task overlaps this documentation refresh. `docs/agents/ACTIVE_WORK.md` is read-only and is not edited.

---

## 2. Historical baseline that must be preserved

### PR #89 — normal Transfer

- head `570d6e077c02107eb712a4ff214cf4442d6c91d8`;
- merge `209289d38e64aafe7ce3e036867bb632cd0363b8`;
- server-side classification and donor-tier validation;
- donor-tier configured gold/core costs and separate result tier;
- actual Dust/core/gold values in history;
- corrected donor/receiver result and history rendering;
- focused policy/integration coverage.

This is a confirmed normal-Transfer baseline, not full Forge parity.

### PR #110 — Forge history item identity

- head `78e10449f9c9c8401bf576f5751998f0fa7da655`;
- merge `84f5c09263f459d726fbc7b9f79557b2cbb0801d`;
- `ForgeHistory` stores first and second item IDs;
- Fusion and Transfer populate those IDs;
- `Player::registerForgeHistoryDescription` resolves by ID with name fallback;
- PR CI reported all 383 C++ tests passing, including the Forge Transfer integration flow.

This fixes item identity, not all action-type, amount or bonus-history semantics.

### PR #177 — Equipment Upgrade audit and Dust rewards

- head `05134a4c96083c9b21e5e86a5e51dcfc3f53bee6`;
- merge `f1d217c43e8e302978f533212e6aa9d1ce2b77c8`;
- `ForgeMonster:getPlayerKiller` handles direct and summon killers;
- one Dust amount is rolled per death and shared with eligible party recipients;
- each party recipient requires current `CONDITION_INFIGHT`;
- `ForgeMonster:creditDust` credits and reports the actual capped amount.

Premium was deliberately left open because a days-only Lua check did not match complete `Player::isPremium()` semantics. Focused gameplay/runtime Dust scenarios were not executed. Do not reopen PR #177 or continue its deleted branch.

### Historical CI boundary

PR #177 head had successful CI run `29205082784`: Detect Build Scope, Fast Checks, Lua Tests and Linux Release/runtime smoke succeeded; platform jobs outside detected scope were skipped. A later CI run `29206161337` on the same recorded head concluded failure and must not be hidden. Neither run is a focused gameplay proof for party Dust, cap boundaries or Premium. The merged source change is preserved; F-007/F-008/F-013 remain runtime-untested.

---

## 3. Current source areas

### Configuration and Forge operations

- `config.lua.dist`;
- `src/config/configmanager.cpp`;
- `data/scripts/systems/item_tiers.lua`;
- `src/items/items_classification.hpp`;
- `src/creatures/players/player.cpp`:
  - `Player::forgeFuseItems`;
  - `Player::forgeTransferItemTier`;
  - `Player::forgeResourceConversion`;
  - `Player::sendForgeResult`;
  - `Player::registerForgeHistoryDescription`;
- `src/server/network/protocol/protocolgame.cpp`:
  - `ProtocolGame::sendOpenForge` and Forge packet serialization;
- `src/game/functions/forge_transfer_policy.hpp`.

### Rewards and effects

- `data/libs/systems/exaltation_forge.lua`:
  - `ForgeMonster:onDeath`;
  - `ForgeMonster:getPlayerKiller`;
  - `ForgeMonster:creditDust`;
- `data/scripts/creaturescripts/monster/forge_kill.lua`;
- `src/creatures/monsters/monster.cpp`;
- `src/items/item.cpp`;
- `src/creatures/combat/combat.cpp`;
- `data/scripts/spells/support/avatar_of_*.lua`.

### Tests and client contract

- current Forge tests under `tests/unit/players/forge/` and `tests/integration/players/`;
- maintained client `blakinio/otclient/modules/game_forge/game_forge.lua`;
- maintained client Forge packet parser under `blakinio/otclient/src/client/protocolgameparse.cpp`.

The old report's references to `opentibiabr/otclient` as the implementation target are superseded. Future client writes belong only in `blakinio/otclient`.

---

## 4. Current-main findings

| Finding | Historical status | Current-main status | Evidence | Remediation PR | Remaining proof | Recommended next scope |
|---|---|---|---|---|---|---|
| F-001 | open | still-open | `config.lua.dist` and `src/config/configmanager.cpp` retain maximum Dust 225; no post-#177 change | none | authoritative target version plus 324→325 and >325 regression/runtime boundaries | separate configuration-limit PR with F-002 only if independently justified |
| F-002 | open | still-open | distributed Fiendish limit 4 conflicts with engine/legacy fallback 3; configuration paths unchanged | none | decide one supported default and test configuration/fallback loading | configuration-limit PR, separate from gameplay validation |
| F-003 | open | still-open | `Player::forgeFuseItems`; regular Fusion still lacks an independent identical-item-ID authority check and historical integration permits different IDs | none | crafted/stale packet regression before any mutation | first bounded server-authority PR |
| F-004 | open | still-open | `Player::forgeFuseItems` and `ProtocolGame::sendOpenForge`; class 4, different IDs and normalized slot restrictions are not fully duplicated server-side | none | crafted Convergence packet tests for class, identity, slot and tier | same bounded authority family as F-003, not atomicity/history |
| F-005 | open | still-open | `Player::forgeTransferItemTier` uses matching classification/tier policy from #89 but does not additionally require class 4 for Convergence | #89 partially relevant | crafted Convergence Transfer class rejection before mutation | same bounded authority family as F-003/F-004 |
| F-006 | open | still-open | `ForgeMonster:onDeath`/`creditDust` have no complete Premium predicate; days-only check was removed in #177 | #177 explicitly left open | exact `Player::isPremium()` binding/placement; normal, final partial day, free-Premium, always-Premium tests | dedicated Premium semantics PR |
| F-007 | remediated statically; runtime pending | runtime-untested | #177 requires `CONDITION_INFIGHT` per shared-party recipient; source unchanged | #177 | focused runtime/gameplay boundaries for active, stale, out-of-range and logged-out members | dedicated Dust runtime-proof PR/test pack |
| F-008 | remediated; runtime pending | runtime-untested | `ForgeMonster:creditDust` uses `min(amount, limit-current)` for credit and message | #177 | cap-edge runtime assertions and persisted resource balance | same Dust runtime-proof scope as F-007/F-013 |
| F-009 | open | target-version-decision-required | Fiendish corpse reward still uses global random min/max; creature difficulty is unused | none | authoritative versioned difficulty→Sliver mapping | defer until version decision; do not guess |
| F-010 | open precision question | target-version-decision-required | Ruse/Amplification path converts floating percentages to integer basis points by truncation | none | authoritative precision/rounding rule for selected target version | defer until version decision; do not bundle with effects fixes |
| F-011 | open | still-open | Avatar spells set `AVATAR_SPELL`; Transcendence checks only `AVATAR_FORGE` in spell/combat state paths | none | compiled regression proving mutual exclusion and cleanup | bounded effects PR with F-012 only |
| F-012 | open | still-open | Momentum trigger feedback can be set before an eligible cooldown is actually reduced | none | deterministic cooldown/no-cooldown regression and runtime feedback | bounded effects PR with F-011 |
| F-013 | remediated; runtime pending | runtime-untested | #177 rolls once in `ForgeMonster:onDeath` and passes the same amount to all eligible recipients | #177 | deterministic party runtime test proving one shared amount and recipient boundaries | Dust runtime-proof scope with F-007/F-008 |
| F-014 | open | still-open | `Player::forgeFuseItems` bonus generation lacks the documented Dust-refill success outcome; value 8 is overloaded for failed retained-tier behavior | none | versioned bonus contract, deterministic forced outcome, packet/history/client result | coordinated F-014–F-019 program |
| F-015 | open | still-open | +2 result compares `tier + 2` with classification ID, treating class 4 as capped at tier 4 instead of 10 | none | forced +2 tests across class/tier boundaries | coordinated bonus server PR after contract design |
| F-016 | open | still-open | bonus selection is not tier-aware and can select impossible decreased/+2 outcomes | none | deterministic selection matrix by tier/outcome | coordinated bonus server PR |
| F-017 | open | still-open | `Player::registerForgeHistoryDescription` reports incomplete Convergence/bonus results despite #110 identity fix | #110 fixes identity only | forced outcome history assertions for all bonuses and both IDs | history/protocol part of coordinated program |
| F-018 | open in upstream client | still-open in maintained client | `blakinio/otclient` `forgeResultData` handles bonus values 1–4 only; no later Forge client PR found | none | agreed server enum/payload plus client presentation/tests for every value | explicit Canary + `blakinio/otclient` program; never upstream write |
| F-019 | open | still-open | server retained tier and result payload can diverge for decreased-tier outcome; client uses supplied `leftTier`/`rightTier` directly | none | packet fixture and client rendering assertion for retained `t-1` | coordinated protocol/client program |
| F-020 | open | still-open | `Player::forgeFuseItems` and `forgeTransferItemTier` remove/move inputs before all output/resource mutations succeed; no rollback | none | injected failure at every mutation boundary with exact resource/item restoration | second bounded PR family: transaction/rollback |
| F-021 | open | still-open | `Player::forgeResourceConversion` removes Slivers before Core creation/insertion and does not restore on failure | none | null creation/add failure injection and rollback assertions | atomicity PR, separate from history fixes |
| F-022 | open | still-open | failed Fusion history in `registerForgeHistoryDescription` uses hardcoded 100 Dust rather than stored/configured cost | none | configured non-100 failure-history regression | third bounded PR family: history amounts/types |
| F-023 | open | still-open | `forgeResourceConversion` history rewrites `SLIVERSTOCORES` and `INCREASELIMIT` as `DUSTTOSLIVERS` | none | round-trip action-type tests for every conversion | history correctness PR with F-022/F-024 |
| F-024 | open | still-open | creation uses configured Dust→Sliver quantity but history records gained 3 | none | non-default configured amount test across mutation and history | history correctness PR with F-022/F-023 |

### Status summary

- **still-open:** F-001–F-006, F-011–F-012, F-014–F-024;
- **runtime-untested:** F-007, F-008, F-013;
- **target-version-decision-required:** F-009, F-010;
- **remediated/superseded/no-longer-applicable:** none of F-001–F-024 is promoted to these final states by this refresh.

PR #89 and #110 remain confirmed repairs outside the unresolved portions described above. PR #177 remains the retained code remediation for F-007/F-008/F-013, but not gameplay proof.

---

## 5. Later PR impact review

The post-#177 history was checked for Forge, Player, protocol, combat, item-tier, client-contract and history overlap.

- instance/lifecycle PRs #180, #183, #201, #231 and #233 do not change Forge functions;
- Cyclopedia PRs #188/#192 do not change Forge contracts;
- #197 changes CI gating only;
- #210 changes boosted creature/boss leader election, not Fiendish Forge reward rules;
- #220 changes Wheel of Destiny Player/protocol paths, not Forge packet/result paths;
- #222 creates E2E coordination documentation but supplies no Forge gameplay or physical-client execution;
- no later merged/open Canary PR remediates F-001–F-024;
- no later `blakinio/otclient` Forge PR was found.

This review does not treat unrelated generic-file edits as Forge remediation.

---

## 6. Validation and test record

### Local execution

Local checkout and local tests are unavailable because the execution environment cannot resolve `github.com`.

Attempted:

```text
getent hosts github.com
# no DNS result

git ls-remote https://github.com/blakinio/canary.git HEAD
# fatal: unable to access 'https://github.com/blakinio/canary.git/': Could not resolve host: github.com
```

Could not be run without a checkout:

```text
git clone https://github.com/blakinio/canary.git
git fetch --all --prune
git pull --ff-only
git checkout docs/equipment-upgrade-handoff-refresh
git status --short --branch
git branch -vv
git remote -v
git worktree list
git diff --check
python tools/agents/task_ownership.py
cmake --preset linux-debug
cmake --build --preset linux-debug --target canary_ut
ctest --test-dir build/linux-debug --output-on-failure
```

No local test is claimed as passed. GitHub API inspection and CI are separate evidence.

### Historical CI

| Head | Run | Concrete jobs/result | Confirms | Does not confirm |
|---|---|---|---|---|
| #89 head `570d6e0…` | `29164115572` | CI success; a later run `29167859855` failed | at least one complete historical regression cycle for the retained Transfer implementation | current-main Forge parity or gameplay |
| #110 head `78e1044…` | `29185907405` and `29185890664` | CI success; PR reports formatting, Lua, Linux debug/release, 383 C++ tests, Windows, macOS and Docker | item-ID history repair compiled and its Forge Transfer integration regression passed | F-017/F-022–F-024 or gameplay |
| #177 head `05134a4…` | `29205082784` | Detect Build Scope, Fast Checks, Lua Tests and Linux Release/runtime smoke success; other platform jobs skipped by scope | Lua remediation syntax/static checks and general runtime smoke | focused party/cap/Premium gameplay |
| #177 head `05134a4…` | `29206161337` | CI failure | records a later non-green run that must not be hidden | no positive proof; inspect only if resuming historical diagnosis, not by reopening #177 |

The final documentation PR's current-head workflow IDs and concrete jobs are recorded in the task/PR before merge.

---

## 7. Required future regression scenarios

1. regular Fusion accepts identical IDs and rejects crafted different IDs before mutation;
2. Convergence Fusion/Transfer enforce class 4 and exact identity/slot/tier rules server-side;
3. every rejected or failed operation preserves items, Dust, cores and gold;
4. Dust capacity and Fiendish defaults follow an explicit selected target version;
5. Premium eligibility matches complete `Player::isPremium()` semantics;
6. one party Dust roll is shared only among eligible recipients, including logout-block boundaries;
7. cap messages report exactly the credited amount;
8. Transcendence cannot overlap spell Avatar and Momentum reports only real reduction;
9. all bonus outcomes are forced deterministically and checked in item state, resources, history, packet and maintained OTClient;
10. every mutation boundary has injected-failure rollback coverage;
11. every conversion action type and configurable amount round-trips into history.

---

## 8. Recommended order of bounded follow-ups

After refreshing from then-current `main`, and only when current code still confirms the finding:

1. **F-003–F-005:** server-authority validation before any mutation;
2. **F-020–F-021:** atomicity and rollback;
3. **F-022–F-024:** history action types and configurable amounts;
4. **F-006:** complete Premium semantics;
5. **runtime proof F-007/F-008/F-013;**
6. **F-011/F-012;**
7. **F-014–F-019:** explicit coordinated Canary + `blakinio/otclient` program;
8. **F-009/F-010:** only after authoritative versioned evidence.

Do not combine configuration limits, server authority, Premium/Dust runtime, Fiendish/effects, Fusion bonuses/protocol, atomicity and history into one PR.

---

## 9. Current-session record

- read all required agent governance, repository map, module catalogue, known risks, build matrix, cross-repository contracts and world-validation methodology;
- verified current `main`, open Forge PRs, active Forge work and historical branch state;
- read PRs #89, #110 and #177 and recorded actual merge commits;
- compared #177 merge to current `main` and reviewed later potentially overlapping PRs;
- inspected current maintained `blakinio/otclient` Forge UI and current PR history;
- reclassified every finding F-001–F-024;
- attempted DNS/Git remote checks and recorded exact failures;
- created documentation branch, task and draft PR #242;
- did not change or prepare gameplay code, tests, workflows, E2E infrastructure or OTClient;
- no uncommitted code fragment exists because no local checkout exists;
- an initial oversized task-record write was rejected by the tool before GitHub mutation; the content was reduced and safely committed through the normal GitHub contents API;
- no temporary write-enabled workflow was created.

Sources were read on 2026-07-13. The primary wiki snapshot remains a historical comparison source, not sole authority for numeric implementation changes.

---

## 10. Handoff

| Field | Value |
|---|---|
| Repository | `blakinio/canary` |
| Main at refresh start | `d4eeab3db322f26ee72d7f0ad958d35dc9bd007d` |
| Branch | `docs/equipment-upgrade-handoff-refresh` |
| PR | #242 |
| Task | `docs/agents/tasks/active/CAN-20260713-equipment-upgrade-handoff-refresh.md` |
| Current status | documentation refresh in progress until PR/cleanup merge |
| Branch exists | yes |
| PR draft | initially yes; final state recorded in PR/task |
| Auto-merge | not enabled until final applicable jobs and review gate pass |
| Review threads | inspect on final head before merge |
| Changed files | this report and task record only |
| Completed | current-main history/overlap review, F-001–F-024 classification, bounded plan, DNS record |
| Incomplete | final PR CI/merge and post-merge task archive until recorded complete |
| Local tests | unavailable; exact DNS error and commands above |
| Cross-repository dependency | F-018/F-019 and later F-014–F-019 use `blakinio/otclient`; upstream is read-only |
| First bounded follow-up | F-003–F-005 server-authority validation before mutation |
| First server file/functions | `src/creatures/players/player.cpp`: `Player::forgeFuseItems`, then `Player::forgeTransferItemTier` |
| First client file when coordinated | `blakinio/otclient/modules/game_forge/game_forge.lua`: `forgeResultData` |

Recommended first local commands for a future implementation agent starting from current `main`:

```text
git fetch origin --prune
git checkout main
git pull --ff-only
git checkout -b fix/forge-server-authority
rg -n "forgeFuseItems|forgeTransferItemTier|sendOpenForge" src tests
git log --oneline -- src/creatures/players/player.cpp src/server/network/protocol/protocolgame.cpp tests
```

Then read the full current functions and existing Forge tests before writing code. If no active bounded branch exists, start from current `main`, not from `validation/equipment-upgrade`.

### Mandatory prohibitions

- **DO NOT REOPEN PR #177.**
- **DO NOT CONTINUE A DELETED HISTORICAL BRANCH.**
- **DO NOT EDIT `ACTIVE_WORK.md`.**
- **DO NOT CLAIM FULL FORGE PARITY.**
- **DO NOT CLAIM GAMEPLAY OR E2E PROOF WITHOUT EXECUTION.**
- **DO NOT MODIFY `opentibiabr/otclient`.**
- **DO NOT FIX ALL FINDINGS IN ONE PR.**
