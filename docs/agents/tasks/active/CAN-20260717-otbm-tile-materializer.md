---
task_id: CAN-20260717-otbm-tile-materializer
program_id: "OTS-OTBM-VALIDATION"
coordination_id: "OTS-OTBM-VALIDATION"
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/otbm-tile-materializer
base_branch: main
created: 2026-07-17T09:50:00+02:00
updated: 2026-07-17T10:06:00+02:00
last_verified_commit: "dc789cc76b877f4887833b8318e9ee7c983cbfaf"
risk: high
related_issue: ""
related_pr: "467"
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

- [x] Add a new ADR for same-coordinate complete raw tile replacement and explicit deferred structural cases.
- [x] Extend the existing native area-materializer scanner wrapper with deterministic physical tile-span evidence after the canonical scanner accepts the full map; do not add another parser.
- [x] Require current and donor maps to have compatible OTBM/items headers and zero unknown attribute tails.
- [x] Require every selected absolute position to exist exactly once in both current and donor maps and under the exact same `TILE_AREA` base key.
- [x] Require a separate approval manifest pinning exact current/donor map SHA-256, World Index/manifests, selected positions, expected current raw tile SHA-256, expected donor raw tile SHA-256, and a non-empty rationale.
- [x] Replace only complete raw tile subtrees; no insertion, deletion, coordinate translation, tile reordering policy, item stack editing, or arbitrary node serialization.
- [x] Preserve every non-selected current byte exactly after excluding selected current/output tile spans.
- [x] Require every selected output raw tile subtree to equal the donor subtree byte-for-byte.
- [x] Reparse the candidate, rebuild canonical World Index, prove selected canonical output tiles equal donor, and run bounded Semantic Diff over the minimal selected bounding box before publication.
- [x] Keep source maps/scanner immutable by pre/post stat+SHA pins and publish output/evidence with create-new, artifact-root-confined semantics only.
- [x] Emit versioned tile-span, approval, and result contracts with truthful rollback and non-claims.
- [x] Add deterministic native-scanner integration tests on synthetic fixtures; commit no `.otbm`, `.widx`, generated reports, renders, or private assets.
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
updated_at: 2026-07-17T10:06:00+02:00
head: dc789cc76b877f4887833b8318e9ee7c983cbfaf
branch: feat/otbm-tile-materializer
pr: 467
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
  - scanner wrapper now adds only physical direct-child tile span evidence after the existing full scanner accepts the map and delegates all existing scanner modes unchanged
  - materializer v1 is replacement-only and requires exact same absolute position canonical parent TILE_AREA and node type on current and donor
  - approval pins current and donor map World Index manifest plus exact raw and canonical state for every selected tile
  - candidate publication is blocked until retained-byte equality donor raw equality native reparse output World Index selected canonical equality and bounded Semantic Diff complete
  - schema JSON validation step passed on head dc789cc76b877f4887833b8318e9ee7c983cbfaf
  - synthetic integration tests cover scanner span evidence single replacement multiple shifted-length replacements missing donor stale expected state and tile/house type mismatch
  - Agent Task Ownership run 29565114577 found only missing checkpoint metadata fields in this task record before this checkpoint update

derived:
  - complete same-coordinate raw tile replacement is the smallest structural boundary below TILE_AREA replacement that avoids tile insertion deletion item-stack editing and arbitrary serialization
  - pinning both raw subtree state and canonical World Index state makes stale reviewed approvals fail closed before mutation
unknown: []
conflicts: []
first_failure:
  marker: ownership-checkpoint-required-fields
  evidence: Agent Task Ownership run 29565114577 failed changed-task checkpoint validation because changed_paths derived first_failure and non-empty head/pr fields were missing; no implementation-path ownership conflict was reported
rejected_hypotheses:
  - full-map serializer
  - second OTBM parser
  - non-zero translation
  - tile insertion or deletion in v1
  - arbitrary item insertion deletion or stack reordering in v1
  - ordinary-tile house-tile conversion in v1
  - in-place source mutation
changed_paths:
  - docs/agents/decisions/ADR-20260717-otbm-raw-tile-replacement-boundary.md
  - docs/agents/tasks/active/CAN-20260717-otbm-tile-materializer.md
  - docs/ai-agent/OTBM_TILE_MATERIALIZATION_APPROVAL.schema.json
  - docs/ai-agent/OTBM_TILE_MATERIALIZATION_RESULT.schema.json
  - docs/ai-agent/OTBM_TILE_MATERIALIZER.md
  - docs/ai-agent/OTBM_TILE_SPANS.schema.json
  - tools/ai-agent/otbm_area_materializer_scan.cpp
  - tools/ai-agent/otbm_tile_materializer.py
  - tools/ai-agent/otbm_tile_materializer_tool.py
  - tools/ai-agent/test_otbm_tile_materializer.py
validation:
  - command: OTBM Map Tools run 29565114508 schema-validation step
    result: PASS
    evidence: all docs/ai-agent/OTBM_*.schema.json files parsed successfully on dc789cc76b877f4887833b8318e9ee7c983cbfaf
  - command: Agent Task Ownership run 29565114577
    result: FAIL
    evidence: checkpoint metadata only; missing changed_paths derived first_failure and non-empty head/pr fields, corrected in this commit
blockers: []
next_action: Inspect the focused OTBM test result on the implementation head, fix any root cause, then synchronize with current main before shared catalogue/changelog integration and the exact-final-head gate.
```
