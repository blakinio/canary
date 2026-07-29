# Oteryn Game Catalog Export Contract

Status: Proposed  
Contract ID: `oteryn.game-catalog`  
Initial schema version: `1.0.0`  
Current additive schema version: `1.1.0`
Producer: `blakinio/canary`  
Consumer: `blakinio/Oteryn-Platform`

## Purpose

This contract defines a deterministic, offline, read-only export of structured game data from the exact loaded Canary runtime into Oteryn Platform.

It does not authorize:

- scraping or importing external wikis as runtime truth;
- modifying Canary gameplay data;
- publishing incomplete content;
- inferring historical versions, availability, spawns or quest completeness;
- starting world services or mutating the database during export.

## Authority and ownership

- Canary is authoritative for the final loaded item, creature and loot semantics.
- Datapack catalogue manifests are authoritative only for explicit release, completeness and availability annotations they contain.
- Oteryn Platform owns persistence, localization, profiles, visibility projections, UI and administration after import.
- A corrected export is a new immutable snapshot. The consumer must never silently repair producer facts.

## Transport

Schema v1 uses operator/deployment files:

```text
game-catalog.json
game-catalog.json.sha256
```

No network push and no browser upload are part of v1.

## CLI boundary

Proposed command:

```bash
canary \
  --export-game-catalog-only \
  --game-catalog-output=/output/game-catalog.json
```

The implementation must use a dedicated CLI-only lifecycle. It must not call the normal server run path after data collection.

The export process may:

- load configuration;
- validate the selected datapack;
- initialize the Lua environment required to load definitions;
- load appearances, final item definitions, scripts and monster definitions required by the first slice;
- read explicit catalogue manifests;
- validate and serialize a snapshot;
- write a temporary file, then atomically replace the requested output;
- write a lowercase SHA-256 sidecar.

The export process must not:

- open login, game, status, HTTP or metrics services;
- enter normal game state;
- execute house rent, market expiration, schedulers, raids or webhooks;
- create backups;
- modify a database;
- require production credentials merely to export static runtime definitions.

If the exact minimum loader split cannot avoid a database dependency, implementation must stop and document the blocker rather than silently use production database state.

## Top-level document

```json
{
  "contract": "oteryn.game-catalog",
  "schema_version": "1.0.0",
  "snapshot": {},
  "releases": [],
  "entities": [],
  "relations": []
}
```

Unknown top-level fields are rejected by schema v1.

## Snapshot provenance

Required fields:

```text
generated_at
canary_commit_sha
protocol_profile
runtime_release
content_target_release
verified_content_through_release
appearances_sha256
entity_count
relation_count
```

Optional fields:

```text
datapack_commit_sha
contains_content_through_release
map_sha256
producer_build_id
```

Protocol support, runtime release, target content release, verified content boundary, datapack revision, appearance revision and map revision are independent facts.

A newer protocol profile does not prove that all content for that protocol release is complete.

Schema `1.0.0` requires `verified_content_through_release` to reference a concrete release. Schema `1.1.0` permits null when no reviewed datapack-wide completeness boundary exists. Null means unknown, never complete or verified. It allows deterministic inactive export and review but is not sufficient for Platform activation.

## Release registry

Every release has a stable `key`, display components and an explicit integer `release_order`.

Versions must never be parsed or compared as floating-point values.

Rules:

- release keys and `release_order` values are unique;
- all entity and relation release references resolve;
- `removed_in`, when present, is an exclusive upper bound;
- conflicting release definitions are blocking;
- historical release claims require reviewed evidence.

## Entities

Schema v1 supports:

```text
item
creature
```

Reserved future types:

```text
npc
quest
spell
area
```

Each entity includes:

```text
type
canonical_key
introduced_in nullable
removed_in nullable
completeness
availability
runtime_present
enabled
identifiers
source_path nullable
data
```

### Stable identity

`canonical_key` is language-independent and stable within the catalogue contract, for example:

```text
item:dragon-shield
creature:dragon
```

Names and numeric server/client IDs are not cross-version identity by themselves. Numeric IDs are namespaced snapshot identifiers.

The exporter must not merge two records only because their names match.

### Completeness

Supported values:

```text
complete
partial
unverified
disabled
missing_dependencies
```

The exporter never promotes an unknown or partial record to `complete`.

### Availability

Initial item values:

```text
obtainable
quest_only
boss_only
event_only
npc_only
starter
registered_only
admin_only
unreachable
unknown
```

Initial creature values:

```text
encounterable
boss_only
event_only
quest_only
registered_only
admin_only
unreachable
unknown
```

A loaded definition proves runtime registration, not player availability. Stronger availability requires explicit evidence such as a reviewed spawn, loot source, NPC offer, quest, event or starter rule.

## Item collection

The item collector must read the final loaded `ItemType` registry after authoritative appearance and item loaders have run.

It must not implement a second partial parser and claim final runtime equivalence.

The first slice exports bounded fields including IDs, name, description, category, weapon type, attack, defense, armor, requirements, slots, classifications, elemental fields and safe opaque attributes.

## Creature collection

The creature collector reads the final `Monsters`/`MonsterType` registry after datapack monster scripts have registered.

The first slice exports bounded runtime fields including name, race/look identifiers, HP, XP, speed, armor, defense, mitigation, boss flags, Bestiary fields, elements, immunities, attacks and defenses.

## Loot relations

Schema v1 supports `creature_loot`.

Each relation has its own identity, release range, completeness and enabled state independent of both endpoint entities.

Loot payload:

```text
chance_numerator
chance_denominator
minimum_count
maximum_count
container_path nullable
condition_data nullable
```

The exporter must preserve the runtime probability representation and must not assume one universal denominator.

Every source and target endpoint must exist in the same snapshot. Dangling references are blocking.

## Datapack metadata

Proposed root:

```text
<DATA_DIRECTORY>/catalog/
```

Initial files:

```text
profile.json
releases.json
versioning/items.json
versioning/creatures.json
availability/items.json
availability/creatures.json
overrides/approved-backports.json
```

Rules:

- malformed or conflicting metadata fails closed;
- manifests are deterministic and reviewable;
- a missing annotation remains unknown rather than guessed;
- only a small evidence-backed fixture set should be seeded initially;
- complete bulk historical annotation is a separate evidence programme.

The repository-default `data-otservbr-global/catalog` seed is intentionally
bounded to dragon shield (`3416`), Dragon (`dragon`) and the resolved runtime
loot block (`dragon|3416|20`). Its historical bounds are null and its
completeness is `unverified`; explicit repository spawns and loot prove only
`encounterable` and `obtainable`. `EVIDENCE.md` maps each claim to repository
source. This seed is not a datapack-wide completeness or deployment claim.

A bounded real-Dragon projection is valid for deterministic metadata
regression. A full default-datapack export must still fail closed if unrelated
runtime loot blocks have unresolved item endpoints or probabilities outside
the declared denominator. Such records require a separate evidence-backed data
integrity task; they must not be silently dropped or normalized by metadata.

## Determinism

The producer must use:

- UTF-8;
- deterministic JSON key ordering;
- entity sorting by type and canonical key;
- relation sorting by type and canonical key;
- stable ordering of identifiers and nested arrays where order is not semantic;
- relative source paths only;
- no machine-specific values;
- no nondeterministic unordered-map iteration leakage.

With identical inputs and a fixed `generated_at`, output must be byte-identical.

## Validation

Before writing the final file, the producer validates:

- contract and schema version;
- release uniqueness and references;
- entity and relation key uniqueness;
- version ranges;
- identifier bounds;
- payload bounds;
- declared counts;
- relation endpoint integrity;
- probability and count ranges;
- path safety;
- deterministic ordering.

Any blocking finding returns a non-zero process exit code and leaves no partial final output.

## Schema synchronization

Canonical paths:

```text
Canary: schemas/game-catalog/v1/game-catalog-snapshot.schema.json
Platform: resources/schemas/game-catalog/v1/game-catalog-snapshot.schema.json
Canary: schemas/game-catalog/v1.1/game-catalog-snapshot.schema.json
Platform: resources/schemas/game-catalog/v1.1/game-catalog-snapshot.schema.json
```

Both files must be byte-identical. Proposed schema v1 SHA-256:

```text
099a8373ff2b0017cc2b321991662dc4e4783b626391aa7a110a6db0559d146b
```

Schema `1.1.0` SHA-256:

```text
323ff6ae849759c9190f2a0c342855194ed74645816adc45051b6d914e67c7ac
```

A schema change requires a new semantic version, compatibility analysis, fixture updates, contract tests and explicit rollout order in both repositories. Schema `1.0.0` remains byte unchanged.

## First shared fixture

The first implementation fixture contains at least:

- two releases;
- one visible item;
- one future item;
- one complete creature;
- one partial creature;
- one visible loot relation;
- one future loot relation.

## Rollout

Schema `1.1.0` uses a consumer-first-safe rollout:

1. merge Platform dual-schema validation, nullable inactive persistence and fail-closed activation while preserving retained `1.0.0` rollback;
2. merge Canary `1.1.0` producer support;
3. generate and review a schema `1.1.0` staging snapshot;
4. keep activation blocked until a concrete verified boundary is supplied by reviewed evidence;
5. add NPCs, quests, map availability and historical profiles in separate tasks.

Older consumers reject `1.1.0` fail closed. Producer `1.1.0` output must not be routed to an older consumer.

No production deployment or profile activation is authorized by this contract.

## Known unknowns

The following remain explicit until implementation discovery proves them:

- the exact loader split that avoids database-dependent late startup work;
- complete historical introduction/removal metadata;
- complete spawn, raid, quest and NPC availability evidence;
- historical item-ID mapping;
- exact 7.60 protocol/runtime compatibility;
- approved public sprite rendering source.
