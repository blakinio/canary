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
last_verified_commit: "70eedf733f39babebf578faa348d653d85d96d76"
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
- [x] Physically observe the target and prove the client enters the expected engagement state.
- [ ] Prove deterministic target removal after engagement begins.
- [x] Keep timeouts bounded and retain exact first-failure evidence.
- [x] Do not depend on random public-world occupancy, production systems or guessed monster names/positions.
- [x] Keep gameplay/datapack, OTBM binary, map and client asset paths unchanged.
- [ ] Pass focused tests, checkpoint validation, ownership and exact-final-head CI/Physical E2E gates before merge.
- [ ] Merge through the normal autonomous gate, then archive this task in a separate lifecycle PR.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T15:45:00+02:00
head: a7e892fa8883b52f8a7e20171803fb55c1741d99
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
  - InstanceArenaService provides an isolated 30-HP attackable Cave Rat at a fixed offset from entry 19976,19988,7.
  - TalkAction permission checks use accounts.type; @test15 is now the dedicated God-account fixture with type 6.
  - Universal Agent E2E run 29830650905 proved arena creation, target visibility, all three exact walk_edge steps, attack_visible and observe_attacking=true with ADM1.
  - run 29830650905 then remained in target_defeated until the existing controlled-client ping seam disconnected the session at about 30 seconds.
  - exact-head Agent Task Ownership run 29833227470 and CI run 29833227606 passed on 70eedf733f39babebf578faa348d653d85d96d76.
  - Universal Agent E2E run 29833227815 reached the physical job with exact Canary and controlled OTClient builds passing.
  - run 29833227815 failed before gameplay because Knight 15 does not exist in docker/data/02-test_account_players.sql; Canary rejected the requested character for account 115.
  - docker/data/02-test_account_players.sql instead provides Paladin 15 on account 115 at level 500, vocation 3.
  - the scenario and focused evidence test now use the existing Paladin 15 fixture and explicitly reject the nonexistent Knight 15 assumption.
  - no shared runner, workflow, map, datapack, OTBM binary, client source or client asset change is required by the three runtime failures.
derived:
  - using Paladin 15 is the narrowest evidence-backed correction because it preserves the authorized account and high-level real-combat approach without adding fixture rows or privileged setup actions.
unknown:
  - whether Paladin 15 removes the 30-HP Cave Rat within the bounded 20000 ms target-defeated wait
conflicts: []
first_failure:
  marker: Physical client / combat/deterministic-combat — login phase 1
  evidence: Universal Agent E2E run 29833227815 logged Failed to get character Knight 15 from account 115 and trying to connect into another account character; the source fixture contains Paladin 15 but no Knight 15
rejected_hypotheses:
  - add a generic creature-spawn fixture interface; the merged arena service already provides the deterministic target
  - extend target_defeated beyond 30 seconds; rejected because the existing controlled-client ping seam disconnects first
  - add privileged skill or spell setup for ADM1; rejected in favor of an existing high-level fixture on the same authorized account
  - use Knight 15 from account 115; rejected because that character does not exist in the bootstrap fixture
changed_paths:
  - docs/agents/tasks/active/CAN-20260721-e2e-gameplay-004-combat-vertical-slice.md
  - docker/data/01-test_account.sql
  - tests/e2e/scenarios/combat/deterministic-combat.json
  - tests/e2e/test_deterministic_combat.py
validation:
  - command: Agent Task Ownership run 29833227470 on 70eedf733f39babebf578faa348d653d85d96d76
    result: PASS
    evidence: active-task ownership and checkpoint validation passed
  - command: CI run 29833227606 on 70eedf733f39babebf578faa348d653d85d96d76
    result: PASS
    evidence: incremental repository CI completed successfully
  - command: Universal Agent E2E run 29833227815 on 70eedf733f39babebf578faa348d653d85d96d76
    result: FAIL
    evidence: exact builds passed; physical first failure was the nonexistent Knight 15 fixture requested on account 115 before gameplay began
blockers: []
next_action: Verify ownership, CI and Universal Agent E2E on the exact head using existing Paladin 15; if target removal and the canonical two-session lifecycle pass, checkpoint the successful runtime evidence and proceed to the normal final gate without adding shared platform capability.
```
