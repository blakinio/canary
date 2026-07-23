---
task_id: CAN-20260723-e2e-gameplay-008-cross-system-journey
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-GAMEPLAY-008-CROSS-SYSTEM-JOURNEY
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/e2e-gameplay-008-cross-system-journey
base_branch: main
created: 2026-07-23
updated: 2026-07-23
last_verified_commit: "3d66a9cb6c40b58954cc180181030a1fdc0d95ea"
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
- [ ] Pass exact-head Agent Task Ownership, CI and Universal Physical E2E validation after the evidence-backed ordering repair.
- [ ] Pass immutable exact-final-head gates and merge the feature PR.
- [ ] Leave this final programme task in `docs/agents/tasks/active` with a validated final checkpoint and one concrete next action; do not archive it in this run.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T12:20:00+02:00
head: 3d66a9cb6c40b58954cc180181030a1fdc0d95ea
branch: feat/e2e-gameplay-008-cross-system-journey
pr: 765
status: validating
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
  - E2E-GAMEPLAY-004 is merged in PR 677 and physical run 29838496367 proved the unpromoted Paladin 15 kills the deterministic 30-HP Cave Rat in about one second, closes the arena and completes the canonical two-session lifecycle.
  - Both lower-level scenarios use the same @test15 / Paladin 15 fixture, controlled OTClient revision and data-canary runtime.
  - Initial PR 765 ordering passed Ownership 29995864093, CI 29996009031 and autofix 29996008810 on head a925113ad76f753f0c7196011817653acedf62ec.
  - Universal Agent E2E run 29995864249 physically passed promotion, arena creation, exact movement edges, attack acquisition and attacking-state confirmation but timed out waiting 20 seconds for Cave Rat removal after promotion.
  - The retained failure artifact reports client exit zero and no fatal runtime log; the first gameplay failure is exactly step target_defeated with present=true expected=false.
  - InstanceArenaService stores the player's returnPosition when the arena is entered and closeArenaForPlayer returns that position; the /instancearena close talkaction teleports the player there.
  - The repaired journey therefore preserves the complete proven combat sequence first, closes back to the original Canary-adjacent position, then preserves the promotion sequence excluding only its duplicate online observation.
derived:
  - Reordering the two already-proven vertical slices is narrower and better evidenced than increasing the death timeout or adding combat setup because it keeps combat in the exact unpromoted state that passed E2E-GAMEPLAY-004.
unknown:
  - Physical runtime outcome of the repaired combat-then-promotion journey has not yet completed.
  - Exact-final-head gates do not yet exist for the repaired feature head.
conflicts: []
first_failure:
  marker: target_defeated-timeout-after-promotion
  evidence: Universal Agent E2E run 29995864249 physical job 89176530614 timed out after 20 seconds with Cave Rat still present after successful post-promotion attack acquisition; retained artifact universal-agent-e2e-journeys-promotion-combat-persistence captured the failure.
rejected_hypotheses:
  - Increase the Cave Rat death timeout: rejected because standalone E2E-GAMEPLAY-004 removes the same 30-HP target in about one second and no evidence supports a timing-only failure.
  - Add privileged skill, spell, damage or kill setup: rejected because the proven combat slice requires none and 008 must compose existing capabilities rather than create a new mechanic.
  - Extend the runner or add a new journey orchestrator: rejected because the existing bounded action-plan runner already composes both vertical slices.
  - Ignore the physical failure because CI is green: rejected because 008 specifically requires real-client cross-system proof.
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-e2e-gameplay-008-cross-system-journey.md
  - tests/e2e/scenarios/journeys/promotion-combat-persistence.json
  - tests/e2e/test_cross_system_promotion_combat_journey.py
validation:
  - command: Agent Task Ownership run 29995864093
    result: PASS
    evidence: Ownership and checkpoint validation passed on pre-repair head a925113ad76f753f0c7196011817653acedf62ec after related_pr was corrected to 765.
  - command: CI run 29996009031 and autofix run 29996008810
    result: PASS
    evidence: Full repository CI and formatting passed on pre-repair head a925113ad76f753f0c7196011817653acedf62ec.
  - command: Universal Agent E2E run 29995864249 / physical job 89176530614
    result: FAIL
    evidence: First physical gameplay failure was target_defeated after promotion; all earlier promotion, arena, movement and attack-acquisition steps passed.
  - command: E2E-GAMEPLAY-004 physical run 29838496367 / artifact 8499077538
    result: PASS
    evidence: The same fixture completed the exact combat sequence before promotion, including Cave Rat removal in about one second and explicit arena close.
blockers: []
next_action: Require clean Ownership, CI and Universal Physical E2E on the repaired combat-then-promotion head; if physical proof passes, freeze one final checkpoint commit under ci:final-gate and run immutable exact-final-head gates.
```
