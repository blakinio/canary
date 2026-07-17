---
task_id: CAN-20260717-physical-movement-e2e-v2
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-E2E-MOVEMENT-002
status: validating
agent: "GPT-5.5 Thinking"
branch: test/e2e-physical-movement-v2
base_branch: main
created: 2026-07-17T15:03:00+02:00
updated: 2026-07-17T20:14:00+02:00
last_verified_commit: "2212b3e2838ddf86b1a7810533788f7617e911c5"
risk: medium
related_issue: ""
related_pr: "481"
depends_on:
  - CAN-20260717-e2e-pr-scenario-selection
blocks:
  - future physical floor-change and teleport scenarios
owned_paths:
  exclusive:
    - tests/e2e/scenarios/movement/physical-movement.json
    - docs/agents/tasks/active/CAN-20260717-physical-movement-e2e-v2.md
  shared: []
  read_only:
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/run_physical_e2e.sh
    - tools/e2e/client/agent_e2e_scenario.lua
    - .github/workflows/universal-agent-e2e.yml
modules_touched:
  - Universal OTS E2E physical movement scenario
reuses:
  - merged same-repository PR scenario auto-selection from PR 477
  - merged initial-position readiness fix from PR 494
  - existing Universal Agent E2E MariaDB/Canary/controlled-OTClient lifecycle
  - existing scenario.steps action-plan contract
  - generic controlled-OTClient scenario driver
  - canonical two-session login/logout/relog persistence sentinel
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Prove one bounded physical east movement with the existing Universal Agent E2E stack, pin the exact post-movement position only from real controlled-OTClient artifact evidence, and merge the deterministic scenario without changing shared E2E infrastructure.

# Acceptance criteria

- [x] Reuse the evidence-backed initial position `32369,32241,7`; do not invent coordinates.
- [x] Reuse the existing single-step east movement discovery probe without changing shared E2E infrastructure.
- [x] Universal Agent E2E automatically selects `movement/physical-movement` on this PR.
- [x] A real controlled OTClient run proves bounded movement and emits the exact `step_position-changed_detail` value.
- [x] Pin only the physically proven exact post-movement position in the scenario assertions.
- [x] Preserve canonical safe logout, persistence wait, relog and second safe logout.
- [ ] Synchronize with current `main`, audit changed paths/reviews, apply `ci:final-gate` before the final checkpoint commit, and require exact-final-head Ownership, CI and selected physical E2E success.
- [ ] Squash merge only after all exact-final-head gates are green.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T20:14:00+02:00
head: 2212b3e2838ddf86b1a7810533788f7617e911c5
branch: test/e2e-physical-movement-v2
pr: 481
status: validating
context_routes:
  - universal-e2e
  - agent-governance
owned_paths:
  - tests/e2e/scenarios/movement/physical-movement.json
  - docs/agents/tasks/active/CAN-20260717-physical-movement-e2e-v2.md
proven:
  - PR 477 is merged and deterministically selects one changed existing scenario manifest on same-repository PRs
  - PR 494 is merged and gates first-session plan execution on a real local-player position before recording initial_position and starting the plan
  - PR 481 discovery head 2212b3e2838ddf86b1a7810533788f7617e911c5 changes only this task record and the movement scenario relative to main
  - Universal Agent E2E run 29601141589 selected the exact job Physical client / movement/physical-movement on discovery head 2212b3e2838ddf86b1a7810533788f7617e911c5
  - physical artifact 8415740677 has digest sha256:2fa6c83d16b114c2ecf8a451a29d092eca0154f1bbdc192fa7c76486a5152212
  - client-events.tsv records initial_position=32369,32241,7 before the movement plan
  - client-events.tsv records step_east-one=success and step_position-changed=success
  - client-events.tsv records exact physical post-movement position step_position-changed_detail=32370,32241,7
  - the same physical artifact records plan=success, logout_request_1=safe, server_persistence_1=confirmed, login_2=success, logout_request_2=safe and e2e=success
  - static OTBM evidence identified 32370,32241,7 only as a candidate; the exact final-position assertion is now authorized by physical artifact 8415740677 rather than static map data
unknown:
  - post-assertion exact-head Ownership, CI and selected physical E2E conclusions
  - whether current main advances again before final-gate preparation
conflicts: []
first_failure:
  marker: active-task-checkpoint-schema
  evidence: Agent Task Ownership run 29601141261 artifact 8415041033 reports first_failure must be a YAML mapping on discovery head 2212b3e2838ddf86b1a7810533788f7617e911c5
rejected_hypotheses:
  - treating static OTBM evidence as movement proof
  - treating the earlier run 29591841409 as movement proof
  - altering the canonical login/relog scenario
  - creating a second workflow or physical runner
  - inventing the final position before artifact evidence
changed_paths:
  - docs/agents/tasks/active/CAN-20260717-physical-movement-e2e-v2.md
  - tests/e2e/scenarios/movement/physical-movement.json
validation:
  - command: Universal Agent E2E run 29601141589
    result: PASS
    evidence: exact discovery head 2212b3e2838ddf86b1a7810533788f7617e911c5 selected Physical client / movement/physical-movement and completed the physical scenario successfully
  - command: physical artifact 8415740677 client-events.tsv inspection
    result: PASS
    evidence: initial 32369,32241,7; one east step; exact changed position 32370,32241,7; canonical persistence/relog lifecycle ends e2e=success
  - command: Agent Task Ownership run 29601141261
    result: FAIL
    evidence: artifact 8415041033 identified the now-corrected first_failure checkpoint schema violation
blockers: []
next_action: Validate the post-evidence head, synchronize with current main if needed, then audit scope/reviews and prepare the repository final gate without changing the physically proven assertion.
```
