---
task_id: CAN-20260724-ots-roadmap-lifecycle-cleanup
program_id: CAN-PROGRAM-OTS-FUTURE-GAMEPLAY-SYSTEMS
coordination_id: OTS-ROADMAP-LIFECYCLE-CLEANUP
status: review
agent: "GPT-5.6 Thinking"
branch: docs/ots-roadmap-lifecycle-cleanup-20260724
base_branch: main
created: 2026-07-24
updated: 2026-07-24
last_verified_commit: "a730d2546533b73e54d3815b7359416ee9452c36"
risk: low
related_issue: ""
related_pr: "878"
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

- [x] Archive the task for merged PR #664.
- [x] Archive the task for merged PR #667.
- [x] Archive the task for merged PR #674.
- [x] Archive the task for merged PR #772.
- [x] Remove the corresponding active records.
- [x] Preserve exact delivery head and squash-merge evidence.
- [x] Change no gameplay, client, map, datapack or product-design content.
- [ ] Pass exact-head Agent Task Ownership and applicable documentation CI.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T16:40:00+02:00
head: a730d2546533b73e54d3815b7359416ee9452c36
branch: docs/ots-roadmap-lifecycle-cleanup-20260724
pr: 878
status: validating
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
  - Archive records for all four completed tasks are present on the branch.
  - Their stale active records are removed on the branch.
  - The changed-file set is limited to one cleanup task plus four active-delete/archive-add lifecycle pairs.
  - Current main drift 9d99a0665050d244a0ee0beb0362080de0f3d19a changes only the unrelated Oteryn programme record.
derived:
  - Removing stale active ownership should unblock exact ownership validation for later OTS roadmap tasks.
unknown:
  - Exact-head GitHub validation outcome for the final checkpoint commit.
conflicts: []
first_failure:
  marker: stale-active-lifecycle
  evidence: PR 799 Agent Task Ownership failed while completed roadmap tasks still retained active ownership.
rejected_hypotheses:
  - Modify gameplay roadmap content as part of lifecycle cleanup.
changed_paths:
  - docs/agents/tasks/active/CAN-20260724-ots-roadmap-lifecycle-cleanup.md
  - docs/agents/tasks/active/CAN-20260721-ots-future-gameplay-roadmap.md
  - docs/agents/tasks/active/CAN-20260721-ots-skill-wheel-pz-rule.md
  - docs/agents/tasks/active/CAN-20260721-ots-roadmap-classification.md
  - docs/agents/tasks/active/CAN-20260723-ots-dynamic-spawn-bounty-roadmap-integration.md
  - docs/agents/tasks/archive/CAN-20260721-ots-future-gameplay-roadmap.md
  - docs/agents/tasks/archive/CAN-20260721-ots-skill-wheel-pz-rule.md
  - docs/agents/tasks/archive/CAN-20260721-ots-roadmap-classification.md
  - docs/agents/tasks/archive/CAN-20260723-ots-dynamic-spawn-bounty-roadmap-integration.md
validation:
  - command: GitHub merged PR evidence review for PRs 664, 667, 674 and 772
    result: PASS
    evidence: Each PR is closed/merged and its exact final head and squash-merge SHA are recorded in the corresponding archive task.
  - command: changed-file and scope review
    result: PASS
    evidence: Only agent task lifecycle paths are changed; no gameplay, roadmap, classification, client, map or datapack content is modified.
  - command: exact-head Agent Task Ownership and CI
    result: NOT_RUN
    evidence: Required workflows must run on the final checkpoint commit after ci:final-gate is applied.
blockers: []
next_action: Require exact-head ownership and CI on PR 878, then mark ready and squash-merge with expected head if all gates pass.
```
