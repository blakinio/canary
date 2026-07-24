# Tibia proficiency reference correlation

TCR-007 adds deterministic, read-only correlation between the stable manifest-bound proficiency index, the canonical appearances index and compact evidence from Canary's existing item loader and Weapon Proficiency subsystem.

Stable public formats:

```text
canary-tibia-proficiency-reference-resolver-v1
canary-tibia-proficiency-reference-correlation-v1
```

The intermediate `canary-tcr007-canary-evidence-v1` inventory is generated from existing repository-owned definitions and source contracts. It is not a replacement appearance parser, a runtime test, protocol proof or gameplay authority.

## Evidence dimensions

The report keeps these dimensions independent:

- exact client-reference proficiency definition;
- canonical appearance proficiency binding;
- Canary item binding;
- normalized definition semantics;
- runtime definition-loading support;
- persistence source support;
- protocol/client evidence;
- automated behavior evidence;
- Physical E2E evidence.

A `confirmed-reference` row means only that the reviewed static definition and loader-backed binding evidence agree for the exact inputs. It does not prove that every perk executes correctly, persistence survives every lifecycle, protocol/UI behavior is correct or gameplay matches Real Tibia.

## Identifier namespaces

```text
client-reference.proficiency-id
appearance.proficiency-id
appearance.object-id
canary.runtime-proficiency-id
canary.item-id
```

Numeric equality alone is never accepted. The resolver must pin exact report hashes and record the reviewed mapping method.

## Canary evidence inventory

```bash
PYTHONPATH=tools/ai-agent \
python tools/ai-agent/tibia_proficiency_reference_correlation_tool.py inventory \
  --repository-root . \
  --output /tmp/TCR007_CANARY_EVIDENCE.json
```

The inventory reuses the TCR-004 normalization logic for current `data/items/proficiencies.json` and records exact hashes plus reviewed source markers from:

- `src/items/items.cpp` — appearance object ID to `ItemType.id`, appearance proficiency flag to `ItemType.proficiencyId`, and rejection of unknown runtime proficiency definitions;
- `src/creatures/players/components/weapon_proficiency.cpp` — runtime definition loading and the `weapon-proficiency` persistence scope.

It does not execute Canary, mutate files, infer protocol behavior or include user-supplied client data.

## Derive reviewed resolver

```bash
python tools/ai-agent/tibia_proficiency_reference_correlation_tool.py derive-resolver \
  --proficiency-index /outside-git/TIBIA_PROFICIENCY_REFERENCE_INDEX.json \
  --appearances-index /outside-git/APPEARANCES_INDEX.json \
  --canary-evidence /tmp/TCR007_CANARY_EVIDENCE.json \
  --review-id tcr007-reviewed-proficiency-join-20260724 \
  --review-statement "Exact definition semantics and loader-backed bindings reviewed." \
  --output /tmp/TCR007_PROFICIENCY_RESOLVER.json
```

A mapping is emitted only when:

- the source proficiency ID is unique;
- exactly one current Canary runtime definition owns the ID;
- the normalized definition semantic SHA-256 agrees;
- at least one canonical object appearance carries that proficiency flag;
- every selected object ID is unique;
- the reviewed Canary protobuf loader contract is present.

Duplicate IDs, missing definitions, semantic mismatches, missing bindings and duplicate appearance object IDs remain explicit resolver findings.

## Build correlation

```bash
python tools/ai-agent/tibia_proficiency_reference_correlation_tool.py correlate \
  --proficiency-index /outside-git/TIBIA_PROFICIENCY_REFERENCE_INDEX.json \
  --appearances-index /outside-git/APPEARANCES_INDEX.json \
  --canary-evidence /tmp/TCR007_CANARY_EVIDENCE.json \
  --resolver /tmp/TCR007_PROFICIENCY_RESOLVER.json \
  --output /tmp/TCR007_PROFICIENCY_CORRELATION.json
```

Per-row states are:

- `confirmed-reference` — reviewed exact definition semantics and loader-backed appearance/item bindings are present;
- `partial` — a reviewed mapping exists but one static target dimension is incomplete;
- `reference-only` — no target definition or appearance binding exists;
- `unresolved-id-space` — candidate target evidence exists but no reviewed mapping authorizes the join;
- `conflicting` — duplicate or semantic-conflict evidence blocks the join;
- `target-only` — appearance/runtime target evidence is not consumed by a reviewed source mapping;
- `stale-evidence` — reserved for dependency provenance failure; stale input hashes fail closed before normal correlation.

## Boundaries

- no user-supplied proficiency reparsing;
- no second appearance parser;
- no `items.xml`, `proficiencies.json`, appearance, datapack, runtime, protocol, client, database or map writes;
- no automatic approval or repair;
- no inference that all perks, XP/mastery formulas, persistence, protocol/UI or gameplay are correct;
- generated inventory, resolver and correlation reports stay outside Git.

Outputs are deterministic UTF-8 JSON. Existing outputs require `--overwrite`; symlink outputs and input/output aliases fail closed.

## Validation

```bash
python -m unittest discover -s tools/ai-agent -p "test_tibia_proficiency_reference_correlation.py" -v
python -m py_compile \
  tools/ai-agent/tibia_proficiency_reference_correlation.py \
  tools/ai-agent/tibia_proficiency_reference_correlation_tool.py \
  tools/ai-agent/test_tibia_proficiency_reference_correlation.py
python -m json.tool docs/ai-agent/TIBIA_PROFICIENCY_REFERENCE_RESOLVER.schema.json >/dev/null
python -m json.tool docs/ai-agent/TIBIA_PROFICIENCY_REFERENCE_CORRELATION.schema.json >/dev/null
python tools/ai-agent/tibia_proficiency_reference_correlation_tool.py --help >/dev/null
```
