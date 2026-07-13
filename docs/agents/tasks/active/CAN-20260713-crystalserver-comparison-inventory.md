---
task_id: CAN-20260713-crystalserver-comparison-inventory
program_id: CAN-PROGRAM-CRYSTALSERVER-COMPARISON
coordination_id: ""
status: active
agent: GPT-5.6 Thinking
branch: docs/crystalserver-comparison-inventory
base_branch: main
created: 2026-07-13T21:01:05Z
updated: 2026-07-13T21:07:00Z
last_verified_commit: "360d79ebad5802edd4d89e99d0f210ab19b36b60"
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
- [x] Draft PR opened in the exact writable repository and verified as base `main`, same-repository head, and four intended files.
- [x] JSON generated and parsed successfully before commit; committed content re-fetched from the branch.
- [ ] Local or CI `git diff --check` evidence recorded.
- [ ] Current-head GitHub checks completed and verified.
- [x] Module catalogue impact handled: none; no reusable runtime/tool interface changed.
- [x] Changelog impact handled: none; no behavior changed.
- [x] Cross-repository impact handled: both comparison repositories remained read-only.
- [ ] Autonomous merge gate satisfied.

# Confirmed context

- Writable repository: `blakinio/canary` only.
- Canary baseline: `360d79ebad5802edd4d89e99d0f210ab19b36b60`.
- CrystalServer baseline/last analyzed commit: `fc0d53b9f9965463b6082c07e6d3d482294541a7`.
- OpenTibiaBR Canary reference baseline: `9365c1c4aa63529b9ff757f53737274894c02b8e`.
- Both compared servers declare client protocol `1525` / 15.25.
- Canary declares `3.6.1`; CrystalServer declares `4.1.9`.
- Draft PR: [#291](https://github.com/blakinio/canary/pull/291).
- PR creation evidence: base `main`, base SHA `360d79e...`, head `docs/crystalserver-comparison-inventory`, four changed files, draft state.
- A local checkout/worktree is unavailable. Shell Git failed with `Could not resolve host: github.com`; inspection and writes use the GitHub connector.
- Therefore local `git status --short --branch`, `git branch -vv`, `git remote -v`, `git worktree list`, ownership checker, `git diff --check`, builds, and tests are not claimed.

# Existing work to reuse

| System | Source | Reuse |
|---|---|---|
| Agent governance | `AGENTS.md`, `docs/agents/**` | Task/program/ownership/PR lifecycle. |
| Build/test matrix | `docs/agents/BUILD_TEST_MATRIX.md` | Candidate-specific validation gates. |
| Cross-repo contract registry | `docs/agents/CROSS_REPO_CONTRACTS.md` | Required for Market/disconnect candidates. |
| Current Canary architecture | `src/**`, `data/**`, `tests/**` | Semantic comparison target. |

# Ownership and overlap check

- Program: `docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md`.
- Open PRs inspected: #224, #245, #264, #279, #283, #284, #288, #289, plus entries in `ACTIVE_WORK.md`.
- Ownership checker: not run locally; unavailable checkout.
- Exact exclusive paths: the four files in frontmatter.
- Shared paths: none.
- PR #291 changed-file list exactly matches the four exclusive paths.
- No current open PR was found changing those four exact paths.
- Candidate work in `src/game/game.cpp` or `src/game/game.hpp` overlaps PR #289 and is deferred.

# Current state

Stage 1 is complete for ten unique candidates. Fifty `fix` search hits and thirty `crash` search hits were screened; the sets overlap and are not claimed as 80 unique commits. Ten unique diffs were opened and compared with current Canary source.

Classification totals: `ALREADY_PRESENT` 2, `CANARY_SUPERIOR` 1, `VALID_FIX_MISSING` 1, `PARTIAL_VALUE` 3, `CLIENT_COUPLED` 2, `DANGEROUS` 1.

Only `CS-001` currently meets `VALID_FIX_MISSING`: current `ConditionLight` deserialization can preserve level zero and `startCondition` divides by that field. No runtime fix is part of this PR.

# Work log

## 2026-07-13T21:01:05Z

- Created task, program, Markdown report, and JSON report.
- Identified one deterministic missing crash guard, three already-present/superior cases, three partial signals, two client-coupled candidates, and one dangerous upstream patch.
- Recorded local sandbox DNS limitation and all missing validation honestly.

## 2026-07-13T21:05:43Z

- Opened draft PR #291 in `blakinio/canary`.
- Verified base/head repository and branch, draft state, baseline SHA, and four changed files.
- Re-fetched the committed JSON from the branch.
- At head `58933b18c898855110f68ff9d80be133efd691eb`, `Agent Task Ownership` completed successfully and general `CI` was queued; later documentation updates moved the head, so final checks must be re-fetched.

# Decisions

| Decision | Reason |
|---|---|
| Treat CrystalServer only as a candidate source | Presence upstream is not correctness evidence. |
| Split bundled commits into separate candidates | One bundle can contain safe, unsafe, content, and protocol changes. |
| Do not copy the CrystalServer `table.unserialize` parser | Compatibility and security are unproven. |
| Do not copy the CrystalServer `removeCreature` early return | It follows partial side effects and may preserve corrupt state. |
| Defer `game.cpp`/`game.hpp` candidates | Open PR #289 overlaps those paths. |
| Keep PR #291 draft | Current-head CI and diff-check evidence are not yet complete. |

# Files and interfaces

| Path | Ownership | Purpose |
|---|---|---|
| `docs/agents/tasks/active/CAN-20260713-crystalserver-comparison-inventory.md` | exclusive | Task state/handoff. |
| `docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md` | exclusive | Long-lived queue and invariants. |
| `artifacts/upstream/crystalserver/CRYSTALSERVER_COMPARISON_STAGE1.md` | exclusive | Human-readable report. |
| `artifacts/upstream/crystalserver/crystalserver_comparison_stage1.json` | exclusive | Machine-readable report. |

# Validation and CI

| Commit/head | Check | Result | Evidence |
|---|---|---|---|
| `58933b18c898855110f68ff9d80be133efd691eb` | Exact changed-file list | passed | Four intended new paths only. |
| `58933b18c898855110f68ff9d80be133efd691eb` | JSON syntax | passed | Generated/parsed before write; committed content re-fetched. |
| `58933b18c898855110f68ff9d80be133efd691eb` | Agent Task Ownership workflow | passed | Run 444 concluded `success`. |
| `58933b18c898855110f68ff9d80be133efd691eb` | General CI | queued at last check | Not a pass claim. |
| current head | Full required GitHub checks | pending | Re-fetch after final documentation commit. |
| current head | `git diff --check` or equivalent | not-run | Requires checkout or CI evidence. |

# Failed approaches and dead ends

- Shell Git cannot resolve GitHub; no local worktree or startup-command evidence exists.
- GitHub code search did not reliably locate every exact symbol, so known current paths were fetched directly at the baseline SHA.
- Commit messages were not accepted as proof; candidate diffs were opened before classification.

# Risks and compatibility

- Runtime/data/protocol: unchanged in this task.
- Security: reports identify candidate surfaces but make no remediation claim.
- Backward compatibility: unchanged.
- Rollback: close PR #291 or revert its documentation commits.

# Remaining work

1. Re-fetch PR #291 current head and workflow/check status.
2. Obtain `git diff --check` or equivalent CI evidence.
3. Keep draft unless the autonomous merge gate is completely satisfied.
4. After merge, create a separate test-first task for `CS-001` with fresh ownership and baseline checks.

# Handoff

## Start here

Read PR #291, the program, and both Stage 1 reports. Re-fetch current `main`, open PRs, and selected upstream diff before acting.

## Do not repeat

- No mass copy/cherry-pick.
- No upstream message as proof.
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

- Final status: active; inventory delivered, draft PR open, current-head CI pending.
- PR: https://github.com/blakinio/canary/pull/291
- Merge commit: none.
- Program record updated: yes.
- Catalogue/changelog: not applicable.
- Archived at: not archived.
