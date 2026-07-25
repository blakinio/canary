---
task_id: CAN-20260725-e2e-failure-evidence-retention
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-FAILURE-EVIDENCE-RETENTION-001
status: implementing
agent: "GPT-5.6 Thinking"
branch: fix/e2e-failure-evidence-retention
base_branch: main
created: 2026-07-25T21:05:00+02:00
updated: 2026-07-25T21:05:00+02:00
last_verified_commit: "8ef88972fd1c473b9f3c0a5cfb9bed98c78bdbc9"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - "Blocked baseline PR #925 and Universal Agent E2E run 30167381956"
blocks:
  - "CAN-20260725-e2e-qri-022-login-relog-baseline"
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260725-e2e-failure-evidence-retention.md
    - .github/workflows/universal-agent-e2e.yml
    - tools/e2e/run_physical_e2e.sh
    - tests/e2e/test_failure_evidence_retention.py
    - tests/e2e/scenarios/retention/failure-evidence-probe.json
  shared:
    - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
  read_only:
    - tools/e2e/run_physical_e2e_lifecycle.sh
    - tools/e2e/result_envelope.py
    - tools/e2e/result_envelope_impl.py
    - tools/e2e/cleanup_certification.py
    - tests/e2e/scenarios/login/scenario.json
    - docs/e2e/baselines/E2E_LOGIN_RELOG_STABILITY_BASELINE.md
modules_touched:
  - Universal Agent E2E workflow failure evidence retention
reuses:
  - canonical physical lifecycle and schema-v3 result envelope
  - schema-v1 cleanup certification
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Guarantee that an ordinary non-zero physical scenario result is uploaded as Universal E2E evidence before the physical job is marked failed.

# Acceptance criteria

- [ ] The physical command exit code is captured without ending the workflow step.
- [ ] Universal E2E evidence upload runs before failure is propagated to the job.
- [ ] The Required physical E2E gate remains red when the physical scenario fails.
- [ ] A controlled temporary failing scenario proves that result and cleanup evidence are retained.
- [ ] The temporary probe scenario is removed before final review.
- [ ] Canonical login/relog still succeeds on the exact final head.
- [ ] Agent Task Ownership, CI and final-gate checks pass on the exact final head.
- [ ] No scenario semantics, retry policy or success criteria are weakened.

# Confirmed blocker

Run `30167381956` retained nine complete successful login/relog attempts. Physical job `89708625391` then failed and GitHub recorded the declared `if: always()` evidence-upload step as skipped. Diagnostic job `89709267589` was cancelled in the physical step and again retained no Universal E2E artifact. PR #925 therefore remains blocked.

# Implementation boundary

The workflow will capture the physical command status, upload the artifact directory, then use a separate step to return the captured status. The canonical lifecycle remains responsible for producing `result.json` and cleanup certification. No retry is added and no failed attempt is converted into success.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T21:05:00+02:00
head: 8ef88972fd1c473b9f3c0a5cfb9bed98c78bdbc9
branch: fix/e2e-failure-evidence-retention
status: implementing
context_routes:
  - agent-governance
  - universal-e2e
proven:
  - PR 925 is blocked because a failed physical job retained no result or cleanup artifact.
  - The existing workflow uploads evidence only after the physical shell step.
derived:
  - A non-failing capture step followed by upload and explicit failure propagation preserves both evidence and gate semantics.
unknown:
  - Exact lower-level cause of the original physical failure.
conflicts: []
first_failure:
  marker: physical-failure-evidence-not-retained
  evidence: run 30167381956, physical job 89708625391, upload step skipped.
changed_paths:
  - docs/agents/tasks/active/CAN-20260725-e2e-failure-evidence-retention.md
validation: []
blockers: []
next_action: Open the bounded draft PR and wait for ownership preflight before changing the workflow.
```
