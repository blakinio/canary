# Universal E2E factual coverage dashboard

## Contract

`canary-universal-e2e-coverage-dashboard-v1`, schema version `1`, is the read-only factual aggregation contract for `E2E-QRI-004`.

The implementation is `tools/e2e/coverage_dashboard.py`. It emits:

- one deterministic machine-readable JSON report validated by `docs/e2e/E2E_COVERAGE_DASHBOARD.schema.json`;
- one deterministic Markdown rendering generated from the same normalized report.

It does not execute a scenario, download a GitHub artifact, change artifact retention, create a workflow, or alter the canonical Universal Physical E2E lifecycle.

## Authoritative inputs

The dashboard uses two independent input populations:

1. **Current registered scenarios** from the existing `tools/e2e/run_agent_e2e.py:discover()` contract over `tests/e2e/scenarios/**/*.json`.
2. **Retained physical evidence** from explicit local directories containing extracted workflow artifacts and canonical `result.json` files.

Registration defines a reviewed scenario row. Registration, source files, documentation, artifact presence, or a declared maturity value do not prove execution.

A retained result contributes coverage only when it validates as:

- `canary-universal-e2e-result-envelope-v1`;
- schema version `3`;
- a complete canonical quality-dimension set;
- a valid run/scenario identity and timestamp.

Cleanup is recognized only when the envelope contains:

- `canary-universal-e2e-cleanup-certification-v1`;
- schema version `1`;
- a boolean `cleanup_certified` value consistent with the envelope's cleanup quality dimension.

Malformed or unsupported `result.json` files are retained under `invalid_evidence`; they never count as successful coverage.

## Factual aggregation rules

Rows are grouped only by the canonical `suite/scenario_id` key.

For every row the report preserves:

- whether the scenario is currently registered and its repository-relative source;
- all supplied valid result count boundaries;
- latest run;
- last successful run;
- last non-successful run;
- strongest proven M0-M5 maturity;
- all nine orthogonal quality dimensions;
- exact run, server revision, client revision, datapack, execution tier, timestamp and retained source reference for selected evidence;
- warnings and unknowns carried by retained envelopes;
- deterministic coverage gaps;
- current, stale, missing or not-evaluated freshness.

### Evidence maturity

The strongest proven maturity is selected only from successful valid envelopes.

A failed, cancelled or timed-out run remains visible but cannot promote maturity even when its manifest declared a higher M-level. `unknown` and `not_proven` are not M0-M5 proof.

### Quality dimensions

M0-M5 and quality dimensions remain independent.

For each quality dimension the dashboard selects the latest retained run that actually evaluated that dimension. If no supplied run evaluated it, the dashboard reports `not-evaluated`. It does not derive one dimension from another and does not calculate an overall score.

Canonical dimensions:

- determinism;
- stability;
- resilience;
- exactly-once;
- concurrency;
- cleanup;
- performance;
- compatibility;
- diagnostics.

Canonical states:

- `not-evaluated`;
- `pass`;
- `fail`;
- `unstable`;
- `blocked`.

### Freshness

The build requires an explicit timezone-aware `--as-of` timestamp.

`--stale-after-days` is optional:

- with a threshold, the latest retained run is `current` or `stale`;
- without a threshold, freshness is `not-evaluated`;
- with no valid retained run, freshness is `missing`.

The dashboard does not invent a project retention duration. Evidence collection and retention remain external to this contract.

## CLI

Build JSON and Markdown from one or more extracted artifact roots:

```sh
python tools/e2e/coverage_dashboard.py build \
  --repo-root . \
  --evidence-root /path/to/extracted-run-1 \
  --evidence-root /path/to/extracted-run-2 \
  --as-of 2026-07-24T17:00:00Z \
  --stale-after-days 30 \
  --json-output artifacts/e2e-coverage/dashboard.json \
  --markdown-output artifacts/e2e-coverage/dashboard.md
```

Validate an existing JSON report:

```sh
python tools/e2e/coverage_dashboard.py validate artifacts/e2e-coverage/dashboard.json
```

Regenerate Markdown from a validated JSON report:

```sh
python tools/e2e/coverage_dashboard.py render \
  artifacts/e2e-coverage/dashboard.json \
  --output artifacts/e2e-coverage/dashboard.md
```

Generated reports belong under `artifacts/**` or another approved temporary output directory and are not committed by this contract.

## Safety and non-goals

The dashboard:

- does not create another runner, lifecycle or workflow;
- does not run or retry scenarios;
- does not download or retain GitHub artifacts;
- does not infer proof from scenario registration, documentation or file presence;
- does not treat a failed run's declared maturity as proven maturity;
- does not infer cleanup from gameplay success;
- does not hide failed attempts, invalid evidence, warnings or unknowns;
- does not emit absolute input paths in the report;
- does not calculate an opaque health or coverage score;
- does not modify Canary, OTClient, MariaDB, maps, datapacks or runtime state.

A later task may add a scheduled artifact-collection seam only after an explicit retention and selection policy is reviewed. That collection concern must remain separate from this pure aggregation contract.
