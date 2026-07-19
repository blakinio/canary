---
task_id: CAN-20260719-e2e-gameplay-005-player-balance-persistence
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-GAMEPLAY-005
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/e2e-gameplay-005-player-balance-persistence
base_branch: main
created: 2026-07-19T15:32:00+02:00
updated: 2026-07-19T17:34:00+02:00
last_verified_commit: "f2f7255859e8cfc1762197c0fc84b1769bc7a5ed"
risk: medium
related_issue: ""
related_pr: "591"
depends_on:
  - merged PR #583 typed player_storage persistence assertions
  - merged PR #586 typed player_item_presence persistence assertions
  - merged PR #589 reusable follow_route execution
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
    - tools/e2e/client/agent_e2e_route.lua
    - tools/e2e/route_plan_execution.py
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
  - merged #589 route executor integration in the shared client driver
public_interfaces:
  - persistence assertion type player_balance
cross_repo_tasks: []
---

# Goal

Extend the existing feature-neutral `scenario.assertions.persistence` contract with a bounded typed `player_balance` assertion for durable Canary bank balance state without exposing arbitrary SQL or encoding feature-specific economy values.

For exact values representable by the controlled client's Lua number boundary, the assertion proves the same expected bank balance after relog through the real maintained OTClient and again through post-cycle SQL after the second safe logout.

# Acceptance criteria

- [x] Add `player_balance` checks with exact `equals` value.
- [x] Restrict `equals` to the exact Lua-safe integer range `0..9007199254740991` so client equality cannot silently round uint64 values.
- [x] Compile only one fixed-shape semicolon-free scalar SQL equality query against `players.balance` by exact fixture character name.
- [x] Do not expose caller-controlled table names, columns, predicates, resource selectors or SQL fragments.
- [x] Emit `player_balance` into phase-two controlled-client persistence checks and read it from `LocalPlayer::getResourceBalance(RESOURCE_BANK_BALANCE)` through the maintained Lua binding.
- [x] Require the same expected balance through both post-relog client verification and final SQL verification.
- [x] Add focused validation/compiler, Lua-plan and runtime-source tests for the client-readable balance path.
- [x] Document the Lua-safe exact range, maintained-client resource-balance proof and feature-owned stronger UI assertions.
- [x] Keep feature-specific expected balances and economy actions out of shared fixtures.
- [x] Preserve merged #589 `follow_route` and shared route-executor integration without duplicating or modifying its owned route files.
- [x] Apply `ci:final-gate` before the eventual final checkpoint commit.
- [ ] Require exact-final-head Ownership, CI, Universal Agent E2E and autofix success before merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19T17:34:00+02:00
head: f2f7255859e8cfc1762197c0fc84b1769bc7a5ed
branch: feat/e2e-gameplay-005-player-balance-persistence
pr: 591
status: implementing
context_routes:
  - universal-e2e
  - agent-governance
owned_paths:
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260719-e2e-gameplay-005-player-balance-persistence.md
  - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
  - tests/e2e/test_player_balance_persistence.py
  - tools/e2e/client/agent_e2e_scenario.lua
  - tools/e2e/persistence_assertions.py
proven:
  - live main at original task start included merged PR 586
  - E2E automation roadmap explicitly lists bank/economy in E2E-GAMEPLAY-005
  - no open PR matched player_balance ownership at original task start
  - schema.sql defines players.balance as unsigned BIGINT and save/load code persists it through player->bankBalance and uint64_t
  - maintained OTClient exposes and Lua-binds LocalPlayer.getResourceBalance; RESOURCE_BANK_BALANCE is resource type 0
  - player_balance is restricted to exact Lua-safe integers 0..2^53-1 and is verified both after relog through the controlled client and after the second safe logout through fixed-shape SQL
  - earlier database-only design was rejected before merge because maintained-client bank-balance evidence exists
  - earlier exact head a4fa1d90b6e58fbfac06480e3d911702e15f3e79 passed CI, Universal Agent E2E, Agent Task Ownership and autofix, but those results were invalidated as final merge evidence when main advanced with overlapping merged PR 589
  - merged PR 589 owns reusable follow_route consumption and changes the shared agent_e2e_scenario.lua and MODULE_CATALOG.md
  - current main synchronization point is a8ad5dcc0d1b5a2e399fc96d24d987fb633b7344 and contains merged PR 589 plus lifecycle update 592
  - a temporary squash sync through PR 593 produced correct content but non-minimal ancestry, so it was rejected as the final branch shape
  - backup/pr591-pre-rebase preserves the pre-rebase PR 591 content
  - feature branch was force-reset to current main a8ad5dcc0d1b5a2e399fc96d24d987fb633b7344 and only PR 591-owned changes were reapplied
  - PR 591 now has exactly six changed files relative to main
  - shared client driver patch relative to main contains only the bank resource constant and player_balance persistence read/type handling; merged follow_route code is inherited unchanged
  - MODULE_CATALOG patch relative to main contains exactly one Universal OTS E2E physical gameplay row update; merged route-plan execution row is inherited unchanged
  - PHYSICAL_GAMEPLAY_ACTION_PLANS and focused player-balance tests were restored from the pre-rebase backup without route ownership expansion
  - post-rebase CI run 29692519567 succeeded on head f2f7255859e8cfc1762197c0fc84b1769bc7a5ed
  - post-rebase Ownership run 29692519527 failed only because this checkpoint used an unsupported validation result label PASS_BUT_SUPERSEDED; the diagnostics artifact identified that exact parser error
  - ci:final-gate remains applied to PR 591
  - PR 591 is intentionally draft until the clean post-rebase exact-final-head gates pass
derived:
  - prior green exact-head evidence cannot be reused after an overlapping main change even when the feature behavior itself was already proven
  - clean rebase-on-main plus a minimal six-file PR diff is safer than carrying a squash-sync ancestry artifact
  - player_balance remains a dual client-plus-SQL assertion for the Lua-safe exact integer range
unknown:
  - corrected post-rebase Ownership conclusion
  - exact final checkpoint SHA and final workflow conclusions
conflicts: []
first_failure:
  marker: ownership_related_pr_binding_window
  evidence: Agent Task Ownership run 29689561663 failed only because the initial task-only checkpoint existed before PR 591 could be bound; focused ownership tooling passed and related_pr was immediately corrected
rejected_hypotheses:
  - database-only player_balance despite a maintained LocalPlayer resource-balance getter
  - full uint64 exact comparison through a generic numeric Lua plan value
  - merging stale green head after overlapping PR 589 reached main
  - keeping the temporary PR 593 squash-sync ancestry when a clean rebase-on-main branch can produce a minimal diff
  - modifying route-plan files owned by merged PR 589
  - exposing arbitrary economy SQL or feature-specific balance fixtures
changed_paths:
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260719-e2e-gameplay-005-player-balance-persistence.md
  - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
  - tests/e2e/test_player_balance_persistence.py
  - tools/e2e/client/agent_e2e_scenario.lua
  - tools/e2e/persistence_assertions.py
validation:
  - command: maintained OTClient source review
    result: PASS
    evidence: LocalPlayer getResourceBalance is public, Lua-bound and RESOURCE_BANK_BALANCE is 0
  - command: exact-head gates on pre-main-drift head a4fa1d90b6e58fbfac06480e3d911702e15f3e79
    result: PASS
    evidence: CI, Universal Agent E2E, Ownership and autofix all succeeded, but this evidence was superseded for final merge by overlapping main changes from PR 589
  - command: post-589 shared-driver integration audit
    result: PASS
    evidence: follow_route and route-executor loading from current main are preserved alongside isolated player_balance persistence handling
  - command: post-rebase six-file scope audit
    result: PASS
    evidence: PR 591 changes exactly six owned/shared files and no route-plan execution implementation files from PR 589
  - command: post-rebase CI run 29692519567
    result: PASS
    evidence: clean rebased head f2f7255859e8cfc1762197c0fc84b1769bc7a5ed
  - command: post-rebase Ownership run 29692519527
    result: FAIL
    evidence: diagnostics artifact reported only unsupported validation result label PASS_BUT_SUPERSEDED; corrected in the next checkpoint metadata commit
  - command: ci:final-gate label
    result: PASS
    evidence: label remains applied; a new final checkpoint will be the last commit after corrected post-rebase Ownership validation
blockers: []
next_action: Require corrected post-rebase Ownership success, then update this task as the single final checkpoint commit and freeze the new head for full exact-head gates.
```
