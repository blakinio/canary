---
task_id: CAN-20260723-e2e-qri-002-canary-restart-recovery
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-QRI-002-CANARY-RESTART-RECOVERY
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/e2e-qri-002-canary-restart-recovery
base_branch: main
created: 2026-07-23
updated: 2026-07-23
last_verified_commit: "489607174f22b8b36663fe2251cdba0423388fbd"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - stable Universal Physical E2E single-Canary lifecycle
  - E2E-GAMEPLAY-007 controlled disconnect/recovery evidence pattern
  - typed player_balance persistence assertion
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260723-e2e-qri-002-canary-restart-recovery.md
    - tests/e2e/scenarios/recovery/canary-restart-recovery.json
    - tests/e2e/test_canary_restart_recovery.py
  shared:
    - tools/e2e/run_physical_e2e.sh
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/client/agent_e2e_scenario.lua
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - .github/workflows/universal-agent-e2e.yml
    - tests/e2e/scenarios/multiclient/**
    - tests/e2e/scenarios/journeys/**
modules_touched:
  - Universal E2E disposable Canary restart/recovery
reuses:
  - existing disposable Canary/MariaDB/controlled-OTClient lifecycle
  - existing generic gameplay plan driver
  - existing typed player_balance persistence contract
  - existing result.json evidence evaluation
public_interfaces:
  - canary-universal-e2e-disposable-canary-restart-recovery-v1
cross_repo_tasks: []
---

# CAN-20260723 — E2E-QRI-002 Canary restart, reconnect and recovery

## Goal

Prove one deterministic real restart of the same disposable Canary process slot inside the canonical Universal Physical E2E lifecycle, followed by expected client disconnect classification, server readiness, real relog, durable-state verification and clean teardown.

## Acceptance criteria

- [ ] Reuse exactly one existing disposable Canary/MariaDB/controlled-OTClient lifecycle and the same pinned Canary binary/configuration.
- [ ] Add only a fixed-purpose `restart_disposable_canary`-equivalent seam with no caller-selected command, PID, host or external target.
- [ ] Prove the old Canary process terminated before the replacement process starts and record old/new PID evidence.
- [ ] Distinguish pre-restart gameplay, restart request, process termination, server startup, readiness, reconnect, relog, persistence assertion and cleanup phases.
- [ ] Execute one already-proven deterministic durable mutation and verify its typed persistent state before restart and after physical relog.
- [ ] Prove no stale/ghost player session prevents re-entry and final `players_online` cleanup is zero.
- [ ] Add focused restart-seam tests, including negative rejection of arbitrary command/PID/host recovery fields.
- [ ] Validate scenario/schema contract and exact changed-file ownership.
- [ ] Pass physical Canary restart E2E, reconnect/relogin, persistence assertion, cleanup and repository CI.
- [ ] Apply `ci:final-gate` before the final checkpoint commit; make no post-green commit; audit reviews and exact final head; squash-merge; archive lifecycle.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T16:00:00+02:00
head: 489607174f22b8b36663fe2251cdba0423388fbd
branch: feat/e2e-qri-002-canary-restart-recovery
pr: none
status: implementing
context_routes:
  - universal-e2e
  - agent-governance
  - cpp-runtime
owned_paths:
  - docs/agents/tasks/active/CAN-20260723-e2e-qri-002-canary-restart-recovery.md
  - tests/e2e/scenarios/recovery/canary-restart-recovery.json
  - tests/e2e/test_canary_restart_recovery.py
  - tools/e2e/run_physical_e2e.sh
  - tools/e2e/run_agent_e2e.py
  - tools/e2e/client/agent_e2e_scenario.lua
proven:
  - Current main preflight head is 489607174f22b8b36663fe2251cdba0423388fbd.
  - No open E2E-QRI-001, E2E-QRI-002 or E2E-QRI-003 pull request was visible in the live open-PR inventory at task start.
  - E2E-QRI-005 result-envelope and E2E-QRI-006 cleanup-certification packages are not implemented on current main; current result.json remains schema version 2 and cleanup is not a first-class certification envelope.
  - The canonical physical runner owns one CANARY_PID, one exact CANARY_BIN and one generated disposable config, so the same process slot can be restarted without a second runner.
  - No fixed-purpose Canary server restart seam exists on current main; the existing recovery contract is client-only g_game.forceLogout().
  - Typed player_balance persistence is already client-plus-SQL and the existing Canary promotion E2E physically uses the God-only /addmoney setup action.
derived:
  - The smallest safe implementation is a manifest-validated boolean recovery capability that can only request restart of the runner-owned disposable Canary process and exposes no target parameter.
  - A deterministic bank-balance mutation followed by the existing typed player_balance check can prove state both before restart in the controlled client and after physical relog, with final SQL confirmation.
unknown:
  - Exact physical behavior of the first implementation under GitHub Actions until the selected recovery scenario runs.
  - Whether SIGTERM shutdown latency requires a bounded wait adjustment; forced arbitrary PID killing is not authorized.
conflicts: []
first_failure:
  marker: none
  evidence: Preflight found a missing fixed-purpose Canary restart seam, not an implementation failure.
rejected_hypotheses:
  - Reuse client forceLogout as QRI-002: rejected because it does not restart the Canary process.
  - Create a second server runner or workflow: rejected because the canonical runner already owns the exact disposable process slot and binary/configuration.
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-e2e-qri-002-canary-restart-recovery.md
validation:
  - command: live GitHub preflight against main and open PR inventory
    result: PASS
    evidence: Main, programme, roadmap, module catalogue, lifecycle runner, recovery scenario and workflow were inspected before ownership was claimed.
blockers: []
next_action: Create the draft PR, implement the minimal manifest guard plus runner-owned restart seam and client recovery synchronization, then run focused and physical GitHub Actions validation.
```
