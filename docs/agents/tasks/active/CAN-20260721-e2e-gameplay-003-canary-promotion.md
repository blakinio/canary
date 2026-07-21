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
last_verified_commit: "751e45e2047987b89f42e6c2f609e2eb0d9cca9c"
risk: low
related_issue: ""
related_pr: "685"
depends_on:
  - merged PR #589 Universal follow_route execution
  - merged PR #600 Thais reference physical route proof
  - merged E2E-GAMEPLAY-005 typed persistence assertion matrix
  - merged E2E-GAMEPLAY-004 administrative @test15 account authorization
  - merged PR #687 controlled OTClient verified FreeType fallback
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
- [x] Make the selected Canary test-datapack NPC spawn deterministic without changing the global datapack or production/external systems.
- [x] Seed exactly the evidence-backed promotion cost through the existing isolated administrative setup surface without changing the shared player fixture.
- [ ] Physically greet the NPC and execute the bounded `promot` -> `yes` dialogue through the real controlled OTClient.
- [ ] Prove M3 persistence as semantic `royal_paladin` and bank balance `0` after safe logout/relog plus final SQL verification.
- [x] Retain exact first-failure evidence and bounded timeouts.
- [x] Keep shared runner/workflow, player fixture SQL, OTBM binaries/maps, global datapack, OTClient source and client assets unchanged.
- [ ] Pass focused tests, checkpoint validation, ownership and exact-final-head CI/Physical E2E gates before merge.
- [ ] Merge through the normal autonomous gate, then archive this task in a separate lifecycle PR.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T00:15:00+02:00
head: 68e93efddb47d460473ad5ddb69105ddabe87de8
branch: feat/e2e-gameplay-003-canary-promotion
pr: 685
status: validating
context_routes:
  - universal-e2e
owned_paths:
  - docs/agents/tasks/active/CAN-20260721-e2e-gameplay-003-canary-promotion.md
  - data-canary/world/canary-npc.xml
  - tests/e2e/scenarios/npc/canary-promotion.json
  - tests/e2e/test_canary_npc_promotion.py
proven:
  - the feature implementation is complete on head 68e93efddb47d460473ad5ddb69105ddabe87de8: selected data-canary Canary NPC spawn is radius zero, scenario npc/canary-promotion exists, and focused evidence coverage exists.
  - Canary NPC source wires promot followed by yes to StdModule.promotePlayer with cost 20000 and minimum level 20.
  - Paladin 15 belongs to account 115, is level 500, starts as Paladin and is adjacent to the selected Canary spawn in the controlled data-canary world.
  - @test15 account type 6 authorizes the existing God-only /addmoney setup command while Paladin 15 remains the normal player character used for the NPC outcome.
  - the scenario seeds exactly 20000 through /addmoney, performs the real NPC dialogue, then uses existing player_vocation and player_balance persistence assertions expecting royal_paladin and zero balance after relog.
  - feature head 68e93efddb47d460473ad5ddb69105ddabe87de8 passed Agent Task Ownership run 29845230906 and incremental CI run 29845231420.
  - Universal Agent E2E run 29845231189 did not reach the feature physical scenario because the generic controlled OTClient build failed first; no NPC-flow first failure was observed.
  - repair PR #687 merged as 5b6b904106856b861676bc7f4eaf52b34ddcef87 and restored controlled OTClient build availability with a SHA512-verified FreeType mirror cache fallback.
  - repair final head passed full final-gate CI 29870292311 and Universal Agent E2E 29870291947, including controlled OTClient build, physical login/relog and Required physical E2E.
  - repair lifecycle PR #702 merged as 751e45e2047987b89f42e6c2f609e2eb0d9cca9c; its archive exists on main and the repair active task has been removed.
  - PR #685 feature diff does not modify shared Universal E2E runner/workflow, player fixture SQL, OTBM/map binaries, global datapack, OTClient source or client assets.
derived:
  - the remaining validation is now feature-specific physical evidence; the previous pre-physical controlled-OTClient blocker is resolved on current main.
  - PR #685 must consume the merged main workflow repair before rerunning physical validation so the old branch copy of Universal E2E does not reproduce the already-fixed infrastructure failure.
unknown:
  - whether the real controlled-client talk cadence completes hi -> promot -> yes without an additional bounded wait
  - whether post-relog physical evidence confirms both royal_paladin and bank balance zero on the first unblocked run
conflicts: []
first_failure:
  marker: Universal Agent E2E / Build controlled OTClient before feature physical execution
  evidence: run 29845231189 failed in the generic controlled OTClient build before npc/canary-promotion started; PR #687 subsequently repaired and physically validated that platform path, so no feature-flow failure is currently known
rejected_hypotheses:
  - add a new generic NPC dialogue action; existing talk plus bounded wait actions are sufficient unless physical evidence proves otherwise
  - create a synthetic promotion NPC; repository-owned Canary NPC already exposes the exact promotion behavior
  - modify docker/data/02-test_account_players.sql to seed balance; existing isolated God-only addmoney setup is narrower
  - change the feature scenario to repair the controlled OTClient build; failure occurred before physical feature execution and is now resolved by merged PR #687
changed_paths:
  - docs/agents/tasks/active/CAN-20260721-e2e-gameplay-003-canary-promotion.md
  - data-canary/world/canary-npc.xml
  - tests/e2e/scenarios/npc/canary-promotion.json
  - tests/e2e/test_canary_npc_promotion.py
validation:
  - command: Agent Task Ownership run 29845230906 on 68e93efddb47d460473ad5ddb69105ddabe87de8
    result: PASS
    evidence: feature ownership and task governance passed before the platform blocker was isolated
  - command: CI run 29845231420 on 68e93efddb47d460473ad5ddb69105ddabe87de8
    result: PASS
    evidence: focused implementation and incremental CI passed
  - command: Universal Agent E2E run 29845231189 on 68e93efddb47d460473ad5ddb69105ddabe87de8
    result: BLOCKED
    evidence: controlled OTClient build failed before physical npc/canary-promotion execution; no feature-flow failure was reached
  - command: PR #687 final-gate CI 29870292311 and Universal Agent E2E 29870291947
    result: PASS
    evidence: merged platform repair restored controlled OTClient build availability and passed physical login/relog plus Required physical E2E
blockers: []
next_action: Update PR #685 branch to consume current main without changing feature semantics so the merged controlled-OTClient fallback is present, then use the resulting exact-head Universal E2E run as the first unblocked physical npc/canary-promotion validation.
```
