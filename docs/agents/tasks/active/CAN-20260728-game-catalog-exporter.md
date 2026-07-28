---
task_id: CAN-20260728-game-catalog-exporter
program_id: none
agent: chatgpt
branch: feat/CAN-20260728-game-catalog-exporter
status: implementing
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

- [ ] `canary --export-game-catalog-only --game-catalog-output=<path>` loads only the bounded catalogue prerequisites and exits without normal world startup.
- [ ] Items, creatures and loot are collected from final authoritative runtime registries rather than a duplicate partial parser.
- [ ] Version, completeness and availability manifests fail closed and preserve UNKNOWN facts.
- [ ] Output is deterministic with fixed `generated_at`, validated before atomic publication and accompanied by a lowercase SHA-256 sidecar.
- [x] The shared sanitized fixture validates and remains byte-compatible with Platform expectations.
- [ ] Tests prove version semantics, collisions, dangling references, exact runtime values, loot numerators/denominators/counts, deterministic bytes, failure preservation and absence of startup side effects.
- [x] Schema bytes remain unchanged and match Platform SHA-256 `099a8373ff2b0017cc2b321991662dc4e4783b626391aa7a110a6db0559d146b`.
- [ ] Required exact-head CI passes before readiness; no production server, datapack activation or deployment occurs.

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
blockers:
  - local clone/build/test unavailable because sandbox DNS cannot resolve github.com; implementation validation must use repository CI until a runnable checkout is available
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
updated_at: 2026-07-28T17:52:11Z
head: c581909e8458af78c9575cc6c4a435dfed9d3fc6
branch: feat/CAN-20260728-game-catalog-exporter
pr: 991
status: validating
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
  - PR 991 is an open mergeable draft on feat/CAN-20260728-game-catalog-exporter at implementation head c581909e8458af78c9575cc6c4a435dfed9d3fc6.
  - Export-only CLI parsing, fail-closed manifest loading, runtime registry collection, semantic validation and atomic snapshot publication are implemented under src/game/catalog.
  - src/main.cpp selects export-only mode before channel resolution and CanaryServer::run; the export path excludes database initialization, maps, services, schedulers and database backup.
  - Items and creatures are collected from final Item::items and Monsters::monsters registries; loot values are collected from MonsterType::info.lootItems.
  - Missing reviewed entity metadata remains unverified and unknown; historical or availability facts are not inferred from external wikis.
  - Unit tests cover CLI options, manifest requirements, final runtime fields, loot values, deterministic bytes, dangling references and preservation of an existing output after validation failure.
  - Exact implementation head CI, Game Catalog and Agent Task Ownership workflows all passed.
  - Contract schema remains version 1.0.0 with SHA-256 099a8373ff2b0017cc2b321991662dc4e4783b626391aa7a110a6db0559d146b.
derived:
  - The implementation is ready for an executable export-only smoke test against a representative datapack and reviewed manifest set.
  - Production startup, deployment and datapack activation remain outside this task.
unknown:
  - Whether the built canary binary completes a representative export-only invocation and produces a schema-valid snapshot and SHA-256 sidecar.
  - Exact reviewed Oteryn versioning and availability manifests for staging content.
  - Complete historical introduced_in, removed_in and availability metadata.
conflicts: []
first_failure:
  marker: none
  evidence: Exact-head workflows are green; executable export-only smoke validation has not run.
rejected_hypotheses:
  - Build a second XML or Lua parser that approximates runtime state.
  - Infer availability or historical release metadata from external wikis.
  - Start normal world services and stop them after export.
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
  - command: CI workflow
    result: PASS
    evidence: exact-head run 30363460607 at c581909e8458af78c9575cc6c4a435dfed9d3fc6
  - command: Game Catalog workflow
    result: PASS
    evidence: exact-head run 30363459905 at c581909e8458af78c9575cc6c4a435dfed9d3fc6
  - command: Agent Task Ownership workflow
    result: PASS
    evidence: exact-head run 30363459906 at c581909e8458af78c9575cc6c4a435dfed9d3fc6
  - command: local executable export-only smoke test
    result: NOT_RUN
    evidence: sandbox DNS cannot resolve github.com and no runnable checkout is available
blockers:
  - A runnable checkout or CI smoke job is required to execute the export-only binary against representative manifests and datapack content.
next_action: Add a bounded CI smoke job that invokes canary --export-game-catalog-only with representative reviewed manifests, validates the snapshot and sidecar, and proves no database or network startup side effects.
```

## Notes

Do not modify binary maps, `items.otb`, production configuration, credentials or external repositories.
