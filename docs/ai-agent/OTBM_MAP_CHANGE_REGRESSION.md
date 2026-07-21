# OTBM Map Change Regression Guard

`OTBM-QA-002` adds a deterministic read-only composition layer that turns already-produced OTBM change evidence into an impacted-validation plan.

Public report contract:

- format: `canary-otbm-map-change-regression-v1`;
- schema: `docs/ai-agent/OTBM_MAP_CHANGE_REGRESSION.schema.json`;
- implementation: `tools/ai-agent/otbm_map_change_regression.py`;
- CLI: `tools/ai-agent/otbm_map_change_regression_tool.py`.

## Ownership boundary

The guard does **not** parse or scan OTBM, build World Indexes, recompute Semantic OTBM Diff, resolve scripts, calculate routes, render maps, write or mutate maps, select Physical E2E scenarios independently, run Physical E2E, or suppress unrelated repository validation.

It composes two existing evidence surfaces only:

1. one required `canary-otbm-semantic-diff-v1` report;
2. zero or one compatible `canary-otbm-e2e-impacted-selection-v1` report produced by OTBM-E2E-008.

Generated regression reports stay outside Git.

## Provenance contract

Every accepted input is supplied with a stable file pin containing filename, byte size, SHA-256 and format. The report preserves exact before/after source-map and World Index SHA-256 identities from Semantic Diff.

When impacted-selection evidence is provided, it must match the exact Semantic Diff before/after map hashes, World Index hashes, scope type, finding total and truncation state. Its recorded Semantic Diff SHA-256 must equal the actual supplied Semantic Diff input pin.

Mismatched or malformed evidence fails closed.

## Static validation policy

The report exposes seven existing OTBM-aware static validation surfaces:

- `otbm-geometry-audit`;
- `otbm-reachability`;
- `otbm-script-resolution`;
- `quest-map-validation`;
- `otbm-spawn-npc-validation`;
- `otbm-storage-dependency-graph`;
- `otbm-map-quality`.

A static validator may be skipped only when an exact **full-index**, non-truncated Semantic Diff proves zero OTBM findings.

Any changed, bounded, truncated, unknown-position, unresolved, conflicting, invalid or unknown-kind evidence selects validation rather than authorizing a skip. Selected entries retain the exact sampled Semantic Diff finding IDs and explicitly state whether that ID set is complete.

This is intentionally conservative. A selected validator is an impacted-validation requirement, not proof that the validator will fail.

## Physical E2E policy

The guard never rebuilds OTBM-E2E-008 route/scenario impact logic.

When an impacted-selection report is supplied, its selected/skipped decisions are reused. Every selected scenario preserves its exact `impactedFindingIds` from Semantic Diff.

A skipped Physical E2E scenario is accepted only when all of the following remain true:

- the Semantic Diff is full-index;
- findings are not truncated;
- the scenario is not fail-closed;
- the scenario retains reason `EXACT_FULL_INDEX_DIFF_PROVES_NON_IMPACT`;
- the scenario has no impacted Semantic Diff finding IDs;
- every baseline route entry is compatible and SHA-pinned.

Without compatible OTBM-E2E-008 evidence, the report sets `manualSelectionRequired=true` and `canSkipAny=false`. Missing evidence therefore selects more review rather than silently proving non-impact.

## Scope and uncertainty

Bounded-region Semantic Diff is valid change evidence but cannot prove global non-impact. Likewise, truncated findings, missing finding positions and unresolved/conflicting evidence cannot authorize skips.

The report records deterministic sampled impact positions, per-floor sampled bounding regions and mechanic-change samples. These are evidence summaries only; they do not infer visual intent, player intent or gameplay correctness.

Unrelated non-OTBM suites are never suppressed by this guard.

## CLI

Example:

```bash
python tools/ai-agent/otbm_map_change_regression_tool.py \
  --semantic-diff artifacts/semantic-diff.json \
  --impacted-selection artifacts/impacted-selection.json \
  --output artifacts/map-change-regression.json
```

`--impacted-selection` is optional. Omitting it leaves Physical E2E selection explicitly manual and does not authorize any Physical E2E skip.

Outputs are create-new by default. Use `--overwrite` only for an explicitly intended replacement. Input symlinks, duplicate input files, output/input collisions, output symlinks and implicit clobbering are rejected.

## Interpretation

A green or empty regression plan does not prove gameplay correctness. It states only which existing validation surfaces may be skipped or must be selected under the exact supplied OTBM evidence.

The strongest skip authority in v1 is exact, current, full-index non-impact evidence. Visual similarity, names, nearby coordinates, expected intent and selected-scope absence never authorize a skip.
