---
task_id: CAN-20260725-e2e-qri-022-login-relog-baseline
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-QRI-022-BASELINE-001
status: implementing
agent: "GPT-5.6 Thinking"
branch: test/e2e-qri-022-login-relog-baseline
base_branch: main
created: 2026-07-25T18:53:04+02:00
updated: 2026-07-25T18:53:04+02:00
last_verified_commit: "3f1f492079709d9562c9c027cfc48a183fa00eb6"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - "E2E-QRI-022 stability certification merged in PR #912, lifecycle-closed in PR #914 and stale active ownership removed in PR #924"
  - "Canonical physical login/relog scenario at tests/e2e/scenarios/login/scenario.json"
blocks:
  - "First factual Universal E2E repeated-run stability baseline"
  - "Evidence-backed threshold selection for E2E-QRI-023 soak and E2E-QRI-024 performance work"
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

Produce the first factual Universal E2E repeated-run stability baseline from exactly ten independent clean executions of the canonical physical `login/relog` scenario in one exact comparable certification cell, preserving every attempt and its independent cleanup evidence.

# Acceptance criteria

- [ ] Exactly ten independently triggered canonical Universal Agent E2E executions target suite `login`, scenario `relog` and one pinned Canary server revision.
- [ ] Every retained run exposes a schema-v3 `canary-universal-e2e-result-envelope-v1` `result.json` and complete schema-v1 cleanup certification.
- [ ] Every attempt remains visible; no failed, cancelled, timed-out or superseded attempt is discarded or replaced by a retry.
- [ ] Scenario, Canary revision, maintained OTClient revision, datapack and emitted execution tier are identical across the counted certification cell.
- [ ] Each workflow run ID, run attempt, artifact ID, artifact digest and extracted evidence-root digest is recorded in the durable baseline.
- [ ] `tools/e2e/stability_certification.py build` runs with explicit `--minimum-runs 10`, then the generated JSON validates and Markdown renders from that JSON.
- [ ] The final classification follows the existing factual contract; `9/10` is recorded as `unstable`, not promoted to pass.
- [ ] No scenario, runner, workflow, artifact-retention, scheduling, retry or runtime behavior is changed in this task.
- [ ] Current-head ownership, focused stability validation and required CI checks pass before merge.
- [ ] Program handoff records the factual outcome without starting QRI-023, QRI-024, nightly scheduling or retention work.

# Confirmed context

- Current task-start `main` is `3f1f492079709d9562c9c027cfc48a183fa00eb6`.
- PR #924 removed the stale active QRI-022 lifecycle record after exact-head Ownership, Stability Certification and full CI passed.
- The canonical scenario is `login/relog` at `tests/e2e/scenarios/login/scenario.json`.
- The scenario pins maintained OTClient `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`, datapack `data-otservbr-global`, map `otservbr`, account `@test1` and character `Knight 1`.
- The scenario requires two successful world entries, two safe logouts and persisted `lastlogin`, `lastlogout` and vocation assertions.
- The stability-certification contract requires exact scenario, server revision, client revision, datapack and execution-tier comparability. Its explicit CLI default minimum is ten runs.
- Stability certification consumes already extracted artifact roots and does not execute scenarios, discover/download artifacts, schedule runs or set retention.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| Canonical Universal Agent E2E | Physical execution | `.github/workflows/universal-agent-e2e.yml` | Existing workflow-dispatch inputs already select `login/relog` and the controlled server revision. |
| Canonical login/relog scenario | Scenario and assertions | `tests/e2e/scenarios/login/scenario.json` | Stable two-session login/logout/relog sentinel with pinned maintained client and datapack. |
| Result envelope v3 | Attempt identity and factual status | `tools/e2e/result_envelope.py`, `tools/e2e/result_envelope_impl.py` | Preserves run identity, attempt history, provenance, failure and quality dimensions. |
| Cleanup certification v1 | Independent cleanup proof | Existing canonical physical lifecycle artifact | Required for a clean stability pass and independent from gameplay success. |
| QRI-022 stability certification | Classification and report generation | `tools/e2e/stability_certification.py`, `docs/e2e/E2E_STABILITY_CERTIFICATION.md` | Already implements minimum-run, fail-closed comparability and `9/10 -> unstable`. |

# Ownership and overlap check

- Program record: `docs/agents/programs/E2E_AUTOMATION_PROGRAM.md`.
- Open PRs inspected: #923, #921, #815, #559, #526 and #514.
- Targeted E2E PR search inspected current open results; no open PR claims the canonical `login/relog` scenario, stability-certification implementation or the new baseline output paths.
- PR #815 is the only open E2E-evidence PR found in the targeted search; its changed-file list is limited to `docs/agents/tasks/active/CAN-20260723-oteryn-native-auth-production-cutover.md`.
- Active-task overlap was checked through current open PR task records and exact changed paths. The repository code-search index is unavailable, so the deterministic ownership workflow remains the authoritative full active-record check.
- Ownership checker result: local command not run because this CHAT continuation has no local checkout; exact-head Agent Task Ownership CI is required before execution/merge.
- Exclusive claims: this task record plus two new baseline report paths.
- Shared claim: narrow completion update to `E2E_AUTOMATION_PROGRAM.md`.
- Read-only dependencies: canonical scenario, physical workflow, result/coverage/stability tooling and schemas.
- Overlaps: none proven.
- Resolution: proceed with the bounded task; stop if Agent Task Ownership reports any structured overlap.

# Current state

The baseline is selected and owned. No physical run has been counted yet and no baseline report exists.

# Plan

1. Validate this task record and exact ownership on the draft PR head.
2. Pin one Canary server revision and verify the first retained result's exact scenario, client, datapack and execution-tier fields before counting further runs.
3. Trigger ten independent canonical `login/relog` executions without hiding retries or failed attempts.
4. Download and extract every physical evidence artifact, preserving workflow run/attempt/artifact IDs and digests.
5. Build, validate and render the QRI-022 stability report with `--minimum-runs 10`.
6. Commit the deterministic JSON report and reviewed Markdown baseline, update the program handoff, run exact-final-head gates and merge only when factual acceptance criteria pass.

# Work log

## 2026-07-25T18:53:04+02:00

- Changed: selected the canonical `login/relog` scenario and declared bounded evidence/report ownership.
- Learned: the current workflow and certification tool already provide all execution and classification primitives; no new runner, workflow or parser is required.
- Failed/blocked: local `task_ownership.py` was not available in CHAT; exact-head ownership CI remains mandatory.
- Result: task ready for draft-PR validation before physical execution.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Use `login/relog` as baseline scenario | It is the canonical fallback sentinel with pinned client/datapack and repeated physical proof history. | none |
| Count exactly ten independent executions | QRI-022 default and roadmap example use ten; `9/10` must remain unstable. | none |
| Keep collection, retention and nightly scheduling outside this task | The delivered certification contract explicitly excludes them and the program requires separation until the first baseline proves need. | none |
| Do not edit the scenario or physical workflow | This task measures current repeatability; changing the measured lifecycle would invalidate the baseline purpose. | none |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `docs/agents/tasks/active/CAN-20260725-e2e-qri-022-login-relog-baseline.md` | exclusive | Task ownership, checkpoint and factual evidence ledger | active |
| `docs/e2e/baselines/E2E_LOGIN_RELOG_STABILITY_BASELINE.md` | exclusive | Reviewed human-readable baseline and exact retained-population references | planned |
| `docs/e2e/baselines/e2e-login-relog-stability-baseline.json` | exclusive | Deterministic schema-v1 stability-certification output | planned |
| `docs/agents/programs/E2E_AUTOMATION_PROGRAM.md` | shared | Completion status and one next programme action | planned |
| `tests/e2e/scenarios/login/scenario.json` | read_only | Canonical measured scenario | unchanged |
| `.github/workflows/universal-agent-e2e.yml` | read_only | Canonical physical execution and artifact production | unchanged |
| `tools/e2e/stability_certification.py` | read_only | Existing report build/validate/render contract | unchanged |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| `3f1f492079709d9562c9c027cfc48a183fa00eb6` | Live main/open-PR/changed-path preflight | pass | No proven overlap on intended paths; PR #815 changes one unrelated active task record. |
| pending | `python tools/agents/checkpoint.py docs/agents/tasks/active/CAN-20260725-e2e-qri-022-login-relog-baseline.md --require-checkpoint` | not-run | To be emitted by exact-head ownership validation. |
| pending | Agent Task Ownership | not-run | Required before physical execution proceeds. |
| pending | Universal E2E Stability Certification | not-run | Required on current/final heads. |
| pending | CI / Required | not-run | Required before merge. |

# Failed approaches and dead ends

- Do not start QRI-023 soak or QRI-024 performance work before this baseline exists.
- Do not pool runs from different Canary, client, datapack or execution-tier cells.
- Do not count artifact presence as gameplay or cleanup success.
- Do not rerun a failure and retain only the successful attempt.

# Risks and compatibility

- Runtime: physical workflow or external build infrastructure may fail; every attempt must remain factual evidence and be classified, not hidden.
- Data/migration: disposable MariaDB fixtures only; no production data or migration.
- Security: credentials remain environment references and must never enter task/report artifacts.
- Backward compatibility: no implementation or scenario change is planned.
- Cross-repo rollout: no repository writes outside `blakinio/canary`; maintained OTClient is consumed at the pinned read-only revision.
- Rollback: delete the unmerged baseline branch/PR; no runtime state outside disposable workflow resources is changed.

# Remaining work

1. Open the draft PR and require exact-head Agent Task Ownership before triggering the first counted physical run.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T18:53:04+02:00
head: 3f1f492079709d9562c9c027cfc48a183fa00eb6
branch: test/e2e-qri-022-login-relog-baseline
pr: none
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
  - The canonical login/relog scenario pins maintained OTClient 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f, data-otservbr-global and the two-session Knight 1 lifecycle.
  - The delivered stability contract requires exact scenario/server/client/datapack/tier comparability, defaults minimum_runs to 10 and classifies 9/10 as unstable.
  - Current targeted open-PR inspection found no claim on the measured scenario, stability implementation or planned baseline report paths.
derived:
  - The first factual baseline can be produced by evidence collection and existing certification without changing reusable implementation.
unknown:
  - The exact execution_tier emitted by the first current workflow-dispatch result envelope.
  - Whether all ten physical attempts will form one complete comparable certification cell.
  - The final pass, unstable, fail, blocked or not-evaluated classification.
conflicts: []
first_failure:
  marker: ownership-ci-not-yet-run
  evidence: The task branch exists but exact-head Agent Task Ownership has not yet validated the new structured claims.
rejected_hypotheses:
  - Start soak or performance work first: rejected because both require factual baseline evidence and the programme orders the baseline first.
  - Add a new runner, retry layer or artifact collector in the baseline task: rejected because existing contracts separate execution/classification from collection, retention and scheduling.
  - Pool historical login/relog successes without explicit retained artifacts: rejected because QRI-022 requires complete comparable result and cleanup evidence for every counted attempt.
changed_paths:
  - docs/agents/tasks/active/CAN-20260725-e2e-qri-022-login-relog-baseline.md
validation:
  - command: live main and targeted open-PR overlap preflight
    result: PASS
    evidence: main 3f1f492079709d9562c9c027cfc48a183fa00eb6; no proven overlap on intended paths; PR 815 changes only an unrelated task record.
  - command: python tools/agents/checkpoint.py docs/agents/tasks/active/CAN-20260725-e2e-qri-022-login-relog-baseline.md --require-checkpoint
    result: NOT_RUN
    evidence: Await exact-head Agent Task Ownership workflow after draft PR creation.
blockers:
  - Exact-head Agent Task Ownership must validate the new task before the first counted physical run.
next_action: Open the draft PR for this exact branch and verify its exact-head Agent Task Ownership result before triggering the first counted login/relog execution.
```
