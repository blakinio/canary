---
task_id: CAN-20260714-protocolgame-player-session-cleanup
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-20260714-protocolgame-player-session-cleanup
status: investigating
agent: chatgpt-e2e-platform
branch: fix/protocolgame-player-session-cleanup
base_branch: main
created: 2026-07-14T16:30:00+02:00
updated: 2026-07-14T16:30:00+02:00
last_verified_commit: "09f7049401253dd38c8f34506946c2fbe287d220"
risk: high
related_issue: ""
related_pr: "pending"
depends_on:
  - CAN-20260713-universal-agent-e2e-platform
blocks:
  - blakinio/canary#245
owned_paths:
  exclusive:
    - src/server/network/protocol/protocolgame.cpp
    - src/server/network/protocol/protocolgame.hpp
    - src/server/network/connection/connection.cpp
    - src/server/network/connection/connection.hpp
    - src/creatures/players/player.cpp
    - src/creatures/players/player.hpp
    - tests/unit/server/CMakeLists.txt
    - tests/unit/server/network/protocol/protocolgame_session_cleanup_test.cpp
    - docs/agents/tasks/active/CAN-20260714-protocolgame-player-session-cleanup.md
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
    - docs/agents/CROSS_REPO_CONTRACTS.md
    - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
  read_only:
    - .github/workflows/universal-agent-e2e.yml
    - tools/e2e/**
    - tests/e2e/**
    - docs/agents/tasks/active/CAN-20260713-universal-agent-e2e-platform.md
modules_touched:
  - ProtocolGame session lifecycle
  - Connection release lifecycle
  - Player online ownership and ping cleanup
reuses:
  - exact shared_ptr identity already used by ProtocolGame::release
  - existing dispatcher and scheduler task APIs
  - existing canary_ut server protocol test target
public_interfaces:
  - ProtocolGame logout/release ownership invariant
cross_repo_tasks:
  - OTC-20260714-protocol-session-reentrancy
---

# Goal

Make a closed game transport detach or remove its exact `Player` session immediately, while ensuring delayed callbacks from an obsolete `ProtocolGame`, `Connection`, logout task or ping task cannot mutate a replacement session for the same character.

The canonical proof remains two logins in one OTClient process. A second process must not replace the same-process relog scenario.

# Confirmed evidence

Universal Agent E2E run #33 used Canary head `c2db33e8ec2419f6cb6cae2bfec593176ca2c106` and OTClient squash `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`.

The retained packet capture establishes that session A sent its leave-game packet on the game connection and that Canary then closed the TCP transport. The server nevertheless retained `Knight 1` as an active `Player` with no client until the later ping-timeout path logged:

`Player Knight 1 has been kicked due to ping timeout. (has client: false)`

Only that delayed cleanup persisted logout and unblocked the replacement login. Session B completed handshake and game start, then its server transport was closed shortly afterwards.

Current source confirms the lifecycle split:

- client opcode `0x14` dispatches to `ProtocolGame::logout()`;
- clean logout calls `Game::removeCreature(player, true)`;
- `Connection::close()` separately schedules `Protocol::release()`;
- `ProtocolGame::release()` clears `player->client` only when the exact protocol still owns it, but does not remove the still-live `Player` from `Game`;
- login reconnects immediately to an existing `Player` whose `client` is null;
- player runtime IDs are stable per character and explicitly are not generation-safe handles.

# Required invariant

An obsolete `ProtocolGame`, `Connection`, ping task, connect task or logout task may operate only on the exact session generation it captured. It must never detach, remove, kick, close or otherwise mutate a replacement `ProtocolGame` for the same `Player` identity.

# Scope

1. Trace `ClientLeaveGame` (`0x14`) through `ProtocolGame::logout()` and `Game::removeCreature()`.
2. Trace connection close through `Connection::close()`, `ProtocolGame::release()` and player detachment.
3. Identify and cancel or identity-guard old ping, connect, logout and disconnect work.
4. Define behavior for an existing game `Player` with `client == nullptr` during login.
5. Add identity-based diagnostic evidence for player GUID/runtime ID, protocol generation, connection generation, dispatcher context and lifecycle transitions.
6. Add a deterministic server regression test with no sleeps or retry windows.

# Acceptance criteria

- [ ] `ClientLeaveGame` removes or fully detaches the exact current player session without waiting for ping timeout.
- [ ] Closing a current game connection cannot leave a live player indefinitely with `client == nullptr`.
- [ ] A stale protocol/connection/task cannot affect a replacement protocol attached to the same character.
- [ ] The deterministic test covers session A leave/cleanup, attachment of session B, then execution of stale A callbacks while B remains active.
- [ ] Diagnostics identify player GUID/runtime ID, protocol generation and connection generation at every relevant boundary without using time windows for correctness.
- [ ] No relog-delay increase, sleep-based workaround, retry window, two-process substitution or server-side packet validation relaxation.
- [ ] Current-head focused tests and required CI pass.
- [ ] Canary PR #245 reruns the unchanged same-process login/logout/relog scenario after this PR merges.

# Initial source findings

- `ProtocolGame::release()` already compares `player->client == shared_from_this()` before detaching, which is the correct identity primitive to extend.
- `ProtocolGame::logout()` sets `acceptPackets=false`, emits session-end information and calls `Game::removeCreature()`.
- `Connection::close()` schedules `protocol->release()` asynchronously after changing connection state.
- Existing-player login treats `client == nullptr` as reconnectable and attaches the new `ProtocolGame` immediately.
- Stable player runtime IDs must not be used as a session generation token.

# Work log

## 2026-07-14T16:30:00+02:00

- Read repository governance, E2E program, current E2E task, current protocol/connection/player source and test registration.
- Confirmed no open Canary PR already owns this cleanup responsibility.
- Created an isolated branch from current `main` and claimed only the server lifecycle/test paths required for diagnosis and repair.
- Paused any assumption that another OTClient change is required; the next change must be justified by server-side identity evidence.

# Validation

| Commit | Check | Result | Notes |
|---|---|---|---|
| `c2db33e8ec2419f6cb6cae2bfec593176ca2c106` | Universal Agent E2E run #33 | failed with actionable lifecycle evidence | Session A TCP closed, but its player remained until ping-timeout cleanup; session B then started and was closed shortly afterwards. |
| task branch | deterministic session lifecycle test | pending | Must execute controlled stale callbacks without sleep. |
| task branch | required CI | pending | Protocol/server C++ change requires focused tests plus Linux/Windows checks. |

# Do not repeat

- Do not replace the scenario with two OTClient processes.
- Do not increase `relog_delay_ms`.
- Do not add sleeps, retry windows or time-based callback suppression.
- Do not weaken transport sequence validation.
- Do not modify OTClient again without new evidence that it failed to send leave-game or close its transport.
- Do not use player GUID/runtime ID as a generation-safe callback token.

# Handoff

Start with run #33 chronology and exact source identity. The first server invariant to prove is whether `ProtocolGame::logout()` actually removes session A before its connection release callback, and why the retained player later reaches ping timeout with `client == nullptr`.