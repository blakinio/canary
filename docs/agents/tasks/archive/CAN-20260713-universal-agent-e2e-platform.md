---
task_id: CAN-20260713-universal-agent-e2e-platform
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-E2E-CANARY-OTCLIENT
status: completed
agent: chatgpt-e2e-platform
branch: feat/universal-agent-e2e-platform
base_branch: main
created: 2026-07-13T12:00:00+02:00
completed: 2026-07-15T14:48:35+02:00
last_verified_commit: d202edc3d56956983984e5cb310f21116bf7122c
risk: medium
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
    - tests/e2e/scenarios/login/relog.json
  shared:
    - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
  read_only:
    - docker/data/01-test_account.sql
    - docker/data/02-test_account_players.sql
    - .github/scripts/docker-quickstart-smoke.sh
modules_touched:
  - universal physical-client E2E platform
  - agent scenario runner
  - login/relog baseline suite
---

# Result

Completed and merged as PR #245, `feat(e2e): bootstrap universal agent test platform`.

The task delivered one reusable physical-client E2E platform with:

- validated JSON scenario discovery and resolution;
- one reusable runtime orchestrator;
- controlled, pinned OTClient automation;
- disposable MariaDB and exact-head Canary execution;
- feature-neutral `login/relog` baseline;
- packet records, SQL state, hashes, screenshots and machine-readable result artifacts;
- one-process client relog validation without retry or delay workarounds.

# Evidence-backed repairs

The platform work exposed and helped prove three independent lifecycle/transport issues:

1. modern first-game-frame sizing left four bytes queued and desynchronized later sequenced packets; fixed by PR #375;
2. exact leave-game transport/session ownership required the PR #360 lifecycle hardening;
3. the E2E driver attempted phase-two `loginWorld()` reentrantly from `onGameEnd`; driver v9 now hands control back to the event loop with `addEvent(startLogin)` before relogging.

No OTClient source modification, artificial relog delay, retry window, two-process workaround or validation relaxation was introduced.

# Final validation

Final PR head: `d202edc3d56956983984e5cb310f21116bf7122c`.

- Universal Agent E2E #38 (`29414341369`): success.
- Physical client / `login/relog`: success.
- CI #2432 (`29414341323`): success.
- Agent Task Ownership #1305 (`29414341309`): success.
- autofix.ci #1414 (`29414341047`): success.
- reviews: none.
- unresolved review threads: none.

The final physical scenario proved two stable world entries, two explicit safe logouts, two server-observed logins, two packet records, persisted `lastlogin` and `lastlogout`, final online count zero, clean client exit and no fatal runtime-log hits.

# Merge

PR #245 merged on 2026-07-15 at `9fc11e04dc5040d1ea18d02e15dac1df47f3fe64`.

# Handoff

Future work must reuse the merged universal E2E platform rather than create a second E2E orchestrator. New generic platform capabilities require a new bounded task under `CAN-PROGRAM-E2E-PLATFORM` with fresh ownership claims. Feature-specific suites should own only their scenarios and assertions.
