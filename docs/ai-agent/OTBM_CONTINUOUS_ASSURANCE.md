# OTBM Continuous Assurance Gate

`OTBM-QA-007` is a read-only fail-closed orchestration layer over existing OTBM evidence.

It does not rerun Semantic Diff, OTBM validators, Physical E2E, World Health, or QA-006 certification. It verifies one exact evidence chain and emits an auditable gate result.

## Inputs

- `canary-otbm-continuous-assurance-execution-v1` — an explicit execution ledger for the validators and Physical E2E scenarios selected by the regression plan.
- `canary-otbm-map-change-regression-v1` — QA-002 deterministic static and represented Physical E2E selection.
- before/after `canary-otbm-world-health-v1`.
- before/after `canary-otbm-region-quest-certification-v1`.

Every input file is read stably and SHA-256 pinned. The execution ledger also pins the exact regression, health, and certification reports it belongs to.

## Gate rules

The gate passes only when all represented requirements are satisfied:

1. The regression plan's before/after map and World Index identities exactly match both World Health and both Certification reports.
2. Execution-ledger static validator IDs exactly equal `regression.staticValidation.selected`; every selected validator has status `passed`.
3. The gate blocks when the QA-002 static selection remains `failClosed`.
4. Execution-ledger Physical E2E `(suite,id)` pairs exactly equal the selected QA-002 physical scenarios; every selected scenario has status `passed`.
5. Manual physical selection requirements block the gate.
6. Explicit World Health problem counts must not increase:
   - structural findings;
   - runtime-handler placement findings;
   - attention mechanics;
   - stale evidence targets;
   - missing Physical E2E scenario targets;
   - targets not physically proven on the current map.
7. A target represented in before-certification must still exist after the change; its C0-C7 level must not decrease and its after state must not be stale.

The output includes exact validation references, per-dimension World Health deltas, per-target certification deltas, and deterministic blocker codes.

## Execution ledger

The execution ledger is intentionally an orchestration input rather than another runner. It records the exact evidence hash and status for each selected validator and Physical E2E scenario. QA-007 validates the selected-set identity and fails closed on missing, extra, failed, or not-run entries.

This keeps execution ownership with the existing validators and Universal Physical E2E while giving the OTBM assurance layer one compact, auditable result boundary.

## Non-claims

- A passed gate applies only to represented OTBM evidence.
- It never suppresses unrelated non-OTBM suites.
- It does not authorize deployment or promotion.
- It does not infer runtime success from static evidence.
- It does not invent missing validator or scenario results.
- It does not create a second parser, validator, pathfinder, E2E runner, or workflow.

## CLI

```bash
python tools/ai-agent/otbm_continuous_assurance_tool.py \
  --execution-ledger /path/to/execution.json \
  --regression-plan /path/to/regression.json \
  --before-world-health /path/to/before-health.json \
  --after-world-health /path/to/after-health.json \
  --before-certification /path/to/before-certification.json \
  --after-certification /path/to/after-certification.json \
  --output /path/to/assurance.json
```

Outputs are create-new by default. `--overwrite` performs an explicit atomic replacement of a regular output file and never allows an input file to be overwritten or aliased.
