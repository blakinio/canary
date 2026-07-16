---
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
name: Oteryn Architecture and Migration
status: active
owner: oteryn-architecture-migration-agent
created: 2026-07-15T15:28:18+02:00
updated: 2026-07-16T01:50:09+02:00
last_verified_commit: "0a311d6cda6a80e31aa3a5ca9406aea7aeadd58c"
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

Define and govern the evidence-backed transition from the legacy `blakinio/canary` laboratory to a clean future Oteryn target without bulk-copying the legacy repository or treating inventory as migration authorization.

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

- Preserve `blakinio/canary` as the writable legacy laboratory, evidence source, validation environment and migration-source candidate.
- Treat one canonical module record under `docs/agents/real-tibia/registry/modules/*.yaml` as the unit of migration decision.
- Define target architecture, baseline pinning, evidence, provenance, dependency and migration-disposition rules before any Oteryn implementation.
- Sequence migration work through one bounded task, branch and PR at a time.
- Revalidate every affected module against the exact target architecture and exact target baseline before selecting `REUSE`, `ADAPT`, `REWRITE`, `DO_NOT_MIGRATE` or `EXPERIMENTAL_ONLY`.
- Reuse existing Upstream Intelligence, Universal Physical-Client E2E and OTBM analysis infrastructure.
- Preserve cross-repository compatibility gates when Canary/OTClient or future Oteryn/client contracts are coupled.

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

Re-verified through OAM-002 feature merge and lifecycle start:

```text
governance/legacy repository: blakinio/canary
OAM-002 feature merge / lifecycle base: 0a311d6cda6a80e31aa3a5ca9406aea7aeadd58c
canonical module count: 62
TSD status: completed
TSD migration disposition baseline: ALL_CANONICAL_MODULES -> REVALIDATE
Universal Physical-Client E2E: PR #245 merged as 9fc11e04dc5040d1ea18d02e15dac1df47f3fe64
Oteryn target repository: blakinio/Otheryn
Oteryn target default branch: main
Oteryn target task-start SHA: 7d1e9cc5b4e799d31ae481b9a65e3f1442ca985e
Oteryn final OAM-002 baseline SHA: 3cc7c1dfea747bb380f3761ee7ff7ac30141a115
OAM-002 upstream baseline: opentibiabr/canary@a879c9312e34381e8eedf397b8ed44510698b689
target write authorization: explicitly granted by the user for autonomous OAM writes
```

OAM-001 feature PR #383 remains completed as `9c28e52db81eb6b99a54e7700ad00288e6dbfd94` with lifecycle archived separately.

OAM-002 target PR #1 established the pinned-upstream content baseline and target CI gates; target PR #2 removed the one-time bootstrap comparison exception. Final target `main@3cc7c1dfea747bb380f3761ee7ff7ac30141a115` was then verified by a closed, unmerged read-only evidence PR #3. The final target matches pinned upstream content except exactly `.github/workflows/required.yml` and `.github/workflows/reusable-docker-quickstart-smoke.yml`.

OAM-002 Canary feature PR #407 passed exact-head ownership and ready-triggered CI gates and squash-merged as `0a311d6cda6a80e31aa3a5ca9406aea7aeadd58c`. Lifecycle-only PR #410 archives the completed task. The merged E2E platform remains the single reusable physical-client orchestration. OAM-002 changed no canonical module disposition and started no OAM-003 implementation.

# Target architecture contract

The authoritative contract for this program is:

```text
docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
```

No migration implementation may start until the contract's required target identity and baseline fields are resolved for the affected package.

# Target repository status

The program uses the exact OAM-002 target identity below and does not infer authorization for any other repository.

Current state:

| Field | Value | Status |
|---|---|---|
| target repository | `blakinio/Otheryn` | ESTABLISHED |
| target default branch | `main` | ESTABLISHED |
| target task-start SHA | `7d1e9cc5b4e799d31ae481b9a65e3f1442ca985e` | PINNED |
| exact target OAM-002 baseline SHA | `3cc7c1dfea747bb380f3761ee7ff7ac30141a115` | PINNED |
| upstream bootstrap source | `opentibiabr/canary@a879c9312e34381e8eedf397b8ed44510698b689` | PINNED |
| bootstrap relationship | pinned upstream content plus two explicit target CI/governance paths | VERIFIED |
| target write authorization | explicit user authorization for autonomous OAM writes to `blakinio/Otheryn` | ESTABLISHED |

The target identity/baseline gate is satisfied. OAM-003 is not started by OAM-002 or by lifecycle PR #410; after this lifecycle PR merges, OAM-003 is merely the next eligible separate bounded task and must begin with fresh live-state, ownership and exact baseline verification.

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

- `REUSE` — implementation can move with minimal change only after target API, ownership/lifecycle, persistence/protocol, tests and coupling are proven compatible.
- `ADAPT` — legacy logic is valuable but must be reshaped to the target architecture or APIs.
- `REVALIDATE` — evidence is insufficient for a stronger decision. This remains the default for all 62 canonical modules.
- `REWRITE` — the functional contract is required, but legacy implementation or coupling should not be transferred.
- `DO_NOT_MIGRATE` — the module does not belong in the target Oteryn product/architecture.
- `EXPERIMENTAL_ONLY` — the work may remain in laboratory/experimental scope but is not a core target candidate.

`REUSE` is never the optimistic default.

# Existing systems to reuse

| Module/tool/contract | Source | Required reuse rule |
|---|---|---|
| Real Tibia module registry | `docs/agents/real-tibia/registry/**` | Sole module identity/dependency/source-of-truth. Never duplicate it. |
| Real Tibia parity governance | `docs/agents/programs/REAL_TIBIA_PARITY_PROGRAM.md` | Preserve source roles, proof layers and bounded evidence. |
| Completed TSD program | `docs/agents/programs/TIBIA_SYSTEM_DECOMPOSITION_PROGRAM.md` | Preserve 62-module inventory and `REVALIDATE` baseline; do not reopen its queue. |
| Upstream Intelligence | `docs/agents/programs/UPSTREAM_INTELLIGENCE_PROGRAM.md` | Reuse source registry and source-role-aware mapping for discovery only. |
| Universal Physical-Client E2E | PR #245; `tools/e2e/**`; `tests/e2e/**` | Add bounded scenarios; never build a second generic orchestrator. |
| OTBM analysis pipeline | existing `tools/ai-agent/**` / `docs/ai-agent/**` | Reuse canonical world/map evidence tools; no duplicate parser/renderer/index. |
| Canary ↔ OTClient contract registry | `docs/agents/CROSS_REPO_CONTRACTS.md` | Use explicit compatibility/version/rollout contracts whenever client coupling exists. |

# Active tasks

No OAM implementation task is active after OAM-002 feature completion. Lifecycle-only PR #410 archives OAM-002 and does not create OAM-003.

# Dependency-aware queue

The current canonical dependency graph requires foundation and persistence contracts before higher-level migrations. This queue is a program plan, not migration authorization.

| Package | Scope | Status | Dependencies | Exact next action |
|---|---|---|---|---|
| `OAM-001` | target architecture and migration evidence contract | completed | completed TSD + current registry | feature PR #383 merged as `9c28e52db81eb6b99a54e7700ad00288e6dbfd94`; lifecycle archived separately |
| `OAM-002` | target repository identity, authorization, default branch and exact upstream/target baseline pinning | completed | completed OAM-001 | feature PR #407 merged as `0a311d6cda6a80e31aa3a5ca9406aea7aeadd58c`; lifecycle archived by PR #410 |
| `OAM-003` | engine/build/runtime foundation revalidation | planned | completed OAM-002 | after OAM-002 lifecycle PR #410 merges, create a separate bounded task only after fresh live target/upstream baseline, ownership and overlap verification; then evaluate `build-system`, `configuration`, `engine-runtime-lifecycle`, `engine-scheduler`, `engine-service-container`, `lua-runtime`, `lua-bindings` |
| `OAM-004` | database and persistence foundation revalidation | blocked | OAM-002, OAM-003 | evaluate `database-connection`, `database-migrations`, `player-persistence`, `world-persistence` and transaction/restart evidence |
| `OAM-005` | account and character lifecycle revalidation | blocked | OAM-004 | evaluate account/auth/character lifecycle and progression boundaries |
| `OAM-006` | network/login/protocol contract revalidation | blocked | OAM-002, OAM-003, OAM-005 | pin target protocol/client compatibility and cross-repo rollout contract |
| `OAM-007` | item/world runtime foundation revalidation | blocked | OAM-003, OAM-004 | evaluate item definitions/instances and world-map/runtime boundaries before content migration |
| `OAM-008` | first low-risk canonical module migration package | blocked | OAM-002 through affected foundation packages | select exactly one module only after evidence proves a disposition stronger than `REVALIDATE` |
| `OAM-009` | target physical-client E2E proof for first migrated module | blocked | OAM-008 plus target/client compatibility | extend the existing E2E platform with one bounded target scenario |
| `OAM-010+` | dependency-ordered domain migrations | planned | proven foundation and prior package dependencies | advance one bounded canonical module/package at a time |

After foundation packages, later domain ordering is determined from the live canonical dependency graph. Expected broad waves are persistence/account/session, core world/runtime, combat, items/economy, creatures/spawns, content systems, client-facing systems and analytics/liveops, but no wave is copied mechanically when its exact dependencies indicate a different order.

# Migration package evidence gate

Every implementation package must prove, where applicable:

1. exact legacy and target SHAs;
2. exact then-current upstream Canary SHA used as target baseline;
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
- Oteryn writes require explicit repository identity and authorization before any task may claim target paths.
- Every external code baseline used for evidence must be pinned by exact SHA.
- Upstream Intelligence mapping remains a discovery hint only.

# AI and deterministic enforcement boundary

AI may correlate evidence, summarize findings, suggest reproduction steps and assist triage. AI must not automatically ban, mutate balances/items, deploy code, execute arbitrary Lua, modify production or invoke unrestricted game APIs.

Deterministic systems remain authoritative for gameplay, sanctions, economy mutation, migration execution and deployment safety.

# Dependencies and blockers

- OAM-002 target identity, default branch, write authorization, target baseline and exact upstream bootstrap source are resolved and its feature PR is merged.
- Lifecycle-only PR #410 is the final archival step for OAM-002 and contains no implementation work.
- OAM-003 is not active. After lifecycle PR #410 merges it becomes the next eligible package, but still requires a new bounded task and fresh exact live-state/ownership/baseline verification before any implementation.
- Dependency: current Real Tibia registry and generated dependency graph.
- Dependency: fresh then-current target/upstream baselines for each later bounded package.
- Dependency: merged Universal Physical-Client E2E for applicable target proof.
- Dependency: Upstream Intelligence for discovery, not authorization.

# Decisions and invariants

- The 62-module canonical registry is the migration inventory; no parallel registry will be created.
- Every module starts from `REVALIDATE` unless fresh target-side evidence proves otherwise.
- Legacy Canary remains an evidence laboratory, not the target image to clone.
- Target baseline is pinned per task/package by exact SHA and never inferred from a moving branch.
- Migration decisions are module-scoped and evidence-scoped, not directory-scoped or PR-history-scoped.
- Migration sequencing follows dependency evidence.
- Physical-client E2E complements focused/integration/runtime proof; it does not replace them.
- World-content work reuses existing OTBM tooling and never treats donor evidence as automatic map-import permission.
- A feature merge is followed by a separate lifecycle-only archive PR.

# Validation strategy

OAM-001 completed with:

- exact four-file documentation/governance diff review;
- Agent Task Ownership #1313: success on final feature head `30d2a65a3c7a104f6b6204eb4c74f88f200eaf75`;
- repository CI #2440: success;
- Fast Checks, Lua Tests, Linux release and Required: success;
- comments, reviews and unresolved review threads: none;
- mergeable immediately before merge: true;
- squash merge with exact-head guard to `9c28e52db81eb6b99a54e7700ad00288e6dbfd94`.

OAM-002 completed with:

- deterministic recursive Git-tree proof rejecting the original 32-entry manual upload against the 6326-entry pinned upstream tree;
- exact upstream bootstrap source `opentibiabr/canary@a879c9312e34381e8eedf397b8ed44510698b689`;
- target bootstrap PR #1 exact-head CI, Repository Audit and Required gate success before squash merge;
- target cleanup PR #2 exact-head CI and Required gate success before squash merge;
- final target baseline `blakinio/Otheryn@3cc7c1dfea747bb380f3761ee7ff7ac30141a115`;
- post-merge recursive tree proof showing only `required.yml` and mixed-case Docker quickstart normalization differ from pinned upstream content;
- Canary feature head `e55f78b6d708f5910907db3ce1c722d2c159a1e6` with Agent Task Ownership run 1497 success;
- latest ready-triggered Canary CI run 2633 success, including Fast Checks, Lua Tests, Linux release and Required;
- no comments, submitted reviews or unresolved review threads;
- exact three-file governance/task diff and mergeable state immediately before merge;
- feature PR #407 squash-merged with exact-head guard as `0a311d6cda6a80e31aa3a5ca9406aea7aeadd58c`;
- no canonical module disposition change and no OAM-003 implementation.

For later migration packages:

- select focused tests from `BUILD_TEST_MATRIX.md`;
- require target build/integration/runtime evidence;
- add physical-client E2E only through the existing platform where applicable;
- require cross-repository compatibility proof when client/protocol behavior is coupled.

# Handoff

## Start here

Read `AGENTS.md`, `docs/agents/README.md`, this program, `docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md`, the completed TSD program, the current canonical registry/generated indexes, all active task records and all live open PRs.

## Task creation protocol

1. Select exactly one still-valid bounded package from this queue.
2. Re-fetch live `main`, open PRs, active tasks, ownership and relevant external heads.
3. Re-verify the established target repository and pin exact current target/upstream task-start SHAs before any later target implementation.
4. Create one task, branch and draft PR with explicit exclusive/shared/read-only paths.
5. Record canonical `module_id` and dependency/evidence requirements for any migration package.
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

## Open questions

- No OAM-002 target identity or baseline fields remain unresolved.
- OAM-003 must freshly re-fetch the exact target task-start head and then-current upstream evidence before making engine/build/runtime migration decisions.

# Exact next task

After lifecycle-only PR #410 merges, `OAM-003` is the next eligible bounded task. It must be opened separately after fresh live-state, ownership/overlap and exact target/upstream baseline verification. This lifecycle PR does not create, claim or start OAM-003.
