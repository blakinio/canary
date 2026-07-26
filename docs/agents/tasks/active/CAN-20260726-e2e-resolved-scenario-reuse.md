---
task_id: CAN-20260726-e2e-resolved-scenario-reuse
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-RESOLVED-SCENARIO-REUSE-001
status: review
agent: "GPT-5.6 Thinking"
branch: fix/e2e-resolved-scenario-reuse
base_branch: main
created: 2026-07-26T09:08:00+02:00
updated: 2026-07-26T10:55:00+02:00
last_verified_commit: "cdba01cbdb9764ac1dae5ca38a0466c025b8cadc"
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
- [x] Canonical physical `login/relog` retains schema-v3 result and schema-v1 cleanup evidence on the exact repair head.
- [ ] Review state and protected final gate pass before merge.

# Confirmed evidence

- PR #948 run `30178099375` failed before scenario execution while repeating PR scenario selection; its incomplete artifact remains excluded.
- PR #953 run `30192743545` proved the selector repair by passing route metadata resolution and exact OTBM preparation, then exposed capture-shell termination before upload.
- PR #953 exact-head run `30193944277` completed the full `login/relog` path successfully, including evidence upload, propagation and the required gate.
- Artifact `8629798669` has digest `sha256:8ed8b3240b2131d65d0f8ab75ee1d32922cf8e51b94b3b9325dbc5396875f4a5`; `result.json` is schema v3 success, cleanup certification is schema v1 certified and `physical-exit-code.txt` is `0`.
- Exact-head ownership, autofix, CI and Universal Agent E2E runs all completed successfully on `cdba01cbdb9764ac1dae5ca38a0466c025b8cadc`.

# Delivered implementation

- `pr_scenario_selection.py` reuses only exact workflow-resolved physical identity and fails closed otherwise.
- `run_physical_e2e.sh` re-enters itself exactly once through `setsid` using `AGENT_E2E_CAPTURE_SESSION=1`.
- The outer script process remains outside the isolated child session and converts signal-style child termination to ordinary workflow failure.
- Existing result, cleanup and physical-exit-code finalization remains inside the isolated child.
- Focused tests cover both bounded mechanisms.

# Boundary

No scenario semantics, Canary runtime, OTClient code, workflow ordering, runner selection, retention policy, scheduling or retry policy changes.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T10:55:00+02:00
head: cdba01cbdb9764ac1dae5ca38a0466c025b8cadc
branch: fix/e2e-resolved-scenario-reuse
pr: 953
status: validating
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
  - Exact-head ownership, autofix, CI and Universal Agent E2E passed on cdba01cbdb9764ac1dae5ca38a0466c025b8cadc.
  - Run 30193944277 completed canonical physical login/relog, evidence upload, propagation and Required physical E2E successfully.
  - Artifact 8629798669 digest sha256:8ed8b3240b2131d65d0f8ab75ee1d32922cf8e51b94b3b9325dbc5396875f4a5 contains schema-v3 success result, schema-v1 certified cleanup and physical exit code 0.
  - PR 953 has no review comments recorded as of 2026-07-26T10:55:00+02:00.
derived:
  - The redundant scenario-resolution and capture-shell termination defects are repaired on the verified implementation head.
unknown:
  - Whether PR 953 remains mergeable after refreshing against the current main branch.
  - Whether the protected final gate has been forced and passed on the final task head.
conflicts: []
first_failure:
  marker: none
  evidence: No unmet runtime invariant remains in exact-head run 30193944277; only lifecycle and final-gate verification remain.
rejected_hypotheses:
  - Treat route-resolution repair alone as complete: rejected by run 30192743545 capture-shell termination.
  - Retry the pre-isolation head: rejected because it could not guarantee failure evidence upload.
  - Change login/relog semantics: rejected because exact-head run 30193944277 passed without scenario changes.
changed_paths:
  - docs/agents/tasks/active/CAN-20260726-e2e-resolved-scenario-reuse.md
  - tools/e2e/pr_scenario_selection.py
  - tools/e2e/run_physical_e2e.sh
  - tests/e2e/test_resolved_scenario_reuse.py
  - tests/e2e/test_physical_session_isolation.py
validation:
  - command: selector and physical-session focused tests
    result: PASS
    evidence: Exact reuse, fail-closed mismatch/missing identity, ordinary exit and SIGTERM isolation tests passed.
  - command: Agent Task Ownership run 30193944171
    result: PASS
    evidence: Exact-head ownership workflow completed successfully.
  - command: CI run 30193944299
    result: PASS
    evidence: Exact-head CI workflow completed successfully.
  - command: Universal Agent E2E run 30193944277
    result: PASS
    evidence: Physical login/relog, upload, propagation and required gate completed successfully; artifact 8629798669 retained.
blockers: []
next_action: Verify PR 953 current base and mergeability, apply ci:final-gate, perform the final task checkpoint commit, and require full protected checks on that exact final head before merge.
```
