---
task_id: CAN-20260721-otbm-qa-002-map-change-regression
program_id: CAN-PROGRAM-OTBM
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/otbm-qa-002-regression-guard-20260721
base_branch: main
created: 2026-07-21
updated: 2026-07-21
last_verified_commit: "eb2e09bc0778f0e88446638edf15c9069e771b11"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - CAN-20260721-otbm-qa-001-world-health complete
blocks:
  - OTBM-QA-003 repair recommendation orchestration
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_map_change_regression.py
    - tools/ai-agent/otbm_map_change_regression_tool.py
    - tools/ai-agent/test_otbm_map_change_regression.py
    - tools/ai-agent/test_otbm_map_change_regression_output_safety.py
    - tools/ai-agent/test_otbm_map_change_regression_schema.py
    - docs/ai-agent/OTBM_MAP_CHANGE_REGRESSION.md
    - docs/ai-agent/OTBM_MAP_CHANGE_REGRESSION.schema.json
    - docs/agents/tasks/active/CAN-20260721-otbm-qa-002-map-change-regression.md
  shared:
    - docs/agents/MODULE_CATALOG.md
  read_only:
    - docs/ai-agent/OTBM_WORLD_QUALITY_REPAIR_ROADMAP.md
    - docs/architecture/otbm-world-quality-repair.md
    - docs/ai-agent/OTBM_SEMANTIC_DIFF.md
    - docs/ai-agent/OTBM_E2E_IMPACTED_SELECTION.md
    - docs/ai-agent/OTBM_MAP_QUALITY_GATE.md
modules_touched:
  - otbm-map-change-regression
reuses:
  - Semantic OTBM Diff
  - OTBM-E2E-008 impacted Physical E2E selection
  - OTBM Map Quality Gate
  - exact before/after World Index provenance from existing reports
public_interfaces:
  - canary-otbm-map-change-regression-v1
cross_repo_tasks: []
---

# CAN-20260721 — OTBM-QA-002 Map Change Regression Guard

## Status

ACTIVE — bounded implementation of the next unrealized roadmap package after OTBM-QA-001 lifecycle closure.

## Goal

Turn exact existing Semantic OTBM Diff evidence plus existing OTBM-E2E-008 impacted-selection evidence into one deterministic, fail-closed impacted-validation plan without parsing/scanning OTBM, rebuilding World Indexes, pathfinding, running E2E, mutating maps or suppressing unrelated non-OTBM validation.

## Bounded slice

- Introduce `canary-otbm-map-change-regression-v1`.
- Consume one exact Semantic Diff report and zero or one compatible OTBM-E2E-008 impacted-selection report.
- Preserve before/after map and World Index provenance and SHA-pin every contributing report.
- Derive deterministic OTBM static-validator selections from explicit Semantic Diff finding kinds/categories and changed mechanic/position evidence only.
- Preserve exact Semantic Diff finding IDs on every selected static validation entry.
- Reuse OTBM-E2E-008 scenario decisions as-is; every skipped physical scenario must retain its exact non-impact evidence, and stale/bounded/truncated/missing physical-selection evidence must fail closed toward selection/manual review rather than authorize skipping.
- Never suppress unrelated non-OTBM suites.
- Keep generated reports outside Git and use create-new/no-clobber output semantics.

## Explicit non-goals

- No second OTBM parser/scanner, World Index, Semantic Diff engine, Script Resolution engine, pathfinder, renderer, writer/materializer, E2E selector, E2E runner or workflow.
- No map mutation, no dynamic Lua execution and no generated `.otbm`/`.widx`/report commits.
- No inference of non-impact from visual similarity, nearby coordinates, names, sprites or intent.
- No feature-specific E2E scenario generation, fixture design, client/server lifecycle, execution, runtime assertions or acceptance decisions.
- No suppression of repository-wide/non-OTBM validation based on this OTBM guard.

## Acceptance criteria

- Identical compatible inputs produce byte-stable semantic output ordering.
- Every accepted input is format-validated, SHA-pinned and tied to compatible exact before/after map provenance.
- Static validation selection is deterministic and traceable to exact Semantic Diff finding IDs.
- Unknown finding kinds/categories select a conservative generic OTBM static validation path rather than being silently ignored.
- Bounded/truncated/incomplete/stale/missing evidence never authorizes a skip.
- Physical scenario decisions are reused from OTBM-E2E-008 without reimplementing its route/scenario impact logic.
- Every skipped Physical E2E scenario retains the exact non-impact evidence from the existing impacted-selection contract.
- Output safety rejects symlinks/input collisions and does not clobber an existing report unless explicitly requested.
- Focused aggregation/schema/output-safety tests and relevant AI Agent/OTBM gates pass.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T14:15:00+02:00
head: eb2e09bc0778f0e88446638edf15c9069e771b11
branch: feat/otbm-qa-002-regression-guard-20260721
pr: none
status: implementing
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - tools/ai-agent/otbm_map_change_regression.py
  - tools/ai-agent/otbm_map_change_regression_tool.py
  - tools/ai-agent/test_otbm_map_change_regression.py
  - tools/ai-agent/test_otbm_map_change_regression_output_safety.py
  - tools/ai-agent/test_otbm_map_change_regression_schema.py
  - docs/ai-agent/OTBM_MAP_CHANGE_REGRESSION.md
  - docs/ai-agent/OTBM_MAP_CHANGE_REGRESSION.schema.json
  - docs/agents/tasks/active/CAN-20260721-otbm-qa-002-map-change-regression.md
proven:
  - OTBM-QA-001 feature PR #672 merged as 7ec75e672fdd1cc91d537e9f169a81f689d0858a and lifecycle PR #678 merged as eb2e09bc0778f0e88446638edf15c9069e771b11.
  - Current main at task start is eb2e09bc0778f0e88446638edf15c9069e771b11.
  - Roadmap identifies OTBM-QA-002 Map Change Regression Guard immediately after delivered OTBM-QA-001.
  - No open PR matching OTBM-QA and no otbm-qa branch was found in the fresh post-lifecycle preflight.
  - Existing Semantic OTBM Diff and OTBM-E2E-008 impacted selection are the canonical change/physical-impact evidence surfaces to reuse.
derived:
  - The smallest bounded v1 should compose existing reports and select validators; it must not rerun Semantic Diff or duplicate OTBM-E2E-008 selection logic.
unknown:
  - Exact Semantic Diff finding taxonomy and OTBM-E2E-008 selected/skipped evidence fields required for the conservative adapters until inspected in implementation.
conflicts: []
first_failure:
  marker: none
  evidence: No implementation validation has run yet.
rejected_hypotheses:
  - Recomputing Semantic Diff inside the regression guard.
  - Reimplementing route/scenario impact selection.
  - Treating bounded or missing evidence as proof of non-impact.
  - Suppressing unrelated non-OTBM suites from OTBM non-impact evidence.
changed_paths:
  - docs/agents/tasks/active/CAN-20260721-otbm-qa-002-map-change-regression.md
validation: []
blockers: []
next_action: Open a draft PR, bind this active task to it, inspect exact Semantic Diff and OTBM-E2E-008 schemas/implementations, then implement the smallest deterministic fail-closed regression-plan v1 with focused tests.
```
