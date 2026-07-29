---
task_id: CAN-20260729-game-catalog-metadata-evidence
program_id: CAN-PROGRAM-GAME-CATALOG-COMPLETENESS
coordination_id: "OTS-20260728-game-catalog-v1"
status: ready
agent: "chatgpt"
branch: feat/CAN-20260729-game-catalog-metadata-evidence
base_branch: main
created: 2026-07-29T13:27:36Z
updated: 2026-07-29T16:41:22Z
last_verified_commit: "5ab9d1288875d2318d4943652caa76a9e774bcfb"
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
    - tests/game_catalog/test_default_metadata.py
  shared:
    - docs/agents/programs/GAME_CATALOG_COMPLETENESS_PROGRAM.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CROSS_REPO_CONTRACTS.md
    - docs/contracts/GAME_CATALOG_EXPORT_CONTRACT.md
    - docs/systems/GAME_CATALOG_EXPORTER.md
    - docs/agents/CHANGELOG.md
    - .github/workflows/game-catalog.yml
  read_only:
    - src/game/catalog/**
    - schemas/game-catalog/v1.1/**
modules_touched:
  - oteryn.game-catalog manifest metadata
reuses:
  - Game Catalog exporter from PR #991
  - tools/game-catalog/validate_snapshot.py
  - .github/workflows/game-catalog.yml
public_interfaces:
  - oteryn.game-catalog schema 1.1.0 metadata semantics
cross_repo_tasks:
  - OTERYN-20260729-game-catalog-null-boundary
---

# Goal

Create the first bounded, reviewed metadata baseline for the Game Catalog schema 1.1 exporter by proving the target datapack and evidence sources, adding only evidence-backed release/versioning/availability annotations, and validating a deterministic non-production export.

# Acceptance criteria

- [x] The exact target datapack/profile and manifest root are verified from repository and deployment contracts.
- [x] Every seeded release, `introduced_in`, `removed_in`, completeness, availability, and enabled claim has a reviewable evidence reference.
- [x] Missing or conflicting evidence remains `unknown`, `unverified`, or a blocking finding.
- [x] The bounded manifest set covers reviewed item, creature, and loot examples without claiming bulk historical completeness.
- [x] Manifest loading and snapshot validation fail closed for malformed, conflicting, dangling, or unsupported data.
- [x] Two fixed-input exports are byte-identical apart from the controlled `generated_at`.
- [x] No production profile is imported or activated.
- [x] Relevant focused checks and current-head GitHub checks pass.
- [x] Module catalogue, contract, architecture, changelog, and program impacts are updated or explicitly recorded as none.
- [x] Cross-repository impact is documented and schema 1.1 consumer compatibility is merged before producer metadata.
- [ ] Autonomous merge gate is satisfied.

# Confirmed context

- PR #991 merged the deterministic offline exporter as `4ae896d9c6ad33e4193a314f47daeff9ea4ac66b`.
- The archived task explicitly leaves complete historical metadata, availability evidence, additional entity types, and production activation outside its slice.
- The exporter loads required `profile.json` and `releases.json`, optional item/creature/loot versioning and availability manifests, and defaults the manifest root to `<DATA_DIRECTORY>/catalog`.
- PR #991 did not add a production `data-*/catalog/**` manifest set; its runtime smoke creates isolated manifests under `artifacts/**`.
- The contract forbids inferring historical or availability facts from external wikis.
- The user explicitly authorized writes to `blakinio/canary` and `blakinio/Oteryn-Platform`.
- `config.lua.dist` selects `data-otservbr-global` as the repository default datapack, so the default manifest root is `data-otservbr-global/catalog`.
- `src/core.hpp` proves protocol/runtime client version `15.25`, but `docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md` explicitly states that protocol `15.25` does not prove complete content coverage.
- Platform PR #299 merged schema 1.1 consumer support as `b2b2871eed0375e22d48de5dd4947fe29c2bb974`.
- Canary PR #1006 merged schema 1.1 producer support as `3ad7155dd833e105cebfd4b472800a4156ac1e90`; null remains unknown and is activation-blocking.
- Repository source proves a bounded runtime seed: item `3416` dragon shield, creature `Dragon`, its spawn entries, and the dragon-to-dragon-shield loot relation. It does not prove either entity's historical `introduced_in` release or a complete datapack-wide verified-content boundary.
- The reviewed seed uses source keys `3416`, `dragon`, and `dragon|3416|20`; the last key is the zero-based position of dragon shield in the final Dragon runtime loot list.
- A bounded real-Dragon runtime projection exports the reviewed seed deterministically. A full default-datapack export still fails closed on pre-existing unresolved loot item endpoints and chance values greater than `MAX_LOOTCHANCE`; that integrity problem is not converted into catalogue facts.
- Current `main` was verified at `3ad7155dd833e105cebfd4b472800a4156ac1e90` before implementation.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| PR #991 | Runtime exporter and manifest loader | `src/game/catalog/**` | Uses final runtime registries and preserves unknown metadata. |
| Snapshot validator | Schema/semantic validation | `tools/game-catalog/validate_snapshot.py` | Existing fail-closed contract validation. |
| Game Catalog workflow | Build and isolated two-run runtime proof | `.github/workflows/game-catalog.yml` | Proves deterministic output and absence of endpoint syscalls. |
| Contract registry | Producer/consumer rollout boundary | `docs/agents/CROSS_REPO_CONTRACTS.md` | Schema 1.1 consumer-first rollout is merged in Platform #299 and Canary #1006. |
| Program record | Multi-task sequencing | `docs/agents/programs/GAME_CATALOG_COMPLETENESS_PROGRAM.md` | Keeps metadata, entity families, staging, and production gates separate. |

# Ownership and overlap check

- Program record: new `CAN-PROGRAM-GAME-CATALOG-COMPLETENESS`.
- Open PRs inspected: narrow `catalog` search returned no open matching PR.
- Active tasks inspected: narrow repository searches returned no active Game Catalog continuation record.
- Ownership checker result: local `python tools/agents/task_ownership.py` passed with 35 active task records; Agent Task Ownership run `30456714386` also passed.
- Exclusive claims: this task record and `data-otservbr-global/catalog/**`; narrow GitHub searches found no matching open PR or indexed task.
- Shared claims: program, catalogue, contract, cross-repository registry, architecture documentation, changelog, and Game Catalog workflow.
- Read-only dependencies: existing exporter and schema 1.1.
- Overlaps: none found by narrow GitHub search or deterministic ownership validation.
- Resolution: ownership is clear. Schema 1.1 removes the representation blocker; the separate default-datapack loot-integrity finding does not overlap the bounded metadata files.

# Current state

The archived exporter and schema 1.1 rollout are complete. The repository-default manifest root now contains a bounded Dragon/dragon-shield/loot seed. Runtime and content targets are `15.25`, while both content-boundary fields, all historical bounds, and completeness remain null or unverified. Repository spawns and runtime loot prove only `encounterable` and `obtainable`. Two bounded real-Dragon exports are deterministic after normalizing the controlled `generated_at`.

The full default datapack currently fails catalogue validation on pre-existing unresolved loot endpoints and loot chances above `MAX_LOOTCHANCE`. The exporter correctly fails closed. This task does not silently drop, clamp, or invent those records; the program must track their integrity repair separately before staging or production.

# Plan

1. Add the bounded Dragon, dragon-shield, and loot manifests with null historical bounds.
2. Pin claim-level repository evidence in tests and documentation.
3. Extend exact-head Game Catalog CI with two reviewed-metadata exports and syscall isolation.
4. Run deterministic focused export validation and current-head CI.
5. Update the program, contracts, catalogue, checkpoint, and merge/archive lifecycle.
6. Register the full default-datapack loot-integrity finding as a separate task before staging.

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

## 2026-07-29T16:25:00Z

- Changed: merged Platform #299 and Canary #1006 in consumer-first order; synchronized this branch with schema 1.1; added the reviewed default profile, release registry, item/creature/loot versioning, item/creature availability, claim-level evidence, focused tests, and an exact-head reviewed-metadata runtime smoke.
- Learned: dragon shield is runtime item `3416` and zero-based Dragon loot block `20`, producing source key `dragon|3416|20`. The bounded runtime exports 32,941 items/creatures and 21 Dragon loot relations.
- Validated: 13 focused Python tests passed; ownership passed for 36 active tasks; two 24,267,183-byte schema 1.1 snapshots and lowercase SHA-256 sidecars passed validation and were identical after normalizing only `generated_at`.
- Failed/blocked: local `ptrace` is unavailable, while the exact-head workflow retains syscall isolation. A full default-datapack export separately failed closed on pre-existing unresolved loot endpoints and out-of-range loot chance values.
- Result: the metadata seed is implemented without historical or completeness inference. Publication and exact-head CI remain before merge; full-datapack loot integrity is a separate pre-staging blocker.

## 2026-07-29T16:41:22Z

- Changed: published the bounded metadata implementation as `5ab9d1288875d2318d4943652caa76a9e774bcfb` and applied `ci:final-gate` before this final readiness checkpoint.
- Validated: Agent Task Ownership `30471275199`, CI `30471275856`, Universal E2E Stability `30471273492`, and Game Catalog `30471274026` passed on the implementation head.
- Proven: Game Catalog compiled the exporter and passed the isolated two-run export, schema and sidecar validation, normalized determinism comparison, no-network/no-database syscall tracing, and exact reviewed Dragon metadata assertions.
- Result: the bounded metadata package is ready for its exact-final-head gate. The full default-datapack loot-integrity finding remains a separate program blocker and is not hidden or reclassified.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Split metadata, entity families, and production activation into separate tasks | Repository policy requires bounded branches/PRs; schema and production risks differ materially. | none |
| Start with metadata evidence | Additional entity and activation work depends on trustworthy release/completeness/availability boundaries. | none |
| Target the repository-default datapack, not an unverified deployment | `config.lua.dist` selects `data-otservbr-global`; actual deployed configuration remains unknown. | none |
| Do not invent a v1 verified-content boundary or sentinel release | The schema requires a concrete release, but neither protocol 15.25 nor current datapack presence proves completeness. | required cross-repository schema decision |
| Use schema 1.1 with a null verified boundary | Platform #299 and Canary #1006 preserve unknown evidence and block activation. | none |
| Validate the seed through a bounded real-Dragon projection | It proves exact runtime identities and relation keys without hiding unrelated default-datapack integrity failures. | none |
| Keep full-datapack loot integrity separate | Fixing missing item endpoints or out-of-range chances requires evidence per source record and must not be bundled into reviewed metadata. | none |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `docs/agents/tasks/active/CAN-20260729-game-catalog-metadata-evidence.md` | exclusive | Task state and checkpoint | ready |
| `docs/agents/programs/GAME_CATALOG_COMPLETENESS_PROGRAM.md` | shared | Multi-task sequence and gates | active |
| `src/game/catalog/**` | read_only | Existing manifest loader/exporter | reused unchanged |
| `schemas/game-catalog/v1.1/**` | read_only | Unknown-boundary contract shape | reused unchanged |
| `data-otservbr-global/catalog/**` | exclusive | Repository-default reviewed metadata manifests | implemented |
| `tests/game_catalog/test_default_metadata.py` | exclusive | Claim-to-source regression tests | 3 tests pass |
| `.github/workflows/game-catalog.yml` | shared | Two-run reviewed-metadata runtime and syscall proof | passed on implementation head |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| `23a8148f72805676fa623c15ffa6ad20e7dc3d2f` | GitHub open PR/issue search for `catalog` | passed | No open matching PR or issue returned. |
| `666369126319bdac3ecc4ff83584011db1ce6c2f` | Agent Task Ownership `30456714386` | passed | Structured claims validated with no overlap. |
| `666369126319bdac3ecc4ff83584011db1ce6c2f` | CI `30456714463` | passed | Exact-head documentation/fast checks passed. |
| `20ab2db1d0041f86fc7978730c6cc289eb7ea763` | Game Catalog `30469294109` | passed | Schema 1.1 compile, isolated two-run export, sidecars, validation, and syscall isolation passed before producer merge. |
| `3ad7155dd833e105cebfd4b472800a4156ac1e90` + working tree | `python3 -m unittest discover -s tests/game_catalog -p 'test_*.py' -v` | passed | 13 tests, including 3 claim-to-source metadata tests. |
| `3ad7155dd833e105cebfd4b472800a4156ac1e90` + working tree | Bounded real-Dragon export, two controlled timestamps | passed | Both schema 1.1 snapshots contain 32,941 entities and 21 relations, valid sidecars, exact reviewed records, and match after normalizing only `generated_at`. |
| `3ad7155dd833e105cebfd4b472800a4156ac1e90` + working tree | Full repository-default datapack export | blocked | Fail-closed validation reports pre-existing unresolved item endpoints and loot chances above the declared denominator. |
| `5ab9d1288875d2318d4943652caa76a9e774bcfb` | Agent Task Ownership `30471275199` | passed | Exact implementation-head ownership and overlap validation. |
| `5ab9d1288875d2318d4943652caa76a9e774bcfb` | CI `30471275856` | passed | Exact implementation-head Required aggregator passed. |
| `5ab9d1288875d2318d4943652caa76a9e774bcfb` | Universal E2E Stability `30471273492` | passed | Exact implementation-head stability certification passed. |
| `5ab9d1288875d2318d4943652caa76a9e774bcfb` | Game Catalog `30471274026` | passed | Contract tests, compilation, two export-only runtime executions, schema/sidecar/determinism validation, syscall isolation, and reviewed metadata assertions passed. |
| PR #1005 before final checkpoint | `ci:final-gate` label | applied | Applied before the final checkpoint commit as required by `BUILD_TEST_MATRIX.md`. |

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
- Backward compatibility: schema `1.0.0` remains byte unchanged; this profile explicitly selects schema `1.1.0`.
- Cross-repo rollout: Platform #299 and Canary #1006 are merged in consumer-first order; null-boundary activation remains blocked.
- Rollback: no activation occurs; generated snapshots remain immutable files and prior active consumer state must remain unchanged.
- Data integrity: unresolved default-datapack loot endpoints and out-of-range chance values block a full snapshot until reviewed separately.

# Remaining work

1. Pass the full exact-final-head gate without further commits, audit reviews and main drift, then squash-merge PR #1005.
2. Let the repository lifecycle archive this task, then create a separate bounded task for default-datapack loot endpoint/probability integrity before staging.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T16:41:22Z
head: 5ab9d1288875d2318d4943652caa76a9e774bcfb
branch: feat/CAN-20260729-game-catalog-metadata-evidence
pr: 1005
status: ready
context_routes:
  - agent-governance
  - cpp-runtime
  - lua-data
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260729-game-catalog-metadata-evidence.md
  - docs/agents/programs/GAME_CATALOG_COMPLETENESS_PROGRAM.md
  - data-otservbr-global/catalog/**
  - tests/game_catalog/test_default_metadata.py
  - .github/workflows/game-catalog.yml
proven:
  - PR 991 merged the deterministic offline Game Catalog exporter and its task is archived.
  - Platform PR 299 merged schema 1.1 consumer support as b2b2871eed0375e22d48de5dd4947fe29c2bb974.
  - Canary PR 1006 merged schema 1.1 producer support as 3ad7155dd833e105cebfd4b472800a4156ac1e90.
  - data-otservbr-global is the repository default and its catalog root is the default manifest root.
  - Schema 1.1 preserves an unknown verified-content boundary as null and Platform blocks its activation.
  - Item 3416, creature Dragon, explicit Dragon spawns and Dragon loot block 20 prove the bounded runtime identities and availability claims.
  - Two bounded real-Dragon exports validated 32941 entities and 21 relations and matched after normalizing only generated_at.
  - The reviewed loot relation resolves to loot:dragon:dragon-shield with chance 110/100000.
  - Implementation-head Agent Task Ownership 30471275199, CI 30471275856, Universal E2E Stability 30471273492 and Game Catalog 30471274026 passed.
  - ci:final-gate was applied before the final checkpoint commit.
derived:
  - The bounded metadata seed is implementable without historical or completeness inference.
  - Full default-datapack integrity must be repaired before staging but does not invalidate the reviewed Dragon seed.
unknown:
  - Whether any deployed environment uses this repository-default profile.
  - Historical introduced_in and removed_in releases for the bounded dragon and dragon-shield seed.
  - Reviewed fixes for each unresolved default-datapack loot endpoint and out-of-range chance.
conflicts:
  - A full default-datapack snapshot fails closed on pre-existing unresolved loot endpoints and chances above MAX_LOOTCHANCE.
first_failure:
  marker: default-datapack-loot-integrity
  evidence: Full export validation reports dangling loot targets and chance numerators above the 100000 denominator.
rejected_hypotheses:
  - Use protocol 15.25 as completeness evidence: repository policy explicitly rejects that inference.
  - Silently drop dangling loot relations: the contract requires fail-closed endpoint integrity.
  - Clamp out-of-range loot chances without source review: the metadata task does not own datapack behavior corrections.
changed_paths:
  - docs/agents/programs/GAME_CATALOG_COMPLETENESS_PROGRAM.md
  - docs/agents/tasks/active/CAN-20260729-game-catalog-metadata-evidence.md
  - data-otservbr-global/catalog/**
  - tests/game_catalog/test_default_metadata.py
  - .github/workflows/game-catalog.yml
validation:
  - command: python3 -m unittest discover -s tests/game_catalog -p test_*.py -v
    result: PASS
    evidence: 13 focused tests passed, including three claim-to-source metadata tests.
  - command: python3 tools/agents/task_ownership.py
    result: PASS
    evidence: 36 active task records validated.
  - command: two bounded real-Dragon exports plus schema/sidecar validation
    result: PASS
    evidence: 24267183 bytes each; 32941 entities; 21 relations; normalized documents identical.
blockers:
  - Full exact-final-head validation must pass on the checkpoint commit before merge.
next_action: Freeze the final checkpoint commit, require exact-final-head Ownership, full CI and Game Catalog success, audit reviews and main drift, then squash-merge PR 1005 with the validated expected head.
```

# Handoff

## Start here

Read root and nested agent rules, the program record, this checkpoint, PR #991's archived task, the live draft PR, and current branch/head.

## Do not repeat

- Do not reopen PR #991 or its archived task.
- Do not infer historical or availability facts from external wikis.
- Treat `data-otservbr-global` only as the repository default; do not claim the deployed production datapack until direct configuration evidence proves it.
- Do not reopen the merged schema 1.1 producer/consumer tasks.
- Do not hide the full default-datapack loot-integrity failure by dropping relations or changing probabilities without record-level evidence.
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
- Which reviewed source corrections resolve every default-datapack loot-integrity failure?

# Completion

- Final status: ready
- PR: #1005
- Merge commit: none
- Program record updated: yes
- Catalogue updated: yes
- Changelog updated: yes
- Archived at: not archived
