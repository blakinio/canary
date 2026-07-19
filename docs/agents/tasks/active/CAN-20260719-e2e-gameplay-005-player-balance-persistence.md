---
task_id: CAN-20260719-e2e-gameplay-005-player-balance-persistence
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-GAMEPLAY-005
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/e2e-gameplay-005-player-balance-persistence
base_branch: main
created: 2026-07-19T15:32:00+02:00
updated: 2026-07-19T15:58:00+02:00
last_verified_commit: "f9d6d9ec7efeed1216a1c52f9734ab094629df8d"
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
    - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
    - docs/agents/MODULE_CATALOG.md
  read_only:
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/client/agent_e2e_scenario.lua
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
public_interfaces:
  - persistence assertion type player_balance
cross_repo_tasks: []
---

# Goal

Extend the existing feature-neutral `scenario.assertions.persistence` contract with a bounded typed `player_balance` assertion for the durable Canary player bank balance without exposing arbitrary SQL, encoding feature-specific economy values, or claiming a generic controlled-client bank-balance read surface.

The assertion proves exact post-cycle database equality for `players.balance` after the full physical two-session lifecycle. Feature scenarios own the bank/economy action that changes the balance and any stronger client-visible outcome.

# Acceptance criteria

- [x] Add `player_balance` checks with exact `equals` value.
- [x] Validate `equals` as a strict integer in the current unsigned BIGINT range `0..18446744073709551615`.
- [x] Compile only one fixed-shape semicolon-free scalar SQL equality query against `players.balance` by exact fixture character name.
- [x] Do not expose caller-controlled table names, columns, predicates or SQL fragments.
- [x] Keep `player_field` as the only current phase-two controlled-client typed persistence check; bank balance remains database-only.
- [x] Add focused validation/compiler and mixed-contract tests.
- [x] Document the database-only bank-balance boundary and feature-owned stronger assertions.
- [x] Keep feature-specific expected balances and economy actions out of shared fixtures.
- [x] Apply `ci:final-gate` before the final checkpoint commit.
- [ ] Require exact-final-head Ownership, CI and Universal Agent E2E success before merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19T15:58:00+02:00
head: f9d6d9ec7efeed1216a1c52f9734ab094629df8d
branch: feat/e2e-gameplay-005-player-balance-persistence
pr: 591
status: validating
context_routes:
  - universal-e2e
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/CAN-20260719-e2e-gameplay-005-player-balance-persistence.md
  - tests/e2e/test_player_balance_persistence.py
  - tools/e2e/persistence_assertions.py
  - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
  - docs/agents/MODULE_CATALOG.md
proven:
  - live main at task start is 1e64918de8a53aaf15647ee602e02bad25d02387 and includes merged PR 586
  - draft PR 591 owns branch feat/e2e-gameplay-005-player-balance-persistence
  - E2E automation roadmap explicitly lists bank/economy in E2E-GAMEPLAY-005 and permits persistence work independently of route planning
  - no open PR matched player_balance or bank-balance typed persistence ownership at task start
  - schema.sql defines players.balance as bigint(20) UNSIGNED NOT NULL DEFAULT 0
  - savePlayerFirst writes players.balance from player->bankBalance in the canonical player save path
  - loadPlayerBasicInfo restores player bank balance from result->getNumber<uint64_t>("balance")
  - maintained OTClient repository search found no generic bankBalance/getBankBalance persistence getter surface suitable for a reusable phase-two client assertion
  - player_balance validation accepts only id, type and equals and enforces the full unsigned-64 range
  - player_balance compiles only to fixed-shape semicolon-free exact equality SQL against players.balance by escaped exact fixture character
  - player_field remains the only type returned for phase-two controlled-client checks; player_balance stays database-only
  - focused tests cover exact SQL, uint64 boundaries, invalid numeric types/ranges, rejection of arbitrary SQL fields, character escaping and mixed manifest/Lua-plan behavior
  - canonical PHYSICAL_GAMEPLAY_ACTION_PLANS documentation defines the database-only player_balance boundary and feature-owned stronger client/UI assertions
  - MODULE_CATALOG patch audit contains exactly one intended Universal OTS E2E row update
  - no feature-specific expected balance or bank/economy action was added to shared scenario fixtures
  - ci:final-gate was applied to PR 591 before this final checkpoint commit
derived:
  - exact unsigned-64 equality against players.balance is a bounded typed database assertion for durable bank/economy state
  - database-only treatment avoids claiming a generic maintained-client bank balance API that was not found in the searched maintained-client surface
unknown:
  - exact-final-head workflow conclusions after this final checkpoint
conflicts: []
first_failure:
  marker: ownership_related_pr_binding_window
  evidence: Agent Task Ownership run 29689561663 failed at changed active task checkpoint validation on the initial task-only head, created before PR 591 existed with related_pr empty; focused ownership-tooling unit tests in the same job passed, and the task was immediately bound to related_pr 591
rejected_hypotheses:
  - exposing arbitrary economy SQL
  - adding feature-specific balance values to shared fixtures
  - claiming bank balance is directly client-readable without a verified generic maintained-client surface
  - modifying economy gameplay, bank NPCs, items, route execution or OTBM tooling
changed_paths:
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260719-e2e-gameplay-005-player-balance-persistence.md
  - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
  - tests/e2e/test_player_balance_persistence.py
  - tools/e2e/persistence_assertions.py
validation:
  - command: Agent Task Ownership run 29689561663
    result: FAIL
    evidence: initial task-only checkpoint validation failed before PR 591 binding; focused unit tests passed
  - command: PR 591 persistence_assertions patch audit
    result: PASS
    evidence: only bounded player_balance validation/compile branches plus explicit item branch separation were added
  - command: PR 591 PHYSICAL_GAMEPLAY_ACTION_PLANS patch audit
    result: PASS
    evidence: only typed player_balance contract/evidence boundary text was added
  - command: PR 591 MODULE_CATALOG patch audit
    result: PASS
    evidence: patch contains exactly one intended Universal OTS E2E row update
  - command: ci:final-gate label
    result: PASS
    evidence: label applied before this final checkpoint commit
blockers: []
next_action: Make no further commits. Mark PR ready and require exact-final-head Agent Task Ownership, CI, Universal Agent E2E and autofix success plus clean review/merge state before expected-head squash merge.
```
