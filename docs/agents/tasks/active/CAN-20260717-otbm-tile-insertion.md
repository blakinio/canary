---
task_id: CAN-20260717-otbm-tile-insertion
program_id: "OTS-OTBM-VALIDATION"
coordination_id: "OTS-OTBM-VALIDATION"
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/otbm-tile-insertion
base_branch: main
created: 2026-07-17T15:15:00+02:00
updated: 2026-07-17T15:15:00+02:00
last_verified_commit: "9bb6ffe2941a447eff4166cecc714992db166d93"
risk: high
related_issue: ""
related_pr: ""
depends_on:
  - "OTBM bounded raw tile materializer #467"
  - "OTBM bounded tile-area materializer #426"
  - "OTBM World Index #219"
  - "Semantic OTBM Diff #311"
blocks:
  - "future same-coordinate tile deletion"
  - "future raw tile type conversion"
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_tile_insertion_materializer.py
    - tools/ai-agent/otbm_tile_insertion_materializer_tool.py
    - tools/ai-agent/test_otbm_tile_insertion_materializer.py
    - docs/ai-agent/OTBM_TILE_INSERTION_MATERIALIZER.md
    - docs/ai-agent/OTBM_TILE_INSERTION_APPROVAL.schema.json
    - docs/ai-agent/OTBM_TILE_INSERTION_RESULT.schema.json
    - docs/agents/decisions/ADR-20260717-otbm-raw-tile-insertion-boundary.md
    - docs/agents/tasks/active/CAN-20260717-otbm-tile-insertion.md
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/ai-agent/otbm_area_materializer_scan.cpp
    - tools/ai-agent/otbm_area_materializer.py
    - tools/ai-agent/otbm_tile_materializer.py
    - tools/ai-agent/otbm_world_index.py
    - tools/ai-agent/otbm_semantic_diff.py
modules_touched:
  - OTBM bounded raw tile insertion materializer
reuses:
  - existing native structural scanner and tile-span mode
  - existing normalized TILE_AREA span scanner
  - existing bounded raw tile replacement helpers
  - canonical World Index
  - Semantic OTBM Diff
public_interfaces:
  - canary-otbm-tile-insertion-approval-v1
  - canary-otbm-tile-insertion-result-v1
cross_repo_tasks: []
---

# Goal

Implement the next smallest structural OTBM write boundary: insert one or more complete donor `OTBM_TILE`/`OTBM_HOUSETILE` raw subtrees at exact same absolute coordinates into already-existing current `TILE_AREA` parents, only when the selected tile is absent from current and exists exactly once in donor. Write only a distinct output copy.

# Acceptance criteria

- [ ] Add an ADR that limits v1 to same-coordinate insertion into an already-existing current TILE_AREA; no TILE_AREA creation, tile deletion, translation, item-level serialization, or in-place mutation.
- [ ] Reuse existing tile-area and tile span scanners; do not add another parser or scanner mode.
- [ ] Require selected position absent in current and present exactly once in donor.
- [ ] Require the canonical target TILE_AREA to exist exactly once in current and pin its reviewed raw SHA-256/byte length in approval.
- [ ] Require donor raw tile and canonical World Index tile hashes in approval.
- [ ] Insert complete donor raw tile subtrees immediately before the physical `NODE_END` of their existing current TILE_AREA parent, with deterministic position order for multiple inserts into the same area.
- [ ] Prove the output with inserted spans removed is byte-for-byte identical to the complete current map.
- [ ] Prove each inserted output raw tile equals donor byte-for-byte.
- [ ] Reparse output, rebuild World Index, prove inserted canonical tiles equal donor, and run bounded Semantic OTBM Diff.
- [ ] Keep source maps/scanner immutable and publish output/evidence create-new under artifact root.
- [ ] Add deterministic synthetic integration tests, schemas and documentation; commit no maps, World Index files, generated evidence, renders, or private assets.
- [ ] Pass exact-final-head ownership, OTBM Map Tools, AI Agent Tools and full final-gate CI before squash merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T15:15:00+02:00
head: 9bb6ffe2941a447eff4166cecc714992db166d93
branch: feat/otbm-tile-insertion
pr: ""
status: implementing
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - tools/ai-agent/otbm_tile_insertion_materializer.py
  - tools/ai-agent/otbm_tile_insertion_materializer_tool.py
  - tools/ai-agent/test_otbm_tile_insertion_materializer.py
  - docs/ai-agent/OTBM_TILE_INSERTION_MATERIALIZER.md
  - docs/ai-agent/OTBM_TILE_INSERTION_APPROVAL.schema.json
  - docs/ai-agent/OTBM_TILE_INSERTION_RESULT.schema.json
  - docs/agents/decisions/ADR-20260717-otbm-raw-tile-insertion-boundary.md
  - docs/agents/tasks/active/CAN-20260717-otbm-tile-insertion.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - PR 467 completed exact same-coordinate complete raw tile replacement and deliberately deferred insertion/deletion
  - existing native scanner already exposes both TILE_AREA spans and tile spans after the canonical parser accepts the full map
  - current open PR audit found no OTBM PR overlapping this scope
  - no local checkout is available because container network cannot resolve github.com; connector-backed GitHub branch/PR/CI workflow is required
  - open PR 481 is Universal E2E movement work and does not overlap OTBM paths
  - open PR 453 is unrelated security documentation and will not be touched
derived:
  - insertion can preserve every current byte exactly by adding donor raw tile bytes immediately before the existing parent TILE_AREA NODE_END
  - output retained-byte proof can hash the output excluding inserted spans and compare it with the complete current map hash/count
  - deterministic grouping by area and position avoids reordering any existing current child
unknown:
  - exact first CI failures, if any, until implementation is published
conflicts: []
first_failure:
  marker: local-checkout-network-unavailable
  evidence: container git clone failed because github.com could not be resolved; no repository mutation was attempted outside blakinio/canary
rejected_hypotheses:
  - build a second OTBM parser
  - modify the native scanner when existing area/tile span modes already provide required boundaries
  - create missing TILE_AREA parents in insertion v1
  - serialize a tile from canonical World Index data instead of copying reviewed donor raw bytes
  - combine insertion with deletion, translation, type conversion, or item-stack editing in one writer version
changed_paths:
  - docs/agents/tasks/active/CAN-20260717-otbm-tile-insertion.md
validation: []
blockers: []
next_action: Open the draft PR, then add the bounded ADR, implementation, schemas, docs and deterministic tests on this branch.
```
