---
task_id: CAN-20260729-game-catalog-loot-threshold-schema
program_id: CAN-PROGRAM-GAME-CATALOG-COMPLETENESS
coordination_id: "OTS-20260728-game-catalog-v1"
status: completed
agent: "chatgpt"
branch: feat/CAN-20260729-game-catalog-loot-threshold-schema
base_branch: main
created: 2026-07-29T18:11:53Z
updated: 2026-07-29T19:22:35Z
last_verified_commit: "daf6553426a57c8474a372160b2f1e3b4536b171"
risk: high
related_issue: ""
related_pr: 1012
depends_on:
  - CAN-20260729-game-catalog-loot-integrity
  - OTERYN-20260729-game-catalog-runtime-threshold
blocks:
  - Game Catalog staging snapshot
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260729-game-catalog-loot-threshold-schema.md
    - schemas/game-catalog/v1.2/**
    - tests/game_catalog/fixtures/v1.2/**
  shared:
    - src/game/catalog/game_catalog_manifest.hpp
    - src/game/catalog/game_catalog_manifest.cpp
    - src/game/catalog/game_catalog_exporter.cpp
    - tests/unit/game/catalog/game_catalog_test.cpp
    - tools/game-catalog/validate_snapshot.py
    - tests/game_catalog/test_validate_snapshot.py
    - tests/game_catalog/test_default_metadata.py
    - data-otservbr-global/catalog/profile.json
    - .github/workflows/game-catalog.yml
    - docs/agents/programs/GAME_CATALOG_COMPLETENESS_PROGRAM.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CROSS_REPO_CONTRACTS.md
    - docs/contracts/GAME_CATALOG_EXPORT_CONTRACT.md
    - docs/systems/GAME_CATALOG_EXPORTER.md
    - docs/agents/CHANGELOG.md
modules_touched:
  - oteryn.game-catalog schema 1.2 producer
reuses:
  - Game Catalog exporter from PR #991
  - endpoint integrity from PR #1010
  - Platform schema 1.2 consumer from PR #310
public_interfaces:
  - oteryn.game-catalog schema 1.2 creature_loot chance model
cross_repo_tasks:
  - OTERYN-20260729-game-catalog-runtime-threshold
completed: 2026-07-29T19:22:35Z
---

# Goal

Emit the consumer-approved Game Catalog schema 1.2 runtime loot-threshold model from Canary without changing schema 1.0/1.1 bytes, dropping or clamping configured thresholds, or activating any snapshot.

# Acceptance criteria

- [x] Pin byte-identical Platform schema 1.2 and sanitized fixture files with exact SHA-256 hashes.
- [x] Preserve schema 1.0 and 1.1 bytes, hashes, manifests, export, and validation behavior.
- [x] Accept schema 1.2 profiles only with an explicit positive loot roll maximum.
- [x] Emit `canary_dynamic_threshold_v1`, exact configured threshold, and declared roll maximum for every schema 1.2 loot relation.
- [x] Reject mixed or malformed schema/model payloads fail closed.
- [x] Keep exact count, nesting, condition, metadata, ordering, determinism, atomic publication, and sidecar behavior.
- [x] Make the repository-default schema 1.2 export succeed with zero dangling endpoints and all 92 over-maximum configured thresholds preserved.
- [x] Keep export-only runtime free of database and network endpoint syscalls.
- [x] Pass focused Python/C++ tests, exact-head Game Catalog, ownership, repository CI, and stability workflows.
- [x] Update the program, module catalogue, contract, system design, changelog, and cross-repository record.
- [x] Do not import, activate, deploy, or mutate a production snapshot.
- [ ] Satisfy the autonomous merge gate.

# Confirmed context

- Canary PR #1010 merged as `24ce121f487f711cc19214f59ac0fb21d80ff737`, proving zero dangling endpoints and preserving exactly 92 configured thresholds above the schema 1.1 denominator.
- Platform PR #310 merged as `2a97d0a04f1d6ecc02f4ec52b8aba1839a0ac77b` with consumer-first schema 1.2, inactive transactional import, persistence, public projection, and rollback protection.
- Platform schema 1.2 SHA-256 is `a9fa1e3c6366a90d61005796511c344ced9c39594ed676276279a5917287c6de`.
- Platform fixture SHA-256 is `42b832954f9aa68cf7e2465351f92266771b8132d9634757391d010eaec84855`.
- Schemas 1.0 and 1.1 remain immutable compatibility contracts.

# Plan

1. Pin the exact consumer schema and fixture.
2. Add schema-aware manifest loading, relation emission, and semantic validation.
3. Migrate the repository-default profile and workflow fixtures to 1.2 while retaining focused legacy tests.
4. Prove complete default-datapack publication, determinism, sidecars, and isolation.
5. Run exact-head gates, merge, and archive this task.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Use `loot_roll_maximum` only in schema 1.2 profiles | Avoid reinterpreting the legacy probability denominator while supplying the consumer-approved threshold context. | Platform ADR 0019 |
| Emit threshold fields only for schema 1.2 | Schema 1.0/1.1 bytes and semantics remain unchanged. | Platform ADR 0019 |
| Keep default threshold values exact | PR #1010 proved these are configured runtime evidence, not malformed probability numerators. | none |

# Validation and CI

Never write `passed` without verification on the stated commit.

# Work log

## 2026-07-29T18:11:53Z

- Changed: created the bounded producer task after Platform #310 and Canary lifecycle #1011 merged.
- Validated: ownership accepted 33 active tasks before the new claim.
- Result: schema 1.2 implementation may proceed without overlap; production remains excluded.

## 2026-07-29T18:18:00Z

- Changed: pinned the exact Platform schema/fixture, added schema-aware manifest loading, threshold-model emission and semantic validation, migrated the default profile/workflow to 1.2, and retained focused legacy behavior.
- Validated: 17 focused Python tests, task ownership, checkpoint validation, immutable 1.0/1.1 hashes, and exact 1.2 schema/fixture hashes pass locally.
- Result: exact C++ compilation and full default-datapack runtime export remain for CI.

## 2026-07-29T18:36:30Z

- Learned: diagnostic run `30480109834` did not reach CMake or runtime because its reusable build runner remained stuck installing Mono/NuGet.
- Result: publish a neutral checkpoint to cancel the stuck concurrency group and obtain a fresh exact-head runner; the runtime exit-139 finding remains unresolved.

## 2026-07-29T18:46:00Z

- Learned: fresh run `30480742859` reproduced exit 139 after `proficiencies.json` and before manifest loading; schema parsing, relation validation, serialization, and publication have not begun at the crash point.
- Changed: enabled the existing loader-duration telemetry only in the isolated CI config so the next run identifies the exact failing definition loader.
- Result: the remaining failure is in default-datapack definition initialization, not the schema 1.2 file contract.

## 2026-07-29T18:52:00Z

- Validated: exact-head Game Catalog run `30481456654` passed contract/fixture validation, C++ compilation, two deterministic schema 1.2 exports, reviewed metadata, and the complete default datapack with all 92 over-maximum thresholds preserved.
- Validated: runtime job `90677903702` and its exact-artifact rerun `90678481552` both passed, including SHA-256 sidecars and empty database/network endpoint syscall traces.
- Validated: CI `30481461659`, Agent Task Ownership `30481456054`, and Universal E2E Stability `30481455717` passed on `e85be1bf6e237448d624d28ff891362d5f67f9b6`.
- Result: schema 1.2 producer acceptance is complete. The telemetry-sensitive earlier exit 139 remains explicit and is queued as a separate loader-stability task before staging or production readiness.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T19:22:35Z
head: 8bc7dff7508610585e7343ffe73634f34ab02f09
branch: feat/CAN-20260729-game-catalog-loot-threshold-schema
pr: 1012
status: ready
context_routes:
  - agent-governance
  - cpp-runtime
  - lua-data
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260729-game-catalog-loot-threshold-schema.md
  - schemas/game-catalog/v1.2/**
  - tests/game_catalog/fixtures/v1.2/**
  - src/game/catalog/game_catalog_manifest.hpp
  - src/game/catalog/game_catalog_manifest.cpp
  - src/game/catalog/game_catalog_exporter.cpp
  - tools/game-catalog/validate_snapshot.py
  - tests/game_catalog/fixtures/v1.2/**
  - tests/game_catalog/test_validate_snapshot.py
  - tests/game_catalog/test_default_metadata.py
  - tests/unit/game/catalog/game_catalog_test.cpp
  - data-otservbr-global/catalog/profile.json
  - .github/workflows/game-catalog.yml
proven:
  - Canary PR 1010 resolves default-datapack endpoints and preserves exactly 92 configured over-maximum thresholds.
  - Platform PR 310 merged consumer-first schema 1.2 support.
  - Platform schema and fixture hashes are pinned and known.
  - Canary schema 1.2 and fixture bytes match the merged Platform files exactly.
  - Focused validation accepts schema 1.2 threshold evidence above the roll maximum and rejects mixed payloads.
  - Exact-head C++ compilation and two complete runtime-smoke executions pass with schema 1.2.
  - The complete default datapack publishes atomically with zero dangling endpoints and exactly 92 configured thresholds above roll maximum.
  - Both complete runtime jobs produce valid lowercase SHA-256 sidecars and no database/network endpoint syscalls.
derived:
  - Canary may now emit schema 1.2 after pinning identical bytes and branching producer semantics by schema version.
unknown:
  - Root cause of the two telemetry-free pre-manifest exit-139 failures.
conflicts:
  - Default initialization exited 139 twice without loader telemetry, while two exact-artifact executions with loader telemetry passed; staging must retain a separate stability gate rather than infer the cause.
first_failure:
  marker: none
  evidence: Final-head Game Catalog run 30482339983 passed; prior exit-139 evidence remains preserved under conflicts and the program queue.
rejected_hypotheses:
  - Change schema 1.1 in place because its bytes and probability semantics are immutable.
  - Clamp configured thresholds because that loses runtime evidence.
  - Treat threshold divided by roll maximum as a context-free percentage because runtime modifiers remain active.
changed_paths:
  - .github/workflows/game-catalog.yml
  - data-otservbr-global/catalog/profile.json
  - docs/agents/CHANGELOG.md
  - docs/agents/CROSS_REPO_CONTRACTS.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/programs/GAME_CATALOG_COMPLETENESS_PROGRAM.md
  - docs/agents/tasks/active/CAN-20260729-game-catalog-loot-threshold-schema.md
  - docs/contracts/GAME_CATALOG_EXPORT_CONTRACT.md
  - docs/systems/GAME_CATALOG_EXPORTER.md
  - schemas/game-catalog/v1.2/game-catalog-snapshot.schema.json
  - src/game/catalog/game_catalog_exporter.cpp
  - src/game/catalog/game_catalog_manifest.cpp
  - src/game/catalog/game_catalog_manifest.hpp
  - tests/game_catalog/fixtures/v1.2/minimal-snapshot.json
  - tests/game_catalog/test_default_metadata.py
  - tests/game_catalog/test_validate_snapshot.py
  - tests/unit/game/catalog/game_catalog_test.cpp
  - tools/game-catalog/validate_snapshot.py
validation:
  - command: python3 tools/agents/task_ownership.py
    result: PASS
    evidence: 33 active task records validated before this task was added.
  - command: python3 -m unittest discover -s tests/game_catalog -p test_*.py -v
    result: PASS
    evidence: 17 focused schema, metadata, runtime-formula, and semantic validation tests pass.
  - command: sha256sum schemas and fixtures
    result: PASS
    evidence: Schema 1.0 and 1.1 retain their pinned hashes; schema 1.2 is a9fa1e3c6366a90d61005796511c344ced9c39594ed676276279a5917287c6de and fixture is 42b832954f9aa68cf7e2465351f92266771b8132d9634757391d010eaec84855.
  - command: python3 tools/agents/task_ownership.py
    result: PASS
    evidence: 34 active task records validate after the new ownership claim.
  - command: Game Catalog 30479374835
    result: FAIL
    evidence: Contract and C++ compilation passed; default-datapack runtime export exited 139. The next workflow revision captures and prints the redirected process log before propagating failure.
  - command: Game Catalog 30480109834
    result: NOT_RUN
    evidence: Contract passed, but the reusable build runner remained in dependency installation and never reached CMake or the diagnostic runtime step.
  - command: Game Catalog 30480742859
    result: FAIL
    evidence: Contract, C++ compilation, deterministic schema 1.2 smoke, and reviewed metadata export passed; complete default-datapack initialization reproducibly exited 139 immediately after proficiencies and before manifest loading.
  - command: Game Catalog 30482339983
    result: PASS
    evidence: Contract, C++ compilation, deterministic and reviewed exports, full default-datapack schema 1.2 publication, 92 preserved over-maximum thresholds, sidecars, and endpoint isolation passed on 8bc7dff7508610585e7343ffe73634f34ab02f09.
  - command: Export-only runtime smoke rerun 90678481552
    result: PASS
    evidence: The exact same binary artifact and head repeated the complete runtime proof successfully.
  - command: CI 30482340085 and readiness-gate rerun 30483038437
    result: PASS
    evidence: Repository CI and the branch-protection Required aggregator passed on the exact final head.
  - command: Agent Task Ownership 30482339673
    result: PASS
    evidence: Ownership and lifecycle validation passed on the exact implementation head.
  - command: Universal E2E Stability Certification 30482339647
    result: PASS
    evidence: Repository stability certification passed on the exact implementation head.
blockers: []
next_action: Start the separate telemetry-independent definition-loader stability task before any staging snapshot work.
```

## Automated lifecycle completion

- Feature PR: #1012.
- Feature head: `8bc7dff7508610585e7343ffe73634f34ab02f09`.
- Merge commit: `daf6553426a57c8474a372160b2f1e3b4536b171`.
- Merged at: `2026-07-29T19:22:35Z`.
- This record was moved from `tasks/active` by the post-merge lifecycle automation.
