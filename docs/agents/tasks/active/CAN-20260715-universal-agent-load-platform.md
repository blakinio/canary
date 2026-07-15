---
task_id: CAN-20260715-universal-agent-load-platform
program_id: CAN-PROGRAM-E2E-PLATFORM
status: implementing
agent: chatgpt-e2e-platform
branch: feat/universal-agent-load-platform
base_branch: main
created: 2026-07-15T15:40:00+02:00
updated: 2026-07-15T16:25:00+02:00
last_verified_commit: 6c67cefa8de9147c2cc71542df1e26d013714fd0
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

Add one reusable, deterministic and loopback-only load/stress layer beside the merged physical-client E2E platform. The first bounded capability exercises Canary's real TCP status protocol at controlled concurrency, collects latency/throughput/error and Canary CPU/RSS evidence, and retains the existing real-OTClient `login/relog` scenario as the correctness sentinel.

This task does **not** claim to simulate authenticated gameplay players. It establishes an honest transport/status-protocol capacity baseline that can scale cheaply without spawning hundreds of graphical OTClient processes.

The first real concurrent run also exposed a Canary status-protocol crash. This task may repair that narrowly because the failure is directly exercised by the new bounded load surface and the fix remains inside the status protocol implementation.

# Acceptance criteria

- [x] A standard-library Python load runner sends the structurally correct Canary `status-xml` request over real TCP.
- [x] Targets are restricted to loopback addresses so the tool cannot be pointed at production or third-party servers.
- [x] JSON profiles support bounded `load` and multi-stage `stress` modes.
- [x] Results include attempts, successes, failures, error rate, throughput, connect/round-trip P50/P95/P99/max, bytes received and error breakdown.
- [x] When a local Canary PID is supplied, results include sampled peak RSS and process CPU percentage.
- [x] A small gating `status-smoke` profile and larger load/stress example profiles are provided.
- [x] The runtime reuses existing Canary smoke lifecycle helpers instead of creating a second database/map/config bootstrap implementation.
- [x] A dedicated workflow builds the exact PR Canary head, runs the gating load profile against a disposable local database/server and uploads machine-readable evidence.
- [ ] Concurrent `ProtocolStatus` requests do not crash Canary and the status query throttle state is synchronized without changing its policy semantics.
- [ ] Existing Universal Agent E2E `login/relog` remains unchanged and passes on the feature head.
- [x] Focused Python unit tests and bytecode compilation pass.
- [ ] Current-head CI, ownership, load workflow and physical E2E checks pass before merge.
- [x] No OTClient source change, upstream write, production host, production credential, binary map asset or gameplay/client protocol behavior change.

# Ownership and overlap

- Task-start main: `63fbacc9ab2d31b480de9d756194e22ce22b7d35`.
- Current observed main after task start: `9f388e1a79802e7d507842883aeb04d1c9ffc7a2`; the two intervening merges are documentation/context-routing work and do not overlap E2E/runtime implementation. `CHANGELOG.md` will be resolved from current main before merge.
- The completed #245 platform task was archived by PR #382 before this task claimed E2E platform paths.
- Open PR #316 owns only Targuna donor-audit paths and does not overlap this task.
- Open PR #386 is Oteryn lifecycle documentation only and does not overlap this task.
- No other open PR observed on 2026-07-15 claims `ProtocolStatus` implementation paths.
- Existing physical E2E orchestration and OTClient automation are read-only for this task.
- `ACTIVE_WORK.md` is not edited.

# Implementation plan

1. Add a loopback-only valid `ProtocolStatus` XML load generator and focused tests.
2. Add load/stress profile manifests with explicit gating policy.
3. Add a thin runtime adapter that reuses `.github/scripts/smoke_test_canary.py` lifecycle helpers and runs the load profile only after exact-head Canary is online.
4. Add a thin GitHub Actions workflow around the existing reusable Canary build and disposable database.
5. Use real exact-head load evidence to repair only proven harness/runtime defects.
6. Run unit/compile checks, exact-head load proof and unchanged physical `login/relog` E2E.
7. Update durable docs, review the complete diff and merge after all gates are green.

# Work log

## 2026-07-15T15:40:00+02:00

- Changed: created a fresh platform task after archiving the stale completed #245 task ownership.
- Decision: the first load platform measures status/transport/control-plane capacity and explicitly does not claim authenticated-player capacity.
- Decision: existing physical `login/relog` E2E remains the correctness sentinel; no OTClient modification or multi-process client workaround.

## 2026-07-15T16:25:00+02:00

- PROVEN: Universal Agent Load #1 (`29421251772`) built exact-head Canary and reached a clean online state, but 100/100 requests produced no valid XML response.
- PROVEN: the initial runner sent framed body `FF + info`.
- PROVEN: `ServicePort::make_protocol()` consumes the first body byte as `PROTOCOL_IDENTIFIER`; `ProtocolStatus::onRecvFirstMessage()` then expects another `0xFF` before the four-byte `info` command.
- Changed: runner request framing is now exact body `FF FF + info`, framed as `06 00 FF FF 69 6E 66 6F`; focused regression test locks those exact bytes.
- Changed: response reading now consumes the bounded raw response through EOF and records a diagnostic hex preview for invalid responses.
- PROVEN: Universal Agent Load #3 (`29422353758`) with corrected framing caused exact-head Canary to exit with code `-11` while processing the 100-request / concurrency-10 smoke stage. Evidence contained 8 empty responses, 7 connection resets and 85 later connection refusals after the server process died.
- PROVEN: `ProtocolStatus::ipConnectMap` is a process-wide static `std::map`; `onRecvFirstMessage()` reads and writes it before dispatching the response, while Canary's network service runs with multiple I/O threads.
- DERIVED: unsynchronized concurrent access to `ipConnectMap` is the concrete highest-confidence cause of the observed status-load `SIGSEGV`; the next patch will serialize the existing throttle check+update critical section without changing throttle policy.
- CONFLICT resolved: the earlier task note that `0xFF + info` was the complete request was incorrect; the required body is `0xFF + 0xFF + info` because service selection consumes the first identifier byte.

# Context checkpoint

- **Current task/PR:** `CAN-20260715-universal-agent-load-platform`, PR #384, branch `feat/universal-agent-load-platform`.
- **Current head:** `6c67cefa8de9147c2cc71542df1e26d013714fd0` before the pending `ProtocolStatus` synchronization patch.
- **PROVEN green:** focused Python compile/tests; Agent Task Ownership #1330; CI #2456.
- **PROVEN failing:** Universal Agent Load #3 exact-head runtime; Canary exits `-11` under 10 concurrent valid status XML requests.
- **PROVEN protocol contract:** framed request bytes `06 00 FF FF 69 6E 66 6F`; status service is registered on configured `STATUS_PORT`.
- **DERIVED root cause:** static `ProtocolStatus::ipConnectMap` has unsynchronized concurrent check/write access from network I/O callbacks.
- **Physical E2E:** run #45 was in progress when the load crash was diagnosed; it must be rerun/verified on the final current head after the runtime patch.
- **Main delta:** main advanced to `9f388e1a79802e7d507842883aeb04d1c9ffc7a2` via documentation-only #383/#385; no runtime/E2E implementation overlap observed.
- **Blockers:** load gate remains red until the status crash is fixed and revalidated.
- **next_action:** add a narrow mutex-protected `ipConnectMap` throttle critical section in `protocolstatus.hpp/.cpp`, then inspect exact-head load artifacts and keep the physical E2E unchanged.

# Validation

| Commit | Check | Result | Notes |
|---|---|---|---|
| `6c67cefa8de9147c2cc71542df1e26d013714fd0` | focused Python unit tests / compile | pass | workflow Validate load platform |
| `6c67cefa8de9147c2cc71542df1e26d013714fd0` | CI #2456 | pass | repository CI |
| `6c67cefa8de9147c2cc71542df1e26d013714fd0` | Agent Task Ownership #1330 | pass | path ownership before runtime expansion |
| `b5965437c803181732e82943f5126314aaaa932d` | Universal Agent Load #1 | fail | incomplete status request: `FF + info` |
| `6c67cefa8de9147c2cc71542df1e26d013714fd0` | Universal Agent Load #3 | fail | corrected request exposes Canary `SIGSEGV` under concurrency |
| pending | Universal Agent E2E | pending | unchanged physical `login/relog` on final head |
| pending | final Universal Agent Load | pending | exact-head Canary `status-smoke` after synchronization fix |

# Handoff

Start with this task checkpoint, PR #384, `docs/agents/programs/E2E_AUTOMATION_PROGRAM.md`, merged PR #245, archived task `CAN-20260713-universal-agent-e2e-platform`, `tools/e2e/run_agent_load.py`, `tools/e2e/run_agent_load_runtime.py`, `.github/scripts/smoke_test_canary.py`, `src/server/network/protocol/protocolstatus.cpp`, and `src/server/network/protocol/protocolstatus.hpp`.

Do not create a second physical-client E2E orchestrator, do not modify OTClient for load generation, and do not describe status-protocol concurrency as equivalent to logged-in gameplay players.
