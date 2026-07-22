---
task_id: CAN-20260722-e2e-platform-test15-premium-fixture
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-PLATFORM-TEST15-PREMIUM-FIXTURE
status: review
agent: "GPT-5.6 Thinking"
branch: fix/e2e-test15-premium-fixture
base_branch: main
created: 2026-07-22
updated: 2026-07-22
risk: low
related_issue: ""
related_pr: ""
depends_on: []
blocks:
  - CAN-20260721-e2e-gameplay-003-canary-promotion
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260722-e2e-platform-test15-premium-fixture.md
    - docker/data/01-test_account.sql
    - tests/e2e/test_test15_premium_fixture.py
  read_only:
    - data/scripts/creaturescripts/player/login.lua
    - data/libs/functions/player.lua
    - docker/data/02-test_account_players.sql
    - tools/e2e/run_physical_e2e.sh
modules_touched:
  - Universal E2E deterministic account fixture
reuses:
  - existing @test15 administrative E2E account
  - existing MariaDB fixture bootstrap
public_interfaces: []
cross_repo_tasks: []
---

# CAN-20260722 — deterministic premium state for @test15 E2E fixture

## Goal

Make the existing privileged `@test15` Universal E2E fixture deterministically premium at database bootstrap so promotion-oriented relog scenarios exercise the premium persistence path instead of the intentional free-account demotion path.

## Acceptance criteria

- [x] Seed a bounded premium expiry for account id 115 using the existing test fixture SQL only.
- [x] Preserve all account credentials, account type, coins, and player rows.
- [x] Prove the fixture update targets only account id 115 and derives expiry relative to import time.
- [x] Keep runtime login/promotion behavior unchanged.
- [ ] Pass focused tests, ownership and exact-head CI before merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T17:05:00+02:00
head: db76461d4fd13509301da0f432cf47999da0b01f
branch: fix/e2e-test15-premium-fixture
pr: null
status: validating
context_routes:
  - universal-e2e
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/CAN-20260722-e2e-platform-test15-premium-fixture.md
  - docker/data/01-test_account.sql
  - tests/e2e/test_test15_premium_fixture.py
proven:
  - @test15 is account id 115 and its prior fixture insert did not seed premium time.
  - PlayerLoginGlobal demotes a promoted vocation on login when player:isPremium() is false.
  - Player.isPremium returns premium days or FREE_PREMIUM; the physical E2E runtime does not force FREE_PREMIUM.
  - fixture SQL now sets only account id 115 to 30 premium days with lastday derived from UNIX_TIMESTAMP at each fresh import.
derived:
  - promotion relog coverage using @test15 now follows the premium persistence branch without changing production login or NPC behavior.
unknown: []
conflicts: []
first_failure:
  marker: final SQL vocation=7 failed after completed second login/logout
  evidence: PR #718 Universal Agent E2E run 29925051292 and its single rerun both reproduced the failure while balance=0 persisted.
rejected_hypotheses:
  - transient physical E2E flake; the single allowed rerun reproduced the same final vocation failure.
  - generic savePlayer loses vocation; save/load persists exact vocation id, while login.lua intentionally demotes non-premium promoted players.
changed_paths:
  - docs/agents/tasks/active/CAN-20260722-e2e-platform-test15-premium-fixture.md
  - docker/data/01-test_account.sql
  - tests/e2e/test_test15_premium_fixture.py
validation:
  - command: source review of PlayerLoginGlobal premium promotion branch and @test15 fixture
    result: PASS
    evidence: non-premium promoted players are intentionally demoted on login; account 115 previously had no premium seed.
blockers: []
next_action: Open the narrow platform PR, apply ci:final-gate, and require exact-head ownership and CI success before merge.
```
