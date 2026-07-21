# OTBM World Quality, Repair and Certification Roadmap

> Repository: `blakinio/canary`  
> Successor context: completed `OTS-OTBM-VALIDATION` phases 1–8 and completed `CAN-PROGRAM-OTBM-E2E-ROUTING` / OTBM-E2E-001..009  
> Status: planning / successor roadmap  
> Evidence rule: static evidence, candidate validation and Physical E2E are distinct proof levels

## Mission

Move the delivered OTBM stack from a collection of powerful bounded tools into one continuous world-assurance model that can answer, without inventing evidence:

- what is structurally or semantically unhealthy in the current map;
- what changed between two exact map snapshots;
- which mechanics, routes, regions and Physical E2E scenarios are impacted;
- whether a reviewed repair can be expressed through an already-approved bounded mutation path;
- whether a candidate map passes static quality, provenance and impacted Physical E2E checks;
- which regions or quests are statically clean, runtime-correlated, reachable and physically proven.

This roadmap does **not** reopen the completed OTBM validation or OTBM-E2E route programmes. Every future package starts as a new bounded task from then-current `main` and composes already-delivered contracts.

## Delivered baseline to reuse

The successor roadmap assumes the following capabilities already exist and remain canonical:

| Capability | Delivered boundary |
|---|---|
| Unified OTBM World Index | exact tiles, stacks, item IDs, AID, UID, house doors, teleports and map/index provenance |
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
| OTBM-E2E-001..007 | executable routes, landmarks, interactions, exact-map preflight, physical route proof, triage and coverage matrix |
| OTBM-E2E-008 | Semantic Diff impacted Physical E2E selection |
| OTBM-E2E-009 | approved candidate-map validation with selected Physical E2E and exact candidate provenance |

## Non-negotiable architecture rules

1. No second OTBM parser, scanner, World Index, Script Resolution implementation, pathfinder, factual renderer, mutation engine, E2E runner or workflow.
2. `unresolved`, `partially-resolved`, `referenced-only`, `conflicting`, stale, truncated, ambiguous or missing-provenance evidence fails closed.
3. Source maps are immutable inputs. Mutation happens only on distinct candidate copies through already-approved bounded paths.
4. Recommendation, human/review approval, candidate mutation, static candidate validation and Physical E2E proof are separate stages.
5. A green static gate does not prove gameplay correctness. A successful route does not prove an unrelated mechanic. A Semantic Diff non-impact decision applies only to represented OTBM-aware scenarios.
6. Generated `.otbm`, `.widx`, client assets, reports and renders remain external artifacts and are never committed.
7. Factual map imagery uses the existing renderer and compatible real assets only. AI-generated map imagery is not evidence.

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
- every selected scenario retains exact Semantic Diff finding IDs.

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

This package adds orchestration only. It must not broaden any writer/materializer. Unsupported mutation shapes stay unsupported.

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

A dashboard may calculate convenience percentages, but gates and certification decisions must use explicit evidence dimensions and blockers rather than a single score.

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
3. select impacted static validators and OTBM-aware Physical E2E;
4. aggregate resulting world-health deltas;
5. fail closed on new errors, unresolved/conflicting evidence according to explicit policy, stale provenance or failed selected Physical E2E;
6. emit an auditable certification delta.

This is a gate/orchestration layer, not a replacement for the individual validators.

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
          OTBM-QA-003 Repair Recommendations
                      |
                      v
          OTBM-QA-004 Candidate Repair Orchestration
                      |
        +-------------+-------------+
        |                           |
        v                           v
OTBM-QA-005 Coverage          OTBM-QA-006 Certification
        |                           |
        +-------------+-------------+
                      |
                      v
          OTBM-QA-007 Continuous Assurance Gate
```

OTBM-QA-001 and OTBM-QA-002 may proceed independently when live ownership is disjoint. OTBM-QA-003 should consume their stable evidence rather than copy their logic. OTBM-QA-004 depends on reviewed recommendation semantics and existing mutation/candidate-validation contracts. Dashboard/certification work may start with already-delivered evidence but must not claim complete world coverage before the required inputs exist.

# Recommended implementation sequence

1. **OTBM-QA-001** — establish the unified, explicit world-health evidence model.
2. **OTBM-QA-002** — make map changes automatically select the right static and Physical E2E checks.
3. **OTBM-QA-003** — turn exact findings into reviewable, non-mutating repair recommendations.
4. **OTBM-QA-004** — connect approved recommendations to the existing create-new candidate pipeline and OTBM-E2E-009.
5. **OTBM-QA-005/006** — expose factual coverage and certification for regions, quests and mechanics.
6. **OTBM-QA-007** — integrate the mature evidence chain into a continuous assurance gate.

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
- treating static cleanliness as proof that gameplay works.

# Completion definition for the successor programme

A future programme built from this roadmap should be considered complete only when:

1. current world health can be summarized deterministically from exact compatible evidence;
2. exact map changes select affected static and Physical E2E checks fail-closed;
3. repair recommendations are reviewable and never mutate automatically;
4. approved repairs use only existing or separately approved bounded mutation contracts;
5. candidate maps are reindexed, diffed, quality-checked and physically validated where impacted;
6. regions/quests/mechanics expose explicit current certification dimensions and stale state;
7. all orchestration preserves exact provenance and source-map immutability;
8. no parallel parser/pathfinder/writer/renderer/E2E stack has been introduced.
