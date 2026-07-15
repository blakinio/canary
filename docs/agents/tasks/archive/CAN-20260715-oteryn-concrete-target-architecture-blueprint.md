---
task_id: CAN-20260715-oteryn-concrete-target-architecture-blueprint
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: ""
status: completed
agent: "GPT-5.5 Thinking"
branch: docs/oteryn-concrete-target-architecture
base_branch: main
created: 2026-07-15T17:04:47+02:00
completed: 2026-07-15T17:27:00+02:00
last_verified_commit: "fd37e93249187de2410c44d0da0494794d94553e"
risk: low
related_issue: ""
related_pr: "387"
depends_on:
  - CAN-20260715-oteryn-target-architecture-contract
blocks: []
owned_paths:
  exclusive:
    - docs/architecture/oteryn-target-server-architecture.md
    - docs/agents/tasks/archive/CAN-20260715-oteryn-concrete-target-architecture-blueprint.md
  shared:
    - docs/agents/CHANGELOG.md
  read_only:
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/real-tibia/**
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

# Result

The supporting Oteryn concrete architecture task is completed.

- Feature PR: #387.
- Final feature head: `2e862b57fbbbb068fc4a4c1f96eed3b9ba95628c`.
- Squash merge: `fd37e93249187de2410c44d0da0494794d94553e`.
- Feature changed files: exactly 3.
- Runtime/gameplay/database/protocol implementation/client/Lua/datapack/OTBM/map/asset behavior changes: 0.
- Oteryn repository created or modified: no.
- OAM-002 opened: no.

# Architecture established

The merged blueprint is:

```text
docs/architecture/oteryn-target-server-architecture.md
```

It establishes the first-version target as:

```text
single game-server process
+ single authoritative world runtime
+ single logical game-state authority
+ single channel
+ modular monolith
+ explicit app/engine/platform/protocol/scripting/game ownership
+ external database through explicit persistence boundaries
```

The destination repository layout is a convergence target, not authorization for a bulk source-tree rewrite. New Oteryn-owned code should follow explicit target ownership roots while inherited upstream paths may remain temporarily until bounded module migration requires movement.

# User-directed exclusions

The user explicitly directed that `instances` and `multichannel` are not implemented in initial Oteryn.

The architecture therefore preserves:

- canonical `instances` module remains `REVALIDATE` and is skipped/deferred from initial migration waves;
- fork-specific `src/game/multichannel/**` is future experimental evidence only;
- no new canonical multichannel module was invented;
- no initial-core abstraction is required solely to anticipate instances or multichannel;
- neither feature may block the single-world/single-channel initial core.

# Three-way evidence model

Each later bounded module package evaluates semantic evidence from exact pinned revisions of:

```text
then-current upstream opentibiabr/canary
vs
legacy blakinio/canary
vs
zimbadev/crystalserver when relevant
+
question-specific Real Tibia evidence when parity is claimed
```

This is comparison evidence, not a three-way text merge or automatic import path. CrystalServer remains donor-only evidence.

Design-time observed revisions used while writing the blueprint were:

```text
blakinio/canary@55f3e4126604ae26fbf09c04c90b96f330bd741d
opentibiabr/canary@a879c9312e34381e8eedf397b8ed44510698b689
zimbadev/crystalserver@fdd2b1f13f53894c584346ef3de43658045c42a7
```

They are not the future OAM-002 target baseline.

# Validation and merge gate

Final feature head `2e862b57fbbbb068fc4a4c1f96eed3b9ba95628c`:

- Agent Task Ownership #1344: success;
- initial CI #2469: success;
- ready-state CI #2470: success;
- ready-state Fast Checks: success;
- ready-state Lua Tests: success;
- ready-state Linux release: success;
- ready-state Required: success;
- exact changed-file review: only `docs/agents/CHANGELOG.md`, this task's active record and `docs/architecture/oteryn-target-server-architecture.md`;
- PR comments: none;
- submitted reviews: none;
- unresolved review threads: none;
- mergeable immediately before merge: true;
- current `main` immediately before merge: `55f3e4126604ae26fbf09c04c90b96f330bd741d`;
- branch compare immediately before merge: ahead 4, behind 0;
- squash merge used exact-head guard for `2e862b57fbbbb068fc4a4c1f96eed3b9ba95628c`.

# Safety limits preserved

- No write was made to `opentibiabr/canary`, `opentibiabr/otclient`, `opentibiabr/remeres-map-editor`, `opentibiabr/client-editor` or `zimbadev/crystalserver`.
- No Oteryn target repository was invented or modified.
- No canonical module received a migration disposition stronger than `REVALIDATE`.
- No second module registry, taxonomy, dependency graph, Upstream Intelligence mapper, E2E platform or OTBM stack was created.
- No bulk source-tree, datapack, map or donor import was authorized.

# Program state

This supporting architecture task does not change numbered OAM package state:

- OAM-001: completed.
- OAM-002: still blocked pending explicit Oteryn target repository identity, default branch, exact target/upstream baseline and write authorization.
- OAM-003+: remain blocked behind OAM-002 and their dependency gates.

# Completion

- Final status: completed.
- Feature PR: #387.
- Feature squash merge: `fd37e93249187de2410c44d0da0494794d94553e`.
- Catalogue updated: not applicable; no reusable runtime interface was implemented.
- Changelog updated: yes, in feature PR #387.
- Archived through separate lifecycle-only PR.
