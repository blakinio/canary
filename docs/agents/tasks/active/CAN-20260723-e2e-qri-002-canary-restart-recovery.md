---
task_id: CAN-20260723-e2e-qri-002-canary-restart-recovery
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-QRI-002-CANARY-RESTART-RECOVERY
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/e2e-qri-002-canary-restart-recovery-v2
base_branch: main
created: 2026-07-23
updated: 2026-07-23
last_verified_commit: "304c51ac46e2ddef53cd0ce3653d0609845ef315"
risk: medium
related_issue: ""
related_pr: "805"
depends_on:
  - stable Universal Physical E2E single-Canary lifecycle
  - E2E-GAMEPLAY-007 controlled disconnect/recovery evidence pattern
  - typed player_balance persistence assertion
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260723-e2e-qri-002-canary-restart-recovery.md
    - tools/e2e/client/agent_e2e_canary_restart_recovery.lua
    - tests/e2e/scenarios/recovery/canary-restart-recovery.json
    - tests/e2e/test_canary_restart_recovery.py
  shared:
    - tools/e2e/run_physical_e2e.sh
    - tools/e2e/run_physical_e2e_core.sh
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/client/agent_e2e_scenario.lua
    - .github/workflows/universal-agent-e2e.yml
    - tests/e2e/scenarios/multiclient/**
    - tests/e2e/scenarios/journeys/**
modules_touched:
  - Universal E2E disposable Canary restart/recovery
reuses:
  - existing disposable Canary/MariaDB/controlled-OTClient lifecycle
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
- [ ] Add focused restart-seam tests, including negative guard coverage proving no arbitrary command/PID/host recovery target surface exists.
- [ ] Validate scenario/schema contract and exact changed-file ownership.
- [ ] Pass physical Canary restart E2E, reconnect/relogin, persistence assertion, cleanup and repository CI.
- [ ] Apply `ci:final-gate` before the final checkpoint commit; make no post-green commit; audit reviews and exact final head; squash-merge; archive lifecycle.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T16:15:00+02:00
head: 304c51ac46e2ddef53cd0ce3653d0609845ef315
branch: feat/e2e-qri-002-canary-restart-recovery-v2
pr: 805
status: implementing
context_routes:
  - universal-e2e
  - agent-governance
  - cpp-runtime
owned_paths:
  - docs/agents/tasks/active/CAN-20260723-e2e-qri-002-canary-restart-recovery.md
  - tools/e2e/client/agent_e2e_canary_restart_recovery.lua
  - tests/e2e/scenarios/recovery/canary-restart-recovery.json
  - tests/e2e/test_canary_restart_recovery.py
  - tools/e2e/run_physical_e2e.sh
  - tools/e2e/run_physical_e2e_core.sh
proven:
  - Current main preflight was refreshed to b8a88f073b2609b444fa15370aae30ac9f80b908 before shared E2E files were edited.
  - QRI-003 is active in PR 803 but declares shared E2E runner/client/workflow paths read-only and owns only its Journey 002 task/scenario/test files.
  - No open QRI-001 pull request was visible at the refreshed overlap check.
  - QRI-005 result-envelope and QRI-006 cleanup-certification packages are not implemented on current main; current result.json remains schema version 2 and cleanup is not a first-class certification envelope.
  - The implementation does not modify run_agent_e2e.py, the generic gameplay driver, the workflow, trade files or Journey 002 files.
  - The public physical E2E entrypoint delegates the existing canonical lifecycle body unchanged to run_physical_e2e_core.sh and only activates the fixed restart watcher for the exact recovery/canary-restart-recovery key.
  - The restart seam reads only the canonical runner-owned canary.pid, verifies /proc/<pid>/exe equals the exact CANARY_BIN, sends fixed SIGTERM, proves the old PID is inactive, then launches the same exact CANARY_BIN with the existing config/database and records a distinct replacement PID.
  - The selected vertical slice credits the reset Paladin 15 fixture with exactly 12345 bank gold, verifies that value in the controlled client before restart, requests /save, physically relogs after restart, verifies the same value again in the controlled client, and retains typed player_balance final SQL compilation.
  - Readiness is not released to the client until the replacement server emits a new server-online marker and the fixed Paladin 15 players_online count is zero, preventing a stale-session false recovery.
derived:
  - Moving the unchanged lifecycle body behind the canonical public entrypoint avoids a second workflow or independently implemented server runner while permitting a bounded sidecar restart watcher to update the process slot the original body cannot mutate across shell-process boundaries.
unknown:
  - Exact physical behavior of the implementation under GitHub Actions until the selected recovery scenario completes.
  - Whether the exact Canary process exits within the bounded SIGTERM wait on the hosted runner; no SIGKILL fallback is implemented.
conflicts: []
first_failure:
  marker: none
  evidence: No implementation failure has been observed yet; current validation is entering CI/physical execution.
rejected_hypotheses:
  - Reuse client forceLogout as QRI-002: rejected because it does not restart the Canary process.
  - Add a generic command/PID/host restart contract: rejected because the recovery seam is exact-scenario gated and resolves only the canonical canary.pid plus exact CANARY_BIN identity.
  - Add a second workflow or independent server lifecycle: rejected; the unchanged canonical lifecycle body is reused.
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-e2e-qri-002-canary-restart-recovery.md
  - tools/e2e/client/agent_e2e_canary_restart_recovery.lua
  - tests/e2e/scenarios/recovery/canary-restart-recovery.json
  - tests/e2e/test_canary_restart_recovery.py
  - tools/e2e/run_physical_e2e.sh
  - tools/e2e/run_physical_e2e_core.sh
validation:
  - command: CI run 30014586503 on implementation head a163d71775fc5705c4f4f52f55d1471ae9b73684
    result: PASS
    evidence: Repository CI completed successfully before the focused-test correction and ownership checkpoint commits; exact-current-head rerun remains required.
  - command: Universal Agent E2E run 30014588310
    result: RUNNING
    evidence: Physical validation was queued from the implementation head; exact-current-head validation remains required after all implementation changes settle.
blockers: []
next_action: Register the reusable restart contract in shared docs, audit current-head CI/Ownership/Universal Agent E2E, fix any physical failure, then enter exact-final-head gate sequencing.
```
