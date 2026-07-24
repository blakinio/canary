# OTBM Runtime Incident Evidence Bridge

`otbm_runtime_incident_evidence_bridge_tool.py` resolves one explicit reviewed incident selector to compact exact static OTBM evidence by composing a QA-018-compatible manifest and delegating extraction to the canonical Compact Evidence Gateway.

The bridge is an evidence-consumption boundary. It is not a log parser, runtime failure classifier, root-cause engine, route planner, Physical E2E runner, map repair path or source-report semantic validator.

## Contracts

Reviewed bindings use `canary-otbm-runtime-incident-evidence-bindings-v1`.

Each binding contains:

- one stable binding ID;
- exactly one reviewed selector;
- one or more exact QA-018 source specifications with safe relative paths, SHA-256, expected report format and reviewed JSON Pointer extracts;
- optional opaque `contextReferences` for downstream-owned artifacts such as retained failure-triage evidence.

The bridge report uses `canary-otbm-runtime-incident-evidence-v1` and retains:

- the selected binding ID and normalized selector;
- exact bindings file and canonical hashes;
- the normalized `canary-otbm-evidence-gateway-manifest-v1`;
- the exact embedded `canary-otbm-evidence-bundle-v1` and bundle hash in executed mode;
- explicit policy flags proving that the bridge does not diagnose, pathfind, run E2E, mutate evidence or emit a downstream `NEXT_ACTION`.

## Supported selectors

Exactly one selector is required:

- exact position `[x,y,z]`;
- `transition-id`;
- `interaction-id`;
- `landmark-id`;
- `route-id`;
- `preflight-reference`.

Selectors are exact reviewed metadata. Free-form logs, error text, screenshots and runtime telemetry are never searched or fuzzily matched.

Duplicate selector bindings are rejected as ambiguous. Unsupported or missing selectors fail closed.

## QA-018 delegation

Binding normalization calls `otbm_evidence_gateway.normalize_manifest()` for the source/extract specification.

Executed mode calls `otbm_evidence_gateway.build_evidence_bundle()` directly. QA-018 therefore remains the canonical owner of:

- safe relative source paths;
- exact source SHA-256 validation;
- expected source report format validation;
- JSON Pointer extraction;
- bounded extract sizes;
- deterministic source/extract ordering;
- `canary-otbm-evidence-bundle-v1` hashing.

The bridge does not reinterpret extracted values or upgrade static correlation into runtime proof.

## Plan and executed modes

Plan-only mode resolves the reviewed selector and emits the exact normalized QA-018 manifest without reading evidence source files.

Executed mode additionally verifies that the bindings file has not changed since the plan was created and delegates evidence extraction to QA-018. A source hash mismatch, source format mismatch, missing JSON Pointer or other QA-018 incompatibility fails closed.

## CLI

```sh
python tools/ai-agent/otbm_runtime_incident_evidence_bridge_tool.py \
  --bindings reviewed-bindings.json \
  --route-id thais-temple-depot \
  --output artifacts/incident-evidence.json
```

Use `--plan-only` to emit only the resolved plan. Output paths are relative to the bindings directory, create-new/no-clobber by default, and may be replaced only with explicit `--overwrite`. Symlink escapes and collisions with the bindings input or selected QA-018 source files are rejected.

Generated plans and evidence bundles remain external artifacts and must not be committed.

## Ownership boundary

The bridge does not:

- parse OTBM or rebuild the World Index;
- parse arbitrary runtime logs or discover selectors;
- classify or reclassify OTBM Physical E2E failures;
- diagnose runtime root cause;
- validate source-report semantics beyond QA-018 identity/extraction checks;
- run Reachability/BFS or regenerate routes/preflight;
- run or retry Physical E2E;
- control Canary, MariaDB or OTClient;
- mutate maps, datapacks, reports or assets;
- generate feature-specific assertions, repair instructions or `NEXT_ACTION`.

Runtime/E2E owners keep runtime classification and acceptance ownership. OWA-004 returns only compact exact compatible OTBM-owned static evidence for an explicit reviewed selector.
