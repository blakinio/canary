---
task_id: CAN-20260717-e2e-initial-position-readiness
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-E2E-POSITION-READY-001
status: ready
agent: "GPT-5.5 Thinking"
branch: fix/e2e-initial-position-readiness
base_branch: main
created: 2026-07-17T17:55:00+02:00
updated: 2026-07-17T18:28:00+02:00
last_verified_commit: "855fbb7734ecb8cdd311bf55de89af20a8de77c5"
risk: medium
related_issue: ""
related_pr: "494"
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
- [x] First-session plan execution waits for a real local player and position instead of assuming they exist synchronously inside `onGameStart`.
- [x] Record `initial_position` exactly once before `runNextStep()` can execute.
- [x] Bound the readiness wait and fail closed if the local player position never becomes available.
- [x] Keep second-session relog behavior unchanged.
- [x] Add focused regression coverage for the readiness gate.
- [x] Keep workflow, physical runner, resolver and movement manifest unchanged.
- [ ] Pass applicable exact-final-head Ownership, CI and Universal Agent E2E gates.
- [ ] Squash merge before retrying the blocked movement proof PR #481.

## Proven blocker

Universal Agent E2E run `29591841409` selected `movement/physical-movement` on exact head `f6d69453257eee842dc2d8b7daf53b5d162d2020`. Physical artifact `8412192393` (`sha256:73a8991bc8f073af04743889261c230e12c33c95c6305621bd12c2f812f0910f`) proves the scenario plan loaded and first login succeeded, then `/otclientrc.lua` failed in the `onGameStart` callback because `initialPosition` was nil. No movement step marker was emitted. The final client marker was `error=unexpected disconnect before safe logout in phase 1`, so this run is not movement proof.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T18:28:00+02:00
head: 855fbb7734ecb8cdd311bf55de89af20a8de77c5
branch: fix/e2e-initial-position-readiness
pr: 494
status: ready
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
  - PR 494 changes only the generic client driver, its focused regression test and this task record
  - first-session onGameStart now enters waitForInitialPositionAndStartPlan instead of dereferencing the local player synchronously
  - readiness polls at 100 ms for at most 50 checks, copies the proven position into an immutable baseline, records initial_position, then schedules the existing plan
  - readiness failure is explicit and fail-closed after the bounded wait
  - second-session safe-logout timing remains on the existing SESSION_HOLD_MS path
  - Agent Task Ownership run 29594347991 passed on 855fbb7734ecb8cdd311bf55de89af20a8de77c5
  - CI run 29594348318 passed on the same head, including the focused readiness regression
  - Universal Agent E2E run 29594348275 passed on the same head and preserved canonical physical login/logout/relog behavior through the new readiness gate
  - branch is zero commits behind current main and changes exactly three expected files
  - no submitted reviews or unresolved review threads exist
  - ci:final-gate was applied before this final checkpoint commit
derived:
  - g_game.getLocalPlayer() is not guaranteed to be ready synchronously at onGameStart even though login_1 has been emitted
  - the physical plan must be gated on successful position capture, otherwise movement assertions can start without a valid baseline
  - a bounded short poll in the existing driver is smaller and safer than changing the workflow, runner or scenario contract
  - copying x/y/z into a standalone baseline prevents the initial position reference from changing if the live player position object mutates during movement
  - canonical E2E success proves the readiness gate does not regress the required two-session persistence sentinel
unknown:
  - exact-final-head Ownership, CI and Universal Agent E2E conclusions after this final checkpoint commit
  - exact number of readiness polls observed before the local player became available in the canonical run
  - whether the east movement succeeds after PR 494 merges and PR 481 is retried
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
  - tests/e2e/test_agent_e2e_scenario_plan.py
  - tools/e2e/client/agent_e2e_scenario.lua
validation:
  - command: physical artifact inspection
    result: FAIL
    evidence: login_1 succeeded, initialPosition was nil in onGameStart, and no movement marker was emitted
  - command: implementation scope audit
    result: PASS
    evidence: workflow, physical runner, resolver and movement scenario are unchanged
  - command: Agent Task Ownership run 29594347991
    result: PASS
    evidence: ownership and checkpoint validation passed on pre-final head 855fbb7734ecb8cdd311bf55de89af20a8de77c5
  - command: CI run 29594348318
    result: PASS
    evidence: repository CI and focused regression passed on the same pre-final head
  - command: Universal Agent E2E run 29594348275
    result: PASS
    evidence: canonical physical login/logout/relog passed on the same pre-final head
  - command: base, scope and review audit
    result: PASS
    evidence: zero commits behind main, exactly three expected files, no reviews and no unresolved review threads
  - command: final-gate preparation
    result: PASS
    evidence: ci:final-gate applied before this checkpoint commit
blockers: []
next_action: Make no further feature-branch changes. Require exact-final-head Ownership, CI and Universal Agent E2E success, then mark ready and squash merge PR 494; after lifecycle cleanup, synchronize PR 481 with the new main and rerun movement/physical-movement for artifact-backed position proof.
```
