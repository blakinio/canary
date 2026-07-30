# Tibia Client Reference Evidence Gateway

TCR-010 exposes small reviewed fragments of stable Tibia client-reference reports through the existing OTBM-QA-018 Compact Evidence Gateway.

It does not add another extractor. The adapter resolves one exact reviewed binding, constructs the canonical `canary-otbm-evidence-gateway-manifest-v1`, and delegates extraction to `otbm_evidence_gateway.build_evidence_bundle()`.

## Public contracts

```text
canary-tibia-client-reference-evidence-bindings-v1
canary-tibia-client-reference-evidence-gateway-v1
```

The executed report embeds the unchanged QA-018 output:

```text
canary-otbm-evidence-bundle-v1
```

Schemas:

- `docs/ai-agent/TIBIA_CLIENT_REFERENCE_EVIDENCE_BINDINGS.schema.json`
- `docs/ai-agent/TIBIA_CLIENT_REFERENCE_EVIDENCE_GATEWAY.schema.json`

## Supported reviewed kinds

Each binding contains exactly one source report and one to four non-root JSON Pointer extracts.

| Kind | Exact allowed source format | Typical reviewed pointer |
|---|---|---|
| `house` | `canary-otbm-house-reference-parity-v1` | `/houses/0` |
| `content` | `canary-tibia-content-reference-correlation-v1` | `/records/0` |
| `proficiency` | `canary-tibia-proficiency-reference-correlation-v1` | `/rows/0` |
| `drift` | `canary-tibia-client-reference-drift-v1` | `/findings/0` |

Pointers are authored and reviewed explicitly. The adapter does not search reports, infer IDs, choose records by name, reinterpret fields, or turn a report fragment into a gameplay conclusion.

## Binding example

Keep the binding file beside the exact retained source reports outside Git.

```json
{
  "format": "canary-tibia-client-reference-evidence-bindings-v1",
  "schemaVersion": 1,
  "bindings": [
    {
      "id": "drift.staticdata-family",
      "kind": "drift",
      "sources": [
        {
          "id": "drift.staticdata-family.source",
          "path": "tcr009-drift.json",
          "sha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
          "format": "canary-tibia-client-reference-drift-v1",
          "extracts": [
            {
              "id": "drift.staticdata-family.finding",
              "pointer": "/findings/0"
            }
          ]
        }
      ],
      "contextReferences": [
        "TCR-009",
        "retained-report:reviewed"
      ]
    }
  ]
}
```

The SHA-256 in a real binding must match the exact source bytes. The placeholder above is not evidence.

## Plan-only mode

Plan-only mode validates and normalizes the reviewed binding without reading the selected source report.

```sh
python tools/ai-agent/tibia_client_reference_evidence_gateway_tool.py \
  --bindings /retained/tcr/bindings.json \
  --binding-id drift.staticdata-family \
  --output artifacts/tcr010-plan.json \
  --plan-only
```

The output path is relative to the bindings directory.

## Execute mode

```sh
python tools/ai-agent/tibia_client_reference_evidence_gateway_tool.py \
  --bindings /retained/tcr/bindings.json \
  --binding-id drift.staticdata-family \
  --output artifacts/tcr010-evidence.json
```

Execution verifies:

- the binding file is unchanged since plan construction;
- normalized binding content matches its canonical hash;
- the binding ID, kind, context references and QA-018 manifest still match;
- the selected source is a non-symlink regular file below the bindings directory;
- source SHA-256 and report format match exactly;
- every reviewed JSON Pointer resolves;
- every serialized extract remains within the QA-018 bound;
- the QA-018 bundle contract and bundle hash are present.

## Safety and evidence boundary

The adapter is transport/query only:

- no client package parsing;
- no OTBM parsing or World Index rebuild;
- no source-report semantic validation or reinterpretation;
- no fuzzy record selection or inferred identifiers;
- no map, datapack, client, report or runtime mutation;
- no E2E execution;
- no downstream acceptance decision;
- no TCR-011 adoption routing.

A fragment retains the proof boundary of its source report. Extracting a house, content, proficiency or drift row does not upgrade it to runtime, protocol, gameplay, map-authority or mutation proof.

## Failure behavior

The adapter fails closed on malformed or duplicate-key JSON, duplicate binding IDs, unsupported kinds, wrong source formats, unsafe paths, symlinks, root-document extraction, too many extracts, stale binding hashes, changed source hashes, missing pointers, oversized extracts and output/input collisions.
