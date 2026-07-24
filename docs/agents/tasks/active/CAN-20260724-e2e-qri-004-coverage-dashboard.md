---
task_id: CAN-20260724-e2e-qri-004-coverage-dashboard
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-QRI-004
status: validating
agent: "GPT-5.6 Thinking"
branch: docs/e2e-qri-004-compact-handover
base_branch: main
created: 2026-07-24
updated: 2026-07-24
last_verified_commit: "1f93e0c3bd278699c797de65166a37f4f0abec0c"
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
updated_at: 2026-07-24T22:39:10+02:00
head: 1f93e0c3bd278699c797de65166a37f4f0abec0c
branch: docs/e2e-qri-004-compact-handover
pr: 885
status: validating
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
proven:
  - E2E-QRI-005 delivery PR 850, lifecycle PR 861 and discovery PR 869 established the single schema-v3 canary-universal-e2e-result-envelope-v1 contract.
  - E2E-QRI-006 delivery PR 871, hardening PR 875 and lifecycle PR 881 established canary-universal-e2e-cleanup-certification-v1 and physically proved cleanup 18 of 18 with basename-only client events.
  - E2E-QRI-001, E2E-QRI-002 and E2E-QRI-003 are delivered foundations, including the representative promotion-combat-persistence M4 sentinel.
  - The E2E automation programme names E2E-QRI-004 as the next recommended package before E2E-QRI-022.
  - The result envelope schema v3 validates exact run and scenario identity, M0-M5 maturity, nine orthogonal quality dimensions, attempts, last-success and first-failure evidence, warnings and explicit unknowns.
  - Cleanup certification is embedded into schema-v3 result.json only under the exact cleanup schema-v1 contract and independently promotes only the cleanup quality dimension.
  - The canonical scenario inventory is filesystem discovery through tools/e2e/run_agent_e2e.py over tests/e2e/scenarios/**/*.json; there is no separate scenario registry file in that interface.
  - The existing OTBM-QA-005 factual dashboard is subsystem-specific but establishes a reusable fail-closed reporting pattern: explicit contracts, independent dimensions, deterministic gaps and not-evaluated missing evidence.
  - PR 885 contains a pure deterministic JSON and Markdown coverage consumer, focused tests, schema and operator documentation without runner, lifecycle, workflow, artifact-download or runtime-state changes.
  - The report preserves exact selected run/revision/tier/timestamp evidence, latest run, last success, last failure, invalid inputs, warnings, unknowns and explicit freshness policy.
  - Strongest M0-M5 maturity is selected only from successful valid schema-v3 envelopes; a failed declared higher M-level remains visible but cannot promote coverage.
  - Cleanup is accepted only after full cleanup schema-v1 validation and exact agreement with the independent cleanup quality dimension.
  - Evidence paths are normalized repository-independent references; absolute paths, parent traversal and result symlinks escaping an evidence root are rejected or retained as invalid evidence without leaking host paths.
  - The focused suite passes 15 of 15 against the repository's actual canonical result-envelope, cleanup-certification and scenario-discovery modules under WSL2 Ubuntu; no validator stubs or reconstructed blobs are involved.
  - The shared module catalogue now records the dashboard contract, paths and fail-closed reuse boundary adjacent to its result-envelope and cleanup-certification dependencies.
  - Universal Agent E2E run 30114455072 completed successfully on PR head 3dc2ac0dae6d155f4a93844a042d3ed8ecbea3fb, including the physical client login/relog job and Required physical E2E aggregator.
derived:
  - Registration defines the reviewed row population but cannot prove execution; retained valid evidence alone supplies maturity and quality states.
  - The stable v1 grouping key is suite/scenario_id; selected evidence references preserve exact run, revision, execution tier and timestamp fields.
  - Freshness is evaluated only against explicit as-of and optional stale-after values; without a threshold it remains not-evaluated.
  - V1 consumes explicit local extracted evidence roots and reports that supplied boundary; GitHub artifact discovery, download, scheduling and retention remain outside the aggregation contract.
unknown:
  - The exact current registered scenario count and which scenarios have complete retained schema-v3 result and cleanup evidence until the aggregator runs in an exact checkout against a selected retained artifact population.
  - Which retained workflow artifact set will be selected for the first repository-wide factual baseline.
  - Whether a later scheduled evidence-collection seam is justified after the first explicit extracted-artifact baseline.
  - Exact final-head Ownership, CI, Universal Agent E2E and applicable autofix outcomes after the catalogue/checkpoint commit.
conflicts: []
first_failure:
  marker: checkpoint-validation-unsupported-result
  evidence: Agent Task Ownership run 30114306996 rejected validation item 4 because PASS_WITH_BOUNDARY is not a supported checkpoint result; this checkpoint now uses PASS and preserves the boundary in evidence and UNKNOWN.
rejected_hypotheses:
  - Treat scenario registration, documentation or result artifact presence as proof of executed M0-M5 or quality-dimension coverage.
  - Create a second E2E runner, workflow, result envelope, cleanup evidence path or GitHub artifact collector inside the first dashboard contract.
  - Reuse the OTBM-QA-005 implementation directly; its selectors, evidence formats and dimensions are OTBM-specific, while only its fail-closed reporting pattern is applicable.
  - Accept an exact cleanup contract header without validating the complete cleanup schema-v1 body.
changed_paths:
  - docs/agents/tasks/active/CAN-20260724-e2e-qri-004-coverage-dashboard.md
  - docs/agents/MODULE_CATALOG.md
  - tools/e2e/coverage_dashboard.py
  - tests/e2e/test_coverage_dashboard.py
  - docs/e2e/E2E_COVERAGE_DASHBOARD.md
  - docs/e2e/E2E_COVERAGE_DASHBOARD.schema.json
validation:
  - command: live E2E-QRI programme, dependency and roadmap review
    result: PASS
    evidence: QRI-005 and QRI-006 are merged and lifecycle-closed; the roadmap requires factual JSON plus a human-readable retained-evidence view and recommends QRI-004 next.
  - command: live PR, ownership and exact-head verification
    result: PASS
    evidence: PR 885 is open, non-draft and mergeable; the preceding exact-head ownership run exposed and localized the unsupported checkpoint result before this repair.
  - command: python3 -m py_compile tools/e2e/coverage_dashboard.py tests/e2e/test_coverage_dashboard.py
    result: PASS
    evidence: Exact reconstructed blobs matching the GitHub source and test SHA-1 values compiled successfully.
  - command: python3 -m unittest -v tests/e2e/test_coverage_dashboard.py
    result: PASS
    evidence: 15 of 15 focused tests passed in WSL2 Ubuntu with Python 3.14.4 against the checked-out repository's actual canonical result-envelope, cleanup-certification and scenario-discovery modules; the symlink escape case also executed and passed.
  - command: python -m unittest -v tests/e2e/test_coverage_dashboard.py
    result: FAIL
    evidence: Native Windows Python 3.12.0 reached the actual canonical cleanup module but that POSIX lifecycle module cannot import because os.killpg is unavailable; 7 errors, 1 assertion mismatch and 1 platform-specific skip were observed. The dashboard's canonical physical-E2E execution environment is Linux, where the complete suite passes.
  - command: python3 -m json.tool docs/e2e/E2E_COVERAGE_DASHBOARD.schema.json
    result: PASS
    evidence: Parsed local reconstruction matched the exact GitHub schema blob SHA-1 46769ffed08efe2e172f36c548caa3cb8663eadd.
  - command: result-envelope, cleanup, scenario-discovery and existing-dashboard reuse inventory
    result: PASS
    evidence: Exact canonical contracts and consumer fields were identified; scenario rows resolve through existing discover(); OTBM-QA-005 was reviewed as a pattern but rejected as a direct reusable implementation.
  - command: docs/agents/KNOWN_RISKS.md and docs/agents/BUILD_TEST_MATRIX.md targeted review
    result: PASS
    evidence: Generated reports stay outside Git; Python tool changes require bytecode compilation and focused unit tests, with no Canary compilation required by the changed implementation boundary.
  - command: Agent Task Ownership run 30124758665
    result: FAIL
    evidence: Exact head 1f93e0c3bd278699c797de65166a37f4f0abec0c exceeded the checkpoint compactness limit with 17 proven items; the superseded reconstructed-blob evidence was removed so the next exact head has the allowed 16.
blockers:
  - Exact final-head Ownership, CI, Universal Agent E2E and applicable autofix must pass before merge.
  - Final review-thread and changed-file audits remain pending on the frozen final head.
next_action: Commit and push this catalogue/checkpoint finalization without further source changes, require exact-final-head Ownership, CI, Universal Agent E2E and applicable autofix, then perform the review and expected-head squash-merge audit.
```
