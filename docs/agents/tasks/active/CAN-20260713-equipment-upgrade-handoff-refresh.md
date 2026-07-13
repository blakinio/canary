---
task_id: CAN-20260713-equipment-upgrade-handoff-refresh
status: in_progress
agent: "GPT-5.6 Thinking"
branch: docs/equipment-upgrade-handoff-refresh
base_branch: main
created: 2026-07-13T12:35:00+02:00
updated: 2026-07-13T12:35:00+02:00
last_verified_commit: "d4eeab3db322f26ee72d7f0ad958d35dc9bd007d"
risk: low
related_pr: "pending"
depends_on:
  - merged Forge transfer repair PR #89
  - merged Forge history identity repair PR #110
  - merged Equipment Upgrade validation and Dust repair PR #177
owned_paths:
  exclusive:
    - docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_VALIDATION.md
    - docs/agents/tasks/active/CAN-20260713-equipment-upgrade-handoff-refresh.md
  shared: []
  read_only:
    - config.lua.dist
    - src/config/configmanager.cpp
    - data/scripts/systems/item_tiers.lua
    - data/libs/systems/exaltation_forge.lua
    - data/scripts/creaturescripts/monster/forge_kill.lua
    - src/creatures/players/player.cpp
    - src/server/network/protocol/protocolgame.cpp
    - src/items/item.cpp
    - src/creatures/combat/combat.cpp
    - tests/unit/players/forge/forge_test.cpp
    - tests/integration/players/forge_integration_test.cpp
cross_repo_tasks:
  - repository: blakinio/otclient
    mode: read_only
    scope: F-018/F-019 Forge result presentation
---

# Goal

Refresh the durable Equipment Upgrade / Exaltation Forge handoff against current `main`. This task is documentation-only: no gameplay, protocol, tests, workflow or OTClient change.

# Current repository state

- Repository: `blakinio/canary`.
- Current `main`: `d4eeab3db322f26ee72d7f0ad958d35dc9bd007d`.
- Last merged Forge PR: #177, merge `f1d217c43e8e302978f533212e6aa9d1ce2b77c8`.
- Historical branch `validation/equipment-upgrade`: not found; do not continue it.
- Open Forge PRs: none found.
- Active Forge tasks: none found.
- Maintained client: `blakinio/otclient`, observed `main` `2fcfa2b61f4cd2e47beb49ec036a01152979dd79`.
- `docs/agents/ACTIVE_WORK.md` is read-only and not owned.

# Preserved baseline

| PR | Merge | Preserved result |
|---|---|---|
| #89 | `209289d38e64aafe7ce3e036867bb632cd0363b8` | normal Transfer validation, donor-tier costs/result and actual history costs |
| #110 | `84f5c09263f459d726fbc7b9f79557b2cbb0801d` | Forge history item identity by item ID with name fallback |
| #177 | `f1d217c43e8e302978f533212e6aa9d1ce2b77c8` | direct/summon killer, one shared Dust roll, current logout block and actual capped credit/message |

# Current finding status

- `still-open`: F-001–F-006, F-011–F-012, F-014–F-024.
- `runtime-untested`: F-007, F-008, F-013; PR #177 implementation is preserved but focused runtime/gameplay proof is absent.
- `target-version-decision-required`: F-009 and F-010.
- No finding is claimed fully remediated by this refresh.

The comparison from #177 merge to current `main` contains 77 later commits but no change to Forge configuration, item-tier tables, Player Forge functions, Forge reward Lua, Forge effects/tests or this report. Later generic Player/protocol/creature changes were reviewed as unrelated to these Forge functions. Maintained OTClient still presents bonus values only 1–4, so F-018 remains open and cross-repository.

# Local checkout and tests

Local checkout is unavailable because the execution environment cannot resolve `github.com`.

```text
getent hosts github.com
# no DNS result

git ls-remote https://github.com/blakinio/canary.git HEAD
# fatal: unable to access 'https://github.com/blakinio/canary.git/': Could not resolve host: github.com
```

The following could not be run without a checkout:

```text
git clone https://github.com/blakinio/canary.git
git fetch --all --prune
git pull --ff-only
git checkout docs/equipment-upgrade-handoff-refresh
git status --short --branch
git branch -vv
git remote -v
git worktree list
git diff --check
python tools/agents/task_ownership.py
cmake --preset linux-debug
cmake --build --preset linux-debug --target canary_ut
ctest --test-dir build/linux-debug --output-on-failure
```

None of these local checks is claimed as passed. CI is separate evidence.

# Recommended bounded follow-ups

1. F-003–F-005: server authority before mutation.
2. F-020–F-021: atomicity and rollback.
3. F-022–F-024: history action types and configurable amounts.
4. F-006: complete Premium semantics.
5. Runtime proof for F-007/F-008/F-013.
6. F-011/F-012.
7. F-014–F-019 as coordinated Canary + `blakinio/otclient` work.
8. F-009/F-010 only after authoritative versioned evidence.

# Work log

- Read the required governance, repository, risk, build, cross-repository and world-validation documents.
- Verified current `main`, open PRs and absence of active Forge work.
- Re-read PRs #89, #110 and #177 and the current report.
- Compared #177 merge with current `main`; no later Forge-source/test/report change was found.
- Inspected maintained `blakinio/otclient`; no later Forge PR exists and bonus UI remains limited to values 1–4.
- Recorded the exact DNS failure and unavailable local commands.
- Created this documentation-only branch and task.

# Remaining work

1. Refresh the main report and detailed F-001–F-024 matrix.
2. Open/update the documentation PR and inspect the final diff.
3. Mark ready, inspect concrete final-head CI jobs, merge if clean.
4. Archive this task in a separate lifecycle cleanup PR.

# Invariants

- DO NOT REOPEN PR #177.
- DO NOT CONTINUE A DELETED HISTORICAL BRANCH.
- DO NOT EDIT ACTIVE_WORK.md.
- DO NOT CLAIM FULL FORGE PARITY.
- DO NOT CLAIM GAMEPLAY OR E2E PROOF WITHOUT EXECUTION.
- DO NOT MODIFY `opentibiabr/otclient`.
- DO NOT FIX ALL FINDINGS IN ONE PR.
