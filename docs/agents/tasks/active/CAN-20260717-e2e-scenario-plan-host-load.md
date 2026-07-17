---
task_id: CAN-20260717-e2e-scenario-plan-host-load
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-E2E-PLAN-LOAD-001
status: implementing
agent: "GPT-5.5 Thinking"
branch: fix/e2e-scenario-plan-host-load
base_branch: main
created: 2026-07-17T15:42:00+02:00
updated: 2026-07-17T15:52:00+02:00
last_verified_commit: "6619598b43b0c9b0bb0062dfba904e22003127b3"
risk: medium
related_issue: ""
related_pr: "483"
depends_on:
  - CAN-20260717-e2e-pr-scenario-selection
blocks:
  - CAN-20260717-physical-movement-e2e-v2
owned_paths:
  exclusive:
    - tools/e2e/client/agent_e2e_scenario.lua
    - tests/e2e/test_agent_e2e_scenario_plan.py
    - docs/agents/tasks/active/CAN-20260717-e2e-scenario-plan-host-load.md
  shared: []
  read_only:
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/run_physical_e2e.sh
    - .github/workflows/universal-agent-e2e.yml
modules_touched:
  - Universal OTS E2E physical gameplay action-plan loader
reuses:
  - existing generated scenario-plan.lua contract
  - existing generic controlled-OTClient scenario driver
  - existing Universal Agent E2E workflow and physical runner
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Make the existing generic physical OTClient driver read the already-generated `scenario-plan.lua` from the host evidence directory without changing the scenario-plan contract or creating another runner.

# Acceptance criteria

- [x] Preserve the existing generated `scenario-plan.lua` format and source-of-truth resolver.
- [x] Read the plan through host filesystem I/O that works for the external artifact directory.
- [x] Keep the same validated plan content and runtime behavior.
- [x] Fail closed with distinct read/load/runtime errors.
- [x] Add a focused regression that prevents returning to `dofile(PLAN_PATH)` for the host artifact path.
- [x] Keep workflow, physical runner and scenario resolver unchanged.
- [ ] Pass focused tests and applicable exact-final-head gates.
- [ ] Squash merge before retrying the blocked movement PR.

## Proven blocker

Universal Agent E2E run `29582792694` selected `movement/physical-movement` on exact head `83f7dff29bae00bdd1f31596fde870a3ec3f3c04`. Its evidence artifact `8408520847` contains `scenario-plan.lua`, while the controlled OTClient reported that `dofile` could not open the absolute plan path. The same evidence directory successfully accepted `client-events.tsv` through `io.open`, isolating the boundary to plan loading rather than plan generation.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T15:52:00+02:00
head: 6619598b43b0c9b0bb0062dfba904e22003127b3
branch: fix/e2e-scenario-plan-host-load
pr: 483
status: implementing
context_routes:
  - universal-e2e
  - agent-governance
owned_paths:
  - tools/e2e/client/agent_e2e_scenario.lua
  - tests/e2e/test_agent_e2e_scenario_plan.py
  - docs/agents/tasks/active/CAN-20260717-e2e-scenario-plan-host-load.md
proven:
  - selected non-default physical scenario execution works through merged PR 477
  - run 29582792694 reached the exact selected physical-client job
  - scenario-plan.lua was present in evidence artifact 8408520847
  - driver io.open writes to the same external evidence directory successfully
  - dofile on the absolute external plan path failed before login
  - PR 483 changes exactly the generic client driver, its focused regression test and this task record
  - driver now reads PLAN_PATH through io.open and loads the same generated plan content through the OTClient Lua runtime
  - PR patch audit shows no workflow, physical-runner or resolver changes
unknown:
  - exact-head CI and physical E2E conclusions for PR 483
  - whether movement succeeds after PR 483 is merged and PR 481 is retriggered
conflicts: []
first_failure:
  marker: scenario-plan-host-load
  evidence: physical artifact 8408520847 from run 29582792694
rejected_hypotheses:
  - missing scenario-plan generation
  - treating the failed run as movement proof
  - creating a second physical runner or workflow
changed_paths:
  - docs/agents/tasks/active/CAN-20260717-e2e-scenario-plan-host-load.md
  - tests/e2e/test_agent_e2e_scenario_plan.py
  - tools/e2e/client/agent_e2e_scenario.lua
validation:
  - command: PR changed-file and patch audit
    result: PASS
    evidence: exactly three expected paths and no workflow or runner changes
blockers: []
next_action: Require PR 483 Ownership, CI and Universal Agent E2E success, then prepare exact-final-head validation and squash merge before retrying PR 481.
```
