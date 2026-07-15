---
task_id: CAN-20260714-protocolgame-leave-game-dispatch
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-20260714-protocolgame-leave-game-dispatch
status: active
agent: GPT-5.6-Thinking
branch: fix/protocolgame-leave-game-dispatch
base_branch: main
created: 2026-07-14T20:30:00+02:00
updated: 2026-07-15T09:05:00+02:00
last_verified_commit: "0352a5a15f5688c8b8e3cd7c38543f0ccc402901"
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
    - src/server/network/protocol/protocol.hpp
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
4. Trace the validated `ProtocolGame` opcode `0x14` dispatch and exact-player logout path including every denial path.
5. Trace exact player removal, release and player-client identity.
6. Determine whether session B closes in transport validation, packet dispatch, or stale session cleanup using the post-merge physical E2E evidence.
7. Keep stable identity diagnostics for connection ID, protocol address, player GUID/runtime ID, callback begin/dispatch/complete, logout result, release, removal, and stale-session rejection.

# Acceptance criteria

- [x] Deterministic no-sleep test queues a real leave-game packet, closes/removes external connection/protocol ownership, drains the dispatcher, and observes exactly one parse, removal and release.
- [x] The exact player session is removed or fully detached immediately after an accepted leave-game dispatch.
- [x] A denied logout is reported explicitly and cannot silently degrade into a detached ghost player.
- [x] Delayed A release/logout work cannot detach or remove active B.
- [x] Transport mismatch diagnostics distinguish received sequence, expected sequence, connection, and protocol without relaxing validation.
- [x] Sequence rejection does not advance the last accepted client sequence.
- [x] No timers, sleeps, retry windows, relog-delay increases, callback suppression, two-process substitution, packet-validation relaxation, or OTClient change.
- [x] Full implementation-head C++ CI passes on Linux debug/tests, Linux release including Global smoke, Windows CMake, Windows Solution, macOS and Docker (CI #2329, run `29395955944`, head `0352a5a15f5688c8b8e3cd7c38543f0ccc402901`).
- [ ] After merge, unchanged same-process PR #245 E2E passes both complete sessions.

# Work log

## 2026-07-14T22:05:00+02:00 — takeover

- User explicitly transferred PR #360 and the previous agent's task to GPT-5.6 Thinking.
- Verified the PR still contained only this task record at head `b3aa436be2a88deb20179e15dd56fa9049a5dfda`; no implementation had been pushed.
- Re-read run #34 artifacts and corrected the packet-sequence hypothesis: wire sequence ordering is monotonic, so OTClient PR #11 is not the evidence-backed fix for #245.
- Expanded the owned transport paths narrowly to permit non-relaxing mismatch diagnostics required to locate the production close.
- The next commit must add production-path diagnostics and deterministic coverage before another physical run.

## 2026-07-15T00:43:00+02:00 — transport correctness and exact leave dispatch seam

- Re-verified PR #360 before writes at head `ecb735b0b8d56350ef4b0815e381513b8a5a3694`; it still contained no production implementation and no newer third-party work.
- Added typed inbound transport outcomes: accepted, zero sequence, sequence mismatch, checksum mismatch, decrypt failure and malformed frame.
- Changed current-game sequence handling to calculate and compare the expected sequence before mutation, and to persist it only after the entire frame passes checksum and decrypt validation.
- Added stable lifecycle diagnostics for transport rejection, accepted `0x14`, queue publication, dispatcher begin and dispatcher completion with exact connection/protocol identity.
- Added deterministic production-class tests proving that zero, mismatch, duplicate and malformed frames do not consume the next accepted sequence.
- Added a narrow virtual leave-game dispatch/release seam in `Protocol`; it reuses the #339 strong callback ownership instead of introducing a parallel lifetime mechanism.

## 2026-07-15T09:05:00+02:00 — exact-session completion and current-head validation

- Added explicit `ClientLeaveGameState` transitions: none, queued, dispatching, completed, denied and rejected.
- The validated `0x14` path captures the exact player on the dispatcher and requires both `player == expectedPlayer` and `expectedPlayer->client == self` before mutation; identity is checked again after production logout callbacks.
- `g_game().removeCreature(expectedPlayer, true)` is now observed instead of silently ignored; remove failure becomes explicit `Rejected` state.
- Connection release is scoped through `releaseFromConnection()` so a validated leave cannot release before dispatch completion, duplicate completion is ignored, and stale A cannot clear B.
- Denied/rejected exact sessions preserve the live `Player -> ProtocolGame` edge while dropping the reverse edge during connection release, preventing a detached online ghost.
- Added no-sleep coverage for accepted leave with close-before-dispatch, duplicate completion, stale A vs active B, explicit denial, remove failure and inbound transport rejection without sequence advance.
- Corrected the unit fixture to use Canary's dedicated unit-test `Player()` constructor and isolated only runtime map/Lua/output side effects when the `BUILD_TESTS` remove callback seam is active; production behavior is unchanged.
- CI #2329 (`29395955944`) passed the full implementation head `0352a5a15f5688c8b8e3cd7c38543f0ccc402901`: Linux debug including all tests, Linux release including Canary and Global runtime smoke, Windows CMake, Windows Solution, macOS and Docker. The prior one-off Global smoke load-order failure did not reproduce on the unchanged datapack in #2329.
- PR #360 is ready for final docs-only-head validation and squash merge; the remaining program-level criterion is the unchanged one-process physical E2E on #245 after #360 lands on `main`.

# Do not repeat

- Do not rerun PR #245 on server code that does not contain the merged #360 fix.
- Do not modify OTClient without new packet evidence that it failed to send leave-game or close TCP.
- Do not use player GUID alone as a session generation token.
- Do not treat delayed ping-timeout persistence as successful safe logout.
- Do not infer protocol frame boundaries from TCP segment boundaries.
