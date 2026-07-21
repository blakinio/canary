---
task_id: CAN-20260721-e2e-controlled-otclient-build-stability
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-CONTROLLED-OTCLIENT-BUILD-STABILITY
status: implementing
agent: "GPT-5.6 Thinking"
branch: fix/e2e-controlled-otclient-build-stability
base_branch: main
created: 2026-07-21
updated: 2026-07-21
last_verified_commit: "e11ad06beebb3cd7c11a4d686f749ac54155cce5"
risk: medium
related_issue: ""
related_pr: "687"
depends_on:
  - merged Universal physical E2E platform PR #245
blocks:
  - PR #685 E2E-GAMEPLAY-003 Canary NPC promotion physical validation
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260721-e2e-controlled-otclient-build-stability.md
    - .github/workflows/universal-agent-e2e.yml
    - tests/e2e/test_controlled_otclient_build_workflow.py
  read_only:
    - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
    - docs/architecture/universal-e2e-gameplay-validation.md
    - tools/e2e/run_physical_e2e.sh
    - tests/e2e/scenarios/**
public_interfaces: []
cross_repo_tasks: []
---

# CAN-20260721 — controlled OTClient build stability

## Goal

Restore deterministic Universal Physical E2E availability after the pinned controlled OTClient build began failing reproducibly before physical scenario execution, without changing the pinned client revision or any feature scenario semantics.

## Acceptance criteria

- [x] Prove the failure is outside the blocked feature scenario: exact Canary build, scenario resolution, database bootstrap, ownership and incremental CI are green while physical execution is skipped because controlled OTClient build fails first.
- [x] Prove the pinned OTClient revision and hosted runner image match a recent successful Universal E2E build.
- [x] Test bounded controlled OTClient build parallelism without changing client source or revision and reject it as sufficient when the pre-Ninja failure persists.
- [x] Retain failure-only build diagnostics as an artifact for future first-failure analysis.
- [x] Replace opaque combined configure/build execution with explicit logged CMake configure and bounded build commands while preserving scenario-driven client source pinning.
- [x] Add focused workflow-contract coverage for source pinning, explicit logged configure/build, bounded parallelism, diagnostics retention and unrelated route behavior.
- [ ] Pass ownership, CI and Universal Agent E2E on the exact repair head.
- [ ] Merge through the normal autonomous gate and archive this task in a separate lifecycle PR.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T18:35:00+02:00
head: 6e9bf85781571c85cb6c3e8704fc342a650e3c8b
branch: fix/e2e-controlled-otclient-build-stability
pr: 687
status: implementing
context_routes:
  - universal-e2e
  - ci-repair
owned_paths:
  - docs/agents/tasks/active/CAN-20260721-e2e-controlled-otclient-build-stability.md
  - .github/workflows/universal-agent-e2e.yml
  - tests/e2e/test_controlled_otclient_build_workflow.py
proven:
  - blocked feature PR #685 exact head 68e93efddb47d460473ad5ddb69105ddabe87de8 passed Agent Task Ownership run 29845230906 and incremental CI run 29845231420.
  - Universal Agent E2E run 29845231189 passed scenario resolution, database bootstrap and exact Canary build on each attempt but failed before physical execution because Build controlled OTClient failed at Build OTClient release.
  - controlled OTClient build failed on three blocked-feature workflow attempts/jobs: 88684384444, 88686187662 and 88688491327; physical scenario execution was skipped each time.
  - the failed jobs all use pinned blakinio/otclient revision 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f.
  - successful E2E-GAMEPLAY-004 controlled OTClient job 88661289948 used the same pinned client revision and the same hosted runner image ubuntu-24.04 version 20260714.240.1.
  - the OTClient linux-release CMake build preset does not define a jobs/parallel limit.
  - initial PR #687 repair head b668699b3bf06341c2a1b1c25640ed8affe25757 passed Agent Task Ownership run 29848126195 and incremental CI run 29848126448.
  - Universal Agent E2E run 29848126832 on b668699b3bf06341c2a1b1c25640ed8affe25757 still failed at Build controlled OTClient despite --parallel 2; exact Canary, scenario resolution and database bootstrap passed.
  - the new failure-only artifact 8502357355 uploaded successfully and contained CMakeCache.txt but no .ninja_log, proving the failure occurred before the Ninja build phase and rejecting build parallelism as the root-cause fix.
  - CMakeCache.txt confirms project otclient, RelWithDebInfo, IPO disabled, unity enabled, x64-linux manifest mode and the expected vcpkg toolchain; no feature scenario or Canary runtime had started.
  - PR #687 now executes explicit `cmake --preset linux-release -DTOGGLE_BIN_FOLDER=ON -DOPTIONS_ENABLE_IPO=OFF` with output captured to otclient-configure.log.
  - PR #687 then executes explicit `cmake --build --preset linux-release --parallel 2` with output captured to otclient-build.log.
  - failure diagnostics retain both explicit command logs plus available CMake, Ninja and vcpkg diagnostic files.
  - focused coverage pins scenario-driven client repository/ref resolution, explicit configure/build commands, bounded parallelism, diagnostics retention and the unchanged route-download expression.
  - current main advanced by one unrelated OTBM repair commit to e11ad06beebb3cd7c11a4d686f749ac54155cce5; none of the three repair-owned paths overlap that commit.
derived:
  - parallelism was a disproven sufficient-fix hypothesis because the bounded attempt still failed before Ninja started.
  - replacing the opaque combined wrapper with explicit logged configure/build is the narrowest next diagnostic/repair step because it preserves the same CMake presets, options, vcpkg setup and pinned client revision while making the exact failing phase and stderr durable.
unknown:
  - exact CMake/vcpkg failure text; the next failure artifact will contain it if explicit configure/build still fails
  - whether the explicit configure/build path itself avoids the current wrapper-stage failure
conflicts: []
first_failure:
  marker: Universal Agent E2E / Build controlled OTClient / pre-Ninja configure stage
  evidence: repair run 29848126832 job 88694184226 failed with only CMakeCache.txt retained and no .ninja_log; diagnostic artifact 8502357355 uploaded successfully
rejected_hypotheses:
  - modify PR #685 NPC scenario to fix the failure; rejected because the failure occurs before physical execution and exact Canary/scenario/bootstrap validation are green
  - change the pinned OTClient revision; rejected because the same exact revision built successfully in accepted E2E-GAMEPLAY-004 evidence
  - change shared physical runner semantics; rejected because the runner never starts in the observed failure
  - keep an unrelated route-download regex rewrite introduced by full-file workflow editing; rejected and removed before validation
  - treat --parallel 2 as a sufficient fix; rejected by run 29848126832 because no Ninja build phase was reached
changed_paths:
  - docs/agents/tasks/active/CAN-20260721-e2e-controlled-otclient-build-stability.md
  - .github/workflows/universal-agent-e2e.yml
  - tests/e2e/test_controlled_otclient_build_workflow.py
validation:
  - command: Agent Task Ownership run 29848126195 on b668699b3bf06341c2a1b1c25640ed8affe25757
    result: PASS
    evidence: ownership and checkpoint validation passed
  - command: CI run 29848126448 on b668699b3bf06341c2a1b1c25640ed8affe25757
    result: PASS
    evidence: incremental required CI passed
  - command: Universal Agent E2E run 29848126832 on b668699b3bf06341c2a1b1c25640ed8affe25757
    result: FAIL
    evidence: exact Canary, scenario resolution and DB bootstrap passed; controlled OTClient failed before Ninja and diagnostics artifact 8502357355 was retained
blockers: []
next_action: Verify ownership, CI and Universal Agent E2E on the exact head with explicit logged OTClient configure/build; if it fails, inspect otclient-configure.log or otclient-build.log from the retained diagnostics artifact and fix only the proven failing phase.
```
