---
task_id: CAN-20260715-universal-agent-load-platform
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: ""
status: ready
agent: chatgpt-e2e-platform
branch: feat/universal-agent-load-platform-v2
base_branch: main
created: 2026-07-15T15:40:00+02:00
updated: 2026-07-16T08:52:00+02:00
last_verified_commit: 9f28610e4e8c107f7d8b2d9291ad6d9b8a4fc2ca
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
- [x] Current-head CI, ownership, load workflow and physical E2E pass on the last verified branch head.
- [x] Module catalogue/documentation/changelog impact is current.
- [ ] Autonomous merge gate satisfied on the final state-record head.

# Confirmed context

- Repository write target is exactly `blakinio/canary`; upstream repositories remain read-only.
- PR #393 remains the existing same-repository PR for branch `feat/universal-agent-load-platform-v2`; no competing task, branch or PR was created.
- Handed-off head `e0f8f957bf1c7b24c98f594eff86cf6674ab5191` matched the live pre-sync PR head.
- Main was integrated twice as it advanced: first through merge result `669c840950049d782cd56932d92ddb606eba030c` for `main@264a86b1eddf5f68666281c47489166f343c3e84`, then through merge result `b5d894ac58c2c66013cbba6296ebf7fc855a2547` for `main@0c0972526814f099b51fd3481f28331b9434446d`; both branch updates used `force: false`.
- The second synchronization overlapped only shared `CHANGELOG.md` and `MODULE_CATALOG.md`; PR #406 content was preserved first, then only this task's two documentation entries were reapplied.
- `E2E_AUTOMATION_PROGRAM.md` was reviewed and requires no contract change.
- On exact head `9f28610e4e8c107f7d8b2d9291ad6d9b8a4fc2ca`, Wheel #234, Ownership #1498, autofix #1499, CI #2634, Universal Agent Load #35 and Universal Agent E2E #77 all completed successfully.
- Universal Agent Load #35 passed without a rerun. Historical Load #34 had one Canary `SIGSEGV`/exit `-11`; one policy-allowed failed-jobs rerun passed on the same SHA, there was no second identical failure, and no speculative runtime patch was made.
- After the final green gate, `main` advanced by exactly two commits to `c32e42469f302ab108dea08d9b90164458696328`: OAM-002 target-baseline governance completion and lifecycle archival.
- Those two current-main commits touch only `docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md`, `docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md`, and the OAM-002 active/archive task paths; they do not overlap any of PR #393's 11 changed paths.
- Live PR recalculation against `main@c32e42469f302ab108dea08d9b90164458696328` reports PR #393 mergeable with exactly 11 intended changed paths and no submitted reviews or unresolved review threads.
- The available GitHub connector exposes no merge-branch/update-branch operation, and this task forbids synthesizing replacement branch history. Therefore the branch is not rewritten merely to absorb two disjoint governance commits; final delivery uses GitHub's normal squash merge against the current base if exact-head checks on this final state-record commit remain green and live mergeability remains true.
- This environment still has no mounted local Git checkout, so local `git status --short --branch`, `git branch -vv`, `git remote -v`, and `git worktree list` remain unavailable; no clean-working-tree claim is made.

# Current state

The implementation and documentation are ready for merge. Exact head `9f28610e4e8c107f7d8b2d9291ad6d9b8a4fc2ca` passed all six required workflow families. Current `main@c32e42469f302ab108dea08d9b90164458696328` is two disjoint Oteryn-governance commits ahead of the branch; GitHub recalculated PR #393 as mergeable against that current base, with the same 11 intended changed paths and no review blockers. This state-record commit is the final task-file mutation and must itself receive the required exact-head workflow gate before squash merge.

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| `9f28610e4e8c107f7d8b2d9291ad6d9b8a4fc2ca` | Wheel of Destiny Validation #234 | passed | exact-head |
| `9f28610e4e8c107f7d8b2d9291ad6d9b8a4fc2ca` | Agent Task Ownership #1498 | passed | exact-head |
| `9f28610e4e8c107f7d8b2d9291ad6d9b8a4fc2ca` | autofix.ci #1499 | passed | exact-head |
| `9f28610e4e8c107f7d8b2d9291ad6d9b8a4fc2ca` | Universal Agent Load #35 | passed | exact-head; no rerun required |
| `9f28610e4e8c107f7d8b2d9291ad6d9b8a4fc2ca` | CI #2634 | passed | exact-head |
| `9f28610e4e8c107f7d8b2d9291ad6d9b8a4fc2ca` | Universal Agent E2E #77 | passed | exact-head physical client login/relog |
| `9f28610e4e8c107f7d8b2d9291ad6d9b8a4fc2ca` | current-main overlap audit | passed | `main` advanced to `c32e42469f302ab108dea08d9b90164458696328`; two new commits are disjoint from all 11 PR paths |
| `9f28610e4e8c107f7d8b2d9291ad6d9b8a4fc2ca` | live PR/review gate | passed | GitHub reports mergeable; 11 intended paths; no reviews or unresolved review threads |

# Risks and compatibility

- Runtime: concurrent `ProtocolStatus` status traffic touches process-wide throttle state; preserve the narrow synchronization semantics already in the PR.
- Data/migration: no data or schema migration is part of this task.
- Security: load targets remain literal loopback only; do not expand to production or third-party hosts.
- Backward compatibility: status throttle semantics must not be weakened.
- Cross-repo rollout: none; OTClient remains read-only and unchanged.
- Rollback: PR is unmerged until the final state-record-head gate succeeds.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T08:52:00+02:00
head: 9f28610e4e8c107f7d8b2d9291ad6d9b8a4fc2ca
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
  - Main 0c0972526814f099b51fd3481f28331b9434446d was integrated without force through merge result b5d894ac58c2c66013cbba6296ebf7fc855a2547.
  - CHANGELOG and MODULE_CATALOG contain the Universal Agent Load entries while preserving PR 406 current-main content.
  - Wheel 234, Ownership 1498, autofix 1499, Universal Agent Load 35, CI 2634 and Universal Agent E2E 77 all passed on exact head 9f28610e4e8c107f7d8b2d9291ad6d9b8a4fc2ca.
  - Main later advanced exactly two commits to c32e42469f302ab108dea08d9b90164458696328.
  - The two new main commits touch only Oteryn governance and lifecycle paths and do not overlap any of PR 393's 11 changed paths.
  - GitHub recalculated PR 393 as mergeable against main c32e42469f302ab108dea08d9b90164458696328 with exactly 11 intended changed paths.
  - Live review inspection found no submitted reviews and no unresolved review threads.
derived:
  - The two post-gate main commits do not invalidate the task implementation or exact-head workflow evidence because they are path-disjoint governance-only changes.
  - A normal GitHub squash merge can combine the current base and PR head without rewriting the published task branch; this is preferable to synthesizing a branch merge commit when no merge-branch connector operation is available.
  - This final task-record commit requires exact-head workflow verification before merge because it changes the PR head.
unknown:
  - Local working-tree status and every uncommitted path in any checkout not mounted in this execution environment.
  - Final workflow conclusions on this state-record commit until GitHub Actions completes.
conflicts: []
first_failure:
  marker: Universal Agent Load 34 first attempt / Run exact-head loopback load profile
  evidence: Canary exited -11 during concurrent status requests; one policy-allowed failed-job rerun passed on the same SHA, with no second identical failure.
rejected_hypotheses:
  - The first Load 34 SIGSEGV proves a deterministic regression requiring an immediate speculative patch: one policy-allowed rerun passed on the same unchanged SHA and final Load 35 passed without rerun.
  - The two new main commits conflict with PR 393: their changed paths are limited to Oteryn governance and lifecycle records and do not overlap the PR's 11 paths.
  - The task branch must be rewritten or a synthetic merge commit must be created to absorb disjoint governance-only main commits: GitHub already reports the PR mergeable against the current base and normal squash delivery preserves current main.
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
  - command: Required workflow set on 9f28610e4e8c107f7d8b2d9291ad6d9b8a4fc2ca
    result: PASS
    evidence: Wheel 234, Ownership 1498, autofix 1499, Universal Agent Load 35, CI 2634 and Universal Agent E2E 77 completed successfully.
  - command: Current-main overlap and live PR gate on 9f28610e4e8c107f7d8b2d9291ad6d9b8a4fc2ca
    result: PASS
    evidence: Main c32e42469f302ab108dea08d9b90164458696328 is two path-disjoint Oteryn-governance commits ahead; PR remains mergeable with 11 intended paths and no review blockers.
blockers:
  - Exact-current-head required workflows must pass on this final state-record commit before squash merge.
next_action: Verify all required workflows on this final state-record head, then recheck current main, 11-path diff, mergeability and review state; if clean, squash-merge PR 393 with expected_head_sha and verify merged state.
```

# Handoff

The authoritative continuation state is the `## Context checkpoint` above. Do not reconstruct from chat history, create a competing task/branch/PR, modify OTClient, weaken throttles or load assertions, or bypass exact-current-head CI and review gates.
