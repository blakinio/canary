---
task_id: CAN-20260717-oteryn-item-world-runtime-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: "OAM-007"
status: ready
agent: oteryn-architecture-migration-agent
branch: docs/oam-007-item-world-runtime-revalidation
base_branch: main
created: 2026-07-17T06:45:00+02:00
updated: 2026-07-17T09:00:00+02:00
last_verified_commit: "9382d1f5320e8ee465b4e813c4b85cd028feeb9f"
risk: high
related_issue: "22"
related_pr: "455"
depends_on: [OAM-003, OAM-004, OAM-006]
blocks: [OAM-008]
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260717-oteryn-item-world-runtime-revalidation.md
    - docs/agents/OTERYN_OAM_007_ITEM_WORLD_RUNTIME_REVALIDATION.md
  shared:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
  read_only:
    - .github/workflows/universal-agent-e2e.yml
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/real-tibia/registry/modules/item-definitions.yaml
    - docs/agents/real-tibia/registry/modules/item-instances.yaml
    - docs/agents/real-tibia/registry/modules/world-map-runtime.yaml
    - blakinio/canary@c2e181f892ce2f094e887f1da5c6c7df207629c9
    - blakinio/canary@9382d1f5320e8ee465b4e813c4b85cd028feeb9f
    - blakinio/Otheryn@c547d8ad70ef1252624c255476e6cb83fa125e14
    - blakinio/Otheryn@68c4f39f7b1b45f880543c258627b4ccf73dbc86
    - opentibiabr/canary@e0ac98e399d0f7e483f3668f57b78fcc45b6e53f
    - blakinio/otclient@2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
modules_touched: [item-definitions, item-instances, world-map-runtime]
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

| Module | Disposition | Evidence |
|---|---|---|
| `item-definitions` | `ADAPT` | bounded Otheryn PR #23 delivered the verified Canary PR #81 magic-field add-item registration behavior |
| `item-instances` | `REUSE` | checked principal runtime paths matched task-start target, legacy and upstream |
| `world-map-runtime` | `REUSE` | target/upstream aligned; the divergent legacy map fork lacked proven target necessity |

# Completion evidence

- Otheryn PR #23 exact head `cd6fae153ebe495ec9030c9c729f2ceef06872ef` passed ready CI #84, Required #81 and autofix.ci #74 and squash-merged as `68c4f39f7b1b45f880543c258627b4ccf73dbc86`.
- Windows Solution and Linux debug tests passed, including focused `ItemParsePolicyTest` coverage.
- Full heavy Universal Agent E2E #136 (`29559180590`) passed `Required physical E2E` against exact Otheryn `68c4f39f7b1b45f880543c258627b4ccf73dbc86` and OTClient `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`.
- Run #136 server binary SHA-256: `dde78689009209901ca01bcffa94b8aa35267976d1c66037b63d756aff3c8a7a`.
- Run #136 OTClient binary SHA-256: `ceb606775390296d2ce98c7f47e87a35ec457287123246119272e6f3eb6ad72a`.
- Run #136 evidence digest: `sha256:3d3386341791470d78ae6e4140f4009f5191998d08ca23e8a967f91feb932a6f`.
- Runtime proof recorded two successful logins, two safe logouts, persistence checks, client exit code zero and no fatal runtime log hits.
- The exact physical run is a runtime regression smoke; the specific occupied-tile magic-field behavior is proven by the focused policy test plus PR #81 provenance.
- Temporary controlled-server pin and `ci:final-gate` label were removed before final governance scope.
- Canary `main` was re-fetched through `9382d1f5320e8ee465b4e813c4b85cd028feeb9f`; the two intervening commits affect only security validation/lifecycle paths and do not overlap the three OAM-007 governance files.
- `world-zones`, `instances` and OAM-008 were not started.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T09:00:00+02:00
head: 7a420e46607e60220eca347790f62a12e0b33c8b
branch: docs/oam-007-item-world-runtime-revalidation
pr: 455
status: ready
context_routes: [agent-governance, item-definitions, item-instances, world-map-runtime]
owned_paths:
  - docs/agents/tasks/active/CAN-20260717-oteryn-item-world-runtime-revalidation.md
  - docs/agents/OTERYN_OAM_007_ITEM_WORLD_RUNTIME_REVALIDATION.md
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
proven:
  - item-definitions disposition is ADAPT
  - item-instances disposition is REUSE
  - world-map-runtime disposition is REUSE
  - Otheryn PR 23 merged as 68c4f39f7b1b45f880543c258627b4ccf73dbc86 after exact-head ready gates passed
  - Universal Agent E2E 136 passed exact final-target runtime proof with Required physical E2E success
  - temporary controlled-server pin is absent from final governance scope
  - live Canary main 9382d1f5320e8ee465b4e813c4b85cd028feeb9f has no OAM-007 governance-path overlap
derived:
  - only item-definitions required target code adaptation
  - legacy-only map runtime divergence is insufficient migration authorization
  - focused behavior proof and physical runtime smoke are complementary
unknown:
  - final Canary feature-governance merge SHA
  - final Canary lifecycle merge SHA
conflicts: []
first_failure:
  marker: none active
  evidence: target delivery, exact final-target runtime proof and final live-main overlap check are complete
rejected_hypotheses:
  - legacy Canary is the target image
  - every Map Tile or MapCache difference must be ported
  - the unrelated manual healing-rune part of PR 81 belongs in OAM-007
  - physical login/relog alone proves occupied-tile magic-field damage
  - downstream world modules belong in OAM-007
changed_paths:
  - docs/agents/tasks/active/CAN-20260717-oteryn-item-world-runtime-revalidation.md
  - docs/agents/OTERYN_OAM_007_ITEM_WORLD_RUNTIME_REVALIDATION.md
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
validation:
  - command: exact canonical blob matrix and legacy-delta provenance review
    result: PASS
    evidence: one required item-definition adaptation isolated; other legacy deltas failed the adaptation gate
  - command: Otheryn PR 23 ready CI 84 and Required 81
    result: PASS
    evidence: exact head cd6fae153ebe495ec9030c9c729f2ceef06872ef; merge 68c4f39f7b1b45f880543c258627b4ccf73dbc86
  - command: Universal Agent E2E 136 / Required physical E2E
    result: PASS
    evidence: exact Otheryn 68c4f39f7b1b45f880543c258627b4ccf73dbc86 plus OTClient 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f passed login/relog and persistence checks
  - command: live-main overlap through 9382d1f5320e8ee465b4e813c4b85cd028feeb9f
    result: PASS
    evidence: intervening security-only drift does not touch OAM-007 report, task or program
blockers: []
next_action: Pass exact-head draft ownership/CI, mark PR 455 ready, require ready-triggered final-head gates, squash-merge, then archive in a separate lifecycle-only PR.
```
