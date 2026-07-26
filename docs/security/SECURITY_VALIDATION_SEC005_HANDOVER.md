# OTS-SEC-005 recovery handover

## Current state

- Repository: `blakinio/canary`
- Replacement pull request: `#974`
- Replacement branch: `feat/security-authenticated-session-transport-recovery`
- Historical source pull request: `#514`
- Historical source head: `3fbaba7fe44808b889c5409ff844b796d9283554`
- Current replacement implementation/docs head before final checkpoint: `95445cc1877c089431fe09690a340b5405145bc6`
- Replacement state: draft, current-main integration in progress
- Historical PR #514 state: open, not merged, not safely mergeable; retained only as exact package-source evidence until replacement merge

## Recovered work

PR #974 starts from current `main` and recovers the bounded authenticated Canary game-session and post-login transport validation package without merging or rebasing the stale PR branch.

The following package-specific files were transferred byte-for-byte from the proven #514 head:

- `tools/security/game_session_runtime.py`;
- `tools/security/game_session_runtime_runner.py`;
- `tests/security/test_game_session_runtime.py`;
- `tests/security/test_game_session_runtime_runner.py`;
- `tests/security/runtime_scenarios/canary-game-session.json`;
- `docs/security/SECURITY_VALIDATION_SEC005.md` before its recovery-state refresh;
- this handover before its recovery-state refresh.

The current Security Validation workflow was extended manually with focused SEC-005 compilation/tests and one disposable `game-session` job. The current programme, module catalogue and changelog were updated narrowly; newer unrelated entries were preserved.

No C++ runtime source, datapack, production configuration, credential, map asset, public target, upstream repository, Otheryn repository or maintained-client repository is modified.

## Package behavior

The package uses repository-owned disposable fixtures and literal loopback only. It proves the current first-game Adler32/RSA handoff before XTEA/sequenced transport, then exercises five fixed code-owned cases:

- authenticated control;
- zero sequence;
- sequence gap;
- sequence replay;
- invalid XTEA padding.

Each negative case requires recovery with the still-expected accepted sequence and is followed by a fresh authenticated control session from a distinct deterministic loopback source and fixture. Manifests cannot supply credentials, packet bytes, key material, commands, executables or network targets.

## Evidence

Historical package proof from PR #514 remains useful but is not sufficient for replacement merge:

- first passing implementation head `c45050f81ce4b2f337b4573df60384627affd8fc`;
- Agent Task Ownership `29618885740`: PASS;
- repository CI `29618885853`: PASS;
- Security Validation `29618885799`: PASS;
- five case probes and five fresh authenticated controls passed with no fatal/sanitizer findings.

Current-main replacement evidence before the final gate:

- replacement head `205ab3f1055c5fc06b120f700898727a7a4b9240` passed repository CI run `30220015807` and the focused validation job of Security Validation run `30220015814`;
- the first replacement Ownership run `30220015705` failed only because the new task still had `related_pr: pending`; PR #974 was then bound and subsequent Ownership run `30220289801` passed;
- replacement head `8c9a2a2ad90e5aa44c72dd782c2ccdcaaeadaff0` passed focused Security Validation job `89841469291` in run `30220289843`;
- a fresh exact-final-head Linux build plus disposable SEC-003, SEC-004 and SEC-005 runtime remains mandatory before merge.

## First failures and repairs

1. Historical SEC-005 first runtime failure used the wrong first-game framing. Source/runtime evidence established the pre-XTEA Adler32 envelope; the package was corrected and subsequently passed.
2. Historical PR #514 and replacement PR #974 each initially failed task ownership because `related_pr` was not yet bound. Both task records were corrected; no implementation or validation contract was weakened.
3. PR #514 became hundreds of commits behind current `main`. It was not merged or mechanically rebased. PR #974 selectively recovered the package onto current `main` and manually reintegrated shared files.

## Remaining merge gate

Before PR #974 may merge:

1. synchronize with current `main` without dropping either current-main work or the twelve intended replacement paths;
2. apply `ci:final-gate` before the final checkpoint commit;
3. update the task checkpoint once with the exact pre-final evidence and no remaining implementation uncertainty;
4. mark PR #974 ready;
5. obtain successful exact-head Agent Task Ownership, repository CI, Security Validation and autofix results;
6. confirm the Security Validation run includes a fresh exact-head Canary build and successful disposable malformed-status, login-parser and authenticated game-session jobs;
7. confirm exactly the twelve intended paths, no forbidden files, no unresolved reviews/threads and `behind_by=0`;
8. squash-merge with expected-head protection.

After replacement merge:

1. comment on and close PR #514 as superseded by #974;
2. perform a separate lifecycle PR that archives the recovery task and records final replacement head, runs, artifacts and merge SHA in the programme/handover/catalogue;
3. release interacting Security Validation ownership;
4. update the OAM-053 blocker checkpoint and repeat a fresh `network-transport` eligibility preflight.

## Safety boundary

SEC-005 remains limited to repository-owner-authorized disposable/local Canary infrastructure. It does not prove arbitrary-account authorization, session races, economy/transaction safety, Redis/multichannel behavior, maintained-client hostile-server resilience, sustained capacity or production deployment safety.
