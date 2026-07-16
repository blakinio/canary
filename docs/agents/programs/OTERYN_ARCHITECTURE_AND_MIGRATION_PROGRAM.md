---
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
name: Oteryn Architecture and Migration
status: active
owner: oteryn-architecture-migration-agent
created: 2026-07-15T15:28:18+02:00
updated: 2026-07-16T22:53:00+02:00
last_verified_commit: "02d1b08162a3ad17d6283af16ad481f29c4ec213"
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

Re-verified through OAM-006 target delivery and exact controlled-server physical-client proof:

```text
governance/legacy repository: blakinio/canary
latest re-fetched Canary main: 02d1b08162a3ad17d6283af16ad481f29c4ec213
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
OAM-005 target task-start: 67212530b03c10175da2c0d9eabcee8991a05924
OAM-005 final target head: a6d42f6cec024f81a7541084425ec1d43d66d2b8
OAM-005 Canary feature merge: 6374230a40b70d3e0cffe8d93a3171393ece7cd7
OAM-005 lifecycle merge: a1d82a5989fe9e3b7ac6c495804cb1cd83c59090
OAM-006 Canary task-start: a1d82a5989fe9e3b7ac6c495804cb1cd83c59090
OAM-006 upstream evidence: opentibiabr/canary@e0ac98e399d0f7e483f3668f57b78fcc45b6e53f
OAM-006 target task-start: a6d42f6cec024f81a7541084425ec1d43d66d2b8
OAM-006 target PR final head: 5342b374306abb44b6b5e201c85f6a0182c99286
OAM-006 final target head: c547d8ad70ef1252624c255476e6cb83fa125e14
OAM-006 maintained client: blakinio/otclient@2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
OAM-006 exact physical proof: Universal Agent E2E #118 / run 29531221365 / Required physical E2E PASS
OAM-006 cross-repo contract: OTS-001
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

OAM-004 revalidated four database/persistence foundation modules and completed target, feature-governance and lifecycle delivery.

OAM-004 dispositions are:

```text
database-connection ADAPT
database-migrations ADAPT
player-persistence  ADAPT
world-persistence   ADAPT
```

OAM-005 revalidated the bounded account/character lifecycle foundation and completed target, feature-governance and lifecycle delivery.

OAM-005 dispositions are:

```text
account-lifecycle       REUSE
account-authentication  ADAPT
character-lifecycle     ADAPT
```

OAM-006 revalidated the bounded `protocol` module and selected `ADAPT`. Target PR #21 wired the OAM-005 secure login-session primitive into the supported modern login/game handoff without replacing `IOLoginData`, removing fallbacks or mutating the maintained client. The target squash-merged as `c547d8ad70ef1252624c255476e6cb83fa125e14` after exact-head gates, and Universal Agent E2E #118 proved the exact final target against maintained OTClient `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f` with full heavy `login/relog` and `Required physical E2E` success.

OAM-006 disposition is:

```text
protocol ADAPT
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
| OAM-006 target task-start | `a6d42f6cec024f81a7541084425ec1d43d66d2b8` | PINNED |
| OAM-006 final target head | `c547d8ad70ef1252624c255476e6cb83fa125e14` | TARGET DELIVERY COMPLETE |
| OAM-006 maintained client | `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f` | PINNED + UNCHANGED |
| OAM-006 exact physical proof | Universal Agent E2E #118 (`29531221365`) | REQUIRED PHYSICAL E2E PASS |
| OAM-006 cross-repo contract | `OTS-001` | VERIFIED |
| OAM-006 Canary feature governance | PR #436 | READY FOR FINAL GATES |
| target write authorization | explicit user authorization for autonomous OAM writes to `blakinio/Otheryn` | ESTABLISHED |

Every future package must re-fetch and pin fresh task-start baselines. OAM-007 must not treat OAM-006 delivery or any current main as an unverified moving-state assumption.

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
| Universal Physical-Client E2E | PR #245; `tools/e2e/**`; `tests/e2e/**`; OAM-006 controlled-server extension | Add bounded scenarios/exact controlled server revisions; never build a second generic orchestrator. |
| OTBM analysis pipeline | existing `tools/ai-agent/**` / `docs/ai-agent/**` | Reuse canonical world/map evidence tools. |
| Canary ↔ OTClient contract registry | `docs/agents/CROSS_REPO_CONTRACTS.md` | Use explicit compatibility/version/rollout contracts when client coupling exists. |
| OAM-003 engine-foundation report | `docs/agents/OTERYN_OAM_003_ENGINE_FOUNDATION_REVALIDATION.md` | Durable evidence for seven OAM-003 decisions and delivered target seams. |
| OAM-004 persistence-foundation report | `docs/agents/OTERYN_OAM_004_PERSISTENCE_FOUNDATION_REVALIDATION.md` | Durable evidence for four OAM-004 `ADAPT` decisions and delivered target persistence seams. |
| OAM-005 account/character lifecycle report | `docs/agents/OTERYN_OAM_005_ACCOUNT_CHARACTER_LIFECYCLE_REVALIDATION.md` | Durable evidence for OAM-005 `REUSE`/`ADAPT` decisions and the bounded login-session primitive. |
| OAM-006 network/login/protocol report | `docs/agents/OTERYN_OAM_006_NETWORK_LOGIN_PROTOCOL_REVALIDATION.md` | Durable evidence for the `protocol` `ADAPT` decision, exact target delivery and exact controlled-server physical-client proof. |

# Active tasks

`OAM-006` is the only active OAM implementation task in this feature-governance package. Target delivery and exact cross-repository physical proof are complete; Canary PR #436 is being finalized for its exact-head feature-governance gate.

`OAM-007` is not active and is not created or started here. It may become next eligible only after OAM-006 feature governance and the required separate lifecycle-only archival merge.

# Dependency-aware queue

| Package | Scope | Status | Dependencies | Exact next action |
|---|---|---|---|---|
| `OAM-001` | target architecture and migration evidence contract | completed | completed TSD + current registry | merged and lifecycle archived |
| `OAM-002` | target repository identity, authorization and exact baseline pinning | completed | OAM-001 | feature + lifecycle completed |
| `OAM-003` | engine/build/runtime foundation revalidation | completed | OAM-002 | feature + lifecycle completed |
| `OAM-004` | database and persistence foundation revalidation | completed | completed OAM-003 lifecycle | target, feature governance and lifecycle complete |
| `OAM-005` | account and character lifecycle revalidation | completed | completed OAM-004 feature + lifecycle | target, feature governance and lifecycle complete |
| `OAM-006` | network/login/protocol contract revalidation | ready | completed OAM-005 feature + lifecycle | target `c547d8ad70ef1252624c255476e6cb83fa125e14` and exact E2E #118 complete; pass final PR #436 gates, squash-merge, then archive in a separate lifecycle PR |
| `OAM-007` | item/world runtime foundation revalidation | blocked | OAM-003, OAM-004, completed OAM-006 lifecycle sequencing gate | do not start in this package; after OAM-006 lifecycle, re-fetch live state and evaluate item definitions/instances plus world-map/runtime boundaries |
| `OAM-008` | first low-risk canonical module migration package | blocked | affected foundation packages | select exactly one module after dependencies and evidence gates are complete |
| `OAM-009` | target physical-client E2E proof for first migrated module | blocked | OAM-008 plus target/client compatibility | reuse the existing E2E platform with one bounded target scenario |
| `OAM-010+` | dependency-ordered domain migrations | planned | proven foundation and prior package dependencies | advance one bounded package at a time |

OAM-006 is feature-ready, not lifecycle-complete. OAM-007 remains not started until a separate OAM-006 lifecycle package merges.

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

- OAM-001 and OAM-002 are completed and lifecycle archived.
- OAM-003 feature and lifecycle work are complete.
- OAM-004 feature and lifecycle work are complete.
- OAM-005 feature and lifecycle work are complete; final target is `a6d42f6cec024f81a7541084425ec1d43d66d2b8` and lifecycle merge is `a1d82a5989fe9e3b7ac6c495804cb1cd83c59090`.
- OAM-006 `protocol` disposition is `ADAPT`.
- Otheryn PR #21 exact head `5342b374306abb44b6b5e201c85f6a0182c99286` passed CI #80, Required #78 and autofix.ci #71 and squash-merged as `c547d8ad70ef1252624c255476e6cb83fa125e14`.
- `Otheryn:main` was verified at `c547d8ad70ef1252624c255476e6cb83fa125e14` for final OAM-006 target delivery.
- Universal Agent E2E #118 (`29531221365`) completed the full heavy path with `Required physical E2E` success for exact Otheryn `c547d8ad70ef1252624c255476e6cb83fa125e14` and OTClient `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`.
- Run #118 recorded two successful current-profile protocol-1525 logins/relogs, two safe logouts, persistence checks, zero client exit code and no fatal runtime log.
- Run #114 is explicitly rejected as final target evidence because immediate-parent reuse skipped heavy physical jobs.
- Cross-repository contract `OTS-001` records the server-first-safe opaque session-key handoff for the exact maintained-client pair.
- Canary PR #436 remains the feature-governance boundary; its exact final-head ownership/CI/review gate and separate lifecycle archival are still required before OAM-006 is complete.
- OAM-007 remains not started until OAM-006 lifecycle completion.
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
- An unchanged maintained client may remain read-only when its exact commit treats the changed field opaquely and physical proof verifies the pair.
- World-content work reuses existing OTBM tooling.
- Every feature merge is followed by separate lifecycle-only archival.
- Target delivery completion does not by itself authorize the next package; lifecycle completion remains required.
- A next-eligible package is not an active package; it still requires a new bounded task and fresh exact evidence.

# Validation strategy

OAM-001 and OAM-002 completed their exact-head feature and lifecycle gates.

OAM-003 completed its target, feature-governance and lifecycle gates.

OAM-004 completed with target PRs #11/#12/#13/#14, Canary feature PR #420 and separate lifecycle PR #428, all using exact-head gates.

OAM-005 completed target, feature-governance and lifecycle delivery with `account-lifecycle` → `REUSE`, `account-authentication` → `ADAPT` and `character-lifecycle` → `ADAPT`.

OAM-006 target and cross-repository proof completed with:

- `protocol` → `ADAPT`;
- task-start target `a6d42f6cec024f81a7541084425ec1d43d66d2b8`, upstream `e0ac98e399d0f7e483f3668f57b78fcc45b6e53f` and maintained client `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`;
- target PR #21 exact final head `5342b374306abb44b6b5e201c85f6a0182c99286` with ready-triggered CI #80 and Required #78 success;
- zero target PR comments, submitted reviews or unresolved review threads at final merge gate;
- target PR #21 squash-merged with exact-head guard as `c547d8ad70ef1252624c255476e6cb83fa125e14`;
- existing Universal Agent E2E extended in-place with optional controlled server repository/exact SHA inputs;
- full heavy Universal Agent E2E #118 / run `29531221365` with `Required physical E2E` success;
- artifact-recorded server commit `c547d8ad70ef1252624c255476e6cb83fa125e14` and client commit `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`;
- controlled server binary SHA-256 `a69674e53911f4c529fe62d4dee0209633a73a14903c61f8e5fbca1bdbd8097d` and OTClient binary SHA-256 `b562247f8a0499738bf89eb9f8132146a26b2be57d9fb45e9586a0e0659d97ed`;
- cross-repository contract `OTS-001`;
- no maintained-client source mutation, no packet-validation relaxation and no rollback of OAM-004D persistence semantics.

Canary feature-governance PR #436 must now pass its own exact final-head ownership/CI/review gates before squash merge. A separate lifecycle-only package must then archive OAM-006 before OAM-007 can start.

# Handoff

## Start here

Read `AGENTS.md`, `docs/agents/README.md`, this program, `docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md`, `docs/agents/OTERYN_OAM_006_NETWORK_LOGIN_PROTOCOL_REVALIDATION.md`, `docs/agents/CROSS_REPO_CONTRACTS.md`, the current canonical registry/generated indexes, all active task records and live open PRs.

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
- Do not re-enable MySQL automatic reconnect or arbitrary SQL statement replay.
- Do not infer persistence safety from `DBTransaction` existence.
- Do not claim player SQL + KV atomicity.
- Do not restore whole legacy `IOLoginData` over OAM-004D target persistence changes.
- Do not treat `LoginSessionManager` presence alone as live authentication proof.
- Do not merge speculative OTClient transport hardening from closed PR #11.
- Do not use incrementally reused E2E #114 as the exact-target OAM-006 proof; use full heavy E2E #118.
- Do not start OAM-007 inside OAM-006 feature governance or lifecycle archival.

## Known gaps carried forward

- Complete child `LuaScriptInterface` reconstruction/reload semantics.
- Untouched polymorphic Lua userdata safety.
- Concurrent configuration reload correctness under arbitrary future target consumers.
- Broader incremental removal of contextual/global DI access.
- Player SQL commit followed by later durable KV flush remains non-atomic.
- Generic KV eviction persistence failure handling remains outside OAM-004D.
- Complete crash/restart recovery semantics for untouched persistence paths remain unproven.
- Generic DDL reversibility remains unproven.
- OAM-006 exact physical proof covers the maintained `current` profile at protocol 1525 and does not claim exhaustive physical coverage of every old-protocol profile.
- OAM-006 physical proof establishes successful live token handoff but is not an adversarial replay matrix; primitive single-use/lifetime evidence remains in OAM-005 focused tests.
- DB-session/password fallbacks remain preserved and CI-covered but were not the exact controlled-server physical path exercised by E2E #118.

# Exact next task

First complete Canary feature-governance PR #436 with exact final-head ownership/CI/review gates, then create and merge a separate lifecycle-only OAM-006 archival PR. Only after that lifecycle merge may `OAM-007 — item/world runtime foundation revalidation` become the next eligible bounded package. Before OAM-007 starts, re-fetch live `main`, open PRs, active tasks, ownership/overlap state and exact target/upstream/legacy baselines; then create one separate bounded task/branch/PR only if the package remains eligible.
