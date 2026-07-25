---
task_id: CAN-20260725-e2e-qri-022-login-relog-baseline
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-QRI-022-BASELINE-001
status: implementing
agent: "GPT-5.6 Thinking"
branch: test/e2e-qri-022-login-relog-baseline
base_branch: main
created: 2026-07-25T18:53:04+02:00
updated: 2026-07-25T18:56:35+02:00
last_verified_commit: "6824b584f8358009658a86ea6eae7dc0bc1b3ec1"
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

- [ ] Exactly ten independently triggered Universal Agent E2E executions target suite `login`, scenario `relog` and one pinned Canary server revision.
- [ ] Every retained run contains schema-v3 `result.json` and complete schema-v1 cleanup certification.
- [ ] Failed, cancelled, timed-out and superseded attempts remain visible; retries never replace earlier evidence.
- [ ] Scenario, Canary revision, OTClient revision, datapack and emitted execution tier match across the counted cell.
- [ ] Workflow run/attempt IDs, artifact IDs, artifact digests and extracted-root digests are recorded.
- [ ] Stability JSON is built with `--minimum-runs 10`, validates, and renders the reviewed Markdown baseline.
- [ ] Existing factual classification is preserved, including `9/10 -> unstable`.
- [ ] No scenario, runner, workflow, retention, scheduling, retry or runtime behavior changes.
- [ ] Exact-head ownership, Stability Certification and CI pass before merge.
- [ ] Program handoff records the result without starting QRI-023, QRI-024 or nightly/retention work.

# Confirmed context

- Task-start `main`: `3f1f492079709d9562c9c027cfc48a183fa00eb6`.
- Draft PR: #925; first task-record head: `6824b584f8358009658a86ea6eae7dc0bc1b3ec1`.
- Canonical scenario: `tests/e2e/scenarios/login/scenario.json`, suite/id `login/relog`.
- Scenario pins OTClient `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`, datapack `data-otservbr-global`, map `otservbr`, account `@test1`, character `Knight 1`.
- It requires two world entries, two safe logouts and persisted `lastlogin`, `lastlogout` and vocation assertions.
- QRI-022 requires exact scenario/server/client/datapack/tier comparability; CLI default minimum is ten.
- Certification consumes extracted artifacts and does not execute/download/schedule runs or set retention.

# Ownership and overlap check

- Program record: `docs/agents/programs/E2E_AUTOMATION_PROGRAM.md`.
- Open PRs inspected: #923, #921, #815, #559, #526 and #514.
- Targeted open-E2E search found no PR claiming `login/relog`, stability implementation or planned baseline report paths.
- PR #815 changes only `docs/agents/tasks/active/CAN-20260723-oteryn-native-auth-production-cutover.md`.
- Repository code search is unavailable; exact-head Agent Task Ownership remains the authoritative full active-record check.
- Local `task_ownership.py` was not run because CHAT has no local checkout.
- Proven overlap: none. Stop if Ownership CI reports one.

# Plan

1. Validate exact ownership on draft PR #925.
2. Pin one Canary server revision and inspect the first result's exact comparability fields.
3. Trigger ten independent `login/relog` physical executions, preserving every attempt.
4. Download/extract every evidence artifact and record IDs/digests.
5. Build, validate and render QRI-022 output with `--minimum-runs 10`.
6. Commit deterministic JSON plus reviewed Markdown, update program handoff, pass final-head gates and merge.

# Work log

## 2026-07-25T18:56:35+02:00

- Created branch `test/e2e-qri-022-login-relog-baseline` from exact `main`.
- Created draft PR #925 with one task-record file.
- Agent Task Ownership and CI were queued on head `6824b584f8358009658a86ea6eae7dc0bc1b3ec1` before this PR-number checkpoint commit.
- No physical attempt has been counted.

# Validation and CI

| Commit | Check | Result | Evidence |
|---|---|---|---|
| `3f1f492079709d9562c9c027cfc48a183fa00eb6` | Main/open-PR preflight | pass | No proven overlap on intended paths. |
| `6824b584f8358009658a86ea6eae7dc0bc1b3ec1` | Agent Task Ownership | queued | Run `30166614836`; superseded by this checkpoint commit once emitted. |
| `6824b584f8358009658a86ea6eae7dc0bc1b3ec1` | CI | queued | Run `30166614919`; superseded by this checkpoint commit once emitted. |
| pending | checkpoint validator / Ownership / CI | not-run | Required on the current PR head. |

# Risks and boundaries

- Physical/infrastructure failures remain evidence and may produce `unstable`, `fail` or `blocked`.
- Disposable MariaDB only; no production data, migration or deployment.
- Credentials remain environment references and must not enter reports.
- No writes outside `blakinio/canary`; pinned OTClient is read-only.
- Do not pool historical successes without complete retained artifacts and cleanup proof.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T18:56:35+02:00
head: 6824b584f8358009658a86ea6eae7dc0bc1b3ec1
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
  - Main at task selection is 3f1f492079709d9562c9c027cfc48a183fa00eb6 and QRI-022 lifecycle debt is closed through PR 924.
  - Draft PR 925 exists in blakinio/canary with the bounded task record and no physical attempts counted.
  - Canonical login/relog pins OTClient 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f, data-otservbr-global and the two-session Knight 1 lifecycle.
  - QRI-022 requires exact comparability, defaults minimum_runs to 10 and classifies 9/10 as unstable.
  - Targeted open-PR inspection found no claim on the scenario, stability implementation or planned baseline outputs.
derived:
  - Existing execution and certification contracts are sufficient; this task needs evidence collection and durable reporting, not reusable implementation changes.
unknown:
  - Exact execution_tier emitted by the first current workflow-dispatch result.
  - Whether ten attempts form one complete comparable cell.
  - Final factual classification.
conflicts: []
first_failure:
  marker: current-head-ownership-ci-not-yet-run
  evidence: PR 925 was checkpointed after creation; exact-head Agent Task Ownership must run on the new commit.
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
  - command: exact-head Agent Task Ownership and checkpoint validation
    result: NOT_RUN
    evidence: Await workflow on the current PR head after this checkpoint commit.
blockers:
  - Exact-head Agent Task Ownership must validate PR 925 before the first counted physical run.
next_action: Verify exact-head Agent Task Ownership on PR 925, then pin the Canary server revision and trigger the first counted login/relog execution.
```
