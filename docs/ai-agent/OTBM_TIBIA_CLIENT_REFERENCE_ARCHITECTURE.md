# OTBM Tibia Client Reference Architecture

> Repository: `blakinio/canary`  
> Programme: `CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE`  
> Coordination: `OTBM-TIBIA-CLIENT-REFERENCE`  
> Status: planned architecture  
> Initial research pin: `beats-dh/Beats-Assets-Editor@ed827be34c279d1279ad3dde3af434b148ac05c7`  
> Evidence rule: official-client data is reference evidence; static agreement is not runtime/gameplay proof

## 1. Purpose

Define one deterministic, provenance-pinned way to ingest user-supplied Tibia 15.x client files outside Git, normalize selected client-side data into bounded reference indexes, and correlate that evidence with the existing canonical Canary/OTBM analysis stack.

The architecture is intended to let an agent answer questions such as:

- which houses, monsters, bosses, quests, achievements or proficiency definitions are present in one exact client snapshot;
- whether a house registry/layout from that snapshot corresponds to the exact current OTBM world evidence;
- whether a current Canary content definition exists for a client-visible registry entry;
- whether a newer client snapshot changed a house layout, registry entry, appearance semantic or proficiency definition;
- which existing OTBM validator, subsystem owner or bounded repair path must review a confirmed difference.

It is **not** an automatic Real Tibia importer. It does not convert client files into a complete server implementation and does not authorize map, datapack, runtime, protocol or asset mutation.

## 2. Research basis and licensing boundary

The initial format inventory is based on read-only inspection of:

```text
beats-dh/Beats-Assets-Editor
commit: ed827be34c279d1279ad3dde3af434b148ac05c7
project name in repository docs: Canary Studio Editor
```

Observed relevant feature domains include:

- appearances;
- sprites/catalog;
- staticdata;
- staticmapdata;
- proficiency;
- minimap;
- Canary monster Lua;
- Canary NPC Lua;
- DAT merge;
- QM/RCC/sounds.

The external repository is licensed CC BY-NC-SA 4.0 while this repository is GPLv2. Therefore:

- treat the external project as **research, format-discovery and interoperability evidence**;
- pin the exact external commit used for any architectural claim;
- do not copy source code into Canary under this programme;
- implement any parser independently from observed file contracts, independently derived test fixtures and locally supplied user files;
- do not commit proprietary Tibia client files or derived large asset dumps;
- obtain separate legal review/permission before any future direct code reuse.

This document is an engineering plan, not legal advice.

## 3. Existing canonical Canary boundaries

This programme extends existing evidence; it does not replace it.

### 3.1 OTBM map authority

The Unified OTBM World Index remains the only canonical full-world map evidence cache.

Reuse it for:

- exact tile positions and tile kinds;
- house IDs and tile flags;
- exact item placements and stack traversal order;
- item IDs;
- AID/UID;
- house-door IDs;
- teleport sources/destinations;
- exact bounded position and region queries.

No second OTBM parser, scanner or full-world map index may be introduced by this programme.

### 3.2 Appearance and asset authority

Reuse the existing:

- `canary-appearances-index-v1`;
- `canary-client-assets-index-v1`;
- `canary-otbm-asset-compatibility-v1`.

Do not introduce another canonical appearances or client-assets index merely because Canary Studio has its own loaders.

New reference indexes may point to these existing artifacts by exact SHA-256 and may add source-specific metadata not represented by them, but they must not re-own their responsibilities.

### 3.3 Mechanics and runtime correlation

Reuse:

- OTBM Script Resolution;
- Quest Map Validator;
- OTBM Reachability and its canonical BFS/path semantics;
- OTBM Spawn/Boss/NPC Validator;
- OTBM Storage Dependency Graph;
- OTBM Quest State Reachability;
- OTBM Geometry Audit;
- OTBM Critical Access Integrity;
- Semantic OTBM Diff;
- Map Quality / World Health / coverage / certification evidence;
- Universal Physical E2E for runtime/gameplay proof.

A client-reference parser never executes Lua and never upgrades unresolved runtime evidence to handled.

### 3.4 Mutation authority

A reference finding cannot directly mutate a map.

Any OTBM change must route through the already delivered capability chain as applicable:

```text
reference finding
  -> exact OTBM/current-state correlation
  -> repair preflight / recommendation
  -> explicit reviewed approval
  -> existing bounded patch/materialization capability
  -> create-new candidate
  -> native reparse
  -> rebuilt World Index
  -> Semantic Diff
  -> selected static QA
  -> impacted Physical E2E when required
```

The programme must not add a generic OTBM serializer, arbitrary item-stack editor or in-place writer.

## 4. Source package model

### 4.1 User-supplied input

A user may supply one exact Tibia client package or selected files from a package. The files remain outside Git.

Candidate inputs include:

- `appearances*.dat` or equivalent exact appearance file;
- `catalog-content.json`;
- sprite asset containers referenced by the catalog;
- `staticdata*.dat`;
- `staticmapdata*.dat`;
- proficiency definition file when present and explicitly selected;
- optional official-client minimap tiles/markers;
- optional other files only after a separate bounded format review.

The programme must not recursively ingest an arbitrary client directory by default. Selection is explicit and bounded.

### 4.2 Untrusted-input policy

Every selected path must:

- resolve below one explicitly supplied package root;
- reject symlink/path escape;
- be a regular file;
- enforce documented size bounds before full reads;
- be hashed before parsing;
- fail closed on malformed compression/protobuf/JSON;
- never execute contained code;
- never load DLL/EXE content merely because it exists in the package.

RCC/PE/QM/sounds remain outside the initial OTBM reference programme.

## 5. Root provenance contract

### 5.1 Planned format

```text
canary-tibia-client-reference-manifest-v1
```

### 5.2 Required identity

The manifest pins:

- manifest format/version;
- one stable `referenceId` assigned by the operator/task;
- package root identity recorded as a display label only, never trusted as version proof;
- explicit source role: `official-client-reference` or another reviewed role;
- observed/import timestamp as metadata only;
- user-declared client build/version when supplied;
- evidence state for build/version: `proven`, `declared`, `unknown`, `conflicting`;
- parser implementation revision/commit;
- exact selected input paths relative to package root;
- byte size and SHA-256 for every selected input;
- optional catalog/package metadata when present;
- exact SHA-256 of every generated reference index.

Timestamps never substitute for content hashes.

### 5.3 Build/version rule

A filename containing `15.x`, a package directory name or an application UI label does not prove an exact Tibia build.

If exact build provenance is unavailable:

```text
clientBuildEvidence = unknown
```

The reference can still be compared by exact file hashes. Agents must describe it by reference ID/hash rather than inventing a release label.

## 6. StaticData reference index

### 6.1 Planned format

```text
canary-tibia-staticdata-index-v1
```

### 6.2 Schema families

Research evidence shows at least two wire-incompatible top-level layouts.

Legacy-style categories:

- creatures;
- titles;
- houses;
- bosses;
- quests.

Newer-client categories observed by the pinned research source:

- monsters;
- monster classes;
- achievements;
- houses;
- bosses;
- quests.

The implementation must not assume that successful protobuf decoding proves the correct schema because protobuf unknown fields can be skipped. Schema selection needs deterministic evidence and must retain the selected schema family in the output.

The initial implementation task should independently verify a robust discriminator against user-supplied files. Round-trip fidelity is a candidate technique discovered during research, not an implementation mandate until reproduced by Canary-owned tests.

### 6.3 Normalized record families

The index should preserve source values without inventing semantics.

#### Monster/client creature registry

Candidate fields:

- numeric ID;
- name;
- outfit/look data;
- difficulty;
- occurrence;
- NPC flag;
- hostile flag.

#### Monster class registry

Candidate fields:

- numeric ID;
- name.

#### Achievement/title registry

Candidate fields:

- numeric ID;
- name;
- description;
- grade.

The normalized output must preserve whether the record came from a legacy `title` schema or a newer `achievement` schema rather than silently relabeling one as the other.

#### House registry

Candidate fields:

- house ID;
- name;
- description;
- rent;
- beds;
- position;
- size;
- guildhall flag;
- town;
- premium flag.

Field ordering differences between schema families must be normalized only after the selected schema is proven.

#### Boss registry

Candidate fields:

- boss ID;
- name;
- outfit/look data;
- archfoe flag.

#### Quest registry

Candidate fields observed in the research source are only:

- quest ID;
- name.

A quest registry entry does **not** prove quest stages, storages, handlers, map positions, rewards or completion logic.

### 6.4 Output guarantees

The index must include:

- source file SHA-256;
- selected schema family;
- exact category counts;
- deterministic record ordering;
- duplicate-ID findings per category;
- missing required-field findings;
- bounded malformed/unresolved evidence;
- no gameplay conclusions.

## 7. StaticMapData house-layout index

### 7.1 Planned format

```text
canary-tibia-staticmapdata-index-v1
```

### 7.2 Observed reference shape

The pinned research source models static map data as house details containing:

```text
HouseDetail
  house_id
  layout
    position
    size
      width
      height
      floors
    tiles
      floor_data
        rows
          tiles
            object_id
            wall_info.is_wall
            door_info.is_door
```

### 7.3 What it may prove

For one exact client reference snapshot, successful parsing may prove the presence of client-side house-layout records with:

- exact recorded house ID;
- recorded origin coordinate;
- recorded dimensions and floor count;
- ordered row/tile payload;
- recorded per-tile object ID;
- recorded wall/door booleans.

### 7.4 What it does not prove

`staticmapdata` is **not** a full OTBM source.

It does not by itself prove:

- OTBM node type or raw serialization;
- complete item stacks;
- server item-ID namespace;
- action IDs;
- unique IDs;
- house-door IDs;
- teleport destinations;
- tile flags/PZ;
- scripted mechanics;
- spawn/NPC placement;
- quest state;
- runtime accessibility.

Therefore the programme must never implement:

```text
staticmapdata -> automatic complete OTBM generation
```

### 7.5 `object_id` namespace boundary

The `object_id` carried by client static-map records must be treated as a distinct, unresolved identifier namespace until an exact mapping to the existing appearance/server/map namespaces is proven.

No implementation may equate:

```text
staticmapdata.object_id == OTBM itemId
```

merely because numeric values happen to match.

A future resolver may use exact, provenance-pinned mapping evidence. Name-based or visual sprite heuristics are not sufficient.

## 8. Proficiency reference index

### 8.1 Planned format

```text
canary-tibia-proficiency-index-v1
```

### 8.2 Candidate normalized fields

Research evidence shows proficiency entries with:

- `ProficiencyId`;
- name;
- optional version;
- ordered levels;
- optional XP requirement per level;
- ordered perks.

Candidate perk fields include:

- augment type;
- Bestiary ID/name;
- damage type;
- element ID;
- range;
- skill ID;
- spell ID;
- perk type;
- numeric value.

The exact on-disk filename/location is not standardized by this architecture. The implementation requires an explicit selected file and records its hash.

### 8.3 Binding layers

There are three distinct evidence layers:

1. client proficiency definition;
2. appearance-side proficiency flag/ID from the existing canonical appearances index;
3. Canary item/runtime proficiency binding.

The programme may correlate them only when identifier namespaces are explicitly resolved.

Do not treat a matching proficiency ID as proof that:

- the server applies all perks;
- XP/mastery progression is correct;
- persistence is correct;
- protocol/UI is correct;
- gameplay matches Real Tibia.

Those require subsystem-owned runtime, persistence, protocol and E2E evidence.

## 9. Existing appearances/assets integration

The new root manifest references existing canonical artifacts rather than replacing them:

```text
client reference manifest
  -> canary-appearances-index-v1
  -> canary-client-assets-index-v1
  -> optional canary-otbm-asset-compatibility-v1
```

The architecture may later extend appearance interpretation when a new client field is not currently preserved, but the change must update the canonical appearance index rather than creating a second parallel appearance parser.

In particular, the existing appearance index already exposes a proficiency flag ID and many walkability/interaction flags. New work should first verify current coverage before adding fields.

## 10. Optional minimap reference

### 10.1 Official-client minimap tiles

Official-client minimap tiles may provide advisory evidence for:

- floor coverage;
- geographic bounds;
- visible/explored geometry;
- visual comparison.

They cannot independently determine:

- OTBM item stacks;
- AID/UID;
- server house semantics;
- teleport mechanics;
- scripted transitions;
- canonical Reachability edges.

### 10.2 OTClient `.otmm`

An `.otmm` file represents one OTClient user's explored/local minimap state. It is useful for debugging and local visual evidence, not as a canonical Real Tibia world reference.

### 10.3 Pathfinder boundary

No minimap input may create a second pathfinder or override canonical OTBM Reachability. At most it can produce a separately labeled comparison finding.

## 11. Identifier and namespace model

Every index field that participates in a join must declare an identifier space.

Initial identifier spaces include:

```text
client-reference.house-id
client-reference.monster-id
client-reference.boss-id
client-reference.quest-id
client-reference.achievement-id
client-reference.monster-class-id
client-reference.staticmap-object-id
client-reference.proficiency-id
appearance.object-id
appearance.outfit-id
appearance.sprite-id
otbm.item-id
otbm.house-id
otbm.house-door-id
canary.item-id
canary.creature-name
canary.storage-key
```

Direct equality is permitted only when a resolver contract explicitly declares two spaces equivalent for the selected evidence set.

### 11.1 Resolver classifications

Use at least:

- `exact` — explicit same-namespace or reviewed deterministic mapping;
- `one-to-one-mapped` — exact external mapping evidence;
- `ambiguous` — multiple candidates;
- `missing-left`;
- `missing-right`;
- `conflicting`;
- `unresolved`.

Never resolve IDs by display-name similarity alone.

Names may be used as discovery hints but not as mutation authorization.

## 12. House Reference Parity consumer

### 12.1 Planned format

```text
canary-otbm-house-reference-parity-v1
```

### 12.2 Inputs

Required:

- exact `canary-tibia-client-reference-manifest-v1`;
- exact `canary-tibia-staticdata-index-v1`;
- exact `canary-tibia-staticmapdata-index-v1`;
- exact canonical `canary-otbm-world-index-v1` plus manifest.

Optional existing evidence:

- Geometry Audit;
- Critical Access Integrity;
- Reachability;
- Semantic Diff when comparing an OTBM change.

### 12.3 Comparison dimensions

For one reviewed house-ID resolver:

- house presence on each side;
- registry position versus layout origin versus OTBM house bounds;
- declared size versus observed OTBM house-tile population;
- declared floors versus observed OTBM house floors;
- layout dimensions versus observed house component bounds;
- staticmap door/wall flags as reference-only topology evidence;
- exact OTBM house-door placements from World Index;
- disconnected house-ID components from Geometry;
- selected critical-access evidence.

### 12.4 Finding states

Use at least:

- `conforming`;
- `reference-only`;
- `otbm-only`;
- `mismatch`;
- `partial`;
- `unresolved-id-space`;
- `conflicting`;
- `stale-evidence`.

A mismatch is a review finding. It is not automatic permission to modify a house.

### 12.5 Tile-level caution

Because static-map `object_id` is not proven to be the OTBM server item ID, v1 house parity should prioritize:

- footprint;
- floors;
- position;
- house presence;
- wall/door boolean topology;

before any object-level parity claim.

Object-level joins are a separate bounded package after the ID-space resolver is proven.

## 13. Global content registry correlation

### 13.1 Planned format

```text
canary-tibia-content-reference-correlation-v1
```

### 13.2 Consumers

#### Monsters

Correlate client registry evidence with existing Canary creature-definition and OTBM spawn/NPC evidence.

A client monster record can prove a client-visible registry entry. It cannot prove combat stats, loot, spells, spawn presence or authentic runtime behavior.

#### Bosses

Correlate boss registry entries with existing Canary creature/Bosstiary/spawn evidence.

Keep:

- client boss registry;
- Canary `rewardBoss` definition evidence;
- Bosstiary class evidence;
- spawn-boss evidence

as separate dimensions.

#### Quests

Use the client quest registry as inventory/discovery evidence only.

Correlate with:

- existing quest source inventory;
- Quest Map Validator;
- Storage Dependency Graph;
- Quest State Reachability;
- runtime/E2E evidence when available.

A client quest ID/name must never synthesize missing stages, storages, AIDs or handlers.

#### Achievements

Route achievement/title registry evidence to the existing Achievement validation ownership. Do not create a second achievement validator inside OTBM tooling.

## 14. Proficiency parity consumer

### 14.1 Planned format

```text
canary-tibia-proficiency-reference-correlation-v1
```

### 14.2 Inputs

- exact proficiency reference index;
- exact existing appearances index;
- explicitly selected Canary item-definition evidence;
- existing proficiency runtime/validation evidence when available.

### 14.3 Dimensions

- proficiency definition exists;
- appearance binding exists;
- Canary item binding exists;
- definition values agree where the same semantics are proven;
- runtime support evidence;
- persistence evidence;
- protocol/client evidence;
- automated behavior evidence;
- physical E2E evidence.

OTBM owns only map/item correlation dimensions. Gameplay implementation is routed to the proficiency subsystem owner.

## 15. Client-reference drift

### 15.1 Planned format

```text
canary-tibia-client-reference-drift-v1
```

### 15.2 Inputs

Two complete exact reference manifests:

```text
baseline reference A
current reference B
```

### 15.3 Deterministic change families

- input component added/removed/changed;
- staticdata schema-family change;
- monster/class/achievement/house/boss/quest additions/removals/field changes;
- staticmap house addition/removal/layout metadata change;
- proficiency definition/level/perk change;
- appearance changes through the existing canonical appearance-index comparison path;
- asset coverage changes through existing client-assets evidence.

### 15.4 Dependency-scoped staleness

A changed client-reference component marks only consumers that declare that component as a dependency stale.

This must integrate conceptually with existing release provenance/freshness rules rather than introduce timestamp-based freshness.

## 16. Evidence gateway integration

After the reference formats are stable, bounded extracts may be exposed through the existing OTBM Compact Evidence Gateway.

Candidate reviewed extracts:

- one house registry record;
- one house layout summary;
- one monster/boss/quest registry record;
- one proficiency definition;
- one drift finding.

The gateway remains transport/query only. It must not re-parse client files or reinterpret reference semantics.

## 17. Adoption router

### 17.1 Planned format

```text
canary-tibia-reference-adoption-routing-v1
```

This is a review-oriented classification result, not an executor.

### 17.2 Routing table

| Finding family | Owner / next evidence path |
|---|---|
| House footprint/layout mismatch | OTBM House Reference Parity -> existing repair recommendation/preflight if a precise supported mutation exists |
| Missing/changed map region not representable by existing bounded writers | donor/region planning or new separately reviewed mutation architecture; never synthesize from staticmapdata |
| Monster/boss registry gap | creature/Bosstiary/spawn module task |
| Quest registry gap | quest parity task using Quest Map Validator/storage/runtime evidence |
| Achievement registry gap | existing Achievement validation/programme |
| Proficiency definition/binding gap | proficiency subsystem task; OTBM only supplies item/map evidence |
| Appearance/asset gap | existing appearance/assets/QA-014 path |
| Minimap geometry discrepancy | review-only geometry investigation; canonical OTBM evidence remains World Index/Geometry/Reachability |

### 17.3 Mutation gate

Routing may classify:

- `no-change-required`;
- `review-required`;
- `otbm-supported-repair-candidate`;
- `otbm-unsupported-mutation`;
- `non-otbm-owner`;
- `blocked-by-reference`;
- `blocked-by-id-space`;
- `conflicting`.

It cannot create an approval or run a writer.

## 18. End-to-end architecture

```text
USER-SUPPLIED TIBIA CLIENT FILES (outside Git)
        |
        v
canary-tibia-client-reference-manifest-v1
  exact selected files + SHA-256 + source/build evidence
        |
        +-------------------- existing ----------------------+
        |                                                    |
        v                                                    v
staticdata reference index                         appearances/assets indexes
staticmapdata reference index                      QA-014 compatibility
proficiency reference index
optional minimap reference
        |                                                    |
        +---------------------+------------------------------+
                              v
                  identifier-space resolvers
                              |
                              v
                  parity/correlation consumers
           +------------------+--------------------+
           |                  |                    |
           v                  v                    v
   house reference       content registry     proficiency
       parity              correlation        correlation
           |                  |                    |
           v                  v                    v
 World Index/Geometry   Quest/Spawn/NPC/     subsystem-owned
 Critical Access        Achievement owners   runtime evidence
           |
           +------------------+--------------------+
                              v
                       exact findings
                              |
                              v
                  reference drift/freshness
                              |
                              v
                   compact evidence gateway
                              |
                              v
                      adoption routing
                   /          |           \
                  v           v            v
         existing OTBM    non-OTBM      blocked /
         repair chain     module task    unresolved
                  |
                  v
          create-new candidate only
                  |
                  v
     reparse -> World Index -> Semantic Diff
                  |
                  v
         QA / certification / selected E2E
```

## 19. Failure model

The reference ingestion and every consumer fail closed for:

- missing selected file;
- changed SHA-256;
- unsafe path/symlink/path escape;
- unsupported or ambiguous schema;
- malformed compression/protobuf/JSON;
- duplicate IDs where uniqueness is required;
- ambiguous identifier mapping;
- mismatched manifest/index provenance;
- stale dependent evidence;
- truncated/bounded evidence when a complete comparison is required;
- unsupported client build semantics;
- attempts to use staticmapdata as full OTBM authority;
- attempts to use minimap evidence as mechanics/pathfinding authority.

`UNKNOWN` remains `UNKNOWN`.

## 20. Security and privacy boundaries

- Never commit proprietary client files or extracted asset archives.
- Never execute binaries from a supplied package.
- Never load arbitrary native libraries/plugins from the package.
- Prefer standard-library parser implementations where practical.
- Put generated indexes/reports in `artifacts/**` or another approved external artifact path.
- Hash source bytes before parse and record parser revision.
- Use bounded outputs and exact counts to protect agent context.
- Reject output aliasing with inputs and unsafe/symlink outputs.
- Default to create-new/no-clobber for generated evidence.

## 21. Testing strategy for implementation packages

Every future implementation package must include focused tests for its own contract.

At minimum:

### Manifest

- deterministic ordering/hash behavior;
- path confinement;
- symlink rejection;
- changed-file detection;
- missing-file failure;
- build evidence states.

### StaticData

- old schema fixture;
- new schema fixture;
- ambiguous/wrong-schema case;
- raw and supported compressed wrappers;
- duplicate/missing ID findings;
- deterministic output;
- real-file opt-in test outside Git.

### StaticMapData

- house/layout parse;
- dimensions/floor/row consistency;
- malformed tile rows;
- compression variants;
- deterministic output;
- real-file opt-in test outside Git.

### Proficiency

- explicit file selection;
- level/perk preservation;
- numeric fidelity sufficient for semantic comparison;
- duplicate IDs;
- deterministic output;
- appearance binding join with exact provenance.

### Parity consumers

- exact compatible provenance;
- stale/mixed provenance rejection;
- missing-side classifications;
- ambiguous ID-space classification;
- bounded samples plus exact totals;
- no mutation side effects.

### Drift

- identical snapshots -> zero semantic changes;
- component-only changes mark only dependent dimensions;
- deterministic change ordering;
- no timestamp freshness inference.

## 22. Delivery sequence

Implementation is split into bounded packages defined by the programme document.

Recommended dependency order:

```text
TCR-001 package manifest
   |
   +--> TCR-002 staticdata index
   |
   +--> TCR-003 staticmapdata index
   |        |
   |        +--> TCR-005 house reference parity
   |
   +--> TCR-004 proficiency index
   |        |
   |        +--> TCR-007 proficiency correlation
   |
   +--> TCR-006 content registry correlation
   |
   +--> TCR-008 optional minimap reference
   |
   +--> TCR-009 client-reference drift
                |
                +--> TCR-010 evidence gateway integration
                |
                +--> TCR-011 reviewed adoption router
```

TCR-005 is the first recommended OTBM parity consumer because staticdata/staticmapdata provide uniquely useful house reference evidence and the current OTBM stack already has strong house, geometry and access evidence.

## 23. Initial success criteria

The programme's first useful vertical slice is complete when an agent can, for one exact user-supplied client snapshot and one exact OTBM World Index:

1. prove the selected client files by SHA-256;
2. build deterministic staticdata and staticmapdata indexes;
3. select one reviewed house ID;
4. produce a fail-closed house parity result comparing registry/layout evidence with exact OTBM house evidence;
5. preserve unresolved `object_id` namespace instead of guessing item IDs;
6. route any mismatch to review without mutating the map;
7. expose exact source/index hashes in the report;
8. rerun deterministically with byte-identical output for the same evidence set.

This vertical slice does not require an OTBM modification.

## 24. Explicit non-goals

This architecture does not authorize:

- copying Canary Studio source code;
- committing Tibia client binaries/assets;
- treating a client package as complete server truth;
- replacing the existing OTBM parser/World Index;
- replacing the existing appearances/assets indexes;
- creating a second pathfinder or renderer;
- auto-generating a full OTBM from staticmapdata;
- guessing server item IDs from client/staticmap object IDs;
- guessing quest logic from quest ID/name;
- auto-writing `items.xml` proficiency attributes;
- automatic monster/NPC/datapack creation;
- direct production deployment;
- declaring gameplay parity from static client/server/map agreement.

## 25. Handoff

A future implementation agent must start from the programme queue, re-fetch current `main`, open PRs and active tasks, then implement exactly one bounded package.

The first implementation package should be `TCR-001` unless current repository state already contains an equivalent canonical client-package manifest. The first OTBM parity consumer should be `TCR-005` only after `TCR-001`, `TCR-002` and `TCR-003` are merged and stable.
