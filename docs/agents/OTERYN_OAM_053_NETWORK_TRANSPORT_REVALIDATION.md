# OAM-053 Network Transport revalidation

Status: **governance complete; Canary lifecycle pending**

Program: `CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION`

Coordination: `OAM-053`

## Final disposition

```text
network-transport → ADAPT
```

Otheryn retained its existing connection, multiprotocol and protocol-session-handoff architecture. The target adapted only evidence-backed transport profile authority, framing, sequence/XTEA rejection and recovery invariants absent from its upstream-derived codec.

## Pinned delivery chain

```text
Canary preflight merge:     6a9e6cf106b3e0193fb6a9d923a37cee38888f66
Otheryn feature head:       7376eff79e166595a91f4581d8eef6e6c228e754
Otheryn feature merge:      c25fff72dd8b89f6ef1565af2d84ab9eef33dce9
Otheryn lifecycle head:     34036aa6db8e6f8942a970a214f09493d1fbcd51
Otheryn lifecycle merge:    9703da845384423ad85883216bf8853642c21bcd
Canary governance head:     bacd3b880487c8c35d0e1230b956520cd201ad7c
Canary governance merge:    91d96d8aa72b3851c4db89a71de9ea9722bcc63b
upstream evidence baseline: 7644bcbcbbad4a09e52a5707ed531e4dd21d8a79
maintained OTClient:        5568cb6f5e2fd6162c78cde304deea5d32461e05
```

Pinned Canary donors:

- authoritative transport profiles: `bbff04524bbb99ab54c9571c24382399b904cbd8`;
- checksum-free block-count symmetry: `4535836d4df0fc669033ed73f525754a1a2d1b40`;
- complete captured current first frame: `5c750e13fb95f46225807b8907a95ce3091283c8`;
- SEC-005 current-main runtime recovery: `1408aaa886240034a90fc33873e9b9e0fa47cab6`.

## Why ADAPT

Otheryn already contained the complete connection and protocol-profile surfaces, so wholesale migration was invalid. Pure `REUSE` was also invalid because the target still had:

- one broad current-modern transport contract rather than explicit login, sequenced-game and checksum-free-game profiles;
- checksum/compression authority partly retained in mutable `Protocol` state;
- accepted sequence state advancing before complete checksum/XTEA acceptance;
- untyped inbound rejection without expected/received sequence evidence;
- asymmetric checksum-free block-count encoding;
- incomplete fail-closed guards around truncated checksum/header and encrypted padding boundaries.

The target therefore integrated only transport-owned invariants while preserving later Otheryn multiprotocol, typed profile and session-handoff evolution.

## Delivered target behavior

- explicit current login, current sequenced-game and current checksum-free-game profiles;
- complete profile authority for framing, checksum, compression and encrypted layout;
- typed inbound outcomes with expected/received sequence evidence;
- accepted sequence commit only after checksum and decrypt acceptance;
- checksum-free block-count encode/decode symmetry;
- captured first-frame sizing of 172 bytes with sequence/checksum and 168 bytes without checksum;
- fail-closed truncated checksum, invalid XTEA block size, missing inner length/padding and oversized padding;
- deterministic regressions for profile contracts, sizing, symmetry, truncation, zero, gap, replay and decrypt rejection.

No wholesale `Connection` or `ProtocolGame` replacement, account-login semantics, character-list behavior, gameplay opcode layout, schema, datapack, client, deployment or production configuration was added.

## Exact target evidence

Feature head `7376eff79e166595a91f4581d8eef6e6c228e754` passed:

- Otheryn CI `30225971903`;
- Otheryn `Required` `30225971757`;
- Otheryn autofix `30225971771` with no follow-up commit;
- Fast Checks and Lua;
- Linux release/debug, full Linux CTest, Canary runtime smoke and schema import;
- Docker, macOS and Windows build/runtime gates.

PR #163 changed exactly eleven intended paths, had `behind_by=0`, no comments, reviews or review threads, and squash-merged with expected-head protection as `c25fff72dd8b89f6ef1565af2d84ab9eef33dce9`.

Target lifecycle PR #164 changed only the active/archive task pair and final report, passed Required `30226763484`, had a clean three-path audit and merged as `9703da845384423ad85883216bf8853642c21bcd`.

## Canary governance evidence

Governance head `bacd3b880487c8c35d0e1230b956520cd201ad7c` passed:

- Agent Task Ownership `30226993622`;
- CI `30226993717`, including Fast Checks, Lua and stable `Required`.

Runtime build jobs were correctly not applicable for the two-file documentation scope. PR #980 changed exactly the active checkpoint and this durable report, had `behind_by=0`, no comments, reviews or review threads, and squash-merged with expected-head protection as `91d96d8aa72b3851c4db89a71de9ea9722bcc63b`.

## First failures

- The first target Ready head used donor-only `Dispatcher::executeSerialEventsForTest()`. Target-native `close(true)` cleanup was sufficient because focused connections were never accepted into `Connection::protocol`; the subsequent full CTest passed.
- The first Docker attempt failed before project compilation with a transient `curl: (35) Recv failure: Connection reset by peer` during vcpkg bootstrap. No source or Docker change was made; the next full run passed.

## Boundary classification

| Boundary | Result |
|---|---|
| ownership | Target and Canary governance ownership complete; no active overlapping transport owner. |
| connection lifecycle | Existing Otheryn ownership retained; no wholesale replacement. |
| framing | Explicit profile-owned modern and legacy contracts. |
| checksum/sequence | Typed rejection and post-validation accepted-sequence commit. |
| crypto/compression | Profile-owned XTEA payload and compression contracts; no new algorithm. |
| protocol compatibility | Existing six target protocol profiles preserved. |
| login protocol | Deferred to OAM-054. |
| gameplay/client/schema | Unchanged and outside this package. |
| operations | No endpoint, credential, host or production action. |

## Nonclaims

OAM-053 does not claim complete wire compatibility for all clients, arbitrary account authorization, login or character-list correctness, gameplay packet correctness, session lifecycle race safety, economy or transaction safety, Redis/multichannel correctness, hostile-server client resilience, sustained capacity, denial-of-service resistance or production deployment safety.

## Lifecycle

The completed Canary task is archived at `docs/agents/tasks/archive/CAN-20260726-oteryn-oam053-eligibility-preflight.md`. After the lifecycle PR merges, the programme must be reconciled durably before OAM-054 starts.
