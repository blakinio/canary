---
task_id: CAN-20260726-e2e-controlled-server-prelifecycle-retention
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-QRI-022-RETENTION-003
status: ready
agent: "GPT-5.6 Thinking"
branch: fix/e2e-controlled-server-prelifecycle-retention
base_branch: main
created: 2026-07-26T19:08:00+02:00
updated: 2026-07-26T22:46:00+02:00
last_verified_commit: "698c8698a98571ca61715779f8bb67af6f659fc7"
risk: medium
related_issue: ""
related_pr: "965"
depends_on:
  - "Blocked ten-attempt login/relog baseline merged in PR #961 as 191d628259c05048cae3c9b9a0a9b233de6294f4"
  - "Controlled physical-lifecycle nonzero-result retention merged in PR #940"
  - "Canonical schema-v3 result envelope and schema-v1 cleanup certification"
blocks:
  - "Fresh exact ten-attempt login/relog stability certification"
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260726-e2e-controlled-server-prelifecycle-retention.md
    - .github/workflows/universal-agent-e2e.yml
    - tests/e2e/test_failure_evidence_retention.py
  shared: []
  read_only:
    - tools/e2e/result_envelope.py
    - tools/e2e/result_envelope_impl.py
    - tools/e2e/run_physical_e2e.sh
    - tools/e2e/cleanup_certification.py
    - docs/e2e/E2E_STABILITY_CERTIFICATION.md
    - tests/e2e/baselines/login-relog-stability-baseline-20260726.md
modules_touched:
  - Universal Agent E2E workflow evidence retention
reuses:
  - canonical Universal Agent E2E physical-client job
  - canary-universal-e2e-result-envelope-v1 schema version 3
  - existing universal-agent-e2e evidence artifact
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Remove the redundant exact-head Canary artifact download from controlled-server physical jobs and retain a canonical fail-closed schema-v3 result envelope when setup fails before `run_physical_e2e.sh` starts.

# Scope

- Keep the existing Universal Agent E2E workflow and artifact path.
- Skip `canary-linux-release` download only when `needs.resolve.outputs.server_repository` selects a controlled server whose binary was built in the physical job.
- Preserve the exact-head Canary artifact path for normal same-head execution.
- Finalize a schema-v3 infrastructure failure envelope from the existing result-envelope implementation when any post-checkout setup step prevents the physical lifecycle from starting.
- Do not claim cleanup certification when the lifecycle never starts.
- Upload evidence before propagating failure.
- Add focused static/behavioral tests; do not create a second runner, workflow or evidence schema.
- Use one temporary same-repository controlled-server pin to exercise the repaired path, then remove it before readiness.

# Acceptance criteria

- [x] Controlled-server jobs skip the redundant exact-head Canary artifact download.
- [x] Normal exact-head jobs still download and resolve `canary-linux-release`.
- [x] A pre-lifecycle setup failure produces a valid schema-v3 infrastructure result envelope.
- [x] Pre-lifecycle failure cleanup remains explicitly not certified.
- [x] Evidence upload precedes failure propagation.
- [x] Focused tests cover both controlled-server selection and pre-lifecycle finalization.
- [x] Temporary controlled-server physical validation passes and retains complete evidence.
- [x] Temporary controlled-server pin is removed before readiness.
- [x] Exact-final-head ownership, CI, physical E2E, review and merge gates pass.

# Result

The isolated workflow repair was squash-merged in PR #965 as `698c8698a98571ca61715779f8bb67af6f659fc7`:

- controlled-server jobs no longer request the redundant exact-head `canary-linux-release` artifact;
- normal exact-head jobs retain their existing artifact download path;
- setup failures before physical lifecycle execution finalize the canonical schema-v3 infrastructure failure envelope;
- pre-lifecycle failures do not synthesize cleanup certification;
- evidence upload remains ordered before failure propagation;
- the temporary controlled-server validation pin was removed before merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T20:46:00Z
head: 698c8698a98571ca61715779f8bb67af6f659fc7
branch: main
pr: 965
status: ready
context_routes:
  - agent-governance
  - universal-e2e
owned_paths:
  - docs/agents/tasks/active/CAN-20260726-e2e-controlled-server-prelifecycle-retention.md
  - .github/workflows/universal-agent-e2e.yml
  - tests/e2e/test_failure_evidence_retention.py
proven:
  - PR 965 squash-merged the isolated repair into main as 698c8698a98571ca61715779f8bb67af6f659fc7
  - controlled-server jobs skip canary-linux-release while normal exact-head jobs preserve the download and executable-resolution path
  - pre-lifecycle setup failures finalize the canonical schema-v3 result envelope before evidence upload without synthesizing cleanup certification
  - temporary controlled-server validation run 30212632481 job 89823920090 passed login/relog and Required physical E2E while skipping Download exact-head Canary binary
  - artifact 8635242125 digest sha256:ed35af46b32947de0dfe256c5c34b23f56f0d47fdeb0f5ef404b0bf30c15fa93 retains schema-v3 success and schema-v1 cleanup certified with 18 of 18 checks
  - final head b021b6729c92b9b103e0c401e2764de0433f75b8 passed ownership 30216205699, autofix 30216205716, CI 30216205834 and Universal Agent E2E 30216205871
  - final exact-head physical job 89833603848 downloaded Canary normally and passed login/relog plus Required physical E2E job 89833811257
  - PR 965 had no comments, reviews or unresolved review threads before merge
  - merge commit 698c8698a98571ca61715779f8bb67af6f659fc7 was identical to main immediately after merge
derived:
  - the workflow defect that blocked attempts 8 through 10 of the first baseline is repaired and a fresh factual ten-attempt population is unblocked
unknown: []
conflicts: []
first_failure:
  marker: controlled-server-redundant-canary-download
  evidence: baseline run 30198264756 attempts 8 through 10 failed after controlled-server build success at Download exact-head Canary binary
rejected_hypotheses:
  - retry or replace the failed baseline attempts because the measurement contract forbids hidden replacement
  - create a second workflow or evidence schema because the canonical Universal E2E lifecycle and result envelope already cover the required behavior
changed_paths:
  - .github/workflows/universal-agent-e2e.yml
  - tests/e2e/test_failure_evidence_retention.py
  - docs/agents/tasks/active/CAN-20260726-e2e-controlled-server-prelifecycle-retention.md
validation:
  - command: focused failure evidence retention tests
    result: PASS
    evidence: CI run 30212484302
  - command: controlled-server physical login/relog and retained evidence
    result: PASS
    evidence: run 30212632481 job 89823920090 artifact 8635242125
  - command: exact-final-head ownership autofix CI and Universal Agent E2E
    result: PASS
    evidence: runs 30216205699 30216205716 30216205834 and 30216205871
  - command: review and merge gate
    result: PASS
    evidence: no comments reviews or unresolved threads; PR 965 merged as 698c8698a98571ca61715779f8bb67af6f659fc7
blockers: []
next_action: Create a fresh isolated task and draft PR for exactly ten sequential controlled-server login/relog attempts on current main, with no replacement retries, then generate QRI-022 with minimum_runs=10.
```
