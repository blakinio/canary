---
task_id: CAN-20260719-e2e-gameplay-005-player-magic-level-persistence
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-GAMEPLAY-005
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/e2e-gameplay-005-player-magic-level-persistence
base_branch: main
created: 2026-07-19T18:05:00+02:00
updated: 2026-07-19T18:05:00+02:00
last_verified_commit: "d4f8bb3aa3a6ca31b54f324797078360da28f8f8"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - merged PR #591 typed player_balance persistence assertions
  - existing Universal Physical E2E two-session lifecycle
blocks:
  - feature-owned progression scenarios requiring typed durable magic-level assertions
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260719-e2e-gameplay-005-player-magic-level-persistence.md
    - tests/e2e/test_player_magic_level_persistence.py
  shared:
    - tools/e2e/persistence_assertions.py
    - tools/e2e/client/agent_e2e_scenario.lua
    - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
    - docs/agents/MODULE_CATALOG.md
  read_only:
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/run_physical_e2e.sh
    - tools/e2e/client/agent_e2e_route.lua
    - tools/e2e/route_plan_execution.py
    - tests/e2e/test_persistence_assertions.py
    - tests/e2e/test_player_balance_persistence.py
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
  - maintained OTClient LocalPlayer getMagicLevel binding
public_interfaces:
  - persistence assertion type player_magic_level
cross_repo_tasks: []
---

# Goal

Extend the existing feature-neutral `scenario.assertions.persistence` contract with one bounded typed `player_magic_level` assertion that proves durable Canary magic level through the real maintained OTClient after relog and again through final post-cycle SQL.

This task deliberately covers only the durable base magic-level value stored in `players.maglevel`. It does not include `manaspent`, magic-level percent, temporary bonuses, vocation normalization, individual combat skills, or feature-specific progression values.

# Acceptance criteria

- [ ] Add `player_magic_level` checks with exact non-negative `equals` value compatible with the maintained OTClient `uint16_t` getter boundary.
- [ ] Compile only one fixed-shape semicolon-free scalar SQL equality query against `players.maglevel` by exact fixture character name.
- [ ] Do not expose caller-controlled table names, columns, predicates or SQL fragments.
- [ ] Emit `player_magic_level` into phase-two controlled-client persistence checks and read it through maintained `LocalPlayer:getMagicLevel()` after relog.
- [ ] Require the same expected value through both post-relog client verification and final SQL verification.
- [ ] Add focused validation/compiler, Lua-plan and runtime-source tests.
- [ ] Document the exact durable-value boundary and explicitly exclude `manaspent`, percentages and temporary/base-vs-effective normalization questions from this slice.
- [ ] Keep feature-specific expected magic levels and progression actions out of shared fixtures.
- [ ] Preserve merged #589 `follow_route` behavior and merged #591 `player_balance` behavior in shared client/persistence files.
- [ ] Keep PR #594 OTBM route-preflight ownership untouched; `MODULE_CATALOG.md` is shared-index-only overlap and must receive one narrow E2E row update.
- [ ] Apply `ci:final-gate` before the final checkpoint commit.
- [ ] Require exact-final-head Ownership, CI, Universal Agent E2E and autofix success before merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19T18:05:00+02:00
head: d4f8bb3aa3a6ca31b54f324797078360da28f8f8
branch: feat/e2e-gameplay-005-player-magic-level-persistence
pr: null
status: implementing
context_routes:
  - universal-e2e
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/CAN-20260719-e2e-gameplay-005-player-magic-level-persistence.md
  - tests/e2e/test_player_magic_level_persistence.py
  - tools/e2e/persistence_assertions.py
  - tools/e2e/client/agent_e2e_scenario.lua
  - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
  - docs/agents/MODULE_CATALOG.md
proven:
  - live main at task start is d4f8bb3aa3a6ca31b54f324797078360da28f8f8 and includes merged PR 591
  - E2E-GAMEPLAY-005 explicitly covers vocation/progression persistence and may proceed independently of route planning
  - no open PR matched magic-level or progression persistence ownership at task start
  - open PR 594 owns OTBM-E2E-004 route preflight and overlaps only the shared MODULE_CATALOG.md index with this planned task
  - schema.sql defines players.maglevel as int(11) NOT NULL DEFAULT 0
  - savePlayerFirst writes players.maglevel from player->magLevel
  - loadPlayerBasicInfo restores player->magLevel from players.maglevel as uint32_t and derives manaSpent/percent separately
  - maintained OTClient LocalPlayer exposes getMagicLevel returning uint16_t
  - maintained OTClient Lua registration binds LocalPlayer.getMagicLevel
  - the smallest complete progression slice is exact durable magic level only; manaspent, percentages, temporary bonuses and individual skills remain separate contracts
derived:
  - a client-plus-SQL player_magic_level assertion can reuse the existing phase-two persistence plan and fixed scalar SQL boundary without runner or workflow changes
unknown:
  - exact validator range after reconciling server DB uint32 load with maintained-client uint16 getter boundary
  - focused tests and final workflow conclusions
conflicts: []
first_failure: null
rejected_hypotheses:
  - bundling all skills and magic level into one broad progression PR
  - treating manaspent or magic-level percent as the same durable equality contract
  - adding feature-specific progression expectations to shared fixtures
  - modifying OTBM route preflight or route execution packages
changed_paths:
  - docs/agents/tasks/active/CAN-20260719-e2e-gameplay-005-player-magic-level-persistence.md
validation: []
blockers: []
next_action: Open a draft PR, bind related_pr, then implement the smallest client-plus-SQL player_magic_level contract with focused tests and narrow shared-document updates.
```
