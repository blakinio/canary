---
task_id: CAN-20260729-game-catalog-schema-1-1
program_id: CAN-PROGRAM-GAME-CATALOG-COMPLETENESS
coordination_id: "OTS-20260728-game-catalog-v1"
status: planned
agent: "chatgpt"
branch: feat/CAN-20260729-game-catalog-schema-1-1
base_branch: main
created: 2026-07-29T15:20:00Z
updated: 2026-07-29T15:20:00Z
last_verified_commit: "pending"
risk: high
related_issue: ""
related_pr: null
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
    - docs/agents/programs/GAME_CATALOG_COMPLETENESS_PROGRAM.md
    - docs/agents/CROSS_REPO_CONTRACTS.md
    - docs/agents/MODULE_CATALOG.md
    - docs/contracts/GAME_CATALOG_EXPORT_CONTRACT.md
    - docs/systems/GAME_CATALOG_EXPORTER.md
    - CHANGELOG.md
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
- [ ] Canary and Platform schema/fixture bytes and SHA-256 values match exactly.
- [ ] Focused unit, validator, exporter and exact-head CI checks pass.
- [ ] Contract, exporter documentation, module catalogue, changelog and program state are current.
- [ ] Atomic cross-repository merge remains blocked until Platform PR #299 is ready.
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
5. Synchronize exact schema/fixture bytes with Platform PR #299.
6. Run focused validation and exact-head CI; merge neither side until both are ready.

# Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T15:20:00Z
head: pending
branch: feat/CAN-20260729-game-catalog-schema-1-1
pr: pending
status: investigating
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
  - docs/agents/programs/GAME_CATALOG_COMPLETENESS_PROGRAM.md
  - docs/agents/CROSS_REPO_CONTRACTS.md
  - docs/agents/MODULE_CATALOG.md
  - docs/contracts/GAME_CATALOG_EXPORT_CONTRACT.md
  - docs/systems/GAME_CATALOG_EXPORTER.md
  - CHANGELOG.md
proven:
  - Schema 1.0.0 requires verified_content_through_release to be a concrete release key.
  - The exporter stores the field as a non-null string and hard-codes schema_version 1.0.0.
  - Metadata task PR #1005 cannot honestly add a production-default profile under schema 1.0.0.
  - Platform draft PR #299 is the authorized consumer counterpart.
derived:
  - A new schema version is required; schema 1.0.0 must remain unchanged.
  - The producer must serialize null rather than invent a release.
unknown:
  - Exact schema and fixture SHA-256 values until both repositories generate the same bytes.
conflicts: []
first_failure:
  marker: v1-verified-boundary-unrepresentable
  evidence: Required concrete v1 field conflicts with the unproven datapack-wide boundary.
rejected_hypotheses:
  - Infer the boundary from protocol 15.25.
  - Invent a sentinel release.
  - Mutate schema 1.0.0 in place.
changed_paths:
  - docs/agents/tasks/active/CAN-20260729-game-catalog-schema-1-1.md
validation:
  - command: overlap search
    result: PASS
    evidence: PR #1005 has complementary ownership and no other matching active task was found.
blockers:
  - Atomic merge is held until Platform PR #299 is ready.
next_action: Publish the draft PR and implement schema 1.1.0 producer support without datapack activation.
```

# Risks and compatibility

- Older consumers must reject 1.1.0 fail closed.
- New consumers must retain stored 1.0.0 rollback compatibility.
- Null means unknown, never complete or verified.
- No production import, activation, secrets, database access or network calls are part of this task.
