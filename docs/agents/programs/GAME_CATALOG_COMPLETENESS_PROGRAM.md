---
program_id: CAN-PROGRAM-GAME-CATALOG-COMPLETENESS
name: Oteryn Game Catalog completeness and activation
status: active
owner: chatgpt
created: 2026-07-29T13:27:36Z
updated: 2026-07-29T13:27:36Z
last_verified_commit: "23a8148f72805676fa623c15ffa6ad20e7dc3d2f"
primary_paths:
  - src/game/catalog/**
  - schemas/game-catalog/**
  - tools/game-catalog/**
  - tests/game_catalog/**
  - data-*/catalog/**
shared_integration_paths:
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CROSS_REPO_CONTRACTS.md
  - docs/contracts/GAME_CATALOG_EXPORT_CONTRACT.md
  - docs/systems/GAME_CATALOG_EXPORTER.md
  - .github/workflows/game-catalog.yml
related_programs: []
cross_repo_contracts:
  - OTS-20260728-game-catalog-v1
---

# Mission

Deliver a complete, evidence-backed Oteryn Game Catalog path from reviewed Canary metadata through additional entity families, staging proof, and a separately gated production activation.

# Scope

- Build reviewed historical versioning, completeness, and availability metadata without converting missing evidence into facts.
- Extend the catalogue through separate bounded entity-family tasks for NPCs and shop offers, spells, quests and rewards, and areas/spawns/raids.
- Preserve deterministic offline export, schema validation, immutable snapshots, SHA-256 publication, and database/network isolation.
- Coordinate schema and rollout compatibility with the Oteryn Platform consumer.
- Produce staging import, activation, rollback, and production-readiness evidence before any production gate.

# Explicit exclusions

- External wikis are not runtime or historical truth; they may only identify claims that must be proven from reviewed evidence.
- This program does not authorize writes outside `blakinio/canary`; `blakinio/Oteryn-Platform` remains read-only until separately authorized.
- Production activation is not automatic. It requires direct environment evidence, rollback proof, compatible deployed revisions, and the repository's manual production gate.
- Secrets, credentials, database dumps, proprietary assets, `**/*.otbm`, and `**/items.otb` are excluded.
- Unknown release, availability, spawn, quest, or map facts remain explicit `unknown`.

# Existing systems to reuse

| Module/tool/contract | Source | Required reuse rule |
|---|---|---|
| Offline Game Catalog exporter | `src/game/catalog/**`, PR #991 | Extend final runtime registry collection; do not build a second parser or normal-server export path. |
| Snapshot validator | `tools/game-catalog/validate_snapshot.py` | Keep schema and semantic validation fail-closed. |
| Game Catalog workflow | `.github/workflows/game-catalog.yml` | Preserve exact-head deterministic export and no-network/no-database syscall proof. |
| File contract | `oteryn.game-catalog` schema `1.0.0` | Version schema changes explicitly and keep producer/consumer compatibility evidence synchronized. |
| Archived exporter task | `CAN-20260728-game-catalog-exporter`, PR #991 | Reuse its PROVEN facts; do not reopen or expand the archived task. |

# Active tasks

| Task ID | Branch | PR | State | Exact next action |
|---|---|---:|---|---|
| `CAN-20260729-game-catalog-metadata-evidence` | `feat/CAN-20260729-game-catalog-metadata-evidence` | pending | investigating | Verify the exact target datapack and repository-backed evidence sources, then declare its exact manifest ownership. |

# Queue

1. Complete `CAN-20260729-game-catalog-metadata-evidence`: bounded reviewed release/versioning/availability manifests and deterministic validation, without production activation.
2. Add NPCs and shop offers in a new versioned producer/consumer contract task.
3. Add spells in a separate versioned contract task.
4. Add quests and rewards in a separate versioned contract task.
5. Add areas, spawns, raids, and map attainability in separate evidence-backed tasks.
6. Certify compatible consumer schema/import behavior; this requires separate write authorization for `blakinio/Oteryn-Platform`.
7. Generate a reviewed staging snapshot and prove import, candidate activation, rollback, and visibility.
8. Verify production revisions, storage, routing, permissions, monitoring, rollback, and operator procedure.
9. Cross the manual production activation gate only after every blocker is closed.

# Completed work

| Task/PR | Result | Merge commit | Follow-up |
|---|---|---|---|
| `CAN-20260728-game-catalog-exporter` / #991 | Deterministic offline item, creature, and loot exporter | `4ae896d9c6ad33e4193a314f47daeff9ea4ac66b` | Start reviewed metadata evidence. |

# Dependencies and blockers

- Later entity families require explicit schema/version and consumer compatibility decisions.
- Consumer mutations are blocked by the current repository allowlist.
- Production activation requires direct environment evidence and remains a manual gate.
- The exact production datapack/profile and reviewed evidence boundary are not yet verified.

# Decisions and invariants

- Work is split into one branch, task record, and draft PR per bounded entity/evidence/activation package.
- Missing evidence stays unknown and never becomes complete or available by inference.
- Runtime fields come from final Canary registries; reviewed manifests contain only evidence-backed annotations.
- Schema changes are versioned, fail closed, and coordinated through the cross-repository contract registry.
- No task may weaken deterministic export, atomic publication, or network/database isolation.
- No production action occurs from a repository PR alone.

# Validation strategy

- Metadata tasks: schema/manifest checks, focused unit tests, deterministic two-run export, and exact-head Game Catalog workflow.
- Entity tasks: focused C++/Lua tests, schema fixtures, producer/consumer contract tests, and full exact-head applicable CI.
- Activation tasks: staging artifact digest, transactional import, candidate activation, rollback, visibility, deployed-revision verification, monitoring, and operator approval.

# Handoff

## Start here

Read `AGENTS.md`, `docs/agents/README.md`, this program record, the active task record, and overlapping open PRs before selecting work.

## Task creation protocol

1. Select exactly one bounded queue item.
2. Inspect active ownership and overlapping PRs.
3. Create one task record, branch, worktree, and draft PR.
4. Declare exact exclusive/shared/read-only paths.
5. Implement, validate, merge, archive the task, and update this program record.

## Do not repeat

- Do not reopen archived task `CAN-20260728-game-catalog-exporter`.
- Do not infer historical or availability facts from external wikis.
- Do not add all future entity types in one schema/implementation PR.
- Do not treat a staging artifact or repository merge as production activation.

## Open questions

- Which exact datapack/profile is the production export target?
- Which repository-backed records satisfy review requirements for each historical and availability claim?
- Which schema version and rollout order will be used for each additional entity family?
