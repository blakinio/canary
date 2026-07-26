---
task_id: CAN-20260726-e2e-login-relog-stability-post-retention
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-QRI-022-BASELINE-004
status: implementing
agent: "GPT-5.6 Thinking"
branch: test/e2e-login-relog-stability-post-retention-20260726
base_branch: main
created: 2026-07-26T23:03:00+02:00
updated: 2026-07-26T23:07:00+02:00
last_verified_commit: "1c877d40332f0986fae58573cbd8fe1675fb6efe"
risk: medium
related_issue: ""
related_pr: "975"
depends_on:
  - "Controlled-server pre-lifecycle retention repair merged in PR #965 as 698c8698a98571ca61715779f8bb67af6f659fc7"
  - "Factual blocked ten-attempt baseline merged in PR #961 as 191d628259c05048cae3c9b9a0a9b233de6294f4"
  - "QRI-022 deterministic stability certification merged in PR #912"
blocks:
  - "First complete factual ten-attempt login/relog stability classification after the controlled-server retention repair"
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260726-e2e-login-relog-stability-post-retention.md
    - tests/e2e/baselines/login-relog-stability-post-retention-20260726.md
    - docs/e2e/baselines/E2E_LOGIN_RELOG_STABILITY_POST_RETENTION_20260726.md
    - docs/e2e/baselines/e2e-login-relog-stability-post-retention-20260726.json
    - .github/e2e-controlled-server.env
  shared: []
  read_only:
    - .github/workflows/universal-agent-e2e.yml
    - tests/e2e/scenarios/login/scenario.json
    - tools/e2e/stability_certification.py
    - tools/e2e/coverage_dashboard.py
    - tools/e2e/result_envelope.py
    - tools/e2e/cleanup_certification.py
    - docs/e2e/E2E_STABILITY_CERTIFICATION.md
    - tests/e2e/baselines/login-relog-stability-baseline-20260726.md
    - docs/e2e/baselines/E2E_LOGIN_RELOG_STABILITY_BASELINE_20260726.md
    - docs/e2e/baselines/e2e-login-relog-stability-baseline-20260726.json
modules_touched:
  - Universal E2E factual login/relog stability baseline
reuses:
  - canonical Universal Agent E2E login/relog physical lifecycle
  - canary-universal-e2e-result-envelope-v1 schema version 3
  - canary-universal-e2e-cleanup-certification-v1 schema version 1
  - canary-universal-e2e-stability-certification-v1 schema version 1
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Produce one fresh factual QRI-022 stability classification from exactly ten sequential controlled-server physical `login/relog` attempts against current `main` after the PR #965 retention repair.

# Measurement contract

- Pin the runtime server to exact current-main commit `7a09367589dfc08e482edadbe77e556ecf0cfaa7` through the temporary same-repository `.github/e2e-controlled-server.env` file.
- Use exactly suite/scenario `login/relog` through the canonical Universal Agent E2E workflow.
- Attempt 1 is the initial pull-request-triggered physical job.
- Attempts 2 through 10 are sequential reruns of that same physical job and workflow run, preserving distinct `GITHUB_RUN_ATTEMPT` identities.
- Stop after attempt 10 regardless of outcome. Do not start attempt 11.
- Do not replace, hide, retry around or discard any counted failed attempt.
- Retain the artifact ID, digest, result envelope, cleanup certification, run/job identity and factual outcome for every counted attempt.
- Build QRI-022 from only these ten extracted artifact roots with explicit `minimum_runs=10`.
- Preserve exact scenario/server/client/datapack/execution-tier cell boundaries; do not pool incomparable evidence.
- Remove `.github/e2e-controlled-server.env` before readiness so no permanent controlled-server pin is merged.
- Preserve the PR #961 blocked population unchanged as historical evidence.

# Acceptance criteria

- [x] Fresh isolated branch and task claim only the new evidence outputs and one temporary controlled-server pin.
- [x] Draft PR #975 targets `blakinio/canary:main` from the same repository.
- [x] Controlled server is pinned to `7a09367589dfc08e482edadbe77e556ecf0cfaa7` for the counted population.
- [ ] Exactly ten sequential physical attempts complete with no replacement retries and no attempt 11.
- [ ] Every counted attempt has retained authoritative schema-v3 result and schema-v1 cleanup evidence, or the missing evidence is preserved as a factual blocker without synthesis.
- [ ] All comparable attempts normalize into one exact scenario/server/client/datapack/tier cell.
- [ ] QRI-022 JSON and Markdown are generated with explicit `minimum_runs=10` from only the fresh population.
- [ ] The baseline dossier records run, attempt, job, artifact, digest, status and cleanup outcome for all ten attempts.
- [ ] Temporary controlled-server pin is removed before readiness.
- [ ] Exact-final-head ownership, CI, review and merge gates pass.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T21:07:00Z
head: 1c877d40332f0986fae58573cbd8fe1675fb6efe
branch: test/e2e-login-relog-stability-post-retention-20260726
pr: 975
status: implementing
context_routes:
  - agent-governance
  - universal-e2e
owned_paths:
  - docs/agents/tasks/active/CAN-20260726-e2e-login-relog-stability-post-retention.md
  - tests/e2e/baselines/login-relog-stability-post-retention-20260726.md
  - docs/e2e/baselines/E2E_LOGIN_RELOG_STABILITY_POST_RETENTION_20260726.md
  - docs/e2e/baselines/e2e-login-relog-stability-post-retention-20260726.json
  - .github/e2e-controlled-server.env
proven:
  - current main is 7a09367589dfc08e482edadbe77e556ecf0cfaa7 after disjoint RTEC parties evidence PR 958
  - PR 975 is an open mergeable same-repository draft targeting main
  - temporary controlled-server pin selects blakinio/canary at 7a09367589dfc08e482edadbe77e556ecf0cfaa7
  - Universal Agent E2E run 30220358871 was queued from exact population head 1c877d40332f0986fae58573cbd8fe1675fb6efe
  - PR 965 is merged as 698c8698a98571ca61715779f8bb67af6f659fc7 with no comments reviews or unresolved review threads
  - controlled-server physical validation in run 30212632481 passed login/relog while skipping the redundant exact-head Canary download
  - no open PR was found for QRI-022 controlled-server or login/relog stability work before PR 975 was created
  - prior PR 961 preserved its blocked population without replacement retries
  - the canonical QRI-022 builder requires explicit comparable retained evidence and defaults to minimum_runs 10
derived:
  - the disjoint main advance does not alter the repaired Universal E2E workflow and 7a09367589dfc08e482edadbe77e556ecf0cfaa7 is the exact current-main server revision for this population
  - the initial physical job from run 30220358871 is attempt 1 regardless of pass or failure
unknown:
  - physical job identity outcome artifact and evidence completeness for attempt 1
  - outcome and retained evidence completeness of attempts 2 through 10
conflicts: []
first_failure:
  marker: none
  evidence: run 30220358871 is queued and no counted outcome exists yet
rejected_hypotheses:
  - reuse or extend the PR 961 population because the requested classification requires a fresh post-repair population
  - modify the Universal Agent E2E workflow because PR 965 already repaired the controlled-server path
  - replace any failed counted attempt because the measurement contract forbids replacement retries
changed_paths:
  - docs/agents/tasks/active/CAN-20260726-e2e-login-relog-stability-post-retention.md
  - .github/e2e-controlled-server.env
validation:
  - command: live repository PR CI and ownership preflight
    result: PASS
    evidence: current main 7a09367589dfc08e482edadbe77e556ecf0cfaa7; PR 975 same-repository draft; PR 965 merged cleanly
  - command: Universal Agent E2E initial population run
    result: NOT_RUN
    evidence: run 30220358871 queued from head 1c877d40332f0986fae58573cbd8fe1675fb6efe
blockers: []
next_action: Inspect Universal Agent E2E run 30220358871 and count its physical job as attempt 1 regardless of outcome; after completion rerun that exact physical job once for attempt 2.
```
