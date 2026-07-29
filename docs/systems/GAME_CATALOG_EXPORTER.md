# Game Catalog Exporter Architecture

Status: Proposed  
Contract: `oteryn.game-catalog` / schemas `1.0.0`, `1.1.0`, `1.2.0`

## Goal

Provide a deterministic, offline Canary export of final runtime items, creatures and loot for Oteryn Platform without starting world services or mutating runtime databases.

## Design principles

1. Final loaded runtime registries are the source of truth for exported parameters.
2. Explicit datapack manifests supply only reviewed version, completeness and availability metadata.
3. Missing evidence remains unknown.
4. The exporter is a separate CLI lifecycle, not a normal server startup with ports disabled afterward.
5. Output is immutable, bounded, deterministic and transaction-like at the filesystem boundary.
6. External wikis are research/UX references only.
7. Schema `1.1.0` represents an unproven datapack-wide verified-content boundary as null; null never implies completeness or activation safety.

## First vertical slice

Included:

- release registry;
- snapshot provenance;
- items;
- creatures;
- creature loot;
- completeness and availability metadata;
- deterministic JSON and SHA-256;
- schema and semantic validation.

Deferred:

- NPCs and shop offers;
- quests and rewards;
- spawns, raids and map attainability;
- public sprite extraction;
- historical snapshot production;
- automatic 7.60/8.x runtime compatibility.

## Proposed source layout

```text
src/game/catalog/
├── catalog_export_mode.hpp
├── game_catalog_exporter.hpp
├── game_catalog_exporter.cpp
├── game_catalog_snapshot.hpp
├── game_catalog_version.hpp
├── game_catalog_version.cpp
├── game_catalog_manifest.hpp
├── game_catalog_manifest.cpp
├── game_catalog_validator.hpp
├── game_catalog_validator.cpp
├── game_catalog_json_writer.hpp
├── game_catalog_json_writer.cpp
├── dto/
│   ├── catalog_entity.hpp
│   ├── catalog_relation.hpp
│   ├── catalog_item.hpp
│   └── catalog_creature.hpp
└── collectors/
    ├── item_catalog_collector.hpp
    ├── item_catalog_collector.cpp
    ├── creature_catalog_collector.hpp
    ├── creature_catalog_collector.cpp
    ├── loot_catalog_collector.hpp
    └── loot_catalog_collector.cpp
```

Proposed support files:

```text
schemas/game-catalog/v1/game-catalog-snapshot.schema.json
schemas/game-catalog/v1.1/game-catalog-snapshot.schema.json
schemas/game-catalog/v1.2/game-catalog-snapshot.schema.json

tools/game-catalog/
├── validate_manifest.py
├── validate_snapshot.py
└── compare_snapshots.py

tests/game_catalog/
├── game_catalog_version_test.cpp
├── game_catalog_manifest_test.cpp
├── game_catalog_item_collector_test.cpp
├── game_catalog_creature_collector_test.cpp
├── game_catalog_loot_collector_test.cpp
├── game_catalog_determinism_test.cpp
└── fixtures/
```

## Datapack metadata layout

Metadata resolves relative to the selected `DATA_DIRECTORY`:

```text
<DATA_DIRECTORY>/catalog/
├── profile.json
├── releases.json
├── versioning/
│   ├── items.json
│   └── creatures.json
├── availability/
│   ├── items.json
│   └── creatures.json
└── overrides/
    └── approved-backports.json
```

The implementation must not hardcode `data-otservbr-global` as the only allowed source.

`profile.json` declares the output schema version. Schema `1.0.0` requires a concrete `verified_content_through_release`. Schema `1.1.0` permits null and serializes it unchanged. Unsupported versions and a null boundary mislabeled as `1.0.0` fail closed.

The first repository-default schema 1.1 seed lives under
`data-otservbr-global/catalog`. It reviews only Dragon, dragon shield and their
resolved loot relation. Exact claim sources are recorded in
`data-otservbr-global/catalog/EVIDENCE.md`; historical bounds and completeness
remain null or unverified. CI loads the real Dragon definition in a bounded
runtime projection and exports the seed twice. This projection does not
certify the complete datapack: unresolved item endpoints and out-of-range loot
probabilities found by a full export remain separate fail-closed integrity
findings before staging.

## CLI lifecycle

Proposed arguments:

```text
--export-game-catalog-only
--game-catalog-output=<path>
--game-catalog-generated-at=<RFC3339>   # tests/reproducible builds only
```

### Main dispatch

`main()` detects the export-only flag before normal `CanaryServer::run()` and calls a dedicated method such as:

```cpp
int CanaryServer::exportGameCatalogOnly(const CatalogExportOptions &options);
```

The implementation should reuse the existing CLI-only Lua API documentation mode pattern but must define its own loader boundary.

### Required phases

```text
parse and validate CLI arguments
load configuration
validate datapack selection
initialize minimum runtime services required by loaders
load appearances and final item definitions
load Lua libraries/scripts needed by monster registration
load monsters
load catalogue manifests
collect items
collect creatures
collect loot relations
validate schema-level shape
validate semantic integrity
serialize deterministically
write temporary output
flush and atomically rename
write SHA-256 sidecar
clean shutdown
```

### Forbidden phases

```text
database migration/update
market expiration
house rent/payment or transfer
world/map start unless separately proven necessary for a later availability slice
network service registration
webhooks
runtime scheduler/event execution
server online state
production backup
```

## Loader discovery requirement

Current normal startup combines definition loading with late operations that may depend on the database or world state. Implementation must inspect the exact current loader graph and create the smallest safe split.

Acceptable solutions include:

- extracting a reusable `loadCatalogDefinitions()` sequence from existing authoritative loaders;
- adding an explicit load profile to an existing orchestrator;
- separating late DB/runtime initialization from static definition registration.

Unacceptable solutions include:

- parsing selected XML/Lua files independently and claiming final runtime parity;
- connecting to production DB because it is convenient;
- skipping loader failures;
- inventing defaults for missing definitions.

## Item collector

Input authority:

```text
Item::items final loaded registry
```

Responsibilities:

- iterate valid final-registry item types with a nonzero runtime ID and nonempty name;
- collect final values after appearance and XML/custom overlays;
- assign stable canonical keys using reviewed rules;
- preserve namespaced numeric identifiers;
- attach reviewed version/availability metadata;
- produce explicit `unverified`/`unknown` states when metadata is absent;
- avoid exporting reserved/invalid sprite placeholders as normal public items.

`ItemType::loaded` indicates that an `items.xml` overlay was parsed. It is not a final-registry membership flag: appearance-backed records can be valid runtime loot endpoints without that overlay and must be exported.

Canonical identity cannot rely solely on display name or current server ID. Any collision is blocking and must be resolved through reviewed manifest identity metadata.

## Creature collector

Input authority:

```text
Monsters final registry and MonsterType records
```

Responsibilities:

- export registered creature definitions;
- preserve final HP, XP, movement, defense, boss and Bestiary fields;
- serialize attacks, defenses, elements and immunities as bounded non-executable data;
- preserve source provenance where available;
- classify registration separately from encounterability.

A creature definition without spawn/raid/quest evidence remains `registered_only` or `unknown`.

## Loot collector

Input authority:

```text
MonsterType::info.lootItems
```

Responsibilities:

- create one or more deterministic relations for each runtime loot entry;
- resolve item targets against exported item entities;
- preserve the configured loot threshold and count bounds without clamping or dropping source records;
- preserve nested container information through `container_path` or a later versioned structure;
- reject unresolved item endpoints;
- apply relation-specific version/completeness metadata.

A loot relation may have a later introduction version than both its creature and item.

The default runtime compares the configured threshold after schedule/rate scaling and a dynamic factor against `getLootRandom()`. Schemas 1.0 and 1.1 expose only a bounded rational probability, so thresholds above the declared denominator remain a fail-closed publication blocker. Schema evolution must be consumer first and must identify the runtime model plus its configured threshold and roll maximum; the exporter must not reinterpret those values as a context-free percentage.

## Version model

Versions are registry objects, not floats.

Each release contains:

```text
key
display_label
major
minor
patch
build nullable
release_order
protocol_family nullable
released_at nullable
```

Visibility uses:

```text
introduced_order <= target_order
AND (removed_order IS NULL OR target_order < removed_order)
```

`removed_in` is exclusive.

## Provenance

Every snapshot records at least:

- exact Canary Git commit;
- selected datapack revision when provable;
- protocol profile;
- runtime release;
- content target release;
- verified content boundary;
- appearance file SHA-256;
- optional map SHA-256;
- generation timestamp;
- entity and relation counts.

Do not infer a release from filenames or directory names.

## Deterministic serialization

Rules:

- UTF-8 without BOM;
- one defined newline policy;
- stable JSON key order;
- releases sorted by `release_order` then key;
- entities sorted by type then canonical key;
- relations sorted by type then canonical key;
- identifiers sorted by namespace then value;
- stable nested structures where order is non-semantic;
- no absolute paths;
- no locale-dependent number/string formatting.

The writer serializes to `<output>.tmp.<random>` in the same directory and replaces the final file only after validation and successful close/flush.

Failure removes the temporary file when possible and leaves any prior valid snapshot untouched.

## Validation layers

### Manifest validation

- known schema/version;
- no duplicate release/entity keys;
- no conflicting annotations;
- safe relative paths;
- valid release references;
- release range ordering;
- explicit override reason and provenance.

### Snapshot validation

- declared counts equal actual counts;
- unique canonical keys;
- numeric bounds;
- item and creature payload requirements;
- relation endpoint integrity;
- probability/count integrity;
- deterministic sort order;
- schema conformance;
- no secret-like fields or executable content.

## Security

- output path is operator supplied but must reject empty paths and directory targets;
- temporary files use restricted process defaults;
- no raw credentials, DB strings, environment dumps or personal data are exported;
- source paths are repository/datapack-relative;
- opaque attributes remain data and are never executed by the consumer;
- external URLs are not fetched during export.

## Tests

### Focused C++ tests

- release ordering does not use floats;
- exclusive removed-release semantics;
- duplicate canonical key rejection;
- invalid release range rejection;
- missing relation endpoint rejection;
- item collector reads final registry values;
- creature collector reads final `MonsterType` values;
- loot chance/count preservation;
- deterministic ordering;
- fixed timestamp produces byte-identical output;
- failed validation leaves no final partial file.

### Runtime boundary tests

- export-only mode binds no service ports;
- export-only mode does not enter normal game state;
- export-only mode does not execute DB migration/market/house/backup paths;
- malformed manifest returns non-zero;
- output and sidecar hashes match;
- schema file hash matches Platform contract fixture.

## CI proposal

```text
.github/workflows/game-catalog.yml
```

Jobs:

1. validate JSON schema syntax;
2. validate manifest fixtures;
3. build focused exporter/test targets;
4. run focused unit tests;
5. generate a minimal fixture snapshot twice with a fixed timestamp;
6. compare byte-for-byte;
7. validate against schema;
8. verify SHA-256 sidecar;
9. compare the canonical schema hash expected by the Platform contract.

## Cross-repository rollout

1. Architecture/contracts accepted in both repositories.
2. Platform importer/storage merged inactive.
3. Canary exporter merged.
4. Sanitized staging snapshot generated and reviewed.
5. Staging import and rollback proven.
6. Public items/creatures enabled in a separate Platform slice.

Canary exporter deployment is producer-first safe because it is an offline optional CLI. Platform must reject unsupported schema versions.

## Later extension points

NPCs require a bounded const iteration API over the NPC registry and explicit shop relation models.

Quests require a reviewed canonical registry/manifest; filenames and storage references alone are insufficient.

Map availability requires spawn, raid, scripted creation, reachability and exact map/datapack evidence. It should reuse existing world-index and validation tooling rather than create a second map scanner.

Historical profiles require snapshots generated from compatible historical runtime/datapack/asset baselines. Filtering a modern snapshot does not recreate historical mechanics or parameters.

## Implementation gate

Before implementation begins, the agent must:

- confirm no overlapping active task/PR ownership;
- update the task checkpoint;
- verify the matching Platform contract/schema hash;
- inspect current build/test registration conventions;
- prove or document the minimal loader split;
- open a draft PR early;
- keep NPCs, quests and map availability out of the first slice.
