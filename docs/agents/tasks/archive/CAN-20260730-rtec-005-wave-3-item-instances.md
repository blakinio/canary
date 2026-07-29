---
task_id: CAN-20260730-rtec-005-wave-3-item-instances
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-005-WAVE-3
status: completed
agent: "GPT-5.6 Thinking"
branch: docs/rtec-005-wave-3-item-instances-20260730
base_branch: main
created: 2026-07-30T00:12:00+02:00
updated: 2026-07-30T00:51:00+02:00
last_verified_commit: "146f0d6bd6a7c330bc4a39f03d23f1879ae4053f"
risk: medium
related_issue: ""
related_pr: "1022"
depends_on:
  - CAN-20260730-rtec-005-wave-3-coordination
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/archive/CAN-20260730-rtec-005-wave-3-item-instances.md
  shared: []
  read_only:
    - docs/agents/real-tibia/evidence/modules/item-instances/**
modules_touched:
  - item-instances
reuses:
  - canary-real-tibia-evidence-record-v1
  - canary-real-tibia-module-evidence-index-v1
  - canary-real-tibia-version-history-v1
public_interfaces: []
cross_repo_tasks: []
---

# Result

- Added the bounded `item-instances` dossier and candidate `RT-ITEM-INSTANCES-0001`.
- Kept the candidate `review-needed` with pending coordinator review and an unpublished module evidence index.
- Added exact-baseline history `RTVH-ITEM-INSTANCES-0001` required by the corpus contract.
- Preserved explicit nonclaims for static ItemType correctness, containers, movement, decay scheduling, serialization completeness, ownership safety, gameplay and parity.
- Preserved all owner requests and coordinator-owned shared files unchanged.
- PR #1022 passed Agent Task Ownership `30495869574`, Evidence Contracts `30495869351`, Module Registry `30495869545`, Upstream Intelligence `30495869359` and full CI `30496001023`, then squash-merged as `0b088e3fc9313d02c317032271f6323c78569bfd`.

## Final checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-30T00:51:00+02:00
head: 146f0d6bd6a7c330bc4a39f03d23f1879ae4053f
branch: docs/rtec-005-wave-3-item-instances-20260730
pr: 1022
merge_sha: 0b088e3fc9313d02c317032271f6323c78569bfd
status: completed
context_routes:
  - agent-governance
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/archive/CAN-20260730-rtec-005-wave-3-item-instances.md
changed_paths:
  - docs/agents/tasks/archive/CAN-20260730-rtec-005-wave-3-item-instances.md
  - docs/agents/tasks/active/CAN-20260730-rtec-005-wave-3-item-instances.md
proven:
  - worker PR 1022 changed only its task and item-instances dossier root
  - RT-ITEM-INSTANCES-0001 remains a bounded unpublished candidate for coordinator adjudication
  - exact-head ownership, evidence contracts, module registry, upstream intelligence and full CI passed
  - PR 1022 squash-merged as 0b088e3fc9313d02c317032271f6323c78569bfd
derived:
  - coordinator PR 1020 must independently adjudicate and publish or reject the candidate
unknown:
  - coordinator adjudication outcome
conflicts: []
first_failure:
  marker: none
  evidence: candidate corpus shape was corrected proactively from the configuration sibling diagnostic before this worker final gate
rejected_hypotheses:
  - publish from the worker lane
  - mutate owner requests or shared global files
validation:
  - command: full exact-head worker gate
    result: PASS
    evidence: runs 30495869574, 30495869351, 30495869545, 30495869359 and 30496001023
blockers: []
next_action: Merge the shared worker lifecycle PR, then let coordinator PR 1020 adjudicate the candidate.
```
