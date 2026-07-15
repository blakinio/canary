---
task_id: CAN-20260715-current-game-first-frame-framing
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-20260715-current-game-first-frame-framing
status: implementing
agent: GPT-5.5-Thinking
branch: fix/current-game-first-frame-framing
base_branch: main
created: 2026-07-15T12:20:00+02:00
updated: 2026-07-15T12:20:00+02:00
last_verified_commit: "c67c84749ffd1de04983be9ae9841b6ca5756aed"
risk: high
related_issue: ""
related_pr: ""
depends_on:
  - CAN-20260714-protocolgame-leave-game-dispatch
  - CAN-20260713-universal-agent-e2e-platform
blocks:
  - blakinio/canary#245
owned_paths:
  exclusive:
    - src/server/network/connection/connection.cpp
    - src/server/network/protocol/protocol_profile.hpp
    - src/server/network/protocol/protocol_profile.cpp
    - src/server/network/protocol/transport_codec.cpp
    - src/server/network/protocol/transport_codec.hpp
    - tests/unit/server/network/protocol/transport_codec_test.cpp
    - docs/agents/tasks/active/CAN-20260715-current-game-first-frame-framing.md
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
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
  - TransportCodec first-inbound body-size decoding contract
cross_repo_tasks: []
---

# Goal

Correct the modern current-game first inbound frame length so Canary consumes the complete physical OTClient login packet before switching to sequenced encrypted game traffic. Preserve checksum-free `CurrentGamePlain` framing after negotiation and make no OTClient or E2E timing change.

# Confirmed evidence

Unchanged one-process Universal Agent E2E run #35 (`29398519891`) used PR #245 head `2fecabe61f9557101322cee390dcf9a65dce07cc`, Canary merge head `b02dea1c05bedb198452c94784e1afe3eac9f27b`, and pinned OTClient `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`.

The retained PCAP proves:

- each modern game login packet is 174 bytes on the wire;
- its outer two-byte block-count header is `0x0015` (21 blocks);
- the physical body therefore has `21 * 8 + 4 = 172` bytes;
- `CurrentGamePlain.decodeBodySize()` currently returns only `21 * 8 = 168` because `modernLengthExtraBytes == 0`;
- Canary therefore leaves exactly four bytes of the first login frame unread in the socket;
- the next header/body read starts four bytes late and produces deterministic false sequence mismatches such as received `65536` while expected `1`;
- the actual client wire sequences are monotonic `1,2,3` for session A and `1,2,3,4` for session B.

This is independent of the merged leave-game lifecycle: `ClientLeaveGame` never reaches dispatch because the transport stream is already desynchronized.

# Invariant

The initial modern game handshake is asymmetric: the reusable checksum-free `CurrentGamePlain` profile must keep its normal post-negotiation framing, while the first inbound current-game login frame must consume the additional four bytes represented outside the block count. The first-frame exception must be explicit and bounded; subsequent frames remain governed by the negotiated profile.

# Acceptance criteria

- [ ] A focused deterministic test proves raw block count `0x0015` consumes 172 body bytes for the first inbound current-game frame and only the profile's normal size afterward.
- [ ] No four bytes of the first physical login frame remain to contaminate the next header read.
- [ ] Existing checksum-free `CurrentGamePlain` encode/decode behavior remains unchanged for non-first frames.
- [ ] Sequenced game packets `1,2,3...` are accepted in order after login; validation is not relaxed.
- [ ] No OTClient change, no E2E script change, no delays, retries, timers or two-process workaround.
- [ ] Relevant C++ tests and full required CI pass on the exact current head.
- [ ] PR #245 is synchronized with the merged fix and the unchanged one-process `login/relog` physical E2E passes both sessions before #245 is merged.

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
- Do not restore `CurrentGamePlain.modernLengthExtraBytes = CHECKSUM_LENGTH` globally; PR #155 correctly established the reusable checksum-free post-negotiation contract.
- Do not infer application frames from TCP segment boundaries; use the outer block-count framing.
