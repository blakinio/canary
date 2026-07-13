---
task_id: CAN-20260713-forge-server-authority
program_id: CAN-PROGRAM-EQUIPMENT-UPGRADE-PARITY
coordination_id: ""
status: active
agent: "GPT-5.6 Thinking"
branch: fix/forge-server-authority
base_branch: main
created: 2026-07-13T13:15:00+02:00
updated: 2026-07-13T13:15:00+02:00
last_verified_commit: "3ad10132cbd76adc42f946da3ca3077e5bd6bbd0"
risk: medium
related_issue: ""
related_pr: "draft pending"
depends_on:
  - PR #89 normal Transfer policy
  - PR #110 Forge history item identity
  - PR #177 Dust reward remediation
blocks:
  - later Forge atomicity/history/reward/effect tasks only by shared Player path sequencing
owned_paths:
  exclusive:
    - src/creatures/players/player.cpp
    - tests/integration/game/forge_it.cpp
    - docs/agents/tasks/active/CAN-20260713-forge-server-authority.md
  shared:
    - docs/agents/programs/EQUIPMENT_UPGRADE_PARITY_PROGRAM.md
    - docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_VALIDATION.md
    - docs/agents/CHANGELOG.md
  read_only:
    - src/server/network/protocol/protocolgame.cpp
    - src/game/functions/forge_transfer_policy.hpp
    - tests/unit/players/forge_test.cpp
    - docs/agents/CROSS_REPO_CONTRACTS.md
modules_touched:
  - Player Forge Fusion authority
  - Player Forge Transfer authority
  - Forge integration tests
reuses:
  - existing `Player::getForgeItemFromId` distinct-instance lookup
  - `ForgeTransferPolicy` rules merged in PR #89
  - current integration fixture in `tests/integration/game/forge_it.cpp`
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Reject invalid normal Fusion, Convergence Fusion and Convergence Transfer requests on the server before any inventory, resource or history mutation, resolving findings F-003–F-005.

# Acceptance criteria

- [ ] Normal Fusion rejects different item IDs, imbued inputs, non-forgeable classification/tier and any other crafted request outside the live rules before mutation.
- [ ] Convergence Fusion accepts only different class-4 item IDs with the same normalized equipment slot and same requested tier, without imbuements and below the configured class-4 tier cap.
- [ ] Convergence Transfer requires both donor and receiver to be class 4; existing normal Transfer behavior from PR #89 remains unchanged.
- [ ] Focused negative integration tests prove unchanged items, tiers, Dust, cores, bank/gold, exaltation chest count and Forge history.
- [ ] Existing identical-item normal Fusion and normal Transfer success regressions remain valid.
- [ ] Relevant focused checks completed.
- [ ] Current-head GitHub checks verified.
- [ ] Module catalogue impact handled or confirmed none.
- [ ] Documentation/changelog impact handled.
- [ ] Program queue/handoff updated.
- [ ] Cross-repository impact confirmed none.
- [ ] Autonomous merge gate satisfied.

# Confirmed context

- Current program base was created from `main` after merge #244; latest observed main commit before branch creation was `3ad10132cbd76adc42f946da3ca3077e5bd6bbd0`.
- Open PR search found no Forge implementation PR. PR #245 is a reusable E2E platform and changes no Forge gameplay.
- The current report classifies F-003, F-004 and F-005 as still open.
- `ProtocolGame::sendOpenForge` filters normal Fusion to two equal IDs/tier, groups Convergence Fusion by class 4 and normalized slot, and groups Convergence Transfer by classification. Those client-facing lists are not server authority.
- `Player::forgeFuseItems` currently resolves two items and pre-validates resources but does not enforce the complete normal/Convergence pair contract before mutation.
- `Player::forgeTransferItemTier` currently checks donor tier and matching nonzero classification, but a crafted convergence request can use a non-class-4 pair.
- The local command `git clone --filter=blob:none --no-checkout https://github.com/blakinio/canary.git` failed with `Could not resolve host: github.com`; no local build or test will be claimed unless that environment changes.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| PR #89 | Preserve normal Transfer classification/donor-tier/resource/result rules | `src/game/functions/forge_transfer_policy.hpp`, Player and tests | Avoids regression while adding only convergence class-4 authority. |
| Current Forge integration fixture | Extend item types and resource invariants | `tests/integration/game/forge_it.cpp` | Already exercises Player Forge flow with real inventory/resource state. |
| `Player::getForgeItemFromId` | Resolve distinct copies before validation | `player.cpp` | Existing same-ID regression must remain intact. |
| Validation report | Update F-003–F-005 evidence after checks | `docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_VALIDATION.md` | Durable finding source of truth. |

# Ownership and overlap check

- Program record: `docs/agents/programs/EQUIPMENT_UPGRADE_PARITY_PROGRAM.md`.
- Open PRs inspected: Forge/Equipment Upgrade/Exaltation searches; only unrelated E2E platform #245 matched generic Forge text.
- Active tasks inspected: `ACTIVE_WORK.md`, live open PRs and repository search; no active Forge implementation task found.
- Ownership checker result: unavailable locally because the repository cannot be cloned; GitHub Agent Task Ownership workflow will be the recorded check.
- Exclusive claims: `player.cpp`, Forge integration test and this task record.
- Shared claims: program record, validation report and changelog only for narrow status entries.
- Read-only dependencies: protocol filtering, transfer policy/unit tests and cross-repo contract registry.
- Overlaps: `player.cpp` is a broad shared runtime file; no current open Forge PR owns the Forge functions.
- Resolution: make only localized Forge-function edits and recheck open PR changed files before readiness.

# Current state

The server trusts several client-selected Fusion/Convergence properties. Existing different-ID normal Fusion integration coverage currently succeeds, demonstrating F-003. Convergence-specific negative tests are absent.

# Plan

1. Add one local normalization/authority block in `Player::forgeFuseItems` before resource pre-validation.
2. Add class-4 and no-imbuement convergence authority in `Player::forgeTransferItemTier` before resource mutation.
3. Convert the historical different-ID normal Fusion success test into a no-mutation rejection regression.
4. Add Convergence Fusion rejection tests for non-class-4, same ID and different normalized slot.
5. Add Convergence Transfer rejection for non-class-4 and verify normal Transfer success remains unchanged.
6. Update report, program, changelog, task and PR evidence.
7. Inspect current-head CI job by job, fix failures, mark ready and squash-merge when the autonomous gate is satisfied.

# Work log

## 2026-07-13T13:15:00+02:00

- Changed: created the parity program, task branch and ownership record.
- Learned: no active Forge implementation PR exists; the generic E2E platform is non-overlapping.
- Failed/blocked: local clone failed because `github.com` DNS resolution is unavailable.
- Result: bounded F-003–F-005 task is visible and ready for implementation through GitHub API.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Keep authority separate from rollback/history fixes | Makes rejection behavior reviewable and avoids masking F-020/F-021 mutation-order work | none |
| Match the same two-hand-to-hand normalization used by `sendOpenForge` | Keeps server validation aligned with the existing supported-client list contract | none |
| Reject before all resource and inventory mutation | Required to prove crafted requests cannot consume or create anything | none |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `src/creatures/players/player.cpp` | exclusive | Server authority before Forge mutation | planned |
| `tests/integration/game/forge_it.cpp` | exclusive | Crafted-request and no-mutation regressions | planned |
| parity program/report/changelog | shared | Durable status and sequencing | planned |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| branch start | local clone/build/test | blocked | `Could not resolve host: github.com`; no local result claimed |

Never write `passed` without verification on the stated commit.

# Failed approaches and dead ends

- Local clone from GitHub is unavailable in the execution container due DNS resolution failure.

# Risks and compatibility

- Runtime: rejection order must remain before chest creation, input removal, resource deductions and history registration.
- Data/migration: none.
- Security: closes crafted/stale packet trust gaps.
- Backward compatibility: valid normal Fusion/Transfer and valid class-4 Convergence operations must remain accepted.
- Cross-repo rollout: none; no payload or opcode change.
- Rollback: squash revert of this bounded PR restores prior authority behavior.

# Remaining work

1. Implement server authority and focused integration tests.

# Handoff

## Start here

Open this task, `Player::forgeFuseItems`, `Player::forgeTransferItemTier`, `tests/integration/game/forge_it.cpp` and the parity program.

## Do not repeat

- Do not reopen #177/#241/#246.
- Do not edit protocol or OTClient for this task.
- Do not bundle atomic rollback, history, rewards, effects or bonus payload work.

## Required reads

- `AGENTS.md`
- `docs/agents/README.md`
- `docs/agents/programs/EQUIPMENT_UPGRADE_PARITY_PROGRAM.md`
- `docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_VALIDATION.md`
- current Forge source/tests and open PRs

## Open questions

- None for F-003–F-005; the selected constraints are already explicit in the current report and client-facing list generation.

# Completion

- Final status: active
- PR: draft pending
- Merge commit:
- Program record updated: initial
- Catalogue updated: not required unless a public helper/interface is added
- Changelog updated: pending
- Archived at:
