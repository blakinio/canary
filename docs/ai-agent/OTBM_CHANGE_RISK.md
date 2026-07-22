# OTBM Deterministic Change Risk Classification

`otbm_change_risk_tool.py` is a transparent review aid for one exact before/after map change. It does not decide whether a change is safe.

## Contracts

`canary-otbm-change-risk-policy-v1` declares visible non-negative integer weights for exactly these factors:

- critical infrastructure;
- identifier semantics;
- quest dependency paths;
- fragile routes;
- invalidated certification;
- multi-region impact;
- unresolved/conflicting dependency evidence;
- asset-driven walkability semantics.

The same policy declares strictly increasing thresholds for `low`, `medium`, `high` and `critical` (`low` starts at zero).

`canary-otbm-change-risk-input-v1` pins exact before/after map SHA-256 values. Each factor is `present`, `unresolved` or `absent` and retains exact source report format/hash plus finding IDs. Present or unresolved factors require evidence; omitted factors normalize to absent.

## Classification

Present and unresolved factors contribute their explicit policy weight. The report exposes every weight, contribution and evidence reference. Unresolved factors are listed separately so uncertainty can never silently lower the score.

The resulting `canary-otbm-change-risk-v1` includes the deterministic sum and threshold-derived level. No hidden model judgement participates in the result.

## Proof boundary

The classification:

- does not prove a gameplay regression;
- does not authorize skipping validation;
- does not authorize a repair;
- does not authorize merge;
- does not replace Map Quality, Semantic Diff, certification or Physical E2E gates.

Upstream validators remain responsible for producing the exact evidence represented by each factor.

## CLI

```sh
python tools/ai-agent/otbm_change_risk_tool.py \
  --policy risk-policy.json \
  --input risk-input.json \
  --output risk-report.json
```

Output is create-new/no-clobber by default. `--overwrite` performs atomic replacement. Symlink output and input/output aliases are rejected.
