# OAM-053 Network Transport revalidation

Status: **target disposition and lifecycle complete; Canary governance pending**

Program: `CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION`

Coordination: `OAM-053`

## Final disposition

```text
network-transport → ADAPT
```

Otheryn retained its existing connection, multiprotocol and protocol-session-handoff architecture. The target adapted only evidence-backed transport authority, framing, sequence/XTEA rejection and recovery invariants that were absent from its upstream-derived transport codec.

## Pinned evidence

```text
Canary preflight base:      ba08e346540f017773b9268832d304c7f5664ac2
Canary preflight merge:     6a9e6cf106b3e0193fb6a9d923a37cee38888f66
Otheryn target task start:  64ad965eee40f62ff996980fd8a0d329245c519f
Otheryn feature head:       7376eff79e166595a91f4581d8eef6e6c228e754
Otheryn feature merge:      c25fff72dd8b89f6ef1565af2d84ab9eef33dce9
Otheryn lifecycle head:     34036aa6db8e6f8942a970a214f09493d1fbcd51
Otheryn lifecycle merge:    9703da845384423ad85883216bf8853642c21bcd
upstream evidence baseline: 7644bcbcbbad4a09e52a5707ed531e4dd21d8a79
maintained OTClient:        5568cb6f5e2fd6162c78cde304deea5d32461e05
```

Pinned Canary donor merges:

- authoritative transport profiles: `bbff04524bbb99ab54c9571c24382399b904cbd8`;
- checksum-free block-count symmetry: `4535836d4df0fc669033ed73f525754a1a2d1b40`;
- complete captured current first frame: `5c750e13fb95f46225807b8907a95ce3091283c8`;
- SEC-005 current-main runtime recovery: `1408aaa886240034a90fc33873e9b9e0fa47cab6`.

## Canonical boundary

The canonical `network-transport` record owns:

- connection create, accept, read, write, timeout and close lifecycle;
- transport frame length encode/decode;
- checksum and accepted-sequence state;
- XTEA and compression transforms;
- protocol callback publication and connection-scoped release coordination.

It excludes account credential authentication, login character-list semantics, game opcode layouts, gameplay dispatch and claims of complete malformed-input or server-client compatibility proof.

## Why ADAPT

At task start Otheryn already contained the complete connection and protocol-profile surfaces, so wholesale migration was invalid. However, the target still matched upstream transport codec behavior in key areas:

- one broad current-modern transport profile rather than explicit current login, sequenced-game and checksum-free-game contracts;
- checksum/compression authority partly retained in mutable `Protocol` state;
- accepted sequence state advanced before complete checksum and XTEA acceptance;
- inbound rejection collapsed to `bool` without expected/received sequence evidence;
- checksum-free modern block-count encoding subtracted checksum bytes unconditionally;
- truncated checksum/header and malformed encrypted padding boundaries lacked the bounded fail-closed guards proven by donors and SEC-005.

Pure `REUSE` was therefore rejected. The target proof semantically integrated only transport-owned invariants while retaining later Otheryn multiprotocol, `GameProfile`, session-handoff and module-engine evolution.

## Target delivery

Otheryn PR #163 changed exactly eleven paths:

- `src/server/network/message/outputmessage.hpp`;
- `src/server/network/protocol/protocol.hpp`;
- `src/server/network/protocol/protocol.cpp`;
- `src/server/network/protocol/protocol_profile.hpp`;
- `src/server/network/protocol/protocol_profile.cpp`;
- `src/server/network/protocol/transport_codec.hpp`;
- `src/server/network/protocol/transport_codec.cpp`;
- `tests/unit/server/CMakeLists.txt`;
- `tests/unit/server/network/protocol/oam_053_network_transport_test.cpp`;
- the target task and report.

Delivered behavior:

- explicit current login, current sequenced-game and current checksum-free-game profiles;
- complete profile authority for checksum, compression, framing and encrypted layout;
- typed inbound outcomes with expected/received sequence evidence;
- accepted sequence commit only after checksum and decrypt acceptance;
- checksum-free block-count encode/decode symmetry;
- complete captured first-frame sizing of 172 bytes with sequence/checksum and 168 bytes without checksum;
- fail-closed truncated checksum, invalid XTEA block size, missing inner length/padding and oversized padding;
- deterministic regressions for profile contracts, sizing, symmetry, truncation, zero, gap, replay and decrypt rejection.

No wholesale `Connection` or `ProtocolGame` replacement, account-login semantics, character-list behavior, gameplay opcode layout, schema, datapack, client, deployment or production configuration was added.

## Target validation

Exact feature head `7376eff79e166595a91f4581d8eef6e6c228e754` passed:

- Otheryn CI `30225971903`;
- Otheryn `Required` `30225971757`;
- Otheryn autofix `30225971771` with no follow-up commit;
- Fast Checks and Lua;
- Linux release and Linux debug;
- full Linux CTest, Canary runtime smoke and schema import;
- Docker image;
- macOS build and runtime smoke;
- Windows CMake and runtime smoke.

The final feature branch was `behind_by=0`, comments, reviews and review threads were empty, and PR #163 squash-merged with expected-head protection as `c25fff72dd8b89f6ef1565af2d84ab9eef33dce9`.

Lifecycle PR #164 changed only the active/archive task pair and final report. Exact lifecycle head `34036aa6db8e6f8942a970a214f09493d1fbcd51` passed Required `30226763484`, had a clean three-path discussion/drift audit and squash-merged as `9703da845384423ad85883216bf8853642c21bcd`.

## First failures

- The first Ready head used donor-only `Dispatcher::executeSerialEventsForTest()`. The target has no such public hook. Focused test connections are never accepted into `Connection::protocol`, so target-native `close(true)` cleanup was sufficient; the subsequent full CTest passed.
- The first Docker attempt failed before project compilation with `curl: (35) Recv failure: Connection reset by peer` during vcpkg bootstrap. No source or Docker change was made; the next complete Docker run passed.

## Boundary classification

| Boundary | Result |
|---|---|
| ownership/lifecycle | Target feature and lifecycle are complete; no active overlapping transport owner remains. |
| connection lifecycle | Existing Otheryn ownership retained; no wholesale replacement. |
| framing | Explicit profile-owned modern and legacy framing contracts. |
| checksum/sequence | Typed rejection and post-validation accepted-sequence commit. |
| crypto/compression | Profile-owned XTEA payload and compression contracts; no new algorithm. |
| protocol compatibility | Existing six target protocol profiles preserved. |
| login protocol | Explicitly deferred to OAM-054. |
| gameplay dispatch | Unchanged and outside this package. |
| client | Maintained client used as required inventory evidence; no client mutation. |
| persistence/schema | Not applicable; no schema or durable gameplay state change. |
| runtime tests | Full target CTest and platform runtime smoke passed. |
| security | SEC-005 evidence informed bounded invariants; complete exploit resistance is not claimed. |
| operations | No production endpoint, credential, host or deployment action. |

## Rejected alternatives

- retain the upstream-derived target transport unchanged and classify it as `REUSE`;
- copy Canary `Connection` or `ProtocolGame` wholesale;
- consume sequence state before full checksum/XTEA acceptance;
- change production runtime to accommodate a donor-only test helper;
- treat a transient dependency download reset as a source defect;
- begin `login-protocol` before transport lifecycle and governance complete.

## Nonclaims

OAM-053 does not claim complete wire compatibility for all clients, arbitrary account authorization, login or character-list correctness, gameplay packet correctness, session lifecycle race safety, economy or transaction safety, Redis/multichannel correctness, hostile-server maintained-client resilience, sustained capacity, denial-of-service resistance or production deployment safety.
