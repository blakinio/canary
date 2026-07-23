---
task_id: CAN-20260722-e2e-oteryn-native-auth-gateway
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-20260721-oteryn-identity-auth
status: validating
agent: "GPT-5.6 Thinking"
branch: feat/CAN-20260722-e2e-oteryn-native-auth-gateway
base_branch: main
created: 2026-07-22T23:30:00+02:00
updated: 2026-07-23T09:34:44+02:00
last_verified_commit: aad1d0af96b4a1d80305c931dcb6d025ac7ed3ed
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
- [ ] Prove replay of the same Game Session credential fails closed and does not produce a second successful world entry.
- [x] Retain exact server/client/Gateway commit and binary hash evidence plus machine-readable first-failure evidence.
- [x] Keep claims bounded: this scenario does not prove production TLS/private-network routing, credential rotation, missing Platform hardening, full browser OAuth, or immediate security-generation revocation.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T09:34:44+02:00
head: aad1d0af96b4a1d80305c931dcb6d025ac7ed3ed
branch: feat/CAN-20260722-e2e-oteryn-native-auth-gateway
pr: 740
status: validating
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
  - Universal Agent E2E run 29963476030 built the exact maintained OTClient, exact Canary adapter implementation commit and exact Oteryn Platform Gateway successfully before physical execution.
  - Physical job 89075275034 proved Gateway session issuance, one successful Knight 1 world entry, stable online state and controlled safe logout; server_login_count was exactly 1 and SQL persistence/cleanup assertions passed.
  - The first physical failure was in the OTClient E2E driver's safe-logout event ordering: onSessionEnd fired before onGameEnd and aborted before replay_attempt, while Canary had already accepted and completed the intended safe logout.
  - Commit aad1d0af96b4a1d80305c931dcb6d025ac7ed3ed makes first-session logout completion idempotent across onSessionEnd/onGameEnd and bounds replay start retries until the client is offline.
  - PR #748 appeared after this task started but its changed files are confined to its own task/scenario/test/fault-recovery driver and do not overlap PR #740 changed paths.
derived:
  - The remaining acceptance gap is replay rejection proof; the first native-auth Gateway to Canary world entry itself is no longer unknown.
  - Adapter PR #722 head f7afb7d06b35fce1008861852caaffbf2ae93811 is one task-record-only commit ahead of tested implementation head 285dec6a034aa3620ae5ca12549fb9e8e1b35631, so the tested adapter source is unchanged.
unknown:
  - Whether the corrected driver will complete the replay-rejection assertion on the next exact-head Universal Agent E2E run.
  - Production Gateway-to-Canary private-network/TLS and service-credential rotation remain unproven.
conflicts:
  - none
first_failure:
  marker: safe-logout-session-end-before-replay
  evidence: Universal Agent E2E run 29963476030, physical job 89075275034, artifact universal-agent-e2e-login-oteryn-native-auth; first session entered and logged out successfully, but onSessionEnd caused driver failure before replay_attempt.
rejected_hypotheses:
  - Canary adapter or Gateway failed before world entry: run 29963476030 recorded gateway_session=received, login_1=success and online_stable_1=confirmed with one Canary server login.
  - Create a second dedicated E2E orchestrator: forbidden by the Universal E2E programme; PR #740 extends the canonical orchestrator instead.
validation:
  - command: Universal Agent E2E run 29963476030 on 5b7890c4c5cf419e9f72cd7da403940aab7525c6
    result: FAIL
    evidence: Physical job 89075275034 failed only after successful first world entry/safe logout and before replay_attempt; all build/bootstrap jobs passed.
  - command: driver root-cause fix aad1d0af96b4a1d80305c931dcb6d025ac7ed3ed
    result: NOT_RUN
    evidence: exact-head rerun is pending after the safe-logout event-order fix.
  - command: active ownership overlap check against PR #748
    result: PASS
    evidence: PR #748 changed-file list has no overlap with PR #740 changed paths.
blockers:
  - Replay of the same Game Session credential has not yet been proven fail-closed by a green physical E2E run.
next_action: Run and inspect Universal Agent E2E on the corrected PR #740 head, fixing only the first remaining native-auth evidence boundary until replay rejection is green.
```
