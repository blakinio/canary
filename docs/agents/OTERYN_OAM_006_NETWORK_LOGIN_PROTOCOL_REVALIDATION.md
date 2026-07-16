# OAM-006 — Network, Login and Protocol Contract Revalidation

Status: **ready**

## Pinned baselines

- governance/legacy task-start: `blakinio/canary@a1d82a5989fe9e3b7ac6c495804cb1cd83c59090`
- target task-start: `blakinio/Otheryn@a6d42f6cec024f81a7541084425ec1d43d66d2b8`
- upstream evidence: `opentibiabr/canary@e0ac98e399d0f7e483f3668f57b78fcc45b6e53f`
- maintained client: `blakinio/otclient@2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`
- final target: `blakinio/Otheryn@c547d8ad70ef1252624c255476e6cb83fa125e14`

## Canonical module and disposition

`protocol` → **ADAPT**.

The target/upstream baseline had a usable protocol substrate, but the live modern login path did not expose the OAM-005 secure login-session primitive. A bounded adaptation was required; no maintained-client source mutation was justified.

## Evidence

### Target/upstream baseline

At the pinned task-start revisions the target and upstream had identical `ProtocolLogin` and `ProtocolGame` blobs. The target login path rejected every non-old protocol profile before authentication and the live game path did not consume the OAM-005 `LoginSessionManager` token.

### Legacy bounded evidence

Legacy Canary PR #80 (`d2e02a3d533bfdfdedc3a81a8f4e4801bc828f22`) provided the bounded modern-login compatibility seam while preserving the configured old-protocol gate.

Legacy Canary PR #82 (`9cafe7e945391a6f170f5b96bf68713d91d758be`) provided the secure-session handoff evidence:

- modern `authType == "session"` login issues an OAM-005 token bound to account, character set and protocol profile;
- the token is transported through the existing session-key field;
- game login consumes the token first for the matching modern profile;
- successful token consumption passes a pre-authenticated account id into the existing character ownership/deletion authentication path;
- existing DB-backed `account_sessions` and password authentication remain as fallbacks;
- old-protocol behavior is preserved.

### Maintained client compatibility

At `blakinio/otclient@2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`, `EnterGame.onSessionKey` stores the server-provided value opaquely and `CharacterList.tryLogin` forwards it unchanged to `g_game.loginWorld`. No client source change was required.

OTClient PR #11 was closed without merge after retained packet evidence disproved its original duplicate-sequence interpretation. No speculative client transport hardening is part of OAM-006.

## Delivered target adaptation

Otheryn PR #21 applied the bounded target change over the OAM-004D/OAM-005 target:

1. supported modern account-login profiles are no longer unconditionally rejected;
2. modern `AUTH_TYPE=session` issues the OAM-005 single-use token through the existing session-key field and fails closed if issuance fails;
3. the current modern profile consumes the token first during game-world authentication;
4. successful token consumption feeds only the authenticated account id into the existing ownership/deletion path;
5. DB-backed session and password fallbacks remain available;
6. `ProtocolGame` and the public `IOLoginData` signature remain unchanged;
7. sequence/checksum/XTEA validation and OAM-004D persistence boundaries remain unchanged;
8. the manual Windows Solution/MSBuild path now includes the OAM-005 `LoginSessionManager` implementation through bounded `Directory.Build.targets` registration.

PR #21 final exact head `5342b374306abb44b6b5e201c85f6a0182c99286` passed ready-triggered CI #80, Required #78 and autofix.ci #71, with a clean comment/review/thread gate, then squash-merged as `c547d8ad70ef1252624c255476e6cb83fa125e14`.

## Exact cross-repository physical proof

The existing Universal Agent E2E was extended in-place with optional controlled-server repository/exact-SHA inputs. No second E2E orchestrator was created.

Universal Agent E2E #118 (`29531221365`) was forced through the full heavy path and completed **PASS** on governance head `47138164f65283256bf6639937241f7f5f52a63a`:

- `Required physical E2E`: PASS;
- controlled server request: `blakinio/Otheryn@c547d8ad70ef1252624c255476e6cb83fa125e14`;
- recorded controlled server commit: `c547d8ad70ef1252624c255476e6cb83fa125e14`;
- maintained client commit: `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`;
- controlled server binary SHA-256: `a69674e53911f4c529fe62d4dee0209633a73a14903c61f8e5fbca1bdbd8097d`;
- OTClient binary SHA-256: `b562247f8a0499738bf89eb9f8132146a26b2be57d9fb45e9586a0e0659d97ed`;
- two protocol-login/world-entry successes for profile `current`, protocol 1525;
- two stable online confirmations and two explicit safe logouts;
- two packet records and two server login observations;
- `lastlogin` and `lastlogout` persistence checks passed;
- post-run online count returned to zero;
- client exit code was zero and no fatal runtime log was detected.

The exact-target evidence artifact is `universal-agent-e2e-login-relog` from run #118, digest `sha256:0db430d258e6048b826af5c46a453e00647c7b30a2a700d8f0245a43fd6145cc`.

A preceding run #114 was deliberately rejected as target proof because immediate-parent reuse skipped the heavy physical jobs. OAM-006 completion relies on full run #118, not #114.

## Final disposition rationale

`protocol` is **ADAPT** because the task-start target/upstream substrate remained structurally usable, but bounded modern-login and secure session-token wire integration were required. The exact final target and unchanged maintained-client baseline completed the physical login/relog contract successfully.

## Known gaps and limits

- The exact physical proof covers the maintained current profile (`1525`) and the `login/relog` path; it does not claim exhaustive physical coverage of every old-protocol profile.
- OAM-005 focused tests remain the primitive-level evidence for token lifetime/single-use behavior; OAM-006 physical E2E proves successful live handoff, not an adversarial replay matrix.
- Existing DB-session/password fallbacks were preserved in code and target CI, but the exact controlled-server physical scenario exercised the maintained modern session flow.
- No claim is made that player SQL persistence and later Wheel KV flush are atomic; OAM-004 residual limitations remain unchanged.

## Explicit non-goals

- no client transport hardening based on disproven sequence evidence;
- no packet validation relaxation;
- no production credential/database access;
- no protocol redesign unrelated to the secure session handoff;
- no wholesale `IOLoginData` replacement;
- no OAM-007/OAM-008 implementation.
