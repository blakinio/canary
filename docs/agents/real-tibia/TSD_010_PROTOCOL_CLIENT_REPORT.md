# TSD-010 — Protocol and Client Decomposition

> Task-start main: `381cc076fa35e138292197f751f26c2e7b89dd08`.
> Read-only upstream baselines: `opentibiabr/canary@a879c9312e34381e8eedf397b8ed44510698b689` and `opentibiabr/otclient@bdea0b23b4a738809d698cb7e4f88a299dd6bffc`.
> Inventory only; no packet, transport, login, session or maintained-client compatibility claim.

## Result

Registry grows from **56** to **60** records. Existing records remain unchanged.

Added only:

- `network-transport`;
- `login-protocol`;
- `protocol-compatibility`;
- `protocol-session-handoff`.

Preserved unchanged:

- `protocol`;
- `physical-client-e2e`;
- `account-authentication`;
- `account-lifecycle`;
- `character-lifecycle`;
- `player-persistence`;
- every gameplay module.

## Evidence inventory

### Network transport

Canary `Connection`, base `Protocol` and `TransportCodec` own socket accept/read/write/timeout/close state, transport body sizing, checksum and accepted-sequence handling, XTEA/compression transforms, callback publication and connection-scoped protocol release. Maintained OTClient's base `framework/net/Protocol` and connection layer independently expose connection state plus checksum, sequence, XTEA and compression state.

These are corresponding transport implementation surfaces only. Their presence on both sides does not prove equivalent framing, crypto, sequence, checksum, compression or timeout behavior.

### Login protocol

Canary `ProtocolLogin` owns the account-login wire phase around authentication: client/profile resolution, login-layout selection, response transport setup, session-key field, world/character-list serialization and disconnect after the response. Maintained OTClient `modules/gamelib/ProtocolLogin` independently builds the login packet, parses login responses/session key and character lists, then disconnects.

Credential verification remains `account-authentication`; the fact that both ends implement a login parser/serializer is not wire-compatibility proof.

### Protocol compatibility

Canary `ProtocolProfileRegistry` owns version, wire-family, RSA family, support state, asset signatures, transport/challenge behavior, login layouts and server feature masks. Maintained OTClient `modules/game_features` owns a version-gated client feature matrix.

The two are durable compatibility inventories, but no one-to-one equivalence is inferred between a Canary `ProtocolFeature` bit and an OTClient `GameFeature`. Packet captures or explicit paired fixtures remain required for compatibility claims.

### Protocol session handoff

`ProtocolSessionHintStore` owns an independent bounded register → lease → consume/resolve → expire/clear lifecycle for carrying login-phase protocol-profile knowledge into the subsequent game connection. It keys hints with remote IP, hashed account session, allowed character names and profile behavior, with TTL/capacity and reusable-vs-one-shot handling.

This store does not own credential authentication or player sessions. Its state machine is implementation inventory only and does not prove replay resistance, race freedom or successful physical relog.

## Candidate decisions

| Candidate | Decision | Reason |
|---|---|---|
| `network-transport` | `ADD_NOW` | independent connection/framing/checksum/sequence/crypto/compression/release lifecycle with current server and client roots |
| `login-protocol` | `ADD_NOW` | distinct account-login request/response and character-list/session-key wire phase on server and maintained client |
| `protocol-compatibility` | `ADD_NOW` | independent server profile registry plus maintained-client version feature matrix |
| `protocol-session-handoff` | `ADD_NOW` | independent bounded hint registration/lease/consume/expiry state machine |
| `game-protocol` | `ALREADY_COVERED` | preserve broad existing `protocol` umbrella for the monolithic game packet contract |
| `game-session` | `MERGE_WITH_ANOTHER_MODULE` | current server/client session state is intertwined with `ProtocolGame` packet routing, `Connection` transport and client `Game`; no clean additional root is established |
| `connection-session-release` | `MERGE_WITH_ANOTHER_MODULE` | callback/release coordination is part of `network-transport`; leave-game semantics stay in broad `protocol` |
| `login-authentication` | `ALREADY_COVERED` | credential/session-token policy remains `account-authentication` |
| `physical-client-runtime` | `ALREADY_COVERED` | reusable live-client orchestration remains `physical-client-e2e` |
| `protocol-opcodes` | `MERGE_WITH_ANOTHER_MODULE` | byte/opcode contracts remain inside broad `protocol`; individual opcode modules would be too granular |
| `client-game-features` | `MERGE_WITH_ANOTHER_MODULE` | version-gated compatibility metadata belongs in `protocol-compatibility`; gameplay feature implementations remain their domain modules |
| individual client modules/opcodes/feature flags | `REJECT_AS_TOO_GRANULAR` | implementation entries, not independent durable module lifecycles |

## Dependencies

- `network-transport` has no decomposition dependency.
- `login-protocol` depends on `account-authentication` and `network-transport`.
- `protocol-compatibility` has no decomposition dependency.
- `protocol-session-handoff` depends on `protocol-compatibility`.

All four new records begin at lifecycle/implementation/evidence `inventory`; persistence, protocol, automated tests, runtime validation and gameplay E2E remain `not-assessed`.

The pre-existing `protocol` record remains unchanged at its existing maturity. TSD-010 does not downgrade or upgrade it.

## Discovery expectations

```text
src/server/network/connection/connection.cpp
  → network-transport
src/server/network/protocol/protocol.cpp
  → network-transport + protocol
src/server/network/protocol/transport_codec.cpp
  → network-transport + protocol
src/server/network/protocol/protocollogin.cpp
  → login-protocol + protocol
src/server/network/protocol/protocol_profile.cpp
  → protocol-compatibility + protocol
src/server/network/protocol/protocol_session_hint.cpp
  → protocol-session-handoff + protocol

maintained OTClient:
src/framework/net/protocol.cpp
  → network-transport + protocol
modules/gamelib/protocollogin.lua
  → login-protocol + protocol
modules/game_features/features.lua
  → protocol-compatibility + protocol
```

Upstream Intelligence source roles remain mandatory: server sources consume only server/data/tests/docs buckets; client sources consume only client/data/tests/docs buckets. The broad client `protocol` mapping remains an umbrella and does not transfer server-only session-handoff records into client changes.

## Evidence limits

TSD-010 does not prove packet layout equivalence, login/game handshake correctness, checksum/sequence compatibility, encryption/compression compatibility, feature-gate equivalence, session-handoff safety, malformed-input handling, client/server version interoperability, physical-client E2E, Real Tibia parity or Oteryn readiness.

A matching parser, serializer, class name, compile result or unit test is not wire compatibility evidence.

## Next package

After feature merge and lifecycle archive:

```text
task: CAN-20260714-tibia-system-decomposition-analytics-security-ai
package: TSD-011
branch: docs/tibia-system-decomposition-analytics-security-ai
```
