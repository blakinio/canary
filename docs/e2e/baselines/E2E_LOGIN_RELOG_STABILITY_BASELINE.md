# Login/relog repeated-run stability baseline

## Factual outcome

**Overall baseline population: `BLOCKED`.**

The retained QRI-022 certification cell contains nine complete clean passes and is therefore `not-evaluated` against the explicit minimum of ten. The tenth required physical attempt failed, but the workflow did not retain its `result.json` or cleanup certification. The missing failed-attempt envelope prevents a truthful `pass`, `unstable`, or `fail` classification for the complete intended population.

A later diagnostic rerun is preserved as separate workflow evidence and does not replace attempt 10. It was cancelled in the same physical step and again retained no Universal E2E artifact.

## Exact comparable cell

- Scenario: `login/relog`
- Workflow run: `30167381956`
- Pull request: `#925`
- PR head: `ef5153d09a2dc70469daf360020b81986949bb69`
- Runtime server revision emitted by the PR run: `770bb4ba9bf9dbf2fd32c3342b30cd6ab93f991d`
- Maintained OTClient revision: `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`
- Datapack: `data-otservbr-global`
- Map SHA-256: `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2`
- Execution tier: `pr-required`
- Certification cell: `aa3660dd10a3cc8615e2`
- Explicit minimum: `10`

## Retained complete attempts

| Attempt | Physical job | Artifact | Artifact digest | `result.json` SHA-256 | Cleanup SHA-256 | Extracted-root digest | Duration ms |
|---:|---:|---:|---|---|---|---|---:|
| 1 | `89704918233` | `8622212268` | `sha256:0e114d3a99c68d8bc3ad0643f002a4ceeae5f46266cd06de34e8bfedbb6d1107` | `sha256:bfdf8e7276922ee65b29b53516765abbafbcc8d51be0b1f6cefbf06740c8a456` | `sha256:827b8962a9f245494b6dc35ff0409ca01179179d29cf10f6c0993809a823adb5` | `sha256:9452ee00177001f7d37ce75751df157ca20bde7ba2d0a4078395dc1bac87719b` | 57104 |
| 2 | `89705220969` | `8622244029` | `sha256:001870969bf5d4ac3b8d7ecdbc208c8335a63e696368ad3d781bac54d3f01bae` | `sha256:868fdb2b5ea28b00188b1ac317380eccfc63b8f779b51b9d3d934ce980e227db` | `sha256:af389491d77ab696bf4135c9adef15c34fb0da4a1a8e0357d22c0f532c3842b9` | `sha256:bc8d58d5df373cde556e61141a5d68c19f45eea0cdba8f2d3181ef005740b46b` | 59493 |
| 3 | `89705484870` | `8622271251` | `sha256:8a735f90114f94d610415bf108e79af7b42755143af031a4880eff73dff1837e` | `sha256:7a3bc19d95b8bc9be9bafd8f758389619b6e2db87f415c994f90eb1a352ea8fb` | `sha256:0af28abb3f73c2d632c3b8512f52d284eb81712bbe05d37184ab259d6029a22e` | `sha256:6cc295438fd694ff2fd526cf0a797eab55e667db2a7b980df66ebbf37a8c8bee` | 58861 |
| 4 | `89705778284` | `8622305211` | `sha256:05f5493ba86375f8799919bafd2420d0ed30cb4a6d77788646e2c04d7764504b` | `sha256:a2728dd3df47cb4895bb41e63b16dafdd3a897028272d8d29e655cf10c8223ac` | `sha256:c61dbbebc4fb824282044c75744a925e2a1412d4dca6cbd06091d226ab7439b5` | `sha256:da92012db9c111928c061c4e13594fe4b09acb7c900e7bb40412a5b2c3440fbc` | 60126 |
| 5 | `89706584280` | `8622389319` | `sha256:7bc112d3d78e75508ed211e5ea374131cb44128aaf8925c198cb49b14245b9e6` | `sha256:e051e7f6aaf914a3f1827ec49baf38a37a60f30094e7e3ada9865d7d06c2f207` | `sha256:0705b77075a09c18cca0535d6f11bea3e86355758f235dcea13ff8ad3b076dcd` | `sha256:8b9caaea49dd66f69455849c91e7f7756e5533874c66bacca2933c8eb8841cab` | 58714 |
| 6 | `89706922750` | `8622420067` | `sha256:98b6d92d96cdff8d7f4c4c5afc047738b5ab7a368b90e22719f18e33483a2638` | `sha256:367eefca58afc0d988b63ef7b80d873c1777a08c0c8a80e99973484f65f0dea4` | `sha256:287e10c6311ac1107dc4bf8f05e80feabe8d7e27a1a2d575daf5f08d6593fc1b` | `sha256:2150e3e9f760ae1be6eaf47a9e2a4185244bbe19a74d6d4666e70922ee053137` | 61885 |
| 7 | `89707250964` | `8622456978` | `sha256:1646487ad61b936c03da43b407d88bae05c0687a7e4549e19ee6cb39603d0807` | `sha256:13e979983b87a992f94ac9348ed7e9351a277ea7ebf61a355abc0d26b4800d8b` | `sha256:fb0bb9e3147c5794aeb7f78bda149bf7d5e53234079bc58d58f6c91747877c81` | `sha256:c4b5ab7c334d5db92b42daf4603c68b227bfa10e580a7bb89425c5eb7bffefc1` | 57503 |
| 8 | `89707742935` | `8622500072` | `sha256:ed91167fb951c0575480f911172b96ee20995c7edc5ca1799efde7d3ec3408c1` | `sha256:eb9ffce3ddd2291d246d9aeb5b114bab07ecd30665dec63ac3e7570049c8c45b` | `sha256:0d020e7c6f53857061eea472832765589a98199a9a7301e0f61c691d605be506` | `sha256:8400f97cb726e1267c920e4ee78fdf8d0d294b6c89591fa9c5f2bda738d5369c` | 58792 |
| 9 | `89708207358` | `8622546348` | `sha256:3fb5b3fbe57eb7d6d7aacd8ea25bb9e8df59ea25c2a8ae448fe712e265658a8e` | `sha256:2b326aac0688d919b6a4b7ab356c37e9ec96f36638b01bb2f3eaa33d16fb7bad` | `sha256:a42fc8786b07b7001030c85a3c5e619d000722f4216dceb6ac504b0f107f51f1` | `sha256:107b2339023aac4aefad8e3ac9f000ceb194763d728e451b3bc353c73a4cdc91` | 59692 |

All nine retained envelopes report:

- result contract `canary-universal-e2e-result-envelope-v1`, schema version `3`;
- gameplay status `success`;
- cleanup contract `canary-universal-e2e-cleanup-certification-v1`, schema version `1`;
- cleanup status `certified`;
- identical scenario and comparability provenance.

## Unretained required attempt

### Attempt 10

- Physical job: `89708625391`
- Physical scenario step: `failure`
- Required physical E2E job: `89708847588`
- Required result: `failure`
- Universal E2E artifact: **missing**
- Schema-v3 result envelope: **missing**
- Cleanup certification: **missing**
- Exact lower-level failure inside `run_physical_e2e.sh`: **UNKNOWN** from the retained connector-visible evidence.

The workflow declares the evidence-upload step with `if: always()`, but GitHub recorded that step as skipped after the physical failure. Therefore the original failed attempt cannot be normalized by QRI-022 and cannot be silently replaced.

### Diagnostic rerun — not a replacement

- Physical job: `89709267589`
- Physical scenario step: `cancelled`
- Required physical E2E job: `89709498686`
- Required result: `failure`
- Universal E2E artifact: **missing**
- Result envelope and cleanup certification: **missing**

No further rerun is counted or authorized for this baseline.

## Certification interpretation

The machine-readable QRI-022 report covers the nine explicit extracted roots that contain valid schema-v3 envelopes:

- cell state: `not-evaluated`;
- reason: `insufficient-runs`;
- runs: `9`;
- clean passes: `9`;
- success ratio among retained valid envelopes: `1.000000`;
- duration min / p50 / p95 / max: `57104 / 58861 / 61885 / 61885` ms.

This is not evidence of 100% stability. The intended ten-attempt population contains an unretained failed attempt, so the programme-level conclusion remains `BLOCKED` on failure-evidence retention.

## Boundary

This task does not alter the physical scenario, runner, workflow, retry policy, retention policy, scheduling, fixtures, or runtime. Repairing failure/cancellation evidence retention requires a separate narrow task and pull request.

## Generated QRI-022 certification

# Universal E2E stability certification

- Contract: `canary-universal-e2e-stability-certification-v1` schema 1
- Generated at: `2026-07-25T18:40:00.000Z`
- Explicit minimum runs: `10`
- Certification cells: `1`
- Counted attempts: `9`
- Invalid result files: `0`
- Duplicate attempt identities: `0`

A pass requires every counted attempt to have gameplay status `success` and exact cleanup certification `pass`. Mixed evidence is `unstable`; no retry is hidden.

## Certification cells

| Scenario | Cell | State | Runs | Clean pass | Failed | Blocked | Ratio | Cleanup failures | p50 / p95 ms |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| login/relog | `aa3660dd10a3cc8615e2` | not-evaluated | 9 | 9 | 0 | 0 | 1.000000 | 0 | 58861 / 61885 |

## Evidence details

### login/relog / `aa3660dd10a3cc8615e2`

- State: **not-evaluated** (`insufficient-runs`)
- Provenance: server `770bb4ba9bf9dbf2fd32c3342b30cd6ab93f991d`, client `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`, datapack `data-otservbr-global`, tier `pr-required`
- Failure classes: `{}`
- First divergences: `{}`

Unknowns:
- No route-plan identity was present for this run; the scenario may not use routed execution.
- Scenario evidence maturity is not declared in the current scenario manifest.

Attempts:
- `github-30167381956-1-login-relog#1`: clean-pass, status=success, cleanup=certified, duration_ms=57104, source=`evidence-1:result.json`
- `github-30167381956-2-login-relog#2`: clean-pass, status=success, cleanup=certified, duration_ms=59493, source=`evidence-2:result.json`
- `github-30167381956-3-login-relog#3`: clean-pass, status=success, cleanup=certified, duration_ms=58861, source=`evidence-3:result.json`
- `github-30167381956-4-login-relog#4`: clean-pass, status=success, cleanup=certified, duration_ms=60126, source=`evidence-4:result.json`
- `github-30167381956-5-login-relog#5`: clean-pass, status=success, cleanup=certified, duration_ms=58714, source=`evidence-5:result.json`
- `github-30167381956-6-login-relog#6`: clean-pass, status=success, cleanup=certified, duration_ms=61885, source=`evidence-6:result.json`
- `github-30167381956-7-login-relog#7`: clean-pass, status=success, cleanup=certified, duration_ms=57503, source=`evidence-7:result.json`
- `github-30167381956-8-login-relog#8`: clean-pass, status=success, cleanup=certified, duration_ms=58792, source=`evidence-8:result.json`
- `github-30167381956-9-login-relog#9`: clean-pass, status=success, cleanup=certified, duration_ms=59692, source=`evidence-9:result.json`

No opaque stability score is calculated.

## Next action

Open a separate bounded repair task that makes Universal Agent E2E failure and cancellation evidence durable before repeating the ten-attempt baseline.
