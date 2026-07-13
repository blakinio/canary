---
task_id: CAN-20260713-cyclopedia-live-e2e
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-E2E-CANARY-OTCLIENT
status: implementing
agent: chatgpt-e2e-prototype
branch: test/cyclopedia-live-e2e
base_branch: main
created: 2026-07-13T08:09:00+02:00
updated: 2026-07-13T10:00:00+02:00
last_verified_commit: f8a8efe704bbb342469623f8d92a90e1f01f9dc8
risk: medium
related_issue: ""
related_pr: "224"
depends_on:
  - CAN-20260713-agent-program-ownership
blocks:
  - CAN-E2E-PLATFORM-BOOTSTRAP
owned_paths:
  exclusive:
    - .github/workflows/cyclopedia-live-e2e.yml
    - tools/e2e/cyclopedia_otclient_e2e.lua
    - docker/data/01-test_account.sql
    - docs/agents/tasks/active/CAN-20260713-cyclopedia-live-e2e.md
    - src/lua/modules/modules.cpp
    - src/server/network/protocol/transport_codec.cpp
  shared: []
  read_only:
    - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
    - src/config/configmanager.cpp
    - src/server/network/connection/connection.cpp
    - src/server/network/protocol/protocol.cpp
    - src/server/network/protocol/protocolgame.cpp
    - src/server/network/protocol/protocollogin.cpp
modules_touched:
  - physical-client E2E prototype
  - Cyclopedia scenario automation
  - temporary inbound transport diagnostics
reuses:
  - reusable Linux Canary build workflow
  - existing Docker test-account and player fixtures
  - global datapack and map download contract
  - maintained OTClient Linux artifact
public_interfaces:
  - Cyclopedia E2E result markers
cross_repo_tasks:
  - OTC-E2E-CLIENT-AUTOMATION
---

# Goal

Prove Bestiary, Charms and Bosstiary through a real 15.25 OTClient connected to an exact-head Canary server in two separate login sessions, with disposable MySQL state and reviewable evidence.

# Acceptance criteria

- [ ] Exact Canary head builds and starts with the global datapack and map.
- [x] Real OTClient 15.25 logs into `Knight 1` through the native modern game transport.
- [ ] Bestiary, Charms and Bosstiary parser events are observed during session one.
- [ ] Safe logout and a complete second login succeed.
- [ ] The same three Cyclopedia response families are observed after relog.
- [ ] Database evidence confirms online state during the test and clean offline state afterward.
- [x] Logs, hashes, SQL snapshots, packet records, TCP capture, result markers and a screenshot are uploaded on failure.
- [x] No map, gameplay, schema, production state or committed client asset is modified.
- [ ] Temporary diagnostic source changes are removed or converted into justified permanent hardening before merge.
- [ ] Current-head ownership and repository CI pass.
- [ ] Complete live E2E workflow passes and its artifact is reviewed.

# Confirmed context

- Merged PR #222 defines this PR as the first bounded prototype for `CAN-PROGRAM-E2E-PLATFORM`.
- Canary's default `authType` is `password`.
- The modern game login layout accepts a session-key field containing `account-or-email`, a newline, and the password when password authentication is active.
- Account fixture 101 uses email `test1@example.com`, password `test`, and owns `Knight 1`.
- Current client and asset version resolve to 15.25 in the workflow.
- The real client completes protocol login, pending-game, enter-game and game-start callbacks.
- The first Bestiary request is a single plaintext opcode `0xE1` in the OTClient packet record.
- TCP evidence shows the server endpoint sends FIN/RST immediately after receiving the encrypted packet containing `0xE1`.
- A runtime-only recvbyte module registered for byte 225 did not receive the packet, so the failure currently appears before Lua recvbyte dispatch or the module registration needs explicit load verification.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| PR #222 | Universal E2E ownership and scenario boundary | `docs/agents/programs/E2E_AUTOMATION_PROGRAM.md` | Prevents this prototype from becoming duplicated per-feature infrastructure. |
| Reusable Linux build | Exact-head Canary artifact | `.github/workflows/reusable-build-linux.yml` | Existing supported build path. |
| Test fixtures | Disposable account and characters | `docker/data/01-test_account.sql`, `docker/data/02-test_account_players.sql` | Deterministic existing fixture set. |
| Canary protocol profiles | Native modern game transport and password-mode session key | `src/server/network/protocol/protocolgame.cpp` | Removes the need for a custom account-login framing shim. |
| OTClient packet recorder | Decrypted client/server packet evidence | `cyclopedia-session-1.record` workflow artifact | Proves the requested client opcode without guessing from encrypted TCP bytes. |

# Ownership and overlap check

- Program record: `docs/agents/programs/E2E_AUTOMATION_PROGRAM.md`.
- Open PRs inspected: #224 and current E2E/coordination work.
- Active tasks inspected: no structured exclusive claim was found for the two narrow diagnostic source files.
- Ownership checker: required after each new source claim.
- Exclusive claims: workflow, Cyclopedia Lua scenario, exact account fixture, task record, module dispatcher diagnostics and transport-codec diagnostics.
- Shared claims: none.
- Read-only dependencies: program contract and remaining Canary connection/protocol/authentication sources.
- Overlaps: none confirmed.
- Resolution: keep generic platform extraction out of this PR and remove temporary logging before final merge unless it is retained as justified failure hardening.

# Current state

The environment consistently starts MySQL, Canary, the global datapack/map, Xvfb and a real OTClient 15.25. The client logs `Knight 1` into the world. Roughly 500 ms later it sends Bestiary opcode `0xE1`; Canary immediately closes the game socket before any Bestiary response is recorded. Disabling unrelated OTClient startup modules did not change the result.

A runtime-only Lua module was injected for recvbyte 225 and returned a minimal `0xD5` response, but its callback marker was absent. The next bounded step is source-level logging around sequence/checksum validation and Lua recvbyte dispatch using an exact-head Canary build.

# Plan

1. Add narrow diagnostics for rejected sequence/checksum packets in `transport_codec.cpp`.
2. Add a temporary marker at the entry of `Modules::executeOnRecvbyte` for `0xE1`.
3. Restore an exact-head Canary build in the E2E workflow.
4. Run the physical test and classify the failure as transport rejection versus dispatcher/native handler execution.
5. Implement the smallest evidence-backed fix.
6. Remove diagnostic-only code, restore the full two-session scenario and verify current-head CI.
7. Extract reusable orchestration only after the prototype is proven.

# Work log

## 2026-07-13T08:09:00+02:00

- Changed: replaced account-login orchestration with direct native game-port login and strengthened failure evidence and markers.
- Learned: the prior account-login shim changed global client state and caused OTClient to look for non-existent 14.04 assets.
- Failed/blocked: run 39 failed before world login.
- Result: native 15.25 game login implemented.

## 2026-07-13T09:00:00+02:00

- Changed: disabled unrelated automatic startup packet senders, enabled OTClient packet recording, added internal logs, SQL snapshots and TCP capture.
- Learned: login is real and stable until the first explicit Bestiary request.
- Result: packet recorder identifies the failing client packet as plaintext `0xE1`.

## 2026-07-13T10:00:00+02:00

- Changed: injected a runtime-only byte-225 Lua probe that would bypass the native Bestiary handler and send an empty valid `0xD5` response.
- Learned: the server still closed immediately and no probe callback marker appeared.
- Failed/blocked: live run 67 failed at the same boundary.
- Result: transport/module-entry diagnostics claimed as the next bounded step.

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| a22c49019622248593a4e9f5f7bc7107ce9cd51b | Cyclopedia Live E2E run 39 | failed | Account-login shim changed global client version and loaded wrong assets. |
| 7b82440b96e4f5a46616f3566288fea9797abaf3 | Cyclopedia Live E2E run 65 | failed | Native login succeeds; server closes directly after client opcode `0xE1`. |
| f8a8efe704bbb342469623f8d92a90e1f01f9dc8 | Cyclopedia Live E2E run 67 | failed | Runtime byte-225 probe installed; no callback marker; same immediate server FIN/RST. |
| f8a8efe704bbb342469623f8d92a90e1f01f9dc8 | Agent Task Ownership | passed | Structured task remained conflict-free before new source claims. |
| f8a8efe704bbb342469623f8d92a90e1f01f9dc8 | CI / Required | passed | Repository checks green; live E2E remains the only failing proof. |
| current head | exact-head diagnostic live E2E | pending | Must identify the rejection layer. |

Never write `passed` without verification on the stated commit.

# Failed approaches and dead ends

- Overriding `ProtocolLogin:sendLoginPacket()` and temporarily calling `g_game.setClientVersion(1404)` is invalid. Client version is global runtime state and reloads the wrong asset set.
- Disabling Quick Loot, Imbuement Tracker, Shop, Locales, Weapon Proficiency and Quest Log startup modules did not prevent the close.
- A runtime-only byte-225 module did not receive the request in run 67; do not assume the native Bestiary serializer is reached until exact-head diagnostics prove it.
- Do not duplicate the full workflow for every future feature suite.

# Risks and compatibility

- Runtime: CI-only disposable processes; temporary source logging must not survive unreviewed into production.
- Data/migration: existing schema and fixture imports only; no migration.
- Security: fixed local test credentials in an isolated CI database only.
- Backward compatibility: no intended protocol behavior change until a failing boundary is proven.
- Cross-repo rollout: permanent client automation must later use an explicitly coordinated user-owned OTClient task.
- Rollback: remove the diagnostic commits or close the prototype PR; no persistent runtime state exists.

# Remaining work

1. Build and run the exact-head diagnostic server.
2. Inspect transport/module-entry markers and TCP/packet artifacts.
3. Apply and verify the smallest real fix.
4. Remove diagnostic-only changes and complete the two-session test.

# Handoff

## Start here

Read this task, PR #224, `docs/agents/programs/E2E_AUTOMATION_PROGRAM.md`, and the newest `cyclopedia-live-e2e` artifact.

## Do not repeat

- Do not restore the 14.04 client-version framing shim.
- Do not claim a successful E2E run from server startup or login alone.
- Do not assume `parseBestiarySendRaces()` runs without a dispatcher marker.
- Do not move generic orchestration into a feature-specific permanent contract.

## Required reads

- `AGENTS.md`
- `docs/agents/README.md`
- `docs/agents/programs/E2E_AUTOMATION_PROGRAM.md`
- `.github/workflows/cyclopedia-live-e2e.yml`
- `tools/e2e/cyclopedia_otclient_e2e.lua`
- `src/lua/modules/modules.cpp`
- `src/server/network/protocol/transport_codec.cpp`
- relevant Canary connection, protocol-profile and authentication code

## Open questions

- Whether the close is triggered by sequence/checksum validation, XTEA/padding validation, module dispatch, or the native Bestiary handler must be decided from the next exact-head artifact.
