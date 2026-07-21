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
last_verified_commit: "4723cd157801b5a045531a05f7fe83387a8aca12"
risk: medium
related_issue: ""
related_pr: ""
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
- [ ] Bound controlled OTClient build parallelism through the existing pinned `lukka/run-cmake` interface without changing client source or revision.
- [ ] Retain failure-only build diagnostics as an artifact for future first-failure analysis.
- [ ] Add focused workflow-contract coverage for the bounded build and diagnostics behavior.
- [ ] Pass ownership, CI and Universal Agent E2E on the exact repair head.
- [ ] Merge through the normal autonomous gate and archive this task in a separate lifecycle PR.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T18:10:00+02:00
head: 4723cd157801b5a045531a05f7fe83387a8aca12
branch: fix/e2e-controlled-otclient-build-stability
pr: null
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
  - Universal Agent E2E currently invokes the controlled OTClient build preset without buildPresetAdditionalArgs.
derived:
  - bounding only the controlled-client build parallelism is the narrowest generic mitigation for a reproducible build-stage stability failure whose source revision and runner image are unchanged from a recent success.
  - preserving a failure-only diagnostics artifact is required because current oversized job logs are difficult to retain and inspect precisely through autonomous evidence tooling.
unknown:
  - exact compiler/runtime failure text from the three oversized controlled OTClient job logs
  - whether reducing build parallelism alone resolves the current build-stage failure
conflicts: []
first_failure:
  marker: Universal Agent E2E / Build controlled OTClient / Build OTClient release
  evidence: run 29845231189 failed on three attempts at jobs 88684384444, 88686187662 and 88688491327 before physical-client execution
rejected_hypotheses:
  - modify PR #685 NPC scenario to fix the failure; rejected because the failure occurs before physical execution and exact Canary/scenario/bootstrap validation are green
  - change the pinned OTClient revision; rejected because the same exact revision built successfully in accepted E2E-GAMEPLAY-004 evidence
  - change shared physical runner semantics; rejected because the runner never starts in the observed failure
changed_paths:
  - docs/agents/tasks/active/CAN-20260721-e2e-controlled-otclient-build-stability.md
validation: []
blockers: []
next_action: Add bounded build parallelism and failure-only controlled OTClient diagnostics to Universal Agent E2E with focused workflow-contract coverage, then validate the exact repair head and use its physical E2E result to decide whether the mitigation is sufficient.
```
