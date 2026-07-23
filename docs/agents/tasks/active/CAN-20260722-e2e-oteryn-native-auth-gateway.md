---
task_id: CAN-20260722-e2e-oteryn-native-auth-gateway
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-20260721-oteryn-identity-auth
status: ready
agent: "GPT-5.6 Thinking"
branch: feat/CAN-20260722-e2e-oteryn-native-auth-gateway
base_branch: main
created: 2026-07-22T23:30:00+02:00
updated: 2026-07-23T10:16:00+02:00
last_verified_commit: 1fda058b7cfc2c4d3a7f828a72a80f4c56d05041
risk: high
related_issue: ""
related_pr: "740"
depends_on:
  - "Canary Game Session adapter PR #722 exact implementation head 285dec6a034aa3620ae5ca12549fb9e8e1b35631"
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

- [x] Reuse the canonical Universal Agent E2E workflow; do not create a second orchestrator.
- [x] Build and run OTClient at exact merged PR #17 commit `bb87346f6c516a19d19497d82bb01fb389334ff5`.
- [x] Build and run Oteryn Platform Game Gateway at exact merged PR #122 commit `8006534108d835474dadd208b0ec934e4a12528b`.
- [x] Build and run Canary from exact adapter PR #722 implementation commit `285dec6a034aa3620ae5ca12549fb9e8e1b35631` through the existing controlled-server mechanism.
- [x] Enable the Canary issuer only inside the disposable test runtime with ephemeral service credentials and explicit Platform world id `1`.
- [x] Keep raw Game Login Ticket, Gateway service credentials and Game Session credentials out of committed files and retained logs/artifacts.
- [x] Prove one real maintained-OTClient world entry for account id `101`, character `Knight 1`, world id `1` through Gateway -> Canary issuer.
- [x] Prove replay of the same Game Session credential fails closed and does not produce a second successful world entry.
- [x] Retain exact server/client/Gateway commit and binary hash evidence plus machine-readable first-failure evidence.
- [x] Keep claims bounded: this scenario does not prove production TLS/private-network routing, credential rotation, missing Platform hardening, full browser OAuth, or immediate security-generation revocation.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T10:16:00+02:00
head: 1fda058b7cfc2c4d3a7f828a72a80f4c56d05041
branch: feat/CAN-20260722-e2e-oteryn-native-auth-gateway
pr: 740
status: ready
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
  - Universal Agent E2E run 29988893301 passed on head 1fda058b7cfc2c4d3a7f828a72a80f4c56d05041, including Required physical E2E.
  - Physical job 89151309201 used Canary adapter implementation 285dec6a034aa3620ae5ca12549fb9e8e1b35631, OTClient bb87346f6c516a19d19497d82bb01fb389334ff5 and Gateway 8006534108d835474dadd208b0ec934e4a12528b.
  - Evidence recorded gateway_session=received, login_1=success, online_stable_1=confirmed, replay_attempt=started, replay_rejected=login_error, successful_world_entries=1 and e2e=success.
  - Machine-readable result reported status=success, server_login_count=1, session_record_count=0 and all persistence/cleanup SQL assertions passed.
  - Retained scenario.env contains only non-secret scenario keys; native-auth runtime evidence contains routing/process metadata without raw ticket, service credential or Game Session credential.
  - The historical first failure was isolated to safe-logout event ordering in the E2E driver and resolved by commit aad1d0af96b4a1d80305c931dcb6d025ac7ed3ed.
  - PR #748 changed files do not overlap PR #740 changed paths.
derived:
  - The bounded native-auth cross-repository acceptance gate for Canary adapter PR #722 is satisfied.
  - Adapter PR #722 head f7afb7d06b35fce1008861852caaffbf2ae93811 is task-record-only ahead of tested implementation head 285dec6a034aa3620ae5ca12549fb9e8e1b35631, so tested adapter source is unchanged.
unknown:
  - Production Gateway-to-Canary private-network/TLS and service-credential rotation remain unproven.
conflicts: []
first_failure:
  marker: safe-logout-session-end-before-replay
  evidence: Run 29963476030 failed before replay because onSessionEnd preceded onGameEnd; commit aad1d0af96b4a1d80305c931dcb6d025ac7ed3ed fixed the driver and run 29988893301 then passed replay rejection with exactly one world entry.
rejected_hypotheses:
  - Canary adapter or Gateway failed before world entry: both failing and passing runs proved successful first world entry.
  - Replay could enter a second time: passing evidence recorded replay_rejected=login_error and successful_world_entries=1.
  - Create a second dedicated E2E orchestrator: PR #740 extends the canonical Universal Agent E2E workflow.
validation:
  - command: Universal Agent E2E run 29988893301 on 1fda058b7cfc2c4d3a7f828a72a80f4c56d05041
    result: PASS
    evidence: Physical client job 89151309201 and Required physical E2E job 89152397497 completed successfully.
  - command: CI run 29988893330 on 1fda058b7cfc2c4d3a7f828a72a80f4c56d05041
    result: PASS
    evidence: exact-head CI completed successfully.
  - command: Agent Task Ownership run 29988893207 on 1fda058b7cfc2c4d3a7f828a72a80f4c56d05041
    result: PASS
    evidence: active task ownership and checkpoint validation completed successfully.
  - command: retained native-auth E2E artifact 8556895059
    result: PASS
    evidence: result.json status=success with replay_rejected=login_error, successful_world_entries=1, server_login_count=1 and all SQL assertions passing.
blockers: []
next_action: Merge PR #740 after the labeled final-head gate is green, then checkpoint its E2E evidence into Canary adapter task CAN-20260722-oteryn-game-session-adapter.
```
