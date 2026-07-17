---
task_id: CAN-20260717-e2e-scenario-plan-host-load
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-E2E-PLAN-LOAD-001
status: implementing
agent: "GPT-5.5 Thinking"
branch: fix/e2e-scenario-plan-host-load
base_branch: main
created: 2026-07-17T15:42:00+02:00
updated: 2026-07-17T15:42:00+02:00
last_verified_commit: "9bb6ffe2941a447eff4166cecc714992db166d93"
risk: medium
related_issue: ""
related_pr: ""
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

Make the existing generic physical OTClient driver load the already-generated `scenario-plan.lua` from the host evidence directory without changing the scenario-plan contract or creating another runner.

# Acceptance criteria

- [x] Preserve the existing generated `scenario-plan.lua` format and source-of-truth resolver.
- [ ] Read the plan through host filesystem I/O that works for the external absolute artifact directory.
- [ ] Compile and execute only that generated plan content with the existing OTClient Lua runtime.
- [ ] Fail closed with distinct open/compile/execute errors.
- [ ] Add a focused regression that prevents returning to `dofile(PLAN_PATH)` for the host artifact path.
- [ ] Keep workflow, physical runner and scenario resolver unchanged.
- [ ] Pass focused tests and applicable exact-final-head gates.
- [ ] Squash merge before retrying the blocked movement PR.

## Proven blocker

Universal Agent E2E run `29582792694` selected `movement/physical-movement` on exact head `83f7dff29bae00bdd1f31596fde870a3ec3f3c04`. Its physical job produced artifact `8408520847` (`sha256:9c8265545884d03990b4693d32170737e1743e40b242a0b9b8bacded55194477`). The artifact contains `scenario-plan.lua`, but the controlled OTClient failed before login with `failed to load scenario plan: unable to open file '/home/runner/work/canary/canary/artifacts/scenario-plan.lua': not found`. The same absolute evidence directory successfully accepted `client-events.tsv` through `io.open`, proving the failure is the `dofile` loading boundary rather than missing plan generation.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T15:42:00+02:00
head: 9bb6ffe2941a447eff4166cecc714992db166d93
branch: fix/e2e-scenario-plan-host-load
pr: null
status: implementing
context_routes:
  - universal-e2e
  - agent-governance
owned_paths:
  - tools/e2e/client/agent_e2e_scenario.lua
  - tests/e2e/test_agent_e2e_scenario_plan.py
  - docs/agents/tasks/active/CAN-20260717-e2e-scenario-plan-host-load.md
proven:
  - selected non-default physical scenario execution now works through merged PR 477
  - run 29582792694 reached the exact selected physical-client job
  - scenario-plan.lua was present in the uploaded evidence artifact
  - driver io.open writes to the same absolute artifact directory successfully
  - dofile on the absolute external plan path failed before login
  - maintained OTClient code supports compiling Lua source via load/loadstring
unknown:
  - whether movement succeeds after the plan host-load boundary is repaired
conflicts: []
first_failure:
  marker: scenario-plan-host-load
  evidence: physical artifact 8408520847 from run 29582792694
rejected_hypotheses:
  - missing scenario-plan generation
  - treating the failed run as movement proof
  - creating a second physical runner or workflow
  - moving scenario selection back to connector-specific workflow_dispatch
changed_paths:
  - docs/agents/tasks/active/CAN-20260717-e2e-scenario-plan-host-load.md
validation: []
blockers: []
next_action: Open a draft PR, replace only the driver plan-loading boundary with host io.open plus runtime compilation, add focused regression coverage, then run exact-head validation.
```
