---
task_id: CAN-20260717-physical-movement-e2e-v2
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-E2E-MOVEMENT-002
status: review
agent: "GPT-5.5 Thinking"
branch: test/e2e-physical-movement-v2
base_branch: main
created: 2026-07-17T15:03:00+02:00
updated: 2026-07-17T20:22:02+02:00
last_verified_commit: "bb77e327ceeedfe5556d10da857f18296663b3e8"
risk: medium
related_issue: ""
related_pr: "481"
depends_on:
  - CAN-20260717-e2e-pr-scenario-selection
  - CAN-20260717-e2e-initial-position-readiness
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
updated_at: 2026-07-17T20:22:02+02:00
head: bb77e327ceeedfe5556d10da857f18296663b3e8
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
  - Universal Agent E2E run 29601141589 selected the exact job Physical client / movement/physical-movement on discovery head 2212b3e2838ddf86b1a7810533788f7617e911c5
  - physical artifact 8415740677 has digest sha256:2fa6c83d16b114c2ecf8a451a29d092eca0154f1bbdc192fa7c76486a5152212
  - client-events.tsv records initial_position=32369,32241,7 before the movement plan
  - client-events.tsv records step_east-one=success and step_position-changed=success
  - client-events.tsv records exact physical post-movement position step_position-changed_detail=32370,32241,7
  - the same physical artifact records plan=success, logout_request_1=safe, server_persistence_1=confirmed, login_2=success, logout_request_2=safe and e2e=success
  - static OTBM evidence identified 32370,32241,7 only as a candidate; the exact final-position assertion is authorized by physical artifact 8415740677 rather than static map data
  - the scenario assertion pins step_position-changed_detail=32370,32241,7
  - pre-final head bb77e327ceeedfe5556d10da857f18296663b3e8 passed Agent Task Ownership run 29603399552 and CI run 29603399751
  - final pre-gate scope audit found exactly the movement scenario and this task record as changed paths
  - final pre-gate review audit found zero review threads and zero submitted reviews requiring action
  - PR 481 remained based on main commit 250640758bec48946f31f34c85995632d194fbd0 and mergeable before final checkpoint creation
  - ci:final-gate was applied to PR 481 before this final checkpoint commit
derived:
  - because the physical artifact records the initial position before any plan step and then records one successful east walk followed by exact changed position 32370,32241,7, the scenario may safely require that exact post-movement marker for this deterministic fixture
  - the successful second login and final e2e marker prove the movement assertion did not replace or bypass the canonical logout persistence and relog sentinel
  - checkpoint schema blockers discovered by Ownership were corrected before final-gate preparation and the corrected pre-final head passed Ownership
  - no shared E2E workflow runner resolver or client-driver changes are required for this movement scenario
unknown:
  - exact-final-head Agent Task Ownership conclusion
  - exact-final-head CI conclusion
  - exact-final-head Universal Agent E2E conclusion and selected physical job conclusion
  - whether ready_for_review triggers a fresh required check on the same exact final head
conflicts: []
first_failure:
  marker: none
  evidence: no unresolved pre-final failure; Agent Task Ownership run 29603399552 and CI run 29603399751 passed on bb77e327ceeedfe5556d10da857f18296663b3e8
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
  - command: Agent Task Ownership run 29603399552
    result: PASS
    evidence: corrected pre-final checkpoint head bb77e327ceeedfe5556d10da857f18296663b3e8 passed active-task ownership validation
  - command: CI run 29603399751
    result: PASS
    evidence: corrected pre-final checkpoint head bb77e327ceeedfe5556d10da857f18296663b3e8 passed repository CI
  - command: PR 481 changed-path audit
    result: PASS
    evidence: exactly docs/agents/tasks/active/CAN-20260717-physical-movement-e2e-v2.md and tests/e2e/scenarios/movement/physical-movement.json
  - command: PR 481 review-thread audit
    result: PASS
    evidence: zero review threads and zero submitted reviews requiring action before final checkpoint creation
  - command: ci:final-gate application
    result: PASS
    evidence: label applied to PR 481 before this final checkpoint commit
blockers: []
next_action: Require exact-final-head Agent Task Ownership CI and Physical client / movement/physical-movement success; then mark PR ready, accept any fresh required ready_for_review check on the same head, and squash merge with expected_head_sha before lifecycle archive.
```
