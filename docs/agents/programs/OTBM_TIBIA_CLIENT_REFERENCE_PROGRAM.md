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
| TCR-010 | Compact Evidence Gateway Integration | ready | Stable TCR-005/006/007 and merged TCR-009 `c678d904...` | TCR-005, TCR-006, TCR-007, TCR-009 stable/merged | low | Start the smallest read-only QA-018 gateway integration for bounded house, content, proficiency and drift extracts; do not reparse sources or add mutation authority. |
| TCR-011 | Reviewed Adoption Router | blocked-by-TCR-009-and-TCR-010 | stable TCR-005/006/007 exist; TCR-009/010 are not stable | TCR-005, TCR-006, TCR-007, TCR-009, TCR-010 stable/merged | medium | Do not start until all required producer/gateway contracts are stable/merged. No executor or mutation authority. |

# Stable producer contract state

TCR-000 stabilizes the **architecture/governance contract**.

TCR-001, TCR-002, TCR-003, TCR-004, TCR-005, TCR-006 and TCR-007 stabilize these reference, resolver and correlation contracts:

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
```

The manifest is `stable/merged` as of PR #809 / merge `3227ee1e3b5f323656b101a601f873ae21b61f27`. It provides exact selected-input identity, size, SHA-256, source role, explicit client-build evidence state, parser revision, optional generated-index hash pins and deterministic provenance metadata. It is not StaticData, StaticMapData, map authority or gameplay parity evidence.

The StaticData index is `stable/merged` as of PR #827 / merge `24d106b5eea40371833ce20de96184b55cd9b661`. It provides deterministic manifest-bound records for the reviewed legacy/newer StaticData schema families with explicit schema provenance and findings. It is registry/reference evidence only and does not prove Canary gameplay, runtime behavior, quest completion, spawn behavior, house access, map geometry or OTBM parity.

The StaticMapData index is `stable/merged` as of PR #851 / merge `e8f825cb15fa4fd3b253018d98b4dc78e4a966a9`. It provides deterministic manifest-bound house IDs, layout origin, dimensions/floors, ordered rows and tile object/wall/door reference evidence with explicit findings and bounded input handling. It does not prove OTBM item-ID equivalence, full item stacks, AID/UID/mechanics, map authority, runtime house access or gameplay parity.

The Proficiency index is `stable/merged` as of PR #858 / merge `ce2c6e611f98f82c4f84e948372da0e1d324761f`. It provides deterministic manifest-bound proficiency IDs, names, optional versions, ordered levels, optional XP requirements and reviewed perk records with explicit duplicate findings. It does not prove appearance-ID or Canary runtime equivalence, XP/mastery formulas, perk application, persistence, protocol/UI behavior or gameplay parity.

The house-ID resolver and house reference parity contracts are `stable/merged` as of PR #868 / merge `5641a7ac2420f5a3d512325423088890e92ac3cb`. They provide exact provenance-pinned reviewed house-ID mappings and deterministic comparison of StaticData registry, StaticMapData layout and canonical World Index house evidence. They preserve unresolved `staticmapdata.object_id`, keep evidence dimensions separate and emit review findings only; they do not prove runtime ownership, rent, access or gameplay parity.

The content-reference resolver and correlation contracts are `stable/merged` as of PR #880 / merge `78b3435510c7e09d10a87ca2338bef59a24475bb`. They consume exact manifest-bound StaticData evidence and explicit reviewed mappings to existing creature/spawn, boss, quest/storage and achievement owners while preserving source-family vocabulary and unresolved joins. They emit review evidence only and do not prove runtime behavior, gameplay parity or authorize mutation.

The proficiency-reference resolver and correlation contracts are `stable/merged` as of PR #898 / merge `89acb51d3f3c3b4d6de5c7c8a4557b2d931f88ed`. They consume exact TCR-004 proficiency definitions, canonical appearance proficiency/object bindings and compact Canary loader/runtime evidence through exact reviewed mappings. They keep definition, appearance, item, runtime, persistence, protocol/client, automated behavior and Physical E2E separate; they do not prove gameplay parity or authorize mutation.

TCR-008 is `optional/deferred-no-concrete-use-case`. TCR-009 is `blocked-external-evidence` on `TCR009_REQUIRES_TWO_COMPLETE_EXACT_REFERENCE_SNAPSHOTS` with exact owner request `RTREQ-TCR-ITEM-DEFINITIONS-0002`. TCR-010 and TCR-011 remain dependency-blocked. `canary-tibia-client-reference-drift-v1`, gateway integration and adoption routing are **not stable/merged**.

OWA-003 may later consume `canary-tibia-client-reference-manifest-v1`, `canary-tibia-staticdata-index-v1`, `canary-tibia-staticmapdata-index-v1`, `canary-tibia-proficiency-index-v1`, `canary-otbm-house-id-resolver-v1`, `canary-otbm-house-reference-parity-v1`, `canary-tibia-content-reference-resolver-v1`, `canary-tibia-content-reference-correlation-v1`, `canary-tibia-proficiency-reference-resolver-v1` and `canary-tibia-proficiency-reference-correlation-v1` only within their exact stable provenance/reference boundaries where that dependency is required. It must not infer map authority, `staticmapdata.object_id` equivalence, unreviewed proficiency-ID equivalence, gameplay/runtime parity or any still-planned minimap, drift, gateway or routing output before the owning bounded package merges.

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

Planned public format:

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

Acceptance:

- reuse QA-018 source/hash/format/pointer confinement;
- only reviewed bounded extracts;
- no source parsing in the gateway;
- no semantic reinterpretation.

## TCR-011 — Adoption Router

Planned public format:

```text
canary-tibia-reference-adoption-routing-v1
```

Acceptance:

- deterministic owner/capability classification;
- map changes route only to existing supported repair/materialization capabilities;
- unsupported map changes remain unsupported rather than expanding writers implicitly;
- non-OTBM findings route to their module owners;
- no approval generation, writer execution, deployment or gameplay claim.

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

- Task: `docs/agents/tasks/archive/CAN-20260728-tcr-009-client-reference-drift.md`.
- Feature/preflight PR: `#992`; exact head `ada7a9e6f7d855a2d6f8c34d003b752a49251c1b`; merge `8a88e2f09257e620985770e5e053381df32f916d`.
- Ready-state protected CI: run `30399382989`, success.
- Lifecycle PR: `#993`.
- Disposition: `blocked-external-evidence`; no TCR-009 producer contract was delivered or stabilized.

# Blockers and unresolved references

- Exact client build identity for future user-supplied files is package-specific and must be proven or recorded unknown.
- Staticmap `object_id` -> OTBM/server item ID equivalence is not proven by this programme and is deliberately blocked until a dedicated resolver is evidenced.
- The proficiency filename/location is not standardized in this architecture; implementation must use explicit file selection.
- New client schemas beyond the independently verified old/new staticdata families require a new bounded schema-discovery task.
- Direct source-code reuse from the research repository is blocked by licensing review; independent implementation is the default.

# Exact next action after TCR-009 evidence preflight

All currently executable programme work is complete. TCR-000 through TCR-007 remain stable/merged within their exact evidence boundaries. TCR-008 is optional/deferred because no concrete minimap parity use case was found.

TCR-009 must not resume until owner request `RTREQ-TCR-ITEM-DEFINITIONS-0002` is satisfied with two distinct complete exact retained snapshot sets, each containing a validated manifest plus compatible StaticData, StaticMapData and proficiency indexes with exact hashes, revisions and explicit client-build evidence state. The first failure remains:

```text
TCR009_REQUIRES_TWO_COMPLETE_EXACT_REFERENCE_SNAPSHOTS
```

Do not start TCR-010, TCR-011 or OWA-003 before TCR-009 is genuinely implemented, validated and merged stable. Do not synthesize snapshots, reuse one snapshot as A and B, infer build identity from filenames or commit proprietary/generated client artifacts.

# Handoff

A continuation agent must:

1. read root `AGENTS.md`, repository/context routing and this programme;
2. re-fetch current `main`, active tasks, branches, PRs and retained evidence;
3. inspect `RTREQ-TCR-ITEM-DEFINITIONS-0002` first;
4. resume TCR-009 only if two distinct complete exact snapshot sets now satisfy the request contract;
5. create one new bounded active task/branch/early draft PR for the drift producer;
6. reuse TCR-001 through TCR-004 producers and QA-016 dependency-scoped freshness semantics;
7. preserve unresolved ID spaces and never equate reference drift with gameplay regression;
8. keep all proprietary inputs and generated reports outside Git;
9. leave TCR-008 deferred unless a concrete non-duplicative advisory use case exists;
10. leave TCR-010, TCR-011 and OWA-003 blocked until their exact dependencies are stable/merged.

# Agent kickoff prompt

```text
Continue CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE from repository state.
Repository writes are allowed only in blakinio/canary.
Do not rely on previous chat history.

Fresh preflight is mandatory. Read AGENTS.md, repository/context routing, this programme, OTBM_TIBIA_CLIENT_REFERENCE_ARCHITECTURE.md and owner request RTREQ-TCR-ITEM-DEFINITIONS-0002.

Current durable state:
- TCR-000..007 stable/merged within exact evidence boundaries;
- TCR-008 optional/deferred-no-concrete-use-case;
- TCR-009 blocked-external-evidence on TCR009_REQUIRES_TWO_COMPLETE_EXACT_REFERENCE_SNAPSHOTS;
- TCR-010, TCR-011 and OWA-003 dependency-blocked;
- no canary-tibia-client-reference-drift-v1 stable contract exists.

Resume TCR-009 only when two distinct complete exact retained manifest/index snapshot sets are proven. Otherwise do not create a task or synthetic evidence. Never commit proprietary client packages or generated reports, and never create duplicate parsers, indexes, gateways, assurance engines, pathfinders or E2E runners.
```
