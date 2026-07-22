---
task_id: CAN-20260722-e2e-oteryn-native-auth-gateway
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-20260721-oteryn-identity-auth
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/CAN-20260722-e2e-oteryn-native-auth-gateway
base_branch: main
created: 2026-07-22T23:30:00+02:00
updated: 2026-07-22T23:42:00+02:00
last_verified_commit: 10e569d22c5bbb73ee3f2e327d7c6968cf1dc811
risk: high
related_issue: ""
related_pr: "740"
depends_on:
  - "Canary Game Session adapter PR #722 exact head 285dec6a034aa3620ae5ca12549fb9e8e1b35631"
  - "OTClient PR #17 merged as bb87346f6c516a19d19497d82bb01fb389334ff5"
  - "Oteryn Platform Game Gateway PR #122 merged as 8006534108d835474dadd208b0ec934e4a12528b"
blocks:
  - "CAN-20260722-oteryn-game-session-adapter cross-repository native-auth E2E acceptance gate"
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260722-e2e-oteryn-native-auth-gateway.md
    - tests/e2e/scenarios/login/oteryn-native-auth.json
    - tests/e2e/test_oteryn_native_auth_platform_stub.py
    - tools/e2e/oteryn_native_auth_platform_stub.py
    - tools/e2e/client/oteryn_native_auth_e2e.lua
  shared:
    - .github/workflows/universal-agent-e2e.yml
    - .github/e2e-controlled-server.env
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/run_physical_e2e.sh
    - tools/e2e/server_selection.py
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - src/security/game_session_http_issuer.hpp
    - src/security/game_session_http_issuer.cpp
    - src/server/server.cpp
modules_touched:
  - Universal OTS E2E automation
  - Oteryn native-auth cross-repository integration
reuses:
  - Universal Agent E2E workflow
  - controlled-server exact-ref build support
  - maintained OTClient physical runner
  - Canary Game Session HTTP issuer
public_interfaces:
  - tests/e2e scenario auth.mode=oteryn_gateway
  - tests/e2e scenario assertions.runtime_counts
cross_repo_tasks:
  - OTS-20260721-oteryn-identity-auth
---

# Goal

Extend the single existing Universal Agent E2E orchestrator with one bounded native-auth scenario that proves a maintained OTClient can send a fresh Game Login Ticket to the exact Oteryn Platform Gateway, receive one Canary Game Session, enter the intended character once, and fail closed when the same Game Session credential is replayed.

The test uses the real Gateway and real Canary issuer. A local disposable contract stub supplies only the Gateway's upstream Platform ticket-redeem and login-context dependencies; it is not production Identity evidence and does not remove the separate Platform hardening or private-network/TLS production blockers.

# Acceptance criteria

- [ ] Reuse the canonical Universal Agent E2E workflow; do not create a second orchestrator.
- [ ] Build and run OTClient at exact merged PR #17 commit `bb87346f6c516a19d19497d82bb01fb389334ff5`.
- [ ] Build and run Oteryn Platform Game Gateway at exact merged PR #122 commit `8006534108d835474dadd208b0ec934e4a12528b`.
- [ ] Build and run Canary from exact adapter PR #722 commit `285dec6a034aa3620ae5ca12549fb9e8e1b35631` through the existing controlled-server mechanism.
- [ ] Enable the Canary issuer only inside the disposable test runtime with ephemeral service credentials and explicit Platform world id `1`.
- [ ] Keep raw Game Login Ticket, Gateway service credentials and Game Session credentials out of committed files and retained logs/artifacts.
- [ ] Prove one real maintained-OTClient world entry for account id `101`, character `Knight 1`, world id `1` through Gateway -> Canary issuer.
- [ ] Prove replay of the same Game Session credential fails closed and does not produce a second successful world entry.
- [ ] Retain exact server/client/Gateway commit and binary hash evidence plus machine-readable first-failure evidence.
- [ ] Keep claims bounded: this scenario does not prove production TLS/private-network routing, credential rotation, missing Platform hardening, full browser OAuth, or immediate security-generation revocation.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T23:42:00+02:00
head: 10e569d22c5bbb73ee3f2e327d7c6968cf1dc811
branch: feat/CAN-20260722-e2e-oteryn-native-auth-gateway
pr: 740
status: implementing
context_routes:
  - universal-e2e
  - agent-governance
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260722-e2e-oteryn-native-auth-gateway.md
  - tests/e2e/scenarios/login/oteryn-native-auth.json
  - tests/e2e/test_oteryn_native_auth_platform_stub.py
  - tools/e2e/oteryn_native_auth_platform_stub.py
  - tools/e2e/client/oteryn_native_auth_e2e.lua
  - .github/workflows/universal-agent-e2e.yml
  - .github/e2e-controlled-server.env
  - tools/e2e/run_agent_e2e.py
  - tools/e2e/run_physical_e2e.sh
  - tools/e2e/server_selection.py
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
changed_paths:
  - .github/e2e-controlled-server.env
  - docs/agents/tasks/active/CAN-20260722-e2e-oteryn-native-auth-gateway.md
  - tests/e2e/scenarios/login/oteryn-native-auth.json
  - tests/e2e/test_oteryn_native_auth_platform_stub.py
  - tools/e2e/client/oteryn_native_auth_e2e.lua
  - tools/e2e/oteryn_native_auth_platform_stub.py
  - tools/e2e/run_physical_e2e.sh
  - tools/e2e/server_selection.py
proven:
  - The canonical Universal Agent E2E already builds a controlled maintained OTClient and supports an exact controlled server repository/ref without creating a second orchestrator.
  - Canary adapter PR #722 exact head 285dec6a034aa3620ae5ca12549fb9e8e1b35631 has green CI, Security Validation, Agent Task Ownership and autofix workflows.
  - OTClient PR #17 is merged as bb87346f6c516a19d19497d82bb01fb389334ff5 and Oteryn Platform Gateway PR #122 is merged as 8006534108d835474dadd208b0ec934e4a12528b.
  - PR #740 is the isolated Universal E2E platform task for the missing physical cross-repository proof.
derived:
  - A bounded local Platform dependency stub plus the real Gateway isolates the currently missing Gateway-to-Canary physical integration proof without claiming full production Identity or transport readiness.
unknown:
  - Whether the exact physical scenario will pass before runtime execution.
  - Production Gateway-to-Canary private-network/TLS and service-credential rotation remain unproven.
conflicts:
  - none
first_failure:
  marker: native-auth-e2e-running
  evidence: Universal Agent E2E is being rerun on PR #740 after implementing the native-auth scenario and generic scenario-declared runtime counts.
rejected_hypotheses:
  - Create a second dedicated E2E orchestrator: forbidden by the active Universal E2E programme; extend the canonical orchestrator instead.
validation:
  - command: live repository/PR ownership preflight
    result: PASS
    evidence: No current open Canary PR owns the canonical Universal E2E workflow/tools paths; PR #514 is confined to security-validation paths.
blockers:
  - Physical cross-repository native-auth scenario has not completed successfully yet.
next_action: Inspect the exact-head PR #740 Universal Agent E2E result and fix only the first failing native-auth evidence boundary until the scenario is green.
```
