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
last_verified_commit: "9401d491fdb025c578f2e37e9b2f7f4a48e411de"
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
    - data/scripts/talkactions/gm/instance_arena.lua
    - data-canary/monster/mammals/cave_rat.lua
    - data/XML/groups.xml
    - docker/data/01-test_account.sql
    - docker/data/02-test_account_players.sql
modules_touched:
  - Universal E2E feature-owned combat scenario
reuses:
  - canonical Universal E2E disposable Canary/MariaDB/controlled-OTClient lifecycle
  - existing scenario server selection for data-canary/canary
  - existing Instanced Test Arena deterministic Cave Rat fixture
  - existing talk, walk_edge, wait_creature, attack_visible and observe_attacking actions
public_interfaces: []
cross_repo_tasks: []
---

# CAN-20260721 — E2E-GAMEPLAY-004 deterministic combat vertical slice

## Goal

Deliver one bounded deterministic real-client combat lifecycle on the existing Universal Physical E2E platform, with a source-evidenced creature fixture, bounded combat proof, first-failure evidence and cleanup, without adding a second runner or speculative platform capability.

## Acceptance criteria

- [x] Prove an exact deterministic creature fixture or controlled scenario environment from current repository evidence.
- [x] Reuse the existing generic physical action contract; no new shared action was required.
- [x] Keep navigation bounded to three exact `walk_edge` transitions inside the fixed 12x7 arena; no blind multi-step `walk` is used.
- [ ] Physically observe the target, start combat through `attack_visible`, and prove the client enters attacking state.
- [ ] Prove deterministic target removal after combat begins.
- [x] Keep timeouts bounded and retain exact first-failure evidence.
- [x] Do not depend on random public-world occupancy, production systems or guessed monster names/positions.
- [x] Keep gameplay/datapack, OTBM binary, map and client asset paths unchanged.
- [ ] Pass focused tests, checkpoint validation, ownership and exact-final-head CI/Physical E2E gates before merge.
- [ ] Merge through the normal autonomous gate, then archive this task in a separate lifecycle PR.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T14:05:00+02:00
head: 9401d491fdb025c578f2e37e9b2f7f4a48e411de
branch: feat/e2e-gameplay-004-combat-vertical-slice
pr: 677
status: implementing
context_routes:
  - universal-e2e
owned_paths:
  - docs/agents/tasks/active/CAN-20260721-e2e-gameplay-004-combat-vertical-slice.md
  - tests/e2e/scenarios/combat/deterministic-combat.json
  - tests/e2e/test_deterministic_combat.py
proven:
  - PR 677 is the bounded draft owner for E2E-GAMEPLAY-004.
  - InstanceArenaService configured region slot one starts at 19976,19988,7 on data-canary/canary.
  - InstanceArenaService always spawns one Cave Rat at region minX+4,minY+3 and returns region minX,minY,minZ as player entry.
  - data-canary Cave Rat has 30 health and is attackable.
  - test account 115 is @test15 and owns ADM1 with group_id 6.
  - group 6 may attack monsters while monsters ignore it and cannot attack it.
  - /instancearena create and close are existing registered arena lifecycle commands available to the administrative fixture.
  - the scenario reuses only existing generic physical-client actions and existing data-canary/canary server selection.
  - the previous global-spawn evidence probe was removed in favor of the stronger repository-owned isolated arena fixture.
derived:
  - the isolated arena is a stronger deterministic combat boundary than selecting a public-world monster spawn near Knight 1.
unknown:
  - whether ADM1's ordinary auto-attack removes the 30-HP Cave Rat within the 90000 ms bounded target-defeated wait on the physical runner
conflicts: []
first_failure:
  marker: Agent Task Ownership / Validate changed active task checkpoints
  evidence: run 29827306241 rejected non-active status investigating; the record is now corrected to implementing
rejected_hypotheses:
  - use the nearest public-world monster spawn; rejected because the existing Instanced Test Arena provides a stronger isolated deterministic fixture
  - add a generic creature-spawn fixture interface; rejected because the merged arena service already provides the required deterministic target
  - add a new combat action; rejected because talk, walk_edge, wait_creature, attack_visible and observe_attacking already cover the slice
changed_paths:
  - docs/agents/tasks/active/CAN-20260721-e2e-gameplay-004-combat-vertical-slice.md
  - tests/e2e/scenarios/combat/deterministic-combat.json
  - tests/e2e/test_deterministic_combat.py
validation:
  - command: CI run 29827306433 on 338063a431a64a1fab7c66c3393d18eb1cb316c9
    result: PASS
    evidence: incremental Required gate passed; build jobs were skipped because final-gate label is not yet applied
  - command: Agent Task Ownership run 29827306241
    result: FAIL
    evidence: checkpoint-only failure because tasks/active status investigating is non-active; corrected in this checkpoint
  - command: source contract audit of InstanceArenaService, fixture SQL, groups.xml, arena talkaction and Cave Rat definition
    result: PASS
    evidence: exact deterministic target, administrative fixture permissions, fixed arena coordinates and 30-HP target are all repository-backed
blockers: []
next_action: Verify ownership and Universal Agent E2E on the current PR 677 head; use the physical run's first failure to decide whether ordinary auto-attack completes target removal within the bounded wait, without adding new platform capability unless that run proves it necessary.
```
