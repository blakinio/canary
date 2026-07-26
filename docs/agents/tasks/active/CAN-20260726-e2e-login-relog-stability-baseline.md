---
task_id: CAN-20260726-e2e-login-relog-stability-baseline
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-QRI-022-BASELINE-002
status: validating
agent: "GPT-5.6 Thinking"
branch: test/e2e-login-relog-stability-baseline-20260726
base_branch: main
created: 2026-07-26T12:15:00+02:00
updated: 2026-07-26T12:20:00+02:00
last_verified_commit: "2eb25c2c335b9e02ede2ea064e7213eb4f6f759e"
risk: medium
related_issue: ""
related_pr: "961"
depends_on:
  - "QRI-022 stability certification merged in PR #912 and lifecycle-closed in PR #914"
  - "Failure evidence retention repaired by PR #940"
  - "Resolved physical scenario reuse repaired by PR #953 and merged as ec0d815570415a4c7ca7217e3e2aca41f6023dab"
blocks:
  - "First complete factual Universal E2E repeated-run stability classification"
  - "Evidence-backed threshold selection for later soak and performance work"
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260726-e2e-login-relog-stability-baseline.md
    - tests/e2e/baselines/login-relog-stability-baseline-20260726.md
    - docs/e2e/baselines/E2E_LOGIN_RELOG_STABILITY_BASELINE_20260726.md
    - docs/e2e/baselines/e2e-login-relog-stability-baseline-20260726.json
    - .github/e2e-controlled-server.env
  shared: []
  read_only:
    - tests/e2e/scenarios/login/scenario.json
    - .github/workflows/universal-agent-e2e.yml
    - tools/e2e/stability_certification.py
    - tools/e2e/coverage_dashboard.py
    - tools/e2e/result_envelope.py
    - tools/e2e/result_envelope_impl.py
    - docs/e2e/E2E_STABILITY_CERTIFICATION.md
    - docs/e2e/E2E_STABILITY_CERTIFICATION.schema.json
modules_touched:
  - Universal E2E factual login/relog stability baseline
reuses:
  - canary-universal-e2e-result-envelope-v1 schema version 3
  - canary-universal-e2e-cleanup-certification-v1 schema version 1
  - canary-universal-e2e-stability-certification-v1 schema version 1
  - canonical Universal Agent E2E login/relog physical lifecycle
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Produce a fresh factual Universal E2E stability baseline from exactly ten preserved canonical physical `login/relog` attempts in one comparable cell. Historical attempts from closed PR #925 are excluded.

# Measurement contract

- Runtime Canary/server revision is pinned to repaired `main` commit `ec0d815570415a4c7ca7217e3e2aca41f6023dab` through the temporary same-repository controlled-server pin.
- Suite/scenario is exactly `login/relog`.
- Maintained OTClient revision, datapack identity and execution tier must remain identical across all attempts.
- Attempt 1 is the initial PR-triggered Universal Agent E2E run.
- Attempts 2 through 10 are sequential reruns of the same physical job so the workflow run identity remains stable and `GITHUB_RUN_ATTEMPT` remains distinct.
- Stop after attempt 10 regardless of outcome. Do not replace, hide or retry a failed counted attempt.
- Every attempt must retain its schema-v3 `result.json`, schema-v1 cleanup certification, artifact ID and digest.
- Build the QRI-022 report with explicit `minimum_runs=10` from only this fresh population.
- Remove `.github/e2e-controlled-server.env` before readiness so no permanent controlled-server pin is merged.

# Acceptance criteria

- [x] Fresh isolated branch and task own only evidence/governance paths plus one temporary controlled-server pin.
- [x] Runtime server revision is fixed to repaired main `ec0d815570415a4c7ca7217e3e2aca41f6023dab`.
- [ ] Exactly ten counted physical attempts complete without replacement retries.
- [ ] Every counted attempt retains complete result and cleanup evidence.
- [ ] All ten attempts normalize into one exact scenario/server/client/datapack/tier cell.
- [ ] QRI-022 classification with `minimum_runs=10` is generated and committed as JSON and Markdown.
- [ ] The baseline dossier records run, job, artifact, digest and outcome for every attempt.
- [ ] The temporary controlled-server pin is removed before final validation.
- [ ] Exact-final-head ownership, CI, review and merge gates pass.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T12:20:00+02:00
head: 2eb25c2c335b9e02ede2ea064e7213eb4f6f759e
branch: test/e2e-login-relog-stability-baseline-20260726
pr: 961
status: validating
context_routes:
  - agent-governance
  - universal-e2e
owned_paths:
  - docs/agents/tasks/active/CAN-20260726-e2e-login-relog-stability-baseline.md
  - tests/e2e/baselines/login-relog-stability-baseline-20260726.md
  - docs/e2e/baselines/E2E_LOGIN_RELOG_STABILITY_BASELINE_20260726.md
  - docs/e2e/baselines/e2e-login-relog-stability-baseline-20260726.json
  - .github/e2e-controlled-server.env
proven:
  - main is ec0d815570415a4c7ca7217e3e2aca41f6023dab after merged PR 953
  - draft PR 961 targets blakinio/canary main from the isolated baseline branch
  - no open PR claims the fresh login/relog repeated-run baseline paths
  - QRI-022 requires an explicit minimum of ten and does not execute or download physical evidence
  - closed PR 925 retained only nine valid attempts and explicitly requires a fresh isolated population
  - the temporary pin fixes the runtime server revision to ec0d815570415a4c7ca7217e3e2aca41f6023dab
  - the initial baseline dossier contains no reused historical attempt
  - CI run 30198015400 passed on the first task head
  - ownership run 30198015351 failed only because derived had one leading space in the checkpoint
 derived: []
unknown:
  - corrected-head Universal Agent E2E run id and physical job id
  - maintained OTClient revision and datapack identity emitted by attempt 1
  - outcome and retained evidence identifiers for attempts 1 through 10
conflicts: []
first_failure:
  marker: checkpoint-format
  evidence: ownership run 30198015351 reported invalid list item under proven; corrected in this commit
rejected_hypotheses:
  - reuse PR 925 attempts because its closure explicitly forbids reuse in a later baseline
  - create a second physical runner or workflow because the existing canonical lifecycle and rerun API are sufficient
changed_paths:
  - .github/e2e-controlled-server.env
  - tests/e2e/baselines/login-relog-stability-baseline-20260726.md
  - docs/agents/tasks/active/CAN-20260726-e2e-login-relog-stability-baseline.md
validation:
  - command: live main and overlap preflight
    result: PASS
    evidence: main ec0d815570415a4c7ca7217e3e2aca41f6023dab; no open matching baseline PR
  - command: CI
    result: PASS
    evidence: run 30198015400 on 2eb25c2c335b9e02ede2ea064e7213eb4f6f759e
  - command: Agent Task Ownership
    result: FAIL
    evidence: run 30198015351 failed only on checkpoint indentation; corrected in this commit
  - command: physical ten-attempt population
    result: NOT_RUN
    evidence: corrected-head initial attempt pending
blockers: []
next_action: Require the corrected-head initial Universal Agent E2E physical login/relog attempt to retain complete evidence before scheduling attempt 2.
```
