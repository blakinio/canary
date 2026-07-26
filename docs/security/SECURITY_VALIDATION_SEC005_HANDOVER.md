# OTS-SEC-005 durable handover

## Final state

- Repository: `blakinio/canary`
- Replacement pull request: `#974`
- Exact feature head: `37ccd806c4843739a79b2c5a394e35ac4ae3bacf`
- Squash merge: `1408aaa886240034a90fc33873e9b9e0fa47cab6`
- Historical source pull request: `#514`, closed unmerged as superseded
- Historical source head: `3fbaba7fe44808b889c5409ff844b796d9283554`
- Durable task: `docs/agents/tasks/archive/CAN-20260726-security-authenticated-session-transport-recovery.md`
- Status: merged, runtime-proven and lifecycle-complete after the docs-only lifecycle PR merges

## Delivered package

PR #974 recovered the bounded authenticated Canary game-session and post-login transport validation package from stale PR #514 without merging or mechanically rebasing the old branch.

The package-specific runtime, runner, tests, scenario and original SEC-005 documentation were transferred from the historically proven source blobs. The current Security Validation workflow, programme, module catalogue and changelog were integrated against current `main`, preserving newer unrelated work.

No C++ runtime source, datapack, production configuration, credential, map asset, public target, upstream repository, Otheryn repository or maintained-client repository was modified.

## Behavior

The package uses repository-owned disposable fixtures and literal loopback only. It proves the current first-game Adler32/RSA handoff before XTEA/sequenced transport, then executes five fixed code-owned cases:

- authenticated control;
- zero sequence;
- sequence gap;
- sequence replay;
- invalid XTEA padding.

Each negative case requires same-session recovery with the still-expected accepted sequence and is followed by a fresh authenticated control session from a distinct deterministic loopback source and fixture. Manifests cannot supply credentials, packet bytes, key material, commands, executables or network targets.

## Exact-final evidence

- Agent Task Ownership run `30220958387`: PASS;
- repository CI run `30220958452`: PASS;
- stable CI `Required`: PASS;
- Linux release and Linux debug: PASS;
- full Linux debug tests and schema import: PASS;
- Docker image and Docker Quickstart: PASS;
- autofix run `30220958405`: PASS with no follow-up commit;
- Security Validation run `30220958474`: PASS;
- fresh exact-head Canary build: PASS;
- SEC-003 malformed-status runtime: PASS;
- SEC-004 login-parser runtime: PASS;
- SEC-005 authenticated game-session runtime: PASS.

Final SEC-005 artifact:

- name: `security-game-session`;
- artifact id: `8637308071`;
- digest: `sha256:3c5ef16d0a6b7a3a25cfa0f2c2ed78a883de4a2ea65a06736ce3044c25939cd8`;
- exact head: `37ccd806c4843739a79b2c5a394e35ac4ae3bacf`;
- report status: `success`;
- failure: `null`;
- five case probes: PASS;
- five fresh authenticated controls: PASS;
- fatal/sanitizer findings: none.

## Delivery audit

The feature PR changed exactly twelve intended paths. It contained no C++ runtime, datapack, map, production configuration, credential or external-repository write. Immediately before merge it was Ready, mergeable, `behind_by=0` and had no comments, reviews or review threads. The merge used expected-head protection.

## First failures and repairs

1. Historical SEC-005 first runtime failure used the wrong first-game framing. Source/runtime evidence established the pre-XTEA Adler32 envelope; the package was corrected and subsequently passed.
2. Historical PR #514 and replacement PR #974 initially failed ownership metadata because `related_pr` was not yet bound. The task records were corrected without weakening implementation or tests.
3. The replacement final checkpoint initially used unsupported validation value `PENDING`; it was changed to supported `BLOCKED`, then Ownership passed.
4. PR #514 became hundreds of commits behind `main`. A fresh current-main replacement was used instead of direct merge or wholesale rebase.
5. Current `main` advanced during final validation. The branch was resynchronized, the helper removed, and the full exact-head gate was repeated on the final head.

## Ownership release

PR #514 was commented with the replacement evidence and closed as superseded after PR #974 merged. Security Validation no longer owns an active overlapping SEC-005 implementation lane.

OAM-053 may now perform a fresh `network-transport` eligibility preflight. SEC-005 is reusable evidence for its exact registered assertions only; it is not complete proof of transport equivalence.

## Safety boundary

SEC-005 remains limited to repository-owner-authorized disposable/local Canary infrastructure. It does not prove arbitrary-account authorization, session lifecycle races, economy or transaction safety, Redis/multichannel behavior, maintained-client hostile-server resilience, sustained capacity or production deployment safety.
