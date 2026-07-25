---
task_id: CAN-20260725-e2e-qri-022-stability-certification
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-QRI-022
status: completed
agent: "GPT-5.6 Thinking"
branch: feat/e2e-qri-022-stability-certification
base_branch: main
created: 2026-07-25
updated: 2026-07-25
last_verified_commit: "5463786e682c7820d201eeaff268cb6ef6bfd4f7"
risk: medium
related_issue: ""
related_pr: "912"
depends_on:
  - merged and lifecycle-closed E2E-QRI-004 factual coverage dashboard
  - merged and lifecycle-closed E2E-QRI-005 result envelope
  - merged and lifecycle-closed E2E-QRI-006 cleanup certification
blocks:
  - first factual physical repeated-run stability baseline
  - later E2E-QRI-023 soak and E2E-QRI-024 performance trend packages
owned_paths:
  exclusive: []
  shared: []
  read_only: []
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

# CAN-20260725 — E2E-QRI-022 stability certification

## Completion

- Final status: completed.
- Delivery PR: #912.
- Exact final delivery PR head: `bf70034702987487bb2c6d94d60d281e71b02ddd`.
- Squash merge commit: `5463786e682c7820d201eeaff268cb6ef6bfd4f7`.
- Lifecycle closure PR: pending final linkage.
- Final Agent Task Ownership: PASS, run `30154299184`.
- Final full `ci:final-gate` CI: PASS, run `30154299240`.
- Final `autofix.ci`: PASS, run `30154299188`.
- Final focused Stability Certification: PASS, run `30154299179`.
- Fresh Universal Agent E2E run `30154299235` remains to be recorded before closure merge.

## Delivered contract

- `canary-universal-e2e-stability-certification-v1`, schema version 1, deterministically consumes explicitly supplied retained Universal E2E schema-v3 result roots and emits JSON plus Markdown from one normalized report.
- Exact comparable cells require scenario, Canary revision, maintained OTClient revision, datapack and execution tier.
- An explicit positive minimum run count is required; the default is 10.
- `pass` requires every counted attempt to be a gameplay success with complete independent cleanup certification.
- Mixed evidence such as 9/10 is `unstable`; all-failure evidence is `fail`; insufficient evidence is `not-evaluated`; incomplete or duplicate evidence is `blocked`.
- Every attempt, source, cleanup result, failure class, first divergence and duration remains visible. Duplicate identities, unsafe paths, future evidence, missing provenance and internally inconsistent reports fail closed.
- The package adds no physical runner, hidden retry, artifact downloader, retention policy, nightly schedule or opaque score.

## Validation

- Exact-head focused workflow compiled the implementation and tests, ran the canonical-module suite and parsed the strict schema: PASS, run `30154299179`.
- Exact-head Agent Task Ownership: PASS, run `30154299184`.
- Exact-head full final-gate CI: PASS, run `30154299240`.
- Exact-head autofix: PASS, run `30154299188`.
- PR #912 had no comments, review submissions or unresolved inline review threads before merge.

## Failure history retained

- Initial integration tooling removed the checkpoint `head:` key; checkpoint validation rejected it before push, and the repaired integration passed.
- A checkpoint used unsupported validation result `UNKNOWN`; Agent Task Ownership rejected it and the record was repaired to use `NOT_RUN`.
- The first final-gate Universal Agent E2E run was cancelled during controlled OTClient compilation. A selective job rerun built OTClient but split Canary and OTClient artifacts across workflow attempts, causing the physical job to fail before scenario execution while downloading the exact-head Canary artifact.
- One fresh workflow run was then triggered so both binaries and physical evidence would belong to one attempt; its exact outcome is recorded before lifecycle closure merge.
- Failed and superseded attempts remain documented and were not hidden.

## Evidence boundaries

- Contract/unit validation proves deterministic report construction and fail-closed validation; it does not constitute a physical repeated-run stability baseline.
- Artifact collection, retained-population selection, scheduling and retention remain outside this contract.
- The first selected physical scenario and retained artifact population remain a separate follow-up package.

## Lifecycle closure

Delivery PR #912 is merged. This archive record releases all E2E-QRI-022 owned paths; final closure linkage and the fresh physical E2E outcome are added before the docs-only lifecycle PR is merged.
