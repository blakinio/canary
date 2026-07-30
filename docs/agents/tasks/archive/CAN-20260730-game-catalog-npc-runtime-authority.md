---
task_id: CAN-20260730-game-catalog-npc-runtime-authority
program_id: GAME-CATALOG-PRODUCTION-COMPLETION
coordination_id: GAME-CATALOG-SCHEMA-1.3-NPC-SHOPS
agent: "GPT-5.6 Thinking"
status: completed
related_pr: 1037
created: 2026-07-30T23:44:00+02:00
completed: 2026-07-31T00:33:50+02:00
risk: high
---

# CAN-20260730-game-catalog-npc-runtime-authority

## Goal

Identify the authoritative final Canary runtime boundary for NPC entities and NPC buy/sell offers before implementing the schema `1.3.0` producer.

## Result

- PR #1037 documented the final static boundary in `docs/systems/GAME_CATALOG_NPC_RUNTIME_AUTHORITY.md`.
- The producer must execute the configured datapack NPC scripts through the existing Lua runtime boundary and enumerate the final `Npcs` registry.
- Static NPC data comes from final `NpcType` values and `NpcType::info.shopItemVector`.
- Offered items and currencies must reuse the existing final item registry and canonical item-key mapping.
- `ShopBlock::itemBuyPrice` maps to `npc_buy_offer`; `ShopBlock::itemSellPrice` maps to `npc_sell_offer`.
- Ordered nested `ShopBlock` indexes form the exact zero-based `runtime_path`.
- Per-player `openShopWindowTable` vectors, instance currency changes and callback-computed offers remain dynamic and excluded.
- The producer requires a bounded const NPC registry view, normalized registration-source provenance, NPC-only export startup and exact schema `1.3.0` validation.
- No exporter behavior, schema bytes, datapack content, world, database, network, staging, production or deployment state changed in this audit.
- PR #1037 squash-merged as `acd2825999d56bb90f03ae21022593fc01ed3874` from exact final head `e3313f0ceb4f94178e5f237a3bc37f11a17fd2cc`.

## Final checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-31T00:33:50+02:00
head: e3313f0ceb4f94178e5f237a3bc37f11a17fd2cc
branch: feat/CAN-20260730-game-catalog-npc-runtime-authority
pr: 1037
merge_sha: acd2825999d56bb90f03ae21022593fc01ed3874
status: completed
context_routes:
  - agent-governance
  - cpp-runtime
  - lua-data
  - cross-repo
proven:
  - The current export-only loader executes only the core NPC library and does not yet execute the configured datapack NPC directory.
  - Npcs stores one final shared NpcType per lowercase registry key.
  - NpcType retains static currency and ordered shopItemVector data after script registration.
  - ShopBlock retains exact item ID, name, subtype, buy price, sell price, storage key/value and nested child offers.
  - Per-player shop vectors and instance currency mutations are not final static catalog authority.
  - Platform PR 338 pins schema 1.3.0 SHA-256 0282c0ce4b995e4aded440b148dd4eb8a96a441e9924da182a2df2a0f2eef8a8 and fixture SHA-256 c4fd9b187e001065f68d90f93dc67f71bb2ff745fc43c3e73110d49b23407ce7.
  - Exact-head Agent Task Ownership run 30586093333 and full CI run 30586227159 passed on e3313f0ceb4f94178e5f237a3bc37f11a17fd2cc.
  - PR 1037 merged without unresolved review threads or repository rule bypass.
derived:
  - The separate producer can safely extend the existing export-only collector when NPC script loading remains bounded and database/network syscall checks remain fail closed.
  - Static output can remain deterministic by canonical-key sorting and final per-NPC vector order when ambiguous duplicate provenance is rejected.
unknown:
  - Whether every production NPC script executes in export-only mode without top-level persistent-state access; the producer runtime smoke must prove or block this.
  - Whether production datapacks contain intentional duplicate NPC registry provenance.
  - Dialogue-only and per-player offers remain outside schema 1.3.0 static completeness.
conflicts: []
first_failure:
  marker: none
  evidence: The audit and exact-head merge gate completed successfully.
rejected_hypotheses:
  - Parse NPC XML or Lua independently of runtime registration.
  - Treat per-player shop windows as a global static offer list.
  - Infer quest, availability, currency or subtype semantics from external documentation.
  - Start a normal world and scrape live NPC conversations.
validation:
  - command: Canary exact-head final gate
    result: PASS
    evidence: Agent Task Ownership run 30586093333 and CI run 30586227159 at e3313f0ceb4f94178e5f237a3bc37f11a17fd2cc.
  - command: Canary squash merge
    result: PASS
    evidence: PR 1037 merged as acd2825999d56bb90f03ae21022593fc01ed3874.
blockers: []
next_action: Implement the separate CAN-20260730-game-catalog-schema-1-3-producer task from current main and prove exact compatibility with Platform PR 338 before either producer or consumer merge gate is released.
```
