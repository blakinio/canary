---
task_id: CAN-20260725-e2e-qri-022-login-relog-baseline
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-QRI-022-BASELINE-001
status: implementing
agent: "GPT-5.6 Thinking"
branch: test/e2e-qri-022-login-relog-baseline
base_branch: main
created: 2026-07-25T18:53:04+02:00
updated: 2026-07-25T18:58:13+02:00
last_verified_commit: "dbd1129ee6cdf83b3f1d9a1f8a0c4aa542ff747c"
risk: medium
related_issue: ""
related_pr: "925"
depends_on:
  - "E2E-QRI-022 certification merged in PR #912, lifecycle-closed in PR #914 and stale ownership removed in PR #924"
  - "Canonical physical login/relog scenario at tests/e2e/scenarios/login/scenario.json"
blocks:
  - "First factual Universal E2E repeated-run stability baseline"
  - "Evidence-backed threshold selection for E2E-QRI-023 and E2E-QRI-024"
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260725-e2e-qri-022-login-relog-baseline.md
    - docs/e2e/baselines/E2E_LOGIN_RELOG_STABILITY_BASELINE.md
    - docs/e2e/baselines/e2e-login-relog-stability-baseline.json
  shared:
    - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
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

Produce the first factual Universal E2E repeated-run stability baseline from exactly ten independent clean executions of canonical physical `login/relog` in one exact comparable certification cell, preserving every attempt and independent cleanup evidence.

# Acceptance criteria

- [ ] Exactly ten independently triggered Universal Agent E2E executions target suite `login`, scenario `relog` and pinned Canary server revision `3f1f492079709d9562c9c027cfc48a183fa00eb6`.
- [ ] Every retained run contains schema-v3 `result.json` and complete schema-v1 cleanup certification.
- [ ] Failed, cancelled, timed-out and superseded attempts remain visible; retries never replace earlier evidence.
- [ ] Scenario, Canary revision, OTClient revision, datapack and emitted execution tier match across the counted cell.
- [ ] Workflow run/attempt IDs, artifact IDs, artifact digests and extracted-root digests are recorded.
- [ ] Stability JSON is built with `--minimum-runs 10`, validates, and renders the reviewed Markdown baseline.
- [ ] Existing factual classification is preserved, including `9/10 -> unstable`.
- [ ] No scenario, runner, workflow, retention, scheduling, retry or runtime behavior changes.
- [ ] Exact-final-head ownership, Stability Certification and CI pass before merge.
- [ ] Program handoff records the result without starting QRI-023, QRI-024 or nightly/retention work.

# Confirmed context

- Task-start and pinned server revision: `3f1f492079709d9562c9c027cfc48a183fa00eb6`.
- Draft PR: #925; current verified preflight head: `dbd1129ee6cdf83b3f1d9a1f8a0c4aa542ff747c`.
- Canonical scenario: `tests/e2e/scenarios/login/scenario.json`, suite/id `login/relog`.
- Scenario pins OTClient `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`, datapack `data-otservbr-global`, map `otservbr`, account `@test1`, character `Knight 1`.
- It requires two world entries, two safe logouts and persisted `lastlogin`, `lastlogout` and vocation assertions.
- QRI-022 requires exact scenario/server/client/datapack/tier comparability; CLI default minimum is ten.
- Certification consumes extracted artifacts and does not execute/download/schedule runs or set retention.
- Exact-head Agent Task Ownership `30166657875` and CI `30166657927` passed on `dbd1129ee6cdf83b3f1d9a1f8a0c4aa542ff747c`.

# Ownership and overlap check

- Program record: `docs/agents/programs/E2E_AUTOMATION_PROGRAM.md`.
- Open PRs inspected: #923, #921, #815, #559, #526 and #514.
- Targeted open-E2E search found no PR claiming `login/relog`, stability implementation or planned baseline report paths.
- PR #815 changes only `docs/agents/tasks/active/CAN-20260723-oteryn-native-auth-production-cutover.md`.
- Exact-head Agent Task Ownership passed and found no structured overlap on the declared claims.

# Plan

1. Dispatch the first physical run from PR #925 using `suite=login`, `scenario=relog`, `server_repository=blakinio/canary`, `server_ref=3f1f492079709d9562c9c027cfc48a183fa00eb6`.
2. Inspect its schema-v3 result and cleanup artifact before counting further runs; pin the emitted execution tier.
3. Trigger nine additional independent runs with identical inputs, preserving every attempt.
4. Download/extract every evidence artifact and record IDs/digests.
5. Build, validate and render QRI-022 output with `--minimum-runs 10`.
6. Commit deterministic JSON plus reviewed Markdown, update program handoff, pass final-head gates and merge.

# Work log

## 2026-07-25T18:56:35+02:00

- Created branch `test/e2e-qri-022-login-relog-baseline` from exact `main`.
- Created draft PR #925 with one task-record file.
- No physical attempt was counted.

## 2026-07-25T18:58:13+02:00

- Agent Task Ownership run `30166657875`: PASS on `dbd1129ee6cdf83b3f1d9a1f8a0c4aa542ff747c`.
- CI run `30166657927`: PASS on the same head.
- Selected exact server revision `3f1f492079709d9562c9c027cfc48a183fa00eb6` for all ten physical runs.
- First physical workflow-dispatch run remains not started.

# Validation and CI

| Commit | Check | Result | Evidence |
|---|---|---|---|
| `3f1f492079709d9562c9c027cfc48a183fa00eb6` | Main/open-PR preflight | pass | No proven overlap on intended paths. |
| `dbd1129ee6cdf83b3f1d9a1f8a0c4aa542ff747c` | Agent Task Ownership | pass | Run `30166657875`. |
| `dbd1129ee6cdf83b3f1d9a1f8a0c4aa542ff747c` | CI | pass | Run `30166657927`. |
| pending | First Universal Agent E2E `login/relog` workflow dispatch | not-run | Must use the pinned server revision and preserve the full artifact. |

# Risks and boundaries

- Physical/infrastructure failures remain evidence and may produce `unstable`, `fail` or `blocked`.
- Disposable MariaDB only; no production data, migration or deployment.
- Credentials remain environment references and must not enter reports.
- No writes outside `blakinio/canary`; pinned OTClient is read-only.
- Do not pool historical successes without complete retained artifacts and cleanup proof.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T18:58:13+02:00
head: dbd1129ee6cdf83b3f1d9a1f8a0c4aa542ff747c
branch: test/e2e-qri-022-login-relog-baseline
pr: 925
status: implementing
context_routes:
  - agent-governance
  - universal-e2e
owned_paths:
  - docs/agents/tasks/active/CAN-20260725-e2e-qri-022-login-relog-baseline.md
  - docs/e2e/baselines/E2E_LOGIN_RELOG_STABILITY_BASELINE.md
  - docs/e2e/baselines/e2e-login-relog-stability-baseline.json
  - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
proven:
  - Main at task selection and the pinned server revision are 3f1f492079709d9562c9c027cfc48a183fa00eb6.
  - Draft PR 925 exists in blakinio/canary and no physical attempt is counted.
  - Canonical login/relog pins OTClient 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f, data-otservbr-global and the two-session Knight 1 lifecycle.
  - QRI-022 requires exact comparability, defaults minimum_runs to 10 and classifies 9/10 as unstable.
  - Agent Task Ownership 30166657875 and CI 30166657927 passed on dbd1129ee6cdf83b3f1d9a1f8a0c4aa542ff747c with no ownership conflict.
derived:
  - Existing execution and certification contracts are sufficient; the task now needs physical evidence collection and durable reporting.
unknown:
  - Exact execution_tier emitted by the first workflow-dispatch result.
  - Whether ten attempts form one complete comparable cell.
  - Final factual classification.
conflicts: []
first_failure:
  marker: first-counted-physical-run-not-started
  evidence: Ownership and CI preflight passed, but no Universal Agent E2E workflow_dispatch run has been triggered for this baseline.
rejected_hypotheses:
  - Start QRI-023 or QRI-024 first: rejected because the programme orders the factual baseline first.
  - Add runner, retry, collector, retention or scheduling behavior: rejected as outside the bounded baseline contract.
  - Pool historical successes without explicit complete artifacts: rejected by QRI-022 evidence requirements.
changed_paths:
  - docs/agents/tasks/active/CAN-20260725-e2e-qri-022-login-relog-baseline.md
validation:
  - command: live main and targeted open-PR overlap preflight
    result: PASS
    evidence: main 3f1f492079709d9562c9c027cfc48a183fa00eb6; no proven overlap; PR 815 changes one unrelated task record.
  - command: Agent Task Ownership
    result: PASS
    evidence: run 30166657875 on dbd1129ee6cdf83b3f1d9a1f8a0c4aa542ff747c.
  - command: CI
    result: PASS
    evidence: run 30166657927 on dbd1129ee6cdf83b3f1d9a1f8a0c4aa542ff747c.
blockers:
  - The current GitHub connector exposes workflow inspection and reruns but not creation of a new workflow_dispatch run; the first counted physical execution requires the bounded local/GitHub CLI execution step.
next_action: Trigger the first Universal Agent E2E workflow_dispatch run for PR 925 with suite=login, scenario=relog, server_repository=blakinio/canary and server_ref=3f1f492079709d9562c9c027cfc48a183fa00eb6, then inspect its result.json and cleanup certification before counting further runs.
```
