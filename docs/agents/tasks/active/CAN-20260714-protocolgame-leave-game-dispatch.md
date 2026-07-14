---
task_id: CAN-20260714-protocolgame-leave-game-dispatch
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-20260714-protocolgame-leave-game-dispatch
status: active
agent: GPT-5.6-Thinking
branch: fix/protocolgame-leave-game-dispatch
base_branch: main
created: 2026-07-14T20:30:00+02:00
updated: 2026-07-14T22:05:00+02:00
last_verified_commit: "b3aa436be2a88deb20179e15dd56fa9049a5dfda"
risk: high
related_issue: ""
related_pr: "blakinio/canary#360"
depends_on:
  - CAN-20260713-universal-agent-e2e-platform
blocks:
  - blakinio/canary#245
owned_paths:
  exclusive:
    - src/server/network/connection/connection.cpp
    - src/server/network/connection/connection.hpp
    - src/server/network/protocol/protocol.cpp
    - src/server/network/protocol/protocolgame.cpp
    - src/server/network/protocol/protocolgame.hpp
    - src/server/network/protocol/transport_codec.cpp
    - src/server/network/protocol/transport_codec.hpp
    - tests/unit/server/CMakeLists.txt
    - tests/unit/server/network/protocol/**
    - docs/agents/tasks/active/CAN-20260714-protocolgame-leave-game-dispatch.md
  shared: []
  read_only:
    - .github/workflows/universal-agent-e2e.yml
    - tools/e2e/**
    - tests/e2e/**
    - docs/agents/ACTIVE_WORK.md
    - docs/agents/tasks/active/CAN-20260713-universal-agent-e2e-platform.md
modules_touched:
  - Connection receive callback lifecycle
  - Protocol dispatcher ownership
  - ProtocolGame leave-game cleanup
  - Current game transport diagnostics
reuses:
  - ProtocolReleaseGate merged in #339
  - exact shared_ptr identity checks
  - existing dispatcher test seam
public_interfaces:
  - none planned
cross_repo_tasks: []
---

# Goal

Make an already-received `ClientLeaveGame` packet execute exactly once and complete the exact `ProtocolGame -> Player -> Connection` cleanup before stale session work can affect a replacement session for the same character.

# Confirmed evidence

Universal Agent E2E run #34 (`29355080465`) used Canary test merge head `b9b36e57c5a24bf3374ddb0c5654106d351a4886` and OTClient squash `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`.

The artifact proves:

- session A reached `login_1=success` and `online_stable_1=confirmed`;
- OTClient emitted `logout_request_1=safe`, `logout_1=complete`, and `transport_closed_1=confirmed`;
- the session-A packet record contains outbound leave-game opcode `0x14`;
- the retained PCAP shows monotonic client sequence values `1, 2, 3` for session A and `1, 2, 3, 4` for session B; the earlier `1, 1, 3` interpretation was incorrect TCP-frame parsing;
- Canary acknowledged the session-A leave-game TCP payload and the transport closed immediately;
- Canary did not persist logout/remove the player until roughly 53 seconds later through ping timeout with `has client: false`;
- session B reached `login_2=success` and was disconnected after its two channel-open requests, before `online_stable_2`;
- DB persistence and two packet records succeeded, so the first failed contract marker is `online_stable_2=confirmed`.

PR #339 (`06286302ae429e6ba05a152e3b171b7a43046a0c`) added callback ownership and release deferral, but run #34 proves that the production leave-game path still does not complete immediate cleanup.

# Invariant

An already-received packet callback owns its exact message, `Connection`, and `Protocol` until parsing and completion. It executes exactly once. Any release, ping, logout, or disconnect work captured by session A may mutate only session A and must not close, detach, remove, or otherwise affect session B.

# Required investigation

1. Trace transport acceptance/rejection with received and expected sequence values without mutating the accepted sequence on rejection.
2. Trace `Protocol::sendRecvMessageCallback` publication and completion.
3. Trace `Connection::close`, `resumeWork`, and `ProtocolReleaseGate` state transitions.
4. Trace `ProtocolGame::parsePacket` opcode `0x14` and `ProtocolGame::logout` including every denial path.
5. Trace exact player removal, persistence, client detachment, and ping task cancellation.
6. Determine whether session B closes in transport validation, packet dispatch, or channel handling.
7. Add identity diagnostics for connection ID, protocol address, player GUID/runtime ID, callback begin/dispatch/complete, logout result, release, removal, and stale-session rejection.

# Acceptance criteria

- [ ] Deterministic no-sleep test queues a real leave-game packet, closes/removes manager ownership, drains the dispatcher, and observes exactly one parse and exactly one release.
- [ ] The exact player session is removed or fully detached immediately after an accepted leave-game dispatch.
- [ ] A denied logout is reported explicitly and cannot silently degrade into a detached ghost player.
- [ ] Delayed A release/ping/logout callbacks cannot affect active B.
- [ ] Transport mismatch diagnostics distinguish received sequence, expected sequence, connection, and protocol without relaxing validation.
- [ ] No timers, sleeps, retry windows, relog-delay increases, callback suppression, two-process substitution, packet-validation relaxation, or OTClient change.
- [ ] Full current-head C++ CI passes.
- [ ] After merge, unchanged same-process PR #245 E2E passes both complete sessions.

# Work log

## 2026-07-14T22:05:00+02:00 — takeover

- User explicitly transferred PR #360 and the previous agent's task to GPT-5.6 Thinking.
- Verified the PR still contained only this task record at head `b3aa436be2a88deb20179e15dd56fa9049a5dfda`; no implementation had been pushed.
- Re-read run #34 artifacts and corrected the packet-sequence hypothesis: wire sequence ordering is monotonic, so OTClient PR #11 is not the evidence-backed fix for #245.
- Expanded the owned transport paths narrowly to permit non-relaxing mismatch diagnostics required to locate the production close.
- The next commit must add production-path diagnostics and deterministic coverage before another physical run.

# Do not repeat

- Do not rerun PR #245 on unchanged server code.
- Do not modify OTClient without new packet evidence that it failed to send leave-game or close TCP.
- Do not use player GUID alone as a session generation token.
- Do not treat delayed ping-timeout persistence as successful safe logout.
- Do not infer protocol frame boundaries from TCP segment boundaries.
