---
task_id: CAN-20260726-rtec-005-parties
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-005-W1-PARTIES
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/rtec-005-parties-20260726
base_branch: main
created: 2026-07-26T10:35:03+02:00
updated: 2026-07-26T22:50:00+02:00
last_verified_commit: "ad734f81772eb840c7e1ce18b27ac9ed0d2a4c50"
risk: medium
related_issue: ""
related_pr: "958"
depends_on:
  - RTEC-005-WAVE-1
  - PR-960-PREPUBLICATION-INDEX-GATE
  - PR-968-OWNER-REQUEST-PREPUBLICATION-VIEW
  - PR-957-ITEM-DECAY-CANDIDATE
  - PR-973-ITEM-DECAY-TASK-ARCHIVE
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260726-rtec-005-parties.md
    - docs/agents/real-tibia/evidence/modules/parties/**
    - docs/agents/real-tibia/evidence/requests/**/RTREQ-*-PARTIES-*.yaml
  shared: []
  read_only:
    - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
    - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
    - docs/agents/real-tibia/registry/modules/parties.yaml
    - docs/agents/real-tibia/evidence/modules/item-decay/**
    - src/creatures/players/grouping/party.*
    - tools/agents/real_tibia_evidence.py
    - tools/agents/real_tibia_owner_request.py
modules_touched:
  - parties
reuses:
  - canary-real-tibia-evidence-record-v1
  - canary-real-tibia-generated-indexes-v1
  - prepublication publication view merged in PR 960
  - owner-request prepublication lifecycle view merged in PR 968
  - item-decay candidate merged in PR 957
  - item-decay active ownership released in PR 973
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Deliver one bounded prepublication evidence package that keeps official visible party behavior and the exact current Canary party source path as separate claims.

# Acceptance criteria

- [x] Refresh the remaining worker after PR #957 merged.
- [x] Refresh again after PR #973 archived the completed item-decay task and released its active ownership.
- [x] Pin current official guide/support locators, canonical registry and exact `party.hpp`/`party.cpp` blobs.
- [x] Add `RT-PARTIES-0001`, `RT-PARTIES-0002`, bounded dossier documents, version history and pending structured review.
- [x] Keep both candidates `review-needed` and the published module index empty at `as_of=2026-07-25`.
- [x] Create no owner request because review has not narrowed one non-duplicative owner dimension.
- [x] Make no global-index, programme, runtime, client, protocol, map, workflow or E2E edit.
- [ ] Pass Evidence Contracts, Agent Task Ownership and ordinary CI on the post-cleanup exact head.
- [ ] Hand the validated candidate package to the coordinator for independent adjudication of both records.
- [ ] Pass the Ready-state final gate and squash-merge the worker package.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T22:50:00+02:00
head: ad734f81772eb840c7e1ce18b27ac9ed0d2a4c50
branch: feat/rtec-005-parties-20260726
pr: 958
status: implementing
context_routes:
  - agent-governance
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260726-rtec-005-parties.md
  - docs/agents/real-tibia/evidence/modules/parties/**
  - docs/agents/real-tibia/evidence/requests/**/RTREQ-*-PARTIES-*.yaml
proven:
  - PR 960 merged the prepublication publication view
  - PR 968 merged the owner-request prepublication lifecycle view
  - PR 957 passed Required run 30216659464 and merged as 7e6d0078d7ad87a82aea092ff4285256fcae746f
  - PR 973 passed Ownership run 30217579309 and CI run 30217579385 and archived the item-decay task as ad734f81772eb840c7e1ce18b27ac9ed0d2a4c50
  - registry blob is a2ddd8b0ceb6c5e80e30b17fcb22c5cfd626dc0c
  - party source blobs are 52b08e7321dd4e35bfb68415254239245ed236ee and c3493c962548bffa5e393adc3359137b200b6384
  - current official Party Mode and Shared Experience pages were verified on 2026-07-26
  - RT-PARTIES-0001 records only the official visible requirements
  - RT-PARTIES-0002 records only the selected current Canary lifecycle and Shared Experience path
  - both records remain review-needed with pending coordinator review
  - the module index remains the empty published view at 2026-07-25
  - no owner request or shared global-index edit was made
derived:
  - active ownership is now disjoint because the completed item-decay task is archived
  - the parties package can coexist with merged item-decay evidence without factual publication
unknown:
  - whether the coordinator will accept, change or reject either parties record
  - active multiplier, battle-sign gate, activity call sites, formulas, runtime, protocol, client and physical gameplay proof
conflicts: []
first_failure:
  marker: post-cleanup-refresh-not-yet-validated
  evidence: the lifecycle conflict is resolved and the branch is refreshed, but exact-head gates have not rerun
rejected_hypotheses:
  - weaken glob overlap validation
  - claim whole-module conformance from partial source comparison
  - publish candidate IDs from the worker
  - create a broad feature, protocol or E2E request before review narrows the missing proof
changed_paths:
  - docs/agents/tasks/active/CAN-20260726-rtec-005-parties.md
  - docs/agents/real-tibia/evidence/modules/parties/**
validation:
  - command: item-decay lifecycle cleanup PR 973
    result: PASS
    evidence: active task moved to archive; Ownership 30217579309 and CI 30217579385 succeeded
blockers: []
next_action: Recreate the parties candidate package on ad734f81772eb840c7e1ce18b27ac9ed0d2a4c50 and pass exact-head evidence, ownership, registry, upstream and CI gates.
```
