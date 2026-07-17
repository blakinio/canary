---
task_id: CAN-20260717-otbm-tile-insertion
program_id: "OTS-OTBM-VALIDATION"
coordination_id: "OTS-OTBM-VALIDATION"
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/otbm-tile-insertion
base_branch: main
created: 2026-07-17T15:15:00+02:00
updated: 2026-07-17T15:31:00+02:00
last_verified_commit: "48c8a0bea9f1b05fb0d1e409297e90400660c299"
risk: high
related_issue: ""
related_pr: "482"
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

- [x] Add an ADR that limits v1 to same-coordinate insertion into an already-existing current TILE_AREA; no TILE_AREA creation, tile deletion, translation, item-level serialization, or in-place mutation.
- [x] Reuse existing tile-area and tile span scanners; do not add another parser or scanner mode.
- [x] Require selected position absent in current and present exactly once in donor.
- [x] Require the canonical target TILE_AREA to exist exactly once in current and pin its reviewed raw SHA-256/byte length in approval.
- [x] Require donor raw tile and canonical World Index tile hashes in approval.
- [x] Insert complete donor raw tile subtrees immediately before the physical `NODE_END` of their existing current TILE_AREA parent, with deterministic position order for multiple inserts into the same area.
- [x] Prove the output with inserted spans removed is byte-for-byte identical to the complete current map.
- [x] Prove each inserted output raw tile equals donor byte-for-byte.
- [x] Reparse output, rebuild World Index, prove inserted canonical tiles equal donor, and run bounded Semantic OTBM Diff.
- [x] Keep source maps/scanner immutable and publish output/evidence create-new under artifact root.
- [x] Add deterministic synthetic integration tests, schemas and documentation; commit no maps, World Index files, generated evidence, renders, or private assets.
- [ ] Pass exact-final-head ownership, OTBM Map Tools, AI Agent Tools and full final-gate CI before squash merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T15:31:00+02:00
head: 48c8a0bea9f1b05fb0d1e409297e90400660c299
branch: feat/otbm-tile-insertion
pr: 482
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
  - no open OTBM PR overlapped this scope when PR 482 was opened
  - insertion v1 copies complete donor raw tile subtrees before the existing scanner-proven parent TILE_AREA NODE_END and never serializes a tile independently
  - selected positions must be absent in current tile spans and current World Index and exist exactly once in donor
  - selected current parent TILE_AREA raw hash/length and donor raw/canonical tile state are approval-pinned
  - output retained-byte proof removes only inserted spans and requires the remaining byte sequence to equal the complete current map SHA-256 and byte count
  - candidate publication requires native reparse rebuilt World Index inserted canonical donor equality and bounded Semantic Diff
  - OTBM Map Tools run 29583988676 passed on 48c8a0bea9f1b05fb0d1e409297e90400660c299
  - AI Agent Tools run 29583988723 passed on 48c8a0bea9f1b05fb0d1e409297e90400660c299
  - CI run 29583989208 passed on 48c8a0bea9f1b05fb0d1e409297e90400660c299
  - open PR 481 is Universal E2E movement work and does not overlap OTBM paths
  - open PR 453 is unrelated security documentation and was not touched
derived:
  - deterministic grouping by parent area and position avoids reordering any existing current child
  - a missing tile may be inserted as ordinary or house type without constituting type conversion because no current tile exists at that position
unknown:
  - exact final-head gate results after shared catalogue/changelog and final checkpoint integration
conflicts: []
first_failure:
  marker: world-index-empty-map-fixture-depth
  evidence: OTBM Map Tools run 29583718767 failed three new tests because synthetic current fixtures had no child-item depth anywhere, exposing the existing scanner maxItemDepth=-1 versus binary-index 0 fixture edge; tests were corrected by adding an unrelated support TILE_AREA with a child item, without changing materializer logic
rejected_hypotheses:
  - build a second OTBM parser
  - modify the native scanner when existing area/tile span modes already provide required boundaries
  - create missing TILE_AREA parents in insertion v1
  - serialize a tile from canonical World Index data instead of copying reviewed donor raw bytes
  - combine insertion with deletion, translation, type conversion, or item-stack editing in one writer version
changed_paths:
  - docs/agents/decisions/ADR-20260717-otbm-raw-tile-insertion-boundary.md
  - docs/agents/tasks/active/CAN-20260717-otbm-tile-insertion.md
  - docs/ai-agent/OTBM_TILE_INSERTION_APPROVAL.schema.json
  - docs/ai-agent/OTBM_TILE_INSERTION_MATERIALIZER.md
  - docs/ai-agent/OTBM_TILE_INSERTION_RESULT.schema.json
  - tools/ai-agent/otbm_tile_insertion_materializer.py
  - tools/ai-agent/otbm_tile_insertion_materializer_tool.py
  - tools/ai-agent/test_otbm_tile_insertion_materializer.py
validation:
  - command: OTBM Map Tools run 29583718767
    result: FAIL
    evidence: initial synthetic empty-area fixtures exposed existing World Index maxItemDepth normalization edge; no production writer path failed
  - command: OTBM Map Tools run 29583988676
    result: PASS
    evidence: all focused OTBM tests and schema validation passed after fixture correction on head 48c8a0bea9f1b05fb0d1e409297e90400660c299
  - command: AI Agent Tools run 29583988723
    result: PASS
    evidence: AI agent tool suite passed on head 48c8a0bea9f1b05fb0d1e409297e90400660c299
  - command: CI run 29583989208
    result: PASS
    evidence: repository CI passed on head 48c8a0bea9f1b05fb0d1e409297e90400660c299
blockers: []
next_action: Integrate the reusable module catalogue and changelog narrowly, apply ci:final-gate, write the final checkpoint commit, then require exact-final-head ownership, OTBM Map Tools, AI Agent Tools and full CI before squash merge.
```
