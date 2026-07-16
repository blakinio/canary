---
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
name: Oteryn Architecture and Migration
status: active
owner: oteryn-architecture-migration-agent
created: 2026-07-15T15:28:18+02:00
updated: 2026-07-16T20:20:00+02:00
last_verified_commit: "e7f7b9601d41436a105308efa933f16917bc1b39"
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

Re-verified through OAM-005 target delivery and current Canary governance integration state:

```text
governance/legacy repository: blakinio/canary
latest re-fetched Canary main: e7f7b9601d41436a105308efa933f16917bc1b39
canonical module count: 62
TSD status: completed
TSD migration disposition baseline outside bounded OAM decisions: REVALIDATE
Universal Physical-Client E2E: PR #245 merged as 9fc11e04dc5040d1ea18d02e15dac1df47f3fe64
Oteryn target repository: blakinio/Otheryn
Oteryn target default branch: main
OAM-002 clean target baseline: 3cc7c1dfea747bb380f3761ee7ff7ac30141a115
OAM-003 final target head: a9c7fabc9f4b9bbeca9fed4ab73c36309cd04e2d
OAM-003 Canary feature merge: 780704f3b77c459f852319a249425614b21246fd
OAM-004 final target head: 67212530b03c10175da2c0d9eabcee8991a05924
OAM-004 Canary feature merge: 0507fc5de8049d712345f43db0b05a23a6577a8a
OAM-004 lifecycle merge: 91d2b64ae914ef5d53d52dae873bcd2a71633371
OAM-005 Canary task-start: c2ffe09dc8753734be00c3433fab6f2ebe25d2e8
OAM-005 Canary integration base: 0f25e7fd4d41e90f17fc95d13dba84b7e81d1681
OAM-005 upstream evidence: opentibiabr/canary@e0ac98e399d0f7e483f3668f57b78fcc45b6e53f
OAM-005 target task-start: 67212530b03c10175da2c0d9eabcee8991a05924
OAM-005 target PR #19 head: 2a2e1e5e22df697435e705d8a19d69dcbc46bbfd
OAM-005 final target head: a6d42f6cec024f81a7541084425ec1d43d66d2b8
OAM-005 Canary governance PR: #432
target write authorization: explicitly granted by the user for autonomous OAM writes
```

OAM-001 completed the durable target architecture contract and was lifecycle archived separately.

OAM-002 established the authorized target identity/baseline and completed feature + lifecycle governance.

OAM-003 revalidated seven engine-foundation modules, delivered two bounded target adaptation slices, merged Canary feature PR #411 as `780704f3b77c459f852319a249425614b21246fd`, and completed its separate lifecycle archival before OAM-004 started.

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

OAM-004 revalidated four database/persistence foundation modules, completed target delivery at `blakinio/Otheryn@67212530b03c10175da2c0d9eabcee8991a05924`, merged Canary feature-governance PR #420 as `0507fc5de8049d712345f43db0b05a23a6577a8a`, and completed separate lifecycle archival as `91d2b64ae914ef5d53d52dae873bcd2a71633371`.

OAM-004 dispositions are:

```text
database-connection ADAPT
database-migrations ADAPT
player-persistence  ADAPT
world-persistence   ADAPT
```

OAM-005 revalidated the bounded account/character lifecycle foundation. Target delivery is complete at `blakinio/Otheryn@a6d42f6cec024f81a7541084425ec1d43d66d2b8`; Canary feature governance and a separate lifecycle archive remain required before OAM-006 becomes eligible.

OAM-005 dispositions are:

```text
account-lifecycle       REUSE
account-authentication  ADAPT
character-lifecycle     ADAPT
```

The OAM-005 target adaptation adds only the reusable secure login-session primitive. It does not make that primitive live on the login/game wire; protocol/session-key transport and maintained-client compatibility remain OAM-006 responsibilities.

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
| OAM-004 final target head | `67212530b03c10175da2c0d9eabcee8991a05924` | TARGET + LIFECYCLE COMPLETE |
| OAM-005 target task-start | `67212530b03c10175da2c0d9eabcee8991a05924` | PINNED |
| OAM-005 final target head | `a6d42f6cec024f81a7541084425ec1d43d66d2b8` | TARGET DELIVERY COMPLETE |
| OAM-005 upstream evidence | `opentibiabr/canary@e0ac98e399d0f7e483f3668f57b78fcc45b6e53f` | PINNED FOR OAM-005 |
| target write authorization | explicit user authorization for autonomous OAM writes to `blakinio/Otheryn` | ESTABLISHED |

Every future package must re-fetch and pin fresh task-start baselines; OAM-006 must not treat the OAM-005 final head as an unverified moving-current-state assumption.

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
| OAM-004 persistence-foundation report | `docs/agents/OTERYN_OAM_004_PERSISTENCE_FOUNDATION_REVALIDATION.md` | Durable evidence for four OAM-004 `ADAPT` decisions and delivered target persistence seams. |
| OAM-005 account/character lifecycle report | `docs/agents/OTERYN_OAM_005_ACCOUNT_CHARACTER_LIFECYCLE_REVALIDATION.md` | Durable evidence for OAM-005 `REUSE`/`ADAPT` decisions and the bounded login-session primitive. |

# Active tasks

`OAM-005 — account and character lifecycle revalidation` is the only active OAM package. Its target delivery is complete at `a6d42f6cec024f81a7541084425ec1d43d66d2b8`; its active task is `ready`, and Canary PR #432 is the feature-governance merge vehicle.

OAM-006 is not active and must not be created or started until PR #432 merges and a separate OAM-005 lifecycle-only archive PR also merges.

# Dependency-aware queue

| Package | Scope | Status | Dependencies | Exact next action |
|---|---|---|---|---|
| `OAM-001` | target architecture and migration evidence contract | completed | completed TSD + current registry | merged and lifecycle archived |
| `OAM-002` | target repository identity, authorization and exact baseline pinning | completed | OAM-001 | feature + lifecycle completed |
| `OAM-003` | engine/build/runtime foundation revalidation | completed | OAM-002 | feature PR #411 merged as `780704f3b77c459f852319a249425614b21246fd`; lifecycle archived separately |
| `OAM-004` | database and persistence foundation revalidation | completed | completed OAM-003 lifecycle | target, feature governance and lifecycle complete |
| `OAM-005` | account and character lifecycle revalidation | ready | completed OAM-004 feature + lifecycle | target delivery complete at `a6d42f6cec024f81a7541084425ec1d43d66d2b8`; merge Canary feature PR #432, then complete a separate lifecycle-only archive PR |
| `OAM-006` | network/login/protocol contract revalidation | blocked | completed OAM-005 feature + lifecycle | after OAM-005 lifecycle merge only, become the next eligible bounded package; do not auto-start |
| `OAM-007` | item/world runtime foundation revalidation | blocked | OAM-003, OAM-004 | evaluate item definitions/instances and world-map/runtime boundaries before content migration |
| `OAM-008` | first low-risk canonical module migration package | blocked | affected foundation packages | select exactly one module after dependencies and evidence gates are complete |
| `OAM-009` | target physical-client E2E proof for first migrated module | blocked | OAM-008 plus target/client compatibility | extend existing E2E platform with one bounded target scenario |
| `OAM-010+` | dependency-ordered domain migrations | planned | proven foundation and prior package dependencies | advance one bounded package at a time |

OAM-005 target delivery is complete, but OAM-005 is not lifecycle-complete. OAM-006 remains blocked until both the OAM-005 Canary feature merge and the separate lifecycle archive merge complete.

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
- OAM-003 feature and lifecycle work are complete.
- OAM-004 feature and lifecycle work are complete; final target `67212530b03c10175da2c0d9eabcee8991a05924` remains the OAM-005 task-start target.
- OAM-005 `account-lifecycle` is `REUSE` based on exact task-start cross-repository blob evidence for the checked account core.
- OAM-005 `account-authentication` is `ADAPT`; Otheryn PR #19 merged as `a6d42f6cec024f81a7541084425ec1d43d66d2b8` after exact-head CI #76, Required #75 and autofix.ci #68 passed.
- OAM-005 `character-lifecycle` is `ADAPT`; OAM-004D persistence semantics remain authoritative and must not be replaced by a wholesale legacy `IOLoginData` copy.
- `Otheryn:main` is pinned and verified at `a6d42f6cec024f81a7541084425ec1d43d66d2b8` for final OAM-005 target delivery.
- Otheryn issue #17 is closed as completed; parent issue #15 remains open until OAM-005 governance/lifecycle completion.
- Canary PR #432 must complete its final exact-head ownership/CI/review gate and feature merge.
- A separate lifecycle-only PR must then archive the OAM-005 task and mark OAM-005 completed in this queue.
- OAM-006 remains blocked until that lifecycle PR merges.
- The secure login-session primitive is not live on the wire until OAM-006 integrates and proves exact protocol/session/client compatibility.
- OAM-004 residual gaps remain explicit: player SQL commit and later KV flush are non-atomic; generic KV eviction persistence failure handling is outside OAM-004D; untouched crash/restart recovery and generic DDL reversibility remain unproven.
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
- Target delivery completion does not by itself authorize the next package; lifecycle completion remains required.
- A next-eligible package is not an active package; it still requires a new bounded task and fresh exact evidence.
- A reusable authentication primitive is not evidence that live protocol/client authentication is complete.

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
- separate lifecycle archival before OAM-004 start.

OAM-004 completed with:

- four canonical modules revalidated as `ADAPT`;
- OAM-004A transaction-integrity PR #11 merged as `45ffe6afb915746c69125c9e74f5513c0cecdec4`;
- OAM-004B fail-closed migration PR #12 merged as `1fe44d165fd8637e29ece62b261b7caa33895c65`;
- OAM-004C world-save propagation PR #13 merged as `4b5b94eced0f3c5d88b9a4293e849d888333e0cb`;
- OAM-004D PR #14 merged as `67212530b03c10175da2c0d9eabcee8991a05924` after exact-head CI/Required/autofix and clean review gates;
- Canary PR #420 merged as `0507fc5de8049d712345f43db0b05a23a6577a8a` after exact-head ownership/CI/review gates;
- separate lifecycle PR #428 merged as `91d2b64ae914ef5d53d52dae873bcd2a71633371`;
- no claim of player SQL + KV atomicity and no generic KV subsystem redesign.

OAM-005 target delivery completed with:

- `account-lifecycle` → `REUSE`;
- `account-authentication` → `ADAPT`;
- `character-lifecycle` → `ADAPT`;
- exact account core blob evidence across task-start legacy/target/upstream revisions;
- bounded login-session primitive target PR #19 exact head `2a2e1e5e22df697435e705d8a19d69dcbc46bbfd`;
- ready-triggered CI #76, Required #75 and autofix.ci #68 success;
- Linux release, Linux debug tests, macOS and Windows gates success;
- zero PR comments, submitted reviews or unresolved review threads at final target merge gate;
- PR #19 squash-merged with exact-head guard as `a6d42f6cec024f81a7541084425ec1d43d66d2b8`;
- `Otheryn:main` verified identical to `a6d42f6cec024f81a7541084425ec1d43d66d2b8`;
- no ProtocolLogin/ProtocolGame/packet-layout integration and no rollback of OAM-004D persistence semantics.

Canary PR #432 must now pass its own refreshed exact-head ownership, ready-triggered final CI and clean review gates before feature merge. A separate lifecycle-only archive must pass its own gate afterward.

# Handoff

## Start here

Read `AGENTS.md`, `docs/agents/README.md`, this program, `docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md`, `docs/agents/OTERYN_OAM_005_ACCOUNT_CHARACTER_LIFECYCLE_REVALIDATION.md`, the current canonical registry/generated indexes, all active task records and live open PRs.

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
- Do not re-enable MySQL automatic reconnect or arbitrary SQL statement replay.
- Do not infer persistence safety from `DBTransaction` existence.
- Do not claim player SQL + KV atomicity.
- Do not restore whole legacy `IOLoginData` over OAM-004D target persistence changes.
- Do not claim `LoginSessionManager` is live authentication before OAM-006 wire integration.
- Do not start OAM-006 before OAM-005 feature and lifecycle completion.

## Known gaps carried forward

- Complete child `LuaScriptInterface` reconstruction/reload semantics.
- Untouched polymorphic Lua userdata safety.
- Concurrent configuration reload correctness under arbitrary future target consumers.
- Broader incremental removal of contextual/global DI access.
- Player SQL commit followed by later durable KV flush remains non-atomic.
- Generic KV eviction persistence failure handling remains outside OAM-004D.
- Complete crash/restart recovery semantics for untouched persistence paths remain unproven.
- Generic DDL reversibility remains unproven.
- OAM-005 login-session primitive remains unwired to live login/game protocol flow until OAM-006.
- Old-protocol compatibility, modern session-key transport and maintained-client rollout remain unproven for the OAM-006 boundary.

# Exact next task

Finalize Canary PR #432: verify exact changed files and ownership, use the refreshed exact-head ownership/CI state, mark it ready, require the latest ready-triggered final-head gate plus clean comments/reviews/unresolved-thread state, and squash-merge with exact-head guard. Then create and merge a separate lifecycle-only PR that moves the OAM-005 task from `tasks/active` to `tasks/archive` and marks OAM-005 completed in this queue. Only after that lifecycle merge may OAM-006 become the next eligible bounded package; it must not be auto-created or started by the OAM-005 feature PR.
