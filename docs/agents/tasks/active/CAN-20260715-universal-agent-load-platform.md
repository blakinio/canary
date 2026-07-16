---
task_id: CAN-20260715-universal-agent-load-platform
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: ""
status: ready
agent: chatgpt-e2e-platform
branch: feat/universal-agent-load-platform-v2
base_branch: main
created: 2026-07-15T15:40:00+02:00
updated: 2026-07-16T09:27:00+02:00
last_verified_commit: 79d81a276d9e597420b13a76126ce232087dc3b2
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
- [x] Module catalogue/documentation/changelog impact is current with latest main lifecycle state.
- [ ] Autonomous merge gate satisfied on the final checkpoint head.

# Confirmed context

- Repository write target is exactly `blakinio/canary`; upstream repositories remain read-only.
- PR #393 remains the existing same-repository PR for branch `feat/universal-agent-load-platform-v2`; no competing task, branch or PR was created.
- Handed-off head `e0f8f957bf1c7b24c98f594eff86cf6674ab5191` matched the live pre-sync PR head.
- Main was integrated twice as it advanced: first through merge result `669c840950049d782cd56932d92ddb606eba030c` for `main@264a86b1eddf5f68666281c47489166f343c3e84`, then through merge result `b5d894ac58c2c66013cbba6296ebf7fc855a2547` for `main@0c0972526814f099b51fd3481f28331b9434446d`; both branch updates used `force: false`.
- `E2E_AUTOMATION_PROGRAM.md` was reviewed and requires no contract change.
- Exact head `79d81a276d9e597420b13a76126ce232087dc3b2` passed Wheel #235, Ownership #1506, autofix #1500, CI #2641, Universal Agent Load #36 and Universal Agent E2E #78. Load #36 passed the real `status-smoke` job without rerun.
- Historical Load #34 had one Canary `SIGSEGV`/exit `-11`; one policy-allowed failed-jobs rerun passed on the same SHA, there was no second identical failure, and later Load #35 and #36 both passed without rerun, so no speculative runtime patch was made.
- Main later advanced through OAM-002 governance commits to `c32e42469f302ab108dea08d9b90164458696328`; those changes were path-disjoint from PR #393.
- Main then advanced two more commits to `8950a275e258ccc0f1a6781c9ff9c8ea089210a0`: PR #406 lifecycle status was marked merged and its task archived. This overlapped the shared `docs/agents/MODULE_CATALOG.md` path.
- The shared catalogue overlap was resolved conservatively in commit `39a1f24fd8d7629c13eb4891878adf454d7a321d`: current-main `OTBM real-map repair preflight | merged (#406)` state was preserved, while only the Universal Agent Load row and this task's review date remain as PR #393 catalogue changes.
- The PR still contains exactly 11 intended changed paths. No OTClient source, upstream repository, OTBM/map binary, client asset, generated report or render was added.
- The available GitHub connector exposes no merge-branch/update-branch operation, and this task forbids synthesizing replacement branch history. Current-main lifecycle changes are therefore preserved in shared docs and final delivery uses GitHub's normal squash merge against the current base once this checkpoint commit receives exact-head checks and live mergeability/review state is reverified.
- This environment still has no mounted local Git checkout, so local `git status --short --branch`, `git branch -vv`, `git remote -v`, and `git worktree list` remain unavailable; no clean-working-tree claim is made.

# Current state

The implementation and required documentation are ready for merge and incorporate the latest shared catalogue lifecycle state from `main@8950a275e258ccc0f1a6781c9ff9c8ea089210a0`. Exact head `79d81a276d9e597420b13a76126ce232087dc3b2` passed all six required workflow families. The catalogue-resolution commit `39a1f24fd8d7629c13eb4891878adf454d7a321d` changed only the shared module catalogue; this checkpoint is the final task-file mutation. Its resulting head must receive the required exact-head workflow gate, after which current main, the 11-path diff, mergeability and review state are rechecked immediately before squash merge.

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| `79d81a276d9e597420b13a76126ce232087dc3b2` | Wheel of Destiny Validation #235 | passed | exact-head |
| `79d81a276d9e597420b13a76126ce232087dc3b2` | Agent Task Ownership #1506 | passed | exact-head |
| `79d81a276d9e597420b13a76126ce232087dc3b2` | autofix.ci #1500 | passed | exact-head |
| `79d81a276d9e597420b13a76126ce232087dc3b2` | Universal Agent Load #36 | passed | exact-head status-smoke; no rerun required |
| `79d81a276d9e597420b13a76126ce232087dc3b2` | CI #2641 | passed | exact-head |
| `79d81a276d9e597420b13a76126ce232087dc3b2` | Universal Agent E2E #78 | passed | exact-head physical client login/relog |
| `39a1f24fd8d7629c13eb4891878adf454d7a321d` | latest-main shared catalogue preservation | passed | branch preserves `OTBM real-map repair preflight` as merged (#406) and retains Universal Agent Load row |
| `39a1f24fd8d7629c13eb4891878adf454d7a321d` | changed-file scope | passed | PR changed-file list remains exactly 11 intended paths |

# Risks and compatibility

- Runtime: concurrent `ProtocolStatus` status traffic touches process-wide throttle state; preserve the narrow synchronization semantics already in the PR.
- Data/migration: no data or schema migration is part of this task.
- Security: load targets remain literal loopback only; do not expand to production or third-party hosts.
- Backward compatibility: status throttle semantics must not be weakened.
- Cross-repo rollout: none; OTClient remains read-only and unchanged.
- Rollback: PR is unmerged until the final checkpoint-head gate succeeds.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T09:27:00+02:00
head: 39a1f24fd8d7629c13eb4891878adf454d7a321d
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
  - CHANGELOG and MODULE_CATALOG contain the Universal Agent Load entries.
  - Wheel 235, Ownership 1506, autofix 1500, Universal Agent Load 36, CI 2641 and Universal Agent E2E 78 all passed on exact head 79d81a276d9e597420b13a76126ce232087dc3b2.
  - Main advanced to 8950a275e258ccc0f1a6781c9ff9c8ea089210a0 through OAM-002 and PR 406 lifecycle documentation changes.
  - The latest shared MODULE_CATALOG overlap was resolved by preserving current-main OTBM preflight merged status and reapplying only the Universal Agent Load row plus review date.
  - PR 393 changed-file list remains exactly 11 intended paths.
derived:
  - Latest-main OTBM lifecycle documentation is no longer a content conflict in the final branch tree.
  - The final checkpoint commit requires exact-head workflow verification because it changes the PR head.
  - If current main advances again only through non-overlapping paths and GitHub reports the PR mergeable, normal squash merge preserves those base changes without synthesizing branch history.
unknown:
  - Local working-tree status and every uncommitted path in any checkout not mounted in this execution environment.
  - Final workflow conclusions on this checkpoint commit until GitHub Actions completes.
  - Live mergeability and review state immediately before squash merge.
conflicts: []
first_failure:
  marker: Universal Agent Load 34 first attempt / Run exact-head loopback load profile
  evidence: Canary exited -11 during concurrent status requests; one policy-allowed failed-job rerun passed on the same SHA, with no second identical failure; later Load 35 and 36 passed without rerun.
rejected_hypotheses:
  - The historical Load 34 SIGSEGV proves a deterministic regression requiring a speculative patch: the policy-allowed rerun passed and two later exact-head load workflows passed without rerun.
  - Latest main may be ignored because final CI was green: main changed shared MODULE_CATALOG lifecycle state, so the branch catalogue was explicitly reconciled before merge.
  - PR 406 must remain active in the catalogue to preserve PR 393 history: current-main lifecycle state is authoritative and is preserved as merged (#406).
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
  - command: Required workflow set on 79d81a276d9e597420b13a76126ce232087dc3b2
    result: PASS
    evidence: Wheel 235, Ownership 1506, autofix 1500, Universal Agent Load 36, CI 2641 and Universal Agent E2E 78 completed successfully.
  - command: Latest-main shared catalogue preservation on 39a1f24fd8d7629c13eb4891878adf454d7a321d
    result: PASS
    evidence: OTBM real-map repair preflight remains merged (#406), Universal Agent Load row remains present, and PR scope remains 11 intended paths.
blockers:
  - Exact-current-head required workflows must pass on this final checkpoint commit before squash merge.
next_action: Verify all required workflows on this final checkpoint head, then atomically recheck current main, 11-path diff, mergeability and review state; if clean, squash-merge PR 393 with expected_head_sha and verify merged state.
```

# Handoff

The authoritative continuation state is the `## Context checkpoint` above. Do not reconstruct from chat history, create a competing task/branch/PR, modify OTClient, weaken throttles or load assertions, or bypass exact-current-head CI and review gates.
