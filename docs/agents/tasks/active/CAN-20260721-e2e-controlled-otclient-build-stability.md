---
task_id: CAN-20260721-e2e-controlled-otclient-build-stability
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-CONTROLLED-OTCLIENT-BUILD-STABILITY
status: ready
agent: "GPT-5.6 Thinking"
branch: fix/e2e-controlled-otclient-build-stability
base_branch: main
created: 2026-07-21
updated: 2026-07-21
last_verified_commit: "d83563943e298df33edd084e944812464b8a3ff2"
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

Restore deterministic Universal Physical E2E availability after the pinned controlled OTClient vcpkg configure path began failing before physical scenario execution, without changing the pinned client revision, vcpkg baseline, FreeType port semantics, or feature scenarios.

## Acceptance criteria

- [x] Prove the failure is outside the blocked feature scenario and before physical execution.
- [x] Isolate the first failure to the pinned vcpkg FreeType 2.14.3 source download.
- [x] Reject build parallelism and bounded retry as sufficient fixes using retained exact failure evidence.
- [x] Prove the GitHub `freetype/freetype` `VER-2-14-3` archive has the exact SHA512 required by the pinned vcpkg port.
- [x] Pre-seed only the standard vcpkg downloads cache with the verified mirror archive; do not modify the pinned client, vcpkg baseline, port, or scenario semantics.
- [x] Preserve the original pinned `run-cmake` configure/build contract.
- [x] Retain fallback provenance in successful OTClient artifacts and failure diagnostics.
- [x] Add focused workflow-contract coverage for source pinning, hash/cache placement, unchanged build contract, diagnostics, provenance, and unrelated route behavior.
- [x] Pass ownership, CI and Universal Agent E2E on the exact implementation head, including a successful controlled OTClient build and physical login/relog scenario.
- [ ] Merge through the normal autonomous final gate and archive this task in a separate lifecycle PR.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T23:35:00+02:00
head: f395271524a380d3bf8b0b333b39ec23d96ed701
branch: fix/e2e-controlled-otclient-build-stability
pr: 687
status: ready
context_routes:
  - universal-e2e
  - ci-repair
owned_paths:
  - docs/agents/tasks/active/CAN-20260721-e2e-controlled-otclient-build-stability.md
  - .github/workflows/universal-agent-e2e.yml
  - tests/e2e/test_controlled_otclient_build_workflow.py
proven:
  - PR #685 feature head 68e93efddb47d460473ad5ddb69105ddabe87de8 passed ownership and incremental CI but its Universal E2E never reached physical execution because the generic controlled OTClient build failed first.
  - all failures used pinned blakinio/otclient revision 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f, which had built successfully in accepted E2E-GAMEPLAY-004 evidence.
  - bounded build parallelism was rejected by Universal E2E 29848126832 because the failure remained pre-Ninja; artifact 8502357355 contained no .ninja_log.
  - explicit configure diagnostics from Universal E2E 29848963387 artifact 8502664982 proved vcpkg failed downloading FreeType 2.14.3 from gitlab.freedesktop.org with repeated HTTP 504 responses before compilation.
  - three workflow-level configure retries in Universal E2E 29849912071 all hit the same FreeType HTTP 504, rejecting retry as a sufficient fix.
  - one-shot mirror probe run 29851038067 proved the GitHub freetype/freetype VER-2-14-3 archive SHA512 is c3b6b0cc4b428c9c647ab2148386901dfd315273b68051940e8fea6010d46fdd2913467c3ef58be0d499b8e2ef5a0f1a4cc5e739756155587f4f7dff08ef9695, exactly matching the pinned vcpkg port; the probe workflow was removed before final validation.
  - final workflow pre-seeds vcpkg/downloads/freetype-freetype-VER-2-14-3.tar.gz from the verified GitHub mirror and validates the exact SHA512 before the original vcpkg/run-cmake path consumes it.
  - final workflow preserves the original pinned client ref, pinned vcpkg baseline, pinned run-cmake action, configure preset, build preset and configure options.
  - successful OTClient artifact 8510661114 records source=github-mirror, the exact mirror URL and SHA512, and the standard vcpkg downloads cache path in freetype-source-fallback.txt.
  - exact implementation head f395271524a380d3bf8b0b333b39ec23d96ed701 passed Agent Task Ownership 29867906121, CI 29867906077 and Universal Agent E2E 29867906420.
  - Universal Agent E2E 29867906420 built the controlled OTClient successfully after the verified fallback step and passed Physical client / login/relog plus Required physical E2E.
  - PR #687 changed-file inventory is limited to the workflow, focused contract test and this active task; there are no review threads, reviews or comments blocking merge.
  - PR #687 is ready for review, mergeable, and labeled ci:final-gate before this final checkpoint commit.
derived:
  - verified cache pre-seeding is narrower and safer than changing the pinned OTClient revision, vcpkg baseline, FreeType port/source semantics, or feature scenario.
unknown: []
conflicts: []
first_failure:
  marker: none
  evidence: exact implementation-head ownership, CI and Universal Agent E2E all passed; historical FreeType HTTP 504 is resolved by the verified cache fallback
rejected_hypotheses:
  - modify PR #685 NPC scenario; failure occurred before physical execution
  - change pinned OTClient revision; same revision had accepted prior evidence
  - treat --parallel 2 as sufficient; failure remained pre-Ninja
  - rely only on workflow-level retry; all bounded attempts hit the same HTTP 504
  - replace or fork the vcpkg FreeType port; identical mirror bytes can be supplied through the standard download cache instead
changed_paths:
  - docs/agents/tasks/active/CAN-20260721-e2e-controlled-otclient-build-stability.md
  - .github/workflows/universal-agent-e2e.yml
  - tests/e2e/test_controlled_otclient_build_workflow.py
validation:
  - command: Agent Task Ownership run 29867906121 on f395271524a380d3bf8b0b333b39ec23d96ed701
    result: PASS
    evidence: active ownership, focused tests and checkpoint governance passed
  - command: CI run 29867906077 on f395271524a380d3bf8b0b333b39ec23d96ed701
    result: PASS
    evidence: exact implementation-head incremental CI passed
  - command: Universal Agent E2E run 29867906420 on f395271524a380d3bf8b0b333b39ec23d96ed701
    result: PASS
    evidence: verified FreeType fallback, controlled OTClient build, physical login/relog and Required physical E2E passed
blockers: []
next_action: Complete the normal final-gate and lifecycle closure for PR #687 by merging only after all exact checkpoint-head required checks are green, then archive the completed task in a separate lifecycle PR.
```
