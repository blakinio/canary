---
task_id: CAN-20260730-game-catalog-npc-runtime-authority
program_id: GAME-CATALOG-PRODUCTION-COMPLETION
coordination_id: GAME-CATALOG-SCHEMA-1.3-NPC-SHOPS
status: investigating
agent: "GPT-5.6 Thinking"
branch: feat/CAN-20260730-game-catalog-npc-runtime-authority
base_branch: main
created: 2026-07-30T23:44:00+02:00
updated: 2026-07-30T23:44:00+02:00
last_verified_commit: "3cc30856257fa7e6b3470801807413bb5dad20cc"
risk: high
related_issue: ""
related_pr: ""
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
    - src/**/npc*/**
    - src/**/shop*/**
    - data/**/npc/**
    - data-otservbr-global/**/npc/**
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

- [ ] Identify the final authoritative NPC registry after supported XML/Lua loading, registration and overrides.
- [ ] Trace where deterministic NPC names, runtime paths and stable identities are available.
- [ ] Determine whether buy/sell offers exist as normalized final runtime data or only inside callback/script execution state.
- [ ] Trace item and currency endpoint authority, exact price and subtype semantics, duplicate handling and canonical relation identity requirements.
- [ ] Separate deterministic static offers from dynamic, player-specific, conditional, reputation, quest, vocation, time or stock-dependent behavior.
- [ ] Define the smallest export-only collector boundary that preserves existing no-world, no-database and no-network guarantees.
- [ ] Specify focused unit/runtime-smoke evidence required before implementing schema `1.3.0` production.
- [ ] Record every unavailable or ambiguous fact as unknown rather than inferring it.
- [ ] Do not change exporter behavior, schema bytes, datapack content, production configuration or deployment state in this audit task.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-30T23:44:00+02:00
head: 3cc30856257fa7e6b3470801807413bb5dad20cc
branch: feat/CAN-20260730-game-catalog-npc-runtime-authority
pr: none
status: investigating
context_routes:
  - agent-governance
  - cpp-runtime
  - lua-data
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260730-game-catalog-npc-runtime-authority.md
  - docs/systems/GAME_CATALOG_NPC_RUNTIME_AUTHORITY.md
proven:
  - Canary main at task creation was 3cc30856257fa7e6b3470801807413bb5dad20cc.
  - PR 991 merged the deterministic export-only Game Catalog boundary for final item, creature and loot registries without normal world, database or network startup.
  - Platform PR 338 implements the inactive schema 1.3.0 NPC/shop consumer and remains draft pending Canary producer compatibility.
  - No open Canary Game Catalog NPC/shop producer PR or task branch was found during bounded preflight.
derived:
  - The final-runtime authority audit must precede producer implementation because the consumer contract forbids an approximate independent XML/Lua parser.
  - Runtime-static and player-dynamic shop behavior must be separated before defining export semantics.
unknown:
  - The exact final NPC registry and lifecycle point available to export-only startup.
  - Whether NPC buy/sell offers are retained in normalized C++ runtime structures after script registration.
  - Which conditional offer dimensions can be represented deterministically without player or world state.
conflicts: []
first_failure:
  marker: none
  evidence: Source authority inspection has not yet produced a failure or blocker.
rejected_hypotheses:
  - Parse NPC XML or Lua independently of Canary runtime registration.
  - Infer shop availability, currency, subtype or conditions from names or external documentation.
  - Start a normal world and scrape live NPC responses after startup.
changed_paths:
  - docs/agents/tasks/active/CAN-20260730-game-catalog-npc-runtime-authority.md
validation:
  - command: bounded repository and PR preflight
    result: PASS
    evidence: current main, prior exporter PR 991, Platform program issue 330 and Platform PR 338 dependency were verified through GitHub.
blockers: []
next_action: Trace NPC type loading, Lua registration and shop callback storage from final runtime entry points, then write the authoritative boundary document.
```
