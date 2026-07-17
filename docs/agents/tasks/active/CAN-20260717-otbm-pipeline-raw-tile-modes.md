---
task_id: CAN-20260717-otbm-pipeline-raw-tile-modes
program_id: "OTS-OTBM-VALIDATION"
coordination_id: "OTS-OTBM-VALIDATION"
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/otbm-pipeline-raw-tile-modes
base_branch: main
created: 2026-07-17T21:05:00+02:00
updated: 2026-07-17T21:05:00+02:00
last_verified_commit: "2bd3ab0ab695031904e9330cb60dccd891e55439"
risk: high
related_issue: ""
related_pr: ""
depends_on:
  - "OTBM repair/materialization pipeline #456"
  - "OTBM bounded raw tile replacement #467"
  - "OTBM bounded raw tile insertion #482"
  - "OTBM bounded raw tile deletion #488"
  - "OTBM bounded raw tile type conversion #498"
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260717-otbm-pipeline-raw-tile-modes.md
  shared:
    - tools/ai-agent/otbm_repair_materialization_pipeline.py
    - tools/ai-agent/otbm_repair_materialization_pipeline_tool.py
    - tools/ai-agent/test_otbm_repair_materialization_pipeline.py
    - docs/ai-agent/OTBM_REPAIR_MATERIALIZATION_PIPELINE.md
    - docs/ai-agent/OTBM_REPAIR_MATERIALIZATION_PIPELINE.schema.json
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/ai-agent/otbm_tile_materializer.py
    - tools/ai-agent/otbm_tile_insertion_materializer.py
    - tools/ai-agent/otbm_tile_deletion_materializer.py
    - tools/ai-agent/otbm_tile_type_conversion_materializer.py
    - tools/ai-agent/otbm_world_index.py
    - tools/ai-agent/otbm_semantic_diff.py
modules_touched:
  - OTBM repair/materialization pipeline
reuses:
  - existing pipeline candidate/quality/publication flow
  - bounded raw tile replacement materializer
  - bounded raw tile insertion materializer
  - bounded raw tile deletion materializer
  - bounded raw tile type conversion materializer
  - existing Map Quality Gate
public_interfaces:
  - canary-otbm-repair-materialization-pipeline-v1
cross_repo_tasks: []
---

# Goal

Complete the required structural OTBM finalization surface by extending the existing fail-closed repair/materialization pipeline with four already-approved same-coordinate raw-tile mutation modes: replacement, insertion, deletion and tile-type conversion.

# Acceptance criteria

- [ ] Add `tile-replacement`, `tile-insertion`, `tile-deletion`, and `tile-type-conversion` as modes of the existing pipeline; exactly one mutation mode per run.
- [ ] Call the existing materializer functions unchanged; add no parser, scanner, writer, serializer, World Index, Semantic Diff, script resolver, renderer or deployment path.
- [ ] Validate each existing materializer result format, source/current identity, candidate output identity, structural verification flags and safety invariants before Map Quality evaluation.
- [ ] Keep explicit candidate SHA identity with the rebuilt Map Quality Gate and byte-identical final publication.
- [ ] Extend the existing CLI with four subcommands using the already-required materializer inputs.
- [ ] Extend the existing pipeline schema and documentation without creating a second pipeline contract.
- [ ] Add deterministic tests for mode dispatch and fail-closed mutation-report validation for all four raw-tile modes.
- [ ] Preserve `fixed-width-attribute` and `tile-area` behavior unchanged.
- [ ] Commit no maps, `.widx`, generated reports, evidence or private artifacts.
- [ ] Keep non-zero translation, teleport rewrite, partial TILE_AREA import, arbitrary item-stack editing, generic node serialization, full-map serialization and direct production-map execution explicitly out of scope.
- [ ] Pass exact-final-head Ownership, OTBM Map Tools, AI Agent Tools and full final-gate CI before squash merge, then archive separately.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T21:05:00+02:00
head: 2bd3ab0ab695031904e9330cb60dccd891e55439
branch: feat/otbm-pipeline-raw-tile-modes
pr: pending
status: implementing
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/CAN-20260717-otbm-pipeline-raw-tile-modes.md
  - tools/ai-agent/otbm_repair_materialization_pipeline.py
  - tools/ai-agent/otbm_repair_materialization_pipeline_tool.py
  - tools/ai-agent/test_otbm_repair_materialization_pipeline.py
  - docs/ai-agent/OTBM_REPAIR_MATERIALIZATION_PIPELINE.md
  - docs/ai-agent/OTBM_REPAIR_MATERIALIZATION_PIPELINE.schema.json
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - canonical repair/materialization pipeline is merged and currently supports only fixed-width-attribute and tile-area modes
  - bounded same-coordinate raw tile replacement insertion deletion and tile-type conversion are independently merged and lifecycle complete
  - all four raw-tile materializers already perform their own scanner byte-confinement World Index Semantic Diff source-immutability and create-new publication checks
  - the canonical pipeline already centralizes candidate identity Map Quality reconstruction and final byte-identical create-new publication
  - no competing open PR for raw-tile pipeline mode integration was found at task start
  - latest inspected main is 2bd3ab0ab695031904e9330cb60dccd891e55439 after tile-type conversion lifecycle completion
derived:
  - composition of existing materializers inside the canonical pipeline is the remaining required OTBM finalization step and does not require a new structural writer or ADR
  - translation and generic serialization remain separate explicitly deferred architecture boundaries rather than missing acceptance criteria for this task
unknown:
  - exact implementation head and final CI evidence
conflicts: []
first_failure: null
rejected_hypotheses:
  - creating a second structural repair pipeline
  - adding non-zero translation merely to claim full writer coverage
  - adding a generic OTBM serializer or full-map writer
  - duplicating materializer verification logic instead of validating their published result contracts
changed_paths:
  - docs/agents/tasks/active/CAN-20260717-otbm-pipeline-raw-tile-modes.md
validation: []
blockers: []
next_action: Open a draft PR, extend only the canonical pipeline composition/CLI/schema/docs/tests, then validate exact-head gates.
```
