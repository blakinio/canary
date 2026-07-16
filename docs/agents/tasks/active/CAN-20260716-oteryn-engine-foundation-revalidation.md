---
task_id: CAN-20260716-oteryn-engine-foundation-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: "OAM-003"
status: blocked
agent: oteryn-architecture-migration-agent
branch: docs/oam-003-engine-foundation-revalidation
base_branch: main
created: 2026-07-16T08:53:00+02:00
updated: 2026-07-16T09:10:00+02:00
last_verified_commit: "875444d54056e06008050da66b92ff024763e18e"
risk: high
related_issue: ""
related_pr: "411"
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
    - zimbadev/crystalserver@fdd2b1f13f53894c584346ef3de43658045c42a7
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
cross_repo_tasks:
  - blakinio/Otheryn#4
  - blakinio/Otheryn#5
---

# Goal

Revalidate the seven canonical Oteryn engine-foundation modules against exact target, legacy, upstream and relevant donor baselines; produce evidence-backed dispositions; and split required target adaptation into bounded target work before any broader migration proceeds.

# Acceptance criteria

- [x] Exact OAM-003 task-start SHAs pinned for Canary, Otheryn and upstream Canary.
- [x] Relevant Crystal donor SHA pinned as comparison-only evidence.
- [x] Seven canonical module records pinned and refreshed as task inputs.
- [x] Target-relevant boundaries classified for every module.
- [x] Target/upstream/legacy/donor differences inventoried semantically for the bounded foundation scope.
- [x] Existing reusable foundation implementations/tests identified before proposing new abstractions.
- [x] Each module receives one evidence-backed disposition.
- [x] Runtime-sensitive claims use target bootstrap/runtime evidence where available; unresolved lifecycle/reload concerns produce `ADAPT`, not false `REUSE`.
- [x] Required target work split into linked bounded target artifacts before source changes: Otheryn PR #4 and issue #5.
- [ ] OAM-003A target PR #4 exact-head full ready-cycle CI/Required gates verified and merged or left as an explicit blocker.
- [ ] OAM program queue/handoff updated from the proven OAM-003 result and target follow-up dependencies.
- [ ] Current-head Canary PR #411 ownership/CI/review gates verified.
- [x] Module catalogue/changelog impact currently none; no new reusable platform or cross-cutting helper introduced by governance work.
- [x] Cross-repository impact handled; no protocol/client contract inferred.
- [ ] Autonomous merge gate satisfied.

# PROVEN

- OAM-002 lifecycle completed before OAM-003 start on `blakinio/canary@c32e42469f302ab108dea08d9b90164458696328`.
- OAM-003 target task-start baseline: `blakinio/Otheryn@3cc7c1dfea747bb380f3761ee7ff7ac30141a115`.
- OAM-003 upstream baseline: `opentibiabr/canary@a879c9312e34381e8eedf397b8ed44510698b689`.
- OAM-003 legacy baseline: `blakinio/canary@c32e42469f302ab108dea08d9b90164458696328`.
- Donor comparison baseline: `zimbadev/crystalserver@fdd2b1f13f53894c584346ef3de43658045c42a7`.
- Target foundation runtime/source begins from the pinned upstream content baseline; OAM-002 proved the only final target-vs-upstream differences are two CI/governance files.
- Legacy and upstream histories diverged: legacy 726 commits ahead and 3 behind with merge base `e8237cef...`; legacy is not a monotonic successor.
- Legacy scheduler uses the older `TaskGroup` model; Crystal donor also uses an older `TaskGroup` model.
- Upstream/target scheduler uses lane/WDRR/barrier-parallel policy with focused WDRR/policy tests and explicit compute-service/dispatcher/thread-pool shutdown ordering.
- Legacy and Crystal config use a plain `bool loaded`; upstream/target uses atomic load state plus deferred callbacks under a mutex.
- Legacy lifecycle includes multichannel cluster/Redis/handoff/leadership bootstrap explicitly excluded from initial Oteryn.
- Core DI files are materially identical between legacy and upstream; Crystal retains the same general static/contextual pattern and provides no cleaner composition root.
- Target/upstream and legacy Lua runtime plus typed shared-userdata foundation are materially identical; Crystal's pinned loader lacks the typed `LuaUserdataTraits` layer visible in target/upstream.
- OAM-003 dispositions are:
  - `build-system` → `REUSE`;
  - `configuration` → `ADAPT`;
  - `engine-runtime-lifecycle` → `ADAPT`;
  - `engine-scheduler` → `REUSE`;
  - `engine-service-container` → `ADAPT`;
  - `lua-runtime` → `ADAPT`;
  - `lua-bindings` → `ADAPT`.
- Otheryn PR #4 (`OAM-003A`) was opened before C++ source changes and implements the first minimal composition seam by constructing `CanaryServer` explicitly in `main()` from existing DI-provided dependencies.
- Otheryn issue #5 (`OAM-003B`) records the bounded Lua runtime/bindings adaptation and depends on OAM-003A.

# DERIVED

- No legacy or Crystal foundation module should replace the pinned upstream scheduler/build foundation.
- OAM-003A and OAM-003B are required convergence work resulting from `ADAPT` dispositions; they are not permission to bulk-refactor the target.
- OAM-004 must remain blocked until the program explicitly records the OAM-003 adaptation dependency state.

# UNKNOWN

- Whether Otheryn PR #4 passes the full ready-triggered build/runtime matrix on its exact current head.
- The exact implementation scope of OAM-003B beyond the issue's bounded lifecycle/adapter contract; it must be revalidated after OAM-003A lands.

# CONFLICT

- The durable blueprint status line still references the completed OAM-002 identity blocker. Architecture content remains authoritative; OAM-003 does not casually rewrite the blueprint for stale status metadata.

# Existing work to reuse

| Evidence/system | Reuse decision |
|---|---|
| Oteryn target blueprint | architecture invariants and target boundaries |
| Oteryn architecture contract | exact SHA/boundary/disposition gate |
| TSD engine foundation report | inventory only; refreshed by OAM-003 |
| upstream lane/WDRR scheduler | direct `REUSE` |
| upstream build foundation | direct `REUSE` |
| Boost.DI primitives/current bindings | substrate for `ADAPT`; no second DI container |
| typed Lua shared-userdata helpers | substrate for `ADAPT`; preserve ownership contract |
| OAM-002 target CI evidence | baseline runtime/build evidence |

# Ownership and overlap check

- Open Canary PRs at task start: #393 and #316; neither claimed the seven canonical OAM-003 foundation path records.
- Otheryn had no open PR at task start.
- No pre-existing OAM-003 branch/task was found before creation.
- Target implementation is isolated in Otheryn PR #4; OAM-003B is isolated as issue #5 and has no source branch yet.
- No protocol/client contract or persistence path is claimed.
- Ownership checker for Canary PR #411 remains pending exact-head validation.

# Decisions

| Decision | Reason/evidence |
|---|---|
| Keep target/upstream build system | already target baseline and validated; legacy build adds excluded multichannel-specific dependency/config surfaces |
| Keep upstream scheduler implementation | newer lane/WDRR model with focused tests; legacy/Crystal are older TaskGroup designs |
| Adapt lifecycle/config/DI ownership | current runtime still uses global/contextual access; blueprint requires explicit composition and lifecycle ownership |
| Adapt Lua runtime/bindings incrementally | typed ownership helpers are valuable, but reload lifecycle and domain adapter boundaries are not architecture-complete |
| Split target work | prevents one broad refactor and preserves evidence/rollback boundaries |

# Validation and CI

| Commit/ref | Check | Result |
|---|---|---|
| `c32e42469f302ab108dea08d9b90164458696328` | Canary task-start SHA | PASS |
| `3cc7c1dfea747bb380f3761ee7ff7ac30141a115` | Otheryn task-start SHA | PASS |
| `a879c9312e34381e8eedf397b8ed44510698b689` | upstream task-start SHA | PASS |
| `fdd2b1f13f53894c584346ef3de43658045c42a7` | donor comparison SHA | PASS |
| legacy vs upstream compare | divergence discovery | PASS; 726 ahead / 3 behind |
| Otheryn PR #4 draft head `d6e7d0a599c0b2938999504f363e27c7b1bf3857` | draft-cycle CI | PASS; build jobs skipped because draft, therefore not merge evidence |
| Otheryn PR #4 ready-cycle | full CI / Required | IN PROGRESS |

# Failed approaches and dead ends

- Targeted GitHub code search was unreliable for several canonical IDs/shared-index terms; negative search results were not treated as absence proof.
- Repository-wide compare was used only for discovery, never as a migration decision.
- Legacy recency was rejected as a reason for reuse because its history diverges and includes excluded architecture.
- Crystal was evaluated as comparison-only evidence and did not provide a stronger foundation implementation for any of the seven modules.

# Risks and compatibility

- Runtime: OAM-003A must preserve startup/shutdown behavior; OAM-003B must preserve Lua ownership safety.
- Data/migration: no data migration.
- Protocol/client: no contract change.
- Security: typed shared-userdata contract remains mandatory; polymorphic userdata is not bulk-audited here.
- Backward compatibility: target adaptations must remain behavior-preserving unless a later bounded task proves otherwise.
- Rollback: PR #4 is a small isolated target seam; issue #5 has no source changes yet.

# Remaining work

1. Complete exact-head ready-cycle validation and merge decision for Otheryn PR #4, then update the OAM program queue and Canary PR #411 checkpoint from the result.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T09:10:00+02:00
head: 875444d54056e06008050da66b92ff024763e18e
branch: docs/oam-003-engine-foundation-revalidation
pr: 411
status: investigating
context_routes:
  - agent-governance
  - cpp-runtime
owned_paths:
  - docs/agents/tasks/active/CAN-20260716-oteryn-engine-foundation-revalidation.md
  - docs/agents/OTERYN_OAM_003_ENGINE_FOUNDATION_REVALIDATION.md
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
proven:
  - OAM-003 seven-module evidence matrix is complete
  - build-system and engine-scheduler are REUSE
  - configuration lifecycle service-container lua-runtime and lua-bindings are ADAPT
  - Otheryn PR 4 exists for OAM-003A and contains the first explicit server composition seam
  - Otheryn issue 5 exists for OAM-003B and depends on OAM-003A
derived:
  - OAM-004 remains blocked behind the recorded OAM-003 adaptation dependency chain
unknown:
  - final exact-head ready-cycle result for Otheryn PR 4
conflicts:
  - blueprint status metadata still references completed OAM-002 gate
first_failure:
  marker: OAM-003A target validation incomplete
  evidence: draft-cycle CI passed but build jobs were skipped; ready-cycle is running
rejected_hypotheses:
  - legacy Canary is the preferred foundation because it is newer
  - Crystal provides a stronger scheduler/config/Lua ownership foundation
changed_paths:
  - docs/agents/tasks/active/CAN-20260716-oteryn-engine-foundation-revalidation.md
  - docs/agents/OTERYN_OAM_003_ENGINE_FOUNDATION_REVALIDATION.md
validation:
  - command: semantic cross-source foundation review
    result: PASS
    evidence: durable OAM-003 report
  - command: Otheryn PR 4 draft-cycle CI
    result: PASS
    evidence: CI success with build jobs skipped; full ready-cycle remains the merge gate
blockers:
  - Otheryn PR 4 full ready-cycle exact-head validation
next_action: Verify the latest exact-head ready-cycle CI and Required status for blakinio/Otheryn PR #4 and merge only if all required gates and review state are clean.
```

# Completion

- Final status: investigating
- Canary PR: #411
- Otheryn OAM-003A PR: #4
- Otheryn OAM-003B task: issue #5
- Program record updated: pending
- Catalogue updated: no change required so far
- Changelog updated: no change required so far
- Archived at: not archived
