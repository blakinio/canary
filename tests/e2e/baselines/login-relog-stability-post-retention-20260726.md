# Login/relog post-retention stability baseline 2026-07-27

Status: **unstable**.

## Measurement contract

- Workflow run: `30220474091` on frozen measurement head `d576d7116b8fe74d9fe777bf697130c2179f767c`.
- Scenario: `login/relog`.
- Controlled Canary/server revision: `7a09367589dfc08e482edadbe77e556ecf0cfaa7`.
- Maintained OTClient revision: `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`.
- Datapack: `data-otservbr-global`.
- Execution tier: `pr-required`.
- Population: exactly ten sequential attempts; no failed attempt was replaced and no attempt 11 was executed.
- Historical population from PR #961 and pre-population administrative runs are excluded.

## Attempt ledger

| Attempt | Physical job | Job outcome | Evidence artifact | Artifact digest | Retained evidence |
|---:|---:|---|---:|---|---|
| 1 | `89845173184` | success | `8637478045` | `sha256:c96c665113fa2329a116019d31e33b012ca04dbe27bcfd641f85305c7d661fb3` | schema-v3 success; cleanup certified; duration `57253 ms` |
| 2 | `89846323879` | success | `8637588427` | `sha256:88f69e91c89854746e9ed9d3934e7312ca43e08ede5906da1c148792fc6a6411` | schema-v3 success; cleanup certified; duration `58244 ms` |
| 3 | `89847097395` | success | `8637670465` | `sha256:89e0fdb6c565161af6d0cc36633a9de8eb5d7d3043e9daaea86aa414df1d5e33` | schema-v3 success; cleanup certified; duration `57182 ms` |
| 4 | `89847910808` | success | `8637756621` | `sha256:ed23dc6bd5377d97ad55248329e245bca86cc21c3d0d251974d5f5f7c30320ec` | schema-v3 success; cleanup certified; duration `69134 ms` |
| 5 | `89848764820` | success | `8637846773` | `sha256:4b8bf15b460d79ae52d2c91e027c54bb65837ae6d50d3b84fe439fda235b447e` | schema-v3 success; cleanup certified; duration `54538 ms` |
| 6 | `89849469093` | success | `8637931139` | `sha256:f0db840ab547c1e81889b6ff0330eb7312a6a7d7d1b17a6497c62f9ceaab74d8` | schema-v3 success; cleanup certified; duration `55930 ms` |
| 7 | `89850192014` | success | `8638010664` | `sha256:5c639a2acd43de6d45b18a5ffe086fd0c74c63e18e4d18252f7e4e0584975433` | schema-v3 success; cleanup certified; duration `57894 ms` |
| 8 | `89851152772` | failure | `8638107541` | `sha256:dc6ac4a5271faf2109a98337b853f968526ffdd64dd17474bfda7d35b0897d3f` | schema-v3 failure; cleanup unavailable; `client_build_startup` / infrastructure |
| 9 | `89915320695` | success | `8645497174` | `sha256:f1c6b4bc6d3b777a638dee6f3b6213f91b46233b9de69d02519bec23019c71fe` | schema-v3 success; cleanup certified; duration `54381 ms` |
| 10 | `89918290580` | success | `8645904794` | `sha256:5df199c21f62b3e9f787319bac2792aa649db8a6d77055d49d79456283a944e7` | schema-v3 success; cleanup certified; duration `59430 ms` |

## Factual result

- Nine attempts are complete clean passes in one exact certification cell.
- Attempt 8 is a retained fail-closed schema-v3 infrastructure failure before gameplay because the controlled OTClient artifact could not be downloaded.
- Attempt 8 has no valid schema-v1 cleanup certification; the missing cleanup evidence remains visible and is not synthesized.
- QRI-022 consumes exactly ten extracted artifact roots with explicit `minimum_runs=10`.
- The resulting state is `unstable` / `mixed-outcomes`, not `pass`.

## Certification statistics

- Cell ID: `befa7d114a6a18cfa7c8`.
- Counted attempts: `10`.
- Clean passes: `9`.
- Failed attempts: `1`.
- Clean success ratio: `0.900000`.
- Cleanup-unknown attempts: `1`.
- Duration minimum: `54381 ms`.
- Nearest-rank p50: `57253 ms`.
- Nearest-rank p95: `376610 ms`.
- Maximum: `376610 ms`.

## First divergence

- Failure class: `client_build_startup`.
- Failure category: `infrastructure`.
- First divergence: `client-configuration/phase:client-configuration`.
- The failure occurred at `Download controlled OTClient binary`; the physical gameplay lifecycle did not start for attempt 8.

## Evidence boundary

- JSON certification: `docs/e2e/baselines/e2e-login-relog-stability-post-retention-20260726.json`.
- Rendered certification: `docs/e2e/baselines/E2E_LOGIN_RELOG_STABILITY_POST_RETENTION_20260726.md`.
- This dossier preserves the workflow/job/artifact ledger separately from the schema-level certification.
- Historical blocked evidence from PR #961 remains unchanged.

## Conclusion

The controlled-server download repair removed the former redundant Canary-artifact blocker, but this factual population is still unstable because one of ten counted attempts failed during controlled OTClient artifact acquisition. The result must not be promoted to a stability pass.
