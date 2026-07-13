---
task_id: CAN-20260713-forge-transaction-safety
program_id: CAN-PROGRAM-EQUIPMENT-UPGRADE-PARITY
coordination_id: ""
status: ready_for_merge_pending_final_head_ci
agent: "GPT-5.6 Thinking"
branch: fix/forge-transaction-safety
base_branch: main
created: 2026-07-13T16:02:00+02:00
updated: 2026-07-13T17:42:00+02:00
last_verified_commit: "0a7acd0a70ff7601c63638bbf705d961ada881b1"
risk: high
related_issue: ""
related_pr: "#257"
depends_on:
  - PR #250 Forge server authority, merged as 94f8a3b63271b3708e33496e937620a6cd4b9717
blocks:
  - F-022 through F-024 history remediation
owned_paths:
  exclusive:
    - src/creatures/players/player.cpp
    - src/game/functions/forge_transaction.hpp
    - tests/unit/players/forge_transaction_test.cpp
    - tests/unit/players/CMakeLists.txt
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

- [x] All output items and prices are created/resolved before mutation.
- [x] Every staged item addition/removal is preflighted with Game test mode where the Game API supports it.
- [x] A commit failure restores original input items, stackable resource counts and money/bank state.
- [x] Dust, history and result packets are mutated/emitted only after commit success.
- [x] Sliver-to-Core never consumes Slivers unless the Core can be placed and the commit succeeds.
- [x] Existing #250 invalid-request authority tests remain green.
- [x] Focused transaction-helper tests cover success, false return after partial mutation, exception rollback, reverse order and one-shot commit.
- [x] Integration tests cover successful Sliver-to-Core conversion and full-backpack no-mutation rejection.
- [x] Full implementation-head CI `29261872735` passed after synchronization with `main`.
- [ ] Fresh final-head CI passes after this evidence-only task update.

# Confirmed result

- Fusion precomputes costs, result tiers and every output item before inventory/resource mutation.
- Fusion preflights chest insertion and both input removals, snapshots parents/indexes, stackable resources and money, then commits through `ForgeTransaction`.
- Transfer follows the same prepare/preflight/snapshot/commit model while preserving PR #89 and #250 policy.
- Sliver-to-Core creates and preflights the Core before removing Slivers; a failed commit restores both resource counts.
- `ForgeTransaction` rolls back the failed step and prior completed steps in reverse order for both `false` returns and exceptions.
- History registration, metrics and result packets occur only after a successful transaction.

# Validation

- Permanent diff: this task, `player.cpp`, internal transaction header, registered unit test, players unit CMake and Forge integration test.
- Implementation-head CI: `29261872735` — success.
- Linux debug compiled, passed Canary smoke, imported the database schema and passed full `Run Tests`.
- Linux release, macOS, Windows CMake/MSBuild and Docker build/runtime paths passed.
- Lua Tests, Fast Checks, Agent Task Ownership, Imbuement Validation and autofix passed.
- Temporary materialization PR #258, compile-fix PR #266 and main-sync PR #269 were closed without merge; all runner files were removed.
- Local clone/build remained unavailable because the execution container could not resolve `github.com`; no local pass is claimed.
- This is deterministic transaction-unit/integration and repository runtime-smoke evidence, not a physical-client gameplay test.

# Design boundary

This task does not change retail costs, probabilities, bonus meanings, history descriptions, Premium eligibility, protocol fields or OTClient presentation. It only changes transaction ordering and rollback behavior.

# Compatibility and rollback

- Preserves #250 authority checks, #89 Transfer rules and existing Fusion outcome semantics.
- No protocol, persistence schema, Lua API, configuration, client or asset change.
- Rollback is a squash-revert of PR #257.

# Completion

- Final status: ready_for_merge_pending_final_head_ci
- PR: #257
- Merge commit:
- Archived at: pending lifecycle cleanup
