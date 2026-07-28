---
task_id: CAN-20260728-game-catalog-exporter-slice-1
program_id: OTERYN-GAME-CATALOG
coordination_id: OTERYN-GAME-CATALOG-SLICE-1
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/CAN-20260728-game-catalog-exporter-slice-1
base_branch: main
created: 2026-07-28T10:15:12+02:00
updated: 2026-07-28T10:15:12+02:00
last_verified_commit: "4afd98e5b3d9cf0ce50aca73c697bedcd9ecbc9e"
risk: high
related_issue: ""
related_pr: ""
depends_on:
  - oteryn.game-catalog schema version 1.0.0
blocks:
  - OTERYN-20260728-game-catalog-slice-1
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260728-game-catalog-exporter-slice-1.md
    - src/game/catalog/**
    - schemas/game-catalog/v1/**
    - tools/game-catalog/**
    - tests/game_catalog/**
  shared:
    - src/main.cpp
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
updated_at: 2026-07-28T10:15:12+02:00
head: 4afd98e5b3d9cf0ce50aca73c697bedcd9ecbc9e
branch: feat/CAN-20260728-game-catalog-exporter-slice-1
pr: none
status: implementing
context_routes:
  - agent-governance
  - cpp-runtime
  - cross-repo
  - testing
owned_paths:
  - docs/agents/tasks/active/CAN-20260728-game-catalog-exporter-slice-1.md
  - src/game/catalog/**
  - schemas/game-catalog/v1/**
  - tools/game-catalog/**
  - tests/game_catalog/**
  - src/main.cpp
  - src/canary_server.hpp
  - src/canary_server.cpp
  - CMakeLists.txt
  - cmake/**
  - docs/agents/CROSS_REPO_CONTRACTS.md
  - docs/agents/MODULE_CATALOG.md
  - CHANGELOG.md
proven:
  - main head is architecture merge commit 4afd98e5b3d9cf0ce50aca73c697bedcd9ecbc9e
  - merged architecture requires a deterministic offline exporter using final runtime registries
  - no open Canary PR is dedicated to Game Catalog
  - external wikis are not authoritative game-data sources
  - opentibiabr/canary is read-only and forbidden for writes
  - production deployment and production mutation are excluded
derived:
  - shared fixture and contract validation can be delivered before runtime loader splitting
unknown:
  - exact smallest safe loader boundary between static registries and database/world startup
  - proven DATA_DIRECTORY path for reviewed catalog manifests
  - existing reusable SHA-256 and atomic replacement helper suitable for this exporter
  - executable local test results because the sandbox cannot clone GitHub or run the repository checkout
  - complete historical content and availability facts listed by the architecture
conflicts: []
first_failure:
  marker: sandbox-github-dns-unavailable
  evidence: local git clone failed with Could not resolve host github.com
rejected_hypotheses:
  - implement an independent XML or Lua parser approximating runtime state
  - treat creature registration as proof of encounterability
  - assume a universal loot chance denominator
  - infer version or availability metadata from external wikis
changed_paths:
  - docs/agents/tasks/active/CAN-20260728-game-catalog-exporter-slice-1.md
validation:
  - command: GitHub repository and main-head inspection
    result: PASS
    evidence: main head 4afd98e5b3d9cf0ce50aca73c697bedcd9ecbc9e
  - command: open PR ownership inspection
    result: PASS
    evidence: no Game Catalog PR or identified overlapping owned path
  - command: local checkout/build/test
    result: NOT_RUN
    evidence: sandbox DNS cannot resolve github.com
blockers:
  - runtime loader boundary must be proven before editing startup code
next_action: Add the sanitized shared fixture and automated schema/fixture contract validation before changing the runtime startup path.
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
