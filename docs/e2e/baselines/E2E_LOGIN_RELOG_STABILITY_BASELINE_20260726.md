# Universal E2E stability certification

- Contract: `canary-universal-e2e-stability-certification-v1` schema 1
- Generated at: `2026-07-26T16:50:00.000Z`
- Explicit minimum runs: `10`
- Certification cells: `1`
- Counted attempts: `7`
- Invalid result files: `0`
- Duplicate attempt identities: `0`

A pass requires every counted attempt to have gameplay status `success` and exact cleanup certification `pass`. Mixed evidence is `unstable`; no retry is hidden.

## Certification cells

| Scenario | Cell | State | Runs | Clean pass | Failed | Blocked | Ratio | Cleanup failures | p50 / p95 ms |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| login/relog | `b262885c08b70ee4d9d6` | not-evaluated | 7 | 7 | 0 | 0 | 1.000000 | 0 | 57112 / 63409 |

## Evidence details

### login/relog / `b262885c08b70ee4d9d6`

- State: **not-evaluated** (`insufficient-runs`)
- Provenance: server `ec0d815570415a4c7ca7217e3e2aca41f6023dab`, client `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`, datapack `data-otservbr-global`, tier `pr-required`
- Failure classes: `{}`
- First divergences: `{}`

Unknowns:
- No route-plan identity was present for this run; the scenario may not use routed execution.
- Scenario evidence maturity is not declared in the current scenario manifest.

Attempts:
- `github-30198264756-1-login-relog#1`: clean-pass, status=success, cleanup=certified, duration_ms=54639, source=`evidence-1:result.json`
- `github-30198264756-2-login-relog#2`: clean-pass, status=success, cleanup=certified, duration_ms=58476, source=`evidence-2:result.json`
- `github-30198264756-3-login-relog#3`: clean-pass, status=success, cleanup=certified, duration_ms=59542, source=`evidence-3:result.json`
- `github-30198264756-4-login-relog#4`: clean-pass, status=success, cleanup=certified, duration_ms=57112, source=`evidence-4:result.json`
- `github-30198264756-5-login-relog#5`: clean-pass, status=success, cleanup=certified, duration_ms=63409, source=`evidence-5:result.json`
- `github-30198264756-6-login-relog#6`: clean-pass, status=success, cleanup=certified, duration_ms=50481, source=`evidence-6:result.json`
- `github-30198264756-7-login-relog#7`: clean-pass, status=success, cleanup=certified, duration_ms=56317, source=`evidence-7:result.json`

No opaque stability score is calculated.
