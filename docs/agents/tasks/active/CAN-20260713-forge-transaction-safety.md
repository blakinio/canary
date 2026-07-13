---
task_id: CAN-20260713-forge-transaction-safety
program_id: CAN-PROGRAM-EQUIPMENT-UPGRADE-PARITY
coordination_id: ""
status: in_progress
agent: "GPT-5.6 Thinking"
branch: fix/forge-transaction-safety
base_branch: fix/forge-server-authority
created: 2026-07-13T16:02:00+02:00
updated: 2026-07-13T16:02:00+02:00
last_verified_commit: "d5ca8d3ecfa1d83f69184e1f7ba58dd7906693e5"
risk: high
related_issue: ""
related_pr: ""
depends_on:
  - PR #250 Forge server authority
blocks:
  - F-022 through F-024 history remediation
owned_paths:
  exclusive:
    - src/creatures/players/player.cpp
    - src/game/functions/forge_transaction.hpp
    - tests/unit/players/forge_transaction_test.cpp
    - tests/integration/game/forge_it.cpp
    - docs/agents/tasks/active/CAN-20260713-forge-transaction-safety.md
  shared:
    - docs/agents/programs/EQUIPMENT_UPGRADE_PARITY_PROGRAM.md
    - docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_VALIDATION.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - src/game/game.hpp
    - src/items/cylinder.hpp
    - src/items/thing.hpp
modules_touched:
  - Forge Fusion mutation commit
  - Forge Transfer mutation commit
  - Forge Sliver-to-Core conversion
  - Forge transactional regression coverage
reuses:
  - PR #250 authority policies and rejection order
  - `Game::internalAddItem(..., test=true)`
  - `Game::internalRemoveItem(..., test=true)`
  - Player bank, Dust and inventory APIs
public_interfaces:
  - internal Forge transaction plan/rollback helper
cross_repo_tasks: []
---

# Goal

Resolve F-020 and F-021 by making valid Fusion, Transfer and Sliver-to-Core conversion all-or-nothing across inventory items, Dust, Forge cores/slivers, money and history.

# Acceptance criteria

- [ ] All output items and prices are created/resolved before mutation.
- [ ] Every staged item addition/removal is preflighted with Game test mode.
- [ ] A commit failure restores original input items, resource counts, Dust and money/bank state.
- [ ] History/result packets are emitted only after commit success.
- [ ] Sliver-to-Core never consumes Slivers unless the Core was successfully committed.
- [ ] Existing #250 invalid-request authority tests remain green.
- [ ] Focused rollback/no-mutation tests cover Fusion, Transfer and conversion boundaries.
- [ ] Full current-head CI passes before merge.

# Design boundary

This task does not change retail costs, probabilities, bonus meanings, history descriptions, Premium eligibility, protocol fields or OTClient presentation. It only changes transaction ordering and rollback behavior.

# Initial evidence

- Fusion currently creates/adds the Exaltation Chest, removes both inputs and then performs additional fallible output/resource operations.
- Transfer currently removes both inputs and creates/adds the receiver before deducting all resources.
- Sliver-to-Core currently removes Slivers before creating/adding the Core.
- `Game` exposes test-mode add/remove APIs, and item parent/index can be captured through `Thing::getParent()` plus `Cylinder::getThingIndex()`.

# Work plan

1. Add a small internal transaction helper with staged item operations and resource snapshots.
2. Refactor Sliver-to-Core first as the minimal proof.
3. Refactor Transfer while preserving #89/#250 policy.
4. Refactor Fusion while preserving all current result/bonus semantics.
5. Add deterministic commit-failure injection at the helper boundary for tests only.
6. Run focused and full CI, update the validation report, then retarget the stacked PR to `main` after #250 merges.

# Completion

- Final status: in_progress
- PR:
- Merge commit:
- Archived at:
