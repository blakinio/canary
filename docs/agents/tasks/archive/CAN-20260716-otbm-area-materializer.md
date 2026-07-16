---
task_id: CAN-20260716-otbm-area-materializer
program_id: "OTS-OTBM-VALIDATION"
coordination_id: "OTS-OTBM-VALIDATION"
status: completed
agent: "GPT-5.5 Thinking"
branch: feat/otbm-area-materializer
base_branch: main
created: 2026-07-16T13:20:00+02:00
updated: 2026-07-16T19:43:01Z
last_verified_commit: "851ae2fff3f371bcbc6b42f5f2b476300a7585ca"
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
    - tools/ai-agent/otbm_area_materializer_scan.cpp
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
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/ai-agent/otbm_item_audit_scan.cpp
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
completed: 2026-07-16T19:43:01Z
---

# Goal

Implement the smallest safe structural OTBM materialization boundary: copy, replace, or remove complete same-coordinate `OTBM_TILE_AREA` subtrees in a distinct current-map copy, using explicit reviewed approval and mandatory native reparse, World Index, and Semantic Diff evidence. Do not build a full-map serializer and do not broaden Phase 8.

# Acceptance criteria

- [x] Add an ADR for the raw complete-tile-area subtree boundary and explicit deferred cases.
- [x] Extend native scanner capability through a same-translation-unit wrapper that reuses the existing scanner implementation and emits deterministic direct-child tile-area physical spans; no second parser.
- [x] Require compatible current/donor map headers and zero translation.
- [x] Require full 256x256 tile-area-aligned selected regions and `replace-region` planning semantics.
- [x] Require a separate approval manifest pinned to the merge-plan SHA, exact approved area keys, and every non-blocking plan conflict.
- [x] Materialize only to create-new output/evidence paths under an artifact root; reject in-place, overwrite, symlink, path-escape, and source/output collisions.
- [x] Copy donor tile-area raw subtrees byte-for-byte and preserve all non-selected current bytes exactly.
- [x] Support replacement, insertion, and deletion of whole area subtrees without serializing unrelated OTBM nodes.
- [x] Fail closed on incomplete/ambiguous span evidence, duplicate selected area keys, unknown attribute tails, incompatible headers, truncated conflict evidence, or blocking planner conflicts.
- [x] Reparse the output with the native scanner, rebuild World Index, run bounded Semantic Diff, and verify selected output areas equal donor while retained bytes equal current.
- [x] Prove current map, donor map, and scanner SHA-256/stat identity unchanged before/after.
- [x] Emit versioned span, approval, and materialization-result contracts with rollback/source/output evidence.
- [x] Add real native-scanner integration tests on synthetic OTBM fixtures; no `.otbm`, `.widx`, reports, or assets committed.
- [x] Keep translated fragment import, tile-level overlay merging, and arbitrary node serialization outside v1.
- [x] Update catalogue/changelog narrowly and pass exact-head required checks before merge.

# Confirmed context

- Writable repository is exactly `blakinio/canary`; upstream/donor repositories are read-only.
- Task-start `main` is `368319e6e20672339a6409504d1a9f69c15ea077` after PR #424 and lifecycle PR #425.
- Phase 8 remains existing fixed-width attributes only and is not expanded.
- PR #316 remains Targuna-specific audit work and does not own this materializer's paths.
- Draft PR #426 targets `blakinio/canary:main` from `feat/otbm-area-materializer`.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T19:46:28+02:00
head: 74ce7f097137b55fdb65ff0254c9e72090cb80cb
branch: feat/otbm-area-materializer
pr: 426
status: ready
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - tools/ai-agent/otbm_area_materializer_scan.cpp
  - tools/ai-agent/otbm_area_materializer.py
  - tools/ai-agent/otbm_area_materializer_tool.py
  - tools/ai-agent/test_otbm_area_materializer.py
  - docs/ai-agent/OTBM_AREA_MATERIALIZER.md
  - docs/ai-agent/OTBM_TILE_AREA_SPANS.schema.json
  - docs/ai-agent/OTBM_AREA_MATERIALIZATION_APPROVAL.schema.json
  - docs/ai-agent/OTBM_AREA_MATERIALIZATION_RESULT.schema.json
  - docs/agents/decisions/ADR-20260716-otbm-raw-tile-area-materialization-boundary.md
  - docs/agents/tasks/active/CAN-20260716-otbm-area-materializer.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - extended native binary delegates existing scanner modes and adds only physical direct-child TILE_AREA span evidence after the existing full scanner accepts the map
  - v1 requires replace-region zero translation and complete 256x256 aligned tile areas
  - planner output remains non-executable and a separate SHA-pinned approval must cover every selected area and non-blocking conflict
  - selected donor raw subtrees are copied byte-for-byte and retained current byte streams are proven identical after excluding selected output spans
  - temporary output must pass native reparse, output span validation, selected-area World Index equality with donor, and bounded Semantic Diff before publication
  - real synthetic integration tests cover replacement insertion deletion source immutability nonzero-translation rejection incomplete approval rejection and partial-area rejection
  - MODULE_CATALOG patch contains exactly one new row for OTBM bounded tile-area materializer and no unrelated shared-file drift
  - CHANGELOG patch contains exactly one new Unreleased bullet for this feature
  - CI run 29495414284 passed on 74ce7f097137b55fdb65ff0254c9e72090cb80cb
  - Agent Task Ownership run 29495414189 passed on 74ce7f097137b55fdb65ff0254c9e72090cb80cb
  - OTBM Map Tools run 29495414037 passed on 74ce7f097137b55fdb65ff0254c9e72090cb80cb
  - AI Agent Tools run 29495414055 passed on 74ce7f097137b55fdb65ff0254c9e72090cb80cb
derived:
  - complete same-coordinate tile-area raw subtree materialization is the smallest structural write boundary that avoids a full serializer
unknown: []
conflicts: []
first_failure:
  marker: gcc13-included-scanner-maybe-uninitialized
  evidence: OTBM Map Tools run 29494613581 failed before materializer tests because GCC 13 emitted a maybe-uninitialized false positive inside the included existing writeWorldIndex implementation; a GCC-only diagnostic suppression was scoped strictly around the legacy scanner include and the subsequent focused run passed
rejected_hypotheses:
  - full-map serializer
  - arbitrary translated-region writing in v1
  - tile-level overlay merge in v1
  - in-place source-map mutation
  - executing writerReady false planner output without a separate approval
changed_paths:
  - docs/agents/CHANGELOG.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/decisions/ADR-20260716-otbm-raw-tile-area-materialization-boundary.md
  - docs/agents/tasks/active/CAN-20260716-otbm-area-materializer.md
  - docs/ai-agent/OTBM_AREA_MATERIALIZER.md
  - docs/ai-agent/OTBM_TILE_AREA_SPANS.schema.json
  - docs/ai-agent/OTBM_AREA_MATERIALIZATION_APPROVAL.schema.json
  - docs/ai-agent/OTBM_AREA_MATERIALIZATION_RESULT.schema.json
  - tools/ai-agent/otbm_area_materializer_scan.cpp
  - tools/ai-agent/otbm_area_materializer.py
  - tools/ai-agent/otbm_area_materializer_tool.py
  - tools/ai-agent/test_otbm_area_materializer.py
validation:
  - command: CI run 29495414284
    result: PASS
    evidence: repository CI passed on 74ce7f097137b55fdb65ff0254c9e72090cb80cb
  - command: Agent Task Ownership run 29495414189
    result: PASS
    evidence: task ownership validation passed on 74ce7f097137b55fdb65ff0254c9e72090cb80cb
  - command: OTBM Map Tools run 29495414037
    result: PASS
    evidence: schema validation and real native-scanner focused integration tests passed on 74ce7f097137b55fdb65ff0254c9e72090cb80cb
  - command: AI Agent Tools run 29495414055
    result: PASS
    evidence: repository AI-agent unit and content validation passed on 74ce7f097137b55fdb65ff0254c9e72090cb80cb
blockers: []
next_action: Let required checks run on the task-record readiness commit, then re-inspect the full PR changed-file list and diff and mark PR #426 ready only if the new exact head is green.
```

# Completion

- Final status: ready
- Canary PR: #426
- Catalogue updated: complete
- Changelog updated: complete
- Archived at: not archived

## Automated lifecycle completion

- Feature PR: #426.
- Feature head: `aa650000935862b4de748829768356a83d93f6c3`.
- Merge commit: `851ae2fff3f371bcbc6b42f5f2b476300a7585ca`.
- Merged at: `2026-07-16T19:43:01Z`.
- This record was moved from `tasks/active` by the post-merge lifecycle automation.
