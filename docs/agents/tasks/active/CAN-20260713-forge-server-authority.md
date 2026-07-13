---
task_id: CAN-20260713-forge-server-authority
program_id: CAN-PROGRAM-EQUIPMENT-UPGRADE-PARITY
coordination_id: ""
status: ready_for_review_pending_final_ci
agent: "GPT-5.6 Thinking"
branch: fix/forge-server-authority
base_branch: main
created: 2026-07-13T13:15:00+02:00
updated: 2026-07-13T15:12:00+02:00
last_verified_commit: "58c258de79ceded987d92642923e879c4a9905f6"
risk: medium
related_issue: ""
related_pr: "#250"
depends_on:
  - PR #89 normal Transfer policy
  - PR #110 Forge history item identity
  - PR #177 Dust reward remediation
blocks:
  - later Forge atomicity/history/reward/effect tasks only by shared Player path sequencing
owned_paths:
  exclusive:
    - src/creatures/players/player.cpp
    - src/game/functions/forge_fusion_policy.hpp
    - src/game/functions/forge_transfer_policy.hpp
    - tests/unit/players/forge_test.cpp
    - tests/integration/game/forge_it.cpp
    - docs/agents/tasks/active/CAN-20260713-forge-server-authority.md
  shared:
    - docs/agents/programs/EQUIPMENT_UPGRADE_PARITY_PROGRAM.md
    - docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_VALIDATION.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - src/server/network/protocol/protocolgame.cpp
    - docs/agents/CROSS_REPO_CONTRACTS.md
modules_touched:
  - Player Forge Fusion authority
  - Player Forge Transfer authority
  - Forge authority policy helpers
  - Forge unit and integration tests
reuses:
  - existing `Player::getForgeItemFromId` distinct-instance, tier and imbuement lookup
  - `ForgeTransferPolicy` rules merged in PR #89
  - current integration fixture in `tests/integration/game/forge_it.cpp`
public_interfaces:
  - internal constexpr Forge Fusion/Transfer authority policy helpers
cross_repo_tasks: []
---

# Goal

Reject invalid normal Fusion, Convergence Fusion and Convergence Transfer requests on the server before any inventory, resource or history mutation, resolving findings F-003–F-005.

# Acceptance criteria

- [x] Normal Fusion rejects different item IDs before mutation while existing lookup continues to enforce matching tier, distinct copies and no active imbuements.
- [x] Convergence Fusion accepts only different class-4 item IDs with the same normalized equipment slot and requested tier; existing lookup/tier limits remain effective.
- [x] Convergence Transfer requires both donor and receiver to be class 4; existing normal Transfer behavior from PR #89 remains unchanged.
- [x] Focused negative integration tests prove unchanged items, tiers, Dust, cores, bank/gold, exaltation chest count and Forge history.
- [x] Existing identical-item normal Fusion and normal Transfer success regressions remain valid.
- [x] Relevant focused checks completed on the implementation diff.
- [ ] Fresh final-head GitHub checks verified after final documentation bookkeeping.
- [x] Module catalogue impact handled.
- [x] Documentation/changelog impact handled.
- [x] Program queue/handoff updated.
- [x] Cross-repository impact confirmed none.
- [ ] Autonomous merge gate satisfied.

# Confirmed result

- `Player::forgeFuseItems` now resolves both concrete items and then validates the pair before resource pre-validation, chest creation, input removal or history registration.
- Normal Fusion requires the same item ID and matching nonzero classification.
- Convergence Fusion requires different item IDs, both classification 4 and the same slot after the existing two-hand-to-hand normalization.
- `Player::getForgeItemFromId` remains responsible for exact requested tier, distinct instances and rejecting active imbuements.
- `Player::forgeTransferItemTier` now calls `ForgeTransferPolicy::isValidTransfer`; convergence requires matching class 4 while normal Transfer preserves PR #89 tier/classification behavior.
- No opcode, payload, database schema, OTClient or upstream repository changed.

# Existing work reused

| Module/task/PR | Reuse | Evidence/path | Result |
|---|---|---|---|
| PR #89 | Normal Transfer classification, donor-tier, resource-tier and result-tier policy | `forge_transfer_policy.hpp`, Player and tests | Preserved; normal class-3 tier-2 policy remains accepted. |
| `Player::getForgeItemFromId` | Concrete item resolution, tier, distinct-copy and imbuement checks | `player.cpp` | Reused before pair policy. |
| Forge integration fixture | Real Player inventory/resource/history state | `tests/integration/game/forge_it.cpp` | Extended with no-mutation rejection regressions. |
| Validation report | Finding/evidence source of truth | `OTS_AI_EQUIPMENT_UPGRADE_VALIDATION.md` | F-003–F-005 marked remediated on PR branch with compiled-regression evidence only. |

# Ownership and overlap

- Open Forge/Equipment Upgrade/Exaltation PR searches found no competing implementation PR.
- PR #245 is the shared E2E platform and changes no Forge gameplay.
- Temporary runner PR #252 and evidence runner PR #253 were trigger-only and closed unmerged.
- `player.cpp` is broad, but the diff is localized to `forgeFuseItems` and `forgeTransferItemTier`.
- Final permanent diff contains no runner workflow/script, no `ACTIVE_WORK.md`, no protocol/client change and no upstream write.

# Implementation summary

1. Added `ForgeFusionPolicy::isValid` as a pure constexpr contract.
2. Extended `ForgeTransferPolicy` with convergence-aware classification and combined transfer validation.
3. Added the Fusion pair check immediately after resolving both inputs.
4. Replaced the historical different-ID normal Fusion success regression with a no-mutation rejection test.
5. Added class-4 Convergence Fusion/Transfer rejection integration coverage.
6. Added pure policy boundary tests for identity, class and normalized-slot rules.
7. Updated the validation report, module catalogue, changelog and parity program.

# Work log

## 2026-07-13T13:15:00+02:00

- Created the parity program, task branch and ownership record.
- Confirmed no active overlapping Forge implementation PR.
- Local clone remained blocked by `Could not resolve host: github.com`.

## Source materialization

- Direct local patching was unavailable; a controlled exact-anchor runner was used.
- Failed source runner runs `29249939468` and `29250125565` found no matching anchor and changed no source.
- Diagnostic run `29250247910` proved Python `dedent` had removed the leading C++ tab.
- The script was rewritten with explicit line markers that preserve whitespace.
- Successful source runner: run `29250410323`, job `86817279766`; source commit `fa6bf1fcf4767db13cc3ee84136c3223ffd7f04a`.
- Runner PR #252 was closed unmerged.
- Fast Checks later produced formatting commit `f50c9c73eeb5265461409d419c5daf853fc17ab4`.

## Documentation evidence

- Evidence runner attempts stopped safely on stale catalogue/changelog anchors or workflow bookkeeping; no partial branch commit occurred.
- Successful evidence runner: run `29252490066`, job `86824214976`.
- Runner PR #253 was closed unmerged.
- All temporary workflow/script files were removed from #250 before final-head validation.

# Validation and CI

| Commit/run | Check | Result | Exact evidence boundary |
|---|---|---|---|
| branch environment | local clone/build/test | blocked | DNS failure; no local result claimed |
| `bc1bd696e0ec28e8e6f2b208c27e4164b50f074b`, run `29249235355` | early PR CI | partial only | source patch had not run; build/test jobs skipped |
| implementation diff, run `29250747788` | Lua Tests | success | Lua regression suite passed |
| implementation diff, run `29250747788` | Fast Checks | success | clang-format, StyLua, cmake-format, analysis, yamllint and Lua API documentation checks passed; formatter commit created |
| implementation diff, job `86818664373` | Linux debug | success | CMake, Canary smoke, DB schema import and full `Run Tests` passed |
| implementation diff, job `86818664416` | Linux release | success | CMake, generated Lua docs and Canary/global datapack smoke passed |
| implementation diff, job `86818664344` | macOS | success | configure/build, MySQL and runtime smoke passed |
| implementation diff, jobs `86818664418`, `86818664461` | Windows | success | CMake/runtime path and MSBuild path passed |
| implementation diff, job `86818664405` | Docker | success | image build/export/validation passed |
| final documentation head | full PR CI | pending | required before merge; earlier run is not substituted for final-head evidence |

This is semantic, compiled-regression and generic runtime-smoke evidence. It is not a focused physical-client Forge gameplay test.

# Decisions

| Decision | Reason/evidence |
|---|---|
| Keep authority separate from rollback/history fixes | Makes rejection behavior reviewable and leaves F-020/F-021 mutation ordering explicit. |
| Normalize two-handed items to the hand slot | Matches the existing supported-client Forge list contract. |
| Reject before all mutation | Crafted/stale packets must not consume or create resources. |
| Use pure policy helpers | Enables deterministic boundary tests without changing protocol or persistence. |
| Keep gameplay/E2E status separate | Multi-platform CI and runtime smoke do not prove a player completed every Forge scenario. |

# Risks and compatibility

- Runtime: checks execute only after both actual items are resolved and before mutation.
- Security: closes crafted/stale packet trust gaps.
- Backward compatibility: normal Transfer policy from #89 and valid same-ID normal Fusion remain covered.
- Data/migration: none.
- Cross-repository rollout: none.
- Rollback: squash-revert #250.

# Remaining work

1. Recheck final permanent diff, open overlaps, current `main` and review threads.
2. Mark #250 Ready and inspect every final-head workflow/job.
3. Squash-merge if the autonomous gate is clean.
4. Archive this task in a separate lifecycle PR.
5. Start F-020/F-021 atomicity/rollback from the merged `main`.

# Handoff

Start with PR #250, this task, `forge_fusion_policy.hpp`, `forge_transfer_policy.hpp`, the localized Player Forge functions and focused tests.

Do not:
- reopen #177/#241/#246/#252/#253;
- add protocol or OTClient changes to this PR;
- combine rollback, history, Premium, effects or bonus payload work;
- treat generic CI/runtime smoke as full gameplay or physical-client E2E proof.

# Completion

- Final status: ready_for_review_pending_final_ci
- PR: #250
- Merge commit:
- Program record updated: pending final-head SHA/merge
- Catalogue updated: yes
- Changelog updated: yes
- Archived at:
