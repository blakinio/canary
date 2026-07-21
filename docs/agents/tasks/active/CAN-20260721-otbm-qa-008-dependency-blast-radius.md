---
task_id: CAN-20260721-otbm-qa-008-dependency-blast-radius
program_id: CAN-PROGRAM-OTBM
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/otbm-qa-008-dependency-blast-radius-20260721
base_branch: main
created: 2026-07-21
updated: 2026-07-21
last_verified_commit: "f05ea5e916af00ab1469a2332aaec2d3c9df7478"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - CAN-20260721-otbm-qa-001-world-health complete
  - CAN-20260721-otbm-qa-002-map-change-regression complete
blocks:
  - OTBM-QA-009 dead/orphaned content and quest completeness
  - OTBM-QA-017 deterministic change risk
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_dependency_graph.py
    - tools/ai-agent/otbm_dependency_graph_tool.py
    - tools/ai-agent/test_otbm_dependency_graph.py
    - tools/ai-agent/test_otbm_dependency_graph_output_safety.py
    - tools/ai-agent/test_otbm_dependency_graph_schema.py
    - docs/ai-agent/OTBM_DEPENDENCY_GRAPH.md
    - docs/ai-agent/OTBM_DEPENDENCY_GRAPH_MANIFEST.schema.json
    - docs/ai-agent/OTBM_DEPENDENCY_GRAPH.schema.json
    - docs/agents/tasks/active/CAN-20260721-otbm-qa-008-dependency-blast-radius.md
  shared:
    - docs/agents/MODULE_CATALOG.md
  read_only:
    - docs/ai-agent/OTBM_WORLD_QUALITY_REPAIR_ROADMAP.md
    - docs/ai-agent/OTBM_WORLD_HEALTH.md
    - docs/ai-agent/OTBM_MAP_CHANGE_REGRESSION.md
    - docs/ai-agent/OTBM_COVERAGE_DASHBOARD.md
modules_touched:
  - otbm-dependency-graph
reuses:
  - OTBM-QA-001 World Health
  - OTBM-QA-002 Map Change Regression Guard
  - OTBM-QA-005 Coverage Dashboard when explicitly supplied
public_interfaces:
  - canary-otbm-dependency-graph-manifest-v1
  - canary-otbm-dependency-blast-radius-v1
cross_repo_tasks: []
---

# CAN-20260721 — OTBM-QA-008 Mechanic Dependency and Blast Radius Graph

## Status

ACTIVE — bounded implementation started from current `main`.

## Goal

Build a deterministic read-only dependency overlay over explicitly reviewed nodes and edges backed by exact compatible existing OTBM evidence, then compute direct/transitive blast radius and unresolved dependency boundaries without inventing semantic relationships.

## Bounded slice

- Add a reviewed dependency manifest with explicit node IDs, node kinds, directed impact edges, exact evidence references and blast-radius queries.
- Require compatible QA-001 World Health and QA-002 Map Change Regression evidence; allow compatible QA-005 Coverage Dashboard evidence when explicitly supplied.
- Resolve evidence references only by exact supplied report SHA-256 plus RFC 6901 JSON Pointer and optional exact/subset expectations.
- Treat an edge as proven only when both endpoint nodes and every required evidence reference are proven.
- Compute deterministic direct and transitive impacts only across proven directed edges.
- Surface unresolved/ambiguous boundaries separately; never traverse them as proven impact paths.
- Emit shortest deterministic evidence paths for transitive impacts.
- Keep generated reports outside Git and use create-new/no-clobber output semantics.

## Explicit non-goals

- No OTBM parsing/scanning, World Index construction, Script Resolution, storage graph reconstruction, pathfinding, route planning, E2E selection or Physical E2E execution.
- No dependency edge inference from names, proximity, sprite/item similarity, visual layout or chat history.
- No automatic scenario prioritization, repair approval, mutation or certification assignment.
- No claim that selected-scope absence proves global absence.

## Acceptance criteria

- Current World Health source map equals Regression Guard after-map; compatible World Index provenance is exact when present.
- Optional Coverage Dashboard must prove the same current map/World Index.
- Unknown report SHA, invalid JSON Pointer, failed expectation or unproven endpoint makes the dependent node/edge unresolved rather than proven.
- Duplicate node/edge/query IDs and references to unknown nodes fail closed.
- Proven cycles do not loop indefinitely and deterministic shortest paths are byte-stable.
- Unresolved edges are reported as boundaries and never contribute to transitive proven impact.
- Output safety rejects symlinks, duplicate inputs, input/output collisions and no-clobber violations.
- Focused aggregation/schema/output-safety tests plus relevant AI Agent/OTBM gates pass.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T22:50:00+02:00
head: f05ea5e916af00ab1469a2332aaec2d3c9df7478
branch: feat/otbm-qa-008-dependency-blast-radius-20260721
pr: none
status: implementing
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - tools/ai-agent/otbm_dependency_graph.py
  - tools/ai-agent/otbm_dependency_graph_tool.py
  - tools/ai-agent/test_otbm_dependency_graph.py
  - tools/ai-agent/test_otbm_dependency_graph_output_safety.py
  - tools/ai-agent/test_otbm_dependency_graph_schema.py
  - docs/ai-agent/OTBM_DEPENDENCY_GRAPH.md
  - docs/ai-agent/OTBM_DEPENDENCY_GRAPH_MANIFEST.schema.json
  - docs/ai-agent/OTBM_DEPENDENCY_GRAPH.schema.json
  - docs/agents/tasks/active/CAN-20260721-otbm-qa-008-dependency-blast-radius.md
  - docs/agents/MODULE_CATALOG.md
proven:
  - Current main is f05ea5e916af00ab1469a2332aaec2d3c9df7478 at task start.
  - OTBM-QA-001 through OTBM-QA-005 are merged and QA-005 lifecycle is archived.
  - No otbm-qa branch or open OTBM-QA pull request existed at fresh task preflight.
  - Roadmap requires QA-008 dependency/blast-radius evidence before QA-009 and later risk classification.
  - QA-001 exposes exact current map/World Index provenance and bounded evidence samples; QA-002 exposes exact before/after provenance, sampled change findings and impacted represented Physical E2E decisions.
derived:
  - The smallest safe QA-008 v1 is an explicit reviewed graph whose edges are validated against exact report SHA plus evidence pointers; the tool computes graph reachability but does not infer domain edges.
unknown: []
conflicts: []
first_failure:
  marker: none
  evidence: No implementation failure observed.
rejected_hypotheses:
  - Building a second Script Resolution/storage/route dependency resolver: roadmap and AGENTS require reuse of existing canonical evidence instead.
changed_paths:
  - docs/agents/tasks/active/CAN-20260721-otbm-qa-008-dependency-blast-radius.md
validation: []
blockers: []
next_action: Open the draft PR and implement the reviewed dependency manifest, deterministic graph aggregator, CLI, schemas and focused tests without expanding into domain inference.
```
