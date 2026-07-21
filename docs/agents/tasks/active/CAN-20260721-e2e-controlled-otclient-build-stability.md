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
updated_at: 2026-07-21T18:50:00+02:00
head: 8a946e0473be8235bf05e0d728d41d12b91fd689
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
  - PR #685 feature head 68e93efddb47d460473ad5ddb69105ddabe87de8 passed ownership and incremental CI; its Universal E2E never reached physical execution because the generic controlled OTClient build failed first on three attempts.
  - all blocked-feature failures used pinned blakinio/otclient revision 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f, which had built successfully earlier on the same ubuntu-24.04 image version 20260714.240.1 for accepted E2E-GAMEPLAY-004 evidence.
  - initial PR #687 head b668699b3bf06341c2a1b1c25640ed8affe25757 passed ownership and CI, but Universal E2E 29848126832 still failed before Ninja despite --parallel 2; artifact 8502357355 contained CMakeCache.txt and no .ninja_log.
  - explicit logged configure/build head 506689abbfb396aafb017f13112ae16f90cc6645 passed ownership and CI; Universal E2E 29848963387 isolated the failure specifically to Configure OTClient release and retained artifact 8502664982.
  - otclient-configure.log from artifact 8502664982 proves vcpkg failed downloading freetype-VER-2-14-3.tar.gz from gitlab.freedesktop.org after three internal attempts, each returning HTTP 504.
  - the same configure log proves CMake stopped during vcpkg manifest installation before any Ninja build phase; feature scenario, Canary runtime and OTClient compilation had not started.
  - PR #687 now retries the idempotent configure command at most three workflow-level attempts only for recognized transient failures: HTTP 429/500/502/503/504, timeout, DNS, connection or receive errors.
  - deterministic configure failures outside that transient allowlist still fail immediately; retry backoff is bounded to 15 seconds then 30 seconds.
  - configure diagnostics retain a combined log plus per-attempt logs, while the explicit build remains `cmake --build --preset linux-release --parallel 2` with its own retained log.
  - pinned client repository/ref resolution, vcpkg baseline, dependency source and feature scenario semantics are unchanged.
  - focused coverage pins transient-only classification, bounded retry count/backoff, explicit build parallelism, diagnostics retention and the unchanged route-download expression.
  - CI run 29849755892 passed on retry-policy head 8a946e0473be8235bf05e0d728d41d12b91fd689; ownership run 29849755628 failed only because this checkpoint exceeded the 16-item proven compactness limit, which this commit corrects.
  - current main advanced only through unrelated OTBM repair work relative to the repair branch base; no repair-owned path overlap was identified.
derived:
  - the blocker is an external transient dependency-source availability failure, not feature code, Canary code, OTClient source compilation or build parallelism.
  - bounded transient-only configure retry is narrower than changing the pinned OTClient revision, forking the vcpkg port, replacing the FreeType source URL or weakening deterministic configure failures.
unknown:
  - whether the external FreeType source recovers within the bounded workflow-level configure retries on the retry-policy runtime validation
conflicts: []
first_failure:
  marker: Universal Agent E2E / Build controlled OTClient / Configure OTClient release / vcpkg FreeType source download
  evidence: run 29848963387 job 88696905854; artifact 8502664982 otclient-configure.log reports three HTTP 504 download failures for freetype-VER-2-14-3.tar.gz from gitlab.freedesktop.org
rejected_hypotheses:
  - modify PR #685 NPC scenario; rejected because failure occurs before physical execution
  - change pinned OTClient revision; rejected because the same revision built successfully in accepted evidence
  - treat --parallel 2 as sufficient; rejected because the bounded attempt still failed before Ninja
  - replace FreeType source or vcpkg port; rejected because transient-only retry is less invasive for the proven HTTP 504
changed_paths:
  - docs/agents/tasks/active/CAN-20260721-e2e-controlled-otclient-build-stability.md
  - .github/workflows/universal-agent-e2e.yml
  - tests/e2e/test_controlled_otclient_build_workflow.py
validation:
  - command: Agent Task Ownership run 29848126195 and CI run 29848126448 on b668699b3bf06341c2a1b1c25640ed8affe25757
    result: PASS
    evidence: initial bounded-build repair passed governance and incremental CI
  - command: Universal Agent E2E run 29848126832 on b668699b3bf06341c2a1b1c25640ed8affe25757
    result: FAIL
    evidence: failure remained pre-Ninja and diagnostics artifact 8502357355 was retained
  - command: Agent Task Ownership run 29848962746 and CI run 29848963217 on 506689abbfb396aafb017f13112ae16f90cc6645
    result: PASS
    evidence: explicit logged configure/build repair passed governance and incremental CI
  - command: Universal Agent E2E run 29848963387 on 506689abbfb396aafb017f13112ae16f90cc6645
    result: FAIL
    evidence: configure log proved external FreeType HTTP 504 and artifact 8502664982 retained exact output
  - command: CI run 29849755892 on 8a946e0473be8235bf05e0d728d41d12b91fd689
    result: PASS
    evidence: retry-policy implementation passed incremental CI
blockers: []
next_action: Verify ownership, CI and Universal Agent E2E on the compact-checkpoint exact head; if the immediate-parent runtime evidence shows the retry policy succeeded, proceed to final gate, otherwise inspect retained per-attempt logs and change only the proven failure mode.
```
