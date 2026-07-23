---
task_id: CAN-20260723-e2e-gameplay-008-cross-system-journey
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-GAMEPLAY-008-CROSS-SYSTEM-JOURNEY
status: validating
agent: "GPT-5.6 Thinking"
branch: docs/e2e-gameplay-008-final-checkpoint
base_branch: main
created: 2026-07-23
updated: 2026-07-23
last_verified_commit: "5f0ed6da6c07910730e8cb96115c8ec498931f70"
risk: low
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
- [x] Pass immutable exact-final-head gates and merge the feature PR.
- [ ] Leave this final programme task in `docs/agents/tasks/active` with a validated final checkpoint and one concrete next action; do not archive it in this run.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T13:40:00+02:00
head: 5f0ed6da6c07910730e8cb96115c8ec498931f70
branch: docs/e2e-gameplay-008-final-checkpoint
pr: 765
status: validating
context_routes:
  - universal-e2e
  - agent-governance
  - cpp-runtime
owned_paths:
  - docs/agents/tasks/active/CAN-20260723-e2e-gameplay-008-cross-system-journey.md
proven:
  - E2E-GAMEPLAY-003 Canary promotion is merged in PR 718 and physically proved the bounded hi/promot/yes NPC flow plus Royal Paladin and zero-balance persistence.
  - E2E-GAMEPLAY-004 is merged in PR 677 and physical run 29838496367 proved the unpromoted Paladin 15 kills the deterministic 30-HP Cave Rat, closes the arena and completes the canonical two-session lifecycle.
  - Initial PR 765 ordering passed promotion, arena creation, movement and attack acquisition but physical run 29995864249 timed out at target_defeated after promotion; retained evidence identified that as the first gameplay failure.
  - InstanceArenaService preserves the player returnPosition and /instancearena close teleports the player back there, supporting combat-first composition without a new route or action.
  - Repaired head 21cdfe4de8d5494b338b936cee80c5acd1516dad preserves the exact combat sequence first and the exact promotion sequence second, excluding only the duplicate promotion online observation.
  - Repaired head passed Agent Task Ownership run 29998764282, autofix run 29998764343, CI run 29998764500 and Universal Agent E2E run 29998764675; physical job 89185121476 and Required physical E2E completed successfully.
  - Immutable feature head f0369ab683b5e157dbb491ade028e8e1a8a5f8da passed Agent Task Ownership run 30000991590, autofix run 30000991570, full CI run 30000991832 and Universal Agent E2E run 30000991864; final physical job 89191443270 and Required physical E2E completed successfully.
  - PR 765 changed exactly the active task, journeys/promotion-combat-persistence manifest and focused composition-contract test, had no review threads, and squash-merged to main as 2b2eafcd0d7990f499f25acf74af6526ca72ceee.
  - Shared E2E programme and Module Catalog registration merged through PR 780 as 5f0ed6da6c07910730e8cb96115c8ec498931f70, recording delivered 006/007 reusable contracts and the 008 integration sentinel without claiming a new generic 008 interface.
derived:
  - The successful final physical run proves an M4 cross-system integration sentinel by composing previously proven combat, NPC/economy/vocation and persistence systems without replacing their focused tests.
  - E2E-GAMEPLAY-006, 007 and the first representative 008 journey are now durably registered; future expansion must start from fresh live-state and concrete feature demand rather than reopening these implementation packages.
unknown:
  - Final checkpoint-only PR number and exact final checkpoint validation outcome are not recorded yet.
conflicts: []
first_failure:
  marker: none on accepted final feature head
  evidence: The earlier target_defeated timeout was resolved by preserving the exact proven combat-before-promotion state; repaired and immutable final physical jobs both completed successfully.
rejected_hypotheses:
  - Increase the Cave Rat death timeout: rejected because standalone combat and repaired combat-first journey both remove the same deterministic target without a timeout change.
  - Add privileged skill, spell, damage or kill setup: rejected because the repaired journey physically passes using only existing lower-level capabilities.
  - Extend the runner or add a new journey orchestrator: rejected because the existing bounded action-plan runner completed the full journey.
  - Ignore the original physical failure because CI was green: rejected; the failure was repaired and re-proven physically.
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-e2e-gameplay-008-cross-system-journey.md
validation:
  - command: Final feature Agent Task Ownership run 30000991590
    result: PASS
    evidence: Ownership and checkpoint validation passed on immutable final feature head f0369ab683b5e157dbb491ade028e8e1a8a5f8da.
  - command: Final feature CI run 30000991832 and autofix run 30000991570
    result: PASS
    evidence: Full final-gate repository CI and formatting passed on immutable final feature head.
  - command: Final feature Universal Agent E2E run 30000991864 / physical job 89191443270 / Required physical E2E
    result: PASS
    evidence: Real controlled OTClient completed deterministic combat, arena return, Canary NPC promotion, safe logout, second login, Royal Paladin and zero-balance persistence, and final safe logout on immutable final head.
  - command: Shared documentation PR 780 Agent Task Ownership run 30003684940 and CI run 30003685117
    result: PASS
    evidence: The exact two-file programme/catalog registration passed ownership and repository CI before squash merge.
blockers: []
next_action: Open the final checkpoint-only PR for this task, apply ci:final-gate before its final checkpoint commit, validate the immutable checkpoint head, merge it while keeping this task active, then run the repository checkpoint and resume tools against current main.
```