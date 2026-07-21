---
task_id: CAN-20260721-otbm-qa-002-map-change-regression
program_id: CAN-PROGRAM-OTBM
status: ready
agent: "GPT-5.6 Thinking"
branch: feat/otbm-qa-002-regression-guard-20260721
base_branch: main
created: 2026-07-21
updated: 2026-07-21
last_verified_commit: "2e63c0abbeb3d6c01100fa401d7f6cd6ee9c8ab9"
risk: medium
related_issue: ""
related_pr: "679"
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

READY — bounded implementation is complete in PR #679; `ci:final-gate` is applied and no further feature/checkpoint commits are permitted after this final checkpoint commit.

## Goal

Turn exact existing Semantic OTBM Diff evidence plus existing OTBM-E2E-008 impacted-selection evidence into one deterministic, fail-closed impacted-validation plan without parsing/scanning OTBM, rebuilding World Indexes, pathfinding, running E2E, mutating maps or suppressing unrelated non-OTBM validation.

## Bounded slice

- Introduce `canary-otbm-map-change-regression-v1`.
- Consume one exact Semantic Diff report and zero or one compatible OTBM-E2E-008 impacted-selection report.
- Preserve before/after map and World Index provenance and SHA-pin every contributing report.
- Derive deterministic OTBM static-validator selection from explicit Semantic Diff evidence while retaining exact sampled finding IDs and explicit completeness.
- Skip static OTBM validation only when an exact full-index, non-truncated Semantic Diff proves zero OTBM findings.
- Reuse OTBM-E2E-008 scenario decisions as-is; every skipped physical scenario must retain exact non-impact evidence plus compatible SHA-pinned baseline route evidence.
- Fail closed so bounded, truncated, missing-position, unresolved, conflicting, invalid or unknown evidence selects more validation rather than less.
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
- Unknown finding kinds select conservative validation rather than being silently ignored.
- Bounded/truncated/incomplete/stale/missing evidence never authorizes a skip.
- Physical scenario decisions are reused from OTBM-E2E-008 without reimplementing its route/scenario impact logic.
- Every skipped Physical E2E scenario retains exact full-index non-impact evidence and compatible SHA-pinned baseline route evidence.
- Output safety rejects symlinks, duplicate inputs and input/output collisions and does not clobber an existing report unless explicitly requested.
- Focused aggregation, schema-contract and output-safety tests plus relevant AI Agent/OTBM gates pass.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T15:35:00+02:00
head: 2e63c0abbeb3d6c01100fa401d7f6cd6ee9c8ab9
branch: feat/otbm-qa-002-regression-guard-20260721
pr: 679
status: ready
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
  - docs/agents/MODULE_CATALOG.md
proven:
  - OTBM-QA-001 feature PR #672 merged as 7ec75e672fdd1cc91d537e9f169a81f689d0858a and lifecycle PR #678 merged as eb2e09bc0778f0e88446638edf15c9069e771b11.
  - Fresh post-lifecycle preflight selected OTBM-QA-002 as the next unrealized dependency-order package with no overlapping OTBM-QA PR or branch.
  - Main remains eb2e09bc0778f0e88446638edf15c9069e771b11 and has not advanced from the feature base during implementation.
  - PR #679 is the bounded implementation PR and changes exactly nine intended task/module/documentation/test paths.
  - Existing Semantic Diff and OTBM-E2E-008 impacted-selection schemas and implementations were inspected and are reused without recomputation.
  - The v1 core, CLI, focused regression tests, output-safety tests, schema-contract tests, versioned schema and contract documentation are present.
  - Missing impacted-selection evidence requires manual Physical E2E selection and authorizes no Physical E2E skip.
  - A skipped Physical E2E scenario requires exact full-index non-impact evidence and compatible SHA-pinned baseline route evidence from OTBM-E2E-008.
  - Static OTBM validators are skipped only for an exact full-index non-truncated zero-finding Semantic Diff; uncertainty selects validation.
  - MODULE_CATALOG diff adds exactly one OTBM Map Change Regression Guard row and preserves all existing catalogue text.
  - Pre-final head 2e63c0abbeb3d6c01100fa401d7f6cd6ee9c8ab9 passed CI run 29835159356, Agent Task Ownership run 29835158781, OTBM Map Tools run 29835158788 and AI Agent Tools run 29835158612.
  - ci:final-gate was applied before this final checkpoint commit.
derived:
  - The smallest complete v1 is a read-only validation-plan composer; it does not need another parser, World Index, Semantic Diff implementation, route selector or Physical E2E runner.
unknown:
  - Exact-final-head CI and focused-gate outcomes for this final checkpoint commit until GitHub Actions completes.
conflicts: []
first_failure:
  marker: otbm-map-change-regression-schema-test-ref
  evidence: Initial OTBM Map Tools and AI Agent Tools runs 29834450544 and 29834450477 failed because the schema-contract test read required directly from properties.source even though source is a $ref to $defs.sourceIdentity; the test was corrected and subsequent runs passed.
rejected_hypotheses:
  - Recomputing Semantic Diff inside the regression guard.
  - Reimplementing route/scenario impact selection.
  - Treating bounded or missing evidence as proof of non-impact.
  - Suppressing unrelated non-OTBM suites from OTBM non-impact evidence.
  - Inferring non-impact from visual similarity, names, proximity or intent.
changed_paths:
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260721-otbm-qa-002-map-change-regression.md
  - docs/ai-agent/OTBM_MAP_CHANGE_REGRESSION.md
  - docs/ai-agent/OTBM_MAP_CHANGE_REGRESSION.schema.json
  - tools/ai-agent/otbm_map_change_regression.py
  - tools/ai-agent/otbm_map_change_regression_tool.py
  - tools/ai-agent/test_otbm_map_change_regression.py
  - tools/ai-agent/test_otbm_map_change_regression_output_safety.py
  - tools/ai-agent/test_otbm_map_change_regression_schema.py
validation:
  - command: OTBM Map Tools run 29834450544
    result: FAIL
    evidence: Initial schema-contract test incorrectly dereferenced properties.source.required; implementation/schema JSON validation itself was not the failing assertion.
  - command: AI Agent Tools run 29834450477
    result: FAIL
    evidence: Same schema-contract test failure surfaced through full tools/ai-agent unit-test discovery.
  - command: CI run 29835159356
    result: PASS
    evidence: Repository CI passed on pre-final head 2e63c0abbeb3d6c01100fa401d7f6cd6ee9c8ab9.
  - command: Agent Task Ownership run 29835158781
    result: PASS
    evidence: Active-task ownership, owned path declarations and PR binding passed on pre-final head.
  - command: OTBM Map Tools run 29835158788
    result: PASS
    evidence: OTBM schema JSON validation and focused OTBM tests passed on pre-final head.
  - command: AI Agent Tools run 29835158612
    result: PASS
    evidence: Full tools/ai-agent unit-test discovery and AI-agent validation passed on pre-final head including QA-002 contract tests.
blockers: []
next_action: Mark PR #679 ready for review without changing files. Require exact-final-head CI, Agent Task Ownership, OTBM Map Tools and AI Agent Tools success on this checkpoint commit, confirm mergeability and zero review threads, then squash-merge #679 and perform lifecycle archive in a separate bounded PR before starting the next roadmap package.
```
