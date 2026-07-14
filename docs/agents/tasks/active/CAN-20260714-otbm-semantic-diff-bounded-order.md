---
task_id: CAN-20260714-otbm-semantic-diff-bounded-order
program_id: ""
coordination_id: OTBM-SEMANTIC-DIFF-BOUNDED-ORDER
status: active
agent: "GPT-5.6 Thinking"
branch: fix/otbm-semantic-diff-bounded-order
base_branch: main
created: 2026-07-14T10:30:00+02:00
updated: 2026-07-14T10:50:00+02:00
last_verified_commit: "4463517efa5a9d902f4ee73d70b867e856d6e119"
risk: low
related_issue: ""
related_pr: "#319"
depends_on: []
blocks:
  - CAN-20260714-targuna-donor-isolation
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_semantic_diff_analysis.py
    - tools/ai-agent/test_otbm_semantic_diff.py
    - docs/agents/CHANGELOG.md
    - docs/agents/tasks/active/CAN-20260714-otbm-semantic-diff-bounded-order.md
    - .github/workflows/refresh-otbm-semantic-diff-bounded-order.yml
  shared: []
  read_only:
    - AGENTS.md
    - docs/ai-agent/OTBM_SEMANTIC_DIFF.md
    - tools/ai-agent/otbm_world_index.py
modules_touched:
  - Semantic OTBM Diff bounded tile iteration
reuses:
  - Unified OTBM World Index
  - Semantic OTBM Diff
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Fix bounded Semantic OTBM Diff so a region spanning multiple 256x256 World Index areas is streamed in strict `(z,y,x)` order instead of failing with `World Index tile iteration is not strictly ordered`.

# Acceptance criteria

- [x] Reproduce the failure with a synthetic bounded region spanning adjacent same-floor areas whose local Y ranges interleave.
- [x] Merge selected area iterators in strict position order without materializing a full-map tile list.
- [x] Preserve full-index behavior and fail-closed duplicate/non-increasing position detection.
- [x] Add a focused regression test using real synthetic OTBM indexes.
- [x] Run the dedicated Semantic OTBM Diff workflow and repository CI on the validated head.
- [x] Record changelog impact.
- [ ] Refresh the branch from advanced `main` without losing the validated source/test change.
- [ ] Remove the temporary refresh workflow before merge.
- [ ] Re-run final-head checks, merge autonomously and archive the task.

# Confirmed context

- PR #311 merged Semantic OTBM Diff.
- Bounded Targuna audit PR #316 reproduced a real failure for bounds `31488,31488,4` to `32255,32255,10`.
- `WorldIndex.iter_region_tiles()` iterates one area at a time. Adjacent X areas can each contain overlapping Y ranges, so concatenating them is not globally sorted by `(z,y,x)`.
- `iter_snapshots()` correctly rejects non-increasing positions, but its bounded iterator source violated that precondition.
- The applied fix performs a heap-based k-way merge of only the intersecting area-local iterators and retains the final strict-order guard.
- Regression `test_31_bounded_region_merges_adjacent_areas_in_position_order` builds two real synthetic OTBM area nodes whose local Y ranges interleave.
- Initial regression execution reached the fixture but failed an independent World Index `maxItemDepth` contract because it had only inline ground. The fixture now contains a neutral nested child item and therefore exercises the intended ordering path.
- Temporary patch workflows/scripts self-removed from the branch.
- Ready-state CI run `29319066210` passed Fast Checks, Lua Tests, Linux Release and aggregate `Required` on validated head `4463517efa5a9d902f4ee73d70b867e856d6e119`.
- Merge was then blocked because `main` advanced with Real Tibia parity governance and changed the shared changelog.
- A temporary self-removing refresh workflow will merge current `main`, favor current-main text only for conflicts, restore the PR #319 changelog entry, and push a new head for complete revalidation.

# Plan

1. Refresh from current `main` and remove the temporary refresh workflow.
2. Re-run focused and repository CI on the refreshed final head.
3. Review final diff, reviews and unresolved threads.
4. Satisfy `Required`, squash-merge and archive.
5. Update/resume PR #316 on the merged fix.

# Current state

The validated fix is complete, but PR #319 has a changelog conflict with advanced `main`. This task-record update intentionally triggers the branch-local refresh workflow.

# Validation and CI

| Commit/run | Check | Result | Notes |
|---|---|---|---|
| PR #316 run `29317641389` | real bounded Targuna audit | failed as expected | `SemanticDiffError: World Index tile iteration is not strictly ordered`. |
| `bcf56e2de38bb2a25fc2fa0d9f391eb6009c8da2` | source/regression patch | applied | Heap merge, regression and changelog committed; temporary patch machinery removed. |
| `5759306ec0a6514c572164024753a134c23f2cc2` / OTBM Map Tools | first regression run | failed in fixture setup | `maxItemDepth=-1` versus binary index depth 0; not a heap-merge failure. |
| `ab6873ebbc6b16c701a2a013973ecce9a334922f` | fixture correction | applied | Added a neutral nested item to the two synthetic area tiles. |
| `4463517efa5a9d902f4ee73d70b867e856d6e119` / `29318967704` | OTBM Semantic Diff | passed | Full focused suite and new regression passed. |
| `4463517efa5a9d902f4ee73d70b867e856d6e119` / `29318967705` | OTBM Map Tools | passed | Existing map-tool tests passed. |
| `4463517efa5a9d902f4ee73d70b867e856d6e119` / `29319066210` | ready-state CI | passed | Fast Checks, Lua Tests, Linux Release and `Required` succeeded. |
| refreshed final head | complete checks | pending | Required after conflict-safe refresh. |

# Safety and rollback

- No OTBM, datapack or runtime gameplay change.
- Only read-only evidence iteration changes.
- Rollback by reverting the bugfix merge commit.

# Remaining work

Refresh, revalidate, merge, archive and resume PR #316.

# Completion

- Final status: active
- PR: #319
- Final reviewed head:
- Merge commit:
- Archived at:
