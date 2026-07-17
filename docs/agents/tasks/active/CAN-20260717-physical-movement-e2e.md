---
task_id: CAN-20260717-physical-movement-e2e
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-E2E-MOVEMENT-001
status: implementing
agent: "GPT-5.5 Thinking"
branch: test/e2e-physical-movement
base_branch: main
created: 2026-07-17T08:19:00+02:00
updated: 2026-07-17T09:47:00+02:00
last_verified_commit: "1a9f5fac264c16bfc4e6ce03a9991560d9a80273"
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
- [ ] Pass the selected physical movement scenario plus applicable exact-final-head gates.
- [x] Synchronize the task branch with current `main` and keep the changed-file list bounded to the task record and movement scenario.
- [ ] Merge only after the exact-final-head gate is green.

# Ownership and overlap audit

- Task branch is synchronized through merge commit `1a9f5fac264c16bfc4e6ce03a9991560d9a80273` with current `main` `be9760a88d0c714dfd3e1b6a659e373380d03d65`.
- Current diff against `main` contains only `tests/e2e/scenarios/movement/physical-movement.json` and this task record.
- Open PR #462 owns Security Validation workflow/tools/tests and does not touch physical-client E2E or the movement scenario path.
- Open PR #453 remains documentation-only and does not own the movement scenario path.
- No unresolved path ownership overlap is known for this task.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T09:47:00+02:00
head: 1a9f5fac264c16bfc4e6ce03a9991560d9a80273
branch: test/e2e-physical-movement
pr: 457
status: investigating
context_routes:
  - agent-governance
  - universal-e2e
owned_paths:
  - tests/e2e/scenarios/movement/physical-movement.json
  - docs/agents/tasks/active/CAN-20260717-physical-movement-e2e.md
proven:
  - PR 446 action-plan platform and PR 454 lifecycle archive are merged on main
  - draft PR 457 targets blakinio/canary main from the blakinio/canary task branch
  - shared tools/e2e, canonical login/relog scenario and universal-agent-e2e workflow remain unchanged
  - scenario uses only existing bounded observe_online, walk, wait and observe_position_changed actions
  - exact map SHA-256 is a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2
  - physical packet evidence proves Knight 1 first-session start at 32369,32241,7 and the movement scenario pins initial_position=32369,32241,7
  - matching OTBM town evidence independently records town id 8 Thais at 32369,32241,7
  - read-only bounded OTBM scan of the exact-hash map shows start 32369,32241,7 and all four cardinal neighbors as existing PZ tiles with no child items
  - east candidate 32370,32241,7 contains only inline ground item 409 and no child items; start contains inline ground item 410
  - latest physical client screenshot from the canonical sentinel shows open floor around Knight 1, consistent with the bounded map scan
  - Universal Agent E2E 144 passed the canonical login/relog sentinel before main synchronization and retained the same exact map hash
  - branch was synchronized with current main be9760a88d0c714dfd3e1b6a659e373380d03d65 without force rewriting history
  - post-sync Agent Task Ownership 1916 passed on 1a9f5fac264c16bfc4e6ce03a9991560d9a80273
  - post-sync CI 3056 passed on the same head
  - post-sync Universal Agent E2E 145 passed the canonical login/relog sentinel on the same PR state
  - current diff against main contains exactly the task record and movement scenario
  - open PR 462 is confined to Security Validation paths and does not overlap this task
  - the available GitHub connector and installed plugin surface expose no workflow_dispatch mutation

derived:
  - east is the strongest current deterministic movement candidate because the exact map records a simple neighboring PZ tile with no child items and the physical screenshot is visually consistent with open floor
  - this static and visual evidence is fixture-selection evidence only and cannot prove that the real controlled client successfully moves east
  - lack of a workflow_dispatch connector is an execution-surface limitation, not a reason to change the canonical E2E workflow or create another runner
unknown:
  - whether the controlled OTClient successfully moves east from 32369,32241,7 in the selected movement scenario
  - exact physical post-movement position emitted as step_position-changed_detail
conflicts: []
first_failure:
  marker: selected-movement-workflow-dispatch-unavailable
  evidence: the repository already exposes the required workflow_dispatch inputs, but the available authenticated GitHub connector has no dispatch operation and no installed alternative dispatch plugin exists
rejected_hypotheses:
  - create a second E2E orchestrator or workflow
  - modify the canonical login/relog scenario to force movement through pull_request CI
  - modify the shared workflow solely to work around this session's connector limitation
  - treat a successful canonical login/relog run as movement coverage
  - infer physical movement success or the exact final position from static OTBM data or a screenshot
  - force rewrite the published task branch; AGENTS requires force-with-lease and the connector does not expose it
changed_paths:
  - docs/agents/tasks/active/CAN-20260717-physical-movement-e2e.md
  - tests/e2e/scenarios/movement/physical-movement.json
validation:
  - command: Agent Task Ownership run 29564064826 / number 1916
    result: PASS
    evidence: ownership validation passed on synchronized head 1a9f5fac264c16bfc4e6ce03a9991560d9a80273
  - command: CI run 29564064993 / number 3056
    result: PASS
    evidence: repository CI passed on synchronized head 1a9f5fac264c16bfc4e6ce03a9991560d9a80273
  - command: Universal Agent E2E run 29564065031 / number 145
    result: PASS
    evidence: canonical login/relog sentinel passed after main synchronization; movement/physical-movement was not selected
blockers:
  - a selected Universal Agent E2E workflow_dispatch run for movement/physical-movement cannot be initiated from the currently available authenticated connector surface
next_action: Obtain the existing selected movement/physical-movement workflow_dispatch run on the current task branch through an authorized dispatch-capable surface; use only that physical artifact to prove east-route movement and pin step_position-changed_detail, then apply ci:final-gate before the final checkpoint commit and make no post-green feature commit.
```
