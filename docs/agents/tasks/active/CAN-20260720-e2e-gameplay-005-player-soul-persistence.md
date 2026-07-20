---
task_id: CAN-20260720-e2e-gameplay-005-player-soul-persistence
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-GAMEPLAY-005-SOUL
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/e2e-player-soul-persistence-contract
base_branch: main
created: 2026-07-20T10:17:00+02:00
updated: 2026-07-20T10:17:00+02:00
last_verified_commit: "0a39a0f76d5f811098dfaa7be9deea40347279d5"
risk: medium
related_issue: ""
related_pr: ""
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

- [ ] Support exactly one typed `player_soul` persistence assertion with integer `equals` in `0..255`.
- [ ] Reject booleans, negative values, values above `255`, unknown fields and arbitrary SQL surfaces.
- [ ] Re-verify after relog through maintained `LocalPlayer.getSoul()`.
- [ ] Compile final scalar SQL only against fixed Canary `players.soul`.
- [ ] Preserve all existing persistence assertion behavior and mixed-type compilation.
- [ ] Add focused regression coverage and a durable public contract document.
- [ ] Modify the controlled-client Lua driver only by extending the existing persistence-check dispatch; do not add a second runner or lifecycle.
- [ ] Do not modify workflows, route execution, OTBM tooling, map/client assets or reference repositories.
- [ ] Update the module catalogue narrowly.
- [ ] Apply `ci:final-gate` before the final checkpoint commit and make no post-green final-head commit.
- [ ] Require exact-final-head Ownership, CI, Universal Agent E2E and autofix as applicable plus a clean review blocker audit before squash merge.

# Confirmed context

- Current `main` is exactly `0a39a0f76d5f811098dfaa7be9deea40347279d5` at task start.
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
- Ownership checker result: not run locally because no local checkout is available; GitHub ownership CI is required before merge.
- Exclusive claims: task record, soul persistence doc, focused soul tests.
- Shared claims: persistence compiler, existing controlled-client persistence dispatch, module catalogue row.
- Read-only dependencies: runner, workflows, scenario registry/data, schema.
- Overlaps: none identified.
- Resolution: proceed with the narrow typed contract; stop if live ownership CI or PR state reveals a conflict.

# Current state

Task claimed on a fresh branch from current `main`; implementation not yet started.

# Plan

1. Open a draft PR early, then implement the smallest typed `player_soul` compiler/runtime/SQL extension with focused tests and docs.

# Work log

## 2026-07-20T10:17:00+02:00

- Changed: created the active task record on `feat/e2e-player-soul-persistence-contract`.
- Learned: `players.soul` and maintained `LocalPlayer.getSoul()` form a direct bounded client-plus-SQL persistence surface.
- Failed/blocked: original historical branch name still exists from closed PR #606, so a fresh branch name was used instead of reusing it.
- Result: task ownership is now explicit before implementation.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Add a dedicated typed `player_soul` assertion rather than expose raw `player_field` soul. | Keeps the caller surface bounded to `0..255` and fixed SQL/runtime getters, matching the typed persistence pattern. | none |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `tools/e2e/persistence_assertions.py` | shared | validate/compile typed `player_soul` | planned |
| `tools/e2e/client/agent_e2e_scenario.lua` | shared | read `LocalPlayer.getSoul()` after relog | planned |
| `tests/e2e/test_player_soul_persistence.py` | exclusive | focused regression coverage | planned |
| `docs/e2e/PLAYER_SOUL_PERSISTENCE.md` | exclusive | durable contract | planned |
| `docs/agents/MODULE_CATALOG.md` | shared | reusable surface catalogue | planned |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| `0a39a0f76d5f811098dfaa7be9deea40347279d5` | current `main` comparison | passed | exact compare against `main` returned identical before branch creation |

# Failed approaches and dead ends

- Reusing `feat/e2e-player-soul-persistence`: rejected because the ref still exists from closed, unmerged PR #606.

# Risks and compatibility

- Runtime: only one bounded getter dispatch is added to the existing controlled-client persistence path.
- Data/migration: none; existing `players.soul` column only.
- Security: no arbitrary SQL/table/column or caller-provided commands.
- Backward compatibility: existing assertion types must remain unchanged.
- Cross-repo rollout: none; maintained OTClient getter already exists and remains read-only.
- Rollback: revert the narrow compiler/runtime/test/doc PR.

# Remaining work

1. Open the draft PR and implement the bounded typed contract.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-20T10:17:00+02:00
head: UNKNOWN
branch: feat/e2e-player-soul-persistence-contract
pr: none
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
  - current main at task start is 0a39a0f76d5f811098dfaa7be9deea40347279d5
  - Canary schema.sql persists player soul in players.soul
  - maintained blakinio/otclient LocalPlayer.getSoul returns uint8_t
  - no open PR matched the soul persistence contract in the narrow overlap search
  - PR 600 remains separately owned route work and is not modified
derived:
  - a dedicated player_soul type can enforce the exact 0..255 maintained-client domain while compiling only fixed players.soul SQL
  - extending the existing phase-two persistence dispatch is smaller and safer than exposing soul through caller-selectable raw player_field
unknown:
  - GitHub ownership CI result for the new task branch
  - exact implementation commit SHA
conflicts: []
first_failure:
  marker: historical branch name already existed
  evidence: GitHub create-branch returned Reference already exists for feat/e2e-player-soul-persistence; a fresh branch was created from current main instead
rejected_hypotheses:
  - reuse the historical closed-PR branch: existing ref would blur task ownership and branch history
  - expose raw player_field soul: typed uint8 boundary is narrower and evidence-backed
changed_paths:
  - docs/agents/tasks/active/CAN-20260720-e2e-gameplay-005-player-soul-persistence.md
validation:
  - command: compare 0a39a0f76d5f811098dfaa7be9deea40347279d5 to main
    result: PASS
    evidence: GitHub compare returned identical immediately before branch creation
  - command: narrow open PR search for soul
    result: PASS
    evidence: no open PR result matched the contract
blockers: []
next_action: Open a draft PR from feat/e2e-player-soul-persistence-contract to main, then implement the bounded typed player_soul persistence contract.
```
