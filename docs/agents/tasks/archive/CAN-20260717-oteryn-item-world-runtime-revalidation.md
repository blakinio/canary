---
task_id: CAN-20260717-oteryn-item-world-runtime-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: "OAM-007"
status: completed
agent: oteryn-architecture-migration-agent
branch: docs/oam-007-lifecycle-archive
base_branch: main
created: 2026-07-17T06:45:00+02:00
updated: 2026-07-17T09:41:00+02:00
completed: 2026-07-17T09:41:00+02:00
last_verified_commit: "be9760a88d0c714dfd3e1b6a659e373380d03d65"
risk: high
related_issue: "22"
related_pr: "455"
depends_on:
  - OAM-003
  - OAM-004
  - OAM-006
blocks:
  - OAM-008
owned_paths:
  exclusive:
    - docs/agents/tasks/archive/CAN-20260717-oteryn-item-world-runtime-revalidation.md
  shared:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
  read_only:
    - docs/agents/OTERYN_OAM_007_ITEM_WORLD_RUNTIME_REVALIDATION.md
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/real-tibia/registry/modules/item-definitions.yaml
    - docs/agents/real-tibia/registry/modules/item-instances.yaml
    - docs/agents/real-tibia/registry/modules/world-map-runtime.yaml
    - blakinio/canary@c2e181f892ce2f094e887f1da5c6c7df207629c9
    - blakinio/canary@be9760a88d0c714dfd3e1b6a659e373380d03d65
    - blakinio/Otheryn@c547d8ad70ef1252624c255476e6cb83fa125e14
    - blakinio/Otheryn@68c4f39f7b1b45f880543c258627b4ccf73dbc86
    - opentibiabr/canary@e0ac98e399d0f7e483f3668f57b78fcc45b6e53f
    - blakinio/otclient@2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
modules_touched:
  - item-definitions
  - item-instances
  - world-map-runtime
reuses:
  - docs/agents/OTERYN_OAM_003_ENGINE_FOUNDATION_REVALIDATION.md
  - docs/agents/OTERYN_OAM_004_PERSISTENCE_FOUNDATION_REVALIDATION.md
  - docs/agents/OTERYN_OAM_006_NETWORK_LOGIN_PROTOCOL_REVALIDATION.md
  - Universal Agent E2E
public_interfaces:
  - static item definition loading and lookup
  - runtime item construction and serialization boundary
  - map and tile runtime loading, spatial lookup, movement, visibility and pathfinding
cross_repo_tasks:
  - blakinio/Otheryn#22
  - blakinio/Otheryn#23
---

# Final dispositions

| Module | Disposition | Result |
|---|---|---|
| `item-definitions` | `ADAPT` | bounded magic-field add-item registration adaptation delivered by Otheryn PR #23 |
| `item-instances` | `REUSE` | checked principal runtime paths matched task-start target, legacy and upstream |
| `world-map-runtime` | `REUSE` | target/upstream aligned; divergent legacy map fork lacked proven target necessity |

# Completion evidence

- Otheryn PR #23 exact head `cd6fae153ebe495ec9030c9c729f2ceef06872ef` passed ready CI #84, Required #81 and autofix.ci #74 and squash-merged as `68c4f39f7b1b45f880543c258627b4ccf73dbc86`.
- Windows Solution and Linux debug tests passed, including focused `ItemParsePolicyTest` coverage.
- Full heavy Universal Agent E2E #136 (`29559180590`) passed `Required physical E2E` against exact Otheryn `68c4f39f7b1b45f880543c258627b4ccf73dbc86` and OTClient `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`.
- Run #136 server binary SHA-256: `dde78689009209901ca01bcffa94b8aa35267976d1c66037b63d756aff3c8a7a`.
- Run #136 OTClient binary SHA-256: `ceb606775390296d2ce98c7f47e87a35ec457287123246119272e6f3eb6ad72a`.
- Run #136 evidence digest: `sha256:3d3386341791470d78ae6e4140f4009f5191998d08ca23e8a967f91feb932a6f`.
- Canary feature-governance PR #455 exact final head `003cbd7dc177cc6c95c277b0fe149123a36dbdf4` passed Agent Task Ownership #1893, draft CI #3033 and ready-triggered CI #3034 with `Required` success, with zero comments, zero submitted reviews and zero unresolved review threads.
- Canary feature-governance PR #455 squash-merged as `be9760a88d0c714dfd3e1b6a659e373380d03d65`.
- This lifecycle-only package archives OAM-007 and contains no OAM-008 implementation.

# Carried boundaries

- The exact physical run is a runtime regression smoke; the occupied-tile magic-field behavior remains proven by focused policy coverage plus PR #81 provenance.
- No Real Tibia item-value/appearance parity, map completeness or exhaustive movement/pathfinding correctness is claimed.
- OAM-004 residual persistence gaps remain unchanged, including non-atomic player SQL commit followed by later durable KV flush.
- The divergent legacy Map/Tile/MapCache/MapSector fork remains non-migrated evidence unless a future bounded task proves a concrete target requirement.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T09:41:00+02:00
head: be9760a88d0c714dfd3e1b6a659e373380d03d65
branch: docs/oam-007-lifecycle-archive
pr: pending
status: completed
context_routes:
  - agent-governance
  - item-definitions
  - item-instances
  - world-map-runtime
owned_paths:
  - docs/agents/tasks/archive/CAN-20260717-oteryn-item-world-runtime-revalidation.md
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
proven:
  - item-definitions disposition is ADAPT
  - item-instances disposition is REUSE
  - world-map-runtime disposition is REUSE
  - Otheryn PR 23 merged as 68c4f39f7b1b45f880543c258627b4ccf73dbc86
  - Universal Agent E2E 136 passed exact final-target runtime proof
  - Canary feature-governance PR 455 merged as be9760a88d0c714dfd3e1b6a659e373380d03d65
  - feature final head 003cbd7dc177cc6c95c277b0fe149123a36dbdf4 passed Ownership 1893 and ready CI 3034
  - this package is lifecycle-only and contains no OAM-008 implementation
derived:
  - OAM-007 target delivery and feature governance are complete
  - this lifecycle PR is the final OAM-007 completion boundary
  - OAM-008 may become next eligible only after this lifecycle PR merges
unknown:
  - lifecycle PR number
  - final lifecycle merge SHA
conflicts: []
first_failure:
  marker: none active
  evidence: lifecycle-only validation remains
rejected_hypotheses:
  - OAM-008 can start before OAM-007 lifecycle completion
  - physical login/relog alone proves occupied-tile magic-field damage
  - every legacy map runtime divergence must migrate
changed_paths:
  - docs/agents/tasks/active/CAN-20260717-oteryn-item-world-runtime-revalidation.md
  - docs/agents/tasks/archive/CAN-20260717-oteryn-item-world-runtime-revalidation.md
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
validation:
  - command: OAM-007 target and exact runtime evidence
    result: PASS
    evidence: target 68c4f39f7b1b45f880543c258627b4ccf73dbc86 and E2E 136 are complete
  - command: Canary feature-governance PR 455 final gates
    result: PASS
    evidence: exact head 003cbd7dc177cc6c95c277b0fe149123a36dbdf4; Ownership 1893; ready CI 3034; merge be9760a88d0c714dfd3e1b6a659e373380d03d65
blockers: []
next_action: Pass lifecycle-only exact-head ownership/CI/review gates and squash-merge this archive package. Only then may OAM-008 become next eligible.
```
