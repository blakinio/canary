---
task_id: CAN-20260717-e2e-initial-position-readiness
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-E2E-POSITION-READY-001
status: implementing
agent: "GPT-5.5 Thinking"
branch: fix/e2e-initial-position-readiness
base_branch: main
created: 2026-07-17T17:55:00+02:00
updated: 2026-07-17T17:55:00+02:00
last_verified_commit: "07cbcfd92ceaeb5b22edb0eee7c586f3aa6f4854"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - CAN-20260717-e2e-scenario-plan-host-load
blocks:
  - CAN-20260717-physical-movement-e2e-v2
owned_paths:
  exclusive:
    - tools/e2e/client/agent_e2e_scenario.lua
    - tests/e2e/test_agent_e2e_scenario_plan.py
    - docs/agents/tasks/active/CAN-20260717-e2e-initial-position-readiness.md
  shared: []
  read_only:
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/run_physical_e2e.sh
    - .github/workflows/universal-agent-e2e.yml
    - tests/e2e/scenarios/movement/physical-movement.json
modules_touched:
  - Universal OTS E2E physical gameplay initial-position readiness
reuses:
  - existing generic controlled-OTClient scenario driver
  - existing generated scenario-plan contract
  - existing Universal Agent E2E workflow and physical runner
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Remove the proven race between `onGameStart` and availability of `g_game.getLocalPlayer()` so a physical scenario records an evidence-backed initial position before any movement action is allowed to start.

# Acceptance criteria

- [x] Preserve the existing login/relog lifecycle and scenario-plan contract.
- [ ] First-session plan execution waits for a real local player and position instead of assuming they exist synchronously inside `onGameStart`.
- [ ] Record `initial_position` exactly once before `runNextStep()` can execute.
- [ ] Bound the readiness wait and fail closed if the local player position never becomes available.
- [ ] Keep second-session relog behavior unchanged.
- [ ] Add focused regression coverage for the readiness gate.
- [ ] Keep workflow, physical runner, resolver and movement manifest unchanged.
- [ ] Pass applicable exact-final-head Ownership, CI and Universal Agent E2E gates.
- [ ] Squash merge before retrying the blocked movement proof PR #481.

## Proven blocker

Universal Agent E2E run `29591841409` selected `movement/physical-movement` on exact head `f6d69453257eee842dc2d8b7daf53b5d162d2020`. Physical artifact `8412192393` (`sha256:73a8991bc8f073af04743889261c230e12c33c95c6305621bd12c2f812f0910f`) proves the scenario plan loaded and first login succeeded, then `/otclientrc.lua` failed in the `onGameStart` callback because `initialPosition` was nil. No movement step marker was emitted. The final client marker was `error=unexpected disconnect before safe logout in phase 1`, so this run is not movement proof.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T17:55:00+02:00
head: 07cbcfd92ceaeb5b22edb0eee7c586f3aa6f4854
branch: fix/e2e-initial-position-readiness
pr: null
status: implementing
context_routes:
  - universal-e2e
  - agent-governance
owned_paths:
  - tools/e2e/client/agent_e2e_scenario.lua
  - tests/e2e/test_agent_e2e_scenario_plan.py
  - docs/agents/tasks/active/CAN-20260717-e2e-initial-position-readiness.md
proven:
  - PR 483 merged the host-filesystem scenario-plan loader and its exact-head gates passed
  - run 29591841409 selected movement/physical-movement and loaded a four-step plan
  - first login reached login_1=success
  - no initial_position marker and no movement step marker were emitted
  - OTClient log reports attempt to index upvalue initialPosition as nil in the onGameStart callback
  - artifact 8412192393 was uploaded from exact head f6d69453257eee842dc2d8b7daf53b5d162d2020
  - open PR search found no competing initial-position readiness fix
derived:
  - g_game.getLocalPlayer() is not guaranteed to be ready synchronously at onGameStart even though login_1 has been emitted
  - the physical plan must be gated on successful position capture, otherwise movement assertions can start without a valid baseline
  - a bounded short poll in the existing driver is smaller and safer than changing the workflow, runner or scenario contract
unknown:
  - how many readiness polls are needed on a typical runner before the local player becomes available
  - whether the east movement succeeds after the readiness race is repaired
conflicts: []
first_failure:
  marker: initial-position-readiness
  evidence: artifact 8412192393 from run 29591841409
rejected_hypotheses:
  - treating run 29591841409 as movement proof
  - pinning the static east-neighbor coordinate without a successful physical run
  - changing the movement manifest to work around client lifecycle readiness
  - creating another workflow or physical runner
changed_paths:
  - docs/agents/tasks/active/CAN-20260717-e2e-initial-position-readiness.md
validation:
  - command: physical artifact inspection
    result: FAIL
    evidence: login_1 succeeded, initialPosition was nil in onGameStart, and no movement marker was emitted
blockers: []
next_action: Add a bounded local-player position readiness gate in the existing generic driver, add focused regression coverage, open a draft PR, and require exact-head validation before merging and retrying PR 481.
```
