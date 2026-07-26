---
task_id: CAN-20260726-e2e-resolved-scenario-reuse
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-RESOLVED-SCENARIO-REUSE-001
status: implementing
agent: "GPT-5.6 Thinking"
branch: fix/e2e-resolved-scenario-reuse
base_branch: main
created: 2026-07-26T09:08:00+02:00
updated: 2026-07-26T09:25:00+02:00
last_verified_commit: "178efcdd907162ada14bea57b655d5183c267437"
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
    - tests/e2e/test_resolved_scenario_reuse.py
  shared: []
  read_only:
    - .github/workflows/universal-agent-e2e.yml
    - tools/e2e/run_agent_e2e.py
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

- [x] Reuse is limited to the GitHub Actions job key `physical-client`.
- [x] The pre-resolved suite and scenario must both be present and exactly match the requested values.
- [x] Missing or mismatched resolved identity fails closed.
- [x] Non-physical callers retain the existing PR scenario-selection behavior.
- [x] Focused unit tests cover exact reuse, missing identity, mismatch rejection and the unchanged non-PR path.
- [ ] Canonical physical `login/relog` produces schema-v3 result and schema-v1 cleanup evidence on the exact repair head.
- [ ] Exact-head ownership, CI, review and protected gates pass before merge.

# Confirmed evidence

- PR #948 run `30178099375` completed both controlled builds but failed in physical job `89732680833` while repeating scenario selection in `Resolve route preparation metadata`.
- The dedicated `Resolve scenario` job in that run succeeded and exported `login/relog`.
- Artifact `8625053593` retained an empty scenario manifest and no contract result; physical execution never started.
- PR #948 is closed without merge and none of its evidence is reused.

# Delivered implementation

- `tools/e2e/pr_scenario_selection.py` returns the already proven identity only when `GITHUB_JOB=physical-client`.
- Missing identity or an exact requested/resolved mismatch raises `SelectionError` before execution.
- All other jobs and non-PR invocations retain the previous selector path.
- `tests/e2e/test_resolved_scenario_reuse.py` covers the bounded behavior.
- The temporary patch workflow was removed and is absent from the final repair diff.

# Boundary

No scenario semantics, Canary runtime, OTClient code, runner, retention policy, scheduling or retry behavior changes.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T09:25:00+02:00
head: 178efcdd907162ada14bea57b655d5183c267437
branch: fix/e2e-resolved-scenario-reuse
pr: 953
status: implementing
context_routes:
  - agent-governance
  - universal-e2e
owned_paths:
  - docs/agents/tasks/active/CAN-20260726-e2e-resolved-scenario-reuse.md
  - tools/e2e/pr_scenario_selection.py
  - tests/e2e/test_resolved_scenario_reuse.py
proven:
  - The dedicated Resolve scenario job succeeded before physical job failure in run 30178099375.
  - PR 948 is closed without merge and its incomplete attempt is excluded from future populations.
  - The repair is limited to exact physical-job reuse with fail-closed missing/mismatch checks.
derived:
  - The physical job no longer needs a second immutable PR-delta lookup for the already selected scenario identity.
unknown:
  - Whether the exact repair head completes canonical physical login/relog after the redundant lookup is removed.
conflicts: []
first_failure:
  marker: duplicate-physical-scenario-resolution
  evidence: run 30178099375 job 89732680833 failed at Resolve route preparation metadata before physical scenario execution.
rejected_hypotheses:
  - Retry PR 948 until green: rejected because its incomplete attempt is already factual evidence.
  - Trust arbitrary environment values: rejected because physical reuse requires both values and exact equality.
  - Change login/relog semantics: rejected because the failure is in workflow handoff.
changed_paths:
  - docs/agents/tasks/active/CAN-20260726-e2e-resolved-scenario-reuse.md
  - tools/e2e/pr_scenario_selection.py
  - tests/e2e/test_resolved_scenario_reuse.py
validation:
  - command: local py_compile reconstruction
    result: PASS
    evidence: reconstructed selector compiled before repository update.
blockers: []
next_action: Require exact-head ownership and CI on PR 953, then inspect the canonical physical login/relog artifact before lifecycle closure.
```
