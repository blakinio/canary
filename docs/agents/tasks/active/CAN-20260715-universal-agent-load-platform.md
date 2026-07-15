---
task_id: CAN-20260715-universal-agent-load-platform
program_id: CAN-PROGRAM-E2E-PLATFORM
status: implementing
agent: chatgpt-e2e-platform
branch: feat/universal-agent-load-platform
base_branch: main
created: 2026-07-15T15:40:00+02:00
updated: 2026-07-15T15:40:00+02:00
last_verified_commit: 63fbacc9ab2d31b480de9d756194e22ce22b7d35
risk: medium
related_issue: ""
related_pr: ""
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

Add one reusable, deterministic and loopback-only load/stress layer beside the merged physical-client E2E platform. The first bounded capability will exercise Canary's real TCP status protocol at controlled concurrency, collect latency/throughput/error and Canary CPU/RSS evidence, and retain the existing real-OTClient `login/relog` scenario as the correctness sentinel.

This task does **not** claim to simulate authenticated gameplay players. It establishes an honest transport/status-protocol capacity baseline that can scale cheaply without spawning hundreds of graphical OTClient processes.

# Acceptance criteria

- [ ] A standard-library Python load runner sends valid Canary `status-xml` requests over real TCP.
- [ ] Targets are restricted to loopback addresses so the tool cannot be pointed at production or third-party servers.
- [ ] JSON profiles support bounded `load` and multi-stage `stress` modes.
- [ ] Results include attempts, successes, failures, error rate, throughput, connect/round-trip P50/P95/P99/max, bytes received and error breakdown.
- [ ] When a local Canary PID is supplied, results include sampled peak RSS and process CPU percentage.
- [ ] A small gating `status-smoke` profile and larger load/stress example profiles are provided.
- [ ] The runtime reuses existing Canary smoke lifecycle helpers instead of creating a second database/map/config bootstrap implementation.
- [ ] A dedicated workflow builds the exact PR Canary head, runs the gating load profile against a disposable local database/server and uploads machine-readable evidence.
- [ ] Existing Universal Agent E2E `login/relog` remains unchanged and passes on the feature head.
- [ ] Focused unit tests and bytecode compilation pass.
- [ ] Current-head CI, ownership, load workflow and physical E2E checks pass before merge.
- [ ] No OTClient source change, upstream write, production host, credential, binary map asset or gameplay/protocol behavior change.

# Ownership and overlap

- Task-start main: `63fbacc9ab2d31b480de9d756194e22ce22b7d35`.
- The completed #245 platform task was archived by PR #382 before this task claimed E2E platform paths.
- Open PR #316 owns only Targuna donor-audit paths and does not overlap this task.
- Existing physical E2E orchestration and OTClient automation are read-only for this task.
- `ACTIVE_WORK.md` is not edited.

# Implementation plan

1. Add a loopback-only valid `ProtocolStatus` XML load generator and focused tests.
2. Add load/stress profile manifests with explicit gating policy.
3. Add a thin runtime adapter that reuses `.github/scripts/smoke_test_canary.py` lifecycle helpers and runs the load profile only after exact-head Canary is online.
4. Add a thin GitHub Actions workflow around the existing reusable Canary build and disposable database.
5. Run unit/compile checks, exact-head load proof and unchanged physical `login/relog` E2E.
6. Repair only evidence-backed CI/runtime failures, update durable docs, review the complete diff and merge after all gates are green.

# Work log

## 2026-07-15T15:40:00+02:00

- Changed: created a fresh platform task after archiving the stale completed #245 task ownership.
- Learned: Canary's existing `ProtocolStatus` XML request (`0xFF` + `info`, framed by the normal 2-byte body length) is a valid lightweight real-server request suitable for the first scalable load layer; localhost bypasses the status query throttle intended for remote IPs.
- Decision: the first load platform measures status/transport/control-plane capacity and explicitly does not claim authenticated-player capacity.
- Decision: existing physical `login/relog` E2E remains the correctness sentinel; no OTClient modification or multi-process client workaround.

# Validation

| Commit | Check | Result | Notes |
|---|---|---|---|
| pending | focused Python unit tests | pending | load runner/profile validation |
| pending | Python bytecode compilation | pending | runner + runtime adapter |
| pending | Universal Agent Load | pending | exact-head Canary `status-smoke` |
| pending | Universal Agent E2E | pending | unchanged physical `login/relog` |
| pending | CI / Required | pending | repository gate |
| pending | Agent Task Ownership | pending | path ownership gate |

# Handoff

Start with this task, `docs/agents/programs/E2E_AUTOMATION_PROGRAM.md`, merged PR #245, archived task `CAN-20260713-universal-agent-e2e-platform`, `tools/e2e/run_agent_e2e.py`, `tools/e2e/run_physical_e2e.sh`, `.github/scripts/smoke_test_canary.py`, and `src/server/network/protocol/protocolstatus.cpp`.

Do not create a second physical-client E2E orchestrator, do not modify OTClient for load generation, and do not describe status-protocol concurrency as equivalent to logged-in gameplay players.
