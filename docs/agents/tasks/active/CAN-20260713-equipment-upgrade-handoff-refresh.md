---
task_id: CAN-20260713-equipment-upgrade-handoff-refresh
status: validation_pending
agent: "GPT-5.6 Thinking"
branch: docs/equipment-upgrade-handoff-refresh
base_branch: main
created: 2026-07-13T12:35:00+02:00
updated: 2026-07-13T12:52:00+02:00
last_verified_commit: "d4eeab3db322f26ee72d7f0ad958d35dc9bd007d"
risk: low
related_pr: "#242"
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

Refresh the durable Equipment Upgrade / Exaltation Forge handoff against current `main`. This task is documentation-only: no gameplay, protocol, test, workflow or OTClient change.

# Current repository state

- Repository: `blakinio/canary`.
- Base `main`: `d4eeab3db322f26ee72d7f0ad958d35dc9bd007d`.
- Branch: `docs/equipment-upgrade-handoff-refresh`.
- Draft PR: #242.
- Last merged Forge PR: #177, merge `f1d217c43e8e302978f533212e6aa9d1ce2b77c8`.
- Historical branch `validation/equipment-upgrade`: not found and must not be continued.
- Other open Forge PRs: none found.
- Other active Forge tasks: none found.
- Maintained client: `blakinio/otclient`, observed `main` `2fcfa2b61f4cd2e47beb49ec036a01152979dd79`.
- `docs/agents/ACTIVE_WORK.md` is read-only, not owned and unchanged.

# Preserved baseline

| PR | Merge | Preserved result |
|---|---|---|
| #89 | `209289d38e64aafe7ce3e036867bb632cd0363b8` | normal Transfer authority, donor-tier costs/result and actual history costs |
| #110 | `84f5c09263f459d726fbc7b9f79557b2cbb0801d` | Forge history item identity by ID with name fallback |
| #177 | `f1d217c43e8e302978f533212e6aa9d1ce2b77c8` | direct/summon killer, one shared Dust roll, current logout block and actual capped credit/message |

# Current finding status

- `still-open`: F-001–F-006, F-011–F-012, F-014–F-024.
- `runtime-untested`: F-007, F-008, F-013; #177 code remains, focused runtime/gameplay proof does not.
- `target-version-decision-required`: F-009 and F-010.
- No finding is claimed fully remediated by this refresh.

The full row-by-row evidence, paths, functions, remediation PRs, missing proof and recommended scope are recorded in `docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_VALIDATION.md`.

# Revalidation result

The comparison from #177 merge to current `main` contains 77 later commits but no change to Forge configuration, item-tier tables, Player Forge functions, Forge reward Lua, Forge effects/tests or the Equipment Upgrade report. Later generic Player/protocol/creature changes were reviewed as unrelated to the audited Forge functions. Maintained `blakinio/otclient` still handles bonus values only 1–4, so F-018 remains open and cross-repository.

# Local checkout and tests

Local checkout is unavailable because the execution environment cannot resolve `github.com`.

```text
getent hosts github.com
# no DNS result

git ls-remote https://github.com/blakinio/canary.git HEAD
# fatal: unable to access 'https://github.com/blakinio/canary.git/': Could not resolve host: github.com
```

Could not run without a checkout:

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

None of these local checks is claimed as passed. GitHub API and CI are separate evidence.

# Historical CI evidence

- #89 head `570d6e077c02107eb712a4ff214cf4442d6c91d8`: CI run `29164115572` succeeded; later run `29167859855` failed.
- #110 head `78e10449f9c9c8401bf576f5751998f0fa7da655`: CI runs `29185907405` and `29185890664` succeeded; PR reports 383 C++ tests including Forge Transfer integration.
- #177 head `05134a4c96083c9b21e5e86a5e51dcfc3f53bee6`: CI run `29205082784` succeeded for Detect Build Scope, Fast Checks, Lua Tests and Linux Release/runtime smoke; later CI run `29206161337` failed.
- These runs do not prove focused Forge gameplay or physical-client E2E.

# Work log

- Read all required governance, repository, risk, build, cross-repository and validation documents.
- Verified current main, open PRs, active work and historical branch state.
- Re-read PRs #89, #110 and #177 and recorded actual merge commits.
- Compared #177 merge with current main and reviewed later potentially overlapping PRs.
- Inspected maintained `blakinio/otclient`; no later Forge PR exists and bonus presentation remains limited to values 1–4.
- Reclassified F-001–F-024 and replaced stale current-state/handoff text in the main report.
- Recorded exact DNS failure and unavailable local commands.
- Created branch, task and draft PR #242 using GitHub API only.
- First oversized task write was rejected by the tool before GitHub mutation; a smaller durable record was then committed normally.
- No temporary workflow, gameplay change, test, E2E platform or client change was created.

# Changed files

Expected only:

- `docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_VALIDATION.md`;
- `docs/agents/tasks/active/CAN-20260713-equipment-upgrade-handoff-refresh.md`.

# Recommended bounded follow-ups

1. F-003–F-005: server authority before mutation.
2. F-020–F-021: atomicity and rollback.
3. F-022–F-024: history action types and configurable amounts.
4. F-006: complete Premium semantics.
5. Runtime proof for F-007/F-008/F-013.
6. F-011/F-012.
7. F-014–F-019 as coordinated Canary + `blakinio/otclient` work.
8. F-009/F-010 only after authoritative versioned evidence.

# Remaining work

1. Inspect final changed files/diff and confirm `ACTIVE_WORK.md` is absent.
2. Update PR body and mark Ready for review.
3. Inspect concrete final-head jobs/logs; do not rely only on aggregate `Required`.
4. Merge documentation PR if no blocker.
5. Archive this task in a separate lifecycle cleanup PR.

# Invariants

- DO NOT REOPEN PR #177.
- DO NOT CONTINUE A DELETED HISTORICAL BRANCH.
- DO NOT EDIT ACTIVE_WORK.md.
- DO NOT CLAIM FULL FORGE PARITY.
- DO NOT CLAIM GAMEPLAY OR E2E PROOF WITHOUT EXECUTION.
- DO NOT MODIFY `opentibiabr/otclient`.
- DO NOT FIX ALL FINDINGS IN ONE PR.
