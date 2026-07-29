# Tibia Proficiency Reference Index schema 2

`canary-tibia-proficiency-index-v1` remains the stable format name. New reports emitted by the TCR-004 producer use `schemaVersion: 2`; historical schema-version-1 reports remain valid inputs to TCR-007.

## Reviewed source change

The exact client snapshot identified by package metadata `15.31.69f220` contains repeated proficiency perk records with:

```json
{
  "ElementId": 3,
  "MissileId": 42,
  "Multiplier": 2.0,
  "Probability": 0.01,
  "Type": 32
}
```

Those records intentionally omit `Value`. The producer must preserve the exact fields and must not synthesize `Value` from another field.

## Schema 2 contract

Every source perk requires `Type` and at least one finite numeric effect field:

- `Value`;
- `Multiplier`;
- `Probability`.

Reviewed optional fields are `AugmentType`, `BestiaryId`, `BestiaryName`, `DamageType`, `ElementId`, `MissileId`, `Multiplier`, `Probability`, `Range`, `SkillId`, `SpellId`, and `Value`.

`MissileId` and the other identifier-like fields are unsigned 32-bit integers. `Value`, `Multiplier`, and `Probability` are finite JSON numbers. No gameplay range, formula, probability meaning, or identifier equivalence is inferred.

Unknown fields, duplicate JSON keys, missing `Type`, absence of all three numeric effect fields, wrong types, non-finite numbers, malformed compression, source-binding mismatch, or unsupported schema versions fail closed.

## Compatibility

- schema 1: normalized perks require `value`;
- schema 2: normalized perks require `type` plus at least one of `value`, `multiplier`, or `probability`, and may contain `missileId`;
- TCR-007 accepts only exact schema versions 1 and 2 and computes semantic hashes over the complete normalized definition;
- future or unknown schema versions remain rejected.

A drift consumer must retain exact format, schema version, parser revision, manifest SHA-256, report SHA-256, and source binding for both snapshots. A schema-version difference is explicit compatibility evidence, not an ordinary field finding.

## Proof boundary

The report proves only what the exact selected proficiency file contains. It does not prove appearance/runtime equivalence, item bindings, XP formulas, perk application, persistence, protocol/UI behavior, or gameplay parity.

## Validation

```bash
python -m unittest discover -s tools/ai-agent -p "test_tibia_proficiency_reference_index.py" -v
python -m unittest discover -s tools/ai-agent -p "test_tibia_proficiency_reference_index_schema_v2.py" -v
python -m unittest discover -s tools/ai-agent -p "test_tibia_proficiency_reference_correlation.py" -v
python -m py_compile \
  tools/ai-agent/tibia_proficiency_reference_index.py \
  tools/ai-agent/tibia_proficiency_reference_resolver.py \
  tools/ai-agent/test_tibia_proficiency_reference_index_schema_v2.py
python -m json.tool docs/ai-agent/TIBIA_PROFICIENCY_REFERENCE_INDEX_V2.schema.json > /dev/null
```

Exact real-file validation remains opt-in and outside Git through `CANARY_TIBIA_PROFICIENCY_CURRENT_FILE`.
