---
task_id: CAN-20260716-oteryn-persistence-foundation-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: "OAM-004"
status: blocked
agent: oteryn-architecture-migration-agent
branch: docs/oam-004-persistence-foundation-revalidation
base_branch: main
created: 2026-07-16T10:20:00+02:00
updated: 2026-07-16T10:20:00+02:00
last_verified_commit: "63e45afe684e5f923bc004a59687a5adcaac6f01"
risk: high
related_issue: ""
related_pr: ""
depends_on:
  - OAM-003
blocks:
  - OAM-005
  - OAM-006
  - OAM-007
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260716-oteryn-persistence-foundation-revalidation.md
    - docs/agents/OTERYN_OAM_004_PERSISTENCE_FOUNDATION_REVALIDATION.md
  shared:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
  read_only:
    - docs/architecture/oteryn-target-server-architecture.md
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/real-tibia/registry/modules/database-connection.yaml
    - docs/agents/real-tibia/registry/modules/database-migrations.yaml
    - docs/agents/real-tibia/registry/modules/player-persistence.yaml
    - docs/agents/real-tibia/registry/modules/world-persistence.yaml
    - docs/agents/real-tibia/TSD_002B_PERSISTENCE_TRANSACTIONS_REPORT.md
    - blakinio/Otheryn@a9c7fabc9f4b9bbeca9fed4ab73c36309cd04e2d
    - blakinio/canary@63e45afe684e5f923bc004a59687a5adcaac6f01
    - opentibiabr/canary@a879c9312e34381e8eedf397b8ed44510698b689
modules_touched:
  - database-connection
  - database-migrations
  - player-persistence
  - world-persistence
reuses:
  - docs/agents/real-tibia/TSD_002B_PERSISTENCE_TRANSACTIONS_REPORT.md
  - docs/agents/BUILD_TEST_MATRIX.md
  - docs/agents/KNOWN_RISKS.md
  - docs/agents/MODULE_CATALOG.md
public_interfaces:
  - OAM-004 persistence foundation migration dispositions
cross_repo_tasks: []
---

# Goal

Revalidate the four canonical Oteryn database/persistence foundation modules against exact target, legacy and upstream baselines; prove or reject transaction, migration, save/load and restart/crash assumptions; assign evidence-backed dispositions; and split any required target adaptation into bounded follow-up work before OAM-005 begins.

# Acceptance criteria

- [x] OAM-003 feature and lifecycle completed before OAM-004 start.
- [x] Exact OAM-004 Canary/legacy task-start SHA pinned.
- [x] Exact OAM-004 Otheryn target task-start SHA pinned.
- [x] Exact then-current upstream Canary evidence SHA pinned.
- [x] Four canonical module records pinned and refreshed as task inputs.
- [x] Live open PR/target overlap checked; no direct OAM-004 ownership conflict found.
- [ ] TSD persistence/transactions evidence refreshed against exact OAM-004 baselines.
- [ ] Target/legacy/upstream persistence implementation differences inventoried semantically.
- [ ] Transaction capability separated from proven atomicity, retry safety and rollback completeness.
- [ ] Migration ordering separated from reversibility, partial-failure recovery and deployment safety.
- [ ] Player save/load boundaries and restart/crash evidence classified.
- [ ] World save orchestration and cross-domain consistency evidence classified.
- [ ] Each canonical module receives one evidence-backed disposition.
- [ ] Any required target source change is split into a separate bounded Otheryn task/PR before implementation.
- [ ] OAM program queue/handoff updated from the proven OAM-004 result.
- [ ] Current-head Canary PR ownership/CI/review gates verified.
- [ ] Autonomous merge gate satisfied.

# PROVEN

- OAM-003 lifecycle completed as `blakinio/canary@63e45afe684e5f923bc004a59687a5adcaac6f01`.
- OAM-004 target task-start baseline: `blakinio/Otheryn@a9c7fabc9f4b9bbeca9fed4ab73c36309cd04e2d`.
- OAM-004 upstream evidence baseline: `opentibiabr/canary@a879c9312e34381e8eedf397b8ed44510698b689`.
- OAM-004 legacy/governance task-start baseline: `blakinio/canary@63e45afe684e5f923bc004a59687a5adcaac6f01`.
- Canonical modules are exactly `database-connection`, `database-migrations`, `player-persistence`, `world-persistence`.
- `database-connection` explicitly excludes transaction isolation/retry-safety/rollback-completeness proof.
- `database-migrations` explicitly excludes reversibility, rollback proof and partial-failure recovery.
- `world-persistence` explicitly excludes cross-domain atomicity, crash consistency, restart/reload safety and reconciliation.
- `player-persistence` is mapped broadly across `src/io/**`, `src/database/**` and player state and cannot be inferred reusable from path inventory alone.
- Live Canary open PRs #419, #415 and #316 are OTBM/CI work and do not claim the four OAM-004 canonical persistence records.
- Otheryn had no open PR at OAM-004 start.
- No existing OAM-004 branch or PR was found before this task was created.

# DERIVED

- OAM-004 must distinguish low-level DB transaction capability from correctness of higher-level save transactions.
- No database or persistence module may be marked `REUSE` solely because target began from upstream or because CI starts the server successfully.
- OAM-005 remains blocked until OAM-004 dispositions and any required bounded target adaptation dependencies are recorded.

# UNKNOWN

- Exact target/legacy/upstream differences for database core, migrations and serializers at the pinned baselines.
- Whether reconnect/retry behavior is transaction-safe.
- Whether migration failure can leave a partially advanced schema/version state.
- Whether player save/load is transactionally complete across all owned tables/state.
- Whether world/guild/house/KV/player save orchestration is crash-consistent or requires target adaptation.
- Whether OAM-004 requires any target source change after revalidation.

# CONFLICT

- None proven at task start.

# Ownership and overlap check

- Canary open PR #419: OTBM map quality gate; read-only to OAM-004.
- Canary open PR #415: incremental CI/final-head gate; shared CI infrastructure only and not OAM-004 source ownership.
- Canary open PR #316: Targuna donor evidence; read-only to OAM-004.
- Otheryn open PRs: none at task start.
- No existing OAM-004 PR/branch detected.

# Plan

1. Refresh TSD persistence/transaction evidence and targeted shared-index risk/test entries.
2. Compare exact target/upstream/legacy DB core, migration manager/schema and persistence orchestration paths.
3. Classify transaction, retry, migration-failure, restart/crash and rollback boundaries.
4. Assign evidence-backed dispositions for all four canonical modules.
5. If adaptation is required, create a separate bounded target issue/branch/draft PR before target source changes.
6. Update program state and merge governance only after exact-head gates.

# Validation and CI

| Commit/ref | Check | Result |
|---|---|---|
| `63e45afe684e5f923bc004a59687a5adcaac6f01` | Canary/legacy OAM-004 task-start SHA | PASS |
| `a9c7fabc9f4b9bbeca9fed4ab73c36309cd04e2d` | Otheryn OAM-004 task-start SHA | PASS |
| `a879c9312e34381e8eedf397b8ed44510698b689` | upstream OAM-004 evidence SHA | PASS |

# Risks and compatibility

- Runtime: persistence changes can cause data loss/corruption; no target mutation before evidence-backed bounded scope.
- Data/migration: highest-risk boundary in this package; migration execution against production/real data is out of scope.
- Protocol/client: no direct contract change expected.
- Security/privacy: database credentials and sensitive player state must not be exposed in evidence artifacts.
- Rollback: every future target persistence change must define schema/data rollback or an explicit irreversible migration gate.

# Remaining work

1. Refresh the exact persistence/transactions evidence matrix and assign module dispositions before any target source change.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T10:20:00+02:00
head: 63e45afe684e5f923bc004a59687a5adcaac6f01
branch: docs/oam-004-persistence-foundation-revalidation
pr: none
status: blocked
context_routes:
  - agent-governance
  - database-persistence
owned_paths:
  - docs/agents/tasks/active/CAN-20260716-oteryn-persistence-foundation-revalidation.md
  - docs/agents/OTERYN_OAM_004_PERSISTENCE_FOUNDATION_REVALIDATION.md
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
proven:
  - OAM-003 lifecycle is complete
  - target task-start is a9c7fabc9f4b9bbeca9fed4ab73c36309cd04e2d
  - legacy task-start is 63e45afe684e5f923bc004a59687a5adcaac6f01
  - upstream evidence baseline is a879c9312e34381e8eedf397b8ed44510698b689
  - canonical modules are database-connection database-migrations player-persistence world-persistence
derived:
  - transaction capability is not transaction correctness
  - OAM-005 remains blocked pending OAM-004 evidence and adaptation dependencies
unknown:
  - module dispositions
  - exact transaction retry rollback and crash-consistency behavior
  - whether bounded target adaptation is required
conflicts: []
first_failure:
  marker: OAM-004 evidence matrix incomplete
  evidence: canonical records explicitly leave persistence atomicity rollback and crash safety unassessed
rejected_hypotheses:
  - upstream baseline presence proves persistence correctness
  - DBTransaction call sites prove cross-domain atomicity
changed_paths:
  - docs/agents/tasks/active/CAN-20260716-oteryn-persistence-foundation-revalidation.md
  - docs/agents/OTERYN_OAM_004_PERSISTENCE_FOUNDATION_REVALIDATION.md
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
validation:
  - command: live repository and canonical-record preflight
    result: PASS
    evidence: exact pinned task-start SHAs and four canonical records
blockers:
  - persistence/transaction evidence revalidation incomplete
next_action: Refresh TSD_002B persistence/transaction evidence against the pinned OAM-004 baselines and classify transaction, migration, player and world persistence boundaries.
```

# Completion

- Final status: blocked pending evidence revalidation
- Canary feature PR: pending
- Target implementation PR: none
- Program record updated: pending
- Catalogue updated: not applicable
- Changelog updated: not applicable
- Archived at: not archived
