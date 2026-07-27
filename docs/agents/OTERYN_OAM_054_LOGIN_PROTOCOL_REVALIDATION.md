# OAM-054 Login Protocol revalidation

Status: **target feature and lifecycle complete; Canary governance pending**

Program: `CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION`

Coordination: `OAM-054`

## Final disposition

```text
login-protocol → ADAPT
```

Otheryn retained its account authentication integration, explicit current/11.00/8.60 request layouts, secure opaque login-session tokens and protocol-session handoff. The target adapted only the account-login response wire into a target-owned deterministic contract corresponding to the maintained-client parser.

## Pinned evidence

```text
Canary preflight merge:     d8eb3f5520b2a94e788a31e004bf1aa33b9d7c61
Otheryn task-start main:    9703da845384423ad85883216bf8853642c21bcd
Otheryn synchronized main:  4ad8c0f2ed1c6bd60da9b747b8ff180ced60b593
Otheryn feature head:       f6db2136248b39ccd7aa57178a1c63c788b9bcec
Otheryn feature merge:      e077c51fe948652a4849e15f6c518059f4370717
Otheryn lifecycle head:     08221f7e9ef31158b3cc3d201ad0a06896df15f7
Otheryn lifecycle merge:    41bc0562c263781df85c2f6855295fefa201db0a
upstream evidence baseline: 7644bcbcbbad4a09e52a5707ed531e4dd21d8a79
maintained OTClient:        99ad5de5a19179f21e2e21e961c1ef121a30d08e
```

Relevant Canary donors:

- modern-client login rejection repair: `d2e02a3d533bfdfdedc3a81a8f4e4801bc828f22`;
- secure opaque session-key handoff: `9cafe7e945391a6f170f5b96bf68713d91d758be`.

## Canonical boundary

The canonical `login-protocol` record owns account-login request/response handling, profile/version selection, pre-RSA metadata validation, RSA/XTEA handoff, session-key field, world/character-list serialization, maintained-client parsing correspondence and disconnect after response.

It excludes password hashing or credential policy, account repository ownership, game-world authentication, player attach/detach, gameplay packet routing, client UI/launcher behavior, production endpoints and claims of complete account/session security.

## Why ADAPT

Otheryn already had stronger target-specific architecture than the Canary donor: explicit current/11.00/8.60 login layouts, fail-closed `LoginSessionManager` token issuance and protocol-session hints. Wholesale migration was therefore invalid.

Pure `REUSE` was also invalid. The maintained client decodes modern opcode `0x64` as world list, character list, account status `u8`, subscription status `u8` and premium expiry `u32`, while the target lacked an explicit tested status/subscription/expiry contract. There was no deterministic server serializer/client parser correspondence test.

## Target delivery

Otheryn PR #165 changed exactly six paths:

- `src/server/network/protocol/login_protocol_wire.hpp`;
- `src/server/network/protocol/protocollogin.cpp`;
- `tests/unit/server/CMakeLists.txt`;
- `tests/unit/server/network/protocol/oam_054_login_protocol_test.cpp`;
- the target task and report.

Delivered behavior:

- target-owned opcode `0x28` session-key response framing;
- modern world/character-list serialization;
- explicit modern `AccountStatus::Ok`, free/premium subscription status and premium-expiry `u32` tail;
- preserved legacy character list and premium-days `u16` tail;
- one capped `u8` snapshot, maximum 255 names, shared by secure-token authorization, serialized records and session hints;
- deterministic field-order decoding tests matching the maintained client;
- preserved request parsing, layout/profile selection, RSA/XTEA, account loading/authentication, token issuance, session hints, send and disconnect lifecycle.

No maintained-client write, credential-policy change, account repository change, game-world authentication change, gameplay opcode, schema, datapack, endpoint or production action was added.

## Deterministic tests

Six OAM-054 tests decode each message to exact end:

- session-key opcode and token;
- modern premium response;
- modern free response;
- legacy response with premium days;
- modern response capped at 255 characters;
- legacy response capped at 255 characters.

Existing OAM-044 profile and OAM-045 session-handoff regressions remained in the same full CTest suite.

## Exact-final validation

Exact atomically synchronized head `f6db2136248b39ccd7aa57178a1c63c788b9bcec` passed:

- Otheryn CI `30250360096`;
- Otheryn `Required` `30250359982`;
- Otheryn autofix `30250359933` without a follow-up commit;
- Fast Checks and Lua;
- Linux debug with runtime smoke, schema import and full CTest;
- Linux release;
- Docker image;
- macOS build/runtime smoke;
- Windows CMake/runtime smoke and Solution build.

The final feature branch was based on current main `4ad8c0f2ed1c6bd60da9b747b8ff180ced60b593`, had `behind_by=0`, exactly six paths and no comments, reviews or review threads. PR #165 squash-merged with expected-head protection as `e077c51fe948652a4849e15f6c518059f4370717`.

Lifecycle PR #173 changed only the active/archive task pair and target report. Exact lifecycle head `08221f7e9ef31158b3cc3d201ad0a06896df15f7` passed Required `30252401732`, had `behind_by=0`, no discussions and merged as `41bc0562c263781df85c2f6855295fefa201db0a`.

## First failures and integration repairs

- The preflight identified a maintained-client account-tail correspondence gap. The target serializer now emits explicit status/subscription/expiry fields with deterministic parser-order tests.
- Otheryn `main` advanced through unrelated resilience work during exact-head gates. The feature was repeatedly synchronized without conflict; the final atomically constructed merge commit preserved exactly six approved blobs and was fully retested.
- A workflow-token sync produced `action_required` placeholders. A trusted checkpoint and later atomic merge commit initiated authoritative exact-head gates; no security or CI gate was bypassed.

## Boundary classification

| Boundary | Result |
|---|---|
| ownership/lifecycle | Target feature and lifecycle complete; no active overlapping login-protocol owner. |
| account request parsing | Existing Otheryn current/11.00/8.60 layouts preserved. |
| RSA/XTEA | Existing target handoff preserved; no new algorithm or key source. |
| session key | Existing opaque fail-closed token issuance preserved; response framing tested. |
| response serialization | Target-owned deterministic modern and legacy wire helper. |
| maintained client | Parser correspondence proven for registered fixtures; no client mutation. |
| credential policy | Unchanged and outside OAM-054. |
| game-world authentication | Unchanged and outside OAM-054. |
| persistence/schema | No schema or durable account-state change. |
| runtime tests | Full target CTest and platform runtime smoke passed. |
| operations | No production endpoint, credential, host or deployment action. |

## Nonclaims

OAM-054 does not prove password security, arbitrary-account authorization, every historical protocol version, game-world authentication, reconnect/session races, client UI correctness, sustained capacity, denial-of-service resistance or production deployment safety.
