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
    - data-otservbr-global/catalog/**
  shared:
    - src/main.cpp
    - src/canary_server.hpp
    - src/canary_server.cpp
    - CMakeLists.txt
    - src/CMakeLists.txt
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
  - data-otservbr-global/catalog/**
  - docs/agents/tasks/active/CAN-20260728-game-catalog-exporter.md
  - docs/agents/tasks/deferred/CAN-20260728-game-catalog-*.md
  - src/main.cpp
  - src/canary_server.hpp
  - src/canary_server.cpp
  - CMakeLists.txt
  - src/CMakeLists.txt
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
updated_at: 2026-07-28T09:40:00Z
head: 62ed3824a0e0237653b234374c87a8118ef611cf
branch: feat/CAN-20260728-game-catalog-exporter
pr: 991
status: implementing
context_routes:
  - agent-governance
  - cpp-runtime
  - lua-data
  - real-tibia-parity
  - cross-repo
owned_paths:
  - src/game/catalog/**
  - tools/game-catalog/**
  - tests/game_catalog/**
  - tests/fixtures/game-catalog/**
  - data-otservbr-global/catalog/**
  - docs/agents/tasks/active/CAN-20260728-game-catalog-exporter.md
proven:
  - Canary main is 4afd98e5b3d9cf0ce50aca73c697bedcd9ecbc9e and contains merged architecture PR 989.
  - Shared contract ID is oteryn.game-catalog, schema version is 1.0.0 and expected schema SHA-256 is 099a8373ff2b0017cc2b321991662dc4e4783b626391aa7a110a6db0559d146b.
  - Final runtime registries, not source-text approximations, are authoritative for item, creature and loot values.
  - Registration alone does not prove encounterability; missing reviewed evidence remains registered_only or unknown.
  - Current active-work index has no ownership claim on src/game/catalog, tools/game-catalog, tests/game_catalog or catalogue manifest paths.
  - The shared fixture has identical Git blob SHA e078e87000b3472a26465d4cf0885ee81635a83e in Canary and Platform and content SHA-256 76b61b167e77a0c0379c5c1d179c3fec808ae1cf3d996e30be5784fde699691e.
  - Normal startup initializes the database before loadModules and later starts maps, houses, market, schedulers and network services.
  - The authoritative definition load order inside loadModules is appearances, vocations/outfits/familiars/imbuements/storages, final Item registry, core/datapack Lua and final Monsters registry.
  - Existing generate-lua-api-docs-only parsing proves an early CLI-only path can exit before CanaryServer::run.
derived:
  - Export-only startup must branch before CanaryServer::run database initialization and reuse a smallest safe definition-only loader ending after final Monsters registration.
  - NPCs, maps, houses, market, raids, schedulers, boosted/prey/statistics, webhooks, backups and ports must remain outside that loader boundary.
  - Deterministic publication requires validation and flush/close before atomic rename in the destination directory.
unknown:
  - final DTO field mapping for every bounded runtime item and MonsterType field
  - exact reviewed Oteryn manifests and staging snapshot contents
  - complete historical introduced/removed and availability metadata
conflicts: []
first_failure:
  marker: sandbox-network-unavailable
  evidence: direct git clone failed because github.com DNS could not be resolved
rejected_hypotheses:
  - Build a second XML/Lua parser that approximates runtime state.
  - Infer availability or historical release metadata from external wikis.
  - Start normal world services and stop them after export.
changed_paths:
  - .github/workflows/game-catalog.yml
  - docs/agents/tasks/active/CAN-20260728-game-catalog-exporter.md
  - tests/game_catalog/fixtures/minimal-snapshot.json
  - tests/game_catalog/test_validate_snapshot.py
  - tools/game-catalog/validate_snapshot.py
validation:
  - command: python -m py_compile tools/game-catalog/validate_snapshot.py tests/game_catalog/test_validate_snapshot.py
    result: PASS
    evidence: Game Catalog workflow run 30345793160
  - command: python -m unittest discover -s tests/game_catalog -p 'test_*.py' -v
    result: PASS
    evidence: Game Catalog workflow run 30345793160
  - command: python tools/game-catalog/validate_snapshot.py tests/game_catalog/fixtures/minimal-snapshot.json --schema schemas/game-catalog/v1/game-catalog-snapshot.schema.json --expected-sha256 76b61b167e77a0c0379c5c1d179c3fec808ae1cf3d996e30be5784fde699691e
    result: PASS
    evidence: Game Catalog workflow run 30345793160
  - command: repository CI
    result: PASS
    evidence: CI workflow run 30345793523
  - command: local clone/build/test
    result: NOT_RUN
    evidence: sandbox DNS cannot resolve github.com
blockers:
  - local runtime validation unavailable until CI or another runnable checkout is used
next_action: Inspect exact final Item, Monsters, MonsterType and loot APIs and implement the definition-only exporter boundary without database or world startup.
```

## Notes

Do not modify binary maps, `items.otb`, production configuration, credentials or external repositories.
