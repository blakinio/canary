---
program_id: CAN-PROGRAM-E2E-PLATFORM
name: Universal OTS E2E automation
status: active
owner: e2e-platform-agent
created: 2026-07-13T00:00:00+02:00
updated: 2026-07-15T16:50:00+02:00
last_verified_commit: 3eeb3a77f9be9dc6b509ba286c37c4381a793c3b
primary_paths:
  - tools/e2e/**
  - tests/e2e/**
shared_integration_paths:
  - .github/workflows/universal-agent-e2e.yml
  - .github/workflows/universal-agent-load.yml
related_programs:
  - CAN-PROGRAM-CYCLOPEDIA
  - CAN-PROGRAM-QUEST-AUDIT
  - CAN-PROGRAM-WHEEL-OF-DESTINY
  - CAN-PROGRAM-OTBM
cross_repo_contracts:
  - OTS-E2E-CANARY-OTCLIENT
---

# Mission

Maintain one reusable, disposable validation platform in which autonomous agents can run real Canary, a controlled real OTClient when correctness requires it, and bounded lightweight load generators when capacity/regression evidence requires scale.

The platform must collect machine-readable evidence and clean up without touching production systems. Feature programs consume the common platform; they do not own or duplicate it.

# Current platform state

The physical-client foundation is merged through PR #245 and provides:

- validated JSON scenario discovery and resolution;
- exact-head Canary execution against a disposable database;
- one controlled pinned OTClient process;
- real login, stable world entry, safe logout and same-process relog;
- packet records, SQL state, screenshots, client/server logs and machine-readable result artifacts;
- a `login/relog` compatibility baseline that every generic platform change must preserve.

PR #384 adds a separate load/stress layer for inexpensive concurrency evidence without spawning hundreds of graphical clients. The first supported protocol is Canary `status-xml` over real TCP.

These layers have different proof scopes:

- **Physical E2E** proves real maintained-client compatibility and end-to-end lifecycle behavior.
- **Load/stress** proves bounded server transport/status-path behavior and performance under synthetic concurrent requests.
- A load result is **not** evidence for authenticated gameplay-player capacity unless the profile actually implements and proves the full authenticated gameplay lifecycle.

# Reusable foundations

The repository already contains reusable pieces that must be extended rather than replaced:

- `.github/scripts/smoke_test_canary.py` owns the reusable disposable database/config/map/server lifecycle used by the load runtime adapter;
- `tools/e2e/run_agent_e2e.py` resolves physical E2E scenarios;
- `tools/e2e/run_physical_e2e.sh` owns the real Canary + OTClient physical orchestration;
- `tools/e2e/run_agent_load.py` owns bounded loopback load/stress profile execution and metrics;
- `tools/e2e/run_agent_load_runtime.py` starts exact-head Canary through the existing smoke lifecycle and executes one load profile;
- `.github/workflows/universal-agent-e2e.yml` is the canonical physical-client workflow;
- `.github/workflows/universal-agent-load.yml` is the canonical exact-head load workflow;
- deterministic test accounts/characters remain under `docker/data/**`;
- controlled OTClient source remains user-owned and revision-pinned; upstream OpenTibiaBR repositories stay read-only.

# Platform responsibility

The E2E platform owns reusable infrastructure for:

- disposable MariaDB/MySQL bootstrap, schema import, fixture loading and teardown;
- Canary artifact resolution or local build, isolated configuration, startup, readiness and shutdown;
- map/client asset acquisition with hashes and no committed binary assets;
- controlled OTClient artifact resolution or build from a pinned user-owned revision;
- deterministic account, character, host, port and version configuration;
- login, logout, relog, timeout, crash and cleanup handling;
- stable scenario/profile APIs and generic runners;
- SQL assertions, protocol-event assertions, screenshots, logs, traces and machine-readable results;
- bounded load/stress profiles with explicit gate policy and latency/throughput/error metrics;
- optional exact-process CPU/RSS sampling for local Canary;
- local-safe execution and reusable GitHub Actions execution.

The platform must not encode feature-specific gameplay values or call a transport/status benchmark a gameplay-player benchmark.

# Physical scenario contract

Each physical scenario must define:

- unique scenario ID and owning program;
- required server/client versions and capabilities;
- database and character fixture requirements;
- repeat-safe setup steps;
- client actions or protocol requests;
- observable server, client, UI and SQL assertions;
- relog or persistence checks when relevant;
- timeout and failure markers;
- artifacts to retain;
- cleanup requirements;
- paths the feature task may and may not edit.

Feature programs own their scenario definitions, fixtures and assertions. Generic orchestration changes require a separate platform task.

# Load/stress contract

The canonical load runner is `tools/e2e/run_agent_load.py`.

A load profile must declare:

- schema version, stable profile ID and `load` or `stress` mode;
- supported protocol (`status-xml` in the current implementation);
- a literal loopback target only;
- gate policy and process-sampling interval;
- source-IP strategy;
- one or more bounded stages with request count, concurrency, timeout and explicit thresholds.

Current bundled profiles use `source_ip_strategy: unique-loopback-v4`. Each logical client binds to a distinct address in `127/8`. This keeps traffic local while allowing the server's normal per-IP anti-abuse and status-query throttles to remain unchanged. The harness must never disable or weaken those production policies merely to make a benchmark green.

The result contract includes:

- attempts, successes, failures and error rate;
- throughput;
- bytes received;
- connect and round-trip P50/P95/P99/max latency;
- error breakdown;
- per-stage threshold evaluation;
- optional Canary PID, sampled peak RSS and CPU percentage.

CI runner numbers are regression evidence for the exact runner/environment and are not absolute capacity claims.

# Evidence-backed runtime repair

The first concurrent real `status-xml` run exposed a Canary `SIGSEGV` in the status path. `ProtocolStatus::ipConnectMap` is process-wide mutable state reached from multiple network I/O threads. PR #384 serializes the existing throttle check/update critical section without changing throttle policy.

The follow-up real run then proved that the server's separate `Ban::acceptConnection()` anti-flood rule intentionally admits only a small rapid burst per source IP. The load harness therefore uses distinct loopback source identities instead of modifying the server limiter.

# Interface-change rule

When a feature needs a new generic capability:

1. record the missing capability and proposed interface in the feature task;
2. create a bounded E2E-platform task with explicit ownership;
3. extend the existing runner/orchestrator rather than copying it;
4. add focused tests and real workflow evidence;
5. keep feature-specific expected values in the feature suite;
6. preserve the physical `login/relog` sentinel for generic platform/runtime changes;
7. use the cross-repository coordination contract for any controlled-client change.

# Safety invariants

- no production credentials, database, host or irreversible external action;
- load targets are literal loopback addresses only;
- no committed Tibia assets, downloaded OTBM files, database dumps or secrets;
- every run uses a disposable environment and attempts cleanup;
- external binaries/assets are pinned or hash-recorded;
- failures retain phase-specific machine-readable evidence;
- feature PRs never silently modify shared platform lifecycle behavior;
- no OTClient source modification to make a Canary test pass;
- no artificial relog delays, retries or multi-process workaround for the physical baseline;
- no E2E/load success claim without a verified real workflow result on the relevant head.

# Handoff

## Start here

Read `AGENTS.md`, `docs/agents/README.md`, this program record, the current active E2E task, archived `CAN-20260713-universal-agent-e2e-platform`, `tools/e2e/run_agent_e2e.py`, `tools/e2e/run_physical_e2e.sh`, `tools/e2e/run_agent_load.py`, `tools/e2e/run_agent_load_runtime.py`, and the two universal E2E/load workflows.

## Do not repeat

- Do not create a second physical-client E2E orchestrator.
- Do not create one complete workflow per feature.
- Do not use upstream OpenTibiaBR repositories as writable targets.
- Do not commit client assets or map binaries.
- Do not replace the existing smoke lifecycle without evidence it cannot be reused.
- Do not weaken server anti-abuse limits to make a local load test pass.
- Do not describe status-protocol concurrency as logged-in gameplay-player capacity.
