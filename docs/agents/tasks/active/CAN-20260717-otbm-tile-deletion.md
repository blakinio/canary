---
task_id: CAN-20260717-otbm-tile-deletion
program_id: "OTS-OTBM-VALIDATION"
coordination_id: "OTS-OTBM-VALIDATION"
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/otbm-tile-deletion
base_branch: main
created: 2026-07-17T16:15:00+02:00
updated: 2026-07-17T16:15:00+02:00
last_verified_commit: "4154d43a5b89ddc067569fde6d70f3d2c1e1e320"
risk: high
related_issue: ""
related_pr: ""
depends_on:
  - "OTBM bounded raw tile materializer #467"
  - "OTBM bounded raw tile insertion #482"
  - "OTBM World Index #219"
  - "Semantic OTBM Diff #311"
blocks:
  - "future raw tile type conversion"
  - "future structural operation pipeline integration"
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_tile_deletion_materializer.py
    - tools/ai-agent/otbm_tile_deletion_materializer_tool.py
    - tools/ai-agent/test_otbm_tile_deletion_materializer.py
    - docs/ai-agent/OTBM_TILE_DELETION_MATERIALIZER.md
    - docs/ai-agent/OTBM_TILE_DELETION_APPROVAL.schema.json
    - docs/ai-agent/OTBM_TILE_DELETION_RESULT.schema.json
    - docs/agents/decisions/ADR-20260717-otbm-raw-tile-deletion-boundary.md
    - docs/agents/tasks/active/CAN-20260717-otbm-tile-deletion.md
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/ai-agent/otbm_area_materializer_scan.cpp
    - tools/ai-agent/otbm_area_materializer.py
    - tools/ai-agent/otbm_tile_materializer.py
    - tools/ai-agent/otbm_tile_insertion_materializer.py
    - tools/ai-agent/otbm_world_index.py
    - tools/ai-agent/otbm_semantic_diff.py
modules_touched:
  - OTBM bounded raw tile deletion materializer
reuses:
  - existing native structural scanner and tile-span mode
  - existing raw tile span helpers
  - existing materialization source/publish safety helpers
  - canonical World Index
  - Semantic OTBM Diff
public_interfaces:
  - canary-otbm-tile-deletion-approval-v1
  - canary-otbm-tile-deletion-result-v1
cross_repo_tasks: []
---

# Goal

Implement the smallest safe raw OTBM deletion boundary: remove one or more already-existing complete `OTBM_TILE`/`OTBM_HOUSETILE` raw subtrees at exact approved absolute positions from a distinct current-map copy, leaving the existing parent `TILE_AREA` node in place.

# Acceptance criteria

- [ ] Add an ADR limiting v1 to complete existing tile deletion only; no TILE_AREA deletion, insertion, replacement, translation, type conversion, item-level editing, arbitrary serialization, or in-place source mutation.
- [ ] Reuse the existing raw tile-span scanner and materialization safety helpers; add no parser or scanner mode.
- [ ] Require each selected position to exist exactly once in current raw spans and current World Index under its canonical parent area.
- [ ] Require a separate approval pinning the current map, current World Index/manifest, selected position/area key, exact current raw tile SHA-256/length/node type and canonical World Index tile SHA-256.
- [ ] Remove only complete selected scanner-proven raw tile spans.
- [ ] Prove the output equals current with exactly the approved selected spans removed, byte-for-byte and byte-count exact.
- [ ] Reparse output, rebuild World Index, prove all selected positions are absent, and run bounded Semantic OTBM Diff.
- [ ] Allow the existing parent TILE_AREA to become empty but never remove or synthesize the parent area in v1.
- [ ] Keep current map/scanner immutable and publish output/evidence create-new under artifact root.
- [ ] Add deterministic synthetic native-scanner integration tests, schemas and documentation; commit no maps, indexes, evidence, renders, assets or private artifacts.
- [ ] Pass exact-final-head ownership, OTBM Map Tools, AI Agent Tools and Ready-triggered full final-gate CI before squash merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T16:15:00+02:00
head: 4154d43a5b89ddc067569fde6d70f3d2c1e1e320
branch: feat/otbm-tile-deletion
pr: ""
status: implementing
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - tools/ai-agent/otbm_tile_deletion_materializer.py
  - tools/ai-agent/otbm_tile_deletion_materializer_tool.py
  - tools/ai-agent/test_otbm_tile_deletion_materializer.py
  - docs/ai-agent/OTBM_TILE_DELETION_MATERIALIZER.md
  - docs/ai-agent/OTBM_TILE_DELETION_APPROVAL.schema.json
  - docs/ai-agent/OTBM_TILE_DELETION_RESULT.schema.json
  - docs/agents/decisions/ADR-20260717-otbm-raw-tile-deletion-boundary.md
  - docs/agents/tasks/active/CAN-20260717-otbm-tile-deletion.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - PR 482 completed bounded same-coordinate insertion and was archived through lifecycle PR 486
  - existing scanner tile spans already provide exact complete raw tile deletion boundaries after canonical map acceptance
  - current World Index and Semantic Diff provide canonical absence and bounded semantic verification
  - no open OTBM PR overlaps this scope
  - open PR 481 and PR 453 are unrelated and will not be modified
derived:
  - deletion requires no donor because the approved current raw and canonical state is the complete reviewed deletion target
  - output equality can be proven by hashing current while excluding selected spans and comparing that retained sequence to the complete output
  - keeping the parent TILE_AREA preserves a narrow boundary and avoids parent-area structural deletion semantics
unknown:
  - exact first CI failures if any after implementation publication
conflicts: []
first_failure:
  marker: none
  evidence: no implementation failure observed yet
rejected_hypotheses:
  - build another OTBM parser or scanner mode
  - delete parent TILE_AREA when its last tile is removed
  - combine deletion with insertion replacement translation or type conversion
  - perform item-level structural deletion
changed_paths:
  - docs/agents/tasks/active/CAN-20260717-otbm-tile-deletion.md
validation: []
blockers: []
next_action: Open a draft PR, then add the bounded ADR, deletion writer, approval/result schemas, documentation and native-scanner integration tests.
```
