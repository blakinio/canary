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

Produce deterministic schema `1.3.0` NPC entities and static buy/sell offers from final Canary runtime state without changing schema `1.0.0`-`1.2.0` behavior or crossing the no-world, no-database and no-network boundary.

# Acceptance criteria

- [x] Exact Platform schema and fixture bytes are pinned.
- [ ] Schema `1.0.0`-`1.2.0` output behavior remains unchanged.
- [x] Only the configured datapack NPC directory is loaded through Canary Lua runtime.
- [x] Final NPC registry and registration provenance are exposed read-only.
- [ ] Ambiguous provenance, unsafe paths, collisions, excessive nesting and missing endpoints fail closed.
- [x] Final static `shopItemVector` buy/sell offers are serialized deterministically.
- [x] Dynamic per-player and callback-computed offers remain excluded.
- [ ] Focused C++ and runtime-smoke tests pass.
- [ ] Generated output passes the inactive Platform PR #338 consumer lifecycle.
- [x] No normal world, database, network, staging or production activation is performed.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-31T09:12:00+02:00
head: 12c3c0dca82f102849b88f280323f3e075dd2243
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
  - Audit PR 1037 and lifecycle PRs 1039 and 1042 are merged.
  - Exact Platform schema and fixture hashes pass the dedicated contract workflow.
  - Provenance now comes from the active Lua ScriptEnvironment; CI and ownership passed at 37b35a7a9a2c7dc0eeaec52a0748cb9a4d507671.
  - Schema 1.3 uses an isolated adapter over the existing schema 1.2 builder; earlier versions retain the original path.
derived:
  - Old schemas must not load NPC definitions or emit NPC records.
  - Only final static NpcType shopItemVector state is exportable.
unknown:
  - First compilation result for game_catalog_v13.
  - Synthetic NPC runtime-smoke result.
  - Inactive Platform consumer result.
conflicts: []
first_failure:
  marker: none
  evidence: Initial schema 1.3 adapter compilation has not completed on the current head.
rejected_hypotheses:
  - Parse NPC Lua independently.
  - Use global ItemType prices as per-NPC authority.
  - Export dynamic player shop windows.
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
  - command: Game Catalog 1.3 exact contract workflow
    result: PASS
    evidence: Pinned schema and fixture hashes and all registered fixture validations passed at 37b35a7a9a2c7dc0eeaec52a0748cb9a4d507671.
  - command: CI and Agent Task Ownership
    result: PASS
    evidence: Compilation and ownership passed at 37b35a7a9a2c7dc0eeaec52a0748cb9a4d507671 after the provenance fix.
  - command: schema 1.3 C++ adapter build and runtime smoke
    result: NOT_RUN
    evidence: Exact-head workflows have not completed for the adapter implementation.
blockers: []
next_action: Fix the first exact-head C++ or runtime failure, then add bounded NPC smoke and Platform inactive-consumer proof.
```
