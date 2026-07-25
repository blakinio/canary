# OAM-050 Physical-Client E2E revalidation

## Final disposition

```text
physical-client-e2e → DO_NOT_MIGRATE
```

Universal Physical-Client E2E remains the canonical Canary-hosted validation platform. It owns exact controlled-server and maintained-client selection, disposable database lifecycle, physical OTClient automation, scenario execution, deterministic evidence and cleanup. Otheryn is a controlled server target for that platform, not the owner of a second orchestrator.

## Evidence

- Canary preflight PR #944 passed exact-head Ownership `30176758049` and full CI `30176758136`, then merged as `515af061dda97173cb5ac6cc7885b7cdc3c4504f`.
- Otheryn disposition PR #113 passed Required `30177667228` and merged as `92cc602332f0ea86dbb669541020112c299ec66c`.
- Otheryn lifecycle PR #114 passed Required `30177733797` and merged as `ff90e93d872b6b47720f711483a9832203d5258d`.
- The target added no runtime, build, startup, workflow, E2E runner, controlled-client harness, evidence schema, database fixture system or deployment path.
- Universal Agent E2E already accepts `blakinio/Otheryn` as a controlled server repository with an exact 40-character `server_ref`.
- Canary PR #925 remains authoritative for its original first login/relog repeated-run population: nine complete clean attempts were retained, while the tenth failed without a retained result envelope or cleanup certification.
- The separate E2E repair PR #940 delivered and lifecycle-closed failure evidence retention as `ad647f040a0f0b5b515c2416bf8aa11705dd7e8e`, with controlled success and failure proofs for the `capture → upload → propagate` sequence.

## Retained programme boundary

The Universal E2E programme remains active in Canary. Generic orchestration, lifecycle, retention, cleanup and evidence-contract changes require separate bounded E2E-platform tasks. Feature programmes may own scenarios and assertions but must not create parallel runners or workflows.

The failure/cancellation evidence-retention defect observed by PR #925 is repaired on current Canary `main`. The original incomplete ten-attempt population remains historically blocked and must not be retroactively reclassified or replaced. Repeating the baseline is separate E2E work requiring a fresh ownership preflight and newly retained attempts; neither the repair nor a future repeat creates Otheryn runtime ownership or changes the OAM-050 disposition.

## Target consumption model

Future Otheryn packages may request physical-client proof by selecting an exact target SHA through the canonical Canary workflow and by supplying separately governed feature-owned scenarios or assertions when needed. The platform remains external validation infrastructure and its results are additive to unit, integration, runtime, persistence and protocol evidence.

## Nonclaims

OAM-050 does not claim complete gameplay coverage, general stability, compatibility with every server/client/datapack combination, successful retention under every possible infrastructure failure, completion of a replacement ten-attempt baseline, production deployment readiness, or that static and unit evidence replace exact-revision physical-client execution.