---
task_id: CAN-20260717-physical-movement-e2e-v2
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-E2E-MOVEMENT-002
status: completed
agent: "GPT-5.5 Thinking"
branch: test/e2e-physical-movement-v2
base_branch: main
created: 2026-07-17T15:03:00+02:00
updated: 2026-07-17T19:47:09Z
last_verified_commit: "bbf5aaace311e59e3b46e3dbd0707de87bd6e9f4"
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
completed: 2026-07-17T19:47:09Z
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
updated_at: 2026-07-17T21:12:29+02:00
head: 95a5c67296d479a22274bf5f4b588071ecbacacb
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
  - Universal Agent E2E discovery run 29601141589 selected Physical client / movement/physical-movement on head 2212b3e2838ddf86b1a7810533788f7617e911c5
  - physical artifact 8415740677 has digest sha256:2fa6c83d16b114c2ecf8a451a29d092eca0154f1bbdc192fa7c76486a5152212
  - client-events.tsv records initial_position=32369,32241,7, step_east-one=success, step_position-changed=success and exact step_position-changed_detail=32370,32241,7
  - the same physical artifact records plan=success, logout_request_1=safe, server_persistence_1=confirmed, login_2=success, logout_request_2=safe and e2e=success
  - static OTBM evidence identified 32370,32241,7 only as a candidate; the exact assertion is authorized by real physical-client evidence
  - the scenario pins step_position-changed_detail=32370,32241,7 and preserves the canonical persistence/relog sentinel
  - prior exact-final head dfacf2792b8461f6c8b5d15430acffe2f755fda6 passed Agent Task Ownership run 29603582504, CI run 29603582664 and Universal Agent E2E run 29603582750
  - exact-final physical artifact 8416670164 on dfacf2792b8461f6c8b5d15430acffe2f755fda6 independently records initial_position=32369,32241,7, step_position-changed_detail=32370,32241,7 and e2e=success
  - Required physical E2E in run 29603582750 passed on dfacf2792b8461f6c8b5d15430acffe2f755fda6
  - ready_for_review triggered CI run 29605554215 and autofix.ci run 29605554033 on the same head; both completed successfully
  - main advanced during final validation to f864a9e4d928e2bccfa7a13141362a044e069b27, so merge was correctly withheld
  - PR 481 was synchronized again without force-push by merge commit 95a5c67296d479a22274bf5f4b588071ecbacacb using current main plus only the movement task and movement scenario
  - after resync PR 481 is mergeable against main f864a9e4d928e2bccfa7a13141362a044e069b27
  - post-resync changed-path audit contains exactly the movement task and movement scenario
  - post-resync review audit found zero review threads and zero submitted reviews
  - ci:final-gate was applied again after the resync and before this final checkpoint commit
derived:
  - the bounded one-step east movement is physically proven for the deterministic fixture because a real controlled OTClient changed position from 32369,32241,7 to 32370,32241,7 after exactly one east walk step
  - the exact final-position assertion remains evidence-backed after the main resync because the movement scenario blob is preserved unchanged from the physically validated head
  - the canonical logout persistence relog sentinel remains intact because both discovery and exact-final physical artifacts end with successful persistence relog second safe logout and e2e=success
  - the main advance was a synchronization condition rather than a movement or runtime failure; no feature change was required
unknown:
  - exact-final-head Agent Task Ownership conclusion after this resync checkpoint
  - exact-final-head CI conclusion after this resync checkpoint
  - exact-final-head Universal Agent E2E and Required physical E2E conclusions after this resync checkpoint
  - whether main advances again before squash merge
conflicts: []
first_failure:
  marker: none
  evidence: no unresolved runtime or validation failure; the only post-validation blocker was main advancing, resolved by non-force synchronization to f864a9e4d928e2bccfa7a13141362a044e069b27
rejected_hypotheses:
  - treating static OTBM evidence as movement proof
  - treating run 29591841409 as movement proof
  - altering the canonical login/relog scenario
  - creating a second workflow or physical runner
  - inventing the final position before artifact evidence
  - forcing merge while PR 481 was behind current main
changed_paths:
  - docs/agents/tasks/active/CAN-20260717-physical-movement-e2e-v2.md
  - tests/e2e/scenarios/movement/physical-movement.json
validation:
  - command: Universal Agent E2E run 29601141589
    result: PASS
    evidence: discovery head selected Physical client / movement/physical-movement and real client artifact proved one east step to 32370,32241,7
  - command: physical artifact 8415740677 client-events.tsv inspection
    result: PASS
    evidence: initial 32369,32241,7; one east step; exact changed position 32370,32241,7; canonical persistence/relog lifecycle ends e2e=success
  - command: Universal Agent E2E run 29603582750
    result: PASS
    evidence: prior exact-final head dfacf2792b8461f6c8b5d15430acffe2f755fda6 passed Physical client / movement/physical-movement and Required physical E2E
  - command: exact-final physical artifact 8416670164 client-events.tsv inspection
    result: PASS
    evidence: exact-final head again recorded start 32369,32241,7, post-step 32370,32241,7 and e2e=success
  - command: ready_for_review CI run 29605554215
    result: PASS
    evidence: full ready-triggered final-gate CI passed including Windows, macOS, Linux release/debug and Docker jobs
  - command: post-resync PR 481 scope audit
    result: PASS
    evidence: exactly docs/agents/tasks/active/CAN-20260717-physical-movement-e2e-v2.md and tests/e2e/scenarios/movement/physical-movement.json
  - command: post-resync PR 481 review audit
    result: PASS
    evidence: zero review threads and zero submitted reviews
  - command: post-resync ci:final-gate application
    result: PASS
    evidence: label applied after synchronization with main f864a9e4d928e2bccfa7a13141362a044e069b27 and before this checkpoint commit
blockers: []
next_action: Require exact-final-head Agent Task Ownership, CI, Physical client / movement/physical-movement and Required physical E2E success on this new final checkpoint head; if current main remains unchanged, squash merge PR 481 with expected_head_sha and then complete lifecycle archive.
```

## Automated lifecycle completion

- Feature PR: #481.
- Feature head: `43dfb22b2546a06eca6ebfc48e0fe66491369d46`.
- Merge commit: `bbf5aaace311e59e3b46e3dbd0707de87bd6e9f4`.
- Merged at: `2026-07-17T19:47:09Z`.
- This record was moved from `tasks/active` by the post-merge lifecycle automation.
