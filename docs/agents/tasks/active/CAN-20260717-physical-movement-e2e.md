---
task_id: CAN-20260717-physical-movement-e2e
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-E2E-MOVEMENT-001
status: implementing
agent: "GPT-5.5 Thinking"
branch: test/e2e-physical-movement
base_branch: main
created: 2026-07-17T08:19:00+02:00
updated: 2026-07-17T09:05:35+02:00
last_verified_commit: "4b959674a4d70a6a51d5f3b67ed595028d4d185e"
risk: medium
related_issue: ""
related_pr: "457"
depends_on:
  - CAN-20260716-universal-e2e-gameplay-capabilities-v2
blocks:
  - future physical floor-change and teleport scenarios
owned_paths:
  exclusive:
    - tests/e2e/scenarios/movement/physical-movement.json
    - docs/agents/tasks/active/CAN-20260717-physical-movement-e2e.md
  shared:
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/run_physical_e2e.sh
    - tools/e2e/client/agent_e2e_scenario.lua
    - .github/workflows/universal-agent-e2e.yml
    - tests/e2e/scenarios/login/scenario.json
    - docker/data/02-test_account_players.sql
modules_touched:
  - Universal OTS E2E physical movement scenario
reuses:
  - existing Universal Agent E2E MariaDB/Canary/controlled-OTClient lifecycle
  - merged optional scenario.steps action-plan contract from PR #446
  - generic tools/e2e/client/agent_e2e_scenario.lua driver
  - canonical two-session login/logout/relog persistence sentinel
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Add the first deterministic physical movement scenario on top of the merged Universal OTS E2E action-plan platform without changing or duplicating the shared E2E lifecycle.

# Acceptance criteria

- [x] Use the existing `scenario.steps` contract and generic controlled-OTClient scenario driver.
- [x] Use an existing disposable test account/character and evidence-backed map fixture; do not invent coordinates.
- [x] Prove the exact first-session starting position from physical-client evidence.
- [ ] Perform bounded controlled movement through a physically proven passable route.
- [ ] Assert the exact expected post-movement position using deterministic client evidence markers.
- [x] Preserve the canonical first safe logout, persistence wait, relog with the same character, and second safe logout sentinel in the scenario contract.
- [x] Keep `tools/e2e/**` and `.github/workflows/universal-agent-e2e.yml` unchanged unless a separately owned platform blocker is proven.
- [ ] Pass focused scenario validation and applicable exact-head Universal Agent E2E/CI gates.
- [ ] Audit the final changed-file list and merge only after the exact-final-head gate is green.

# Ownership and overlap audit

- Current task base is `blakinio/canary:main` at `c2e181f892ce2f094e887f1da5c6c7df207629c9`.
- Open PR #451 owns only Security Validation paths and explicitly excludes physical-client E2E paths.
- Open PR #453 is documentation-only for MyAAC/login-stack security findings.
- Open PR #455 changes `.github/e2e-controlled-server.env` plus OAM-007 documentation/task state and does not own `tools/e2e/**`, `tests/e2e/**`, or `.github/workflows/universal-agent-e2e.yml`.
- No overlapping open PR ownership was found for `tests/e2e/scenarios/movement/physical-movement.json`.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T09:05:35+02:00
head: 4b959674a4d70a6a51d5f3b67ed595028d4d185e
branch: test/e2e-physical-movement
pr: 457
status: investigating
context_routes:
  - agent-governance
  - universal-e2e
  - ci-repair
owned_paths:
  - tests/e2e/scenarios/movement/physical-movement.json
  - docs/agents/tasks/active/CAN-20260717-physical-movement-e2e.md
  - docs/agents/CHANGELOG.md
proven:
  - PR 446 action-plan platform and PR 454 lifecycle archive are merged on main
  - current open PRs 451, 453 and 455 do not own the movement scenario path
  - base player fixture leaves posx posy posz at schema defaults, so exact movement coordinates are not proven by docker fixture SQL alone
  - generic gameplay driver emits initial_position and exact post-movement position details
  - required_markers can assert exact event key/value pairs without changing the shared runner
  - canonical login/relog scenario remains available and unchanged
  - draft PR 457 targets blakinio/canary main from blakinio/canary branch test/e2e-physical-movement
  - exploratory scenario uses only the existing bounded actions observe_online walk wait and observe_position_changed
  - shared tools/e2e and universal-agent-e2e workflow are unchanged
  - Agent Task Ownership run 29560247366 / number 1870 passed on head b4b26f91a7778c1478420079e8b7fa42576cd4cd
  - CI run 29560247452 / number 3011 passed on the same head
  - Universal Agent E2E run 29560247505 / number 142 passed the canonical pull-request login/relog sentinel on the same PR state; it did not execute movement/physical-movement
  - run 142 retained the canonical otservbr map SHA-256 a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2, matching the supplied map snapshot and earlier successful physical E2E evidence
  - run 142 session-1 packet evidence contains server map-description opcode 0x64 immediately followed by little-endian position bytes 71 7e f1 7d 07, proving first-session position 32369,32241,7 for Knight 1
  - the matching map snapshot town table records town id 8 Thais with temple position 32369,32241,7, independently agreeing with the physical packet evidence
  - scenario required_markers now pins initial_position=32369,32241,7 from that evidence
  - PR pull_request Universal Agent E2E resolves login/relog by default; selecting movement/physical-movement requires the existing workflow_dispatch inputs rather than changing the shared workflow
  - the available GitHub connector exposes no workflow-dispatch mutation

derived:
  - the exact initial-position assertion is now evidence-backed without inventing coordinates or changing the generic action-plan contract
  - the exploratory east step remains fixture-discovery input until a selected physical movement run proves that route and emits the resulting position
  - lack of a connector workflow-dispatch action is an execution-environment limitation, not evidence that the repository needs a second runner or workflow change
unknown:
  - whether the exploratory single east step is passable from 32369,32241,7
  - exact expected post-movement position
  - whether a selected movement workflow_dispatch run can be triggered through another already-authorized execution surface in this session
conflicts: []
first_failure:
  marker: agent-task-ownership-checkpoint-schema
  evidence: Agent Task Ownership run 29559754880 / number 1858 rejected the changed checkpoint because derived and first_failure were missing and checkpoint status active was unsupported
rejected_hypotheses:
  - create a second E2E orchestrator
  - invent map coordinates from town id or chat history
  - change shared workflow before a concrete platform blocker is proven
  - treat the successful pull-request login/relog run as movement coverage
  - infer the east-step result from static coordinates without selected physical-client evidence
changed_paths:
  - docs/agents/tasks/active/CAN-20260717-physical-movement-e2e.md
  - tests/e2e/scenarios/movement/physical-movement.json
validation:
  - command: Agent Task Ownership run 29560247366 / number 1870
    result: PASS
    evidence: ownership validation passed on head b4b26f91a7778c1478420079e8b7fa42576cd4cd
  - command: CI run 29560247452 / number 3011
    result: PASS
    evidence: repository CI passed on head b4b26f91a7778c1478420079e8b7fa42576cd4cd
  - command: Universal Agent E2E run 29560247505 / number 142
    result: PASS
    evidence: canonical login/relog sentinel passed and retained packet/map evidence proving initial position 32369,32241,7; movement scenario was not selected
blockers: []
next_action: Let validation finish for the pinned-start commit, then obtain a selected movement/physical-movement run through the existing workflow_dispatch surface; use only that selected physical artifact to prove route passability and pin the exact post-movement position before final-gate work.
```
