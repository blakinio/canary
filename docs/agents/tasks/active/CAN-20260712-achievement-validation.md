---
task_id: CAN-20260712-achievement-validation
coordination_id: ""
status: active
agent: "GPT-5.6 Thinking"
branch: feat/achievement-validation-audit
base_branch: main
created: 2026-07-12T17:16:14Z
updated: 2026-07-12T17:16:14Z
last_verified_commit: ""
risk: low
related_issue: ""
related_pr: ""
depends_on: []
blocks: []
owned_paths:
  - tools/ai-agent/achievement_validation.py
  - tools/ai-agent/test_achievement_validation.py
  - docs/ai-agent/ACHIEVEMENT_VALIDATION_REPORT.md
  - docs/ai-agent/ACHIEVEMENT_RUNTIME_TEST_PLAN.json
  - docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md
  - docs/agents/tasks/active/CAN-20260712-achievement-validation.md
  - docs/agents/ACTIVE_WORK.md
  - docs/agents/MODULE_CATALOG.md
modules_touched:
  - AI world validation
  - achievement registry and trigger audit
reuses:
  - OTS AI World Validation evidence methodology
  - existing ACHIEVEMENTS registry
  - existing Player achievement APIs
public_interfaces:
  - achievement validation report format
  - achievement validation CLI
cross_repo_tasks: []
---

# Goal

Create a deterministic, evidence-based audit of Canary achievements that validates registry metadata and active award paths without changing gameplay data.

# Acceptance criteria

- [ ] Parse the active `ACHIEVEMENTS` registry and report structural/metadata defects.
- [ ] Scan active datapacks for static and dynamic achievement award/progress paths.
- [ ] Distinguish definitions, runtime awards, progress-only references, checks, removals, admin-only paths, and unresolved dynamic references.
- [ ] Compare the current registry baseline with the referenced TibiaWiki/Fandom achievements page without copying spoiler text into the repository.
- [ ] Produce a human-readable evidence report and a machine-readable runtime test plan.
- [ ] Add focused unit tests for parser and classifier behavior.
- [ ] Do not modify the achievement registry, active datapacks, map, assets, or engine behavior in this audit PR.
- [ ] Relevant checks completed.
- [ ] Module catalogue impact handled.
- [ ] Documentation/changelog impact handled or recorded as none.
- [ ] Cross-repository impact handled as none.
- [ ] Autonomous merge gate satisfied.

# Confirmed context

- The writable repository is `blakinio/canary`; `opentibiabr/canary` is reference-only.
- `data/scripts/lib/register_achievements.lua` currently registers achievement IDs through 570 with documented gaps.
- The referenced TibiaWiki/Fandom page currently states 562 discovered achievements out of 563 total and lists 562 entries.
- The world-validation project requires evidence-based classification and forbids guessing runtime behavior.
- Open PRs inspected on 2026-07-12; no achievement-validation overlap was found.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| OTS AI World Validation | Evidence layers and handoff rules | `docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md` | Defines structure/reference/semantic/runtime/regression layers. |
| Achievement registry | Canonical definitions | `data/scripts/lib/register_achievements.lua` | Active IDs, names, grades, points, secrecy and descriptions. |
| Player achievement API | Runtime operations | engine/Lua player achievement sources | Defines award, progress, check and removal calls to classify. |

# Ownership and overlap check

- Open PRs inspected: #164, #163, #157, #156, #155, #136 and current search results.
- Active tasks inspected: `docs/agents/ACTIVE_WORK.md` plus open PR state.
- Overlaps: none in achievement registry/tooling paths.
- Resolution: dedicated branch and documentation/tool-only audit scope.

# Current state

The registry exists and runtime calls are distributed across active datapacks. No deterministic repository-wide audit or persistent evidence report currently exists.

# Plan

1. Inventory registry structure and active API conventions.
2. Implement deterministic scanner and classifier.
3. Add focused tests.
4. Run the scanner against current `main` through CI or an available repository checkout.
5. Record evidence, gaps, confidence and bounded follow-up work.

# Work log

## 2026-07-12T17:16:14Z

- Changed: created task branch and persistent task record.
- Learned: current registry ends at ID 570 while the referenced wiki page reports 562 listed achievements; raw highest ID is not the same as count because the registry contains gaps.
- Failed/blocked: local shell cannot resolve `github.com`, so repository-wide execution must use GitHub/CI or another available checkout.
- Result: audit scope claimed; no gameplay files changed.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Keep the first PR read-only | A definition/trigger audit must precede gameplay fixes under the world-validation methodology. | none |
| Do not treat missing static text matches as proof of a broken achievement | Dynamic tables/wrappers can award achievements indirectly. | none |
| Keep wiki-derived spoiler descriptions out of committed reports | Only metadata and source references are needed for validation. | none |

# Files and interfaces

| Path/interface/config/schema | Purpose | Status |
|---|---|---|
| `tools/ai-agent/achievement_validation.py` | deterministic registry/trigger scanner | planned |
| `tools/ai-agent/test_achievement_validation.py` | focused parser/classifier tests | planned |
| `docs/ai-agent/ACHIEVEMENT_VALIDATION_REPORT.md` | evidence report and findings | planned |
| `docs/ai-agent/ACHIEVEMENT_RUNTIME_TEST_PLAN.json` | machine-readable runtime scenarios | planned |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| | focused Python tests | not-run | implementation pending |
| | AI Agent Tools workflow | not-run | PR not opened yet |

Never write `passed` without verification.

# Failed approaches and dead ends

- Direct `git clone` from the execution container failed because DNS resolution for `github.com` is unavailable.

# Risks and compatibility

- Runtime: no runtime change in audit PR.
- Data/migration: none.
- Security: no secrets or player data.
- Backward compatibility: report/tool only.
- Cross-repo rollout: none.
- Rollback: revert documentation/tool commits.

# Remaining work

1. Implement the scanner and tests.
2. Produce an evidence report from current repository state.
3. Open a draft PR and update coordination indexes.

# Handoff

## Start here

Read this task, then inspect `data/scripts/lib/register_achievements.lua`, Player achievement APIs, and all active `addAchievement`/`addAchievementProgress` call sites.

## Do not repeat

Do not infer that an achievement is unobtainable solely because its name does not occur in a direct `player:addAchievement("...")` call.

## Required reads

- `AGENTS.md`
- `docs/agents/ACTIVE_WORK.md`
- `docs/agents/MODULE_CATALOG.md`
- `docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md`
- achievement registry and Player achievement API sources

## Open questions

- Which achievements are awarded through dynamic tables or wrappers that require explicit classifier support?
- Which registry metadata differs from the current referenced wiki baseline?

# Completion

- Final status: active
- PR:
- Merge commit:
- Catalogue updated: no
- Changelog updated: no
- Archived at:
