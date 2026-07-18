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

## First real exact-head evidence

Validated implementation head:

`c45050f81ce4b2f337b4573df60384627affd8fc`

Validation:

- Agent Task Ownership run `29618885740`: PASS;
- repository CI run `29618885853`: PASS;
- Security Validation run `29618885799`: PASS.

The Security Validation run passed focused security tests, exact-head Linux release build, the existing SEC-003 malformed-status runtime, the existing SEC-004 login-parser runtime and the new SEC-005 authenticated game-session runtime.

The SEC-005 artifact reported:

- `status=success`;
- `failure=null`;
- five case probes PASS;
- five fresh authenticated control probes PASS;
- no fatal/sanitizer findings.

Server-side transport diagnostics recorded the expected rejection classes for the bounded negative cases:

- zero sequence;
- sequence mismatch for the gap case;
- sequence mismatch for the replay case;
- decrypt failure for invalid modern padding.

Each affected connection then completed the expected valid recovery exchange.

## Evidence boundary

This evidence proves successful authentication and game-session establishment for the repository-owned disposable fixtures and the registered post-login sequence/XTEA rejection-and-recovery assertions on the tested exact Canary binary.

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
