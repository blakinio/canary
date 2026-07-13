---
task_id: CAN-20260713-equipment-upgrade-handoff-refresh
program_id: ""
coordination_id: ""
status: in_progress
agent: ChatGPT
branch: fix/equipment-upgrade-validation-2
base_branch: main
created: 2026-07-13T10:16:00Z
updated: 2026-07-13T10:16:00Z
last_verified_commit: d4eeab3db322f26ee72d7f0ad958d35dc9bd007d
risk: low
related_issue: ""
related_pr: ""
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
    - src/creatures/players/player.cpp
    - src/game/game.cpp
    - src/server/network/protocol/protocolgame.cpp
    - src/config/configmanager.cpp
    - config.lua.dist
    - data/libs/systems/exaltation_forge.lua
    - src/utils/tools.cpp
    - tests/integration/game/forge_it.cpp
    - tests/unit/players/forge_test.cpp
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

- [ ] `docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_VALIDATION.md` identifies current `main`, historical PRs and the retired historical branch accurately.
- [ ] F-001–F-024 are reclassified against current `main` with evidence level, remaining proof and bounded follow-up scope.
- [ ] Current open Forge PRs/tasks and post-#177 relevant changes are recorded.
- [ ] Local checkout limitation and exact DNS error are recorded; no unexecuted local test is reported as passed.
- [ ] Changed files remain documentation/task only and exclude `docs/agents/ACTIVE_WORK.md`.
- [ ] Current-head GitHub checks and concrete jobs are inspected and recorded.
- [ ] PR is ready, squash-merged and task lifecycle cleanup is completed unless a real blocker is recorded.
- [ ] Module catalogue impact handled: no reusable interface/module change, therefore no catalogue edit required.
- [ ] Changelog impact handled: no behavior or architecture change, therefore no changelog edit required.
- [ ] Cross-repository impact handled: future client work targets `blakinio/otclient`; no cross-repository write in this task.

# Confirmed context

- Writable repository: `blakinio/canary` only.
- Current `main` at task start: `d4eeab3db322f26ee72d7f0ad958d35dc9bd007d`.
- Existing branch reused: `fix/equipment-upgrade-validation-2`; it was force-reset through the GitHub API to the current `main` before this task record was created.
- The reset removed two incomplete experimental files (`.github/workflows/equipment-upgrade-phase1.yml` and `tools/ai-agent/apply_equipment_upgrade_phase1.py`) from the branch; they were never part of a PR and are not retained.
- Historical merge baseline:
  - PR #89 merged as `209289d38e64aafe7ce3e036867bb632cd0363b8`.
  - PR #110 merged as `84f5c09263f459d726fbc7b9f79557b2cbb0801d`.
  - PR #177 merged as `f1d217c43e8e302978f533212e6aa9d1ce2b77c8`; head was `05134a4c96083c9b21e5e86a5e51dcfc3f53bee6`.
- `validation/equipment-upgrade` is historical and must not be continued or reopened.
- No open Forge-specific PR was found in the current repository review; PR #222 only establishes future shared E2E ownership and does not remediate Forge.
- No active Forge-specific task was identified before creating this task.

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
- Active tasks inspected: current task records visible on `main`; no Equipment Upgrade task overlapped the owned report path.
- Ownership checker result: not run locally because the repository could not be cloned due DNS failure.
- Exclusive claims: the Equipment Upgrade report and this task record only.
- Shared claims: none.
- Read-only dependencies: source/config/tests/contracts listed in front matter.
- Overlaps: none identified.
- Resolution: proceed with documentation-only refresh; do not edit `ACTIVE_WORK.md`.

# Current state

The report on `main` still presents PR #177 and `validation/equipment-upgrade` as current. Current source review confirms that many findings remain open, while F-007/F-008/F-013 retain static remediation but no focused runtime/gameplay proof. A complete current-main table is being written into the report.

# Plan

1. Reverify PR #89, #110 and #177 metadata and merge commits.
2. Compare #177 merge to current `main` and inspect current Forge-relevant source/config/client/test paths.
3. Reclassify F-001–F-024 with explicit evidence boundaries.
4. Update the durable report and this task record.
5. Open/update a documentation-only PR, inspect all current-head checks/jobs, mark ready and squash-merge.
6. Perform lifecycle/archive cleanup after merge.

# Work log

## 2026-07-13T10:16:00Z

- Changed: reset `fix/equipment-upgrade-validation-2` to current `main`; created this task record.
- Learned: the original report is stale; the current `main` contains 77 commits after PR #177, including changes to `game.cpp`, `protocolgame.cpp` and `monster.cpp`, but not to the principal Forge implementation files `player.cpp`, `config.lua.dist`, `configmanager.cpp`, `exaltation_forge.lua`, `tools.cpp` or Forge tests.
- Failed/blocked: local clone command failed: `git clone --filter=blob:none --no-checkout https://github.com/blakinio/canary.git canary-handoff` -> `fatal: unable to access 'https://github.com/blakinio/canary.git/': Could not resolve host: github.com`.
- Result: GitHub API is the authoritative execution path for this task; local checkout/build/test evidence is unavailable.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Documentation-only handoff; no gameplay fixes | User explicitly stopped further implementation and required durable state first. | none |
| Reuse current branch after resetting it | Existing branch existed and contained only incomplete, unreviewed scaffolding; duplicate branch is unnecessary. | none |
| Do not edit `ACTIVE_WORK.md` | Repository instructions make task files/live PRs authoritative and forbid manual index edits. | none |
| Future OTClient work targets `blakinio/otclient` | User-owned maintained client is the authorized target; `opentibiabr/otclient` is reference-only. | none |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_VALIDATION.md` | exclusive | Current-main validation and handoff | in progress |
| `docs/agents/tasks/active/CAN-20260713-equipment-upgrade-handoff-refresh.md` | exclusive | Durable task state, evidence and CI lifecycle | in progress |
| `docs/agents/ACTIVE_WORK.md` | forbidden/read-only | Coordination snapshot | unchanged |
| Source/config/tests/client paths | read_only | Current-state evidence | inspected only |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| `d4eeab3d...` | local `git clone --filter=blob:none --no-checkout https://github.com/blakinio/canary.git canary-handoff` | unavailable | DNS: `Could not resolve host: github.com`; therefore no local diff check, Markdown check, ownership tool, build or test was executed. |
| pending | PR current-head GitHub checks | pending | Concrete run IDs/jobs will be added after PR creation. |

Never write `passed` without verification on the stated commit.

# Failed approaches and dead ends

- Two preliminary scaffolding files were created before the user narrowed the task to handoff-only. They were not safe evidence or production changes, had no PR, and the branch was reset to current `main`; they must not be recreated.
- Direct local Git operations are unavailable in this environment due DNS. Do not imply that CI has already replaced unrun local tests; list each executed CI job separately.

# Risks and compatibility

- Runtime: none changed; no runtime proof is added.
- Data/migration: none.
- Security: no secrets or private assets.
- Backward compatibility: documentation only.
- Cross-repo rollout: none in this task; F-014–F-019 require a future coordinated Canary + `blakinio/otclient` program.
- Rollback: revert the documentation PR; no persistent runtime state.

# Remaining work

1. Finish the current-main finding table and exact handoff.
2. Create/update draft PR and verify changed-file boundary.
3. Inspect current-head workflow jobs/logs and merge if green.
4. Archive this task after merge.

# Handoff

## Start here

Read `docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_VALIDATION.md` after this task updates it. The report, this task and live GitHub state are the complete source of truth.

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
- PR: pending
- Merge commit: pending
- Program record updated: not applicable
- Catalogue updated: not required; no module/interface change
- Changelog updated: not required; no behavior/architecture change
- Archived at: pending
