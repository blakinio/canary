---
task_id: CAN-20260721-ots-skill-wheel-pz-rule
program_id: CAN-PROGRAM-OTS-FUTURE-GAMEPLAY-SYSTEMS
status: implementing
agent: "GPT-5.6 Thinking"
branch: docs/ots-skill-wheel-pz-20260721
base_branch: main
created: 2026-07-21
updated: 2026-07-21
last_verified_commit: "dbffdc996273bf2bd1315dd3b56881f222b61ce4"
risk: low
related_issue: ""
related_pr: "667"
depends_on: []
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260721-ots-skill-wheel-pz-rule.md
    - docs/ai-agent/OTS_SKILL_PROGRESSION_2_0.md
  shared:
    - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md
  read_only: []
modules_touched: []
reuses:
  - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md
public_interfaces: []
cross_repo_tasks: []
---

# CAN-20260721 — OTS skill wheel and skill progression follow-up

## Goal

Persist the user's requested future gameplay rules for changing the skill wheel outside the temple without PZ/combat lock and for a Skill Progression 2.0 model that rewards genuine combat with monsters while retaining offline training, traditional training and exercise weapons as distinct progression paths.

## Scope

- Documentation only.
- Record that the skill wheel may be changed outside the temple.
- Require the character to have no PZ/combat lock when changing it.
- Record the Real Combat Training direction for active skilling with monsters.
- Record threat-relative contribution, diminishing returns on one persistent target, bounded combat-activity bonuses and shielding-specific progression principles.
- Record the intended hierarchy between offline training, repetitive monster training, normal hunting, highly active hunting and exercise weapons.
- Treat all example multipliers and timers as simulation inputs, not implementation contracts.
- Do not implement server or client behavior in this task.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T10:25:00Z
head: 593939c58ef1f85946b12a4e32f331e5f5b169ea
branch: docs/ots-skill-wheel-pz-20260721
pr: 667
status: implementing
context_routes:
  - agent-governance
owned_paths:
  - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md
  - docs/ai-agent/OTS_SKILL_PROGRESSION_2_0.md
  - docs/agents/tasks/active/CAN-20260721-ots-skill-wheel-pz-rule.md
proven:
  - The user requested that the skill wheel be changeable outside the temple only when the character has no PZ/combat lock.
  - The user accepted recording a Skill Progression 2.0 direction where genuine combat with appropriate monsters is an efficient free source of skill progression.
  - The recorded design includes threat-relative gain, diminishing returns for prolonged attacks on one persistent target, a bounded combat activity signal, shielding-specific rules and anti-abuse considerations.
  - The intended progression hierarchy keeps offline training as slower convenience, traditional repetitive monster training as a lower-efficiency option, normal hunting as the strong free baseline, active genuine combat as a modest bonus and exercise weapons as the fastest controlled economy-sink path.
  - Example efficiency values and timing windows are explicitly non-contractual and require later simulation.
  - PR #664 merged the durable OTS future gameplay roadmap to main as dbffdc996273bf2bd1315dd3b56881f222b61ce4.
  - PR #667 targets blakinio/canary:main from docs/ots-skill-wheel-pz-20260721.
  - Roadmap section 26 records that temple presence is not mandatory and that skill-wheel changes are blocked while the character has PZ/combat lock.
  - The merged PR #664 task record still exists under tasks/active on main and exclusively claims docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md.
derived:
  - The requested changes are documentation-only product/design direction and do not authorize implementation.
  - The roadmap is a shared durable design surface for this follow-up, while the dedicated Skill Progression 2.0 document and this task record are exclusively owned by PR #667.
unknown:
  - Exact implementation semantics and current Canary/OTClient support must be reverified in a later implementation task.
  - Exact threat coefficients, activity scoring, repetition windows, shielding formulas and progression multipliers require simulation and abuse analysis.
conflicts: []
first_failure:
  marker: Agent Task Ownership / Validate tasks and render ownership index
  evidence: Run 29821539868 failed global ownership validation while the merged PR #664 active task still held an exclusive claim on the same roadmap path; changing the follow-up roadmap claim to shared resolved the ownership failure on run 29821669435.
rejected_hypotheses: []
changed_paths:
  - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md
  - docs/ai-agent/OTS_SKILL_PROGRESSION_2_0.md
  - docs/agents/tasks/active/CAN-20260721-ots-skill-wheel-pz-rule.md
validation:
  - command: GitHub live-state preflight
    result: PASS
    evidence: PR #664 is merged and PR #667 remains the bounded same-repository follow-up.
  - command: Roadmap tail verification
    result: PASS
    evidence: Section 26 explicitly permits skill-wheel changes outside the temple only without PZ/combat lock.
  - command: GitHub Actions Agent Task Ownership run 29821669435
    result: PASS
    evidence: The shared-roadmap ownership model passed global active-task ownership validation before the Skill Progression 2.0 extension.
  - command: Skill Progression 2.0 design record creation
    result: PASS
    evidence: docs/ai-agent/OTS_SKILL_PROGRESSION_2_0.md records the accepted real-combat skilling model and marks quantitative examples as non-contractual.
blockers:
  - Current-head ownership, AI Agent Tools and required CI must pass after the Skill Progression 2.0 documentation extension.
next_action: Validate PR #667 on the new current head; if required checks pass and no review blockers remain, keep squash auto-merge enabled.
```
