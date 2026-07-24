# OTBM Continuous Assurance Operational Adoption

This document records the bounded OWA-006 operational-adoption attempt for the already-delivered QA-002 Map Change Regression Guard and QA-007 Continuous Assurance contracts.

OWA-006 does not add another assurance engine, Semantic Diff implementation, validator runner, pathfinder, OTBM parser/writer, Physical E2E runner or workflow. Its only valid success path is to consume one existing reviewed real map/candidate change evidence chain end-to-end.

## Required real adoption chain

An eligible target must already retain compatible evidence for one concrete reviewed change:

```text
exact before/current/candidate provenance
  -> canonical Semantic OTBM Diff
  -> exact QA-002 selected validation plan
  -> owning static-validator results
  -> selected Universal Physical E2E result where required
  -> before/after QA-001 World Health
  -> before/after QA-006 certification
  -> exact QA-007 execution/result-set validation
  -> auditable assurance decision
```

QA-002 remains the validation-scope owner. QA-007 only validates the exact supplied selected result set and never reruns Semantic Diff, static validators or Physical E2E.

## 2026-07-24 target-selection result

Disposition: `BLOCKED_EXTERNAL_EVIDENCE`.

First failure marker:

`OWA006_NO_RETAINED_REVIEWED_REAL_CANDIDATE_CHAIN`

The current repository and retained task/PR evidence prove the generic capabilities needed to build and validate a candidate chain, but they do not prove one concrete reviewed real candidate chain that OWA-006 can consume.

### Evidence boundary

- OTBM-E2E-009 delivered exact source/candidate/pipeline/Semantic-Diff/impacted-selection hash-chain validation, selected-only delegation to the existing Universal Physical E2E runner, candidate runtime map-hash validation and fail-closed provenance checks.
- The archived OTBM-E2E-009 task explicitly records that its feature task did **not** claim any specific repaired candidate artifact chain as physically gameplay-validated.
- OTBM-QA-004 Reviewed Candidate Repair is an evidence-chain validator over explicit approval and already-produced pipeline/Semantic-Diff/impact/Physical-E2E evidence. It does not create a real candidate or execute Physical E2E.
- The repair/materialization pipeline publishes generated candidate artifacts outside Git and explicitly deferred physical-client E2E to the existing Universal Physical E2E subsystem.
- OWA-001 provides exact current-state campaign evidence for the reviewed Thais route, but it is not a before/current/candidate change chain. Its first target also remains formal QA-006 `C0_NOT_EVALUATED` because no legitimate reviewed QA-005 mechanic binding exists for that pure-movement route.

Repository/PR search found no later OWA-006 owner, no retained concrete QA-004 candidate adoption, and no later concrete OTBM-E2E-009 candidate execution record that closes this gap.

## Why OWA-006 stops here

Without one concrete retained reviewed real candidate artifact chain, OWA-006 cannot truthfully establish the first provenance input required by its contract. Therefore it also cannot legitimately manufacture or claim:

- a candidate-bound Semantic Diff;
- an exact QA-002 plan for that candidate;
- exact selected static-validator result identities;
- candidate-hash-matched selected Physical E2E results;
- compatible before/after QA-001 World Health evidence;
- compatible before/after QA-006 certification evidence;
- a QA-007 assurance decision for a real bounded change.

Using synthetic fixtures, plan-only examples, generic contract tests, the current production map as both before and candidate, or the OWA-001 current-state route would create false production evidence and is prohibited.

## Minimal integration decision

No production-code or workflow integration change is justified by this blocker.

The missing element is producer evidence — one reviewed real candidate/change artifact chain — not an absent QA-002/QA-007 composition capability. The canonical stack already contains:

- Semantic OTBM Diff;
- QA-002 Map Change Regression Guard;
- OTBM-E2E-008 impacted Physical E2E selection;
- OTBM-E2E-009 candidate-map Physical E2E validation;
- QA-001 World Health;
- QA-006 Region and Quest Certification;
- QA-007 Continuous Assurance;
- QA-016 provenance/freshness.

Adding another wrapper, runner, candidate generator or workflow would duplicate existing ownership without producing the missing reviewed real evidence.

## Re-entry condition

OWA-006 can resume only when an existing owning map-repair/change workflow retains or explicitly references one concrete reviewed real candidate chain with exact before/current/candidate identity and all evidence required by the adoption sequence.

At re-entry:

1. verify exact candidate/current/source hashes and compatible World Index provenance;
2. consume the canonical Semantic Diff;
3. let QA-002 select the validation scope;
4. consume exact owning validator and required Universal Physical E2E results;
5. consume compatible before/after QA-001 and QA-006 evidence;
6. let QA-007 validate the exact result set;
7. keep unrelated CI and branch/deployment governance unchanged.

A green OWA assurance result never merges, deploys or promotes a candidate by itself.

## Programme state

The correct current statement is:

```text
all currently executable non-TCR OWA work completed
OWA-006 operational adoption is blocked on one retained reviewed real candidate/change evidence chain
OWA-003 remains dependency-blocked by TCR
```

OWA-006 is not marked functionally complete because its required real adoption success condition has not been proven.
