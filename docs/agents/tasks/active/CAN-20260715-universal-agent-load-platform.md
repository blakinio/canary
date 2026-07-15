---
task_id: CAN-20260715-universal-agent-load-platform
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: ""
status: blocked
agent: chatgpt-e2e-platform
branch: feat/universal-agent-load-platform-v2
base_branch: main
created: 2026-07-15T15:40:00+02:00
updated: 2026-07-15T21:37:34Z
last_verified_commit: d6b9073017bf40dde21ed43242b96a73d1f1bb95
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
- [ ] Autonomous merge gate satisfied.

# Confirmed context

- Repository write target: `blakinio/canary` only.
- Active PR: #393.
- Active branch: `feat/universal-agent-load-platform-v2`.
- Verified PR head before this checkpoint-only update: `d6b9073017bf40dde21ed43242b96a73d1f1bb95`.
- Current main: `264a86b1eddf5f68666281c47489166f343c3e84`.
- The branch is 11 commits ahead and 11 commits behind current main; merge base is `6b613b886092b7face057507d4dd903c39cd5e1b`.
- PR #384 is closed without merge and is historical evidence only.
- This execution environment has no local Git worktree. Local `git status`, local branch/HEAD, and uncommitted paths outside GitHub are therefore not inspectable here.

# Ownership and overlap check

- Agent Task Ownership #1403 passed on `d6b9073017bf40dde21ed43242b96a73d1f1bb95`.
- Narrow open-PR search for `ProtocolStatus` returned only PR #393.
- No ownership overlap is proven on the verified PR head.
- Ownership against current main is not yet revalidated because the branch is 11 commits behind.

# Current state

PR #393 is open and mergeable. The latest CI associated with the verified PR head is red: CI #2536 failed in the Linux release global datapack smoke. Artifact evidence shows Gameplay Analytics load-order errors in global datapack startup. Those files are not part of PR #393's changed-file list. Earlier Universal Agent Load #19, Universal Agent E2E #61, Agent Task Ownership #1403 and CI #2534 succeeded on the verified PR head, but those results do not establish the current-main merge gate.

# Plan

1. Merge current `main@264a86b1eddf5f68666281c47489166f343c3e84` into `feat/universal-agent-load-platform-v2` with a normal non-force update.

# Validation and CI

| Commit | Check | Result | Evidence |
|---|---|---|---|
| `d6b9073017bf40dde21ed43242b96a73d1f1bb95` | Agent Task Ownership #1403 | passed | run `29436191279` |
| `d6b9073017bf40dde21ed43242b96a73d1f1bb95` | Universal Agent Load #19 | passed | run `29436191575` |
| `d6b9073017bf40dde21ed43242b96a73d1f1bb95` | Universal Agent E2E #61 | passed | run `29436191526` |
| `d6b9073017bf40dde21ed43242b96a73d1f1bb95` | CI #2534 | passed | run `29436191580` |
| `d6b9073017bf40dde21ed43242b96a73d1f1bb95` | CI #2536 | failed | run `29438916481`; Linux release job `87432830073`, global datapack smoke |

# Failed approaches and dead ends

- Do not reopen or merge superseded PR #384.
- Do not force-rewrite published history to refresh the branch.
- Do not weaken status throttles or physical E2E checks to obtain green CI.
- Rejected: load workflow is failing on the verified PR head; Universal Agent Load #19 passed.
- Rejected: physical login/relog is failing on the verified PR head; Universal Agent E2E #61 passed.
- Rejected: ownership conflict already existed on the verified PR head; Agent Task Ownership #1403 passed.

# Remaining work

1. Merge current `main@264a86b1eddf5f68666281c47489166f343c3e84` into `feat/universal-agent-load-platform-v2` with a normal non-force update.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-15T21:37:34Z
head: d6b9073017bf40dde21ed43242b96a73d1f1bb95
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
  - Live PR 393 is open and mergeable with branch feat/universal-agent-load-platform-v2 at d6b9073017bf40dde21ed43242b96a73d1f1bb95 before this checkpoint-only update.
  - Current main is 264a86b1eddf5f68666281c47489166f343c3e84.
  - Comparing main to d6b9073017bf40dde21ed43242b96a73d1f1bb95 reports ahead_by 11, behind_by 11 and merge base 6b613b886092b7face057507d4dd903c39cd5e1b.
  - PR 393 has exactly nine changed paths.
  - Agent Task Ownership run 1403 passed on d6b9073017bf40dde21ed43242b96a73d1f1bb95.
  - Universal Agent Load run 19 and Universal Agent E2E run 61 passed with d6b9073017bf40dde21ed43242b96a73d1f1bb95 associated with those runs.
  - Latest CI run 2536 associated with d6b9073017bf40dde21ed43242b96a73d1f1bb95 failed in Linux release global datapack smoke.
  - CI 2536 runtime-smoke artifact shows GameplayAnalytics load-order errors; those Gameplay Analytics files are not in PR 393 changed paths.
  - Narrow open-PR search for ProtocolStatus returned only PR 393.
  - This execution environment has no local Git worktree; local git status and uncommitted paths outside GitHub are not inspectable here.
derived:
  - The latest CI failure is not yet proven to be caused by PR 393 implementation because it occurs outside the PR changed paths and the branch is 11 commits behind current main.
  - Earlier green load, E2E and ownership results do not satisfy a current-main merge gate after main advanced.
unknown:
  - Local working-tree status and any uncommitted paths in a checkout unavailable to this session.
  - Whether integrating current main resolves, preserves or changes the global datapack smoke failure.
  - Whether ownership remains conflict-free after integrating current main.
  - Current-main merge-ref results for CI, Universal Agent Load and Universal Agent E2E.
conflicts: []
first_failure:
  marker: CI 2536 / Build - Linux / Compile (linux-release) / Smoke test Global datapack runtime
  evidence: Run 29438916481 job 87432830073; artifact linux-linux-release-runtime-smoke-logs id 8352824026 contains GameplayAnalytics must be loaded before gameplay_analytics_* errors.
rejected_hypotheses:
  - Load workflow is failing on d6b9073017bf40dde21ed43242b96a73d1f1bb95: Universal Agent Load run 19 passed.
  - Physical login/relog is failing on d6b9073017bf40dde21ed43242b96a73d1f1bb95: Universal Agent E2E run 61 passed.
  - Ownership conflict was present on d6b9073017bf40dde21ed43242b96a73d1f1bb95: Agent Task Ownership run 1403 passed.
  - Current CI is fully green: latest CI run 2536 failed.
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
  - command: Agent Task Ownership run 1403
    result: PASS
    evidence: GitHub Actions run 29436191279 on head d6b9073017bf40dde21ed43242b96a73d1f1bb95.
  - command: Universal Agent Load run 19
    result: PASS
    evidence: GitHub Actions run 29436191575 associated with head d6b9073017bf40dde21ed43242b96a73d1f1bb95.
  - command: Universal Agent E2E run 61
    result: PASS
    evidence: GitHub Actions run 29436191526 associated with head d6b9073017bf40dde21ed43242b96a73d1f1bb95.
  - command: CI run 2536
    result: FAIL
    evidence: GitHub Actions run 29438916481; Linux release global datapack smoke failed.
blockers:
  - Branch is 11 commits behind current main and latest CI is red; current-main gates have not been re-established.
next_action: Merge current main@264a86b1eddf5f68666281c47489166f343c3e84 into feat/universal-agent-load-platform-v2 with a normal non-force update so PR 393 gets a current-main merge ref.
```

# Handoff

## Start here

Read root `AGENTS.md`, `docs/agents/CONTEXT_HANDOFF.md`, `docs/agents/CONTEXT_ROUTING.md`, this checkpoint, and live PR #393. Verify live branch/head/main before changing state.

## Do not repeat

- Do not create a competing task, branch, or PR.
- Do not reopen PR #384.
- Do not use old chat history as evidence.
- Do not modify OTClient or create a second physical E2E orchestrator.
- Do not repair unrelated Gameplay Analytics code before refreshing the PR against current main and re-running gates.
