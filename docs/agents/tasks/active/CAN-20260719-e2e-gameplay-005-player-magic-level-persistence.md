---
task_id: CAN-20260719-e2e-gameplay-005-player-magic-level-persistence
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-GAMEPLAY-005
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/e2e-gameplay-005-player-magic-level-persistence
base_branch: main
created: 2026-07-19T18:05:00+02:00
updated: 2026-07-19T18:22:00+02:00
last_verified_commit: "4bfd391f005a9b2f1219110fc8624fbdc6ce02fe"
risk: medium
related_issue: ""
related_pr: "595"
depends_on:
  - merged PR #591 typed player_balance persistence assertions
  - existing Universal Physical E2E two-session lifecycle
blocks:
  - feature-owned progression scenarios requiring typed durable magic-level assertions
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260719-e2e-gameplay-005-player-magic-level-persistence.md
    - docs/e2e/PLAYER_MAGIC_LEVEL_PERSISTENCE.md
    - tests/e2e/test_player_magic_level_persistence.py
  shared:
    - tools/e2e/persistence_assertions.py
    - tools/e2e/client/agent_e2e_scenario.lua
    - docs/agents/MODULE_CATALOG.md
  read_only:
    - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
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

This task deliberately covers only the durable magic-level value stored in `players.maglevel` and exposed by the maintained client's `uint16_t getMagicLevel()` surface. It does not include `manaspent`, magic-level percent, temporary/base-vs-effective bonuses, vocation normalization, individual combat skills, or feature-specific progression values.

# Acceptance criteria

- [x] Add `player_magic_level` checks with exact `equals` in `0..65535`, matching the maintained OTClient `uint16_t` getter boundary.
- [x] Compile only one fixed-shape semicolon-free scalar SQL equality query against `players.maglevel` by exact fixture character name.
- [x] Do not expose caller-controlled table names, columns, predicates or SQL fragments.
- [x] Emit `player_magic_level` into phase-two controlled-client persistence checks and read it through maintained `LocalPlayer:getMagicLevel()` after relog.
- [x] Require the same expected value through both post-relog client verification and final SQL verification.
- [x] Add focused validation/compiler, Lua-plan and runtime-source tests.
- [x] Document the exact durable-value boundary and explicitly exclude `manaspent`, percentages and temporary/base-vs-effective normalization questions from this slice.
- [x] Keep feature-specific expected magic levels and progression actions out of shared fixtures.
- [x] Preserve merged #589 `follow_route` behavior and merged #591 `player_balance` behavior in shared client/persistence files.
- [x] Keep PR #594 OTBM route-preflight ownership untouched and update `MODULE_CATALOG.md` with exactly one narrow E2E row change.
- [x] Apply `ci:final-gate` before the final checkpoint commit.
- [ ] Require exact-final-head Ownership, CI, Universal Agent E2E and autofix success before merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19T18:22:00+02:00
head: 4bfd391f005a9b2f1219110fc8624fbdc6ce02fe
branch: feat/e2e-gameplay-005-player-magic-level-persistence
pr: 595
status: validating
context_routes:
  - universal-e2e
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/CAN-20260719-e2e-gameplay-005-player-magic-level-persistence.md
  - docs/e2e/PLAYER_MAGIC_LEVEL_PERSISTENCE.md
  - tests/e2e/test_player_magic_level_persistence.py
  - tools/e2e/persistence_assertions.py
  - tools/e2e/client/agent_e2e_scenario.lua
  - docs/agents/MODULE_CATALOG.md
proven:
  - live main at task start is d4f8bb3aa3a6ca31b54f324797078360da28f8f8 and includes merged PR 591
  - draft PR 595 owns branch feat/e2e-gameplay-005-player-magic-level-persistence
  - E2E-GAMEPLAY-005 explicitly covers vocation/progression persistence and may proceed independently of route planning
  - no open PR matched magic-level or progression persistence ownership at task start
  - PR 594 still owns OTBM-E2E-004 route preflight and remains open; this task changes none of its implementation or documentation paths
  - schema.sql defines players.maglevel as int(11) NOT NULL DEFAULT 0
  - savePlayerFirst writes players.maglevel from player->magLevel
  - loadPlayerBasicInfo restores player->magLevel from players.maglevel as uint32_t and derives manaSpent/percent separately
  - maintained OTClient LocalPlayer exposes getMagicLevel returning uint16_t
  - maintained OTClient Lua registration binds LocalPlayer.getMagicLevel
  - exact reusable client-plus-SQL equality is bounded to 0..65535 even though the server DB load surface is wider
  - persistence_assertions.py validates player_magic_level, emits it to phase-two client checks and compiles fixed-shape maglevel SQL while preserving player_balance and database-only storage/item contracts
  - agent_e2e_scenario.lua reads player_magic_level through getMagicLevel and validates the explicit runtime type while preserving follow_route and player_balance behavior
  - focused tests cover SQL shape, uint16 boundaries, invalid values, arbitrary SQL-field rejection, escaping, mixed typed checks, Lua-plan rendering and runtime-source wiring
  - dedicated docs/e2e/PLAYER_MAGIC_LEVEL_PERSISTENCE.md defines the public contract and explicitly excludes manaspent, percentages, temporary/base-effective normalization, vocation and individual skills
  - the attempted full replacement of PHYSICAL_GAMEPLAY_ACTION_PLANS.md was blocked by the tool safety layer; the task did not bypass that block and instead uses a dedicated narrow contract document
  - PR 595 changes exactly six files
  - driver patch audit contains exactly two magic-level persistence hunks and no route execution changes
  - persistence compiler patch audit contains only player_magic_level validation/client inclusion/SQL plus an explicit preserved player_balance compile branch
  - MODULE_CATALOG patch audit contains exactly one Universal OTS E2E physical gameplay row update and leaves OTBM route-preflight and route-plan execution entries untouched
  - corrected Agent Task Ownership run 29694378525 succeeded on checkpoint-fix head d9953e9a6ad8aac62a7079efc8958b3c1af41452
  - pre-final CI run 29694568253 succeeded and Agent Task Ownership run 29694568151 succeeded on implementation/catalogue head 4bfd391f005a9b2f1219110fc8624fbdc6ce02fe
  - main remained d4f8bb3aa3a6ca31b54f324797078360da28f8f8 immediately before final checkpoint preparation
  - ci:final-gate was applied to PR 595 before this final checkpoint commit
derived:
  - a client-plus-SQL player_magic_level assertion reuses the existing phase-two persistence plan and fixed scalar SQL boundary without runner or workflow changes
unknown:
  - exact-final-head workflow conclusions after this final checkpoint
conflicts: []
first_failure:
  marker: ownership_checkpoint_first_failure_shape
  evidence: Agent Task Ownership run 29694251316 failed because first_failure was null; diagnostics required a YAML mapping. Focused ownership tooling tests passed and the checkpoint was corrected.
rejected_hypotheses:
  - bundling all skills and magic level into one broad progression PR
  - permitting values above 65535 that cannot be represented by the maintained client getter used for physical proof
  - treating manaspent or magic-level percent as the same durable equality contract
  - adding feature-specific progression expectations to shared fixtures
  - modifying OTBM route preflight or route execution packages
  - bypassing the tool safety block on a large documentation replacement
changed_paths:
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260719-e2e-gameplay-005-player-magic-level-persistence.md
  - docs/e2e/PLAYER_MAGIC_LEVEL_PERSISTENCE.md
  - tests/e2e/test_player_magic_level_persistence.py
  - tools/e2e/client/agent_e2e_scenario.lua
  - tools/e2e/persistence_assertions.py
validation:
  - command: CI run 29694251372
    result: PASS
    evidence: implementation/documentation head 62048ce3ab2f7e9ecda705f52cc6dab143793397
  - command: Agent Task Ownership run 29694251316
    result: FAIL
    evidence: checkpoint schema required first_failure to be a YAML mapping; corrected in commit d9953e9a6ad8aac62a7079efc8958b3c1af41452
  - command: Agent Task Ownership run 29694378525
    result: PASS
    evidence: corrected checkpoint schema
  - command: PR 595 shared-driver patch audit
    result: PASS
    evidence: exactly two player_magic_level persistence hunks; follow_route and player_balance inherited unchanged
  - command: PR 595 persistence compiler patch audit
    result: PASS
    evidence: bounded player_magic_level validation/client inclusion/fixed SQL only, with preserved explicit player_balance branch
  - command: PR 595 MODULE_CATALOG patch audit
    result: PASS
    evidence: exactly one intended Universal OTS E2E row update
  - command: CI run 29694568253
    result: PASS
    evidence: implementation/catalogue head 4bfd391f005a9b2f1219110fc8624fbdc6ce02fe
  - command: Agent Task Ownership run 29694568151
    result: PASS
    evidence: implementation/catalogue head 4bfd391f005a9b2f1219110fc8624fbdc6ce02fe
  - command: ci:final-gate label
    result: PASS
    evidence: applied before this final checkpoint commit
blockers: []
next_action: Make no further commits. Mark PR ready and require exact-final-head Agent Task Ownership, CI, Universal Agent E2E and autofix success plus clean review/merge state before expected-head squash merge.
```
