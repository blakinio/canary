---
task_id: CAN-20260713-equipment-upgrade-handoff-refresh
status: ready_for_review_pending_ci
agent: "GPT-5.6 Thinking"
branch: docs/equipment-upgrade-handoff-refresh
base_branch: main
created: 2026-07-13T12:35:00+02:00
updated: 2026-07-13T13:02:00+02:00
last_verified_commit: "5f963ea999367b4df65533382742fe0e4d111ef7"
risk: low
related_pr: "#242"
reuses:
  - docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_VALIDATION.md
  - docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md
  - merged Forge baselines from PRs #89, #110 and #177
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
- PR: #242, draft at the time of this record update.
- Last merged Forge PR: #177, merge `f1d217c43e8e302978f533212e6aa9d1ce2b77c8`.
- Historical branch `validation/equipment-upgrade`: not found and must not be continued.
- Other open Forge PRs: none found before opening #242.
- Other active Forge tasks: none found before creating this task.
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

# Exact evidence

- Comparison from #177 merge to current `main`: 77 later commits.
- No later change was found in Forge configuration, item-tier tables, Player Forge functions, Forge reward Lua, Forge item/combat effects, Forge tests or the validation report.
- Later generic Player/protocol/creature changes were reviewed as unrelated to the audited Forge functions.
- Maintained `blakinio/otclient` still handles Forge result bonus values only 1–4, so F-018 remains open and cross-repository.
- Final scope review before ready state showed exactly two changed files:
  - `docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_VALIDATION.md`;
  - `docs/agents/tasks/active/CAN-20260713-equipment-upgrade-handoff-refresh.md`.
- `docs/agents/ACTIVE_WORK.md` is absent from the diff.

# Commands and local-test limitation

Local checkout is unavailable because the execution environment cannot resolve `github.com`.

```text
getent hosts github.com
# no DNS result

git ls-remote https://github.com/blakinio/canary.git HEAD
# fatal: unable to access 'https://github.com/blakinio/canary.git/': Could not resolve host: github.com
```

The following commands could not be run:

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

# CI and test results

Historical evidence:

- #89 head `570d6e077c02107eb712a4ff214cf4442d6c91d8`: CI run `29164115572` succeeded; later run `29167859855` failed.
- #110 head `78e10449f9c9c8401bf576f5751998f0fa7da655`: CI runs `29185907405` and `29185890664` succeeded; PR reports 383 C++ tests including Forge Transfer integration.
- #177 head `05134a4c96083c9b21e5e86a5e51dcfc3f53bee6`: CI run `29205082784` succeeded for Detect Build Scope, Fast Checks, Lua Tests and Linux Release/runtime smoke.
- Later #177 CI run `29206161337`: Detect Build Scope, Lua Tests and Fast Checks succeeded; Linux Release job `86685992572` failed at `Check generated Lua API docs are current`. Runtime smoke and tests were skipped after that failure. This is not Forge gameplay proof.

PR #242 draft-head evidence on `5f963ea999367b4df65533382742fe0e4d111ef7`:

- Agent Task Ownership run `29242755953`: success.
  - Job `Validate active ownership` (`86792443247`) succeeded.
  - Steps included ownership tooling compilation, focused unit tests and active-task/index validation.
- CI run `29242756055`: success.
  - `Detect Build Scope` (`86792444028`) succeeded.
  - `Required` (`86792490230`) succeeded.
  - Lua Tests, Fast Checks, Linux, Windows, macOS, Docker and Docker Quickstart were skipped because the changed paths are documentation-only.
- AI Agent Tools run `29242755959`: success.

These draft-head runs are preliminary. A fresh post-ready run must be inspected job-by-job before merge.

# Decisions

- Do not reopen PR #177 or continue its deleted branch.
- Preserve all merged behavior from #89, #110 and #177.
- Do not claim full Forge parity.
- Keep F-007/F-008/F-013 as runtime-untested, not complete.
- Keep F-009/F-010 blocked on authoritative target-version evidence.
- Keep F-018/F-019 as coordinated Canary + maintained `blakinio/otclient` follow-up.
- Do not implement gameplay changes, tests or E2E platform work in this PR.

# Failed approaches

- Local checkout and all local commands listed above were blocked by DNS resolution failure.
- The first oversized task-record write was rejected by the connector before any GitHub mutation; a smaller valid record was committed.
- An unnecessary attempt to set `maintainer_can_modify` on the same-repository PR returned HTTP 422 because fork collaboration applies only to cross-repository PRs; no repository state changed.

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

1. Mark PR #242 Ready for review.
2. Record final head SHA after this bookkeeping commit.
3. Inspect every concrete post-ready workflow and job; do not rely only on aggregate `Required`.
4. Check review threads.
5. Squash-merge #242 if clean.
6. Archive this task in a separate lifecycle cleanup PR with the exact final feature head, merge SHA, workflow run IDs and final state.

# Handoff

Continue only on PR #242 and branch `docs/equipment-upgrade-handoff-refresh`. The report refresh is complete and the diff is documentation-only. Do not add Forge implementation changes. The next action is to mark the PR Ready for review, inspect fresh final-head CI job-by-job, then merge and archive this task. If blocked, write the exact head SHA, workflow/job ID, failed step and next command into this record and PR conversation.
