---
task_id: CAN-20260726-e2e-qri-022-login-relog-baseline-v2
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-QRI-022-BASELINE-002
status: in_progress
agent: "GPT-5.6 Thinking"
branch: test/e2e-qri-022-login-relog-baseline-v2
base_branch: main
created: 2026-07-26T00:35:00+02:00
updated: 2026-07-26T00:40:00+02:00
last_verified_commit: "ef831709721b1a3c6130ddf81d6a2867a3bb1640"
risk: medium
related_issue: ""
related_pr: "948"
depends_on:
  - "QRI-022 certification merged in PR #912, lifecycle-closed in PR #914 and stale ownership removed in PR #924"
  - "Failure evidence retention repair merged in PR #940 as ad647f040a0f0b5b515c2416bf8aa11705dd7e8e"
  - "Historical incomplete baseline PR #925 closed without merge"
blocks:
  - "First complete factual Universal E2E repeated-run stability classification"
  - "Evidence-backed threshold selection for later soak and performance work"
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260726-e2e-qri-022-login-relog-baseline-v2.md
    - tests/e2e/baselines/login-relog-stability-baseline-v2.md
    - docs/e2e/baselines/E2E_LOGIN_RELOG_STABILITY_BASELINE_V2.md
    - docs/e2e/baselines/e2e-login-relog-stability-baseline-v2.json
  shared: []
  read_only:
    - tests/e2e/scenarios/login/scenario.json
    - .github/workflows/universal-agent-e2e.yml
    - tools/e2e/stability_certification.py
    - tools/e2e/result_envelope.py
    - tools/e2e/result_envelope_impl.py
    - tools/e2e/cleanup_certification.py
    - docs/e2e/E2E_STABILITY_CERTIFICATION.md
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

Produce the first complete factual Universal E2E repeated-run stability baseline from exactly ten preserved canonical physical `login/relog` attempts in one comparable cell after the failure-evidence retention repair.

# Acceptance criteria

- [ ] Draft PR owns only the new v2 task, immutable measurement manifest and final v2 reports.
- [ ] Measurement HEAD is frozen before attempt collection begins.
- [ ] Exactly ten physical attempts are executed sequentially from one workflow run and one fixed measurement HEAD.
- [ ] Every attempt, including any failure, retains a unique artifact, digest, schema-v3 result and schema-v1 cleanup certification.
- [ ] Every retained attempt shares the same scenario, Canary revision, OTClient revision, datapack and execution tier.
- [ ] Workflow run, attempt, physical job, artifact ID and artifact digest are recorded for all ten attempts.
- [ ] QRI-022 is run with `minimum_runs=10` over exactly those ten extracted evidence roots.
- [ ] The machine JSON and human Markdown reports are committed without changing scenario, workflow, runner or runtime behavior.
- [ ] The completed task is archived and the active record removed.
- [ ] Exact final-head ownership, CI, review and protected `Required` gates pass before merge.

# Measurement policy

- Population size is exactly ten attempts.
- The initial PR-triggered physical execution is attempt 1.
- Attempts 2–10 are sequential reruns of the physical job only.
- No attempt may be hidden, replaced or retried out of the population.
- A failed attempt remains part of the population and must be classified from its retained evidence.
- Missing or duplicate evidence blocks the classification.
- No commit is allowed while attempts are being collected.
- The historical population in PR #925 is not reused.

# Expected classification

QRI-022 decides the outcome from the preserved evidence:

- ten clean gameplay successes plus certified cleanup: `pass`;
- a mixture of successes and failures: `unstable`;
- ten failures: `fail`;
- fewer than ten complete envelopes: `not-evaluated`;
- missing, duplicate or incomparable evidence: programme-level `blocked`.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T00:40:00+02:00
head: ef831709721b1a3c6130ddf81d6a2867a3bb1640
branch: test/e2e-qri-022-login-relog-baseline-v2
pr: 948
status: in_progress
context_routes:
  - agent-governance
  - universal-e2e
owned_paths:
  - docs/agents/tasks/active/CAN-20260726-e2e-qri-022-login-relog-baseline-v2.md
  - tests/e2e/baselines/login-relog-stability-baseline-v2.md
  - docs/e2e/baselines/E2E_LOGIN_RELOG_STABILITY_BASELINE_V2.md
  - docs/e2e/baselines/e2e-login-relog-stability-baseline-v2.json
proven:
  - PR #940 merged the failure-evidence retention repair as ad647f040a0f0b5b515c2416bf8aa11705dd7e8e.
  - The repair has controlled success and failure proofs and exact-head full CI.
  - PR #925 is closed without merge and remains an incomplete historical population.
  - Draft PR #948 targets repaired main and owns only new v2 output paths.
  - No physical attempt started on ef831709721b1a3c6130ddf81d6a2867a3bb1640 before the ownership failure was observed.
derived:
  - A new exact ten-attempt population is required; the old nine-envelope report cannot be upgraded by inference.
unknown:
  - Final stability classification of the new ten-attempt population.
conflicts: []
first_failure:
  marker: ownership-checkpoint-changed-paths-incomplete
  evidence: Agent Task Ownership run 30177921265 failed before any physical job; the checkpoint omitted tests/e2e/baselines/login-relog-stability-baseline-v2.md from changed_paths.
rejected_hypotheses:
  - Reuse nine successes from PR #925: rejected because they belong to a pre-repair population and the intended tenth attempt lacked evidence.
  - Modify workflow or scenario while measuring: rejected because this task owns evidence collection and classification only.
  - Retry until ten successes: rejected because every attempt must remain visible in the population.
  - Count the cancelled preflight run as attempt 1: rejected because no physical client job started.
changed_paths:
  - docs/agents/tasks/active/CAN-20260726-e2e-qri-022-login-relog-baseline-v2.md
  - tests/e2e/baselines/login-relog-stability-baseline-v2.md
validation:
  - command: Agent Task Ownership
    result: FAIL
    evidence: run 30177921265; checkpoint changed_paths omitted the immutable manifest.
blockers: []
next_action: Treat the commit containing this corrected checkpoint as the frozen measurement head, require ownership PASS, then collect exactly ten sequential physical attempts without further commits.
```
