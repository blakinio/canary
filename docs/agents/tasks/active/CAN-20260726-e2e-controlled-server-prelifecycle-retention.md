---
task_id: CAN-20260726-e2e-controlled-server-prelifecycle-retention
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-QRI-022-RETENTION-003
status: implementing
agent: "GPT-5.6 Thinking"
branch: fix/e2e-controlled-server-prelifecycle-retention
base_branch: main
created: 2026-07-26T19:08:00+02:00
updated: 2026-07-26T19:08:00+02:00
last_verified_commit: "4bb098d6401a40659b3de2ef506f093eb35ea8d8"
risk: medium
related_issue: ""
related_pr: ""
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

# Acceptance criteria

- [ ] Controlled-server jobs skip the redundant exact-head Canary artifact download.
- [ ] Normal exact-head jobs still download and resolve `canary-linux-release`.
- [ ] A pre-lifecycle setup failure produces a valid schema-v3 infrastructure result envelope.
- [ ] Pre-lifecycle failure cleanup remains explicitly not certified.
- [ ] Evidence upload precedes failure propagation.
- [ ] Focused tests cover both controlled-server selection and pre-lifecycle finalization.
- [ ] Exact-final-head ownership, CI, physical E2E, review and merge gates pass.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T19:08:00+02:00
head: 4bb098d6401a40659b3de2ef506f093eb35ea8d8
branch: fix/e2e-controlled-server-prelifecycle-retention
pr: null
status: implementing
context_routes:
  - agent-governance
  - universal-e2e
owned_paths:
  - docs/agents/tasks/active/CAN-20260726-e2e-controlled-server-prelifecycle-retention.md
  - .github/workflows/universal-agent-e2e.yml
  - tests/e2e/test_failure_evidence_retention.py
proven:
  - main is 4bb098d6401a40659b3de2ef506f093eb35ea8d8
  - draft PR 961 preserves exactly ten attempts with attempts 8 through 10 failing before lifecycle at Download exact-head Canary binary
  - controlled-server physical jobs build CONTROLLED_SERVER_BIN before the exact-head artifact download
  - executable resolution already prefers CONTROLLED_SERVER_BIN when present
  - current workflow unconditionally downloads canary-linux-release
  - existing result envelope classifies infrastructure failures and cleanup absence without inventing certification
  - no open PR other than baseline 961 claims this exact workflow defect
derived:
  - exact-head Canary artifact download is unnecessary when a controlled server binary is selected
unknown:
  - exact focused implementation shape that preserves normal exact-head execution and canonical envelope validation
conflicts: []
first_failure:
  marker: controlled-server-redundant-canary-download
  evidence: workflow run 30198264756 attempts 8 9 and 10 failed consistently at Download exact-head Canary binary after controlled-server build success
rejected_hypotheses:
  - retry or replace failed baseline attempts because the baseline contract forbids hidden replacement
  - create a new workflow or evidence schema because canonical Universal E2E and result envelope already exist
changed_paths:
  - docs/agents/tasks/active/CAN-20260726-e2e-controlled-server-prelifecycle-retention.md
validation:
  - command: live main and overlap preflight
    result: PASS
    evidence: main 4bb098d6401a40659b3de2ef506f093eb35ea8d8; no competing workflow-fix PR
blockers: []
next_action: Open a draft PR and implement the controlled-server download guard with canonical pre-lifecycle failure finalization and focused tests.
```
