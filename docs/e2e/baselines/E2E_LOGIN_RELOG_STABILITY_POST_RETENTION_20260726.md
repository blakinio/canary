# Universal E2E stability certification

- Contract: `canary-universal-e2e-stability-certification-v1` schema 1
- Generated at: `2026-07-27T08:02:48.280Z`
- Explicit minimum runs: `10`
- Certification cells: `1`
- Counted attempts: `10`
- Invalid result files: `0`
- Duplicate attempt identities: `0`

A pass requires every counted attempt to have gameplay status `success` and exact cleanup certification `pass`. Mixed evidence is `unstable`; no retry is hidden.

## Certification cells

| Scenario | Cell | State | Runs | Clean pass | Failed | Blocked | Ratio | Cleanup failures | p50 / p95 ms |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| login/relog | `befa7d114a6a18cfa7c8` | unstable | 10 | 9 | 1 | 0 | 0.900000 | 0 | 57253 / 376610 |

## Evidence details

### login/relog / `befa7d114a6a18cfa7c8`

- State: **unstable** (`mixed-outcomes`)
- Provenance: server `7a09367589dfc08e482edadbe77e556ecf0cfaa7`, client `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`, datapack `data-otservbr-global`, tier `pr-required`
- Failure classes: `{"client_build_startup": 1}`
- First divergences: `{"client-configuration/phase:client-configuration": 1}`

Unknowns:
- Cleanup is observed only and is not QRI-006 certified.
- No route-plan identity was present for this run; the scenario may not use routed execution.
- Scenario evidence maturity is not declared in the current scenario manifest.

Attempts:
- `github-30220474091-1-login-relog#1`: clean-pass, status=success, cleanup=certified, duration_ms=57253, source=`evidence-1:result.json`
- `github-30220474091-2-login-relog#2`: clean-pass, status=success, cleanup=certified, duration_ms=58244, source=`evidence-2:result.json`
- `github-30220474091-3-login-relog#3`: clean-pass, status=success, cleanup=certified, duration_ms=57182, source=`evidence-3:result.json`
- `github-30220474091-4-login-relog#4`: clean-pass, status=success, cleanup=certified, duration_ms=69134, source=`evidence-4:result.json`
- `github-30220474091-5-login-relog#5`: clean-pass, status=success, cleanup=certified, duration_ms=54538, source=`evidence-5:result.json`
- `github-30220474091-6-login-relog#6`: clean-pass, status=success, cleanup=certified, duration_ms=55930, source=`evidence-6:result.json`
- `github-30220474091-7-login-relog#7`: clean-pass, status=success, cleanup=certified, duration_ms=57894, source=`evidence-7:result.json`
- `github-30220474091-8-login-relog#8`: failed, status=failure, cleanup=missing, duration_ms=376610, source=`evidence-8:result.json`
- `github-30220474091-9-login-relog#9`: clean-pass, status=success, cleanup=certified, duration_ms=54381, source=`evidence-9:result.json`
- `github-30220474091-10-login-relog#10`: clean-pass, status=success, cleanup=certified, duration_ms=59430, source=`evidence-10:result.json`

No opaque stability score is calculated.
