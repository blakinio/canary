---
task_id: CAN-20260716-otbm-region-merge-planner
program_id: "OTS-OTBM-VALIDATION"
coordination_id: "OTS-OTBM-VALIDATION"
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/otbm-region-merge-planner
base_branch: main
created: 2026-07-16T11:20:00+02:00
updated: 2026-07-16T11:31:00+02:00
last_verified_commit: "0b058a70cffc515d49ba22d40fee3b0492b92c25"
risk: high
related_issue: ""
related_pr: "424"
depends_on:
  - "OTBM World Index #219"
  - "Semantic OTBM Diff #311"
  - "OTBM script resolution #104"
  - "OTBM repair sandbox verifier #422"
blocks:
  - "future structural OTBM region import writer"
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_region_merge_planner.py
    - tools/ai-agent/otbm_region_merge_planner_tool.py
    - tools/ai-agent/test_otbm_region_merge_planner.py
    - docs/ai-agent/OTBM_REGION_MERGE_PLANNER.md
    - docs/ai-agent/OTBM_REGION_MERGE_PLAN.schema.json
    - docs/agents/tasks/active/CAN-20260716-otbm-region-merge-planner.md
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/ai-agent/otbm_world_index.py
    - tools/ai-agent/otbm_semantic_diff.py
    - tools/ai-agent/otbm_script_resolution.py
modules_touched:
  - OTBM donor/region merge planner
reuses:
  - canonical OTBM World Index
  - existing World Index manifest/source pins
  - existing script-resolution report format
  - existing Semantic Diff terminology and evidence model
public_interfaces:
  - canary-otbm-region-merge-plan-v1
  - OTBM region merge planner CLI
cross_repo_tasks: []
---

# Goal

Create a deterministic read-only review planner for importing an explicit donor OTBM region into an explicit target region using canonical World Index evidence and a declared donor-to-target translation. The planner must classify structural actions and identifier/mechanic conflicts without writing any OTBM.

# Acceptance criteria

- [ ] Consume current and donor canonical `.widx` plus provenance manifests; no OTBM parsing or writing.
- [ ] Require explicit inclusive donor region and explicit target origin/translation; never heuristically align cities or fragments.
- [ ] Support `overlay` and `replace-region` review policies without executing either.
- [ ] Compare canonical tile structure and placement stacks after translation and classify unchanged/add/replace/delete-candidate actions.
- [ ] Retain exact donor/current tile snapshots and deterministic action IDs.
- [ ] Detect target-coordinate overflow and out-of-floor-range translation fail closed.
- [ ] Detect global current-map AID/UID collisions for donor mechanics entering the target region.
- [ ] Distinguish same-identifier same-handler evidence from conflicting/unresolved runtime evidence when explicit current/donor script-resolution reports are supplied.
- [ ] Detect house-door ID reuse and teleport destinations that translate outside donor region or target to missing current/donor tiles; never guess intended destination remapping.
- [ ] Preserve current-only custom content as explicit replace/delete conflicts rather than silently overwriting it.
- [ ] Emit a review-only `canary-otbm-region-merge-plan-v1`; no executable writer instructions.
- [ ] Bound action/conflict samples while retaining exact summary totals.
- [ ] Pin both indexes, manifests and optional script-resolution inputs by SHA-256.
- [ ] Add focused tests, schema/docs and narrow catalogue/changelog updates.
- [ ] Verify current-head required checks before readiness/merge.

# Confirmed context

- Writable repository is exactly `blakinio/canary`; all donor/upstream repositories remain read-only.
- Task-start `main` is `52eb5932d94feeec8a1ba81ece7de7958ed06eea`, the merge of repair sandbox PR #422.
- Open PR #316 owns only Targuna-specific audit workflow/script/task paths and does not overlap generic planner paths.
- World Index already exposes region iteration, exact tile lookup and global AID/UID/house-door/teleport postings.
- Semantic Diff compares same-coordinate canonical indexes; this planner adds only explicit translation-aware review planning and does not create another OTBM parser.
- Phase 8 cannot insert/delete tiles/items and is not broadened by this task.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T11:31:00+02:00
head: 0b058a70cffc515d49ba22d40fee3b0492b92c25
branch: feat/otbm-region-merge-planner
pr: 424
status: implementing
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - tools/ai-agent/otbm_region_merge_planner.py
  - tools/ai-agent/otbm_region_merge_planner_tool.py
  - tools/ai-agent/test_otbm_region_merge_planner.py
  - docs/ai-agent/OTBM_REGION_MERGE_PLANNER.md
  - docs/ai-agent/OTBM_REGION_MERGE_PLAN.schema.json
  - docs/agents/tasks/active/CAN-20260716-otbm-region-merge-planner.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - current World Index API supports bounded region iteration exact tile lookup and global mechanic postings
  - PR 316 Targuna-specific paths do not overlap this generic planner
  - Phase 8 remains fixed-width existing-attribute only and cannot be reused as a structural region writer
  - draft PR 424 targets blakinio/canary main from feat/otbm-region-merge-planner
  - initial CI passed and initial ownership failure is task-checkpoint metadata only
  - current and donor World Index access will use public WorldIndex APIs rather than reading binary records independently
derived:
  - explicit translation-aware planning is the smallest safe step before any future structural writer ADR
unknown:
  - exact script-resolution compatibility rules for translated donor positions until adapter implementation is tested
  - current-head CI after implementation
conflicts: []
first_failure:
  marker: initial-ownership-metadata
  evidence: initial task checkpoint still had pr null and head at the #422 merge commit
rejected_hypotheses:
  - heuristic donor-to-target city matching
  - direct OTBM region writing in this task
  - silent overwrite of current-only custom content
changed_paths:
  - docs/agents/tasks/active/CAN-20260716-otbm-region-merge-planner.md
validation:
  - CI run 29486717150 passed on 0b058a70cffc515d49ba22d40fee3b0492b92c25
  - Ownership run 29486716648 failed only at changed active task checkpoint validation before PR/head binding
blockers: []
next_action: Implement canonical translated tile snapshots, deterministic review actions, and exact mechanic conflict detection over public WorldIndex APIs.
```

# Completion

- Final status: implementing
- Canary PR: #424
- Catalogue updated: pending
- Changelog updated: pending
- Archived at: not archived
