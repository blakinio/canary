# Tibia Reference Adoption Router

TCR-011 adds a deterministic read-only routing boundary over one exact executed TCR-010 evidence report.

It answers only:

> Which already-existing Canary owner/capability should review each exact selected extract next, or must the extract remain explicitly unsupported/blocked?

It does not decide that an extract is a defect, derive a desired state, generate a repair request or approval, execute a writer/materializer, deploy content, run E2E or claim gameplay parity.

## Public contracts

```text
canary-tibia-reference-adoption-routing-request-v1
canary-tibia-reference-adoption-routing-v1
```

Schemas:

- `docs/ai-agent/TIBIA_REFERENCE_ADOPTION_ROUTING_REQUEST.schema.json`
- `docs/ai-agent/TIBIA_REFERENCE_ADOPTION_ROUTING.schema.json`

Implementation:

- `tools/ai-agent/tibia_reference_adoption_router.py`
- `tools/ai-agent/tibia_reference_adoption_router_tool.py`

## Exact input boundary

The router consumes:

1. one executed `canary-tibia-client-reference-evidence-gateway-v1` report;
2. one reviewer-authored routing request.

Every request route pins all of these unchanged TCR-010 extract fields:

```text
bindingId
kind
extract.id
extract.sourceId
extract.pointer
extract.valueSha256
```

The request also pins the gateway file SHA-256, gateway `reportSha256` and embedded QA-018 `evidenceBundleSha256`. The router validates the canonical report, bundle and extract-value hashes before classification.

Every selected gateway extract must appear exactly once in the request. Missing, duplicate or extra routes fail closed.

## Routing dispositions

### `routed`

The exact reviewed extract is assigned to one or more fixed existing owner/capability pairs allowed for that fragment shape.

This means only that the target is the next review boundary. It does not mean the finding is valid, supported by a writer, approved or implemented.

### `unsupported`

No existing bounded capability is selected. Targets must be empty.

Allowed reasons:

- `unsupported-map-change-shape`;
- `unsupported-existing-capability`;
- `unsupported-fragment-shape`.

A house/map extract that cannot be represented through the existing OTBM-QA-003 boundary remains `unsupported-map-change-shape`. The router never widens Phase 8, TILE_AREA, raw-tile or other writers.

### `blocked`

Routing cannot safely continue because required evidence remains unresolved, conflicting, stale or absent. Targets must be empty.

Allowed reasons:

- `conflicting-evidence`;
- `stale-evidence`;
- `unresolved-id-space`;
- `missing-downstream-evidence`.

## Fixed owner/capability inventory

### House/map extracts

The only routable target is:

```text
otbm-repair-recommendation
  -> canary-otbm-repair-recommendation-v1
```

This reuses OTBM-QA-003, which classifies one separate caller-supplied exact mutation request against existing bounded repair/materialization families. TCR-011 never creates that mutation request and never addresses a writer/materializer directly.

### Content extracts

The router uses the exact `sourceCategory` already present in the selected TCR-006 record:

| Source category | Allowed existing targets |
|---|---|
| `creatures`, `monsters`, `monsterClasses` | Cyclopedia Validation; OTBM Spawn/NPC Validation |
| `bosses` | Cyclopedia Validation; OTBM Spawn/NPC Validation |
| `titles`, `achievements` | Achievement Validation |
| `quests` | Quest Map Validation; OTBM Storage Graph |

An unrecognized or missing `sourceCategory` cannot be routed and must remain unsupported/blocked.

### Proficiency extracts

The only routable target is the existing Weapon Proficiency owner recorded in the module catalogue:

```text
weapon-proficiency
  -> module-catalog:weapon-proficiency
```

This does not upgrade static correlation into runtime, persistence, protocol, behavior or Physical E2E proof.

### Drift extracts

The exact TCR-009 `component` and, for StaticData, `family` select only the existing affected TCR owner:

| Drift evidence | Allowed existing target |
|---|---|
| `package-metadata` | TCR client manifest |
| `staticmapdata` | TCR house parity |
| `proficiencies` | TCR proficiency correlation |
| `staticdata` family `houses` | TCR house parity |
| other supported StaticData content families | TCR content correlation |

Unknown components/families remain unsupported/blocked.

## Request example

The hashes below are placeholders and are not evidence.

```json
{
  "format": "canary-tibia-reference-adoption-routing-request-v1",
  "schemaVersion": 1,
  "gateway": {
    "fileSha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
    "reportSha256": "1123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
    "evidenceBundleSha256": "2123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
    "bindingId": "drift.staticdata-family",
    "kind": "drift"
  },
  "review": {
    "reviewId": "tcr011.review.staticdata-family",
    "statement": "Route the exact reviewed StaticData drift finding to its existing TCR consumer owner."
  },
  "routes": [
    {
      "id": "route.staticdata-family",
      "extract": {
        "id": "drift.staticdata-family.finding",
        "sourceId": "drift.staticdata-family.source",
        "pointer": "/findings/0",
        "valueSha256": "3123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
      },
      "disposition": "routed",
      "targets": [
        {
          "owner": "tcr-content-correlation",
          "capability": "canary-tibia-content-reference-correlation-v1"
        }
      ],
      "reasonCode": "reviewed-existing-owner-capability",
      "contextReferences": ["TCR-009", "TCR-010", "TCR-011"]
    }
  ]
}
```

## CLI

```bash
python tools/ai-agent/tibia_reference_adoption_router_tool.py \
  --gateway-report /retained/tcr010-evidence.json \
  --request /retained/tcr011-routing-request.json \
  --output artifacts/tcr011-routing.json
```

Output defaults to create-new/no-clobber behavior. `--overwrite` performs atomic replacement. Input symlinks, output symlinks, input/output aliases, duplicate JSON keys and files above the bounded input limit fail closed.

## Output evidence

The report retains:

- exact gateway file/report/bundle hashes;
- binding ID and kind;
- exact extract identities and value hashes;
- exact request file and canonical hashes;
- reviewer identity/statement;
- deterministic route, disposition and target summaries;
- explicit policy flags proving that no mutation or execution authority was added.

Generated requests and reports remain external evidence artifacts and must not be committed.

## Safety boundary

The router:

- does not open client packages or source reports behind TCR-010;
- does not parse OTBM or build a World Index;
- does not infer IDs, names, coordinates, old state or desired state;
- does not create OTBM-QA-003 recommendation requests;
- does not generate approvals;
- does not execute Phase 8 or any materializer;
- does not mutate maps, datapacks, runtime, database, client or game state;
- does not deploy or promote artifacts;
- does not run Physical E2E;
- does not claim gameplay correctness or Real Tibia parity.
