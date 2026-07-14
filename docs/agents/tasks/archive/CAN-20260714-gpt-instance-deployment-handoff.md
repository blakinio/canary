---
task_id: CAN-20260714-gpt-instance-deployment-handoff
program_id: CAN-PROGRAM-INSTANCED-TEST-ARENA
coordination_id: GPT-INSTANCE-DEPLOYMENT-HANDOFF
status: completed
agent: "GPT-5.6 Thinking"
branch: docs/archive-gpt-instance-deployment-work
base_branch: main
created: 2026-07-14T18:54:20+02:00
updated: 2026-07-14T18:54:20+02:00
last_verified_commit: "709693b4cca42214c52e63ea15a1a22b93f9a113"
risk: low
related_issue: ""
related_pr: ""
depends_on: []
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/archive/CAN-20260714-gpt-instance-deployment-handoff.md
  shared: []
  read_only:
    - docs/agents/ACTIVE_WORK.md
    - docs/architecture/CANARY_ENGINE_PROJECT_HANDOFF.md
    - docs/architecture/instance-manager.md
    - docs/architecture/instanced-test-arena.md
    - docs/agents/programs/INSTANCED_TEST_ARENA_PROGRAM.md
    - src/**
    - data/**
    - tests/**
    - .github/workflows/**
modules_touched:
  - AI content deployment
  - CI required checks
  - dependency injection migration
  - InstanceManager
  - InstanceRegionPool
  - InstanceCreatureBinder
  - creature ownership policy
reuses:
  - existing Canary deployment pipeline
  - existing dependency-injection container
  - existing InstanceManager and region-pool foundation
  - existing repository task and architecture handoffs
public_interfaces:
  - archived session handoff only
cross_repo_tasks: []
---

# Goal

Archive the completed work performed in the ChatGPT project conversation that established the reviewed-content deployment path, repaired required CI checks, connected instance lifecycle to configured map regions, and delivered the stable-ID creature ownership path through the real `Creature::setMaster` call site.

This record also releases all path ownership and prevents a future agent from repeating work that entered `main` after this conversation's direct implementation phase.

# Archive baseline

- Repository: `blakinio/canary`.
- Verified `main` when this archive branch was created: `709693b4cca42214c52e63ea15a1a22b93f9a113`.
- Archive timestamp: `2026-07-14T18:54:20+02:00`.
- No local checkout, local build, or local working-tree state is claimed by this archive operation. Repository state was verified through GitHub metadata and current repository files.

# Work completed in this conversation

## Deployment, DI, handoff, and CI reliability

The conversation completed or supervised the following merged work:

- PR #103 — atomic reviewed-content release engine with staging, active switch, manifest, rollback, and dry-run behavior;
- PR #111 — initial `CANARY_ENGINE_PROJECT_HANDOFF.md` architecture handoff;
- PR #117 — clean `SharedPtrManager` DI migration, superseding unmerged PRs #106 and #112;
- PR #118 — real Canary preflight and post-switch staging validation with automatic rollback;
- PR #119 — `Scripts` DI migration;
- PR #125 — approved AI-promotion handoff materialization into a deployment overlay;
- PR #132 — always emit the required Linux release check when CI runs;
- PR #141 — run main CI for every pull request so documentation/path-only changes cannot leave a required check permanently `Expected`;
- PR #150 — refresh the engine architecture handoff to the then-current repository state.

Known exact merge commits retained from the session:

- #103: `9b966b59b5c59a8097e6caf5ce365645bf0f3a8e`;
- #111: `c5944f5ad48446b389450be672b286d340998e07`;
- #117: `abfbe8679e926d5f4ac31032b6fff9cdf683569a`;
- #132: `107c0481f7037c4432412df2df47a599cdaf2969`.

## Instance lifecycle and creature ownership

The conversation then delivered the following merged slices:

- PR #151 — make `InstanceManager` own and reserve concrete configured `InstanceMapRegion` records; release only after successful cleanup; quarantine a dirty region on cleanup failure;
- PR #159 — stable runtime creature-ID ownership registry, deterministic enumeration, same-owner idempotency, cross-instance rejection, cleanup-time unregister, and region quarantine while owned IDs remain;
- PR #163 — pointer-free summon ownership inheritance and interaction relation policy;
- PR #168 — `InstanceCreatureBinder`, adapting real runtime objects exposing `getID()` to the authoritative stable-ID registry without retaining creature pointers;
- PR #174 — compensating `inheritAndApply(...)` transaction with rollback on false/exception and protection against an ownership-change race during rollback;
- PR #180 — real `Creature::setMaster(..., InstanceCreatureBinder&)` integration with runtime `Monster` tests for normal-world compatibility, same-instance inheritance/reassignment, cross-instance rejection, owned/unowned rejection, and master clearing without erasing the instance boundary.

Known exact merge commits:

- #151: `95244309453e980ac0377379f8ba5605ca3aba6b`;
- #159: `74ea517d13333248d0e0868a5b212eced5ef24dc`;
- #163: `dbcc809bac57bb78425ca39c2523c723cef79bb0`;
- #168: `2cd7ecacef872fe247833515602d670626a9ff18`;
- #174: `409685766e871859775d3286fb989d9d7b0e4533`;
- #180: `f04c6743144648aa67be8281f96cbd1bab958a8d`.

Documentation synchronization PRs created during that sequence included #158, #162, #167, #173, and #178. Temporary patch-runner PR #179 was closed without merge and is not production history.

# Important later repository state not authored by this conversation

After the direct implementation phase above, other agents continued the same program. At archive time, current repository records show these later merged results:

- PR #201 — `Game` owns the runtime `InstanceManager`;
- PR #231 — `Game::removeCreature()` automatically unregisters owned creature IDs;
- PR #233 — `Game::start()` periodically calls `closeExpiredInstances()`;
- PR #287 — evidence-backed Instanced Test Arena region plan using existing OTBM tools;
- PR #289 — real `InstanceArenaService` and two configured regions;
- PR #295 — admin-only `/instancearena create|leave|close` plus narrow Lua bindings and player-session flow;
- PR #304 — real arena monster spawn, binder registration after a nonzero runtime ID, cleanup integration, and the production summon call site using the instance-aware `setMaster` path;
- PR #307 — real arena timeout, expired-session evacuation, and the first production `InstanceScopedEvent` call site;
- PRs #306 and #312 — architecture/program documentation synchronization after the arena runtime merges.

These later changes make the earlier statement "there is no real instance consumer" obsolete. Do not recreate the arena service, region configuration, talkaction, monster spawn, removal unregister, timeout sweep, or warning event.

# Current continuation boundary

At the verified archive baseline, `docs/agents/programs/INSTANCED_TEST_ARENA_PROGRAM.md` records PRs 1–5 as complete and leaves exactly:

1. **PR 6** — run two real arenas and fix only concrete cross-instance leaks in spectator, target, follow, direct combat, area combat, and related call sites by reusing the existing authoritative relation policy;
2. **PR 7** — two-parallel-instances end-to-end proof, independent close, cleanup, region reuse, and final documentation/program closure.

Before continuing, a new agent must re-read current `main` because the repository moves quickly. The authoritative start order is:

1. `AGENTS.md`;
2. `docs/agents/README.md`;
3. `docs/agents/programs/INSTANCED_TEST_ARENA_PROGRAM.md`;
4. `docs/architecture/instanced-test-arena.md`;
5. `docs/architecture/instance-manager.md`;
6. `docs/architecture/CANARY_ENGINE_PROJECT_HANDOFF.md`;
7. current open PRs and active task records.

# Do not repeat

- Do not build another `InstanceManager`, region pool, creature registry, binder, interaction policy, rollback transaction, runtime owner, timeout sweep, arena service, talkaction, monster-spawn path, or removal hook.
- Do not use the earlier conversation prompt that proposed creating the Instanced Test Arena from scratch; that work already exists on `main` through PR #307.
- Do not extend multiworld or multi-channel as part of the arena workstream.
- Do not create another OTBM parser, renderer, script resolver, or AI-generated map visualization.
- Do not edit binary OTBM data manually.
- Do not treat static manager tests as the final PR 6/7 evidence; the remaining work requires concrete two-arena runtime and end-to-end proof.

# Validation history and evidence boundary

The implementation PRs above were merged only after applicable repository CI completed. During the conversation, real failures were diagnosed rather than bypassed, including:

- a required-check deadlock for path-filtered PRs;
- a Visual Studio source-list divergence for the region-pool implementation;
- unconstrained binder templates selecting integer IDs as runtime objects;
- formatter mutation of the `Creature::setMaster` integration branch.

This archive does not claim that all future instance isolation, player lifecycle, cleanup/recovery, or protocol/session end-to-end work is complete. It records only the delivered slices and the later repository state observed at archival time.

# Ownership release and self-archive

- `agent_archive_status`: archived by this record;
- active task owned by this conversation: none;
- active branch ownership after archive merge: none;
- scheduled check-ins or automations: none;
- deferred background execution: none;
- owned runtime, test, workflow, map, Lua, or shared documentation paths: none;
- remaining work must start as a new task from then-current `main` with a new branch and fresh collision check.

No further action should be attributed to this archived conversation after this record is merged.
