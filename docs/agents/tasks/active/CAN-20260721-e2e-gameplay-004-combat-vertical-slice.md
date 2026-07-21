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
last_verified_commit: "a24755e4576044b5998cb8741ba6415b51fb9e82"
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
- [x] Keep navigation bounded to two exact `walk_edge` transitions inside the fixed 12x7 arena; stop before the creature-blocked third tile and use no blind multi-step `walk`.
- [x] Physically observe the target and prove the client enters the expected engagement state.
- [x] Prove deterministic target removal after engagement begins.
- [x] Keep timeouts bounded and retain exact first-failure evidence.
- [x] Do not depend on random public-world occupancy, production systems or guessed monster names/positions.
- [x] Keep gameplay/datapack, OTBM binary, map and client asset paths unchanged.
- [ ] Pass focused tests, checkpoint validation, ownership and exact-final-head CI/Physical E2E gates before merge.
- [ ] Merge through the normal autonomous gate, then archive this task in a separate lifecycle PR.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T16:45:00+02:00
head: a24755e4576044b5998cb8741ba6415b51fb9e82
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
  - E2E-GAMEPLAY-004 requires one deterministic bounded combat lifecycle; the programme does not require a fixed three-edge approach.
  - InstanceArenaService provides an isolated 30-HP attackable Cave Rat at a fixed offset from entry 19976,19988,7.
  - TalkAction permission checks use accounts.type; @test15 is now the dedicated God-account fixture with type 6.
  - Universal Agent E2E run 29830650905 proved arena creation, target visibility, attack_visible and observe_attacking=true with ADM1, then failed at target_defeated before the controlled-client ping disconnect seam.
  - Universal Agent E2E run 29833227815 exposed and proved the nonexistent Knight 15 fixture assumption; source fixture instead provides Paladin 15 on account 115 at level 500, vocation 3.
  - Universal Agent E2E run 29835914774 proved Paladin 15 login, arena creation, target visibility and the first two exact movement edges, then exposed the creature-contested third destination tile.
  - exact-head Agent Task Ownership run 29838496063 and CI run 29838496675 passed on a24755e4576044b5998cb8741ba6415b51fb9e82.
  - exact-head Universal Agent E2E run 29838496367 physically passed the two-edge Paladin 15 scenario.
  - run 29838496367 proved Cave Rat visibility, two exact walk_edge transitions, attack_visible target acquisition, observe_attacking=true, target removal within about one second, observe_attacking=false and explicit /instancearena close.
  - run 29838496367 then completed safe logout, server persistence confirmation, second login, second safe logout and e2e=success in 15 seconds total.
  - run 29838496367 retained two packet records, observed two server logins, exited the client with code 0, had no fatal runtime log hits and left players_online at zero.
  - run 29838496367 SQL assertions passed for Paladin 15 lastlogin > 0 and lastlogout > 0; database-after recorded both persisted timestamps.
  - physical artifact 8499077538 belongs to exact head a24755e4576044b5998cb8741ba6415b51fb9e82 and reports status=success with no missing required markers.
  - no shared runner, workflow, map, datapack, OTBM binary, client source or client asset change was required.
derived:
  - the bounded two-edge approach is the minimal stable route: it reaches a position from which the controlled real client can acquire and defeat the deterministic target while avoiding the creature-contested tile.
unknown: []
conflicts: []
first_failure:
  marker: none on accepted exact-head runtime
  evidence: Universal Agent E2E run 29838496367 and artifact 8499077538 completed the full scenario and canonical two-session lifecycle successfully
rejected_hypotheses:
  - add a generic creature-spawn fixture interface; the merged arena service already provides the deterministic target
  - extend target_defeated beyond 30 seconds; rejected because the existing controlled-client ping seam disconnects first
  - add privileged skill or spell setup for ADM1; rejected in favor of an existing high-level fixture on the same authorized account
  - use Knight 15 from account 115; rejected because that character does not exist in the bootstrap fixture
  - force a third exact approach edge; rejected because the real target can occupy or contest that tile for a normal combat character and the programme does not require three movement steps
changed_paths:
  - docs/agents/tasks/active/CAN-20260721-e2e-gameplay-004-combat-vertical-slice.md
  - docker/data/01-test_account.sql
  - tests/e2e/scenarios/combat/deterministic-combat.json
  - tests/e2e/test_deterministic_combat.py
validation:
  - command: Agent Task Ownership run 29838496063 on a24755e4576044b5998cb8741ba6415b51fb9e82
    result: PASS
    evidence: active-task ownership and checkpoint validation passed
  - command: CI run 29838496675 on a24755e4576044b5998cb8741ba6415b51fb9e82
    result: PASS
    evidence: incremental required CI completed successfully
  - command: Universal Agent E2E run 29838496367 on a24755e4576044b5998cb8741ba6415b51fb9e82
    result: PASS
    evidence: physical client completed combat, cleanup, canonical two-session lifecycle and SQL assertions; artifact 8499077538 has status=success and no missing markers
blockers: []
next_action: Verify ownership, CI and Universal Agent E2E evidence reuse on the checkpoint-only head, then apply the normal final gate to PR 677 if all exact-head checks are green.
```
