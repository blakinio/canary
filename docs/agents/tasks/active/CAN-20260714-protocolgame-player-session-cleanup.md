---
task_id: CAN-20260714-protocolgame-player-session-cleanup
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-20260714-protocolgame-player-session-cleanup
status: ready_for_merge
agent: chatgpt-e2e-platform
branch: fix/protocolgame-player-session-cleanup
base_branch: main
created: 2026-07-14T16:30:00+02:00
updated: 2026-07-14T18:05:00+02:00
last_verified_commit: "41f8be155c80c29bc51c4c1ead6ad91e7e2159dc"
risk: high
related_issue: ""
related_pr: "blakinio/canary#339"
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

The proven race was between an already-received dispatcher packet callback and `Connection::close()`: release could execute before the queued `ClientLeaveGame` callback, detach `Player::client`, and leave the later logout callback without its exact live session.

# Required invariant

An obsolete `ProtocolGame`, `Connection`, ping task, connect task or logout task may operate only on the exact session generation it captured. It must never detach, remove, kick, close or otherwise mutate a replacement `ProtocolGame` for the same `Player` identity.

# Implemented repair

- `Connection` marks the protocol callback as pending before publishing it to the dispatcher.
- `Connection::close()` records a release request and defers `Protocol::release()` while that callback is pending.
- Dispatcher completion consumes the release request exactly once and schedules release only after the packet callback finishes.
- `ProtocolGame::release()` retains exact `shared_ptr` ownership comparison before clearing `player->client`, so stale session A cannot detach replacement session B.
- Lifecycle diagnostics include connection ID, connection/protocol addresses, release state, and connection-I/O versus dispatcher context.
- The deterministic unit test uses no sleeps and proves release deferral, one-shot completion, and stale-A ownership protection for current B.

# Acceptance criteria

- [x] An already-received `ClientLeaveGame` callback completes before connection release can detach its exact protocol session.
- [x] Connection release is deferred while a dispatcher callback is pending and is consumed exactly once after completion.
- [x] A stale protocol cannot clear a replacement protocol attached to the same character.
- [x] The deterministic test covers pending callback, release request, callback completion, duplicate completion, and stale A versus current B.
- [x] Diagnostics identify connection generation, protocol identity and execution context without using time windows for correctness.
- [x] No relog-delay increase, sleep-based workaround, retry window, two-process substitution or server-side packet validation relaxation.
- [x] Current-head focused tests and required CI pass.
- [ ] Canary PR #245 reruns the unchanged same-process login/logout/relog scenario after this PR merges.

# Work log

## 2026-07-14T16:30:00+02:00

- Read repository governance, E2E program, current E2E task, current protocol/connection/player source and test registration.
- Confirmed no open Canary PR already owns this cleanup responsibility.
- Created an isolated branch from current `main` and claimed only the server lifecycle/test paths required for diagnosis and repair.
- Paused any assumption that another OTClient change is required; the next change must be justified by server-side identity evidence.

## 2026-07-14T18:05:00+02:00

- Implemented an explicit per-Connection callback/release gate.
- Preserved exact ProtocolGame ownership checks and added identity diagnostics.
- Added deterministic no-sleep regression coverage.
- Reviewed the six changed paths; no E2E scenario, OTClient pin, relog delay, packet validation, retry or sleep behavior changed.
- Verified current-head workflow run `CI #2080`, `autofix.ci #1358`, `Agent Task Ownership #968`, and `Wheel of Destiny Validation #131` all completed successfully for `41f8be155c80c29bc51c4c1ead6ad91e7e2159dc`.

# Validation

| Commit | Check | Result | Notes |
|---|---|---|---|
| `c2db33e8ec2419f6cb6cae2bfec593176ca2c106` | Universal Agent E2E run #33 | failed with actionable lifecycle evidence | Session A TCP closed, but its player remained until ping-timeout cleanup; session B then started and was closed shortly afterwards. |
| `41f8be155c80c29bc51c4c1ead6ad91e7e2159dc` | deterministic session lifecycle test | passed in CI #2080 | No sleeps; release deferral and stale-session identity behavior are deterministic. |
| `41f8be155c80c29bc51c4c1ead6ad91e7e2159dc` | required current-head workflows | passed | CI, autofix, task ownership, and wheel validation all green. |

# Do not repeat

- Do not replace the scenario with two OTClient processes.
- Do not increase `relog_delay_ms`.
- Do not add sleeps, retry windows or time-based callback suppression.
- Do not weaken transport sequence validation.
- Do not modify OTClient again without new evidence that it failed to send leave-game or close its transport.
- Do not use player GUID/runtime ID as a generation-safe callback token.

# Handoff

Merge PR #339 after the documentation-only current-head checks pass. Then update PR #245 onto the merged server repair and run the unchanged same-process two-session Universal Agent E2E with OTClient pinned to `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`.