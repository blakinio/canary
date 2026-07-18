---
task_id: CAN-20260718-windows-debug-vcpkg-build-type
program_id: agent-governance
coordination_id: ""
status: implementing
agent: "GPT-5.5 Thinking"
branch: fix/windows-debug-vcpkg-build-type
base_branch: main
created: 2026-07-18T06:39:37Z
updated: 2026-07-18T06:39:37Z
last_verified_commit: "7cf5c409caee40a5ec2ca6ff89426a0d24613709"
risk: low
related_issue: ""
related_pr: "485"
depends_on: []
blocks: []
owned_paths:
  exclusive:
    - CMakePresets.json
    - cmake/triplets/x64-windows-test-debug.cmake
    - docs/agents/tasks/active/CAN-20260718-windows-debug-vcpkg-build-type.md
  shared: []
  read_only:
    - docs/agents/BUILD_TEST_MATRIX.md
modules_touched:
  - Windows debug/vcpkg build configuration
reuses:
  - existing windows-debug CMake preset
  - existing x64-windows-test-debug vcpkg triplet
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Complete PR #485 without expanding the build fix beyond restoring normal dual-config vcpkg dependency installation for Windows debug/test-debug configurations.

# Acceptance criteria

- [x] Prove the fix is still required on current `main`.
- [x] Synchronize the published branch with current `main` without reset, stash, plain force, or push to `main`.
- [x] Keep the implementation change limited to the two existing build configuration files.
- [ ] Verify the task record and ownership checkpoint on the current PR head.
- [ ] Verify required Windows debug/vcpkg validation and exact-final-head GitHub checks.
- [ ] Apply `ci:final-gate` before the final checkpoint commit and make no later commit after the green gate.
- [ ] Mark Ready and squash-merge only after the exact-final-head merge gate passes.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-18T06:39:37Z
head: 7cf5c409caee40a5ec2ca6ff89426a0d24613709
branch: fix/windows-debug-vcpkg-build-type
pr: 485
status: validating
context_routes:
  - agent-governance
  - build-toolchain
owned_paths:
  - CMakePresets.json
  - cmake/triplets/x64-windows-test-debug.cmake
  - docs/agents/tasks/active/CAN-20260718-windows-debug-vcpkg-build-type.md
proven:
  - PR 485 targets main from fix/windows-debug-vcpkg-build-type and remains draft.
  - Current main at synchronization was 470a5e6deaaed67c17a2ddb2ab7b5bc1ed9609f6.
  - Before synchronization the branch was 1 commit ahead and 28 commits behind current main.
  - Current main still contains VCPKG_BUILD_TYPE=debug in both affected configurations, so the fix is not already present or obsolete.
  - The 28 intervening main commits did not modify CMakePresets.json or cmake/triplets/x64-windows-test-debug.cmake.
  - The branch was advanced only by non-force fast-forward ref updates through merge heads containing current main; after synchronization it is 0 commits behind current main.
  - The current tree diff against main changes only CMakePresets.json and cmake/triplets/x64-windows-test-debug.cmake before this task record is added.
  - The PR body records a prior clean windows-debug configure PASS, windows-debug build PASS, abseil installation PASS, resolver unittest 4/4 PASS, and a controlled CTest stop at 609/644 with remaining failures classified outside this fix.
derived:
  - The smallest valid implementation remains deletion of the two debug-only VCPKG_BUILD_TYPE restrictions.
  - Exact-final-head Windows CI is required after synchronization because this sandbox cannot execute a native Windows build.
unknown:
  - Local checkout status, branch tracking, remotes and worktree list are not observable because the sandbox has no usable local clone and direct GitHub network access is unavailable.
  - Exact-final-head GitHub check results are pending.
conflicts: []
first_failure:
  marker: none
  evidence: No in-scope implementation failure is currently proven; exact-final-head validation is pending.
rejected_hypotheses:
  - The fix is already on main: current main still contains both VCPKG_BUILD_TYPE=debug restrictions.
  - Main invalidated the fix: intervening main changes do not touch either implementation path.
changed_paths:
  - CMakePresets.json
  - cmake/triplets/x64-windows-test-debug.cmake
  - docs/agents/tasks/active/CAN-20260718-windows-debug-vcpkg-build-type.md
validation:
  - command: compare current main to synchronized branch
    result: PASS
    evidence: branch is 0 behind current main and implementation tree diff is limited to the two intended build files before adding this task record.
  - command: prior local cmake --preset windows-debug
    result: PASS
    evidence: recorded in PR 485 body on the original fix head; not re-run in this non-Windows sandbox.
  - command: prior local cmake --build --preset windows-debug --parallel 16
    result: PASS
    evidence: recorded in PR 485 body on the original fix head; not re-run in this non-Windows sandbox.
  - command: exact-final-head GitHub CI
    result: NOT_RUN
    evidence: final checkpoint head has not been created yet.
blockers:
  - Direct local Windows re-execution is unavailable in this sandbox; exact-head affected-platform CI must provide the post-synchronization Windows validation.
next_action: Validate this task record and current synchronized head, inspect GitHub CI, then apply ci:final-gate before the final checkpoint commit.
```
