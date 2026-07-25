---
task_id: CAN-20260725-e2e-qri-022-stability-certification
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-QRI-022
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/e2e-qri-022-stability-certification
base_branch: main
created: 2026-07-25
updated: 2026-07-25
last_verified_commit: "a6858acd390c0bbb469d0ccbfe5c48419cdb1435"
risk: medium
related_issue: ""
related_pr: "912"
depends_on:
  - "E2E-QRI-004 factual coverage dashboard merged in PR #885 and lifecycle-closed in PR #900"
  - "E2E-QRI-005 result envelope schema v3 merged in PR #850 and lifecycle-closed in PR #861"
  - "E2E-QRI-006 cleanup certification schema v1 merged in PR #871 and lifecycle-closed in PR #881"
blocks:
  - "factual stability evidence for release-certification scenario selection"
  - "later E2E-QRI-023 soak and E2E-QRI-024 performance trend packages"
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260725-e2e-qri-022-stability-certification.md
    - tools/e2e/stability_certification.py
    - tests/e2e/test_stability_certification.py
    - docs/e2e/E2E_STABILITY_CERTIFICATION.md
    - docs/e2e/E2E_STABILITY_CERTIFICATION.schema.json
    - .github/workflows/e2e-stability-certification.yml
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
    - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
  read_only:
    - tools/e2e/coverage_dashboard.py
    - tools/e2e/result_envelope.py
    - tools/e2e/result_envelope_impl.py
    - tools/e2e/cleanup_certification.py
    - tools/e2e/run_agent_e2e.py
    - tests/e2e/scenarios/**
    - docs/architecture/universal-e2e-quality-resilience-roadmap.md
modules_touched:
  - Universal E2E stability certification
reuses:
  - canary-universal-e2e-result-envelope-v1 schema version 3
  - canary-universal-e2e-cleanup-certification-v1 schema version 1
  - canary-universal-e2e-coverage-dashboard-v1 evidence discovery and normalization
public_interfaces:
  - canary-universal-e2e-stability-certification-v1
cross_repo_tasks: []
---

# E2E-QRI-022 flake and stability certification

## Goal

Deliver one deterministic, read-only certification contract over explicitly supplied retained Universal E2E result envelopes. The package preserves every attempt and classifies repeatability without creating a second runner, scheduling workflow, artifact downloader, retention policy or hidden retry layer.

## Scope

- validate exact schema-v3 result envelopes through the existing coverage-dashboard evidence boundary;
- group only directly comparable runs by exact scenario and execution provenance;
- report run/pass/failure counts, success ratio, failure-class distribution, cleanup failures, duration distribution and first-divergence frequency;
- classify a mixed result such as 9/10 as `unstable`, never as `pass`;
- require an explicit minimum run count before certification;
- emit deterministic JSON and Markdown from one normalized report;
- preserve invalid inputs, duplicate run identities, missing provenance and UNKNOWN states.

## Non-goals

- no scenario execution or automatic retries;
- no GitHub artifact discovery/download or retention management;
- no nightly schedule in this contract PR;
- no opaque score or inferred success from registration/documentation/artifact presence;
- no modification of the canonical runner, result envelope or cleanup certification;
- no claim that contract tests constitute physical stability certification.

## Acceptance criteria

- [x] Current `main`, QRI-004 closure, roadmap dependencies and open PR overlap are revalidated.
- [x] One dedicated branch and task record claim exact bounded paths.
- [x] PR #912 is linked, ready for review and marked for the exact final-head gate.
- [x] Versioned implementation, strict schema and operator documentation are present.
- [x] Every supplied attempt remains visible and duplicate run identities fail closed.
- [x] Comparability requires exact scenario, server revision, client revision, datapack and execution tier.
- [x] `pass` requires the explicit minimum run count and every counted attempt to be a clean pass.
- [x] Mixed evidence is `unstable`; all failures are `fail`; insufficient evidence is `not-evaluated`; incomplete evidence is `blocked`.
- [x] Cleanup certification remains independent and cleanup failure prevents a clean pass.
- [x] Duration percentiles and exact failure/divergence distributions are deterministic and validated against tampering.
- [x] Unsafe source paths, inconsistent cell IDs/counts/distributions and unsupported tiers fail closed.
- [x] Focused canonical-module tests, bytecode compilation and schema parsing pass.
- [x] Catalogue, programme and changelog records are updated narrowly.
- [x] Temporary integration/hardening files are absent from the final nine-file diff.
- [ ] Exact final-head Ownership, focused validation, CI and Universal Agent E2E pass before squash merge.
- [x] A physical repeated-run baseline remains a separate follow-up and is not claimed by this package.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T12:20:00+02:00
head: a6858acd390c0bbb469d0ccbfe5c48419cdb1435
branch: feat/e2e-qri-022-stability-certification
pr: 912
status: validating
context_routes:
  - agent-governance
  - universal-e2e
owned_paths:
  - docs/agents/tasks/active/CAN-20260725-e2e-qri-022-stability-certification.md
  - tools/e2e/stability_certification.py
  - tests/e2e/test_stability_certification.py
  - docs/e2e/E2E_STABILITY_CERTIFICATION.md
  - docs/e2e/E2E_STABILITY_CERTIFICATION.schema.json
  - .github/workflows/e2e-stability-certification.yml
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
  - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
proven:
  - QRI-004, QRI-005 and QRI-006 provide the canonical discovery, schema-v3 result-envelope and schema-v1 cleanup-certification boundaries reused by this package.
  - The contract groups exact scenario/server/client/datapack/tier cells, requires an explicit minimum run count and preserves every attempt.
  - Clean pass requires gameplay success plus complete cleanup certification; 9/10 is unstable and historical success without cleanup proof is blocked.
  - Duplicate identities, future evidence, missing provenance, unsafe paths and evidence-root escapes fail closed without host-path leakage.
  - Runtime validation recomputes cell IDs, attempt identities, missing provenance, distributions, duration summaries, cleanup counts and report summary.
  - Exact-head Stability Certification, Agent Task Ownership, full CI and autofix passed on a6858acd390c0bbb469d0ccbfe5c48419cdb1435.
  - Universal Agent E2E run 30151582097 built the exact Canary head and, after a selective job rerun, built and verified the controlled OTClient successfully.
  - The selective rerun produced the OTClient artifact in the new attempt while the Canary artifact remained from the original attempt; the physical job then failed at `Download exact-head Canary binary` before scenario execution.
  - PR #912 has exactly nine intended changed files and no comments, reviews or unresolved review threads in the latest completed audit.
derived:
  - Reusing the QRI-004 evidence boundary avoids a second parser while preserving its fail-closed path rules.
  - The failed physical rerun is an Actions attempt/artifact boundary rather than evidence of a QRI-022 implementation defect; one fresh workflow run is required so both binaries are produced in the same attempt.
  - Physical repeated-run collection, artifact selection and scheduling remain separate from the certification contract.
unknown:
  - Exact workflow outcomes on the fresh final-head run triggered by this checkpoint-only commit.
  - The first selected physical scenario and retained artifact population for a real stability baseline.
conflicts: []
first_failure:
  marker: final-checkpoint-unsupported-validation-result
  evidence: Agent Task Ownership run 30151490550 rejected validation item 5 because `UNKNOWN` is unsupported; the checkpoint was repaired to use `NOT_RUN`. Later final-gate run 30151582097 exposed a separate cross-attempt artifact boundary without changing implementation scope.
rejected_hypotheses:
  - Treating the dashboard's latest stability dimension as repeated-run certification.
  - Hiding failed attempts behind automatic retry or selecting only successful artifacts.
  - Treating the cross-attempt artifact-download failure as a stability-certification implementation failure.
  - Creating another physical runner, downloader, retention policy or scheduled execution path.
changed_paths:
  - .github/workflows/e2e-stability-certification.yml
  - docs/agents/CHANGELOG.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
  - docs/agents/tasks/active/CAN-20260725-e2e-qri-022-stability-certification.md
  - docs/e2e/E2E_STABILITY_CERTIFICATION.md
  - docs/e2e/E2E_STABILITY_CERTIFICATION.schema.json
  - tests/e2e/test_stability_certification.py
  - tools/e2e/stability_certification.py
validation:
  - command: Universal E2E Stability Certification workflow run 30151582013
    result: PASS
    evidence: exact source/test compilation, hardened canonical-module suite and schema parsing passed on a6858acd390c0bbb469d0ccbfe5c48419cdb1435
  - command: Agent Task Ownership workflow run 30151582012
    result: PASS
    evidence: active ownership and checkpoint structure passed on a6858acd390c0bbb469d0ccbfe5c48419cdb1435
  - command: CI workflow run 30151582092
    result: PASS
    evidence: full ci:final-gate matrix passed on a6858acd390c0bbb469d0ccbfe5c48419cdb1435
  - command: autofix workflow run 30151582031
    result: PASS
    evidence: autofix completed successfully on a6858acd390c0bbb469d0ccbfe5c48419cdb1435
  - command: Universal Agent E2E workflow run 30151582097
    result: FAIL
    evidence: exact Canary and controlled OTClient builds passed, but the selective rerun split binary artifacts across attempts and the physical job failed before execution while downloading the Canary artifact
  - command: PR #912 comments, reviews and review threads audit
    result: PASS
    evidence: no comments, reviews or unresolved threads were present in the latest completed audit
  - command: fresh exact final-head gate after this checkpoint-only commit
    result: NOT_RUN
    evidence: ci:final-gate remains applied; the new pull_request workflows have not yet completed
blockers:
  - A real multi-run physical stability baseline requires a separately selected scenario, retained artifact population and execution package after this contract merges.
next_action: Verify the fresh exact-head Stability Certification, Ownership, full CI, autofix and Universal Agent E2E; squash-merge PR #912 only if every required check passes and no review blocker appears.
```
