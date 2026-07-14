---
task_id: CAN-20260714-tibia-system-decomposition-items-economy
program_id: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
coordination_id: REAL-TIBIA-SYSTEM-DECOMPOSITION-TSD-007
status: active
agent: "GPT-5.6 Thinking"
branch: docs/tibia-system-decomposition-items-economy
base_branch: main
created: 2026-07-14T23:30:00+02:00
updated: 2026-07-14T23:58:00+02:00
last_verified_commit: "ff38dc9ff4092a8a1c631f62cea6df1c41c4f6a6"
risk: low
related_issue: ""
related_pr: "366"
depends_on:
  - completed and archived TSD-006
blocks:
  - TSD-008 world content decomposition
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260714-tibia-system-decomposition-items-economy.md
    - docs/agents/real-tibia/TSD_007_ITEMS_ECONOMY_REPORT.md
    - docs/agents/real-tibia/registry/modules/item-definitions.yaml
    - docs/agents/real-tibia/registry/modules/item-instances.yaml
    - docs/agents/real-tibia/registry/modules/containers.yaml
    - docs/agents/real-tibia/registry/modules/item-decay.yaml
    - tools/agents/test_items_registry.py
    - tools/agents/test_upstream_intelligence_items.py
  shared:
    - docs/agents/programs/TIBIA_SYSTEM_DECOMPOSITION_PROGRAM.md
    - docs/agents/real-tibia/generated/**
    - tools/agents/test_combat_registry.py
    - tools/agents/test_creature_registry.py
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - docs/agents/ACTIVE_WORK.md
    - docs/agents/real-tibia/registry/modules/market.yaml
    - docs/agents/real-tibia/registry/modules/imbuements.yaml
    - docs/agents/real-tibia/registry/modules/exaltation-forge.yaml
    - docs/agents/real-tibia/registry/modules/weapons.yaml
    - docs/agents/real-tibia/registry/modules/boss-encounters.yaml
    - docs/agents/real-tibia/registry/modules/player-persistence.yaml
    - docs/agents/real-tibia/registry/modules/protocol.yaml
    - tools/agents/real_tibia_registry*.py
    - tools/agents/upstream_intelligence*.py
    - .github/workflows/**
    - src/items/**
    - src/game/**
    - src/io/**
    - src/account/**
    - data/items/**
    - tests/**
modules_touched:
  - Real Tibia module registry
  - item definitions and instances
  - containers
  - item decay
reuses:
  - existing registry/generator/mapper
public_interfaces:
  - bounded item lifecycle discovery records
cross_repo_tasks: []
---

# Goal

Complete bounded TSD-007 item and economy inventory. Preserve market, Imbuements, Forge, weapons, boss rewards, persistence and protocol records. Add only stable item-definition, item-instance, container and decay lifecycles with verified current paths.

# Exact base and preflight

- Task-start main: `821f213038770d68cd95b1b22afa78937b974210`.
- Open PRs #360 protocol/session, #316 map/content and #245 physical-client E2E remained read-only and non-overlapping.
- `ACTIVE_WORK.md` remained read-only.

# Delivered result

Registry records: 45 → 49. Added only:

- `containers`;
- `item-decay`;
- `item-definitions`;
- `item-instances`.

Existing records modified: 0. `market`, `imbuements`, `exaltation-forge`, `weapons`, `boss-encounters`, player/world persistence and protocol remain stable.

# Classification

- Items/ItemType registry and XML/appearance parsing → `item-definitions`.
- Runtime item factory, attributes, transforms and serialization → `item-instances`.
- Nested container/cylinder, depot, inbox, mailbox and reward-container lifecycle → `containers`.
- Scheduled duration/start/stop/check/transform lifecycle → `item-decay`.
- Movement, stacking, transfer, stash and managed-container behavior remain capabilities because orchestration spans Game/Cylinder/Container.
- Market, Forge, Imbuements, weapons and boss rewards remain already covered.
- Account coins and NPC trade remain deferred to later bounded economy/social inventories.

Detailed evidence: `docs/agents/real-tibia/TSD_007_ITEMS_ECONOMY_REPORT.md`.

# Validation history

Implementation/focused-test head `ff38dc9ff4092a8a1c631f62cea6df1c41c4f6a6`:

- Real Tibia Module Registry #300: success;
- Upstream Intelligence #331: success;
- Agent Task Ownership #1147: success;
- repository CI #2263: success;
- focused registry/source-role tests: success;
- schema and dependency graph validation: success;
- deterministic `generate --check`: success;
- discovery and exact PR-range `affected`: success.

Older TSD-005/TSD-006 focused tests were changed from exact global totals to their package minimum baselines. TSD-007 owns the exact current total of 49. No mapper, module scope or runtime behavior changed.

Later program and task-record commits are documentation-only. This task record cannot embed its own final SHA; live PR #366 metadata and exact-head workflows are authoritative before merge.

# Acceptance criteria

- [x] Added only four confirmed records.
- [x] Preserved all existing records unchanged.
- [x] Regenerated deterministic indexes through the existing generator.
- [x] Added focused registry and source-role tests.
- [x] Passed registry/UI/ownership/repository CI at the implementation head.
- [ ] Exact final-head and ready-state Linux/Required must pass before merge.
- [x] Made no runtime, gameplay, protocol, client, DB, map, OTBM, datapack, asset, workflow or E2E implementation change.

# Safety limits

Inventory does not prove item metadata/appearance/value parity, movement/transfer atomicity, duplication/loss safety, container correctness, serializer completeness, decay timing/restart behavior, market/Forge/Imbuement/weapon/boss-reward correctness, runtime behavior, protocol compatibility, physical-client E2E or Oteryn readiness.

# Handoff

After PR #366 passes exact final-head review and ready-state CI, squash merge it and archive this task in a lifecycle-only PR. Only after that archive merges may TSD-008 start from then-current `main`:

```text
task: CAN-20260714-tibia-system-decomposition-world-content
package: TSD-008
branch: docs/tibia-system-decomposition-world-content
```
