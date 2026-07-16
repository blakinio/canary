---
task_id: CAN-20260715-current-game-first-frame-framing
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-20260715-current-game-first-frame-framing
status: validating
agent: GPT-5.5-Thinking
branch: fix/current-game-first-frame-framing
base_branch: main
created: 2026-07-15T12:20:00+02:00
updated: 2026-07-15T12:35:00+02:00
last_verified_commit: "e2a80cbdbce40029907939b98420c07296bce1b2"
risk: high
related_issue: ""
related_pr: "blakinio/canary#375"
depends_on:
  - CAN-20260714-protocolgame-leave-game-dispatch
  - CAN-20260713-universal-agent-e2e-platform
blocks:
  - blakinio/canary#245
owned_paths:
  exclusive:
    - src/server/network/protocol/protocol_profile.cpp
    - tests/unit/server/network/protocol/transport_codec_test.cpp
    - docs/agents/tasks/active/CAN-20260715-current-game-first-frame-framing.md
  shared: []
  read_only:
    - .github/workflows/universal-agent-e2e.yml
    - tools/e2e/**
    - tests/e2e/**
    - docs/agents/tasks/active/CAN-20260713-universal-agent-e2e-platform.md
    - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
modules_touched:
  - network transport framing
  - current game login handshake
  - physical-client E2E blocker diagnosis
reuses:
  - TransportProfile and TransportCodec
  - existing Connection first-packet path
  - merged inbound sequence diagnostics from #360
public_interfaces:
  - none
cross_repo_tasks: []
---

# Goal

Correct the modern current-game first inbound frame length so Canary consumes the complete physical OTClient login packet before processing sequenced encrypted game traffic. Preserve checksum-free `CurrentGamePlain` framing and make no OTClient or E2E timing change.

# Confirmed evidence

Unchanged one-process Universal Agent E2E run #35 (`29398519891`) used PR #245 head `2fecabe61f9557101322cee390dcf9a65dce07cc`, Canary merge head `b02dea1c05bedb198452c94784e1afe3eac9f27b`, and pinned OTClient `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`.

The retained PCAP proves:

- each modern game login packet is 174 bytes on the wire;
- its outer two-byte block-count header is `0x0015` (21 blocks);
- the physical body therefore has `21 * 8 + 4 = 172` bytes;
- the previous initial `CurrentGamePlain` profile decoded only `21 * 8 = 168` because `modernLengthExtraBytes == 0`;
- Canary therefore left exactly four bytes of the first login frame unread in the socket;
- the next header/body read started four bytes late and produced deterministic false sequence mismatches such as received `65536` while expected `1`;
- the actual client wire sequences are monotonic `1,2,3` for session A and `1,2,3,4` for session B.

This is independent of the merged leave-game lifecycle: `ClientLeaveGame` never reached dispatch because the transport stream was already desynchronized.

# Implementation decision

The current modern handshake now selects `CurrentGameSequence` as its initial transport profile. This is a framing correction, not a relaxation:

- the first game packet is handled by `Connection::parsePacket` through `ProtocolGame::onRecvFirstMessage` and does not pass through `TransportCodec::prepareInbound`, so no sequence validation is applied to the login packet itself;
- `CurrentGameSequence.decodeBodySize(0x0015)` consumes the full captured 172-byte body because the modern block count carries the four-byte sequence/checksum envelope outside the encrypted block count;
- after the login packet negotiates sequenced packets, the same strict sequence profile remains active;
- `CurrentGamePlain` remains unchanged with `modernLengthExtraBytes = 0`, preserving the checksum-free block-count contract established by PR #155.

# Acceptance criteria

- [x] A focused deterministic test proves raw block count `0x0015` consumes 172 body bytes for the default modern initial transport.
- [x] A focused regression test proves `CurrentGamePlain` still decodes the same block count as 168 checksum-free body bytes.
- [x] No OTClient change, no E2E script change, no delays, retries, timers or two-process workaround.
- [x] Sequence validation remains strict and the existing rejection/non-advance tests remain unchanged.
- [ ] Relevant C++ tests and full required CI pass on the exact current head.
- [ ] PR #375 passes review/merge gates and is squash-merged.
- [ ] PR #245 is synchronized with the merged fix and the unchanged one-process `login/relog` physical E2E passes both sessions before #245 is merged.

# Work log

## 2026-07-15T12:35:00+02:00 — root cause and minimal implementation

- Reconstructed the physical game-port stream from run #35 rather than treating TCP segments as protocol frames.
- Proved the first modern login packet body is 172 bytes while the initial `CurrentGamePlain` decoder requested 168, leaving exactly four bytes queued in the socket.
- Confirmed the resulting four-byte offset explains the observed false sequence value `65536` while the PCAP itself carries monotonic client sequences.
- Changed only `currentInitialBehavior.transport` from `CurrentGamePlain` to `CurrentGameSequence`.
- Added two deterministic body-size regressions using the captured `0x0015` block count; no runtime timing or client behavior changed.
- Reviewed the source patch after the full-file GitHub contents update: the semantic production diff is exactly the one-line initial-profile change.

# Preflight

- writable repository: `blakinio/canary` only;
- base: `main@c67c84749ffd1de04983be9ae9841b6ca5756aed`;
- open PR #245 owns only universal E2E files and is read-only to this task;
- open PRs #316 and #374 do not overlap transport runtime paths;
- merged PR #360 task ownership was archived before this task claimed the transport paths;
- upstream repositories remain read-only.

# Do not repeat

- Do not modify the pinned OTClient to hide server framing drift.
- Do not weaken sequence validation.
- Do not restore `CurrentGamePlain.modernLengthExtraBytes = CHECKSUM_LENGTH` globally; PR #155 correctly established the reusable checksum-free contract.
- Do not infer application frames from TCP segment boundaries; use the outer block-count framing.
