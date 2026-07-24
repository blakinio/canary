---
task_id: CAN-20260724-e2e-qri-004-coverage-dashboard
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-QRI-004
status: completed
agent: "GPT-5.6 Thinking"
branch: docs/e2e-qri-004-compact-handover
base_branch: main
created: 2026-07-24
updated: 2026-07-24
last_verified_commit: "e8ed71384d1d0bf00fd98dbeb91bb852a7e064e0"
risk: medium
related_issue: ""
related_pr: "885, 900"
depends_on:
  - merged and lifecycle-closed E2E-QRI-005 result envelope
  - merged and lifecycle-closed E2E-QRI-006 cleanup certification
blocks:
  - E2E-QRI-022 stability certification factual baseline
owned_paths:
  exclusive: []
  shared: []
  read_only: []
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

# CAN-20260724 — E2E-QRI-004 factual coverage dashboard

## Completion

- Final status: completed.
- Delivery PR: #885.
- Lifecycle closure PR: #900.
- Exact final delivery PR head: `8ac86527ee1ab75c1dc843688a4a8a5e2254bd05`.
- Squash merge commit: `e8ed71384d1d0bf00fd98dbeb91bb852a7e064e0`.
- Final Agent Task Ownership: PASS, run `30125061157`.
- Final full `ci:final-gate` CI: PASS, run `30125061503`.
- Final `autofix.ci`: PASS, run `30125061109`.
- Final Universal Agent E2E: PASS, run `30125061437`.

## Delivered contract

- `canary-universal-e2e-coverage-dashboard-v1`, schema version 1, provides deterministic JSON and Markdown views generated from one normalized factual report.
- Current scenario rows reuse canonical `tools/e2e/run_agent_e2e.py` discovery over `tests/e2e/scenarios/**/*.json`; registration defines row population but never proves execution.
- Retained evidence contributes only after validation as `canary-universal-e2e-result-envelope-v1` schema version 3.
- Cleanup contributes only after complete `canary-universal-e2e-cleanup-certification-v1` schema version 1 validation and exact agreement with the independent cleanup quality dimension.
- Strongest M0-M5 maturity is selected only from successful valid evidence. Failed, cancelled and timed-out runs remain visible but cannot promote maturity.
- The report preserves latest run, last success, last failure, exact revisions and timestamps, nine orthogonal quality dimensions, invalid evidence, warnings, unknowns, freshness and deterministic coverage gaps.
- Absolute paths, parent traversal, malformed paths and evidence symlinks escaping the supplied root fail closed without leaking host paths.
- The package adds no runner, lifecycle, workflow, artifact downloader, retention policy, result-envelope implementation or runtime-state mutation.

## Validation

- `python3 -m py_compile tools/e2e/coverage_dashboard.py tests/e2e/test_coverage_dashboard.py`: PASS.
- `python3 -m unittest -v tests/e2e/test_coverage_dashboard.py`: PASS, 15 of 15 tests on WSL2 Ubuntu against the repository's actual canonical result-envelope, cleanup-certification and scenario-discovery modules.
- `python3 -m json.tool docs/e2e/E2E_COVERAGE_DASHBOARD.schema.json`: PASS.
- Native Windows execution remains non-canonical for the POSIX cleanup lifecycle because `os.killpg` is unavailable; this platform boundary was retained rather than misreported as Linux contract failure.
- Exact final-head Agent Task Ownership, autofix, full CI and Universal Agent E2E all passed before squash merge.

## Failure history retained

- Agent Task Ownership run `30114306996` rejected unsupported validation result `PASS_WITH_BOUNDARY`; the checkpoint was repaired to use the supported `PASS` state while preserving the boundary in evidence and unknowns.
- Later ownership runs rejected an overlong proven list and an invalid active-record lifecycle status; the checkpoint was compacted and restored to `status: implementing` while its phase remained `validating`.
- The focused historical freshness fixture initially used inconsistent start and end timestamps; the fixture was corrected and all 15 tests then passed.
- Failed and superseded attempts remain documented and were not hidden by successful reruns.

## Evidence boundaries

- The dashboard consumes only explicitly supplied local extracted artifact roots; artifact selection, download, scheduling and retention remain external to this contract.
- M0-M5 maturity and the nine quality dimensions remain independent factual fields; no opaque aggregate score is calculated.
- The exact repository-wide scenario count and retained-evidence completeness depend on the selected artifact population and remain unknown until the dashboard is run for a chosen baseline.

## Lifecycle closure

The delivery package is merged and all required final-head checks passed. Lifecycle closure PR #900 archives this record, releases every E2E-QRI-004 owned path and allows E2E-QRI-022 to consume the factual dashboard contract without reopening this task.
