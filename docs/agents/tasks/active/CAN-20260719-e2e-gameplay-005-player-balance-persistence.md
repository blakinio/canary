---
task_id: CAN-20260719-e2e-gameplay-005-player-balance-persistence
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-GAMEPLAY-005
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/e2e-gameplay-005-player-balance-persistence
base_branch: main
created: 2026-07-19T15:32:00+02:00
updated: 2026-07-19T16:05:00+02:00
last_verified_commit: "a23c1f50f1fbcfd81ffee6b5b308d790f17f1517"
risk: medium
related_issue: ""
related_pr: "591"
depends_on:
  - merged PR #583 typed player_storage persistence assertions
  - merged PR #586 typed player_item_presence persistence assertions
  - existing Universal Physical E2E two-session lifecycle
blocks:
  - feature-owned bank/economy scenarios requiring typed durable bank-balance assertions
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260719-e2e-gameplay-005-player-balance-persistence.md
    - tests/e2e/test_player_balance_persistence.py
  shared:
    - tools/e2e/persistence_assertions.py
    - tools/e2e/client/agent_e2e_scenario.lua
    - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
    - docs/agents/MODULE_CATALOG.md
  read_only:
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/run_physical_e2e.sh
    - tests/e2e/test_persistence_assertions.py
    - tests/e2e/test_player_storage_persistence.py
    - tests/e2e/test_player_item_persistence.py
    - docs/agents/CHANGELOG.md
    - .github/workflows/**
    - schema.sql
    - src/io/functions/iologindata_save_player.cpp
    - src/io/functions/iologindata_load_player.cpp
    - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
modules_touched:
  - Universal OTS E2E physical gameplay persistence assertions
reuses:
  - existing post-cycle scalar SQL assertion evaluator
  - existing two-session physical login/logout/relog lifecycle
  - existing scenario.assertions.persistence contract
  - maintained OTClient LocalPlayer getResourceBalance binding
public_interfaces:
  - persistence assertion type player_balance
cross_repo_tasks: []
---

# Goal

Extend the existing feature-neutral `scenario.assertions.persistence` contract with a bounded typed `player_balance` assertion for durable Canary bank balance state without exposing arbitrary SQL or encoding feature-specific economy values.

For exact values representable by the controlled client's Lua number boundary, the assertion must prove the same expected bank balance after relog through the real maintained OTClient and again through post-cycle SQL after the second safe logout.

# Acceptance criteria

- [x] Add `player_balance` checks with exact `equals` value.
- [ ] Restrict `equals` to the exact Lua-safe integer range `0..9007199254740991` so client equality cannot silently round uint64 values.
- [x] Compile only one fixed-shape semicolon-free scalar SQL equality query against `players.balance` by exact fixture character name.
- [x] Do not expose caller-controlled table names, columns, predicates or SQL fragments.
- [ ] Emit `player_balance` into phase-two controlled-client persistence checks and read it from `LocalPlayer::getResourceBalance(RESOURCE_BANK_BALANCE)` through the maintained Lua binding.
- [ ] Require the same expected balance through both post-relog client verification and final SQL verification.
- [ ] Add focused validation/compiler, Lua-plan and runtime-source tests for the client-readable balance path.
- [ ] Document the Lua-safe exact range, maintained-client resource-balance proof and feature-owned stronger UI assertions.
- [x] Keep feature-specific expected balances and economy actions out of shared fixtures.
- [x] Apply `ci:final-gate` before the eventual final checkpoint commit.
- [ ] Require exact-final-head Ownership, CI and Universal Agent E2E success before merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19T16:05:00+02:00
head: a23c1f50f1fbcfd81ffee6b5b308d790f17f1517
branch: feat/e2e-gameplay-005-player-balance-persistence
pr: 591
status: implementing
context_routes:
  - universal-e2e
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/CAN-20260719-e2e-gameplay-005-player-balance-persistence.md
  - tests/e2e/test_player_balance_persistence.py
  - tools/e2e/persistence_assertions.py
  - tools/e2e/client/agent_e2e_scenario.lua
  - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
  - docs/agents/MODULE_CATALOG.md
proven:
  - live main at task start is 1e64918de8a53aaf15647ee602e02bad25d02387 and includes merged PR 586
  - PR 591 owns branch feat/e2e-gameplay-005-player-balance-persistence
  - E2E automation roadmap explicitly lists bank/economy in E2E-GAMEPLAY-005 and permits persistence work independently of route planning
  - no open PR matched player_balance or bank-balance typed persistence ownership at task start
  - schema.sql defines players.balance as bigint(20) UNSIGNED NOT NULL DEFAULT 0
  - savePlayerFirst writes players.balance from player->bankBalance in the canonical player save path
  - loadPlayerBasicInfo restores player bank balance from result->getNumber<uint64_t>("balance")
  - maintained OTClient LocalPlayer exposes getResourceBalance(ResourceTypes_t) and getTotalMoney
  - maintained OTClient Lua registration binds LocalPlayer.getResourceBalance
  - maintained OTClient ResourceTypes_t defines RESOURCE_BANK_BALANCE = 0
  - the earlier database-only design was discovered to understate available physical-client evidence before merge and PR 591 was returned to draft
  - exact Lua-number equality must not cover arbitrary uint64 values because values above 2^53-1 are not guaranteed exact under the reusable Lua plan boundary
  - ci:final-gate remains applied; a new final checkpoint will be created only after the corrected client-readable implementation is complete
derived:
  - player_balance should be a dual client-plus-SQL assertion for the Lua-safe exact integer range
  - feature scenarios requiring larger uint64 values need a separate string-safe client contract or database-only feature-specific evidence rather than an unsafe numeric comparison
unknown:
  - exact final implementation head and workflow conclusions after correction
conflicts: []
first_failure:
  marker: ownership_related_pr_binding_window
  evidence: Agent Task Ownership run 29689561663 failed at changed active task checkpoint validation on the initial task-only head, created before PR 591 existed with related_pr empty; focused ownership-tooling unit tests in the same job passed, and the task was immediately bound to related_pr 591
rejected_hypotheses:
  - database-only player_balance despite a maintained LocalPlayer resource-balance getter and Lua binding
  - full uint64 exact comparison through a generic numeric Lua plan value
  - exposing arbitrary economy SQL
  - adding feature-specific balance values to shared fixtures
  - modifying economy gameplay, bank NPCs, items, route execution or OTBM tooling
changed_paths:
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260719-e2e-gameplay-005-player-balance-persistence.md
  - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
  - tests/e2e/test_player_balance_persistence.py
  - tools/e2e/client/agent_e2e_scenario.lua
  - tools/e2e/persistence_assertions.py
validation:
  - command: Agent Task Ownership run 29689561663
    result: FAIL
    evidence: initial task-only checkpoint validation failed before PR 591 binding; focused unit tests passed
  - command: maintained OTClient source review
    result: PASS
    evidence: LocalPlayer getResourceBalance is public, Lua-bound, and RESOURCE_BANK_BALANCE is enum value 0
  - command: PR 591 MODULE_CATALOG patch audit before client-proof correction
    result: PASS
    evidence: patch contained exactly one intended Universal OTS E2E row update
  - command: ci:final-gate label
    result: PASS
    evidence: label was applied before the first checkpoint and remains present; corrected implementation will receive a new final checkpoint and exact-head runs
blockers: []
next_action: Implement exact client-readable player_balance for 0..2^53-1, update focused tests/docs/catalog, audit the corrected diff, then create a new final checkpoint and freeze the new head.
```
