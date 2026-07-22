---
task_id: CAN-20260721-e2e-gameplay-003-canary-promotion
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-GAMEPLAY-003-CANARY-PROMOTION
status: review
agent: "GPT-5.6 Thinking"
branch: feat/e2e-gameplay-003-canary-promotion-v2
base_branch: main
created: 2026-07-21
updated: 2026-07-22
last_verified_commit: "1d303f18f721eb1d0830ad2cab7c96f620d46ec7"
risk: low
related_issue: ""
related_pr: "718"
depends_on:
  - merged PR #589 Universal follow_route execution
  - merged PR #600 Thais reference physical route proof
  - merged E2E-GAMEPLAY-005 typed persistence assertion matrix
  - merged E2E-GAMEPLAY-004 administrative @test15 account authorization
  - merged PR #687 controlled OTClient verified FreeType fallback
  - merged PR #708 generic NPC-private speech action
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
  - merged generic talk_npc action for focused NPC follow-up speech
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
- [x] Consume the merged platform-owned generic `talk_npc` action for focused `promot` and `yes` follow-up speech while keeping public `hi` unchanged.
- [ ] Physically greet the NPC and execute the bounded `promot` -> `yes` dialogue through the real controlled OTClient.
- [ ] Prove M3 persistence as semantic `royal_paladin` and bank balance `0` after safe logout/relog plus final SQL verification.
- [x] Retain exact first-failure evidence and bounded timeouts.
- [x] Keep shared runner/workflow, player fixture SQL, OTBM binaries/maps, global datapack, OTClient source and client assets unchanged.
- [ ] Pass focused tests, checkpoint validation, ownership and exact-final-head CI/Physical E2E gates before merge.
- [ ] Merge through the normal autonomous gate, then archive this task in a separate lifecycle PR.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T11:08:00Z
head: 1d303f18f721eb1d0830ad2cab7c96f620d46ec7
branch: feat/e2e-gameplay-003-canary-promotion-v2
pr: 718
status: validating
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
  - original PR #685 was closed unmerged as superseded because its published branch diverged from main and the available connector exposes no safe native update-branch operation; plain force rewriting was rejected by repository policy.
  - successor PR #718 starts from main 5b4402958daa6584f90b848f385ad24a391b03a4 and retains exactly the same four feature-owned paths.
  - the original PR #685 physical run 29872645552 reached npc/canary-promotion after the controlled OTClient build passed; artifact 8512445446 retained the first feature failure.
  - artifact 8512445446 proves /addmoney seeded 20000 successfully, while public MessageSay follow-ups promot and yes did not promote the player; after relog client vocation remained 2 instead of expected 12 and final SQL also failed server vocation 7 and balance 0.
  - controlled OTClient Game::talk is public MessageSay, while focused Canary follow-up keywords require TALKTYPE_PRIVATE_PN after NPC focus.
  - PR #708 merged as 5b4402958daa6584f90b848f385ad24a391b03a4 and delivers bounded talk_npc through g_game.talkPrivate(MessageModes.NpcTo, receiver, text) while preserving existing public talk.
  - PR #708 final platform head d5d918e81bb5979cc50f2defbde38e1cf1fe9e81 passed Agent Task Ownership 29910232184, full CI 29910232384, Universal Agent E2E 29910232428 and the later ready-triggered CI 29912528465.
  - the feature scenario now keeps setup and hi on public talk, sends promot and yes through talk_npc to receiver Canary, and retains the original bounded waits and M3 persistence expectations.
  - ci:final-gate is applied to PR #718 before this final task/checkpoint commit.
derived:
  - the proven message-mode blocker is resolved by consuming the merged generic action without modifying shared runner or controlled-client automation paths in this feature branch.
unknown:
  - whether the existing 250ms greet/offer settle waits are sufficient once promot and yes use NPC-private speech.
  - whether the promotion and both M3 persistence assertions pass on the first physical run of the exact final successor head.
conflicts: []
first_failure:
  marker: persistence_check_promoted-vocation failed: actual=2 expected=12
  evidence: Universal Agent E2E run 29872645552, Physical client / npc/canary-promotion job 88781609132, artifact 8512445446; final SQL also failed vocation=7 and balance=0.
rejected_hypotheses:
  - the generic controlled OTClient build still blocks feature execution: run 29872645552 built the controlled client and reached the physical scenario.
  - failed /addmoney balance seeding caused the promotion failure: packet/server evidence confirms the 20000 credit succeeded before NPC dialogue.
  - an additional bounded wait alone is sufficient: timing cannot change public MessageSay into required focused NPC-private speech.
  - rewrite the diverged published PR #685 branch with a plain force update: repository policy requires safe history handling and the connector lacks force-with-lease semantics.
changed_paths:
  - docs/agents/tasks/active/CAN-20260721-e2e-gameplay-003-canary-promotion.md
  - data-canary/world/canary-npc.xml
  - tests/e2e/scenarios/npc/canary-promotion.json
  - tests/e2e/test_canary_npc_promotion.py
validation:
  - command: Universal Agent E2E run 29872645552 / Physical client job 88781609132
    result: FAIL
    evidence: first feature-specific physical failure retained in artifact 8512445446; vocation remained unpromoted after relog and final vocation/balance SQL assertions failed.
  - command: PR #708 Agent Task Ownership 29910232184, CI 29910232384, Universal Agent E2E 29910232428 and ready-triggered CI 29912528465
    result: PASS
    evidence: merged platform action is available on current main and passed exact-head platform validation.
blockers: []
next_action: Verify Agent Task Ownership, full CI and Universal Agent E2E on the resulting exact final PR #718 head; inspect the first physical feature result and fix only the first proven feature-specific failure, or prepare merge if all gates and M3 assertions pass.
```
