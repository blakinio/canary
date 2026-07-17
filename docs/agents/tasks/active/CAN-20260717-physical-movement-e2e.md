---
task_id: CAN-20260717-physical-movement-e2e
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-E2E-MOVEMENT-001
status: active
agent: "GPT-5.5 Thinking"
branch: test/e2e-physical-movement
base_branch: main
created: 2026-07-17T08:19:00+02:00
updated: 2026-07-17T08:19:00+02:00
last_verified_commit: "c2e181f892ce2f094e887f1da5c6c7df207629c9"
risk: medium
related_issue: ""
related_pr: ""
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

- [ ] Use the existing `scenario.steps` contract and generic controlled-OTClient scenario driver.
- [ ] Use an existing disposable test account/character and evidence-backed map fixture; do not invent coordinates.
- [ ] Prove the exact first-session starting position from physical-client evidence.
- [ ] Perform bounded controlled movement through a physically proven passable route.
- [ ] Assert the exact expected post-movement position using deterministic client evidence markers.
- [ ] Preserve the canonical first safe logout, persistence wait, relog with the same character, and second safe logout sentinel.
- [ ] Keep `tools/e2e/**` and `.github/workflows/universal-agent-e2e.yml` unchanged unless a separately owned platform blocker is proven.
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
updated_at: 2026-07-17T08:19:00+02:00
head: c2e181f892ce2f094e887f1da5c6c7df207629c9
branch: test/e2e-physical-movement
pr: null
status: active
context_routes:
  - agent-governance
  - universal-e2e
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
unknown:
  - exact physical initial position for Knight 1 on the current downloaded otservbr map
  - first proven passable bounded movement direction/path from that position
  - exact expected post-movement position
conflicts: []
rejected_hypotheses:
  - create a second E2E orchestrator
  - invent map coordinates from town id or chat history
  - change shared workflow before a concrete platform blocker is proven
changed_paths:
  - docs/agents/tasks/active/CAN-20260717-physical-movement-e2e.md
validation: []
blockers: []
next_action: Open the draft PR, add the smallest exploratory movement scenario using the existing action-plan driver, run physical E2E to capture exact initial/final position evidence, then pin the proven deterministic fixture and final assertions.
```
