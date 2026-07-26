---
task_id: CAN-20260726-e2e-controlled-server-prelifecycle-retention
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-QRI-022-RETENTION-003
status: ready
agent: "GPT-5.6 Thinking"
branch: fix/e2e-controlled-server-prelifecycle-retention
base_branch: main
created: 2026-07-26T19:08:00+02:00
updated: 2026-07-26T21:07:00+02:00
last_verified_commit: "8b9546302fc8038e8f7e3113bef87a38d16db543"
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
- [ ] Exact-final-head ownership, CI, physical E2E, review and merge gates pass.

# Result

The isolated repair is ready for final-head validation:

- controlled-server physical jobs no longer request the redundant exact-head `canary-linux-release` artifact;
- normal same-head physical jobs retain their existing artifact download path;
- setup failures after exact-head checkout and before physical lifecycle execution finalize the canonical schema-v3 infrastructure failure envelope;
- pre-lifecycle failures do not synthesize cleanup certification;
- evidence upload remains ordered before failure propagation;
- the temporary controlled-server validation pin was removed and its path is no longer claimed by this completed repair.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T21:07:00+02:00
head: 8b9546302fc8038e8f7e3113bef87a38d16db543
branch: fix/e2e-controlled-server-prelifecycle-retention
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
  - PR 961 merged the factual blocked baseline; attempts 8 through 10 of run 30198264756 failed before lifecycle at Download exact-head Canary binary after controlled-server build success
  - controlled-server jobs now skip canary-linux-release while normal exact-head jobs preserve the existing download and executable-resolution path
  - pre-lifecycle setup failures finalize the canonical result envelope before upload without synthesizing cleanup certification
  - focused workflow-structure and behavioral tests passed in CI run 30212484302 on 61d3bf82099646f1e5aeee1c53c43972835a5589
  - temporary controlled-server head e40ed1ce7314d3fb0b453e36ff3bce8693bb2f57 passed Universal Agent E2E run 30212632481
  - physical job 89823920090 built server 4bb098d6401a40659b3de2ef506f093eb35ea8d8, skipped Download exact-head Canary binary and passed login/relog plus Required physical E2E
  - artifact 8635242125 digest sha256:ed35af46b32947de0dfe256c5c34b23f56f0d47fdeb0f5ef404b0bf30c15fa93 retains schema-v3 success and schema-v1 cleanup certified with 18 of 18 checks
  - retained cell is login/relog with server 4bb098d6401a40659b3de2ef506f093eb35ea8d8, client 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f, data-otservbr-global and pr-required
  - temporary pin was removed by 45668db9cac3a543acd30254617e08e7d25e6e5a and .github/e2e-controlled-server.env is absent from the final changed-file set
  - pre-checkpoint head 45668db9cac3a543acd30254617e08e7d25e6e5a passed ownership 30214008198, CI 30214008285, autofix 30214008168 and Universal Agent E2E 30214008379
  - PR diff is limited to the workflow, focused test and this task record; the PR is ready and was mergeable before the final-gate commit
  - ci:final-gate was applied before final checkpoint commits
  - first final-gate ownership run 30216082439 found only checkpoint compactness overflow, with focused ownership tests and changed-file collection passing
  - this correction reduces proven evidence below the 16-item limit and releases the removed temporary-pin path from final ownership
  - no implementation or test behavior changed after the controlled-path validation

derived:
  - the corrected final-head physical validation must run in full because ci:final-gate remains applied
unknown:
  - outcome of corrected exact-final-head ownership CI physical E2E and review gates
conflicts: []
first_failure:
  marker: controlled-server-redundant-canary-download
  evidence: workflow run 30198264756 attempts 8 9 and 10 failed consistently after controlled-server build success
rejected_hypotheses:
  - retry or replace failed baseline attempts because the baseline contract forbids hidden replacement
  - create a new workflow or evidence schema because canonical Universal E2E and result envelope already exist
  - rely only on static validation because the repaired controlled-server path was physically exercised
changed_paths:
  - .github/workflows/universal-agent-e2e.yml
  - tests/e2e/test_failure_evidence_retention.py
  - docs/agents/tasks/active/CAN-20260726-e2e-controlled-server-prelifecycle-retention.md
validation:
  - command: focused failure evidence retention tests
    result: PASS
    evidence: CI run 30212484302
  - command: controlled-server physical login/relog and artifact retention
    result: PASS
    evidence: run 30212632481 job 89823920090 artifact 8635242125
  - command: first exact-final-head ownership gate
    result: FAIL
    evidence: run 30216082439 reported proven compactness 19 greater than 16; no code or test failure
blockers: []
next_action: Require all corrected exact-final-head checks to pass, verify no comments reviews or unresolved threads, then squash-merge PR 965.
```
