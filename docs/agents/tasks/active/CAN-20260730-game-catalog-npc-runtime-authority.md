---
task_id: CAN-20260730-game-catalog-npc-runtime-authority
program_id: GAME-CATALOG-PRODUCTION-COMPLETION
coordination_id: GAME-CATALOG-SCHEMA-1.3-NPC-SHOPS
status: active
agent: "GPT-5.6 Thinking"
branch: feat/CAN-20260730-game-catalog-npc-runtime-authority
base_branch: main
created: 2026-07-30T23:44:00+02:00
updated: 2026-07-31T00:10:00+02:00
last_verified_commit: "da14a4c70bdfc6d9eb838fa0e053f57ea9186fcb"
risk: high
related_issue: ""
related_pr: "1037"
depends_on:
  - Canary PR 991 deterministic offline Game Catalog exporter
  - Platform PR 338 inactive schema 1.3.0 consumer contract
blocks:
  - CAN-20260730-game-catalog-schema-1-3-producer
  - Platform PR 338 merge compatibility gate
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260730-game-catalog-npc-runtime-authority.md
    - docs/systems/GAME_CATALOG_NPC_RUNTIME_AUTHORITY.md
  shared: []
  read_only:
    - src/game/catalog/**
    - src/creatures/npcs/**
    - src/lua/functions/creatures/npc/**
    - src/lua/scripts/**
    - data/npclib/**
    - data-otservbr-global/npc/**
    - schemas/game-catalog/**
    - tests/unit/game/catalog/**
modules_touched:
  - Oteryn Game Catalog exporter
  - Canary NPC runtime
reuses:
  - Oteryn Game Catalog exporter from PR 991
public_interfaces: []
cross_repo_tasks:
  - OTERYN-20260730-game-catalog-schema-1-3-consumer
  - OTERYN-20260730-game-catalog-schema-1-3-producer-compatibility
---

# Goal

Identify and document the authoritative final Canary runtime boundary for NPC entities and NPC buy/sell offers so the separate schema `1.3.0` producer can extend the existing offline Game Catalog exporter without introducing a second XML/Lua parser, guessing dynamic shop state or entering normal world/database/network startup.

# Acceptance criteria

- [x] Identify the final authoritative NPC registry after supported Lua loading, registration and overrides.
- [x] Trace where deterministic NPC names, runtime paths and stable identities are available.
- [x] Determine whether buy/sell offers exist as normalized final runtime data or only inside callback/script execution state.
- [x] Trace item and currency endpoint authority, exact price and subtype semantics, duplicate handling and canonical relation identity requirements.
- [x] Separate deterministic static offers from dynamic, player-specific, conditional, reputation, quest, vocation, time or stock-dependent behavior.
- [x] Define the smallest export-only collector boundary that preserves existing no-world, no-database and no-network guarantees.
- [x] Specify focused unit/runtime-smoke evidence required before implementing schema `1.3.0` production.
- [x] Record every unavailable or ambiguous fact as unknown rather than inferring it.
- [x] Do not change exporter behavior, schema bytes, datapack content, production configuration or deployment state in this audit task.
- [ ] Pass exact-head governance and documentation checks, then merge and archive this audit before producer implementation.

# Result

The authoritative boundary is documented in `docs/systems/GAME_CATALOG_NPC_RUNTIME_AUTHORITY.md`.

The static producer may use only the final `Npcs::npcs` registry, final `NpcType` fields, final `NpcType::info.shopItemVector`, and the existing item registry/canonical-key mapping. Per-player `openShopWindowTable` vectors, instance-level currency changes and callback-computed offers are dynamic and explicitly excluded.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-31T00:10:00+02:00
head: da14a4c70bdfc6d9eb838fa0e053f57ea9186fcb
branch: feat/CAN-20260730-game-catalog-npc-runtime-authority
pr: 1037
status: validating
context_routes:
  - agent-governance
  - cpp-runtime
  - lua-data
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260730-game-catalog-npc-runtime-authority.md
  - docs/systems/GAME_CATALOG_NPC_RUNTIME_AUTHORITY.md
proven:
  - Canary main at task creation was 3cc30856257fa7e6b3470801807413bb5dad20cc and no overlapping Game Catalog NPC/shop producer PR or task branch existed.
  - PR 991 merged the deterministic export-only Game Catalog boundary for final item, creature and loot registries without normal world, database or network startup.
  - The current export-only loader executes only the core NPC library with g_npcs().load(true, false); it does not execute the configured datapack npc directory and therefore does not populate final NpcType records.
  - Npcs stores one shared NpcType per lowercase registry key; NpcType retains final runtime names, type name, name description, static currency and an ordered shopItemVector.
  - ShopBlock retains exact item server ID, item name, subtype, player-buy price, player-sell price, storage key/value and ordered nested child shops; NpcType::loadShop suppresses exact duplicate blocks.
  - Per-player Npc::shopPlayers and Lua openShopWindowTable tables override the static vector only for a specific player and are not final static catalog authority.
  - Instance-level Npc::setCurrency can diverge from NpcType currency and is runtime-dynamic rather than static producer authority.
  - Platform PR 338 pins schema 1.3.0 SHA-256 0282c0ce4b995e4aded440b148dd4eb8a96a441e9924da182a2df2a0f2eef8a8 and shared-fixture SHA-256 c4fd9b187e001065f68d90f93dc67f71bb2ff745fc43c3e73110d49b23407ce7.
  - The paired fixture maps itemBuyPrice semantics to npc_buy_offer and itemSellPrice semantics to npc_sell_offer, with exact zero-based nested runtime paths.
  - Current NpcType records do not retain source provenance and Npcs has no const enumeration interface; both are bounded implementation requirements for the producer task.
derived:
  - The producer can safely load the configured npc directory through the existing Lua execution boundary without loading the complete datapack script tree, provided the no-database/no-network runtime smoke remains fail closed.
  - Static output can remain deterministic by canonical-key sorting and final per-NPC vector order when duplicate registry provenance across different files is rejected.
  - A ShopBlock storage pair of zero/zero must map to unknown absence/null because the current runtime has no presence bit and cannot distinguish unset from an intentional exact zero/zero requirement.
unknown:
  - Whether the complete production datapack's NPC scripts all execute successfully in export-only mode without top-level persistent-state access; the producer runtime smoke must prove or block this.
  - Whether any production NPC registry key is intentionally registered by more than one source file; the producer must detect this rather than rely on filesystem traversal order.
  - Dialogue-only and per-player offers remain outside the static schema because no deterministic player-independent runtime authority exists for them.
conflicts: []
first_failure:
  marker: none
  evidence: The source audit found implementation prerequisites but no contradiction in the static NpcType/shop authority model.
rejected_hypotheses:
  - Parse NPC XML or Lua independently of Canary runtime registration.
  - Treat per-player openShopWindowTable data as a global static offer list.
  - Infer shop availability, currency, subtype, quest meaning or conditions from names or external documentation.
  - Start a normal world and scrape live NPC responses after startup.
  - Use global ItemType buyPrice/sellPrice maxima as per-NPC offer authority.
changed_paths:
  - docs/agents/tasks/active/CAN-20260730-game-catalog-npc-runtime-authority.md
  - docs/systems/GAME_CATALOG_NPC_RUNTIME_AUTHORITY.md
validation:
  - command: bounded repository and PR preflight
    result: PASS
    evidence: current main, prior exporter PR 991, Platform issue 330, Platform PR 338 and absence of overlapping Canary work were verified through GitHub.
  - command: source authority audit
    result: PASS
    evidence: catalog_runtime, Npcs/NpcType, ShopBlock, Lua Shop/NpcType registration and per-player shop-window paths were traced to their final C++ storage boundaries.
  - command: paired Platform schema and fixture review
    result: PASS
    evidence: exact schema 1.3 NPC/currency/shop fields, canonical identity patterns and fixture direction semantics were verified on Platform PR 338.
  - command: CI run 30585706115 on head da14a4c70bdfc6d9eb838fa0e053f57ea9186fcb
    result: PASS
    evidence: repository CI completed successfully; ownership failed only because active-task frontmatter used an execution status instead of status active.
  - command: exact-head PR checks
    result: NOT_RUN
    evidence: GitHub Actions has not yet completed on the corrected active-task metadata head.
blockers: []
next_action: Validate PR 1037 on its exact corrected documentation head, mark the audit ready and merge it if all repository gates pass, then create the separate schema 1.3.0 producer task from current main.
```
