---
task_id: CAN-20260715-universal-agent-load-platform
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: ""
status: blocked
agent: chatgpt-e2e-platform
branch: feat/universal-agent-load-platform-v2
base_branch: main
created: 2026-07-15T15:40:00+02:00
updated: 2026-07-15T21:48:37Z
last_verified_commit: dd6ec4b32c198fe11213909d5aba9acd3826b39b
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
- [ ] Current-main CI, ownership, load workflow and physical E2E pass.
- [ ] Module catalogue/documentation/changelog impact is current on the final branch head.
- [ ] Autonomous merge gate satisfied.

# Confirmed context

- Repository write target is exactly `blakinio/canary`; upstream repositories remain read-only.
- Active PR is #393 in `blakinio/canary`, base `main`, head repository `blakinio/canary`.
- GitHub PR branch is `feat/universal-agent-load-platform-v2` and the verified pre-checkpoint PR head is `dd6ec4b32c198fe11213909d5aba9acd3826b39b`.
- Current `main` is `264a86b1eddf5f68666281c47489166f343c3e84`.
- Comparing current main to `dd6ec4b32c198fe11213909d5aba9acd3826b39b` reports `diverged`, `ahead_by: 12`, `behind_by: 11`, merge base `6b613b886092b7face057507d4dd903c39cd5e1b`.
- PR #384 is closed without merge and is historical evidence only.
- This execution environment has no mounted local Git worktree for `blakinio/canary`. Local `git status --short --branch`, local branch/HEAD, and every local uncommitted path are therefore not inspectable; no clean-working-tree claim is made.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| Universal physical-client E2E | unchanged correctness sentinel | merged PR #245; `.github/workflows/universal-agent-e2e.yml`; `tools/e2e/run_physical_e2e.sh` | Avoids a second physical-client orchestrator. |
| Canary smoke lifecycle helpers | imported/reused by load runtime | `.github/scripts/smoke_test_canary.py` | Reuses existing DB/config/map/server lifecycle. |
| ProtocolStatus XML info path | real bounded load target | `src/server/network/protocol/protocolstatus.cpp` | Exercises real loopback TCP status/control-plane traffic without claiming gameplay-player capacity. |

# Ownership and overlap check

- Program record: `CAN-PROGRAM-E2E-PLATFORM`.
- Open PRs inspected narrowly: exact task-ID search returns only PR #393; open-PR searches for `protocolstatus.cpp` and `universal-agent-load.yml` returned no competing PR.
- Active task: this record; no duplicate task was created.
- Ownership checker: Agent Task Ownership #1447 passed on exact head `dd6ec4b32c198fe11213909d5aba9acd3826b39b` (run `29452771339`).
- Exclusive claims: load workflow/runner/runtime/profiles/tests, `ProtocolStatus` synchronization implementation, this task record.
- Shared claims: E2E program record, module catalogue, changelog.
- Read-only dependencies: existing physical E2E/client automation and smoke lifecycle helper.
- Overlaps: no active ownership overlap is proven on exact head `dd6ec4b32c198fe11213909d5aba9acd3826b39b`.
- Resolution: branch remains 11 commits behind current main, so ownership and all merge gates must be re-established after normal non-force main integration.

# Current state

PR #393 is open, non-draft and mergeable. The branch is still diverged from current main. On exact pre-checkpoint head `dd6ec4b32c198fe11213909d5aba9acd3826b39b`, Agent Task Ownership #1447, Wheel of Destiny Validation #219 and autofix.ci #1477 are verified successful. CI #2581, Universal Agent Load #20 and Universal Agent E2E #62 are verified `in_progress` with no conclusion yet. Those in-progress checks do not satisfy the merge gate, and after this checkpoint-only commit a continuation agent must verify the new live PR head and its checks again.

# Plan

1. Merge current `main@264a86b1eddf5f68666281c47489166f343c3e84` into `feat/universal-agent-load-platform-v2` with a normal non-force update.

# Work log

## 2026-07-15T21:48:37Z

- Changed: migrated the existing active task to the current authoritative context-checkpoint format without creating a new task, branch or PR.
- Learned: live PR #393 is at `dd6ec4b32c198fe11213909d5aba9acd3826b39b`, current main is `264a86b1eddf5f68666281c47489166f343c3e84`, and the branch is 12 commits ahead / 11 behind.
- Failed/blocked: no local checkout is mounted, so local working-tree status and uncommitted paths cannot be verified in this session; branch freshness remains the first current blocker.
- Result: durable handoff now records live GitHub/CI/ownership evidence and exactly one next action.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Preserve PR #393 and branch `feat/universal-agent-load-platform-v2`; do not create competing work. | Existing live PR/task own the implementation. | none |
| Refresh with current main using a normal non-force merge before further CI repair or merge work. | `compare_commits` proves the branch is 11 commits behind current main; repository policy forbids bypassing branch/history safety. | none |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `.github/workflows/universal-agent-load.yml` | exclusive | exact-head load workflow | changed |
| `tools/e2e/run_agent_load.py` | exclusive | loopback load/stress profile runner | changed |
| `tools/e2e/run_agent_load_runtime.py` | exclusive | Canary runtime adapter | changed |
| `tests/e2e/load/**` | exclusive | smoke/load/stress profiles | changed |
| `tests/e2e/test_load_runner.py` | exclusive | focused runner regression tests | changed |
| `src/server/network/protocol/protocolstatus.cpp` | exclusive | query-throttle synchronization | changed |
| `docs/agents/tasks/active/CAN-20260715-universal-agent-load-platform.md` | exclusive | authoritative task/checkpoint | changed |
| `docs/agents/programs/E2E_AUTOMATION_PROGRAM.md` | shared | program handoff | not changed in current PR |
| `docs/agents/MODULE_CATALOG.md` | shared | reusable interface catalogue | not changed in current PR |
| `docs/agents/CHANGELOG.md` | shared | behavior-level change log | not changed in current PR |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| `d6b9073017bf40dde21ed43242b96a73d1f1bb95` | Agent Task Ownership #1403 | passed | run `29436191279` |
| `d6b9073017bf40dde21ed43242b96a73d1f1bb95` | Universal Agent Load #19 | passed | run `29436191575` |
| `d6b9073017bf40dde21ed43242b96a73d1f1bb95` | Universal Agent E2E #61 | passed | run `29436191526` |
| `d6b9073017bf40dde21ed43242b96a73d1f1bb95` | CI #2534 | passed | run `29436191580` |
| `d6b9073017bf40dde21ed43242b96a73d1f1bb95` | CI #2536 | failed | run `29438916481`; Linux release global datapack smoke; historical pre-checkpoint failure |
| `dd6ec4b32c198fe11213909d5aba9acd3826b39b` | Agent Task Ownership #1447 | passed | run `29452771339` |
| `dd6ec4b32c198fe11213909d5aba9acd3826b39b` | Wheel of Destiny Validation #219 | passed | run `29452771545` |
| `dd6ec4b32c198fe11213909d5aba9acd3826b39b` | autofix.ci #1477 | passed | run `29452771663` |
| `dd6ec4b32c198fe11213909d5aba9acd3826b39b` | CI #2581 | in-progress | run `29452771865`; no conclusion at checkpoint time |
| `dd6ec4b32c198fe11213909d5aba9acd3826b39b` | Universal Agent Load #20 | in-progress | run `29452772681`; no conclusion at checkpoint time |
| `dd6ec4b32c198fe11213909d5aba9acd3826b39b` | Universal Agent E2E #62 | in-progress | run `29452771989`; no conclusion at checkpoint time |

Never treat the in-progress entries above as passed.

# Failed approaches and dead ends

- Do not reopen or merge superseded PR #384.
- Do not force-rewrite published history to refresh the branch.
- Do not weaken status throttles, load assertions or physical E2E checks to obtain green CI.
- Rejected: PR #393 currently has an ownership conflict; exact-head Agent Task Ownership #1447 passed.
- Rejected: another open PR owns this exact load-platform task; exact task-ID search returns only PR #393.
- Rejected: current exact-head CI is fully green; CI #2581, Universal Agent Load #20 and Universal Agent E2E #62 are still in progress.
- Rejected: current main is already integrated; deterministic comparison reports the branch 11 commits behind.

# Risks and compatibility

- Runtime: concurrent `ProtocolStatus` status traffic touches process-wide throttle state; preserve the narrow synchronization semantics already in the PR.
- Data/migration: no data or schema migration is part of this task.
- Security: load targets remain literal loopback only; do not expand to production or third-party hosts.
- Backward compatibility: status throttle semantics must not be weakened.
- Cross-repo rollout: none; OTClient remains read-only and unchanged.
- Rollback: PR is unmerged; normal branch/PR rollback remains available.

# Remaining work

1. Merge current `main@264a86b1eddf5f68666281c47489166f343c3e84` into `feat/universal-agent-load-platform-v2` with a normal non-force update.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-15T21:48:37Z
head: dd6ec4b32c198fe11213909d5aba9acd3826b39b
branch: feat/universal-agent-load-platform-v2
pr: 393
status: blocked
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
  - Live PR 393 is open, non-draft and mergeable with head repository blakinio/canary, base main, branch feat/universal-agent-load-platform-v2 and exact pre-checkpoint head dd6ec4b32c198fe11213909d5aba9acd3826b39b.
  - Current main is 264a86b1eddf5f68666281c47489166f343c3e84.
  - Comparing current main to dd6ec4b32c198fe11213909d5aba9acd3826b39b reports diverged, ahead_by 12, behind_by 11 and merge base 6b613b886092b7face057507d4dd903c39cd5e1b.
  - PR 393 has exactly nine changed implementation/task paths relative to current main.
  - Agent Task Ownership 1447 passed on dd6ec4b32c198fe11213909d5aba9acd3826b39b; no active ownership overlap is proven on that head.
  - Narrow open-PR searches found no competing open PR for protocolstatus.cpp or universal-agent-load.yml; exact task-ID search returned only PR 393.
  - PR 393 has no submitted reviews and no review threads at checkpoint time.
  - Wheel of Destiny Validation 219 and autofix.ci 1477 passed on dd6ec4b32c198fe11213909d5aba9acd3826b39b.
  - CI 2581, Universal Agent Load 20 and Universal Agent E2E 62 are in progress on dd6ec4b32c198fe11213909d5aba9acd3826b39b with no conclusion at checkpoint time.
  - Historical CI 2536 failed in Linux release global datapack smoke on d6b9073017bf40dde21ed43242b96a73d1f1bb95; earlier CI 2534, Load 19, E2E 61 and Ownership 1403 passed on that stated head.
  - This execution environment has no mounted local Git worktree for blakinio/canary; local git status and every local uncommitted path are not inspectable here, so no clean-working-tree claim is made.
derived:
  - The current first merge-gate blocker is branch freshness, because the task branch is 11 commits behind current main and current-main gate results do not yet exist.
  - Exact-head successful ownership/autofix/validation checks do not satisfy the merge gate while required CI/load/E2E are unfinished and the branch is behind main.
  - A fresh agent can continue from PR 393 and this task without using historical chat context.
unknown:
  - Local working-tree status and every uncommitted path in any checkout not mounted in this execution environment.
  - Final conclusions of CI 2581, Universal Agent Load 20 and Universal Agent E2E 62 on dd6ec4b32c198fe11213909d5aba9acd3826b39b.
  - Whether integrating current main resolves, preserves or changes the historical global datapack smoke failure.
  - Current-main merge-ref results for CI, ownership, Universal Agent Load and Universal Agent E2E after main integration.
conflicts: []
first_failure:
  marker: Current-main merge gate / branch freshness
  evidence: compare main@264a86b1eddf5f68666281c47489166f343c3e84 to head dd6ec4b32c198fe11213909d5aba9acd3826b39b reports behind_by 11.
rejected_hypotheses:
  - PR 393 currently has an ownership conflict: Agent Task Ownership 1447 passed on dd6ec4b32c198fe11213909d5aba9acd3826b39b.
  - Another open PR owns this exact load-platform task: exact task-ID search returned only PR 393 and narrow path searches found no competitor.
  - Current exact-head CI is fully green: CI 2581, Universal Agent Load 20 and Universal Agent E2E 62 remain in progress.
  - Current main is already integrated into the branch: deterministic comparison reports behind_by 11.
changed_paths:
  - .github/workflows/universal-agent-load.yml
  - docs/agents/tasks/active/CAN-20260715-universal-agent-load-platform.md
  - src/server/network/protocol/protocolstatus.cpp
  - tests/e2e/load/status-load.json
  - tests/e2e/load/status-smoke.json
  - tests/e2e/load/status-stress.json
  - tests/e2e/test_load_runner.py
  - tools/e2e/run_agent_load.py
  - tools/e2e/run_agent_load_runtime.py
validation:
  - command: Agent Task Ownership 1447
    result: PASS
    evidence: GitHub Actions run 29452771339 on exact head dd6ec4b32c198fe11213909d5aba9acd3826b39b.
  - command: Wheel of Destiny Validation 219
    result: PASS
    evidence: GitHub Actions run 29452771545 on exact head dd6ec4b32c198fe11213909d5aba9acd3826b39b.
  - command: autofix.ci 1477
    result: PASS
    evidence: GitHub Actions run 29452771663 on exact head dd6ec4b32c198fe11213909d5aba9acd3826b39b.
  - command: CI 2581
    result: BLOCKED
    evidence: GitHub Actions run 29452771865 is in_progress with no conclusion at checkpoint time.
  - command: Universal Agent Load 20
    result: BLOCKED
    evidence: GitHub Actions run 29452772681 is in_progress with no conclusion at checkpoint time.
  - command: Universal Agent E2E 62
    result: BLOCKED
    evidence: GitHub Actions run 29452771989 is in_progress with no conclusion at checkpoint time.
blockers:
  - Branch is 11 commits behind current main, so a current-main merge ref and merge-gate validation do not yet exist.
  - Required CI 2581, Universal Agent Load 20 and Universal Agent E2E 62 are unfinished on the pre-checkpoint head.
next_action: Merge current main@264a86b1eddf5f68666281c47489166f343c3e84 into feat/universal-agent-load-platform-v2 with a normal non-force update.
```

# Handoff

This section is human-readable context only. The authoritative continuation state is the `## Context checkpoint` above.

## Start here

Read root `AGENTS.md`, `docs/agents/REPOSITORY_MAP.md`, `docs/agents/CONTEXT_ROUTING.md`, this checkpoint, and live PR #393. Verify the new live PR head and current main before changing state.

## Do not repeat

- Do not create a competing task, branch or PR.
- Do not reopen PR #384.
- Do not use old chat history as evidence.
- Do not modify OTClient or create a second physical E2E orchestrator.
- Do not repair unrelated Gameplay Analytics code before refreshing PR #393 against current main and re-running gates.

## Required reads

- `AGENTS.md`
- `docs/agents/REPOSITORY_MAP.md`
- `docs/agents/CONTEXT_ROUTING.md`
- `docs/agents/CONTEXT_HANDOFF.md`
- `docs/agents/programs/E2E_AUTOMATION_PROGRAM.md`
- live PR #393

## Open questions

- Final outcomes of the in-progress exact-head CI/load/E2E workflows.
- Current-main gate outcomes after normal main integration.

# Completion

- Final status: blocked / handoff-ready
- PR: #393
- Merge commit: none
- Program record updated: not in this checkpoint-only handoff
- Catalogue updated: not in this checkpoint-only handoff
- Changelog updated: not in this checkpoint-only handoff
- Archived at: not applicable; task remains active
