---
task_id: CAN-20260723-e2e-gameplay-008-cross-system-journey
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-GAMEPLAY-008-CROSS-SYSTEM-JOURNEY
status: ready
agent: "GPT-5.6 Thinking"
branch: feat/e2e-gameplay-008-cross-system-journey
base_branch: main
created: 2026-07-23
updated: 2026-07-23
last_verified_commit: "21cdfe4de8d5494b338b936cee80c5acd1516dad"
risk: medium
related_issue: ""
related_pr: "765"
depends_on:
  - E2E-GAMEPLAY-003 Canary NPC promotion vertical slice merged in PR 718
  - E2E-GAMEPLAY-004 deterministic combat vertical slice merged in PR 677
  - E2E-GAMEPLAY-005 typed persistence assertions
  - canonical Universal Physical E2E two-session lifecycle
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260723-e2e-gameplay-008-cross-system-journey.md
    - tests/e2e/scenarios/journeys/promotion-combat-persistence.json
    - tests/e2e/test_cross_system_promotion_combat_journey.py
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
  read_only:
    - tests/e2e/scenarios/npc/canary-promotion.json
    - tests/e2e/scenarios/combat/deterministic-combat.json
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/client/agent_e2e_scenario.lua
    - .github/workflows/universal-agent-e2e.yml
    - src/game/instance/instance_arena_service.cpp
modules_touched:
  - Universal E2E cross-system journey sentinel
reuses:
  - merged Canary NPC promotion scenario behavior
  - merged deterministic combat scenario behavior
  - existing Instanced Test Arena return-position cleanup contract
  - existing bounded action plan compiler and controlled OTClient driver
  - existing typed player_vocation and player_balance persistence assertions
  - existing canonical safe logout, relog and cleanup lifecycle
public_interfaces: []
cross_repo_tasks: []
---

# CAN-20260723 — E2E-GAMEPLAY-008 cross-system journey

## Goal

Compose already physically proven deterministic combat, NPC/economy/vocation and relog/persistence capabilities into one representative real-client journey sentinel without adding a new runner, workflow, action type, datapack mechanic or fixture.

## Acceptance criteria

- [x] Reuse the exact `Paladin 15` controlled fixture, client pin and Canary datapack already proven by the lower-level promotion and combat scenarios.
- [x] Compose the lower-level deterministic combat step sequence followed by the lower-level promotion sequence in one scenario, without introducing a new generic action.
- [x] Preserve deterministic arena cleanup and return to the original world position before entering the NPC promotion flow.
- [x] Re-prove durable Royal Paladin vocation and zero bank balance after relog through existing typed persistence assertions.
- [x] Add focused composition-contract tests that fail when the journey silently diverges from the proven lower-level step contracts.
- [x] Keep journey success as an integration sentinel; do not replace or delete the focused promotion or combat scenarios/tests.
- [x] Pass exact-head Agent Task Ownership, CI and Universal Physical E2E validation after the evidence-backed ordering repair.
- [ ] Pass immutable exact-final-head gates and merge the feature PR.
- [ ] Leave this final programme task in `docs/agents/tasks/active` with a validated final checkpoint and one concrete next action; do not archive it in this run.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T12:55:00+02:00
head: 21cdfe4de8d5494b338b936cee80c5acd1516dad
branch: feat/e2e-gameplay-008-cross-system-journey
pr: 765
status: ready
context_routes:
  - universal-e2e
  - agent-governance
  - cpp-runtime
owned_paths:
  - docs/agents/tasks/active/CAN-20260723-e2e-gameplay-008-cross-system-journey.md
  - tests/e2e/scenarios/journeys/promotion-combat-persistence.json
  - tests/e2e/test_cross_system_promotion_combat_journey.py
proven:
  - E2E-GAMEPLAY-003 Canary promotion is merged in PR 718 and physically proved the bounded hi/promot/yes NPC flow plus Royal Paladin and zero-balance persistence.
  - E2E-GAMEPLAY-004 is merged in PR 677 and physical run 29838496367 proved the unpromoted Paladin 15 kills the deterministic 30-HP Cave Rat, closes the arena and completes the canonical two-session lifecycle.
  - Initial PR 765 ordering passed promotion, arena creation, movement and attack acquisition but physical run 29995864249 timed out at target_defeated after promotion; retained evidence identified that as the first gameplay failure.
  - InstanceArenaService preserves the player returnPosition and /instancearena close teleports the player back there, supporting combat-first composition without a new route or action.
  - Repaired head 21cdfe4de8d5494b338b936cee80c5acd1516dad preserves the exact combat sequence first and the exact promotion sequence second, excluding only the duplicate promotion online observation.
  - Agent Task Ownership run 29998764282 and autofix run 29998764343 passed on repaired head 21cdfe4de8d5494b338b936cee80c5acd1516dad.
  - CI run 29998764500 passed on repaired head 21cdfe4de8d5494b338b936cee80c5acd1516dad.
  - Universal Agent E2E run 29998764675 passed on repaired head; physical job 89185121476 and Required physical E2E proved combat, arena return, NPC promotion, safe logout, relog and durable persistence in one journey.
derived:
  - The successful repaired run proves an M4 cross-system integration sentinel by composing previously proven combat, NPC/economy/vocation and persistence systems without replacing their focused tests.
unknown:
  - Immutable exact-final-head Ownership, CI, autofix and Universal Agent E2E outcomes on the final checkpoint commit are pending.
conflicts: []
first_failure:
  marker: none on repaired head
  evidence: The earlier target_defeated timeout was resolved by preserving the exact proven combat-before-promotion state; repaired physical job 89185121476 completed successfully.
rejected_hypotheses:
  - Increase the Cave Rat death timeout: rejected because standalone combat and repaired combat-first journey both remove the same deterministic target without a timeout change.
  - Add privileged skill, spell, damage or kill setup: rejected because the repaired journey physically passes using only existing lower-level capabilities.
  - Extend the runner or add a new journey orchestrator: rejected because the existing bounded action-plan runner completed the full journey.
  - Ignore the original physical failure because CI was green: rejected; the failure was repaired and re-proven physically.
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-e2e-gameplay-008-cross-system-journey.md
  - tests/e2e/scenarios/journeys/promotion-combat-persistence.json
  - tests/e2e/test_cross_system_promotion_combat_journey.py
validation:
  - command: Agent Task Ownership run 29998764282
    result: PASS
    evidence: Ownership and checkpoint validation passed on repaired pre-final head 21cdfe4de8d5494b338b936cee80c5acd1516dad.
  - command: CI run 29998764500 and autofix run 29998764343
    result: PASS
    evidence: Repository CI and formatting passed on repaired pre-final head.
  - command: Universal Agent E2E run 29998764675 / physical job 89185121476 / Required physical E2E
    result: PASS
    evidence: Real controlled OTClient completed deterministic combat, explicit arena close and return, Canary NPC promotion, safe logout, second login, Royal Paladin and zero-balance persistence, and final safe logout.
blockers: []
next_action: Require immutable exact-final-head Ownership, CI, autofix and Universal Agent E2E on the resulting ci:final-gate checkpoint commit; if all pass, audit exact three-file scope and reviews, squash-merge PR 765, register 006/007/008 shared documentation, then merge one final checkpoint-only update while keeping this task active.
```
