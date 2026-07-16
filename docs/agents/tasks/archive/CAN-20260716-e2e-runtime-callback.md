---
task_id: CAN-20260716-e2e-runtime-callback
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-SEC-003-RUNTIME-HOOK
status: completed
agent: "GPT-5.5 Thinking"
branch: feat/e2e-runtime-callback
base_branch: main
created: 2026-07-16T23:12:00+02:00
updated: 2026-07-16T21:49:56Z
last_verified_commit: "44d8c97bdf1add97acba719a7342b712de5be1fb"
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
completed: 2026-07-16T21:49:56Z
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
- [x] Update the module catalogue narrowly and pass relevant implementation-head CI before final-gate validation.

# Confirmed context

- `blakinio/canary` is the only writable repository.
- PR #439 owns `tools/e2e/run_agent_e2e.py` and physical-client gameplay driver paths but does not own this task's paths.
- OAM-006 PR #436 merged as `c40b26ee9481ec99931347ba26897a785a7a38ca`; its five changed paths do not overlap this task. This task never modified `.github/workflows/universal-agent-e2e.yml`.
- `run_agent_load_runtime.py` already owned exact-head Canary startup, map/database/config preparation, online readiness, process-liveness verification and cleanup for Universal Agent Load.
- The accepted security-platform ADR requires runtime security work to reuse existing E2E/load lifecycle instead of creating a second security-specific launcher.
- PR #444 contains the callback implementation and focused isolated tests.
- Implementation/checkpoint head `3c64b33be097f97f1694a5ee13bafa4eaed1c5c6` passed Agent Task Ownership, repository CI and the complete Universal Agent Load workflow including exact-head Linux build, real loopback `status-smoke` and Required load validation.
- The only shared-index change is one reviewed `Universal Agent Load` row replacement in `docs/agents/MODULE_CATALOG.md`; no changelog entry was added.
- `ci:final-gate` was applied to PR #444 before this final readiness checkpoint commit.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T23:31:00+02:00
head: 0e346cbff1a0a3848fed589eea52d10af66f23d7
branch: feat/e2e-runtime-callback
pr: 444
status: ready
context_routes:
  - agent-governance
  - universal-e2e
owned_paths:
  - tools/e2e/run_agent_load_runtime.py
  - tests/e2e/test_load_runner.py
  - docs/agents/tasks/active/CAN-20260716-e2e-runtime-callback.md
  - docs/agents/MODULE_CATALOG.md
proven:
  - only blakinio/canary is writable
  - current task does not overlap PR 439 exclusive paths
  - OAM-006 PR 436 merged at c40b26ee9481ec99931347ba26897a785a7a38ca without touching this task's four changed paths
  - existing Universal Agent Load runtime owns the disposable Canary lifecycle needed by SEC-003
  - security platform ADR rejects a second security-specific full-stack launcher
  - run_runtime exposes that existing lifecycle to a code-owned in-process callback only after Canary reports online
  - RuntimeContext exposes resolved loopback runtime metadata and server evidence paths without manifest-provided commands executable paths or targets
  - focused tests cover callback context nonzero callback failure post-callback Canary exit detection cleanup/config restoration and the existing load command contract
  - Agent Task Ownership run 29535523253 passed on 3c64b33be097f97f1694a5ee13bafa4eaed1c5c6
  - CI run 29535523480 passed on 3c64b33be097f97f1694a5ee13bafa4eaed1c5c6
  - Universal Agent Load run 29535523351 passed Validate load platform exact-head Linux build real status-smoke and Required load validation on 3c64b33be097f97f1694a5ee13bafa4eaed1c5c6
  - PR diff contains exactly four intended paths and no workflow or security implementation change
  - MODULE_CATALOG patch is exactly one Universal Agent Load row replacement
  - ci:final-gate label was applied before this readiness checkpoint commit
derived:
  - this callback is the smallest reusable interface that lets SEC-003 execute a security-owned driver while Universal Agent Load remains the owner of disposable server lifecycle
  - malformed-packet execution can now remain security-owned without granting manifests arbitrary commands executables or network targets
unknown:
  - exact-final-head CI Ownership and Universal Agent Load results for the readiness commit created from this checkpoint
conflicts: []
first_failure:
  marker: Agent Task Ownership 1788 and 1789 / Validate changed active task checkpoints
  evidence: the initial checkpoint used an invalid empty first_failure mapping and the next revision omitted mandatory derived; both failures were governance-record schema errors and not implementation test failures
rejected_hypotheses:
  - duplicate the Universal E2E or Agent Load lifecycle inside tools/security
  - allow a scenario manifest to provide an arbitrary command executable or host
  - modify the Universal Agent E2E workflow while OAM-006 owned it
changed_paths:
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260716-e2e-runtime-callback.md
  - tools/e2e/run_agent_load_runtime.py
  - tests/e2e/test_load_runner.py
validation:
  - command: Agent Task Ownership run 29535523253
    result: PASS
    evidence: active checkpoint validation and ownership indexing passed on 3c64b33be097f97f1694a5ee13bafa4eaed1c5c6
  - command: CI run 29535523480
    result: PASS
    evidence: repository CI passed on the validated implementation/checkpoint head
  - command: Universal Agent Load run 29535523351
    result: PASS
    evidence: load-platform tests exact-head Canary Linux build real loopback status-smoke and Required load validation all passed
blockers: []
next_action: Run ci:final-gate workflows on this exact readiness head; if all required checks pass and PR 444 remains mergeable with the same four-file diff and no review blockers, mark it ready and squash-merge without any further commit.
```

## Automated lifecycle completion

- Feature PR: #444.
- Feature head: `a8ae4b5c9563e8e620a1bc466c4096d588c11fbd`.
- Merge commit: `44d8c97bdf1add97acba719a7342b712de5be1fb`.
- Merged at: `2026-07-16T21:49:56Z`.
- This record was moved from `tasks/active` by the post-merge lifecycle automation.
