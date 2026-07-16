---
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
name: Oteryn Architecture and Migration
status: active
owner: oteryn-architecture-migration-agent
created: 2026-07-15T15:28:18+02:00
updated: 2026-07-16T10:12:00+02:00
last_verified_commit: "870fc9acb31d8ec19f7466be9b5f4fa99567eb21"
primary_paths:
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
  - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
shared_integration_paths:
  - docs/agents/CHANGELOG.md
related_programs:
  - CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
  - CAN-PROGRAM-REAL-TIBIA-PARITY
  - CAN-PROGRAM-UPSTREAM-INTELLIGENCE
  - CAN-PROGRAM-E2E-PLATFORM
cross_repo_contracts: []
---

# Mission

Define and govern the evidence-backed transition from the legacy `blakinio/canary` laboratory to a clean Oteryn target without bulk-copying the legacy repository or treating inventory as migration authorization.

The program establishes the durable contract for:

```text
current upstream Canary baseline
+
legacy canonical module inventory
+
Real Tibia evidence
+
runtime proof
+
physical-client E2E where applicable
+
explicit Oteryn target architecture
↓
module-by-module migration disposition
↓
bounded Oteryn migration package
```

# Scope

- Preserve `blakinio/canary` as the writable legacy laboratory, evidence source, validation environment and governance repository.
- Treat one canonical module record under `docs/agents/real-tibia/registry/modules/*.yaml` as the unit of migration decision.
- Define target architecture, baseline pinning, evidence, provenance, dependency and migration-disposition rules before migration work.
- Sequence migration work through one bounded task, branch and PR at a time.
- Revalidate every affected module against exact target architecture and exact task baselines before selecting `REUSE`, `ADAPT`, `REWRITE`, `DO_NOT_MIGRATE` or `EXPERIMENTAL_ONLY`.
- Reuse existing Upstream Intelligence, Universal Physical-Client E2E and OTBM analysis infrastructure.
- Preserve cross-repository compatibility gates when server/client contracts are coupled.

# Explicit exclusions

- Do not reactivate `CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION` or create TSD-014/TSD-015.
- Do not create a second module registry, migration registry, taxonomy, dependency graph, source registry, watcher or mapper.
- Do not clone `blakinio/canary` wholesale into Oteryn.
- Do not bulk-copy directories, datapacks, maps, clients or repository history.
- Do not mass cherry-pick legacy PR history.
- Do not migrate a module solely because code exists or CI passes in legacy Canary.
- Do not treat upstream/donor path matches as semantic equivalence, bug proof, ownership or migration authorization.
- Do not create a second physical-client E2E platform.
- Do not create another OTBM parser, renderer, world index, semantic diff, script resolver, reachability scanner, spawn/NPC scanner or storage graph.
- Do not use AI-generated images as map evidence.
- Do not authorize gameplay, runtime, database, protocol, client, OTBM, map or asset changes from this program record alone.

# Current live preflight

Re-verified through OAM-003 feature merge and lifecycle start:

```text
governance/legacy repository: blakinio/canary
latest re-fetched Canary main: 870fc9acb31d8ec19f7466be9b5f4fa99567eb21
canonical module count: 62
TSD status: completed
TSD migration disposition baseline outside bounded OAM decisions: REVALIDATE
Universal Physical-Client E2E: PR #245 merged as 9fc11e04dc5040d1ea18d02e15dac1df47f3fe64
Oteryn target repository: blakinio/Otheryn
Oteryn target default branch: main
OAM-002 clean target baseline: 3cc7c1dfea747bb380f3761ee7ff7ac30141a115
OAM-003 target task-start: 3cc7c1dfea747bb380f3761ee7ff7ac30141a115
OAM-003 upstream evidence: opentibiabr/canary@a879c9312e34381e8eedf397b8ed44510698b689
OAM-003A target merge: 9b5805aaeef50774e9db5225c05529a06cec507e
OAM-003B final target merge: a9c7fabc9f4b9bbeca9fed4ab73c36309cd04e2d
OAM-003 Canary feature merge: 780704f3b77c459f852319a249425614b21246fd
OAM-003 lifecycle PR: #418
target write authorization: explicitly granted by the user for autonomous OAM writes
```

OAM-001 completed the durable target architecture contract and was lifecycle archived separately.

OAM-002 established the authorized target identity/baseline and completed feature + lifecycle governance.

OAM-003 revalidated seven engine-foundation modules, delivered two bounded target adaptation slices and merged Canary feature PR #411 as `780704f3b77c459f852319a249425614b21246fd`. Lifecycle-only PR #418 archives OAM-003. No OAM-004 task, branch or implementation is active in this lifecycle package.

OAM-003 dispositions are:

```text
build-system             REUSE
configuration            ADAPT
engine-runtime-lifecycle ADAPT
engine-scheduler         REUSE
engine-service-container ADAPT
lua-runtime              ADAPT
lua-bindings             ADAPT
```

# Target architecture contract

The authoritative contract is:

```text
docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
```

No later migration implementation may infer authorization from an earlier package. Each package must re-pin exact task-start target/upstream/legacy evidence and satisfy the contract for its affected boundaries.

# Target repository status

| Field | Value | Status |
|---|---|---|
| target repository | `blakinio/Otheryn` | ESTABLISHED |
| target default branch | `main` | ESTABLISHED |
| OAM-002 target baseline | `3cc7c1dfea747bb380f3761ee7ff7ac30141a115` | PINNED |
| OAM-003 final target head | `a9c7fabc9f4b9bbeca9fed4ab73c36309cd04e2d` | PINNED |
| upstream OAM-002/OAM-003 evidence | `opentibiabr/canary@a879c9312e34381e8eedf397b8ed44510698b689` | PINNED FOR COMPLETED PACKAGES |
| target write authorization | explicit user authorization for autonomous OAM writes to `blakinio/Otheryn` | ESTABLISHED |

OAM-004 must not reuse the OAM-003 target/upstream SHAs as moving current-state assumptions. It must re-fetch and pin fresh task-start baselines after lifecycle PR #418 merges.

# Canonical migration unit

The only migration decision unit is a canonical module from:

```text
docs/agents/real-tibia/registry/modules/*.yaml
```

Every migration package must record exact module identity, dependencies/interactions, source/evidence roles, exact SHAs, applicable architecture boundaries, tests/runtime proof, disposition rationale, known gaps and rollback/provenance notes.

Generated indexes are discovery artifacts and must not become a second registry.

# Migration dispositions

- `REUSE` — implementation can remain/move with minimal change only after target compatibility and applicable boundaries/tests are proven.
- `ADAPT` — useful implementation substrate remains, but target architecture requires bounded deliberate changes.
- `REVALIDATE` — evidence is insufficient for a stronger decision; this remains the default outside modules explicitly decided by a bounded package.
- `REWRITE` — the responsibility is required but the legacy implementation should not transfer.
- `DO_NOT_MIGRATE` — the responsibility does not belong in target architecture/product.
- `EXPERIMENTAL_ONLY` — useful only in isolated laboratory/experimental scope.

`REUSE` is never the optimistic default.

# Existing systems to reuse

| Module/tool/contract | Source | Required reuse rule |
|---|---|---|
| Real Tibia module registry | `docs/agents/real-tibia/registry/**` | Sole module identity/dependency/source-of-truth. Never duplicate it. |
| Real Tibia parity governance | `docs/agents/programs/REAL_TIBIA_PARITY_PROGRAM.md` | Preserve source roles, proof layers and bounded evidence. |
| Completed TSD program | `docs/agents/programs/TIBIA_SYSTEM_DECOMPOSITION_PROGRAM.md` | Preserve inventory; do not reopen its queue. |
| Upstream Intelligence | `docs/agents/programs/UPSTREAM_INTELLIGENCE_PROGRAM.md` | Reuse source-role-aware discovery only. |
| Universal Physical-Client E2E | PR #245; `tools/e2e/**`; `tests/e2e/**` | Add bounded scenarios; never build a second generic orchestrator. |
| OTBM analysis pipeline | existing `tools/ai-agent/**` / `docs/ai-agent/**` | Reuse canonical world/map evidence tools. |
| Canary ↔ OTClient contract registry | `docs/agents/CROSS_REPO_CONTRACTS.md` | Use explicit compatibility/version/rollout contracts when client coupling exists. |
| OAM-003 engine-foundation report | `docs/agents/OTERYN_OAM_003_ENGINE_FOUNDATION_REVALIDATION.md` | Durable evidence for seven OAM-003 decisions and delivered target seams. |

# Active tasks

No OAM implementation task is active in this lifecycle branch. PR #418 is lifecycle-only archival for completed OAM-003 and does not create OAM-004.

# Dependency-aware queue

| Package | Scope | Status | Dependencies | Exact next action |
|---|---|---|---|---|
| `OAM-001` | target architecture and migration evidence contract | completed | completed TSD + current registry | merged and lifecycle archived |
| `OAM-002` | target repository identity, authorization and exact baseline pinning | completed | OAM-001 | feature + lifecycle completed |
| `OAM-003` | engine/build/runtime foundation revalidation | completed | OAM-002 | feature PR #411 merged as `780704f3b77c459f852319a249425614b21246fd`; lifecycle archived by PR #418 |
| `OAM-004` | database and persistence foundation revalidation | planned | completed OAM-003 lifecycle | after PR #418 merges, create a separate bounded task only after fresh live target/upstream/legacy baseline, ownership and overlap verification |
| `OAM-005` | account and character lifecycle revalidation | blocked | OAM-004 | evaluate account/auth/character lifecycle and progression boundaries |
| `OAM-006` | network/login/protocol contract revalidation | blocked | OAM-003, OAM-005 | pin target protocol/client compatibility and cross-repo rollout contract |
| `OAM-007` | item/world runtime foundation revalidation | blocked | OAM-003, OAM-004 | evaluate item definitions/instances and world-map/runtime boundaries before content migration |
| `OAM-008` | first low-risk canonical module migration package | blocked | affected foundation packages | select exactly one module after dependencies and evidence gates are complete |
| `OAM-009` | target physical-client E2E proof for first migrated module | blocked | OAM-008 plus target/client compatibility | extend existing E2E platform with one bounded target scenario |
| `OAM-010+` | dependency-ordered domain migrations | planned | proven foundation and prior package dependencies | advance one bounded package at a time |

OAM-004 is only **next eligible after lifecycle merge**. This PR does not start it.

# Migration package evidence gate

Every implementation package must prove, where applicable:

1. exact legacy and target SHAs;
2. exact then-current upstream Canary evidence SHA;
3. canonical module/dependency/path records;
4. target API/lifecycle/ownership compatibility;
5. persistence/schema/migration compatibility;
6. protocol/client compatibility and rollout policy;
7. deterministic focused tests;
8. integration/runtime proof;
9. physical-client E2E where applicable;
10. source provenance/conflicts;
11. explicit known gaps;
12. rollback strategy;
13. one evidence-backed disposition.

Compilation, directory similarity, passing legacy CI or donor similarity is insufficient by itself.

# Source and cross-repository rules

- `blakinio/canary` is the writable legacy laboratory and governance repository.
- `blakinio/Otheryn` is the separately authorized writable target; authorization does not extend to another repository.
- Upstream/client/editor/donor repositories are read-only unless separately authorized.
- Every external baseline used for evidence must be pinned by exact SHA.
- Upstream Intelligence mapping is discovery only.

# AI and deterministic enforcement boundary

AI may correlate evidence, summarize findings, suggest reproduction steps and assist triage. Deterministic systems remain authoritative for gameplay, sanctions, economy mutation, migration execution and deployment safety.

# Dependencies and blockers

- OAM-001 and OAM-002 are completed and lifecycle archived.
- OAM-003 feature work is complete; PR #411 merged as `780704f3b77c459f852319a249425614b21246fd`.
- PR #418 is the required lifecycle-only archival step for OAM-003.
- OAM-004 is not active. It becomes eligible only after PR #418 merges and still requires a new bounded task with fresh exact baselines and ownership checks.
- OAM-003 known residual evidence gaps remain explicit: child Lua interface reload semantics, untouched polymorphic userdata safety, arbitrary-consumer concurrent config reload correctness, and broader incremental DI/global-access convergence.

# Decisions and invariants

- The canonical registry is the migration inventory; no parallel registry will be created.
- A module remains `REVALIDATE` unless a bounded package records/proves another disposition.
- Legacy Canary remains evidence, not a target image to clone.
- Baselines are pinned per task/package by exact SHA.
- Migration decisions are module/evidence scoped, not directory/PR-history scoped.
- Migration sequencing follows dependency evidence.
- Physical-client E2E complements, not replaces, focused/integration/runtime proof.
- World-content work reuses existing OTBM tooling.
- Every feature merge is followed by separate lifecycle-only archival.

# Validation strategy

OAM-001 and OAM-002 completed their exact-head feature and lifecycle gates.

OAM-003 completed with:

- semantic revalidation of seven canonical modules against exact legacy, target, upstream and donor SHAs;
- `build-system` and `engine-scheduler` → `REUSE`;
- `configuration`, `engine-runtime-lifecycle`, `engine-service-container`, `lua-runtime`, `lua-bindings` → `ADAPT`;
- OAM-003A target PR #4 full exact-head CI/Required/review gates before merge `9b5805aaeef50774e9db5225c05529a06cec507e`;
- OAM-003B target PR #6 exact head `49e9e4960d89476016c50d81523715b7551c1bf9` with CI #21, Required #18 and clean review gate before merge `a9c7fabc9f4b9bbeca9fed4ab73c36309cd04e2d`;
- Canary PR #411 final head `9a08fb2d65fa0cd82a9893bf58f69488a68adac0` with Agent Task Ownership #1537 and ready-triggered CI #2671 success;
- zero PR comments, submitted reviews or unresolved review threads before feature merge;
- feature PR #411 squash-merged with exact-head guard as `780704f3b77c459f852319a249425614b21246fd`;
- no OAM-004 implementation.

Lifecycle PR #418 must pass its own exact-head ownership/CI/review gates before merge.

# Handoff

## Start here

Read `AGENTS.md`, `docs/agents/README.md`, this program, `docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md`, `docs/agents/OTERYN_OAM_003_ENGINE_FOUNDATION_REVALIDATION.md`, the current canonical registry/generated indexes, all active task records and live open PRs.

## Task creation protocol

1. Select exactly one still-valid bounded package from this queue.
2. Re-fetch live `main`, open PRs, active tasks, ownership and external heads.
3. Pin exact current target/upstream/legacy task-start SHAs.
4. Create one task, branch and draft PR with explicit ownership.
5. Record canonical module and dependency/evidence requirements.
6. Implement only bounded scope.
7. Review exact-head diff, CI and review state.
8. Squash-merge only after all gates pass.
9. Archive through a separate lifecycle-only PR.

## Do not repeat

- Do not create TSD-014/TSD-015.
- Do not create a second registry, taxonomy, watcher, mapper, E2E platform or OTBM pipeline.
- Do not infer `REUSE` from code presence.
- Do not bulk-copy legacy Canary.
- Do not invent target repository/baselines.
- Do not reopen OAM-003A/B merely to solve explicitly deferred gaps without a new bounded task.

## Known gaps carried forward

- Complete child `LuaScriptInterface` reconstruction/reload semantics.
- Untouched polymorphic Lua userdata safety.
- Concurrent configuration reload correctness under arbitrary future target consumers.
- Broader incremental removal of contextual/global DI access.

# Exact next task

After lifecycle-only PR #418 merges, `OAM-004 — database and persistence foundation revalidation` becomes the next eligible bounded package. It must be opened separately after fresh live-state, ownership/overlap and exact target/upstream/legacy baseline verification. This lifecycle PR does not create, claim or start OAM-004.
