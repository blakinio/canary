---
task_id: CAN-20260716-otbm-region-merge-planner
program_id: "OTS-OTBM-VALIDATION"
coordination_id: "OTS-OTBM-VALIDATION"
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/otbm-region-merge-planner
base_branch: main
created: 2026-07-16T11:20:00+02:00
updated: 2026-07-16T12:40:00+02:00
last_verified_commit: "5614f2bcfd6146b6c0b0efed5b14b01919bb01a9"
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

- [x] Consume current and donor canonical `.widx` plus provenance manifests; no OTBM parsing or writing.
- [x] Require explicit inclusive donor region and explicit target origin/translation; never heuristically align cities or fragments.
- [x] Support `overlay` and `replace-region` review policies without executing either.
- [x] Compare canonical tile structure and placement stacks after translation and classify unchanged/add/replace/delete-candidate actions.
- [x] Retain exact donor/current tile snapshots and deterministic action IDs.
- [x] Detect target-coordinate overflow and out-of-floor-range translation fail closed.
- [x] Detect global current-map AID/UID collisions for donor mechanics entering the target region.
- [x] Distinguish same-identifier same-handler evidence from conflicting/unresolved runtime evidence when explicit current/donor script-resolution reports are supplied.
- [x] Detect house-door ID reuse and teleport destinations that translate outside donor region or target to missing current/donor tiles; never guess intended destination remapping.
- [x] Preserve current-only custom content as explicit replace/delete conflicts rather than silently overwriting it.
- [x] Emit a review-only `canary-otbm-region-merge-plan-v1`; no executable writer instructions.
- [x] Bound action/conflict samples while retaining exact summary totals.
- [x] Pin both indexes, manifests and optional script-resolution inputs by SHA-256.
- [x] Add focused tests, schema/docs and narrow catalogue/changelog updates.
- [ ] Verify current-head required checks before readiness/merge.

# Confirmed context

- Writable repository is exactly `blakinio/canary`; all donor/upstream repositories remain read-only.
- Task-start `main` is `52eb5932d94feeec8a1ba81ece7de7958ed06eea`, the merge of repair sandbox PR #422.
- Current observed `main` advanced to `c36e8548f195843254f16963adc7cb1d497084aa` only through lifecycle/archive PRs after #419/#422; shared catalogue/changelog edits were rebuilt from that current baseline.
- Open PR #316 owns only Targuna-specific audit workflow/script/task paths and does not overlap generic planner paths.
- World Index already exposes region iteration, exact tile lookup and global AID/UID/house-door/teleport postings.
- Semantic Diff compares same-coordinate canonical indexes; this planner adds only explicit translation-aware review planning and does not create another OTBM parser.
- Phase 8 cannot insert/delete tiles/items and is not broadened by this task.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T12:40:00+02:00
head: 5614f2bcfd6146b6c0b0efed5b14b01919bb01a9
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
  - planner reuses public WorldIndex access and existing Semantic Diff manifest/pair provenance validation instead of reparsing OTBM or reimplementing index validation
  - PR 316 Targuna-specific paths do not overlap this generic planner
  - Phase 8 remains fixed-width existing-attribute only and is not expanded
  - draft PR 424 targets blakinio/canary main from feat/otbm-region-merge-planner
  - explicit translation supports overlay and replace-region review semantics with writerReady permanently false in v1
  - global retained-map UID AID and house-door collisions are checked outside the target region as well as inside it
  - internal donor teleport destinations are translated only when they lie inside the selected donor region; external destinations are never guessed or remapped
  - same-handler AID reuse requires explicit compatible current and donor script-resolution evidence; missing or unresolved evidence remains blocking unresolved
  - uniqueId collisions remain blocking regardless of handler evidence
  - output publication without overwrite uses exclusive create-new semantics
  - first OTBM Map Tools failure exposed synthetic fixtures with no node items and was fixed by adding a neutral out-of-scope node-item tile without weakening production validation
  - second OTBM Map Tools failure was a duplicate target_origin keyword in the test helper and was fixed by explicit helper override handling
  - CI run 29490967322 passed on functional head c3ed48f3b80700309178a7348dfd675ce7f88b2e
  - OTBM Map Tools run 29490967134 passed on functional head c3ed48f3b80700309178a7348dfd675ce7f88b2e
  - AI Agent Tools run 29490967167 passed on functional head c3ed48f3b80700309178a7348dfd675ce7f88b2e
  - MODULE_CATALOG patch contains exactly one added planner row and no unrelated drift
  - CHANGELOG patch contains exactly one Unreleased planner bullet and no unrelated drift
derived:
  - explicit translation-aware planning is the smallest safe step before any future structural writer ADR
  - a future structural writer must be a separate bounded task and cannot infer executable operations from writerReady false v1 reports without a new contract
unknown:
  - exact-head CI after final shared-document and checkpoint updates
conflicts: []
first_failure:
  marker: initial-ownership-metadata
  evidence: initial task checkpoint still had pr null and head at the #422 merge commit; later functional test failures were fixture/helper defects and are recorded under proven
rejected_hypotheses:
  - heuristic donor-to-target city matching
  - direct OTBM region writing in this task
  - silent overwrite of current-only custom content
  - treating actionId reuse as safe without explicit compatible handler evidence
  - translating teleport destinations outside the selected donor region
changed_paths:
  - docs/agents/CHANGELOG.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260716-otbm-region-merge-planner.md
  - docs/ai-agent/OTBM_REGION_MERGE_PLAN.schema.json
  - docs/ai-agent/OTBM_REGION_MERGE_PLANNER.md
  - tools/ai-agent/otbm_region_merge_planner.py
  - tools/ai-agent/otbm_region_merge_planner_tool.py
  - tools/ai-agent/test_otbm_region_merge_planner.py
validation:
  - CI run 29490967322 passed on c3ed48f3b80700309178a7348dfd675ce7f88b2e
  - OTBM Map Tools run 29490967134 passed on c3ed48f3b80700309178a7348dfd675ce7f88b2e
  - AI Agent Tools run 29490967167 passed on c3ed48f3b80700309178a7348dfd675ce7f88b2e
  - Ownership run 29490967139 failed only because the checkpoint was intentionally stale during implementation and is corrected by this checkpoint update
blockers: []
next_action: Run all required checks on the new exact head, then set the task to ready and mark PR 424 ready only if the changed-file diff remains clean.
```

# Completion

- Final status: implementing
- Canary PR: #424
- Catalogue updated: yes
- Changelog updated: yes
- Archived at: not archived
