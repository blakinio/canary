---
task_id: CAN-20260721-otbm-qa-008-dependency-blast-radius
program_id: CAN-PROGRAM-OTBM
status: ready
agent: "GPT-5.6 Thinking"
branch: feat/otbm-qa-008-dependency-blast-radius-20260721
base_branch: main
created: 2026-07-21
updated: 2026-07-21
last_verified_commit: "529b58ef42faf8b4dbff59924280e36d080aee93"
risk: medium
related_issue: ""
related_pr: "694"
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

READY — bounded QA-008 implementation is complete in PR #694; exact-final-head gates remain before merge.

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
updated_at: 2026-07-21T23:18:00+02:00
head: 529b58ef42faf8b4dbff59924280e36d080aee93
branch: feat/otbm-qa-008-dependency-blast-radius-20260721
pr: 694
status: ready
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
proven:
  - Current main is still identical to task-start f05ea5e916af00ab1469a2332aaec2d3c9df7478 at the pre-final overlap check.
  - QA-008 delivers canary-otbm-dependency-graph-manifest-v1 and canary-otbm-dependency-blast-radius-v1 as explicit reviewed-evidence contracts.
  - Exact evidence references use supplied report SHA-256 plus RFC 6901 JSON Pointer and optional equals/subset expectations; unresolved evidence fails closed.
  - Only proven reviewed directed edges are traversed; deterministic shortest paths are cycle-safe and unresolved boundaries remain separate.
  - Local isolated focused suite passed 15 tests.
  - Pre-final complete implementation head 529b58ef42faf8b4dbff59924280e36d080aee93 passed CI 29868958752, Agent Task Ownership 29868958091, OTBM Map Tools 29868958405 and AI Agent Tools 29868958228.
  - The earlier Ownership failure 29868582020 was limited to a related_pr mismatch and was corrected before this final checkpoint.
derived:
  - QA-008 remains an evidence overlay rather than a second Script Resolution, storage graph, pathfinder, route planner or E2E impact selector.
unknown: []
conflicts: []
first_failure:
  marker: none
  evidence: No unresolved implementation or governance failure remains before exact-final-head validation.
rejected_hypotheses:
  - Building a second Script Resolution/storage/route dependency resolver: roadmap and AGENTS require reuse of existing canonical evidence instead.
changed_paths:
  - docs/agents/tasks/active/CAN-20260721-otbm-qa-008-dependency-blast-radius.md
  - docs/ai-agent/OTBM_DEPENDENCY_GRAPH.md
  - docs/ai-agent/OTBM_DEPENDENCY_GRAPH.schema.json
  - docs/ai-agent/OTBM_DEPENDENCY_GRAPH_MANIFEST.schema.json
  - tools/ai-agent/otbm_dependency_graph.py
  - tools/ai-agent/otbm_dependency_graph_tool.py
  - tools/ai-agent/test_otbm_dependency_graph.py
  - tools/ai-agent/test_otbm_dependency_graph_output_safety.py
  - tools/ai-agent/test_otbm_dependency_graph_schema.py
validation:
  - command: local focused unittest discovery for test_otbm_dependency_graph*.py
    result: PASS
    evidence: 15 tests passed in isolated reconstructed QA-008 test workspace.
  - command: GitHub Actions CI run 29868958752
    result: PASS
    evidence: pre-final complete implementation head 529b58ef42faf8b4dbff59924280e36d080aee93
  - command: GitHub Actions Agent Task Ownership run 29868958091
    result: PASS
    evidence: pre-final complete implementation head 529b58ef42faf8b4dbff59924280e36d080aee93
  - command: GitHub Actions OTBM Map Tools run 29868958405
    result: PASS
    evidence: pre-final complete implementation head 529b58ef42faf8b4dbff59924280e36d080aee93
  - command: GitHub Actions AI Agent Tools run 29868958228
    result: PASS
    evidence: pre-final complete implementation head 529b58ef42faf8b4dbff59924280e36d080aee93
blockers: []
next_action: Verify exact-final-head CI, Agent Task Ownership, OTBM Map Tools and AI Agent Tools on the immutable final feature head, audit reviews, then squash-merge PR #694 and complete the separate lifecycle archive before starting QA-009.
```
