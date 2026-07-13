---
task_id: CAN-20260713-equipment-upgrade-handoff-refresh
program_id: ""
coordination_id: ""
status: in_progress
agent: ChatGPT
branch: fix/equipment-upgrade-validation-2
base_branch: main
created: 2026-07-13T10:16:00Z
updated: 2026-07-13T10:32:00Z
last_verified_commit: 048503f164cd1f4192d928fd4070134f43e79ccc
risk: low
related_issue: ""
related_pr: "241"
depends_on:
  - PR-89
  - PR-110
  - PR-177
blocks: []
owned_paths:
  exclusive:
    - docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_VALIDATION.md
    - docs/agents/tasks/active/CAN-20260713-equipment-upgrade-handoff-refresh.md
  shared: []
  read_only:
    - AGENTS.md
    - docs/agents/README.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/REPOSITORY_MAP.md
    - docs/agents/KNOWN_RISKS.md
    - docs/agents/BUILD_TEST_MATRIX.md
    - docs/agents/CROSS_REPO_CONTRACTS.md
    - docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md
    - docs/agents/ACTIVE_WORK.md
    - src/creatures/players/player.cpp
    - src/creatures/players/player.hpp
    - src/game/game.cpp
    - src/server/network/protocol/protocolgame.cpp
    - src/config/configmanager.cpp
    - config.lua.dist
    - data/libs/systems/exaltation_forge.lua
    - data/scripts/creaturescripts/monster/forge_kill.lua
    - src/creatures/monsters/monster.cpp
    - src/utils/tools.cpp
    - tests/integration/game/forge_it.cpp
    - tests/unit/players/forge_test.cpp
    - blakinio/otclient:modules/game_forge/game_forge.lua
modules_touched:
  - Equipment Upgrade validation documentation
reuses:
  - PR #89 normal Transfer policy/tests
  - PR #110 Forge history ID resolution
  - PR #177 Dust reward remediation and 24-finding audit
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Refresh the durable Equipment Upgrade / Exaltation Forge validation handoff against current `main`, preserve confirmed merged fixes, record the current F-001–F-024 status and merge documentation-only evidence without gameplay/runtime changes.

# Acceptance criteria

- [x] `docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_VALIDATION.md` identifies current `main`, historical PRs and the retired historical branch accurately.
- [x] F-001–F-024 are reclassified against current `main` with evidence level, remaining proof and bounded follow-up scope.
- [x] Current open Forge PRs/tasks and post-#177 relevant changes are recorded.
- [x] Local checkout limitation and exact DNS error are recorded; no unexecuted local test is reported as passed.
- [x] Changed files are documentation/task only and exclude `docs/agents/ACTIVE_WORK.md`.
- [x] Current-head GitHub checks and concrete jobs were inspected and recorded for verified head `048503f164cd1f4192d928fd4070134f43e79ccc`.
- [ ] PR is squash-merged and task lifecycle cleanup is completed unless a real blocker is recorded.
- [x] Module catalogue impact handled: no reusable interface/module change, therefore no catalogue edit required.
- [x] Changelog impact handled: no behavior or architecture change, therefore no changelog edit required.
- [x] Cross-repository impact handled: future client work targets `blakinio/otclient`; no cross-repository write in this task.

# Confirmed context

- Writable repository: `blakinio/canary` only.
- Current `main` at task start and before verified-head metadata update: `d4eeab3db322f26ee72d7f0ad958d35dc9bd007d`.
- Existing branch reused: `fix/equipment-upgrade-validation-2`; it was force-reset through the GitHub API to current `main` before this task record was created.
- The reset removed two incomplete experimental files (`.github/workflows/equipment-upgrade-phase1.yml` and `tools/ai-agent/apply_equipment_upgrade_phase1.py`) from the branch; they were never part of a PR and are not retained.
- Documentation PR: #241; state after content completion: Ready for review.
- Historical merge baseline:
  - PR #89 merged as `209289d38e64aafe7ce3e036867bb632cd0363b8`.
  - PR #110 merged as `84f5c09263f459d726fbc7b9f79557b2cbb0801d`.
  - PR #177 merged as `f1d217c43e8e302978f533212e6aa9d1ce2b77c8`; head was `05134a4c96083c9b21e5e86a5e51dcfc3f53bee6`.
- `validation/equipment-upgrade` is historical, has no current branch match and must not be continued or reopened.
- No open Forge implementation PR was found. PR #222 only establishes future shared E2E ownership and does not remediate Forge.
- No active Forge-specific task was identified before this record.
- Exact PR #241 changed files at verified-head review:
  - `docs/agents/tasks/active/CAN-20260713-equipment-upgrade-handoff-refresh.md`;
  - `docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_VALIDATION.md`.
- `docs/agents/ACTIVE_WORK.md`, runtime/config/protocol/test paths and both client repositories are unchanged.
- Review threads at readiness review: none.
- Current finding summary:
  - `partially-remediated; runtime-untested`: F-007, F-008, F-013;
  - `target-version-decision-required`: F-009, F-010;
  - `still-open`: all remaining F-001–F-024 findings;
  - fully remediated/superseded/conflicting/no-longer-applicable: none.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| PR #89 | Preserve normal Transfer classification, donor-tier costs, result tier and history behavior | `src/game/functions/forge_transfer_policy.hpp`, `player.cpp`, `protocolgame.cpp`, Forge tests | Confirmed merged baseline; do not regress. |
| PR #110 | Preserve ID-first item resolution in Forge history | `ForgeHistory.firstItemId/secondItemId`, `registerForgeHistoryDescription` | Avoids ambiguous/custom-name lookup. |
| PR #177 | Preserve one Dust roll per kill, logout-block recipient filtering and capped credited amount | `data/libs/systems/exaltation_forge.lua` | Only retained production remediation from the original audit. |
| Universal E2E program #222 | Future scenario ownership only | `docs/agents/programs/E2E_AUTOMATION_PROGRAM.md` | This task must not create a Forge-specific E2E platform. |

# Ownership and overlap check

- Program record: no Forge-specific program; shared future E2E ownership is PR #222/program record.
- Open PRs inspected: current repository open PR list plus Forge search; no Forge implementation PR overlaps these documentation paths.
- Active tasks inspected: `ACTIVE_WORK.md` read-only plus current task context; no Equipment Upgrade task overlapped the owned report path.
- Local ownership checker: not run because the repository could not be cloned due DNS failure.
- CI ownership validation: run `29242597949`, job `Validate active ownership`, success on head `048503f164cd1f4192d928fd4070134f43e79ccc`.
- Exclusive claims: the Equipment Upgrade report and this task record only.
- Shared claims: none.
- Overlaps reviewed: #220 broad Wheel/monster/game/protocol paths; #231/#233 `game.cpp`; #195/#212 weapon proficiency/monster overlap. Current Forge functions/config/Lua/tests were re-read and findings remain as recorded.
- Resolution: documentation-only refresh; no `ACTIVE_WORK.md` edit.

# Current state

PR #241 contains the rewritten current-main report and this task record. It is Ready for review. Verified content head `048503f164cd1f4192d928fd4070134f43e79ccc` passed the concrete checks listed below. This metadata commit records those results and must receive final metadata-equivalent checks before merge.

# Work log

## 2026-07-13T10:16:00Z

- Reset `fix/equipment-upgrade-validation-2` to current `main`; created this task record.
- Confirmed the old report was stale and current main was 77 commits after PR #177. Broad shared files changed later, but principal finding-bearing Forge implementation/config/Lua/tests did not change in the combined comparison.
- Local command failed:

```text
cd /tmp && rm -rf canary-handoff && git clone --filter=blob:none --no-checkout https://github.com/blakinio/canary.git canary-handoff
```

```text
fatal: unable to access 'https://github.com/blakinio/canary.git/': Could not resolve host: github.com
```

- `git fetch`, `git pull`, local checkout, local ownership validation, builds and tests were not attempted after clone failure because no checkout existed.

## 2026-07-13T10:24:00Z

- Opened draft PR #241; rewrote the main validation report with current repository state, full F-001–F-024 table, post-#177 drift review, evidence boundaries, work log, ordered bounded scopes and handoff warnings.
- Two accidental attempts to recreate the already-existing branch returned GitHub 422 `Reference already exists`; no branch state changed.
- A duplicate create-file attempt for this already-created task returned GitHub 422 because `sha` was not supplied; no file state changed.

## 2026-07-13T10:32:00Z

- Confirmed PR changed files are exactly the report and task record; no `ACTIVE_WORK.md` or runtime/client path.
- Confirmed no review threads.
- Updated PR body and marked PR #241 Ready for review.
- Inspected every workflow run and concrete job for head `048503f164cd1f4192d928fd4070134f43e79ccc`; results are recorded below.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Documentation-only handoff; no gameplay fixes | User explicitly stopped further implementation and required durable state first. | none |
| Reuse current branch after resetting it | Existing branch contained only incomplete, unreviewed scaffolding; duplicate branch was unnecessary. | none |
| Do not edit `ACTIVE_WORK.md` | Repository instructions and user requirement forbid manual edit. | none |
| Future OTClient work targets `blakinio/otclient` | User-owned maintained client is the authorized target; `opentibiabr/otclient` is reference-only. | none |
| Do not infer remediation from broad-file overlap | Current finding-bearing functions were re-read; later unrelated edits to shared files are not proof. | none |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_VALIDATION.md` | exclusive | Current-main validation and handoff | complete and verified at `048503f...` |
| `docs/agents/tasks/active/CAN-20260713-equipment-upgrade-handoff-refresh.md` | exclusive | Durable task state, evidence and CI lifecycle | final metadata pending equivalent CI/merge |
| `docs/agents/ACTIVE_WORK.md` | forbidden/read-only | Coordination snapshot | unchanged |
| Source/config/tests/client paths | read_only | Current-state evidence | inspected only |

# Validation and CI

## Local environment

| Command/check | Result | Evidence/limits |
|---|---|---|
| `cd /tmp && rm -rf canary-handoff && git clone --filter=blob:none --no-checkout https://github.com/blakinio/canary.git canary-handoff` | unavailable | `Could not resolve host: github.com`. No local checkout, diff check, Markdown check, ownership tool, build, C++/Lua test, runtime, gameplay or E2E execution. |

## GitHub head `048503f164cd1f4192d928fd4070134f43e79ccc`

| Workflow run | Job | Result | What it proves | What it does not prove |
|---:|---|---|---|---|
| `29242597949` — Agent Task Ownership | `Validate active ownership` | success | Ownership tool compiled; focused ownership tests passed; active tasks validated and ownership index rendered. | No Forge source/runtime/gameplay behavior. |
| `29242597980` — AI Agent Tools | `Validate AI agent tools` | success | AI-agent unit/index/reference/schema/content-pack validation completed. | No Forge-specific runtime/gameplay proof. |
| `29242598112` — CI draft run | `Detect Build Scope` | success | Changed paths were detected. | No compile/test proof. |
| `29242598112` — CI draft run | `Required` | success | The jobs required by that draft scope evaluated successfully. Fast Checks, Lua, builds and smoke were skipped. | Not full CI or runtime proof. |
| `29242668078` — CI ready run | `Detect Build Scope` | success | Ready-event scope resolved correctly. | No behavior proof alone. |
| `29242668078` — CI ready run | `Lua Tests / Run Lua Tests` | success | Repository Lua test suite invoked by this job passed on the recorded head. | No focused live Dust-party or client gameplay scenario. |
| `29242668078` — CI ready run | `Fast Checks / run-checks` | success | clang-format, Stylua, cmake-format diff, Lua API quality/new-binding docs, reviewdog analysis and yamllint passed. | No compiled or runtime Forge behavior. |
| `29242668078` — CI ready run | `Build - Linux / Compile (linux-release)` | success | Linux release CMake/compile and generated Lua API docs check passed. | `Smoke test Canary datapack runtime`, Global smoke, DB import and `Run Tests` were explicitly skipped; no runtime, C++ regression, gameplay or E2E proof. |
| `29242668078` — CI ready run | `Required` | success | Required job aggregation passed after the concrete successful jobs above. | Does not add evidence beyond those concrete jobs. |

Skipped in ready run `29242668078`: Build Docker, macOS, Windows, Docker Quickstart Smoke, Canary datapack runtime smoke, Global datapack runtime smoke, database import and C++ `Run Tests`. These are not reported as passed.

# Failed approaches and dead ends

- Two preliminary scaffolding files were created before the task was narrowed to handoff-only. They were not safe evidence or production changes, had no PR, and were removed by resetting the branch to current `main`; do not recreate them.
- Direct local Git operations remain unavailable due DNS.
- GitHub 422 responses for the already-existing branch and duplicate task creation caused no repository mutation.

# Risks and compatibility

- Runtime: none changed; no runtime proof added.
- Data/migration: none.
- Security: no secrets or private assets.
- Backward compatibility: documentation only.
- Cross-repo rollout: none in this task; F-014–F-019 require a future coordinated Canary + `blakinio/otclient` program.
- Rollback: revert the documentation PR; no persistent runtime state.

# Remaining work

1. Inspect metadata-equivalent checks for the new task-record commit.
2. Recheck main SHA, PR changed files/review threads/mergeability.
3. Enable auto-merge or squash-merge PR #241 when eligible.
4. Create a separate lifecycle cleanup PR moving this task from active to archive; verify and merge it.

# Handoff

## Start here

Read `docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_VALIDATION.md`. The report, this task and live GitHub state are the complete source of truth.

First recommended implementation scope after this documentation lifecycle is complete: F-003–F-005 server-authority validation before mutation. Begin with:

- `src/creatures/players/player.cpp` — `Player::forgeFuseItems`, `Player::forgeTransferItemTier`;
- `tests/integration/game/forge_it.cpp`;
- `tests/unit/players/forge_test.cpp`.

When a local checkout is available, first run:

```text
git fetch origin main
git switch main
git pull --ff-only origin main
python tools/agents/task_ownership.py
rg -n "forgeFuseItems|forgeTransferItemTier|forgeResourceConversion|registerForgeHistoryDescription" src tests
```

Then confirm current CMake presets before building/running focused Forge tests.

## Do not repeat

- DO NOT REOPEN PR #177.
- DO NOT CONTINUE A DELETED HISTORICAL BRANCH.
- DO NOT EDIT `docs/agents/ACTIVE_WORK.md`.
- DO NOT CLAIM FULL FORGE PARITY.
- DO NOT CLAIM GAMEPLAY OR E2E PROOF WITHOUT EXECUTION.
- DO NOT MODIFY `opentibiabr/otclient`.
- DO NOT FIX ALL FINDINGS IN ONE PR.

## Required reads

- `AGENTS.md`
- `docs/agents/README.md`
- `docs/agents/MODULE_CATALOG.md`
- `docs/agents/REPOSITORY_MAP.md`
- `docs/agents/KNOWN_RISKS.md`
- `docs/agents/BUILD_TEST_MATRIX.md`
- `docs/agents/CROSS_REPO_CONTRACTS.md`
- `docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md`
- `docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_VALIDATION.md`
- all overlapping active task records and open PRs at continuation time

## Open questions

- Exact versioned Fiendish difficulty-to-Sliver mapping (F-009).
- Authoritative precision/rounding for Ruse and Amplification (F-010).
- Exact future Canary/`blakinio/otclient` result contract for all Fusion bonuses (F-014–F-019).

# Completion

- Final status: in progress
- PR: #241
- PR state: Ready for review
- Verified content head: `048503f164cd1f4192d928fd4070134f43e79ccc`
- Current metadata commit: created by this update; final checks pending
- Merge commit: pending
- Auto-merge: disabled pending final-head checks
- Review threads: none at verified-head review
- Program record updated: not applicable
- Catalogue updated: not required; no module/interface change
- Changelog updated: not required; no behavior/architecture change
- Archived at: pending
