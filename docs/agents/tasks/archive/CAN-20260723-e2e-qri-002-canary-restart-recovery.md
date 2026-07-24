---
task_id: CAN-20260723-e2e-qri-002-canary-restart-recovery
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-QRI-002-CANARY-RESTART-RECOVERY
status: completed
agent: "GPT-5.6 Thinking"
branch: feat/e2e-qri-002-canary-restart-recovery-v2
base_branch: main
created: 2026-07-23
updated: 2026-07-23
last_verified_commit: "3de39b3c99f50ef75700859cd6da2308714fd273"
risk: medium
related_issue: ""
related_pr: "805"
depends_on:
  - stable Universal Physical E2E single-Canary lifecycle
  - E2E-GAMEPLAY-007 controlled disconnect/recovery evidence pattern
  - typed player_balance persistence assertion
blocks: []
owned_paths:
  exclusive: []
  shared: []
  read_only: []
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

## Completion

- Final status: completed.
- Delivery PR: #805.
- Exact final delivery PR head: `d30619a86b542cf7af60d1e23104975cacf6bdd8`.
- Squash merge commit: `3de39b3c99f50ef75700859cd6da2308714fd273`.
- Final Agent Task Ownership: PASS, run `30045743811`.
- Final full `ci:final-gate` CI: PASS, run `30047847631`.
- Final `autofix.ci`: PASS, run `30047847465`.
- Final Universal Agent E2E: PASS, run `30045744212`.
- Final physical job: `89342380220` PASS.
- Final required physical gate: `89342813845` PASS.
- Final physical artifact: `8579789590`, digest `sha256:428ceb5307bc1f59d261adf311ed89c5f62cb8f02f6e1a0c36af4c9de849b72d`.

## Delivered proof

- The canonical Universal Physical E2E lifecycle remains the only Canary/MariaDB/controlled-OTClient runtime owner; no second runner, workflow, fault executor or production restart API was added.
- `recovery/canary-restart-recovery` uses a fixed-purpose disposable-E2E-only restart seam hard-bound to the selected scenario and `Paladin 15`; callers cannot select arbitrary commands, PIDs, hosts or external restart targets.
- The seam resolves only the single runner-owned direct child whose `/proc/<pid>/exe` exactly matches `CANARY_BIN`, terminates that exact process with bounded `SIGTERM`, proves the old PID inactive, and starts the same exact Canary binary as a replacement with a distinct PID.
- The controlled client performs the deterministic `12345` bank-balance mutation, requests the fixed server save, and the runner proves `balance=12345` in MariaDB before process termination.
- A real server transport loss is observed and classified as the expected injected failure; replacement-server readiness is withheld until a new server-online event and zero ghost `players_online` rows are proven.
- The maintained controlled OTClient physically relogs and proves bank balance `12345` in the fresh session; final typed SQL persistence assertions also pass.
- Safe logout completes, final `players_online=0` is proven, and the replacement Canary is stopped through the same exact-process guard.
- The evidence ledger records successful `pre-restart-gameplay`, `restart-request`, `process-termination`, `server-startup`, `readiness`, `reconnect`, `relog`, `persistence-assertion` and `cleanup` phases.

## Final scope and review audit

- Delivery PR #805 changed exactly six QRI-002 paths:
  - `docs/agents/tasks/active/CAN-20260723-e2e-qri-002-canary-restart-recovery.md`;
  - `tests/e2e/scenarios/recovery/canary-restart-recovery.json`;
  - `tests/e2e/test_canary_restart_recovery.py`;
  - `tools/e2e/client/agent_e2e_canary_restart_recovery.lua`;
  - `tools/e2e/disposable_canary_restart.sh`;
  - `tools/e2e/run_physical_e2e.sh`.
- No trade/multiclient or Journey 002 files were modified.
- Final PR audit found no issue comments, review submissions or inline review threads.
- `ci:final-gate` was applied before the final checkpoint commit and no later delivery-branch commit was made.
- Exact final-head CI, Agent Task Ownership and Universal Agent E2E all passed before squash merge.

## Evidence boundaries

- QRI-002 consumes the repository's existing result envelope; it does not claim delivery of a separate QRI-005 standard result package.
- QRI-002 proves bounded teardown and final zero online rows; it does not claim a separate QRI-006 first-class cleanup-certification contract.
- Earlier failed physical attempts remain retained evidence and were not hidden by retries. Fixes followed the first causal failures: stale client-side pre-restart balance cache, then canonical runner lifecycle-subshell PID versus exact Canary executable PID.
- One later exact-head attempt failed only during GitHub runner container initialization before checkout/build and was rerun without a code change.

## Lifecycle closure

The delivery package is merged and no longer owns active paths. This archive record releases all QRI-002 task ownership. No follow-on QRI package is started by this lifecycle closure.
