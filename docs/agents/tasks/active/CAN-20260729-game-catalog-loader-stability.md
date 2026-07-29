---
task_id: CAN-20260729-game-catalog-loader-stability
program_id: CAN-PROGRAM-GAME-CATALOG-COMPLETENESS
coordination_id: "OTS-20260728-game-catalog-v1"
status: planned
agent: "chatgpt"
branch: fix/CAN-20260729-game-catalog-loader-stability
base_branch: main
created: 2026-07-29T19:35:00Z
updated: 2026-07-29T19:45:00Z
last_verified_commit: "ac354e27eae99b289050ec6dd0892edc9c71cd13"
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
    - src/game/catalog/catalog_runtime.cpp
  shared:
    - src/game/game.cpp
    - tests/game_catalog/**
    - tests/unit/game/catalog/game_catalog_test.cpp
    - .github/workflows/game-catalog.yml
    - docs/agents/programs/GAME_CATALOG_COMPLETENESS_PROGRAM.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
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

- [ ] Reproduce or tightly bound the two exit-139 failures using the exact default datapack, one compiled artifact, and explicit telemetry-disabled/enabled attempts.
- [ ] Capture a symbolized fault location or equivalent sanitizer evidence before selecting a runtime fix; do not infer the cause from logging alone.
- [ ] Fix the smallest proven root cause without making startup telemetry a correctness requirement.
- [ ] Run at least ten sequential telemetry-disabled exports and two telemetry-enabled controls from the same final binary artifact with every attempt visible.
- [ ] Prove all successful attempts publish byte-identical controlled snapshots and valid lowercase SHA-256 sidecars.
- [ ] Preserve zero database/network endpoint syscalls, atomic publication, schema 1.2 semantics, and the 92 reviewed over-maximum thresholds.
- [ ] Keep production configuration, datapack content, schema bytes, import, staging, and production activation unchanged.
- [ ] Pass focused checks, exact-head Game Catalog, CI, ownership, and required stability checks.
- [ ] Update the program record, module catalogue/changelog impact, and durable checkpoint.
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

The exporter is functionally complete, but telemetry-independent definition loading is not certified. Two telemetry-disabled complete loads crashed after proficiencies, while telemetry-enabled executions passed. The next loader is `appearances.dat`, but the faulting frame and trigger remain unknown.

# Plan

1. Publish this task and a draft PR, then add a bounded diagnostic/control matrix that preserves every attempt and captures a symbolized crash.
2. Use the captured fault evidence to implement the smallest root-cause fix.
3. Run the repeated exact-artifact stability proof and final repository merge gate.

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

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Treat telemetry as a control, never a fix | logging changes correlate with the outcome but do not prove causality | not required |
| Require one exact artifact for all counted attempts | excludes compilation drift from the stability classification | not required |
| Preserve each failed attempt and backtrace | prevents a flaky pass from erasing the known conflict | not required |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `src/game/catalog/catalog_runtime.cpp` | exclusive | isolate and repair export-only definition loading | investigating |
| `src/game/game.cpp` | shared | edit only if symbolized evidence identifies appearance loading | read-only pending evidence |
| `.github/workflows/game-catalog.yml` | shared | exact-artifact diagnostic and repeated stability proof | planned |
| `luaStartupLoadTelemetry` | read-only interface | telemetry-off/on experimental control | unchanged |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| `1e155cd8407246a154dbf81c33aa316f0752de8f` | `python3 tools/agents/task_ownership.py` | passed | 33 active task records before this claim |
| `e85be1bf6e237448d624d28ff891362d5f67f9b6` | runtime jobs `90670860532`, `90675503517` | failed | default export exited 139 after proficiencies |
| `e85be1bf6e237448d624d28ff891362d5f67f9b6` | Game Catalog `30481456654`, rerun `90678481552` | passed | telemetry-enabled complete export |
| `ac354e27eae99b289050ec6dd0892edc9c71cd13` | Game Catalog `30485475053` | passed | one complete telemetry-disabled default export passed |
| working tree after `ac354e27eae99b289050ec6dd0892edc9c71cd13` | parse workflow YAML and runtime step with `bash -n` | passed | counted stability workflow parses |

# Failed approaches and dead ends

- Enabling telemetry as a permanent workflow workaround is rejected because it masks rather than explains the stability dependency.
- Inferring that proficiencies caused the crash is rejected because its loader returned and logged success; the fault frame is not captured.
- Treating every telemetry-disabled load as deterministically crashing is rejected by Game Catalog `30485475053`.
- Treating two later passes as disproving the two crashes is rejected because the config condition changed.

# Risks and compatibility

- Runtime: suspected undefined behavior or lifetime/race sensitivity during definition loading.
- Data/migration: no data or migration changes allowed.
- Security: diagnostics must not publish secrets, private paths, dumps, or credentials.
- Backward compatibility: normal startup behavior and all existing schema versions must remain unchanged.
- Cross-repo rollout: no consumer change is expected; any discovered contract impact becomes a separate task.
- Rollback: revert the bounded runtime/workflow commit; staging remains blocked throughout.

# Remaining work

1. Run the 10-off/2-on exact-artifact series and inspect any captured backtrace before changing runtime source.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T19:45:00Z
head: ac354e27eae99b289050ec6dd0892edc9c71cd13
branch: fix/CAN-20260729-game-catalog-loader-stability
pr: 1015
status: investigating
context_routes:
  - agent-governance
  - cpp-runtime
  - ci-repair
owned_paths:
  - docs/agents/tasks/active/CAN-20260729-game-catalog-loader-stability.md
  - src/game/catalog/catalog_runtime.cpp
  - src/game/game.cpp
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
  - Schema 1.2 producer and consumer are merged without staging or production activation.
derived:
  - The failure is intermittent and correlated with, but not deterministically controlled by, loader telemetry.
  - The appearance loader is the next bounded diagnostic target after proficiencies.
unknown:
  - Exact faulting frame and root cause of exit 139.
  - Whether the trigger is timing, stack or heap layout, object lifetime, or another undefined behavior.
conflicts:
  - Telemetry-disabled complete loads failed twice while telemetry-enabled complete loads passed.
first_failure:
  marker: telemetry-independent complete default-datapack definition load
  evidence: Runtime jobs 90670860532 and 90675503517 exited 139 after proficiencies.
rejected_hypotheses:
  - Weapon proficiencies are proven as the faulting loader because their success log precedes the crash.
  - Startup telemetry is an acceptable permanent correctness requirement.
  - Every telemetry-disabled complete load crashes.
  - Later successful runs erase the earlier telemetry-disabled failures.
changed_paths:
  - docs/agents/tasks/active/CAN-20260729-game-catalog-loader-stability.md
  - docs/agents/programs/GAME_CATALOG_COMPLETENESS_PROGRAM.md
  - .github/workflows/game-catalog.yml
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
blockers:
  - Game Catalog staging remains blocked pending telemetry-independent stability.
next_action: Run the 10-off/2-on exact-artifact series and inspect any captured backtrace before changing runtime source.
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
