---
task_id: CAN-20260721-ots-skill-wheel-pz-rule
program_id: CAN-PROGRAM-OTS-FUTURE-GAMEPLAY-SYSTEMS
status: review
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
  - docs/systems/weapon-proficiency.md
public_interfaces: []
cross_repo_tasks: []
---

# CAN-20260721 — OTS skill wheel and skill progression follow-up

## Goal

Persist the user's requested future gameplay rules for changing the skill wheel outside the temple without PZ/combat lock and for a Skill Progression 2.0 model that rewards genuine combat with monsters while retaining offline training, traditional training and exercise weapons as distinct progression paths. Correctly classify Weapon Proficiency as an original-Tibia system, verify current Canary/OTClient baseline support, and prevent the roadmap from introducing a duplicate custom Weapon Mastery layer.

## Scope

- Documentation only.
- Record that the skill wheel may be changed outside the temple.
- Require the character to have no PZ/combat lock when changing it.
- Record the Real Combat Training direction for active skilling with monsters.
- Record threat-relative contribution, diminishing returns on one persistent target, bounded combat-activity bonuses and shielding-specific progression principles.
- Record the intended hierarchy between offline training, repetitive monster training, normal hunting, highly active hunting and exercise weapons.
- Treat all example multipliers and timers as simulation inputs, not implementation contracts.
- Reclassify Weapon Proficiency using explicit `TIBIA-OFFICIAL`, `CANARY-CURRENT`, `OTCLIENT-CURRENT`, `OTS-EXTENSION-CLAIM`, `DESIGN-DIRECTION`, `OPEN` and `CONFLICT` labels.
- Record that Skill Progression 2.0 enhances classic skill progression and must not duplicate Tibia's existing Weapon Proficiency/Mastery system.
- Record current parity gaps as open rather than claiming unsupported current-Tibia parity.
- Do not implement server or client behavior in this task.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T10:45:00Z
head: 61e665e60851ce4043b559ac0ffa288bf21d6c57
branch: docs/ots-skill-wheel-pz-20260721
pr: 667
status: validating
context_routes:
  - agent-governance
owned_paths:
  - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md
  - docs/ai-agent/OTS_SKILL_PROGRESSION_2_0.md
  - docs/agents/tasks/active/CAN-20260721-ots-skill-wheel-pz-rule.md
proven:
  - The user requested that the skill wheel be changeable outside the temple only when the character has no PZ/combat lock.
  - The user accepted recording a Skill Progression 2.0 direction where genuine combat with appropriate monsters is an efficient free source of classic skill progression.
  - The recorded design includes threat-relative gain, diminishing returns for prolonged attacks on one persistent target, a bounded combat activity signal, shielding-specific rules and anti-abuse considerations.
  - The intended progression hierarchy keeps offline training as slower convenience, traditional repetitive monster training as a lower-efficiency option, normal hunting as the strong free baseline, active genuine combat as a modest bonus and exercise weapons as the fastest controlled economy-sink path.
  - Example efficiency values and timing windows are explicitly non-contractual and require later simulation.
  - Current official Tibia already has Weapon Proficiency with per-weapon progression, perk trees and Mastery; the July 2026 official update adds modification of up to two perk slots.
  - Current blakinio/canary contains the Protocol 15.11 Weapon Proficiency baseline with experience, perk selection, Mastery, combat effects, persistence and catalysts.
  - Current OpenTibiaBR OTClient has a dedicated game_proficiency module and release 4.1 includes the proficiency feature.
  - Public TibiaScape material claims its own weapon proficiency but does not expose enough indexed mechanics to prove a distinct extension; it is therefore recorded only as OTS-EXTENSION-CLAIM.
  - Skill Progression 2.0 now explicitly applies its real-combat model to classic skills and does not introduce a second Weapon Mastery system.
  - Normal hunting is documented as progressing classic skill and Weapon Proficiency independently through different mechanics.
  - The 2026 official Weapon Proficiency manipulation flow is not proven in current Canary or OTClient and is recorded as OPEN rather than assumed present.
  - Official Tibia sources conflict on the exact maximum boss proficiency progress value, so exact boss values are recorded as CONFLICT pending current live-data verification.
  - PR #664 merged the durable OTS future gameplay roadmap to main as dbffdc996273bf2bd1315dd3b56881f222b61ce4.
  - PR #667 targets blakinio/canary:main from docs/ots-skill-wheel-pz-20260721.
  - Roadmap section 26 records that temple presence is not mandatory and that skill-wheel changes are blocked while the character has PZ/combat lock.
  - The merged PR #664 task record still exists under tasks/active on main and exclusively claims docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md.
derived:
  - The requested changes are documentation-only product/design direction and do not authorize implementation.
  - The roadmap is a shared durable design surface for this follow-up, while the dedicated Skill Progression 2.0 document and this task record are exclusively owned by PR #667.
  - Current-Tibia parity should be closed before inventing custom Weapon Proficiency extensions.
unknown:
  - Exact implementation semantics for Skill Progression 2.0 require a later bounded implementation task.
  - Exact threat coefficients, activity scoring, repetition windows, shielding formulas and progression multipliers require simulation and abuse analysis.
  - Exact current-Tibia versus Canary Weapon Proficiency parity remains open, including the July 2026 perk-manipulation feature.
  - Exact OTClient support for the July 2026 perk-manipulation UI/protocol flow remains open.
conflicts:
  - Current official Tibia documentation and official update/release material disagree on the maximum boss Weapon Proficiency progress value; do not encode an exact parity requirement until resolved.
first_failure:
  marker: Agent Task Ownership / Validate tasks and render ownership index
  evidence: Run 29821539868 failed global ownership validation while the merged PR #664 active task still held an exclusive claim on the same roadmap path; changing the follow-up roadmap claim to shared resolved the ownership failure on run 29821669435.
rejected_hypotheses:
  - Weapon Proficiency is an OTS-original feature suitable for copying from TibiaScape.
  - A new generic Weapon Mastery layer is needed on top of current Tibia Weapon Proficiency.
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
  - command: Current Tibia Weapon Proficiency verification
    result: PASS
    evidence: Official Tibia game guide and 2025/2026 official announcements prove existing per-weapon proficiency, perk trees, Mastery and the 2026 perk-manipulation update; conflicting exact boss values are explicitly retained as CONFLICT.
  - command: Current Canary Weapon Proficiency verification
    result: PASS
    evidence: docs/systems/weapon-proficiency.md proves the current Protocol 15.11 server baseline including XP, perks, Mastery, persistence, combat effects and catalysts.
  - command: Current OTClient Weapon Proficiency verification
    result: PASS
    evidence: OpenTibiaBR OTClient repository contains modules/game_proficiency and release 4.1 records feat: proficiency from PR #1593.
  - command: Skill Progression 2.0 classification update
    result: PASS
    evidence: docs/ai-agent/OTS_SKILL_PROGRESSION_2_0.md now separates original Tibia, Canary, OTClient, unverified OTS claims and our design direction and rejects duplicate Weapon Mastery.
blockers:
  - Current-head ownership, AI Agent Tools and required CI must pass after the Weapon Proficiency classification update.
next_action: Validate PR #667 on the new current head; if required checks pass and no review blockers remain, keep squash auto-merge enabled.
```
