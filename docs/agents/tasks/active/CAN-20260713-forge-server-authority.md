---
task_id: CAN-20260713-forge-server-authority
program_id: CAN-PROGRAM-EQUIPMENT-UPGRADE-PARITY
coordination_id: ""
status: ready_for_review_pending_final_ci
agent: "GPT-5.6 Thinking"
branch: fix/forge-server-authority
base_branch: main
created: 2026-07-13T13:15:00+02:00
updated: 2026-07-13T15:51:00+02:00
last_verified_commit: "c4a58a5c9c87614e31709111433a247b1fc841b6"
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

- [x] Normal Fusion rejects different item IDs before mutation while existing lookup enforces matching tier, distinct copies and no active imbuements.
- [x] Convergence Fusion accepts only different class-4 item IDs with the same normalized equipment slot and requested tier.
- [x] Convergence Transfer requires class 4; normal Transfer behavior from PR #89 remains unchanged.
- [x] Negative integration tests prove unchanged items, tiers, Dust, cores, bank/gold, exaltation chest count and history.
- [x] Existing valid normal Fusion and normal Transfer regressions remain valid.
- [x] Focused implementation-diff checks completed.
- [ ] Fresh final-head GitHub checks verified after all bookkeeping.
- [x] Module catalogue, report, changelog and program updated.
- [x] Cross-repository impact confirmed none.
- [ ] Autonomous merge gate satisfied.

# Confirmed result

- `Player::forgeFuseItems` validates the resolved item pair before resource checks, chest creation, input removal or history registration.
- Normal Fusion requires identical item IDs and matching nonzero classification.
- Convergence Fusion requires different IDs, both class 4 and the same slot after two-hand-to-hand normalization.
- `Player::getForgeItemFromId` retains exact tier, distinct-instance and active-imbuement rejection.
- `Player::forgeTransferItemTier` uses convergence-aware `ForgeTransferPolicy::isValidTransfer`; normal Transfer preserves #89.
- No opcode, payload, persistence schema, OTClient or upstream repository changed.

# Permanent changed paths

- `src/creatures/players/player.cpp`
- `src/game/functions/forge_fusion_policy.hpp`
- `src/game/functions/forge_transfer_policy.hpp`
- `tests/unit/players/forge_test.cpp`
- `tests/integration/game/forge_it.cpp`
- `docs/agents/programs/EQUIPMENT_UPGRADE_PARITY_PROGRAM.md`
- this task record
- `docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_VALIDATION.md`
- `docs/agents/MODULE_CATALOG.md`
- `docs/agents/CHANGELOG.md`

No temporary workflow/script, `ACTIVE_WORK.md`, protocol or client file remains in the diff.

# Ownership and overlap

- Current `main` remained `3ad10132cbd76adc42f946da3ca3077e5bd6bbd0` at final preflight.
- Open Forge search returned #250 and #245 only.
- #245 owns only universal E2E workflow/runner/scenario paths and has no overlap with #250.
- No open implementation PR owns the Player Forge functions or policy/test paths.
- Review threads on #250: none at final preflight.

# Implementation summary

1. Added pure `ForgeFusionPolicy::isValid`.
2. Extended `ForgeTransferPolicy` with convergence-aware classification and combined validation.
3. Added pair authority immediately after resolving both Fusion inputs.
4. Replaced the invalid different-ID Fusion success regression with no-mutation rejection coverage.
5. Added class-4 Convergence Fusion/Transfer integration rejection coverage.
6. Added pure policy tests for identity, class and normalized-slot boundaries.

# Controlled runner history

The execution environment could not resolve `github.com`, so local clone/build/test remained unavailable.

- Source runner failures `29249939468` and `29250125565`: exact anchor mismatch; no source change.
- Diagnostic source run `29250247910`: proved `dedent` removed a leading C++ tab.
- Successful source runner `29250410323`, job `86817279766`, source commit `fa6bf1fcf4767db13cc3ee84136c3223ffd7f04a`.
- Source runner PR #252 closed unmerged.
- Evidence runner stopped safely on stale anchors/workflow bookkeeping until successful run `29252490066`, job `86824214976`.
- Evidence runner PR #253 closed unmerged.
- Report-history correction run `29252914527`, job `86825584473`, succeeded; runner PR #254 closed unmerged.
- All runner workflow/script files were removed from the permanent PR diff.

# Validation and CI

| Scope | Run/job | Result | Boundary |
|---|---|---|---|
| local environment | clone/build/test | blocked | `Could not resolve host: github.com`; no local pass claimed |
| early pre-source head | CI `29249235355` | partial only | source builds/tests skipped; not implementation evidence |
| implementation diff | CI `29250747788` | success | full multi-platform readiness run |
| Linux debug | job `86818664373` | success | CMake, Canary smoke, schema import and full `Run Tests` |
| Linux release | job `86818664416` | success | CMake, generated Lua docs, Canary/global datapack smoke |
| macOS | job `86818664344` | success | configure/build, MySQL and runtime smoke |
| Windows | jobs `86818664418`, `86818664461` | success | CMake/runtime and MSBuild paths |
| Docker | job `86818664405` | success | image build/export/validation |
| Fast Checks | run `29250747788` | success | formatting/static/doc checks; produced formatter commit `f50c9c73eeb5265461409d419c5daf853fc17ab4` |
| final head `c4a58a5c...` | CI `29253241129` | partial success / infrastructure-stalled | Lua, Fast Checks, Windows, Docker, Linux debug smoke/schema/full tests and Imbuement Validation passed; Linux release stalled in `Install mono for NuGet` without code failure |
| fresh retrigger head | pending | required | bookkeeping-only commit retriggers the full final gate for unchanged production code |

This is semantic, compiled-regression and generic runtime-smoke evidence. It is not focused Forge gameplay or physical-client E2E proof.

# Decisions

- Authority stays separate from F-020/F-021 rollback and F-022–F-024 history work.
- Two-handed slots normalize to hand, matching the current supported-client list contract.
- Rejection happens before every mutation.
- Pure policy helpers provide deterministic boundary coverage.
- Multi-platform CI does not promote the module to full gameplay/E2E parity.

# Risks and compatibility

- Runtime: only localized Forge handlers changed.
- Security: crafted/stale packet trust gaps close.
- Backward compatibility: #89 normal Transfer and valid same-ID Fusion remain covered.
- Data/migration: none.
- Cross-repository rollout: none.
- Rollback: squash-revert #250.

# Remaining work

1. Verify the fresh final-head workflow after the infrastructure-stalled release job.
2. Squash-merge if current-main, overlap, review and CI gates remain clean.
3. Archive this task in a separate lifecycle PR.
4. Start F-020/F-021 atomicity/rollback from merged `main`.

# Handoff

Do not reopen #177, #241, #246, #252, #253 or #254. Do not add protocol/OTClient, rollback, history, Premium, effects or bonus payload work to #250. Preserve the new authority policies in all later tasks.

# Completion

- Final status: ready_for_review_pending_final_ci
- PR: #250
- Merge commit:
- Program record updated: yes, pending final head/merge
- Catalogue updated: yes
- Changelog updated: yes
- Archived at:
