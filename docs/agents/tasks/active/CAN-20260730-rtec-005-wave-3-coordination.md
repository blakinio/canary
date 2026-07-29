---
task_id: CAN-20260730-rtec-005-wave-3-coordination
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-005-WAVE-3
status: active
agent: "GPT-5.6 Thinking"
branch: docs/rtec-005-wave-3-coordination-20260730
base_branch: main
created: 2026-07-30T00:07:00+02:00
updated: 2026-07-30T00:09:00+02:00
last_verified_commit: "1926b3426de4e453efae23c08761dd359d95da52"
risk: medium
related_issue: ""
related_pr: "1020"
depends_on:
  - CAN-20260729-rtec-005-wave-3-preflight
blocks:
  - CAN-20260730-rtec-005-wave-3-configuration
  - CAN-20260730-rtec-005-wave-3-item-instances
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260730-rtec-005-wave-3-coordination.md
    - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
    - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
  shared:
    - docs/agents/real-tibia/evidence/modules/configuration/EVIDENCE_INDEX.yaml
    - docs/agents/real-tibia/evidence/modules/configuration/VERSION_HISTORY.yaml
    - docs/agents/real-tibia/evidence/modules/configuration/records/RT-CONFIGURATION-0001.yaml
    - docs/agents/real-tibia/evidence/modules/configuration/reviews/RTEC-005-W3-CONFIGURATION-REVIEW.md
    - docs/agents/real-tibia/evidence/modules/item-instances/EVIDENCE_INDEX.yaml
    - docs/agents/real-tibia/evidence/modules/item-instances/VERSION_HISTORY.yaml
    - docs/agents/real-tibia/evidence/modules/item-instances/records/RT-ITEM-INSTANCES-0001.yaml
    - docs/agents/real-tibia/evidence/modules/item-instances/reviews/RTEC-005-W3-ITEM-INSTANCES-REVIEW.md
  read_only:
    - docs/agents/real-tibia/evidence/requests/**
    - docs/agents/real-tibia/registry/modules/configuration.yaml
    - docs/agents/real-tibia/registry/modules/item-instances.yaml
    - src/config/configmanager.cpp
    - src/config/configmanager.hpp
    - config.lua.dist
    - src/items/item.cpp
    - src/items/item.hpp
    - src/items/functions/item/attribute.cpp
    - src/items/functions/item/attribute.hpp
    - src/items/functions/item/custom_attribute.cpp
    - src/items/functions/item/custom_attribute.hpp
modules_touched:
  - real-tibia-evidence-collection
  - configuration
  - item-instances
reuses:
  - canary-real-tibia-evidence-record-v1
  - canary-real-tibia-owner-request-v1
  - canary-real-tibia-generated-indexes-v1
  - RTEC-004 validator and generator
  - RTEC-005 two-worker serialized-index model
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Coordinate RTEC-005 wave 3 for the independent `configuration` and `item-instances` dossier roots, independently adjudicate the two candidate records after worker lifecycle completion, and remain the only writer for the programme and generated global index.

# Coordination contract

- This task and its draft pull request exist before either Collector branch.
- At most two Collector workers and two worker PRs may be active.
- Workers own only their new dossier roots and active task files; they must not edit this task, the programme, generated global index, existing owner requests, runtime, data, client, protocol, map, workflow or E2E paths.
- The coordinator PR remains open while worker packages and lifecycle moves merge.
- After both worker lifecycles merge, refresh this branch from current `main`, independently review candidate claims and nonclaims, accept/reject or narrow each record, regenerate module/global indexes deterministically, update the programme handoff, run the full exact-head gate, merge, then archive this task.
- Preserve unchanged unless genuine owner evidence arrives: `RTREQ-FEATURE-VOCATIONS-0001`, `RTREQ-TCR-ITEM-DEFINITIONS-0001`, `RTREQ-TCR-ITEM-DEFINITIONS-0002`.

# Expected candidate boundaries

## `configuration`

Candidate proof may cover current-Canary typed configuration loading/access, default handling, reload/cache behavior and OTC feature-list discovery at `runtime-path-proven`. It must not claim production configuration correctness, secret handling, controlled feature behavior, protocol correctness or runtime feature validation.

## `item-instances`

Candidate proof may cover current-Canary runtime item factory/subtype creation, instance attributes, clone/equality/transform/subtype/charge state and serialization boundaries at `runtime-path-proven`. It must not claim static `ItemType` correctness, container behavior, movement orchestration, scheduled decay, serialization completeness or ownership safety.

# Acceptance criteria

- [x] Open the coordinator branch and active task before worker branches.
- [x] Open draft coordinator PR #1020 before worker branches.
- [ ] Merge both bounded worker packages and their lifecycle moves.
- [ ] Independently adjudicate both candidate records and reviews.
- [ ] Keep all three existing owner requests unchanged unless real owner evidence arrives.
- [ ] Regenerate module and global indexes deterministically at the canonical date.
- [ ] Update the programme queue and handoff with exact merged evidence and check identifiers.
- [ ] Pass exact-head ownership, Evidence Contracts, Module Registry, Upstream Intelligence and full final CI.
- [ ] Squash-merge and archive this coordinator task.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-30T00:09:00+02:00
head: 1926b3426de4e453efae23c08761dd359d95da52
branch: docs/rtec-005-wave-3-coordination-20260730
pr: 1020
status: active
context_routes:
  - agent-governance
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260730-rtec-005-wave-3-coordination.md
  - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
  - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
changed_paths:
  - docs/agents/tasks/active/CAN-20260730-rtec-005-wave-3-coordination.md
proven:
  - wave 3 preflight source PR 1016 merged as 09209bae26b2bb7e14346f08677e2cd8724aa7ae
  - wave 3 preflight lifecycle PR 1019 merged as 8e21a33325d6bd8ddbb647e7c967f940dfd54516
  - configuration and item-instances are the preflight-approved absent and disjoint roots
  - corpus baseline is 15 evidence records, 3 active owner requests and 12 version-history records at as_of 2026-07-29
  - this coordinator task and draft PR 1020 existed before either worker branch
derived:
  - this branch must remain the sole global-index and programme writer for wave 3
  - worker records must remain candidates until independent coordinator adjudication
unknown:
  - exact worker PR numbers and merge SHAs
  - whether candidate claims require narrowing after independent review
  - exact final generated input hash after worker merges
conflicts: []
first_failure:
  marker: none
  evidence: no coordinator validation failure has occurred
rejected_hypotheses:
  - let workers mutate the programme or generated global index
  - alter existing owner requests without owner evidence
  - merge the coordinator before worker lifecycle completion
validation:
  - command: preflight source and lifecycle exact-head gates
    result: PASS
    evidence: PRs 1016 and 1019 merged after successful ownership/full CI
  - command: coordinator branch and draft PR ordering
    result: PASS
    evidence: PR 1020 opened from coordinator branch before worker branch creation
blockers: []
next_action: Create the two bounded worker branches and candidate dossier packages.
```
