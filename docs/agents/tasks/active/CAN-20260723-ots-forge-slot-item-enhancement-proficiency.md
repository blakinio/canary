---
task_id: CAN-20260723-ots-forge-slot-item-enhancement-proficiency
program_id: CAN-PROGRAM-OTS-FUTURE-GAMEPLAY-SYSTEMS
coordination_id: OTS-FORGE-EQUIPMENT-PROGRESSION
status: review
agent: "GPT-5.6 Thinking"
branch: docs/forge-slot-item-enhancement-proficiency-20260723
base_branch: main
created: 2026-07-23
updated: 2026-07-24
last_verified_commit: "599057c820eef50aba2a70cf9d1a27a98adfaf05"
risk: low
related_issue: ""
related_pr: "794"
depends_on: []
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260723-ots-forge-slot-item-enhancement-proficiency.md
    - docs/ai-agent/OTS_FORGE_SLOT_ITEM_ENHANCEMENT_AND_EQUIPMENT_PROFICIENCY.md
  shared: []
  read_only:
    - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md
    - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md
    - docs/ai-agent/OTS_SKILL_PROGRESSION_2_0.md
modules_touched:
  - future-gameplay-product-design
  - equipment-progression-design
reuses:
  - existing Tibia Forge, item Classification and Weapon Proficiency foundations as implementation-time baselines
public_interfaces: []
cross_repo_tasks: []
---

# Forge Slot, Item Enhancement and Equipment Proficiency design

## Goal

Preserve the proposed three-layer equipment progression model: permanent slot mastery, bounded item-instance enhancement and build-oriented Equipment Proficiency.

## Acceptance criteria

- [x] Preserve permanent Forge-style progression on equipment slots.
- [x] Preserve separate item-instance Enhancement and classification-based ceilings.
- [x] Preserve Equipment Proficiency specialisation and controlled Retaliation/Reflect direction.
- [x] Preserve economy, migration, simulation and bounded-RNG requirements.
- [x] Make no runtime, Forge, equipment, item, combat, market or client changes.
- [ ] Pass exact-final Agent Task Ownership and CI on the current PR head.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T16:54:00+02:00
head: 599057c820eef50aba2a70cf9d1a27a98adfaf05
branch: docs/forge-slot-item-enhancement-proficiency-20260723
pr: 794
status: validating
context_routes:
  - agent-governance
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260723-ots-forge-slot-item-enhancement-proficiency.md
  - docs/ai-agent/OTS_FORGE_SLOT_ITEM_ENHANCEMENT_AND_EQUIPMENT_PROFICIENCY.md
proven:
  - The detailed design document is the only product-design file introduced by the original PR head.
  - The document separates slot mastery, item enhancement and equipment proficiency instead of presenting one undifferentiated upgrade system.
  - All concrete caps and values are explicitly illustrative and require economy/combat validation before implementation.
derived:
  - Forge, item Classification and Weapon Proficiency are Tibia foundations; slot-owned mastery, generic Equipment Proficiency and item Enhancement are custom extension directions requiring later central classification.
unknown:
  - Exact current Tibia, Canary and OTClient behavior and implementation coverage at future implementation time.
conflicts: []
first_failure:
  marker: missing-task-record
  evidence: PR 794 originally added only the detailed design document without the active task/checkpoint required by repository governance.
rejected_hypotheses:
  - Treat illustrative +N ceilings, perk levels or sample item values as implementation contracts.
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-ots-forge-slot-item-enhancement-proficiency.md
  - docs/ai-agent/OTS_FORGE_SLOT_ITEM_ENHANCEMENT_AND_EQUIPMENT_PROFICIENCY.md
validation:
  - command: changed-file and design-boundary review
    result: PASS
    evidence: Scope is limited to one future design document plus this task record; no runtime or binary paths are changed.
  - command: exact-head Agent Task Ownership and CI
    result: NOT_RUN
    evidence: Required workflows must run on the task-record final commit after ci:final-gate was applied.
blockers: []
next_action: Require exact-head checks, mark PR 794 ready and squash-merge if all gates pass.
```
