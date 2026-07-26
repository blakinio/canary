---
task_id: CAN-20260726-e2e-login-relog-stability-baseline
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-QRI-022-BASELINE-002
status: implementing
agent: "GPT-5.6 Thinking"
branch: test/e2e-login-relog-stability-baseline-20260726
base_branch: main
created: 2026-07-26T12:15:00+02:00
updated: 2026-07-26T18:56:00+02:00
last_verified_commit: "540a4e68cafb04fa00e963e39b05b75715bc8b38"
risk: medium
related_issue: ""
related_pr: "961"
depends_on:
  - "QRI-022 stability certification merged in PR #912 and lifecycle-closed in PR #914"
  - "Controlled physical-lifecycle failure retention repaired by PR #940"
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
- Every attempt should retain its schema-v3 `result.json`, schema-v1 cleanup certification, artifact ID and digest.
- Build the QRI-022 report with explicit `minimum_runs=10` from only this fresh population.
- Remove `.github/e2e-controlled-server.env` before readiness so no permanent controlled-server pin is merged.

# Acceptance criteria

- [x] Fresh isolated branch and task own only evidence/governance paths plus one temporary controlled-server pin.
- [x] Runtime server revision is fixed to repaired main `ec0d815570415a4c7ca7217e3e2aca41f6023dab`.
- [x] Exactly ten counted physical attempts completed without replacement retries.
- [ ] Every counted attempt retains complete result and cleanup evidence.
- [ ] All ten attempts normalize into one exact scenario/server/client/datapack/tier cell.
- [x] QRI-022 classification with `minimum_runs=10` is generated and committed as JSON and Markdown.
- [x] The baseline dossier records run, job, artifact, digest and outcome for every attempt.
- [x] The temporary controlled-server pin is removed before final validation.
- [ ] Exact-final-head ownership, CI, review and merge gates pass.

# Result

The population is **blocked / not evaluated**, not stable:

- attempts 1–7 are complete clean passes in cell `b262885c08b70ee4d9d6`;
- attempts 8–10 failed before the lifecycle at `Download exact-head Canary binary`;
- their partial artifacts contain no schema-v3 `result.json` or schema-v1 cleanup certification;
- QRI-022 therefore sees seven valid envelopes and reports `not-evaluated` / `insufficient-runs` for explicit `minimum_runs=10`;
- no missing result or cleanup evidence is synthesized.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T18:56:00+02:00
head: 540a4e68cafb04fa00e963e39b05b75715bc8b38
branch: test/e2e-login-relog-stability-baseline-20260726
pr: 961
status: blocked
context_routes:
  - agent-governance
  - universal-e2e
owned_paths:
  - docs/agents/tasks/active/CAN-20260726-e2e-login-relog-stability-baseline.md
  - tests/e2e/baselines/login-relog-stability-baseline-20260726.md
  - docs/e2e/baselines/E2E_LOGIN_RELOG_STABILITY_BASELINE_20260726.md
  - docs/e2e/baselines/e2e-login-relog-stability-baseline-20260726.json
proven:
  - workflow run 30198264756 completed exactly ten sequential physical-job attempts and no attempt 11 was started
  - attempts 1 through 7 retained schema-v3 success results and certified schema-v1 cleanup with physical exit code zero
  - all seven complete envelopes share server ec0d815570415a4c7ca7217e3e2aca41f6023dab, client 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f, datapack data-otservbr-global, tier pr-required, and cell b262885c08b70ee4d9d6
  - attempts 8 through 10 stopped at Download exact-head Canary binary before gameplay
  - artifacts 8634324416 8634412535 and 8634518646 are preserved but contain no result.json or cleanup certification
  - the controlled-server job builds CONTROLLED_SERVER_BIN before the unconditional exact-head Canary artifact download
  - executable resolution already prefers CONTROLLED_SERVER_BIN when it is present
  - QRI-022 generated from ten extracted roots discovers seven valid envelopes and reports not-evaluated with insufficient-runs
  - temporary controlled-server pin is removed from the readiness candidate
derived:
  - the exact-head Canary artifact download is redundant when a controlled server repository is selected
  - PR 940 covers controlled lifecycle nonzero-result retention but not failures before the lifecycle command starts
unknown: []
conflicts:
  - measurement contract requires complete result and cleanup evidence for every attempt but attempts 8 through 10 have only partial pre-lifecycle artifacts
first_failure:
  marker: controlled-server-redundant-canary-download
  evidence: attempts 8 9 and 10 failed consistently at Download exact-head Canary binary after controlled-server build success
rejected_hypotheses:
  - replace attempts 8 through 10 with green reruns because the measurement contract forbids hidden or replacement attempts
  - synthesize result envelopes for pre-lifecycle failures because QRI-022 accepts only authoritative schema-v3 evidence
  - classify the seven complete passes as stable because the explicit minimum is ten
changed_paths:
  - tests/e2e/baselines/login-relog-stability-baseline-20260726.md
  - docs/e2e/baselines/E2E_LOGIN_RELOG_STABILITY_BASELINE_20260726.md
  - docs/e2e/baselines/e2e-login-relog-stability-baseline-20260726.json
  - docs/agents/tasks/active/CAN-20260726-e2e-login-relog-stability-baseline.md
  - .github/e2e-controlled-server.env
validation:
  - command: exact ten-attempt collection
    result: BLOCKED
    evidence: 7 complete clean passes and 3 preserved pre-lifecycle partial artifacts in run 30198264756
  - command: QRI-022 build with minimum_runs=10
    result: PASS
    evidence: cell b262885c08b70ee4d9d6 is not-evaluated reason insufficient-runs run_count 7
  - command: deterministic report consistency validation
    result: PASS
    evidence: cell digest counts ratios duration distribution and evidence-root totals match repository contract
blockers:
  - controlled-server physical jobs must skip the redundant exact-head Canary artifact download and retain fail-closed pre-lifecycle evidence before a fresh baseline can certify ten attempts
next_action: Open one isolated workflow-fix task and PR that guards the exact-head Canary artifact download for controlled-server scenarios and adds pre-lifecycle failure retention.
```
