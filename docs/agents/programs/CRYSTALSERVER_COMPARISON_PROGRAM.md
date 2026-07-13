---
program_id: CAN-PROGRAM-CRYSTALSERVER-COMPARISON
name: CrystalServer Comparison Program
status: active
owner: GPT-5.6 Thinking
created: 2026-07-13T21:01:05Z
updated: 2026-07-13T21:21:00Z
last_verified_commit: "bceccba9349d35a1d84f446757e53ac3adb602e1"
primary_paths:
  - docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md
  - artifacts/upstream/crystalserver/**
shared_integration_paths: []
related_programs: []
cross_repo_contracts: []
---

# Mission

Continuously compare `zimbadev/crystalserver` with current `blakinio/canary`, using CrystalServer only as a read-only candidate source. Accept, adapt, reject, or defer each difference from independent evidence about current Canary behavior, tests, architecture, protocol compatibility, active work, and runtime risk.

# Repository and baseline register

Stage 1 analysis date: 2026-07-13.

| Role | Repository | Stage 1 baseline `main` SHA | Declared server version | Declared client protocol | Access |
|---|---|---|---|---:|---|
| target | `blakinio/canary` | `360d79ebad5802edd4d89e99d0f210ab19b36b60` | `3.6.1` | `1525` / 15.25 | task branches and PRs only |
| comparison | `zimbadev/crystalserver` | `fc0d53b9f9965463b6082c07e6d3d482294541a7` | `4.1.9` | `1525` / 15.25 | read-only |
| reference | `opentibiabr/canary` | `9365c1c4aa63529b9ff757f53737274894c02b8e` | verify per selected task | verify per selected task | read-only |

Last analyzed CrystalServer commit: `fc0d53b9f9965463b6082c07e6d3d482294541a7`.

Stage 1 merged through PR [#291](https://github.com/blakinio/canary/pull/291), squash commit `bceccba9349d35a1d84f446757e53ac3adb602e1`.

Every later task must re-fetch all repository heads, open PRs, active ownership, relevant contracts, and the selected candidate diff.

# Scope

- Review CrystalServer diffs associated with crashes, regressions, desynchronization, overflow, leaks, security, databases, deadlocks, races, invalid state, missing validation, duplicate rewards, item loss, and protocol errors.
- Compare exact behavior against current Canary source, tests, documentation, tasks, PRs, and runtime evidence.
- Preserve repository, SHA, author, date, related PR/issue, files, symbols, and the exact adapted idea.
- Require a failing test or deterministic proof before implementation whenever practical.
- Adapt only the smallest complete fix to current Canary architecture.
- Maintain Markdown and JSON inventories under `artifacts/upstream/crystalserver/`.

# Explicit exclusions

- No writes outside `blakinio/canary`; no direct push to `main`.
- No mass cherry-pick, file replacement, or assumption that CrystalServer is newer or better.
- No `.otbm`, `items.otb`, binary assets, sprites, private dumps, secrets, or production configuration.
- No CrystalServer custom content presented as a Canary fix.
- No weakened tests or validators.
- No client, protocol, protobuf, login, DB schema, migration, multichannel, instance, shared-Lua-userdata, map, identifier, or asset change without extended contract analysis.

# Existing systems to reuse

| System | Source | Reuse rule |
|---|---|---|
| Agent coordination | `AGENTS.md`, `docs/agents/**` | One implementation candidate per task, branch, worktree, and draft PR. |
| Build/test matrix | `docs/agents/BUILD_TEST_MATRIX.md` | Select validation by changed surface and record exact command/head SHA. |
| Cross-repository contracts | `docs/agents/CROSS_REPO_CONTRACTS.md` | Protocol/client changes require linked server and maintained-client evidence. |
| Current Canary architecture | `src/**`, `data/**`, `tests/**`, relevant system docs | Prefer existing abstractions and later Canary behavior. |
| Universal E2E platform | PR #245 after merge and stabilization | Reuse instead of creating parallel feature-specific orchestration. |

# Methodology

1. Record current heads, versions/protocols, open PRs, tasks, ownership, and worktree state.
2. Continue after the recorded last analyzed CrystalServer commit unless deliberately re-auditing an older area.
3. Search broadly, then open each CrystalServer diff and linked discussion.
4. Split bundled commits into independent behavior units.
5. Identify the defect trigger, state transition, and impact.
6. Locate corresponding Canary symbols, tests, and later changes.
7. Determine whether Canary already has an equivalent or safer solution.
8. Check CrystalServer-only dependencies and client/protocol/schema/ID/asset coupling.
9. Define a failing test or deterministic validator before `VALID_FIX_MISSING`.
10. Assign exactly one status and record uncertainty.
11. Implement only through a new bounded task after all gates pass.

Text similarity, `patch-id`, symbol search, and commit messages are signals, not behavioral proof.

# Status model

`ALREADY_PRESENT`, `CANARY_SUPERIOR`, `VALID_FIX_MISSING`, `PARTIAL_VALUE`, `CLIENT_COUPLED`, `CONTENT_ONLY`, `UNVERIFIED`, `DANGEROUS`, or `REJECTED` — exactly one status per candidate at a recorded baseline.

# Risk classes

| Risk | Meaning | Minimum gate |
|---|---|---|
| critical | item/currency loss or duplication, corrupt state, remote security, unrecoverable DB/protocol failure | deterministic reproduction, regression test, focused integration, full affected CI, rollback review |
| high | crash, leak, invalid lifetime, client crash, privilege/input boundary | reproduction or strong proof, focused tests, architecture/security review, full affected CI |
| medium | bounded correctness or performance issue | focused test or benchmark and affected CI |
| low | documentation or unchanged-behavior work | docs/format/path checks and relevant CI |

# Active tasks

None. Select exactly one bounded queue item and create a new task before implementation.

# Queue

| ID | CrystalServer commit | Status | Risk | Area | Next action |
|---|---|---|---|---|---|
| `CS-001` | `a7350014528002fb27ed64d260a96d28a580d41a` | `VALID_FIX_MISSING` | high | `ConditionLight` zero-level division/deserialization | Create a separate test-first task after fresh baseline, ownership, and test-harness checks. |
| `CS-002` | `0c0f1acafd77a86fb5ce56fe768ff6d98d100c35` | `ALREADY_PRESENT` | medium | NPC shop iteration | Closed evidence; no implementation. |
| `CS-003` | `90ac0eb7d2ba0a88476881c972d9de83fbbcb3e8` | `CANARY_SUPERIOR` | high | KV shared Lua userdata GC | Preserve typed shared-class registration. |
| `CS-004` | `dcb4f00ffd55ede2399c979eee3b7fe6e7e0ee6e` | `ALREADY_PRESENT` | high | `Container::replaceThing` validation | Closed evidence; no implementation. |
| `CS-005` | `fc0d53b9f9965463b6082c07e6d3d482294541a7` | `PARTIAL_VALUE` | medium | player GUID index | Benchmark only after `game.cpp`/`game.hpp` ownership clears. |
| `CS-006` | `891685169745e46f665069edcc35847f0704aa21` | `PARTIAL_VALUE` | high | `FS.mkdir` shell construction | Independent security task; do not copy upstream denylist. |
| `CS-007` | `891685169745e46f665069edcc35847f0704aa21` | `PARTIAL_VALUE` | high | `table.unserialize` execution | Independent compatibility/security task; do not copy bespoke parser. |
| `CS-008` | `34cbec0c34325619ef23c5d12c940b7b1c276975` | `CLIENT_COUPLED` | high | Market limits | Establish maintained OTClient limits and integration tests. |
| `CS-009` | `cfc0c5c496eae53f1f33a07f563068f44914ddbb` | `CLIENT_COUPLED` | high | disconnect reason byte | Exact 15.25 client contract task only. |
| `CS-010` | `ffe4db548371c44ce01dfc280af0209318272292` | `DANGEROUS` | critical | creature-removal parent lifetime | Reproduce invariant; design cleanup ordering; never copy early return. |

# Deferred screening backlog

| CrystalServer commit | Preliminary state | Reason |
|---|---|---|
| `9e046413b965982745ca63559f68bd30264bfc9d` | `UNVERIFIED` | Requires current Canary item XML/identifier/asset-contract validation. |
| `809633b1f9fc9a690bef70ac0ecb916d5a5aa5d6` | `UNVERIFIED` | Admin-command limit lacks justified resource bound. |
| `55db69b7be12fa7b6a8865038033d953ae8cff18` | `UNVERIFIED` | Corpse/reward parent handling needs current state-transition tests. |
| `6bda45e7d7b8f0e9a9c55b3b6b779b492504102f` | `UNVERIFIED` | Broad formula rewrite requires official behavior evidence and decomposition. |

# Completed work

| Task/PR | Result | Merge commit | Follow-up |
|---|---|---|---|
| `CAN-20260713-crystalserver-comparison-inventory` / [#291](https://github.com/blakinio/canary/pull/291) | Stage 1 program, ten-candidate Markdown report, and machine-readable JSON; no functional changes | `bceccba9349d35a1d84f446757e53ac3adb602e1` | Select `CS-001` only through a new test-first task after fresh checks. |

# Closed candidates

- `CS-002` — equivalent safe iteration already exists.
- `CS-003` — Canary already uses a safer typed shared-userdata pattern.
- `CS-004` — required null and bounds validation already exists.

# Dependencies and blockers

- Local Git/worktree inspection was unavailable during Stage 1 because shell DNS could not resolve GitHub; future tasks must record their own environment.
- Recheck all open PRs before touching `src/game/game.cpp` or `src/game/game.hpp`; Stage 1 found explicit overlap with PR #289.
- PR #245 is the intended future reusable physical-client E2E base; client-coupled candidates must not duplicate it.
- `CS-010` cannot use the CrystalServer patch because its return follows partial removal side effects.

# Decisions and invariants

- Before every write, `repository_full_name` must equal `blakinio/canary`.
- CrystalServer and OpenTibiaBR Canary remain read-only.
- `VALID_FIX_MISSING` requires deterministic evidence against current Canary.
- Bundled upstream commits are split into independent candidates.
- No candidate replaces an entire Canary file.
- Reports remain under `artifacts/upstream/crystalserver/`.
- Extended surfaces always use extended gates.
- Unknown evidence remains `UNVERIFIED`, never guessed as handled.

# Validation strategy

- Inventory/docs: Markdown/path review, exact changed-file and full-PR-diff review, `git diff --check` or documented unavailable environment, current-head checks.
- C++: failing focused test, correct preset build, focused tests, required platform CI.
- Lua/security: call-site inventory, compatibility/malicious-input corpus, syntax checks, runtime smoke.
- DB: clean import, migration/rollback tests, temporary MariaDB integration.
- Protocol/client: byte-exact server and maintained-client tests plus physical integration.
- Performance: reproducible benchmark and lifecycle/correctness tests.

# Handoff

## Start here

Read `AGENTS.md`, `docs/agents/README.md`, this program, the Stage 1 Markdown/JSON reports, current active tasks, and open PRs. Re-fetch current heads before selecting work.

## Task creation protocol

1. Select one bounded candidate.
2. Re-open its CrystalServer diff and discussion.
3. Compare current Canary code/tests and revise status if evidence changed.
4. Inspect ownership and overlapping PRs.
5. Create one task, branch, worktree, and draft PR with exact path claims.
6. Add failing evidence before the fix where practical.
7. Implement the smallest architecture-native adaptation.
8. Validate, review the complete diff, update provenance/program state, and merge only through the autonomous gate.

## Do not repeat

- Do not rescan from scratch before checking the last analyzed commit and JSON inventory.
- Do not copy the `table.unserialize` parser or `removeCreature` early return.
- Do not combine security candidates merely because one upstream commit bundled them.
- Do not infer official client limits from CrystalServer constants.
- Do not start overlapping `game.cpp`/`game.hpp` work without ownership resolution.

## Open questions

- Which current path can supply zero to `ConditionLight`, and which fixture best proves it?
- Which inputs reach `FS.mkdir` and `table.unserialize`, and are any attacker-controlled?
- What exact protocol 15.25 Market and disconnect contracts are implemented by the maintained OTClient?
- What lifecycle invariant safely handles missing parents during creature removal?
