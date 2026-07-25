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
last_verified_commit: "218a3f957a58b4d1a67f62d2cfb96f76241ae0cc"
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
    - .github/workflows/e2e-qri-022-integration.yml
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

Deliver one deterministic, read-only certification contract over explicitly supplied retained Universal E2E result envelopes. The package must preserve every attempt and classify repeatability without creating a second runner, scheduling workflow, artifact downloader, retention policy or hidden retry layer.

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
- no claim that synthetic tests constitute physical stability certification.

## Acceptance criteria

- [x] Current `main`, QRI-004 closure, roadmap dependencies and open PR overlap are revalidated.
- [x] One dedicated branch and task record claim exact bounded paths.
- [x] Draft PR #912 is opened early and linked from this task.
- [x] Versioned stability certification implementation, strict schema and operator documentation are present.
- [x] Every supplied attempt remains visible and duplicate run identities fail closed in implementation/tests.
- [x] Comparability requires exact scenario, server revision, client revision, datapack and execution tier.
- [x] `pass` requires the explicit minimum run count and every evaluated clean run passing.
- [x] Mixed pass/failure evidence is `unstable`; all evaluated failures are `fail`; insufficient evidence is `not-evaluated`; unresolved provenance is `blocked`.
- [x] Cleanup certification remains independent and a cleanup failure prevents a clean-pass attempt.
- [x] Deterministic duration percentiles and exact failure/divergence distributions are covered by focused tests.
- [ ] Focused tests, bytecode compilation and JSON schema parsing pass against canonical repository modules.
- [ ] Catalogue/program/changelog entries are updated narrowly.
- [ ] The temporary checkout validation/integration workflow removes itself and is absent from final diff.
- [ ] Exact final-head required checks pass before squash merge.
- [x] A physical repeated-run baseline remains explicit follow-up evidence and is not falsely claimed by this implementation package.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T10:10:00+02:00
head: 218a3f957a58b4d1a67f62d2cfb96f76241ae0cc
branch: feat/e2e-qri-022-stability-certification
pr: 912
status: implementing
context_routes:
  - agent-governance
  - universal-e2e
owned_paths:
  - docs/agents/tasks/active/CAN-20260725-e2e-qri-022-stability-certification.md
  - tools/e2e/stability_certification.py
  - tests/e2e/test_stability_certification.py
  - docs/e2e/E2E_STABILITY_CERTIFICATION.md
  - docs/e2e/E2E_STABILITY_CERTIFICATION.schema.json
  - .github/workflows/e2e-qri-022-integration.yml
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
  - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
proven:
  - QRI-004 is merged and lifecycle-closed; its dashboard validates explicit local extracted schema-v3 result roots and preserves invalid evidence without running scenarios.
  - QRI-005 supplies exact run identity, status, duration, execution tier, revisions, failure classification, first failed step, attempt history and nine independent quality dimensions.
  - QRI-006 supplies independent exact cleanup certification; cleanup success must not be inferred from gameplay success.
  - The roadmap requires run count, pass/fail count, success ratio, failure-class distribution, latency distribution, cleanup failures and first-divergence frequency, and explicitly classifies 9/10 as unstable.
  - No open PR or active task with E2E-QRI-022 intent or planned exclusive paths was found during live preflight.
  - Draft PR #912 targets blakinio/canary:main from the dedicated same-repository task branch.
  - The current implementation, focused tests, strict schema and operator documentation are committed on the task branch.
derived:
  - Reusing coverage_dashboard discovery and canonical envelope validation avoids a second result parser and preserves its path-confinement rules.
  - A clean passing attempt requires gameplay status success and exact cleanup certification success; the two facts remain separately reported.
unknown:
  - Focused test outcome against the repository's actual canonical coverage/result/cleanup modules until the checkout workflow completes.
  - The first selected physical scenario set and exact retained artifact population for a real repeated-run baseline.
  - Whether a later scheduled execution seam is justified after the read-only certification contract is proven.
conflicts: []
first_failure:
  marker: draft-pr-connector-safety-retry
  evidence: The first verbose create-pull-request invocation was blocked before mutation by the connector safety layer; the minimal same-repository retry created draft PR #912 successfully.
rejected_hypotheses:
  - Treating the existing dashboard latest stability dimension as repeated-run certification.
  - Hiding failed attempts behind automatic retry or selecting only successful artifacts.
  - Creating another physical E2E runner, workflow lifecycle or artifact contract.
changed_paths:
  - docs/agents/tasks/active/CAN-20260725-e2e-qri-022-stability-certification.md
  - tools/e2e/stability_certification.py
  - tests/e2e/test_stability_certification.py
  - docs/e2e/E2E_STABILITY_CERTIFICATION.md
  - docs/e2e/E2E_STABILITY_CERTIFICATION.schema.json
validation:
  - command: live main and QRI dependency preflight
    result: PASS
    evidence: main 930e0a15767b7e5348bb36c679fa5e458a76f184 includes QRI-004 lifecycle closure PR #900
  - command: same-repository draft PR safety check
    result: PASS
    evidence: PR #912 targets blakinio/canary:main from feat/e2e-qri-022-stability-certification
  - command: local reconstructed source/test bytecode compilation and isolated focused suite
    result: PASS
    evidence: 13 local tests passed and one canonical-module integration test was explicitly skipped because the local sandbox has no repository checkout
blockers:
  - A real multi-run physical stability baseline requires a selected retained artifact population and execution package after this contract is proven.
next_action: Run the one-shot task-owned checkout integration workflow to patch shared records, execute focused tests against canonical modules, parse the schema and remove itself before final review.
```
