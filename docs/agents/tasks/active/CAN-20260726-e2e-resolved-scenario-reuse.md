---
task_id: CAN-20260726-e2e-resolved-scenario-reuse
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-RESOLVED-SCENARIO-REUSE-001
status: implementing
agent: "GPT-5.6 Thinking"
branch: fix/e2e-resolved-scenario-reuse
base_branch: main
created: 2026-07-26T09:08:00+02:00
updated: 2026-07-26T09:08:00+02:00
last_verified_commit: "a4a35495d4a8dc047bd3315b95c9fb577ac597af"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - "Physical failure evidence retention repair merged in PR #940"
  - "Incomplete post-repair baseline PR #948 closed without merge"
blocks:
  - "Fresh exact ten-attempt login/relog stability baseline"
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260726-e2e-resolved-scenario-reuse.md
    - tools/e2e/run_agent_e2e.py
    - tests/e2e/test_resolved_scenario_reuse.py
  shared: []
  read_only:
    - .github/workflows/universal-agent-e2e.yml
    - tools/e2e/pr_scenario_selection.py
    - tests/e2e/scenarios/login/scenario.json
modules_touched:
  - Universal Agent E2E scenario resolution handoff
reuses:
  - existing PR scenario selector
  - existing resolved workflow outputs
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Make the physical-client job reuse the exact scenario identity already proven by the earlier `Resolve scenario` job instead of repeating pull-request changed-path selection.

# Acceptance criteria

- [ ] Reuse is limited to the GitHub Actions job key `physical-client`.
- [ ] The pre-resolved suite and scenario must both be present and exactly match the requested values.
- [ ] Missing or mismatched resolved identity fails closed.
- [ ] Non-physical callers retain the existing PR scenario-selection behavior.
- [ ] Focused unit tests cover exact reuse, missing identity and mismatch rejection.
- [ ] Canonical physical `login/relog` produces schema-v3 result and schema-v1 cleanup evidence on the exact repair head.
- [ ] Exact-head ownership, CI, review and protected gates pass before merge.

# Confirmed evidence

- PR #948 run `30178099375` completed both controlled builds but failed in physical job `89732680833` while re-running `run_agent_e2e.py resolve` inside `Resolve route preparation metadata`.
- The earlier dedicated `Resolve scenario` job in the same run succeeded and exported suite `login` and scenario `relog`.
- The failed physical artifact `8625053593` retained an empty `scenario-manifest.json`; physical execution never started.
- The physical job already receives `AGENT_E2E_SUITE` and `AGENT_E2E_SCENARIO_ID` from `needs.resolve.outputs`.

# Boundary

- No scenario semantics, Canary runtime, OTClient code, runner, retention policy, scheduling or retry behavior changes.
- This repair does not reuse or upgrade the incomplete populations from PR #925 or PR #948.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T09:08:00+02:00
head: a4a35495d4a8dc047bd3315b95c9fb577ac597af
branch: fix/e2e-resolved-scenario-reuse
pr: none
status: implementing
context_routes:
  - agent-governance
  - universal-e2e
owned_paths:
  - docs/agents/tasks/active/CAN-20260726-e2e-resolved-scenario-reuse.md
  - tools/e2e/run_agent_e2e.py
  - tests/e2e/test_resolved_scenario_reuse.py
proven:
  - The dedicated Resolve scenario job succeeded before the physical job in run 30178099375.
  - The physical job failed while repeating scenario resolution and retained an empty scenario manifest.
  - The physical job receives the proven suite and scenario as workflow job environment values.
derived:
  - Reusing the exact matching workflow-resolved identity removes the redundant PR delta lookup while preserving fail-closed selection.
unknown:
  - Whether the next canonical physical run has any independent runtime failure after scenario resolution succeeds.
conflicts: []
first_failure:
  marker: duplicate-physical-scenario-resolution
  evidence: run 30178099375 job 89732680833 failed at Resolve route preparation metadata before physical scenario execution.
rejected_hypotheses:
  - Retry PR 948 until green: rejected because its first incomplete attempt is already part of that population.
  - Trust arbitrary environment values: rejected; reuse is limited to physical-client and requires exact equality with requested values.
  - Change the login/relog scenario: rejected because the defect is in workflow handoff, not scenario semantics.
changed_paths:
  - docs/agents/tasks/active/CAN-20260726-e2e-resolved-scenario-reuse.md
validation:
  - command: fresh main and incomplete-population preflight
    result: PASS
    evidence: main a4a35495d4a8dc047bd3315b95c9fb577ac597af; PR 948 closed without merge.
blockers: []
next_action: Apply the bounded resolver patch and focused tests, then open a draft PR and require exact-head ownership before physical proof.
```
