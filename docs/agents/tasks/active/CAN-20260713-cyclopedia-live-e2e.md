---
task_id: CAN-20260713-cyclopedia-live-e2e
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-E2E-CANARY-OTCLIENT
status: implementing
agent: chatgpt-e2e-prototype
branch: test/cyclopedia-live-e2e
base_branch: main
created: 2026-07-13T08:09:00+02:00
updated: 2026-07-13T08:09:00+02:00
last_verified_commit: ac218d540d9b357f6d895d4d1fc38326f47071d4
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
  shared: []
  read_only:
    - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
    - src/config/configmanager.cpp
    - src/server/network/protocol/protocolgame.cpp
    - src/server/network/protocol/protocollogin.cpp
    - src/server/network/protocol/transport_codec.cpp
modules_touched:
  - physical-client E2E prototype
  - Cyclopedia scenario automation
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
- [ ] Real OTClient 15.25 logs into `Knight 1` through the native modern game transport.
- [ ] Bestiary, Charms and Bosstiary parser events are observed during session one.
- [ ] Safe logout and a complete second login succeed.
- [ ] The same three Cyclopedia response families are observed after relog.
- [ ] Database evidence confirms online state during the test and clean offline state afterward.
- [ ] Logs, hashes, SQL snapshots, result markers and a screenshot are uploaded.
- [ ] No map, gameplay, protocol, schema, client source or production state is modified.
- [ ] Current-head ownership and repository CI pass.
- [ ] Complete live E2E workflow passes and its artifact is reviewed.

# Confirmed context

- Merged PR #222 defines this PR as the first bounded prototype for `CAN-PROGRAM-E2E-PLATFORM`.
- Canary's default `authType` is `password`.
- The modern game login layout accepts a session-key field containing `account-or-email`, a newline, and the password when password authentication is active.
- Account fixture 101 uses email `test1@example.com`, password `test`, and owns `Knight 1`.
- Current client and asset version resolve to 15.25 in the workflow.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| PR #222 | Universal E2E ownership and scenario boundary | `docs/agents/programs/E2E_AUTOMATION_PROGRAM.md` | Prevents this prototype from becoming duplicated per-feature infrastructure. |
| Reusable Linux build | Exact-head Canary artifact | `.github/workflows/reusable-build-linux.yml` | Existing supported build path. |
| Test fixtures | Disposable account and characters | `docker/data/01-test_account.sql`, `docker/data/02-test_account_players.sql` | Deterministic existing fixture set. |
| Canary protocol profiles | Native modern game transport and password-mode session key | `src/server/network/protocol/protocolgame.cpp` | Removes the need for a custom account-login framing shim. |

# Ownership and overlap check

- Program record: `docs/agents/programs/E2E_AUTOMATION_PROGRAM.md`.
- Open PRs inspected: #224 and current E2E/coordination work.
- Active tasks inspected: coordination task from #222 is read-only for this prototype's files.
- Exclusive claims: workflow, Cyclopedia Lua scenario, exact account fixture correction and this task record.
- Shared claims: none.
- Read-only dependencies: program contract and Canary transport/authentication sources.
- Overlaps: no structured exclusive overlap identified.
- Resolution: keep common-platform extraction out of this PR.

# Current state

The environment reaches a running Canary server and a running OTClient. The previous login attempt failed before entering the world because a test shim temporarily changed the global client version from 15.25 to 14.04 to alter account-login framing, which caused missing 14.04 assets and a closed socket.

# Plan

1. Remove the entire `ProtocolLogin` framing override.
2. Log directly into the modern game port with the password-mode session-key form.
3. Keep version 15.25 and its assets active for the full process lifetime.
4. Run the real two-session scenario and inspect every artifact.
5. Repair only evidence-backed failures until the workflow passes.
6. Keep reusable platform extraction for a separate task after the prototype is proven.

# Work log

## 2026-07-13T08:09:00+02:00

- Changed: replaced account-login orchestration with direct native game-port login and strengthened failure evidence and markers.
- Learned: the prior account-login shim changed global client state and caused OTClient to look for non-existent 14.04 assets.
- Failed/blocked: run 39 failed in `Run physical OTClient under Xvfb with relog` before world login.
- Result: root-cause fix pushed; new live run pending.

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| a22c49019622248593a4e9f5f7bc7107ce9cd51b | Cyclopedia Live E2E run 39 | failed | Canary/database/map/client startup passed; account-login shim caused 14.04 asset lookup and connection loss. |
| current head | CI | pending | Required before readiness. |
| current head | Agent Task Ownership | pending | Required after adding this structured task. |
| current head | Cyclopedia Live E2E | pending | Must complete both physical-client sessions. |

Never write `passed` without verification on the stated commit.

# Failed approaches and dead ends

- Overriding `ProtocolLogin:sendLoginPacket()` and temporarily calling `g_game.setClientVersion(1404)` is invalid. Client version is global runtime state, not a framing-only switch, and it reloads the wrong asset set.
- Do not duplicate the full workflow for every future feature suite.

# Risks and compatibility

- Runtime: CI-only disposable processes; no production runtime change.
- Data/migration: existing schema and fixture imports only; no migration.
- Security: fixed local test credentials in an isolated CI database only.
- Backward compatibility: no server/client protocol implementation change.
- Cross-repo rollout: permanent client automation must later use an explicitly coordinated user-owned OTClient task.
- Rollback: delete this prototype branch/PR; no persistent runtime state exists.

# Remaining work

1. Verify the new workflow run and inspect its evidence archive.
2. Fix the next factual failure, if any.
3. Update this task and PR with exact final results.

# Handoff

## Start here

Read this task, PR #224, `docs/agents/programs/E2E_AUTOMATION_PROGRAM.md`, and the newest `cyclopedia-live-e2e` artifact.

## Do not repeat

- Do not restore the 14.04 client-version framing shim.
- Do not claim a successful E2E run from server startup alone.
- Do not move generic orchestration into a feature-specific permanent contract.

## Required reads

- `AGENTS.md`
- `docs/agents/README.md`
- `docs/agents/programs/E2E_AUTOMATION_PROGRAM.md`
- `.github/workflows/cyclopedia-live-e2e.yml`
- `tools/e2e/cyclopedia_otclient_e2e.lua`
- relevant Canary protocol-profile and authentication code

## Open questions

- Whether the next failure, if any, belongs to scenario timing, OTClient parser compatibility, or Canary response behavior must be decided from the next artifact rather than guessed.
