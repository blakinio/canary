---
task_id: CAN-20260715-universal-agent-load-platform
program_id: CAN-PROGRAM-E2E-PLATFORM
status: implementing
agent: chatgpt-e2e-platform
branch: feat/universal-agent-load-platform-v2
base_branch: main
created: 2026-07-15T15:40:00+02:00
updated: 2026-07-15T19:21:26+02:00
last_verified_commit: f5cff58fa01d70cd7b67ac403f3d1eea3a78829a
risk: medium
related_issue: ""
related_pr: "393"
depends_on:
  - CAN-20260713-universal-agent-e2e-platform
blocks: []
owned_paths:
  exclusive:
    - .github/workflows/universal-agent-load.yml
    - tools/e2e/run_agent_load.py
    - tools/e2e/run_agent_load_runtime.py
    - tests/e2e/load/**
    - tests/e2e/test_load_runner.py
    - src/server/network/protocol/protocolstatus.cpp
    - docs/agents/tasks/active/CAN-20260715-universal-agent-load-platform.md
  shared:
    - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - src/server/network/protocol/protocolstatus.hpp
    - .github/scripts/smoke_test_canary.py
    - .github/workflows/universal-agent-e2e.yml
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/run_physical_e2e.sh
    - tools/e2e/client/**
    - tests/e2e/scenarios/login/**
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

This task does **not** claim to simulate authenticated gameplay players. It provides status/transport/control-plane regression and bounded capacity evidence without spawning hundreds of graphical OTClient processes.

# Acceptance criteria

- [x] Standard-library Python load runner sends the structurally correct Canary `status-xml` request over real TCP.
- [x] Targets are restricted to literal loopback addresses.
- [x] JSON profiles support bounded `load` and multi-stage `stress` modes.
- [x] Results include attempts, successes, failures, error rate, throughput, connect/round-trip P50/P95/P99/max, bytes and error breakdown.
- [x] Optional local Canary PID sampling reports peak RSS and process CPU percentage.
- [x] Gating `status-smoke` plus larger load/stress profiles exist.
- [x] Runtime adapter reuses `.github/scripts/smoke_test_canary.py` lifecycle helpers.
- [ ] Dedicated exact-head GitHub Actions load workflow passes on the replacement PR current head.
- [ ] Concurrent `ProtocolStatus` status queries remain crash-free on the replacement PR current head.
- [ ] Existing Universal Agent E2E `login/relog` passes unchanged on the replacement PR current head.
- [ ] Focused Python tests, bytecode compilation, repository CI and ownership pass on the current head.
- [x] No OTClient source change, upstream write, production target, binary map/client asset or gameplay behavior change.

# Proven protocol contract

`ServicePort::make_protocol()` consumes the first body byte as the service `PROTOCOL_IDENTIFIER`. `ProtocolStatus::onRecvFirstMessage()` then consumes the protocol opcode and reads four raw bytes `info`.

Canonical framed request:

```text
06 00 FF FF 69 6E 66 6F
```

The first `FF` selects `ProtocolStatus`; the second `FF` selects XML info inside `ProtocolStatus`.

# Evidence-backed runtime repair

Historical implementation work in superseded PR #384 produced a valid concurrent status run that exposed a real Canary `SIGSEGV`. The concrete shared state was process-wide `ProtocolStatus::ipConnectMap`, reached from network I/O callbacks without synchronization. The bounded repair serializes the existing throttle lookup/update critical section. It does not disable, relax or change throttle semantics.

Synthetic load profiles use distinct `127/8` source addresses so normal per-IP status throttles remain active. This is a loopback-only test technique and is not exposed as a production-target load tool.

# Replacement history

- Original implementation PR #384 accumulated 29 commits while `main` advanced through unrelated agent-context work.
- `main` reached `6b613b886092b7face057507d4dd903c39cd5e1b`; the only overlapping content path was `docs/agents/CHANGELOG.md`, producing a merge conflict and preventing a current merge-ref gate cycle.
- Published history was not force-rewritten because repository policy forbids plain force push.
- This replacement branch starts exactly from `main@6b613b886092b7face057507d4dd903c39cd5e1b` and reapplies only the bounded verified implementation.

# Historical evidence retained from PR #384

Verified old feature head `e6d59275201f746453c3db8943e09a2703a741e5`:

- CI #2495: pass.
- Agent Task Ownership #1369: pass.
- Universal Agent Load #16 (`29430993797`): pass; 100/100 requests, 0 failures, error rate `0.0`, P95 round trip `2.046 ms`, aggregate `5425.422` req/s on that GitHub-hosted runner, no fatal/crash evidence.
- Universal Agent E2E #58 (`29430996846`): pass with controlled OTClient `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`; two real logins, two safe logouts, two packet records, persistence confirmation, final online count `0`, client exit `0`, no fatal runtime logs.

Historical metrics are regression evidence only. They are not production capacity claims and do not replace current replacement-PR validation.

# Current plan

1. Reapply the bounded runner, runtime, profiles, focused tests, status-map synchronization, workflow and durable docs on current `main`.
2. Close PR #384 as superseded and open one clean replacement draft PR.
3. Set `related_pr` to the replacement PR and perform one final test-only update so current-head CI/load/physical E2E all run on the same head.
4. Repair only evidence-backed failures.
5. Review complete diff, comments/reviews/threads and current `main` delta; mark ready and squash-merge only after all gates are green.

# Handoff

Start with this task and the replacement PR. PR #384 is historical evidence only after replacement. Reuse the merged physical E2E platform; do not create a second physical-client orchestrator, modify OTClient for load generation, weaken server throttles to make a benchmark green, or describe status-protocol throughput as logged-in gameplay-player capacity.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-15T17:21:26Z
head: f5cff58fa01d70cd7b67ac403f3d1eea3a78829a
branch: feat/universal-agent-load-platform-v2
pr: 393
status: implementing
context_routes:
  - docs/agents/TASK_LIFECYCLE.md
  - docs/agents/CONTEXT_HANDOFF.md
owned_paths:
  - tools/e2e/run_agent_load_runtime.py
  - docs/agents/tasks/active/CAN-20260715-universal-agent-load-platform.md
proven:
  - PR 393 CI run 2517 passed on head 1820a6ef97f4ec00c5a3ac9523d517b00f2f5f52.
  - Universal Agent Load run 17 failed because initialize_database received an argparse Namespace without skip_database_init.
  - Agent Task Ownership run 1390 failed because this changed active task lacked a Context checkpoint section.
  - tools/e2e/run_agent_load_runtime.py now declares --skip-database-init with the smoke helper compatible default false behavior.
derived:
  - The two observed current-head blockers can be repaired without changing the physical E2E orchestrator or ProtocolStatus throttle semantics.
unknown:
  - Current-head results after the two blocker repairs.
  - Final result of Universal Agent E2E run 59 or its replacement run on the repaired head.
conflicts: []
first_failure:
  marker: Universal Agent Load / Run exact-head loopback load profile
  evidence: run 29434516961 job 87419272626 reported Namespace object has no attribute skip_database_init
rejected_hypotheses:
  - Load runner unit tests are broken: Validate load platform passed in Universal Agent Load run 17.
changed_paths:
  - tools/e2e/run_agent_load_runtime.py
  - docs/agents/tasks/active/CAN-20260715-universal-agent-load-platform.md
validation:
  - command: CI run 2517
    result: PASS
    evidence: GitHub Actions run 29434517022 on previous PR head 1820a6ef97f4ec00c5a3ac9523d517b00f2f5f52
  - command: Universal Agent Load run 17
    result: FAIL
    evidence: runtime adapter missing skip_database_init argument
  - command: Agent Task Ownership run 1390
    result: FAIL
    evidence: changed active task missing required Context checkpoint
blockers:
  - Re-run current-head PR checks after checkpoint commit and inspect any remaining evidence-backed failures.
next_action: Verify PR 393 current head checks and repair only the next first failing gate if one remains.
```
