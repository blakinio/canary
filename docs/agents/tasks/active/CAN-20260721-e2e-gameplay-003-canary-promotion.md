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
last_verified_commit: "ff3f4b499e23c56d4e45aa17a4cdcc1a3eaf7797"
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
  - merged PR #719 corrected player_vocation persistence evidence boundary
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
  - merged player_vocation SQL-only post-cycle persistence boundary
  - existing player_balance client-plus-SQL M3 persistence assertion
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
- [x] Physically greet the NPC and execute the bounded `promot` -> `yes` dialogue through the real controlled OTClient.
- [x] Prove M3 persistence as semantic `royal_paladin` and bank balance `0` after safe logout/relog plus final SQL verification.
- [x] Remove obsolete client-vocation success markers after the merged platform evidence-boundary correction while retaining semantic `player_vocation=royal_paladin` and exact server SQL.
- [x] Retain exact first-failure evidence and bounded timeouts.
- [x] Keep shared runner/workflow, player fixture SQL, OTBM binaries/maps, global datapack, OTClient source and client assets unchanged.
- [ ] Pass focused tests, checkpoint validation, ownership and exact-final-head CI/Physical E2E gates before merge.
- [ ] Merge through the normal autonomous gate, then archive this task in a separate lifecycle PR.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T13:42:00Z
head: ff3f4b499e23c56d4e45aa17a4cdcc1a3eaf7797
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
  - original PR #685 was closed unmerged as superseded rather than rewriting its published history with a plain force update.
  - successor PR #718 retains exactly four feature-owned paths.
  - PR #708 merged as 5b4402958daa6584f90b848f385ad24a391b03a4 and provides bounded talk_npc through MessageModes.NpcTo while preserving public talk.
  - PR #718 exact-head run 29914323150 reached the real npc/canary-promotion physical scenario after exact Canary and controlled OTClient builds passed.
  - physical job 88909987894 artifact 8527963786 records successful /addmoney 20000 setup, public hi, NPC-private promot and yes, plan success, safe first logout, second login and durable post-cycle evaluation.
  - the same artifact proves final SQL players.vocation=7 and players.balance=0 both passed, so Royal Paladin promotion and the 20000 bank cost persisted through the canonical two-session cycle.
  - the only failure in that run was the shared platform phase-two client-vocation comparison actual=2 expected=12; it was not a gameplay or timing failure.
  - PR #719 corrected that reusable evidence boundary by keeping semantic player_vocation exact server SQL after the full relog cycle while no longer materializing LocalPlayer.getVocation as exact promoted-vocation equality.
  - PR #719 exact head 4463fcb8d4064d15362fbf41a3971bcb903f8ed6 passed Agent Task Ownership 29921435997, CI 29921436493, Universal Agent E2E 29921436878, ready-triggered autofix 29923472742 and ready-triggered CI 29923473076, then merged as 997343078104831ae3761e691c96fd8ff8d6cfa2.
  - PR #718 was synchronized to merged main without force-push by building a current-main tree containing exactly its four feature-owned paths and fast-forwarding the branch to merge commit ff3f4b499e23c56d4e45aa17a4cdcc1a3eaf7797.
  - the feature scenario retains semantic player_vocation=royal_paladin and player_balance=0; only obsolete required client markers persistence_check_promoted-vocation and its detail marker were removed.
  - the focused feature test now proves player_vocation is absent from phase-two client checks while exact SQL vocation=7 remains compiled and balance remains client-plus-SQL verified.
  - ci:final-gate remains applied to PR #718.
derived:
  - the original message-mode blocker is resolved and the existing 250ms greet/offer settle waits were sufficient in physical execution.
  - promotion mechanics and durable persistence are already proven; the fresh post-#719 run primarily validates the corrected evidence boundary and remaining feature-owned required markers.
  - the prior artifact reported initial_position=1944,1346,7 while the manifest still requires initial_position=1942,1345,7; this is a candidate next feature-specific failure but must be confirmed by the fresh exact-head run before editing.
unknown:
  - whether the fresh exact-head physical run confirms the previous initial-position mismatch as the next first failure.
  - whether any other feature-specific marker fails after removal of the obsolete client-vocation markers.
conflicts: []
first_failure:
  marker: persistence check promoted-vocation (vocation) failed: actual=2 expected=12
  evidence: PR #718 Universal Agent E2E run 29914323150, Physical client job 88909987894, artifact 8527963786; final SQL simultaneously passed vocation=7 and balance=0. This reusable false-negative is resolved by merged PR #719.
rejected_hypotheses:
  - NPC-private speech still fails to promote: final SQL proves vocation=7 and balance=0.
  - failed /addmoney balance seeding caused the promotion failure: final balance=0 after a 20000 seed and promotion proves the economy path executed.
  - a longer wait is required: the existing cadence produced the correct durable promotion state.
  - change royal_paladin client expectation to 2: that would collapse promoted and base Paladin client values and was rejected in favor of the truthful SQL-only vocation boundary merged in PR #719.
  - rewrite the diverged published PR #685 branch with a plain force update: repository policy requires safe history handling.
changed_paths:
  - docs/agents/tasks/active/CAN-20260721-e2e-gameplay-003-canary-promotion.md
  - data-canary/world/canary-npc.xml
  - tests/e2e/scenarios/npc/canary-promotion.json
  - tests/e2e/test_canary_npc_promotion.py
validation:
  - command: Universal Agent E2E run 29872645552 / Physical client job 88781609132
    result: FAIL
    evidence: original public MessageSay follow-ups did not promote; retained as historical first feature failure.
  - command: PR #718 Universal Agent E2E run 29914323150 / Physical client job 88909987894
    result: FAIL
    evidence: real NPC-private dialogue and durable vocation=7 plus balance=0 succeeded; only the now-corrected shared client-vocation evidence boundary failed.
  - command: PR #719 Agent Task Ownership 29921435997, CI 29921436493, Universal Agent E2E 29921436878, autofix 29923472742 and ready-triggered CI 29923473076
    result: PASS
    evidence: corrected player_vocation persistence boundary passed exact-head platform validation and merged as 997343078104831ae3761e691c96fd8ff8d6cfa2.
blockers: []
next_action: Verify Agent Task Ownership, full CI and Universal Agent E2E on the resulting exact final PR #718 head; inspect the first fresh physical feature result and fix only the first proven remaining feature-specific failure, or prepare merge if all gates pass.
```
