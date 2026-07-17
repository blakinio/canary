---
task_id: CAN-20260717-oteryn-vocations-migration
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: "OAM-008"
status: implementing
agent: oteryn-architecture-migration-agent
branch: docs/oam-008-vocations-migration
base_branch: main
created: 2026-07-17T10:10:00+02:00
updated: 2026-07-17T10:10:00+02:00
last_verified_commit: "317c1c4235377c388883aa2fd425d324f8ce4d2e"
risk: low
related_issue: "24"
related_pr: "pending"
depends_on:
  - OAM-007
blocks:
  - OAM-009
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260717-oteryn-vocations-migration.md
    - docs/agents/OTERYN_OAM_008_VOCATIONS_MIGRATION.md
  shared:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
  read_only:
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/real-tibia/registry/modules/vocations.yaml
    - docs/agents/real-tibia/generated/MODULE_DEPENDENCIES.md
    - src/creatures/players/vocations/vocation.cpp
    - src/creatures/players/vocations/vocation.hpp
    - data/XML/vocations.xml
    - blakinio/canary@317c1c4235377c388883aa2fd425d324f8ce4d2e
    - blakinio/Otheryn@68c4f39f7b1b45f880543c258627b4ccf73dbc86
    - opentibiabr/canary@e0ac98e399d0f7e483f3668f57b78fcc45b6e53f
modules_touched:
  - vocations
reuses:
  - docs/agents/OTERYN_OAM_003_ENGINE_FOUNDATION_REVALIDATION.md
  - docs/agents/OTERYN_OAM_004_PERSISTENCE_FOUNDATION_REVALIDATION.md
  - docs/agents/OTERYN_OAM_005_ACCOUNT_CHARACTER_LIFECYCLE_REVALIDATION.md
  - docs/agents/OTERYN_OAM_006_NETWORK_LOGIN_PROTOCOL_REVALIDATION.md
  - docs/agents/OTERYN_OAM_007_ITEM_WORLD_RUNTIME_REVALIDATION.md
public_interfaces:
  - vocation registry lookup and reload
  - promotion relation lookup
  - vocation growth and regeneration configuration
cross_repo_tasks:
  - blakinio/Otheryn#24
  - blakinio/Otheryn#25
---

# Goal

Migrate exactly the canonical `vocations` module as the first evidence-selected low-risk Oteryn module package, with `REUSE` as the working disposition and proof-only target changes.

# Scope

- Keep `vocation.cpp`, `vocation.hpp` and `vocations.xml` unchanged.
- Prove exact target/legacy/upstream identity.
- Add focused target tests for registry lookup and promotion semantics.
- Do not include combat, spells, weapons, Wheel, persistence, protocol/client or another canonical module.
- Keep OAM-009 separate for physical-client E2E.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T10:10:00+02:00
head: 1bc2cda302d1732ebb7d953e8cede7b5e83d6eb3
branch: docs/oam-008-vocations-migration
pr: pending
status: implementing
context_routes:
  - agent-governance
  - vocations
owned_paths:
  - docs/agents/tasks/active/CAN-20260717-oteryn-vocations-migration.md
  - docs/agents/OTERYN_OAM_008_VOCATIONS_MIGRATION.md
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
proven:
  - OAM-007 feature and lifecycle are complete
  - Canary task-start is 317c1c4235377c388883aa2fd425d324f8ce4d2e
  - Otheryn task-start is 68c4f39f7b1b45f880543c258627b4ccf73dbc86
  - upstream evidence head is e0ac98e399d0f7e483f3668f57b78fcc45b6e53f
  - vocations has no canonical depends_on dependencies
  - vocation.cpp, vocation.hpp and vocations.xml are exact-blob identical across target legacy and upstream
  - no open Canary PR overlaps canonical vocation paths
  - no open Otheryn PR existed at task-start
  - Otheryn issue 24 and proof-only PR 25 were created
derived:
  - vocations is the strongest current low-risk first-module candidate
  - implementation transfer is unnecessary because target already contains exact canonical content
  - focused target proof is still required before REUSE can be finalized
unknown:
  - Otheryn PR 25 exact-head test and CI result
  - final Otheryn PR 25 merge SHA
  - final Canary feature-governance merge SHA
  - final Canary lifecycle merge SHA
conflicts: []
first_failure:
  marker: none active
  evidence: target draft CI has not completed yet
rejected_hypotheses:
  - exact blob identity alone authorizes REUSE
  - world-zones legacy cache divergence should be copied into the cleaner target
  - instances is a low-risk first migration slice
  - OAM-009 physical-client proof belongs inside OAM-008
changed_paths:
  - docs/agents/tasks/active/CAN-20260717-oteryn-vocations-migration.md
  - docs/agents/OTERYN_OAM_008_VOCATIONS_MIGRATION.md
validation:
  - command: exact canonical vocations blob matrix
    result: PASS
    evidence: all three canonical paths are identical across target legacy and upstream
  - command: live open PR overlap audit
    result: PASS
    evidence: no open Canary PR touches canonical vocation paths; no open Otheryn PR existed before PR 25
blockers: []
next_action: Require Otheryn PR 25 focused tests and exact-head draft/ready CI, then finalize the REUSE disposition and Canary governance package. Keep OAM-009 blocked until OAM-008 feature and lifecycle complete.
```
