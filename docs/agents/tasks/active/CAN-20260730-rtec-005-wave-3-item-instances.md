---
task_id: CAN-20260730-rtec-005-wave-3-item-instances
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-005-WAVE-3
status: ready
agent: "GPT-5.6 Thinking"
branch: docs/rtec-005-wave-3-item-instances-20260730
base_branch: main
created: 2026-07-30T00:12:00+02:00
updated: 2026-07-30T00:25:00+02:00
last_verified_commit: "c5e6760cb73cc3a65f2ea9e51934086be98895c6"
risk: medium
related_issue: ""
related_pr: "1022"
depends_on:
  - CAN-20260730-rtec-005-wave-3-coordination
blocks:
  - CAN-20260730-rtec-005-wave-3-coordination
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260730-rtec-005-wave-3-item-instances.md
    - docs/agents/real-tibia/evidence/modules/item-instances/**
  shared: []
  read_only:
    - docs/agents/tasks/active/CAN-20260730-rtec-005-wave-3-coordination.md
    - docs/agents/real-tibia/registry/modules/item-instances.yaml
    - src/items/item.cpp
    - src/items/item.hpp
    - src/items/functions/item/attribute.cpp
    - src/items/functions/item/attribute.hpp
    - src/items/functions/item/custom_attribute.cpp
    - src/items/functions/item/custom_attribute.hpp
modules_touched:
  - item-instances
reuses:
  - canary-real-tibia-evidence-record-v1
  - canary-real-tibia-module-evidence-index-v1
  - canary-real-tibia-version-history-v1
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Create the bounded `item-instances` evidence dossier and one coordinator-reviewable current-Canary candidate record without editing shared programme, global index, owner-request, runtime, data, client, protocol, map, workflow or E2E paths.

# Claim boundary

The candidate proves only the selected source path for runtime item factory/subtype creation, instance integer/string/custom attributes, clone/equality/transform/subtype/charge state, serialization boundaries and ownership-related attributes at `runtime-path-proven`.

It does not claim static `ItemType` correctness, containers, movement orchestration, scheduled decay, serialization completeness, ownership safety, gameplay or Real Tibia parity.

# Acceptance criteria

- [x] Worker branch and active task created after coordinator PR #1020.
- [x] Draft worker PR #1022 opened.
- [x] Added MODULE, behavior model, decisions, empty publication index, candidate version history, candidate record and pending review.
- [x] Kept record `review-needed` and review `pending` for coordinator adjudication.
- [x] Applied `ci:final-gate` before final checkpoint commits.
- [ ] Pass exact-head ownership, Evidence Contracts, Module Registry and final CI.
- [ ] Squash-merge, then archive through the shared worker lifecycle PR.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-30T00:25:00+02:00
head: 787002c05e37a03abd32e2ea5d5d795128491c29
branch: docs/rtec-005-wave-3-item-instances-20260730
pr: 1022
status: ready
context_routes:
  - agent-governance
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260730-rtec-005-wave-3-item-instances.md
  - docs/agents/real-tibia/evidence/modules/item-instances/**
changed_paths:
  - docs/agents/tasks/active/CAN-20260730-rtec-005-wave-3-item-instances.md
  - docs/agents/real-tibia/evidence/modules/item-instances/MODULE.md
  - docs/agents/real-tibia/evidence/modules/item-instances/BEHAVIOR_MODEL.md
  - docs/agents/real-tibia/evidence/modules/item-instances/DECISIONS.md
  - docs/agents/real-tibia/evidence/modules/item-instances/EVIDENCE_INDEX.yaml
  - docs/agents/real-tibia/evidence/modules/item-instances/VERSION_HISTORY.yaml
  - docs/agents/real-tibia/evidence/modules/item-instances/records/RT-ITEM-INSTANCES-0001.yaml
  - docs/agents/real-tibia/evidence/modules/item-instances/reviews/RTEC-005-W3-ITEM-INSTANCES-REVIEW.md
proven:
  - coordinator PR 1020 existed before this worker branch
  - item-instances registry and selected sources were pinned by merged wave 3 preflight
  - item-instances dossier root was absent at preflight
  - PR 1022 contains only the owned task and item-instances dossier root
  - RT-ITEM-INSTANCES-0001 remains review-needed with pending coordinator review
  - module evidence index remains empty before coordinator publication
  - candidate version history records only the exact current-Canary observation baseline
  - worker did not modify shared programme, generated index or owner-request paths
  - ci:final-gate was applied before the final checkpoint commits
derived:
  - the worker output remains a candidate package until coordinator adjudication
unknown:
  - exact corrected-head check identifiers and conclusions
  - coordinator acceptance, narrowing or rejection outcome
conflicts: []
first_failure:
  marker: Real Tibia Evidence Contracts / candidate corpus shape
  evidence: the configuration sibling run 30495526058 established that a new candidate dossier requires a non-empty exact-baseline version history and canonical 2026-07-29 module-index date; this worker applies the same deterministic correction before relying on its own final gate
rejected_hypotheses:
  - claim static ItemType correctness, serialization completeness or ownership safety from selected paths
  - edit shared global publication paths
  - publish the candidate in module/global evidence indexes before coordinator review
  - wait for an identical deterministic failure before correcting the sibling package
validation:
  - command: merged wave 3 preflight
    result: PASS
    evidence: PRs 1016 and 1019
  - command: candidate package path and state audit
    result: PASS
    evidence: eight changed paths are inside the declared worker boundary and the candidate evidence index is unpublished
blockers: []
next_action: Verify corrected exact-head checks, mark PR 1022 ready, squash-merge, and include this task in the shared worker lifecycle archive.
```
