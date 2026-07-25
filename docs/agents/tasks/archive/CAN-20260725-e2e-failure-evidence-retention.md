---
task_id: CAN-20260725-e2e-failure-evidence-retention
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-FAILURE-EVIDENCE-RETENTION-001
status: completed
agent: "GPT-5.6 Thinking"
branch: fix/e2e-failure-evidence-retention
base_branch: main
created: 2026-07-25T21:05:00+02:00
updated: 2026-07-25T23:36:00+02:00
last_verified_commit: "c44225d27e9d0572dd125781b2e05b01d40262fa"
risk: medium
related_issue: ""
related_pr: "940"
depends_on:
  - "Blocked baseline PR #925 and Universal Agent E2E run 30167381956"
blocks: []
owned_paths:
  exclusive: []
  shared: []
  read_only: []
modules_touched:
  - Universal Agent E2E workflow failure evidence retention
reuses:
  - canonical physical lifecycle and schema-v3 result envelope
  - schema-v1 cleanup certification
public_interfaces: []
cross_repo_tasks: []
---

# CAN-20260725 — Universal E2E failure evidence retention

## Completion

- Final status: completed.
- Delivery PR: #940.
- The physical workflow now executes an explicit `capture → upload → propagate` sequence.
- A non-zero physical result no longer terminates the evidence-producing step before upload.
- The original physical status is retained in `physical-exit-code.txt` and is propagated only after artifact upload.
- The Required physical E2E aggregator remains red for a failed physical scenario.
- No retry, retry-until-green behavior, scenario weakening or cleanup bypass was introduced.

## Physical proof

### Success path

- Exact head: `44cfbe2c2b4bffba972ecad6e0399f33980d5ae2`.
- Universal Agent E2E run: `30173640092`.
- Physical `login/relog`, evidence upload, result propagation and Required gate: PASS.
- Artifact: `8623867686`.
- Artifact digest: `sha256:6616f4f82c9b99ce7e10970cdbf583fe0d112e06fdd9fb75f73c9232db4f7526`.
- Retained result: schema version 3, `status=success`, `scenario=login/relog`.
- Retained cleanup certification: schema version 1, `status=certified`, lifecycle exit code `0`.
- Retained physical exit code: `0`.

### Controlled failure path

- Exact head: `c44225d27e9d0572dd125781b2e05b01d40262fa`.
- Universal Agent E2E run: `30174792620`.
- Physical probe job: `89724272988`.
- Physical capture step: PASS and retained status `1`.
- Evidence upload step: PASS.
- Propagation step: expected FAIL.
- Required physical E2E job `89724476985`: expected FAIL.
- Artifact: `8624187169`.
- Artifact digest: `sha256:da30bab7f52ac5af6a55e9ded0a4a1b641c82af394bef8d64a82987989a75325`.
- Retained result: schema version 3, `status=failure`, `scenario=retention/failure-evidence-probe`; required marker evaluation is false while the remaining gameplay, SQL and runtime checks are retained.
- Retained cleanup certification: schema version 1, `status=certified`, lifecycle exit code `1`, all required cleanup checks pass.
- Retained physical exit code: `1`.

## Delivered changes

- `.github/workflows/universal-agent-e2e.yml` captures the physical shell status, uploads `artifacts/`, then propagates the captured status.
- `tools/e2e/run_physical_e2e.sh` records original exit status and normalizes signal-style shell exits without bypassing result-envelope or cleanup finalization.
- `tests/e2e/test_failure_evidence_retention.py` enforces finalization ordering, signal handling and workflow upload-before-propagation ordering.
- The temporary controlled failure scenario is removed from the final delivery head and guarded against accidental retention.

## Validation

- Agent Task Ownership on `c44225d27e9d0572dd125781b2e05b01d40262fa`: PASS, run `30174792538`.
- CI on `c44225d27e9d0572dd125781b2e05b01d40262fa`: PASS, run `30174792612`.
- Controlled failure proof: expected workflow failure with retained evidence, run `30174792620`.
- PR #940 has no comments or unresolved inline review threads at archive time.
- The archive/probe-removal commit is the final-head candidate. Merge is prohibited unless its exact-head ownership, CI and canonical physical `login/relog` checks pass.

## Failure history retained

- The first implementation returned a non-zero status from the physical shell step. GitHub skipped the later upload action despite its declared `if: always()` condition.
- The repair was changed to make the capture step technically successful, retain the original status as a step output, upload evidence, and fail only in a separate propagation step.
- The first temporary probe manifest failed static scenario validation and never became a physical attempt. It was corrected to the canonical login/relog contract before the controlled physical failure proof.
- Failed and superseded attempts remain documented and were not treated as successes.

## Lifecycle closure

PR #940 releases all repair-owned paths after merge. Baseline PR #925 may resume only after this repair is merged and a fresh ownership preflight confirms no conflict.
