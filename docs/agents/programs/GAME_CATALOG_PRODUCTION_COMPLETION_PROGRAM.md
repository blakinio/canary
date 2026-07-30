---
program_id: GAME-CATALOG-PRODUCTION-COMPLETION
status: active
coordination_issue: blakinio/Oteryn-Platform#330
producer_repository: blakinio/canary
consumer_repository: blakinio/Oteryn-Platform
producer_subprogram: CAN-PROGRAM-GAME-CATALOG-COMPLETENESS
created: 2026-07-29T22:20:00Z
updated: 2026-07-29T22:20:00Z
---

# Game Catalog Production Completion Program — Canary Registration

## Purpose

Register Canary as the final-runtime producer in the cross-repository `GAME-CATALOG-PRODUCTION-COMPLETION` programme and connect the existing `CAN-PROGRAM-GAME-CATALOG-COMPLETENESS` evidence programme to the Platform-owned import, activation, rollback and public-visibility lifecycle.

The authoritative programme tracker is `blakinio/Oteryn-Platform#330`. The Platform programme and current-state audit own the complete dependency graph, validation matrix and manual production gate. This document records Canary-specific ownership and task boundaries.

## Current producer baseline

At the programme preflight:

- current Canary `main` advanced from `09209bae26b2bb7e14346f08677e2cd8724aa7ae` to `8e21a33325d6bd8ddbb647e7c967f940dfd54516` through an unrelated task-archive commit;
- the latest Game Catalog runtime merge remained PR #1015 at `37942a3222d3c98bff32610e894640d584d4861a`;
- no Game Catalog source, schema, workflow or contract path changed after PR #1015;
- no open Game Catalog PR or matching branch existed before this task;
- schemas `1.0.0`, `1.1.0` and `1.2.0` remained byte-identical to Platform and immutable;
- the repository-default profile remained schema `1.2.0` with null verified and contained-through boundaries.

The current producer exports only final runtime items, creatures and creature loot. It does not export NPCs, shop offers, quests, rewards, spawns or raids.

## Relationship to the existing completeness programme

`docs/agents/programs/GAME_CATALOG_COMPLETENESS_PROGRAM.md` remains the producer evidence subprogramme for:

- complete runtime definition coverage;
- reviewed metadata and historical evidence;
- additional entity families;
- staging and production-readiness evidence.

This parent registration does not replace or fork that programme. Future bounded producer tasks must update the existing subprogramme when they change its queue or proven evidence.

## Producer authority for NPCs and shops

Canary already has a final loaded NPC authority:

- `Npcs` owns a private ordered map of lowercase registry key to `NpcType`;
- Lua `NpcType(name)` creation resolves through `g_npcs().getNpcType(name, true)`;
- `NpcType` retains runtime `name`, lowercase name, `typeName`, `nameDescription`, currency, callbacks/scripts and an ordered shop vector;
- `NpcType::loadShop` writes final deduplicated `ShopBlock` values to `info.shopItemVector`;
- `ShopBlock` preserves item ID/name, subtype, buy/sell prices, storage key/value and nested child offers.

The registry map currently exposes lookup but no proven bounded read-only iteration surface. A dedicated authority task must design and test that surface before the producer collector task.

The producer must not parse selected Lua/XML files as a parallel source of truth.

## Consumer-first schema dependency

Schema `1.3.0` is proposed for NPC entities and `npc_buy_offer` / `npc_sell_offer` relations.

The required order is:

1. Platform architecture task pins exact proposal bytes and fixture.
2. Platform consumer implementation accepts `1.3.0` inactive, validates and persists typed NPC/shop data, preserves rollback and keeps public activation blocked.
3. Canary runtime-authority task proves safe deterministic registry iteration and relation identity.
4. Canary producer task pins byte-identical schema/fixture and emits exact final runtime data.
5. Cross-repository staging proves import, candidate activation and rollback.
6. Platform public projection remains a separate task.

Canary must not merge a `1.3.0` default producer while the current Platform consumer still maps every non-item entity to creature persistence and every relation to loot persistence.

## Canary-owned task queue

| Task | Scope | Required dependency |
|---|---|---|
| `CAN-20260730-game-catalog-program-registration` | this documentation-only registration | Platform issue #330 |
| `CAN-20260730-game-catalog-npc-runtime-authority` | bounded final registry iteration, stable NPC/offer identity and concurrency proof | Platform `1.3.0` architecture |
| `CAN-20260730-game-catalog-schema-1-3-producer` | byte-identical schema/fixture, NPC/shop collector, exact values, determinism and runtime smoke | compatible Platform consumer + authority task |
| `CAN-20260730-game-catalog-quest-authority-audit` | prove canonical quest/mission authority or design reviewed manifest | independent after NPC/shop architecture |
| `CAN-20260730-game-catalog-schema-1-4-producer` | quest/mission/reward producer | compatible Platform consumer |
| `CAN-20260730-game-catalog-creation-source-audit` | map spawns, raids, events, scripts, summons, instances and admin/test source taxonomy | existing World Index/reachability tools |
| `CAN-20260730-game-catalog-schema-1-5-producer` | creation and availability evidence relations | compatible Platform consumer |
| `CAN-20260730-game-catalog-historical-evidence-program` | exact revisions, evidence review and historically compatible runtime bundles | stable entity contracts |
| `CAN-20260730-game-catalog-artifact-manifest` | immutable artifact provenance and optional signature manifest | stable producer |

Planning identifiers do not claim active implementation. Each task requires its own record, branch, PR, owned paths, validation and one next action.

## Required reuse

- Reuse the existing export-only lifecycle; do not enter normal world startup.
- Keep the complete collection/serialization operation on the dispatcher thread unless a later concurrency proof authorizes a different boundary.
- Reuse final `ItemType`, `MonsterType`, `Npcs`/`NpcType` and confirmed runtime registries.
- Reuse the Unified OTBM World Index and existing reachability/pathfinding tooling for map evidence.
- Reuse the reviewed metadata manifest pattern; unknown facts remain unknown.
- Reuse atomic temporary-file publication and lowercase SHA-256 sidecars.
- Reuse existing endpoint, collision and deterministic-order validation patterns.

## Producer invariants

Every new collector must:

- preserve exact runtime values and explicit null/unknown states;
- fail on canonical-key collisions and dangling entity/currency endpoints;
- preserve nested shop/storage semantics rather than flattening them lossily;
- avoid database and network endpoint syscalls;
- avoid backups, schedulers, raids and normal world services;
- never publish a partial output or destroy the previous valid output after failure;
- remain deterministic with fixed timestamp and identical inputs;
- retain telemetry-off/on loader stability evidence where Lua definitions are involved.

NPC registration alone does not prove map placement or encounterability. A shop offer alone does not prove public item obtainability unless the NPC, location, currency and requirements are also available. Those claims belong to later evidence tasks.

## Schema compatibility

| Version | Producer status |
|---|---|
| `1.0.0` | immutable retained compatibility |
| `1.1.0` | immutable nullable verified boundary |
| `1.2.0` | immutable exact runtime loot threshold model |
| `1.3.0` | proposed NPC/shop contract; not yet a supported producer |
| `1.4.0` | provisional quest/reward scope; blocked by authority audit |
| `1.5.0` | provisional creation/availability scope; blocked by source audit |

Any change to an existing version is forbidden. New versions require exact schema and fixture hash parity with Platform.

## Historical evidence policy

Historical facts require exact revision-pinned evidence. Preferred order:

1. runnable historical Canary/runtime plus matching datapack;
2. exact historical source and asset revisions;
3. repository migrations and changelogs;
4. official data or reproducible maintained-client observation;
5. external wiki only as a research lead.

A modern filtered snapshot must never be labelled a historical runtime snapshot.

## Transport and production boundary

Canary may create immutable `game-catalog.json`, lowercase `.sha256` and a later reviewed deployment manifest. It must not push data through a public unauthenticated endpoint or use production database credentials.

Canary does not own Platform import, profile activation, rollback, public projection or production approval. No Canary task may claim production readiness from green producer CI alone.

## Current evidence state

### PROVEN

- Final runtime NPC and shop objects exist in `Npcs`/`NpcType`/`ShopBlock`.
- The registry map is private and lacks a proven exporter iteration API.
- Existing schemas and collectors cover items, creatures and loot only.
- Unified OTBM World Index and reachability tooling exist and must be reused.
- Platform must implement the new consumer before Canary emits schema `1.3.0`.

### DERIVED

- The first Canary implementation task should be the bounded NPC runtime-authority task, not a Lua parser or complete collector.

### UNKNOWN

- Complete NPC aliases, locations and encounterability.
- Canonical quest runtime authority.
- Complete spawn/raid/scripted-creation taxonomy.
- Historical introduction/removal facts.
- Live staging and production state.

### CONFLICT

- Platform issue #301 contains older producer-first and Canary-read-only assumptions; Platform issue #330 and current explicit authorization supersede those assumptions for this programme.

## Next action

Wait for the independent Platform `OTERYN-20260730-game-catalog-schema-1-3-architecture` proposal, then start `CAN-20260730-game-catalog-npc-runtime-authority` on a separate branch.
