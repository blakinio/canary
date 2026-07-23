---
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
module_id: otbm-tooling
name: OTBM Tibia Client Reference Programme
status: active
owner: OTBM analysis tooling / Real Tibia parity
created: 2026-07-23T10:00:00+02:00
updated: 2026-07-23T23:35:00+02:00
last_verified_commit: "24d106b5eea40371833ce20de96184b55cd9b661"
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
| TCR-003 | StaticMapData House Index | planned (next candidate) | exact stable manifest + independently verified fixture | TCR-001 merged | medium | After fresh ownership/reuse preflight, implement only `canary-tibia-staticmapdata-index-v1` with house/layout provenance, row/dimension consistency and unresolved object-ID namespace. |
| TCR-004 | Proficiency Reference Index | planned | exact explicit proficiency file + appearances index | TCR-001 merged | medium | Implement `canary-tibia-proficiency-index-v1`; preserve levels/perks and correlate only explicit proficiency-ID evidence. |
| TCR-005 | OTBM House Reference Parity | planned | staticdata + staticmapdata + World Index | TCR-002, TCR-003 | medium | Build the first parity consumer `canary-otbm-house-reference-parity-v1`; compare one reviewed house-ID resolver and fail closed on ID-space/provenance uncertainty. |
| TCR-006 | Global Content Registry Correlation | planned | staticdata index + existing subsystem evidence | TCR-002 | medium | Add read-only correlation for monsters/bosses/quests/achievements, routing each dimension to existing validators/programmes without duplicating ownership. |
| TCR-007 | Proficiency Reference Correlation | planned | proficiency + appearances + Canary item/runtime evidence | TCR-004 | medium | Add `canary-tibia-proficiency-reference-correlation-v1`; keep OTBM/item evidence separate from runtime/persistence/protocol proof. |
| TCR-008 | Optional Minimap Reference | planned | exact official-client tile/marker selection | TCR-001 merged | low | Add only if a concrete parity use case exists; preserve advisory-only status and never alter canonical Reachability/pathfinding. |
| TCR-009 | Client Reference Drift | planned | two complete exact reference manifests/index sets | TCR-002, TCR-003, TCR-004 | medium | Implement deterministic `canary-tibia-client-reference-drift-v1` and dependency-scoped staleness inputs. |
| TCR-010 | Compact Evidence Gateway Integration | planned | stable TCR report formats | TCR-005, TCR-006, TCR-007, TCR-009 | low | Add reviewed JSON-pointer extracts to the existing QA-018 evidence gateway; do not reparse or reinterpret source semantics. |
| TCR-011 | Reviewed Adoption Router | planned | stable parity/drift findings | TCR-005, TCR-006, TCR-007, TCR-009 | medium | Implement review-only routing to existing OTBM repair chains or subsystem tasks; no approval generation and no executor. |

# Stable producer contract state

TCR-000 stabilizes the **architecture/governance contract**.

TCR-001 and TCR-002 stabilize these producer contracts:

```text
canary-tibia-client-reference-manifest-v1
canary-tibia-staticdata-index-v1
```

The manifest is `stable/merged` as of PR #809 / merge `3227ee1e3b5f323656b101a601f873ae21b61f27`. It provides exact selected-input identity, size, SHA-256, source role, explicit client-build evidence state, parser revision, optional generated-index hash pins and deterministic provenance metadata. It is not StaticData, StaticMapData, map authority or gameplay parity evidence.

The StaticData index is `stable/merged` as of PR #827 / merge `24d106b5eea40371833ce20de96184b55cd9b661`. It provides deterministic manifest-bound records for the reviewed legacy/newer StaticData schema families with explicit schema provenance and findings. It is registry/reference evidence only and does not prove Canary gameplay, runtime behavior, quest completion, spawn behavior, house access, map geometry or OTBM parity.

The following remain planned and **not stable/merged**: `canary-tibia-staticmapdata-index-v1`, `canary-tibia-proficiency-index-v1`, all parity/correlation reports and `canary-tibia-client-reference-drift-v1`.

OWA-003 may later consume `canary-tibia-client-reference-manifest-v1` and `canary-tibia-staticdata-index-v1` only within their exact stable provenance/reference boundaries where that dependency is required. It must not infer map authority, gameplay/runtime parity or any still-planned TCR producer/parity output before the owning bounded package merges.

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

Planned public format:

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

Planned public format:

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

Planned public format:

```text
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
- no heuristic ID/name mapping;
- footprint/floor/position/house presence evidence separated from unproven object-ID parity;
- mismatches are review findings only;
- no mutation, pathfinding or geometry recomputation.

## TCR-006 — Global Content Registry Correlation

Planned public format:

```text
canary-tibia-content-reference-correlation-v1
```

Acceptance:

- monster, boss, quest and achievement registry records remain distinct;
- existing creature/spawn/quest/achievement evidence is consumed, not rebuilt;
- missing Canary evidence is not automatically classified as a defect without the relevant module proof;
- dynamic/unresolved source behavior remains unresolved.

## TCR-007 — Proficiency Reference Correlation

Planned public format:

```text
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

This proves the integration architecture before broader content correlation or any repair proposal.

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

# Last completed task

- Task: `docs/agents/tasks/archive/CAN-20260723-tcr-002-staticdata-reference-index.md`
- PR: `#827` — merged.
- Merge commit: `24d106b5eea40371833ce20de96184b55cd9b661`.
- Scope: TCR-002 exact manifest-bound StaticData registry/reference producer only; no StaticMapData/proficiency parser, no gameplay/runtime parity claim and no map/runtime mutation.

# Blockers and unresolved references

- Exact client build identity for future user-supplied files is package-specific and must be proven or recorded unknown.
- Staticmap `object_id` -> OTBM/server item ID equivalence is not proven by this programme and is deliberately blocked until a dedicated resolver is evidenced.
- The proficiency filename/location is not standardized in this architecture; implementation must use explicit file selection.
- New client schemas beyond the independently verified old/new staticdata families require a new bounded schema-discovery task.
- Direct source-code reuse from the research repository is blocked by licensing review; independent implementation is the default.

# Exact next action after TCR-002

TCR-002 is merged. After this lifecycle/discovery closure lands, perform a fresh ownership/PR/reuse preflight and start **only TCR-003 — StaticMapData House Index** if it remains the first unowned, unblocked, dependency-satisfied queue item.

Do not start TCR-004 or TCR-005 in the TCR-003 task or PR.

# Handoff

A continuation agent must:

1. read root `AGENTS.md`, `REPOSITORY_MAP.md`, `CONTEXT_ROUTING.md`;
2. route `otbm` + `real-tibia-parity` + `agent-governance`;
3. read this programme and `OTBM_TIBIA_CLIENT_REFERENCE_ARCHITECTURE.md`;
4. re-fetch current `main`, active tasks and open PRs;
5. search `MODULE_CATALOG.md` and current OTBM/client-reference paths for an equivalent implementation;
6. select exactly one still-planned queue item;
7. create one active task, branch and early draft PR;
8. keep user-supplied client files outside Git;
9. preserve `UNKNOWN` rather than guessing client build, item ID mappings or gameplay semantics;
10. use existing OTBM/QA/repair/E2E owners instead of creating duplicates;
11. treat `canary-tibia-client-reference-manifest-v1` and `canary-tibia-staticdata-index-v1` as stable/merged only within their exact provenance/reference boundaries; do not upgrade planned StaticMapData, proficiency, parity/correlation or drift contracts to stable without their own merged packages.

# Agent kickoff prompt

```text
Continue the OTBM Tibia Client Reference Programme from repository state.
Repository writes are allowed only in blakinio/canary.
Do not rely on previous chat history.

PROGRAM: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
RECOMMENDED_MODE: CHAT for preflight/planning/PR/CI; escalate to CODEX only when a bounded local implementation/test loop becomes necessary.
CONTEXT_ROUTES: agent-governance, otbm, real-tibia-parity

REQUIRED_READS:
- AGENTS.md
- docs/agents/REPOSITORY_MAP.md
- docs/agents/CONTEXT_ROUTING.md
- docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md
- docs/agents/REAL_TIBIA_PARITY_PLAYBOOK.md
- docs/agents/programs/REAL_TIBIA_PARITY_PROGRAM.md
- docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md
- docs/ai-agent/OTBM_TIBIA_CLIENT_REFERENCE_ARCHITECTURE.md
- docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md

SEARCH_FIRST:
- current main and open PRs/active tasks overlapping OTBM/client-reference paths;
- docs/agents/MODULE_CATALOG.md for existing canonical interfaces;
- tools/ai-agent for any already-delivered equivalent of the selected TCR package;
- docs/agents/real-tibia/registry/modules/otbm-tooling.yaml.

EXTERNAL RESEARCH BASELINE:
- beats-dh/Beats-Assets-Editor@ed827be34c279d1279ad3dde3af434b148ac05c7 is read-only research/format evidence only.
- Do not copy its source code into Canary.
- User-supplied Tibia client files are untrusted external inputs and must remain outside Git.

NON-NEGOTIABLE REUSE:
- no second OTBM parser/scanner/World Index;
- no second appearances/assets canonical index;
- no second Script Resolution engine;
- no second pathfinder or factual renderer;
- no second mutation/finalization pipeline;
- no second Physical E2E platform.

SAFETY:
- never commit .otbm, .widx, items.otb, Tibia client binaries/assets or extracted proprietary archives;
- pin exact SHA-256 for every selected external input;
- do not infer a client build from filenames;
- do not equate staticmapdata.object_id with OTBM/server itemId without explicit proven mapping;
- staticmapdata is house-layout reference evidence, not a full OTBM source;
- minimap evidence never overrides canonical World Index/Reachability mechanics evidence;
- unresolved/ambiguous/conflicting evidence stays explicit;
- no finding authorizes mutation by itself.

TASK SELECTION:
1. Revalidate the programme queue against current repository state.
2. Select exactly one still-valid package.
3. The next candidate is TCR-003 StaticMapData House Index only if it remains unowned, unblocked and dependency-satisfied.
4. Create a fresh active task, branch and early draft PR before substantial implementation.
5. Implement only that bounded package with deterministic tests and exact provenance.
6. Update the task checkpoint after material discoveries and before handoff.
7. Do not silently continue into TCR-004 or another TCR package in the same PR.

TCR-003 TARGET CONTRACT:
- canary-tibia-staticmapdata-index-v1;
- consume exact stable `canary-tibia-client-reference-manifest-v1` provenance;
- require one explicit selected StaticMapData input and exact source hash binding;
- preserve house IDs, layout origin, dimensions, floors, rows and tile records deterministically;
- fail closed on malformed dimensions/row shapes and bounded compressed-input violations;
- keep `staticmapdata.object_id` in its own unresolved namespace unless an exact mapping is proven;
- no OTBM parsing/writing, no gameplay conclusions, no runtime mutation and no proprietary client data in Git.

Before implementation, prove that no equivalent canonical StaticMapData index already exists and that no active task/PR owns TCR-003. If one exists, stop duplication and update the programme with the reuse/ownership decision instead.
```
