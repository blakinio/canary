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
last_verified_commit: "c4ad42785f2629001aa5474b7da2a1b12b17ad4d"
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
  - merged PR #723 deterministic @test15 premium fixture for promotion relog persistence
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
  - merged deterministic premium @test15 fixture required by promotion relog policy
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
- [x] Remove the unstable exact initial-position marker after repeated physical evidence showed adjacent safe-login tiles while NPC discovery remained deterministic.
- [x] Retain exact first-failure evidence and bounded timeouts.
- [x] Keep shared runner/workflow, OTBM binaries/maps, global datapack, OTClient source and client assets unchanged.
- [ ] Pass focused tests, checkpoint validation, ownership and exact-final-head CI/Physical E2E gates before merge.
- [ ] Merge through the normal autonomous gate, then archive this task in a separate lifecycle PR.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T17:05:00Z
head: c4ad42785f2629001aa5474b7da2a1b12b17ad4d
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
  - PR #708 merged generic NPC-private talk_npc support, and PR #719 merged the SQL-only exact player_vocation persistence boundary.
  - PR #718 physical run 29914323150 proved /addmoney 20000, public hi, NPC-private promot and yes, first safe logout, second login, final SQL vocation=7 and balance=0; its only failure was the corrected shared client-vocation comparison.
  - Fresh PR #718 exact-head physical run 29925051292 reproduced successful NPC actions and balance debit but ended with vocation=3 after the second login/logout, while the scenario also observed an adjacent initial tile rather than the hard-coded marker.
  - Source inspection proved PlayerLoginGlobal demotes promoted non-premium players on login, while the existing @test15 account fixture had no premium time; a second identical physical run reproduced the demotion, rejecting a transient-flake explanation.
  - PR #723 added a bounded premium window to deterministic @test15 fixture imports, passed Agent Task Ownership, CI, Universal Agent E2E and physical login/relog, and merged to main as fce787f7427bc2d824cf528b7801d4b369089adc.
  - PR #718 was synchronized to main containing PR #723 without force-push by merge commit a1f9518ccff87e7203eae5ee16e47c8abe8c8abc.
  - Repeated physical runs reported differing adjacent initial positions, so exact initial_position equality is not a stable gameplay invariant; wait_creature Canary plus dialogue and persistence markers are the deterministic contract.
  - The feature scenario and focused test now omit any exact initial_position required marker while retaining NPC visibility, dialogue, balance, semantic vocation SQL and two-session persistence evidence.
derived:
  - The deterministic premium fixture resolves the relog-time promotion demotion root cause without changing production login or NPC behavior.
  - Removing exact initial_position evidence does not weaken the promotion contract because the scenario still requires successful login, online stability, Canary visibility, full dialogue, two safe logouts and post-cycle persistence.
unknown:
  - Whether the current final feature head passes the full exact-head Ownership, CI and Universal Physical E2E gates after integrating PR #723 and removing the unstable position marker.
conflicts: []
first_failure:
  marker: none
  evidence: No unresolved current-head failure is known; exact-final-head validation is pending after the final feature-owned corrections.
rejected_hypotheses:
  - NPC-private speech still fails to promote: earlier final SQL proved vocation=7 and balance=0 after the full dialogue.
  - The post-relog vocation=3 result was a transient flake: a second identical physical run reproduced it and source policy matched the non-premium fixture precondition.
  - A single exact initial_position tile is required for deterministic NPC interaction: repeated runs used adjacent safe-login tiles while Canary remained discoverable through wait_creature.
changed_paths:
  - docs/agents/tasks/active/CAN-20260721-e2e-gameplay-003-canary-promotion.md
  - data-canary/world/canary-npc.xml
  - tests/e2e/scenarios/npc/canary-promotion.json
  - tests/e2e/test_canary_npc_promotion.py
validation:
  - command: PR #718 Universal Agent E2E run 29914323150 / Physical client job 88909987894
    result: FAIL
    evidence: Real NPC-private dialogue and final SQL vocation=7 plus balance=0 succeeded; only the subsequently corrected shared client-vocation evidence boundary failed.
  - command: PR #718 Universal Agent E2E run 29925051292
    result: FAIL
    evidence: Fresh run exposed unstable initial-position equality and deterministic relog demotion of non-premium @test15.
  - command: PR #723 required checks and Universal Agent E2E physical login/relog
    result: PASS
    evidence: Premium fixture prerequisite passed required validation and merged as fce787f7427bc2d824cf528b7801d4b369089adc.
  - command: Current PR #718 exact-final-head validation
    result: NOT_RUN
    evidence: Pending after integration of PR #723 and feature-owned removal of exact initial_position marker.
blockers: []
next_action: Verify focused test and checkpoint validation, then require Agent Task Ownership, full CI and Universal Agent E2E to pass on the exact current PR #718 head; if green, audit reviews and changed paths, mark ready, enable auto-merge and merge through the normal gate.
```
