---
task_id: CAN-20260713-crystalserver-comparison-inventory
program_id: CAN-PROGRAM-CRYSTALSERVER-COMPARISON
coordination_id: ""
status: active
agent: GPT-5.6 Thinking
branch: docs/crystalserver-comparison-inventory
base_branch: main
created: 2026-07-13T21:01:05Z
updated: 2026-07-13T21:01:05Z
last_verified_commit: "360d79ebad5802edd4d89e99d0f210ab19b36b60"
risk: low
related_issue: ""
related_pr: ""
depends_on: []
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260713-crystalserver-comparison-inventory.md
    - docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md
    - artifacts/upstream/crystalserver/CRYSTALSERVER_COMPARISON_STAGE1.md
    - artifacts/upstream/crystalserver/crystalserver_comparison_stage1.json
  shared: []
  read_only:
    - AGENTS.md
    - docs/agents/README.md
    - docs/agents/ACTIVE_WORK.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/REPOSITORY_MAP.md
    - docs/agents/KNOWN_RISKS.md
    - docs/agents/BUILD_TEST_MATRIX.md
    - docs/agents/CROSS_REPO_CONTRACTS.md
    - src/**
    - data/**
    - data-otservbr-global/**
    - tests/**
modules_touched: []
reuses:
  - agent task/program governance
  - current source and test contracts
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Create the evidence-backed Stage 1 inventory for the CrystalServer comparison program without changing runtime behavior, datapacks, protocol, database, maps, assets, or production configuration.

# Acceptance criteria

- [x] Exact `main` baseline SHAs and declared server/client versions are recorded for `blakinio/canary`, `zimbadev/crystalserver`, and the read-only `opentibiabr/canary` reference.
- [x] Open PRs and their changed paths are inspected for overlap.
- [x] A durable program record is created.
- [x] A Markdown report and machine-readable JSON report are created under `artifacts/upstream/crystalserver/`.
- [x] At least ten bounded candidates have opened CrystalServer diffs, current Canary source evidence, one classification, risk, dependencies, and proposed validation.
- [x] No functional source, datapack, schema, protocol, map, asset, secret, or production configuration file is changed.
- [ ] Markdown/path review and `git diff --check` are completed in a local checkout or equivalent CI environment.
- [ ] Current-head GitHub checks are verified.
- [x] Module catalogue impact handled: none; this task adds no reusable runtime/tool interface.
- [x] Documentation/changelog impact handled: program/report only; no behavior-level changelog entry.
- [x] Cross-repository impact handled: both comparison repositories remain read-only.
- [ ] Autonomous merge gate satisfied.

# Confirmed context

- Writable repository: `blakinio/canary` only.
- Canary baseline: `360d79ebad5802edd4d89e99d0f210ab19b36b60`.
- CrystalServer baseline and last analyzed commit: `fc0d53b9f9965463b6082c07e6d3d482294541a7`.
- OpenTibiaBR Canary reference baseline: `9365c1c4aa63529b9ff757f53737274894c02b8e`.
- Both compared servers declare client protocol `1525` (15.25).
- Canary declares server release `3.6.1`; CrystalServer declares software version `4.1.9`.
- The GitHub connection grants write access to `blakinio/canary` and read-only access to both comparison repositories.
- A local checkout/worktree is unavailable in this environment. `git ls-remote https://github.com/blakinio/canary.git refs/heads/main` failed with `Could not resolve host: github.com`; repository inspection and writes use the GitHub connector.
- Therefore local `git status --short --branch`, `git branch -vv`, `git remote -v`, `git worktree list`, `python tools/agents/task_ownership.py`, and `git diff --check` cannot be claimed as run.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| Agent governance | Task/program lifecycle and ownership | `AGENTS.md`, `docs/agents/README.md`, templates | Prevents cross-task writes and preserves handoff. |
| Build/test matrix | Candidate-specific validation requirements | `docs/agents/BUILD_TEST_MATRIX.md` | Separates docs, C++, Lua, DB, and protocol evidence. |
| Cross-repo contract registry | Protocol/client escalation gate | `docs/agents/CROSS_REPO_CONTRACTS.md` | Required for Market/disconnect candidates. |
| Current source/tests | Semantic comparison target | `src/**`, `data/**`, `tests/**` | Text similarity alone is not evidence of behavior. |

# Ownership and overlap check

- Program record: `docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md` (created by this task).
- Open PRs inspected: #224, #245, #264, #279, #283, #284, #288, #289, plus entries listed in the possibly stale `ACTIVE_WORK.md`.
- Active tasks inspected through live open PR metadata and changed-file lists; local directory enumeration was unavailable.
- Ownership checker result: not run; no local checkout.
- Exclusive claims: the four documentation/report paths in frontmatter.
- Shared claims: none.
- Read-only dependencies: governance docs, source, datapacks, and tests.
- Overlaps: no current open PR changed the four exact owned paths. Candidate work involving `src/game/game.cpp` or `src/game/game.hpp` overlaps PR #289 and must not start until rechecked.
- Resolution: Stage 1 edits only new paths. Future candidate implementations require separate tasks, branches, worktrees, and draft PRs.

# Current state

The Stage 1 evidence inventory is complete for ten unique candidates. It does not assert that every matching CrystalServer commit has been semantically reviewed. Fifty `fix` search hits and thirty `crash` search hits were screened; those search result sets overlap. Ten unique diffs were opened and compared against current Canary source.

# Plan

1. Publish this documentation-only branch and open a draft PR.
2. Verify the PR repository, base/head, changed-file list, and full diff.
3. Verify current-head checks; keep the PR draft if required evidence is unavailable.
4. After this inventory merges, select only one non-overlapping candidate from the program queue and create a separate implementation task.

# Work log

## 2026-07-13T21:01:05Z

- Changed: created the Stage 1 task, program record, Markdown report, and JSON report.
- Learned: one deterministic crash candidate is missing in current Canary (`ConditionLight` zero-level division); several CrystalServer fixes are already present or Canary is safer; protocol/client candidates lack contract proof; one upstream null-parent patch would leave partial removal state if transplanted directly.
- Failed/blocked: local Git/worktree and ownership commands are unavailable because the sandbox cannot resolve GitHub through shell networking.
- Result: documentation-only inventory ready for PR review; no functional change made.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Treat CrystalServer only as a candidate source | Presence upstream is not proof; current Canary behavior and tests govern. | none |
| Split bundled commits into independently classified candidates | One commit can contain safe, unsafe, content-only, and client-coupled changes. | none |
| Do not transplant the CrystalServer `table.unserialize` parser | It is a large bespoke parser without compatibility/security proof. | none |
| Do not transplant the CrystalServer `removeCreature` early return | It occurs after tile removal and before lifecycle cleanup, risking corrupt partial state. | none |
| Defer `game.cpp`/`game.hpp` implementation work | Open PR #289 currently owns overlapping paths. | none |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `docs/agents/tasks/active/CAN-20260713-crystalserver-comparison-inventory.md` | exclusive | Task state and handoff | created |
| `docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md` | exclusive | Long-lived program state and queue | created |
| `artifacts/upstream/crystalserver/CRYSTALSERVER_COMPARISON_STAGE1.md` | exclusive | Human-readable Stage 1 report | created |
| `artifacts/upstream/crystalserver/crystalserver_comparison_stage1.json` | exclusive | Machine-readable Stage 1 report | created |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| pending | Local startup Git commands | unavailable | No local checkout; shell DNS to GitHub failed. |
| pending | Manual changed-path and full-diff review through GitHub | pending | Perform after draft PR creation. |
| pending | `git diff --check` | not-run | Requires checkout or CI. |
| pending | Current-head GitHub checks | pending | Verify after branch files are committed. |

Never write `passed` without verification on the stated commit.

# Failed approaches and dead ends

- GitHub file fetch cannot list a directory; active task discovery was therefore reconstructed from open PRs and their changed-file lists rather than inventing directory state.
- Repository code search did not reliably find every exact symbol; relevant current files were fetched directly by known path and baseline SHA.
- CrystalServer commit messages were not accepted as proof; candidate diffs were opened before classification.

# Risks and compatibility

- Runtime: none in this task; reports only.
- Data/migration: none in this task.
- Security: reports identify possible shell execution and dynamic-evaluation surfaces but do not modify them.
- Backward compatibility: unchanged.
- Cross-repo rollout: none; client-coupled candidates remain gated.
- Rollback: revert the documentation/report commits or close the PR.

# Remaining work

1. Open and verify the draft PR.
2. Obtain current-head CI evidence.
3. Merge only if the documentation-only autonomous merge gate is satisfied.
4. Create a separate task for `CS-001` after rechecking ownership and current `main`.

# Handoff

## Start here

Read the program record and both Stage 1 reports. Re-fetch current `main`, all open PRs, and the selected CrystalServer commit before acting on any candidate.

## Do not repeat

- Do not mass-copy or cherry-pick CrystalServer.
- Do not treat a matching commit message as evidence.
- Do not combine `FS.mkdir` and `table.unserialize` remediation merely because CrystalServer bundled them.
- Do not copy the `removeCreature` early-return patch.
- Do not implement Market/disconnect packet changes without OTClient contract tests.
- Do not start a `game.cpp`/`game.hpp` candidate while ownership overlaps remain unresolved.

## Required reads

- `AGENTS.md`
- `docs/agents/README.md`
- `docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md`
- all overlapping active task records and live open PRs
- `docs/agents/MODULE_CATALOG.md`
- `docs/agents/KNOWN_RISKS.md`
- `docs/agents/BUILD_TEST_MATRIX.md`
- `docs/agents/CROSS_REPO_CONTRACTS.md`
- selected CrystalServer diff, current Canary source/tests, and relevant system docs

## Open questions

- Which current Canary call sites can pass a zero light level without deserialization?
- Are `FS.mkdir` or `table.unserialize` reachable from untrusted runtime input?
- What exact maintained OTClient limits and disconnect payload contracts apply to protocol 15.25?
- What invariant should `Game::removeCreature` enforce when a creature lacks a parent after tile-side effects?

# Completion

- Final status: active; Stage 1 artifacts created, PR/CI verification pending.
- PR: pending.
- Merge commit: none.
- Program record updated: yes.
- Catalogue updated: not applicable.
- Changelog updated: not applicable.
- Archived at: not archived.
