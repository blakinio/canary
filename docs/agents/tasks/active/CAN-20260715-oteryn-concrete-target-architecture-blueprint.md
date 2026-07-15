---
task_id: CAN-20260715-oteryn-concrete-target-architecture-blueprint
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: ""
status: active
agent: "GPT-5.5 Thinking"
branch: docs/oteryn-concrete-target-architecture
base_branch: main
created: 2026-07-15T17:04:47+02:00
updated: 2026-07-15T17:18:00+02:00
last_verified_commit: "1f27cec3ebe5c10af02d96e42ec2d1ca07aecbdf"
risk: low
related_issue: ""
related_pr: "387"
depends_on:
  - CAN-20260715-oteryn-target-architecture-contract
blocks: []
owned_paths:
  exclusive:
    - docs/architecture/oteryn-target-server-architecture.md
    - docs/agents/tasks/active/CAN-20260715-oteryn-concrete-target-architecture-blueprint.md
  shared:
    - docs/agents/CHANGELOG.md
  read_only:
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/real-tibia/**
    - docs/agents/programs/TIBIA_SYSTEM_DECOMPOSITION_PROGRAM.md
    - docs/agents/programs/UPSTREAM_INTELLIGENCE_PROGRAM.md
    - docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md
    - src/**
    - data/**
    - data-otservbr-global/**
modules_touched: []
reuses:
  - Real Tibia canonical 62-module registry and generated dependency/path indexes
  - Oteryn target architecture and migration contract
  - Upstream Intelligence source roles and revision-pinned discovery
  - CrystalServer comparison evidence model
  - Universal Physical-Client E2E platform
  - existing OTBM analysis pipeline
public_interfaces:
  - Oteryn concrete target server architecture blueprint
cross_repo_tasks: []
---

# Goal

Define the concrete target server architecture for the first Oteryn product baseline: process/runtime model, ownership layers, module boundaries, persistence, protocol, Lua/content boundaries, repository/file layout, dependency rules and three-way source-evaluation rules, without creating or modifying an Oteryn repository and without migrating runtime code.

# Acceptance criteria

- [x] A durable target architecture blueprint defines server, runtime, game/domain, persistence, protocol, Lua/content, tests/tooling and repository/file layout.
- [x] The blueprint is compatible with clean bootstrap from a pinned then-current `opentibiabr/canary` baseline but does not require a bulk source-tree rewrite.
- [x] `instances` and fork-specific `multichannel` are explicitly excluded from the initial Oteryn core and first migration waves; they remain future candidates only.
- [x] The blueprint preserves the canonical 62-module registry as the only module inventory and does not create a second registry.
- [x] Per-module evaluation explicitly compares upstream Canary, legacy `blakinio/canary` and CrystalServer with source-role-aware evidence rather than plain file similarity.
- [x] No Oteryn repository identity, branch or SHA is invented and OAM-002 remains blocked.
- [x] No runtime, gameplay, database, protocol implementation, Lua/datapack, map, OTBM or asset behavior changes.
- [x] Documentation/changelog impact is recorded consistently without changing OAM package state or module dispositions.
- [ ] Current-head GitHub checks and autonomous merge gate are verified before merge.

# Confirmed context

- Writable repository: `blakinio/canary` only.
- Task-start `main`: `55f3e4126604ae26fbf09c04c90b96f330bd741d`.
- Observed upstream comparison head: `opentibiabr/canary@a879c9312e34381e8eedf397b8ed44510698b689`.
- Observed donor comparison head: `zimbadev/crystalserver@fdd2b1f13f53894c584346ef3de43658045c42a7`.
- Open PR #384 is independent E2E load/stress work; open PR #316 is independent Targuna OTBM/donor audit. No Oteryn architecture overlap was found.
- Oteryn target repository/default branch/target SHA/write authorization remain UNKNOWN/BLOCKED.
- The Oteryn contract explicitly permits architecture/evidence work in `blakinio/canary` while target implementation is blocked.
- User decision: initial Oteryn is single-world/single-channel; `instances` and `multichannel` may be documented as future work but are not implemented or migrated now.

# Existing work to reuse

| Module/task/program | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| OAM-001 | Target architecture/evidence rules | `docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md` | Governs all later migration decisions. |
| TSD | Canonical module boundaries and dependencies | `docs/agents/real-tibia/registry/**`, generated indexes | Sole module inventory; no duplicate architecture registry. |
| Upstream Intelligence | Source-role-aware discovery | `docs/agents/programs/UPSTREAM_INTELLIGENCE_PROGRAM.md` | Upstream/donor changes are candidates, never automatic imports. |
| CrystalServer Comparison | Conservative donor evaluation | `docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md` | Distinguishes already-present, superior, missing-fix, partial, dangerous and unverified candidates. |
| Universal E2E | Physical-client proof | existing `tools/e2e/**`, `tests/e2e/**` | Reused later; no second orchestrator. |
| OTBM tooling | World/content evidence | existing `tools/ai-agent/**`, `docs/ai-agent/**` | Reused later; no parser/renderer duplication. |

# Ownership and overlap check

- Program record: `CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION` (read-only for this supporting design task; OAM package state is unchanged).
- Open PRs inspected: #384, #316; neither owns the intended architecture paths.
- Active task path with this task ID did not exist before branch creation.
- Exclusive claims: new architecture blueprint and this active task record.
- Shared claim: architecture changelog.
- Read-only dependencies: Oteryn contract/program, registry, TSD/Upstream/Crystal programs and all runtime/data source trees.
- Overlaps: none found.
- Resolution: proceed with documentation/governance only.

# Current state

OAM-001 defined the migration contract but not a concrete server/file architecture. PR #387 now adds the concrete design blueprint without opening OAM-002 or authorizing implementation. OAM-002 remains blocked because no authorized Oteryn target repository exists.

# Plan

1. Define the first-version Oteryn architecture and target repository layout. — completed.
2. Define source-role-aware three-way module evaluation against upstream Canary, legacy Canary and CrystalServer. — completed.
3. Explicitly defer instances and multichannel from initial core. — completed.
4. Record the architecture-level change in the changelog and durable task/PR state. — completed.
5. Review exact diff, CI, comments/reviews/threads and merge only from a synchronized current base. — in progress.

# Work log

## 2026-07-15T17:05:55+02:00

- Changed: created task branch and active task record; opened draft PR #387.
- Learned: no overlap with open PR #384 or #316; OAM-002 blockers remain unchanged.
- Failed/blocked: target implementation remains blocked by missing Oteryn repository identity/authorization, but documentation design is permitted.
- Result: architecture task visible and bounded.

## 2026-07-15T17:18:00+02:00

- Changed: added `docs/architecture/oteryn-target-server-architecture.md` and architecture changelog entry.
- Learned: initial target can preserve clean upstream bootstrap while converging incrementally toward explicit ownership roots; no bulk source-tree rewrite is required.
- Failed/blocked: none for documentation scope.
- Result: concrete architecture covers runtime, layering, repository tree, module contracts, persistence, protocol, Lua/content, world/OTBM, tests, build, operations and three-way source evaluation; instances/multichannel are future-only.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Initial Oteryn is a modular monolith, single-world and single-channel | User direction plus minimum-complexity bootstrap; current fork instance/multichannel features are not required for the first target | recorded in architecture blueprint |
| Preserve 62-module registry as logical inventory | Existing canonical registry already owns identity/dependencies; duplicating it would create drift | OAM contract |
| Bootstrap from upstream Canary, then converge toward target ownership layout incrementally | Avoids cloning fork baggage and avoids a risky bulk source-tree rewrite | OAM contract + blueprint |
| CrystalServer remains donor evidence only | Existing comparison program forbids assuming donor code is newer/better or official behavior | existing comparison program |
| Do not add speculative instance/multichannel abstractions to initial core | Future features must not increase initial core coupling before a proven need exists | user direction + blueprint |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `docs/architecture/oteryn-target-server-architecture.md` | exclusive | Concrete target architecture and repository layout | implemented |
| `docs/agents/CHANGELOG.md` | shared | Record architecture-level change | implemented |
| `docs/agents/tasks/active/CAN-20260715-oteryn-concrete-target-architecture-blueprint.md` | exclusive | Durable task/checkpoint state | implemented |
| `docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md` | read_only | Governing OAM contract referenced by blueprint | unchanged |
| `docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md` | read_only | OAM queue/blockers; no package state changed by this support task | unchanged |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| task-start | live main/open PR/source-head preflight | PASS | GitHub connector evidence; no target repo identity invented |
| `1f27cec3ebe5c10af02d96e42ec2d1ca07aecbdf` | changed-file inventory | PASS | only architecture blueprint, task record and changelog before this checkpoint update |
| current head | required GitHub checks | not-run/pending | verify after final task checkpoint commit |

# Failed approaches and dead ends

- None affecting repository state. No attempt was made to create or write an Oteryn repository.

# Risks and compatibility

- Runtime: documentation only; no runtime change.
- Data/migration: no schema/data/map migration.
- Security: no security implementation change.
- Backward compatibility: no code/interface behavior change.
- Cross-repo rollout: none; all external repositories remain read-only.
- Rollback: revert documentation PR if architecture contract needs revision.

# Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-15T17:18:00+02:00
head: 1f27cec3ebe5c10af02d96e42ec2d1ca07aecbdf
branch: docs/oteryn-concrete-target-architecture
pr: 387
status: validating
context_routes:
  - cpp-runtime
  - real-tibia-parity
  - upstream-intelligence
owned_paths:
  - docs/architecture/oteryn-target-server-architecture.md
  - docs/agents/tasks/active/CAN-20260715-oteryn-concrete-target-architecture-blueprint.md
  - docs/agents/CHANGELOG.md
proven:
  - blakinio/canary main was 55f3e4126604ae26fbf09c04c90b96f330bd741d at task start
  - upstream Canary observed head is a879c9312e34381e8eedf397b8ed44510698b689
  - CrystalServer observed head is fdd2b1f13f53894c584346ef3de43658045c42a7
  - OAM-002 remains blocked by unavailable Oteryn target identity and authorization
  - user excludes instances and multichannel from initial Oteryn implementation
  - PR 387 contains documentation/governance only
  - concrete architecture blueprint and changelog entry are implemented
derived:
  - architecture/governance documentation can guide later OAM packages without opening OAM-002
  - initial target should not carry fork-specific instance or multichannel coupling
  - target tree is a convergence destination, not authorization for a bulk source-tree refactor
unknown:
  - Oteryn target repository
  - Oteryn target default branch
  - Oteryn target task-start SHA
  - Oteryn target write authorization
conflicts: []
first_failure:
  marker: OAM-002 target identity gate
  evidence: Oteryn target repository/default branch/SHA/write authorization unavailable
rejected_hypotheses:
  - copy legacy fork layout wholesale: prohibited by OAM contract
  - copy CrystalServer architecture wholesale: donor role is comparison-only
  - include instances or multichannel in initial core: explicitly rejected by user direction
changed_paths:
  - docs/agents/CHANGELOG.md
  - docs/agents/tasks/active/CAN-20260715-oteryn-concrete-target-architecture-blueprint.md
  - docs/architecture/oteryn-target-server-architecture.md
validation:
  - command: live GitHub preflight
    result: PASS
    evidence: current main and open PRs verified at task start
  - command: PR changed-file inventory
    result: PASS
    evidence: only intended documentation/governance paths
blockers:
  - OAM-002 remains blocked, but this docs-only architecture task is not blocked
next_action: Review the exact PR #387 diff and current-head checks; synchronize with main if it advances before merge.
```

# Remaining work

1. Review exact current-head diff and GitHub checks, then complete the autonomous merge gate.

# Handoff

## Start here

Read this task, PR #387 and `docs/architecture/oteryn-target-server-architecture.md`.

## Do not repeat

- Do not create an Oteryn repository or open OAM-002 without explicit target authorization.
- Do not add `instances` or `multichannel` to the initial Oteryn core.
- Do not create a second module registry or three-way auto-merge system.

## Required reads

- `AGENTS.md`
- `docs/agents/REPOSITORY_MAP.md`
- `docs/agents/CONTEXT_ROUTING.md`
- `docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md`
- `docs/architecture/oteryn-target-server-architecture.md`
- current PR #387

## Open questions

- Oteryn target repository identity and write authorization remain unresolved by design.

# Completion

- Final status: active
- PR: #387
- Merge commit: none
- Program record updated: not-applicable; no OAM package state changed
- Catalogue updated: not-applicable; no reusable runtime interface was implemented
- Changelog updated: yes
- Archived at: pending lifecycle-only PR after feature merge
