---
task_id: CAN-20260717-otbm-tile-deletion
program_id: "OTS-OTBM-VALIDATION"
coordination_id: "OTS-OTBM-VALIDATION"
status: completed
agent: "GPT-5.5 Thinking"
branch: feat/otbm-tile-deletion
base_branch: main
created: 2026-07-17T16:15:00+02:00
updated: 2026-07-17T15:36:01Z
last_verified_commit: "59fd2eed488e365d2759bffc69526fc87838dd77"
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
completed: 2026-07-17T15:36:01Z
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
- [x] Pass exact-final-head ownership, OTBM Map Tools, AI Agent Tools and Ready-triggered full final-gate CI before squash merge.

## Final evidence

- Feature PR: #488.
- Exact final feature head: `ab97944bd1e3b6dc4272d19ef14f9b33d8b30a2e`.
- Agent Task Ownership run `29591607653`: success.
- OTBM Map Tools run `29591607686`: success.
- AI Agent Tools run `29591607522`: success.
- Ready/final-gate full CI run `29591607872`: success.
- Feature squash merge: `59fd2eed488e365d2759bffc69526fc87838dd77`.
- Merged at: `2026-07-17T15:36:01Z`.
- Automated lifecycle PR #493 was closed without merge because token-created recursive ownership/CI runs were `action_required`; lifecycle is completed through a separate normal protected PR.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T15:36:01Z
head: ab97944bd1e3b6dc4272d19ef14f9b33d8b30a2e
branch: feat/otbm-tile-deletion
pr: 488
status: completed
context_routes:
  - otbm
  - agent-governance
proven:
  - deletion v1 removes only complete selected scanner-proven raw tile spans and preserves parent TILE_AREA nodes
  - approval pins current map/index/manifest and exact selected raw plus canonical tile state
  - output retained-byte proof requires exact equality to current with only approved tile spans omitted
  - candidate publication requires native reparse rebuilt World Index selected-position absence and bounded Semantic Diff
  - exact final-head Agent Task Ownership run 29591607653 passed
  - exact final-head OTBM Map Tools run 29591607686 passed
  - exact final-head AI Agent Tools run 29591607522 passed
  - exact final-head full final-gate CI run 29591607872 passed
  - feature PR 488 squash-merged as 59fd2eed488e365d2759bffc69526fc87838dd77
  - MODULE_CATALOG diff was exactly one additive bounded tile deletion row
  - CHANGELOG diff was exactly one additive Unreleased tile deletion bullet
  - no OTBM maps WIDX generated evidence renders client assets or private artifacts were committed
conflicts: []
first_failure:
  marker: stale-approval-exception-expectation
  evidence: initial focused OTBM validation showed the shared selection helper correctly rejected a stale raw SHA while the new test expected a narrower deletion subclass; the test expectation was corrected without changing production validation logic
validation:
  - command: OTBM Map Tools run 29591607686
    result: PASS
    evidence: exact final-head focused OTBM tests and schema validation passed
  - command: AI Agent Tools run 29591607522
    result: PASS
    evidence: exact final-head AI agent tool suite passed
  - command: Agent Task Ownership run 29591607653
    result: PASS
    evidence: exact final-head task ownership and checkpoint validation passed
  - command: CI run 29591607872
    result: PASS
    evidence: exact final-head full final-gate CI passed
blockers: []
next_action: Task completed and archived. Future raw tile type conversion or structural-operation pipeline integration requires a separate bounded ADR/task.
```
