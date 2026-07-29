---
task_id: CAN-20260729-game-catalog-loader-stability
program_id: CAN-PROGRAM-GAME-CATALOG-COMPLETENESS
coordination_id: "OTS-20260728-game-catalog-v1"
status: review
agent: "chatgpt"
branch: fix/CAN-20260729-game-catalog-loader-stability
base_branch: main
created: 2026-07-29T19:35:00Z
updated: 2026-07-29T20:30:00Z
last_verified_commit: "3ffd9557078a12e8e285d20b3af98a56dbc86c58"
risk: high
related_issue: ""
related_pr: 1015
depends_on:
  - CAN-20260729-game-catalog-loot-threshold-schema
blocks:
  - Game Catalog staging snapshot
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260729-game-catalog-loader-stability.md
    - src/canary_server.hpp
    - src/game/catalog/catalog_runtime.cpp
  shared:
    - tests/game_catalog/**
    - tests/unit/game/catalog/game_catalog_test.cpp
    - .github/workflows/game-catalog.yml
    - docs/agents/programs/GAME_CATALOG_COMPLETENESS_PROGRAM.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - src/game/game.cpp
    - config.lua.dist
    - data-otservbr-global/**
    - schemas/game-catalog/**
modules_touched:
  - oteryn.game-catalog export-only definition loader
reuses:
  - Offline Game Catalog exporter from PR #991
  - Schema 1.2 producer from PR #1012
  - Existing luaStartupLoadTelemetry loader instrumentation
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Find and remove the cause of the default-datapack export-only definition-loader crash, then certify that successful schema 1.2 export is repeatable with startup loader telemetry both disabled and enabled before any staging work.

# Acceptance criteria

- [x] Reproduce or tightly bound the two exit-139 failures using the exact default datapack, one compiled artifact, and explicit telemetry-disabled/enabled attempts.
- [x] Capture a symbolized fault location or equivalent sanitizer evidence before selecting a runtime fix; do not infer the cause from logging alone.
- [x] Fix the smallest proven root cause without making startup telemetry a correctness requirement.
- [x] Run at least ten sequential telemetry-disabled exports and two telemetry-enabled controls from the same final binary artifact with every attempt visible.
- [x] Prove all successful attempts publish byte-identical controlled snapshots and valid lowercase SHA-256 sidecars.
- [x] Preserve zero database/network endpoint syscalls, atomic publication, schema 1.2 semantics, and the 92 reviewed over-maximum thresholds.
- [x] Keep production configuration, datapack content, schema bytes, import, staging, and production activation unchanged.
- [ ] Pass focused checks, exact-head Game Catalog, CI, ownership, and required stability checks.
- [x] Update the program record, module catalogue/changelog impact, and durable checkpoint.
- [ ] Autonomous merge gate satisfied.

# Confirmed context

- Canary PR #1012 merged schema 1.2 producer support as `daf6553426a57c8474a372160b2f1e3b4536b171`; its lifecycle PR #1013 merged as `1e155cd8407246a154dbf81c33aa316f0752de8f`.
- Runtime jobs `90670860532` and `90675503517` exited 139 in the complete default-datapack export after `Weapon proficiencies loaded!`.
- The same schema, exporter, and reviewed metadata paths passed before the complete default-datapack phase in both failed jobs.
- Game Catalog run `30481456654` and exact-artifact rerun job `90678481552` passed with existing loader telemetry enabled.
- Game Catalog run `30482339983` passed the final schema 1.2 proof; lifecycle run `30484342589` repeated it successfully.
- Telemetry-independent stability is a separate queue item and explicit staging blocker; production remains manually gated.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| Export-only loader | instrument and repair in place | `src/game/catalog/catalog_runtime.cpp` | It owns the isolated definition-load sequence. |
| Normal startup loader | compare ordering and semantics read-only first | `src/canary_server.cpp` | It is the established loader behavior, not a second implementation target. |
| Game Catalog workflow | extend the exact-artifact proof | `.github/workflows/game-catalog.yml` | It already isolates DB/network syscalls and validates complete output. |
| Startup load telemetry | use only as an experimental control | `luaStartupLoadTelemetry` | The observed correlation must not become a correctness dependency. |

# Ownership and overlap check

- Program record: `CAN-PROGRAM-GAME-CATALOG-COMPLETENESS`, queue item 2.
- Open PRs inspected: no open PR matched `catalog_runtime` or `game-catalog`.
- Active tasks inspected: no active task claims the owned runtime/workflow paths.
- Ownership checker result: 33 active task records passed on `1e155cd8407246a154dbf81c33aa316f0752de8f`.
- Exclusive claims: task record and export-only loader.
- Shared claims: appearance loader only if fault evidence points there, focused tests/workflow, program/catalogue/changelog.
- Read-only dependencies: production config, default datapack, and schema bytes.
- Overlaps: none found.
- Resolution: proceed on one dedicated branch and draft PR.

# Current state

The root cause is an export-only Lua thread-ownership violation: `CanaryServer` starts the dispatcher in its constructor, but the original export path loaded definitions directly from the process main thread while registered `GlobalEvents` could execute on the dispatcher. The complete export now runs as one serial dispatcher event, and the counted post-fix exact-artifact series passes independently of telemetry.

# Plan

1. Publish the final checkpoint, force the exact-final-head gate, audit reviews and base drift, then squash-merge PR #1015.

# Work log

## 2026-07-29T19:35:00Z

- Changed: claimed the telemetry-independent pre-staging stability task.
- Learned: failed logs end after proficiencies; the next loader is appearance protobuf/item registration, but no fault frame is proven.
- Failed/blocked: staging is blocked until the crash is diagnosed and repeated telemetry-disabled exports pass.
- Result: diagnostic task is implementation-ready.

## 2026-07-29T19:40:00Z

- Changed: opened draft PR #1015 and added a telemetry-disabled, post-mortem core/backtrace capture to the exact-artifact runtime workflow.
- Learned: the existing release binary can remain uninstrumented during reproduction; `gdb` runs only after failure against the captured core.
- Failed/blocked: no new run has produced the fault frame yet.
- Result: the next PR run is a bounded diagnostic and is expected to remain red if the known crash reproduces.

## 2026-07-29T19:45:00Z

- Changed: replaced the single complete export with a counted exact-artifact series of ten telemetry-disabled attempts and two telemetry-enabled controls.
- Learned: Game Catalog `30485475053` passed one complete telemetry-disabled default export, disproving deterministic failure whenever telemetry is off.
- Failed/blocked: the intermittent crash did not reproduce in the first post-mortem run, so no fault frame exists yet.
- Result: each next attempt retains mode, ordinal, status, digest, log, endpoint trace, and a post-mortem backtrace on crash.

## 2026-07-29T20:05:00Z

- Changed: reproduced five failures in ten telemetry-disabled attempts and implemented dispatcher-thread serialization for the complete export task.
- Learned: crash frames land in LuaJIT while another thread executes `GlobalEvents::think -> LuaScriptInterface::callFunction`; export-only loading was using the same Lua state from the process main thread.
- Failed/blocked: the serialization fix is not compiled or runtime-validated yet.
- Result: appearance loading and schema serialization are rejected as root causes; the exact-artifact series now tests the proven concurrency boundary.

## 2026-07-29T20:30:00Z

- Changed: compiled the dispatcher-thread fix and ran the full counted exact-artifact stability gate.
- Learned: Game Catalog `30487172289` passed 10/10 telemetry-disabled and 2/2 telemetry-enabled attempts with one digest and no endpoint syscalls.
- Failed/blocked: Agent Task Ownership `30487172093` rejected only the frontmatter spelling `in-progress`; runtime ownership did not overlap.
- Result: corrected the lifecycle status to `review`; final-head protected validation is the only remaining gate.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Treat telemetry as a control, never a fix | logging changes correlate with the outcome but do not prove causality | not required |
| Require one exact artifact for all counted attempts | excludes compilation drift from the stability classification | not required |
| Preserve each failed attempt and backtrace | prevents a flaky pass from erasing the known conflict | not required |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `src/game/catalog/catalog_runtime.cpp` | exclusive | serialize the complete export as one dispatcher event | complete |
| `src/canary_server.hpp` | exclusive | declare the dispatcher-thread export implementation | complete |
| `src/game/game.cpp` | read-only | appearance loading was inspected and rejected as the root cause | unchanged |
| `.github/workflows/game-catalog.yml` | shared | exact-artifact diagnostic and repeated stability proof | complete |
| `luaStartupLoadTelemetry` | read-only interface | telemetry-off/on experimental control | unchanged |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| `1e155cd8407246a154dbf81c33aa316f0752de8f` | `python3 tools/agents/task_ownership.py` | passed | 33 active task records before this claim |
| `e85be1bf6e237448d624d28ff891362d5f67f9b6` | runtime jobs `90670860532`, `90675503517` | failed | default export exited 139 after proficiencies |
| `e85be1bf6e237448d624d28ff891362d5f67f9b6` | Game Catalog `30481456654`, rerun `90678481552` | passed | telemetry-enabled complete export |
| `ac354e27eae99b289050ec6dd0892edc9c71cd13` | Game Catalog `30485475053` | passed | one complete telemetry-disabled default export passed |
| working tree after `ac354e27eae99b289050ec6dd0892edc9c71cd13` | parse workflow YAML and runtime step with `bash -n` | passed | counted stability workflow parses |
| `421e7957f41f8f3a5d84e7aaaea3fe3e87eb7b92` | Game Catalog `30486191705` | failed as diagnostic | 5/10 telemetry-off attempts failed; 2/2 telemetry-on controls passed |
| working tree after `421e7957f41f8f3a5d84e7aaaea3fe3e87eb7b92` | 17 focused Python tests, checkpoint/ownership, workflow shell, clang-format | passed | source fix is ready for exact CI compilation |
| `3ffd9557078a12e8e285d20b3af98a56dbc86c58` | Game Catalog `30487172289` | passed | release compilation and 10-off/2-on exact-artifact proof passed |
| `3ffd9557078a12e8e285d20b3af98a56dbc86c58` | CI `30487172320` | passed | repository CI passed |
| `3ffd9557078a12e8e285d20b3af98a56dbc86c58` | Agent Task Ownership `30487172093` | failed | frontmatter used unsupported `in-progress`; corrected to `review` in the final checkpoint |

# Failed approaches and dead ends

- Enabling telemetry as a permanent workflow workaround is rejected because it masks rather than explains the stability dependency.
- Inferring that proficiencies caused the crash is rejected because its loader returned and logged success; the fault frame is not captured.
- Treating every telemetry-disabled load as deterministically crashing is rejected by Game Catalog `30485475053`.
- Appearance protobuf loading is the root cause is rejected by fault frames in LuaJIT and concurrent `GlobalEvents::think`.
- Snapshot serialization is the root cause is rejected because failed attempts crash during definition loading before manifest/export construction.
- Treating two later passes as disproving the two crashes is rejected because the config condition changed.

# Risks and compatibility

- Runtime: the complete export must remain on the serial dispatcher thread; the workflow retains counted telemetry-off/on regression evidence.
- Data/migration: no data or migration changes allowed.
- Security: diagnostics must not publish secrets, private paths, dumps, or credentials.
- Backward compatibility: normal startup behavior and all existing schema versions must remain unchanged.
- Cross-repo rollout: no consumer change is expected; any discovered contract impact becomes a separate task.
- Rollback: revert the bounded runtime/workflow commit; staging remains blocked throughout.

# Remaining work

1. Publish this final checkpoint, require exact-final-head gates, audit reviews and base drift, then squash-merge PR #1015.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T20:30:00Z
head: 3ffd9557078a12e8e285d20b3af98a56dbc86c58
branch: fix/CAN-20260729-game-catalog-loader-stability
pr: 1015
status: ready
context_routes:
  - agent-governance
  - cpp-runtime
  - ci-repair
owned_paths:
  - docs/agents/tasks/active/CAN-20260729-game-catalog-loader-stability.md
  - src/canary_server.hpp
  - src/game/catalog/catalog_runtime.cpp
  - tests/game_catalog/**
  - tests/unit/game/catalog/game_catalog_test.cpp
  - .github/workflows/game-catalog.yml
  - docs/agents/programs/GAME_CATALOG_COMPLETENESS_PROGRAM.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - Two complete default-datapack export jobs exited 139 after weapon proficiencies loaded.
  - Two telemetry-enabled executions of one exact artifact passed the complete default-datapack proof.
  - Later final-head and lifecycle Game Catalog runs also passed with telemetry enabled.
  - Game Catalog 30485475053 passed one complete telemetry-disabled default export.
  - Game Catalog 30486191705 reproduced 5 failures in 10 telemetry-disabled attempts while both telemetry-enabled controls passed.
  - Symbolized crashes occur in LuaJIT while a concurrent dispatcher thread executes GlobalEvents::think through LuaScriptInterface::callFunction.
  - Dispatcher-thread serialization compiled and Game Catalog 30487172289 passed 10 telemetry-disabled and 2 telemetry-enabled exact-artifact attempts.
  - All 12 post-fix attempts emitted byte-identical snapshots, valid lowercase SHA-256 sidecars, zero endpoint syscalls, and 92 reviewed over-maximum thresholds.
  - CI 30487172320 passed on the implementation head.
  - Schema 1.2 producer and consumer are merged without staging or production activation.
derived:
  - The LuaJIT crashes were caused by export-only definition loading racing the already-running dispatcher for one Lua state.
  - The serial dispatcher event restores the normal Lua thread-ownership boundary and prevents registered events from executing mid-load.
unknown:
  - Exact-final-head protected workflow outcome after the final checkpoint.
conflicts: []
first_failure:
  marker: Agent Task Ownership requires a supported active frontmatter status
  evidence: Run 30487172093 rejected `in-progress`; this checkpoint changes it to `review`.
rejected_hypotheses:
  - Weapon proficiencies are proven as the faulting loader because their success log precedes the crash.
  - Startup telemetry is an acceptable permanent correctness requirement.
  - Every telemetry-disabled complete load crashes.
  - Appearance protobuf or snapshot serialization is the proven crash source.
  - Dispatcher serialization does not affect the failure rate.
  - Later successful runs erase the earlier telemetry-disabled failures.
changed_paths:
  - src/canary_server.hpp
  - src/game/catalog/catalog_runtime.cpp
  - .github/workflows/game-catalog.yml
  - docs/agents/CHANGELOG.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260729-game-catalog-loader-stability.md
  - docs/agents/programs/GAME_CATALOG_COMPLETENESS_PROGRAM.md
validation:
  - command: python3 tools/agents/task_ownership.py
    result: PASS
    evidence: 33 active task records validate before this claim.
  - command: failed runtime log inspection
    result: PASS
    evidence: Jobs 90670860532 and 90675503517 both end with exit 139 after proficiencies.
  - command: parse .github/workflows/game-catalog.yml with PyYAML
    result: PASS
    evidence: Telemetry-disabled post-mortem workflow parses locally.
  - command: Game Catalog 30485475053
    result: PASS
    evidence: Complete telemetry-disabled default export passed on ac354e27eae99b289050ec6dd0892edc9c71cd13.
  - command: Game Catalog 30486191705
    result: FAIL
    evidence: Expected diagnostic failure; 5/10 telemetry-off attempts crashed with LuaJIT/concurrent GlobalEvents frames and 2/2 telemetry-on controls passed.
  - command: focused local validation
    result: PASS
    evidence: 17 Game Catalog Python tests, task ownership/checkpoint, workflow shell parsing, clang-format, and diff check pass.
  - command: Game Catalog 30487172289
    result: PASS
    evidence: Release compilation and the 10-off/2-on exact-artifact stability proof passed on 3ffd9557078a12e8e285d20b3af98a56dbc86c58.
  - command: CI 30487172320
    result: PASS
    evidence: Repository CI passed on the implementation head.
  - command: Agent Task Ownership 30487172093
    result: FAIL
    evidence: Unsupported frontmatter status `in-progress`; corrected to `review` in this checkpoint.
blockers:
  - none for this task; staging remains a separate task and production activation remains manual
next_action: Publish this final checkpoint, require exact-final-head gates, audit reviews and base drift, then squash-merge PR 1015.
```

# Handoff

## Start here

Read this checkpoint, `.github/workflows/game-catalog.yml`, `src/game/catalog/catalog_runtime.cpp`, and the failed runtime job logs before changing source.

## Do not repeat

- Do not infer a faulting loader from the last successful log line.
- Do not use telemetry-enabled success as the root-cause fix.
- Do not change schema bytes, datapack content, staging, import, or production activation.

## Required reads

- `AGENTS.md`
- `docs/agents/REPOSITORY_MAP.md`
- `docs/agents/CONTEXT_ROUTING.md`
- `docs/agents/programs/GAME_CATALOG_COMPLETENESS_PROGRAM.md`
- `docs/agents/BUILD_TEST_MATRIX.md`
- `docs/agents/MODULE_CATALOG.md`
- `src/game/catalog/catalog_runtime.cpp`
- `.github/workflows/game-catalog.yml`

## Open questions

- What is the first symbolized faulting frame?
- Does the same exact artifact remain stable across ten telemetry-disabled attempts after the fix?
