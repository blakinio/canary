---
task_id: CAN-20260730-game-catalog-schema-1-3-producer
program_id: GAME-CATALOG-PRODUCTION-COMPLETION
coordination_id: GAME-CATALOG-SCHEMA-1.3-NPC-SHOPS
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/CAN-20260730-game-catalog-schema-1-3-producer
base_branch: main
created: 2026-07-31T00:59:00+02:00
updated: 2026-07-31T09:12:00+02:00
last_verified_commit: "37b35a7a9a2c7dc0eeaec52a0748cb9a4d507671"
risk: high
related_issue: ""
related_pr: "1040"
depends_on:
  - Canary PR 991 deterministic offline Game Catalog exporter
  - Canary PR 1037 NPC/shop runtime authority audit
  - Platform PR 338 inactive schema 1.3.0 consumer contract
blocks:
  - Platform PR 338 compatibility and merge gate
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260730-game-catalog-schema-1-3-producer.md
    - schemas/game-catalog/v1.3/game-catalog-snapshot.schema.json
    - tests/game_catalog/fixtures/v1.3/minimal-snapshot.json
    - src/creatures/npcs/npcs.hpp
    - src/creatures/npcs/npcs.cpp
    - src/lua/functions/creatures/npc/npc_type_functions.cpp
    - src/game/catalog/CMakeLists.txt
    - src/game/catalog/catalog_runtime.cpp
    - src/game/catalog/game_catalog_exporter.hpp
    - src/game/catalog/game_catalog_exporter.cpp
    - src/game/catalog/game_catalog_v13.hpp
    - src/game/catalog/game_catalog_v13.cpp
    - src/game/catalog/game_catalog_manifest.hpp
    - src/game/catalog/game_catalog_manifest.cpp
    - tools/game-catalog/validate_snapshot.py
    - tests/unit/game/catalog/game_catalog_test.cpp
    - tests/game_catalog/runtime-datapack/npc/**
    - .github/workflows/game-catalog.yml
    - .github/workflows/game-catalog-v13.yml
  shared: []
  read_only:
    - docs/systems/GAME_CATALOG_NPC_RUNTIME_AUTHORITY.md
    - schemas/game-catalog/v1/**
    - schemas/game-catalog/v1.1/**
    - schemas/game-catalog/v1.2/**
    - tests/game_catalog/fixtures/v1/**
    - tests/game_catalog/fixtures/v1.1/**
    - tests/game_catalog/fixtures/v1.2/**
    - src/creatures/creatures_definitions.hpp
    - src/lua/scripts/**
modules_touched:
  - Oteryn Game Catalog exporter
  - Canary NPC runtime registry
  - export-only Lua startup
reuses:
  - Game Catalog exporter from PR 991
  - NPC/shop runtime authority from PR 1037
public_interfaces:
  - bounded const enumeration of final NPC registry
  - exact schema 1.3.0 offline snapshot contract
cross_repo_tasks:
  - OTERYN-20260730-game-catalog-schema-1-3-consumer
  - OTERYN-20260730-game-catalog-schema-1-3-producer-compatibility
---

# Goal

Implement the deterministic Canary producer for the exact pinned `oteryn.game-catalog` schema `1.3.0`, adding final runtime NPC entities and static NPC buy/sell offers to the existing export-only collector while preserving schemas `1.0.0` through `1.2.0`, avoiding a second XML/Lua parser and retaining the no-world, no-database and no-network boundary.

# Acceptance criteria

- [x] Copy the exact Platform PR #338 schema and fixture bytes and pin SHA-256 `0282c0ce4b995e4aded440b148dd4eb8a96a441e9924da182a2df2a0f2eef8a8` and `c4fd9b187e001065f68d90f93dc67f71bb2ff745fc43c3e73110d49b23407ce7`.
- [ ] Preserve schema `1.0.0`-`1.2.0` bytes and old-version output behavior.
- [x] Load only the configured datapack NPC directory through the existing Lua runtime boundary in export mode.
- [x] Expose a bounded const final NPC registry view and retain normalized source provenance at `NpcType(name)` registration.
- [ ] Reject ambiguous provenance, unsafe paths, canonical collisions, excessive nesting and missing endpoints fail closed.
- [x] Emit deterministic NPC entities and exact static buy/sell relations from final `NpcType::info.shopItemVector`.
- [x] Exclude per-player shop windows, instance currency changes and callback-computed offers.
- [ ] Add explicit C++ and Python typed validation and focused unit/runtime-smoke tests.
- [ ] Prove generated artifacts pass the exact Platform PR #338 inactive consumer lifecycle.
- [x] Do not import, activate, deploy or start a normal world in staging or production.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-31T09:12:00+02:00
head: 14143f77e83ed4bb1c3132090a07ac5123ce0b3d
branch: feat/CAN-20260730-game-catalog-schema-1-3-producer
pr: 1040
status: implementing
context_routes:
  - agent-governance
  - cpp-runtime
  - lua-data
  - cross-repo
  - testing
owned_paths:
  - docs/agents/tasks/active/CAN-20260730-game-catalog-schema-1-3-producer.md
  - schemas/game-catalog/v1.3/game-catalog-snapshot.schema.json
  - tests/game_catalog/fixtures/v1.3/minimal-snapshot.json
  - src/creatures/npcs/npcs.hpp
  - src/creatures/npcs/npcs.cpp
  - src/lua/functions/creatures/npc/npc_type_functions.cpp
  - src/game/catalog/CMakeLists.txt
  - src/game/catalog/catalog_runtime.cpp
  - src/game/catalog/game_catalog_exporter.hpp
  - src/game/catalog/game_catalog_exporter.cpp
  - src/game/catalog/game_catalog_v13.hpp
  - src/game/catalog/game_catalog_v13.cpp
  - src/game/catalog/game_catalog_manifest.hpp
  - src/game/catalog/game_catalog_manifest.cpp
  - tools/game-catalog/validate_snapshot.py
  - tests/unit/game/catalog/game_catalog_test.cpp
  - tests/game_catalog/runtime-datapack/npc/**
  - .github/workflows/game-catalog.yml
  - .github/workflows/game-catalog-v13.yml
proven:
  - Audit PR 1037 and lifecycle PRs 1039 and 1042 are merged and ownership is released.
  - Exact Platform schema and fixture bytes are pinned and pass the dedicated contract workflow.
  - Manifest dispatch and Python validation accept schema 1.3.0 while retaining earlier registered schemas.
  - NPC registry enumeration and runtime registration provenance are implemented.
  - Provenance is read from the active Lua ScriptEnvironment, removing the npclib startup segfault; exact-head CI and ownership passed at 37b35a7a9a2c7dc0eeaec52a0748cb9a4d507671.
  - Schema 1.3 uses an isolated adapter over the existing schema 1.2 document builder; earlier schemas keep the original build and publish path.
derived:
  - Old schemas must not load datapack NPC definitions or serialize NPC records.
  - Only final NpcType shopItemVector state is exportable; dynamic player shop windows remain excluded.
unknown:
  - First compilation result for the isolated C++ schema 1.3 adapter.
  - Runtime behavior of the bounded synthetic NPC datapack smoke.
  - Exact inactive Platform consumer compatibility result.
conflicts: []
first_failure:
  marker: none
  evidence: Exact-head workflows are queued for the initial schema 1.3 adapter implementation.
rejected_hypotheses:
  - Parse NPC scripts independently from Canary runtime registration.
  - Use global ItemType buy/sell maxima as per-NPC authority.
  - Flatten player-specific or callback-computed offers into the static snapshot.
changed_paths:
  - .github/workflows/game-catalog-v13.yml
  - docs/agents/tasks/active/CAN-20260730-game-catalog-schema-1-3-producer.md
  - schemas/game-catalog/v1.3/game-catalog-snapshot.schema.json
  - src/creatures/npcs/npcs.cpp
  - src/creatures/npcs/npcs.hpp
  - src/game/catalog/CMakeLists.txt
  - src/game/catalog/catalog_runtime.cpp
  - src/game/catalog/game_catalog_manifest.cpp
  - src/game/catalog/game_catalog_v13.cpp
  - src/game/catalog/game_catalog_v13.hpp
  - tests/game_catalog/fixtures/v1.3/minimal-snapshot.json
  - tools/game-catalog/validate_snapshot.py
validation:
  - command: Game Catalog 1.3 Producer exact contract workflow
    result: PASS
    evidence: Exact schema and fixture SHA-256 checks and all registered fixture validations passed at 37b35a7a9a2c7dc0eeaec52a0748cb9a4d507671.
  - command: CI and Agent Task Ownership
    result: PASS
    evidence: Compilation and ownership passed at 37b35a7a9a2c7dc0eeaec52a0748cb9a4d507671 after the provenance fix.
  - command: schema 1.3 C++ adapter build and runtime smoke
    result: RUNNING
    evidence: Exact-head workflows are running after activation of game_catalog_v13.
blockers: []
next_action: Fix the first exact-head C++ or runtime failure, then add bounded synthetic NPC runtime smoke and Platform inactive-consumer proof.
```
