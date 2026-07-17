---
task_id: CAN-20260717-oteryn-vocations-migration
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: "OAM-008"
status: completed
agent: oteryn-architecture-migration-agent
branch: docs/oam-008-vocations-migration
base_branch: main
created: 2026-07-17T10:10:00+02:00
updated: 2026-07-17T08:53:06Z
last_verified_commit: "acdddd924fed170da51a8a54114607842f0cbb68"
risk: low
related_issue: "24"
related_pr: "469"
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
    - blakinio/Otheryn@f59a58426b4d3910ba0cdc0d2332c24f31a1db4f
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
completed: 2026-07-17T08:53:06Z
---

# Final disposition

`vocations` → `REUSE`.

The exact canonical implementation/data was already present in the target, so OAM-008 migrated the module by accepting that target implementation after exact provenance, focused tests and full target compatibility gates. The target merge adds proof only, not vocation behavior changes.

# Scope

- `vocation.cpp`, `vocation.hpp` and `vocations.xml` remain unchanged.
- Otheryn PR #25 adds only focused target tests and unit-test registration.
- Combat, spells, weapons, Wheel, persistence, protocol/client and every other canonical module remain out of scope.
- OAM-009 remains separate for physical-client E2E.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T10:38:00+02:00
head: 9d4300e79dc59180e6c352776bf38d6c96798493
branch: docs/oam-008-vocations-migration
pr: 469
status: ready
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
  - final disposition is REUSE
  - Otheryn PR 25 final head is 9453a1754501ce183e20d294df1064a5ccbad54c
  - Otheryn CI 88 Required 84 and autofix 77 passed
  - Linux debug Run Tests passed
  - both focused VocationsTest cases were executed and passed as CTest cases 78 and 79 of 325
  - Otheryn PR 25 had zero comments reviews and unresolved review threads at final merge gate
  - Otheryn PR 25 squash-merged as f59a58426b4d3910ba0cdc0d2332c24f31a1db4f
  - Canary governance PR is 469
derived:
  - exact blob identity plus focused target proof and full compatibility gates satisfy the bounded REUSE acceptance rule
  - target delivery is test-only because implementation transfer was unnecessary
  - OAM-009 remains the separate physical-client proof boundary
unknown:
  - final Canary feature-governance merge SHA
  - final Canary lifecycle merge SHA
conflicts: []
first_failure:
  marker: none active
  evidence: the earlier scope-skipped CI 86 was rejected as focused proof; full exact-head CI 88 supplied the required real test execution
rejected_hypotheses:
  - exact blob identity alone authorizes REUSE
  - green aggregate CI with skipped tests proves focused vocation behavior
  - world-zones legacy cache divergence should be copied into the cleaner target
  - instances is a low-risk first migration slice
  - OAM-009 physical-client proof belongs inside OAM-008
changed_paths:
  - docs/agents/tasks/active/CAN-20260717-oteryn-vocations-migration.md
  - docs/agents/OTERYN_OAM_008_VOCATIONS_MIGRATION.md
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
validation:
  - command: exact canonical vocations blob matrix
    result: PASS
    evidence: all three canonical paths are identical across target legacy and upstream
  - command: live open PR overlap audit
    result: PASS
    evidence: no open Canary PR touches canonical vocation paths; no open Otheryn PR existed before PR 25
  - command: Otheryn draft CI 86 and Required 82
    result: FAIL
    evidence: aggregate was green but C++ build and focused test jobs were skipped; this run was not accepted as focused proof
  - command: Otheryn exact-head CI 88 Required 84 and autofix 77
    result: PASS
    evidence: exact head 9453a1754501ce183e20d294df1064a5ccbad54c completed the full matrix and Linux debug Run Tests
  - command: focused vocation CTest artifact review
    result: PASS
    evidence: both VocationsTest cases executed and passed as tests 78 and 79 of 325
blockers: []
next_action: Update the shared Oteryn migration program with OAM-008 REUSE and final target merge, then pass Canary PR 469 exact-head draft and ready ownership/CI/review gates, squash-merge, and archive OAM-008 in a separate lifecycle-only PR. Keep OAM-009 blocked until lifecycle completion.
```

## Automated lifecycle completion

- Feature PR: #469.
- Feature head: `c5c53dcbacabe48c08ebaf70f0a0622f70784aa6`.
- Merge commit: `acdddd924fed170da51a8a54114607842f0cbb68`.
- Merged at: `2026-07-17T08:53:06Z`.
- This record was moved from `tasks/active` by the post-merge lifecycle automation.
