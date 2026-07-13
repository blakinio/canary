---
task_id: CAN-20260713-crystalserver-comparison-inventory
program_id: CAN-PROGRAM-CRYSTALSERVER-COMPARISON
coordination_id: ""
status: ready_for_merge
agent: GPT-5.6 Thinking
branch: docs/crystalserver-comparison-inventory
base_branch: main
created: 2026-07-13T21:01:05Z
updated: 2026-07-13T21:12:00Z
last_verified_commit: "720fd7cf7d99c8c47b0cb84767d15416af6e0667"
risk: low
related_issue: ""
related_pr: "https://github.com/blakinio/canary/pull/291"
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

Create the evidence-backed Stage 1 CrystalServer comparison inventory without changing runtime behavior, datapacks, protocol, database, maps, assets, or production configuration.

# Acceptance criteria

- [x] Exact `main` baseline SHAs and declared versions/protocols recorded.
- [x] Live open PRs and changed paths inspected for overlap.
- [x] Durable program record created.
- [x] Markdown and machine-readable JSON reports created under `artifacts/upstream/crystalserver/`.
- [x] Ten bounded candidates include opened CrystalServer diffs, current Canary evidence, one status, risk, dependencies, tests, decision, and provenance.
- [x] No functional source, datapack, schema, protocol, map, asset, secret, or production configuration changed.
- [x] Draft PR opened in the exact writable repository and verified as base `main`, same-repository head, and four intended paths.
- [x] JSON generated and parsed before commit; committed content re-fetched from the branch.
- [x] Full changed-file list and authored four-file diff reviewed; no unrelated or forbidden path found.
- [x] Local `git diff --check` was unavailable because no checkout/worktree and shell DNS failed; the exact limitation is documented as allowed by the autonomous merge gate.
- [x] Current-head GitHub checks at `720fd7cf7d99c8c47b0cb84767d15416af6e0667` passed: ownership validation and required CI.
- [x] No review submissions, requested changes, or unresolved review threads exist.
- [x] Module catalogue, changelog, and compatibility-note impact handled: not applicable because no behavior/interface changed.
- [x] Cross-repository impact handled: both comparison repositories remained read-only.
- [x] Autonomous merge gate satisfied for the verified head; this final task-record-only commit must receive the same required checks before merge.

# Confirmed context

- Writable repository: `blakinio/canary` only.
- Canary baseline: `360d79ebad5802edd4d89e99d0f210ab19b36b60`.
- CrystalServer baseline/last analyzed commit: `fc0d53b9f9965463b6082c07e6d3d482294541a7`.
- OpenTibiaBR Canary reference baseline: `9365c1c4aa63529b9ff757f53737274894c02b8e`.
- Both compared servers declare client protocol `1525` / 15.25.
- Canary declares `3.6.1`; CrystalServer declares `4.1.9`.
- Draft PR: [#291](https://github.com/blakinio/canary/pull/291).
- PR base/head and URL were verified: `blakinio/canary:main` <- `blakinio/canary:docs/crystalserver-comparison-inventory`.
- A local checkout/worktree is unavailable. Shell Git failed with `Could not resolve host: github.com`; local startup commands, ownership checker, `git diff --check`, build, and tests are not claimed.

# Existing work to reuse

| System | Source | Reuse |
|---|---|---|
| Agent governance | `AGENTS.md`, `docs/agents/**` | Task/program/ownership/PR lifecycle. |
| Build/test matrix | `docs/agents/BUILD_TEST_MATRIX.md` | Candidate-specific validation gates. |
| Cross-repo contracts | `docs/agents/CROSS_REPO_CONTRACTS.md` | Required for Market/disconnect candidates. |
| Current Canary | `src/**`, `data/**`, `tests/**` | Semantic comparison target. |

# Ownership and overlap check

- Program: `docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md`.
- Open PRs inspected: #224, #245, #264, #279, #283, #284, #288, #289, plus entries in `ACTIVE_WORK.md`.
- PR #289 task `CAN-20260713-instance-arena-service` explicitly claims `src/game/game.cpp` and `src/game/game.hpp` as shared paths; `CS-005` and other overlapping implementations are deferred.
- Exact exclusive paths: the four files in frontmatter.
- Shared paths: none.
- PR #291 changed-file list exactly matches those four exclusive paths.
- Current-head `Agent Task Ownership` workflow run 448 passed all focused tests and ownership-index validation.

# Current state

Stage 1 deeply reviewed ten unique candidates after screening 50 `fix` and 30 `crash` search hits; the search sets overlap and are not claimed as 80 unique commits.

Classification totals: `ALREADY_PRESENT` 2, `CANARY_SUPERIOR` 1, `VALID_FIX_MISSING` 1, `PARTIAL_VALUE` 3, `CLIENT_COUPLED` 2, `DANGEROUS` 1.

Only `CS-001` currently meets `VALID_FIX_MISSING`: current `ConditionLight` deserialization can preserve level zero and `startCondition` divides by that field. No runtime fix is part of PR #291.

# Work log

## 2026-07-13T21:01:05Z

- Created task, program, Markdown report, and JSON report.
- Identified one deterministic missing crash guard, three already-present/superior cases, three partial signals, two client-coupled candidates, and one dangerous upstream patch.
- Recorded all unavailable local validation explicitly.

## 2026-07-13T21:05:43Z

- Opened draft PR #291 in `blakinio/canary`.
- Verified base/head repository and branch, draft state, baseline SHA, and four changed files.
- Re-fetched the committed JSON from the branch.

## 2026-07-13T21:12:00Z

- Verified PR head `720fd7cf7d99c8c47b0cb84767d15416af6e0667` is mergeable.
- `Agent Task Ownership` run 448: `success`; focused unit tests, tooling compilation, task validation, and ownership-index rendering passed.
- CI run 1543: `success`; changed-path detection and the required aggregate job passed; runtime builds/tests were correctly skipped for documentation-only scope.
- No reviews or unresolved review threads exist.
- Final task-record-only commit created; required checks must be re-read on its resulting head before merge.

# Decisions

| Decision | Reason |
|---|---|
| CrystalServer is only a candidate source | Upstream presence is not correctness evidence. |
| Bundled commits are split | Independent parts can require different statuses/gates. |
| Do not copy the upstream `table.unserialize` parser | Compatibility and security are unproven. |
| Do not copy the upstream `removeCreature` early return | It follows partial side effects and may preserve corrupt state. |
| Defer `game.cpp`/`game.hpp` candidates | PR #289 has explicit overlapping ownership. |

# Files and interfaces

| Path | Ownership | Purpose |
|---|---|---|
| `docs/agents/tasks/active/CAN-20260713-crystalserver-comparison-inventory.md` | exclusive | Task state/handoff. |
| `docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md` | exclusive | Long-lived queue/invariants. |
| `artifacts/upstream/crystalserver/CRYSTALSERVER_COMPARISON_STAGE1.md` | exclusive | Human-readable report. |
| `artifacts/upstream/crystalserver/crystalserver_comparison_stage1.json` | exclusive | Machine-readable report. |

# Validation and CI

| Head | Check | Result |
|---|---|---|
| `720fd7cf7d99c8c47b0cb84767d15416af6e0667` | Exact changed-file list/full authored diff | passed; four intended files only |
| `720fd7cf7d99c8c47b0cb84767d15416af6e0667` | JSON syntax/content fetch | passed |
| `720fd7cf7d99c8c47b0cb84767d15416af6e0667` | Agent Task Ownership run 448 | passed |
| `720fd7cf7d99c8c47b0cb84767d15416af6e0667` | CI run 1543 required aggregate | passed |
| final task-record head | Required workflows | must pass before merge; do not infer from previous head |
| local | `git diff --check` | unavailable; exact environment documented |

# Failed approaches and dead ends

- Shell Git cannot resolve GitHub; no local checkout/worktree/startup-command evidence exists.
- Code search did not reliably locate every exact symbol; known paths were fetched directly at baseline SHAs.
- Commit messages were not accepted as proof; diffs were opened before classification.

# Risks and compatibility

- Runtime/data/protocol: unchanged.
- Security: candidate surfaces documented; no remediation claim.
- Backward compatibility: unchanged.
- Rollback: close/revert PR #291.

# Remaining work

1. Verify required workflows on the final task-record head.
2. Mark PR #291 ready and squash-merge only if the final head remains mergeable and unblocked.
3. Archive this task and update the program in a narrow cleanup PR.
4. Create a separate test-first task for `CS-001` after cleanup merges and fresh ownership checks pass.

# Handoff

## Start here

Read PR #291, the program, and both reports. Re-fetch current `main`, open PRs, and the selected upstream diff before acting.

## Do not repeat

- No mass copy/cherry-pick.
- No commit message as proof.
- Do not combine `FS.mkdir` and `table.unserialize` remediation.
- Do not copy the `removeCreature` early return.
- Do not change Market/disconnect packets without maintained-client contracts.
- Do not enter overlapping `game.cpp`/`game.hpp` paths while ownership remains unresolved.

## Open questions

- Which current path supplies zero to `ConditionLight`, and which fixture best proves it?
- Are `FS.mkdir` or `table.unserialize` reachable from untrusted input?
- What exact maintained OTClient Market/disconnect contracts apply to protocol 15.25?
- What complete lifecycle behavior is required when a creature parent is absent?

# Completion

- Final status: ready for merge after final-head checks.
- PR: https://github.com/blakinio/canary/pull/291
- Merge commit: none.
- Program record updated: yes.
- Catalogue/changelog: not applicable.
- Archived at: pending cleanup PR.
