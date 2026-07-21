---
task_id: CAN-20260721-e2e-gameplay-004-combat-vertical-slice
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-GAMEPLAY-004-COMBAT-VERTICAL-SLICE
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/e2e-gameplay-004-combat-vertical-slice
base_branch: main
created: 2026-07-21
updated: 2026-07-21
last_verified_commit: "1940f0365e63be357b26f2715b50fb59a92ed340"
risk: low
related_issue: ""
related_pr: "677"
depends_on:
  - merged Universal physical gameplay action contract PR 446
  - merged Universal scenario server-selection PR 468
  - merged Instanced Test Arena monster-spawn PR 304
blocks:
  - representative deterministic combat coverage required before E2E-GAMEPLAY-008 cross-system journeys
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260721-e2e-gameplay-004-combat-vertical-slice.md
    - docker/data/01-test_account.sql
    - tests/e2e/scenarios/combat/deterministic-combat.json
    - tests/e2e/test_deterministic_combat.py
  read_only:
    - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
    - docs/architecture/universal-e2e-gameplay-validation.md
    - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/run_physical_e2e.sh
    - tools/e2e/client/agent_e2e_scenario.lua
    - src/game/instance/instance_arena_service.cpp
    - src/game/instance/instance_arena_service.hpp
    - src/lua/creature/talkaction.cpp
    - data/scripts/talkactions/gm/instance_arena.lua
    - data-canary/monster/mammals/cave_rat.lua
    - data/XML/groups.xml
    - docker/data/02-test_account_players.sql
modules_touched:
  - Universal E2E feature-owned combat scenario
  - deterministic administrative E2E fixture permissions
reuses:
  - canonical Universal E2E disposable Canary/MariaDB/controlled-OTClient lifecycle
  - existing scenario server selection for data-canary/canary
  - existing Instanced Test Arena deterministic Cave Rat fixture
  - existing physical gameplay plan actions
public_interfaces: []
cross_repo_tasks: []
---

# CAN-20260721 — E2E-GAMEPLAY-004 deterministic combat vertical slice

## Goal

Deliver one bounded deterministic real-client combat lifecycle on the existing Universal Physical E2E platform, with a source-evidenced creature fixture, bounded proof, first-failure evidence and cleanup, without adding a second runner or speculative platform capability.

## Acceptance criteria

- [x] Prove an exact deterministic creature fixture or controlled scenario environment from current repository evidence.
- [x] Reuse the existing generic physical action contract; no new shared action was required.
- [x] Keep navigation bounded to three exact `walk_edge` transitions inside the fixed 12x7 arena; no blind multi-step `walk` is used.
- [ ] Physically observe the target and prove the client enters the expected engagement state.
- [ ] Prove deterministic target removal after engagement begins.
- [x] Keep timeouts bounded and retain exact first-failure evidence.
- [x] Do not depend on random public-world occupancy, production systems or guessed monster names/positions.
- [x] Keep gameplay/datapack, OTBM binary, map and client asset paths unchanged.
- [ ] Pass focused tests, checkpoint validation, ownership and exact-final-head CI/Physical E2E gates before merge.
- [ ] Merge through the normal autonomous gate, then archive this task in a separate lifecycle PR.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T14:35:00+02:00
head: 1940f0365e63be357b26f2715b50fb59a92ed340
branch: feat/e2e-gameplay-004-combat-vertical-slice
pr: 677
status: implementing
context_routes:
  - universal-e2e
owned_paths:
  - docs/agents/tasks/active/CAN-20260721-e2e-gameplay-004-combat-vertical-slice.md
  - docker/data/01-test_account.sql
  - tests/e2e/scenarios/combat/deterministic-combat.json
  - tests/e2e/test_deterministic_combat.py
proven:
  - PR 677 is the bounded draft owner for E2E-GAMEPLAY-004.
  - InstanceArenaService slot one entry is 19976,19988,7 and its Cave Rat spawn is region minX+4,minY+3.
  - data-canary Cave Rat has 30 health and is usable as the bounded target.
  - ADM1 belongs to test account 115 and player group 6, whose flags permit the required arena interaction while remaining ignored by monsters.
  - TalkAction permission checks use accounts.type rather than players.group_id, and /instancearena requires at least gamemaster account type.
  - the first physical run logged login success and talk dispatch but failed target_visible because @test15 still had normal account type 1, so the arena command never executed.
  - @test15 is now the dedicated God-account administrative fixture with accounts.type 6, aligned with ADM1 group_id 6.
  - the scenario reuses only existing generic physical-client actions and existing data-canary/canary server selection.
  - no shared runner, workflow, map, datapack, OTBM binary, client source or client asset change is required by the first runtime failure.
derived:
  - correcting the existing ADM1 administrative fixture is narrower than adding scenario setup SQL or a new generic creature-fixture interface.
unknown:
  - whether the existing bounded client interaction removes the 30-HP Cave Rat within the 90000 ms target-defeated wait after arena creation succeeds
conflicts: []
first_failure:
  marker: Physical client / combat/deterministic-combat — step target_visible
  evidence: Universal Agent E2E run 29827965337 reached login_1=success and step_create_arena=success at the client-send layer, then failed wait_creature because @test15 was accounts.type 1 while the talkaction requires gamemaster-or-higher account type
rejected_hypotheses:
  - use the nearest public-world monster spawn; rejected because the existing Instanced Test Arena provides a stronger isolated deterministic fixture
  - add a generic creature-spawn fixture interface; rejected because the merged arena service already provides the deterministic target
  - add scenario setup SQL to the shared runner; rejected because the existing ADM1 fixture can be corrected directly without a new public interface
changed_paths:
  - docs/agents/tasks/active/CAN-20260721-e2e-gameplay-004-combat-vertical-slice.md
  - docker/data/01-test_account.sql
  - tests/e2e/scenarios/combat/deterministic-combat.json
  - tests/e2e/test_deterministic_combat.py
validation:
  - command: Agent Task Ownership run 29827965004 on 737ee9b79169c7b9630efda516f202308cc88b0e
    result: PASS
    evidence: active-task ownership and checkpoint validation passed before the first physical runtime run
  - command: CI run 29827965198 on 737ee9b79169c7b9630efda516f202308cc88b0e
    result: PASS
    evidence: incremental repository CI completed successfully
  - command: Universal Agent E2E run 29827965337 on 737ee9b79169c7b9630efda516f202308cc88b0e
    result: FAIL
    evidence: exact-head scenario resolution, DB bootstrap, Canary build and OTClient build passed; physical scenario first failed at target_visible because arena creation was not authorized for normal account type 1
  - command: TalkActions::checkWord and account fixture audit
    result: PASS
    evidence: source confirms account-type authorization and @test15 was type 1; fixture changed to ACCOUNT_TYPE_GOD value 6
blockers: []
next_action: Verify ownership, CI and Universal Agent E2E on the new exact head with @test15 account type 6; use the next physical first failure or success to resolve the remaining target-removal unknown without adding shared platform capability.
```
