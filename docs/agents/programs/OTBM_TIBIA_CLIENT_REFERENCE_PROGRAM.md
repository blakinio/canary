---
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
module_id: otbm-tooling
name: OTBM Tibia Client Reference Programme
status: active
owner: OTBM analysis tooling / Real Tibia parity
created: 2026-07-23T10:00:00+02:00
updated: 2026-07-28T23:33:00+02:00
last_verified_commit: "8a88e2f09257e620985770e5e053381df32f916d"
primary_paths:
  - docs/ai-agent/OTBM_TIBIA_CLIENT_REFERENCE_ARCHITECTURE.md
  - docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md
  - tools/ai-agent/tibia_client_reference*.py
  - tools/ai-agent/otbm_*reference*.py
shared_integration_paths:
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md
  - docs/agents/real-tibia/registry/modules/otbm-tooling.yaml
  - docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md
  - docs/agents/CHANGELOG.md
related_programs:
  - CAN-PROGRAM-REAL-TIBIA-PARITY
cross_repo_contracts: []
---

# Mission

Build a deterministic, read-only, provenance-pinned reference layer for exact user-supplied Tibia 15.x client files and connect that evidence to the existing Canary OTBM/Real Tibia parity stack without duplicating canonical parsers, validators, pathfinders, renderers, mutation engines or E2E infrastructure.

The programme is a successor/extension of the mature OTBM tooling stack. It adds **client reference evidence**, not a second map authority.

# Authoritative architecture

`docs/ai-agent/OTBM_TIBIA_CLIENT_REFERENCE_ARCHITECTURE.md`

# Scope

Included:

- exact client-package selection and SHA-256 provenance;
- read-only staticdata indexing with explicit schema family;
- read-only staticmapdata house-layout indexing;
- read-only proficiency indexing;
- reuse of existing canonical appearances/assets evidence;
- explicit identifier-space resolution;
- house reference parity against canonical OTBM World Index evidence;
- bounded monster/boss/quest/achievement registry correlation routed to existing subsystem owners;
- bounded proficiency correlation routed to the proficiency subsystem owner;
- optional minimap reference evidence with strict non-authority boundaries;
- deterministic reference-to-reference drift;
- evidence-gateway integration after formats stabilize;
- reviewed adoption routing into existing OTBM repair/materialization or non-OTBM tasks.

Excluded:

- copying code from `beats-dh/Beats-Assets-Editor`;
- committing proprietary Tibia client files/assets;
- automatic full OTBM generation from staticmapdata;
- guessing item/server ID mappings;
- creating a second OTBM parser, World Index, pathfinder, renderer, Script Resolution engine or E2E platform;
- automatic map/datapack/runtime/protocol/client mutation;
- declaring gameplay parity from static reference agreement.

# Target baseline model

Keep these independent:

```text
server revision
protocol/client target
reference client package identity
reference client build evidence state
map SHA-256
World Index SHA-256
appearances index SHA-256
client-assets index SHA-256
datapack revision
spawn/NPC sidecar revision
```

Never infer the map version from the protocol/client version and never infer the client build from a filename alone.

# Initial research baseline

## External research source

```text
repository: beats-dh/Beats-Assets-Editor
role: read-only format/interoperability research
commit: ed827be34c279d1279ad3dde3af434b148ac05c7
license observed: CC BY-NC-SA 4.0
```

Research observations used by the architecture:

- modern/legacy appearance parsing and sprite/catalog handling exist in the project;
- newer-client staticdata uses a different top-level protobuf field layout than the legacy schema;
- newer-client staticdata exposes monsters, monster classes, achievements, houses, bosses and quests;
- staticmapdata exposes house IDs, layout origin, dimensions/floors and tile-level object/wall/door records;
- proficiency definitions expose IDs, levels, XP requirements and perk records;
- the project can inspect Canary `items.xml` proficiency bindings;
- client minimap tiles and OTClient `.otmm` support exist but are different evidence classes.

These observations authorize format investigation only. They do not authorize source-code copying or direct server/map modification.

# Existing reusable Canary modules

Mandatory reuse before implementation:

| Need | Existing owner |
|---|---|
| Full OTBM parsing/indexing | Unified OTBM World Index |
| AID/UID/house-door/teleport inventory | World Index + item/mechanic audit |
| Lua/XML mechanic resolution | OTBM Script Resolution |
| Appearance semantics | `canary-appearances-index-v1` |
| Client sprite asset coverage | `canary-client-assets-index-v1` |
| Map-used appearance/asset compatibility | QA-014 `canary-otbm-asset-compatibility-v1` |
| Walkability/routes/transitions | canonical OTBM Reachability |
| Spawn/NPC/boss map correlation | OTBM Spawn/Boss/NPC Validator |
| Quest map/source correlation | Quest Map Validator |
| Storage progression evidence | OTBM Storage Dependency Graph / Quest State Reachability |
| Geometry/house components | OTBM Geometry Audit |
| Critical house/landmark access | OTBM Critical Access Integrity |
| Before/after map semantics | Semantic OTBM Diff |
| Review-only map change planning | repair preflight/recommendation / donor-region planner |
| Approved bounded OTBM mutation | existing patch/materialization pipelines |
| Static/release evidence aggregation | Map Quality / World Health / QA-016/017/018 |
| Runtime/gameplay proof | Universal Physical E2E |

# Source and proof matrix

| Question | Client reference proves | Existing Canary/OTBM evidence required | Still not proven |
|---|---|---|---|
| Does a client registry contain monster X? | exact selected client registry record | optional Canary definition/spawn correlation | combat/loot/spawn/runtime parity |
| Does a client registry contain quest X? | exact quest ID/name record | Quest Map Validator + storage/runtime evidence | quest stages/handlers/rewards/completion |
| What house metadata is client-visible? | exact staticdata house record | OTBM house evidence for parity | live ownership/rent/runtime access |
| What house layout is encoded client-side? | exact staticmapdata layout record | World Index/Geometry/Critical Access | full OTBM item stack/AID/UID/mechanics |
| Which proficiency definition is present? | exact selected proficiency record | appearance/item/runtime/persistence/protocol joins | gameplay effect correctness |
| Did a client snapshot change? | exact reference-index semantic diff | affected subsystem validation | regression/gameplay impact |

# Queue

| ID | Scope | Status | Evidence baseline | Dependencies | Risk | Exact next action |
|---|---|---|---|---|---|---|
| TCR-000 | Architecture, programme and discovery integration | merged | Canary main `d5a08db0...`; Beats research pin `ed827be3...` | none | low | Complete. Architecture/governance merged in PR #762; no producer output format was delivered. |
| TCR-001 | Client Package Manifest | merged | `canary-tibia-client-reference-manifest-v1`; PR #809; merge `3227ee1e...` | TCR-000 merged | medium | Complete. Exact package/reference provenance producer is stable/merged. |
| TCR-002 | StaticData Reference Index | merged | `canary-tibia-staticdata-index-v1`; PR #827; merge `24d106b5...` | TCR-001 merged | medium | Complete. Exact manifest-bound StaticData registry/reference producer is stable/merged; it is not gameplay/runtime/map parity proof. |
| TCR-003 | StaticMapData House Index | merged | `canary-tibia-staticmapdata-index-v1`; PR #851; merge `e8f825c...` | TCR-001, TCR-002 merged | medium | Complete. Exact manifest-bound StaticMapData house-layout producer is stable/merged; object-ID mapping and gameplay/map authority remain unresolved. |
| TCR-004 | Proficiency Reference Index | merged | `canary-tibia-proficiency-index-v1`; PR #858; merge `ce2c6e6...` | TCR-001 merged | medium | Complete. Exact manifest-bound proficiency-definition producer is stable/merged; cross-namespace/runtime/gameplay equivalence remains unproven. |
| TCR-005 | OTBM House Reference Parity | merged | `canary-otbm-house-id-resolver-v1` + `canary-otbm-house-reference-parity-v1`; PR #868; merge `5641a7a...` | TCR-002/TCR-002A, TCR-003, World Index | medium | Complete. Exact reviewed house-ID resolution and read-only house reference parity are stable/merged; object-ID, runtime and gameplay parity remain unresolved. |
| TCR-006 | Global Content Registry Correlation | merged | `canary-tibia-content-reference-resolver-v1` + `canary-tibia-content-reference-correlation-v1`; PR #880; merge `78b34355...` | TCR-002/TCR-002A | medium | Complete. Exact reviewed cross-namespace resolution and read-only content registry correlation are stable/merged; runtime/gameplay parity and mutation remain unproven. |
| TCR-007 | Proficiency Reference Correlation | merged | `canary-tibia-proficiency-reference-resolver-v1` + `canary-tibia-proficiency-reference-correlation-v1`; PR #898; merge `89acb51d...` | TCR-004 | medium | Complete. Exact reviewed proficiency/appearance/item resolution and read-only correlation are stable/merged; runtime, persistence, protocol/client, automated behavior, Physical E2E and gameplay parity remain separate evidence dimensions. |
| TCR-008 | Optional Minimap Reference | optional/deferred-no-concrete-use-case | no concrete parity use case found in fresh 2026-07-28 preflight | TCR-001 merged | low | Do not implement on speculation. Reopen only for a documented advisory-only use case not already covered by World Index, landmarks, Reachability, factual rendering or StaticMapData. |
| TCR-009 | Client Reference Drift | merged | `canary-tibia-client-reference-drift-v1`; PR #1018; merge `c678d904...`; consumed request `RTREQ-TCR-ITEM-DEFINITIONS-0002`; retained evidence summary `6224a175...`; retained drift `be0593cb...` | TCR-002, TCR-003, TCR-004/TCR-004A | medium | Complete. Deterministic manifest/index drift is stable/merged; StaticData `legacy -> newer` remains an explicit family boundary and the contract grants no gameplay or mutation authority. |
| TCR-010 | Compact Evidence Gateway Integration | merged | `canary-tibia-client-reference-evidence-bindings-v1` + `canary-tibia-client-reference-evidence-gateway-v1`; PR #1027; merge `34a2a375...`; delegates to QA-018 | TCR-005, TCR-006, TCR-007, TCR-009 stable/merged | low | Complete. Exact reviewed binding transport is stable/merged; no parsing, reinterpretation, mutation, E2E, acceptance or routing authority. |
| TCR-011 | Reviewed Adoption Router | merged | `canary-tibia-reference-adoption-routing-request-v1` + `canary-tibia-reference-adoption-routing-v1`; PR #1029; merge `094523da...` | TCR-005, TCR-006, TCR-007, TCR-009, TCR-010 stable/merged | medium | Complete. Exact reviewed extract routing is stable/merged; map work routes only through QA-003, unsupported/blocked outcomes remain explicit, and no parser, target-state, approval, writer, deployment, E2E or gameplay authority was added. |

# Stable producer contract state

TCR-000 stabilizes the **architecture/governance contract**.

TCR-001 through TCR-007 and TCR-009 through TCR-011 stabilize these reference, resolver, correlation, drift, compact gateway and reviewed adoption-routing contracts:

```text
canary-tibia-client-reference-manifest-v1
canary-tibia-staticdata-index-v1
canary-tibia-staticmapdata-index-v1
canary-tibia-proficiency-index-v1
canary-otbm-house-id-resolver-v1
canary-otbm-house-reference-parity-v1
canary-tibia-content-reference-resolver-v1
canary-tibia-content-reference-correlation-v1
canary-tibia-proficiency-reference-resolver-v1
canary-tibia-proficiency-reference-correlation-v1
canary-tibia-client-reference-drift-v1
canary-tibia-client-reference-evidence-bindings-v1
canary-tibia-client-reference-evidence-gateway-v1
canary-tibia-reference-adoption-routing-request-v1
canary-tibia-reference-adoption-routing-v1
```

The manifest is `stable/merged` as of PR #809 / merge `3227ee1e3b5f323656b101a601f873ae21b61f27`. It provides exact selected-input identity, size, SHA-256, source role, explicit client-build evidence state, parser revision, optional generated-index hash pins and deterministic provenance metadata. It is not StaticData, StaticMapData, map authority or gameplay parity evidence.

The StaticData index is `stable/merged` as of PR #827 / merge `24d106b5eea40371833ce20de96184b55cd9b661`. It provides deterministic manifest-bound records for the reviewed legacy/newer StaticData schema families with explicit schema provenance and findings. It is registry/reference evidence only and does not prove Canary gameplay, runtime behavior, quest completion, spawn behavior, house access, map geometry or OTBM parity.

The StaticMapData index is `stable/merged` as of PR #851 / merge `e8f825cb15fa4fd3b253018d98b4dc78e4a966a9`. It provides deterministic manifest-bound house IDs, layout origin, dimensions/floors, ordered rows and tile object/wall/door reference evidence with explicit findings and bounded input handling. It does not prove OTBM item-ID equivalence, full item stacks, AID/UID/mechanics, map authority, runtime house access or gameplay parity.

The Proficiency index is `stable/merged` as of PR #858 / merge `ce2c6e611f98f82c4f84e948372da0e1d324761f`. It provides deterministic manifest-bound proficiency IDs, names, optional versions, ordered levels, optional XP requirements and reviewed perk records with explicit duplicate findings. It does not prove appearance-ID or Canary runtime equivalence, XP/mastery formulas, perk application, persistence, protocol/UI behavior or gameplay parity.

The house-ID resolver and house reference parity contracts are `stable/merged` as of PR #868 / merge `5641a7ac2420f5a3d512325423088890e92ac3cb`. They provide exact provenance-pinned reviewed house-ID mappings and deterministic comparison of StaticData registry, StaticMapData layout and canonical World Index house evidence. They preserve unresolved `staticmapdata.object_id`, keep evidence dimensions separate and emit review findings only; they do not prove runtime ownership, rent, access or gameplay parity.

The content-reference resolver and correlation contracts are `stable/merged` as of PR #880 / merge `78b3435510c7e09d10a87ca2338bef59a24475bb`. They consume exact manifest-bound StaticData evidence and explicit reviewed mappings to existing creature/spawn, boss, quest/storage and achievement owners while preserving source-family vocabulary and unresolved joins. They emit review evidence only and do not prove runtime behavior, gameplay parity or authorize mutation.

The proficiency-reference resolver and correlation contracts are `stable/merged` as of PR #898 / merge `89acb51d3f3c3b4d6de5c7c8a4557b2d931f88ed`. They consume exact TCR-004 proficiency definitions, canonical appearance proficiency/object bindings and compact Canary loader/runtime evidence through exact reviewed mappings. They keep definition, appearance, item, runtime, persistence, protocol/client, automated behavior and Physical E2E separate; they do not prove gameplay parity or authorize mutation.

The client-reference drift contract is `stable/merged` as of PR #1018 / merge `c678d90483af945b3bbf0a40f6d6b9ce99da4a3f`. It compares exact retained manifest/index snapshots, preserves dependency-scoped staleness and fails closed across the StaticData schema-family boundary. It does not prove gameplay impact or authorize mutation.

The client-reference evidence binding and gateway contracts are `stable/merged` as of PR #1027 / merge `34a2a3750f20c318ecc07aa7407ca0b9a9311834`. They expose one exact reviewed house, content, proficiency or drift extract through QA-018 path, SHA-256, format, JSON Pointer and serialized-size enforcement. They add no parser, semantic reinterpretation, E2E, acceptance or routing authority.

The reviewed adoption-routing request and report contracts are `stable/merged` as of PR #1029 / merge `094523da1c07eaebcc7096606b690a25cf3474a9`. They require one exact executed TCR-010 report plus one reviewer-authored hash-pinned request, cover every selected extract exactly once, route only to a closed inventory of existing owners/capabilities and preserve explicit unsupported/blocked outcomes. Map work routes only through QA-003; the contracts add no target-state inference, approval, mutation request, writer execution, deployment, E2E or gameplay authority.

TCR-008 remains `optional/deferred-no-concrete-use-case`. All required TCR packages TCR-000 through TCR-011 are now stable/merged. OWA-003 is dependency-ready as the next separate bounded package.

OWA-003 may consume stable TCR-001 through TCR-011 contracts only within their exact provenance boundaries. No consumer may infer map authority, `staticmapdata.object_id` equivalence, unreviewed proficiency-ID equivalence, gameplay/runtime parity, approval or mutation authority.

# Package contracts

## TCR-001 — Client Package Manifest

Stable public format:

```text
canary-tibia-client-reference-manifest-v1
```

Required behavior:

- one explicit package root;
- explicit selected files;
- safe relative paths only;
- no recursive arbitrary binary execution/inspection;
- byte size + SHA-256 for every selected input;
- explicit source role;
- client build/version evidence state (`proven`, `declared`, `unknown`, `conflicting`);
- exact parser revision;
- exact generated-index hashes;
- deterministic JSON;
- create-new/no-clobber output by default;
- symlink/input-output alias rejection.

Acceptance:

- same stable input produces byte-identical manifest;
- changed byte content changes the relevant hash;
- missing/unsafe selected input fails closed;
- no proprietary input is copied into Git/output bundle.

## TCR-002 — StaticData Reference Index

Stable public format:

```text
canary-tibia-staticdata-index-v1
```

Acceptance:

- old/new schema handling is independently reproduced and tested;
- wrong/ambiguous schema cannot silently relabel categories;
- raw and explicitly supported compressed variants are bounded;
- duplicate IDs are explicit findings;
- category/source schema is retained per output;
- quest records remain ID/name inventory only;
- no gameplay conclusions are emitted.

## TCR-003 — StaticMapData House Index

Stable public format:

```text
canary-tibia-staticmapdata-index-v1
```

Acceptance:

- exact source hash retained;
- house IDs/layout positions/dimensions/floors/rows/tiles preserved deterministically;
- malformed dimensions/row shapes become findings/errors;
- staticmap object IDs are labeled in their own unresolved namespace;
- no OTBM is parsed or written by this tool.

## TCR-004 — Proficiency Reference Index

Stable public format:

```text
canary-tibia-proficiency-index-v1
```

Acceptance:

- explicit file selection only;
- deterministic ID/level/perk preservation;
- duplicate proficiency IDs fail/report per contract;
- exact source hash retained;
- appearance-side proficiency correlation reuses the canonical appearance index;
- no `items.xml` write behavior exists in this package.

## TCR-005 — OTBM House Reference Parity

Stable public formats:

```text
canary-otbm-house-id-resolver-v1
canary-otbm-house-reference-parity-v1
```

Required joins:

```text
staticdata house registry
        +
staticmapdata house layout
        +
canonical World Index house evidence
        +
optional existing Geometry / Critical Access / Reachability
```

Acceptance:

- exact manifest/index/map provenance required;
- one explicit provenance-pinned reviewed house-ID resolver is required;
- no heuristic ID/name/proximity or numeric-identity mapping;
- footprint/floor/position/house presence evidence separated from unproven object-ID parity;
- mismatches are review findings only;
- no mutation, pathfinding or geometry recomputation.

## TCR-006 — Global Content Registry Correlation

Stable public formats:

```text
canary-tibia-content-reference-resolver-v1
canary-tibia-content-reference-correlation-v1
```

Acceptance:

- monster, boss, quest and achievement registry records remain distinct;
- existing creature/spawn/quest/achievement evidence is consumed, not rebuilt;
- missing Canary evidence is not automatically classified as a defect without the relevant module proof;
- dynamic/unresolved source behavior remains unresolved.

## TCR-007 — Proficiency Reference Correlation

Stable public formats:

```text
canary-tibia-proficiency-reference-resolver-v1
canary-tibia-proficiency-reference-correlation-v1
```

Acceptance:

- definition, appearance binding, Canary item binding, runtime, persistence, protocol and E2E are separate dimensions;
- OTBM never claims ownership of gameplay implementation;
- missing runtime proof cannot be upgraded by matching static IDs.

## TCR-008 — Optional Minimap Reference

No implementation should begin until a specific use case is selected.

Acceptance must preserve:

- official-client minimap data as geometry/reference evidence only;
- OTClient `.otmm` as local/user exploration evidence only;
- no second pathfinder;
- no override of World Index/Reachability mechanics truth.

## TCR-009 — Client Reference Drift

Stable public format:

```text
canary-tibia-client-reference-drift-v1
```

Acceptance:

- exact baseline/current manifests;
- deterministic added/removed/changed records;
- no timestamp-based freshness;
- changed component marks only declared consumers stale;
- unchanged dependent evidence remains distinguishable from changed dependent evidence.

## TCR-010 — Evidence Gateway

Stable public formats:

```text
canary-tibia-client-reference-evidence-bindings-v1
canary-tibia-client-reference-evidence-gateway-v1
```

Acceptance:

- reuse QA-018 source/hash/format/pointer confinement;
- only reviewed bounded extracts;
- no source parsing in the gateway;
- no semantic reinterpretation.

## TCR-011 — Adoption Router

Stable public formats:

```text
canary-tibia-reference-adoption-routing-request-v1
canary-tibia-reference-adoption-routing-v1
```

Acceptance:

- require one exact executed TCR-010 report plus one reviewer-authored hash-pinned request;
- preserve exact binding, kind, extract ID, source ID, JSON Pointer and extract value SHA-256;
- deterministic fixed owner/capability classification with complete one-time extract coverage;
- map changes route only to existing OTBM-QA-003 Repair Recommendation, never directly to a writer/materializer;
- unsupported and blocked outcomes remain explicit rather than expanding writers or inventing target state;
- non-OTBM findings route only to existing module/TCR owners;
- no parser, approval generation, mutation request, writer execution, deployment, E2E or gameplay claim.

# First vertical slice

The first implementation milestone is **not** “import Tibia Global.”

It is:

```text
one exact client reference snapshot
  -> TCR-001 manifest
  -> TCR-002 staticdata index
  -> TCR-003 staticmapdata index
  -> one reviewed house ID
  -> TCR-005 house parity
  -> exact report, zero mutation
```

This vertical slice is delivered by TCR-001 through TCR-005. It proves the integration architecture before broader content correlation or any repair proposal.

# Validation matrix

| Package | Determinism | Provenance | Path safety | Schema/format tests | Existing evidence reuse | Runtime/E2E required |
|---|---|---|---|---|---|---|
| TCR-001 | required | required | required | manifest fixtures | n/a | no |
| TCR-002 | required | required | required | old/new/compression | no duplicate appearance parser | no |
| TCR-003 | required | required | required | layout/dimension/compression | World Index only in consumer | no |
| TCR-004 | required | required | required | proficiency fixtures | appearances index | no |
| TCR-005 | required | exact cross-input | n/a | parity fixtures | World Index/Geometry/Critical Access | no, unless later claiming gameplay |
| TCR-006 | required | exact cross-input | n/a | correlation fixtures | quest/spawn/achievement owners | module-specific |
| TCR-007 | required | exact cross-input | n/a | correlation fixtures | proficiency owners | yes for gameplay claims |
| TCR-008 | required | required | required | minimap fixtures | no pathfinder duplication | no |
| TCR-009 | required | both snapshots | n/a | drift fixtures | release provenance/freshness | no |
| TCR-010 | existing QA-018 | existing QA-018 | existing QA-018 | pointer fixtures | evidence gateway | no |
| TCR-011 | required | exact finding refs | n/a | routing fixtures | repair/subsystem owners | downstream |

# Last bounded lifecycle disposition

- TCR-009 feature PR `#1018` merged as `c678d90483af945b3bbf0a40f6d6b9ce99da4a3f`.
- TCR-009 lifecycle PR `#1025` merged as `7095f27c684f0825278c5fcc4b78f93f85ab087b`.
- Discovery reconciliation PR `#1026` merged as `6c7bdb8817d2010620d119a9a1f6b944895bc73d`.
- TCR-010 feature PR `#1027` merged as `34a2a3750f20c318ecc07aa7407ca0b9a9311834` after readiness/final-gate run `30522402785` passed.
- TCR-011 feature PR `#1029` merged as `094523da1c07eaebcc7096606b690a25cf3474a9` after readiness/final-gate CI `30530210426` passed.
- TCR-011 lifecycle PR `#1030` archives the terminal task and marks OWA-003 dependency-ready.

# Blockers and unresolved references

- Exact client build identity for future user-supplied files is package-specific and must be proven or recorded unknown.
- Staticmap `object_id` -> OTBM/server item ID equivalence is not proven by this programme and is deliberately blocked until a dedicated resolver is evidenced.
- The proficiency filename/location is not standardized in this architecture; implementation must use explicit file selection.
- New client schemas beyond the independently verified old/new staticdata families require a new bounded schema-discovery task.
- Direct source-code reuse from the research repository is blocked by licensing review; independent implementation is the default.

# Exact next action after TCR programme completion

Start one bounded OWA-003 package from the merged TCR-011 lifecycle state. Consume only exact stable TCR evidence through the reviewed adoption router, preserve unsupported/blocked outcomes and reuse existing repair/subsystem owners; do not add a second parser, router, executor, approval or mutation path.

# Handoff

Continue from `main` merge `094523da1c07eaebcc7096606b690a25cf3474a9` and the archived TCR-011 checkpoint after lifecycle PR #1030 merges. The required TCR sequence is complete; OWA-003 is dependency-ready but remains a separate bounded task with its own ownership, evidence and merge gate.
