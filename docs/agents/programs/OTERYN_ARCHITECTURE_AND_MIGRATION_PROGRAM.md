---
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
name: Oteryn Architecture and Migration
status: active
owner: oteryn-architecture-migration-agent
created: 2026-07-15T15:28:18+02:00
updated: 2026-07-17T20:51:21+02:00
last_verified_commit: "02403617318049575814c0e24740469829355b0d"
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

Govern the evidence-backed transition from legacy `blakinio/canary` to clean target `blakinio/Otheryn` one bounded canonical module/package at a time. The canonical migration unit is `docs/agents/real-tibia/registry/modules/*.yaml`; generated indexes are discovery artifacts only.

Target architecture remains authoritative at `docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md`.

# Non-negotiable rules

- `blakinio/canary` is the writable governance/legacy laboratory and evidence source.
- `blakinio/Otheryn` is the separately authorized writable target.
- `blakinio/otclient` and other upstream/donor repositories are read-only unless separately authorized.
- One bounded OAM package, task, branch and PR at a time.
- Exact task-start and final-head SHAs are required.
- Every feature merge is followed by separate lifecycle/archive before another OAM package starts.
- Final merge requires clean comments, reviews and unresolved review threads.
- Reuse the existing Universal Physical-Client E2E; never create a second generic orchestrator.
- No bulk copy, mass cherry-pick, parallel migration registry, duplicate OTBM pipeline or speculative client fork.
- Never infer `REUSE` from file presence or blob identity alone; require provenance, target compatibility and applicable focused/integration/runtime proof.
- Never re-enable MySQL automatic reconnect or arbitrary SQL replay.
- Never claim player SQL and KV persistence are atomic.
- Preserve explicit OAM-004 residual gaps.
- Closed speculative OTClient PR #11 remains excluded.

# Migration dispositions

`REUSE`, `ADAPT`, `REVALIDATE`, `REWRITE`, `DO_NOT_MIGRATE`, `EXPERIMENTAL_ONLY`.

`REVALIDATE` remains the default outside modules explicitly decided by a bounded package. `REUSE` is never optimistic by default.

# Completed package history

| Package | Result | Durable completion |
|---|---|---|
| OAM-001 | target architecture/evidence contract | complete + lifecycle archived |
| OAM-002 | target identity, authorization, baseline pinning | complete + lifecycle archived |
| OAM-003 | engine/build/runtime foundation | complete + lifecycle archived |
| OAM-004 | database/persistence foundation | complete + lifecycle archived |
| OAM-005 | account/character lifecycle | target `a6d42f6cec024f81a7541084425ec1d43d66d2b8`; lifecycle `a1d82a5989fe9e3b7ac6c495804cb1cd83c59090` |
| OAM-006 | protocol → `ADAPT` | target `c547d8ad70ef1252624c255476e6cb83fa125e14`; physical run `29531221365`; feature `c40b26ee9481ec99931347ba26897a785a7a38ca`; lifecycle `b0ea0ba9508cc78d5580f44181115e9b304eb7da` |
| OAM-007 | item-definitions `ADAPT`; item-instances `REUSE`; world-map-runtime `REUSE` | target `68c4f39f7b1b45f880543c258627b4ccf73dbc86`; physical run `29559180590`; feature `be9760a88d0c714dfd3e1b6a659e373380d03d65`; lifecycle `317c1c4235377c388883aa2fd425d324f8ce4d2e` |
| OAM-008 | `vocations → REUSE` | target `f59a58426b4d3910ba0cdc0d2332c24f31a1db4f`; feature `acdddd924fed170da51a8a54114607842f0cbb68`; lifecycle `e27eeefa4c3b4a6072c8c8ffda73da806fe20b9b` |
| OAM-009 | exact-target physical-client proof for first migrated `vocations` module | feature `533a1063ab2d25199fb39239e28dace6a064d395`; lifecycle `02403617318049575814c0e24740469829355b0d` |

# OAM-008 durable state

OAM-008 selected exactly one low-risk canonical module: `vocations`. Canonical `vocation.cpp`, `vocation.hpp` and `data/XML/vocations.xml` were exact-blob identical across task-start target, legacy and upstream, but identity alone was not accepted as authorization.

Proof-only Otheryn PR #25 added focused acceptance tests only. Final head `9453a1754501ce183e20d294df1064a5ccbad54c` passed autofix #77, CI #88 and Required #84; both `VocationsTest` cases executed and passed. Target merge is `f59a58426b4d3910ba0cdc0d2332c24f31a1db4f`. Canary feature merge is `acdddd924fed170da51a8a54114607842f0cbb68`; lifecycle merge is `e27eeefa4c3b4a6072c8c8ffda73da806fe20b9b`.

OAM-008 disposition remains:

```text
vocations REUSE
```

It does not claim Real Tibia vocation-value parity, combat-formula parity, spell/weapon eligibility or Wheel behavior.

# OAM-009 durable completion

OAM-009 proved one bounded runtime claim: exact target `blakinio/Otheryn@f59a58426b4d3910ba0cdc0d2332c24f31a1db4f` can physically log in deterministic fixture `Knight 1`, whose persisted DB `vocation` is `4`, through the accepted vocation registry boundary.

The exact target load path is fail-closed when `setVocation(vocationId)` cannot resolve the persisted ID. The canonical `login/relog` scenario was extended by exactly one SQL assertion:

```sql
SELECT vocation = 4 FROM players WHERE name = 'Knight 1'
```

A real proof gap was found during implementation: the existing physical runner declared but did not execute canonical `scenario.assertions.sql`. Preliminary run `29589941229` was therefore rejected as final evidence. The existing generic runner was extended in place to execute each canonical SQL assertion independently, fail closed, and require scalar stdout exactly `1`; no second workflow, runner or orchestrator was created.

Accepted exact-target proof:

- Universal Agent E2E run: `29593102547`
- exact Otheryn: `f59a58426b4d3910ba0cdc0d2332c24f31a1db4f`
- maintained OTClient: `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`
- physical login/logout/relog/logout: PASS
- all three canonical SQL assertions: PASS, including `vocation = 4`
- artifact digest: `sha256:f880b2fb58c53d8e53aad4cc30725a26a050c352bd5412a10c56b8a61f327f3f`
- server executable SHA256: `3a191e398ea22818a9e71cd3ce0fe60486e1e0592cddb379295504a77dc62925`
- client executable SHA256: `5dcaed6cdfcaecf2de4b9de80183a28fe8e0722e21b4df588cc627c558da5ee9`

The proof-only controlled-server pin was removed before merge.

Final Canary feature head `d90866eeb30b8e1f6fbd3b45f452d68fc0f6185c` passed:

- Agent Task Ownership `29603179802` — PASS
- CI `29603179331` — PASS after retrying one transient Windows `Setup vcpkg` failure that occurred before code compilation
- Universal Agent E2E `29603179422` — PASS
- final PR audit — zero comments, zero reviews, zero review threads

Feature PR #489 squash-merged as `533a1063ab2d25199fb39239e28dace6a064d395`.

Automated lifecycle PR #501 was superseded because its automation-token checks were `action_required`. Equivalent manual lifecycle PR #502 passed Ownership and CI with a clean review state and squash-merged as `02403617318049575814c0e24740469829355b0d`.

OAM-009 does not create a new migration disposition and does not expand `vocations → REUSE` beyond this bounded runtime claim.

# Current live state

```text
latest reconciled Canary main: 02403617318049575814c0e24740469829355b0d
Otheryn proof target: f59a58426b4d3910ba0cdc0d2332c24f31a1db4f
maintained OTClient: 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
OAM-001..OAM-009: feature/lifecycle complete
OAM-009 task: archived
OAM-010: not created and not started
```

No OAM implementation task is active in this reconciliation record.

# Dependency-aware queue

| Package | Status | Exact next action |
|---|---|---|
| OAM-001..OAM-009 | completed | preserve durable evidence and sequencing |
| OAM-010+ | planned, not active | only after this reconciliation merges: fresh live-state, active ownership, open-PR overlap and exact target/upstream/legacy preflight; then create exactly one bounded task |

A next-eligible package is not an active package.

# Evidence gate for every future package

Where applicable, prove exact legacy/target/upstream SHAs, canonical module/dependency identity, target architecture compatibility, persistence/schema compatibility, protocol/client compatibility, deterministic focused tests, integration/runtime proof, physical-client E2E, provenance/conflicts, known gaps, rollback strategy and one explicit disposition.

Compilation, directory similarity, donor similarity or green legacy CI is insufficient by itself.

# Decisions and invariants

- The canonical registry remains the sole migration inventory.
- Legacy Canary is evidence, not a target image to clone.
- Baselines are pinned per package by exact SHA.
- Migration sequencing follows dependency evidence.
- Physical-client E2E complements rather than replaces focused/integration/runtime proof.
- Exact controlled-server E2E must record the actual producer revision; Canary-only or incrementally reused evidence cannot substitute for exact-target proof.
- Every feature merge requires separate lifecycle archival.
- Declaring SQL in a scenario manifest is not execution evidence; OAM-009 required fail-closed execution evidence.
- OAM-010 remains unstarted until this program reconciliation merges and a fresh preflight creates a new bounded task.

# Known gaps carried forward

- Complete child `LuaScriptInterface` reconstruction/reload semantics remain unproven.
- Untouched polymorphic Lua userdata safety remains unproven.
- Concurrent configuration reload correctness under arbitrary future target consumers remains unproven.
- Broader incremental removal of contextual/global DI access remains incomplete.
- Player SQL commit followed by later durable KV flush remains non-atomic.
- Generic KV eviction persistence failure handling remains outside OAM-004D.
- Complete crash/restart recovery semantics for untouched persistence paths remain unproven.
- Generic DDL reversibility remains unproven.
- OAM-006 does not claim exhaustive old-protocol physical coverage.
- OAM-007 does not claim Real Tibia item value/appearance parity, map completeness or exhaustive movement/pathfinding correctness.
- OAM-008 does not claim broad vocation gameplay parity.
- OAM-009 proves only the deterministic vocation-ID-4 login/logout/relog/logout boundary described above.

# Handoff

Read `AGENTS.md`, `docs/agents/README.md`, this program, `docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md`, `docs/agents/OTERYN_OAM_008_VOCATIONS_MIGRATION.md`, `docs/agents/OTERYN_OAM_009_VOCATIONS_PHYSICAL_E2E.md`, `docs/agents/CROSS_REPO_CONTRACTS.md`, the current canonical registry/generated indexes, archived OAM tasks, active tasks and live open PRs.

For the next package:

1. Re-fetch live Canary `main`, open PRs, active tasks and ownership.
2. Re-fetch exact target/upstream/legacy heads.
3. Select exactly one dependency-valid bounded canonical package.
4. Create one task, branch and draft PR with explicit ownership.
5. Implement only bounded scope and preserve all residual gaps.
6. Require exact-head CI/runtime/E2E/review gates as applicable.
7. Squash-merge feature, then complete separate lifecycle/archive.
8. Reconcile durable program state before starting another OAM package when queue state changes.

# Exact next task

Merge this program-only OAM-009 completion reconciliation after exact-head Ownership/CI/review gates. After that, `OAM-010+ — dependency-ordered domain migrations` is only next eligible; no OAM-010 task, branch or PR exists yet. A fresh live-state and exact target/upstream/legacy preflight is mandatory before creating it.
