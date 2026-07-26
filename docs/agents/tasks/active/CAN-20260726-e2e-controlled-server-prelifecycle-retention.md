---
task_id: CAN-20260726-e2e-controlled-server-prelifecycle-retention
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-QRI-022-RETENTION-003
status: implementing
agent: "GPT-5.6 Thinking"
branch: fix/e2e-controlled-server-prelifecycle-retention
base_branch: main
created: 2026-07-26T19:08:00+02:00
updated: 2026-07-26T19:26:00+02:00
last_verified_commit: "61d3bf82099646f1e5aeee1c53c43972835a5589"
risk: medium
related_issue: ""
related_pr: "965"
depends_on:
  - "Blocked ten-attempt login/relog baseline retained in draft PR #961"
  - "Controlled physical-lifecycle nonzero-result retention merged in PR #940"
  - "Canonical schema-v3 result envelope and schema-v1 cleanup certification"
blocks:
  - "Fresh exact ten-attempt login/relog stability certification"
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260726-e2e-controlled-server-prelifecycle-retention.md
    - .github/workflows/universal-agent-e2e.yml
    - .github/e2e-controlled-server.env
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
- [ ] Temporary controlled-server physical validation passes and retains complete evidence.
- [ ] Temporary controlled-server pin is removed before readiness.
- [ ] Exact-final-head ownership, CI, physical E2E, review and merge gates pass.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T19:26:00+02:00
head: 61d3bf82099646f1e5aeee1c53c43972835a5589
branch: fix/e2e-controlled-server-prelifecycle-retention
pr: 965
status: validating
context_routes:
  - agent-governance
  - universal-e2e
owned_paths:
  - docs/agents/tasks/active/CAN-20260726-e2e-controlled-server-prelifecycle-retention.md
  - .github/workflows/universal-agent-e2e.yml
  - .github/e2e-controlled-server.env
  - tests/e2e/test_failure_evidence_retention.py
proven:
  - main is 4bb098d6401a40659b3de2ef506f093eb35ea8d8 at branch creation
  - draft PR 965 targets main from the isolated workflow-fix branch
  - draft PR 961 preserves exactly ten attempts with attempts 8 through 10 failing before lifecycle at Download exact-head Canary binary
  - controlled-server physical jobs now skip the exact-head canary-linux-release download
  - executable resolution now searches only artifact roots that are required for the selected server source
  - pre-lifecycle setup failures now invoke the canonical result-envelope finalizer before evidence upload
  - pre-lifecycle cleanup remains not certified because no cleanup certification is synthesized
  - CI run 30212484302 passed on implementation head 61d3bf82099646f1e5aeee1c53c43972835a5589
  - focused behavioral and workflow-structure tests passed in CI
derived:
  - a temporary controlled-server pin is required to physically exercise the repaired branch because the ordinary PR event uses exact-head Canary
unknown:
  - outcome and retained evidence of the temporary controlled-server physical validation
  - outcome of exact-final-head gates after removing the temporary pin
conflicts: []
first_failure:
  marker: controlled-server-redundant-canary-download
  evidence: workflow run 30198264756 attempts 8 9 and 10 failed consistently at Download exact-head Canary binary after controlled-server build success
rejected_hypotheses:
  - retry or replace failed baseline attempts because the baseline contract forbids hidden replacement
  - create a new workflow or evidence schema because canonical Universal E2E and result envelope already exist
  - rely only on static validation because the repaired controlled-server path can be exercised with a temporary same-repository pin
changed_paths:
  - .github/workflows/universal-agent-e2e.yml
  - tests/e2e/test_failure_evidence_retention.py
  - docs/agents/tasks/active/CAN-20260726-e2e-controlled-server-prelifecycle-retention.md
validation:
  - command: live main and overlap preflight
    result: PASS
    evidence: no competing workflow-fix PR
  - command: CI
    result: PASS
    evidence: run 30212484302 on 61d3bf82099646f1e5aeee1c53c43972835a5589
  - command: focused failure evidence retention tests
    result: PASS
    evidence: implementation CI completed successfully
  - command: ordinary exact-head Universal Agent E2E
    result: IN_PROGRESS
    evidence: run 30212484393
blockers: []
next_action: Complete the ordinary exact-head E2E run, then add one temporary controlled-server pin and require the repaired path to retain complete physical evidence.
```
