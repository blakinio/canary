---
task_id: CAN-20260717-otbm-tile-type-conversion
program_id: "OTS-OTBM-VALIDATION"
coordination_id: "OTS-OTBM-VALIDATION"
status: validating
agent: "GPT-5.5 Thinking"
branch: feat/otbm-tile-type-conversion
base_branch: main
created: 2026-07-17T19:53:00+02:00
updated: 2026-07-17T20:30:00+02:00
last_verified_commit: "54d4cd9ad4be73083a74dffbcafb23d87ce1c92a"
risk: high
related_issue: ""
related_pr: "498"
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

- [x] Add an ADR limiting v1 to exact same-coordinate complete raw tile-node type conversion only.
- [x] Reuse the existing tile-span scanner and complete raw tile replacement writer; add no parser, scanner mode, generic serializer, or item-stack writer.
- [x] Require every selected position to exist exactly once in current and donor maps under the same canonical parent `TILE_AREA`.
- [x] Require current and donor node types to be different and limited to `OTBM_TILE` (5) and `OTBM_HOUSETILE` (14).
- [x] Require separate SHA-pinned approval for current/donor maps, indexes, manifests, exact raw subtrees and canonical World Index tiles.
- [x] Prove non-selected current bytes are preserved exactly and selected output raw subtrees equal donor byte-for-byte.
- [x] Reparse output, rebuild World Index, prove selected canonical output tiles equal donor, and run bounded Semantic OTBM Diff.
- [x] Keep source maps/scanner immutable and publish output/evidence create-new under artifact root.
- [x] Add deterministic synthetic conversion tests in both directions plus stale/same-type rejection coverage.
- [x] Commit no maps, `.widx`, generated evidence, renders, client assets or private artifacts.
- [ ] Pass exact-final-head ownership, OTBM Map Tools, AI Agent Tools and full final-gate CI before squash merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T20:30:00+02:00
head: 54d4cd9ad4be73083a74dffbcafb23d87ce1c92a
branch: feat/otbm-tile-type-conversion
pr: 498
status: validating
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
  - existing replacement writer proves retained-current-byte equality and donor raw-subtree equality and is reused rather than duplicated
  - open PR search found no competing OTBM tile type conversion work at task start
  - complete donor raw subtree carries the target node type and house metadata so no node serializer or house-id synthesis is required
  - PR 498 is the bounded tile type conversion feature PR
  - approval requires current and donor exact map/index/manifest provenance plus selected raw SHA length node type and canonical tile SHA
  - conversion validator requires exact same position and canonical parent TILE_AREA and rejects equal current donor node types
  - materialization reuses the complete raw tile replacement writer and then requires native reparse rebuilt World Index selected donor equality and bounded Semantic Diff
  - focused tests cover TILE to HOUSETILE HOUSETILE to TILE same-type rejection and stale-current-raw rejection
  - exact pre-final head 54d4cd9ad4be73083a74dffbcafb23d87ce1c92a passed Agent Task Ownership run 29603081771
  - exact pre-final head 54d4cd9ad4be73083a74dffbcafb23d87ce1c92a passed OTBM Map Tools run 29603082046
  - exact pre-final head 54d4cd9ad4be73083a74dffbcafb23d87ce1c92a passed AI Agent Tools run 29603081805
  - exact pre-final head 54d4cd9ad4be73083a74dffbcafb23d87ce1c92a passed CI run 29603082126
  - MODULE_CATALOG diff is one additive conversion-materializer row and CHANGELOG diff is one additive conversion bullet
  - PR 498 has no conversation comments and no inline review threads before final-gate preparation
  - current main 2edc59f59c417f82efb0547f3ff87b426f8bbe5a is one non-overlapping lifecycle rename ahead of the feature base, limited to the completed initial-position task record
  - PR 498 remains mergeable against current main and pull-request CI validates the current GitHub merge ref
  - ci:final-gate label was applied before this immutable final checkpoint commit
derived:
  - the smallest safe conversion boundary is a constrained complete-subtree replacement with the inverse node-type predicate from replacement v1
  - copying a complete approved house donor subtree is safer than changing a raw node-type byte because house metadata layout differs
  - the single main advancement since the feature base cannot overlap this OTBM feature because it only renames the unrelated initial-position E2E task record
unknown:
  - exact final checkpoint commit SHA until this commit is created
  - exact-final-head gate conclusions triggered by this checkpoint commit
conflicts: []
first_failure:
  marker: stale-active-task-checkpoint
  evidence: Agent Task Ownership run 29602457086 failed changed active task checkpoint validation on an earlier head; the corrected checkpoint subsequently passed run 29603081771
rejected_hypotheses:
  - editing the node-type byte in place
  - synthesizing house identifiers or house metadata
  - item-level conversion
  - generic OTBM serialization
  - treating the unrelated lifecycle-only main advancement as a reason to duplicate or recreate the feature branch
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
  - command: Agent Task Ownership run 29603081771
    result: PASS
    evidence: corrected active-task ownership and checkpoint validation passed on 54d4cd9ad4be73083a74dffbcafb23d87ce1c92a
  - command: OTBM Map Tools run 29603082046
    result: PASS
    evidence: focused OTBM validation including tile type conversion tests passed on 54d4cd9ad4be73083a74dffbcafb23d87ce1c92a
  - command: AI Agent Tools run 29603081805
    result: PASS
    evidence: AI agent tool suite passed on 54d4cd9ad4be73083a74dffbcafb23d87ce1c92a
  - command: CI run 29603082126
    result: PASS
    evidence: repository CI passed on 54d4cd9ad4be73083a74dffbcafb23d87ce1c92a
  - command: compare main advancement 250640758bec48946f31f34c85995632d194fbd0..2edc59f59c417f82efb0547f3ff87b426f8bbe5a
    result: PASS
    evidence: exactly one unrelated lifecycle rename under docs/agents/tasks for the completed initial-position E2E task
blockers: []
next_action: Freeze the checkpoint commit as the exact final feature head, require Ownership, OTBM Map Tools, AI Agent Tools and full ci:final-gate CI on that head, then squash merge with expected-head protection and archive the task in a separate lifecycle PR.
```
