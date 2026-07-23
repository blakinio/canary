# OTBM World Assurance Operations Roadmap

> Repository: `blakinio/canary`  
> Programme: `CAN-PROGRAM-OTBM-WORLD-ASSURANCE-OPERATIONS`  
> Successor context: completed and lifecycle-closed OTBM-QA-001..018  
> Status: active / OWA-001..006 planned  
> Evidence rule: static evidence, Physical E2E proof and candidate revalidation remain distinct proof levels

## Purpose

This roadmap operationalizes the completed OTBM-QA stack against reviewed real Canary world targets. It does **not** reopen OTBM-QA-001..018 and it does **not** create OTBM-QA-019.

The goal is to move from:

```text
we have strong OTBM QA contracts
```

to:

```text
we know exactly which reviewed regions, routes, quests and mechanics
have current evidence, current certification, current blockers and current runtime proof
```

The closed QA roadmap remains authoritative for the delivered OTBM-QA-001..018 contracts. This successor roadmap owns only operational use, visualization, integration and hardening of those contracts.

## Non-negotiable reuse rules

1. Unified OTBM World Index remains the only canonical full-world OTBM index.
2. OTBM Script Resolution remains the canonical AID/UID/item/position-to-handler evidence source.
3. OTBM Reachability/BFS remains the only canonical OTBM pathfinder.
4. Semantic OTBM Diff remains the canonical exact before/after semantic change evidence.
5. The factual OTBM renderer remains the only map visualization path used as evidence; AI-generated map imagery is prohibited as evidence.
6. Existing bounded repair/materialization/finalization paths remain the only approved OTBM mutation paths.
7. Universal Physical E2E owns physical execution and runtime proof.
8. Source maps are immutable inputs; generated `.otbm`, `.widx`, reports, evidence bundles and renders remain external artifacts.
9. `unresolved`, `partially-resolved`, `referenced-only`, `conflicting`, stale, truncated, ambiguous or missing-provenance evidence fails closed whenever the claim depends on it.
10. A dashboard percentage, heatmap colour or risk score never replaces explicit evidence dimensions or blockers.

## Operational target model

World assurance operates only on explicitly reviewed targets. Candidate target classes include:

- world-level reviewed population summaries;
- city or region;
- semantic landmark route;
- one explicitly selected quest chain;
- teleport or transition network;
- dungeon/region;
- reviewed critical infrastructure set;
- reviewed house-door/transition set;
- reviewed mechanic set.

Each target retains, as applicable:

```text
exact source-map SHA-256
World Index provenance
QA-005 coverage dimensions
QA-006 C0-C7 certification
QA-016 freshness/staleness
exact blockers
existing route/preflight references
retained Physical E2E evidence where required
candidate-map validation evidence where required
```

The existence of a target in the campaign does not prove that the target is healthy. A target may legitimately remain C0, stale, unresolved or blocked.

# OWA-001 — Real-World Certification Campaign

**Priority: highest.**

## Goal

Systematically apply the delivered QA stack to reviewed real-world targets and maintain a reproducible certification inventory.

## Flow

```text
reviewed target definition
  -> exact current map / World Index provenance
  -> QA-005 factual coverage dimensions
  -> QA-006 bounded certification
  -> QA-016 freshness state
  -> existing Physical E2E references where required
  -> current certification + exact blockers
```

## Initial pilot policy

Prefer an already reviewed semantic target rather than inventing coordinates or target semantics. `thais.temple -> thais.depot` is a preferred pilot candidate only when its current Semantic Landmark, route-plan, preflight and map/index provenance remain exact and current.

The first campaign task must revalidate the pilot against then-current `main`; this roadmap does not freeze coordinates or certify the route by itself.

## Campaign outputs

- reviewed target inventory;
- exact current C0-C7 state per target;
- independent coverage dimensions;
- stale/provenance state;
- exact blockers and unresolved/conflicting evidence;
- retained Physical E2E references where applicable;
- bounded roll-up summaries for operator review.

Generated campaign result artifacts remain outside Git.

## Success condition

A reproducible campaign exists for at least one reviewed real-world target set. Success means “current certification state is known”, not “the world is globally healthy”.

# OWA-002 — Factual Certification and Coverage Map

**Priority: second, after real OWA-001 evidence exists.**

## Goal

Provide a factual visual layer over reviewed campaign targets without creating a second renderer or converting presentation into proof.

## Candidate overlay dimensions

- C0-C7 certification level;
- stale certification;
- unresolved/conflicting Script Resolution state;
- statically unreachable or conditional reviewed targets;
- route fragility for reviewed paths;
- missing current Physical E2E proof;
- identifier/selector conflicts;
- critical-access findings;
- selected World Health dimensions.

## Required behavior

- reuse the existing factual renderer;
- use compatible real assets only;
- attach an exact evidence reference to every rendered marker/region;
- preserve source-map and evidence provenance;
- never infer semantic meaning from sprite appearance;
- never use AI-generated map imagery as evidence;
- never treat colour, percentage or heat intensity as a merge/certification gate;
- keep generated renders and manifests outside Git.

## Success condition

An operator can inspect reviewed certification/coverage state spatially and trace every visible finding back to exact machine-readable evidence.

# OWA-003 — TCR-to-QA Drift and Freshness Integration

**Priority: dependency-gated.**

## Goal

Use stable exact Tibia Client Reference outputs to invalidate or refresh only the QA/certification dimensions that explicitly depend on them.

## Dependency

Implementation starts only after the required owning TCR packages and formats are merged and stable. OWA never parses client files itself.

## Intended flow

```text
stable TCR exact parity/drift finding
  -> explicit dependency mapping
  -> QA-016 dependency-scoped staleness
  -> QA-008 proven blast radius where declared
  -> QA-002 impacted validation selection
  -> owning validators / Universal Physical E2E execute
  -> QA-007 assurance
  -> refreshed QA-006 certification state
```

## Hard boundaries

- no `staticdata`, `staticmapdata`, proficiency or minimap parsing in OWA;
- no guessed item/server/object identifier mapping;
- client reference is not map authority;
- quest ID/name drift does not prove quest-stage/runtime changes;
- matching proficiency IDs do not prove runtime/persistence/protocol parity;
- dependency uncertainty fails closed to stale/review-required or broader validation.

## Success condition

A stable TCR change can deterministically identify which OTBM certification/assurance dimensions become stale or require revalidation without duplicating TCR ownership.

# OWA-004 — Runtime Incident to OTBM Evidence Bridge

**Priority: after campaign semantics are established; independent of TCR.**

## Goal

Make exact OTBM-owned static context cheap to retrieve when a runtime owner reports a concrete map-related selector.

## Candidate explicit inputs

- `x,y,z` position;
- transition ID;
- interaction ID;
- landmark ID;
- exact route-plan/preflight reference;
- runtime-observed map SHA-256 when retained.

## Evidence returned through existing contracts

- exact tile/item/AID/UID/house-door/teleport context;
- Script Resolution state and correlated handlers;
- reachability/transition evidence;
- Semantic Landmark and Route Interaction references;
- existing route-plan/preflight/failure-triage evidence;
- current QA-001/005/006/016 dimensions;
- exact blockers and provenance mismatch.

## Hard ownership boundary

The bridge does not:

- become a general log parser;
- determine runtime root cause beyond OTBM-owned static correlation;
- control Canary, MariaDB or OTClient lifecycle;
- generate feature-specific assertions or fixtures;
- generate `NEXT_ACTION` for E2E owners;
- replay/retry Physical E2E;
- promote static correlation to runtime success/failure proof.

## Success condition

A runtime/E2E/feature owner can supply an exact selector and receive compact OTBM evidence without manually opening many reports and without transferring runtime ownership to OTBM.

# OWA-005 — QA Contract Hardening and Adversarial Fixtures

**Priority: may proceed in parallel when path ownership is disjoint.**

## Goal

Increase confidence in the delivered QA stack by testing cross-contract invariants and fail-closed behavior with bounded deterministic synthetic fixtures.

## Candidate invariant families

- identical stable input yields byte-identical deterministic output where required;
- changing a dependency byte/hash invalidates exactly the relevant provenance/freshness state;
- unresolved/conflicting/ambiguous/stale/truncated evidence never silently upgrades to handled or safe;
- bounded/truncated evidence never authorizes global absence or safe skip;
- source-map immutability and create-new/no-clobber guarantees hold;
- unsafe paths, symlinks and input/output aliasing fail closed where supported;
- duplicate IDs/selectors stay explicit findings and are never auto-repaired;
- unknown/missing appearance evidence never becomes compatible/walkable by default;
- candidate/current map hash mismatch invalidates candidate/Physical E2E proof;
- canonical ordering rules prevent nondeterministic reports.

## Test policy

- use synthetic/generated fixtures, never production map mutation;
- default to repository-supported and Python standard-library infrastructure;
- third-party fuzz/property frameworks require explicit justification in their own bounded task;
- test canonical implementations rather than cloning their logic into a new harness layer.

## Success condition

High-value determinism, provenance and fail-closed invariants have durable regression coverage across the most critical QA composition boundaries.

# OWA-006 — Continuous Assurance Operational Adoption

**Priority: last among initial packages because it can affect merge/release gating.**

## Goal

Apply the already-delivered QA-002 and QA-007 contracts to one real bounded map/candidate change path.

## Required sequence

```text
exact before/current/candidate provenance
  -> Semantic Diff
  -> QA-002 selected static + represented Physical E2E plan
  -> owning validators / Universal Physical E2E execute
  -> before/after QA-001 World Health
  -> before/after QA-006 certification
  -> QA-007 exact execution/result-set validation
  -> auditable assurance decision
```

## Hard boundaries

- QA-007 does not rerun validators or E2E;
- selected result sets must exactly match the QA-002 plan;
- uncertain/manual selection remains fail-closed;
- unrelated non-OTBM suites are never suppressed;
- assurance success does not authorize deployment or production promotion;
- adoption begins with one bounded change class before any broader policy expansion.

## Success condition

One real bounded change path consumes existing QA assurance evidence end-to-end without weakening branch protection, unrelated CI or deployment governance.

# Recommended sequence

1. **OWA-001** — launch the first real-world certification campaign.
2. **OWA-002** — add factual certification/coverage visualization after pilot evidence exists.
3. **OWA-005** — harden core invariants in parallel where ownership permits.
4. **OWA-004** — add incident-oriented compact static evidence consumption.
5. **OWA-003** — integrate TCR drift only when stable owning TCR outputs exist.
6. **OWA-006** — adopt Continuous Assurance on one bounded real change path.

OWA-003 may move based on actual TCR delivery. OWA-006 remains deliberately later because merge/release policy changes require mature campaign semantics and explicit CI ownership.

# Operational assurance loop

```text
reviewed real-world target
  -> exact current evidence
  -> QA-005 coverage
  -> QA-006 certification
  -> Physical E2E where required
  -> QA-016 freshness

map/source/appearance/TCR dependency changes
  -> QA-008 explicit dependency paths
  -> QA-002 impacted validation
  -> owning validators / Universal Physical E2E
  -> QA-007 assurance
  -> refreshed certification
```

# Cross-program boundaries

## OTBM-QA-001..018

Closed and complete. OWA consumes the delivered contracts and does not renumber or reopen them.

## OTBM Tibia Client Reference

TCR owns client-package manifests, reference indexes, parity/correlation and reference drift. OWA-003 consumes stable exact outputs only after their owning packages merge.

## Universal Physical E2E / OTBM-E2E routing

E2E owns runtime execution, feature-specific scenarios, fixtures, assertions, persistence/relog proof and retained runtime artifacts. OWA may consume exact retained results and expose coverage gaps, but does not invent or prioritize E2E scenarios merely because a gap exists.

## Map repair/materialization

OWA may expose findings, certification deltas and assurance outcomes. Any repair remains review-gated and must use the existing approved bounded mutation/finalization chain.

# Completion definition

The programme is complete only when:

1. at least one reviewed real-world certification campaign is reproducible from exact current evidence;
2. factual certification/coverage visualization exists and every rendered marker is evidence-linked;
3. stable TCR drift, if delivered, propagates through explicit dependency-scoped freshness/impact evidence without duplicate parsing;
4. runtime incident selectors can retrieve compact OTBM evidence without transferring runtime ownership;
5. high-value determinism/provenance/fail-closed invariants have adversarial/property-style regression coverage;
6. one bounded real map/candidate change path uses the existing QA-002/007 assurance chain;
7. no parallel parser, World Index, Script Resolution engine, pathfinder, renderer, writer, E2E runner or E2E workflow has been introduced;
8. generated map, evidence, certification and render artifacts remain outside Git.

Completion still does not imply that every tile, quest or mechanic in the entire world is gameplay-correct. Certification remains reviewed-target- and evidence-bounded.

# First next action

After this roadmap/programme bootstrap is merged and archived, start **OWA-001** as a new bounded task from then-current `main`:

1. revalidate current reviewed semantic targets and their provenance;
2. select the first pilot target set without inventing coordinates;
3. compose existing QA-005/006/016 evidence and retained Physical E2E references;
4. emit the first external campaign certification ledger;
5. record exact gaps/blockers without generating new E2E ownership decisions.
