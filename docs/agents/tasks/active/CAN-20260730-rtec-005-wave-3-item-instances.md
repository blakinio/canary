---
task_id: CAN-20260730-rtec-005-wave-3-item-instances
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-005-WAVE-3
status: active
agent: "GPT-5.6 Thinking"
branch: docs/rtec-005-wave-3-item-instances-20260730
base_branch: main
created: 2026-07-30T00:12:00+02:00
updated: 2026-07-30T00:12:00+02:00
last_verified_commit: "8e21a33325d6bd8ddbb647e7c967f940dfd54516"
risk: medium
related_issue: ""
related_pr: ""
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

The candidate may prove only the selected source path for runtime item factory/subtype creation, instance integer/string/custom attributes, clone/equality/transform/subtype/charge state, serialization boundaries and ownership-related attributes at `runtime-path-proven`.

It must not claim static `ItemType` correctness, containers, movement orchestration, scheduled decay, serialization completeness, ownership safety, gameplay or Real Tibia parity.

# Acceptance criteria

- [x] Worker branch and active task created after coordinator PR #1020.
- [ ] Open draft worker PR.
- [ ] Add MODULE, behavior model, decisions, empty module index/history, candidate record and pending review.
- [ ] Keep record `review-needed` and review `pending` for coordinator adjudication.
- [ ] Pass exact-head ownership, Evidence Contracts, Module Registry and final CI.
- [ ] Squash-merge, then archive through the shared worker lifecycle PR.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-30T00:12:00+02:00
head: pending-first-commit
branch: docs/rtec-005-wave-3-item-instances-20260730
pr: null
status: active
context_routes:
  - agent-governance
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260730-rtec-005-wave-3-item-instances.md
  - docs/agents/real-tibia/evidence/modules/item-instances/**
changed_paths:
  - docs/agents/tasks/active/CAN-20260730-rtec-005-wave-3-item-instances.md
proven:
  - coordinator PR 1020 existed before this worker branch
  - item-instances registry and selected sources were pinned by merged wave 3 preflight
  - item-instances dossier root was absent at preflight
  - worker does not own shared programme, generated index or owner-request paths
derived:
  - the worker output must remain a candidate package until coordinator adjudication
unknown:
  - exact worker PR number
  - exact final candidate head and check identifiers
conflicts: []
first_failure:
  marker: none
  evidence: no worker validation failure has occurred
rejected_hypotheses:
  - claim static ItemType correctness, serialization completeness or ownership safety from selected paths
  - edit shared global publication paths
validation:
  - command: merged wave 3 preflight
    result: PASS
    evidence: PRs 1016 and 1019
blockers: []
next_action: Open the draft worker PR and populate the bounded dossier package.
```
