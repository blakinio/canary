# OTBM Identifier, Selector and Collision Integrity

`OTBM-QA-013` adds a deterministic read-only evidence-composition layer for identifier and reviewed-selector ambiguity. It does not parse OTBM, rescan Lua/XML, resolve routes or mutate content.

## Public contracts

- reviewed policy: `canary-otbm-identifier-integrity-policy-v1`;
- report: `canary-otbm-identifier-integrity-v1`.

The implementation reuses:

- the Unified OTBM World Index for exact mechanic placements, positions, `actionId`, `uniqueId`, `houseDoorId`, tile and house scope;
- existing `canary-otbm-script-resolution-v1` evidence for handler conflicts and unresolved identifier state;
- the existing Reachability transition-manifest parser contract for transition ID/source/destination semantics;
- the reviewed `canary-otbm-route-interactions-v1` registry for exact selector semantics.

It never creates another parser, World Index, Script Resolution engine, transition resolver, pathfinder, renderer or E2E runner.

## Repetition is not automatically a defect

Repeated AIDs and item IDs are common reusable selectors. QA-013 therefore does not classify repetition alone as a conflict.

For `actionId` and `uniqueId`, an exact repeated value without reviewed uniqueness/reuse policy is emitted as `review-required`. For house doors, reuse is evaluated in exact `houseId + houseDoorId` scope; the same door ID in different houses is not treated as a same-house collision.

A reviewed policy expectation can declare:

- `unique` — more than one exact placement in the declared scope is conflicting;
- `reviewed-reuse` — repeated placements are explicitly reviewed for reuse and remain non-conflicting.

The policy is evidence, not a renumbering or repair instruction.

## Reviewed role compatibility

Optional `placementRoles` bind exact World Index `placementOrdinal`, namespace/value and reviewed role/compatibility class. A selector is reported as a reviewed role conflict only when the supplied exact bindings for the same namespace/value contain more than one reviewed compatibility class.

Names, item sprites, source proximity or map proximity never create an incompatible-role finding.

## Script Resolution evidence

QA-013 consumes existing Script Resolution aggregate identifier evidence:

- `conflicting` remains a conflict;
- `unresolved`, `partially-resolved` and `referenced-only` remain unresolved evidence;
- repeated placement counts do not promote unresolved evidence to a conflict.

The tool does not scan Lua/XML or reconstruct registration precedence.

## Transition IDs

Optional `canary-otbm-transition-manifest-v1` input is analyzed through the existing transition parser contract. Duplicate transition IDs are conflicting because the canonical parser requires unique IDs. The report distinguishes identical duplicate definitions from duplicate IDs carrying incompatible definitions.

No destination is inferred and no connectivity/pathfinding calculation is performed.

## Route Interaction selector ambiguity

The existing Route Interaction Registry already rejects byte-equivalent duplicate canonical selectors. QA-013 additionally identifies two different reviewed mechanic selectors that can both match the same exact resolver query.

For mechanic selectors, overlap exists only when:

1. exact positions are equal; and
2. every selector field present in both entries (`itemId`, `actionId`, `uniqueId`, `houseDoorId`) has the same value.

The report publishes the exact witness query that satisfies both selectors. Transition selectors remain keyed by exact `transitionId` and are validated by the existing registry contract.

## Provenance and fail-closed behavior

The reviewed policy pins:

- source-map SHA-256;
- World Index SHA-256;
- optional Script Resolution file SHA-256;
- optional transition-manifest file SHA-256;
- optional Route Interaction Registry file SHA-256.

The CLI also requires the canonical World Index provenance manifest so the source-map and actual World Index hashes can be checked before analysis. Optional evidence presence must exactly match the policy pins.

Inputs are read with stable-file checks. Symlink inputs are rejected. Output is create-new by default, cannot alias or hard-link an input, and overwrite uses an atomic replacement.

## CLI

```bash
python tools/ai-agent/otbm_identifier_integrity_tool.py \
  --policy /evidence/identifier-policy.json \
  --world-index /evidence/world.widx \
  --world-index-manifest /evidence/world.widx.json \
  --script-resolution /evidence/script-resolution.json \
  --transitions /evidence/transitions.json \
  --interactions /evidence/route-interactions.json \
  --output /evidence/identifier-integrity.json
```

The three optional evidence inputs must be omitted when their corresponding policy provenance entry is `null`.

## Proof boundary

The report is static evidence. It does not prove runtime behavior, player intent, global uniqueness outside the reviewed scope, gameplay correctness or safe repair. It never changes identifiers or authorizes automatic map/datapack mutation.
