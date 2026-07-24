# Real Tibia evidence corpus

This directory contains the versioned, machine-readable contracts used by `CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION`.

The corpus stores compact metadata, bounded claims, proof boundaries, stable owner-result references and hashes. It does not store official-client packages, captures, videos, screenshots, maps, binaries, database dumps or other proprietary/large artifacts.

## Contract versions

| Contract | Format | Schema version | Schema |
|---|---|---:|---|
| Evidence record | `canary-real-tibia-evidence-record-v1` | 1 | `schemas/evidence-record.schema.json` |
| Owner request | `canary-real-tibia-owner-request-v1` | 1 | `schemas/owner-request.schema.json` |
| Module evidence index | `canary-real-tibia-module-evidence-index-v1` | 1 | `schemas/module-evidence-index.schema.json` |
| Version history | `canary-real-tibia-version-history-v1` | 1 | `schemas/version-history.schema.json` |
| Generated factual indexes | `canary-real-tibia-generated-indexes-v1` | 1 | `schemas/generated-indexes.schema.json` |

Files with a `.yaml` suffix use the YAML 1.2 JSON-compatible subset. The standard-library validator rejects duplicate JSON keys and does not silently normalize YAML aliases, implicit values or unknown fields.

## Layout

```text
docs/agents/real-tibia/evidence/
├── README.md
├── schemas/
├── generated/
│   └── EVIDENCE_INDEXES.json
├── modules/
│   └── <canonical-module-id>/
│       ├── MODULE.md
│       ├── BEHAVIOR_MODEL.md
│       ├── VERSION_HISTORY.yaml
│       ├── EVIDENCE_INDEX.yaml
│       ├── DECISIONS.md
│       ├── records/
│       │   └── RT-<MODULE>-NNNN.yaml
│       └── reviews/
│           └── <review-id>.md
└── requests/
    ├── e2e/
    ├── otbm/
    ├── tcr/
    ├── protocol/
    └── feature/
```

Do not create empty module directories or index-only placeholder dossier trees. A module directory starts only when a bounded dossier, evidence record, history record or related owner request exists.

## Validation

```sh
python tools/agents/real_tibia_evidence.py validate
python tools/agents/real_tibia_evidence.py generate --check --as-of 2026-07-24
python -m unittest -v tools/agents/test_real_tibia_evidence.py
```

The runtime validator and generator use only Python 3.12 standard-library modules. Published Draft 2020-12 JSON Schemas provide an interchange contract; CI may use `jsonschema` to verify schema/example compatibility, but corpus acceptance does not depend on it.

Validation fails closed for:

- unknown schema versions, fields or enum values;
- noncanonical module IDs or wrong record placement;
- duplicate evidence, request or version-history IDs;
- unsafe paths, symlinks and repository escapes;
- malformed dates, commit SHAs, SHA-256 values or version axes;
- missing `proves` / `does_not_prove` boundaries;
- missing references, nonreciprocal supersession or cycles;
- lower/static evidence promoted to gameplay or physical-client proof;
- invalid owner-request transitions or owner-controlled states without owner evidence;
- committed external/proprietary artifact payloads;
- stale, missing or manually edited generated indexes.

`UNKNOWN`, `CONFLICT`, `STALE`, `SUPERSEDED` and `REJECTED` are valid explicit states. They are never normalized into success.

## Version history

Every record keeps these lifecycle cells distinct:

- `announced_in`;
- `introduced_in`;
- `observed_in`;
- `changed_in`;
- `deprecated_in`;
- `removed_in`;
- `effective_from`;
- `effective_until`.

Each cell preserves separate axes for official Tibia release, official client build, protocol profile, Canary commit, maintained OTClient commit, map SHA-256, datapack revision, appearances/items revision, spawn/NPC sidecar revision and database schema revision.

Use `DERIVED_RANGE`, `LOWER_BOUND`, `UPPER_BOUND` or `UNKNOWN` when the first exact version is not proven. A filename, directory, donor branch, OTBM label or wiki statement never authorizes an invented exact introduction version.

## Owner requests

Requests are contracts directed to Universal E2E, OTBM/OWA, TCR, protocol/client owners or feature programmes. The Collector may create and advance Collector-controlled states, but transitions to `accepted-by-owner`, `active` and `result-available` require an owner actor and stable owner evidence reference.

Owner execution paths remain read-only for the Collector. A request does not authorize a Collector task to implement an E2E runner, OTBM parser, client-reference parser, protocol change or feature behavior.

## Generated factual indexes

`generated/EVIDENCE_INDEXES.json` and per-module `EVIDENCE_INDEX.yaml` files are derived only from validated records. Generation is deterministic, filesystem-order-independent and atomic.

Generated facts include:

- evidence by module;
- evidence by authority dimension;
- evidence/version-history references by version axis;
- unresolved conflicts;
- stale evidence;
- active owner requests;
- superseded records;
- strongest proof maturity per independent module/authority dimension.

Generated outputs never contain an opaque confidence score, overall parity percentage, release approval, whole-game parity conclusion or evidence inferred from file presence.

## Proof boundary

A structurally valid or reviewed record means only that its bounded evidence is represented accurately. It does not prove Real Tibia parity, release readiness or faithful whole-game reproduction. Static source, map, protocol or client-reference evidence cannot be promoted into gameplay or physical-client proof without the corresponding owner-produced evidence.
