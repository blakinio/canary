---
task_id: CAN-20260729-rtec-005-chat-communication
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-005-W2-CHAT-COMMUNICATION
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/rtec-005-chat-communication-20260729
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
    - docs/agents/tasks/active/CAN-20260729-rtec-005-chat-communication.md
    - docs/agents/real-tibia/evidence/modules/chat-communication/**
    - docs/agents/real-tibia/evidence/requests/**/RTREQ-*-CHAT-COMMUNICATION-*.yaml
  shared: []
  read_only:
    - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
    - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
    - docs/agents/real-tibia/registry/modules/chat-communication.yaml
    - src/creatures/interactions/chat.cpp
    - src/creatures/interactions/chat.hpp
modules_touched:
  - chat-communication
reuses:
  - canary-real-tibia-evidence-record-v1
  - canary-real-tibia-generated-indexes-v1
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Deliver one bounded prepublication evidence package for the exact current Canary chat-channel registry, callback, membership and private-channel lifecycle source path without changing implementation or shared publication ownership.

# Acceptance criteria

- [x] Pin the canonical registry and exact `chat.hpp`/`chat.cpp` source blobs.
- [ ] Add `RT-CHAT-COMMUNICATION-0001`, bounded dossier documents, version history and pending structured review.
- [ ] Keep the candidate `review-needed` and the published module index empty at `as_of=2026-07-26`.
- [ ] Create no owner request because the missing dimensions are not sufficiently narrowed.
- [ ] Make no global-index, programme, runtime, data, client, protocol, map, workflow or E2E edit.
- [ ] Pass Evidence Contracts, Agent Task Ownership and ordinary CI on the exact candidate head.
- [ ] Pass ready-state final gate, squash-merge and archive the worker task.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T10:10:00+02:00
head: 18411a50e81d857fba8cf42bfa9b1f4c67a3904a
branch: feat/rtec-005-chat-communication-20260729
pr: none
status: implementing
context_routes:
  - agent-governance
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260729-rtec-005-chat-communication.md
  - docs/agents/real-tibia/evidence/modules/chat-communication/**
proven:
  - coordinator PR 1000 exists before this branch
  - registry blob is d736ff891a48315aa4bd7c34a5a553ca1d31ffd3
  - chat.cpp blob is 152a40857f4b184e968eb51601a75634d8d37946
  - chat.hpp blob is 09f8a727fef239b95b1bb5da20356801769732f0
  - worker paths do not overlap the engine-scheduler worker
derived:
  - the selected source can support only a bounded current-canary runtime-path claim
unknown:
  - configured channel data and Lua callback correctness
  - protocol/client delivery, privacy, moderation and physical gameplay behavior
conflicts: []
first_failure:
  marker: none
  evidence: worker created from the exact wave baseline
rejected_hypotheses:
  - claim protocol or security correctness from source registration
  - edit the shared generated index from the worker
changed_paths:
  - docs/agents/tasks/active/CAN-20260729-rtec-005-chat-communication.md
validation:
  - command: ownership precondition
    result: PASS
    evidence: PR 1000 exists and selected paths are disjoint
blockers: []
next_action: Open the draft worker PR and add the bounded candidate dossier.
```
