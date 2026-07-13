---
task_id: CAN-20260713-conditionlight-zero-level
program_id: CAN-PROGRAM-CRYSTALSERVER-COMPARISON
coordination_id: CS-001
status: active
agent: "GPT-5.6 Thinking"
branch: fix/conditionlight-zero-level
base_branch: main
created: 2026-07-13T23:47:32+02:00
updated: 2026-07-13T23:47:32+02:00
last_verified_commit: "b2036bd5d56423894b72eaa2ebaff32feba382a5"
risk: high
related_issue: ""
related_pr: ""
depends_on:
  - "CAN-PROGRAM-CRYSTALSERVER-COMPARISON Stage 1 / PR #291"
blocks: []
owned_paths:
  exclusive:
    - src/creatures/combat/condition.cpp
    - tests/unit/game/condition_light_test.cpp
    - tests/unit/game/CMakeLists.txt
    - docs/agents/tasks/active/CAN-20260713-conditionlight-zero-level.md
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
  - existing GoogleTest canary_ut target
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Prevent `ConditionLight` from dividing by zero or retaining an invalid zero light level when a condition is constructed or deserialized with level `0`, without changing valid light behavior.

# Acceptance criteria

- [ ] A focused regression test proves zero-level deserialization is normalized to `1`.
- [ ] A focused regression test proves starting a zero-level light condition does not divide by zero and produces a valid interval.
- [ ] Valid nonzero light levels preserve their existing interval and serialization behavior.
- [ ] The implementation is limited to the missing `ConditionLight` input boundaries.
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
- No open PR found by `ConditionLight` or `condition.cpp` search at task creation.
- Local Git/worktree/build inspection is unavailable: `git ls-remote https://github.com/blakinio/canary.git refs/heads/main` failed with `Could not resolve host: github.com`.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| Condition serialization | `PropWriteStream` / `PropStream` round trip | `src/creatures/combat/condition.*` | Exercises the persisted invalid input boundary without inventing a parser. |
| Existing `canary_ut` target | GoogleTest registration | `tests/unit/CMakeLists.txt`, `tests/unit/game/CMakeLists.txt` | Focused test belongs in the existing unit target. |
| CrystalServer comparison program | Candidate provenance and risk classification | `docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md` | Keeps the adaptation evidence-backed and bounded. |

# Ownership and overlap check

- Program record: `CAN-PROGRAM-CRYSTALSERVER-COMPARISON`.
- Open PRs inspected: all open PRs returned on 2026-07-13; direct searches for `ConditionLight` and `condition.cpp` returned no overlaps.
- Active tasks inspected: live PR/task metadata plus `ACTIVE_WORK.md`; no declared overlap found for the owned runtime/test paths.
- Ownership checker result: not run locally because no checkout is available; GitHub ownership CI is required before readiness.
- Exclusive claims: runtime file, focused test, game test CMake entry, this task record.
- Shared claims: comparison program and changelog, narrow edits only.
- Read-only dependencies: headers, stream implementation, governance/build docs.
- Overlaps: none known.
- Resolution: proceed with one candidate, one branch and one PR; stop if ownership CI reports a conflict.

# Current state

The defect is reproducible by source proof: level `0` reaches an integer divisor in `startCondition`, and the persisted level boundary accepts `0` unchanged. The smallest complete adaptation is to clamp the divisor defensively and normalize deserialized levels.

# Plan

1. Publish this task and a draft PR.
2. Inspect the exact test fixture and stream APIs used by current `canary_ut`.
3. Add focused failing regression coverage for construction/start and deserialization.
4. Apply the smallest two-boundary runtime fix.
5. Run/observe focused and required CI, repair failures from logs, and review the full diff.
6. Mark ready, enable auto-merge or squash-merge after the autonomous gate.
7. Archive this task and update the program in a separate cleanup PR.

# Work log

## 2026-07-13T23:47:32+02:00

- Changed: created branch and claimed exact paths.
- Learned: current main still contains both missing zero-level guards; existing update/setter paths are already safe.
- Failed/blocked: local Git and build unavailable because DNS cannot resolve `github.com`.
- Result: implementation may proceed through GitHub branch and CI evidence.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Adapt only the two missing boundaries | Matches current Canary architecture and avoids broad Condition refactoring. | none |
| Keep the runtime divisor guard even with deserialization normalization | Constructor/direct creation can still supply level `0`; defense in depth closes both independent paths. | none |
| Add no public getter solely for testing | Avoids expanding runtime API for a private invariant. Tests should use existing serialization/runtime observable behavior. | none |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `src/creatures/combat/condition.cpp` | exclusive | clamp start divisor and deserialized level | planned |
| `tests/unit/game/condition_light_test.cpp` | exclusive | focused regression tests | planned |
| `tests/unit/game/CMakeLists.txt` | exclusive | register test source | planned |
| comparison program | shared | active task/provenance then completion | planned |
| changelog | shared | behavior-level completion note | planned |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| `b2036bd5d56423894b72eaa2ebaff32feba382a5` | local Git/worktree/build preflight | unavailable | DNS failure recorded above. |

Never write `passed` without verification on the stated commit.

# Failed approaches and dead ends

- Local repository clone/fetch is unavailable in the current execution environment.

# Risks and compatibility

- Runtime: high before fix because integer division by zero can terminate the server process.
- Data/migration: no schema or migration; persisted zero levels are normalized in memory when loaded.
- Security: no new input surface; malformed/legacy persisted input becomes safe.
- Backward compatibility: valid levels remain unchanged; invalid zero becomes minimum valid level `1`.
- Cross-repo rollout: none; no protocol/client contract changes.
- Rollback: revert the implementation PR; no data rewrite or irreversible migration occurs.

# Remaining work

1. Open the draft PR and add focused tests plus the minimal fix.

# Handoff

## Start here

Read this task, the comparison program, CrystalServer commit `a735001...`, and the current `ConditionLight` implementation.

## Do not repeat

- Do not copy unrelated CrystalServer code.
- Do not remove the start-time guard merely because deserialization is normalized.
- Do not add public runtime API only to expose private state to a test.

## Required reads

- `AGENTS.md`
- `docs/agents/README.md`
- `docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md`
- all overlapping active task records
- `docs/agents/MODULE_CATALOG.md`
- `src/creatures/combat/condition.*`
- `tests/unit/**` harness and CMake registration

## Open questions

- Which existing fixture can instantiate a minimal concrete creature without unrelated world setup?

# Completion

- Final status: active
- PR:
- Merge commit:
- Program record updated: pending
- Catalogue updated: not required unless implementation changes a reusable/public interface
- Changelog updated: pending
- Archived at: pending
