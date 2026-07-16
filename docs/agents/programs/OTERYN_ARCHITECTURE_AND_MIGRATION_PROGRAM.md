---
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
name: Oteryn Architecture and Migration
status: active
owner: oteryn-architecture-migration-agent
created: 2026-07-15T15:28:18+02:00
updated: 2026-07-16T09:58:00+02:00
last_verified_commit: "8950a275e258ccc0f1a6781c9ff9c8ea089210a0"
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

Re-verified during OAM-003 governance finalization:

```text
governance/legacy repository: blakinio/canary
latest re-fetched Canary main: 8950a275e258ccc0f1a6781c9ff9c8ea089210a0
canonical module count: 62
TSD status: completed
TSD migration disposition baseline outside bounded OAM decisions: REVALIDATE
Universal Physical-Client E2E: PR #245 merged as 9fc11e04dc5040d1ea18d02e15dac1df47f3fe64
Oteryn target repository: blakinio/Otheryn
Oteryn target default branch: main
OAM-002 clean target baseline: 3cc7c1dfea747bb380f3761ee7ff7ac30141a115
OAM-003 target task-start: 3cc7c1dfea747bb380f3761ee7ff7ac30141a115
OAM-003 legacy task-start: c32e42469f302ab108dea08d9b90164458696328
OAM-003 upstream evidence: opentibiabr/canary@a879c9312e34381e8eedf397b8ed44510698b689
OAM-003 donor comparison: zimbadev/crystalserver@fdd2b1f13f53894c584346ef3de43658045c42a7
OAM-003A target merge: 9b5805aaeef50774e9db5225c05529a06cec507e
OAM-003B final target merge: a9c7fabc9f4b9bbeca9fed4ab73c36309cd04e2d
target write authorization: explicitly granted by the user for autonomous OAM writes
```

OAM-001 feature PR #383 completed the durable target architecture contract and was archived separately.

OAM-002 feature PR #407 established the authorized target identity/baseline and merged as `0a311d6cda6a80e31aa3a5ca9406aea7aeadd58c`; lifecycle PR #410 completed and archived OAM-002 as `c32e42469f302ab108dea08d9b90164458696328`.

OAM-003 revalidated seven engine-foundation modules and delivered two bounded target adaptation slices. OAM-003A PR `blakinio/Otheryn#4` merged as `9b5805aaeef50774e9db5225c05529a06cec507e`. OAM-003B PR `blakinio/Otheryn#6` merged as `a9c7fabc9f4b9bbeca9fed4ab73c36309cd04e2d`; issue #5 is completed. No OAM-004 task is active.

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

The authoritative contract for this program is:

```text
docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
```

No later migration implementation may infer authorization from an earlier package. Each package must re-pin its exact task-start target/upstream evidence and satisfy the contract for its affected boundaries.

# Target repository status

The program uses the exact authorized target below and does not infer authorization for any other repository.

| Field | Value | Status |
|---|---|---|
| target repository | `blakinio/Otheryn` | ESTABLISHED |
| target default branch | `main` | ESTABLISHED |
| OAM-002 target baseline | `3cc7c1dfea747bb380f3761ee7ff7ac30141a115` | PINNED |
| OAM-003 final target head | `a9c7fabc9f4b9bbeca9fed4ab73c36309cd04e2d` | PINNED |
| upstream bootstrap/evidence source | `opentibiabr/canary@a879c9312e34381e8eedf397b8ed44510698b689` | PINNED FOR OAM-002/OAM-003 EVIDENCE |
| target write authorization | explicit user authorization for autonomous OAM writes to `blakinio/Otheryn` | ESTABLISHED |

The target identity gate is satisfied. The current OAM-003 target adaptation chain is complete, but OAM-004 remains blocked until Canary PR #411 merges and OAM-003 is archived through a separate lifecycle-only PR.

# Canonical migration unit

The only migration decision unit is a canonical module from:

```text
docs/agents/real-tibia/registry/modules/*.yaml
```

A migration package must name at least:

```text
module_id
legacy source paths
target paths
depends_on
interacts_with
source/evidence set
runtime proof
physical-client E2E proof when applicable
migration disposition
disposition rationale
known gaps
rollback/provenance notes
exact legacy SHA
exact target SHA
exact upstream/donor SHAs when used
```

Generated indexes are discovery artifacts and must not become a second registry.

# Migration dispositions

The program uses these evidence-backed outcomes:

- `REUSE` — implementation can remain/move with minimal change only after target compatibility and applicable tests/boundaries are proven.
- `ADAPT` — useful implementation substrate remains, but target architecture requires bounded deliberate changes.
- `REVALIDATE` — evidence is insufficient for a stronger decision; this remains the default outside modules explicitly decided by a bounded package.
- `REWRITE` — the responsibility is required, but the legacy implementation should not transfer.
- `DO_NOT_MIGRATE` — the responsibility does not belong in target architecture/product.
- `EXPERIMENTAL_ONLY` — useful only in isolated laboratory/experimental scope.

`REUSE` is never the optimistic default.

# Existing systems to reuse

| Module/tool/contract | Source | Required reuse rule |
|---|---|---|
| Real Tibia module registry | `docs/agents/real-tibia/registry/**` | Sole module identity/dependency/source-of-truth. Never duplicate it. |
| Real Tibia parity governance | `docs/agents/programs/REAL_TIBIA_PARITY_PROGRAM.md` | Preserve source roles, proof layers and bounded evidence. |
| Completed TSD program | `docs/agents/programs/TIBIA_SYSTEM_DECOMPOSITION_PROGRAM.md` | Preserve inventory; do not reopen its queue. |
| Upstream Intelligence | `docs/agents/programs/UPSTREAM_INTELLIGENCE_PROGRAM.md` | Reuse source registry and source-role-aware mapping for discovery only. |
| Universal Physical-Client E2E | PR #245; `tools/e2e/**`; `tests/e2e/**` | Add bounded scenarios; never build a second generic orchestrator. |
| OTBM analysis pipeline | existing `tools/ai-agent/**` / `docs/ai-agent/**` | Reuse canonical world/map evidence tools; no duplicate parser/renderer/index. |
| Canary ↔ OTClient contract registry | `docs/agents/CROSS_REPO_CONTRACTS.md` | Use explicit compatibility/version/rollout contracts whenever client coupling exists. |
| OAM-003 engine-foundation report | `docs/agents/OTERYN_OAM_003_ENGINE_FOUNDATION_REVALIDATION.md` | Durable evidence for the seven OAM-003 module decisions and delivered target seams. |

# Active tasks

`OAM-003` is the active bounded governance task in Canary PR #411. Its evidence matrix and target adaptation chain are complete. The remaining work is Canary feature merge and separate lifecycle archival. No OAM-004 implementation task is active.

# Dependency-aware queue

The canonical dependency graph requires foundation and persistence contracts before higher-level migrations. This queue is a program plan, not migration authorization.

| Package | Scope | Status | Dependencies | Exact next action |
|---|---|---|---|---|
| `OAM-001` | target architecture and migration evidence contract | completed | completed TSD + current registry | merged and lifecycle archived |
| `OAM-002` | target repository identity, authorization and exact baseline pinning | completed | OAM-001 | feature PR #407 and lifecycle PR #410 completed |
| `OAM-003` | engine/build/runtime foundation revalidation | ready | OAM-002 | merge Canary PR #411 after fresh exact-head gates, then archive OAM-003 through a separate lifecycle-only PR |
| `OAM-004` | database and persistence foundation revalidation | blocked | completed OAM-003 governance + lifecycle | only after OAM-003 lifecycle completion, create a separate bounded task with fresh live target/upstream/legacy baselines and ownership/overlap checks |
| `OAM-005` | account and character lifecycle revalidation | blocked | OAM-004 | evaluate account/auth/character lifecycle and progression boundaries |
| `OAM-006` | network/login/protocol contract revalidation | blocked | OAM-003, OAM-005 | pin target protocol/client compatibility and cross-repo rollout contract |
| `OAM-007` | item/world runtime foundation revalidation | blocked | OAM-003, OAM-004 | evaluate item definitions/instances and world-map/runtime boundaries before content migration |
| `OAM-008` | first low-risk canonical module migration package | blocked | affected foundation packages | select exactly one module only after evidence proves an appropriate disposition and dependencies are complete |
| `OAM-009` | target physical-client E2E proof for first migrated module | blocked | OAM-008 plus target/client compatibility | extend the existing E2E platform with one bounded target scenario |
| `OAM-010+` | dependency-ordered domain migrations | planned | proven foundation and prior package dependencies | advance one bounded canonical module/package at a time |

After foundation packages, later domain ordering is determined from the live canonical dependency graph. No wave is copied mechanically when exact dependencies indicate a different order.

# Migration package evidence gate

Every implementation package must prove, where applicable:

1. exact legacy and target SHAs;
2. exact then-current upstream Canary SHA used as evidence/baseline;
3. canonical `module_id` and current registry dependency/path records;
4. target API/lifecycle/ownership compatibility;
5. persistence/schema/migration compatibility;
6. protocol/client compatibility and rollout policy;
7. deterministic focused tests;
8. integration/runtime proof;
9. physical-client E2E for user-visible/session/protocol behavior;
10. source provenance and conflicts;
11. known gaps and explicit unresolved evidence;
12. rollback strategy;
13. one evidence-backed migration disposition.

Compilation, directory similarity, passing legacy CI or donor similarity is insufficient by itself.

# Source and cross-repository rules

- `blakinio/canary` is the writable legacy laboratory and governance repository for this program.
- `blakinio/Otheryn` is the separately and explicitly authorized writable Oteryn target; that authorization does not extend to any other repository.
- `opentibiabr/canary`, `opentibiabr/otclient`, `opentibiabr/remeres-map-editor` and `opentibiabr/client-editor` are read-only references.
- Donor repositories are read-only comparison sources and are not official Real Tibia authorities.
- Oteryn writes require explicit repository identity and authorization before a task may claim target paths.
- Every external code baseline used for evidence must be pinned by exact SHA.
- Upstream Intelligence mapping remains a discovery hint only.

# AI and deterministic enforcement boundary

AI may correlate evidence, summarize findings, suggest reproduction steps and assist triage. AI must not automatically ban, mutate balances/items, deploy code, execute arbitrary Lua, modify production or invoke unrestricted game APIs.

Deterministic systems remain authoritative for gameplay, sanctions, economy mutation, migration execution and deployment safety.

# Dependencies and blockers

- OAM-002 is completed and lifecycle archived.
- OAM-003 evidence and target delivery are complete at `blakinio/Otheryn@a9c7fabc9f4b9bbeca9fed4ab73c36309cd04e2d`.
- OAM-003 remaining gate: Canary feature PR #411 exact-head ownership/CI/review merge gate, followed by a separate lifecycle-only archive PR.
- OAM-004 is not active and remains blocked until OAM-003 lifecycle completion.
- Known OAM-003 residual evidence gaps remain explicit: complete child Lua interface reload semantics, untouched polymorphic userdata safety, and concurrent config reload correctness under arbitrary future consumers.
- Dependency: current canonical registry and generated dependency graph.
- Dependency: fresh then-current target/upstream baselines for every later bounded package.
- Dependency: merged Universal Physical-Client E2E for applicable target proof.
- Dependency: Upstream Intelligence for discovery, not authorization.

# Decisions and invariants

- The canonical registry is the migration inventory; no parallel registry will be created.
- A module remains `REVALIDATE` unless a bounded package records and proves a stronger/different disposition.
- Legacy Canary remains an evidence laboratory, not the target image to clone.
- Target baseline is pinned per task/package by exact SHA and never inferred from a moving branch.
- Migration decisions are module-scoped and evidence-scoped, not directory-scoped or PR-history-scoped.
- Migration sequencing follows dependency evidence.
- Physical-client E2E complements focused/integration/runtime proof; it does not replace them.
- World-content work reuses existing OTBM tooling and never treats donor evidence as automatic map-import permission.
- A feature merge is followed by a separate lifecycle-only archive PR.

# Validation strategy

OAM-001 completed with exact-head governance/CI/review gates and separate lifecycle archival.

OAM-002 completed with deterministic target bootstrap/tree evidence, exact-head target/Canary gates, feature merge and separate lifecycle archival.

OAM-003 target-side validation completed with:

- semantic revalidation of seven canonical modules against exact legacy, target, upstream and donor SHAs;
- `build-system` and `engine-scheduler` decided `REUSE`;
- `configuration`, `engine-runtime-lifecycle`, `engine-service-container`, `lua-runtime` and `lua-bindings` decided `ADAPT`;
- OAM-003A target PR #4 full exact-head CI/Required/autofix success and clean review state before squash merge `9b5805aaeef50774e9db5225c05529a06cec507e`;
- OAM-003B target PR #6 exact head `49e9e4960d89476016c50d81523715b7551c1bf9` with CI #21 success, `Required` #18 success, autofix success and no comments/reviews/unresolved threads before squash merge `a9c7fabc9f4b9bbeca9fed4ab73c36309cd04e2d`;
- no persistence, protocol/client, map/content or domain-feature binding migration.

OAM-003 Canary governance validation must still be repeated on the final PR #411 head after this program update before merge.

For later migration packages:

- select focused tests from `BUILD_TEST_MATRIX.md`;
- require target build/integration/runtime evidence;
- add physical-client E2E only through the existing platform where applicable;
- require cross-repository compatibility proof when client/protocol behavior is coupled.

# Handoff

## Start here

Read `AGENTS.md`, `docs/agents/README.md`, this program, `docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md`, `docs/agents/OTERYN_OAM_003_ENGINE_FOUNDATION_REVALIDATION.md`, the current canonical registry/generated indexes, all active task records and all live open PRs.

## Task creation protocol

1. Select exactly one still-valid bounded package from this queue.
2. Re-fetch live `main`, open PRs, active tasks, ownership and relevant external heads.
3. Pin exact current target/upstream/legacy task-start SHAs before implementation.
4. Create one task, branch and draft PR with explicit exclusive/shared/read-only paths.
5. Record canonical `module_id` and dependency/evidence requirements.
6. Implement and validate only the bounded scope.
7. Review exact current-head diff, CI, comments, reviews and unresolved threads.
8. Squash-merge only after all gates pass.
9. Archive through a separate lifecycle-only PR.

## Do not repeat

- Do not create TSD-014/TSD-015.
- Do not create a second registry, taxonomy, watcher, mapper, E2E platform or OTBM pipeline.
- Do not infer `REUSE` from code presence.
- Do not bulk-copy legacy Canary.
- Do not invent a target repository or baseline.
- Do not reopen OAM-003A/B merely to solve the explicitly deferred Lua child-interface or broad DI/config concerns; those require separately bounded evidence when they become relevant.

## Open questions / known gaps

- Complete child `LuaScriptInterface` reconstruction/reload semantics remain unresolved.
- Safety of untouched polymorphic Lua userdata families remains unproven outside future touched packages.
- Concurrent configuration reload correctness under arbitrary future target consumers remains unproven.

# Exact next task

OAM-003 remains the active package until Canary PR #411 merges and its task is archived through a separate lifecycle-only PR. Only after that lifecycle completion does `OAM-004 — database and persistence foundation revalidation` become the next eligible bounded task. OAM-004 must start separately with fresh live-state, ownership/overlap and exact target/upstream/legacy baseline verification.
