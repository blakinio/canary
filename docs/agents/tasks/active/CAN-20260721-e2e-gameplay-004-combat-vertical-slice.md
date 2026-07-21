---
task_id: CAN-20260721-e2e-gameplay-004-combat-vertical-slice
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-GAMEPLAY-004-COMBAT-VERTICAL-SLICE
status: investigating
agent: "GPT-5.6 Thinking"
branch: feat/e2e-gameplay-004-combat-vertical-slice
base_branch: main
created: 2026-07-21
updated: 2026-07-21
last_verified_commit: "87c4f71b0deb880da7ba4228bc29e769db2c5818"
risk: low
related_issue: ""
related_pr: ""
depends_on:
  - merged Universal physical gameplay action contract PR 446
  - merged Universal follow_route execution PR 589
  - merged Thais temple-to-depot physical route proof PR 600
blocks:
  - representative deterministic combat coverage required before E2E-GAMEPLAY-008 cross-system journeys
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260721-e2e-gameplay-004-combat-vertical-slice.md
    - tests/e2e/scenarios/combat/deterministic-combat.json
    - tests/e2e/test_deterministic_combat.py
  read_only:
    - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
    - docs/architecture/universal-e2e-gameplay-validation.md
    - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/run_physical_e2e.sh
    - tools/e2e/client/agent_e2e_scenario.lua
    - tools/e2e/route_plan_execution.py
    - data-otservbr-global/world/otservbr-monster.xml
    - docker/data/02-test_account_players.sql
modules_touched:
  - Universal E2E feature-owned combat scenario
reuses:
  - canonical Universal E2E disposable Canary/MariaDB/controlled-OTClient lifecycle
  - existing attack_visible, wait_creature and observe_attacking physical actions
  - existing follow_route execution when nontrivial navigation is required
public_interfaces: []
cross_repo_tasks: []
---

# CAN-20260721 — E2E-GAMEPLAY-004 deterministic combat vertical slice

## Goal

Deliver one bounded deterministic real-client combat lifecycle on the existing Universal Physical E2E platform, with a source-evidenced creature fixture, bounded attack proof, first-failure evidence and cleanup, without adding a second runner or speculative platform capability.

## Acceptance criteria

- [ ] Prove an exact deterministic creature fixture or controlled scenario environment from current repository evidence.
- [ ] Use the existing generic physical action contract; do not add a new shared action unless a concrete reusable gap is proven and split into a separate platform task.
- [ ] Use `follow_route` for any nontrivial navigation rather than blind directional walking.
- [ ] Physically observe the target, start attack through `attack_visible`, and prove the client enters attacking state.
- [ ] Prove at least one deterministic combat outcome beyond target acquisition when the existing observable surfaces support it.
- [ ] Keep timeouts bounded and retain exact first-failure evidence.
- [ ] Do not depend on random public-world occupancy, production systems or guessed monster names/positions.
- [ ] Keep gameplay/datapack, OTBM binary, map and client asset paths unchanged unless a separately owned prerequisite is proven necessary.
- [ ] Pass focused tests, checkpoint validation, ownership and exact-final-head CI/Physical E2E gates before merge.
- [ ] Merge through the normal autonomous gate, then archive this task in a separate lifecycle PR.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T13:40:00+02:00
head: 87c4f71b0deb880da7ba4228bc29e769db2c5818
branch: feat/e2e-gameplay-004-combat-vertical-slice
pr: ""
status: investigating
context_routes:
  - universal-e2e
owned_paths:
  - docs/agents/tasks/active/CAN-20260721-e2e-gameplay-004-combat-vertical-slice.md
  - tests/e2e/scenarios/combat/deterministic-combat.json
  - tests/e2e/test_deterministic_combat.py
proven:
  - Universal physical gameplay action contract PR 446 is merged and exposes attack_visible, wait_creature, observe_attacking and bounded health observation surfaces.
  - Universal follow_route execution PR 589 and Thais temple-to-depot physical route proof PR 600 are merged.
  - E2E-GAMEPLAY-003 quest/NPC feature PR 637 and lifecycle PR 663 are merged.
  - E2E-GAMEPLAY-005 persistence closure PR 666 and lifecycle PR 673 are merged.
  - no open pull request matched a deterministic E2E-GAMEPLAY-004 combat vertical slice during live preflight.
derived:
  - E2E-GAMEPLAY-004 is the nearest unconditional missing package in the ordered gameplay queue; multi-client and recovery work remain demand-gated.
unknown:
  - exact current monster spawn nearest to the deterministic Knight 1 fixture that is suitable for an isolated bounded combat proof
  - whether existing generic client observations are sufficient to prove a deterministic post-attack outcome without a feature-owned observer adapter
conflicts: []
first_failure:
  marker: none
  evidence: no unresolved implementation or runtime failure is established at task start
rejected_hypotheses:
  - start E2E-GAMEPLAY-006 speculatively without a concrete multi-client feature consumer
  - start E2E-GAMEPLAY-007 before selecting a stable baseline scenario and explicit safe fault seam
changed_paths:
  - docs/agents/tasks/active/CAN-20260721-e2e-gameplay-004-combat-vertical-slice.md
validation:
  - command: live open-PR search for deterministic combat physical E2E ownership
    result: PASS
    evidence: no open PR matching the E2E-GAMEPLAY-004 combat vertical-slice scope was found
  - command: current programme and architecture queue audit
    result: PASS
    evidence: E2E-GAMEPLAY-004 is defined as the deterministic combat slice; E2E-GAMEPLAY-006 and 007 remain conditional
blockers: []
next_action: Audit current Knight 1 fixture position against data-otservbr-global/world/otservbr-monster.xml and select one exact isolated deterministic target, or prove that a separate generic fixture capability is required before scenario implementation.
```
