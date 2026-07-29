---
task_id: CAN-20260729-game-catalog-metadata-evidence
program_id: CAN-PROGRAM-GAME-CATALOG-COMPLETENESS
coordination_id: "OTS-20260728-game-catalog-v1"
status: investigating
agent: "chatgpt"
branch: feat/CAN-20260729-game-catalog-metadata-evidence
base_branch: main
created: 2026-07-29T13:27:36Z
updated: 2026-07-29T13:27:36Z
last_verified_commit: "23a8148f72805676fa623c15ffa6ad20e7dc3d2f"
risk: high
related_issue: ""
related_pr: ""
depends_on:
  - CAN-20260728-game-catalog-exporter
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260729-game-catalog-metadata-evidence.md
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
- Ownership checker result: not run; no local Git checkout is available in this session.
- Exclusive claims: this task record only until the exact target datapack and implementation paths are verified.
- Shared claims: program, catalogue, contract, cross-repository registry, and architecture documentation.
- Read-only dependencies: existing exporter, v1 schema, and workflow.
- Overlaps: none found by narrow GitHub search; exact structured ownership remains unverified locally.
- Resolution: run the deterministic ownership checker and update exact claims before any manifest or implementation edit.

# Current state

The archived exporter is complete. No reviewed production manifest root was found in PR #991's changed files, and the intended production datapack/profile has not yet been proven. This task is therefore in evidence and ownership preflight.

# Plan

1. Verify the exact target `DATA_DIRECTORY`, catalogue manifest root, and repository-backed evidence sources.
2. Run structured ownership validation and declare exact manifest/tool/test paths.
3. Define a bounded seed set with claim-level evidence and explicit unknowns.
4. Implement manifests and any minimum validator/test support required for fail-closed review.
5. Run deterministic focused export validation and current-head CI.
6. Update the program, contracts, catalogue, checkpoint, and merge/archive lifecycle.

# Work log

## 2026-07-29T13:27:36Z

- Changed: created the multi-task Game Catalog completeness program and this first bounded metadata task.
- Learned: the merged exporter accepts external manifests but PR #991 supplied only isolated CI manifests, not a production `data-*/catalog/**` baseline.
- Failed/blocked: local ownership tooling and implementation cannot run because this session has no Git checkout.
- Result: safe repository coordination is established without metadata or production activation claims.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Split metadata, entity families, and production activation into separate tasks | Repository policy requires bounded branches/PRs; schema and production risks differ materially. | none |
| Start with metadata evidence | Additional entity and activation work depends on trustworthy release/completeness/availability boundaries. | none |
| Keep target datapack unknown until proven | PR #991 did not add a production manifest set and the exporter supports configurable datapacks. | none |
| Preserve schema v1 in this task | Metadata population can use the existing v1 contract; new entity types require separate versioned contracts. | none |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `docs/agents/tasks/active/CAN-20260729-game-catalog-metadata-evidence.md` | exclusive | Task state and checkpoint | active |
| `docs/agents/programs/GAME_CATALOG_COMPLETENESS_PROGRAM.md` | shared | Multi-task sequence and gates | active |
| `src/game/catalog/**` | read_only | Existing manifest loader/exporter | inspected |
| `schemas/game-catalog/v1/**` | read_only | Existing contract shape | inspected |
| exact `data-*/catalog/**` target | unresolved | Reviewed metadata manifests | not claimed |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| `23a8148f72805676fa623c15ffa6ad20e7dc3d2f` | GitHub open PR/issue search for `catalog` | passed | No open matching PR or issue returned. |
| pending | `python tools/agents/task_ownership.py` | blocked | No local checkout in this session. |
| pending | Game Catalog focused validation | not-run | No implementation changes yet. |

Never write `passed` without verification on the stated commit.

# Failed approaches and dead ends

- Reopening archived task `CAN-20260728-game-catalog-exporter` is invalid because its lifecycle is complete.
- Treating CI-generated manifests as production metadata is invalid; they are isolated smoke inputs.
- Using external wiki claims as manifest truth is forbidden by the contract.

# Risks and compatibility

- Runtime: incorrect manifest selection could export the wrong content profile.
- Data/migration: bulk historical annotation without reviewed evidence would create false facts.
- Security: production paths, credentials, and dumps are excluded.
- Backward compatibility: this task preserves schema `1.0.0`; unsupported future schema versions must fail closed.
- Cross-repo rollout: Platform remains read-only and may require a separate task only if v1 semantics change.
- Rollback: no activation occurs; generated snapshots remain immutable files and prior active consumer state must remain unchanged.

# Remaining work

1. In a synchronized checkout of this branch, run the ownership checker and verify the exact production `DATA_DIRECTORY`/catalogue root plus repository-backed evidence sources before claiming or editing manifest paths.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T13:27:36Z
head: UNKNOWN
branch: feat/CAN-20260729-game-catalog-metadata-evidence
pr: none
status: investigating
context_routes:
  - agent-governance
  - cpp-runtime
  - lua-data
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260729-game-catalog-metadata-evidence.md
  - docs/agents/programs/GAME_CATALOG_COMPLETENESS_PROGRAM.md
proven:
  - PR 991 merged the deterministic offline Game Catalog exporter and its task is archived.
  - The exporter defaults manifests to <DATA_DIRECTORY>/catalog and preserves missing annotations as unverified or unknown.
  - PR 991 changed no production data-*/catalog manifest path; its workflow creates isolated CI manifests.
  - Narrow GitHub searches found no open catalog PR or issue.
  - Current authorization permits repository writes only in blakinio/canary.
derived:
  - Metadata evidence must be completed before trustworthy additional-entity visibility or production activation.
  - The work must be split across bounded tasks and versioned cross-repository contracts.
unknown:
  - The exact intended production DATA_DIRECTORY and catalogue manifest root.
  - The reviewed repository-backed evidence set for historical and availability claims.
  - Exact consumer changes and schema versions required by each additional entity family.
conflicts: []
first_failure:
  marker: target-datapack-and-ownership-unverified
  evidence: No production manifest path exists in PR 991 and local task_ownership.py could not run without a checkout.
rejected_hypotheses:
  - Continue the archived exporter task: PR 996 archived it as completed.
  - Treat isolated CI manifests as production metadata: the workflow creates them under artifacts for smoke testing only.
  - Infer metadata from external wikis: the v1 contract forbids it.
changed_paths:
  - docs/agents/programs/GAME_CATALOG_COMPLETENESS_PROGRAM.md
  - docs/agents/tasks/active/CAN-20260729-game-catalog-metadata-evidence.md
validation:
  - command: Narrow GitHub open PR and issue search for catalog
    result: PASS
    evidence: No matching open PR or issue returned on 2026-07-29.
  - command: python tools/agents/task_ownership.py
    result: BLOCKED
    evidence: No local Git checkout is available in this session.
blockers:
  - Exact target datapack and structured ownership must be verified before manifest edits.
  - Local checkout is required for implementation and deterministic validation.
next_action: In a synchronized checkout of this branch, run task_ownership.py and verify the exact production DATA_DIRECTORY/catalogue root plus repository-backed evidence sources before editing manifests.
```

# Handoff

## Start here

Read root and nested agent rules, the program record, this checkpoint, PR #991's archived task, the live draft PR, and current branch/head.

## Do not repeat

- Do not reopen PR #991 or its archived task.
- Do not infer historical or availability facts from external wikis.
- Do not claim `data-otservbr-global` or another datapack as production until configuration/deployment evidence proves it.
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

- Which exact datapack/profile is the production export target?
- Which repository-backed records meet the review threshold for release and availability claims?

# Completion

- Final status: investigating
- PR: pending
- Merge commit: none
- Program record updated: yes
- Catalogue updated: not required yet
- Changelog updated: not required yet
- Archived at: not archived
