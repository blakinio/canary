---
task_id: CAN-20260717-otbm-tile-type-conversion
program_id: "OTS-OTBM-VALIDATION"
coordination_id: "OTS-OTBM-VALIDATION"
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/otbm-tile-type-conversion
base_branch: main
created: 2026-07-17T19:53:00+02:00
updated: 2026-07-17T19:53:00+02:00
last_verified_commit: "250640758bec48946f31f34c85995632d194fbd0"
risk: high
related_issue: ""
related_pr: ""
depends_on:
  - "OTBM bounded raw tile materializer #467"
  - "OTBM bounded raw tile insertion #482"
  - "OTBM bounded raw tile deletion #488"
  - "OTBM World Index #219"
  - "Semantic OTBM Diff #311"
blocks:
  - "future structural operation pipeline integration"
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_tile_type_conversion_materializer.py
    - tools/ai-agent/otbm_tile_type_conversion_materializer_tool.py
    - tools/ai-agent/test_otbm_tile_type_conversion_materializer.py
    - docs/ai-agent/OTBM_TILE_TYPE_CONVERSION_MATERIALIZER.md
    - docs/ai-agent/OTBM_TILE_TYPE_CONVERSION_APPROVAL.schema.json
    - docs/ai-agent/OTBM_TILE_TYPE_CONVERSION_RESULT.schema.json
    - docs/agents/decisions/ADR-20260717-otbm-raw-tile-type-conversion-boundary.md
    - docs/agents/tasks/active/CAN-20260717-otbm-tile-type-conversion.md
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
---

# Goal

Implement the next smallest structural OTBM write boundary: convert an already-existing complete raw `OTBM_TILE` subtree to `OTBM_HOUSETILE`, or vice versa, only by replacing that complete current subtree with a separately approved complete donor subtree at the exact same absolute position and canonical parent `TILE_AREA`.

# Acceptance criteria

- [ ] Add an ADR limiting v1 to exact same-coordinate complete raw tile-node type conversion only.
- [ ] Reuse the existing tile-span scanner and complete raw tile replacement writer; add no parser, scanner mode, generic serializer, or item-stack writer.
- [ ] Require every selected position to exist exactly once in current and donor maps under the same canonical parent `TILE_AREA`.
- [ ] Require current and donor node types to be different and limited to `OTBM_TILE` (5) and `OTBM_HOUSETILE` (14).
- [ ] Require separate SHA-pinned approval for current/donor maps, indexes, manifests, exact raw subtrees and canonical World Index tiles.
- [ ] Prove non-selected current bytes are preserved exactly and selected output raw subtrees equal donor byte-for-byte.
- [ ] Reparse output, rebuild World Index, prove selected canonical output tiles equal donor, and run bounded Semantic OTBM Diff.
- [ ] Keep source maps/scanner immutable and publish output/evidence create-new under artifact root.
- [ ] Add deterministic synthetic conversion tests in both directions plus stale/same-type rejection coverage.
- [ ] Commit no maps, `.widx`, generated evidence, renders, client assets or private artifacts.
- [ ] Pass exact-final-head ownership, OTBM Map Tools, AI Agent Tools and full final-gate CI before squash merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T19:53:00+02:00
head: 250640758bec48946f31f34c85995632d194fbd0
branch: feat/otbm-tile-type-conversion
pr: pending
status: implementing
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
  - docs/agents/tasks/active/CAN-20260717-otbm-tile-type-conversion.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - bounded same-coordinate complete raw tile replacement is merged and archived
  - bounded same-coordinate complete raw tile insertion is merged and archived
  - bounded same-coordinate complete raw tile deletion is merged and archived
  - existing replacement writer already proves retained-current-byte equality and donor raw-subtree equality
  - open PR search found no competing OTBM tile type conversion work
  - no new parser scanner mode or arbitrary serializer is required for type conversion because the complete donor raw subtree already carries the target node type and house metadata

derived:
  - the smallest safe conversion boundary is a constrained complete-subtree replacement with the inverse node-type predicate from replacement v1
unknown:
  - exact final CI evidence for the new conversion boundary
conflicts: []
first_failure: null
rejected_hypotheses:
  - editing the node-type byte in place
  - synthesizing house identifiers or house metadata
  - item-level conversion
  - generic OTBM serialization
changed_paths:
  - docs/agents/tasks/active/CAN-20260717-otbm-tile-type-conversion.md
validation: []
blockers: []
next_action: Open the draft PR, implement the bounded conversion by reusing existing scanner/writer/index/diff helpers, then validate through repository CI.
```
