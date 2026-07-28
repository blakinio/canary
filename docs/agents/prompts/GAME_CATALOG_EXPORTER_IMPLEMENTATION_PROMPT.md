# Game Catalog Exporter implementation prompt

Use this prompt to start the first implementation slice without relying on chat history.

```text
Continue task CAN-20260728-game-catalog-export-architecture from the current blakinio/canary repository state.

WRITES

Writes are authorized only in blakinio/canary for this task.
Treat opentibiabr/canary, blakinio/Oteryn-Platform and all external repositories as read-only unless a new explicit authorization is provided.
Never push directly to main.

GOAL

Implement the first deterministic offline Canary producer for contract oteryn.game-catalog schema 1.0.0.

The first slice covers:
- releases and snapshot provenance;
- final runtime items;
- final runtime creatures;
- creature loot relations;
- explicit version/completeness/availability manifests;
- deterministic JSON output and SHA-256 sidecar;
- focused tests and CI.

Do not implement NPCs, quests, spawns, raids, map attainability, public sprite extraction or historical profiles in this slice.

MANDATORY STARTUP

Read:
- AGENTS.md
- docs/agents/REPOSITORY_MAP.md
- docs/agents/CONTEXT_ROUTING.md
- docs/agents/tasks/active/CAN-20260728-game-catalog-export-architecture.md
- docs/contracts/GAME_CATALOG_EXPORT_CONTRACT.md
- docs/systems/GAME_CATALOG_EXPORTER.md
- schemas/game-catalog/v1/game-catalog-snapshot.schema.json

Search first:
- docs/agents/MODULE_CATALOG.md
- docs/agents/KNOWN_RISKS.md
- docs/agents/BUILD_TEST_MATRIX.md
- docs/agents/CROSS_REPO_CONTRACTS.md
- open PRs and active tasks touching main.cpp, canary_server.*, item registries/loaders, MonsterType/Monsters, Lua startup, datapacks, CMake or tests

Inspect current Git state before editing. Resolve any ownership overlap before implementation.

CONTRACT

Producer: blakinio/canary
Consumer: blakinio/Oteryn-Platform
Contract ID: oteryn.game-catalog
Schema: 1.0.0
Expected schema SHA-256: 099a8373ff2b0017cc2b321991662dc4e4783b626391aa7a110a6db0559d146b

Verify the matching Platform schema/contract read-only before claiming compatibility. Do not change the schema silently. If a schema defect is found, stop and coordinate a versioned contract change in both repositories.

CLI

Implement or adapt:

canary \
  --export-game-catalog-only \
  --game-catalog-output=/path/game-catalog.json

A fixed generated-at option may exist only for deterministic testing/reproducible generation.

LIFECYCLE REQUIREMENTS

The export-only path may load configuration, datapack definitions and the minimum runtime registries required for items, monsters and loot.

It must not:
- bind login/game/status/HTTP/metrics ports;
- start the world;
- enter normal game state;
- mutate or migrate a database;
- process houses, market expiry, raids, schedulers, webhooks or backups;
- require production credentials.

Inspect the exact current loader graph. Reuse authoritative loaders and final registries. Do not parse a subset of XML/Lua files independently and call it runtime truth.

If static definition loading cannot currently be separated from database-dependent operations, record the exact call path and implement the smallest safe loader split. Do not connect to production DB as a workaround.

PROPOSED STRUCTURE

Use repository conventions and adapt paths if current evidence requires it:

src/game/catalog/**
schemas/game-catalog/v1/**
tools/game-catalog/**
tests/game_catalog/**
<DATA_DIRECTORY>/catalog/**

Prefer small DTOs, collectors, a manifest reader, semantic validator and deterministic writer. Reuse existing JSON, hashing, filesystem and test utilities where available.

ITEMS

Read the final Item::items/ItemType registry after authoritative appearance and item loading.

Export bounded fields defined by the schema.
Do not use display name or numeric server ID alone as permanent cross-version identity.
Canonical-key collisions are blocking and require reviewed manifest metadata.
Reserved/invalid placeholders must not become normal public items.

CREATURES

Read the final Monsters/MonsterType registry after authoritative monster registration.

Export bounded runtime values, not source-code text.
Registration does not prove encounterability. Without evidence, use registered_only or unknown.

LOOT

Read final MonsterType loot blocks.
Resolve every target to an exported item entity.
Preserve chance numerator/denominator and count bounds.
Do not assume one universal denominator.
Relations have independent introduced/removed/completeness fields.
Dangling endpoints are blocking.

VERSIONS

Never compare versions as floats.
Use the explicit release registry and release_order.
removed_in is exclusive.
Protocol profile, runtime release, content target, verified content boundary, datapack revision, appearances hash and map hash are separate facts.

MANIFESTS

Resolve from <DATA_DIRECTORY>/catalog/**.
Malformed or conflicting manifests fail closed.
Missing historical/version/availability evidence remains unknown.
Do not mass-annotate data by guessing from external wikis or current names.

DETERMINISM

Use stable UTF-8 serialization and canonical sorting.
With identical inputs and fixed generated_at, output must be byte-identical.
Write a temporary file in the destination directory, validate it, flush/close it, atomically replace the final path, then write the lowercase SHA-256 sidecar.
A failed run must preserve a prior valid output.

VALIDATION

Prove:
- schema syntax and contract version;
- release uniqueness and references;
- canonical-key uniqueness;
- valid exclusive version ranges;
- bounded payloads;
- declared counts;
- relation endpoint integrity;
- valid loot probabilities/counts;
- safe relative source paths;
- deterministic sorting;
- no secrets/executable content.

TESTS

At minimum add focused evidence for:
- version ordering without floats;
- removed_in exclusivity;
- invalid range rejection;
- duplicate key rejection;
- dangling relation rejection;
- final item registry collection;
- final MonsterType collection;
- loot preservation;
- byte-identical fixed-time output;
- output hash sidecar;
- failed validation leaves no partial final file;
- export-only mode starts no services and performs no DB/world/market/house/backup mutation.

Use the repository build/test matrix and current CMake conventions. Do not invent successful validation.

CROSS-REPOSITORY FIXTURE

Create or validate one sanitized minimal fixture with:
- at least two releases;
- one visible item;
- one future item;
- one complete creature;
- one partial creature;
- one visible loot relation;
- one future loot relation.

The corresponding Platform implementation must be able to import the same fixture and prove version/completeness gating.

DELIVERY

Create a dedicated implementation task/branch if repository governance requires architecture closure before code.
Open a draft PR early.
Update the checkpoint after discoveries, implementation, validation and CI changes.
Review the full changed-file list and diff.
Do not modify .otbm, items.otb, production secrets or unrelated datapack content.
Do not deploy or activate anything in production.

At completion report:
- exact task, branch and PR;
- contract/schema version and verified SHA-256;
- changed paths;
- exact tests/commands and outcomes;
- CI on the final head;
- proven loader boundary;
- remaining UNKNOWN facts;
- deferred child tasks;
- exactly one next_action.
```
