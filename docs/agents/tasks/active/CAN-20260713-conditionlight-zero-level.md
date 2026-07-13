---
task_id: CAN-20260713-conditionlight-zero-level
program_id: CAN-PROGRAM-CRYSTALSERVER-COMPARISON
coordination_id: CS-001
status: active
agent: "GPT-5.6 Thinking"
branch: fix/conditionlight-zero-level
base_branch: main
created: 2026-07-13T23:47:32+02:00
updated: 2026-07-14T00:11:00+02:00
last_verified_commit: "6c90768a2afa5b24bdac2852a0846e747c5a80e1"
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
- [x] Module catalogue impact is recorded as none because no reusable interface is added or changed.
- [x] Changelog records the completed runtime safety fix.
- [x] Program queue and handoff are updated.
- [x] Cross-repository impact is recorded as none.
- [ ] Autonomous merge gate is satisfied.

# Confirmed context

- Target repository: `blakinio/canary`; write permission is available only there.
- Base `main` at task creation: `b2036bd5d56423894b72eaa2ebaff32feba382a5`.
- CrystalServer candidate: `zimbadev/crystalserver@a7350014528002fb27ed64d260a96d28a580d41a`, PR #822.
- Current Canary `ConditionLight::startCondition` computed `ticks / lightInfo.level` without a guard.
- Current Canary `ConditionLight::unserializeProp` assigned a serialized level directly, including `0`.
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
- Ownership checker result: GitHub Actions `Agent Task Ownership` run `29288244773`, job `Validate active ownership`, passed on `6c90768a2afa5b24bdac2852a0846e747c5a80e1`.
- Exclusive claims: runtime file, focused test, condition-test CMake entry, task record, and temporary self-removing patch files.
- Shared claims: comparison program and changelog, narrow edits only.
- Read-only dependencies: headers, stream implementation, governance/build docs.
- Overlaps: none reported by ownership CI.
- Resolution: proceed to full ready-state runtime CI.

# Current state

Implementation and focused regression source are complete in draft PR #297. The final diff contains exactly six expected paths and no temporary runner files. Ownership CI passes. Draft-state CI run `29288245051` completed successfully but intentionally skipped `Build - Linux`, so it is not evidence that the new C++ test compiled or ran.

# Plan

1. Mark PR #297 Ready to trigger the full runtime build/test matrix.
2. Inspect Linux configure/build/unit-test jobs and the Required aggregate on the resulting current head.
3. Repair any failure from exact job logs; return to draft if code changes are needed.
4. Review final diff, reviews and unresolved threads, then merge only when the autonomous gate is complete.
5. Archive this task and update the program in a separate cleanup PR.

# Work log

## 2026-07-13T23:47:32+02:00

- Changed: created branch and claimed exact paths.
- Learned: current main still contained both missing zero-level guards; existing update/setter paths were already safe.
- Failed/blocked: local Git and build unavailable because DNS cannot resolve `github.com`.
- Result: implementation could proceed through GitHub branch and CI evidence.

## 2026-07-14T00:02:00+02:00

- Changed: opened draft PR #297 and moved focused test ownership to the existing `tests/unit/players/condition/` suite.
- Learned: the repository already uses a bounded branch-only patch workflow with write-scoped token, exact script execution and `git diff --check` for environments without a usable local checkout.
- Failed/blocked: direct raw-file download was also blocked by local DNS; replacing the full 2,946-line source through the contents API would be unsafe.
- Result: claimed temporary workflow/script paths; both were required to delete themselves in the generated implementation commit.

## 2026-07-14T00:05:00+02:00

- Changed: normalized zero light levels at both missing runtime boundaries; added three focused serialization/runtime tests; registered the test; updated program and changelog.
- Learned: existing serialization provides sufficient observation of private light state, so no public test-only API is needed.
- Failed/blocked: local execution remains unavailable; GitHub CI must compile and execute the new tests.
- Result: implementation complete on the branch; temporary patch files removed from the generated commit.

## 2026-07-14T00:11:00+02:00

- Changed: reviewed the six-file PR diff and added an explicit `<optional>` include to avoid a PCH-only dependency.
- Learned: draft-state CI path scoping reports success while skipping Linux runtime build jobs; that aggregate is insufficient for this C++ task.
- Failed/blocked: none in ownership validation; full C++ validation still pending.
- Result: ownership passed on head `6c90768...`; PR must enter Ready state for complete runtime CI.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Adapt only the two missing boundaries | Matches current Canary architecture and avoids broad Condition refactoring. | none |
| Normalize the runtime level before division, not only the divisor | Constructor/direct creation can supply level `0`; keeping object state at the established minimum matches `setParam` and makes the invariant observable. | none |
| Keep deserialization normalization | Prevents persisted malformed/legacy data from retaining invalid state. | none |
| Add no public getter solely for testing | Existing serialization and creature-light state expose the invariant without expanding runtime API. | none |
| Use a self-removing exact-anchor patch runner | It avoids unsafe full-file replacement and follows an existing repository pattern; final diff contains no workflow/script. | none |
| Do not treat draft Required success as C++ validation | The run explicitly skipped `Build - Linux`; only ready-state runtime jobs can satisfy the gate. | none |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `src/creatures/combat/condition.cpp` | exclusive | normalize start level and deserialized level | implemented and reviewed |
| `tests/unit/players/condition/condition_light_test.cpp` | exclusive | focused regression tests | implemented and reviewed |
| `tests/unit/players/condition/CMakeLists.txt` | exclusive | register test source | implemented and reviewed |
| temporary patch workflow/script | exclusive | exact-anchor branch mutation, then self-removal | absent from final diff |
| comparison program | shared | active task and provenance | updated |
| changelog | shared | behavior-level completion note | updated |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| `b2036bd5d56423894b72eaa2ebaff32feba382a5` | local Git/worktree/build preflight | unavailable | DNS failure recorded above. |
| `8ede33176f4a37187bb2c3af5d5d40ba5a07c437` | draft PR publication | passed | PR #297 targets `blakinio/canary:main` from the same repository. |
| `b2c5859943560c6b8bec6e1cb03ce3568b86f73a` | bounded exact-anchor patch runner | passed | Generated six-file implementation diff; workflow and script removed themselves. |
| `6c90768a2afa5b24bdac2852a0846e747c5a80e1` | Agent Task Ownership run `29288244773` | passed | Focused tooling tests and ownership validation succeeded; no overlap reported. |
| `6c90768a2afa5b24bdac2852a0846e747c5a80e1` | draft CI run `29288245051` | incomplete | Workflow/Required succeeded, but Linux/macOS/Windows builds and Lua tests were skipped; not accepted as C++ validation. |

Never write `passed` without verification on the stated commit.

# Failed approaches and dead ends

- Local repository clone/fetch and raw-file download are unavailable in the current execution environment.
- Full `condition.cpp` replacement through the contents API was rejected as unsafe and unnecessary.
- Draft-state Required success alone was rejected because the runtime build job was skipped.

# Risks and compatibility

- Runtime: high before fix because integer division by zero can terminate the server process.
- Data/migration: no schema or migration; persisted zero levels are normalized in memory when loaded.
- Security: no new input surface; malformed/legacy persisted input becomes safe.
- Backward compatibility: valid levels remain unchanged; invalid zero becomes minimum valid level `1`.
- Cross-repo rollout: none; no protocol/client contract changes.
- Rollback: revert the implementation PR; no data rewrite or irreversible migration occurs.

# Remaining work

1. Mark PR #297 Ready and verify full Linux runtime build/unit tests plus Required on the resulting current head.
2. Review reviews/threads and merge only if every autonomous gate passes.
3. Archive the task and remove it from the active program list in a separate cleanup PR.

# Handoff

## Start here

Read this task, PR #297, the comparison program, CrystalServer commit `a735001...`, and the current `ConditionLight` implementation.

## Do not repeat

- Do not copy unrelated CrystalServer code.
- Do not remove the start-time normalization merely because deserialization is normalized.
- Do not add public runtime API only to expose private state to a test.
- Do not leave the temporary workflow or patch script in the final PR diff.
- Do not accept a Required aggregate when the Linux build job is skipped.

## Required reads

- `AGENTS.md`
- `docs/agents/README.md`
- `docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md`
- all overlapping active task records
- `docs/agents/MODULE_CATALOG.md`
- `src/creatures/combat/condition.*`
- `tests/unit/players/condition/**`

## Open questions

- None; full ready-state runtime CI is the remaining evidence gate.

# Completion

- Final status: active
- PR: #297
- Merge commit:
- Program record updated: yes, active task/queue state
- Catalogue updated: not required; no reusable/public interface change
- Changelog updated: yes
- Archived at: pending
