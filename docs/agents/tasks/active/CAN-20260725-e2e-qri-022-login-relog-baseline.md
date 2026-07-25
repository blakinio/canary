---
task_id: CAN-20260725-e2e-qri-022-login-relog-baseline
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-QRI-022-BASELINE-001
status: blocked
agent: "GPT-5.6 Thinking"
branch: test/e2e-qri-022-login-relog-baseline
base_branch: main
created: 2026-07-25T18:53:04+02:00
updated: 2026-07-25T20:54:00+02:00
last_verified_commit: "544a26e6da117625dbee4ee592b3fabc469b5596"
risk: medium
related_issue: ""
related_pr: "925"
depends_on:
  - "E2E-QRI-022 certification merged in PR #912, lifecycle-closed in PR #914 and stale ownership removed in PR #924"
  - "Canonical physical login/relog scenario at tests/e2e/scenarios/login/scenario.json"
blocks:
  - "First complete factual Universal E2E repeated-run stability classification"
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

Produce the first factual Universal E2E repeated-run stability baseline from ten preserved canonical physical `login/relog` attempts in one exact comparable cell.

# Acceptance criteria

- [x] One exact scenario/server/client/datapack/execution-tier cell was selected.
- [x] Nine complete attempts retain schema-v3 results and certified schema-v1 cleanup evidence.
- [x] Workflow run, job, artifact and digest evidence is recorded for every retained complete attempt.
- [x] The original tenth failure and one diagnostic rerun remain visible and are not replaced by later success.
- [x] The retained nine-envelope QRI-022 report uses explicit `minimum_runs=10` and truthfully returns `not-evaluated`.
- [x] No scenario, runner, workflow, retention, scheduling, retry or runtime behavior was changed in this PR.
- [ ] The tenth required attempt retains its result envelope and cleanup evidence.
- [ ] A complete ten-attempt QRI-022 classification is available.
- [ ] Autonomous merge gate is satisfied.

# Factual result

- Draft PR: #925.
- Trigger/head SHA: `ef5153d09a2dc70469daf360020b81986949bb69`.
- Workflow run: `30167381956`.
- Comparable runtime server revision: `770bb4ba9bf9dbf2fd32c3342b30cd6ab93f991d`.
- Maintained OTClient: `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`.
- Datapack/tier: `data-otservbr-global` / `pr-required`.
- Retained attempts 1-9: clean gameplay success plus certified cleanup.
- Machine QRI-022 cell: `aa3660dd10a3cc8615e2`, `not-evaluated`, reason `insufficient-runs`, 9/10 complete envelopes.
- Overall intended population: `BLOCKED` because the tenth failed attempt retained no Universal E2E artifact, result envelope or cleanup certification.

# Failure and diagnostic evidence

## Required attempt 10

- Physical job `89708625391`: failed in `Run selected physical-client scenario`.
- Evidence upload step declared with `if: always()` was recorded as skipped.
- Required physical E2E job `89708847588`: failure because `physical-client` failed.
- Exact lower-level cause inside `run_physical_e2e.sh`: `UNKNOWN` from connector-visible retained evidence.

## One diagnostic rerun

- Physical job `89709267589`: physical scenario step cancelled.
- Evidence upload was again skipped.
- Required physical E2E job `89709498686`: failure.
- This rerun is diagnostic only and does not replace attempt 10.
- No further rerun is allowed for this baseline.

# Durable outputs

- `tests/e2e/baselines/login-relog-stability-baseline.md`
- `docs/e2e/baselines/e2e-login-relog-stability-baseline.json`
- `docs/e2e/baselines/E2E_LOGIN_RELOG_STABILITY_BASELINE.md`

The Markdown dossier contains all nine artifact IDs and digests, result/cleanup/root hashes, the unretained attempt evidence and the generated QRI-022 interpretation.

# Validation and CI

| Commit/run | Check | Result | Evidence |
|---|---|---|---|
| `ef5153d09a2dc70469daf360020b81986949bb69` | Agent Task Ownership | pass | `30167381859` |
| `ef5153d09a2dc70469daf360020b81986949bb69` | CI | pass | `30167381945` |
| `30167381956` attempts 1-9 | Physical `login/relog` and cleanup | pass | Artifacts `8622212268` through `8622546348`, exact list in baseline dossier |
| `30167381956` attempt 10 | Physical `login/relog` | fail | Physical job `89708625391`; Required `89708847588` |
| `30167381956` diagnostic rerun | Failure-retention diagnostic | fail | Physical job `89709267589`; Required `89709498686` |
| `bdf70b86db010951622529eb0d16b924ce189295` | Durable JSON/Markdown evidence committed | pass | Report and dossier paths exist on PR #925 |
| `544a26e6da117625dbee4ee592b3fabc469b5596` | Final blocked handoff | pass | No more writes should be made to PR #925 until the repair dependency is resolved |

# Decisions

| Decision | Reason/evidence |
|---|---|
| Do not classify the complete population as pass | The tenth required attempt failed and has no contract envelope. |
| Do not classify it as ordinary `9/10 unstable` | QRI-022 can classify only preserved normalized attempts; the failed attempt lacks required evidence. |
| Keep the machine report at nine roots / `not-evaluated` | It truthfully represents the explicit valid extracted artifact population. |
| Mark the programme-level population `BLOCKED` | Collection and retention are external to QRI-022, and the missing failure evidence prevents complete classification. |
| Repair retention in a separate task | PR #925 explicitly owns evidence measurement only and must not change the workflow under measurement. |

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T20:54:00+02:00
head: 544a26e6da117625dbee4ee592b3fabc469b5596
branch: test/e2e-qri-022-login-relog-baseline
pr: 925
status: blocked
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
  - Attempts 1 through 9 are clean physical login/relog passes with complete schema-v3 result envelopes and certified schema-v1 cleanup in one exact cell.
  - The retained QRI-022 cell aa3660dd10a3cc8615e2 has nine clean passes and is not-evaluated because minimum_runs is 10.
  - Required attempt 10 job 89708625391 failed and its evidence upload step was skipped, leaving no result envelope or cleanup certification.
  - One diagnostic rerun job 89709267589 was cancelled in the physical step and again retained no Universal E2E artifact.
  - The complete intended population cannot be truthfully classified as pass, unstable or fail and is blocked on evidence retention.
derived:
  - Failure and cancellation evidence retention is a prerequisite to repeating the baseline and to any later soak/performance threshold work.
unknown:
  - Exact lower-level failure inside run_physical_e2e.sh for attempt 10.
  - Why GitHub skipped the declared if-always upload and post-job steps after the physical failure/cancellation.
conflicts: []
first_failure:
  marker: physical-failure-evidence-not-retained
  evidence: attempt 10 physical job 89708625391 failed; upload skipped; Required job 89708847588 failed.
rejected_hypotheses:
  - Treat nine retained successes as a stability pass: rejected because minimum_runs is 10 and the tenth required attempt failed.
  - Replace attempt 10 with a successful retry: rejected by the all-attempts-retained-no-hidden-retry policy.
  - Modify the workflow inside PR 925: rejected because this PR measures the existing lifecycle and does not own workflow behavior.
changed_paths:
  - docs/agents/tasks/active/CAN-20260725-e2e-qri-022-login-relog-baseline.md
  - tests/e2e/baselines/login-relog-stability-baseline.md
  - docs/e2e/baselines/e2e-login-relog-stability-baseline.json
  - docs/e2e/baselines/E2E_LOGIN_RELOG_STABILITY_BASELINE.md
validation:
  - command: Agent Task Ownership
    result: PASS
    evidence: run 30167381859 on ef5153d09a2dc70469daf360020b81986949bb69.
  - command: CI
    result: PASS
    evidence: run 30167381945 on ef5153d09a2dc70469daf360020b81986949bb69.
  - command: QRI-022 retained-envelope classification
    result: BLOCKED
    evidence: nine valid clean envelopes produce not-evaluated; tenth failed attempt lacks retained contract evidence.
blockers:
  - Universal Agent E2E does not retain result and cleanup evidence for the observed physical failure/cancellation condition.
next_action: Open a separate bounded repair task and draft PR that makes Universal Agent E2E failure and cancellation evidence durable before repeating this ten-attempt baseline.
```
