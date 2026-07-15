---
task_id: CAN-20260715-oteryn-target-architecture-contract
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: ""
status: active
agent: "GPT-5.5 Thinking"
branch: docs/oteryn-target-architecture-contract
base_branch: main
created: 2026-07-15T15:28:18+02:00
updated: 2026-07-15T15:41:06+02:00
last_verified_commit: "775d1ad2738601ed99a3f1df3d71c427a8107e6a"
risk: low
related_issue: ""
related_pr: "383"
depends_on: []
blocks:
  - OAM-002
owned_paths:
  exclusive:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/tasks/active/CAN-20260715-oteryn-target-architecture-contract.md
  shared:
    - docs/agents/CHANGELOG.md
  read_only:
    - AGENTS.md
    - docs/agents/README.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CROSS_REPO_CONTRACTS.md
    - docs/agents/programs/TIBIA_SYSTEM_DECOMPOSITION_PROGRAM.md
    - docs/agents/programs/REAL_TIBIA_PARITY_PROGRAM.md
    - docs/agents/programs/UPSTREAM_INTELLIGENCE_PROGRAM.md
    - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
    - docs/agents/real-tibia/**
    - docs/agents/tasks/active/CAN-20260714-targuna-donor-isolation.md
    - .github/workflows/universal-agent-e2e.yml
    - tools/e2e/**
    - tests/e2e/**
modules_touched: []
reuses:
  - Real Tibia canonical module registry-as-code
  - Upstream Intelligence source registry and source-role-aware mapper
  - Universal Physical-Client E2E platform
  - existing OTBM analysis pipeline
public_interfaces:
  - Oteryn target architecture and migration evidence contract
cross_repo_tasks: []
---

# Goal

Create the first documentation-only package for a new Oteryn architecture and migration program. Define an explicit target architecture contract, evidence-backed module migration dispositions, baseline pinning rules and dependency-aware bounded package queue without changing runtime, gameplay, protocol, database, client, OTBM, map, assets or the canonical module registry.

# Acceptance criteria

- [x] Do not reactivate `CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION` or create TSD-014/TSD-015.
- [x] Create exactly one new Oteryn architecture/migration program after confirming no duplicate live program, task or PR.
- [x] Define the target architecture contract and migration evidence contract.
- [x] Define `REUSE`, `ADAPT`, `REVALIDATE`, `REWRITE`, `DO_NOT_MIGRATE` and `EXPERIMENTAL_ONLY` with evidence gates.
- [x] Keep canonical modules from `docs/agents/real-tibia/registry/modules/*.yaml` as the migration decision unit.
- [x] Record target repository and exact target baseline as unavailable rather than inventing them.
- [x] Define dependency-aware bounded package ordering from the current canonical dependency graph.
- [x] Reuse the existing Upstream Intelligence, Universal Physical-Client E2E and OTBM platforms; create no duplicate registry, watcher, mapper, parser, renderer or E2E orchestrator.
- [x] Identify the exact next bounded task and its blocker.
- [x] Change documentation/governance only; no runtime, gameplay, DB, protocol implementation, client, map, OTBM or asset changes.
- [x] Review exact changed files and current-head CI before readiness/merge.
- [x] Module catalogue impact handled: no reusable implementation/module interface is introduced, so no catalogue edit is required.
- [x] Changelog records the architecture-level contract.
- [x] Cross-repository impact handled: no external repository write and no migration until an explicit Oteryn repository/baseline exists.
- [ ] Autonomous merge gate satisfied.

# Confirmed context

- Writable repository: `blakinio/canary` only.
- Task-start `main`: `d60d63dc37689ccc9ff7e9c37cfa2ebe71cbdc51`.
- Live compare at task start `d60d63d...` to `main`: identical.
- Only open PR at task start: draft PR #316 `audit(otbm): isolate bounded Targuna donor clusters`.
- PR #316 owns only its Targuna audit workflow/script/task and planned Targuna reports; it does not overlap this task's exclusive paths.
- PR #316 had no comments, submitted reviews or unresolved review threads at preflight.
- `CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION` is completed; its queue ends at TSD-013.
- Canonical Real Tibia registry count: 62 modules.
- All 62 modules remain conservatively classified `REVALIDATE` for future Oteryn decisions.
- `docs/agents/real-tibia/registry/**` remains the only canonical module registry.
- Upstream Intelligence program is active; UI-001/UI-001A are completed and UI-002 remains planned. Mapping is discovery-only.
- Universal Physical-Client E2E PR #245 is merged as `9fc11e04dc5040d1ea18d02e15dac1df47f3fe64`; the platform provides one reusable login/relog baseline.
- A later independent lifecycle-only PR #382 was opened to archive the stale E2E active task record; it changes only that task's active/archive paths and does not overlap this task.
- No accessible repository named Oteryn was found during live GitHub repository search.
- `docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md` did not exist on task-start `main`.
- No task-start open PR implemented an Oteryn target architecture contract.
- Target Oteryn repository identity: unavailable.
- Target Oteryn default branch: unavailable.
- Target Oteryn baseline SHA: unavailable.
- Therefore this task is limited to a design/contract package and cannot authorize migration implementation.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| Real Tibia registry-as-code | canonical module identity, dependencies, paths, source roles and maturity | `docs/agents/real-tibia/**` | Prevents a second taxonomy or migration registry. |
| TSD completed program | 62-module decomposition and conservative `REVALIDATE` baseline | `docs/agents/programs/TIBIA_SYSTEM_DECOMPOSITION_PROGRAM.md` | Provides the legacy inventory without migration authorization. |
| Upstream Intelligence | read-only source discovery and source-role-aware mapping | `docs/agents/programs/UPSTREAM_INTELLIGENCE_PROGRAM.md` | Reuse for candidate discovery; path matches remain hints only. |
| Universal Physical-Client E2E | reusable physical-client validation | PR #245; `tools/e2e/**`; `tests/e2e/**` | Future migrated modules should add bounded scenarios instead of a second platform. |
| OTBM analysis pipeline | world index, semantic diff, script resolution, reachability, spawn/NPC and storage evidence | existing `tools/ai-agent/**` and `docs/ai-agent/**` | Future world-content migration evidence must reuse it. |

# Ownership and overlap check

- Program record: new `CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION` proposed by this task only.
- Task-start open PR inspected: #316.
- Active task inspected for #316: `CAN-20260714-targuna-donor-isolation`.
- Stale E2E active-path record inspected; feature PR #245 is merged and independent lifecycle PR #382 now owns only its archival paths.
- Agent Task Ownership run #1312 succeeded on feature head `775d1ad2738601ed99a3f1df3d71c427a8107e6a`.
- Exclusive claims: new Oteryn program file, new target contract, this task record.
- Shared claim: `docs/agents/CHANGELOG.md` only.
- Read-only dependencies: registry, existing programs, E2E platform and OTBM tooling.
- Overlaps: none found with PR #316 or PR #382.
- Resolution: proceed with docs-only task; repeat ownership/current-head checks after every head change before merge.

# Current state

PR #383 is open and ready for review. The feature package contains only the four intended documentation/governance paths. No Oteryn implementation or external repository change is authorized.

# Plan

1. Add the new Oteryn architecture/migration program record.
2. Add the target architecture and migration evidence contract.
3. Add an architecture-level changelog entry.
4. Open a draft PR early and verify ownership CI.
5. Review comments, reviews, unresolved threads, exact changed files and current-head required checks.
6. Mark ready and squash-merge only if every gate is green.
7. Use a separate lifecycle-only PR to archive this task.
8. Stop before OAM-002 unless an explicit Oteryn repository and exact target baseline become available under authorized ownership.

# Work log

## 2026-07-15T15:28:18+02:00

- Changed: claimed the bounded docs-only architecture-contract task on a branch created from exact current `main`.
- Learned: Oteryn repository/baseline are not available; PR #316 is the only task-start live PR and does not overlap; PR #245 is merged but its active task metadata is stale.
- Failed/blocked: target repository identity/default branch/baseline cannot be pinned because no accessible Oteryn repository exists.
- Result: first package may define the contract only; migration implementation remains blocked.

## 2026-07-15T15:41:06+02:00

- Changed: adopted the already-created same-scope branch/PR #383 instead of duplicating it; corrected one `then-current` wording typo in the contract and synchronized this task record with live PR/CI state.
- Learned: independent PR #382 now archives the stale E2E task metadata and does not overlap OAM-001 ownership.
- Verified: feature head `775d1ad2738601ed99a3f1df3d71c427a8107e6a` had successful Agent Task Ownership #1312 and CI #2438, exactly four intended changed files, and no comments/reviews/unresolved threads before ready transition.
- Result: PR #383 was moved from draft to ready; all checks must be re-evaluated on the new head created by this task-record synchronization before merge.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Keep the 62 canonical module records as migration units. | Registry-as-code is the existing source of truth; TSD explicitly forbids a second registry. | — |
| Default every module to `REVALIDATE` until target-side evidence exists. | TSD-013 closed with all 62 modules at `REVALIDATE`; target repo/baseline are absent. | — |
| Treat Oteryn repo/baseline as blocking inputs, not guessed values. | No accessible Oteryn repository was found during preflight. | — |
| Reuse existing Upstream Intelligence, E2E and OTBM platforms. | Existing governance and merged platform/tooling prohibit parallel replacements. | — |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md` | exclusive | long-lived program and bounded queue | delivered |
| `docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md` | exclusive | target architecture, evidence and migration disposition contract | delivered |
| `docs/agents/tasks/active/CAN-20260715-oteryn-target-architecture-contract.md` | exclusive | task ownership and handoff | active |
| `docs/agents/CHANGELOG.md` | shared | architecture-level discovery note | delivered |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| `775d1ad2738601ed99a3f1df3d71c427a8107e6a` | Agent Task Ownership #1312 | passed | Current ownership validation before this task-record synchronization. |
| `775d1ad2738601ed99a3f1df3d71c427a8107e6a` | repository CI #2438 | passed | Current-head CI before ready transition. |
| `775d1ad2738601ed99a3f1df3d71c427a8107e6a` | exact changed-file review | passed | Exactly four intended docs/governance paths. |
| `775d1ad2738601ed99a3f1df3d71c427a8107e6a` | comments/reviews/unresolved threads | passed | None observed before ready transition. |
| pending new head | ready-state required checks | pending | Must complete after this task-record synchronization before merge. |

Never write `passed` without verification on the stated commit.

# Failed approaches and dead ends

- Do not reactivate TSD or create TSD-014/TSD-015.
- Do not create a second module/migration registry.
- Do not invent an Oteryn repository, branch or SHA.
- Do not clone `blakinio/canary` wholesale into Oteryn.
- Do not use donor/upstream path matches as migration authorization.
- Do not create a second E2E platform, Upstream Intelligence watcher/mapper or OTBM analysis stack.

# Risks and compatibility

- Runtime: none; documentation/governance only.
- Data/migration: none; no DB/schema/data migration.
- Security: no credentials, production access or external writes.
- Backward compatibility: no runtime/API/protocol behavior changes.
- Cross-repo rollout: blocked until Oteryn repository identity, authorization and exact baseline exist.
- Rollback: revert the documentation commit/PR.

# Remaining work

1. Verify required CI/review state on the current post-synchronization head and merge if clean.
2. Archive this task in a separate lifecycle-only PR.
3. OAM-002 remains blocked pending explicit Oteryn repository identity and exact target baseline.

# Handoff

## Start here

Read this task, `docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md`, `docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md`, the completed TSD program, current Real Tibia registry and live GitHub state.

## Do not repeat

Do not reinterpret `REVALIDATE` as `REUSE`, create a parallel migration registry, or migrate code before target repository/baseline/architecture evidence exists.

## Required reads

- `AGENTS.md`
- `docs/agents/README.md`
- `docs/agents/MODULE_CATALOG.md`
- `docs/agents/programs/TIBIA_SYSTEM_DECOMPOSITION_PROGRAM.md`
- `docs/agents/programs/REAL_TIBIA_PARITY_PROGRAM.md`
- `docs/agents/programs/UPSTREAM_INTELLIGENCE_PROGRAM.md`
- `docs/agents/programs/E2E_AUTOMATION_PROGRAM.md`
- `docs/agents/real-tibia/**`
- all overlapping active task records and live open PRs

## Open questions

- Oteryn target repository identity, default branch and exact baseline SHA are unavailable.
- Repository ownership/write authorization for a future Oteryn target is unavailable.

# Completion

- Final status: active
- PR: #383
- Merge commit:
- Program record updated: delivered; lifecycle completion pending
- Catalogue updated: not-applicable
- Changelog updated: yes
- Archived at:
