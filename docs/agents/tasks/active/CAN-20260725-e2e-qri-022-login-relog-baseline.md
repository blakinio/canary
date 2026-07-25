---
task_id: CAN-20260725-e2e-qri-022-login-relog-baseline
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-QRI-022-BASELINE-001
status: implementing
agent: "GPT-5.6 Thinking"
branch: test/e2e-qri-022-login-relog-baseline
base_branch: main
created: 2026-07-25T18:53:04+02:00
updated: 2026-07-25T19:06:00+02:00
last_verified_commit: "64b51cb32600da2693f84e5468c98ca746a15aef"
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
    - tests/e2e/baselines/login-relog-stability-baseline.md
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

Produce the first factual Universal E2E repeated-run stability baseline from exactly ten preserved executions of canonical physical `login/relog` in one exact comparable certification cell.

# Acceptance criteria

- [ ] Exactly ten counted attempts use suite `login`, scenario `relog` and one exact Canary revision.
- [ ] Every retained attempt contains schema-v3 `result.json` and complete schema-v1 cleanup certification.
- [ ] Failures, cancellations, timeouts and superseded attempts remain visible.
- [ ] Scenario, Canary revision, OTClient revision, datapack and execution tier match across the counted cell.
- [ ] Workflow run/attempt IDs, artifact IDs, artifact digests and extracted-root digests are recorded.
- [ ] Stability JSON is built with `--minimum-runs 10`, validates, and renders reviewed Markdown.
- [ ] Existing factual classification is preserved, including `9/10 -> unstable`.
- [ ] No scenario, runner, workflow, retention, scheduling, retry or runtime behavior changes.
- [ ] Exact-final-head ownership, Stability Certification and CI pass before merge.

# Confirmed context

- Draft PR #925 is the bounded owner.
- Canonical scenario is `login/relog` at `tests/e2e/scenarios/login/scenario.json`.
- Scenario pins OTClient `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`, datapack `data-otservbr-global`, map `otservbr`, account `@test1`, character `Knight 1`.
- QRI-022 requires exact scenario/server/client/datapack/tier comparability and defaults to ten runs.
- Exact-head Agent Task Ownership `30166716019` and CI `30166716083` passed on `64b51cb32600da2693f84e5468c98ca746a15aef`.
- The connector cannot create `workflow_dispatch`, but the existing PR workflow is triggered by behaviorless files under `tests/e2e/**` and falls back to canonical `login/relog` when no single scenario manifest is selected.

# Execution method

1. Add the behaviorless evidence manifest `tests/e2e/baselines/login-relog-stability-baseline.md`.
2. Treat that manifest commit as the exact Canary revision for the repeated-run cell.
3. Let the existing PR-triggered Universal Agent E2E run canonical `login/relog` without modifying the scenario, runner or workflow.
4. Inspect the first result and cleanup evidence before repeating the physical job.
5. Re-run the completed physical job sequentially on the same workflow run/head, preserving every run attempt and artifact.
6. Build and validate the QRI-022 report from exactly ten retained attempts.

# Work log

## 2026-07-25T19:06:00+02:00

- Added exclusive ownership for a behaviorless `tests/e2e/**` baseline manifest.
- Rejected modifying the scenario or workflow merely to trigger execution.
- The exact measured server revision will be the next commit that adds the trigger manifest.

# Validation and CI

| Commit | Check | Result | Evidence |
|---|---|---|---|
| `64b51cb32600da2693f84e5468c98ca746a15aef` | Agent Task Ownership | pass | `30166716019` |
| `64b51cb32600da2693f84e5468c98ca746a15aef` | CI | pass | `30166716083` |
| pending | Ownership after new exclusive claim | not-run | Must pass before trigger manifest is added. |

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T19:06:00+02:00
head: 64b51cb32600da2693f84e5468c98ca746a15aef
branch: test/e2e-qri-022-login-relog-baseline
pr: 925
status: implementing
context_routes:
  - agent-governance
  - universal-e2e
owned_paths:
  - docs/agents/tasks/active/CAN-20260725-e2e-qri-022-login-relog-baseline.md
  - tests/e2e/baselines/login-relog-stability-baseline.md
  - docs/e2e/baselines/E2E_LOGIN_RELOG_STABILITY_BASELINE.md
  - docs/e2e/baselines/e2e-login-relog-stability-baseline.json
  - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
proven:
  - PR 925 owns the bounded baseline task.
  - Canonical login/relog pins OTClient 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f and data-otservbr-global.
  - Existing PR path filters can trigger Universal Agent E2E from a behaviorless tests/e2e baseline manifest without changing scenario or workflow behavior.
  - Ownership and CI passed on 64b51cb32600da2693f84e5468c98ca746a15aef before the new claim.
derived:
  - A PR-triggered run plus sequential physical-job reruns can produce distinct preserved run attempts on one exact head.
unknown:
  - Exact trigger-manifest commit SHA.
  - Exact execution tier emitted by the first physical result.
  - Whether all ten attempts form one complete comparable cell.
  - Final factual classification.
conflicts: []
first_failure:
  marker: trigger-manifest-not-created
  evidence: New path ownership is declared but the behaviorless tests/e2e manifest has not yet been committed.
rejected_hypotheses:
  - Modify scenario or workflow to start the baseline: rejected because this task measures existing behavior.
  - Pool historical successes without complete artifacts: rejected by QRI-022 evidence requirements.
changed_paths:
  - docs/agents/tasks/active/CAN-20260725-e2e-qri-022-login-relog-baseline.md
validation:
  - command: Agent Task Ownership
    result: PASS
    evidence: run 30166716019 on 64b51cb32600da2693f84e5468c98ca746a15aef before the new path claim.
blockers:
  - Exact-head Agent Task Ownership must validate the added tests/e2e baseline-manifest claim before its creation.
next_action: Wait for exact-head Agent Task Ownership on this claim commit, then create tests/e2e/baselines/login-relog-stability-baseline.md to start the first physical run.
```
