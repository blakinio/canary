# OTBM Repair Recommendation Orchestrator

`OTBM-QA-003` adds a deterministic, review-only layer between an exact finding and the already-delivered bounded OTBM mutation families.

Public contracts:

- request: `canary-otbm-repair-recommendation-request-v1`;
- output: `canary-otbm-repair-recommendation-v1`;
- request schema: `docs/ai-agent/OTBM_REPAIR_RECOMMENDATION_REQUEST.schema.json`;
- report schema: `docs/ai-agent/OTBM_REPAIR_RECOMMENDATION.schema.json`;
- implementation: `tools/ai-agent/otbm_repair_recommendation.py`;
- CLI: `tools/ai-agent/otbm_repair_recommendation_tool.py`.

## Purpose

The orchestrator answers one narrow question:

> Given one exact caller-supplied finding/target request and one compatible existing Repair Preflight report, which already-delivered mutation family, if any, is technically capable of representing the declared change shape?

It does **not** answer whether the finding is a real defect, whether the proposed target state matches Real Tibia, whether the repair is gameplay-correct, or whether mutation is approved.

## Inputs

### Exact recommendation request

The request is caller-supplied and must contain:

- a finding report format, SHA-256 and finding ID;
- exact source-map SHA-256;
- the exact Repair Preflight selector;
- explicit expected old state;
- explicit proposed target state;
- one declared mutation shape;
- whether runtime-handler resolution is required for the recommendation;
- a non-empty review rationale.

The orchestrator never derives or invents AID, UID, item ID, house-door ID, teleport destination, coordinate, stack order, expected old state or target state.

### Repair Preflight

One `canary-otbm-repair-preflight-v1` report is required.

The request and preflight must have identical:

- source-map SHA-256;
- normalized selector.

The preflight remains the authority for:

- number of matching mechanic placements;
- native patch-anchor correlation;
- runtime/script-resolution status;
- Phase 8 patch/review readiness;
- review-only bounded attribute draft plan evidence.

The recommendation layer does not rerun Item Audit, native patch-anchor scanning or Script Resolution.

## Recommendation states

### `no-repair-evidence`

No Repair Preflight candidate matches the exact selector. No mutation path is recommended.

### `ambiguous-target`

More than one candidate matches, or native patch-anchor evidence is ambiguous. The orchestrator does not choose a candidate.

### `blocked-by-runtime-evidence`

The request declares that runtime handling matters and the exact candidate remains unresolved, partially resolved, referenced-only, conflicting or otherwise not runtime-resolved.

Runtime blockers are preserved. They are never promoted to handled by a review rule or by the existence of a writer.

### `review-required`

The exact target is correlated but there is not yet enough evidence for a supported technical path, or no mutation shape was requested.

For the attribute path, this includes the absence of a Repair Preflight `reviewReady` Phase 8 draft plan.

### `supported-by-existing-attribute-path`

Requires all of the following:

- one exact correlated Repair Preflight target;
- no blocking runtime evidence when runtime handling is required;
- a request operation in the existing Phase 8 set:
  - `set-action-id`;
  - `set-unique-id`;
  - `set-house-door-id`;
  - `set-teleport-destination`;
- `patchable=true`;
- `reviewReady=true`;
- an existing `canary-otbm-bounded-patch-plan-v1` draft.

The draft remains review-only. The recommendation does not execute it.

### `supported-by-existing-tile-area-path`

The request must explicitly declare a shape already representable by the bounded TILE_AREA family:

- `policy=replace-region`;
- zero translation;
- complete 256x256-aligned x/y bounds;
- non-reversed 3D bounds.

This state is **capability-only**. It does not replace the existing requirements for a canonical current/donor World Index pair, exact `canary-otbm-region-merge-plan-v1`, zero blocking plan conflicts, complete untruncated conflict evidence, a separately reviewed `canary-otbm-area-materialization-approval-v1`, exact raw TILE_AREA span evidence and all post-write verification.

### `supported-by-existing-raw-tile-path`

The request must contain one exact position equal to `selector.position` and one of the already-delivered shape families:

- raw-tile replacement;
- raw-tile insertion;
- raw-tile deletion;
- raw-tile type conversion.

Basic shape constraints are preserved:

- insertion requires an absent expected old state;
- deletion requires an absent proposed target state;
- replacement requires both old and target states;
- type conversion requires the exact `5 ↔ 14` `OTBM_TILE`/`OTBM_HOUSETILE` node-type pair.

This state is also **capability-only**. It does not prove the materializer-specific exact current/donor span, parent TILE_AREA, World Index, node-type, raw SHA-256 or approval gates. Those remain mandatory downstream and are revalidated by the existing materializer.

### `unsupported-mutation-shape`

The declared change cannot be represented by the bounded capability inventory under the supplied exact request shape. The orchestrator does not widen a writer or reinterpret the request heuristically.

## Capability is not approval

Every report has:

```text
review.requiresHumanReview = true
review.approvalGenerated = false
review.mapModified = false
review.gameplayCorrectnessProven = false
review.playerIntentProven = false
review.supportedPathMeansRepairCorrect = false
```

A `supported-by-existing-*` state means only that the declared exact shape belongs to an already-delivered technical mutation family.

Before mutation, downstream work must still perform exact current-state revalidation, writer/materializer-specific evidence checks and explicit approval. Candidate generation must remain create-new and must retain native reparse, canonical World Index and Semantic Diff evidence.

## Safety boundary

The orchestrator:

- parses JSON reports only;
- never opens or parses an OTBM;
- never builds a World Index;
- never executes Script Resolution;
- never executes Phase 8 or a materializer;
- never generates an approval;
- never publishes a candidate map;
- never runs Physical E2E;
- never creates a workflow.

Input request and Repair Preflight files are SHA-256 pinned in the output. CLI inputs must be distinct regular non-symlink files. Output defaults to create-new/no-clobber semantics and rejects input/output collisions and symlink targets; explicit `--overwrite` uses atomic replacement.

Generated recommendation reports are external evidence artifacts and must not be committed.

## CLI

```bash
python tools/ai-agent/otbm_repair_recommendation_tool.py \
  --request /external/artifacts/repair-request.json \
  --repair-preflight /external/artifacts/repair-preflight.json \
  --output /external/artifacts/repair-recommendation.json
```

Use `--overwrite` only when replacement of an existing report is explicitly intended.

## Interpretation boundary

The recommendation layer deliberately separates:

1. exact finding/target declaration;
2. Repair Preflight evidence;
3. technical mutation-family support;
4. human/review approval;
5. candidate mutation;
6. static candidate validation;
7. Physical E2E proof.

A technically supported path must never collapse these stages into an automatic repair decision.
