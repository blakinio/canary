---
task_id: CAN-20260730-game-catalog-schema-1-3-producer
program_id: GAME-CATALOG-PRODUCTION-COMPLETION
coordination_id: GAME-CATALOG-SCHEMA-1.3-NPC-SHOPS
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/CAN-20260730-game-catalog-schema-1-3-producer
base_branch: main
created: 2026-07-31T00:59:00+02:00
updated: 2026-07-31T00:59:00+02:00
last_verified_commit: "da84057b43f9a3451c70fe06eb52c6e589715959"
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
    - src/game/catalog/catalog_runtime.cpp
    - src/game/catalog/game_catalog_exporter.hpp
    - src/game/catalog/game_catalog_exporter.cpp
    - src/game/catalog/game_catalog_manifest.hpp
    - src/game/catalog/game_catalog_manifest.cpp
    - tools/game-catalog/validate_snapshot.py
    - tests/unit/game/catalog/game_catalog_test.cpp
    - tests/game_catalog/runtime-datapack/npc/**
    - .github/workflows/game-catalog.yml
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

- [ ] Copy the exact Platform PR #338 schema and fixture bytes and pin SHA-256 `0282c0ce4b995e4aded440b148dd4eb8a96a441e9924da182a2df2a0f2eef8a8` and `c4fd9b187e001065f68d90f93dc67f71bb2ff745fc43c3e73110d49b23407ce7`.
- [ ] Preserve schema `1.0.0`-`1.2.0` bytes and old-version output behavior.
- [ ] Load only the configured datapack NPC directory through the existing Lua runtime boundary in export mode.
- [ ] Expose a bounded const final NPC registry view and retain normalized source provenance at `NpcType(name)` registration.
- [ ] Reject ambiguous provenance, unsafe paths, canonical collisions, excessive nesting and missing endpoints fail closed.
- [ ] Emit deterministic NPC entities and exact static buy/sell relations from final `NpcType::info.shopItemVector`.
- [ ] Exclude per-player shop windows, instance currency changes and callback-computed offers.
- [ ] Add explicit C++ and Python typed validation and focused unit/runtime-smoke tests.
- [ ] Prove generated artifacts pass the exact Platform PR #338 inactive consumer lifecycle.
- [ ] Do not import, activate, deploy or start a normal world in staging or production.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-31T00:59:00+02:00
head: da84057b43f9a3451c70fe06eb52c6e589715959
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
  - src/game/catalog/catalog_runtime.cpp
  - src/game/catalog/game_catalog_exporter.hpp
  - src/game/catalog/game_catalog_exporter.cpp
  - src/game/catalog/game_catalog_manifest.hpp
  - src/game/catalog/game_catalog_manifest.cpp
  - tools/game-catalog/validate_snapshot.py
  - tests/unit/game/catalog/game_catalog_test.cpp
  - tests/game_catalog/runtime-datapack/npc/**
  - .github/workflows/game-catalog.yml
proven:
  - Producer branch was rebased before code work onto Canary main da84057b43f9a3451c70fe06eb52c6e589715959.
  - Audit PR 1037 merged as acd2825999d56bb90f03ae21022593fc01ed3874 and defines final Npcs/NpcType/shopItemVector authority.
  - Audit lifecycle PR 1039 merged as f71d3b844adfc5cc4fbfa62b8e7f4e223fd3eb4f and released audit ownership.
  - No overlapping open Canary schema 1.3 producer PR or branch was found during bounded preflight.
  - Platform PR 338 pins schema SHA-256 0282c0ce4b995e4aded440b148dd4eb8a96a441e9924da182a2df2a0f2eef8a8 and fixture SHA-256 c4fd9b187e001065f68d90f93dc67f71bb2ff745fc43c3e73110d49b23407ce7.
  - Current export-only startup loads core npclib but not the configured NPC directory.
  - Current Npcs registry is private, NpcType lacks provenance, and exporter/validators support only schemas 1.0.0 through 1.2.0.
derived:
  - Schema 1.3.0 must retain schema 1.2.0 loot semantics while adding typed NPC/shop dispatch.
  - Old schemas must not serialize NPC records or otherwise change produced bytes.
  - Registration provenance can be captured from LuaScriptInterface::getLoadingFile at luaNpcTypeCreate.
unknown:
  - Whether every production NPC script executes under bounded export-only startup without top-level persistent-state access.
  - Whether production datapacks intentionally register one NPC key from multiple source files.
  - The first implementation failure from compilation, unit tests or runtime smoke.
conflicts: []
first_failure:
  marker: none
  evidence: Producer implementation validation has not run.
rejected_hypotheses:
  - Parse NPC scripts independently from Canary runtime registration.
  - Use global ItemType buy/sell maxima as per-NPC authority.
  - Flatten player-specific or callback-computed offers into the static snapshot.
changed_paths:
  - docs/agents/tasks/active/CAN-20260730-game-catalog-schema-1-3-producer.md
validation:
  - command: bounded producer preflight
    result: PASS
    evidence: current main, merged audit lifecycle, Platform hashes and absence of overlapping producer work were verified.
  - command: exact implementation checks
    result: NOT_RUN
    evidence: Producer code has not yet been committed or executed.
blockers: []
next_action: Copy exact schema and fixture bytes, then extend manifest and validator type dispatch before runtime collection changes.
```
