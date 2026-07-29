---
task_id: CAN-20260729-game-catalog-schema-1-1
program_id: CAN-PROGRAM-GAME-CATALOG-COMPLETENESS
coordination_id: "OTS-20260728-game-catalog-v1"
status: implementing
agent: "chatgpt"
branch: feat/CAN-20260729-game-catalog-schema-1-1
base_branch: main
created: 2026-07-29T15:20:00Z
updated: 2026-07-29T15:20:00Z
last_verified_commit: "pending"
risk: high
related_issue: ""
related_pr: 1006
depends_on:
  - CAN-20260728-game-catalog-exporter
blocks:
  - CAN-20260729-game-catalog-metadata-evidence
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260729-game-catalog-schema-1-1.md
    - schemas/game-catalog/v1.1/**
    - src/game/catalog/game_catalog_manifest.hpp
    - src/game/catalog/game_catalog_manifest.cpp
    - src/game/catalog/game_catalog_exporter.cpp
    - tests/unit/game/catalog/game_catalog_test.cpp
    - tests/game_catalog/fixtures/v1.1/**
  shared:
    - tools/game-catalog/validate_snapshot.py
    - tests/game_catalog/test_validate_snapshot.py
    - .github/workflows/game-catalog.yml
    - docs/agents/CROSS_REPO_CONTRACTS.md
    - docs/agents/MODULE_CATALOG.md
    - docs/contracts/GAME_CATALOG_EXPORT_CONTRACT.md
    - docs/systems/GAME_CATALOG_EXPORTER.md
    - docs/agents/CHANGELOG.md
  read_only:
    - data-otservbr-global/catalog/**
modules_touched:
  - Game Catalog exporter contract
reuses:
  - Game Catalog exporter from PR #991
  - tools/game-catalog/validate_snapshot.py
public_interfaces:
  - oteryn.game-catalog schema 1.1.0
cross_repo_tasks:
  - OTERYN-20260729-game-catalog-null-boundary
---

# Goal

Add Game Catalog schema 1.1.0 so the producer can emit an explicit null `verified_content_through_release` when the datapack-wide evidence boundary is unknown, without changing schema 1.0.0 or weakening deterministic and fail-closed validation.

# Acceptance criteria

- [ ] Schema 1.0.0 remains byte unchanged.
- [ ] Schema 1.1.0 changes only the versioned semantics needed to permit a null verified-content boundary.
- [ ] Manifest loading accepts schema 1.1.0 with a nullable verified boundary and continues to reject unsupported versions.
- [ ] Exported schema 1.1.0 documents preserve null without a sentinel.
- [ ] C++ and Python validation accept null only under schema 1.1.0 and reject schema/version mismatches.
- [ ] Fixed-input exports remain deterministic.
- [ ] Canary and Platform schema bytes and SHA-256 match exactly, and each repository's sanitized fixture validates.
- [ ] Focused unit, validator, exporter and exact-head CI checks pass.
- [ ] Contract, exporter documentation, module catalogue and changelog are current.
- [ ] Consumer-first rollout keeps producer merge blocked until Platform PR #299 is merged.
- [ ] No datapack manifest or production activation is included.

# Ownership and overlap

- PR #1005 owns `data-otservbr-global/catalog/**` and treats exporter/schema paths as read-only.
- This task owns the versioned producer/schema change and treats the datapack manifest root as read-only.
- The tasks are ordered: schema 1.1.0 first, then metadata manifests resume in #1005.
- Platform counterpart: `OTERYN-20260729-game-catalog-null-boundary`, draft PR #299.

# Current state

Schema 1.0.0 requires a concrete `verified_content_through_release`. Repository evidence does not prove a datapack-wide boundary. Protocol 15.25, current runtime presence, external wikis and sentinel releases are not valid substitutes.

# Plan

1. Add byte-stable schema/fixture 1.1.0 while retaining 1.0.0.
2. Make manifest schema version and verified boundary explicit versioned fields.
3. Update snapshot construction and validation for nullable 1.1.0 semantics.
4. Add C++/Python tests for 1.0 compatibility, 1.1 null acceptance and version mismatch rejection.
5. Synchronize exact schema bytes with Platform PR #299 and validate both sanitized fixtures.
6. Run focused validation and exact-head CI; merge Platform first, then Canary.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T15:20:00Z
head: fef73c5b4a43f3d64afb8770b2aef38041d6c2fc
branch: feat/CAN-20260729-game-catalog-schema-1-1
pr: 1006
status: implementing
context_routes:
  - agent-governance
  - cpp-runtime
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260729-game-catalog-schema-1-1.md
  - schemas/game-catalog/v1.1/**
  - src/game/catalog/game_catalog_manifest.hpp
  - src/game/catalog/game_catalog_manifest.cpp
  - src/game/catalog/game_catalog_exporter.cpp
  - tests/unit/game/catalog/game_catalog_test.cpp
  - tests/game_catalog/fixtures/v1.1/**
  - tools/game-catalog/validate_snapshot.py
  - tests/game_catalog/test_validate_snapshot.py
  - .github/workflows/game-catalog.yml
  - docs/agents/CROSS_REPO_CONTRACTS.md
  - docs/agents/MODULE_CATALOG.md
  - docs/contracts/GAME_CATALOG_EXPORT_CONTRACT.md
  - docs/systems/GAME_CATALOG_EXPORTER.md
  - docs/agents/CHANGELOG.md
proven:
  - Schema 1.0.0 requires verified_content_through_release to be a concrete release key.
  - The exporter stores the field as a non-null string and hard-codes schema_version 1.0.0.
  - Metadata task PR #1005 cannot honestly add a production-default profile under schema 1.0.0.
  - Platform draft PR #299 is the authorized consumer counterpart.
derived:
  - A new schema version is required; schema 1.0.0 must remain unchanged.
  - The producer must serialize null rather than invent a release.
unknown:
  - Exact current-head C++ build, exporter smoke and CI results until the implementation commit runs.
conflicts: []
first_failure:
  marker: v1-verified-boundary-unrepresentable
  evidence: Required concrete v1 field conflicts with the unproven datapack-wide boundary.
rejected_hypotheses:
  - Infer the boundary from protocol 15.25.
  - Invent a sentinel release.
  - Mutate schema 1.0.0 in place.
changed_paths:
  - .github/workflows/game-catalog.yml
  - schemas/game-catalog/v1.1/game-catalog-snapshot.schema.json
  - src/game/catalog/game_catalog_exporter.cpp
  - src/game/catalog/game_catalog_manifest.cpp
  - src/game/catalog/game_catalog_manifest.hpp
  - tests/game_catalog/fixtures/v1.1/minimal-snapshot.json
  - tests/game_catalog/test_validate_snapshot.py
  - tests/unit/game/catalog/game_catalog_test.cpp
  - tools/game-catalog/validate_snapshot.py
  - docs/agents/CHANGELOG.md
  - docs/agents/CROSS_REPO_CONTRACTS.md
  - docs/agents/MODULE_CATALOG.md
  - docs/contracts/GAME_CATALOG_EXPORT_CONTRACT.md
  - docs/systems/GAME_CATALOG_EXPORTER.md
  - docs/agents/tasks/active/CAN-20260729-game-catalog-schema-1-1.md
validation:
  - command: overlap search
    result: PASS
    evidence: PR #1005 has complementary ownership and no other matching active task was found.
  - command: python -m unittest discover -s tests/game_catalog -p 'test_*.py' -v
    result: PASS
    evidence: 10 validator tests passed for schema 1.0 compatibility, schema 1.1 null handling and mismatched-version rejection.
  - command: python tools/game-catalog/validate_snapshot.py for v1 and v1.1 fixtures
    result: PASS
    evidence: Schema hashes 099a8373... and 323ff6ae... plus fixture hashes ec0658bb... and 747467af... validated.
  - command: python tools/agents/task_ownership.py
    result: PASS
    evidence: 35 active task records validated locally.
  - command: focused C++ build and unit tests
    result: NOT_RUN
    evidence: CMake is not installed in the local execution environment; exact-head Game Catalog CI is required.
blockers:
  - Platform PR #299 must merge before Canary schema 1.1.0 producer support.
  - Current-head CI has not run for the implementation commit.
next_action: Publish the implementation commit to PR #1006 and use exact-head CI to validate compilation, tests and export-only runtime behavior.
```

# Risks and compatibility

- Older consumers must reject 1.1.0 fail closed.
- New consumers must retain stored 1.0.0 rollback compatibility.
- Null means unknown, never complete or verified.
- No production import, activation, secrets, database access or network calls are part of this task.
