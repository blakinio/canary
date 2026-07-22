---
task_id: CAN-20260721-e2e-gameplay-003-canary-promotion
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-GAMEPLAY-003-CANARY-PROMOTION
status: blocked
agent: "GPT-5.6 Thinking"
branch: feat/e2e-gameplay-003-canary-promotion
base_branch: main
created: 2026-07-21
updated: 2026-07-22
last_verified_commit: "49eb4c040135cadbfc2f3028c495462dfc10dea1"
risk: low
related_issue: ""
related_pr: "685"
depends_on:
  - merged PR #589 Universal follow_route execution
  - merged PR #600 Thais reference physical route proof
  - merged E2E-GAMEPLAY-005 typed persistence assertion matrix
  - merged E2E-GAMEPLAY-004 administrative @test15 account authorization
  - merged PR #687 controlled OTClient verified FreeType fallback
  - pending platform-owned Universal E2E NPC-private speech action task
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
    - data/npclib/npc_system/npc_handler.lua
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
  - existing public talk/wait/wait_creature actions for setup and greeting
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
- [x] Use an existing deterministic player/account fixture and existing typed persistence assertions.
- [x] Make the selected Canary test-datapack NPC spawn deterministic without changing the global datapack or production/external systems.
- [x] Seed exactly the evidence-backed promotion cost through the existing isolated administrative setup surface without changing the shared player fixture.
- [ ] Consume a platform-owned generic NPC-private speech action for focused NPC dialogue; do not implement the shared action in this feature PR.
- [ ] Physically greet the NPC and execute the bounded `promot` -> `yes` dialogue through the real controlled OTClient.
- [ ] Prove M3 persistence as semantic `royal_paladin` and bank balance `0` after safe logout/relog plus final SQL verification.
- [x] Retain exact first-failure evidence and bounded timeouts.
- [x] Keep shared runner/workflow, player fixture SQL, OTBM binaries/maps, global datapack, OTClient source and client assets unchanged.
- [ ] Pass focused tests, checkpoint validation, ownership and exact-final-head CI/Physical E2E gates before merge.
- [ ] Merge through the normal autonomous gate, then archive this task in a separate lifecycle PR.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T07:07:05Z
head: 49eb4c040135cadbfc2f3028c495462dfc10dea1
branch: feat/e2e-gameplay-003-canary-promotion
pr: 685
status: blocked
context_routes:
  - universal-e2e
  - agent-governance
  - cpp-runtime
owned_paths:
  - docs/agents/tasks/active/CAN-20260721-e2e-gameplay-003-canary-promotion.md
  - data-canary/world/canary-npc.xml
  - tests/e2e/scenarios/npc/canary-promotion.json
  - tests/e2e/test_canary_npc_promotion.py
proven:
  - PR #685 remains open and draft; branch feat/e2e-gameplay-003-canary-promotion consumed current main through merge commit 49eb4c040135cadbfc2f3028c495462dfc10dea1 without adding feature-semantic paths beyond the four owned files.
  - head 49eb4c040135cadbfc2f3028c495462dfc10dea1 passed Agent Task Ownership run 29898211828 and CI run 29898212010; Universal Agent E2E run 29898211999 was still in progress when this checkpoint was written.
  - the earlier unblocked PR validation run 29872645552 reached Physical client / npc/canary-promotion after the controlled OTClient build passed; physical artifact universal-agent-e2e-npc-canary-promotion id 8512445446 retained the first feature failure.
  - result.json in artifact 8512445446 reports the first client assertion failure after relog as persistence check promoted-vocation failed with actual client vocation 2 and expected 12; final SQL also reports server vocation is not 7 and balance is not 0.
  - the same physical evidence records successful /addmoney execution and Canary server log confirmation that 20000 gold coins were added to Paladin 15, rejecting failed balance seeding as the cause of the missing promotion.
  - session-1.record shows hi, promot and yes were each sent by the controlled OTClient with talk mode byte 01, while no Canary promotion offer or congratulations response was received; only the delayed greeting response was observed.
  - controlled OTClient Game::talk always delegates to MessageSay, while Game::talkPrivate is a separate API; the current Universal E2E talk action calls g_game.talk(step.text).
  - Canary NpcHandler establishes interaction during greet, and once interaction exists its keyword handler processes player speech only when msgtype is TALKTYPE_PRIVATE_PN; therefore focused promot and yes sent through the current public talk action are not valid NPC-private dialogue messages.
  - E2E programme interface-change rules require a separate Universal E2E platform task for a new generic action; this feature task owns the scenario and expectations but keeps shared runner/client automation read-only.
derived:
  - increasing only greet-settle or offer-settle cannot repair the proven failure because the follow-up message mode remains public MessageSay after NPC focus is established.
  - PR #685 is blocked on a generic bounded NPC-private speech action that can use the controlled OTClient talkPrivate API with NPC message mode and an explicit receiver.
unknown:
  - the final platform action name and manifest contract are not yet defined by a separate platform-owned task.
  - whether the promotion and both M3 persistence assertions pass after the feature scenario consumes the future NPC-private speech action.
  - the exact nonzero final bank balance in the failed run; retained SQL proves only that it was not zero.
conflicts: []
first_failure:
  marker: persistence_check_promoted-vocation failed: actual=2 expected=12
  evidence: Universal Agent E2E run 29872645552, Physical client / npc/canary-promotion job 88781609132, artifact 8512445446 result.json and session-1.record; final SQL also failed vocation=7 and balance=0.
rejected_hypotheses:
  - the generic controlled OTClient build still blocks feature execution: run 29872645552 built the controlled client and reached the physical scenario.
  - failed /addmoney balance seeding caused the promotion failure: packet/server evidence confirms the 20000 credit succeeded before NPC dialogue.
  - an additional bounded wait alone is sufficient: Game::talk always emits MessageSay and focused Canary dialogue requires TALKTYPE_PRIVATE_PN, so timing does not change the required message mode.
  - the existing generic talk action is sufficient for the complete focused NPC dialogue: physical packet evidence shows promot and yes remained public MessageSay and no promotion occurred.
changed_paths:
  - docs/agents/tasks/active/CAN-20260721-e2e-gameplay-003-canary-promotion.md
  - data-canary/world/canary-npc.xml
  - tests/e2e/scenarios/npc/canary-promotion.json
  - tests/e2e/test_canary_npc_promotion.py
validation:
  - command: Universal Agent E2E run 29872645552 / Physical client job 88781609132
    result: FAIL
    evidence: first feature-specific physical failure retained in artifact 8512445446; vocation remained unpromoted after relog and final vocation/balance SQL assertions failed.
  - command: Agent Task Ownership run 29898211828 on 49eb4c040135cadbfc2f3028c495462dfc10dea1
    result: PASS
    evidence: current merged-main feature head ownership gate passed before checkpoint update.
  - command: CI run 29898212010 on 49eb4c040135cadbfc2f3028c495462dfc10dea1
    result: PASS
    evidence: current merged-main feature head CI passed before checkpoint update.
blockers:
  - the feature-owned scenario cannot send focused NPC follow-up speech with the current generic talk action; a separate Universal E2E platform task must add a bounded NPC-private speech action before PR #685 can complete physical M3 validation.
next_action: Create a separate Universal E2E platform task and PR for one generic bounded NPC-private speech action using the controlled OTClient talkPrivate API, then return to PR #685 to consume that stable interface.
```
