---
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
name: Oteryn Architecture and Migration
status: active
owner: oteryn-architecture-migration-agent
created: 2026-07-15T15:28:18+02:00
updated: 2026-07-15T15:53:27+02:00
last_verified_commit: "9c28e52db81eb6b99a54e7700ad00288e6dbfd94"
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

Verified at program bootstrap from live GitHub:

```text
writable repository: blakinio/canary
main SHA: d60d63dc37689ccc9ff7e9c37cfa2ebe71cbdc51
open PRs: #316 only
canonical module count: 62
TSD status: completed
TSD migration disposition baseline: ALL_CANONICAL_MODULES -> REVALIDATE
Upstream Intelligence: active; UI-001/UI-001A completed; UI-002 planned
Universal Physical-Client E2E: PR #245 merged as 9fc11e04dc5040d1ea18d02e15dac1df47f3fe64
Oteryn repository availability: unavailable
Oteryn target default branch: unavailable
Oteryn target baseline SHA: unavailable
```

PR #316 is an independent Targuna donor-cluster audit. Its paths and ownership are read-only to this program and its evidence cannot become final migration proof without merge and fresh revalidation.

The merged E2E platform remains the single reusable physical-client orchestration. Its stale active task record was archived by independent lifecycle-only PR #382, merged as `63fbacc9ab2d31b480de9d756194e22ce22b7d35`.

OAM-001 feature PR #383 was squash-merged as `9c28e52db81eb6b99a54e7700ad00288e6dbfd94` after current-head ownership and required CI passed. The target repository identity, default branch, baseline SHA and write authorization remain unavailable.

# Target architecture contract

The authoritative contract for this program is:

```text
docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
```

No migration implementation may start until the contract's required target identity and baseline fields are resolved for the affected package.

# Target repository status

The program does not invent a target repository.

Current state:

| Field | Value | Status |
|---|---|---|
| target repository | unavailable | BLOCKED |
| target default branch | unavailable | BLOCKED |
| exact target baseline SHA | unavailable | BLOCKED |
| upstream parent/baseline | must be then-current `opentibiabr/canary` pinned by exact SHA when OAM-002 starts | UNPINNED |
| target write authorization | unavailable | BLOCKED |

Until these fields are resolved, Oteryn work is architecture/governance only.

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

No OAM implementation task is active after OAM-001 lifecycle completion. `OAM-002` remains blocked and must not be opened until an authorized Oteryn target repository is explicitly designated or created and exact baseline inputs can be pinned.

# Dependency-aware queue

The current canonical dependency graph requires foundation and persistence contracts before higher-level migrations. This queue is a program plan, not migration authorization.

| Package | Scope | Status | Dependencies | Exact next action |
|---|---|---|---|---|
| `OAM-001` | target architecture and migration evidence contract | completed | completed TSD + current registry | feature PR #383 merged as `9c28e52db81eb6b99a54e7700ad00288e6dbfd94`; lifecycle archived separately |
| `OAM-002` | target repository identity, authorization, default branch and exact upstream/target baseline pinning | blocked | completed OAM-001; Oteryn repository must exist | designate/create authorized Oteryn target outside this program's current write scope, then pin exact SHA |
| `OAM-003` | engine/build/runtime foundation revalidation | blocked | OAM-002 | evaluate `build-system`, `configuration`, `engine-runtime-lifecycle`, `engine-scheduler`, `engine-service-container`, `lua-runtime`, `lua-bindings` against target |
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

- `blakinio/canary` is the only writable repository in the current program context.
- `opentibiabr/canary`, `opentibiabr/otclient`, `opentibiabr/remeres-map-editor` and `opentibiabr/client-editor` are read-only references.
- Donor repositories are read-only comparison sources and are not official Real Tibia authorities.
- Oteryn writes require explicit repository identity and authorization before any task may claim target paths.
- Every external code baseline used for evidence must be pinned by exact SHA.
- Upstream Intelligence mapping remains a discovery hint only.

# AI and deterministic enforcement boundary

AI may correlate evidence, summarize findings, suggest reproduction steps and assist triage. AI must not automatically ban, mutate balances/items, deploy code, execute arbitrary Lua, modify production or invoke unrestricted game APIs.

Deterministic systems remain authoritative for gameplay, sanctions, economy mutation, migration execution and deployment safety.

# Dependencies and blockers

- Blocker: no accessible Oteryn repository identity.
- Blocker: no Oteryn default branch.
- Blocker: no exact Oteryn target baseline SHA.
- Blocker: no write authorization for an Oteryn repository in the current repository allowlist.
- Dependency: current Real Tibia registry and generated dependency graph.
- Dependency: then-current upstream Canary when OAM-002 begins.
- Dependency: merged Universal Physical-Client E2E for target proof.
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
3. Resolve target repository identity and exact baseline before any target implementation.
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

- Which repository is the authorized Oteryn target?
- What is its default branch?
- What exact then-current `opentibiabr/canary` SHA will seed the target baseline?
- What exact Oteryn target SHA will OAM-002 pin after the repository exists?

# Exact next task

`OAM-002` is the next bounded task after OAM-001 lifecycle completion, but it is blocked until an authorized Oteryn repository exists or an existing target is explicitly designated. The next task must not be opened by guessing repository identity or creating a repository outside explicit ownership.
