---
task_id: CAN-20260717-otbm-pipeline-raw-tile-modes
program_id: "OTS-OTBM-VALIDATION"
coordination_id: "OTS-OTBM-VALIDATION"
status: completed
agent: "GPT-5.5 Thinking"
branch: feat/otbm-pipeline-raw-tile-modes
base_branch: main
created: 2026-07-17T21:05:00+02:00
updated: 2026-07-17T20:02:51Z
last_verified_commit: "cb149d427e6a954ee3ab163758465627bc1e643c"
risk: high
related_issue: ""
related_pr: "506"
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
    - tools/ai-agent/otbm_repair_pipeline_raw_tile_contracts.py
    - tools/ai-agent/otbm_repair_pipeline_raw_tile_executors.py
    - tools/ai-agent/otbm_repair_pipeline_structural_cli.py
    - tools/ai-agent/test_otbm_repair_materialization_pipeline_raw_tiles.py
  shared:
    - tools/ai-agent/otbm_repair_materialization_pipeline.py
    - tools/ai-agent/otbm_repair_materialization_pipeline_tool.py
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
completed: 2026-07-17T20:02:51Z
---

# Goal

Complete the required structural OTBM finalization surface by extending the existing fail-closed repair/materialization pipeline with four already-approved same-coordinate raw-tile mutation modes: replacement, insertion, deletion and tile-type conversion.

# Acceptance criteria

- [x] Add `tile-replacement`, `tile-insertion`, `tile-deletion`, and `tile-type-conversion` as modes of the existing pipeline; exactly one mutation mode per run.
- [x] Call the existing materializer functions unchanged; add no parser, scanner, writer, serializer, World Index, Semantic Diff, script resolver, renderer or deployment path.
- [x] Validate each existing materializer result format, source/current identity, candidate output identity, structural verification flags and safety invariants before Map Quality evaluation.
- [x] Keep explicit candidate SHA identity with the rebuilt Map Quality Gate and byte-identical final publication.
- [x] Extend the existing CLI with four subcommands using the already-required materializer inputs.
- [x] Extend the existing pipeline schema and documentation without creating a second pipeline contract.
- [x] Add deterministic tests for mode dispatch and fail-closed mutation-report validation for all four raw-tile modes.
- [x] Preserve `fixed-width-attribute` and `tile-area` behavior unchanged at the canonical pipeline boundary.
- [x] Commit no maps, `.widx`, generated reports, evidence or private artifacts.
- [x] Keep non-zero translation, teleport rewrite, partial TILE_AREA import, arbitrary item-stack editing, generic node serialization, full-map serialization and direct production-map execution explicitly out of scope.
- [ ] Pass exact-final-head Ownership, OTBM Map Tools, AI Agent Tools and full final-gate CI before squash merge, then archive separately.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T21:22:00+02:00
head: 7c00702e5cdbc3bff1b831cf46c67b788e90f191
branch: feat/otbm-pipeline-raw-tile-modes
pr: 506
status: implementing
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/CAN-20260717-otbm-pipeline-raw-tile-modes.md
  - tools/ai-agent/otbm_repair_materialization_pipeline.py
  - tools/ai-agent/otbm_repair_materialization_pipeline_tool.py
  - tools/ai-agent/otbm_repair_pipeline_raw_tile_contracts.py
  - tools/ai-agent/otbm_repair_pipeline_raw_tile_executors.py
  - tools/ai-agent/otbm_repair_pipeline_structural_cli.py
  - tools/ai-agent/test_otbm_repair_materialization_pipeline_raw_tiles.py
  - docs/ai-agent/OTBM_REPAIR_MATERIALIZATION_PIPELINE.md
  - docs/ai-agent/OTBM_REPAIR_MATERIALIZATION_PIPELINE.schema.json
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - canonical repair/materialization pipeline was already merged and centralized candidate identity Map Quality reconstruction and final byte-identical create-new publication
  - bounded same-coordinate raw tile replacement insertion deletion and tile-type conversion are independently merged and lifecycle complete
  - all four raw-tile materializers keep their existing scanner byte-confinement World Index Semantic Diff source-immutability and create-new publication checks
  - PR 506 composes those existing materializers through thin executor adapters and keeps run_pipeline as the only finalization path
  - raw tile report validation requires the existing exact report format current-source SHA candidate output SHA and size structuralVerificationComplete operation-specific verification flags and safety invariants before Map Quality evaluation
  - the public canonical pipeline CLI now registers tile-replacement tile-insertion tile-deletion and tile-type-conversion subcommands while preserving attribute and tile-area commands
  - pipeline result schema v1 was extended in place with the four new modes and four existing materializer result formats
  - focused tests exercise all four mode dispatch paths through run_pipeline and fail closed when required verification is missing
  - no competing open PR for raw-tile pipeline mode integration was found at task start
  - first Ownership run 29607000543 failed only because the initial checkpoint used first_failure null instead of a YAML mapping
derived:
  - composition of existing materializers inside the canonical pipeline is the remaining required OTBM finalization step and does not require a new structural writer or ADR
  - splitting contracts executors and CLI preparation into thin adapter modules avoids duplicating run_pipeline while keeping connector writes bounded
  - translation and generic serialization remain separate explicitly deferred architecture boundaries rather than missing acceptance criteria for this task
unknown:
  - current OTBM Map Tools AI Agent Tools and CI conclusions after the implementation/documentation commits
  - exact final feature head and ready-triggered final-gate run IDs
conflicts: []
first_failure:
  marker: active-task-checkpoint-schema
  evidence: Agent Task Ownership run 29607000543 artifact 8417238050 reports first_failure must be a YAML mapping
rejected_hypotheses:
  - creating a second structural repair pipeline
  - adding non-zero translation merely to claim full writer coverage
  - adding a generic OTBM serializer or full-map writer
  - duplicating materializer writer/scanner verification logic
  - representing raw tile mutations as tile-area or attribute reports
changed_paths:
  - docs/agents/tasks/active/CAN-20260717-otbm-pipeline-raw-tile-modes.md
  - docs/ai-agent/OTBM_REPAIR_MATERIALIZATION_PIPELINE.md
  - docs/ai-agent/OTBM_REPAIR_MATERIALIZATION_PIPELINE.schema.json
  - tools/ai-agent/otbm_repair_materialization_pipeline.py
  - tools/ai-agent/otbm_repair_materialization_pipeline_tool.py
  - tools/ai-agent/otbm_repair_pipeline_raw_tile_contracts.py
  - tools/ai-agent/otbm_repair_pipeline_raw_tile_executors.py
  - tools/ai-agent/otbm_repair_pipeline_structural_cli.py
  - tools/ai-agent/test_otbm_repair_materialization_pipeline_raw_tiles.py
validation:
  - command: Agent Task Ownership run 29607000543
    result: FAIL
    evidence: initial checkpoint first_failure was null; corrected in this commit
blockers: []
next_action: Inspect current OTBM Map Tools AI Agent Tools and CI results, fix any implementation regressions, then update Module Catalog and Changelog before final-gate preparation.
```

## Automated lifecycle completion

- Feature PR: #506.
- Feature head: `cd3585d154a0e0768e456925cacc3c701732a774`.
- Merge commit: `cb149d427e6a954ee3ab163758465627bc1e643c`.
- Merged at: `2026-07-17T20:02:51Z`.
- This record was moved from `tasks/active` by the post-merge lifecycle automation.
