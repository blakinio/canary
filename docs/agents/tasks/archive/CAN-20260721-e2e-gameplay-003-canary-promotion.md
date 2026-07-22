---
task_id: CAN-20260721-e2e-gameplay-003-canary-promotion
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-GAMEPLAY-003-CANARY-PROMOTION
status: ready
agent: "GPT-5.6 Thinking"
branch: feat/e2e-gameplay-003-canary-promotion-v2
base_branch: main
created: 2026-07-21
updated: 2026-07-22
last_verified_commit: "88694e96b5033f0fe7ee65d69f3b6dbdc5aa6dd2"
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
- [x] Pass focused tests, ownership, exact-final-head CI, Universal Physical E2E and ready-triggered final CI gates before merge.
- [ ] Archive this merged task in a separate lifecycle PR.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T18:05:00Z
head: 88694e96b5033f0fe7ee65d69f3b6dbdc5aa6dd2
branch: main
pr: 718
status: ready
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
  - PR #708 merged generic NPC-private talk_npc support and PR #719 merged the SQL-only exact player_vocation persistence boundary.
  - Source inspection and two physical reproductions proved promoted non-premium players are demoted by PlayerLoginGlobal on relog; PR #723 fixed the deterministic @test15 fixture with bounded premium time and merged as fce787f7427bc2d824cf528b7801d4b369089adc.
  - Repeated physical runs used adjacent safe-login tiles, proving exact initial_position equality was not a stable gameplay invariant; deterministic Canary discovery remains enforced through wait_creature.
  - Exact feature head e749a6c7cf915ccad220237ba8050f96c4ce614d passed Agent Task Ownership run 29941359997 and CI run 29941360196.
  - Universal Agent E2E run 29941360152 passed on exact feature head e749a6c7cf915ccad220237ba8050f96c4ce614d, including Physical client / npc/canary-promotion job 89002700058 and Required physical E2E job 89003163482.
  - Final physical evidence proved the real /addmoney 20000, public hi, NPC-private promot and yes flow plus two-session persistence with Royal Paladin server vocation 7 and bank balance 0.
  - PR #718 review audit was clean with no review threads, reviews or comments, and its changed-file scope was exactly the four task-owned paths.
  - Ready-triggered final CI run 29943638930 and autofix run 29943638693 passed on the frozen feature head; PR #718 then squash-merged to main as 88694e96b5033f0fe7ee65d69f3b6dbdc5aa6dd2.
derived:
  - The merged vertical slice is deterministic at the gameplay-contract level without relying on a single exact safe-login tile.
  - Promotion durability is proven through exact server SQL after relog, while client-readable balance persistence remains independently verified.
unknown: []
conflicts: []
first_failure:
  marker: none
  evidence: No unresolved feature or validation failure remains after the successful exact-final-head gates and merged PR #718.
rejected_hypotheses:
  - NPC-private speech still fails to promote: final exact-head physical E2E passed the full promotion and persistence flow.
  - The post-relog vocation=3 result was a transient flake: repeated reproduction and source policy proved the missing-premium fixture precondition.
  - A single exact initial_position tile is required for deterministic NPC interaction: repeated runs used adjacent safe-login tiles while Canary remained discoverable and the final scenario passed.
changed_paths:
  - docs/agents/tasks/active/CAN-20260721-e2e-gameplay-003-canary-promotion.md
  - data-canary/world/canary-npc.xml
  - tests/e2e/scenarios/npc/canary-promotion.json
  - tests/e2e/test_canary_npc_promotion.py
validation:
  - command: Agent Task Ownership run 29941359997 on e749a6c7cf915ccad220237ba8050f96c4ce614d
    result: PASS
    evidence: Exact-final-head ownership validation succeeded.
  - command: CI run 29941360196 on e749a6c7cf915ccad220237ba8050f96c4ce614d
    result: PASS
    evidence: Exact-final-head CI succeeded before ready transition.
  - command: Universal Agent E2E run 29941360152 / Physical job 89002700058 / Required physical job 89003163482
    result: PASS
    evidence: Exact-final-head real-client Canary promotion and persistence scenario succeeded end to end.
  - command: Ready-triggered final CI run 29943638930 and autofix run 29943638693
    result: PASS
    evidence: Full final-gate matrix and autofix completed successfully on the frozen feature head.
  - command: PR #718 merge state
    result: PASS
    evidence: Squash-merged to main as 88694e96b5033f0fe7ee65d69f3b6dbdc5aa6dd2 after clean review audit and exact four-file scope confirmation.
blockers: []
next_action: Archive this merged active task record under docs/agents/tasks/archive in the lifecycle-only PR, then release its ownership claims.
```
