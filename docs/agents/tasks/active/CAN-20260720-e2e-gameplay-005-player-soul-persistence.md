---
task_id: CAN-20260720-e2e-gameplay-005-player-soul-persistence
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-GAMEPLAY-005-SOUL
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/e2e-player-soul-persistence-contract
base_branch: main
created: 2026-07-20T10:17:00+02:00
updated: 2026-07-20T10:42:00+02:00
last_verified_commit: "0a39a0f76d5f811098dfaa7be9deea40347279d5"
risk: medium
related_issue: ""
related_pr: "615"
depends_on:
  - merged E2E-GAMEPLAY-005 typed persistence foundation
  - merged PR #608 player_vocation persistence
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260720-e2e-gameplay-005-player-soul-persistence.md
    - docs/e2e/PLAYER_SOUL_PERSISTENCE.md
    - tests/e2e/test_player_soul_persistence.py
  shared:
    - tools/e2e/persistence_assertions.py
    - tools/e2e/client/agent_e2e_scenario.lua
    - docs/agents/MODULE_CATALOG.md
  read_only:
    - tools/e2e/run_agent_e2e.py
    - tests/e2e/scenarios/**
    - .github/workflows/**
    - schema.sql
modules_touched:
  - Universal OTS E2E physical gameplay action plans
reuses:
  - Universal Agent E2E two-session lifecycle
  - typed persistence assertion compiler
  - maintained OTClient LocalPlayer.getSoul API
public_interfaces:
  - typed player_soul persistence assertion
cross_repo_tasks: []
---

# Goal

Add one bounded reusable `player_soul` persistence assertion that accepts an exact unsigned 8-bit soul value, re-verifies it after relog through maintained `LocalPlayer.getSoul()`, and verifies final durable state through fixed scalar SQL against Canary `players.soul`.

# Acceptance criteria

- [x] Support exactly one typed `player_soul` persistence assertion with integer `equals` in `0..255`.
- [x] Reject booleans, negative values, values above `255`, unknown fields and arbitrary SQL surfaces.
- [x] Re-verify after relog through maintained `LocalPlayer.getSoul()`.
- [x] Compile final scalar SQL only against fixed Canary `players.soul`.
- [x] Preserve all existing persistence assertion behavior and mixed-type compilation.
- [x] Add focused regression coverage and a durable public contract document.
- [x] Modify the controlled-client Lua driver only by extending the existing persistence-check dispatch; do not add a second runner or lifecycle.
- [x] Do not modify workflows, route execution, OTBM tooling, map/client assets or reference repositories.
- [x] Update the module catalogue narrowly.
- [x] Apply `ci:final-gate` before the final checkpoint commit and make no post-green final-head commit.
- [ ] Require exact-final-head Ownership, CI, Universal Agent E2E and autofix as applicable plus a clean review blocker audit before squash merge.

# Confirmed context

- Current `main` was exactly `0a39a0f76d5f811098dfaa7be9deea40347279d5` at task start and remained the latest main during pre-final validation.
- Canary `schema.sql` defines `players.soul` as unsigned integer persistence state.
- Maintained `blakinio/otclient` exposes `LocalPlayer.getSoul()` returning `uint8_t`.
- Existing Universal E2E already compiles typed persistence checks into one phase-two controlled-client plan and fixed scalar SQL.
- Open PR #600 owns separate OTBM route work and is read-only/out of scope for this task.
- No open PR matched a `soul` persistence contract during the narrow overlap search.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| Universal OTS E2E physical gameplay action plans | two-session login/logout/relog lifecycle and persistence plan | `tools/e2e/run_agent_e2e.py`, `tools/e2e/client/agent_e2e_scenario.lua` | Already proves physical relog persistence without a second orchestrator. |
| Typed persistence assertion compiler | bounded validation and fixed SQL compilation | `tools/e2e/persistence_assertions.py` | Existing extension point for one new fixed typed contract. |
| Maintained OTClient | `LocalPlayer.getSoul()` | `blakinio/otclient:src/client/localplayer.h` | Direct maintained client getter with a bounded `uint8_t` domain. |

# Ownership and overlap check

- Program record: `docs/agents/programs/E2E_AUTOMATION_PROGRAM.md`.
- Open PRs inspected: narrow `soul` search returned no open match; PR #600 remains separate route ownership.
- Active tasks inspected: prior merged vocation task record plus current `ACTIVE_WORK.md` convenience index; no soul contract owner identified.
- Agent Task Ownership succeeded on repaired pre-final head `7386751046272221e0fe8562c2c273303628c2a2` in run `29728444212`.
- Exclusive claims: task record, soul persistence doc, focused soul tests.
- Shared claims: persistence compiler, existing controlled-client persistence dispatch, module catalogue row.
- Read-only dependencies: runner, workflows, scenario registry/data, schema.
- Overlaps: none identified.
- Resolution: proceed to exact-final-head gates; stop if final ownership or blocker audit reveals a conflict.

# Current state

Implementation is complete on draft PR #615. The functional diff contains exactly one typed compiler/SQL extension, two small controlled-client dispatch additions, focused tests, one contract document, this task record and one narrowly updated catalogue row. The `ci:final-gate` label was applied before this checkpoint commit. This commit is the final checkpoint commit; no further repository commit is permitted after its exact head becomes green.

# Plan

1. Treat the SHA produced by this checkpoint commit as frozen final PR head.
2. Require exact-head Agent Task Ownership, CI, Universal Agent E2E and autofix outcome as applicable.
3. Audit changed files/diff, reviews, comments, review threads, mergeability and main drift against the frozen head.
4. Squash merge PR #615 only with `expected_head_sha` equal to the frozen final head.

# Work log

## 2026-07-20T10:17:00+02:00

- Changed: created the active task record on `feat/e2e-player-soul-persistence-contract`.
- Learned: `players.soul` and maintained `LocalPlayer.getSoul()` form a direct bounded client-plus-SQL persistence surface.
- Failed/blocked: original historical branch name still exists from closed PR #606, so a fresh branch name was used instead of reusing it.
- Result: task ownership was explicit before implementation.

## 2026-07-20T10:36:00+02:00

- Changed: implemented typed `player_soul` validation/client emission/fixed SQL, added maintained-client `getSoul()` runtime verification, focused tests, durable docs and the narrow module-catalogue update.
- Learned: the Lua driver needs only two bounded dispatch additions; no runner/workflow/client-repository mutation is required.
- Failed/blocked: the first PR Ownership run rejected the initial task metadata because the draft PR had been opened after the task record and `related_pr`/checkpoint PR were still unset.
- Result: governance metadata was repaired; pre-final Ownership and CI subsequently succeeded.

## 2026-07-20T10:42:00+02:00

- Changed: applied `ci:final-gate` before this final checkpoint commit.
- Learned: pre-final E2E successfully completed scope selection, scenario resolution/validation and database bootstrap before its heavy builds queued; the exact final head will receive the authoritative full final-gate run.
- Failed/blocked: none remaining before exact-final-head validation.
- Result: the next SHA produced by this commit is frozen for final validation and merge gating.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Add a dedicated typed `player_soul` assertion rather than expose raw `player_field` soul. | Keeps the caller surface bounded to `0..255` and fixed SQL/runtime getters, matching the typed persistence pattern. | none |
| Use maintained `LocalPlayer.getSoul()` after relog. | The maintained API already exposes the exact `uint8_t` client-visible value; no client fork or generic getter is needed. | none |
| Use the exact-final-head E2E after the final checkpoint as authoritative. | `ci:final-gate` explicitly requires fresh full validation of the frozen final head; pre-final incremental/heavy work cannot substitute for it. | none |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `tools/e2e/persistence_assertions.py` | shared | validate/compile typed `player_soul` | implemented |
| `tools/e2e/client/agent_e2e_scenario.lua` | shared | read `LocalPlayer.getSoul()` after relog | implemented |
| `tests/e2e/test_player_soul_persistence.py` | exclusive | focused regression coverage | implemented |
| `docs/e2e/PLAYER_SOUL_PERSISTENCE.md` | exclusive | durable contract | implemented |
| `docs/agents/MODULE_CATALOG.md` | shared | reusable surface catalogue | implemented, audited to one-row diff |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| `0a39a0f76d5f811098dfaa7be9deea40347279d5` | current `main` comparison at task start | passed | exact compare against `main` returned identical before branch creation |
| `63e75d7aeb53531c340426602db81999702d13ad` | PR #615 changed-file/diff audit | passed | exactly six intended paths; compiler and Lua patches bounded; catalogue reduced to one intended row after correction |
| `63e75d7aeb53531c340426602db81999702d13ad` | CI run `29728300555` | passed | completed success |
| `63e75d7aeb53531c340426602db81999702d13ad` | first Agent Task Ownership run `29728300398` | failed | initial changed task lacked current PR metadata because it was committed before draft PR creation |
| `7386751046272221e0fe8562c2c273303628c2a2` | Agent Task Ownership run `29728444212` | passed | repaired active-task PR/checkpoint metadata accepted |
| `7386751046272221e0fe8562c2c273303628c2a2` | CI run `29728444405` | passed | completed success |
| `7386751046272221e0fe8562c2c273303628c2a2` | Universal Agent E2E run `29728444402` pre-final progress | superseded by final-gate head | scope, scenario resolution/validation and database bootstrap completed successfully before heavy builds queued; final checkpoint commit intentionally creates the authoritative exact final head |
| final checkpoint head | exact-final-head Ownership, CI, Universal Agent E2E and autofix | not run yet | workflow outcomes necessarily occur after this commit and are audited externally before merge |

# Failed approaches and dead ends

- Reusing `feat/e2e-player-soul-persistence`: rejected because the ref still exists from closed, unmerged PR #606.
- The first full-file `MODULE_CATALOG.md` replacement accidentally changed one unrelated Wheel of Destiny documentation path; patch audit detected it immediately and a follow-up commit restored the original entry. The resulting PR catalogue diff is limited to the intended Universal E2E row.
- The initial task record predated PR #615 and therefore failed changed-task lifecycle validation until `related_pr`, checkpoint PR and a concrete checkpoint head were recorded.

# Risks and compatibility

- Runtime: only one bounded getter dispatch is added to the existing controlled-client persistence path.
- Data/migration: none; existing `players.soul` column only.
- Security: no arbitrary SQL/table/column or caller-provided commands.
- Backward compatibility: existing assertion types remain unchanged and mixed-type behavior is regression-covered.
- Cross-repo rollout: none; maintained OTClient getter already exists and remains read-only.
- Rollback: revert the narrow compiler/runtime/test/doc PR.

# Remaining work

1. Inspect exact-final-head workflow outcomes without committing further changes.
2. Perform the clean review/comment/thread/main-drift blocker audit against the frozen head.
3. Mark PR ready only when appropriate and require any resulting exact-head workflows to finish without moving the head.
4. Squash merge with the frozen `expected_head_sha` only after all gates are green.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-20T10:42:00+02:00
head: 7386751046272221e0fe8562c2c273303628c2a2
branch: feat/e2e-player-soul-persistence-contract
pr: 615
status: implementing
context_routes:
  - agent-governance
  - universal-e2e
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260720-e2e-gameplay-005-player-soul-persistence.md
  - docs/e2e/PLAYER_SOUL_PERSISTENCE.md
  - tests/e2e/test_player_soul_persistence.py
  - tools/e2e/persistence_assertions.py
  - tools/e2e/client/agent_e2e_scenario.lua
  - docs/agents/MODULE_CATALOG.md
proven:
  - current main at task start and during pre-final validation was 0a39a0f76d5f811098dfaa7be9deea40347279d5
  - Canary schema.sql persists player soul in players.soul
  - maintained blakinio/otclient LocalPlayer.getSoul returns uint8_t
  - no open PR matched the soul persistence contract in the narrow overlap search
  - PR 600 remains separately owned route work and is not modified
  - implementation accepts only exact integer player_soul equals values in 0..255
  - implementation emits player_soul to the existing phase-two client plan and reads maintained LocalPlayer.getSoul after relog
  - final SQL surface is fixed to players.soul with the existing escaped fixture-character boundary
  - PR patch audit shows exactly six intended paths
  - controlled-client Lua patch contains only the two intended soul dispatch additions
  - final MODULE_CATALOG patch changes only the Universal OTS E2E physical gameplay action plans row
  - pre-final Agent Task Ownership run 29728444212 succeeded on 7386751046272221e0fe8562c2c273303628c2a2
  - pre-final CI run 29728444405 succeeded on 7386751046272221e0fe8562c2c273303628c2a2
  - ci:final-gate was applied before this final checkpoint commit
  - pre-final E2E scope, scenario resolution and database bootstrap jobs succeeded before the final checkpoint superseded that head
 derived:
  - a dedicated player_soul type enforces the exact 0..255 maintained-client domain while compiling only fixed players.soul SQL
  - extending the existing phase-two persistence dispatch is smaller and safer than exposing soul through caller-selectable raw player_field
  - no maintained-client repository mutation is needed because LocalPlayer.getSoul already exposes the required exact value
  - the SHA produced by this commit is the only acceptable merge head after exact-final-head gates complete
unknown:
  - the SHA produced by this final checkpoint commit
  - exact-final-head Ownership, CI, Universal Agent E2E and autofix outcomes
  - review/comment/thread blocker state against the frozen head
conflicts: []
first_failure:
  marker: historical branch name already existed
  evidence: GitHub create-branch returned Reference already exists for feat/e2e-player-soul-persistence; a fresh branch was created from current main instead
rejected_hypotheses:
  - reuse the historical closed-PR branch: existing ref would blur task ownership and branch history
  - expose raw player_field soul: typed uint8 boundary is narrower and evidence-backed
  - add a second E2E runner or lifecycle: existing phase-two persistence dispatch already provides the required client verification seam
changed_paths:
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260720-e2e-gameplay-005-player-soul-persistence.md
  - docs/e2e/PLAYER_SOUL_PERSISTENCE.md
  - tests/e2e/test_player_soul_persistence.py
  - tools/e2e/client/agent_e2e_scenario.lua
  - tools/e2e/persistence_assertions.py
validation:
  - command: compare 0a39a0f76d5f811098dfaa7be9deea40347279d5 to main at task start and pre-final validation
    result: PASS
    evidence: main remained on the same OAM-022 durable completion head with no overlapping drift
  - command: PR 615 compiler and Lua patch audit
    result: PASS
    evidence: fixed bounded compiler/SQL changes and exactly two controlled-client dispatch additions
  - command: PR 615 MODULE_CATALOG patch audit
    result: PASS
    evidence: only the Universal OTS E2E physical gameplay action plans row differs from base after correction
  - command: Agent Task Ownership run 29728444212 on 7386751046272221e0fe8562c2c273303628c2a2
    result: PASS
    evidence: repaired active-task metadata accepted
  - command: CI run 29728444405 on 7386751046272221e0fe8562c2c273303628c2a2
    result: PASS
    evidence: workflow completed success
  - command: Universal Agent E2E run 29728444402 on 7386751046272221e0fe8562c2c273303628c2a2
    result: SUPERSEDED
    evidence: scope, scenario resolution/validation and database bootstrap succeeded; final checkpoint commit creates the authoritative exact final head for full final-gate validation
  - command: exact-final-head Ownership, CI, Universal Agent E2E and autofix
    result: NOT_RUN
    evidence: this commit creates the new frozen final head; exact-head workflow outcomes necessarily occur after the commit
blockers: []
next_action: Inspect exact-final-head gates for the frozen SHA produced by this commit, then perform the clean review blocker audit and squash merge with expected_head_sha if all required evidence is green.
```
