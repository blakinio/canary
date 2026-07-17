---
task_id: CAN-20260717-otbm-tile-type-conversion
program_id: "OTS-OTBM-VALIDATION"
coordination_id: "OTS-OTBM-VALIDATION"
status: completed
agent: "GPT-5.5 Thinking"
branch: feat/otbm-tile-type-conversion
base_branch: main
created: 2026-07-17T19:53:00+02:00
updated: 2026-07-17T20:55:00+02:00
last_verified_commit: "49a344f2cdb3d8dc72f6607f72ab091b311d12eb"
risk: high
related_issue: ""
related_pr: "498"
depends_on:
  - "OTBM bounded raw tile materializer #467"
  - "OTBM bounded raw tile insertion #482"
  - "OTBM bounded raw tile deletion #488"
  - "OTBM World Index #219"
  - "Semantic OTBM Diff #311"
blocks: []
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_tile_type_conversion_materializer.py
    - tools/ai-agent/otbm_tile_type_conversion_materializer_tool.py
    - tools/ai-agent/test_otbm_tile_type_conversion_materializer.py
    - docs/ai-agent/OTBM_TILE_TYPE_CONVERSION_MATERIALIZER.md
    - docs/ai-agent/OTBM_TILE_TYPE_CONVERSION_APPROVAL.schema.json
    - docs/ai-agent/OTBM_TILE_TYPE_CONVERSION_RESULT.schema.json
    - docs/agents/decisions/ADR-20260717-otbm-raw-tile-type-conversion-boundary.md
    - docs/agents/tasks/archive/CAN-20260717-otbm-tile-type-conversion.md
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/ai-agent/otbm_area_materializer_scan.cpp
    - tools/ai-agent/otbm_tile_materializer.py
    - tools/ai-agent/otbm_tile_insertion_materializer.py
    - tools/ai-agent/otbm_tile_deletion_materializer.py
    - tools/ai-agent/otbm_world_index.py
    - tools/ai-agent/otbm_semantic_diff.py
modules_touched:
  - OTBM bounded raw tile type conversion materializer
reuses:
  - existing native structural scanner and tile-span mode
  - existing complete raw tile replacement byte writer
  - existing materialization source and publication safety helpers
  - canonical World Index
  - Semantic OTBM Diff
public_interfaces:
  - canary-otbm-tile-type-conversion-approval-v1
  - canary-otbm-tile-type-conversion-result-v1
cross_repo_tasks: []
completed: 2026-07-17T20:55:00+02:00
---

# Goal

Implement the bounded structural OTBM write boundary for converting an existing complete raw `OTBM_TILE` subtree to `OTBM_HOUSETILE`, or vice versa, only by replacing that complete current subtree with a separately approved complete donor subtree at the exact same absolute position and canonical parent `TILE_AREA`.

# Acceptance criteria

- [x] ADR limits v1 to exact same-coordinate complete raw tile-node type conversion.
- [x] Existing tile-span scanner and complete raw tile replacement writer are reused; no parser, scanner mode, generic serializer, or item-stack writer was added.
- [x] Every selected position must exist exactly once in current and donor maps under the same canonical parent `TILE_AREA`.
- [x] Current and donor node types must differ and be limited to `OTBM_TILE` (5) and `OTBM_HOUSETILE` (14).
- [x] Separate SHA-pinned approval covers maps, indexes, manifests, exact raw subtrees and canonical World Index tiles.
- [x] Non-selected current bytes are preserved exactly and selected output raw subtrees equal donor byte-for-byte.
- [x] Output is reparsed, World Index rebuilt, selected canonical output tiles proven equal to donor, and bounded Semantic OTBM Diff produced.
- [x] Source maps/scanner remain immutable and output/evidence use create-new publication below the artifact root.
- [x] Deterministic tests cover both conversion directions plus same-type and stale-raw rejection.
- [x] No maps, `.widx`, generated evidence, renders, client assets or private artifacts were committed.
- [x] Exact-final-head Ownership, OTBM Map Tools, AI Agent Tools and full ready-triggered final-gate CI passed before squash merge.
- [x] Feature PR #498 squash merged with expected-head protection.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T20:55:00+02:00
head: 49a344f2cdb3d8dc72f6607f72ab091b311d12eb
branch: feat/otbm-tile-type-conversion
pr: 498
status: completed
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - tools/ai-agent/otbm_tile_type_conversion_materializer.py
  - tools/ai-agent/otbm_tile_type_conversion_materializer_tool.py
  - tools/ai-agent/test_otbm_tile_type_conversion_materializer.py
  - docs/ai-agent/OTBM_TILE_TYPE_CONVERSION_MATERIALIZER.md
  - docs/ai-agent/OTBM_TILE_TYPE_CONVERSION_APPROVAL.schema.json
  - docs/ai-agent/OTBM_TILE_TYPE_CONVERSION_RESULT.schema.json
  - docs/agents/decisions/ADR-20260717-otbm-raw-tile-type-conversion-boundary.md
  - docs/agents/tasks/archive/CAN-20260717-otbm-tile-type-conversion.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - bounded same-coordinate raw tile replacement insertion and deletion were already merged and archived
  - conversion reuses the existing complete raw tile replacement writer and canonical scanner World Index and Semantic Diff
  - exact final feature head 49a344f2cdb3d8dc72f6607f72ab091b311d12eb passed Agent Task Ownership run 29603711591
  - exact final feature head 49a344f2cdb3d8dc72f6607f72ab091b311d12eb passed OTBM Map Tools run 29603711584
  - exact final feature head 49a344f2cdb3d8dc72f6607f72ab091b311d12eb passed AI Agent Tools run 29603711599
  - exact final feature head 49a344f2cdb3d8dc72f6607f72ab091b311d12eb passed CI run 29603711787
  - ready-triggered full final-gate CI run 29603821692 passed on the same exact final head
  - PR 498 squash merged as 008fe64b1f6494a1ba87cac8d4bb86581dec6456
  - no physical-client E2E was required because this feature proves bounded structural materialization only and explicitly makes no gameplay correctness claim
derived:
  - complete approved donor-subtree replacement is the smallest safe type-conversion boundary because TILE and HOUSETILE property layouts differ
  - no generic OTBM serializer or synthetic house-ID allocation is necessary for this bounded operation
unknown: []
conflicts: []
first_failure:
  marker: active-task-status
  evidence: an earlier final-gate candidate failed Ownership only because the task under tasks/active used status validating; the corrected exact final head passed all required gates
rejected_hypotheses:
  - editing only the raw node-type byte
  - synthesizing house identifiers or metadata
  - item-level conversion
  - generic OTBM serialization
  - merging while exact-final-head Ownership was red
changed_paths:
  - docs/agents/CHANGELOG.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/decisions/ADR-20260717-otbm-raw-tile-type-conversion-boundary.md
  - docs/agents/tasks/active/CAN-20260717-otbm-tile-type-conversion.md
  - docs/ai-agent/OTBM_TILE_TYPE_CONVERSION_APPROVAL.schema.json
  - docs/ai-agent/OTBM_TILE_TYPE_CONVERSION_MATERIALIZER.md
  - docs/ai-agent/OTBM_TILE_TYPE_CONVERSION_RESULT.schema.json
  - tools/ai-agent/otbm_tile_type_conversion_materializer.py
  - tools/ai-agent/otbm_tile_type_conversion_materializer_tool.py
  - tools/ai-agent/test_otbm_tile_type_conversion_materializer.py
validation:
  - command: Agent Task Ownership run 29603711591
    result: PASS
    evidence: exact final feature head
  - command: OTBM Map Tools run 29603711584
    result: PASS
    evidence: exact final feature head
  - command: AI Agent Tools run 29603711599
    result: PASS
    evidence: exact final feature head
  - command: CI run 29603711787
    result: PASS
    evidence: exact final feature head
  - command: ready-triggered full CI run 29603821692
    result: PASS
    evidence: exact final feature head
  - command: squash merge PR 498
    result: PASS
    evidence: merge commit 008fe64b1f6494a1ba87cac8d4bb86581dec6456
blockers: []
next_action: none
```

## Lifecycle completion

- Feature PR: #498.
- Exact final feature head: `49a344f2cdb3d8dc72f6607f72ab091b311d12eb`.
- Feature merge commit: `008fe64b1f6494a1ba87cac8d4bb86581dec6456`.
- Required exact-head runs: Ownership `29603711591`, OTBM Map Tools `29603711584`, AI Agent Tools `29603711599`, CI `29603711787`, ready-triggered full CI `29603821692`.
- Physical-client E2E: not required for this structural-only boundary.
