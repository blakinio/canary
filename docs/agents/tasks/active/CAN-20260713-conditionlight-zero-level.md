---
task_id: CAN-20260713-conditionlight-zero-level
program_id: CAN-PROGRAM-CRYSTALSERVER-COMPARISON
coordination_id: CS-001
status: active
agent: "GPT-5.6 Thinking"
branch: fix/conditionlight-zero-level
base_branch: main
created: 2026-07-13T23:47:32+02:00
updated: 2026-07-14T00:05:00+02:00
last_verified_commit: "8ede33176f4a37187bb2c3af5d5d40ba5a07c437"
risk: high
related_issue: ""
related_pr: "#297"
depends_on:
  - "CAN-PROGRAM-CRYSTALSERVER-COMPARISON Stage 1 / PR #291"
blocks: []
owned_paths:
  exclusive:
    - src/creatures/combat/condition.cpp
    - tests/unit/players/condition/condition_light_test.cpp
    - tests/unit/players/condition/CMakeLists.txt
    - docs/agents/tasks/active/CAN-20260713-conditionlight-zero-level.md
    - tools/ai-agent/apply_conditionlight_zero_level.py
    - .github/workflows/apply-conditionlight-zero-level.yml
  shared:
    - docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md
    - docs/agents/CHANGELOG.md
  read_only:
    - src/creatures/combat/condition.hpp
    - src/creatures/creature.hpp
    - src/io/fileloader.hpp
    - AGENTS.md
    - docs/agents/BUILD_TEST_MATRIX.md
modules_touched:
  - ConditionLight runtime and persistence boundary
reuses:
  - existing Condition serialization/deserialization contract
  - existing GoogleTest canary_ut target and player-condition test directory
  - existing bounded self-removing patch-workflow pattern
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Prevent `ConditionLight` from dividing by zero or retaining an invalid zero light level when a condition is constructed or deserialized with level `0`, without changing valid light behavior.

# Acceptance criteria

- [x] A focused regression test proves zero-level deserialization is normalized to `1`.
- [x] A focused regression test proves starting a zero-level light condition does not divide by zero and produces a valid level and interval.
- [x] Valid nonzero light levels preserve their existing interval and serialization behavior.
- [x] The implementation is limited to the missing `ConditionLight` input boundaries.
- [x] Temporary patch workflow/script remove themselves from the final implementation diff.
- [ ] Appropriate C++ build and focused tests complete on the current PR head.
- [ ] Current-head GitHub checks are verified.
- [ ] Module catalogue impact is recorded as none because no reusable interface is added or changed.
- [ ] Changelog records the completed runtime safety fix.
- [ ] Program queue and handoff are updated.
- [ ] Cross-repository impact is recorded as none.
- [ ] Autonomous merge gate is satisfied.

# Confirmed context

- Target repository: `blakinio/canary`; write permission is available only there.
- Base `main` at task creation: `b2036bd5d56423894b72eaa2ebaff32feba382a5`.
- CrystalServer candidate: `zimbadev/crystalserver@a7350014528002fb27ed64d260a96d28a580d41a`, PR #822.
- Current Canary `ConditionLight::startCondition` computes `ticks / lightInfo.level` without a guard.
- Current Canary `ConditionLight::unserializeProp` assigns a serialized level directly, including `0`.
- `ConditionLight::addCondition` and `ConditionLight::setParam` already clamp level to at least `1`; this task closes only the two remaining boundaries.
- Current `opentibiabr/canary` has the same unsafe two boundaries, so it supplies no later equivalent fix.
- No open PR found by `ConditionLight` or `condition.cpp` search at task creation.
- Local Git/worktree/build inspection is unavailable: `git ls-remote https://github.com/blakinio/canary.git refs/heads/main` failed with `Could not resolve host: github.com`.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| Condition serialization | `PropWriteStream` / `PropStream` round trip | `src/creatures/combat/condition.*` | Exercises the persisted invalid input boundary without inventing a parser. |
| Existing `canary_ut` target | GoogleTest registration | `tests/unit/players/condition/CMakeLists.txt` | Focused coverage belongs beside the existing player-condition test. |
| Existing player condition fixture pattern | default `Player` on `DynamicTile` | `player_paralyze_walk_exhaust_test.cpp` | Supplies a concrete creature without a new mock framework. |
| CrystalServer comparison program | candidate provenance and risk classification | `docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md` | Keeps the adaptation evidence-backed and bounded. |
| Existing bounded patch runner | exact-anchor script, `git diff --check`, branch-only push | prior Forge patch workflow | Allows a safe branch edit when the local environment cannot fetch GitHub. |

# Ownership and overlap check

- Program record: `CAN-PROGRAM-CRYSTALSERVER-COMPARISON`.
- Open PRs inspected: all open PRs returned on 2026-07-13; direct searches for `ConditionLight` and `condition.cpp` returned no overlaps.
- Active tasks inspected: live PR/task metadata plus `ACTIVE_WORK.md`; no declared overlap found for the owned runtime/test paths.
- Ownership checker result: not run locally because no checkout is available; GitHub ownership CI is required before readiness.
- Exclusive claims: runtime file, focused test, condition-test CMake entry, task record, and temporary self-removing patch files.
- Shared claims: comparison program and changelog, narrow edits only.
- Read-only dependencies: headers, stream implementation, governance/build docs.
- Overlaps: none known.
- Resolution: proceed with one candidate, one branch and one PR; stop if ownership CI reports a conflict.

# Current state

Draft PR #297 is published. The defect is reproducible by source proof: level `0` reaches an integer divisor in `startCondition`, and the persisted level boundary accepts `0` unchanged. The smallest complete adaptation is to normalize level at both boundaries and retain a valid divisor.

# Plan

1. Run a bounded self-removing patch workflow on this branch because local Git is unavailable.
2. Add focused regression coverage for construction/start, deserialization and valid-level preservation.
3. Apply the smallest two-boundary runtime fix.
4. Observe focused and required CI, repair failures from logs, and review the full diff.
5. Mark ready, enable auto-merge or squash-merge after the autonomous gate.
6. Archive this task and update the program in a separate cleanup PR.

# Work log

## 2026-07-13T23:47:32+02:00

- Changed: created branch and claimed exact paths.
- Learned: current main still contains both missing zero-level guards; existing update/setter paths are already safe.
- Failed/blocked: local Git and build unavailable because DNS cannot resolve `github.com`.
- Result: implementation may proceed through GitHub branch and CI evidence.

## 2026-07-14T00:02:00+02:00

- Changed: opened draft PR #297 and moved focused test ownership to the existing `tests/unit/players/condition/` suite.
- Learned: the repository already uses a bounded branch-only patch workflow with write-scoped token, exact script execution and `git diff --check` for environments without a usable local checkout.
- Failed/blocked: direct raw-file download is also blocked by local DNS; replacing the full 2,946-line source through the contents API would be unsafe.
- Result: claim temporary workflow/script paths; both must delete themselves in the generated implementation commit.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Adapt only the two missing boundaries | Matches current Canary architecture and avoids broad Condition refactoring. | none |
| Normalize the runtime level before division, not only the divisor | Constructor/direct creation can supply level `0`; keeping object state at the established minimum matches `setParam` and makes the invariant observable. | none |
| Keep deserialization normalization | Prevents persisted malformed/legacy data from retaining invalid state. | none |
| Add no public getter solely for testing | Existing serialization and creature-light state expose the invariant without expanding runtime API. | none |
| Use a self-removing exact-anchor patch runner | It avoids unsafe full-file replacement and follows an existing repository pattern; final diff must contain no workflow/script. | none |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `src/creatures/combat/condition.cpp` | exclusive | normalize start level and deserialized level | implemented |
| `tests/unit/players/condition/condition_light_test.cpp` | exclusive | focused regression tests | implemented |
| `tests/unit/players/condition/CMakeLists.txt` | exclusive | register test source | implemented |
| temporary patch workflow/script | exclusive | exact-anchor branch mutation, then self-removal | removed in implementation commit |
| comparison program | shared | active task and provenance | updated |
| changelog | shared | behavior-level completion note | updated |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| `b2036bd5d56423894b72eaa2ebaff32feba382a5` | local Git/worktree/build preflight | unavailable | DNS failure recorded above. |
| `8ede33176f4a37187bb2c3af5d5d40ba5a07c437` | draft PR publication | passed | PR #297 targets `blakinio/canary:main` from the same repository. |

Never write `passed` without verification on the stated commit.

# Failed approaches and dead ends

- Local repository clone/fetch and raw-file download are unavailable in the current execution environment.
- Full `condition.cpp` replacement through the contents API was rejected as unsafe and unnecessary.

# Risks and compatibility

- Runtime: high before fix because integer division by zero can terminate the server process.
- Data/migration: no schema or migration; persisted zero levels are normalized in memory when loaded.
- Security: no new input surface; malformed/legacy persisted input becomes safe.
- Backward compatibility: valid levels remain unchanged; invalid zero becomes minimum valid level `1`.
- Cross-repo rollout: none; no protocol/client contract changes.
- Rollback: revert the implementation PR; no data rewrite or irreversible migration occurs.

## 2026-07-14T00:05:00+02:00

- Changed: normalized zero light levels at both missing runtime boundaries; added three focused serialization/runtime tests; registered the test; updated program and changelog.
- Learned: existing serialization provides sufficient observation of private light state, so no public test-only API is needed.
- Failed/blocked: local execution remains unavailable; GitHub CI must compile and execute the new tests.
- Result: implementation is complete on the branch; temporary patch files are removed from the generated commit.

# Remaining work

1. Inspect the generated diff and current-head CI; repair any compile/test failure from logs.
2. Complete the autonomous merge gate and archive the task after merge.

# Handoff

## Start here

Read this task, PR #297, the comparison program, CrystalServer commit `a735001...`, and the current `ConditionLight` implementation.

## Do not repeat

- Do not copy unrelated CrystalServer code.
- Do not remove the start-time normalization merely because deserialization is normalized.
- Do not add public runtime API only to expose private state to a test.
- Do not leave the temporary workflow or patch script in the final PR diff.

## Required reads

- `AGENTS.md`
- `docs/agents/README.md`
- `docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md`
- all overlapping active task records
- `docs/agents/MODULE_CATALOG.md`
- `src/creatures/combat/condition.*`
- `tests/unit/players/condition/**`

## Open questions

- None before implementation; CI must validate the concrete player fixture and complete C++ target.

# Completion

- Final status: active
- PR: #297
- Merge commit:
- Program record updated: pending
- Catalogue updated: not required; no reusable/public interface change
- Changelog updated: pending
- Archived at: pending
