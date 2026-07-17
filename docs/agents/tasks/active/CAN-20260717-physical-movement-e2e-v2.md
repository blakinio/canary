---
task_id: CAN-20260717-physical-movement-e2e-v2
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-E2E-MOVEMENT-002
status: implementing
agent: "GPT-5.5 Thinking"
branch: test/e2e-physical-movement-v2
base_branch: main
created: 2026-07-17T15:03:00+02:00
updated: 2026-07-17T15:07:00+02:00
last_verified_commit: "034cc170640a660735b9bb1f03e86f9eae4af3e8"
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
  - existing Universal Agent E2E MariaDB/Canary/controlled-OTClient lifecycle
  - existing scenario.steps action-plan contract
  - generic controlled-OTClient scenario driver
  - canonical two-session login/logout/relog persistence sentinel
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Retry the bounded physical movement scenario now that merged PR #477 can automatically select exactly one changed scenario manifest on a same-repository PR, and obtain real controlled-OTClient movement evidence before merging any exact final-position assertion.

# Acceptance criteria

- [x] Reuse the evidence-backed initial position `32369,32241,7`; do not invent coordinates.
- [x] Reuse the existing single-step east movement discovery probe without changing shared E2E infrastructure.
- [ ] Universal Agent E2E automatically selects `movement/physical-movement` on this PR.
- [ ] A real controlled OTClient run proves bounded movement and emits the exact `step_position-changed_detail` value.
- [ ] Pin only the physically proven exact post-movement position in the scenario assertions.
- [ ] Preserve canonical safe logout, persistence wait, relog and second safe logout.
- [ ] Synchronize with current `main`, audit changed paths/reviews, apply `ci:final-gate` before the final checkpoint commit, and require exact-final-head Ownership, CI and selected physical E2E success.
- [ ] Squash merge only after all exact-final-head gates are green.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T15:07:00+02:00
head: 034cc170640a660735b9bb1f03e86f9eae4af3e8
branch: test/e2e-physical-movement-v2
pr: 481
status: implementing
context_routes:
  - universal-e2e
  - agent-governance
owned_paths:
  - tests/e2e/scenarios/movement/physical-movement.json
  - docs/agents/tasks/active/CAN-20260717-physical-movement-e2e-v2.md
proven:
  - original PR 457 was closed without merge because selected workflow dispatch was unavailable at that time
  - archived task CAN-20260717-physical-movement-e2e explicitly permits a future retry when an authorized selected-run surface exists
  - PR 477 is merged and adds deterministic same-repository PR selection when exactly one existing scenario manifest is changed
  - PR 481 changes exactly one scenario manifest plus this task record
  - physical packet evidence from the prior task proves first-session start at 32369,32241,7
  - exact-map static evidence identifies east neighbor 32370,32241,7 only as a candidate, not movement proof
unknown:
  - exact post-movement position emitted by the real controlled client
conflicts: []
first_failure: null
rejected_hypotheses:
  - treating static OTBM evidence as movement proof
  - altering the canonical login/relog scenario
  - creating a second workflow or physical runner
  - inventing the final position before artifact evidence
changed_paths:
  - docs/agents/tasks/active/CAN-20260717-physical-movement-e2e-v2.md
  - tests/e2e/scenarios/movement/physical-movement.json
validation: []
blockers: []
next_action: Let the PR synchronize event run movement/physical-movement through the merged selector; inspect only the resulting physical artifact before pinning the final position.
```
