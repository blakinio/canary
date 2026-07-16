---
task_id: CAN-20260716-otbm-area-materializer
program_id: "OTS-OTBM-VALIDATION"
coordination_id: "OTS-OTBM-VALIDATION"
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/otbm-area-materializer
base_branch: main
created: 2026-07-16T13:20:00+02:00
updated: 2026-07-16T13:25:00+02:00
last_verified_commit: "2c8e2c0593b7f9ae8d6314121e322bf69575aaa2"
risk: high
related_issue: ""
related_pr: "426"
depends_on:
  - "OTBM World Index #219"
  - "Semantic OTBM Diff #311"
  - "Phase 8 bounded attribute patcher #325"
  - "OTBM donor/region merge planner #424"
blocks:
  - "future translated structural region import"
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_area_materializer.py
    - tools/ai-agent/otbm_area_materializer_tool.py
    - tools/ai-agent/test_otbm_area_materializer.py
    - docs/ai-agent/OTBM_AREA_MATERIALIZER.md
    - docs/ai-agent/OTBM_TILE_AREA_SPANS.schema.json
    - docs/ai-agent/OTBM_AREA_MATERIALIZATION_APPROVAL.schema.json
    - docs/ai-agent/OTBM_AREA_MATERIALIZATION_RESULT.schema.json
    - docs/agents/decisions/ADR-20260716-otbm-raw-tile-area-materialization-boundary.md
    - docs/agents/tasks/active/CAN-20260716-otbm-area-materializer.md
  shared:
    - tools/ai-agent/otbm_item_audit_scan.cpp
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/ai-agent/otbm_region_merge_planner.py
    - tools/ai-agent/otbm_world_index.py
    - tools/ai-agent/otbm_semantic_diff.py
    - tools/ai-agent/otbm_bounded_patch.py
modules_touched:
  - OTBM bounded tile-area materializer
reuses:
  - native OTBM scanner physical framing
  - canonical World Index
  - Semantic OTBM Diff
  - donor/region merge plan v1
public_interfaces:
  - canary-otbm-tile-area-spans-v1
  - canary-otbm-area-materialization-approval-v1
  - canary-otbm-area-materialization-result-v1
cross_repo_tasks: []
---

# Goal

Implement the smallest safe structural OTBM materialization boundary: copy or replace complete same-coordinate `OTBM_TILE_AREA` subtrees from a donor map into a distinct current-map copy, using explicit reviewed approval and mandatory reparse/World Index/Semantic Diff evidence. Do not build a full-map serializer and do not broaden Phase 8.

# Acceptance criteria

- [ ] Add an ADR for the raw complete-tile-area subtree boundary and explicit deferred cases.
- [ ] Extend the existing native scanner with deterministic direct-child tile-area physical spans; no second parser.
- [ ] Require compatible current/donor map headers and zero translation.
- [ ] Require full 256x256 tile-area-aligned selected regions and `replace-region` planning semantics.
- [ ] Require a separate approval manifest pinned to the merge-plan SHA and exact approved area keys.
- [ ] Materialize only to a new path under an artifact root; reject in-place, overwrite, symlink and hardlink/source collisions.
- [ ] Copy donor tile-area raw subtrees byte-for-byte and preserve all non-selected current bytes exactly.
- [ ] Support replacement and insertion of whole area subtrees without serializing unrelated OTBM nodes.
- [ ] Fail closed on incomplete/ambiguous span evidence, duplicate selected area keys, unknown attribute tails, incompatible headers or planner conflicts not explicitly approved.
- [ ] Reparse the output with the native scanner, rebuild World Index, run Semantic Diff and verify output selected areas equal donor while retained areas equal current.
- [ ] Prove source and donor SHA-256 unchanged before/after.
- [ ] Emit a versioned evidence result with rollback/source/output pins.
- [ ] Add real native-scanner integration tests on synthetic OTBM fixtures; no `.otbm`, `.widx`, reports or assets committed.
- [ ] Keep translated fragment import, tile-level overlay merging and arbitrary node serialization outside v1.
- [ ] Update catalogue/changelog narrowly and pass exact-head required checks before merge.

# Confirmed context

- Writable repository is exactly `blakinio/canary`; upstream/donor repositories are read-only.
- Task-start `main` is `368319e6e20672339a6409504d1a9f69c15ea077` after PR #424 and lifecycle PR #425.
- Phase 8 remains existing fixed-width attributes only and is not expanded.
- Existing scanner already traverses physical OTBM node framing and preserves escape-aware physical byte offsets for bounded attributes.
- PR #316 remains Targuna-specific audit work and does not own the proposed materializer paths.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T13:25:00+02:00
head: 2c8e2c0593b7f9ae8d6314121e322bf69575aaa2
branch: feat/otbm-area-materializer
pr: 426
status: implementing
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - tools/ai-agent/otbm_area_materializer.py
  - tools/ai-agent/otbm_area_materializer_tool.py
  - tools/ai-agent/test_otbm_area_materializer.py
  - docs/ai-agent/OTBM_AREA_MATERIALIZER.md
  - docs/ai-agent/OTBM_TILE_AREA_SPANS.schema.json
  - docs/ai-agent/OTBM_AREA_MATERIALIZATION_APPROVAL.schema.json
  - docs/ai-agent/OTBM_AREA_MATERIALIZATION_RESULT.schema.json
  - docs/agents/decisions/ADR-20260716-otbm-raw-tile-area-materialization-boundary.md
  - docs/agents/tasks/active/CAN-20260716-otbm-area-materializer.md
  - tools/ai-agent/otbm_item_audit_scan.cpp
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - Phase 8 cannot be broadened into structural map writing
  - existing native scanner already parses OTBM physical node framing and direct OTBM_TILE_AREA ancestry
  - same-coordinate complete tile-area raw subtree copying avoids coordinate and teleport rewriting
  - task-start main includes merged region planner and archived lifecycle record
  - no open PR was found for a generic structural OTBM region writer or materializer
  - PR 316 remains separate Targuna-specific audit work
  - draft PR 426 targets blakinio/canary main from feat/otbm-area-materializer
derived:
  - complete same-coordinate tile-area replacement is the smallest structural materialization boundary that can avoid a full serializer
unknown:
  - exact scanner span-report fields and insertion-point invariant until implementation tests prove them
  - exact approval conflict-disposition shape until planner report adapter is implemented
conflicts: []
first_failure:
  marker: none-yet
  evidence: task initialized after clean #424/#425 lifecycle completion
rejected_hypotheses:
  - full-map serializer
  - arbitrary translated-region writing in v1
  - tile-level overlay merge in v1
  - in-place source-map mutation
changed_paths:
  - docs/agents/tasks/active/CAN-20260716-otbm-area-materializer.md
validation:
  - command: startup repository and lifecycle verification
    result: PASS
    evidence: main 368319e6e20672339a6409504d1a9f69c15ea077 includes merged PR 424 and lifecycle PR 425
blockers: []
next_action: Implement native direct-child tile-area span evidence, then prove raw subtree replacement and insertion invariants with synthetic integration tests.
```

# Completion

- Final status: implementing
- Canary PR: #426
- Catalogue updated: pending
- Changelog updated: pending
- Archived at: not archived
