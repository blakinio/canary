# Login/relog stability baseline 2026-07-26

Status: **blocked / not evaluated**.

## Measurement contract

- Workflow run: `30198264756` on measurement head `540a4e68cafb04fa00e963e39b05b75715bc8b38`.
- Scenario: `login/relog`.
- Controlled Canary/server revision: `ec0d815570415a4c7ca7217e3e2aca41f6023dab`.
- Maintained OTClient revision: `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`.
- Datapack: `data-otservbr-global`.
- Execution tier: `pr-required`.
- Population: exactly ten sequential attempts; no attempt was replaced and no attempt 11 was executed.
- Historical attempts from PR #925 are excluded.

## Attempt ledger

| Attempt | Physical job | Job outcome | Evidence artifact | Artifact digest | Retained evidence |
|---:|---:|---|---:|---|---|
| 1 | `89785787418` | success | `8631128171` | `sha256:8cf22c72184fb3158e2b23327ff4787e3af400b66ec045682fba993e3aaf385e` | schema-v3 success; cleanup certified; exit 0 |
| 2 | `89786507692` | success | `8631210383` | `sha256:0e62b255c21cb14ed689c3531d37d8cd00bc5b46f99e74f6f3567fc1cc719627` | schema-v3 success; cleanup certified; exit 0 |
| 3 | `89787210002` | success | `8631297049` | `sha256:541fc3285acc4d59d83bf12775392eb26788b609cc982ce3355bec7f6dc3c7c2` | schema-v3 success; cleanup certified; exit 0 |
| 4 | `89787937779` | success | `8631371934` | `sha256:b861e1fddc489c7b32d1bb139cf1f70b92bd510729de6bed129d5f0c5771ca4b` | schema-v3 success; cleanup certified; exit 0 |
| 5 | `89788722842` | success | `8631478129` | `sha256:7bc5c0d8e593f2ade964e20ed4a84436376036c4bb62c9753ca537b7f4a9bb09` | schema-v3 success; cleanup certified; exit 0 |
| 6 | `89789583264` | success | `8631572479` | `sha256:ad4cc7100e5492e5045f85d9d507f5579340cae8233ca31543cd7298893b7010` | schema-v3 success; cleanup certified; exit 0 |
| 7 | `89790410623` | success | `8631662170` | `sha256:49ec7ca3e24d5fe14c4b60c649d9d5d25cc8d2d8ee5ff8d3d4bcaa2cdefb0ba6` | schema-v3 success; cleanup certified; exit 0 |
| 8 | `89815467932` | failure | `8634324416` | `sha256:fe68fa2e4a7f6d0021353733e2d21f5507104a341e22572fc1d95f7cdef01597` | pre-lifecycle `download-artifact` failure; no result.json or cleanup certification |
| 9 | `89816228951` | failure | `8634412535` | `sha256:e443ba549ef21754e1c4b148ee27a412a1b566bba5ad1706ba40329e812aeb5d` | pre-lifecycle `download-artifact` failure; no result.json or cleanup certification |
| 10 | `89817061499` | failure | `8634518646` | `sha256:de3fcceebfc6d191885077369d20531998ff60c33fee064ae59083af79ed5ac3` | pre-lifecycle `download-artifact` failure; no result.json or cleanup certification |

## Factual result

- Attempts 1–7 are complete clean passes in one exact certification cell.
- Attempts 8–10 failed before the physical lifecycle at `Download exact-head Canary binary`.
- The upload step retained partial artifacts for attempts 8–10, but those artifacts contain no schema-v3 `result.json` and no schema-v1 cleanup certification.
- The missing result and cleanup records are not synthesized, promoted or hidden.
- QRI-022 therefore discovers seven valid result envelopes from ten preserved artifact roots.
- With explicit `minimum_runs=10`, the certification state is `not-evaluated` with reason `insufficient-runs`; this population does not prove stability.

## Complete-cell statistics

- Cell ID: `b262885c08b70ee4d9d6`.
- Clean passes: `7`.
- Counted QRI attempts: `7`.
- Duration minimum: `50481 ms`.
- Nearest-rank p50: `57112 ms`.
- Nearest-rank p95: `63409 ms`.
- Maximum: `63409 ms`.

## First divergence

The controlled-server physical job builds `CONTROLLED_SERVER_BIN`, but the workflow still unconditionally executes `actions/download-artifact` for `canary-linux-release`. The later executable resolution already prefers `CONTROLLED_SERVER_BIN`, so this download is unnecessary for controlled-server scenarios. Attempts 8–10 consistently stopped at that redundant download before gameplay and cleanup evidence generation.

## Evidence boundary

- JSON certification: `docs/e2e/baselines/e2e-login-relog-stability-baseline-20260726.json`.
- Rendered certification: `docs/e2e/baselines/E2E_LOGIN_RELOG_STABILITY_BASELINE_20260726.md`.
- The JSON contract reports only valid schema-v3 envelopes; this dossier preserves the three resultless workflow failures separately.

## Conclusion

This ten-attempt collection is a factual blocked baseline, not a stability pass. A dedicated workflow fix must remove the redundant controlled-server artifact download and retain a fail-closed pre-lifecycle result before any fresh certification population is started.
