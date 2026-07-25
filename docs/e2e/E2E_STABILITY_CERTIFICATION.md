# Universal E2E stability certification

`tools/e2e/stability_certification.py` builds the deterministic `canary-universal-e2e-stability-certification-v1` schema-version-1 report from explicitly supplied extracted Universal E2E artifact roots.

The tool is a read-only evidence consumer. It does not execute scenarios, retry failures, discover or download GitHub artifacts, schedule nightly work, set retention, mutate runtime state or replace the canonical physical lifecycle.

## Authoritative inputs

Each discovered `result.json` must validate as:

- `canary-universal-e2e-result-envelope-v1`;
- schema version 3;
- with cleanup interpreted only through complete `canary-universal-e2e-cleanup-certification-v1` schema-version-1 validation and exact agreement with the cleanup quality dimension.

Discovery and current-envelope normalization reuse `tools/e2e/coverage_dashboard.py`. Absolute, traversing or evidence-root-escaping result paths remain invalid evidence and are never counted.

The caller supplies one or more already extracted local artifact roots. Collection, execution, artifact download, retention and selection of the physical baseline remain external to this contract.

## Certification cell

Runs are comparable only inside the same exact cell:

- scenario (`suite/scenario_id`);
- Canary/server revision;
- maintained OTClient revision;
- datapack identity;
- execution tier.

A missing or `unknown` comparability value blocks the cell. Evidence from different cells is reported separately and is never pooled to reach the minimum run count.

The cell identifier is a deterministic digest over the full scenario and provenance values. The full values remain present in the report; the identifier is not a confidence score.

## Counted attempts

The schema-v3 result envelope's `attempt_history` is expanded so an earlier failed attempt cannot disappear behind a later successful result.

The current attempt uses the exact top-level status, timestamps, duration, failure evidence and cleanup certification. Historical failed attempts remain failures. A historical successful attempt that lacks independent cleanup certification is retained but blocks certification rather than being promoted to a clean pass.

Duplicate `(scenario, run_id, attempt)` identities are retained with every source occurrence and block every affected cell. They are not silently deduplicated or counted twice as valid independent evidence.

## Classification

The caller chooses an explicit positive `minimum_runs` value. The CLI default is 10.

| State | Factual rule |
|---|---|
| `pass` | The cell meets the explicit minimum and every counted attempt has gameplay status `success` plus exact cleanup certification pass. |
| `unstable` | The minimum is met and the cell contains a mixture of clean passes and failed attempts. `9/10` is therefore unstable. |
| `fail` | The minimum is met and no counted attempt is a clean pass. |
| `not-evaluated` | Comparable complete evidence exists, but fewer than the explicit minimum attempts are present. |
| `blocked` | Provenance is incomplete, an attempt identity is duplicated, or a historical successful attempt lacks independent cleanup certification. |

A gameplay-success result with cleanup failure is a failed attempt for clean stability certification. Gameplay and cleanup remain separately visible in each attempt.

## Reported facts

Each certification cell includes:

- total counted attempts;
- clean pass, failed and blocked attempt counts;
- clean success ratio;
- cleanup failure and cleanup-unknown counts;
- exact failure-class distribution;
- exact first-divergence distribution;
- deterministic duration minimum, nearest-rank p50, nearest-rank p95 and maximum;
- exact ordered attempt references and sources;
- duplicate identities, missing provenance, warnings and unknowns.

The summary aggregates factual counts and state distribution. No opaque stability score is calculated.

## CLI

Build JSON and Markdown from one or more extracted evidence roots:

```sh
python3 tools/e2e/stability_certification.py build \
  --evidence-root /path/to/extracted/run-set-a \
  --evidence-root /path/to/extracted/run-set-b \
  --as-of 2026-07-25T10:00:00+02:00 \
  --minimum-runs 10 \
  --output-json /tmp/e2e-stability.json \
  --output-markdown /tmp/e2e-stability.md
```

Validate an existing report:

```sh
python3 tools/e2e/stability_certification.py validate /tmp/e2e-stability.json
python3 -m json.tool docs/e2e/E2E_STABILITY_CERTIFICATION.schema.json >/dev/null
```

Render Markdown from the validated JSON contract:

```sh
python3 tools/e2e/stability_certification.py render \
  /tmp/e2e-stability.json \
  --output /tmp/e2e-stability.md
```

## Evidence boundary

This package proves deterministic representation and classification of supplied retained evidence. Unit tests prove the contract implementation, including the required `9/10 -> unstable` behavior and fail-closed cases.

It does not by itself prove that any current physical scenario is stable. The first real stability baseline requires a separately selected physical scenario and retained artifact population produced through the existing canonical Universal E2E lifecycle. That baseline must preserve every run and may not promote missing or synthetic evidence into physical success.
