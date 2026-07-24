---
task_id: CAN-20260723-ots-charm-bestiary-drome-mastery
program_id: CAN-PROGRAM-OTS-FUTURE-GAMEPLAY-SYSTEMS
coordination_id: OTS-CHARM-BESTIARY-DROME-MASTERY
status: review
agent: "GPT-5.6 Thinking"
branch: docs/charm-bestiary-drome-mastery-20260723
base_branch: main
created: 2026-07-23
updated: 2026-07-24
last_verified_commit: "e372b04f3adf16ec4300a88ad53e1b589a86809d"
risk: low
related_issue: ""
related_pr: "784"
depends_on: []
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260723-ots-charm-bestiary-drome-mastery.md
    - docs/ai-agent/OTS_CHARM_BESTIARY_AND_DROME_MASTERY.md
  shared: []
  read_only:
    - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md
    - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md
    - docs/ai-agent/OTS_BOUNTY_AND_WEEKLY_TASKS_REWORK.md
modules_touched:
  - future-gameplay-product-design
  - charm-bestiary-drome-design
reuses:
  - existing Tibia Bestiary, Charm and Tibiadrome foundations as implementation-time baselines
public_interfaces: []
cross_repo_tasks: []
---

# Charm, Bestiary and Drome Mastery design

## Goal

Preserve the proposed staged Charm/Bestiary progression, creature-family mastery, persistent Charm loadouts and bounded Drome integration as a durable future-gameplay design record.

## Acceptance criteria

- [x] Preserve staged Charm Point rewards and Bestiary-gated effective Charm levels.
- [x] Preserve Level 1-4 progression and Creature Family Mastery direction.
- [x] Preserve persistent assignments/loadouts and Drome amplifier boundaries.
- [x] Keep all numerical examples non-contractual and require telemetry/simulation.
- [x] Make no runtime, client, datapack, map or economy configuration changes.
- [ ] Pass exact-final Agent Task Ownership and CI on the current PR head.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T16:50:00+02:00
head: e372b04f3adf16ec4300a88ad53e1b589a86809d
branch: docs/charm-bestiary-drome-mastery-20260723
pr: 784
status: validating
context_routes:
  - agent-governance
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260723-ots-charm-bestiary-drome-mastery.md
  - docs/ai-agent/OTS_CHARM_BESTIARY_AND_DROME_MASTERY.md
proven:
  - The detailed design document is the only product-design file introduced by the original PR head.
  - The document explicitly describes a future design and does not claim implementation in current Canary or OTClient.
  - Exact formulas, costs, caps and balance values remain open pending telemetry and simulation.
derived:
  - The underlying Bestiary, Charm and Tibiadrome concepts are Tibia foundations, while staged rewards, Level 4/Family Mastery and loadout behavior are custom extension directions requiring later central classification.
unknown:
  - Exact current Tibia, Canary and OTClient behavior and implementation coverage at future implementation time.
conflicts: []
first_failure:
  marker: missing-task-record
  evidence: PR 784 originally added only the detailed design document without the active task/checkpoint required by repository governance.
rejected_hypotheses:
  - Treat illustrative percentages or capstones as final implementation values.
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-ots-charm-bestiary-drome-mastery.md
  - docs/ai-agent/OTS_CHARM_BESTIARY_AND_DROME_MASTERY.md
validation:
  - command: changed-file and design-boundary review
    result: PASS
    evidence: Scope is limited to one future design document plus this task record; no runtime or binary paths are changed.
  - command: exact-head Agent Task Ownership and CI
    result: NOT_RUN
    evidence: Required workflows must run on the task-record final commit after ci:final-gate was applied.
blockers: []
next_action: Require exact-head checks, mark PR 784 ready and squash-merge if all gates pass.
```
