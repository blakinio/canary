---
task_id: CAN-20260728-game-catalog-exporter-slice-1
program_id: OTERYN-GAME-CATALOG
coordination_id: OTERYN-GAME-CATALOG-SLICE-1
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/CAN-20260728-game-catalog-exporter-slice-1
base_branch: main
created: 2026-07-28T10:15:12+02:00
updated: 2026-07-28T11:05:00+02:00
last_verified_commit: "a0f27e4cbc5e1489f5912bca5b589f3c713c9472"
risk: high
related_issue: ""
related_pr: "990"
depends_on:
  - oteryn.game-catalog schema version 1.0.0
blocks:
  - OTERYN-20260728-game-catalog-slice-1
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260728-game-catalog-exporter-slice-1.md
    - .github/workflows/game-catalog-contract.yml
    - src/game/catalog/**
    - schemas/game-catalog/v1/**
    - tools/game-catalog/**
    - tests/game_catalog/**
  shared:
    - src/main.cpp
    - src/game/CMakeLists.txt
    - tests/unit/game/CMakeLists.txt
    - src/canary_server.hpp
    - src/canary_server.cpp
    - CMakeLists.txt
    - cmake/**
    - docs/agents/CROSS_REPO_CONTRACTS.md
    - docs/agents/MODULE_CATALOG.md
    - CHANGELOG.md
  read_only:
    - authoritative item registry and loader code
    - Monsters and MonsterType registry code
    - loot structures and registration code
modules_touched:
  - deterministic offline Game Catalog exporter
  - authoritative runtime registry collection
  - atomic snapshot publication
reuses:
  - authoritative item loaders and final item registry
  - authoritative Monsters and MonsterType registry
  - existing CLI, CMake, hashing, JSON and atomic-file conventions where proven
public_interfaces:
  - canary --export-game-catalog-only --game-catalog-output=<path>
  - canary --export-game-catalog-only --game-catalog-output=<path> --game-catalog-generated-at=<UTC-RFC3339>
cross_repo_tasks:
  - OTERYN-20260728-game-catalog-slice-1
---

# Goal

Deliver the Canary half of the first production-quality version-aware Oteryn Game Catalog slice: a deterministic offline exporter that reuses final runtime registries, validates reviewed manifests, emits the shared schema with a SHA-256 sidecar, fails closed and starts no world/network/database side effects.

# Acceptance criteria

- [ ] The shared fixture and schema are byte-identical with `blakinio/Oteryn-Platform`.
- [ ] Export-only CLI loads authoritative item, MonsterType and loot registries without starting services or mutating the database.
- [ ] Identical inputs plus fixed `generated_at` produce byte-identical validated output and sidecar.
- [ ] Invalid manifests, ranges, identities or relation endpoints fail closed and preserve the previous valid output.
- [ ] Focused and repository-required tests and exact-final-head CI pass.
- [ ] No production deployment or production mutation occurs.

## Cross-repository contract and rollout

```yaml
contract_id: oteryn.game-catalog
schema_version: 1.0.0
expected_schema_sha256: 099a8373ff2b0017cc2b321991662dc4e4783b626391aa7a110a6db0559d146b
canary_schema: schemas/game-catalog/v1/game-catalog-snapshot.schema.json
platform_schema: resources/schemas/game-catalog/v1/game-catalog-snapshot.schema.json
compatibility: atomic-required
rollout_order:
  - validate byte-identical schema and shared fixture in both repositories
  - deliver Canary deterministic offline exporter
  - deliver Platform inactive transactional importer
  - deliver Platform profile activation and rollback
  - deliver public and administrative surfaces
  - run cross-repository E2E and generate a staging-only snapshot
production_activation: forbidden
```

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-28T11:05:00+02:00
head: a0f27e4cbc5e1489f5912bca5b589f3c713c9472
branch: feat/CAN-20260728-game-catalog-exporter-slice-1
pr: 990
status: implementing
context_routes:
  - agent-governance
  - cpp-runtime
  - cross-repo
  - testing
owned_paths:
  - docs/agents/tasks/active/CAN-20260728-game-catalog-exporter-slice-1.md
  - .github/workflows/game-catalog-contract.yml
  - src/game/catalog/**
  - schemas/game-catalog/v1/**
  - tools/game-catalog/**
  - tests/game_catalog/**
  - src/main.cpp
  - src/game/CMakeLists.txt
  - tests/unit/game/CMakeLists.txt
  - src/canary_server.hpp
  - src/canary_server.cpp
  - CMakeLists.txt
  - cmake/**
  - docs/agents/CROSS_REPO_CONTRACTS.md
  - docs/agents/MODULE_CATALOG.md
  - CHANGELOG.md
proven:
  - main head contains architecture merge commit 4afd98e5b3d9cf0ce50aca73c697bedcd9ecbc9e
  - merged architecture requires a deterministic offline exporter using final runtime registries
  - normal Canary startup calls loadConfigLua, validateDatapack, initializeDatabase, loadModules, map loading, house and market processing, world start and service registration
  - loadModules registers final appearances, items and monsters before database-dependent boosted-creature, Bosstiary, prey and Cyclopedia calls
  - export-only CLI selection now occurs before CanaryServer injection and cluster identity resolution
  - the catalogue loader reuses authoritative definitions while excluding database initialization, map loading, house/market/raid/scheduler/webhook/backup and service registration
  - exporter consumes final Item and MonsterType registries and exact LootBlock fields with MAX_LOOTCHANCE 100000
  - exporter validates strict reviewed manifests, release_order ranges, exclusive removed_in, canonical identities and relation endpoints
  - exporter serializes deterministically and publishes output plus lowercase SHA-256 sidecar with previous-file restoration on failure
  - Platform and Canary schema files have the same Git blob SHA a3c239a6d61385edde0b06f72cdf781f4ce58df3
  - draft PR #990 tracks this task
  - sanitized fixture contains two releases, visible/future items, complete/partial creatures and visible/future loot relations
  - shared validator performs pinned hash checks, Draft 2020-12 validation, semantic integrity checks and two-release visibility assertions
  - Game Catalog Contract run 30345033491 passed on exporter head 86a2325ee0cf89935103d1cc60b8914d6c8942f9
  - external wikis are not authoritative game-data sources
  - opentibiabr/canary is read-only and forbidden for writes
  - production deployment and production mutation are excluded
derived:
  - matching Git blob SHAs prove the two schema files are byte-identical
  - identical fixture and validator bytes plus pinned SHA-256 values create a cross-repository contract gate
  - the smallest safe loader candidate is the definition-registration prefix of loadModules before runtime persistence calls
unknown:
  - C++ compile and unit-test result for current head
  - whether all Lua dependencies needed for MonsterType registration are available in export-only mode without unrelated regular NPC/event startup
  - exact reviewed Oteryn catalog manifest content for a staging snapshot
  - complete historical content and availability facts listed by the architecture
conflicts: []
first_failure:
  marker: sandbox-github-dns-unavailable
  evidence: local git clone failed with Could not resolve host github.com
rejected_hypotheses:
  - implement an independent XML or Lua parser approximating runtime state
  - treat creature registration as proof of encounterability
  - assume a floating release number or an inferred universal probability denominator
  - infer version or availability metadata from external wikis
changed_paths:
  - .github/workflows/game-catalog-contract.yml
  - docs/agents/tasks/active/CAN-20260728-game-catalog-exporter-slice-1.md
  - src/game/CMakeLists.txt
  - src/game/catalog/CMakeLists.txt
  - src/game/catalog/catalog_definition_loader.cpp
  - src/game/catalog/catalog_definition_loader.hpp
  - src/game/catalog/game_catalog_exporter.cpp
  - src/game/catalog/game_catalog_exporter.hpp
  - src/main.cpp
  - tests/game_catalog/fixtures/v1/minimal-snapshot.json
  - tests/game_catalog/game_catalog_exporter_test.cpp
  - tests/unit/game/CMakeLists.txt
  - tools/game-catalog/validate_contract_fixture.py
validation:
  - command: GitHub repository and main-head inspection
    result: PASS
    evidence: main contains 4afd98e5b3d9cf0ce50aca73c697bedcd9ecbc9e
  - command: GitHub schema blob comparison
    result: PASS
    evidence: both schema paths resolve to blob a3c239a6d61385edde0b06f72cdf781f4ce58df3
  - command: local synthetic fixture semantic validation
    result: PASS
    evidence: counts, ranges, endpoints, probability/count bounds and 15.20/15.21 visibility assertions passed; fixture SHA-256 c947e461c1ee8f6fbf511c9890b61135d2585d6c16e2e99a0f72dd5a946c2181
  - command: local validator syntax and semantic smoke
    result: PASS
    evidence: Python validator executed against a Draft 2020-12 smoke schema and the exact fixture
  - command: Game Catalog Contract
    result: PASS
    evidence: workflow run 30345033491
  - command: Canary CI
    result: IN_PROGRESS
    evidence: workflow run 30345034243 began on exporter integration head 86a2325ee0cf89935103d1cc60b8914d6c8942f9; current head requires a renewed run
  - command: local checkout/build/test
    result: NOT_RUN
    evidence: sandbox DNS cannot resolve github.com
blockers:
  - full C++ compile and runtime-loader validation depend on CI because no local checkout is available
next_action: Inspect final-head Canary ownership and CI, fix the first compile or test failure, then add deterministic exporter integration fixtures.
```

## Deferred child tasks

- NPC catalogue.
- Quests.
- Spawn and raid availability.
- Map reachability.
- Public sprite sourcing.
- Historical release metadata.
- Backport administration.
- 7.60 compatibility.
