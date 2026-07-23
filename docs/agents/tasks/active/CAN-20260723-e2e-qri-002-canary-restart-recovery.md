---
task_id: CAN-20260723-e2e-qri-002-canary-restart-recovery
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-QRI-002-CANARY-RESTART-RECOVERY
status: ready
agent: "GPT-5.6 Thinking"
branch: feat/e2e-qri-002-canary-restart-recovery-v2
base_branch: main
created: 2026-07-23
updated: 2026-07-23
last_verified_commit: "b5747dee88c914ea64a704f831e145d3495af777"
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

- [x] Reuse exactly one existing disposable Canary/MariaDB/controlled-OTClient lifecycle and the same pinned Canary binary/configuration.
- [x] Add only a fixed-purpose restart seam with no caller-selected command, PID, host or external target.
- [x] Prove the old Canary process terminated before the replacement process starts and record old/new PID evidence.
- [x] Distinguish pre-restart gameplay, restart request, process termination, server startup, readiness, reconnect, relog, persistence assertion and cleanup phases.
- [x] Execute one deterministic durable mutation and verify persisted state before restart and after physical relog.
- [x] Prove no stale/ghost player session prevents re-entry and final `players_online` cleanup is zero.
- [x] Add focused restart-seam tests, including negative guard coverage proving no arbitrary command/PID/host recovery target surface exists.
- [x] Validate scenario/schema contract and exact changed-file ownership.
- [x] Pass physical Canary restart E2E, reconnect/relogin, persistence assertion, cleanup and repository CI.
- [x] Apply `ci:final-gate` before the final checkpoint commit; make no later feature-branch commit; audit reviews and exact final head; squash-merge; archive lifecycle.

## Candidate evidence audit

- Candidate feature head physically exercised before this final checkpoint: `b5747dee88c914ea64a704f831e145d3495af777`.
- Repository CI on candidate head: PASS, run `30028686263`.
- Agent Task Ownership on candidate head: PASS, run `30028685955`.
- Universal Agent E2E: PASS after retrying one infrastructure-only container initialization failure, run `30028686182`.
- Physical job: PASS, job `89334202962`.
- Required physical gate: PASS, job `89334733509`.
- Physical evidence artifact: `8578842360`, digest `sha256:6b6ccdc4ddf80b2a5ffa894e0be78d057ebd6eb92bf67c965d34535ae4e2258e`.
- Real process proof: old Canary PID `4774` terminated and was inactive before replacement; replacement Canary PID `4951` started from the same exact binary.
- Durable mutation proof: database balance `12345` confirmed before termination; controlled OTClient confirmed balance `12345` after physical relog; final typed SQL assertion passed.
- Recovery proof: real server disconnect observed and classified as expected; replacement server readiness observed; pre-relog ghost-session count `0`; second physical login succeeded.
- Cleanup proof: safe logout completed; replacement Canary stopped through the same exact-process guard; final `players_online=0`.
- All restart phases passed: pre-restart-gameplay, restart-request, process-termination, server-startup, readiness, reconnect, relog, persistence-assertion and cleanup.
- Client exit code `0`; two packet records and two server logins observed; no fatal runtime log hits.
- Latest observed `main` before final checkpoint: `0a2ae8e3d504ab2398395820512cd45f3b169722`. Fresh comparison found no overlap with the six QRI-002 runtime/task paths; parallel QRI-001 and QRI-003 lifecycles are already merged/archived.
- Exact PR scope audit before final checkpoint: six changed paths only, all within declared QRI-002 ownership; no trade or Journey 002 files.
- Review audit before final checkpoint: no PR comments, no review submissions and no inline review threads.
- `ci:final-gate` was applied to PR #805 before this final checkpoint commit.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T23:25:00+02:00
head: b5747dee88c914ea64a704f831e145d3495af777
branch: feat/e2e-qri-002-canary-restart-recovery-v2
pr: 805
status: ready
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
  - The canonical Universal Physical E2E runner remains the only physical lifecycle runner; no second runner, workflow, fault executor or production restart API was added.
  - The restart seam is hard-bound to recovery/canary-restart-recovery and Paladin 15 and accepts no arbitrary command, PID, host or target selector.
  - Runner-owned lifecycle PID resolution is bounded to the single exact direct child whose /proc executable matches CANARY_BIN; replacement startup uses the same exact binary and updates runner-owned cleanup state.
  - The selected vertical slice credits exactly 12345 bank gold, requests fixed server save, proves database persistence before termination, physically restarts Canary, observes the disconnect, waits for new-server readiness and zero ghost rows, relogs and proves the same 12345 balance through the fresh client session.
  - Physical result status is success with every restart check true, old PID 4774, new PID 4951, ghost count 0 and final players_online count 0.
  - Repository CI and Agent Task Ownership passed on candidate head b5747dee88c914ea64a704f831e145d3495af777.
  - Universal Agent E2E run 30028686182 passed exact Canary build, controlled OTClient build, physical recovery scenario and required physical gate after a retry of an infrastructure-only container-init failure.
  - Artifact 8578842360 retains the exact physical result, phase ledger, client events, PIDs, SQL assertions and cleanup evidence.
  - Latest observed main 0a2ae8e3d504ab2398395820512cd45f3b169722 has no QRI-002 path overlap; final PR validation runs against the current pull-request merge candidate.
  - PR #805 had zero comments, zero reviews and zero review threads before final checkpoint.
derived:
  - Database verification after the fixed /save request is the correct pre-restart persistence proof because the maintained client's local bank resource cache does not necessarily refresh immediately after the God-only setup command.
  - The initial canonical runner PID may be a lifecycle subshell; the restart seam therefore resolves only its exact direct Canary-binary child before termination and never exposes a caller-selected PID surface.
unknown:
  - Exact final checkpoint-head gate results until this final checkpoint commit completes Agent Task Ownership, full ci:final-gate CI and Universal Agent E2E validation.
conflicts: []
first_failure:
  marker: none
  evidence: Candidate physical run 30028686182 passed the complete real restart, disconnect, readiness, relog, persistence and cleanup contract.
rejected_hypotheses:
  - Reuse client forceLogout as QRI-002: rejected because it does not restart the Canary process.
  - Add a generic command/PID/host restart contract: rejected because QRI-002 requires a fixed-purpose disposable-E2E-only seam.
  - Add a second workflow or independent server lifecycle: rejected.
  - Treat the maintained client's stale local pre-restart balance cache as persistence truth: rejected; exact DB persistence after fixed /save is authoritative before termination while fresh-client balance plus final SQL prove post-restart persistence.
  - Treat the runner lifecycle subshell PID as the Canary executable PID: rejected; exact direct-child /proc executable matching is required before SIGTERM.
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-e2e-qri-002-canary-restart-recovery.md
  - tools/e2e/disposable_canary_restart.sh
  - tools/e2e/client/agent_e2e_canary_restart_recovery.lua
  - tests/e2e/scenarios/recovery/canary-restart-recovery.json
  - tests/e2e/test_canary_restart_recovery.py
  - tools/e2e/run_physical_e2e.sh
validation:
  - command: CI run 30028686263
    result: PASS
    evidence: Repository CI passed on candidate feature head b5747dee88c914ea64a704f831e145d3495af777.
  - command: Agent Task Ownership run 30028685955
    result: PASS
    evidence: Task ownership, focused contract coverage and changed-file governance passed on candidate head.
  - command: Universal Agent E2E run 30028686182
    result: PASS
    evidence: Physical job 89334202962 and required gate 89334733509 passed after retrying an infrastructure-only container initialization failure.
  - command: Physical artifact 8578842360 audit
    result: PASS
    evidence: Every restart phase and check is true; old/new PIDs differ; balance 12345 persists; ghost count and final players_online are zero; client exit is zero.
  - command: Current-main scope and PR review audit
    result: PASS
    evidence: main 0a2ae8e3d504ab2398395820512cd45f3b169722 adds no overlap with QRI-002 paths; PR diff is exactly six owned paths; comments, reviews and review threads are empty.
blockers:
  - Exact final checkpoint-head Agent Task Ownership, full ci:final-gate CI and Universal Agent E2E must pass with no later feature-branch commit.
next_action: Make no further feature-branch commit. Require exact final checkpoint-head gates, then re-audit scope/reviews, mark PR #805 ready, squash-merge with expected final head SHA, verify main, and complete lifecycle-only active-to-archive closure.
```
