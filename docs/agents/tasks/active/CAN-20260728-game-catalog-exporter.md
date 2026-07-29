---
task_id: CAN-20260728-game-catalog-exporter
program_id: none
agent: chatgpt
branch: feat/CAN-20260728-game-catalog-exporter
status: ready
related_pr: 991
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260728-game-catalog-exporter.md
    - src/game/catalog/**
    - tools/game-catalog/**
    - tests/game_catalog/**
    - tests/fixtures/game-catalog/**
    - tests/unit/game/catalog/**
    - data-otservbr-global/catalog/**
  shared:
    - src/main.cpp
    - src/canary_server.hpp
    - src/canary_server.cpp
    - CMakeLists.txt
    - src/CMakeLists.txt
    - src/game/CMakeLists.txt
    - tests/unit/game/CMakeLists.txt
    - .github/workflows/game-catalog.yml
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CROSS_REPO_CONTRACTS.md
    - docs/agents/BUILD_TEST_MATRIX.md
required_reads:
  - AGENTS.md
  - docs/agents/REPOSITORY_MAP.md
  - docs/agents/CONTEXT_ROUTING.md
  - docs/contracts/GAME_CATALOG_EXPORT_CONTRACT.md
  - docs/systems/GAME_CATALOG_EXPORTER.md
  - docs/agents/CROSS_REPO_CONTRACTS.md
  - schemas/game-catalog/v1/game-catalog-snapshot.schema.json
search_first:
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/KNOWN_RISKS.md
  - docs/agents/BUILD_TEST_MATRIX.md
  - startup CLI, item registry, MonsterType registry, loot and atomic writer implementations
optional_reads:
  - docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md
---

# CAN-20260728-game-catalog-exporter

## Goal

Deliver the deterministic offline Canary exporter for contract `oteryn.game-catalog` schema `1.0.0`, using final runtime item, MonsterType and loot registries plus reviewed fail-closed manifests, without starting the world, network services or database-mutating startup work.

## Acceptance criteria

- [x] `canary --export-game-catalog-only --game-catalog-output=<path>` loads only the bounded catalogue prerequisites and exits without normal world startup.
- [x] Items, creatures and loot are collected from final authoritative runtime registries rather than a duplicate partial parser.
- [x] Version, completeness and availability manifests fail closed and preserve UNKNOWN facts.
- [x] Output is deterministic with fixed `generated_at`, validated before atomic publication and accompanied by a lowercase SHA-256 sidecar.
- [x] The shared sanitized fixture validates and remains byte-compatible with Platform expectations.
- [x] Tests prove version semantics, collisions, dangling references, exact runtime values, loot numerators/denominators/counts, deterministic bytes, failure preservation and absence of startup side effects.
- [x] Schema bytes remain unchanged and match Platform SHA-256 `099a8373ff2b0017cc2b321991662dc4e4783b626391aa7a110a6db0559d146b`.
- [x] Required exact-head exporter CI and cross-repository staging validation pass; no production server, datapack activation or deployment occurs.

## Ownership

```yaml
owned_paths:
  - src/game/catalog/**
  - tools/game-catalog/**
  - tests/game_catalog/**
  - tests/fixtures/game-catalog/**
  - tests/unit/game/catalog/**
  - data-otservbr-global/catalog/**
  - docs/agents/tasks/active/CAN-20260728-game-catalog-exporter.md
  - docs/agents/tasks/deferred/CAN-20260728-game-catalog-*.md
  - src/main.cpp
  - src/canary_server.hpp
  - src/canary_server.cpp
  - CMakeLists.txt
  - src/CMakeLists.txt
  - src/game/CMakeLists.txt
  - tests/unit/game/CMakeLists.txt
  - .github/workflows/game-catalog.yml
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CROSS_REPO_CONTRACTS.md
modules:
  - game-catalog-export
  - items
  - monsters
  - startup-cli
  - cross-repo-contracts
dependencies:
  - contract: oteryn.game-catalog
  - schema_version: 1.0.0
  - parent: CAN-20260728-game-catalog-export-architecture
  - OTERYN-20260728-game-catalog-implementation
blockers: []
cross_repository_tasks:
  - OTERYN-20260728-game-catalog-implementation
```

## Coordination

- Rollout order: Canary exporter and shared fixture validation first; Platform importer second; Platform activation/public visibility third; cross-repository E2E fourth.
- Schema changes are atomic cross-repository contract changes. The existing schema must not be modified silently.
- External wikis are never authoritative for exported facts.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T06:45:00Z
implementation_head: 84b089f9a919bb85773798584e5b0205e2e5895c
branch: feat/CAN-20260728-game-catalog-exporter
pr: 991
status: ready
context_routes:
  - agent-governance
  - cpp-runtime
  - lua-data
  - cross-repo
owned_paths:
  - src/game/catalog/**
  - tools/game-catalog/**
  - tests/game_catalog/**
  - tests/unit/game/catalog/**
  - data-otservbr-global/catalog/**
  - docs/agents/tasks/active/CAN-20260728-game-catalog-exporter.md
proven:
  - Export-only CLI parsing, fail-closed manifest loading, final runtime registry collection, semantic validation and atomic snapshot publication are implemented.
  - Export mode is selected before normal CanaryServer startup and excludes database initialization, maps, listeners, schedulers, backups and database-backed shutdown work.
  - Items and creatures are read from final runtime registries and loot from MonsterType runtime loot blocks.
  - Non-unique ware and race values remain data-only; only globally unique values become identifiers, identifiers are deterministically sorted, and producer-side collision validation fails closed.
  - Missing reviewed metadata remains unverified or unknown; historical and availability facts are not inferred from external wikis.
  - Fixed-input exports are byte deterministic apart from the explicitly controlled generated_at value and include lowercase SHA-256 sidecars.
  - Exact-head Game Catalog run 30427617799 passed contract validation, C++ compilation and two export-only runtime executions without network or database endpoint syscalls.
  - Exact artifact 8714331268 has digest sha256:e389915bff1f79e21cbb7b112717550587d3a556afa11e707c0036ba8b2aa5a6 and records producer SHA 84b089f9a919bb85773798584e5b0205e2e5895c.
  - Platform Game Catalog Contract run 30428491404 passed MariaDB import, staging activation, candidate activation and rollback using that generated artifact.
  - No production deployment or production profile activation occurred.
derived:
  - The exporter and schema 1.0.0 consumer are cross-repository compatible for the first item, creature and loot slice.
  - The bounded staging artifact is evidence only and does not authorize production activation.
unknown:
  - Complete historical introduced_in, removed_in and availability metadata remains outside this slice.
  - Exact reviewed manifests for future production content remain a separate evidence programme.
conflicts: []
first_failure:
  marker: none
  evidence: Exact-head exporter smoke and cross-repository MariaDB lifecycle are green.
rejected_hypotheses:
  - Build a second XML or Lua parser that approximates runtime state.
  - Infer availability or historical release metadata from external wikis.
  - Start normal world services and stop them after export.
  - Treat non-unique ware_id or race_id values as globally unique identifiers.
changed_paths:
  - src/game/catalog/**
  - src/main.cpp
  - src/canary_server.hpp
  - src/canary_server.cpp
  - src/game/CMakeLists.txt
  - tests/unit/game/catalog/game_catalog_test.cpp
  - tests/unit/game/CMakeLists.txt
  - tools/game-catalog/**
  - tests/game_catalog/**
  - .github/workflows/game-catalog.yml
validation:
  - command: Game Catalog workflow
    result: PASS
    evidence: exact-head run 30427617799 at 84b089f9a919bb85773798584e5b0205e2e5895c
  - command: Agent Task Ownership workflow
    result: PASS
    evidence: exact-head run 30427617671
  - command: Universal E2E Stability Certification
    result: PASS
    evidence: exact-head run 30427617625
  - command: Platform cross-repository MariaDB lifecycle
    result: PASS
    evidence: Platform Game Catalog Contract run 30428491404 using Canary run 30427617799 artifact 8714331268
blockers: []
next_action: Merge Canary PR #991 before Platform PR #272.
```

## Notes

Do not modify binary maps, `items.otb`, production configuration, credentials or external repositories.
