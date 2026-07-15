---
task_id: CAN-20260715-universal-agent-load-platform
program_id: CAN-PROGRAM-E2E-PLATFORM
status: validating
agent: chatgpt-e2e-platform
branch: feat/universal-agent-load-platform
base_branch: main
created: 2026-07-15T15:40:00+02:00
updated: 2026-07-15T18:37:00+02:00
last_verified_commit: e6d59275201f746453c3db8943e09a2703a741e5
risk: medium
related_issue: ""
related_pr: "384"
depends_on:
  - CAN-20260713-universal-agent-e2e-platform
blocks: []
owned_paths:
  exclusive:
    - tools/e2e/run_agent_load.py
    - tools/e2e/run_agent_load_runtime.py
    - tests/e2e/load/**
    - tests/e2e/test_load_runner.py
    - .github/workflows/universal-agent-load.yml
    - src/server/network/protocol/protocolstatus.cpp
    - src/server/network/protocol/protocolstatus.hpp
    - docs/agents/tasks/active/CAN-20260715-universal-agent-load-platform.md
  shared:
    - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/e2e/run_physical_e2e.sh
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/client/**
    - tests/e2e/scenarios/login/**
    - .github/workflows/universal-agent-e2e.yml
    - .github/scripts/smoke_test_canary.py
modules_touched:
  - universal E2E load/stress platform
  - Canary status-protocol load client
  - Canary ProtocolStatus query throttle synchronization
reuses:
  - merged PR #245 universal physical-client E2E platform
  - existing exact-head reusable Linux Canary build
  - existing smoke_test_canary.py database/config/map lifecycle helpers
  - Canary ProtocolStatus XML info request contract
  - existing physical login/relog E2E as correctness sentinel
public_interfaces:
  - run_agent_load.py profile CLI and JSON result contract
  - run_agent_load_runtime.py exact-head Canary load runtime
  - universal-agent-load workflow_dispatch profile interface
cross_repo_tasks: []
---

# Goal

Add one reusable, deterministic and loopback-only load/stress layer beside the merged physical-client E2E platform. The first bounded capability exercises Canary's real TCP status protocol at controlled concurrency, collects latency/throughput/error and Canary CPU/RSS evidence, and preserves the existing real-OTClient `login/relog` scenario as the correctness sentinel.

This task does **not** claim to simulate authenticated gameplay players. It establishes a status/transport/control-plane regression and capacity baseline that can scale cheaply without spawning hundreds of graphical OTClient processes.

# Acceptance criteria

- [x] A standard-library Python load runner sends the structurally correct Canary `status-xml` request over real TCP.
- [x] Targets are restricted to literal loopback addresses.
- [x] JSON profiles support bounded `load` and multi-stage `stress` modes.
- [x] Results include attempts, successes, failures, error rate, throughput, connect/round-trip P50/P95/P99/max, bytes and error breakdown.
- [x] A local Canary PID can be sampled for peak RSS and process CPU percentage.
- [x] A gating `status-smoke` profile plus larger load/stress example profiles exist.
- [x] Runtime bootstrap reuses `.github/scripts/smoke_test_canary.py` lifecycle helpers.
- [x] Dedicated exact-head GitHub Actions load workflow uploads machine-readable evidence.
- [x] Concurrent `ProtocolStatus` requests no longer crash Canary; the existing status-query throttle check/update is synchronized without changing policy semantics.
- [x] Existing Universal Agent E2E `login/relog` remains unchanged and passed on verified head `e6d59275201f746453c3db8943e09a2703a741e5`.
- [x] Focused Python unit tests and bytecode compilation pass.
- [ ] Final current-head CI, ownership, load workflow and physical E2E pass after the last diff-review cleanup commit.
- [x] No OTClient source change, upstream write, production host/credential, binary map asset or gameplay behavior change.

# Ownership and overlap

- Task-start main: `63fbacc9ab2d31b480de9d756194e22ce22b7d35`.
- The completed #245 platform task was archived by merged PR #382 before this task claimed E2E platform paths.
- Open donor-audit/Oteryn documentation work observed during this task did not overlap the owned E2E or `ProtocolStatus` implementation paths.
- Existing physical E2E orchestration and OTClient automation remain read-only.
- `ACTIVE_WORK.md` is not edited.

# Proven protocol contract

`ServicePort::make_protocol()` consumes the first body byte as the service `PROTOCOL_IDENTIFIER`. `ProtocolStatus::onRecvFirstMessage()` then consumes the protocol opcode and expects four raw bytes `info`.

The canonical framed request is therefore:

```text
06 00 FF FF 69 6E 66 6F
```

The first `FF` selects `ProtocolStatus`; the second `FF` selects XML info within `ProtocolStatus`.

# Evidence-backed runtime repair

The first valid concurrent status run exposed a real Canary `SIGSEGV`. `ProtocolStatus::ipConnectMap` is process-wide mutable state reached from network I/O callbacks. The task was explicitly expanded to own this narrow runtime path after confirming no overlapping active owner.

The repair serializes the existing throttle lookup/update critical section with a mutex. It does not disable, relax or change status-query throttling semantics. Synthetic load profiles use distinct loopback source addresses in `127/8` so normal per-IP anti-abuse/status throttles remain active.

# Work log

## 2026-07-15T15:40:00+02:00

- Created a fresh platform task after archiving stale completed #245 ownership.
- Chose a bounded `status-xml` load surface and explicitly separated it from authenticated-player capacity claims.
- Preserved the one-process real OTClient `login/relog` scenario as the generic correctness sentinel.

## 2026-07-15T16:25:00+02:00

- Universal Agent Load #1 (`29421251772`) proved the first request framing was incomplete.
- Source inspection proved service routing consumes the first `0xFF`, requiring body `FF FF + info`.
- Universal Agent Load #3 (`29422353758`) then exposed a Canary `SIGSEGV` under concurrent valid status requests.
- Inspection identified unsynchronized process-wide `ProtocolStatus::ipConnectMap` check/write access as the concrete race surface; the critical section was synchronized.

## 2026-07-15T18:37:00+02:00

- Universal Agent Load #16 (`29430993797`) completed successfully on verified head `e6d59275201f746453c3db8943e09a2703a741e5`.
- Load artifact `universal-agent-load-status-smoke` recorded 100 attempts, 100 successes, 0 failures, error rate `0.0`, aggregate throughput `5425.422` req/s and P95 round-trip `2.046 ms`; these are CI-runner regression measurements, not absolute production capacity claims.
- Runtime summary was `success/complete`, Canary stderr was empty and no fatal/crash pattern was present.
- Universal Agent E2E #58 (`29430996846`) completed successfully on the same PR merge test state with exact controlled OTClient ref `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`.
- E2E evidence recorded two successful logins, two packet records, safe logout for both sessions, persistence confirmation, zero final online count, client exit `0`, no fatal runtime logs and `e2e=success`.
- Full diff review found and repaired one unrelated accidental deletion of the historical PR #297 changelog entry.
- Final action: make one focused test-only refinement that mirrors real `ServicePort` identifier consumption; this becomes the final head and intentionally retriggers CI, ownership, load and physical E2E before readiness/merge.

# Validation

| Commit | Check | Result | Notes |
|---|---|---|---|
| `e6d59275201f746453c3db8943e09a2703a741e5` | CI #2495 | pass | repository CI |
| `e6d59275201f746453c3db8943e09a2703a741e5` | Agent Task Ownership #1369 | pass | owned paths conflict-free |
| `e6d59275201f746453c3db8943e09a2703a741e5` | Universal Agent Load #16 | pass | 100/100 status requests; no crash |
| `e6d59275201f746453c3db8943e09a2703a741e5` | Universal Agent E2E #58 | pass | unchanged real one-process login/relog |
| final head | CI / ownership / load / physical E2E | pending | required after final diff-review cleanup |

# Handoff

Start with this task, PR #384, `docs/agents/programs/E2E_AUTOMATION_PROGRAM.md`, archived `CAN-20260713-universal-agent-e2e-platform`, `tools/e2e/run_agent_load.py`, `tools/e2e/run_agent_load_runtime.py`, `.github/scripts/smoke_test_canary.py`, `src/server/network/protocol/protocolstatus.cpp`, and the unchanged physical E2E platform.

Do not create a second physical-client E2E orchestrator, do not modify OTClient for load generation, do not weaken server anti-abuse limits to make a benchmark green, and do not describe status-protocol concurrency as logged-in gameplay-player capacity.
