---
task_id: CAN-20260721-otbm-qa-005-coverage-dashboard
program_id: CAN-PROGRAM-OTBM
status: complete
agent: "GPT-5.6 Thinking"
branch: feat/otbm-qa-005-coverage-dashboard-20260721
base_branch: main
created: 2026-07-21
updated: 2026-07-21
last_verified_commit: "1387ca873ad159079d2d68899485dd9b91c167c4"
risk: medium
related_issue: ""
related_pr: "688"
depends_on:
  - CAN-20260721-otbm-qa-004-reviewed-candidate-repair complete
blocks:
  - OTBM-QA-006 region and quest certification
owned_paths:
  exclusive: []
  shared: []
  read_only:
    - tools/ai-agent/otbm_coverage_dashboard.py
    - tools/ai-agent/otbm_coverage_dashboard_tool.py
    - docs/ai-agent/OTBM_COVERAGE_DASHBOARD.md
    - docs/ai-agent/OTBM_COVERAGE_DASHBOARD_TARGETS.schema.json
    - docs/ai-agent/OTBM_COVERAGE_DASHBOARD.schema.json
modules_touched:
  - otbm-coverage-dashboard
reuses:
  - OTBM-E2E coverage matrix
  - OTBM Map Quality Gate
  - OTBM World Health Aggregator
  - Quest Map Validation
  - canonical executable OTBM route plans
  - OTBM-QA-004 reviewed candidate repair evidence
public_interfaces:
  - canary-otbm-coverage-dashboard-targets-v1
  - canary-otbm-coverage-dashboard-v1
cross_repo_tasks: []
---

# CAN-20260721 — OTBM-QA-005 Coverage Dashboard and Evidence Model

## Status

COMPLETE — bounded implementation merged through feature PR #688.

## Delivered

- Added reviewed `canary-otbm-coverage-dashboard-targets-v1` and deterministic read-only `canary-otbm-coverage-dashboard-v1` contracts.
- Added reviewed target kinds `world`, `region`, `landmark-route`, `quest` and `mechanic-set` without inferring target membership or criticality from names, proximity, sprites or chat history.
- Reused the existing OTBM-E2E Coverage Matrix for exact reviewed-mechanic indexed, script, reachability, Physical E2E and stale-provenance evidence.
- Reused compatible Map Quality and World Health evidence without recomputing either report.
- Added optional exact-SHA-bound Quest Map Validation, canonical executable route-plan and QA-004 reviewed-candidate-repair evidence bindings.
- Preserved independent dimensions for exact-map indexing, source correlation, script resolution, static reachability, interaction resolution, static quality, executable-route coverage, Physical E2E proof, candidate-map validation and stale evidence.
- Kept missing optional evidence as `not-evaluated`; stale evidence is never promoted to current proof.
- Added transparent target-declared `requiredDimensions` / `requirementsSatisfied` without assigning QA-006 C0-C7 certification levels or an opaque score gate.
- Added deterministic coverage gaps, fail-closed provenance validation, create-new/no-clobber output safety, schemas, contract documentation and focused aggregation/schema/output-safety tests.
- Introduced no OTBM parser/scanner, World Index, Script Resolution engine, pathfinder, renderer, writer/materializer, route generator, validator duplication, Physical E2E runner or workflow.

## Merge evidence

- Feature PR: #688 — `feat(otbm): add factual coverage dashboard`.
- Final feature head: `98fec7830eff2faf3faa671d7e39840dcf24ec5e`.
- Squash merge: `1387ca873ad159079d2d68899485dd9b91c167c4`.
- Exact-final-head CI run `29850882428`: success.
- Exact-head Agent Task Ownership run `29850608294`: success.
- Exact-head OTBM Map Tools run `29850608410`: success.
- Exact-head AI Agent Tools run `29850608578`: success.
- Feature PR changed exactly ten intended paths; `MODULE_CATALOG` changed by exactly one added QA-005 row.
- Final review audit found zero inline review threads and zero review submissions.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T19:20:00+02:00
head: 98fec7830eff2faf3faa671d7e39840dcf24ec5e
branch: feat/otbm-qa-005-coverage-dashboard-20260721
pr: 688
status: complete
context_routes:
  - otbm
  - agent-governance
owned_paths: []
proven:
  - PR #688 merged to main as 1387ca873ad159079d2d68899485dd9b91c167c4.
  - Exact-final-head CI run 29850882428 passed on 98fec7830eff2faf3faa671d7e39840dcf24ec5e.
  - Agent Task Ownership run 29850608294 passed on the same final feature head.
  - OTBM Map Tools run 29850608410 passed on the same final feature head.
  - AI Agent Tools run 29850608578 passed on the same final feature head.
  - PR #688 changed exactly ten intended paths and its MODULE_CATALOG diff added exactly one new row.
  - PR #688 had zero inline review threads and zero review submissions at final review audit.
  - canary-otbm-coverage-dashboard-targets-v1 and canary-otbm-coverage-dashboard-v1 are now delivered OTBM-QA-005 public contracts.
  - The implementation remains read-only evidence aggregation and does not assign formal QA-006 certification levels.
derived:
  - After lifecycle archive completion, OTBM-QA-006 may be considered only after a fresh live-state and dependency-order preflight.
unknown: []
conflicts: []
first_failure:
  marker: none
  evidence: No unresolved feature validation failure remained at merge.
changed_paths:
  - docs/agents/tasks/active/CAN-20260721-otbm-qa-005-coverage-dashboard.md
  - docs/agents/tasks/archive/CAN-20260721-otbm-qa-005-coverage-dashboard.md
validation:
  - command: GitHub Actions CI run 29850882428
    result: PASS
    evidence: Exact-final-head full repository CI completed successfully before feature merge.
  - command: GitHub Actions Agent Task Ownership run 29850608294
    result: PASS
    evidence: Exact-head task ownership validation passed.
  - command: GitHub Actions OTBM Map Tools run 29850608410
    result: PASS
    evidence: Exact-head OTBM focused validation passed.
  - command: GitHub Actions AI Agent Tools run 29850608578
    result: PASS
    evidence: Exact-head AI-agent unit and validation suite passed.
blockers: []
next_action: Complete the lifecycle-only active-to-archive PR. After it merges, perform a fresh live-state preflight before starting any successor package.
```
