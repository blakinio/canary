---
task_id: CAN-20260716-oteryn-persistence-foundation-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: "OAM-004"
status: blocked
agent: oteryn-architecture-migration-agent
branch: docs/oam-004-persistence-foundation-revalidation
base_branch: main
created: 2026-07-16T10:20:00+02:00
updated: 2026-07-16T10:46:00+02:00
last_verified_commit: "63e45afe684e5f923bc004a59687a5adcaac6f01"
risk: high
related_issue: ""
related_pr: "420"
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
cross_repo_tasks:
  - blakinio/Otheryn#7
  - blakinio/Otheryn#8
  - blakinio/Otheryn#9
  - blakinio/Otheryn#10
  - blakinio/Otheryn#11
---

# Goal

Revalidate the four canonical Oteryn database/persistence foundation modules against exact target, legacy and upstream baselines; prove or reject transaction, migration, save/load and restart/crash assumptions; assign evidence-backed dispositions; deliver bounded target adaptations required by those dispositions; and stop before OAM-005.

# Acceptance criteria

- [x] OAM-003 feature and lifecycle completed before OAM-004 start.
- [x] Exact OAM-004 Canary/legacy task-start SHA pinned.
- [x] Exact OAM-004 Otheryn target task-start SHA pinned.
- [x] Exact then-current upstream Canary evidence SHA pinned.
- [x] Four canonical module records pinned and refreshed as task inputs.
- [x] Live open PR/target overlap checked; no direct OAM-004 ownership conflict found.
- [x] TSD persistence/transactions evidence refreshed against exact OAM-004 baselines.
- [x] Target/legacy/upstream persistence implementation differences inventoried semantically for the bounded DB/migration/player/world scope.
- [x] Transaction capability separated from atomicity, retry safety and rollback completeness.
- [x] Migration ordering separated from reversibility, partial-failure recovery and deployment safety.
- [x] Player save/load transaction and failure-propagation boundaries classified.
- [x] World save orchestration and cross-domain consistency boundaries classified.
- [x] Each canonical module receives one evidence-backed disposition.
- [x] Required target adaptations split into separate bounded Otheryn issues before relevant source changes.
- [ ] OAM-004A target PR #11 exact-head full ready-cycle gates verified and merged or retained as an explicit blocker.
- [ ] OAM-004B/C/D implemented and validated in dependency order or explicitly retained as blockers.
- [ ] OAM program queue/handoff updated from final OAM-004 result.
- [ ] Current-head Canary PR #420 ownership/CI/review gates verified.
- [ ] Canary feature PR #420 merged and lifecycle archived separately.

# PROVEN

- OAM-003 lifecycle completed as `blakinio/canary@63e45afe684e5f923bc004a59687a5adcaac6f01`.
- OAM-004 target task-start baseline: `blakinio/Otheryn@a9c7fabc9f4b9bbeca9fed4ab73c36309cd04e2d`.
- OAM-004 upstream evidence baseline: `opentibiabr/canary@a879c9312e34381e8eedf397b8ed44510698b689`.
- OAM-004 legacy/governance task-start baseline: `blakinio/canary@63e45afe684e5f923bc004a59687a5adcaac6f01`.
- Canonical modules are exactly `database-connection`, `database-migrations`, `player-persistence`, `world-persistence`.
- Final OAM-004 dispositions are currently:
  - `database-connection` → `ADAPT`;
  - `database-migrations` → `ADAPT`;
  - `player-persistence` → `ADAPT`;
  - `world-persistence` → `ADAPT`.
- Target/upstream DB core enabled MySQL automatic reconnect, retried/resubmitted failed statements, acquired the long-lived transaction lock only after `BEGIN`, and committed the generic transaction after a callback returned `false`.
- MySQL automatic reconnect can reset connection/session state and roll back an active server-side transaction, so silent reconnect/replay is incompatible with a fail-closed local transaction contract.
- Legacy has the same generic transaction callback-false semantics and is not a ready DB-core fix source.
- Target/upstream and legacy migration managers continue after failed migration load/runtime steps and can advance `db_version` through later successfully-called migrations; generic reversibility is not proven.
- `IOLoginData::savePlayer()` has a broad outer transaction and converts many boolean failures to exceptions/rollback, but some sub-save calls do not expose a uniform failure result and the whole player transaction inherits DB-core reconnect/retry semantics.
- `IOMapSerialize::saveHouseItems()` uses the generic transaction helper while its guard returns `false` on failure; at task-start semantics that false path can commit a preceding house-item delete.
- Legacy has the same house-save transaction/helper behavior.
- `IOGuild::saveGuild()` returns `void` and ignores the DB update result.
- `SaveManager::saveAll()` returns `void`, logs failures and continues across domains without an aggregate success result; `scheduleAll()` can run the save as a detached task.
- Bounded target issues created before relevant source mutations:
  - OAM-004A #7 database transaction integrity;
  - OAM-004B #8 fail-closed migration chain;
  - OAM-004C #9 world save rollback/result propagation;
  - OAM-004D #10 player failure-propagation audit.
- OAM-004A implementation PR #11 was opened before DB-core source changes.
- OAM-004A final candidate head `420e23b33a6a39e2e379ee045b0fd5f764984f77` changes exactly the OAM-004A architecture note plus `src/database/database.cpp` and `.hpp`; temporary patch tooling was removed from the final diff.
- OAM-004A disables auto-reconnect and arbitrary SQL resend, locks before `BEGIN`, rolls back callback `false`, and restores local transaction state on failed begin.
- OAM-004A draft-cycle CI/Required passed; full ready-cycle CI #26 / Required #23 is in progress and is the merge gate.

# DERIVED

- No OAM-004 module qualifies for unconditional `REUSE` at the pinned task-start baseline.
- OAM-004A must merge before OAM-004B/C/D source work starts, because all three depend on the final DB transaction contract.
- OAM-005 remains blocked until OAM-004 feature and lifecycle completion.
- Persistence correctness must remain domain-owned; OAM-004C must not invent one giant transaction across players, guilds, houses and KV.

# UNKNOWN

- Final exact-head OAM-004A full CI/Required result.
- Exact OAM-004B migration result contract and focused test implementation.
- Exact OAM-004C aggregate save-result API shape after OAM-004A lands.
- Exact OAM-004D list of player sub-save operations requiring explicit failure propagation.
- Complete crash/restart recovery semantics for untouched persistence paths.

# CONFLICT

- None between OAM-004 ownership and live open PRs at task start.

# Ownership and overlap check

- Canary open PR #419: OTBM map quality gate; read-only to OAM-004.
- Canary open PR #415: CI/final-head infrastructure; not persistence source ownership.
- Canary open PR #316: Targuna donor evidence; read-only to OAM-004.
- Otheryn had no open PR at OAM-004 start.
- OAM-004 target work is isolated into issues #7–#10; only PR #11 is active source work at this checkpoint.
- No protocol/client or static map migration path is claimed.

# Decisions

| Decision | Reason/evidence |
|---|---|
| `database-connection` → `ADAPT` | silent reconnect/replay plus callback-false commit and BEGIN-lock window violate fail-closed transaction semantics |
| `database-migrations` → `ADAPT` | chain can continue and advance version after earlier migration failure; semantic result not enforced |
| `player-persistence` → `ADAPT` | valuable broad transaction exists, but failure propagation is not uniform and DB-core contract was unsafe |
| `world-persistence` → `ADAPT` | known house rollback bug plus unobservable guild/global save failures |
| Split A/B/C/D | prevents one high-risk persistence refactor and preserves exact dependency/rollback boundaries |
| Do not start OAM-005 | OAM-004 adaptations and lifecycle must complete first |

# Validation and CI

| Commit/ref | Check | Result |
|---|---|---|
| `63e45afe684e5f923bc004a59687a5adcaac6f01` | Canary/legacy OAM-004 task-start SHA | PASS |
| `a9c7fabc9f4b9bbeca9fed4ab73c36309cd04e2d` | Otheryn OAM-004 task-start SHA | PASS |
| `a879c9312e34381e8eedf397b8ed44510698b689` | upstream OAM-004 evidence SHA | PASS |
| OAM-004A PR #11 head `420e23b33a6a39e2e379ee045b0fd5f764984f77` | draft-cycle CI #25 / Required #22 | PASS; not full merge evidence |
| OAM-004A PR #11 ready-cycle | full CI #26 / Required #23 | IN PROGRESS |

# Failed approaches and rejected hypotheses

- GitHub code search returned no results for known DB symbols in some queries; negative search results were rejected as absence proof.
- TSD-002B inventory was not treated as ACID/retry/crash proof.
- Upstream inheritance was rejected as automatic persistence correctness.
- Legacy was inspected for candidate fixes but contains the same migration, transaction-helper and house-save failures for the relevant slices.
- Global `DBTransaction` semantics were not changed before a bounded target PR existed.
- OAM-004B/C/D source work was not started before the final OAM-004A dependency contract.

# Risks and compatibility

- Runtime: persistence changes can cause data loss/corruption; every target slice requires exact-head DB/runtime gates.
- Data/migration: no production/user DB access and no destructive migration execution.
- Protocol/client: no direct contract change.
- Security/privacy: no credentials or sensitive player data in evidence artifacts.
- Rollback: schema/data rollback must be explicit per future migration; generic DDL rollback is not claimed.
- Concurrency: one shared MYSQL handle and transaction lock ordering is a material OAM-004A concern.

# Remaining work

1. Complete exact-head ready-cycle validation and merge decision for Otheryn PR #11; only after merge re-pin the target head and start OAM-004B in dependency order.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T10:46:00+02:00
head: 63e45afe684e5f923bc004a59687a5adcaac6f01
branch: docs/oam-004-persistence-foundation-revalidation
pr: 420
status: blocked
context_routes:
  - agent-governance
  - database-persistence
owned_paths:
  - docs/agents/tasks/active/CAN-20260716-oteryn-persistence-foundation-revalidation.md
  - docs/agents/OTERYN_OAM_004_PERSISTENCE_FOUNDATION_REVALIDATION.md
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
proven:
  - all four OAM-004 modules are ADAPT
  - OAM-004A issue 7 and PR 11 exist for fail-closed DB transaction semantics
  - OAM-004B issue 8 owns fail-closed migration chain
  - OAM-004C issue 9 owns world save rollback and result propagation
  - OAM-004D issue 10 owns player save failure propagation audit
  - OAM-004A final candidate head is 420e23b33a6a39e2e379ee045b0fd5f764984f77
derived:
  - OAM-004B C and D depend on the final OAM-004A transaction contract
  - OAM-005 remains blocked until OAM-004 governance and lifecycle complete
unknown:
  - final OAM-004A ready-cycle result and merge SHA
  - final B C D implementation results
  - complete crash restart recovery semantics for untouched persistence paths
conflicts: []
first_failure:
  marker: OAM-004A exact-head target validation incomplete
  evidence: ready-cycle CI 26 and Required 23 are still running
rejected_hypotheses:
  - upstream inheritance proves persistence correctness
  - DBTransaction presence proves rollback completeness
  - legacy contains ready persistence fixes for the proven failures
changed_paths:
  - docs/agents/tasks/active/CAN-20260716-oteryn-persistence-foundation-revalidation.md
  - docs/agents/OTERYN_OAM_004_PERSISTENCE_FOUNDATION_REVALIDATION.md
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
validation:
  - command: semantic persistence cross-source review
    result: PASS
    evidence: durable OAM-004 report
  - command: OAM-004A draft-cycle CI and Required
    result: PASS
    evidence: CI 25 and Required 22 on 420e23b33a6a39e2e379ee045b0fd5f764984f77; full ready-cycle remains merge gate
blockers:
  - OAM-004A full ready-cycle exact-head validation
next_action: Verify full exact-head CI 26 and Required 23 for Otheryn PR 11; if green and review state is clean, squash-merge OAM-004A before starting OAM-004B.
```

# Completion

- Final status: blocked on OAM-004A target gate
- Canary feature PR: #420
- Target issues: #7, #8, #9, #10
- Active target implementation PR: #11
- Program record updated: pending final OAM-004 chain result
- Catalogue updated: not applicable
- Changelog updated: not applicable
- Archived at: not archived
