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
last_verified_commit: "60ed8b044c2307418caf051bcd7fac3aa1257faf"
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
modules_touched:
  - Universal E2E cross-system journey sentinel
reuses:
  - merged Canary NPC promotion scenario behavior
  - merged deterministic combat scenario behavior
  - existing bounded action plan compiler and controlled OTClient driver
  - existing typed player_vocation and player_balance persistence assertions
  - existing canonical safe logout, relog and cleanup lifecycle
public_interfaces: []
cross_repo_tasks: []
---

# CAN-20260723 — E2E-GAMEPLAY-008 cross-system journey

## Goal

Compose already physically proven NPC/economy/vocation, deterministic combat and relog/persistence capabilities into one representative real-client journey sentinel without adding a new runner, workflow, action type, datapack mechanic or fixture.

## Acceptance criteria

- [x] Reuse the exact `Paladin 15` controlled fixture, client pin and Canary datapack already proven by the lower-level promotion and combat scenarios.
- [x] Compose the lower-level promotion step sequence followed by the lower-level combat sequence in one scenario, without introducing a new generic action.
- [x] Preserve deterministic arena cleanup before the canonical safe logout/relog lifecycle.
- [x] Re-prove durable Royal Paladin vocation and zero bank balance after relog through existing typed persistence assertions.
- [x] Add focused composition-contract tests that fail when the journey silently diverges from the proven lower-level step contracts.
- [x] Keep journey success as an integration sentinel; do not replace or delete the focused promotion or combat scenarios/tests.
- [ ] Pass exact-head Agent Task Ownership, CI and Universal Physical E2E validation.
- [ ] Pass immutable exact-final-head gates and merge the feature PR.
- [ ] Leave this final programme task in `docs/agents/tasks/active` with a validated final checkpoint and one concrete next action; do not archive it in this run.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T11:40:00+02:00
head: 60ed8b044c2307418caf051bcd7fac3aa1257faf
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
  - E2E-GAMEPLAY-004 is merged in PR 677 and physically proved deterministic instance-arena creation, exact approach edges, Cave Rat combat, target removal and explicit arena cleanup.
  - Both lower-level scenarios use the same @test15 / Paladin 15 fixture, the same controlled OTClient revision and the same data-canary Canary map runtime.
  - E2E-GAMEPLAY-006 and E2E-GAMEPLAY-007 are merged and their lifecycle task ownership has been released.
  - PR 765 contains exactly the active task, one journeys scenario and one focused composition-contract test on predecessor head 60ed8b044c2307418caf051bcd7fac3aa1257faf.
  - Universal Agent E2E scenario resolution succeeded on predecessor head 60ed8b044c2307418caf051bcd7fac3aa1257faf for journeys/promotion-combat-persistence.
derived:
  - The journey is a pure composition of the exact lower-level promotion steps and combat steps excluding only the duplicate combat online observation, followed by the existing two-session persistence lifecycle.
unknown:
  - Physical runtime outcome of the composed promotion-plus-combat journey has not yet completed.
  - Exact-final-head CI and Universal Physical E2E evidence do not yet exist for this task.
conflicts: []
first_failure:
  marker: checkpoint-related-pr-mismatch
  evidence: Initial Ownership run 29995668222 rejected related_pr as empty while validating PR 765; implementation and scenario resolution were not implicated.
rejected_hypotheses:
  - Add a new journey orchestrator: rejected because the existing scenario action-plan runner already composes bounded steps.
  - Add new combat, NPC or persistence actions: rejected because all required actions and assertions are already physically proven.
  - Replace focused 003/004 tests with the journey: rejected because 008 is an integration sentinel only.
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-e2e-gameplay-008-cross-system-journey.md
  - tests/e2e/scenarios/journeys/promotion-combat-persistence.json
  - tests/e2e/test_cross_system_promotion_combat_journey.py
validation:
  - command: Universal Agent E2E run 29995668576 scenario resolution
    result: PASS
    evidence: Existing runner discovered, validated and resolved journeys/promotion-combat-persistence on predecessor head 60ed8b044c2307418caf051bcd7fac3aa1257faf.
  - command: Agent Task Ownership run 29995668222
    result: FAIL
    evidence: Governance-only failure because frontmatter related_pr was empty instead of current PR 765; corrected in this checkpoint commit.
blockers: []
next_action: Require clean exact-head Ownership, CI and Universal Physical E2E on PR 765 after the related_pr correction; repair only the first proven failure if any, otherwise freeze the final checkpoint and run immutable final-head gates.
```
