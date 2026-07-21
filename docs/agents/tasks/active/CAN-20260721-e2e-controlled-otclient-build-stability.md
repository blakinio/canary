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
- [x] Isolate and prove the exact configure failure from retained logs.
- [x] Add bounded retries only for recognized transient network failures while preserving fail-fast behavior for deterministic configure errors.
- [x] Keep explicit logged configure and bounded build commands plus focused workflow-contract coverage.
- [ ] Pass ownership, CI and Universal Agent E2E on the exact repair head.
- [ ] Merge through the normal autonomous gate and archive this task in a separate lifecycle PR.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T18:45:00+02:00
head: 1503961ad24da9c0f5d034b91b7eaebdbac356ce
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
  - Universal Agent E2E run 29845231189 passed scenario resolution, database bootstrap and exact Canary build on each attempt but failed before physical execution because Build controlled OTClient failed before producing a client artifact.
  - controlled OTClient build failed on three blocked-feature workflow attempts/jobs: 88684384444, 88686187662 and 88688491327; physical scenario execution was skipped each time.
  - the failed jobs all use pinned blakinio/otclient revision 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f.
  - successful E2E-GAMEPLAY-004 controlled OTClient job 88661289948 used the same pinned client revision and the same hosted runner image ubuntu-24.04 version 20260714.240.1.
  - initial PR #687 repair head b668699b3bf06341c2a1b1c25640ed8affe25757 passed Agent Task Ownership run 29848126195 and incremental CI run 29848126448.
  - Universal Agent E2E run 29848126832 on b668699b3bf06341c2a1b1c25640ed8affe25757 still failed before Ninja despite --parallel 2; artifact 8502357355 retained CMakeCache.txt and no .ninja_log, rejecting parallelism as a sufficient fix.
  - explicit logged configure/build repair head 506689abbfb396aafb017f13112ae16f90cc6645 passed Agent Task Ownership run 29848962746 and CI run 29848963217.
  - Universal Agent E2E run 29848963387 on 506689abbfb396aafb017f13112ae16f90cc6645 failed specifically at Configure OTClient release; build was skipped and diagnostic artifact 8502664982 uploaded successfully.
  - otclient-configure.log from artifact 8502664982 proves vcpkg failed while downloading freetype-VER-2-14-3.tar.gz from gitlab.freedesktop.org after its three internal attempts, each ending with HTTP 504.
  - the same log shows vcpkg install failed and CMake stopped during project/toolchain configuration before any Ninja build phase.
  - PR #687 now retries the idempotent configure command at most three workflow-level attempts only when the attempt log matches recognized transient network failures: HTTP 429/500/502/503/504, timeout, DNS resolution, connection or receive failures.
  - deterministic configure failures that do not match the transient-network allowlist still fail immediately.
  - configure retries use 15-second then 30-second bounded backoff and retain the combined configure log plus each per-attempt log.
  - the build remains explicit and bounded as `cmake --build --preset linux-release --parallel 2` with output captured to otclient-build.log.
  - pinned client repository/ref resolution, vcpkg baseline and dependency source are unchanged.
  - focused coverage pins transient-only retry classification, bounded retry count/backoff, explicit build parallelism, diagnostics retention and the unchanged route-download expression.
  - current main advanced by one unrelated OTBM repair commit to e11ad06beebb3cd7c11a4d686f749ac54155cce5; none of the three repair-owned paths overlap that commit.
derived:
  - the reproducible blocker is an external transient dependency-source availability failure, not feature code, Canary code, OTClient source compilation or build parallelism.
  - bounded transient-only configure retry is narrower than changing the pinned OTClient revision, forking the vcpkg port, replacing the FreeType source URL or weakening deterministic configure failures.
unknown:
  - whether the external FreeType source recovers within the bounded workflow-level configure retries on the next exact-head run
conflicts: []
first_failure:
  marker: Universal Agent E2E / Build controlled OTClient / Configure OTClient release / vcpkg FreeType source download
  evidence: run 29848963387 job 88696905854; artifact 8502664982 otclient-configure.log reports three HTTP 504 download failures for freetype-VER-2-14-3.tar.gz from gitlab.freedesktop.org
rejected_hypotheses:
  - modify PR #685 NPC scenario to fix the failure; rejected because the failure occurs before physical execution and exact Canary/scenario/bootstrap validation are green
  - change the pinned OTClient revision; rejected because the same exact revision built successfully in accepted E2E-GAMEPLAY-004 evidence
  - change shared physical runner semantics; rejected because the runner never starts in the observed failure
  - keep an unrelated route-download regex rewrite introduced by full-file workflow editing; rejected and removed before validation
  - treat --parallel 2 as a sufficient fix; rejected by run 29848126832 because no Ninja build phase was reached
  - replace the FreeType source URL or vcpkg port; rejected because the proven failure is HTTP 504 from the canonical dependency source and bounded transient retry is less invasive
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
  - command: Agent Task Ownership run 29848962746 on 506689abbfb396aafb017f13112ae16f90cc6645
    result: PASS
    evidence: ownership and checkpoint validation passed
  - command: CI run 29848963217 on 506689abbfb396aafb017f13112ae16f90cc6645
    result: PASS
    evidence: incremental required CI passed
  - command: Universal Agent E2E run 29848963387 on 506689abbfb396aafb017f13112ae16f90cc6645
    result: FAIL
    evidence: controlled OTClient explicit configure failed on external FreeType HTTP 504; artifact 8502664982 retained exact configure output
blockers: []
next_action: Verify ownership, CI and Universal Agent E2E on the exact head with transient-only bounded configure retries; if configure still fails, inspect the retained per-attempt logs to determine whether all retries hit the same external 504 or a new deterministic failure before changing any source or pin.
```
