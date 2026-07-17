---
task_id: CAN-20260717-otbm-tile-deletion
program_id: "OTS-OTBM-VALIDATION"
coordination_id: "OTS-OTBM-VALIDATION"
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/otbm-tile-deletion
base_branch: main
created: 2026-07-17T16:15:00+02:00
updated: 2026-07-17T16:55:00+02:00
last_verified_commit: "349e453fc8107418c439eeda447dfb78aced7919"
risk: high
related_issue: ""
related_pr: "488"
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

- [x] Add an ADR limiting v1 to complete existing tile deletion only; no TILE_AREA deletion, insertion, replacement, translation, type conversion, item-level editing, arbitrary serialization, or in-place source mutation.
- [x] Reuse the existing raw tile-span scanner and materialization safety helpers; add no parser or scanner mode.
- [x] Require each selected position to exist exactly once in current raw spans and current World Index under its canonical parent area.
- [x] Require a separate approval pinning the current map, current World Index/manifest, selected position/area key, exact current raw tile SHA-256/length/node type and canonical World Index tile SHA-256.
- [x] Remove only complete selected scanner-proven raw tile spans.
- [x] Prove the output equals current with exactly the approved selected spans removed, byte-for-byte and byte-count exact.
- [x] Reparse output, rebuild World Index, prove all selected positions are absent, and run bounded Semantic OTBM Diff.
- [x] Allow the existing parent TILE_AREA to become empty but never remove or synthesize the parent area in v1.
- [x] Keep current map/scanner immutable and publish output/evidence create-new under artifact root.
- [x] Add deterministic synthetic native-scanner integration tests, schemas and documentation; commit no maps, indexes, evidence, renders, assets or private artifacts.
- [ ] Pass exact-final-head ownership, OTBM Map Tools, AI Agent Tools and Ready-triggered full final-gate CI before squash merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T16:55:00+02:00
head: 349e453fc8107418c439eeda447dfb78aced7919
branch: feat/otbm-tile-deletion
pr: 488
status: validating
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
  - existing scanner tile spans provide exact complete raw tile deletion boundaries after canonical map acceptance
  - deletion v1 removes only complete selected scanner-proven raw tile spans and preserves parent TILE_AREA nodes
  - approval pins current map/index/manifest and exact selected raw plus canonical tile state
  - output retained-byte proof requires exact equality to current with only approved tile spans omitted
  - candidate publication requires native reparse rebuilt World Index selected-position absence and bounded Semantic Diff
  - focused OTBM Map Tools run 29587981584 passed after correcting the stale-approval test exception expectation without changing production validation logic
  - AI Agent Tools run 29587981549 passed on the corrected implementation
  - CI run 29587981619 passed on the corrected implementation
  - later OTBM Map Tools run 29588887337 passed on head 349e453fc8107418c439eeda447dfb78aced7919
  - later AI Agent Tools run 29588887224 passed on head 349e453fc8107418c439eeda447dfb78aced7919
  - later CI run 29588887442 passed on head 349e453fc8107418c439eeda447dfb78aced7919
  - MODULE_CATALOG diff is exactly one additive bounded tile deletion row
  - CHANGELOG diff is exactly one additive Unreleased tile deletion bullet
  - no OTBM maps WIDX generated evidence renders client assets or private artifacts are committed
  - open E2E and security PRs are unrelated and were not modified
derived:
  - deletion requires no donor because approved current raw and canonical state is the complete reviewed deletion target
  - retaining an empty parent TILE_AREA keeps deletion v1 below parent-area structural semantics
unknown:
  - exact final-head gate results after this checkpoint-only commit
conflicts: []
first_failure:
  marker: stale-approval-exception-expectation
  evidence: OTBM Map Tools run 29587465137 showed the shared selection helper correctly rejected a stale raw SHA but the new test expected the narrower deletion subclass; the test was corrected to accept the shared TileMaterializerError contract without changing production validation logic
rejected_hypotheses:
  - build another OTBM parser or scanner mode
  - delete parent TILE_AREA when its last tile is removed
  - combine deletion with insertion replacement translation or type conversion
  - perform item-level structural deletion
changed_paths:
  - docs/agents/CHANGELOG.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/decisions/ADR-20260717-otbm-raw-tile-deletion-boundary.md
  - docs/agents/tasks/active/CAN-20260717-otbm-tile-deletion.md
  - docs/ai-agent/OTBM_TILE_DELETION_APPROVAL.schema.json
  - docs/ai-agent/OTBM_TILE_DELETION_MATERIALIZER.md
  - docs/ai-agent/OTBM_TILE_DELETION_RESULT.schema.json
  - tools/ai-agent/otbm_tile_deletion_materializer.py
  - tools/ai-agent/otbm_tile_deletion_materializer_tool.py
  - tools/ai-agent/test_otbm_tile_deletion_materializer.py
validation:
  - command: OTBM Map Tools run 29587465137
    result: FAIL
    evidence: stale approval was correctly rejected but the test expected a narrower exception subclass
  - command: OTBM Map Tools run 29587981584
    result: PASS
    evidence: all focused OTBM tests and schema validation passed after correcting only the test expectation
  - command: AI Agent Tools run 29587981549
    result: PASS
    evidence: AI agent tool suite passed after the test-only correction
  - command: CI run 29587981619
    result: PASS
    evidence: repository CI passed after the test-only correction
  - command: OTBM Map Tools run 29588887337
    result: PASS
    evidence: focused OTBM validation passed on pre-checkpoint head 349e453fc8107418c439eeda447dfb78aced7919
  - command: AI Agent Tools run 29588887224
    result: PASS
    evidence: AI agent validation passed on pre-checkpoint head 349e453fc8107418c439eeda447dfb78aced7919
  - command: CI run 29588887442
    result: PASS
    evidence: repository CI passed on pre-checkpoint head 349e453fc8107418c439eeda447dfb78aced7919
blockers: []
next_action: Treat this checkpoint-only commit as the exact final feature head; make no further feature commits, require exact-final-head ownership, OTBM Map Tools, AI Agent Tools and Ready-triggered full final-gate CI success, then squash merge and archive the task in a separate lifecycle PR.
```
