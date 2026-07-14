# Bounded OTBM fixed-width attribute patcher

Phase 8 introduces the first write-capable OTBM safety surface in this repository. It does **not** serialize a map and it does not create a second parser. The tool asks the existing native scanner for exact physical metadata around each supported logical payload byte, copies the source map, changes only the payload-byte location and then proves the result with the existing World Index and Semantic Diff pipelines.

## Supported operations

The v1 plan can replace an attribute only when that attribute already exists on an item node:

| Plan kind | Existing OTBM attribute | Logical payload |
|---|---|---:|
| `set-action-id` | action ID | unsigned 16-bit |
| `set-unique-id` | unique ID | unsigned 16-bit |
| `set-house-door-id` | house-door ID | unsigned 8-bit |
| `set-teleport-destination` | teleport destination | x:16, y:16, z:8 |

The following are deliberately unsupported:

- inserting or removing an attribute;
- changing an item ID, count, subtype or stack order;
- adding or removing an item, tile or node;
- changing tile flags, house ID, ground or border geometry;
- rewriting or reserializing the complete OTBM tree;
- modifying the source map in place.

A broader writer requires a later task and a separate safety review.

## Identity and expected state

Every operation identifies one existing attribute with redundant evidence:

- exact `x,y,z`;
- tile-local placement index;
- item ID;
- item depth;
- attribute kind;
- exact expected old value.

The plan also pins the source base name, SHA-256, byte size, OTBM version and items major/minor version. The complete operation must be inside one explicit region of no more than 1,000,000 coordinates.

A missing, repeated or ambiguous anchor is an error. The tool does not infer which duplicate item the author intended.

## Physical-byte boundary

OTBM uses `0xFD` as an escape prefix for logical marker bytes `0xFD`, `0xFE` and `0xFF`. Therefore a logical byte can occupy one or two physical bytes.

The native scanner mode:

```text
otbm_item_audit_scan --patch-anchors MAP OUTPUT.json
```

emits `canary-otbm-patch-anchors-native-v1` with the physical offset, encoded size and decoded value of each supported payload byte. Python normalizes this as `canary-otbm-patch-anchors-v1` and adds source/scanner hashes.

The patch is rejected when any replacement logical byte would change the physical encoded width. When an encoded byte has a `0xFD` prefix, the prefix is framing and remains immutable; only the following logical payload location may differ. This preserves all following offsets and the total file length.

## Execution

Compile the scanner first:

```bash
g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Werror \
  tools/ai-agent/otbm_item_audit_scan.cpp \
  -o tools/ai-agent/otbm_item_audit_scan
```

Apply a reviewed plan:

```bash
python tools/ai-agent/otbm_bounded_patch_tool.py \
  --plan /external/reviewed-plan.json \
  --source /external/source.otbm \
  --scanner tools/ai-agent/otbm_item_audit_scan \
  --artifact-root /external/phase8-artifacts \
  --output patched.otbm \
  --evidence-directory evidence \
  --result result.json
```

The source map may be outside the artifact root. The patched output, evidence directory and result must be new, distinct paths below the artifact root. A symlink at the destination or in any existing parent component, a path escape and an existing destination are rejected.

The tool has no overwrite option.

## Required plan shape

```json
{
  "format": "canary-otbm-bounded-patch-plan-v1",
  "source": {
    "fileName": "source.otbm",
    "sha256": "<64 lowercase hex characters>",
    "size": 123456,
    "otbmVersion": 4,
    "itemsMajor": 3,
    "itemsMinor": 57
  },
  "region": {
    "from": [1024, 2048, 7],
    "to": [1030, 2060, 7]
  },
  "operations": [
    {
      "id": "repair-teleport-1",
      "kind": "set-teleport-destination",
      "position": [1025, 2050, 7],
      "tilePlacementIndex": 3,
      "itemId": 1387,
      "itemDepth": 0,
      "expected": [0, 0, 0],
      "replacement": [1101, 2101, 8]
    }
  ]
}
```

The normative input contract is `OTBM_BOUNDED_PATCH_PLAN.schema.json`. Runtime validation is stricter than schema-only validation: it also checks unique operation IDs, distinct target identities, region volume and actual scanner evidence. Every position tuple contains exactly three integers.

## Validation sequence

The patcher fails closed unless all steps succeed:

1. Resolve regular source/scanner files and confined new output paths.
2. Hash the source and scanner.
3. Fully parse the source with native `--patch-anchors` mode.
4. Match every operation to exactly one scanner anchor and exact old value.
5. Validate each physical source byte and its canonical OTBM escape width.
6. Copy the source to a temporary file below the artifact root.
7. Change logical payload locations only; retain escape prefixes and file length.
8. Stream-compare source and copy and reject any change outside the exact planned payload offsets.
9. Fully reparse the patched copy and require identical anchor offsets/sizes with replacement values.
10. Run the legacy scanner parse on the patched copy.
11. Build canonical before/after World Index files with the existing scanner.
12. Run bounded Semantic Diff and require exactly the planned mechanic findings, unchanged tile counts and unchanged placement counts.
13. Recheck the source hash and size.
14. Publish the output with an exclusive hard link, publish evidence into a newly created exclusive directory, and publish the result last with another exclusive hard link.

A failure before the final result removes temporary or partially published output and evidence. The untouched source remains the rollback authority.

## Result and evidence

A successful run writes `canary-otbm-bounded-patch-result-v1`. It records:

- source and output hashes/sizes;
- normalized operations and scanner-proven encoded metadata;
- every physical payload offset whose value changed;
- equality outside those payload offsets (`outsideScannerSpansEqual` remains the v1 field name);
- full reparse, World Index and Semantic Diff status;
- evidence directory and manifest;
- non-executing factual render request;
- rollback instruction to delete the patched copy and retain the pinned source.

The normative result contract is `OTBM_BOUNDED_PATCH_RESULT.schema.json`.

The evidence directory includes native and normalized before/after anchor reports, a full post-patch scan, before/after World Index files and manifests, the bounded Semantic Diff and an evidence manifest. These are external artifacts and must not be committed.

## Visual verification

The result contains a non-executing request for the existing factual renderer. Rendering requires the real source map, patched map and real client assets. Visual evidence supplements byte and semantic proof; it does not replace them. AI-generated map imagery is prohibited.

## Testing policy

Repository tests construct a tiny synthetic OTBM and cover:

- action ID, unique ID, house-door ID and teleport replacement;
- exact source pin, lowercase source hash and expected-old-value failures;
- ambiguous repeated attributes;
- OTBM escape-width changes and immutable escape prefixes;
- existing output, destination symlink, parent symlink and path-escape rejection;
- cleanup after post-validation or final-result publication failure;
- source immutability, equal file length and exact changed payload offsets;
- exact three-integer position schema shape;
- full scanner reparse, World Index and bounded Semantic Diff.

No production or user-supplied map is patched by CI.
