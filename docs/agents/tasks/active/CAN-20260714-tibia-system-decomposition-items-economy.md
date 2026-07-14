---
task_id: CAN-20260714-tibia-system-decomposition-items-economy
program_id: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
coordination_id: REAL-TIBIA-SYSTEM-DECOMPOSITION-TSD-007
status: active
agent: "GPT-5.6 Thinking"
branch: docs/tibia-system-decomposition-items-economy
base_branch: main
created: 2026-07-14T23:30:00+02:00
updated: 2026-07-14T23:30:00+02:00
last_verified_commit: "821f213038770d68cd95b1b22afa78937b974210"
risk: low
related_issue: ""
related_pr: ""
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

# Preflight

- Base: `821f213038770d68cd95b1b22afa78937b974210`.
- Open #360 protocol/session, #316 map/content and #245 E2E remain read-only.
- `ACTIVE_WORK.md` remains read-only.

# Boundary decision

- `item-definitions`: Items/ItemType registry and appearance/XML parsing.
- `item-instances`: Item factory, attributes, clone/serialization/transform state.
- `containers`: nested inventory/depot/inbox/reward/mailbox cylinder lifecycle.
- `item-decay`: scheduled start/stop/check/transform lifecycle.

Movement, stacking and transfer remain item/container capabilities because generic orchestration is spread across Game/Cylinder rather than one narrow root. Market, store/coin, Forge, Imbuements, weapons and boss rewards remain existing or deferred boundaries.

# Acceptance

Add only four records, preserve all existing records, regenerate indexes, add focused tests, pass exact-head/ready CI, and change no runtime/gameplay/protocol/client/DB/map/asset/workflow/E2E implementation.

# Handoff

After feature merge, create a lifecycle-only archive. TSD-008 may start only after that merge.