---
task_id: CAN-20260726-e2e-login-relog-stability-post-retention
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-QRI-022-BASELINE-004
status: implementing
agent: "GPT-5.6 Thinking"
branch: test/e2e-login-relog-stability-post-retention-20260726
base_branch: main
created: 2026-07-26T23:03:00+02:00
updated: 2026-07-27T10:04:00+02:00
last_verified_commit: "d576d7116b8fe74d9fe777bf697130c2179f767c"
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
- Freeze the counted population on exact PR head `d576d7116b8fe74d9fe777bf697130c2179f767c`.
- Attempt 1 is the initial physical job triggered by that frozen measurement head.
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
- [x] Exactly ten sequential physical attempts complete with no replacement retries and no attempt 11.
- [x] Every counted attempt has retained authoritative schema-v3 result and schema-v1 cleanup evidence, or the missing evidence is preserved as a factual blocker without synthesis.
- [x] All comparable attempts normalize into one exact scenario/server/client/datapack/tier cell.
- [x] QRI-022 JSON and Markdown are generated with explicit `minimum_runs=10` from only the fresh population.
- [x] The baseline dossier records run, attempt, job, artifact, digest, status and cleanup outcome for all ten attempts.
- [x] Temporary controlled-server pin is removed before readiness.
- [ ] Exact-final-head ownership, CI, review and merge gates pass.

# Result

The fresh population is **unstable**, not stable:

- workflow run `30220474091` contains exactly ten counted sequential attempts and no attempt 11;
- attempts 1–7, 9 and 10 are complete clean passes;
- attempt 8 is a retained schema-v3 `client_build_startup` / infrastructure failure at controlled OTClient artifact download;
- attempt 8 has no valid schema-v1 cleanup certification, and the missing cleanup evidence remains explicit;
- all ten results share server `7a09367589dfc08e482edadbe77e556ecf0cfaa7`, client `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`, datapack `data-otservbr-global`, tier `pr-required`, and cell `befa7d114a6a18cfa7c8`;
- QRI-022 with explicit `minimum_runs=10` reports `unstable` / `mixed-outcomes`, with nine clean passes and one failure;
- no retry, missing cleanup evidence or infrastructure failure is hidden or promoted.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-27T08:04:00Z
head: d576d7116b8fe74d9fe777bf697130c2179f767c
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
proven:
  - frozen measurement head d576d7116b8fe74d9fe777bf697130c2179f767c triggered Universal Agent E2E run 30220474091
  - run 30220474091 completed exactly ten sequential physical attempts and no attempt 11 was started
  - attempts 1 through 7 9 and 10 retained schema-v3 success results and certified schema-v1 cleanup
  - attempt 8 retained schema-v3 failure result client_build_startup category infrastructure and no valid cleanup certification
  - every result shares server 7a09367589dfc08e482edadbe77e556ecf0cfaa7 client 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f datapack data-otservbr-global and tier pr-required
  - all ten results normalize into certification cell befa7d114a6a18cfa7c8
  - QRI-022 generated from exactly ten extracted artifact roots with minimum_runs 10 reports unstable mixed-outcomes
  - population counts are nine clean passes one failed attempt zero blocked attempts and one cleanup-unknown attempt
  - temporary controlled-server pin is removed from the final readiness candidate
  - historical PR 961 baseline remains unchanged
  - pre-population runs 30220358871 and 30220408569 are excluded
  - every counted artifact ID and digest is preserved in the baseline dossier
derived:
  - the post-PR-965 controlled-server path avoids the former redundant exact-head Canary download
  - controlled OTClient artifact availability remains a factual infrastructure stability risk
unknown: []
conflicts:
  - the population meets the explicit minimum but one retained infrastructure failure prevents a stability pass
first_failure:
  marker: controlled-otclient-artifact-download
  evidence: attempt 8 job 89851152772 failed before gameplay with client_build_startup at client-configuration/phase:client-configuration
rejected_hypotheses:
  - replace attempt 8 with another green rerun because the measurement contract forbids replacement retries
  - omit attempt 8 from QRI-022 because it has an authoritative schema-v3 fail-closed result
  - synthesize schema-v1 cleanup certification for attempt 8
  - classify nine clean passes as stable because mixed complete evidence is unstable
changed_paths:
  - tests/e2e/baselines/login-relog-stability-post-retention-20260726.md
  - docs/e2e/baselines/E2E_LOGIN_RELOG_STABILITY_POST_RETENTION_20260726.md
  - docs/e2e/baselines/e2e-login-relog-stability-post-retention-20260726.json
  - docs/agents/tasks/active/CAN-20260726-e2e-login-relog-stability-post-retention.md
validation:
  - command: exact ten-attempt collection
    result: PASS
    evidence: nine clean passes and one retained fail-closed infrastructure failure in run 30220474091 with no attempt 11
  - command: QRI-022 build with minimum_runs=10
    result: PASS
    evidence: cell befa7d114a6a18cfa7c8 is unstable reason mixed-outcomes run_count 10
  - command: deterministic report consistency validation
    result: PASS
    evidence: cell digest counts ratios duration distribution failure distribution and evidence-root totals match the repository contract
  - command: final exact-head GitHub gates
    result: NOT_RUN
    evidence: final evidence commit and ci:final-gate validation have not completed
blockers: []
next_action: Apply ci:final-gate, publish the final evidence commit with the temporary pin removed, then complete exact-head CI review and squash merge PR 975.
```
