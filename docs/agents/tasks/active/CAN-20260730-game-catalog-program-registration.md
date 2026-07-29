---
task_id: CAN-20260730-game-catalog-program-registration
program_id: GAME-CATALOG-PRODUCTION-COMPLETION
coordination_id: OTERYN-PLATFORM-330
status: ready
agent: chatgpt
branch: docs/CAN-20260730-game-catalog-program-registration
base_branch: main
created: 2026-07-29T22:20:00Z
updated: 2026-07-29T23:03:00Z
last_verified_commit: c678d90483af945b3bbf0a40f6d6b9ce99da4a3f
risk: low
related_issue: blakinio/Oteryn-Platform#330
related_pr: 1023
depends_on:
  - OTERYN-20260730-game-catalog-program-audit
blocks:
  - CAN-20260730-game-catalog-npc-runtime-authority
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260730-game-catalog-program-registration.md
    - docs/agents/programs/GAME_CATALOG_PRODUCTION_COMPLETION_PROGRAM.md
  shared: []
  read_only:
    - docs/agents/programs/GAME_CATALOG_COMPLETENESS_PROGRAM.md
    - docs/agents/CROSS_REPO_CONTRACTS.md
    - docs/contracts/GAME_CATALOG_EXPORT_CONTRACT.md
    - src/creatures/npcs/**
modules_touched:
  - Game Catalog programme governance
public_interfaces: []
cross_repo_tasks:
  - OTERYN-20260730-game-catalog-program-audit
  - OTERYN-20260730-game-catalog-schema-1-3-architecture
---

# Goal

Register Canary in `GAME-CATALOG-PRODUCTION-COMPLETION`, reuse the existing completeness programme and record the consumer-first producer backlog without runtime, schema, datapack, workflow or environment changes.

# Result

- Registered Platform issue #330 as the parent programme.
- Kept `CAN-PROGRAM-GAME-CATALOG-COMPLETENESS` as the producer evidence subprogramme.
- Recorded NPC authority, schema `1.3.0` producer, quest authority, creation-source, history and artifact-manifest tasks.
- Recorded that Platform complete inactive consumer support must precede Canary `1.3.0` producer support.
- Refreshed the branch from current Canary `main` `c678d90483af945b3bbf0a40f6d6b9ce99da4a3f`; intervening commits do not touch Game Catalog paths.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T23:03:00Z
head: 08b536ee84b745c2053920d9056f75d10422a26f
branch: docs/CAN-20260730-game-catalog-program-registration
pr: 1023
status: ready
context_routes:
  - agent-governance
  - cpp-runtime
  - lua-data
  - otbm
  - cross-repo
  - testing
owned_paths:
  - docs/agents/tasks/active/CAN-20260730-game-catalog-program-registration.md
  - docs/agents/programs/GAME_CATALOG_PRODUCTION_COMPLETION_PROGRAM.md
changed_paths:
  - docs/agents/tasks/active/CAN-20260730-game-catalog-program-registration.md
  - docs/agents/programs/GAME_CATALOG_PRODUCTION_COMPLETION_PROGRAM.md
proven:
  - Current Canary main is c678d90483af945b3bbf0a40f6d6b9ce99da4a3f and its post-preflight changes are unrelated Real Tibia evidence/task records.
  - Latest Game Catalog runtime merge remains PR 1015 and no catalog source/schema/workflow path changed afterward.
  - Existing schemas 1.0.0, 1.1.0 and 1.2.0 remain immutable and byte-identical to Platform.
  - Final Npcs/NpcType/ShopBlock state exists and the registry map has no proven exporter iteration API.
  - Existing Unified OTBM World Index and reachability tooling must be reused.
  - PR 1023 contains only this task and the parent programme registration document.
  - Before the current-main refresh, exact head 4aaafd6ea0a0afffee19e04d66fb951e2c024e33 passed Agent Task Ownership and full Canary CI.
derived:
  - The next Canary implementation is a bounded NPC runtime-authority task after Platform architecture, not a producer collector or Lua parser.
unknown:
  - Safe deterministic NPC registry iteration API.
  - Quest canonical authority and complete creation-source taxonomy.
  - Historical introduction/removal evidence.
  - Live staging and production state.
conflicts:
  - Platform issue 301 retains producer-first and Canary-read-only assumptions superseded by issue 330 and current authorization.
first_failure:
  marker: Agent Task Ownership checkpoint validation
  evidence: four record-only convention failures were corrected; no product or contract implementation changed.
rejected_hypotheses:
  - Replace the existing producer completeness programme with a duplicate.
  - Parse selected Lua/XML files as final runtime authority.
  - Claim production readiness from producer CI alone.
validation:
  - command: GitHub main drift and Game Catalog path comparison
    result: PASS
    evidence: branch refreshed from c678d90483af945b3bbf0a40f6d6b9ce99da4a3f; intervening paths are unrelated.
  - command: pre-refresh exact-head 4aaafd6ea0a0afffee19e04d66fb951e2c024e33 ownership and CI
    result: PASS
    evidence: Agent Task Ownership run 30497787273 and CI run 30497787491 succeeded.
  - command: current-main exact-head ownership and CI
    result: NOT_RUN
    evidence: pending on this refreshed two-file head.
blockers:
  - current-main exact-head ownership and CI evidence pending.
next_action: Verify the refreshed exact head, inspect reviews and mergeability, then keep PR 1023 ready for review.
```
