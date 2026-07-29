---
task_id: CAN-20260729-rtec-005-wave-3-preflight
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-005-WAVE-3-PREFLIGHT
status: ready
agent: "GPT-5.6 Thinking"
branch: docs/rtec-005-wave-3-preflight-20260729
base_branch: main
created: 2026-07-29T23:15:00+02:00
updated: 2026-07-29T23:24:00+02:00
last_verified_commit: "ab47084a3cef7917cacfde093aa9c9f892d6e5d6"
risk: medium
related_issue: ""
related_pr: "1016"
depends_on:
  - RTEC-005 wave 2
blocks:
  - RTEC-005 wave 3 coordinator and collectors
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260729-rtec-005-wave-3-preflight.md
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

# Goal

Select one fresh bounded RTEC-005 wave of two independent absent dossier roots without changing evidence, owner requests, runtime, data, client, protocol, map, workflow or E2E paths.

# Selected Collector boundaries

## Collector A — `configuration`

- Registry record: `docs/agents/real-tibia/registry/modules/configuration.yaml` blob `1978a0ac02f3139104e0d1bfb3037563f90ae784`.
- Current-Canary source pins:
  - `src/config/configmanager.cpp` blob `74c8a6f558257aa8bddf57f56116838390dcb25c`;
  - `src/config/configmanager.hpp` blob `8c1e90a7f0f1f894879b54a2de9971ffaeb48e1f`;
  - `config.lua.dist` blob `021dc3e49aadbecead4d5b6d7d3b7ca6243b776e`.
- Bounded scope: typed configuration loading and access, `config.lua` and default-value discovery, reload boundaries and feature-flag discovery.
- Nonclaims: controlled feature behavior, production configuration, secrets, protocol correctness and runtime feature validation.

## Collector B — `item-instances`

- Registry record: `docs/agents/real-tibia/registry/modules/item-instances.yaml` blob `95327a52cbb2dc2ab7c63a34332925d0048972fd`.
- Current-Canary source pins:
  - `src/items/item.cpp` blob `62e8117dc7dcb135d4849c22832a251032420a93`;
  - `src/items/item.hpp` blob `a882313ba808ff0170d5231953694f6345af1399`;
  - `src/items/functions/item/attribute.cpp` blob `715b5ac3e0b231506b338f64bd10074548de0c37`;
  - `src/items/functions/item/attribute.hpp` blob `4f6ca169a47fe6d7b6ff88f286a28e755af0959e`;
  - `src/items/functions/item/custom_attribute.cpp` blob `701a65fa142df5233ee1ad2a25e8b43c25262e07`;
  - `src/items/functions/item/custom_attribute.hpp` blob `54f532fd4e15283f71994884ad71040b090f042f`.
- Bounded scope: runtime item factory and subtype creation, integer/string/custom attributes, clone/equality/transform/subtype/charge state, serialization boundaries and ownership-related attributes.
- Nonclaims: static `ItemType` registry, containers, movement orchestration, scheduled decay, serialization completeness and ownership safety.

# Safety and concurrency

- Both dossier roots are absent on current `main` and their registry/source paths are disjoint.
- Retain the RTEC-005 cap of two Collector workers, at most two worker PRs and exactly one coordinator-only serialized global-index lane.
- Create and merge one coordinator task before either Collector branch.
- Workers must not edit the programme, generated global index, existing owner requests, runtime, data, client, protocol, map, workflow or E2E paths.
- Preserve unchanged: `RTREQ-FEATURE-VOCATIONS-0001`, `RTREQ-TCR-ITEM-DEFINITIONS-0001`, `RTREQ-TCR-ITEM-DEFINITIONS-0002`.

# Acceptance criteria

- [x] Verify both registry records and all selected source files at exact blobs.
- [x] Verify both dossier roots are absent.
- [x] Verify no open PR overlaps the selected roots.
- [x] Preserve the three active owner requests unchanged.
- [x] Open PR #1016, apply `ci:final-gate`, and pass exact-head CI and ownership checks.
- [ ] Merge and archive before starting the coordinator task.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T23:24:00+02:00
head: ab47084a3cef7917cacfde093aa9c9f892d6e5d6
branch: docs/rtec-005-wave-3-preflight-20260729
pr: 1016
status: ready
context_routes:
  - agent-governance
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260729-rtec-005-wave-3-preflight.md
changed_paths:
  - docs/agents/tasks/active/CAN-20260729-rtec-005-wave-3-preflight.md
proven:
  - configuration and item-instances dossier roots are absent on current main
  - both registry records and all selected source files exist at the exact blobs recorded above
  - no open pull request matched both selected module roots
  - current generated indexes contain 15 evidence records, 3 active owner requests and 12 version-history records at as_of 2026-07-29
  - RTEC-005 remains limited to two workers, two worker PRs and one serialized coordinator index lane
  - PR 1016 targets blakinio/canary main from blakinio/canary branch docs/rtec-005-wave-3-preflight-20260729
  - ci:final-gate was applied before the final checkpoint commits
  - Agent Task Ownership run 30491978876 passed on head ab47084a3cef7917cacfde093aa9c9f892d6e5d6
  - CI run 30491979028 and its Required job 90711868909 passed on head ab47084a3cef7917cacfde093aa9c9f892d6e5d6
derived:
  - configuration and item-instances form a safe bounded RTEC-005 wave 3 pair
  - one coordinator task must precede worker branches and alone owns later shared-index adjudication
unknown:
  - merge outcome after the refreshed final checkpoint commit
  - exact evidence claims each Collector will submit
  - whether either Collector will need a new owner request
conflicts: []
first_failure:
  marker: Agent Task Ownership / Validate changed active task checkpoints
  evidence: run 30491838633 required checkpoint fields changed_paths, first_failure and owned_paths; commit ab47084a3cef7917cacfde093aa9c9f892d6e5d6 added them and passed run 30491978876
rejected_hypotheses:
  - reuse the merged wave 2 task or PR
  - let workers update the shared global index
  - modify existing owner requests without real owner evidence
  - bypass the Required branch-protection check after merge initially reported it pending
validation:
  - command: connector-based registry, source-pin, dossier-absence and open-PR audit
    result: PASS
    evidence: exact blobs and absent roots recorded in this task
  - command: repository full final gate
    result: PASS
    evidence: CI run 30491979028 including Required job 90711868909 at ab47084a3cef7917cacfde093aa9c9f892d6e5d6
  - command: Agent Task Ownership
    result: PASS
    evidence: run 30491978876 at ab47084a3cef7917cacfde093aa9c9f892d6e5d6
blockers: []
next_action: Verify the refreshed exact-head checks, squash-merge PR 1016, and archive before creating the coordinator task.
```
