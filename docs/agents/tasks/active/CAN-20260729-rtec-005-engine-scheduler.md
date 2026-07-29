---
task_id: CAN-20260729-rtec-005-engine-scheduler
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-005-W2-ENGINE-SCHEDULER
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/rtec-005-engine-scheduler-20260729
base_branch: main
created: 2026-07-29T10:10:00+02:00
updated: 2026-07-29T10:10:00+02:00
last_verified_commit: "18411a50e81d857fba8cf42bfa9b1f4c67a3904a"
risk: medium
related_issue: ""
related_pr: ""
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
- [ ] Add `RT-ENGINE-SCHEDULER-0001`, bounded dossier documents, version history and pending structured review.
- [ ] Keep the candidate `review-needed` and the published module index empty at `as_of=2026-07-26`.
- [ ] Create no owner request because the missing runtime dimensions are not sufficiently narrowed.
- [ ] Make no global-index, programme, runtime, data, client, protocol, map, workflow or E2E edit.
- [ ] Pass Evidence Contracts, Agent Task Ownership and ordinary CI on the exact candidate head.
- [ ] Pass ready-state final gate, squash-merge and archive the worker task.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T10:10:00+02:00
head: 18411a50e81d857fba8cf42bfa9b1f4c67a3904a
branch: feat/rtec-005-engine-scheduler-20260729
pr: none
status: implementing
context_routes:
  - agent-governance
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260729-rtec-005-engine-scheduler.md
  - docs/agents/real-tibia/evidence/modules/engine-scheduler/**
proven:
  - coordinator PR 1000 exists before this branch
  - registry blob is bcf728df9999d2bda9019918066200a69f1daad5
  - dispatcher blobs are 8a537385a76095104c3ab71e19a770f6ad282c38 and 22ffa032c2bb3fac4ad4189569a7dc1d43c0d699
  - task blobs are 7747d584370a25f2569da987225b31d556b69472 and 9435a7704a0da81ae12ffef5d18f9dc29bdbf882
  - thread-pool blobs are c753278ae0e1b4f439e1ad72bbca599d575bbda6 and a5e3c54fadecb53367b9d5580de2b1a053f94572
  - worker paths do not overlap the chat-communication worker
derived:
  - the selected source can support only a bounded current-canary runtime-path claim
unknown:
  - ordering, fairness, race safety, timing accuracy and shutdown correctness
  - feature-specific timers, persistence scheduling and physical gameplay behavior
conflicts: []
first_failure:
  marker: none
  evidence: worker created from the exact wave baseline
rejected_hypotheses:
  - claim concurrency or timing properties from source presence
  - edit the shared generated index from the worker
changed_paths:
  - docs/agents/tasks/active/CAN-20260729-rtec-005-engine-scheduler.md
validation:
  - command: ownership precondition
    result: PASS
    evidence: PR 1000 exists and selected paths are disjoint
blockers: []
next_action: Open the draft worker PR and add the bounded candidate dossier.
```
