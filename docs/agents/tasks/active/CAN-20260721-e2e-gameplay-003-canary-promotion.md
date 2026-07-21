---
task_id: CAN-20260721-e2e-gameplay-003-canary-promotion
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-GAMEPLAY-003-CANARY-PROMOTION
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/e2e-gameplay-003-canary-promotion
base_branch: main
created: 2026-07-21
updated: 2026-07-21
last_verified_commit: "4723cd157801b5a045531a05f7fe83387a8aca12"
risk: low
related_issue: ""
related_pr: "685"
depends_on:
  - merged PR #589 Universal follow_route execution
  - merged PR #600 Thais reference physical route proof
  - merged E2E-GAMEPLAY-005 typed persistence assertion matrix
  - merged E2E-GAMEPLAY-004 administrative @test15 account authorization
blocks:
  - representative deterministic NPC coverage required before E2E-GAMEPLAY-008 cross-system journeys
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260721-e2e-gameplay-003-canary-promotion.md
    - data-canary/world/canary-npc.xml
    - tests/e2e/scenarios/npc/canary-promotion.json
    - tests/e2e/test_canary_npc_promotion.py
  read_only:
    - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
    - docs/architecture/universal-e2e-gameplay-validation.md
    - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
    - docs/e2e/PERSISTENCE_ASSERTION_MATRIX.md
    - data-canary/npc/canary.lua
    - data/npclib/npc_system/modules.lua
    - data/scripts/talkactions/god/add_money.lua
    - docker/data/01-test_account.sql
    - docker/data/02-test_account_players.sql
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/persistence_assertions.py
    - tools/e2e/run_physical_e2e.sh
    - tools/e2e/client/agent_e2e_scenario.lua
modules_touched:
  - Universal E2E feature-owned NPC scenario
  - deterministic Canary test-datapack NPC fixture
reuses:
  - canonical Universal E2E disposable Canary/MariaDB/controlled-OTClient lifecycle
  - existing declarative talk/wait/wait_creature actions
  - existing player_vocation and player_balance M3 persistence assertions
  - existing data-canary Canary NPC promotion behavior
  - existing God-only addmoney talkaction as isolated deterministic setup
public_interfaces: []
cross_repo_tasks: []
---

# CAN-20260721 — E2E-GAMEPLAY-003 Canary NPC promotion vertical slice

## Goal

Deliver one bounded deterministic real-client NPC flow on the existing Universal Physical E2E platform: interact with the repository-owned `Canary` NPC, promote an existing Paladin fixture through the real NPC dialogue, and prove the promoted vocation plus spent bank balance persist through the canonical safe logout/relog lifecycle.

## Acceptance criteria

- [x] Select an existing repository-owned NPC and exact dialogue behavior from source evidence; do not invent NPC names or keywords.
- [x] Use an existing deterministic player/account fixture and existing typed persistence assertions; no new shared action or assertion type is required.
- [ ] Make the selected Canary test-datapack NPC spawn deterministic without changing the global datapack or production/external systems.
- [ ] Seed exactly the evidence-backed promotion cost through the existing isolated administrative setup surface without changing the shared player fixture.
- [ ] Physically greet the NPC and execute the bounded `promot` -> `yes` dialogue through the real controlled OTClient.
- [ ] Prove M3 persistence as semantic `royal_paladin` and bank balance `0` after safe logout/relog plus final SQL verification.
- [ ] Retain exact first-failure evidence and bounded timeouts.
- [ ] Keep shared runner/workflow, player fixture SQL, OTBM binaries/maps, global datapack, OTClient source and client assets unchanged.
- [ ] Pass focused tests, checkpoint validation, ownership and exact-final-head CI/Physical E2E gates before merge.
- [ ] Merge through the normal autonomous gate, then archive this task in a separate lifecycle PR.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T17:40:00+02:00
head: d17c5d0afce7faac3d5c98d2935be5ddaf7af5d1
branch: feat/e2e-gameplay-003-canary-promotion
pr: 685
status: implementing
context_routes:
  - universal-e2e
owned_paths:
  - docs/agents/tasks/active/CAN-20260721-e2e-gameplay-003-canary-promotion.md
  - data-canary/world/canary-npc.xml
  - tests/e2e/scenarios/npc/canary-promotion.json
  - tests/e2e/test_canary_npc_promotion.py
proven:
  - E2E-GAMEPLAY-004 is merged and lifecycle-archived; E2E-GAMEPLAY-005 persistence coverage is already merged.
  - PR #589 merged reusable follow_route execution and PR #600 merged the first physical semantic landmark route, so E2E-GAMEPLAY-003 is no longer blocked by missing route-consumption capability.
  - no open PR was found that already owns E2E-GAMEPLAY-003 or data-canary/world/canary-npc.xml.
  - data-canary/npc/canary.lua defines NPC Canary and wires keyword promot followed by yes to StdModule.promotePlayer with cost 20000 and minimum level 20.
  - StdModule.promotePlayer calls player:removeMoneyBank(cost), sets the promoted vocation, grants 100 minor charm echoes and records promoted=true in player KV.
  - docker fixture Paladin 15 belongs to account 115, is level 500 and starts as server vocation 3 (Paladin).
  - account @test15 is type 6 from completed E2E-GAMEPLAY-004, which is the account-type permission path already physically proven for privileged TalkActions while Paladin 15 remains a normal group-1 combat/player character.
  - data/scripts/talkactions/god/add_money.lua exposes `/addmoney playername, amount`, calls Bank.credit for the exact amount and is restricted to groupType god.
  - canonical persistence mapping defines royal_paladin as server vocation 7 and controlled-client vocation 12.
  - accepted E2E-GAMEPLAY-004 physical artifact observed Paladin 15 entering data-canary at 1942,1345,7; data-canary/world/canary-npc.xml has a Canary spawn at 1943,1345,7.
  - the selected NPC spawn currently has radius 6, which is the only identified deterministic-fixture risk for an immediate adjacent dialogue flow.
derived:
  - constraining only the selected test-datapack spawn radius to zero is narrower than adding a new NPC, duplicating promotion logic or changing the global datapack.
  - invoking `/addmoney Paladin 15, 20000` in the disposable test session is narrower than modifying the shared player fixture and permits existing player_balance to prove the full promotion cost was consumed.
  - the privileged command is setup only; the feature outcome remains the repository-owned NPC dialogue and is independently verified by post-relog vocation and balance assertions.
unknown:
  - whether the real controlled-client talk cadence completes the NPC focus/promotion sequence without additional bounded waits
conflicts: []
first_failure:
  marker: none yet
  evidence: implementation validation has not run
rejected_hypotheses:
  - start E2E-GAMEPLAY-007 fault/recovery next; rejected because no explicit safe scenario-owned fault-injection seam is currently exposed by the physical action contract
  - add a new generic NPC dialogue action; existing talk plus bounded wait actions are sufficient for the concrete flow unless physical evidence proves otherwise
  - create a synthetic promotion NPC; rejected because the repository-owned Canary NPC already exposes the exact promotion behavior
  - modify docker/data/02-test_account_players.sql only to seed 20000 balance; rejected after source review found the narrower existing God-only addmoney setup command on the already-authorized disposable @test15 account
  - use a global-world NPC/quest with guessed coordinates or storages; rejected in favor of the controlled data-canary fixture
changed_paths:
  - docs/agents/tasks/active/CAN-20260721-e2e-gameplay-003-canary-promotion.md
validation: []
blockers: []
next_action: Implement the deterministic Canary NPC spawn, promotion scenario and focused evidence test, then run ownership, incremental CI and Universal Agent E2E on the exact head and react only to the first retained physical failure.
```
