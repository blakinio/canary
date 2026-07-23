# OTBM World Quality, Repair and Certification Roadmap

> Repository: `blakinio/canary`  
> Successor context: completed `OTS-OTBM-VALIDATION` phases 1–8 and completed `CAN-PROGRAM-OTBM-E2E-ROUTING` / OTBM-E2E-001..009  
> Status: complete / OTBM-QA-001..018 delivered and lifecycle-closed
> Evidence rule: static evidence, candidate validation and Physical E2E are distinct proof levels

## Mission

Move the delivered OTBM stack from a collection of powerful bounded tools into one continuous world-assurance model that can answer, without inventing evidence:

- what is structurally or semantically unhealthy in the current map;
- what changed between two exact map snapshots;
- what exact mechanics, routes, quest chains, regions and downstream validation consumers are affected;
- whether a reviewed repair can be expressed through an already-approved bounded mutation path;
- whether a candidate map passes static quality, provenance and impacted Physical E2E checks;
- which regions or quests are statically clean, source-correlated, reachable and physically proven;
- where the world contains dead/orphaned content, fragile connectivity, impossible state progression, identifier conflicts or stale certification;
- how downstream agents can query compact exact OTBM evidence without duplicating OTBM logic or taking ownership away from their own subsystem.

This roadmap does **not** reopen the completed OTBM validation or OTBM-E2E route programmes. Every future package starts as a new bounded task from then-current `main` and composes already-delivered contracts.

## Delivered baseline to reuse

The successor roadmap assumes the following capabilities already exist and remain canonical:

| Capability | Delivered boundary |
|---|---|
| Unified OTBM World Index | exact tiles, stacks, item IDs, AID, UID, house doors, teleports and map/index provenance |
| Item/Mechanic Audit | exact placements and mechanic identifiers on the indexed map |
| Quest Map Validator | bounded source-to-map correlation for quest mechanics and storages |
| Script Resolution | conservative AID/UID/item/position handler correlation; unresolved/conflicting stays blocked |
| Reachability | canonical and only OTBM pathfinder/BFS with reviewed transitions |
| Spawn/NPC validation | active-datapack creature/NPC placement and bounded geometry correlation |
| Storage dependency graph | conservative selected-source prerequisite/result evidence |
| Semantic OTBM Diff | exact tile/item/mechanic/walkability before/after findings with stable IDs |
| Geometry Audit | bounded structural and reviewed adjacency evidence |
| Map Quality Gate | fail-closed aggregation of compatible geometry, reachability and Script Resolution evidence |
| Repair preflight | exact reviewed repair-target correlation and review-only bounded patch planning |
| Repair sandbox and materializers | create-new bounded attribute/tile-area/raw-tile mutation paths with confinement proof |
| Repair/materialization pipeline | one approved mutation mode per run, candidate revalidation and create-new publication |
| Semantic Landmark Registry | reviewed semantic names bound to exact map/index provenance and route anchors |
| Route Interaction Registry | reviewed exact mechanic/transition selectors bound to supported physical activation semantics |
| OTBM-E2E-001..007 | executable routes, landmarks, interactions, exact-map preflight, physical route proof, triage and coverage matrix |
| OTBM-E2E-008 | Semantic Diff impacted Physical E2E selection |
| OTBM-E2E-009 | approved candidate-map validation with selected Physical E2E and exact candidate provenance |

## Non-negotiable architecture rules

1. No second OTBM parser, scanner, World Index, Script Resolution implementation, pathfinder, factual renderer, mutation engine, E2E runner or workflow.
2. `unresolved`, `partially-resolved`, `referenced-only`, `conflicting`, stale, truncated, ambiguous or missing-provenance evidence fails closed whenever the claim depends on it.
3. Source maps are immutable inputs. Mutation happens only on distinct candidate copies through already-approved bounded paths.
4. Recommendation, human/review approval, candidate mutation, static candidate validation and Physical E2E proof are separate stages.
5. A green static gate does not prove gameplay correctness. A successful route does not prove an unrelated mechanic. A Semantic Diff non-impact decision applies only to represented OTBM-aware scenarios.
6. Generated `.otbm`, `.widx`, client assets, reports and renders remain external artifacts and are never committed.
7. Factual map imagery uses the existing renderer and compatible real assets only. AI-generated map imagery is not evidence.
8. New analysis layers consume existing canonical reports/indexes where possible instead of rescanning or copying classifier logic.
9. Downstream-agent support is evidence-only: OTBM may expose exact compact context, but subsystem-specific scenario design, runtime execution and acceptance decisions remain with the subsystem owner.

# Successor work packages

The identifiers below define roadmap packages, not authorization to implement them. Each package requires a fresh active task, ownership audit and draft PR.

## OTBM-QA-001 — World Health Aggregator

**Goal:** produce one deterministic read-only health model over compatible existing reports without rescanning or reinterpreting the map.

### Inputs

As applicable and exact-provenance compatible:

- World Index summary;
- Item/Mechanic Audit;
- Quest Map Validation;
- Script Resolution;
- Reachability;
- Spawn/NPC validation;
- Storage dependency graph;
- Geometry Audit;
- Map Quality Gate;
- OTBM-E2E coverage matrix.

### Outputs

A versioned world-health report with explicit dimensions rather than one opaque pass/fail number:

- structural findings;
- unresolved/conflicting runtime-handler evidence;
- unreachable/conditional mechanics;
- stale evidence;
- missing Physical E2E coverage;
- exact bounded samples and exact totals;
- provenance for every contributing report.

### Acceptance boundary

The aggregator may summarize and correlate exact compatible evidence. It must not deduplicate distinct findings into an invented defect, infer player intent, or treat selected-scope absence as global absence.

A convenience health percentage or score may be derived for presentation, but it must expose its deterministic inputs and must never replace explicit evidence dimensions or become the sole merge/certification gate.

## OTBM-QA-002 — Map Change Regression Guard

**Goal:** turn an exact reviewed map change into a deterministic impacted-validation plan.

### Flow

```text
before map + after/candidate map
  -> canonical World Indexes
  -> Semantic OTBM Diff
  -> impacted positions/mechanics/regions
  -> impacted static validators
  -> OTBM-E2E-008 impacted Physical E2E selection
  -> selected checks only when non-impact is proven fail-closed
```

### Required behavior

- bounded/truncated/stale/missing evidence selects more validation rather than less;
- unrelated non-OTBM suites are never suppressed by OTBM non-impact evidence;
- every skipped OTBM-aware scenario records the exact non-impact evidence that authorized the skip;
- every selected scenario retains exact Semantic Diff finding IDs;
- safe map refactoring may reuse this guard, but non-impact is never inferred from visual similarity or intent.

## OTBM-QA-003 — Repair Recommendation Orchestrator

**Goal:** generate reviewable repair recommendations from exact findings without mutating a map.

### Flow

```text
health/regression finding
  -> exact selector and evidence bundle
  -> existing repair preflight
  -> supported existing mutation mode?
  -> review recommendation
```

### Recommendation states

- `no-repair-evidence`;
- `review-required`;
- `supported-by-existing-attribute-path`;
- `supported-by-existing-tile-area-path`;
- `supported-by-existing-raw-tile-path`;
- `unsupported-mutation-shape`;
- `blocked-by-runtime-evidence`;
- `ambiguous-target`.

The orchestrator never invents an AID, UID, item, teleport destination, tile, stack order or coordinate. It does not execute a writer.

## OTBM-QA-004 — Reviewed Candidate Repair Orchestration

**Goal:** compose review approval with the existing repair/materialization pipeline and existing OTBM-E2E-009 candidate validation.

### Flow

```text
reviewed recommendation
  -> explicit approval pinned to exact source and expected old state
  -> one existing bounded mutation mode
  -> create-new candidate
  -> full native reparse + World Index
  -> Semantic OTBM Diff
  -> compatible Map Quality evidence
  -> OTBM-E2E-008 impacted scenario selection
  -> OTBM-E2E-009 selected Physical E2E
  -> candidate evidence bundle
```

### Hard rule

This package adds orchestration only. It must not broaden any writer/materializer. Unsupported mutation shapes stay unsupported. Automatic unreviewed map repair remains out of scope.

## OTBM-QA-005 — Coverage Dashboard and Certification Model

**Goal:** expose factual coverage and certification state for the full world, a region, landmark route, quest or selected mechanic set.

### Evidence dimensions

For each reviewed target, retain independent states such as:

- indexed on exact map;
- source-correlated;
- script-resolved;
- statically reachable;
- interaction-resolved;
- static quality compatible;
- covered by an executable route;
- physically runtime-proven;
- candidate-map validated;
- stale against current map.

A dashboard may calculate convenience percentages or an explicitly derived quality score, but gates and certification decisions must use explicit evidence dimensions and blockers rather than one opaque score.

The same evidence may expose **coverage gaps** such as a mechanic that is indexed, source-correlated, script-resolved and reachable but has no current physical proof. This is evidence for downstream owners; it is not an instruction to create or prioritize a specific E2E scenario.

## OTBM-QA-006 — Region and Quest Certification

**Goal:** certify bounded, explicitly defined targets against exact map provenance.

### Candidate certification levels

```text
C0 NOT_EVALUATED
C1 STATIC_INDEXED
C2 STATIC_CORRELATED
C3 STATIC_REACHABLE
C4 STATIC_QUALITY_GREEN
C5 PHYSICAL_ROUTE_PROVEN
C6 FEATURE_OR_MECHANIC_PHYSICALLY_PROVEN
C7 CANDIDATE_CHANGE_REVALIDATED
```

A target receives only the strongest level for which all required lower-level evidence is exact, current and non-blocking. Certification is invalidated or marked stale when relevant map/source/evidence provenance changes.

Examples of bounded certification targets:

- `thais.city`;
- `thais.temple -> thais.depot`;
- one reviewed quest chain;
- one teleport network;
- one dungeon/region;
- a reviewed set of critical house doors or transitions.

## OTBM-QA-007 — Continuous World Assurance Gate

**Goal:** provide a release/merge-oriented orchestration layer over already-proven contracts.

### Intended behavior

For a relevant map PR or approved candidate:

1. pin exact before/after/candidate provenance;
2. run Semantic Diff;
3. select impacted static validators and OTBM-aware Physical E2E through existing contracts;
4. aggregate resulting world-health deltas;
5. fail closed on new errors, unresolved/conflicting evidence according to explicit policy, stale provenance or failed selected Physical E2E;
6. emit an auditable certification delta.

This is a gate/orchestration layer, not a replacement for the individual validators.

# Advanced analysis packages

## OTBM-QA-008 — Mechanic Dependency and Blast Radius Graph

**Goal:** build a deterministic dependency overlay that explains what exact map/mechanic evidence depends on a changed node and what may be impacted downstream.

### Candidate node types

- exact tile/item placement;
- item ID, AID, UID and house-door selector;
- teleport source/destination;
- reviewed transition ID;
- Script Resolution handler evidence;
- storage key/operation evidence;
- landmark/region anchor;
- executable route/interaction reference;
- quest/mechanic target;
- OTBM-aware coverage target or existing scenario reference.

### Edge policy

Edges require explicit compatible evidence. Source proximity, similar names, visual proximity and chat memory do not create dependency edges.

### Outputs

- direct dependencies;
- transitive impacted targets where every edge is proven;
- unresolved/ambiguous dependency boundaries;
- exact evidence paths explaining why a target is considered impacted;
- bounded blast-radius summaries suitable for OTBM-QA-002 and OTBM-QA-017.

The graph is an analysis overlay. It does not become a second Script Resolution engine, storage graph, route planner or E2E selector.

## OTBM-QA-009 — Dead/Orphaned Content and Quest Completeness Audit

**Goal:** identify content that appears disconnected from a complete evidence chain and summarize quest/mechanic completeness conservatively.

### Candidate findings

- map AID/UID/mechanic placement with no resolved active handler;
- active literal handler/selector with no correlated placement in selected scope;
- teleport/transition target that is statically unreachable from its reviewed entry context;
- NPC/spawn/boss placement that is disconnected from a reviewed access context;
- quest stage reference with no selected-scope producer or consumer evidence;
- reviewed quest entry with missing evidence for a required door/lever/teleport/boss/reward/exit stage;
- mechanic that is statically represented but has no route/interaction evidence required by the declared completeness target.

### Quest completeness view

For one explicitly selected quest, the audit may correlate evidence for:

```text
entry
-> NPC/source trigger
-> storage prerequisites/results
-> AID/UID/item mechanics
-> doors/levers/passages
-> teleports/floor transitions
-> boss/spawn evidence
-> reward/chest evidence
-> exit/return path
```

Classification remains evidence-based: `confirmed`, `map-only`, `script-only`, `unresolved`, `conflicting`, `not-applicable` or another existing compatible state. The audit does not execute Lua and does not claim that a player can complete the quest at runtime.

## OTBM-QA-010 — Quest State Reachability

**Goal:** derive a conservative state-transition view for selected quest/mechanic scopes by composing existing storage dependency evidence with exact map and interaction prerequisites.

### Intended model

```text
known state prerequisite
  + exact resolved mechanic/interaction evidence
  -> proven literal/same-key state transition
  -> newly reachable static state
```

### Safety boundary

- reuse the existing Storage Dependency Graph rather than infer execution order independently;
- dynamic storage keys/values and dynamic Lua remain unresolved;
- inequalities, `else` assumptions and nearby source operations do not create exact transitions;
- route availability may be correlated to a state only when the required state-to-mechanic relationship is explicit;
- absence of a selected-scope producer means `external-or-unproven`, not impossible globally.

The output may identify a **potentially unreachable quest state** when the selected evidence proves no valid predecessor path, but this remains static evidence rather than runtime gameplay proof.

## OTBM-QA-011 — Connectivity Resilience, Route Fragility, Entrapment and Teleport Networks

**Goal:** analyze how robust world connectivity is without creating another pathfinder.

### Reuse

All path and connectivity calculations must reuse the existing Reachability graph/BFS and reviewed transition model.

### Capabilities

- route fragility analysis for reviewed start/goal pairs;
- identification of critical crossings or transition edges whose removal disconnects a reviewed route/region;
- alternative-route resilience where multiple independent paths can be proven;
- disconnected or weakly connected reviewed regions/components;
- one-way transition and teleport-network topology;
- teleport dead ends, cycles, suspicious destinations and changed destinations;
- static escape/entrapment candidates where a reviewed entry exists but no reviewed exit path can be proven;
- detection of regions reachable only through unresolved or unsupported transitions.

### Caveat

A static entrapment finding may be resolved by runtime state, scripts or mechanics outside selected evidence. Such cases remain review candidates unless exact evidence closes the gap.

## OTBM-QA-012 — Critical Infrastructure, House and Spawn Access Integrity

**Goal:** provide targeted integrity checks for high-value world access points without guessing semantic importance.

### Critical Infrastructure Registry

A reviewed registry may identify exact targets such as:

- temples/recovery points;
- depots;
- banks;
- ships/transport hubs;
- city entrances;
- quest hubs;
- other explicitly reviewed operationally critical landmarks.

Criticality is review metadata tied to exact landmark/map provenance, not inferred from item names or map appearance.

### House integrity

Candidate checks include:

- house tile/component connectivity;
- exact house-door ID evidence;
- reviewed entrance-to-house connectivity;
- mixed or suspicious PZ evidence already supported by canonical geometry semantics;
- missing/ambiguous house-door selectors;
- changes that appear to bypass or sever a reviewed house entrance.

### Spawn/NPC/boss access integrity

Correlate existing Spawn/NPC validation with reviewed entry/region reachability to identify placements that are statically inaccessible from their declared access context. This does not prove intended public accessibility unless the target explicitly declares it.

## OTBM-QA-013 — Identifier, Selector and Collision Integrity

**Goal:** provide a global or bounded inventory of identifier/selector ambiguity that may cause mechanics to resolve incorrectly.

### Candidate checks

- duplicate UID definitions/placements where uniqueness is required;
- AID reuse correlated to incompatible resolved handlers or incompatible reviewed mechanic roles;
- house-door ID conflicts under explicit house/door semantics;
- conflicting exact route-interaction selectors;
- duplicate reviewed transition IDs or incompatible source/destination definitions;
- selector combinations that resolve ambiguously to multiple placements or handlers.

Repeated AIDs or item IDs are not automatically defects. Findings must distinguish intentional reusable selectors from evidence-backed conflicts.

## OTBM-QA-014 — Asset and Appearance Compatibility Audit

**Goal:** detect when the exact OTBM map remains unchanged but its interpreted semantics may change because item/appearance/client-asset evidence changed.

### Candidate checks

- OTBM item IDs missing required canonical item/appearance evidence;
- missing or incompatible appearance records;
- referenced sprites/assets absent from the compatible asset set;
- appearance-flag changes that alter canonical walkability classification;
- ground/static-blocker/conditional-blocker/unknown-appearance classification deltas caused by asset updates;
- route/quality/certification evidence made stale by changed appearance provenance.

This audit reuses canonical appearances and renderer inputs. It does not rewrite `items.otb`, client assets or OTBM.

## OTBM-QA-015 — Static Map Performance Hotspot Analyzer

**Goal:** identify regions whose static OTBM structure deserves targeted runtime performance investigation.

### Candidate evidence

- unusually high item-stack depth or item count per tile;
- dense decorated regions;
- high concentrations of teleports/mechanics/transitions;
- dense spawn/NPC correlation where compatible evidence exists;
- unusually large connected structural regions or local node density;
- before/after hotspot deltas from Semantic Diff.

The analyzer reports **static hotspot candidates only**. It must not claim CPU, memory, network or client-render performance impact without runtime profiling owned by the appropriate subsystem.

# Lifecycle, release and risk packages

## OTBM-QA-016 — Release Provenance, Upgrade Compatibility, Quality History and Certification Freshness

**Goal:** make every reviewed map baseline and upgrade reproducible and explain exactly which evidence becomes stale after change.

### Release / Map Bill of Materials

A release manifest should pin, as applicable:

```text
map SHA-256
World Index SHA/provenance
scanner/tool revision
items/appearances provenance
selected datapack/source evidence
Script Resolution evidence
transition manifest
landmark registry
interaction registry
quality evidence
coverage/certification evidence
```

### Map upgrade compatibility

For `old.otbm -> new.otbm`, correlate Semantic Diff and dependent evidence to identify:

- removed/changed AID, UID and house-door placements;
- teleport destination changes;
- invalidated landmarks/regions;
- changed route/transition/interaction evidence;
- affected quest/mechanic completeness targets;
- stale coverage/certification dimensions;
- impacted OTBM-aware scenario references exposed by existing OTBM-E2E-008.

### Quality history

Retain comparable exact-provenance snapshots of health/certification dimensions over time so regressions and improvements are visible without treating upload/modified timestamps as evidence of map freshness.

### Certification freshness

Any relevant map, source, handler, appearance, transition, landmark, interaction or runtime-proof provenance change invalidates or marks stale only the certification dimensions that depend on it. Certification does not remain permanently valid after its dependencies change.

## OTBM-QA-017 — Deterministic Change Risk Classification

**Goal:** provide a transparent review aid that classifies the potential scope of an exact OTBM change without replacing evidence-based gates.

### Candidate factors

- touches reviewed critical infrastructure;
- changes AID/UID/house-door/teleport semantics;
- affects a quest/mechanic dependency path;
- changes a critical/fragile route or only known crossing;
- invalidates current certification;
- affects multiple regions or downstream coverage targets;
- has unresolved/conflicting dependency evidence;
- changes asset-driven walkability semantics.

Risk levels such as `low`, `medium`, `high`, `critical` must be derived from an explicit versioned policy with visible contributing factors. No opaque AI score may authorize a safe skip, repair or merge.

# Downstream-agent support package

## OTBM-QA-018 — Compact OTBM Evidence Gateway

**Goal:** make the OTBM stack easier for other agents, especially Universal E2E consumers, to use without transferring subsystem ownership to OTBM.

This package is a read-only/query and evidence-composition boundary over existing canonical contracts. It does not create another parser, validator, route planner or E2E tool.

### Candidate query surfaces

A stable interface may expose operations conceptually equivalent to:

```text
resolve_position
resolve_mechanic
resolve_transition
resolve_landmark
resolve_route_evidence
resolve_impact
resolve_health
resolve_coverage_gap
resolve_static_failure_context
```

Exact public names and formats require a separate implementation task and MODULE_CATALOG review.

### Compact evidence pack

For one selected target, the gateway may compose only compatible exact evidence such as:

- source map and World Index provenance;
- exact `x,y,z`;
- item ID, AID, UID, house-door ID and teleport destination where present;
- Script Resolution state and exact sources/handlers where resolved;
- reachability/transition evidence;
- existing semantic landmark and route-interaction evidence;
- existing executable route/preflight references where applicable;
- current health/certification/coverage dimensions;
- exact blockers and unresolved/conflicting states.

The purpose is to reduce downstream agent context usage and avoid forcing an E2E or feature agent to manually open many OTBM reports.

### Help provided to Universal E2E and E2E agents

OTBM may provide:

- exact evidence bundles for a requested position/mechanic/transition/landmark;
- existing route-plan and route-preflight artifacts;
- exact impacted positions/mechanics/routes/interaction IDs;
- existing OTBM-E2E-008 impacted-scenario selection artifacts, without redefining scenario ownership;
- coverage-gap evidence such as `static evidence present + reachable + no current physical proof`;
- bounded static reproducer context: exact region, relevant tiles, mechanics, transitions and correlated source evidence;
- static correlation for a runtime-reported position, transition ID or interaction ID;
- provenance information proving whether the E2E runtime map matches the evidence baseline.

### Hard ownership boundary

OTBM-QA-018 must **not**:

- generate or own Universal E2E scenario manifests;
- generate feature-specific expected outcomes or assertions;
- decide account, character, storage or runtime fixtures;
- control Canary/MariaDB/OTClient lifecycle;
- execute, replay or retry Physical E2E;
- create a second E2E runner or workflow;
- become a general runtime failure investigator beyond returning OTBM-owned static correlation and existing route-triage evidence;
- generate `NEXT_ACTION` for the E2E agent;
- own E2E backlog prioritization merely because a coverage gap exists;
- promote static evidence to runtime success.

Universal E2E remains responsible for scenario definitions, feature-owned fixtures, runtime actions/assertions, execution lifecycle, persistence/relog proof and runtime artifacts. OTBM helps by making exact map evidence cheap and reliable to consume.

# Cross-cutting use cases

The packages above support the following previously discussed directions without creating additional parallel infrastructure:

## Safe map refactoring

```text
Semantic Diff
-> blast radius / criticality
-> regression guard
-> reviewed repair/materialization when applicable
-> candidate validation
-> selected Physical E2E through existing contracts
-> certification delta
```

## World-wide quest/mechanic health

```text
World Health
+ dependency graph
+ dead/orphaned audit
+ quest completeness
+ quest-state reachability
+ connectivity resilience
-> factual health and coverage inventory
```

## Region/quest certification

```text
exact target definition
-> indexed/correlated/reachable/quality evidence
-> route/physical evidence when required
-> current certification
-> automatic stale marking on dependency change
```

## Map upgrade review

```text
old release manifest + new candidate
-> Semantic Diff
-> asset compatibility
-> dependency blast radius
-> upgrade compatibility
-> deterministic change risk
-> impacted validation evidence
```

## E2E-agent assistance without E2E ownership

```text
E2E/feature agent asks for map context
-> OTBM Evidence Gateway
-> compact exact evidence + blockers + provenance
-> downstream agent keeps ownership of scenario/runtime decisions
```

# Programme closure reconciliation — 2026-07-23

> Delivery status: **COMPLETE — OTBM-QA-001..018 delivered**
>
> This closes the consolidated successor roadmap as a tooling/governance programme. It does **not** certify that an arbitrary or current world is globally healthy or gameplay-correct. Every health, regression, certification, repair, risk and evidence claim still requires the exact compatible inputs and proof level required by its own contract.

## Delivery ledger

| Package | Delivered feature PR | Lifecycle closure PR | Durable capability |
|---|---:|---:|---|
| OTBM-QA-001 | #672 | #678 | World Health Aggregator |
| OTBM-QA-002 | #679 | #680 | Map Change Regression Guard |
| OTBM-QA-003 | #681 | #682 | Repair Recommendation Orchestrator |
| OTBM-QA-004 | #684 | #686 | Reviewed Candidate Repair Orchestration |
| OTBM-QA-005 | #688 | #689 | Coverage Dashboard |
| OTBM-QA-006 | #759 | #767 | Region and Quest Certification |
| OTBM-QA-007 | #759 | #767 | Continuous World Assurance Gate |
| OTBM-QA-008 | #694 | #698 | Dependency and Blast-Radius Graph |
| OTBM-QA-009 | #700 | #704 | Dead/Orphaned Content and Completeness Audit |
| OTBM-QA-010 | #709 | #710 | Quest State Reachability |
| OTBM-QA-011 | #713 | #716 | Connectivity Resilience |
| OTBM-QA-012 | #717 | #721 | Critical Access Integrity |
| OTBM-QA-013 | #724 | #731 | Identifier and Selector Integrity |
| OTBM-QA-014 | #734 | #752 | Asset and Appearance Compatibility |
| OTBM-QA-015 | #735 | #752 | Static Map Performance Hotspots |
| OTBM-QA-016 | #737 | #752 | Release Provenance and Certification Freshness |
| OTBM-QA-017 | #739 | #752 | Deterministic Change Risk |
| OTBM-QA-018 | #741 | #752 | Compact Evidence Gateway |

Shared public-interface governance for QA-014..018 was reconciled in #743. QA-006/007 shared catalogue/changelog registration was reconciled in #768. Closure PR #773 also restores the previously missing shared discovery entries for QA-008 and QA-009.

## Completion-definition reconciliation

The sixteen programme completion conditions are satisfied by the delivered contracts as follows:

1. Deterministic current-world health composition: QA-001.
2. Fail-closed impacted static and represented Physical E2E selection for exact map changes: QA-002.
3. Explicit proven dependency/blast-radius paths without invented edges: QA-008.
4. Conservative dead/orphaned-content and selected quest/mechanic completeness auditing: QA-009.
5. Selected quest-state reachability without dynamic Lua execution: QA-010.
6. Connectivity fragility, reviewed transition/teleport topology and static entrapment candidates through the canonical Reachability graph: QA-011.
7. Bounded critical-access, identifier, asset/appearance and static-hotspot evidence: QA-012..015.
8. Reviewable repair recommendations without automatic mutation: QA-003.
9. Reviewed candidate repair orchestration restricted to existing approved bounded mutation contracts: QA-004.
10. Candidate evidence chains retain native reparse/reindex, Semantic Diff, quality and impacted Physical E2E boundaries through QA-004 and the existing OTBM-E2E candidate-validation stack.
11. Exact release BOM/provenance, upgrade comparison and dependency-scoped certification freshness: QA-016.
12. Explicit target coverage dimensions and bounded C0-C7 certification with stale-state handling: QA-005/006.
13. Transparent evidence-derived change-risk classification: QA-017.
14. Compact exact downstream evidence without transferring E2E/feature ownership: QA-018.
15. Exact provenance and source-map immutability remain mandatory across the programme.
16. The programme reuses the canonical World Index, Script Resolution, Reachability, Semantic Diff, renderer, bounded mutation pipeline and Universal Physical E2E; it introduces no parallel parser/pathfinder/writer/renderer/E2E stack.

## Closure boundary

Future work may consume or extend these stable contracts through new bounded tasks, but it does not reopen OTBM-QA-001..018. New Real Tibia/client-reference, parity, content-reconstruction or feature-runtime programmes remain separate ownership domains and must preserve the reuse and proof-level rules above.

# Proposal-to-package inventory

This table preserves the OTBM-focused proposals raised during the design discussion and shows where they belong.

| Proposal | Roadmap home |
|---|---|
| automatic bounded repair after evidence/review | OTBM-QA-003 / 004 |
| world-wide health audit | OTBM-QA-001 |
| map regression protection | OTBM-QA-002 / 007 |
| safe map refactoring | OTBM-QA-002 / 004 / 007 / 016 |
| repair suggestions with exact coordinates/IDs/evidence | OTBM-QA-003 |
| coverage dashboard / full-world coverage | OTBM-QA-005 |
| derived map quality score | OTBM-QA-005, presentation only |
| region/quest certification | OTBM-QA-006 |
| mechanic dependency graph | OTBM-QA-008 |
| blast-radius analyzer | OTBM-QA-008 |
| dead/orphaned content detector | OTBM-QA-009 |
| quest completeness analyzer | OTBM-QA-009 |
| diagnosis of why a quest may be statically incomplete | OTBM-QA-009 / 010 / 011 |
| quest state reachability | OTBM-QA-010 |
| route fragility / alternative-route resilience | OTBM-QA-011 |
| teleport network audit | OTBM-QA-011 |
| region connectivity analysis | OTBM-QA-011 |
| escape/entrapment detector | OTBM-QA-011 |
| critical infrastructure registry | OTBM-QA-012 |
| house integrity audit | OTBM-QA-012 |
| spawn/NPC/boss accessibility audit | OTBM-QA-012 |
| duplicate/collision detector for identifiers/selectors | OTBM-QA-013 |
| asset/appearance-to-OTBM consistency | OTBM-QA-014 |
| map performance hotspot candidates | OTBM-QA-015 |
| release manifest / map bill of materials | OTBM-QA-016 |
| old-map to new-map compatibility checker | OTBM-QA-016 |
| historical quality tracking | OTBM-QA-016 |
| certification expiry/stale propagation | OTBM-QA-016 |
| transparent change risk score/classification | OTBM-QA-017 |
| E2E-ready compact OTBM evidence pack | OTBM-QA-018 |
| impacted mechanics/routes/landmarks for downstream test consumers | OTBM-QA-018, reusing OTBM-QA-002/008 and OTBM-E2E-008 |
| mechanic evidence resolver | OTBM-QA-018 |
| coverage-gap evidence for E2E owners | OTBM-QA-005 / 018 |
| minimal static reproducer context | OTBM-QA-018 |
| static OTBM correlation for E2E-reported failures | OTBM-QA-018 |
| stable read-only OTBM query API for agents | OTBM-QA-018 |

The earlier ideas of automatic E2E scenario generation, E2E scenario skeleton generation, E2E replay, general runtime failure investigation and automatic E2E `NEXT_ACTION` are deliberately **not** part of the OTBM roadmap because they belong to Universal E2E or feature-programme ownership. OTBM-QA-018 supplies evidence to those owners instead.

# Dependency order

```text
Delivered OTBM stack + OTBM-E2E-001..009
        |
        +---------------------------+
        |                           |
        v                           v
OTBM-QA-001 World Health      OTBM-QA-002 Regression Guard
        |                           |
        +-------------+-------------+
                      |
                      v
             OTBM-QA-008 Dependency Graph
                      |
        +-------------+----------------------------+
        |                    |                     |
        v                    v                     v
 OTBM-QA-009          OTBM-QA-011           OTBM-QA-012/013/014/015
 Dead/Quest           Connectivity           Domain/Asset/Hotspot
        |                    |                     |
        v                    |                     |
 OTBM-QA-010 Quest State     |                     |
        |                    |                     |
        +--------------------+---------------------+
                             |
                             v
                OTBM-QA-017 Change Risk
                             |
             +---------------+---------------+
             |                               |
             v                               v
 OTBM-QA-003 Repair Recommendations   OTBM-QA-016 Release/Upgrade/Freshness
             |                               |
             v                               |
 OTBM-QA-004 Candidate Repair                |
             |                               |
             +---------------+---------------+
                             |
                +------------+------------+
                |                         |
                v                         v
        OTBM-QA-005 Coverage       OTBM-QA-006 Certification
                |                         |
                +------------+------------+
                             |
                             v
                OTBM-QA-007 Continuous Gate
                             |
                             v
                OTBM-QA-018 Evidence Gateway
                (read-only downstream surface;
                 may also expose earlier stable evidence)
```

OTBM-QA-001 and OTBM-QA-002 may proceed independently when live ownership is disjoint. OTBM-QA-008 should compose their stable evidence. Domain-specific audits may proceed independently when they reuse canonical inputs and do not duplicate each other. OTBM-QA-018 may expose already-stable earlier contracts incrementally; it does not need to wait for every future package before providing useful compact evidence.

# Recommended implementation sequence

1. **OTBM-QA-001** — establish the unified, explicit world-health evidence model.
2. **OTBM-QA-002** — make map changes select the right static and represented Physical E2E checks fail-closed.
3. **OTBM-QA-008** — establish explicit dependency/blast-radius evidence for later diagnostics and risk classification.
4. **OTBM-QA-009** — add dead/orphaned-content and quest-completeness analysis.
5. **OTBM-QA-010** — add conservative quest-state reachability over existing storage evidence.
6. **OTBM-QA-011** — add route fragility, alternative-route, teleport-network and entrapment analysis using the same Reachability graph.
7. **OTBM-QA-012/013/014/015** — add critical-world, identifier, asset and static-hotspot integrity views as separate bounded tasks.
8. **OTBM-QA-017** — derive transparent change-risk classification from stable evidence.
9. **OTBM-QA-003/004** — turn exact findings into reviewable recommendations and approved create-new candidate orchestration.
10. **OTBM-QA-016** — establish release manifests, upgrade compatibility, historical quality and certification freshness.
11. **OTBM-QA-005/006** — expose factual coverage and certification for regions, quests and mechanics.
12. **OTBM-QA-007** — integrate mature evidence into the continuous assurance gate.
13. **OTBM-QA-018** — provide or progressively extend the compact downstream evidence gateway; it may start earlier for already-stable contracts when ownership is clean.

# Explicit non-goals

The successor roadmap does not authorize:

- automatic unreviewed map repair;
- in-place source/production map writes;
- production deployment;
- a generic/full-map serializer;
- non-zero coordinate translation in the canonical finalizer unless separately designed and approved;
- arbitrary item-stack editing;
- guessing missing identifiers or destinations;
- executing dynamic Lua in static analysis;
- AI-generated map imagery;
- replacing the existing World Index, Reachability BFS, Script Resolution, Semantic Diff, factual renderer, repair/materialization pipeline or Universal Physical E2E;
- treating static cleanliness as proof that gameplay works;
- treating static hotspot evidence as runtime performance proof;
- treating a duplicate AID/item ID as a defect without incompatible role/handler evidence;
- generating or owning Universal E2E scenarios, fixtures, runtime assertions or client/server lifecycle;
- a second Physical E2E runner/workflow;
- general E2E replay, retry, runtime-failure investigation or `NEXT_ACTION` generation under OTBM ownership.

# Completion definition for the consolidated successor programme

A future programme built from this roadmap should be considered complete only when:

1. current world health can be summarized deterministically from exact compatible evidence;
2. exact map changes select affected static and represented Physical E2E checks fail-closed;
3. dependency/blast-radius evidence explains downstream impact without invented edges;
4. dead/orphaned content and selected quest completeness can be audited conservatively;
5. selected quest-state reachability can be evaluated without executing dynamic Lua;
6. connectivity fragility, teleport networks and static entrapment candidates can be analyzed through the existing Reachability graph;
7. critical infrastructure, house/spawn access, identifier collisions, asset compatibility and static hotspot candidates have bounded evidence contracts;
8. repair recommendations are reviewable and never mutate automatically;
9. approved repairs use only existing or separately approved bounded mutation contracts;
10. candidate maps are reindexed, diffed, quality-checked and physically validated where impacted;
11. release manifests and upgrade compatibility preserve exact provenance and make stale certification explicit;
12. regions/quests/mechanics expose explicit current certification dimensions and stale state;
13. change risk is transparent and evidence-derived rather than opaque;
14. downstream agents can obtain compact exact OTBM evidence without duplicating OTBM tooling or transferring E2E/feature ownership to OTBM;
15. all orchestration preserves exact provenance and source-map immutability;
16. no parallel parser/pathfinder/writer/renderer/E2E stack has been introduced.
