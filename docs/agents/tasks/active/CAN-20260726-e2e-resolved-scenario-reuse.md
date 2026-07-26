---
task_id: CAN-20260726-e2e-resolved-scenario-reuse
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-RESOLVED-SCENARIO-REUSE-001
status: implementing
agent: "GPT-5.6 Thinking"
branch: fix/e2e-resolved-scenario-reuse
base_branch: main
created: 2026-07-26T09:08:00+02:00
updated: 2026-07-26T10:02:00+02:00
last_verified_commit: "1e93c4f4daadae3dee36c7f24689f89a2abaab98"
risk: medium
related_issue: ""
related_pr: "953"
depends_on:
  - "Physical failure evidence retention repair merged in PR #940"
  - "Incomplete post-repair baseline PR #948 closed without merge"
blocks:
  - "Fresh exact ten-attempt login/relog stability baseline"
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260726-e2e-resolved-scenario-reuse.md
    - tools/e2e/pr_scenario_selection.py
    - tools/e2e/run_physical_e2e.sh
    - tests/e2e/test_resolved_scenario_reuse.py
    - tests/e2e/test_physical_session_isolation.py
  shared: []
  read_only:
    - .github/workflows/universal-agent-e2e.yml
    - tools/e2e/run_agent_e2e.py
    - tests/e2e/test_failure_evidence_retention.py
    - tests/e2e/scenarios/login/scenario.json
modules_touched:
  - Universal Agent E2E scenario resolution and physical process isolation
reuses:
  - existing PR scenario selector
  - existing resolved workflow outputs
  - existing capture-upload-propagate workflow contract
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Make the physical-client job reuse the exact scenario identity already proven by `Resolve scenario` and isolate the complete physical runner process session so child failures or signals cannot terminate the workflow capture shell before evidence upload.

# Acceptance criteria

- [x] Reuse is limited to `GITHUB_JOB=physical-client`.
- [x] The resolved suite and scenario must both be present and exactly match the requested values.
- [x] Missing or mismatched identity fails closed.
- [x] Non-physical callers retain existing PR selection.
- [x] Focused selector tests cover exact reuse, missing identity, mismatch and unchanged non-PR behavior.
- [x] The complete physical runner is launched once in an independent session.
- [x] Ordinary child exit codes are preserved and signal-style exits are normalized to workflow failure after isolation.
- [x] Focused process tests cover ordinary failure, SIGTERM isolation and single-session entry.
- [ ] Canonical physical `login/relog` retains schema-v3 result and schema-v1 cleanup evidence on the exact repair head.
- [ ] Exact-head ownership, CI, review and protected gates pass before merge.

# Confirmed evidence

- PR #948 run `30178099375` failed before scenario execution while repeating PR scenario selection; its incomplete artifact remains excluded.
- PR #953 run `30192743545` proved the selector repair: route metadata resolution and OTBM preparation passed.
- The same run then failed inside `Run selected physical-client scenario`; GitHub skipped upload and propagate, leaving no physical artifact.
- The workflow source already contains `set +e`, explicit status capture, `if: always()` upload and later propagation, so the observed skip indicates the capture shell itself did not survive the child execution path.

# Delivered implementation

- `pr_scenario_selection.py` reuses only exact workflow-resolved physical identity and fails closed otherwise.
- `run_physical_e2e.sh` now re-enters itself exactly once through `setsid` using `AGENT_E2E_CAPTURE_SESSION=1`.
- The outer script process remains outside the isolated child session and converts signal-style child termination to ordinary workflow failure.
- Existing result, cleanup and physical-exit-code finalization remains inside the isolated child.
- Focused tests cover both bounded mechanisms.

# Boundary

No scenario semantics, Canary runtime, OTClient code, workflow ordering, runner selection, retention policy, scheduling or retry policy changes.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T10:02:00+02:00
head: 1e93c4f4daadae3dee36c7f24689f89a2abaab98
branch: fix/e2e-resolved-scenario-reuse
pr: 953
status: implementing
context_routes:
  - agent-governance
  - universal-e2e
owned_paths:
  - docs/agents/tasks/active/CAN-20260726-e2e-resolved-scenario-reuse.md
  - tools/e2e/pr_scenario_selection.py
  - tools/e2e/run_physical_e2e.sh
  - tests/e2e/test_resolved_scenario_reuse.py
  - tests/e2e/test_physical_session_isolation.py
proven:
  - Exact physical-job selector reuse passes four focused tests.
  - Run 30192743545 passed route metadata resolution and exact OTBM preparation, removing the PR 948 first failure.
  - The workflow capture shell still did not reach upload after the physical child failure in job 89771011878.
derived:
  - Isolating the entire physical script session is required in addition to isolating its lifecycle child.
unknown:
  - Exact lower-level gameplay or infrastructure failure from job 89771011878 because no artifact was retained.
  - Whether the new isolated exact head produces a successful or contract-complete failed physical artifact.
conflicts: []
first_failure:
  marker: physical-capture-shell-terminated-before-upload
  evidence: run 30192743545 job 89771011878 passed route preparation, failed physical execution and skipped upload/propagate.
rejected_hypotheses:
  - Treat route-resolution repair alone as complete: rejected by physical proof 30192743545.
  - Retry the same exact head until success: rejected because it would not repair missing failure evidence.
  - Change login/relog semantics: rejected because the defect is process containment and evidence handoff.
changed_paths:
  - docs/agents/tasks/active/CAN-20260726-e2e-resolved-scenario-reuse.md
  - tools/e2e/pr_scenario_selection.py
  - tools/e2e/run_physical_e2e.sh
  - tests/e2e/test_resolved_scenario_reuse.py
  - tests/e2e/test_physical_session_isolation.py
validation:
  - command: selector focused tests
    result: PASS
    evidence: four independent tests passed before physical proof.
  - command: Universal Agent E2E run 30192743545
    result: FAIL
    evidence: selector repair passed route preparation; physical child failure still terminated capture before upload.
blockers: []
next_action: Require exact-head ownership and focused CI on the process-isolated repair, then inspect the next physical artifact before lifecycle closure.
```
