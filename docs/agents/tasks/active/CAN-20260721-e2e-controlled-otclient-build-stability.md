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
- [x] Bound controlled OTClient build parallelism through the existing pinned `lukka/run-cmake` interface without changing client source or revision.
- [x] Retain failure-only build diagnostics as an artifact for future first-failure analysis.
- [x] Add focused workflow-contract coverage for the bounded build and diagnostics behavior.
- [ ] Pass ownership, CI and Universal Agent E2E on the exact repair head.
- [ ] Merge through the normal autonomous gate and archive this task in a separate lifecycle PR.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T18:25:00+02:00
head: b60a90dbb6b1b6c3fab5e4518a0f64dcdea45d82
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
  - controlled OTClient build failed on three workflow attempts/jobs: 88684384444, 88686187662 and 88688491327; physical scenario execution was skipped each time.
  - the failed jobs all use pinned blakinio/otclient revision 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f.
  - successful E2E-GAMEPLAY-004 controlled OTClient job 88661289948 used the same pinned client revision and the same hosted runner image ubuntu-24.04 version 20260714.240.1.
  - the OTClient linux-release CMake build preset does not define a jobs/parallel limit.
  - the pinned lukka/run-cmake action exposes buildPresetAdditionalArgs for extra cmake --build arguments.
  - PR #687 changes only the Universal build-otclient job plus this task and one focused workflow-contract test.
  - the controlled OTClient build now passes --parallel 2 through the existing pinned run-cmake action without changing client source or revision.
  - a failure-only otclient-linux-release-build-diagnostics artifact retains CMake cache/configure logs, Ninja log and available vcpkg issue/log files.
  - focused coverage pins scenario-driven client repository/ref resolution, the exact pinned run-cmake action, bounded parallelism, diagnostics retention and the unchanged route-download expression.
  - current main advanced by one unrelated OTBM repair commit to e11ad06beebb3cd7c11a4d686f749ac54155cce5; none of the three repair-owned paths overlap that commit.
  - compare against the repair branch base reports the workflow diff as exactly 17 additions and zero deletions after removing a transient full-file rewrite artifact.
derived:
  - bounding only the controlled-client build parallelism is the narrowest generic mitigation for a reproducible build-stage stability failure whose source revision and runner image are unchanged from a recent success.
  - preserving a failure-only diagnostics artifact improves future autonomous first-failure analysis without changing the success-path artifact contract.
unknown:
  - exact compiler/runtime failure text from the three oversized pre-repair controlled OTClient job logs
  - whether reducing build parallelism alone resolves the current build-stage failure
conflicts: []
first_failure:
  marker: Universal Agent E2E / Build controlled OTClient / Build OTClient release
  evidence: blocked feature run 29845231189 failed on three attempts at jobs 88684384444, 88686187662 and 88688491327 before physical-client execution
rejected_hypotheses:
  - modify PR #685 NPC scenario to fix the failure; rejected because the failure occurs before physical execution and exact Canary/scenario/bootstrap validation are green
  - change the pinned OTClient revision; rejected because the same exact revision built successfully in accepted E2E-GAMEPLAY-004 evidence
  - change shared physical runner semantics; rejected because the runner never starts in the observed failure
  - keep an unrelated route-download regex rewrite introduced by full-file workflow editing; rejected and removed before validation
changed_paths:
  - docs/agents/tasks/active/CAN-20260721-e2e-controlled-otclient-build-stability.md
  - .github/workflows/universal-agent-e2e.yml
  - tests/e2e/test_controlled_otclient_build_workflow.py
validation: []
blockers: []
next_action: Verify Agent Task Ownership, CI and Universal Agent E2E on the exact PR #687 head; if the controlled OTClient build and required physical E2E pass, checkpoint the successful repair evidence and proceed to the normal final gate before unblocking PR #685.
```
