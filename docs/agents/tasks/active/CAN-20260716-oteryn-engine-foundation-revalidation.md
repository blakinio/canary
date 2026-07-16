---
task_id: CAN-20260716-oteryn-engine-foundation-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: "OAM-003"
status: ready
agent: oteryn-architecture-migration-agent
branch: docs/oam-003-engine-foundation-revalidation
base_branch: main
created: 2026-07-16T08:53:00+02:00
updated: 2026-07-16T09:55:00+02:00
last_verified_commit: "8950a275e258ccc0f1a6781c9ff9c8ea089210a0"
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
    - blakinio/Otheryn@a9c7fabc9f4b9bbeca9fed4ab73c36309cd04e2d
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
  - blakinio/Otheryn#6
---

# Goal

Revalidate the seven canonical Oteryn engine-foundation modules against exact target, legacy, upstream and relevant donor baselines; assign evidence-backed dispositions; deliver the minimum bounded target adaptations required by those dispositions; and stop before OAM-004.

# Acceptance criteria

- [x] Exact OAM-003 task-start SHAs pinned for Canary, Otheryn and upstream Canary.
- [x] Relevant Crystal donor SHA pinned as comparison-only evidence.
- [x] Seven canonical module records pinned and refreshed as task inputs.
- [x] Target-relevant boundaries classified for every module.
- [x] Target/upstream/legacy/donor differences inventoried semantically.
- [x] Existing reusable implementations/tests identified before target adaptation.
- [x] Each module receives one evidence-backed disposition.
- [x] Runtime-sensitive claims use target runtime/build evidence; unresolved concerns remain explicit.
- [x] OAM-003A target PR #4 passed full exact-head gates and merged.
- [x] OAM-003B target PR #6 passed full exact-head gates and merged.
- [x] OAM-003B issue #5 closed as completed.
- [x] Durable OAM-003 report updated with final target delivery evidence and known gaps.
- [ ] OAM program queue/handoff updated with OAM-003 ready-for-governance-merge state and OAM-004 lifecycle dependency.
- [ ] Current-head Canary PR #411 ownership/CI/review gates verified.
- [ ] Canary feature PR #411 squash-merged.
- [ ] Task archived through a separate lifecycle-only PR.
- [x] Module catalogue/changelog impact: none; no new generic platform or parallel registry introduced.
- [x] Cross-repository impact handled; no protocol/client contract inferred.

# PROVEN

- OAM-002 lifecycle completed before OAM-003 start on `blakinio/canary@c32e42469f302ab108dea08d9b90164458696328`.
- OAM-003 target task-start baseline: `blakinio/Otheryn@3cc7c1dfea747bb380f3761ee7ff7ac30141a115`.
- OAM-003 upstream baseline: `opentibiabr/canary@a879c9312e34381e8eedf397b8ed44510698b689`.
- OAM-003 legacy baseline: `blakinio/canary@c32e42469f302ab108dea08d9b90164458696328`.
- Donor comparison baseline: `zimbadev/crystalserver@fdd2b1f13f53894c584346ef3de43658045c42a7`.
- Latest re-fetched Canary `main` during governance finalization: `8950a275e258ccc0f1a6781c9ff9c8ea089210a0`.
- Legacy and upstream histories diverged: legacy was 726 commits ahead and 3 behind with merge base `e8237cef...`; legacy is not a monotonic successor.
- Legacy and Crystal schedulers use older `TaskGroup` models; target/upstream uses lane/WDRR/barrier-parallel scheduling with focused tests.
- Legacy/Crystal config uses plain `bool loaded`; target/upstream uses atomic load state plus mutex-protected deferred callbacks.
- Legacy lifecycle contains multichannel cluster/Redis/handoff/leadership bootstrap explicitly excluded from initial Oteryn.
- Core DI primitives are materially shared; no donor provides a cleaner replacement composition model.
- Target/upstream/legacy Lua runtime plus typed shared-userdata foundation is materially shared; Crystal lacks the target typed ownership layer.
- Final dispositions:
  - `build-system` → `REUSE`;
  - `configuration` → `ADAPT`;
  - `engine-runtime-lifecycle` → `ADAPT`;
  - `engine-scheduler` → `REUSE`;
  - `engine-service-container` → `ADAPT`;
  - `lua-runtime` → `ADAPT`;
  - `lua-bindings` → `ADAPT`.
- OAM-003A PR `blakinio/Otheryn#4` passed full exact-head target `CI`, `Required` and autofix gates with no review blockers and squash-merged as `9b5805aaeef50774e9db5225c05529a06cec507e`.
- OAM-003B PR `blakinio/Otheryn#6` changed exactly six bounded files, no domain/feature binding implementation, and passed full exact-head target `CI #21`, `Required #18` and autofix on `49e9e4960d89476016c50d81523715b7551c1bf9` with no comments, submitted reviews or unresolved threads.
- OAM-003B squash-merged as final OAM-003 target head `a9c7fabc9f4b9bbeca9fed4ab73c36309cd04e2d`.
- OAM-003B issue `blakinio/Otheryn#5` is closed as completed.
- OAM-003B delivered explicit root `LuaEnvironment` shutdown/reload ownership while preserving typed shared-userdata infrastructure and leaving child-interface reload reconstruction explicitly unresolved.

# DERIVED

- No legacy or Crystal foundation module should replace the retained target/upstream build or scheduler foundation.
- The minimum OAM-003 target adaptation chain is complete at `Otheryn@a9c7fabc...`.
- OAM-004 can become the next eligible bounded package only after OAM-003 Canary governance merge and lifecycle archival; OAM-004 is not started by this task.
- Remaining global/contextual DI access and Lua child-interface reload gaps are future bounded evidence concerns, not reasons to reopen the completed OAM-003A/B slices.

# UNKNOWN

- Complete Lua child `LuaScriptInterface` reconstruction/reload semantics remain unresolved.
- Safety of untouched polymorphic Lua userdata families remains unproven outside touched packages.
- Concurrent configuration reload correctness under arbitrary future target consumers remains unproven.

# CONFLICT

- Durable blueprint status metadata still references the already completed OAM-002 identity blocker. Architecture content remains authoritative; OAM-003 does not casually rewrite the blueprint merely to refresh its status line.

# Existing work reused

| Evidence/system | Reuse decision |
|---|---|
| Oteryn target blueprint | architecture invariants and target boundaries |
| Oteryn architecture contract | exact SHA/boundary/disposition gate |
| TSD engine foundation report | inventory only; refreshed by OAM-003 |
| upstream lane/WDRR scheduler | direct `REUSE` |
| upstream build foundation | direct `REUSE` |
| Boost.DI primitives/current bindings | substrate for bounded `ADAPT`; no second DI container |
| typed Lua shared-userdata helpers | retained substrate; ownership contract unchanged |
| OAM-002 target CI evidence | baseline runtime/build evidence |

# Ownership and overlap check

- Open Canary PRs at OAM-003 start were unrelated to the seven canonical foundation records claimed by this task.
- Otheryn had no open PR at OAM-003 task start.
- No pre-existing OAM-003 task/branch was found before creation.
- OAM-003A and OAM-003B were isolated in target PRs #4 and #6; issue #5 tracked the second bounded slice.
- No protocol/client or persistence implementation path was claimed.
- Canary PR #411 previously achieved green `CI #2650` and `Agent Task Ownership #1517` before final target-delivery updates; fresh exact-head gates are required after these governance changes.

# Decisions

| Decision | Reason/evidence |
|---|---|
| Keep target/upstream build system | validated baseline; legacy build adds excluded multichannel-specific surfaces |
| Keep upstream scheduler | newer lane/WDRR model with focused tests; legacy/Crystal are older TaskGroup designs |
| Adapt lifecycle/config/DI ownership incrementally | target blueprint requires explicit composition; OAM-003A establishes first seam without broad refactor |
| Adapt Lua runtime/bindings incrementally | OAM-003B establishes root lifecycle/reload boundary while preserving typed ownership helpers; child reload and untouched domain bindings remain bounded future concerns |
| Stop before OAM-004 | feature and lifecycle governance gates for OAM-003 must complete first |

# Validation and CI

| Commit/ref | Check | Result |
|---|---|---|
| `c32e42469f302ab108dea08d9b90164458696328` | Canary OAM-003 task-start SHA | PASS |
| `3cc7c1dfea747bb380f3761ee7ff7ac30141a115` | Otheryn OAM-003 task-start SHA | PASS |
| `a879c9312e34381e8eedf397b8ed44510698b689` | upstream evidence SHA | PASS |
| `fdd2b1f13f53894c584346ef3de43658045c42a7` | donor comparison SHA | PASS |
| legacy vs upstream compare | divergence discovery | PASS; 726 ahead / 3 behind |
| Otheryn PR #4 | full exact-head target CI / Required / review gate | PASS; merged `9b5805aaeef50774e9db5225c05529a06cec507e` |
| Otheryn PR #6 head `49e9e4960d89476016c50d81523715b7551c1bf9` | full exact-head CI #21 / Required #18 / review gate | PASS |
| Otheryn PR #6 | squash merge | PASS; `a9c7fabc9f4b9bbeca9fed4ab73c36309cd04e2d` |
| Canary PR #411 prior head `cc79c3251b830fe65931c9228c0178669063c4d2` | CI #2650 / Agent Task Ownership #1517 | PASS; superseded by final governance updates, so fresh gates required |

# Failed approaches and dead ends

- Targeted GitHub code search was unreliable for several canonical IDs/shared-index terms; negative search results were not treated as absence proof.
- Repository-wide compare was used only for discovery, never as migration authorization.
- Legacy recency was rejected as a reason for reuse because its history diverges and contains excluded architecture.
- Crystal was comparison-only and did not provide a stronger foundation implementation for any of the seven modules.
- OAM-003A draft-cycle build jobs were skipped and were not accepted as merge evidence; the full ready-cycle was required.
- OAM-003B draft-cycle build jobs were skipped and were not accepted as merge evidence; the full ready-cycle was required.
- Canary ownership validation rejected intermediate non-contract status/result tokens; the task/checkpoint was corrected to repository-valid states rather than bypassing validation.

# Risks and compatibility

- Runtime: OAM-003A/B preserve proven startup/shutdown behavior and passed target runtime smoke.
- Data/migration: no data migration.
- Protocol/client: no contract change.
- Security: typed shared-userdata ownership contract remains mandatory; untouched polymorphic userdata is not globally audited here.
- Backward compatibility: delivered seams are behavior-preserving foundation adaptations.
- Rollback: OAM-003A and OAM-003B are separate squash-merged target commits with bounded scopes.

# Remaining work

1. Update the authoritative OAM program queue, then verify exact-current-head Canary PR #411 ownership, CI, changed files and review state; squash-merge when all gates pass and archive OAM-003 separately.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T09:55:00+02:00
head: 8950a275e258ccc0f1a6781c9ff9c8ea089210a0
branch: docs/oam-003-engine-foundation-revalidation
pr: 411
status: ready
context_routes:
  - agent-governance
  - cpp-runtime
owned_paths:
  - docs/agents/tasks/active/CAN-20260716-oteryn-engine-foundation-revalidation.md
  - docs/agents/OTERYN_OAM_003_ENGINE_FOUNDATION_REVALIDATION.md
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
proven:
  - all seven OAM-003 foundation modules have explicit dispositions
  - build-system and engine-scheduler are REUSE
  - configuration engine-runtime-lifecycle engine-service-container lua-runtime and lua-bindings are ADAPT
  - OAM-003A merged in Otheryn as 9b5805aaeef50774e9db5225c05529a06cec507e
  - OAM-003B merged in Otheryn as a9c7fabc9f4b9bbeca9fed4ab73c36309cd04e2d
  - OAM-003B issue 5 is completed
  - final OAM-003 target head is a9c7fabc9f4b9bbeca9fed4ab73c36309cd04e2d
derived:
  - target adaptation chain required by OAM-003 is complete
  - OAM-004 remains separate and cannot start before OAM-003 governance and lifecycle completion
unknown:
  - complete child Lua interface reload semantics
  - untouched polymorphic userdata safety
  - arbitrary-consumer concurrent configuration reload correctness
conflicts:
  - blueprint status metadata still references completed OAM-002 blocker
first_failure:
  marker: none remaining in target delivery
  evidence: OAM-003A and OAM-003B exact-head target gates passed and both PRs merged
rejected_hypotheses:
  - legacy Canary is the preferred foundation because it is newer
  - Crystal provides a stronger scheduler config or Lua ownership foundation
changed_paths:
  - docs/agents/tasks/active/CAN-20260716-oteryn-engine-foundation-revalidation.md
  - docs/agents/OTERYN_OAM_003_ENGINE_FOUNDATION_REVALIDATION.md
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
validation:
  - command: semantic cross-source foundation review
    result: PASS
    evidence: durable OAM-003 report
  - command: Otheryn PR 4 full exact-head ready-cycle
    result: PASS
    evidence: merged as 9b5805aaeef50774e9db5225c05529a06cec507e
  - command: Otheryn PR 6 full exact-head ready-cycle
    result: PASS
    evidence: CI 21 and Required 18 on 49e9e4960d89476016c50d81523715b7551c1bf9; merged as a9c7fabc9f4b9bbeca9fed4ab73c36309cd04e2d
blockers: []
next_action: Update the OAM program record with completed OAM-003 target adaptation evidence and the lifecycle gate before OAM-004.
```

# Completion

- Final status: ready for governance merge gates
- Canary feature PR: #411
- OAM-003A target PR: `blakinio/Otheryn#4` merged as `9b5805aaeef50774e9db5225c05529a06cec507e`
- OAM-003B target issue: `blakinio/Otheryn#5` completed
- OAM-003B target PR: `blakinio/Otheryn#6` merged as `a9c7fabc9f4b9bbeca9fed4ab73c36309cd04e2d`
- Final OAM-003 target head: `a9c7fabc9f4b9bbeca9fed4ab73c36309cd04e2d`
- Program record updated: pending final OAM-003 queue update
- Catalogue updated: not applicable
- Changelog updated: not applicable
- Archived at: not archived
