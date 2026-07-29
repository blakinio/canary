---
task_id: CAN-20260729-rtec-005-engine-scheduler
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-005-W2-ENGINE-SCHEDULER
status: review
agent: "GPT-5.6 Thinking"
branch: feat/rtec-005-engine-scheduler-20260729
base_branch: main
created: 2026-07-29T10:10:00+02:00
updated: 2026-07-29T10:20:00+02:00
last_verified_commit: "c4ccd32e74795d1a1a5f22df9c7ae5f21fea3314"
risk: medium
related_issue: ""
related_pr: "1002"
depends_on:
  - PR-1000-RTEC-005-WAVE-2-COORDINATOR
blocks:
  - RTEC-005-WAVE-2-COORDINATOR-ADJUDICATION
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260729-rtec-005-engine-scheduler.md
    - docs/agents/real-tibia/evidence/modules/engine-scheduler/**
    - docs/agents/real-tibia/evidence/requests/**/RTREQ-*-ENGINE-SCHEDULER-*.yaml
  shared: []
  read_only:
    - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
    - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
    - docs/agents/real-tibia/registry/modules/engine-scheduler.yaml
    - src/game/scheduling/dispatcher.cpp
    - src/game/scheduling/dispatcher.hpp
    - src/game/scheduling/task.cpp
    - src/game/scheduling/task.hpp
    - src/lib/thread/thread_pool.cpp
    - src/lib/thread/thread_pool.hpp
modules_touched:
  - engine-scheduler
reuses:
  - canary-real-tibia-evidence-record-v1
  - canary-real-tibia-generated-indexes-v1
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Deliver one bounded prepublication evidence package for the exact current Canary dispatcher, task and thread-pool scheduling source path without changing implementation or shared publication ownership.

# Acceptance criteria

- [x] Pin the canonical registry and exact dispatcher/task/thread-pool source blobs.
- [x] Add `RT-ENGINE-SCHEDULER-0001`, bounded dossier documents, version history and pending structured review.
- [x] Keep the candidate `review-needed` and the published module index empty at `as_of=2026-07-26`.
- [x] Create no owner request because the missing runtime dimensions are not sufficiently narrowed.
- [x] Make no global-index, programme, runtime, data, client, protocol, map, workflow or E2E edit.
- [ ] Pass Evidence Contracts, Agent Task Ownership and ordinary CI on the exact candidate head.
- [ ] Pass ready-state final gate, squash-merge and archive the worker task.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T10:20:00+02:00
head: c4ccd32e74795d1a1a5f22df9c7ae5f21fea3314
branch: feat/rtec-005-engine-scheduler-20260729
pr: 1002
status: validating
context_routes:
  - agent-governance
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260729-rtec-005-engine-scheduler.md
  - docs/agents/real-tibia/evidence/modules/engine-scheduler/**
proven:
  - coordinator PR 1000 exists before this branch
  - exact registry and source blobs are pinned
  - RT-ENGINE-SCHEDULER-0001 is limited to the selected current Canary source path at runtime-path-proven
  - candidate review remains pending and module index remains unpublished at as_of 2026-07-26
  - no owner request or shared path was changed
derived:
  - coordinator adjudication is required before publication
unknown:
  - ordering, fairness, race safety, timing accuracy and shutdown correctness
  - feature-specific timers, persistence scheduling and physical gameplay behavior
conflicts: []
first_failure:
  marker: none
  evidence: candidate package assembled within worker ownership
rejected_hypotheses:
  - claim concurrency or timing properties from source presence
  - edit the shared generated index from the worker
changed_paths:
  - docs/agents/tasks/active/CAN-20260729-rtec-005-engine-scheduler.md
  - docs/agents/real-tibia/evidence/modules/engine-scheduler/**
validation:
  - command: worker package boundary review
    result: PASS
    evidence: PR 1002 changes only its task and engine-scheduler dossier
  - command: exact-head Evidence Contracts, Agent Task Ownership and ordinary CI
    result: NOT_RUN
    evidence: pending current head workflows
blockers: []
next_action: Pass exact-head validation, apply the final gate, mark PR 1002 ready and merge it without broadening scope.
```
