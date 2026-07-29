---
task_id: CAN-20260729-game-catalog-schema-1-1
program_id: CAN-PROGRAM-GAME-CATALOG-COMPLETENESS
coordination_id: "OTS-20260728-game-catalog-v1"
status: completed
agent: "chatgpt"
branch: feat/CAN-20260729-game-catalog-schema-1-1
base_branch: main
created: 2026-07-29T15:20:00Z
updated: 2026-07-29T16:18:03Z
last_verified_commit: "3ad7155dd833e105cebfd4b472800a4156ac1e90"
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
completed: 2026-07-29T16:18:03Z
---

# Goal

Add Game Catalog schema 1.1.0 so the producer can emit an explicit null `verified_content_through_release` when the datapack-wide evidence boundary is unknown, without changing schema 1.0.0 or weakening deterministic and fail-closed validation.

# Acceptance criteria

- [x] Schema 1.0.0 remains byte unchanged.
- [x] Schema 1.1.0 changes only the versioned semantics needed to permit a null verified-content boundary.
- [x] Manifest loading accepts schema 1.1.0 with a nullable verified boundary and continues to reject unsupported versions.
- [x] Exported schema 1.1.0 documents preserve null without a sentinel.
- [x] C++ and Python validation accept null only under schema 1.1.0 and reject schema/version mismatches.
- [x] Fixed-input exports remain deterministic.
- [x] Canary and Platform schema bytes and SHA-256 match exactly, and each repository's sanitized fixture validates.
- [x] Focused unit, validator, exporter and exact-head CI checks pass.
- [x] Contract, exporter documentation, module catalogue and changelog are current.
- [x] Platform PR #299 merged before producer finalization.
- [x] No datapack manifest or production activation is included.

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
updated_at: 2026-07-29T16:07:15Z
head: 57dd84c10ba582597ba00daa38437a3c88b99c4d
branch: feat/CAN-20260729-game-catalog-schema-1-1
pr: 1006
status: ready
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
  - Platform PR #299 merged consumer support as b2b2871eed0375e22d48de5dd4947fe29c2bb974.
  - Schema 1.0.0 remains SHA-256 099a8373ff2b0017cc2b321991662dc4e4783b626391aa7a110a6db0559d146b.
  - Schema 1.1.0 is byte-identical across Canary and Platform with SHA-256 323ff6ae849759c9190f2a0c342855194ed74645816adc45051b6d914e67c7ac.
  - Game Catalog run 30466876088 compiled the producer and passed two export-only runtime executions with deterministic snapshots and sidecars.
derived:
  - A new schema version is required; schema 1.0.0 must remain unchanged.
  - The producer must serialize null rather than invent a release.
unknown: []
conflicts: []
first_failure:
  marker: none
  evidence: Versioned producer and consumer support now represent the unknown boundary explicitly and exact-head validation passed.
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
    result: PASS
    evidence: Game Catalog 30466876088 compiled the Linux release exporter and passed contract, fixture, focused tests and export-only runtime smoke at 57dd84c10ba582597ba00daa38437a3c88b99c4d.
  - command: exact-head Canary gates
    result: PASS
    evidence: CI 30466876132, Agent Task Ownership 30466876597 and Universal E2E Stability 30466875836 passed at 57dd84c10ba582597ba00daa38437a3c88b99c4d.
  - command: consumer-first cross-repository gate
    result: PASS
    evidence: Platform PR 299 passed its exact-head gates and squash-merged as b2b2871eed0375e22d48de5dd4947fe29c2bb974 before this producer finalization.
  - command: ci:final-gate label
    result: PASS
    evidence: Label applied to PR 1006 before this final checkpoint commit.
blockers: []
next_action: Wait for exact-final-head required checks, verify unchanged scope and review state, then squash-merge PR 1006.
```

# Risks and compatibility

- Older consumers must reject 1.1.0 fail closed.
- New consumers must retain stored 1.0.0 rollback compatibility.
- Null means unknown, never complete or verified.
- No production import, activation, secrets, database access or network calls are part of this task.

## Automated lifecycle completion

- Feature PR: #1006.
- Feature head: `20ab2db1d0041f86fc7978730c6cc289eb7ea763`.
- Merge commit: `3ad7155dd833e105cebfd4b472800a4156ac1e90`.
- Merged at: `2026-07-29T16:18:03Z`.
- This record was moved from `tasks/active` by the post-merge lifecycle automation.
