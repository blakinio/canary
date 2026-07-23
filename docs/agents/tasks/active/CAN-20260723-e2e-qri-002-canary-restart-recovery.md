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
last_verified_commit: "2c790c8278392dc2729473e3a0455267855b4937"
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
    - tools/e2e/disposable_canary_restart.sh
    - tools/e2e/client/agent_e2e_canary_restart_recovery.lua
    - tests/e2e/scenarios/recovery/canary-restart-recovery.json
    - tests/e2e/test_canary_restart_recovery.py
  shared:
    - tools/e2e/run_physical_e2e.sh
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
updated_at: 2026-07-23T16:58:00+02:00
head: 2c790c8278392dc2729473e3a0455267855b4937
branch: feat/e2e-qri-002-canary-restart-recovery-v2
pr: 805
status: implementing
context_routes:
  - universal-e2e
  - agent-governance
  - cpp-runtime
owned_paths:
  - docs/agents/tasks/active/CAN-20260723-e2e-qri-002-canary-restart-recovery.md
  - tools/e2e/disposable_canary_restart.sh
  - tools/e2e/client/agent_e2e_canary_restart_recovery.lua
  - tests/e2e/scenarios/recovery/canary-restart-recovery.json
  - tests/e2e/test_canary_restart_recovery.py
  - tools/e2e/run_physical_e2e.sh
proven:
  - The latest observed main head is b9414cadf0b9cce263b3e79c4ac4e3829ba53769; final branch refresh against then-current main remains required before the final gate.
  - QRI-001 is now active in PR 806 but its current write-set is confined to its own task plus trade/multiclient files and does not overlap the QRI-002 runner or recovery seam.
  - QRI-003 is active in PR 803 but declares shared E2E runner/client/workflow paths read-only and owns only its Journey 002 task/scenario/test files.
  - QRI-005 result-envelope and QRI-006 cleanup-certification packages are not implemented on current main; current result.json remains schema version 2 and cleanup is not a first-class certification envelope.
  - The implementation does not modify run_agent_e2e.py, the generic gameplay driver, the workflow, trade files or Journey 002 files.
  - The prototype duplicate run_physical_e2e_core.sh was removed; the canonical run_physical_e2e.sh remains the only physical lifecycle runner.
  - The canonical runner sources one fixed-purpose disposable_canary_restart.sh seam and invokes it synchronously, so the same shell that owns CANARY_PID verifies, terminates and replaces exactly that process, then updates CANARY_PID to the replacement process for normal cleanup.
  - The restart seam is hard-bound to recovery/canary-restart-recovery and Paladin 15, exposes no manifest target object and accepts no arbitrary command, PID, host or process selector.
  - The seam validates /proc/<pid>/exe against the exact CANARY_BIN before every termination, uses fixed SIGTERM without SIGKILL fallback, proves the old PID inactive, starts the same CANARY_BIN with the existing generated config/database, and records a distinct replacement PID.
  - The selected vertical slice credits the reset Paladin 15 fixture with exactly 12345 bank gold, verifies that value in the controlled client before restart, requests /save, physically relogs after restart, verifies the same value again in the controlled client, and retains typed player_balance final SQL compilation.
  - Readiness is not released to the client until the replacement server emits a new server-online marker and Paladin 15 has zero players_online rows; final cleanup additionally requires all players_online rows to be zero and stops the replacement Canary through the same exact-process guard.
  - Repository CI and Agent Task Ownership were green on implementation head 77978b17778f4306fd74693908f07b13d276257e before the focused-test correction.
  - Universal Agent E2E run 30015827298 built exact-head Canary and the controlled OTClient successfully, then failed before Canary/client startup with result phase scenario-resolution and an empty restart phase file.
  - The focused contract test had one invalid source-order assumption: it searched for mutation then save then restart marker text globally, while saveAndRequestRestart and requestRestart are correctly defined before mutatePersistentState and reached through callbacks. The test now validates each callback body and the explicit callback wiring instead of function-definition order.
derived:
  - A sourced fixed-purpose seam is the smallest reusable change that keeps restart ownership inside the existing canonical runner and avoids a second orchestrator, runner or workflow.
  - The first physical run did not exercise SIGTERM, replacement startup, ghost-session readiness, reconnect or persistence because validation stopped during scenario-resolution before those phases.
unknown:
  - Exact physical behavior of the restart seam under GitHub Actions after the focused-test correction.
  - Whether the exact Canary process exits within the bounded SIGTERM wait on the hosted runner; no SIGKILL fallback is implemented.
conflicts: []
first_failure:
  marker: scenario-resolution
  evidence: Universal Agent E2E run 30015827298 produced result.json phase scenario-resolution with shell_exit_code 1 and an empty canary-restart-phases.tsv; exact source inspection proved the focused mutation-order regex contradicted the valid callback-definition order, and commit 2c790c8278392dc2729473e3a0455267855b4937 replaced that source-order assertion with callback-chain assertions.
rejected_hypotheses:
  - Reuse client forceLogout as QRI-002: rejected because it does not restart the Canary process.
  - Add a generic command/PID/host restart contract: rejected because the recovery seam is exact-scenario and exact-character gated and uses only the runner-owned CANARY_PID plus exact CANARY_BIN identity.
  - Add a second workflow or independent server lifecycle: rejected.
  - Retain the prototype run_physical_e2e_core.sh copy: rejected and removed because direct synchronous integration in the canonical runner is narrower and preserves one runner/process owner.
  - Attribute run 30015827298 to Canary SIGTERM or stale players_online behavior: rejected because retained evidence shows no restart phase was entered.
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-e2e-qri-002-canary-restart-recovery.md
  - tools/e2e/disposable_canary_restart.sh
  - tools/e2e/client/agent_e2e_canary_restart_recovery.lua
  - tests/e2e/scenarios/recovery/canary-restart-recovery.json
  - tests/e2e/test_canary_restart_recovery.py
  - tools/e2e/run_physical_e2e.sh
validation:
  - command: CI run 30015826832 on head 77978b17778f4306fd74693908f07b13d276257e
    result: PASS
    evidence: Repository CI passed on the single-runner implementation before the focused-test correction.
  - command: Agent Task Ownership run 30015824940 on head 77978b17778f4306fd74693908f07b13d276257e
    result: PASS
    evidence: Changed-file ownership and task checkpoint validation passed before the focused-test correction.
  - command: Universal Agent E2E run 30015827298 on head 77978b17778f4306fd74693908f07b13d276257e
    result: FAIL
    evidence: Exact Canary and controlled OTClient builds passed; selected physical scenario failed at scenario-resolution before any restart phase because the focused test encoded invalid source-definition ordering.
blockers:
  - exact-current-head repository CI and Agent Task Ownership must pass after the focused-test correction
  - exact-current-head Universal Agent E2E must physically prove termination, replacement startup, readiness, reconnect/relog, persistence and cleanup
  - reusable contract must be registered in MODULE_CATALOG.md and completed behavior recorded in CHANGELOG.md before final gate
next_action: Inspect the new exact-current-head validation runs, fix the first physical restart phase if any remains, then refresh from current main and batch the module catalogue, changelog and final checkpoint before ci:final-gate sequencing.
```
