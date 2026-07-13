---
task_id: CAN-20260713-otbm-tooling-program-handoff
coordination_id: "OTS-OTBM-VALIDATION"
status: ready_for_review_pending_ci
agent: "GPT-5.6 Thinking"
branch: docs/otbm-tooling-program-handoff
base_branch: main
created: 2026-07-13T12:52:00+02:00
updated: 2026-07-13T13:00:00+02:00
last_verified_commit: "2d9cb2984e611c43709bfa8136b5890cf281a7ed"
risk: low
related_issue: ""
related_pr: "#247"
depends_on:
  - "merged Unified OTBM World Index #219 and lifecycle #223"
  - "merged Quest Map Validator #225 and lifecycle #236"
  - "merged The Beginning audit #204"
  - "merged The Beginning repair plan #207"
blocks:
  - "next bounded OTBM/quest follow-up selection"
owned_paths:
  exclusive:
    - docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md
    - docs/agents/tasks/active/CAN-20260713-otbm-tooling-program-handoff.md
  shared: []
  read_only:
    - AGENTS.md
    - docs/agents/README.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/REPOSITORY_MAP.md
    - docs/agents/KNOWN_RISKS.md
    - docs/agents/BUILD_TEST_MATRIX.md
    - docs/agents/CROSS_REPO_CONTRACTS.md
    - docs/ai-agent/OTBM_HD_PIPELINE.md
    - docs/ai-agent/OTBM_SCRIPT_RESOLUTION.md
    - docs/ai-agent/OTBM_WORLD_INDEX.md
    - docs/ai-agent/OTBM_WORLD_INDEX.schema.json
    - docs/ai-agent/QUEST_MAP_VALIDATION.md
    - docs/ai-agent/QUEST_MAP_VALIDATION.schema.json
    - docs/ai-agent/THE_BEGINNING_OTBM_AUDIT.md
    - docs/ai-agent/THE_BEGINNING_REPAIR_PLAN.md
    - tools/ai-agent/otbm_item_audit_scan.cpp
    - tools/ai-agent/otbm_world_index.py
    - tools/ai-agent/otbm_world_index_tool.py
    - tools/ai-agent/otbm_script_resolution.py
    - tools/ai-agent/otbm_map_tool.py
    - tools/ai-agent/otbm_render_tool.py
    - tools/ai-agent/otbm_renderer.py
    - tools/ai-agent/otbm_hd.py
    - tools/ai-agent/otbm_hd_tool.py
    - tools/ai-agent/quest_map_validation.py
    - tools/ai-agent/quest_map_validation_tool.py
    - tools/ai-agent/test_quest_map_validation.py
    - .github/workflows/otbm-world-index.yml
    - .github/workflows/quest-map-validation.yml
    - data-otservbr-global/npc/carlos.lua
    - data-otservbr-global/npc/santiago.lua
    - data-otservbr-global/scripts/lib/register_actions.lua
    - data-otservbr-global/scripts/quests/the_beginning/the_beginning_tutorial_moveevents.lua
    - data-otservbr-global/scripts/quests/the_beginning/the_beginning_zirella_wood.lua
    - data-otservbr-global/scripts/quests/the_beginning/the_beginning_zirella_door.lua
cross_repo_tasks: []
---

# Goal

Refresh the single authoritative OTBM tooling roadmap into a complete, self-contained programme handoff for the next agent. This task is documentation-only and must not start a new implementation, parser, validator, renderer, gameplay repair, workflow, map or asset change.

# Current repository state

- Repository: `blakinio/canary`.
- Base at branch creation: `56ee9bc72b91ba1110cd6d957c7eb0d974fc54e1`.
- Current `main` before Ready transition: `88e0140329a91fb877633307d2b749fecb175a43`.
- Branch: `docs/otbm-tooling-program-handoff`.
- Draft PR: #247.
- Existing authoritative programme document: `docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md`.
- No competing `docs/ai-agent/OTBM_TOOLING_ROADMAP_HANDOFF.md` exists.
- `docs/agents/ACTIVE_WORK.md` is read-only, not owned and unchanged.
- Open-PR searches found no direct OTBM/Quest Map Validator implementation overlap. PR #245 is adjacent universal E2E infrastructure and currently owns only its own task record; it does not own the OTBM roadmap.
- Final pre-ready changed-file list contains exactly the roadmap and this task record.

# Verified historical baseline

| Work | State | Head | Merge |
|---|---|---|---|
| Unified OTBM World Index #219 | merged | `452cdc6aaa183a7b4ce05ea83a013046764ecdb1` | `97ff786663b30cafbd933799d8549a6dd3e3370b` |
| World Index lifecycle #223 | merged | `5cd9fb524e117600e26103b3491ba1b41e866b94` | `97639776bb37c4f9aa1fa301cf43e7693a03a735` |
| Quest Map Validator #225 | merged | `857985c8c0849fa2b86d8c1d688fbe663d0018fa` | `b23c8a353b09c066e72de178b8e86f0309740211` |
| Quest Map Validator lifecycle #236 | merged | `68965a9b60d45d95ab8aadb3275820f4929f118f` | `51766f5ebade7f7c3632ba57991472b4f9adec79` |
| The Beginning audit #204 | merged | `de5dc8bd70f0e2f98681e0bbf531843177508881` | `dfa535cbfdcb14a6fe4f19880a1281016d35b4c9` |
| The Beginning repair plan #207 | merged | `00e1e390847ccc0a7c2e567e9ac8a117cff330ed` | `f96680987955cde24d4264e9473bde70501ed534` |
| Carlos repair #157 | merged | `6b68b25d42776747e994b516eca4a16ffd2c6c48` | `813a2ce39daced46802e6801e4abd275709b8672` |

# Local checkout and DNS limitation

Local checkout is unavailable. The exact command executed was:

```text
git ls-remote https://github.com/blakinio/canary.git HEAD
```

It failed with:

```text
fatal: unable to access 'https://github.com/blakinio/canary.git/': Could not resolve host: github.com
```

After this confirmed DNS failure, clone/fetch/ls-remote was not repeated. GitHub API was used for repository, file, PR, branch, workflow, job and review inspection and for documentation mutations. No local checkout, local unit test, local formatter, local ownership check or local build result is claimed.

# Acceptance criteria

- [x] Reconstruct current `main`, merged/open PRs, branches, tasks, ownership and historical workflow evidence.
- [x] Update the existing authoritative roadmap instead of creating a competing programme document.
- [x] Record exact contracts for World Index, Quest Map Validator, script resolution and factual rendering.
- [x] Record real-map provenance and The Beginning correlation evidence.
- [x] Recheck The Beginning findings against current `main`, including merged Carlos repair.
- [x] Record bounded Phases 3–8 without implementing them.
- [x] Select exactly one next bounded scope that is still open, owner-free and map-free.
- [x] Record hard prohibitions, DNS/local-checkout boundary and first-command handoff.
- [x] Keep changed files documentation-only and exclude `ACTIVE_WORK.md`.
- [x] Open a draft PR and inspect the exact changed-file list.
- [ ] Mark Ready, inspect fresh concrete CI jobs/reviews, enable auto-merge and reach squash merge.
- [ ] Archive this task in a separate documentation-only lifecycle PR.

# Safety boundaries

- Do not reopen PR #225 or continue `feat/quest-map-validator`.
- Do not reactivate the archived Quest Map Validator task.
- Do not create a new OTBM parser, map renderer, World Index, script resolver or Quest Map Validator.
- Do not execute or guess dynamic Lua and do not promote unresolved evidence to handled.
- Do not edit `docs/agents/ACTIVE_WORK.md`.
- Do not commit `.otbm`, `.widx`, `items.otb`, appearances, sprite sheets, client assets or generated large reports/renders.
- Do not use AI image generation for map visualization.
- Do not modify the map or upstream repositories.

# Validation and CI

Draft-head `2d9cb2984e611c43709bfa8136b5890cf281a7ed`:

- Agent Task Ownership run `29244622842`: success.
  - Job `Validate active ownership` (`86798452530`) succeeded.
  - Ownership tooling compilation, focused unit tests and active-task/index validation succeeded.
- AI Agent Tools run `29244622820`: success.
  - Job `Validate AI agent tools` (`86798452521`) succeeded, including unit tests, registries, reference validation, schemas and realistic content-pack checks.
- CI run `29244622919`: success.
  - `Detect Build Scope` (`86798452854`) succeeded.
  - `Required` (`86798499039`) succeeded.
  - Lua, Fast Checks, Linux, Windows, macOS, Docker and Docker Quickstart were skipped because the net diff is documentation-only.

These are draft-head checks. A fresh final-head/post-ready run remains required before merge.

# Work log

## 2026-07-13T12:52:00+02:00

- Read the mandatory agent/governance/tooling documentation and current implementation contracts through the GitHub API.
- Confirmed that the existing roadmap is the programme document to update; no competing handoff file will be created.
- Verified PR and merge metadata for Phases 1–2, The Beginning audit/plan and the already-merged Carlos repair.
- Confirmed from current `main` that Santiago's `easy` branch still persists greet stage 11 while the normal equivalent persists stage 12, making it the first still-open implementation-ready package.
- Confirmed from current `main` that the rope-success branch still checks `< 22` without writing stage 22.
- Confirmed local Git access is blocked by DNS and recorded the exact command/error.

## 2026-07-13T13:00:00+02:00

- Opened draft PR #247 and confirmed its net changed-file list contains exactly two documentation files.
- Replaced the stale roadmap with the complete programme handoff, preserving exact evidence boundaries and selecting Santiago persistence as the next bounded package.
- Inspected draft-head ownership, AI Agent Tools and CI jobs individually; all emitted checks succeeded.
- Main advanced independently from `56ee9bc7...` to `88e01403...` through unrelated documentation lifecycle work; no owned-path overlap was introduced.

# Failed approaches and corrections

- Local checkout/fetch was blocked by the recorded DNS failure; no local result is claimed.
- An attempted contents-API write used the create-file action for an existing roadmap and was rejected with HTTP 422 because the current blob SHA was required; the correct update-file action was then used.
- A temporary empty `README_DO_NOT_CREATE.tmp` file was accidentally created while loading the correct PR action and immediately deleted in the next commit. It is absent from the PR diff and changed-file list.
- An attempted create-file call against the existing task record was rejected before mutation because the current SHA was required; the task was updated through the correct update-file action.

# Remaining work

1. Mark PR #247 Ready for review.
2. Record the resulting final head SHA and inspect every fresh workflow/job.
3. Inspect review threads and mergeability.
4. Enable auto-merge and allow squash merge after the required gate succeeds.
5. Archive this task in a separate cleanup PR with exact feature head, merge SHA and workflow evidence.

# Handoff

Continue only on PR #247 and branch `docs/otbm-tooling-program-handoff` until it merges. Do not add code, gameplay, workflow, map, asset or `ACTIVE_WORK.md` changes. After merge, create one documentation-only cleanup branch that moves this task to `docs/agents/tasks/archive/`, records final evidence and updates the roadmap only if final merge/main metadata must be pinned.