---
task_id: CAN-20260724-e2e-qri-004-coverage-dashboard
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-QRI-004
status: implementing
agent: "GPT-5.6 Thinking"
branch: docs/e2e-qri-004-compact-handover
base_branch: main
created: 2026-07-24
updated: 2026-07-24
last_verified_commit: "c010a05ed6fe69bf8bbc01a9ae2a5d0f749ea0a1"
risk: medium
related_issue: ""
related_pr: "885"
depends_on:
  - E2E-QRI-005 merged result envelope and lifecycle closure
  - E2E-QRI-006 merged cleanup certification and lifecycle closure
blocks:
  - E2E-QRI-022 stability certification factual baseline
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260724-e2e-qri-004-coverage-dashboard.md
    - tools/e2e/coverage_dashboard.py
    - tests/e2e/test_coverage_dashboard.py
    - docs/e2e/E2E_COVERAGE_DASHBOARD.md
    - docs/e2e/E2E_COVERAGE_DASHBOARD.schema.json
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
    - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
  read_only:
    - docs/architecture/universal-e2e-quality-resilience-roadmap.md
    - docs/architecture/universal-e2e-gameplay-validation.md
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/result_envelope.py
    - tools/e2e/result_envelope_impl.py
    - tools/e2e/cleanup_certification.py
    - tests/e2e/scenarios/**
modules_touched:
  - Universal E2E factual coverage dashboard
reuses:
  - canary-universal-e2e-result-envelope-v1 schema version 3
  - canary-universal-e2e-cleanup-certification-v1 schema version 1
  - tools/e2e/run_agent_e2e.py scenario discovery and validation
public_interfaces:
  - canary-universal-e2e-coverage-dashboard-v1
cross_repo_tasks: []
---

# E2E-QRI-004 factual coverage dashboard

## Goal

Deliver a bounded factual M0-M5 and orthogonal quality-dimension coverage dashboard that consumes existing Universal E2E evidence contracts without creating another runner, workflow, result envelope, evidence collector or inferred coverage model.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T19:18:00+02:00
head: c010a05ed6fe69bf8bbc01a9ae2a5d0f749ea0a1
branch: docs/e2e-qri-004-compact-handover
pr: 885
status: implementing
context_routes:
  - agent-governance
  - universal-e2e
owned_paths:
  - docs/agents/tasks/active/CAN-20260724-e2e-qri-004-coverage-dashboard.md
  - tools/e2e/coverage_dashboard.py
  - tests/e2e/test_coverage_dashboard.py
  - docs/e2e/E2E_COVERAGE_DASHBOARD.md
  - docs/e2e/E2E_COVERAGE_DASHBOARD.schema.json
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
  - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
proven:
  - E2E-QRI-005 delivery PR 850, lifecycle PR 861 and discovery PR 869 established the single schema-v3 canary-universal-e2e-result-envelope-v1 contract.
  - E2E-QRI-006 delivery PR 871, hardening PR 875 and lifecycle PR 881 established canary-universal-e2e-cleanup-certification-v1 and physically proved cleanup 18 of 18 with basename-only client events.
  - E2E-QRI-001, E2E-QRI-002 and E2E-QRI-003 are delivered foundations, including the representative promotion-combat-persistence M4 sentinel.
  - The E2E automation programme names E2E-QRI-004 as the next recommended package before E2E-QRI-022.
  - The result envelope schema v3 validates exact run and scenario identity, M0-M5 maturity, nine orthogonal quality dimensions, attempts, last-success and first-failure evidence, warnings and explicit unknowns.
  - Cleanup certification is embedded into schema-v3 result.json only under the exact cleanup schema-v1 contract and independently promotes only the cleanup quality dimension.
  - The canonical scenario inventory is filesystem discovery through tools/e2e/run_agent_e2e.py over tests/e2e/scenarios/**/*.json; there is no separate scenario registry file in that interface.
  - The existing OTBM-QA-005 factual dashboard is subsystem-specific but establishes a reusable fail-closed reporting pattern: explicit contracts, independent dimensions, deterministic gaps and not-evaluated missing evidence.
  - PR 885 now contains the pure coverage aggregator, focused unit tests, schema and operator documentation without runner, lifecycle or workflow changes.
  - The implemented report preserves exact selected run/revision/tier/timestamp evidence, last success, last failure, invalid inputs, warnings, unknowns and explicit freshness policy; a failed declared higher M-level cannot promote strongest proven maturity.
derived:
  - Registration may define the reviewed row population but cannot prove execution; strongest maturity comes only from successful valid schema-v3 envelopes.
  - The stable grouping key for v1 is the canonical scenario key suite/scenario_id; every retained evidence reference preserves exact run, revision, tier and timestamp fields.
  - Freshness is evaluated only against an explicit as-of time and optional stale-after policy; without a threshold freshness remains not-evaluated.
  - V1 consumes explicit local extracted evidence roots and reports the supplied evidence boundary; GitHub artifact discovery, download, scheduling and retention policy remain outside this pure aggregation contract.
unknown:
  - The exact current registered scenario count and which scenarios have complete retained schema-v3 result and cleanup evidence until the aggregator runs in an exact checkout against a selected retained artifact population.
  - Which retained workflow artifact set will be selected for the first repository-wide factual baseline.
  - Whether a later scheduled evidence-collection seam is justified after the first explicit extracted-artifact baseline.
conflicts: []
first_failure:
  marker: none
  evidence: Implementation is committed; exact focused test and final-head validation are pending.
rejected_hypotheses:
  - Treat scenario registration, documentation or result artifact presence as proof of executed M0-M5 or quality-dimension coverage.
  - Create a second E2E runner, workflow, result envelope, cleanup evidence path or GitHub artifact collector inside the first dashboard contract.
  - Reuse the OTBM-QA-005 implementation directly; its selectors, evidence formats and dimensions are OTBM-specific, while only its fail-closed reporting pattern is applicable.
changed_paths:
  - docs/agents/tasks/active/CAN-20260724-e2e-qri-004-coverage-dashboard.md
  - tools/e2e/coverage_dashboard.py
  - tests/e2e/test_coverage_dashboard.py
  - docs/e2e/E2E_COVERAGE_DASHBOARD.md
  - docs/e2e/E2E_COVERAGE_DASHBOARD.schema.json
validation:
  - command: live E2E-QRI programme, dependency and roadmap review
    result: PASS
    evidence: QRI-005 and QRI-006 are merged and lifecycle-closed; the roadmap requires a factual JSON and human-readable retained-evidence view and recommends QRI-004 next.
  - command: live PR, head, CI and ownership verification
    result: PASS
    evidence: PR 885 was open and draft on c010a05ed6fe69bf8bbc01a9ae2a5d0f749ea0a1; Agent Task Ownership and CI succeeded, but incremental CI skipped Fast Checks before the ci:final-gate label was applied.
  - command: result-envelope, cleanup, scenario-discovery and existing-dashboard reuse inventory
    result: PASS
    evidence: Exact canonical contracts and consumer fields were identified; scenario rows resolve through existing discover(); OTBM-QA-005 was reviewed as a pattern but rejected as a direct reusable implementation.
  - command: docs/agents/KNOWN_RISKS.md and docs/agents/BUILD_TEST_MATRIX.md targeted review
    result: PASS
    evidence: Generated reports stay outside Git; Python tool changes require bytecode compilation and focused unit tests, with no Canary compilation unless compiled integration changes.
blockers: []
next_action: Run exact-head focused Python, bytecode, schema and final-gate CI validation, repair the first owned failure if any, then complete shared discovery documentation and the final checkpoint.
```
