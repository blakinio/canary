# OTBM World Quality, Repair and Certification Architecture

## Status

Successor architecture after completion of:

- `OTS-OTBM-VALIDATION` phases 1–8 and its bounded post-Phase-8 repair/materialization extensions;
- `CAN-PROGRAM-OTBM-E2E-ROUTING`, including OTBM-E2E-001 through OTBM-E2E-009.

This document defines how the delivered contracts compose into a future world-assurance system. It does not reopen either completed programme and does not authorize map mutation or deployment by itself.

## Architectural objective

Provide one fail-closed evidence chain from exact OTBM source state to world health, change impact, reviewed repair, candidate validation and bounded certification:

```text
exact source map
  -> canonical World Index
  -> existing static evidence producers
  -> world health / coverage correlation

exact before + after/candidate
  -> Semantic OTBM Diff
  -> impacted validators and mechanics
  -> impacted OTBM-aware Physical E2E selection

reviewed finding
  -> existing repair preflight
  -> explicit human/review approval
  -> existing bounded mutation path on a distinct copy
  -> candidate map
  -> reparse + World Index + Semantic Diff + Map Quality
  -> selected Physical E2E
  -> certification delta
```

The architecture is composition and orchestration. It is not a new parser, pathfinder, renderer, writer or E2E platform.

# Layer model

## Layer 0 — Immutable source and provenance

Authority:

- exact source `.otbm` bytes;
- SHA-256 identity;
- canonical scanner/tool identity;
- exact client appearance evidence where required;
- exact selected source/datapack hashes where correlation requires them.

Rules:

- source maps are immutable inputs;
- generated maps and indexes live in artifact space;
- every downstream executable or mutation decision must be traceable back to exact source/candidate identity.

## Layer 1 — Canonical map evidence

Reuse:

- Unified OTBM World Index;
- Item/Mechanic Audit;
- exact tile/item/AID/UID/house-door/teleport evidence.

Responsibilities:

- exact positions and stacks;
- canonical map/index provenance;
- bounded deterministic queries.

No other layer may rescan OTBM with an independent parser.

## Layer 2 — Static semantic evidence

Reuse:

- Quest Map Validator;
- Script Resolution;
- Reachability and reviewed transitions;
- Spawn/NPC validation;
- Storage dependency graph;
- Geometry Audit;
- Semantic Landmark Registry;
- Route Interaction Registry.

Responsibilities:

- source-to-map correlation;
- conservative handler resolution;
- walkability/reachability;
- actor/spawn evidence;
- storage prerequisite/result evidence;
- reviewed geometry and route semantics.

Rules:

- `unresolved`, `partially-resolved`, `referenced-only` and `conflicting` remain explicit states;
- selected-scope absence is not global absence;
- static evidence is not runtime proof.

## Layer 3 — Quality and health correlation

Reuse:

- OTBM Map Quality Gate;
- OTBM-E2E coverage matrix;
- compatible outputs from Layers 1–2.

Future responsibility:

- deterministic world-health aggregation;
- explicit counts and bounded samples by evidence dimension;
- identification of stale, unresolved, unreachable, structurally suspicious or physically unproven targets.

The layer must preserve component evidence rather than collapse different findings into an inferred single defect.

## Layer 4 — Change impact selection

Reuse:

- Semantic OTBM Diff;
- OTBM-E2E-008 impacted scenario selection.

Responsibilities:

- exact before/after finding IDs;
- position/mechanic/route impact correlation;
- safe selection of impacted OTBM-aware tests;
- fail-closed expansion of validation when evidence is incomplete.

A skip is allowed only by exact compatible non-impact evidence. Missing, stale, bounded, truncated or ambiguous evidence selects the scenario/check instead.

## Layer 5 — Repair recommendation and review

Reuse:

- Item/Mechanic Audit;
- Script Resolution;
- repair preflight;
- existing patch/materialization capability inventory.

Future responsibility:

- produce a non-mutating recommendation;
- identify whether the exact change shape is already supported;
- carry exact target position, expected old state, evidence hashes and blockers;
- require explicit review/approval before mutation.

This layer never decides that a suspicious finding is definitely wrong merely because a technically possible patch exists.

## Layer 6 — Bounded candidate mutation

Reuse only existing approved mutation boundaries:

- Phase 8 existing fixed-width attribute patching;
- complete approved `TILE_AREA` materialization;
- bounded raw tile replacement;
- bounded raw tile insertion;
- bounded raw tile deletion;
- bounded `OTBM_TILE` / `OTBM_HOUSETILE` conversion;
- canonical repair/materialization finalization pipeline.

Rules:

- exactly one supported mutation mode per canonical pipeline run unless a separately approved contract changes that rule;
- candidate output is create-new;
- source map remains byte-identical;
- no generic serialization or hidden widening of writer scope;
- unsupported mutation shapes fail closed.

## Layer 7 — Candidate static validation

Required evidence after mutation:

- successful native reparse;
- rebuilt canonical World Index;
- exact candidate SHA-256;
- Semantic OTBM Diff against the source/baseline;
- compatible Geometry/Reachability/Script Resolution evidence as required;
- Map Quality result tied to the exact candidate.

A candidate is never promoted merely because bytes were written successfully.

## Layer 8 — Candidate physical validation

Reuse:

- OTBM-E2E-008 impacted Physical E2E selection;
- OTBM-E2E-009 candidate-map Physical E2E validation;
- canonical Universal Physical E2E lifecycle.

Responsibilities:

- revalidate selected current scenario manifests;
- execute only represented impacted OTBM-aware scenarios when non-impact evidence safely permits it;
- prove runtime `map.sha256` equals the exact candidate SHA;
- retain route/runtime/first-failure evidence.

Physical success is target-specific. It does not globally certify unrelated mechanics.

## Layer 9 — Coverage and certification

Future responsibility:

Expose the strongest current evidence level for explicitly reviewed targets.

Suggested dimensions:

```text
indexed
sourceCorrelated
scriptResolved
reachable
interactionResolved
qualityCompatible
routeCovered
physicalRouteProven
physicalMechanicProven
candidateRevalidated
stale
```

Certification is a structured evidence state, not a single score.

# Canonical orchestration flows

## Flow A — Current world health

```text
source map
  -> World Index
  -> existing validators
  -> provenance compatibility check
  -> Map Quality + coverage correlation
  -> world-health report
```

This flow is read-only.

## Flow B — Map regression assessment

```text
before map + after map
  -> World Index before/after
  -> Semantic Diff
  -> impacted static evidence dimensions
  -> impacted routes/mechanics
  -> OTBM-E2E-008 scenario selection
  -> validation plan
```

The result is a plan/evidence set, not a mutation.

## Flow C — Reviewed repair recommendation

```text
exact finding
  -> exact selector
  -> repair preflight
  -> runtime/script evidence
  -> supported mutation-mode lookup
  -> recommendation + blockers
  -> human/review decision
```

No map is written.

## Flow D — Approved repair to validated candidate

```text
approved repair
  -> existing bounded mutation path
  -> internal candidate
  -> source immutability proof
  -> native reparse
  -> World Index
  -> Semantic Diff
  -> Map Quality
  -> publish create-new candidate + evidence
```

## Flow E — Candidate physical proof

```text
validated candidate
  -> OTBM-E2E-008 impacted selection
  -> OTBM-E2E-009 disposable candidate runtime
  -> selected Physical E2E
  -> exact candidate map hash proof
  -> result/triage artifacts
```

## Flow F — Certification update

```text
prior certification evidence
  + current source/candidate provenance
  + health results
  + impact results
  + selected Physical E2E results
  -> certification delta
```

Any changed required provenance invalidates or marks stale the affected certification dimension until revalidated.

# Evidence maturity model

The following levels are intentionally monotonic only when all lower-level prerequisites required by the target are current:

| Level | Meaning |
|---|---|
| `C0 NOT_EVALUATED` | no current compatible evidence bundle |
| `C1 STATIC_INDEXED` | exact target exists in the canonical World Index |
| `C2 STATIC_CORRELATED` | required source/script/static semantic correlation is non-blocking |
| `C3 STATIC_REACHABLE` | required route/mechanic reachability is confirmed under reviewed policy |
| `C4 STATIC_QUALITY_GREEN` | required compatible static quality gates are green |
| `C5 PHYSICAL_ROUTE_PROVEN` | controlled OTClient physically executes the exact reviewed route on the exact map |
| `C6 PHYSICAL_MECHANIC_PROVEN` | target mechanic/feature outcome has exact runtime evidence, not mere coordinate traversal |
| `C7 CANDIDATE_REVALIDATED` | an approved candidate change has passed exact static and selected Physical E2E revalidation |

Not every target requires every dimension. A pure static geometry target may never need `C6`; a quest certification normally does.

# Fail-closed decision rules

The following conditions block a positive executable, repair-ready, skip or certification claim when relevant:

- source/candidate SHA mismatch;
- World Index mismatch;
- stale evidence hash;
- incompatible report format/version;
- truncated evidence where full evidence is required;
- ambiguous placement;
- unresolved/conflicting required Script Resolution;
- unknown required interaction semantics;
- unsupported mutation shape;
- missing explicit approval;
- failed native reparse;
- failed candidate quality gate;
- selected Physical E2E failure;
- runtime map hash not equal to the exact candidate hash.

When evidence is insufficient, the system selects more validation or reports a blocker. It never guesses a safe skip or safe repair.

# Repair safety boundary

## Recommendation is not approval

A recommendation may state that an existing mutation path technically supports a reviewed shape. It must not authorize execution.

## Approval is not mutation

Approval pins:

- exact source identity;
- exact target selector/position;
- expected old state;
- intended replacement/new state;
- chosen existing mutation mode;
- required evidence hashes.

## Mutation is not correctness proof

A successful bounded materialization proves only the declared structural mutation and confinement properties until static/candidate validation completes.

## Static validation is not gameplay proof

Physical E2E remains required whenever the acceptance claim concerns runtime gameplay behavior.

# Regression guard architecture

The regression guard should be an orchestration policy over existing contracts, not a second validator.

For an OTBM-relevant PR or candidate:

1. obtain exact before/after map identities;
2. build/reuse canonical compatible World Indexes;
3. run Semantic Diff;
4. map findings to impacted static evidence dimensions;
5. run OTBM-E2E-008 for represented OTBM-aware scenarios;
6. run selected static checks and, when authorized/required, selected Physical E2E;
7. compare world-health/certification deltas;
8. fail closed according to explicit policy.

A non-impact result may reduce work only when the exact evidence contract proves it. It may never suppress unrelated general gameplay tests.

# Dashboard architecture

A future dashboard/report surface should be a renderer of deterministic evidence, not a source of truth.

Recommended views:

- full-world health summary;
- region summary;
- quest/mechanic target summary;
- unresolved/conflicting Script Resolution inventory;
- unreachable/conditional mechanic inventory;
- stale provenance inventory;
- Physical E2E coverage gaps;
- certification state and last exact map hash;
- before/after health delta for a candidate.

Convenience percentages are permitted only as derived presentation. Exact findings, blockers and evidence hashes remain authoritative.

# Ownership boundaries

## OTBM tooling owns

- static map evidence;
- semantic diff;
- reachability and transition evidence;
- quality/health correlation;
- repair recommendation evidence;
- approval-gated candidate mutation through existing bounded paths;
- candidate static validation;
- certification evidence assembly.

## Universal Physical E2E owns

- disposable server/database/client lifecycle;
- controlled real OTClient execution;
- exact runtime map-hash proof;
- route/mechanic physical evidence;
- logout/relog/persistence behavior;
- runtime artifacts and failure evidence.

## Feature/quest programmes own

- target-specific expected behavior;
- exact feature assertions;
- quest/NPC/reward/storage semantics;
- whether a physical mechanic outcome is sufficient for feature acceptance.

No layer should duplicate another layer's implementation to avoid an integration dependency.

# Implementation constraints for future tasks

Every future implementation package must:

- start from then-current `main`;
- create a new active task and draft PR;
- verify live path ownership and open PR overlap;
- search `MODULE_CATALOG.md` before adding reusable interfaces;
- reuse existing OTBM contracts and public entrypoints;
- add focused deterministic tests for any new orchestration contract;
- keep generated maps/reports/indexes outside Git;
- apply exact-final-head validation before merge;
- preserve the completed OTBM-E2E route programme as historical delivered state.

# Explicit non-goals

This architecture does not introduce or authorize:

- autonomous unreviewed repair;
- direct production deployment;
- in-place source-map mutation;
- a second OTBM parser or World Index;
- a second pathfinder;
- a second Script Resolution engine;
- a second Semantic Diff implementation;
- a second factual renderer;
- a generic/full-map serializer;
- arbitrary item-stack editing;
- guessed coordinates, IDs, destinations or quest state;
- dynamic Lua execution in static analysis;
- AI-generated map evidence;
- a second Physical E2E runner/workflow;
- global gameplay-correctness claims from static quality alone.

## Roadmap

The dependency-ordered successor work packages are defined in:

`docs/ai-agent/OTBM_WORLD_QUALITY_REPAIR_ROADMAP.md`
