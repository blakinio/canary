---
task_id: CAN-20260724-ots-roadmap-lifecycle-cleanup
program_id: CAN-PROGRAM-OTS-FUTURE-GAMEPLAY-SYSTEMS
coordination_id: OTS-ROADMAP-LIFECYCLE-CLEANUP
status: in_progress
agent: "GPT-5.6 Thinking"
branch: docs/ots-roadmap-lifecycle-cleanup-20260724
base_branch: main
created: 2026-07-24
updated: 2026-07-24
last_verified_commit: "6e223c142f34285b98ea70d79131c79b1680e2d0"
risk: low
related_issue: ""
related_pr: ""
depends_on: []
blocks:
  - PR 799 ownership validation
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260724-ots-roadmap-lifecycle-cleanup.md
    - docs/agents/tasks/active/CAN-20260721-ots-future-gameplay-roadmap.md
    - docs/agents/tasks/active/CAN-20260721-ots-skill-wheel-pz-rule.md
    - docs/agents/tasks/active/CAN-20260721-ots-roadmap-classification.md
    - docs/agents/tasks/active/CAN-20260723-ots-dynamic-spawn-bounty-roadmap-integration.md
    - docs/agents/tasks/archive/CAN-20260721-ots-future-gameplay-roadmap.md
    - docs/agents/tasks/archive/CAN-20260721-ots-skill-wheel-pz-rule.md
    - docs/agents/tasks/archive/CAN-20260721-ots-roadmap-classification.md
    - docs/agents/tasks/archive/CAN-20260723-ots-dynamic-spawn-bounty-roadmap-integration.md
  shared: []
  read_only:
    - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md
    - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md
    - docs/ai-agent/OTS_SKILL_PROGRESSION_2_0.md
    - docs/ai-agent/OTS_DYNAMIC_SPAWN_AND_HUNTING_CAPACITY.md
    - docs/ai-agent/OTS_BOUNTY_AND_WEEKLY_TASKS_REWORK.md
modules_touched:
  - agent-governance
  - future-gameplay-product-design
reuses:
  - existing merged PR and task evidence
public_interfaces: []
cross_repo_tasks: []
---

# OTS roadmap lifecycle cleanup

## Goal

Archive four completed OTS future-gameplay documentation tasks whose delivery PRs already merged but whose task records incorrectly remained active, thereby retaining stale ownership over the central roadmap and classification paths.

## Acceptance criteria

- [ ] Archive the task for merged PR #664.
- [ ] Archive the task for merged PR #667.
- [ ] Archive the task for merged PR #674.
- [ ] Archive the task for merged PR #772.
- [ ] Remove the corresponding active records.
- [ ] Preserve exact delivery head and squash-merge evidence.
- [ ] Change no gameplay, client, map, datapack or product-design content.
- [ ] Pass exact-head Agent Task Ownership and applicable documentation CI.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T16:30:00+02:00
head: 6e223c142f34285b98ea70d79131c79b1680e2d0
branch: docs/ots-roadmap-lifecycle-cleanup-20260724
pr: null
status: in_progress
context_routes:
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/CAN-20260724-ots-roadmap-lifecycle-cleanup.md
  - docs/agents/tasks/active/CAN-20260721-ots-future-gameplay-roadmap.md
  - docs/agents/tasks/active/CAN-20260721-ots-skill-wheel-pz-rule.md
  - docs/agents/tasks/active/CAN-20260721-ots-roadmap-classification.md
  - docs/agents/tasks/active/CAN-20260723-ots-dynamic-spawn-bounty-roadmap-integration.md
  - docs/agents/tasks/archive/CAN-20260721-ots-future-gameplay-roadmap.md
  - docs/agents/tasks/archive/CAN-20260721-ots-skill-wheel-pz-rule.md
  - docs/agents/tasks/archive/CAN-20260721-ots-roadmap-classification.md
  - docs/agents/tasks/archive/CAN-20260723-ots-dynamic-spawn-bounty-roadmap-integration.md
proven:
  - PR 664 merged as dbffdc996273bf2bd1315dd3b56881f222b61ce4 from final head 5568053b36aa7291b23aa749c18850c9c5c012cb.
  - PR 667 merged as 92ac0d378540f2c6f54d5399c849445e20772bd8 from final head 8c9c825a60ba615da2e9baa0444d032e40e35059.
  - PR 674 merged as 87c4f71b0deb880da7ba4228bc29e769db2c5818 from final head 292085e1e2ebd4988d2e8e67795cb1911aa90e3d.
  - PR 772 merged as 87b943fe1f51ea235547cf7ff10bc922e52cb53d from final head 97d6dac5fbaf12491eb4cca3bee64dc600fe50d6.
  - All four corresponding task records remain under docs/agents/tasks/active on current main.
derived:
  - Stale active ownership can block later roadmap work even though the owning deliveries are complete.
unknown: []
conflicts: []
first_failure:
  marker: stale-active-lifecycle
  evidence: PR 799 Agent Task Ownership failed while completed roadmap tasks still retained active ownership.
rejected_hypotheses:
  - Modify gameplay roadmap content as part of lifecycle cleanup.
changed_paths:
  - docs/agents/tasks/active/CAN-20260724-ots-roadmap-lifecycle-cleanup.md
validation: []
blockers: []
next_action: Archive the four completed task records and delete their active copies.
```
