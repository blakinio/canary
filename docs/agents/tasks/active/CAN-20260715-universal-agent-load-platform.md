---
task_id: CAN-20260715-universal-agent-load-platform
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: ""
status: ready
agent: chatgpt-e2e-platform
branch: feat/universal-agent-load-platform-v2
base_branch: main
created: 2026-07-15T15:40:00+02:00
updated: 2026-07-16T01:42:00+02:00
last_verified_commit: 049989273ab883eadc70f05828d25274a8a335e7
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

Add a reusable loopback-only load/stress layer beside the merged physical-client E2E platform, while preserving the existing real-OTClient login/relog scenario as the correctness sentinel.

# Acceptance criteria

- [x] Loopback-only status protocol runner and bounded profiles exist.
- [x] Runtime adapter reuses existing Canary smoke lifecycle helpers.
- [x] Focused runner tests exist.
- [x] No OTClient source change or upstream write.
- [x] Current-main CI, ownership, load workflow and physical E2E pass on the last verified branch head.
- [x] Module catalogue/documentation/changelog impact is current.
- [ ] Autonomous merge gate satisfied on the readiness-checkpoint head.

# Confirmed context

- Repository write target is exactly `blakinio/canary`; upstream repositories remain read-only.
- PR #393 remains the existing same-repository PR for branch `feat/universal-agent-load-platform-v2`; no competing task, branch or PR was created.
- Handed-off head `e0f8f957bf1c7b24c98f594eff86cf6674ab5191` matched the live pre-sync PR head.
- Main was integrated twice as it advanced: first through merge result `669c840950049d782cd56932d92ddb606eba030c` for `main@264a86b1eddf5f68666281c47489166f343c3e84`, then through merge result `b5d894ac58c2c66013cbba6296ebf7fc855a2547` for current `main@0c0972526814f099b51fd3481f28331b9434446d`; both branch updates used `force: false`.
- The second synchronization overlapped only shared `CHANGELOG.md` and `MODULE_CATALOG.md`; current-main PR #406 content was preserved first, then only this task's two documentation entries were reapplied.
- `E2E_AUTOMATION_PROGRAM.md` was reviewed and requires no contract change.
- On exact head `049989273ab883eadc70f05828d25274a8a335e7`, Wheel #233, Ownership #1488, autofix #1492, CI #2623, Universal Agent Load #34 and Universal Agent E2E #76 all completed successfully.
- Universal Agent Load #34 initially observed one Canary `SIGSEGV`/exit `-11` during concurrent status requests; the runtime code was unchanged from an earlier fully green head, so one failed-jobs rerun was used under policy and passed on the same SHA. There was no second identical failure and no speculative runtime patch was made.
- Live verification after those checks showed `main` still exactly `0c0972526814f099b51fd3481f28331b9434446d`, PR #393 mergeable, 11 intended changed paths, and no unresolved review threads.
- This environment still has no mounted local Git checkout, so local `git status --short --branch`, `git branch -vv`, `git remote -v`, and `git worktree list` remain unavailable; no clean-working-tree claim is made.

# Current state

The task is ready. Implementation, current-main synchronization, documentation, exact-head CI/load/E2E evidence and live review state are satisfied on last verified head `049989273ab883eadc70f05828d25274a8a335e7`. This readiness checkpoint is the final task-record update; its resulting commit must receive the same required exact-head checks and remain current with `main` before squash merge.

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| `049989273ab883eadc70f05828d25274a8a335e7` | Wheel of Destiny Validation #233 | passed | exact-head |
| `049989273ab883eadc70f05828d25274a8a335e7` | Agent Task Ownership #1488 | passed | exact-head |
| `049989273ab883eadc70f05828d25274a8a335e7` | autofix.ci #1492 | passed | exact-head |
| `049989273ab883eadc70f05828d25274a8a335e7` | Universal Agent Load #34 | passed | first load attempt crashed Canary with exit `-11`; one policy-allowed failed-job rerun passed on the same SHA |
| `049989273ab883eadc70f05828d25274a8a335e7` | CI #2623 | passed | exact-head |
| `049989273ab883eadc70f05828d25274a8a335e7` | Universal Agent E2E #76 | passed | exact-head physical client login/relog |
| `049989273ab883eadc70f05828d25274a8a335e7` | current-main ancestry | passed | `main` remained `0c0972526814f099b51fd3481f28331b9434446d` |
| `049989273ab883eadc70f05828d25274a8a335e7` | live PR/review gate | passed | mergeable; 11 intended paths; no unresolved review threads |

# Risks and compatibility

- Runtime: concurrent `ProtocolStatus` status traffic touches process-wide throttle state; preserve the narrow synchronization semantics already in the PR.
- Data/migration: no data or schema migration is part of this task.
- Security: load targets remain literal loopback only; do not expand to production or third-party hosts.
- Backward compatibility: status throttle semantics must not be weakened.
- Cross-repo rollout: none; OTClient remains read-only and unchanged.
- Rollback: PR is unmerged until the final readiness-head gate succeeds.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T01:42:00+02:00
head: 049989273ab883eadc70f05828d25274a8a335e7
branch: feat/universal-agent-load-platform-v2
pr: 393
status: ready
context_routes:
  - agent-governance
  - universal-e2e
  - cpp-runtime
  - ci-repair
owned_paths:
  - .github/workflows/universal-agent-load.yml
  - tools/e2e/run_agent_load.py
  - tools/e2e/run_agent_load_runtime.py
  - tests/e2e/load/**
  - tests/e2e/test_load_runner.py
  - src/server/network/protocol/protocolstatus.cpp
  - docs/agents/tasks/active/CAN-20260715-universal-agent-load-platform.md
  - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - Repository write target is exactly blakinio/canary.
  - Live task branch is feat/universal-agent-load-platform-v2 and PR is 393.
  - Current main is 0c0972526814f099b51fd3481f28331b9434446d and was integrated without force through merge result b5d894ac58c2c66013cbba6296ebf7fc855a2547.
  - Current-main PR 406 shared documentation was preserved during conflict resolution.
  - CHANGELOG and MODULE_CATALOG contain the Universal Agent Load entries on top of current-main content.
  - Wheel 233, Ownership 1488, autofix 1492, Universal Agent Load 34, CI 2623 and Universal Agent E2E 76 all passed on exact head 049989273ab883eadc70f05828d25274a8a335e7.
  - Load 34 required one failed-job rerun after a single Canary SIGSEGV exit -11; the rerun passed on the same SHA and no second identical failure occurred.
  - Main remained 0c0972526814f099b51fd3481f28331b9434446d after the exact-head gate.
  - PR 393 was mergeable with 11 intended changed paths and no unresolved review threads after the exact-head gate.
derived:
  - Implementation, documentation, branch freshness and review requirements are satisfied on the last verified head.
  - The readiness checkpoint commit itself requires exact-current-head workflow verification before squash merge because it changes the PR head.
unknown:
  - Local working-tree status and every uncommitted path in any checkout not mounted in this execution environment.
  - Final workflow conclusions on the readiness-checkpoint commit until GitHub Actions completes.
conflicts: []
first_failure:
  marker: Universal Agent Load 34 first attempt / Run exact-head loopback load profile
  evidence: Canary exited -11 during concurrent status requests; one failed-job rerun passed on the same SHA, with no second identical failure.
rejected_hypotheses:
  - The first Load 34 SIGSEGV proves a deterministic regression requiring an immediate speculative patch: one policy-allowed rerun passed on the same unchanged SHA and there was no second identical failure.
  - PR 406 conflicts with load implementation paths: overlap was limited to shared CHANGELOG and MODULE_CATALOG entries and was resolved by preserving current-main content first.
  - Historical green checks alone satisfy the readiness-checkpoint head gate: this final task-record commit changes the head and must be reverified.
changed_paths:
  - .github/workflows/universal-agent-load.yml
  - docs/agents/CHANGELOG.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260715-universal-agent-load-platform.md
  - src/server/network/protocol/protocolstatus.cpp
  - tests/e2e/load/status-load.json
  - tests/e2e/load/status-smoke.json
  - tests/e2e/load/status-stress.json
  - tests/e2e/test_load_runner.py
  - tools/e2e/run_agent_load.py
  - tools/e2e/run_agent_load_runtime.py
validation:
  - command: Required workflow set on 049989273ab883eadc70f05828d25274a8a335e7
    result: PASS
    evidence: Wheel 233, Ownership 1488, autofix 1492, Universal Agent Load 34, CI 2623 and Universal Agent E2E 76 completed successfully.
  - command: Current-main and live PR gate on 049989273ab883eadc70f05828d25274a8a335e7
    result: PASS
    evidence: Main remained 0c0972526814f099b51fd3481f28331b9434446d; PR was mergeable with 11 intended paths and no unresolved review threads.
blockers: []
next_action: Verify all required workflows, current-main ancestry, intended changed-file list, mergeability and review state on this readiness-checkpoint commit; if all pass, squash-merge PR 393 with expected_head_sha and verify the merged PR state.
```

# Handoff

The authoritative continuation state is the `## Context checkpoint` above. Do not reconstruct from chat history, create a competing task/branch/PR, modify OTClient, weaken throttles or load assertions, or bypass exact-current-head CI and review gates.
