---
task_id: CAN-20260716-e2e-runtime-callback
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-SEC-003-RUNTIME-HOOK
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/e2e-runtime-callback
base_branch: main
created: 2026-07-16T23:12:00+02:00
updated: 2026-07-16T23:17:00+02:00
last_verified_commit: "bf3ebd8c320f10c6012aaaf9ff8e3862cf110022"
risk: medium
related_issue: ""
related_pr: "444"
depends_on:
  - CAN-PROGRAM-E2E-PLATFORM
blocks:
  - OTS-SEC-003 malformed packet and parser runtime scenarios
owned_paths:
  exclusive:
    - tools/e2e/run_agent_load_runtime.py
    - tests/e2e/test_load_runner.py
    - docs/agents/tasks/active/CAN-20260716-e2e-runtime-callback.md
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - .github/workflows/universal-agent-load.yml
    - .github/workflows/universal-agent-e2e.yml
    - tools/security/**
    - tests/security/**
modules_touched:
  - Universal Agent Load
reuses:
  - .github/scripts/smoke_test_canary.py
  - existing run_agent_load_runtime.py server/database/config lifecycle
public_interfaces:
  - code-owned Python callback API for running one bounded executor inside the existing local Canary runtime lifecycle
cross_repo_tasks: []
---

# Goal

Expose the already-existing Universal Agent Load local Canary lifecycle as a small code-owned Python callback API so bounded consumers such as OTS-SEC-003 can run a reviewed in-repository executor after disposable Canary startup without copying server/database/config lifecycle and without adding arbitrary command execution to manifests.

# Acceptance criteria

- [x] Preserve the existing `run_agent_load_runtime.py` CLI behavior and load-profile result contract.
- [x] Add a typed runtime context containing only resolved runtime paths, configured loopback ports, server PID and server log paths.
- [x] Add a Python callback entry point that owns the existing map/database/config/startup/cleanup lifecycle and invokes one caller-supplied in-process callable only after Canary reports online.
- [x] Verify Canary remains alive after the callback returns successfully.
- [x] Preserve config restoration and process cleanup on success and failure.
- [x] Do not add manifest-provided commands, executable paths, hosts or public-target selection.
- [x] Add focused tests for callback invocation, callback failure propagation, server-exit detection and cleanup/config restoration without requiring a real Canary binary.
- [x] Keep Universal Agent Load CLI backward compatible.
- [ ] Update the module catalogue narrowly and pass relevant CI before merge.

# Confirmed context

- `blakinio/canary` is the only writable repository.
- Open PR #439 owns `tools/e2e/run_agent_e2e.py` and physical-client gameplay driver paths but does not own this task's paths.
- Open PR #436 owns `.github/workflows/universal-agent-e2e.yml`; this task keeps that workflow read-only.
- `run_agent_load_runtime.py` already owns exact-head Canary startup, map/database/config preparation, online readiness, process-liveness verification and cleanup for Universal Agent Load.
- The accepted security-platform ADR requires runtime security work to reuse existing E2E/load lifecycle instead of creating a second security-specific launcher.
- PR #444 contains the callback implementation and focused isolated tests on implementation head `bf3ebd8c320f10c6012aaaf9ff8e3862cf110022`.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T23:17:00+02:00
head: bf3ebd8c320f10c6012aaaf9ff8e3862cf110022
branch: feat/e2e-runtime-callback
pr: 444
status: implementing
context_routes:
  - agent-governance
  - universal-e2e
owned_paths:
  - tools/e2e/run_agent_load_runtime.py
  - tests/e2e/test_load_runner.py
  - docs/agents/tasks/active/CAN-20260716-e2e-runtime-callback.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - only blakinio/canary is writable
  - current task does not overlap PR 439 exclusive paths
  - current task keeps PR 436 shared workflow path read-only
  - existing Universal Agent Load runtime already owns disposable Canary lifecycle needed by SEC-003
  - security platform ADR rejects a second security-specific full-stack launcher
  - run_runtime now exposes the existing lifecycle to a code-owned in-process callback after Canary reports online
  - RuntimeContext exposes resolved loopback runtime metadata and server evidence paths without manifest-provided commands or targets
  - focused tests cover callback context, nonzero callback failure, post-callback Canary exit detection, cleanup/config restoration and the existing load command contract
unknown:
  - exact Universal Agent Load and repository CI result on the repaired checkpoint head
conflicts: []
first_failure:
  marker: Agent Task Ownership 1788 / Validate changed active task checkpoints
  evidence: initial checkpoint encoded first_failure as an empty inline mapping; ownership validation requires the explicit marker/evidence mapping contract and the task record was corrected in this commit
rejected_hypotheses:
  - duplicate the Universal E2E or Agent Load lifecycle inside tools/security
  - allow a scenario manifest to provide an arbitrary command or executable
changed_paths:
  - docs/agents/tasks/active/CAN-20260716-e2e-runtime-callback.md
  - tools/e2e/run_agent_load_runtime.py
  - tests/e2e/test_load_runner.py
validation:
  - command: Agent Task Ownership run 29535275811
    result: FAIL
    evidence: implementation tests completed but checkpoint validation rejected the initial first_failure shape before ownership indexing
blockers: []
next_action: Inspect Universal Agent Load and CI on the repaired checkpoint head, then update shared module/changelog documentation from current main and complete exact-final-head validation.
```
