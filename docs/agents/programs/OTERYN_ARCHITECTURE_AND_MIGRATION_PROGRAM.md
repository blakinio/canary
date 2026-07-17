---
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
name: Oteryn Architecture and Migration
status: active
owner: oteryn-architecture-migration-agent
created: 2026-07-15T15:28:18+02:00
updated: 2026-07-17T11:05:00+02:00
last_verified_commit: "e27eeefa4c3b4a6072c8c8ffda73da806fe20b9b"
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
cross_repo_contracts:
  - OTS-001
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

Re-verified through completed OAM-008 feature and lifecycle boundaries:

```text
governance/legacy repository: blakinio/canary
latest re-fetched Canary main: e27eeefa4c3b4a6072c8c8ffda73da806fe20b9b
canonical module count: 62
TSD status: completed
TSD migration disposition baseline outside bounded OAM decisions: REVALIDATE
Universal Physical-Client E2E: PR #245 merged as 9fc11e04dc5040d1ea18d02e15dac1df47f3fe64
Oteryn target repository: blakinio/Otheryn
Oteryn target default branch: main
OAM-002 clean target baseline: 3cc7c1dfea747bb380f3761ee7ff7ac30141a115
OAM-003 final target head: a9c7fabc9f4b9bbeca9fed4ab73c36309cd04e2d
OAM-004 final target head: 67212530b03c10175da2c0d9eabcee8991a05924
OAM-005 final target head: a6d42f6cec024f81a7541084425ec1d43d66d2b8
OAM-005 lifecycle merge: a1d82a5989fe9e3b7ac6c495804cb1cd83c59090
OAM-006 final target head: c547d8ad70ef1252624c255476e6cb83fa125e14
OAM-006 exact physical proof: Universal Agent E2E #118 / run 29531221365 / Required physical E2E PASS
OAM-006 Canary feature merge: c40b26ee9481ec99931347ba26897a785a7a38ca
OAM-006 lifecycle merge: b0ea0ba9508cc78d5580f44181115e9b304eb7da
OAM-007 final target head: 68c4f39f7b1b45f880543c258627b4ccf73dbc86
OAM-007 exact physical proof: Universal Agent E2E #136 / run 29559180590 / Required physical E2E PASS
OAM-007 Canary feature merge: be9760a88d0c714dfd3e1b6a659e373380d03d65
OAM-007 lifecycle merge: 317c1c4235377c388883aa2fd425d324f8ce4d2e
OAM-008 Canary task-start: 317c1c4235377c388883aa2fd425d324f8ce4d2e
OAM-008 target task-start: 68c4f39f7b1b45f880543c258627b4ccf73dbc86
OAM-008 upstream evidence: opentibiabr/canary@e0ac98e399d0f7e483f3668f57b78fcc45b6e53f
OAM-008 canonical module: vocations
OAM-008 target PR final head: 9453a1754501ce183e20d294df1064a5ccbad54c
OAM-008 final target head: f59a58426b4d3910ba0cdc0d2332c24f31a1db4f
OAM-008 target focused proof: CI #88 / Required #84 / autofix #77 PASS; both VocationsTest cases executed and passed
OAM-008 Canary feature merge: acdddd924fed170da51a8a54114607842f0cbb68
OAM-008 lifecycle archive merge: e27eeefa4c3b4a6072c8c8ffda73da806fe20b9b
OAM-009 implementation: not created and not started
target write authorization: explicitly granted by the user for autonomous OAM writes
```

OAM-001 completed the durable target architecture contract and was lifecycle archived separately.

OAM-002 established the authorized target identity/baseline and completed feature + lifecycle governance.

OAM-003 revalidated seven engine-foundation modules and completed target, feature-governance and lifecycle delivery.

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

OAM-004 completed database/persistence foundation revalidation with:

```text
database-connection ADAPT
database-migrations ADAPT
player-persistence  ADAPT
world-persistence   ADAPT
```

OAM-005 completed account/character lifecycle revalidation with:

```text
account-lifecycle       REUSE
account-authentication  ADAPT
character-lifecycle     ADAPT
```

OAM-006 completed the bounded `protocol` package with `ADAPT`, final target `c547d8ad70ef1252624c255476e6cb83fa125e14`, exact heavy E2E #118, feature merge `c40b26ee9481ec99931347ba26897a785a7a38ca` and lifecycle merge `b0ea0ba9508cc78d5580f44181115e9b304eb7da`.

OAM-007 completed item/world runtime foundation revalidation with:

```text
item-definitions  ADAPT
item-instances    REUSE
world-map-runtime REUSE
```

Its final target is `68c4f39f7b1b45f880543c258627b4ccf73dbc86`, exact heavy E2E #136 passed, feature governance merged as `be9760a88d0c714dfd3e1b6a659e373380d03d65`, and lifecycle merged as `317c1c4235377c388883aa2fd425d324f8ce4d2e`.

OAM-008 selected exactly one low-risk canonical module: `vocations`. Canonical `vocation.cpp`, `vocation.hpp` and `data/XML/vocations.xml` were exact-blob identical across task-start target, legacy and upstream. Exact blob identity alone was not accepted as authorization: proof-only Otheryn PR #25 added focused acceptance tests, final head `9453a1754501ce183e20d294df1064a5ccbad54c` passed autofix #77, CI #88 and Required #84, Linux debug `Run Tests` passed, and both `VocationsTest` cases were executed and passed. The target PR had zero comments, zero submitted reviews and zero unresolved review threads and squash-merged as `f59a58426b4d3910ba0cdc0d2332c24f31a1db4f`. Canary feature-governance PR #469 exact head `c5c53dcbacabe48c08ebaf70f0a0622f70784aa6` passed Ownership #1970, draft CI #3111 and ready CI #3112 with clean review state and squash-merged as `acdddd924fed170da51a8a54114607842f0cbb68`. Post-merge lifecycle automation archived the task through PR #472, merged as `e27eeefa4c3b4a6072c8c8ffda73da806fe20b9b`.

OAM-008 disposition is:

```text
vocations REUSE
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
| OAM-004 final target head | `67212530b03c10175da2c0d9eabcee8991a05924` | TARGET + LIFECYCLE COMPLETE |
| OAM-005 final target head | `a6d42f6cec024f81a7541084425ec1d43d66d2b8` | TARGET + FEATURE + LIFECYCLE COMPLETE |
| OAM-006 final target head | `c547d8ad70ef1252624c255476e6cb83fa125e14` | TARGET + FEATURE + LIFECYCLE COMPLETE |
| OAM-006 exact physical proof | Universal Agent E2E #118 (`29531221365`) | REQUIRED PHYSICAL E2E PASS |
| OAM-006 lifecycle merge | `b0ea0ba9508cc78d5580f44181115e9b304eb7da` | COMPLETE |
| OAM-007 final target head | `68c4f39f7b1b45f880543c258627b4ccf73dbc86` | TARGET DELIVERY COMPLETE |
| OAM-007 exact physical proof | Universal Agent E2E #136 (`29559180590`) | REQUIRED PHYSICAL E2E PASS |
| OAM-007 lifecycle merge | `317c1c4235377c388883aa2fd425d324f8ce4d2e` | COMPLETE |
| OAM-008 target task-start | `68c4f39f7b1b45f880543c258627b4ccf73dbc86` | PINNED |
| OAM-008 canonical module | `vocations` | REUSE |
| OAM-008 final target head | `f59a58426b4d3910ba0cdc0d2332c24f31a1db4f` | TARGET PROOF DELIVERY COMPLETE |
| OAM-008 focused target proof | CI #88 / Required #84 / autofix #77 | PASS |
| OAM-008 Canary feature governance | PR #469 → `acdddd924fed170da51a8a54114607842f0cbb68` | MERGED |
| OAM-008 lifecycle archive | PR #472 → `e27eeefa4c3b4a6072c8c8ffda73da806fe20b9b` | COMPLETE |
| target write authorization | explicit user authorization for autonomous OAM writes to `blakinio/Otheryn` | ESTABLISHED |

Every future package must re-fetch and pin fresh task-start baselines. OAM-009 must not treat OAM-008 delivery or any current main as an unverified moving-state assumption.

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
| Universal Physical-Client E2E | PR #245; `tools/e2e/**`; `tests/e2e/**`; OAM-006 controlled-server extension | Reuse in-place; never build a second generic orchestrator. |
| OTBM analysis pipeline | existing `tools/ai-agent/**` / `docs/ai-agent/**` | Reuse canonical world/map evidence tools. |
| Canary ↔ OTClient contract registry | `docs/agents/CROSS_REPO_CONTRACTS.md` | Use explicit compatibility/version/rollout contracts when client coupling exists. |
| OAM-003 engine-foundation report | `docs/agents/OTERYN_OAM_003_ENGINE_FOUNDATION_REVALIDATION.md` | Durable OAM-003 evidence. |
| OAM-004 persistence-foundation report | `docs/agents/OTERYN_OAM_004_PERSISTENCE_FOUNDATION_REVALIDATION.md` | Durable OAM-004 evidence. |
| OAM-005 account/character lifecycle report | `docs/agents/OTERYN_OAM_005_ACCOUNT_CHARACTER_LIFECYCLE_REVALIDATION.md` | Durable OAM-005 evidence. |
| OAM-006 network/login/protocol report | `docs/agents/OTERYN_OAM_006_NETWORK_LOGIN_PROTOCOL_REVALIDATION.md` | Durable OAM-006 evidence. |
| OAM-007 item/world runtime report | `docs/agents/OTERYN_OAM_007_ITEM_WORLD_RUNTIME_REVALIDATION.md` | Durable OAM-007 evidence. |
| OAM-008 vocations migration report | `docs/agents/OTERYN_OAM_008_VOCATIONS_MIGRATION.md` | Durable evidence for first low-risk module selection, exact canonical identity, focused target proof and `vocations` `REUSE`. |

# Active tasks

No OAM implementation task is active. OAM-008 is feature and lifecycle complete; its task is archived under `docs/agents/tasks/archive/`.

`OAM-009` is the next eligible package but is not active and is not created or started in this completion record. It still requires a fresh live-state, exact Otheryn/client baselines and one bounded physical-client scenario definition before task creation.

# Dependency-aware queue

| Package | Scope | Status | Dependencies | Exact next action |
|---|---|---|---|---|
| `OAM-001` | target architecture and migration evidence contract | completed | completed TSD + current registry | merged and lifecycle archived |
| `OAM-002` | target repository identity, authorization and exact baseline pinning | completed | OAM-001 | feature + lifecycle completed |
| `OAM-003` | engine/build/runtime foundation revalidation | completed | OAM-002 | feature + lifecycle completed |
| `OAM-004` | database and persistence foundation revalidation | completed | completed OAM-003 lifecycle | target, feature governance and lifecycle complete |
| `OAM-005` | account and character lifecycle revalidation | completed | completed OAM-004 feature + lifecycle | target, feature governance and lifecycle complete |
| `OAM-006` | network/login/protocol contract revalidation | completed | completed OAM-005 feature + lifecycle | target, exact E2E, feature governance and lifecycle complete |
| `OAM-007` | item/world runtime foundation revalidation | completed | completed OAM-006 lifecycle | target, exact E2E, feature governance and lifecycle complete |
| `OAM-008` | first low-risk canonical module migration package: `vocations` | completed | completed OAM-007 lifecycle | target proof, feature merge `acdddd924fed170da51a8a54114607842f0cbb68` and lifecycle archive `e27eeefa4c3b4a6072c8c8ffda73da806fe20b9b` complete |
| `OAM-009` | target physical-client E2E proof for first migrated module | planned | completed OAM-008 lifecycle plus target/client compatibility | after this program completion record merges, re-fetch exact target/client state and define one bounded scenario using existing Universal Agent E2E |
| `OAM-010+` | dependency-ordered domain migrations | planned | proven foundation and prior package dependencies | advance one bounded package at a time |

OAM-008 is fully complete. OAM-009 is next eligible but remains not created and not started until a fresh preflight after this completion record.

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
- A consumer repository need not be mutated merely to mirror a registry entry when the exact consumer commit is unchanged and compatibility is proven; the governance registry must still pin the exact producer/consumer pair and rollout behavior.

# AI and deterministic enforcement boundary

AI may correlate evidence, summarize findings, suggest reproduction steps and assist triage. Deterministic systems remain authoritative for gameplay, sanctions, economy mutation, migration execution and deployment safety.

# Dependencies and blockers

- OAM-001 through OAM-008 are feature and lifecycle complete.
- OAM-008 selected exactly one canonical module, `vocations`, with final disposition `REUSE`.
- OAM-008 exact task-start baselines are Canary `317c1c4235377c388883aa2fd425d324f8ce4d2e`, Otheryn `68c4f39f7b1b45f880543c258627b4ccf73dbc86` and upstream `e0ac98e399d0f7e483f3668f57b78fcc45b6e53f`.
- The three canonical vocation paths were exact-blob identical across task-start target, legacy and upstream.
- Otheryn PR #25 changed only test registration and focused vocation tests; no canonical vocation implementation or XML changed.
- Otheryn PR #25 final head `9453a1754501ce183e20d294df1064a5ccbad54c` passed autofix #77, CI #88 and Required #84; both focused vocation tests executed and passed.
- Otheryn PR #25 squash-merged as `f59a58426b4d3910ba0cdc0d2332c24f31a1db4f`.
- Canary PR #469 final head `c5c53dcbacabe48c08ebaf70f0a0622f70784aa6` passed Ownership #1970, draft CI #3111 and ready CI #3112 with clean review state and squash-merged as `acdddd924fed170da51a8a54114607842f0cbb68`.
- Post-merge lifecycle automation PR #472 archived the OAM-008 task and merged as `e27eeefa4c3b4a6072c8c8ffda73da806fe20b9b`.
- OAM-009 is next eligible only after this completion program record merges and a fresh exact target/client preflight is performed.
- OAM-004 residual gaps remain explicit: player SQL commit and later KV flush are non-atomic; generic KV eviction persistence failure handling is outside OAM-004D; untouched crash/restart recovery and generic DDL reversibility remain unproven.

# Decisions and invariants

- The canonical registry is the migration inventory; no parallel registry will be created.
- A module remains `REVALIDATE` unless a bounded package records/proves another disposition.
- Legacy Canary remains evidence, not a target image to clone.
- Baselines are pinned per task/package by exact SHA.
- Migration decisions are module/evidence scoped, not directory/PR-history scoped.
- Migration sequencing follows dependency evidence.
- Physical-client E2E complements, not replaces, focused/integration/runtime proof.
- Exact controlled-server E2E must record the actual producer revision; a Canary-only or incrementally reused run cannot substitute for an exact-target proof.
- Every feature merge is followed by separate lifecycle-only archival.
- Target delivery completion does not by itself authorize the next package; lifecycle completion remains required.
- A next-eligible package is not an active package; it still requires a new bounded task and fresh exact evidence.
- Exact blob identity is not sufficient by itself for `REUSE`; OAM-008 required focused target test execution and full target compatibility gates.
- A scope-skipped green aggregate is not accepted as focused behavior proof.

# Validation strategy

OAM-001 through OAM-007 completed their bounded feature/lifecycle packages under the sequencing contract.

OAM-008 completed with:

- exactly one canonical module: `vocations`;
- final disposition `REUSE`;
- identical canonical blobs across task-start target, legacy and upstream;
- target PR #25 exact final head `9453a1754501ce183e20d294df1064a5ccbad54c`;
- autofix #77, full CI #88 and Required #84 success;
- both focused `VocationsTest` cases executed and passed;
- target proof-only merge `f59a58426b4d3910ba0cdc0d2332c24f31a1db4f`;
- Canary feature PR #469 exact head `c5c53dcbacabe48c08ebaf70f0a0622f70784aa6` with Ownership #1970, draft CI #3111 and ready CI #3112 success;
- Canary feature merge `acdddd924fed170da51a8a54114607842f0cbb68`;
- post-merge lifecycle archive PR #472 merged as `e27eeefa4c3b4a6072c8c8ffda73da806fe20b9b`;
- no canonical vocation code/data mutation, no maintained-client mutation and no physical-client proof claim inside OAM-008.

This program-only completion record reconciles the already-merged automated lifecycle archive with the durable Oteryn queue. After it merges, OAM-009 may undergo a fresh bounded preflight.

# Handoff

## Start here

Read `AGENTS.md`, `docs/agents/README.md`, this program, `docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md`, `docs/agents/OTERYN_OAM_008_VOCATIONS_MIGRATION.md`, `docs/agents/CROSS_REPO_CONTRACTS.md`, the current canonical registry/generated indexes, archived OAM task records, all active task records and live open PRs.

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
- Do not infer `REUSE` from code presence or exact blob identity alone.
- Do not bulk-copy legacy Canary.
- Do not invent target repository/baselines.
- Do not re-enable MySQL automatic reconnect or arbitrary SQL statement replay.
- Do not infer persistence safety from `DBTransaction` existence.
- Do not claim player SQL + KV atomicity.
- Do not restore whole legacy `IOLoginData` over OAM-004D target persistence changes.
- Do not merge speculative OTClient transport hardening from closed PR #11.
- Do not mutate canonical vocation implementation/data merely to force a migration diff when exact target content is already reusable.
- Do not accept scope-skipped CI as focused OAM-008 behavior proof.
- Do not start OAM-009 before fresh exact target/client preflight.

## Known gaps carried forward

- Complete child `LuaScriptInterface` reconstruction/reload semantics.
- Untouched polymorphic Lua userdata safety.
- Concurrent configuration reload correctness under arbitrary future target consumers.
- Broader incremental removal of contextual/global DI access.
- Player SQL commit followed by later durable KV flush remains non-atomic.
- Generic KV eviction persistence failure handling remains outside OAM-004D.
- Complete crash/restart recovery semantics for untouched persistence paths remain unproven.
- Generic DDL reversibility remains unproven.
- OAM-006 exact physical proof does not claim exhaustive physical coverage of every old-protocol profile.
- OAM-007 does not claim Real Tibia item value/appearance parity, map completeness or exhaustive movement/pathfinding correctness.
- OAM-008 does not claim Real Tibia vocation value parity, combat formula parity, spell/weapon eligibility or Wheel behavior.
- OAM-008 does not include physical-client E2E; OAM-009 remains the separate proof boundary.

# Exact next task

Merge this program-only OAM-008 lifecycle completion record after exact-head ownership/CI/review gates. Then `OAM-009 — target physical-client E2E proof for first migrated module` becomes next eligible but remains not created until a fresh live-state and exact Otheryn/client preflight defines one bounded scenario using the existing Universal Agent E2E platform.
