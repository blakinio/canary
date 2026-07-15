---
task_id: CAN-20260715-oteryn-concrete-target-architecture-blueprint
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: ""
status: active
agent: "GPT-5.5 Thinking"
branch: docs/oteryn-concrete-target-architecture
base_branch: main
created: 2026-07-15T17:04:47+02:00
updated: 2026-07-15T17:04:47+02:00
last_verified_commit: "55f3e4126604ae26fbf09c04c90b96f330bd741d"
risk: low
related_issue: ""
related_pr: ""
depends_on:
  - CAN-20260715-oteryn-target-architecture-contract
blocks: []
owned_paths:
  exclusive:
    - docs/architecture/oteryn-target-server-architecture.md
    - docs/agents/tasks/active/CAN-20260715-oteryn-concrete-target-architecture-blueprint.md
  shared:
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/CHANGELOG.md
  read_only:
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

- [ ] A durable target architecture blueprint defines server, runtime, game/domain, persistence, protocol, Lua/content, tests/tooling and repository/file layout.
- [ ] The blueprint is compatible with clean bootstrap from a pinned then-current `opentibiabr/canary` baseline but does not require a bulk source-tree rewrite.
- [ ] `instances` and fork-specific `multichannel` are explicitly excluded from the initial Oteryn core and first migration waves; they remain future candidates only.
- [ ] The blueprint preserves the canonical 62-module registry as the only module inventory and does not create a second registry.
- [ ] Per-module evaluation explicitly compares upstream Canary, legacy `blakinio/canary` and CrystalServer with source-role-aware evidence rather than plain file similarity.
- [ ] No Oteryn repository identity, branch or SHA is invented and OAM-002 remains blocked.
- [ ] No runtime, gameplay, database, protocol implementation, Lua/datapack, map, OTBM or asset behavior changes.
- [ ] Documentation/changelog/program/contract references are updated consistently.
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

- Program record: `CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION`.
- Open PRs inspected: #384, #316; neither owns the intended architecture paths.
- Active task path with this task ID did not exist before branch creation.
- Exclusive claims: new architecture blueprint and this active task record.
- Shared claims: Oteryn contract, program and changelog.
- Read-only dependencies: registry, TSD/Upstream/Crystal programs and all runtime/data source trees.
- Overlaps: none found.
- Resolution: proceed with documentation/governance only.

# Current state

OAM-001 defined the migration contract but not a concrete server/file architecture. OAM-002 remains blocked because no authorized Oteryn target repository exists. This supporting architecture task fills the design gap without opening OAM-002 or authorizing implementation.

# Plan

1. Define the first-version Oteryn architecture and target repository layout.
2. Define source-role-aware three-way module evaluation against upstream Canary, legacy Canary and CrystalServer.
3. Explicitly defer instances and multichannel from initial core.
4. Link the blueprint from the Oteryn contract/program and update the changelog.
5. Review exact diff, CI, comments/reviews/threads and merge only from a synchronized current base.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Initial Oteryn is a modular monolith, single-world and single-channel | User direction plus minimum-complexity bootstrap; current fork instance/multichannel features are not required for the first target | recorded in architecture blueprint |
| Preserve 62-module registry as logical inventory | Existing canonical registry already owns identity/dependencies; duplicating it would create drift | OAM contract |
| Bootstrap from upstream Canary, then converge toward target ownership layout incrementally | Avoids cloning fork baggage and avoids a risky bulk source-tree rewrite | OAM contract + blueprint |
| CrystalServer remains donor evidence only | Existing comparison program forbids assuming donor code is newer/better or official behavior | existing comparison program |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `docs/architecture/oteryn-target-server-architecture.md` | exclusive | Concrete target architecture and repository layout | planned |
| `docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md` | shared | Link blueprint and preserve implementation blockers | planned |
| `docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md` | shared | Record supporting architecture task and initial-core exclusions | planned |
| `docs/agents/CHANGELOG.md` | shared | Record architecture-level change | planned |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| task-start | live main/open PR/source-head preflight | PASS | GitHub connector evidence; no target repo identity invented |

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
updated_at: 2026-07-15T17:04:47+02:00
head: 55f3e4126604ae26fbf09c04c90b96f330bd741d
branch: docs/oteryn-concrete-target-architecture
pr: none
status: implementing
context_routes:
  - cpp-runtime
  - real-tibia-parity
  - upstream-intelligence
owned_paths:
  - docs/architecture/oteryn-target-server-architecture.md
  - docs/agents/tasks/active/CAN-20260715-oteryn-concrete-target-architecture-blueprint.md
  - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
  - docs/agents/CHANGELOG.md
proven:
  - blakinio/canary main is 55f3e4126604ae26fbf09c04c90b96f330bd741d at task start
  - upstream Canary observed head is a879c9312e34381e8eedf397b8ed44510698b689
  - CrystalServer observed head is fdd2b1f13f53894c584346ef3de43658045c42a7
  - OAM-002 remains blocked by unavailable Oteryn target identity and authorization
  - user excludes instances and multichannel from initial Oteryn implementation
derived:
  - architecture/governance documentation may proceed without opening OAM-002
  - initial target should not carry fork-specific instance or multichannel coupling
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
changed_paths:
  - docs/agents/tasks/active/CAN-20260715-oteryn-concrete-target-architecture-blueprint.md
validation:
  - command: live GitHub preflight
    result: PASS
    evidence: current main and open PRs verified
blockers:
  - OAM-002 remains blocked, but this docs-only architecture task is not blocked
next_action: Create the concrete Oteryn target server architecture blueprint and link it from the OAM contract/program.
```

# Remaining work

1. Create the concrete architecture blueprint and linked contract/program/changelog updates.

# Completion

- Final status: active
- PR: none
- Merge commit: none
- Program record updated: pending
- Catalogue updated: not-applicable unless a new reusable implementation interface is introduced
- Changelog updated: pending
- Archived at: pending
