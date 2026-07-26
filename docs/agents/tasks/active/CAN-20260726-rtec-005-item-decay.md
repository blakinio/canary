---
task_id: CAN-20260726-rtec-005-item-decay
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-005-W1-ITEM-DECAY
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/rtec-005-item-decay-20260726
base_branch: main
created: 2026-07-26T10:34:53+02:00
updated: 2026-07-26T22:10:00+02:00
last_verified_commit: "97cf0b1367db6845f86b0169aa4d08ab01ca0d4f"
risk: medium
related_issue: ""
related_pr: "957"
depends_on:
  - RTEC-005-WAVE-1
  - PR-960-PREPUBLICATION-INDEX-GATE
  - PR-968-OWNER-REQUEST-PREPUBLICATION-VIEW
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260726-rtec-005-item-decay.md
    - docs/agents/real-tibia/evidence/modules/item-decay/**
    - docs/agents/real-tibia/evidence/requests/**/RTREQ-*-ITEM-DECAY-*.yaml
  shared: []
  read_only:
    - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
    - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
    - docs/agents/real-tibia/registry/modules/item-decay.yaml
    - src/items/decay/**
    - tools/agents/real_tibia_evidence.py
    - tools/agents/real_tibia_owner_request.py
modules_touched:
  - item-decay
reuses:
  - canary-real-tibia-evidence-record-v1
  - canary-real-tibia-generated-indexes-v1
  - prepublication publication view merged in PR 960
  - owner-request prepublication lifecycle view merged in PR 968
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Deliver one bounded prepublication evidence package for the exact current Canary item-decay source path without changing implementation or shared publication ownership.

# Acceptance criteria

- [x] Refresh the branch through `main@414be71495fdfdccc089c7b0cab2e7006b28dc30`.
- [x] Pin the canonical registry and exact `decay.hpp`/`decay.cpp` source blobs.
- [x] Add `RT-ITEM-DECAY-0001`, bounded dossier documents, version history and pending structured review.
- [x] Keep the candidate `review-needed` and the published module index empty at `as_of=2026-07-25`.
- [x] Create no owner request because the missing owner dimension is not sufficiently narrowed.
- [x] Make no global-index, programme, runtime, data, client, protocol, map, workflow or E2E edit.
- [x] Pass Evidence Contracts, Agent Task Ownership and ordinary CI on the exact candidate head.
- [x] Hand the validated candidate package to the coordinator for adjudication.
- [ ] Pass the Ready-state final gate and squash-merge the worker package.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T22:10:00+02:00
head: 97cf0b1367db6845f86b0169aa4d08ab01ca0d4f
branch: feat/rtec-005-item-decay-20260726
pr: 957
status: implementing
context_routes:
  - agent-governance
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260726-rtec-005-item-decay.md
  - docs/agents/real-tibia/evidence/modules/item-decay/**
  - docs/agents/real-tibia/evidence/requests/**/RTREQ-*-ITEM-DECAY-*.yaml
proven:
  - PR 960 merged the prepublication publication view
  - PR 968 merged the owner-request prepublication lifecycle view as 414be71495fdfdccc089c7b0cab2e7006b28dc30
  - registry blob is 03901f5a28e0dbc4a8db55fdf892410b730558b7
  - decay source blobs are 0d540e10dc73b65f2ce1aa00bfb9dd72994dcc5f and 458cda4ac92f21289ca1072447e79c71de645ae8
  - RT-ITEM-DECAY-0001 records only the duration-bucket and transform/removal source path
  - the record remains review-needed with pending coordinator review
  - the module index is the empty published view at 2026-07-25
  - no owner request or shared global-index edit was made
  - exact head 97cf0b1367db6845f86b0169aa4d08ab01ca0d4f passed Evidence Contracts run 30216450484
  - exact head 97cf0b1367db6845f86b0169aa4d08ab01ca0d4f passed Agent Task Ownership run 30216450461
  - exact head 97cf0b1367db6845f86b0169aa4d08ab01ca0d4f passed ordinary CI run 30216450568
  - exact head 97cf0b1367db6845f86b0169aa4d08ab01ca0d4f passed Module Registry run 30216450483 and Upstream Intelligence run 30216450469
derived:
  - the candidate is structurally valid and remains unpublished pending coordinator adjudication
unknown:
  - whether the coordinator will accept, change or reject RT-ITEM-DECAY-0001
  - runtime timing, restart recovery, persistence, metadata, gameplay and physical-client proof
conflicts: []
first_failure:
  marker: final-gate-not-yet-run
  evidence: the candidate head is green and handed to the coordinator; Ready-state Required validation remains
rejected_hypotheses:
  - backdate evidence
  - publish candidate IDs from the worker
  - create a broad runtime or E2E request without a narrowed owner contract
changed_paths:
  - docs/agents/tasks/active/CAN-20260726-rtec-005-item-decay.md
  - docs/agents/real-tibia/evidence/modules/item-decay/**
validation:
  - command: Real Tibia Evidence Contracts run 30216450484
    result: PASS
    evidence: source contracts, publication view, generated indexes and production owner-request dry-run succeeded
  - command: Agent Task Ownership run 30216450461
    result: PASS
    evidence: changed-task checkpoint and ownership validation succeeded
  - command: ordinary CI run 30216450568
    result: PASS
    evidence: exact-head ordinary CI succeeded
blockers: []
next_action: Apply the final-gate label, mark PR 957 Ready, pass the Required check, then squash-merge the item-decay worker package.
```
