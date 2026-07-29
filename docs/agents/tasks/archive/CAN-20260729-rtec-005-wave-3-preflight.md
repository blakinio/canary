---
task_id: CAN-20260729-rtec-005-wave-3-preflight
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-005-WAVE-3-PREFLIGHT
status: completed
agent: "GPT-5.6 Thinking"
branch: docs/rtec-005-wave-3-preflight-20260729
base_branch: main
created: 2026-07-29T23:15:00+02:00
updated: 2026-07-29T23:48:00+02:00
last_verified_commit: "4aebd4261467aa3a545c94eb789ba6484d32a3bc"
risk: medium
related_issue: ""
related_pr: "1016"
depends_on:
  - RTEC-005 wave 2
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/archive/CAN-20260729-rtec-005-wave-3-preflight.md
  shared: []
  read_only:
    - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
    - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
    - docs/agents/real-tibia/evidence/modules/**
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
  - RTEC-004 and RTEC-005 two-worker serialized-index result
public_interfaces: []
cross_repo_tasks: []
---

# Result

- Selected `configuration` and `item-instances` as absent, disjoint RTEC-005 wave 3 Collector roots.
- Pinned both registry records and every selected current-Canary source file to exact Git blobs.
- Preserved the two-worker, two-worker-PR and one serialized coordinator integration-lane cap.
- Preserved all three active owner requests unchanged.
- Corrected the durable ordering rule: open the coordinator task/PR before workers, retain it as the integration lane, and merge it only after both worker lifecycles.
- PR #1016 changed only the preflight task, passed exact-head Agent Task Ownership run `30492521053` and full CI run `30492521233`, and squash-merged as `09209bae26b2bb7e14346f08677e2cd8724aa7ae`.

# Collector boundaries

## `configuration`

Typed configuration loading/access, default and reload boundaries, and OTC feature-list discovery only. No claim about production configuration, secrets, controlled feature behavior, protocol correctness or runtime feature validation.

## `item-instances`

Runtime item factory/subtype creation, item attributes, clone/equality/transform/subtype/charge state, serialization boundaries and ownership-related attributes only. No claim about static ItemType correctness, containers, movement orchestration, scheduled decay, serialization completeness or ownership safety.

## Final checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T23:48:00+02:00
head: 4aebd4261467aa3a545c94eb789ba6484d32a3bc
branch: docs/rtec-005-wave-3-preflight-20260729
pr: 1016
merge_sha: 09209bae26b2bb7e14346f08677e2cd8724aa7ae
status: completed
context_routes:
  - agent-governance
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/archive/CAN-20260729-rtec-005-wave-3-preflight.md
changed_paths:
  - docs/agents/tasks/archive/CAN-20260729-rtec-005-wave-3-preflight.md
  - docs/agents/tasks/active/CAN-20260729-rtec-005-wave-3-preflight.md
proven:
  - configuration and item-instances were absent and disjoint on the audited main baseline
  - all selected registry and current-Canary source blobs were pinned
  - no open PR overlapped the selected roots at preflight
  - the corpus baseline remained 15 evidence records, 3 active owner requests and 12 version-history records at as_of 2026-07-29
  - Agent Task Ownership run 30492521053 passed on exact head 4aebd4261467aa3a545c94eb789ba6484d32a3bc
  - CI run 30492521233 passed Linux release/debug, Docker image/quickstart, Lua, Fast Checks and Required on the exact head
  - PR 1016 squash-merged as 09209bae26b2bb7e14346f08677e2cd8724aa7ae
derived:
  - one coordinator task and PR must be opened before either worker branch
  - that coordinator remains the only shared-index lane and merges after both worker lifecycles
unknown:
  - exact worker candidate claims until their packages are submitted
  - whether a sufficiently narrow new owner request will be needed
conflicts: []
first_failure:
  marker: Agent Task Ownership / Validate changed active task checkpoints
  evidence: run 30491838633 identified missing checkpoint ownership fields; the corrected exact head passed run 30492521053
rejected_hypotheses:
  - let workers edit shared generated indexes or the programme
  - alter existing owner requests without real owner evidence
  - merge the coordinator before workers
validation:
  - command: Agent Task Ownership
    result: PASS
    evidence: run 30492521053
  - command: repository full final gate
    result: PASS
    evidence: run 30492521233
  - command: squash merge
    result: PASS
    evidence: PR 1016 merged as 09209bae26b2bb7e14346f08677e2cd8724aa7ae
blockers: []
next_action: Merge this archive-only lifecycle move, then open the RTEC-005 wave 3 coordinator task and PR before creating either worker branch.
```
