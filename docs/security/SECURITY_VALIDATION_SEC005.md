# OTS-SEC-005 authenticated game-session validation

## Scope

OTS-SEC-005 extends the OTS Security Validation Platform with one bounded Canary game-session runtime package. It reuses the existing disposable Canary/MariaDB `run_runtime` lifecycle and targets only the callback-provided literal loopback game service.

The plan contract is `ots-security-game-session-plan-v1`, the report contract is `ots-security-game-session-report-v1`, and the code-owned driver is `canary-game-session-v1`.

Scenario JSON contains only the schema, stable id, exact repository authorization, driver/service identifiers and a bounded ordered list of fixed case ids. It cannot provide account credentials, character names, packet bytes, cryptographic material, commands, executables, source addresses or target coordinates.

## Runtime boundary

The driver uses repository-owned disposable test account/player fixtures selected only in code. It mirrors the maintained current-client first game-message boundary:

1. receive and validate the server challenge;
2. send the pre-XTEA first game message with modern padding, `ClientPendingGame`, Adler32 framing and the reviewed RSA handoff;
3. validate a decryptable non-authentication-error server frame;
4. start post-login client sequencing at sequence 1;
5. require a valid sequence-1 control exchange before running a case.

The registered cases are:

- `authenticated-control`;
- `post-login-zero-sequence`;
- `post-login-sequence-gap`;
- `post-login-sequence-replay`;
- `post-login-invalid-xtea-padding`.

For zero sequence, sequence gap and invalid padding, the tested connection must recover with the still-expected valid sequence. For replay, one valid packet first advances accepted state, the same packet is repeated, and the next valid sequence must still succeed. Every case is followed by a fresh authenticated control session using a distinct deterministic loopback source and a distinct disposable fixture.

## Deterministic evidence

The report records normalized evidence only:

- plan SHA-256 and exact repository authorization;
- exact Canary binary SHA-256;
- SHA-256 pins for the core, runner and reused runtime provider;
- code-owned fixture ids and deterministic case/control loopback sources;
- challenge, login and post-login packet hashes and sizes;
- decrypted server-frame sequence/compression plus payload hash and size;
- tested and recovery sequences;
- fresh authenticated control-session outcome;
- fatal/sanitizer findings and one stable failure code or success.

It does not serialize passwords or arbitrary response bodies and contains no timestamp.

## Historical source evidence

The original implementation was completed on stale PR #514. Its first fully passing runtime head was:

`c45050f81ce4b2f337b4573df60384627affd8fc`

Historical validation:

- Agent Task Ownership run `29618885740`: PASS;
- repository CI run `29618885853`: PASS;
- Security Validation run `29618885799`: PASS.

That Security Validation run passed focused security tests, an exact-head Linux release build, the existing SEC-003 malformed-status runtime, the existing SEC-004 login-parser runtime and the SEC-005 authenticated game-session runtime. Its SEC-005 artifact reported five passing case probes, five passing fresh authenticated controls and no fatal/sanitizer findings.

This historical evidence proves that the package design worked on that exact old Canary head. It is retained as source-package evidence only and is not current-main merge evidence.

## Current-main recovery

Draft PR #974 recovers SEC-005 from stale PR #514 onto current `main` under task `CAN-20260726-security-authenticated-session-transport-recovery`.

The seven package-specific files were transferred byte-for-byte from the proven PR #514 head. The Security Validation workflow, programme, catalogue and changelog were integrated manually against their current contents so newer repository work was not overwritten. No runtime C++, datapack, production configuration, external repository or public target is changed.

On replacement head `8c9a2a2ad90e5aa44c72dd782c2ccdcaaeadaff0`:

- Agent Task Ownership run `30220289801`: PASS;
- focused Security Validation job in run `30220289843`: PASS, including Python compilation, all focused security tests, scenario registry validation, runtime-adapter validation and registered static scenarios;
- full current-main Canary build and disposable SEC-003/SEC-004/SEC-005 runtime remain required on the exact final PR head before merge.

The replacement must not use historical PR #514 checks as a substitute for a fresh exact-final-head runtime result.

## Rejection evidence

The historical passing runtime recorded the expected server-side rejection classes for the bounded negative cases:

- zero sequence;
- sequence mismatch for the gap case;
- sequence mismatch for the replay case;
- decrypt failure for invalid modern padding.

Each affected connection then completed the expected valid recovery exchange.

## Evidence boundary

A passing exact-head result proves successful authentication and game-session establishment for the repository-owned disposable fixtures and the registered post-login sequence/XTEA rejection-and-recovery assertions on the tested exact Canary binary.

It does not prove:

- authorization correctness for arbitrary accounts or characters;
- broader session lifecycle and reconnect/logout race safety;
- multi-client concurrency safety;
- economy, market, trade, depot or database transaction safety;
- Redis/multichannel ownership correctness;
- maintained-client server-response resilience;
- packet-flood or sustained capacity behavior;
- production deployment safety.

Those remain separate bounded tasks. A green SEC-005 result must not be generalized into complete authenticated-session or economy security.
