---
task_id: CAN-20260716-oteryn-engine-foundation-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: "OAM-003"
status: planned
agent: oteryn-architecture-migration-agent
branch: docs/oam-003-engine-foundation-revalidation
base_branch: main
created: 2026-07-16T08:53:00+02:00
updated: 2026-07-16T08:53:00+02:00
last_verified_commit: "c32e42469f302ab108dea08d9b90164458696328"
risk: high
related_issue: ""
related_pr: ""
depends_on:
  - OAM-002
blocks:
  - OAM-004
  - OAM-006
  - OAM-007
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260716-oteryn-engine-foundation-revalidation.md
    - docs/agents/OTERYN_OAM_003_ENGINE_FOUNDATION_REVALIDATION.md
  shared:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
  read_only:
    - docs/architecture/oteryn-target-server-architecture.md
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/real-tibia/registry/modules/build-system.yaml
    - docs/agents/real-tibia/registry/modules/configuration.yaml
    - docs/agents/real-tibia/registry/modules/engine-runtime-lifecycle.yaml
    - docs/agents/real-tibia/registry/modules/engine-scheduler.yaml
    - docs/agents/real-tibia/registry/modules/engine-service-container.yaml
    - docs/agents/real-tibia/registry/modules/lua-runtime.yaml
    - docs/agents/real-tibia/registry/modules/lua-bindings.yaml
    - blakinio/Otheryn@3cc7c1dfea747bb380f3761ee7ff7ac30141a115
    - blakinio/canary@c32e42469f302ab108dea08d9b90164458696328
    - opentibiabr/canary@a879c9312e34381e8eedf397b8ed44510698b689
modules_touched:
  - build-system
  - configuration
  - engine-runtime-lifecycle
  - engine-scheduler
  - engine-service-container
  - lua-runtime
  - lua-bindings
reuses:
  - docs/architecture/oteryn-target-server-architecture.md
  - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
  - docs/agents/real-tibia/TSD_002A_ENGINE_FOUNDATION_REPORT.md
  - docs/agents/BUILD_TEST_MATRIX.md
  - docs/agents/MODULE_CATALOG.md
public_interfaces:
  - OAM-003 engine foundation migration dispositions
cross_repo_tasks: []
---

# Goal

Revalidate the seven canonical Oteryn engine-foundation modules against exact live target, legacy and upstream baselines; produce evidence-backed per-module migration dispositions and identify the minimum target implementation work, if any, without starting persistence or higher-level domain migration.

# Acceptance criteria

- [x] Exact OAM-003 task-start SHAs pinned for Canary, Otheryn and upstream Canary.
- [x] Seven canonical module records pinned and refreshed as task inputs.
- [ ] Target-relevant boundaries classified for every module as applicable, not-applicable or unresolved with evidence.
- [ ] Target/upstream/legacy source differences relevant to each module inventoried semantically, not by repository-wide bulk diff alone.
- [ ] Existing reusable foundation implementations/tests identified before proposing new abstractions.
- [ ] Each module receives one evidence-backed disposition: `REUSE`, `ADAPT`, `REVALIDATE`, `REWRITE`, `DO_NOT_MIGRATE` or `EXPERIMENTAL_ONLY`.
- [ ] Runtime-sensitive lifecycle/scheduler/Lua claims have controlled runtime evidence or remain explicitly unresolved.
- [ ] Any required Otheryn implementation is split into an explicitly linked bounded target task/PR before target source changes; no bulk legacy import.
- [ ] OAM program queue/handoff updated from the proven OAM-003 result.
- [ ] Current-head GitHub checks verified.
- [ ] Module catalogue/changelog impact handled or explicitly none.
- [ ] Cross-repository impact handled; no protocol/client contract is inferred without evidence.
- [ ] Autonomous merge gate satisfied.

# Confirmed context

PROVEN:

- OAM-002 lifecycle completed on `blakinio/canary@c32e42469f302ab108dea08d9b90164458696328`.
- OAM-003 target task-start baseline is `blakinio/Otheryn@3cc7c1dfea747bb380f3761ee7ff7ac30141a115`.
- OAM-003 upstream task-start baseline is `opentibiabr/canary@a879c9312e34381e8eedf397b8ed44510698b689`.
- OAM-003 legacy evidence baseline is `blakinio/canary@c32e42469f302ab108dea08d9b90164458696328`.
- Otheryn has no open PR at task start.
- Canary open PR #393 changes status-protocol load tooling, `src/server/network/protocol/protocolstatus.cpp`, catalogue/changelog and E2E paths; it does not claim the seven OAM-003 canonical foundation paths.
- Canary open PR #316 is OTBM/Targuna evidence work and does not claim the seven OAM-003 foundation paths.
- No `OAM-003` branch or repository search result existed before this task branch was created.
- The target baseline is pinned-upstream content except the two OAM-002 target CI/governance paths; therefore target runtime/foundation source begins OAM-003 from the pinned upstream implementation.
- Comparing pinned upstream `a879c931...` with legacy Canary `c32e4246...` shows the histories diverged: legacy is 726 commits ahead and 3 behind with merge base `e8237cef...`.
- Relevant visible legacy divergence already includes build/configuration surfaces such as `CMakeLists.txt`, `cmake/modules/BaseConfig.cmake`, `cmake/modules/CanaryLib.cmake` and `config.lua.dist`; this does not by itself authorize reuse.

DERIVED:

- OAM-003 must evaluate legacy foundation changes selectively; repository-wide legacy adoption is invalid.
- Because target foundation source currently matches pinned upstream, any stronger-than-`REUSE upstream` decision must be justified by specific legacy/donor evidence and target architecture fit.
- OAM-003 is evidence-first. Target source changes, if justified, require a linked bounded `blakinio/Otheryn` task/PR rather than edits from this Canary governance branch.

UNKNOWN:

- Which of the seven foundation modules can remain upstream-native without adaptation.
- Which legacy foundation deltas are still relevant, correct and architecturally compatible with Oteryn.
- Whether runtime/lifecycle/scheduler/Lua evidence is sufficient for dispositions stronger than `REVALIDATE`.

CONFLICT:

- The durable blueprint's status line still says implementation is blocked by the OAM-002 target identity gate, while OAM-002 is now completed. The blueprint remains authoritative for architecture content, but its status line is stale metadata and is not edited casually by OAM-003 unless required by a reviewed architecture-doc update.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| Oteryn target blueprint | architecture invariants and foundation target zones | `docs/architecture/oteryn-target-server-architecture.md` | Defines composition root, explicit lifecycle, scheduling, services and Lua adapter direction. |
| Oteryn architecture contract | package evidence/disposition gate | `docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md` | Governs exact SHA provenance, boundary classification and migration dispositions. |
| TSD engine foundation report | prior inventory evidence | `docs/agents/real-tibia/TSD_002A_ENGINE_FOUNDATION_REPORT.md` | Reuse inventory only; OAM-003 must refresh against live pinned SHAs. |
| DI service access | existing reusable DI surface | `src/lib/di/**`, catalogue entry | Reuse before proposing another service container. |
| Build/test matrix | validation selection | `docs/agents/BUILD_TEST_MATRIX.md` | Defines build/runtime validation expectations. |

# Ownership and overlap check

- Program record: `CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION` inspected after OAM-002 lifecycle merge.
- Open PRs inspected: Canary #393 and #316; Otheryn has none.
- Active OAM task/branch search: no pre-existing OAM-003 task or branch found.
- Ownership checker result: pending PR/CI validation.
- Exclusive claims: this task record and the OAM-003 revalidation report only.
- Shared claims: OAM program record only.
- Read-only dependencies: blueprint, architecture contract, seven canonical module records and pinned repository states.
- Overlaps: no proven path ownership conflict. PR #393 is runtime-adjacent but its concrete source edit is `ProtocolStatus`, outside the seven canonical foundation path records.
- Resolution: proceed evidence-first; do not edit target runtime source until per-module evidence justifies a linked target task.

# Current state

OAM-003 is active as a bounded engine-foundation revalidation package. No target implementation has started.

Canonical task modules:

```text
build-system
configuration
engine-runtime-lifecycle
engine-scheduler
engine-service-container
lua-runtime
lua-bindings
```

# Plan

1. Refresh the prior TSD engine-foundation inventory against the exact OAM-003 target/upstream/legacy SHAs and build a per-module evidence/disposition matrix.

# Work log

## 2026-07-16T08:53:00+02:00

- Changed: created OAM-003 task branch and bounded task record.
- Learned: target foundation source begins from pinned upstream; legacy history has substantial divergence and cannot be adopted wholesale.
- Failed/blocked: targeted GitHub code search did not reliably return shared-index/module hits, so the small authoritative shared indexes and exact canonical records were read directly after targeted searches returned no results.
- Result: OAM-003 evidence phase started; no target code changes.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Start OAM-003 as evidence-first governance work in `blakinio/canary`. | Canonical dispositions must be proven before target implementation; Canary is the governance/evidence repository. | none |
| Require a separate linked target task/PR for any Otheryn source changes. | Preserves repository-specific ownership and prevents bulk legacy migration. | none |
| Keep all seven modules `REVALIDATE` until OAM-003 evidence closes their boundaries. | Existing registry state is inventory-only and target architecture requires runtime proof for runtime-sensitive modules. | none |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `docs/agents/tasks/active/CAN-20260716-oteryn-engine-foundation-revalidation.md` | exclusive | authoritative OAM-003 checkpoint | active |
| `docs/agents/OTERYN_OAM_003_ENGINE_FOUNDATION_REVALIDATION.md` | exclusive | durable per-module evidence/disposition report | planned |
| `docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md` | shared | queue and handoff after proven result | pending |
| seven canonical module records | read_only | canonical identity/scope/dependencies | pinned inputs |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| `c32e42469f302ab108dea08d9b90164458696328` | live Canary main pin | PASS | GitHub commit search |
| `3cc7c1dfea747bb380f3761ee7ff7ac30141a115` | live Otheryn main pin | PASS | GitHub commit search |
| `a879c9312e34381e8eedf397b8ed44510698b689` | live upstream main pin | PASS | GitHub commit search |
| legacy vs upstream repository compare | GitHub compare | PASS as discovery evidence | diverged; 726 ahead / 3 behind; semantic module review still required |

Never write `passed` without verification on the stated commit.

# Failed approaches and dead ends

- Targeted GitHub repository code search returned no reliable hits for several exact canonical module IDs/shared-index terms; this negative result is not treated as proof of absence.
- Repository-wide compare is retained only as discovery evidence; its size and mixed scope make it invalid as a migration decision by itself.

# Risks and compatibility

- Runtime: lifecycle/scheduler/Lua modules require runtime proof before strong dispositions.
- Data/migration: no data migration in OAM-003.
- Security: Lua userdata lifetime remains an explicit known risk; no binding change is authorized from inventory alone.
- Backward compatibility: target currently matches pinned upstream runtime behavior; any adaptation must prove compatibility and rollback.
- Cross-repo rollout: no protocol/client coupling proven in current scope; cross-repo remains not-applicable unless evidence changes this.
- Rollback: governance/report changes are revertible; target source remains untouched until a separately reviewed target PR.

# Remaining work

1. Refresh the TSD engine-foundation inventory and write the per-module OAM-003 evidence/disposition matrix.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T08:53:00+02:00
head: c32e42469f302ab108dea08d9b90164458696328
branch: docs/oam-003-engine-foundation-revalidation
pr: none
status: investigating
context_routes:
  - agent-governance
  - cpp-runtime
owned_paths:
  - docs/agents/tasks/active/CAN-20260716-oteryn-engine-foundation-revalidation.md
  - docs/agents/OTERYN_OAM_003_ENGINE_FOUNDATION_REVALIDATION.md
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
proven:
  - OAM-002 lifecycle completed before OAM-003 start
  - Canary task-start SHA is c32e42469f302ab108dea08d9b90164458696328
  - Otheryn task-start SHA is 3cc7c1dfea747bb380f3761ee7ff7ac30141a115
  - upstream task-start SHA is a879c9312e34381e8eedf397b8ed44510698b689
  - target foundation source starts from pinned upstream content
  - no open Otheryn PR and no pre-existing OAM-003 branch were found
  - legacy Canary and upstream histories diverged substantially
derived:
  - legacy foundation changes require selective semantic review
  - target implementation, if required, needs a separate linked Otheryn task/PR
unknown:
  - per-module OAM-003 migration dispositions
  - sufficiency of runtime evidence for lifecycle scheduler and Lua boundaries
conflicts:
  - blueprint status metadata still references the completed OAM-002 gate
first_failure:
  marker: per-module evidence matrix not yet refreshed against exact OAM-003 SHAs
  evidence: canonical records remain inventory-only with runtime validation not assessed
rejected_hypotheses:
  - legacy Canary can be adopted wholesale because it is newer: histories diverged and the contract forbids bulk legacy import
changed_paths:
  - docs/agents/tasks/active/CAN-20260716-oteryn-engine-foundation-revalidation.md
validation:
  - command: live SHA and open-PR/branch verification
    result: PASS
    evidence: GitHub connector live state
  - command: legacy vs upstream compare
    result: PASS
    evidence: 726 ahead, 3 behind, merge base e8237cef...
blockers: []
next_action: Refresh TSD_002A engine-foundation evidence against the exact OAM-003 target, legacy and upstream SHAs and write the per-module evidence/disposition matrix.
```

# Handoff

## Start here

Read root `AGENTS.md`, repository/context routing docs, this checkpoint, live OAM-003 PR, Oteryn architecture blueprint/contract, OAM program record and the seven pinned canonical module records.

## Do not repeat

Do not rediscover OAM-002 target identity. For OAM-003 task start use exactly target `3cc7c1df...`, legacy `c32e4246...`, upstream `a879c931...` until a material head change requires explicit revalidation.

## Required reads

- `AGENTS.md`
- `docs/agents/REPOSITORY_MAP.md`
- `docs/agents/CONTEXT_ROUTING.md`
- `docs/architecture/oteryn-target-server-architecture.md`
- `docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md`
- `docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md`
- `docs/agents/real-tibia/TSD_002A_ENGINE_FOUNDATION_REPORT.md`
- seven canonical module records listed in frontmatter

## Open questions

- Which foundation modules are safe to keep upstream-native?
- Which legacy deltas are worth adapting to target architecture?
- Which runtime boundaries need new controlled evidence before OAM-003 can complete?

# Completion

- Final status: investigating
- PR: pending
- Merge commit: none
- Program record updated: pending
- Catalogue updated: not applicable yet
- Changelog updated: not applicable yet
- Archived at: not archived
