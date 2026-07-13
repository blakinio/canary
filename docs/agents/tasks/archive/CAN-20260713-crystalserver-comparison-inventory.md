---
task_id: CAN-20260713-crystalserver-comparison-inventory
program_id: CAN-PROGRAM-CRYSTALSERVER-COMPARISON
coordination_id: ""
status: completed
agent: GPT-5.6 Thinking
branch: docs/crystalserver-comparison-inventory
base_branch: main
created: 2026-07-13T21:01:05Z
updated: 2026-07-13T21:20:30Z
last_verified_commit: "5850d70a227bf60ae1ee594677a4a4f92b6be953"
risk: low
related_issue: ""
related_pr: "https://github.com/blakinio/canary/pull/291"
depends_on: []
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/archive/CAN-20260713-crystalserver-comparison-inventory.md
    - docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md
  shared: []
  read_only:
    - artifacts/upstream/crystalserver/CRYSTALSERVER_COMPARISON_STAGE1.md
    - artifacts/upstream/crystalserver/crystalserver_comparison_stage1.json
modules_touched: []
reuses:
  - agent task/program governance
  - current source and test contracts
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Create and merge the evidence-backed Stage 1 CrystalServer comparison inventory without changing runtime behavior, datapacks, protocol, database, maps, assets, secrets, or production configuration.

# Result

Completed and merged through PR [#291](https://github.com/blakinio/canary/pull/291).

- Squash merge: `bceccba9349d35a1d84f446757e53ac3adb602e1`.
- Final reviewed PR head: `5850d70a227bf60ae1ee594677a4a4f92b6be953`.
- Four documentation/report paths only.
- Program record: `docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md`.
- Human report: `artifacts/upstream/crystalserver/CRYSTALSERVER_COMPARISON_STAGE1.md`.
- JSON report: `artifacts/upstream/crystalserver/crystalserver_comparison_stage1.json`.
- No functional implementation was included.

# Baselines

| Repository | Baseline SHA | Declared version/protocol | Access |
|---|---|---|---|
| `blakinio/canary` | `360d79ebad5802edd4d89e99d0f210ab19b36b60` | server `3.6.1`, client `1525` | writable target only |
| `zimbadev/crystalserver` | `fc0d53b9f9965463b6082c07e6d3d482294541a7` | server `4.1.9`, client `1525` | read-only |
| `opentibiabr/canary` | `9365c1c4aa63529b9ff757f53737274894c02b8e` | verify per future task | read-only |

Last analyzed CrystalServer commit: `fc0d53b9f9965463b6082c07e6d3d482294541a7`.

# Inventory result

Fifty `fix` and thirty `crash` search hits were screened; the sets overlap. Ten unique diffs were deeply reviewed.

| Status | Count |
|---|---:|
| `ALREADY_PRESENT` | 2 |
| `CANARY_SUPERIOR` | 1 |
| `VALID_FIX_MISSING` | 1 |
| `PARTIAL_VALUE` | 3 |
| `CLIENT_COUPLED` | 2 |
| `DANGEROUS` | 1 |

Only `CS-001` was classified `VALID_FIX_MISSING`: current `ConditionLight` deserialization can retain level zero and `ConditionLight::startCondition` divides by that field. The fix was deliberately not implemented in this inventory task.

# Key decisions

- CrystalServer remains a source of candidates, not proof.
- Do not copy the CrystalServer `table.unserialize` parser.
- Do not copy the CrystalServer `Game::removeCreature` early return; it follows partial removal side effects.
- Market and disconnect candidates remain client-coupled.
- `src/game/game.cpp` and `src/game/game.hpp` candidates remain deferred while overlapping ownership exists.
- Every implementation requires a separate task, branch, worktree, draft PR, fresh baselines, and candidate-specific validation.

# Validation and CI

| Evidence | Result |
|---|---|
| PR #291 exact repository/base/head and four-file changed-path review | passed |
| JSON generation, parse, and committed-content fetch | passed |
| Agent Task Ownership run 450 | success |
| Ready-state CI run 1546 | success |
| Fast checks, Reviewdog, yamllint, Lua tests | success |
| Linux release configure/compile and required aggregate | success |
| Reviews/requested changes/unresolved threads | none |
| Local Git/worktree and `git diff --check` | unavailable; shell DNS could not resolve GitHub, documented before merge |

# Provenance and artifacts

The reports record, per candidate: CrystalServer repository and commit, author, date, linked PR number where available, files, symbols, exact problem, current Canary evidence, status, risk, dependencies, proposed tests, decision, rationale, and any upstream idea considered for adaptation.

# Remaining program work

1. Create a separate test-first task for `CS-001` after re-fetching current heads, open PRs, ownership, relevant tests, and the CrystalServer diff.
2. Independently investigate `CS-006` (`FS.mkdir`) and `CS-007` (`table.unserialize`) without copying the upstream denylist/parser.
3. Treat `CS-008` and `CS-009` as cross-repository client-contract work.
4. Reproduce and redesign `CS-010`; never transplant the partial-state early return.
5. Continue from the recorded `last analyzed CrystalServer commit`, not from chat history.

# Handoff

## Start here

Read:

- `AGENTS.md`;
- `docs/agents/README.md`;
- `docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md`;
- both reports under `artifacts/upstream/crystalserver/`;
- all current active tasks and open PRs;
- the selected CrystalServer diff and corresponding current Canary source/tests.

## Do not repeat

- Do not rescan from the beginning without first checking the JSON inventory and last analyzed commit.
- Do not infer correctness from commit messages or matching protocol numbers.
- Do not combine independently gated candidates merely because CrystalServer bundled them.
- Do not implement on overlapping paths without resolving ownership.

# Completion

- Final status: completed.
- Feature PR: https://github.com/blakinio/canary/pull/291
- Feature head: `5850d70a227bf60ae1ee594677a4a4f92b6be953`.
- Merge commit: `bceccba9349d35a1d84f446757e53ac3adb602e1`.
- Program record updated: in cleanup PR.
- Catalogue/changelog: not applicable; no interface or behavior changed.
- Archived at: `docs/agents/tasks/archive/CAN-20260713-crystalserver-comparison-inventory.md`.
