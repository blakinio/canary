---
task_id: CAN-20260729-game-catalog-metadata-evidence
program_id: CAN-PROGRAM-GAME-CATALOG-COMPLETENESS
coordination_id: "OTS-20260728-game-catalog-v1"
status: blocked
agent: "chatgpt"
branch: feat/CAN-20260729-game-catalog-metadata-evidence
base_branch: main
created: 2026-07-29T13:27:36Z
updated: 2026-07-29T13:40:57Z
last_verified_commit: "000ce71c52229c9d8e56b2ab9e90a3e139f2e303"
risk: high
related_issue: ""
related_pr: 1005
depends_on:
  - CAN-20260728-game-catalog-exporter
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260729-game-catalog-metadata-evidence.md
    - data-otservbr-global/catalog/**
  shared:
    - docs/agents/programs/GAME_CATALOG_COMPLETENESS_PROGRAM.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CROSS_REPO_CONTRACTS.md
    - docs/contracts/GAME_CATALOG_EXPORT_CONTRACT.md
    - docs/systems/GAME_CATALOG_EXPORTER.md
  read_only:
    - src/game/catalog/**
    - schemas/game-catalog/v1/**
    - .github/workflows/game-catalog.yml
modules_touched:
  - oteryn.game-catalog manifest metadata
reuses:
  - Game Catalog exporter from PR #991
  - tools/game-catalog/validate_snapshot.py
  - .github/workflows/game-catalog.yml
public_interfaces:
  - oteryn.game-catalog schema 1.0.0 metadata semantics
cross_repo_tasks: []
---

# Goal

Create the first bounded, reviewed metadata baseline for the existing Game Catalog v1 exporter by proving the target datapack and evidence sources, adding only evidence-backed release/versioning/availability annotations, and validating a deterministic non-production export.

# Acceptance criteria

- [ ] The exact target datapack/profile and manifest root are verified from repository and deployment contracts.
- [ ] Every seeded release, `introduced_in`, `removed_in`, completeness, availability, and enabled claim has a reviewable evidence reference.
- [ ] Missing or conflicting evidence remains `unknown`, `unverified`, or a blocking finding.
- [ ] The bounded manifest set covers reviewed item, creature, and loot examples without claiming bulk historical completeness.
- [ ] Manifest loading and snapshot validation fail closed for malformed, conflicting, dangling, or unsupported data.
- [ ] Two fixed-input exports are byte-identical apart from the controlled `generated_at`.
- [ ] No production profile is imported or activated.
- [ ] Relevant focused checks and current-head GitHub checks pass.
- [ ] Module catalogue, contract, architecture, changelog, and program impacts are updated or explicitly recorded as none.
- [ ] Cross-repository impact is documented; no consumer mutation is made without separate authorization.
- [ ] Autonomous merge gate is satisfied.

# Confirmed context

- PR #991 merged the deterministic offline exporter as `4ae896d9c6ad33e4193a314f47daeff9ea4ac66b`.
- The archived task explicitly leaves complete historical metadata, availability evidence, additional entity types, and production activation outside its slice.
- The exporter loads required `profile.json` and `releases.json`, optional item/creature/loot versioning and availability manifests, and defaults the manifest root to `<DATA_DIRECTORY>/catalog`.
- PR #991 did not add a production `data-*/catalog/**` manifest set; its runtime smoke creates isolated manifests under `artifacts/**`.
- The v1 contract forbids inferring historical or availability facts from external wikis.
- The current repository allowlist permits writes only to `blakinio/canary`.
- `config.lua.dist` selects `data-otservbr-global` as the repository default datapack, so the default manifest root is `data-otservbr-global/catalog`.
- `src/core.hpp` proves protocol/runtime client version `15.25`, but `docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md` explicitly states that protocol `15.25` does not prove complete content coverage.
- The v1 schema requires `snapshot.verified_content_through_release` to be a non-null release key, while the contract requires missing evidence to remain unknown.
- Repository source proves a bounded runtime seed: item `3416` dragon shield, creature `Dragon`, its spawn entries, and the dragon-to-dragon-shield loot relation. It does not prove either entity's historical `introduced_in` release or a complete datapack-wide verified-content boundary.
- Current main was most recently observed at `23a8148f72805676fa623c15ffa6ad20e7dc3d2f` before this branch was created.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| PR #991 | Runtime exporter and manifest loader | `src/game/catalog/**` | Uses final runtime registries and preserves unknown metadata. |
| Snapshot validator | Schema/semantic validation | `tools/game-catalog/validate_snapshot.py` | Existing fail-closed contract validation. |
| Game Catalog workflow | Build and isolated two-run runtime proof | `.github/workflows/game-catalog.yml` | Proves deterministic output and absence of endpoint syscalls. |
| Contract registry | Producer/consumer rollout boundary | `docs/agents/CROSS_REPO_CONTRACTS.md` | Existing coordination ID and one-sided failure rules. |
| Program record | Multi-task sequencing | `docs/agents/programs/GAME_CATALOG_COMPLETENESS_PROGRAM.md` | Keeps metadata, entity families, staging, and production gates separate. |

# Ownership and overlap check

- Program record: new `CAN-PROGRAM-GAME-CATALOG-COMPLETENESS`.
- Open PRs inspected: narrow `catalog` search returned no open matching PR.
- Active tasks inspected: narrow repository searches returned no active Game Catalog continuation record.
- Ownership checker result: local `python tools/agents/task_ownership.py` passed with 35 active task records; Agent Task Ownership run `30456714386` also passed.
- Exclusive claims: this task record and `data-otservbr-global/catalog/**`; narrow GitHub searches found no matching open PR or indexed task.
- Shared claims: program, catalogue, contract, cross-repository registry, and architecture documentation.
- Read-only dependencies: existing exporter, v1 schema, and workflow.
- Overlaps: none found by narrow GitHub search or deterministic ownership validation.
- Resolution: ownership is clear; metadata implementation is blocked by the v1 verified-content-boundary representation conflict and consumer write authorization.

# Current state

The archived exporter is complete and ownership of the repository-default manifest root is proven. A bounded dragon/dragon-shield runtime, spawn, and loot seed is repository-backed, but its historical introduction release remains unknown. Schema v1 cannot represent an unknown snapshot-wide `verified_content_through_release`, and protocol `15.25` cannot be reused as content-completeness evidence. Implementing the required profile now would invent a fact. A synchronized producer/consumer schema decision is required before manifests can be added.

# Plan

1. Obtain explicit write authorization for `blakinio/Oteryn-Platform`.
2. Create a separate versioned cross-repository contract task that can represent an unknown verified-content boundary without weakening fail-closed behavior.
3. Resume this metadata task with the bounded dragon, dragon-shield, and loot seed while leaving `introduced_in` and `removed_in` null.
4. Implement manifests and minimum validator/test support.
5. Run deterministic focused export validation and current-head CI.
6. Update the program, contracts, catalogue, checkpoint, and merge/archive lifecycle.

# Work log

## 2026-07-29T13:27:36Z

- Changed: created the multi-task Game Catalog completeness program and this first bounded metadata task.
- Learned: the merged exporter accepts external manifests but PR #991 supplied only isolated CI manifests; `config.lua.dist` selects `data-otservbr-global`, so its default catalogue root is `data-otservbr-global/catalog`.
- Failed/blocked: local ownership tooling and implementation cannot run because this session has no Git checkout; GitHub ownership CI will validate the exact claim.
- Result: safe repository coordination is established without metadata or production activation claims.

## 2026-07-29T13:40:57Z

- Changed: no runtime or manifest files; inspected the synchronized branch and repository-backed item, creature, spawn, loot, protocol, schema, and evidence contracts.
- Learned: item `3416`, creature `Dragon`, its spawn entries, and dragon-shield loot are valid bounded runtime/availability evidence, but no reviewed historical introduction or datapack-wide verified-content boundary is present.
- Failed/blocked: schema v1 requires a concrete `verified_content_through_release`, while repository policy requires that this unknown remain unknown.
- Result: metadata implementation is blocked pending a synchronized versioned producer/consumer contract and explicit Platform write authorization.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Split metadata, entity families, and production activation into separate tasks | Repository policy requires bounded branches/PRs; schema and production risks differ materially. | none |
| Start with metadata evidence | Additional entity and activation work depends on trustworthy release/completeness/availability boundaries. | none |
| Target the repository-default datapack, not an unverified deployment | `config.lua.dist` selects `data-otservbr-global`; actual deployed configuration remains unknown. | none |
| Do not invent a v1 verified-content boundary or sentinel release | The schema requires a concrete release, but neither protocol 15.25 nor current datapack presence proves completeness. | required cross-repository schema decision |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `docs/agents/tasks/active/CAN-20260729-game-catalog-metadata-evidence.md` | exclusive | Task state and checkpoint | active |
| `docs/agents/programs/GAME_CATALOG_COMPLETENESS_PROGRAM.md` | shared | Multi-task sequence and gates | active |
| `src/game/catalog/**` | read_only | Existing manifest loader/exporter | inspected |
| `schemas/game-catalog/v1/**` | read_only | Existing contract shape | inspected |
| `data-otservbr-global/catalog/**` | exclusive | Repository-default reviewed metadata manifests | ownership proven; implementation blocked |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| `23a8148f72805676fa623c15ffa6ad20e7dc3d2f` | GitHub open PR/issue search for `catalog` | passed | No open matching PR or issue returned. |
| `666369126319bdac3ecc4ff83584011db1ce6c2f` | Agent Task Ownership `30456714386` | passed | Structured claims validated with no overlap. |
| `666369126319bdac3ecc4ff83584011db1ce6c2f` | CI `30456714463` | passed | Exact-head documentation/fast checks passed. |
| pending | Game Catalog focused validation | not-run | No implementation changes yet. |

Never write `passed` without verification on the stated commit.

# Failed approaches and dead ends

- Reopening archived task `CAN-20260728-game-catalog-exporter` is invalid because its lifecycle is complete.
- Treating CI-generated manifests as production metadata is invalid; they are isolated smoke inputs.
- Using external wiki claims as manifest truth is forbidden by the contract.
- Treating protocol `15.25` as `verified_content_through_release=15.25` is invalid; the repository evidence policy explicitly separates protocol and content coverage.
- Inventing a `0.0.0` or other sentinel release is invalid without a versioned producer/consumer contract.

# Risks and compatibility

- Runtime: incorrect manifest selection could export the wrong content profile.
- Data/migration: bulk historical annotation without reviewed evidence would create false facts.
- Security: production paths, credentials, and dumps are excluded.
- Backward compatibility: schema `1.0.0` cannot honestly represent the current unknown boundary; any correction must be versioned and older consumers must fail closed.
- Cross-repo rollout: the necessary schema correction requires a synchronized Platform task, but Platform is read-only under current authorization.
- Rollback: no activation occurs; generated snapshots remain immutable files and prior active consumer state must remain unchanged.

# Remaining work

1. Obtain explicit repository-write authorization for `blakinio/Oteryn-Platform` so a synchronized versioned contract can represent an unknown `verified_content_through_release` before manifest implementation.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T13:40:57Z
head: 000ce71c52229c9d8e56b2ab9e90a3e139f2e303
branch: feat/CAN-20260729-game-catalog-metadata-evidence
pr: 1005
status: blocked
context_routes:
  - agent-governance
  - cpp-runtime
  - lua-data
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260729-game-catalog-metadata-evidence.md
  - docs/agents/programs/GAME_CATALOG_COMPLETENESS_PROGRAM.md
  - data-otservbr-global/catalog/**
proven:
  - PR 991 merged the deterministic offline Game Catalog exporter and its task is archived.
  - The exporter defaults manifests to <DATA_DIRECTORY>/catalog and preserves missing annotations as unverified or unknown.
  - PR 991 changed no production data-*/catalog manifest path; its workflow creates isolated CI manifests.
  - Narrow GitHub searches found no open catalog PR or issue.
  - Current authorization permits repository writes only in blakinio/canary.
  - config.lua.dist selects data-otservbr-global as the repository default datapack and therefore data-otservbr-global/catalog as its default manifest root.
  - src/core.hpp proves protocol version 15.25, while the evidence policy states that protocol version does not prove content coverage.
  - Item 3416, creature Dragon, Dragon spawn entries and the dragon-shield loot relation are present in repository source.
  - Schema v1 requires verified_content_through_release to be a concrete release key.
derived:
  - Metadata evidence must be completed before trustworthy additional-entity visibility or production activation.
  - The work must be split across bounded tasks and versioned cross-repository contracts.
  - A versioned producer/consumer schema decision is required before an honest metadata profile can represent the unknown verified-content boundary.
unknown:
  - Whether the deployed production configuration uses the repository-default data-otservbr-global datapack/profile.
  - Historical introduced_in and removed_in releases for the bounded dragon and dragon-shield seed.
  - Exact consumer changes and schema versions required by each additional entity family.
conflicts:
  - Schema v1 requires a non-null verified_content_through_release, but repository policy requires the unproven datapack-wide boundary to remain unknown.
first_failure:
  marker: verified-content-boundary-unrepresentable
  evidence: Protocol 15.25 and bounded runtime presence do not prove datapack-wide content coverage, while schema v1 forbids null.
rejected_hypotheses:
  - Continue the archived exporter task: PR 996 archived it as completed.
  - Treat isolated CI manifests as production metadata: the workflow creates them under artifacts for smoke testing only.
  - Infer metadata from external wikis: the v1 contract forbids it.
  - Use protocol 15.25 as the verified content boundary: REAL_TIBIA_EVIDENCE_SOURCES.md explicitly rejects that inference.
  - Invent an unreviewed sentinel release: it would add producer/consumer semantics outside schema v1.
changed_paths:
  - docs/agents/programs/GAME_CATALOG_COMPLETENESS_PROGRAM.md
  - docs/agents/tasks/active/CAN-20260729-game-catalog-metadata-evidence.md
validation:
  - command: Narrow GitHub open PR and issue search for catalog
    result: PASS
    evidence: No matching open PR or issue returned on 2026-07-29.
  - command: Agent Task Ownership run 30456714386
    result: PASS
    evidence: Exact structured ownership passed at 666369126319bdac3ecc4ff83584011db1ce6c2f.
  - command: CI run 30456714463
    result: PASS
    evidence: Exact-head documentation and fast checks passed at 666369126319bdac3ecc4ff83584011db1ce6c2f.
  - command: python tools/agents/task_ownership.py
    result: PASS
    evidence: Local synchronized checkout validated 35 active task records at 000ce71c52229c9d8e56b2ab9e90a3e139f2e303.
blockers:
  - Current authorization forbids the Platform consumer mutation required for a synchronized schema correction.
  - Schema v1 cannot represent the unknown verified-content boundary without inventing a fact.
next_action: Obtain explicit repository-write authorization for blakinio/Oteryn-Platform so a synchronized versioned contract can represent an unknown verified_content_through_release before manifest implementation.
```

# Handoff

## Start here

Read root and nested agent rules, the program record, this checkpoint, PR #991's archived task, the live draft PR, and current branch/head.

## Do not repeat

- Do not reopen PR #991 or its archived task.
- Do not infer historical or availability facts from external wikis.
- Treat `data-otservbr-global` only as the repository default; do not claim the deployed production datapack until direct configuration evidence proves it.
- Do not mutate Oteryn Platform under the current repository allowlist.
- Do not activate production from this task.

## Required reads

- `AGENTS.md`
- `docs/agents/AGENTS.md`
- `docs/agents/REPOSITORY_MAP.md`
- `docs/agents/CONTEXT_ROUTING.md`
- `docs/agents/programs/GAME_CATALOG_COMPLETENESS_PROGRAM.md`
- `docs/agents/CROSS_REPO_CONTRACTS.md`
- `docs/contracts/GAME_CATALOG_EXPORT_CONTRACT.md`
- `docs/systems/GAME_CATALOG_EXPORTER.md`
- `src/game/catalog/catalog_runtime.cpp`
- `src/game/catalog/game_catalog_manifest.cpp`
- `.github/workflows/game-catalog.yml`

## Open questions

- Does the deployed production configuration retain the repository-default `data-otservbr-global` datapack/profile?
- Which repository-backed records meet the review threshold for release and availability claims?

# Completion

- Final status: investigating
- PR: #1005
- Merge commit: none
- Program record updated: yes
- Catalogue updated: not required yet
- Changelog updated: not required yet
- Archived at: not archived
