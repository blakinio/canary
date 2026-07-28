---
task_id: CAN-20260726-e2e-login-relog-stability-post-retention
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-QRI-022-BASELINE-004
status: ready
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
updated_at: 2026-07-27T10:46:54Z
head: d15f70804cdcf098c2427f0e0062543ed6f4807f
branch: test/e2e-login-relog-stability-post-retention-20260726
pr: 975
status: ready
context_routes:
  - agent-governance
  - universal-e2e
owned_paths:
  - docs/agents/tasks/active/CAN-20260726-e2e-login-relog-stability-post-retention.md
  - tests/e2e/baselines/login-relog-stability-post-retention-20260726.md
  - docs/e2e/baselines/E2E_LOGIN_RELOG_STABILITY_POST_RETENTION_20260726.md
  - docs/e2e/baselines/e2e-login-relog-stability-post-retention-20260726.json
proven:
  - run 30220474091 contains exactly ten sequential counted login/relog attempts and no attempt 11
  - attempts 1 through 7 9 and 10 are clean passes with certified cleanup
  - attempt 8 is a retained client_build_startup infrastructure failure before gameplay with missing cleanup certification
  - QRI-022 minimum_runs 10 classifies cell befa7d114a6a18cfa7c8 as unstable mixed-outcomes with nine clean passes and one failure
  - temporary controlled-server pin is absent from the final changed-file set
  - exact head d15f70804cdcf098c2427f0e0062543ed6f4807f passed Agent Task Ownership CI autofix and full Universal Agent E2E including physical login/relog and Required physical E2E
  - PR 975 is ready for review and mergeable with no comments reviews or review threads at checkpoint capture
  - changed files are limited to the active task and the three QRI-022 evidence outputs
derived:
  - controlled OTClient artifact availability remains the only observed stability risk in the counted population
unknown:
  - the post-checkpoint commit head and its required-check state must be verified live before merge
conflicts: []
first_failure:
  marker: controlled-otclient-artifact-download
  evidence: attempt 8 job 89851152772 failed before gameplay at client-configuration/phase:client-configuration
rejected_hypotheses:
  - replace or omit attempt 8 because the measurement contract and authoritative schema-v3 result require retaining it
  - classify nine clean passes as stable because QRI-022 defines mixed outcomes as unstable
changed_paths:
  - docs/agents/tasks/active/CAN-20260726-e2e-login-relog-stability-post-retention.md
  - tests/e2e/baselines/login-relog-stability-post-retention-20260726.md
  - docs/e2e/baselines/E2E_LOGIN_RELOG_STABILITY_POST_RETENTION_20260726.md
  - docs/e2e/baselines/e2e-login-relog-stability-post-retention-20260726.json
validation:
  - command: exact ten-attempt collection and QRI-022 minimum_runs=10
    result: PASS
    evidence: run 30220474091 and certification cell befa7d114a6a18cfa7c8 report nine clean passes one retained failure
  - command: Agent Task Ownership run 30250274300
    result: PASS
    evidence: final validated head d15f70804cdcf098c2427f0e0062543ed6f4807f
  - command: CI runs 30250274515 and 30252933650
    result: PASS
    evidence: required checks and ready-for-review rerun both completed successfully on d15f70804cdcf098c2427f0e0062543ed6f4807f
  - command: Universal Agent E2E run 30250274492
    result: PASS
    evidence: build Canary build OTClient physical login/relog evidence upload propagation and Required physical E2E all succeeded
  - command: python tools/agents/checkpoint.py docs/agents/tasks/active/CAN-20260726-e2e-login-relog-stability-post-retention.md --require-checkpoint
    result: PASS
    evidence: compact checkpoint validated before handoff
blockers: []
next_action: Verify the post-checkpoint PR head and required checks, then squash-merge PR 975 if it remains mergeable and review-clean.
```
