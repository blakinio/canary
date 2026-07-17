---
task_id: CAN-20260717-otbm-tile-materializer
program_id: "OTS-OTBM-VALIDATION"
coordination_id: "OTS-OTBM-VALIDATION"
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/otbm-tile-materializer
base_branch: main
created: 2026-07-17T09:50:00+02:00
updated: 2026-07-17T09:50:00+02:00
last_verified_commit: ""
risk: high
related_issue: ""
related_pr: ""
depends_on:
  - "OTBM World Index #219"
  - "Semantic OTBM Diff #311"
  - "Phase 8 bounded attribute patcher #325"
  - "OTBM bounded tile-area materializer #426"
  - "OTBM repair/materialization pipeline #456"
blocks:
  - "future same-coordinate tile insertion/deletion"
  - "future arbitrary item stack editing"
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_area_materializer_scan.cpp
    - tools/ai-agent/otbm_tile_materializer.py
    - tools/ai-agent/otbm_tile_materializer_tool.py
    - tools/ai-agent/test_otbm_tile_materializer.py
    - docs/ai-agent/OTBM_TILE_MATERIALIZER.md
    - docs/ai-agent/OTBM_TILE_SPANS.schema.json
    - docs/ai-agent/OTBM_TILE_MATERIALIZATION_APPROVAL.schema.json
    - docs/ai-agent/OTBM_TILE_MATERIALIZATION_RESULT.schema.json
    - docs/agents/decisions/ADR-20260717-otbm-raw-tile-replacement-boundary.md
    - docs/agents/tasks/active/CAN-20260717-otbm-tile-materializer.md
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/ai-agent/otbm_item_audit_scan.cpp
    - tools/ai-agent/otbm_area_materializer.py
    - tools/ai-agent/otbm_world_index.py
    - tools/ai-agent/otbm_semantic_diff.py
    - tools/ai-agent/otbm_repair_materialization_pipeline.py
modules_touched:
  - OTBM bounded raw tile materializer
reuses:
  - native OTBM scanner physical framing
  - bounded TILE_AREA materializer scanner wrapper
  - canonical World Index
  - Semantic OTBM Diff
public_interfaces:
  - canary-otbm-tile-spans-v1
  - canary-otbm-tile-materialization-approval-v1
  - canary-otbm-tile-materialization-result-v1
cross_repo_tasks: []
---

# Goal

Implement the smallest safe tile-level structural OTBM write boundary: replace one or more already-existing current `OTBM_TILE`/`OTBM_HOUSETILE` subtrees with complete raw donor tile subtrees at the exact same absolute positions and the exact same parent `TILE_AREA` key, writing only a distinct output copy. Do not insert or delete tiles, translate coordinates, edit item stacks, serialize arbitrary nodes, or modify a source map in place.

# Acceptance criteria

- [ ] Add a new ADR for same-coordinate complete raw tile replacement and explicit deferred structural cases.
- [ ] Extend the existing native area-materializer scanner wrapper with deterministic physical tile-span evidence after the canonical scanner accepts the full map; do not add another parser.
- [ ] Require current and donor maps to have compatible OTBM/items headers and zero unknown attribute tails.
- [ ] Require every selected absolute position to exist exactly once in both current and donor maps and under the exact same `TILE_AREA` base key.
- [ ] Require a separate approval manifest pinning exact current/donor map SHA-256, World Index/manifests, selected positions, expected current raw tile SHA-256, expected donor raw tile SHA-256, and a non-empty rationale.
- [ ] Replace only complete raw tile subtrees; no insertion, deletion, coordinate translation, tile reordering policy, item stack editing, or arbitrary node serialization.
- [ ] Preserve every non-selected current byte exactly after excluding selected current/output tile spans.
- [ ] Require every selected output raw tile subtree to equal the donor subtree byte-for-byte.
- [ ] Reparse the candidate, rebuild canonical World Index, prove selected canonical output tiles equal donor, and run bounded Semantic Diff over the minimal selected bounding box before publication.
- [ ] Keep source maps/scanner immutable by pre/post stat+SHA pins and publish output/evidence with create-new, artifact-root-confined semantics only.
- [ ] Emit versioned tile-span, approval, and result contracts with truthful rollback and non-claims.
- [ ] Add deterministic native-scanner integration tests on synthetic fixtures; commit no `.otbm`, `.widx`, generated reports, renders, or private assets.
- [ ] Integrate shared catalogue/changelog only after resolving current overlap with PR #462 and require exact-final-head required checks before squash merge.

# Confirmed context

- Writable repository is exactly `blakinio/canary`; all `opentibiabr/*` repositories remain read-only.
- Existing Phase 8 fixed-width attribute patching is not expanded.
- Existing TILE_AREA materialization remains unchanged and is reused as the scanner-extension foundation.
- Open PR audit found no OTBM path overlap. PR #462 currently overlaps only the shared `docs/agents/MODULE_CATALOG.md` and `docs/agents/CHANGELOG.md` paths; those shared edits are deferred until final synchronization.
- Physical-client E2E is not required for this structural-confinement slice and no gameplay-correctness claim will be made.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T09:50:00+02:00
head: ""
branch: feat/otbm-tile-materializer
pr: ""
status: implementing
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - tools/ai-agent/otbm_area_materializer_scan.cpp
  - tools/ai-agent/otbm_tile_materializer.py
  - tools/ai-agent/otbm_tile_materializer_tool.py
  - tools/ai-agent/test_otbm_tile_materializer.py
  - docs/ai-agent/OTBM_TILE_MATERIALIZER.md
  - docs/ai-agent/OTBM_TILE_SPANS.schema.json
  - docs/ai-agent/OTBM_TILE_MATERIALIZATION_APPROVAL.schema.json
  - docs/ai-agent/OTBM_TILE_MATERIALIZATION_RESULT.schema.json
  - docs/agents/decisions/ADR-20260717-otbm-raw-tile-replacement-boundary.md
  - docs/agents/tasks/active/CAN-20260717-otbm-tile-materializer.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - existing TILE_AREA materializer is raw-subtree based and does not serialize arbitrary OTBM nodes
  - existing native scanner already validates tile structure and exposes absolute tile positions through canonical scan semantics
  - current continuation boundary explicitly defers partial-area/tile-level structural merge to a future ADR and bounded task
  - no open PR owns the planned OTBM implementation paths
  - PR #462 overlaps only the two shared agent index paths planned for late integration
unknown: []
conflicts: []
rejected_hypotheses:
  - full-map serializer
  - second OTBM parser
  - non-zero translation
  - tile insertion or deletion in v1
  - arbitrary item insertion deletion or stack reordering in v1
  - in-place source mutation
validation: []
blockers: []
next_action: Open an early draft PR, then implement the scanner tile-span mode and bounded raw same-position tile replacement on the task branch.
```
