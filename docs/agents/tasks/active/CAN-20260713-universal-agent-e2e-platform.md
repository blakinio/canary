---
task_id: CAN-20260713-universal-agent-e2e-platform
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-E2E-CANARY-OTCLIENT
status: implementing
agent: chatgpt-e2e-platform
branch: feat/universal-agent-e2e-platform
base_branch: main
created: 2026-07-13T12:00:00+02:00
updated: 2026-07-14T10:15:00+02:00
last_verified_commit: 7bbf64eed0c1ef52edd51484abfc834f70ca3ead
risk: medium
related_issue: ""
related_pr: "245"
depends_on:
  - CAN-20260713-agent-program-ownership
blocks: []
owned_paths:
  exclusive:
    - .github/workflows/universal-agent-e2e.yml
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/run_physical_e2e.sh
    - tools/e2e/client/agent_e2e.lua
    - tests/e2e/README.md
    - tests/e2e/scenarios/login/scenario.json
    - docs/agents/tasks/active/CAN-20260713-universal-agent-e2e-platform.md
  shared:
    - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
  read_only:
    - .github/workflows/cyclopedia-live-e2e.yml
    - tools/e2e/cyclopedia_otclient_e2e.lua
    - docs/agents/tasks/active/CAN-20260713-cyclopedia-live-e2e.md
    - docker/data/01-test_account.sql
    - docker/data/02-test_account_players.sql
    - .github/scripts/docker-quickstart-smoke.sh
modules_touched:
  - universal physical-client E2E platform
  - agent scenario runner
  - login/relog baseline suite
reuses:
  - merged PR 222 ownership and program contract
  - Canary reusable Linux build
  - Docker test account and player fixtures
  - global datapack/map download contract
  - paused PR 224 as evidence only
public_interfaces:
  - run_agent_e2e.py CLI
  - run_physical_e2e.sh runtime contract
  - scenario JSON contract
  - workflow_dispatch suite/scenario interface
cross_repo_tasks:
  - OTC-E2E-CLIENT-AUTOMATION
---

# Goal

Create a standalone, reusable physical-client E2E platform from current `main` that autonomous agents can invoke for any feature suite. Prove the platform first with a generic login/logout/relog scenario that does not belong to Cyclopedia.

# Acceptance criteria

- [x] The work is isolated from paused Cyclopedia PR #224.
- [x] One generic CLI discovers and validates scenarios.
- [ ] One reusable/manual GitHub Actions workflow runs a selected suite and scenario.
- [ ] The baseline scenario starts a disposable database, exact-head Canary and a real OTClient.
- [ ] The client logs into a deterministic test character, logs out, logs in again and exits cleanly.
- [ ] SQL evidence proves online state during the run and offline state afterward.
- [ ] Logs, hashes, screenshot and machine-readable result are uploaded.
- [x] Feature agents can add scenarios without copying the whole environment workflow.
- [x] No production credentials, committed map/client assets or Cyclopedia-specific assertions.
- [ ] Current-head ownership, CI and physical E2E checks pass before merge.

# Confirmed context

- PR #222 is merged and defines `CAN-PROGRAM-E2E-PLATFORM`.
- PR #224 is closed as superseded historical evidence and must not be continued.
- Evidence from #224 proves that a disposable database, Canary, the global map, Xvfb, OTClient 15.25 and direct password-mode game login can start in GitHub Actions.
- Evidence from #224 after the first feature request is not accepted as a generic platform result.
- The first platform proof is therefore the feature-neutral `login/relog` baseline.
- `blakinio/otclient` publishes the controlled `linux-linux-release` artifact from its `ci.yml` workflow.

# Ownership and overlap check

- Program record: `docs/agents/programs/E2E_AUTOMATION_PROGRAM.md`.
- Historical E2E PR #224 was inspected and closed as superseded; it owns no active platform path.
- `ACTIVE_WORK.md` is not edited.
- No structured exclusive claim was found for the universal workflow, CLI, runtime script, client driver or login scenario paths.

# Plan

1. Keep scenario discovery and validation in `run_agent_e2e.py`.
2. Keep platform runtime orchestration in one reusable `run_physical_e2e.sh` script.
3. Keep GitHub Actions as a thin artifact/bootstrap adapter around the runtime script.
4. Run the generic login/relog suite and repair only evidence-backed platform failures.
5. Update the program record and merge when all gates pass.
6. Add feature suites later through separate feature-owned tasks.

# Work log

## 2026-07-13T12:00:00+02:00

- Changed: created a dedicated platform branch and claimed only universal E2E paths.
- Learned: previous work incorrectly continued a Cyclopedia-owned experiment instead of opening the platform task required by PR #222.
- Result: scopes separated; implementation started from current `main`.

## 2026-07-13T13:00:00+02:00

- Changed: added scenario validation CLI, generic OTClient login/relog driver, login scenario manifest, documentation and the first workflow draft.
- Learned: the first workflow revision failed before jobs started; reusable-build token permissions are the leading configuration cause.
- Result: runtime orchestration is being extracted into a reusable shell entrypoint and the workflow will be recreated with correct caller permissions.

## 2026-07-13T20:10:00+02:00

- Changed: added a fail-fast database preflight with per-phase stdout/stderr artifacts and corrected MariaDB client authentication through `MYSQL_PWD` in both preflight and physical jobs.
- Learned: run #13 failed before schema import with concrete artifact error `ERROR 1045 (28000): Access denied for user 'root'@'172.18.0.1' (using password: NO)`; the MariaDB CLI did not consume the previously exported `MARIADB_PWD` variable.
- Result: smallest platform-only fix committed; current-head validation is pending and no physical success is claimed.

## 2026-07-13T21:10:00+02:00

- Changed: made the generic driver accept an `onGameEnd` callback as logout completion only after the driver has emitted `logout_request_N=safe`; an online transition callback is recorded and ignored, while a real pre-logout disconnect fails explicitly.
- Learned: run #15 proved both protocol logins and both `onGameStart` callbacks, but the driver immediately treated `onGameEnd` callbacks as completed logouts without ever requesting safe logout. The artifact had no `logout_request_*` markers, both sessions completed in two seconds, SQL never observed `players_online`, and `lastlogin` remained unset.
- Result: the false-positive session state machine is corrected with the smallest driver-only change; current-head physical validation is pending.

## 2026-07-13T23:05:00+02:00

- Changed: restored the intended online-transition guard in `onGameEnd`; callbacks received while `g_game.isOnline()` are now recorded as `game_end_transition_N=ignored-online`, while a disconnected pre-logout callback still fails.
- Learned: run #20 on head `1dca835fcab13785c926848dd76116d946bb5417` proved a real world login, SQL captured the character online, and the screenshot still showed the live game UI, yet the driver failed one second after `onGameStart` on an `onGameEnd` callback before the scheduled safe logout. This is concrete evidence that the callback can be transitional while the client remains online.
- Result: smallest driver-only fix committed at `19cbe628c21beaca9ca1f9aedfb5ec9f6ca12862`; current-head physical validation is pending and no success is claimed.

## 2026-07-14T10:15:00+02:00

- Changed: removed `g_game.cancelLogin()` from the completed-safe-logout `onGameEnd` handler and advanced the generic driver contract to v8.
- Learned: run #27 proved first-session stable login, safe logout and persisted `lastlogin`/`lastlogout`; phase two then reached protocol login, pending game, enter game and `onGameStart`, but failed 105 ms later without a matching Canary kick/logout. The only driver action capable of scheduling an unscoped second game-end transition was `cancelLogin()` called from the first completed `onGameEnd`.
- Result: the driver no longer mutates transport state from a completion callback. The database persistence gate remains the authoritative boundary before relog. Current-head physical validation is required; no success is claimed yet.

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| 9e46cd789e9f3b7acb51f7df0279e936c50a05ca | CI / Required | passed | Repository checks green. |
| 9e46cd789e9f3b7acb51f7df0279e936c50a05ca | Agent Task Ownership | passed | New paths conflict-free. |
| 9e46cd789e9f3b7acb51f7df0279e936c50a05ca | Universal Agent E2E | startup_failure | No jobs created; workflow caller configuration was rebuilt. |
| 32b4e9f78c0e481453e9e9615337c1886c0e2039 | Universal Agent E2E #13 / database preflight | failed | Schema phase artifact: root TCP authentication attempted with no password. |
| ed43e30b144520ff543731be80ced315bce42dd9 | Universal Agent E2E #15 / physical client | failed | Real protocol/game-start markers occurred twice, but no safe logout was requested; immediate `onGameEnd` callbacks produced false logout success and SQL assertions remained false. |
| 1dca835fcab13785c926848dd76116d946bb5417 | Universal Agent E2E #20 / physical client | failed | Real login and SQL online capture succeeded; the screenshot remained in-world, but an online transitional `onGameEnd` callback was misclassified as a disconnect before safe logout. |
| 7bbf64eed0c1ef52edd51484abfc834f70ca3ead | Universal Agent E2E #27 / login-relog | failed | Phase one completed and persisted; phase two reached `onGameStart`, then an unscoped stale `onGameEnd` was misclassified 105 ms later. Canary emitted no matching second-session kick/logout. |
| 50f67f45c5eaccb7ce13db103cf27a186f8e9a47 | Universal Agent E2E / login-relog | pending | Driver v8 removes the post-logout `cancelLogin()` mutation; current-head proof is required. |

# Failed approaches and dead ends

- Do not continue platform development in PR #224.
- Do not make Cyclopedia the owner of database, server, client, login or cleanup orchestration.
- Do not copy one complete workflow per feature.
- Do not treat a workflow startup failure as a scenario failure.
- Do not use `MARIADB_PWD` as proof of MariaDB CLI authentication; run #13 showed it was ignored.
- Do not accept `onGameEnd` as logout proof unless the driver first requested safe logout.
- Do not classify `onGameEnd` as a disconnect while `g_game.isOnline()` remains true; run #20 proved that callback can be transitional.
- Do not call `g_game.cancelLogin()` from the completed logout callback; run #27 showed the unscoped follow-up transition can be attributed to the next phase.

# Remaining work

1. Wait for current-head database preflight, builds and physical login/relog evidence.
2. Repair only concrete current-head platform failures.
3. Rebase or merge current `main`, then rerun the exact-head scenario.
4. Review the complete diff and all repository gates.
5. Update task/program records and merge only after current-head physical success.

# Handoff

## Start here

Read this task, `docs/agents/programs/E2E_AUTOMATION_PROGRAM.md`, merged PR #222 and closed PR #224 only as historical evidence.

## Do not repeat

Do not edit or reopen PR #224 as the universal platform.

## Required reads

- `AGENTS.md`
- `docs/agents/README.md`
- `docs/agents/programs/E2E_AUTOMATION_PROGRAM.md`
- `docs/agents/templates/E2E_SCENARIO.md`
- `.github/scripts/docker-quickstart-smoke.sh`
- Docker test fixtures

## Open questions

- Whether direct use of the current `blakinio/otclient` main artifact is stable enough for the permanent contract will be decided from the first successful workflow evidence.
