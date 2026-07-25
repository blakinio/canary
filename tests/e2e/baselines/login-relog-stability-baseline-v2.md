# Physical login/relog stability baseline v2 — immutable execution manifest

Status: measurement in progress  
Task: `CAN-20260726-e2e-qri-022-login-relog-baseline-v2`  
Pull request: `#948`  
Repair base: `ad647f040a0f0b5b515c2416bf8aa11705dd7e8e`

## Exact measurement cell

- Workflow: `Universal Agent E2E`
- Scenario: `login/relog`
- Scenario manifest: `tests/e2e/scenarios/login/scenario.json`
- Canary source: PR #948 exact merge ref generated from the frozen head containing this file
- Maintained OTClient: scenario-pinned exact SHA
- Datapack: `data-otservbr-global`
- Execution tier: `pr-required`
- Required retained population: exactly `10`
- QRI-022 `minimum_runs`: `10`

## Collection procedure

1. The initial PR-triggered physical job is attempt 1.
2. Attempts 2 through 10 are sequential reruns of that physical job only.
3. No repository commit is allowed after this manifest lands and before all ten attempts are retained.
4. Every observed attempt belongs to the population regardless of success, failure or cancellation.
5. Every attempt must produce a unique retained artifact with:
   - schema-v3 `result.json`;
   - schema-v1 `cleanup-certification.json`;
   - `physical-exit-code.txt`;
   - exact server and OTClient revisions;
   - GitHub artifact ID and digest.
6. Missing, duplicate or incomparable evidence blocks certification; it is not replaced by a later success.
7. The historical population from PR #925 is excluded.

## Classification rule

The final report is produced by `tools/e2e/stability_certification.py` over exactly the ten extracted evidence roots with `--minimum-runs 10`.

- all ten attempts pass gameplay and cleanup: `pass`;
- mixed pass/failure population: `unstable`;
- all ten attempts fail: `fail`;
- fewer than ten complete attempts: `not-evaluated`;
- missing, duplicate or cross-cell evidence: programme-level `blocked`.

This file does not alter scenario semantics, workflow behavior, runner behavior, retention policy, scheduling or runtime code.
