# OAM-006 — Network, Login and Protocol Contract Revalidation

Status: **implementing**

## Pinned baselines

- governance/legacy: `blakinio/canary@a1d82a5989fe9e3b7ac6c495804cb1cd83c59090`
- target task-start: `blakinio/Otheryn@a6d42f6cec024f81a7541084425ec1d43d66d2b8`
- upstream evidence: `opentibiabr/canary@e0ac98e399d0f7e483f3668f57b78fcc45b6e53f`
- maintained client: `blakinio/otclient@2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`

## Canonical module

`protocol` → working disposition `ADAPT`.

## Evidence

### Target/upstream baseline

The pinned target and upstream have identical `ProtocolLogin` and `ProtocolGame` blobs. The target login path still rejects all non-old protocol profiles before authentication and emits `accountDescriptor + "\n" + password` as the modern session-key value. The target game path does not consume the OAM-005 `LoginSessionManager` token.

### Legacy bounded evidence

Legacy Canary PR #80 (`d2e02a3d533bfdfdedc3a81a8f4e4801bc828f22`) removes only the unconditional `!oldProtocol` rejection while retaining the configured old-protocol gate.

Legacy Canary PR #82 (`9cafe7e945391a6f170f5b96bf68713d91d758be`) adds the bounded secure-session handoff:

- modern `authType == "session"` login issues an OAM-005 token bound to account, character set and protocol profile;
- the token is transported through the existing session-key field;
- game login consumes the token first for the matching modern profile;
- successful token consumption passes a pre-authenticated account id into `IOLoginData::gameWorldAuthentication`;
- character ownership and deletion checks still execute;
- existing DB-backed `account_sessions` and password authentication remain as fallbacks;
- old-protocol behavior is preserved.

The target implementation must apply this seam surgically over the current OAM-004D/OAM-005 target and must not wholesale replace `IOLoginData`.

### Maintained client compatibility

At `blakinio/otclient@2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`:

- `EnterGame.onSessionKey` stores the server-provided value in `G.sessionKey` without parsing its contents;
- `CharacterList.tryLogin` forwards `G.sessionKey` to `g_game.loginWorld` unchanged.

Therefore no maintained-client source change is currently justified for replacing the historical descriptor/password session-key payload with an opaque server-issued token.

### Physical-client proof baseline

Universal Agent E2E #37 (`29412296047`) completed successfully with the same maintained client baseline, two stable world entries, two explicit safe logouts, immediate persistence confirmation and no sequence mismatch. OTClient PR #11 was later closed without merge after the retained packet capture disproved its original duplicate-sequence interpretation.

## Required target adaptation

1. Permit supported modern account-login protocol profiles instead of unconditionally rejecting all non-old profiles.
2. Issue the OAM-005 single-use token for the modern session auth layout.
3. Consume the token on game login with exact protocol-profile and character binding.
4. Pass only a successful token's account id into the existing character ownership/deletion authentication path.
5. Preserve DB-session/password fallback behavior and old-protocol compatibility.
6. Preserve strict network framing/sequence validation and OAM-004D persistence semantics.

## Validation requirements

- exact-head Otheryn CI/Required/autofix;
- focused deterministic tests for authentication/fallback seams where feasible;
- full maintained-client physical login/logout/relog proof against the adapted server contract;
- exact server/client SHAs recorded in cross-repo contract governance;
- clean comments/reviews/unresolved-thread gate before merge.

## Explicit non-goals

- no client transport hardening based on disproven sequence evidence;
- no packet validation relaxation;
- no production credential/database access;
- no protocol redesign unrelated to the secure session handoff;
- no OAM-007/OAM-008 implementation.
