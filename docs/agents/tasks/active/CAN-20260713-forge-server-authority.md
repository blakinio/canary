---
task_id: CAN-20260713-forge-server-authority
program_id: CAN-PROGRAM-EQUIPMENT-UPGRADE-PARITY
coordination_id: ""
status: active
agent: "GPT-5.6 Thinking"
branch: fix/forge-server-authority
base_branch: main
created: 2026-07-13T13:15:00+02:00
updated: 2026-07-13T14:25:00+02:00
last_verified_commit: "60606cd13c11c75edb6588fcf0ff300f8b4493e5"
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
    - .github/workflows/forge-server-authority-patch.yml
    - tools/ai-agent/apply_forge_server_authority_patch.py
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

- [ ] Normal Fusion rejects different item IDs before mutation while existing lookup continues to enforce matching tier, distinct copies and no active imbuements.
- [ ] Convergence Fusion accepts only different class-4 item IDs with the same normalized equipment slot and requested tier; existing lookup/tier limits remain effective.
- [ ] Convergence Transfer requires both donor and receiver to be class 4; existing normal Transfer behavior from PR #89 remains unchanged.
- [ ] Focused negative integration tests prove unchanged items, tiers, Dust, cores, bank/gold, exaltation chest count and Forge history.
- [ ] Existing identical-item normal Fusion and normal Transfer success regressions remain valid.
- [ ] Relevant focused checks completed.
- [ ] Current-head GitHub checks verified.
- [ ] Module catalogue impact handled.
- [ ] Documentation/changelog impact handled.
- [ ] Program queue/handoff updated.
- [ ] Cross-repository impact confirmed none.
- [ ] Autonomous merge gate satisfied.

# Confirmed context

- Current program base was created from `main` after merge #244; branch base is `3ad10132cbd76adc42f946da3ca3077e5bd6bbd0`.
- Open PR search found no Forge implementation PR. PR #245 is a reusable E2E platform and changes no Forge gameplay.
- The current report classifies F-003, F-004 and F-005 as still open.
- `ProtocolGame::sendOpenForge` filters normal Fusion to two equal IDs/tier, groups Convergence Fusion by class 4 and normalized slot, and groups Convergence Transfer by classification. Those client-facing lists are not server authority.
- `Player::forgeFuseItems` resolves two items and pre-validates resources but does not enforce the complete normal/Convergence pair contract before mutation.
- `Player::forgeTransferItemTier` checks donor tier and matching nonzero classification, but a crafted convergence request can use a non-class-4 pair.
- The local command `git clone --filter=blob:none --no-checkout https://github.com/blakinio/canary.git` failed with `Could not resolve host: github.com`; no local build or test is claimed.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| PR #89 | Preserve normal Transfer classification/donor-tier/resource/result rules | `src/game/functions/forge_transfer_policy.hpp`, Player and tests | Avoids regression while adding only convergence class-4 authority. |
| Current Forge integration fixture | Extend item types and resource invariants | `tests/integration/game/forge_it.cpp` | Already exercises Player Forge flow with real inventory/resource state. |
| `Player::getForgeItemFromId` | Resolve distinct copies, matching tier and reject imbued items before pair authority | `player.cpp` | Existing same-ID and single-copy regressions must remain intact. |
| Validation report | Update F-003–F-005 evidence after checks | `docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_VALIDATION.md` | Durable finding source of truth. |

# Ownership and overlap check

- Program record: `docs/agents/programs/EQUIPMENT_UPGRADE_PARITY_PROGRAM.md`.
- Open PRs inspected: Forge/Equipment Upgrade/Exaltation searches; only unrelated E2E platform #245 matched generic Forge text.
- Active tasks inspected: `ACTIVE_WORK.md`, live open PRs and repository search; no active Forge implementation task found.
- Ownership checker result: local checker unavailable because the repository cannot be cloned; GitHub Agent Task Ownership workflow is required on every current head.
- Exclusive claims: localized Player Forge functions, both policy helpers, focused Forge unit/integration tests, task record and temporary task-local patch files.
- Shared claims: program, report, catalogue and changelog only for narrow status/interface entries.
- Read-only dependencies: protocol list generation and cross-repository registry.
- Overlaps: `player.cpp` is a broad runtime file; no current open PR owns the Forge functions.
- Resolution: make only localized Forge-function edits, remove temporary runner files before readiness and recheck all open PR changed files.

# Current state

The server trusts several client-selected Fusion/Convergence properties. Existing different-ID normal Fusion integration coverage currently succeeds, demonstrating F-003. Convergence-specific negative tests are absent.

# Plan

1. Apply one pair-authority block in `Player::forgeFuseItems` before resource pre-validation.
2. Extend the existing transfer helper with class-4 convergence authority and call it before resource mutation.
3. Convert the historical different-ID normal Fusion success test into a no-mutation rejection regression.
4. Add Convergence Fusion rejection tests for non-class-4, same ID and different normalized slot.
5. Add Convergence Transfer rejection for non-class-4 and preserve normal Transfer success coverage.
6. Remove temporary patch workflow/script from the final diff.
7. Update report, program, catalogue, changelog, task and PR evidence.
8. Inspect current-head CI job by job, fix failures, mark ready and squash-merge when the autonomous gate is satisfied.

# Work log

## 2026-07-13T13:15:00+02:00

- Changed: created the parity program, task branch and ownership record.
- Learned: no active Forge implementation PR exists; the generic E2E platform is non-overlapping.
- Failed/blocked: local clone failed because `github.com` DNS resolution is unavailable.
- Result: bounded F-003–F-005 task became visible.

## 2026-07-13T14:25:00+02:00

- Changed: opened draft PR #250; created a task-local exact-anchor workflow and an idempotent Python patch script because full local Git operations are unavailable.
- Learned: the first push containing a newly introduced workflow did not execute that workflow; ordinary PR CI on `bc1bd696e0ec28e8e6f2b208c27e4164b50f074b` only validated the documentation/workflow scope and skipped source builds/tests.
- Failed/blocked: no source patch has yet been claimed applied; temporary runner files must not remain in the final diff.
- Result: ownership now covers every path the bounded patch will edit.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Keep authority separate from rollback/history fixes | Makes rejection behavior reviewable and avoids masking F-020/F-021 mutation-order work | none |
| Match the same two-hand-to-hand normalization used by `sendOpenForge` | Keeps server validation aligned with the existing supported-client list contract | none |
| Reject before all resource and inventory mutation | Required to prove crafted requests cannot consume or create anything | none |
| Use a temporary exact-anchor patch runner | GitHub contents API cannot safely replace a 13k-line C++ file without a local clone; anchors fail closed on drift | none |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `src/creatures/players/player.cpp` | exclusive | Server authority before Forge mutation | planned |
| `src/game/functions/forge_fusion_policy.hpp` | exclusive | Pure regular/Convergence Fusion pair policy | planned |
| `src/game/functions/forge_transfer_policy.hpp` | exclusive | Preserve normal rules and add convergence class-4 policy | planned |
| `tests/unit/players/forge_test.cpp` | exclusive | Pure policy boundaries | planned |
| `tests/integration/game/forge_it.cpp` | exclusive | Crafted-request and no-mutation regressions | planned |
| temporary patch workflow/script | exclusive | Controlled branch-local materialization only | temporary; remove before readiness |
| program/report/catalogue/changelog | shared | Durable status, interface and sequencing | pending |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| branch start | local clone/build/test | blocked | `Could not resolve host: github.com`; no local result claimed |
| `bc1bd696e0ec28e8e6f2b208c27e4164b50f074b` | CI run `29249235355` | partial only | Detect Build Scope/Required succeeded; Fast/Lua/Linux/platform jobs skipped because source patch had not run |

Never write `passed` without verification on the stated commit.

# Failed approaches and dead ends

- Local clone and local validation are unavailable due DNS resolution failure.
- Adding the temporary workflow and expecting it to execute in the same introducing push did not materialize the patch; a subsequent existing-workflow update is required.

# Risks and compatibility

- Runtime: rejection order must remain before chest creation, input removal, resource deductions and history registration.
- Data/migration: none.
- Security: closes crafted/stale packet trust gaps.
- Backward compatibility: valid normal Fusion/Transfer and valid class-4 Convergence operations must remain accepted.
- Cross-repo rollout: none; no payload or opcode change.
- Rollback: squash revert of this bounded PR restores prior authority behavior.

# Remaining work

1. Execute the existing task-local runner, inspect the exact patch and remove runner files.
2. Validate and finish PR #250.

# Handoff

## Start here

Open PR #250, this task, `Player::forgeFuseItems`, `Player::forgeTransferItemTier`, both policy helpers, `tests/integration/game/forge_it.cpp` and the parity program.

## Do not repeat

- Do not reopen #177/#241/#246.
- Do not edit protocol or OTClient for this task.
- Do not bundle atomic rollback, history, rewards, effects or bonus payload work.
- Do not treat the partial CI run before source materialization as implementation evidence.

## Required reads

- `AGENTS.md`
- `docs/agents/README.md`
- `docs/agents/programs/EQUIPMENT_UPGRADE_PARITY_PROGRAM.md`
- `docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_VALIDATION.md`
- current Forge source/tests and open PRs

## Open questions

- None for F-003–F-005; the selected constraints are explicit in the report and current client-facing list generation.

# Completion

- Final status: active
- PR: #250
- Merge commit:
- Program record updated: initial
- Catalogue updated: pending helper entry
- Changelog updated: pending
- Archived at:
