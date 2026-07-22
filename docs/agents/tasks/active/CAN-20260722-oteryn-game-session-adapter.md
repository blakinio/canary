---
task_id: CAN-20260722-oteryn-game-session-adapter
program_id: none
coordination_id: OTS-20260721-oteryn-identity-auth
status: blocked
agent: "GPT-5.6 Thinking"
branch: feat/CAN-20260722-oteryn-game-session-adapter
base_branch: main
created: 2026-07-22T16:00:00+02:00
updated: 2026-07-22T22:42:00+02:00
last_verified_commit: 90687ecb13ec2e96a9f2a1ed3ae4ab514d84cd61
risk: high
related_issue: ""
related_pr: "722"
depends_on:
  - "Oteryn Platform architecture/OAuth/ticket/Gateway phases"
  - "OTClient PR #17 merged as bb87346f6c516a19d19497d82bb01fb389334ff5"
  - "Oteryn Platform Gateway PR #122 merged as 8006534108d835474dadd208b0ec934e4a12528b"
  - "Oteryn Platform docs/contracts/GAME_SESSION_CANARY_CONTRACT.md"
blocks:
  - "production Oteryn native-auth cross-repository E2E"
  - "legacy password-auth cutover"
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260722-oteryn-game-session-adapter.md
    - src/security/game_session_http_issuer.hpp
    - src/security/game_session_http_issuer.cpp
    - src/security/CMakeLists.txt
    - src/server/server.cpp
    - src/main.cpp
    - vcproj/settings.props
    - tests/unit/security/game_session_http_issuer_test.cpp
    - tests/unit/security/CMakeLists.txt
  shared:
    - docs/agents/CROSS_REPO_CONTRACTS.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - src/security/login_session_manager.hpp
    - src/security/login_session_manager.cpp
    - src/account/account.hpp
    - src/account/account.cpp
    - src/server/network/protocol/protocollogin.cpp
    - src/server/network/protocol/protocolgame.cpp
    - src/game/multichannel/channel_context.hpp
modules_touched:
  - Canary login session authentication
  - Oteryn Game Session HTTP issuer
reuses:
  - LoginSessionManager
  - Account::load and Account::getAccountPlayers
  - ServiceManager process lifecycle
  - existing GameSessionKey world-entry field consumed by ProtocolGame
public_interfaces:
  - POST /internal/v1/game-sessions
  - GET /health
cross_repo_tasks:
  - OTS-20260721-oteryn-identity-auth
---

# Goal

Implement the Canary-side Game Session compatibility adapter for the Oteryn native-auth flow without transmitting or validating the user's Oteryn password in the supported path.

# Acceptance criteria

- [x] Revalidate OTClient Phase 5 merge, Platform Gateway contract and Canary LoginSessionManager semantics.
- [x] Select Candidate B and document replay, expiry, revocation, restart and process/world semantics.
- [x] Preserve final Canary character ownership/deletion/ban/runtime admission checks by leaving the existing ProtocolGame -> IOLoginData path authoritative.
- [x] Keep legacy authentication unchanged while the adapter is disabled/not configured.
- [x] Bind external issuance to exact account, explicitly configured Platform world route and ProtocolProfileId::Current without password fallback.
- [x] Use SHA-256 bearer service authentication and avoid logging raw Game Session/service credentials.
- [x] Reject duplicate login_attempt_id issuance within the token TTL without storing raw Game Session credentials.
- [x] Add focused unit coverage for issue/consume, expiry, replay, duplicate attempt, failed-attempt reservation release, wrong account/character/profile, restart and routing semantics.
- [x] Register new C++ source in CMake and maintained Visual Studio build entry points.
- [x] Prove Linux debug unit tests, Linux release/runtime smoke, macOS, Windows and Docker on the exact final validated implementation/documentation head.
- [x] Update cross-repository contract, module catalogue and changelog with rollout/failure semantics.
- [x] Prove the final documentation/checkpoint head through the repository exact-final-head gate.
- [ ] Prove full OTClient -> Oteryn Gateway -> Canary native-auth E2E before any production-readiness claim.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T22:42:00+02:00
head: 90687ecb13ec2e96a9f2a1ed3ae4ab514d84cd61
branch: feat/CAN-20260722-oteryn-game-session-adapter
pr: 722
status: blocked
context_routes:
  - agent-governance
  - cpp-runtime
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260722-oteryn-game-session-adapter.md
  - src/security/game_session_http_issuer.hpp
  - src/security/game_session_http_issuer.cpp
  - src/security/CMakeLists.txt
  - src/server/server.cpp
  - src/main.cpp
  - vcproj/settings.props
  - tests/unit/security/game_session_http_issuer_test.cpp
  - tests/unit/security/CMakeLists.txt
  - docs/agents/CROSS_REPO_CONTRACTS.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
changed_paths:
  - docs/agents/CHANGELOG.md
  - docs/agents/CROSS_REPO_CONTRACTS.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260722-oteryn-game-session-adapter.md
  - src/main.cpp
  - src/security/CMakeLists.txt
  - src/security/game_session_http_issuer.cpp
  - src/security/game_session_http_issuer.hpp
  - src/server/server.cpp
  - tests/unit/security/CMakeLists.txt
  - tests/unit/security/game_session_http_issuer_test.cpp
  - vcproj/settings.props
proven:
  - Candidate B is implemented as a disabled-by-default per-process HTTP issuer reusing LoginSessionManager.
  - Account and allowed-character data are loaded authoritatively by numeric Canary account id without Oteryn password authentication.
  - ServiceManager requires explicit CANARY_GAME_SESSION_ISSUER_WORLD_ID and does not equate Platform game_worlds.id with Canary ChannelContext channel_id.
  - LoginSessionManager provides SHA-256-only process-local storage, 60-second TTL and atomic single-use consume bound to account, character names and protocol profile.
  - Duplicate login_attempt_id issuance is fail-closed for the token TTL; failed issuance releases the reservation without retaining raw Game Session credentials.
  - Existing ProtocolGame and IOLoginData world-entry ownership/deletion/ban/runtime checks remain unchanged and authoritative after token issuance.
  - Cross-repository contract, module catalogue and changelog document the issuer, rollout order, retry/failure semantics and production blockers.
  - Exact final head 90687ecb13ec2e96a9f2a1ed3ae4ab514d84cd61 passed CI run 29956181134, Security Validation run 29956181252, Agent Task Ownership run 29956181022 and autofix run 29956180932.
derived:
  - Candidate B preserves stronger single-use world-entry semantics than replayable account_sessions.
  - A lost successful create-session response intentionally cannot be recovered by repeating the same login_attempt_id; the orphan token expires and the client must start a fresh native-login attempt.
  - Gateway protocol v1 safely supports only ProtocolProfileId::Current without expanding the cross-repository request contract.
unknown:
  - Full native OTClient -> Oteryn Gateway -> Canary E2E behavior has not yet been proven by an orchestrator covering all three repositories.
  - Exact production private-network/TLS boundary and service-credential rotation mechanism for Gateway -> Canary remain unproven.
  - Whether future production requirements mandate multi-world routing or same-world horizontal replicas in the first expansion remains unresolved.
conflicts:
  - Prior handoff claimed Oteryn Platform PR 123 was merged; live PR state and current Platform main prove it was closed unmerged and its advertised hardening remains absent.
first_failure:
  marker: cross-repo-native-auth-e2e-unproven
  evidence: Canary exact-final-head compile/unit/security/ownership validation is green, but the existing Universal Agent E2E workflow does not orchestrate the Oteryn Platform Gateway, so no full OTClient -> Gateway -> Canary native-auth proof exists yet.
rejected_hypotheses:
  - Reuse ProtocolLogin issuer unchanged: it requires account password authentication.
  - Use DB account_sessions as single-use: current contract records replay until expiry/deletion.
  - Serve the issuer through existing Tibia ServicePort multiplexing: it lacks the required HTTP/service-auth boundary.
  - Issue all tokens in the login-gateway process: LoginSessionManager storage is process-local.
  - Treat Platform game_worlds.id as Canary ChannelContext channel_id: ServiceManager uses a separately configured Platform world id and only logs local channel identity.
validation:
  - command: exact-head CI run 29956181134 on 90687ecb13ec2e96a9f2a1ed3ae4ab514d84cd61
    result: PASS
    evidence: full final-gate matrix completed successfully, including Linux debug tests, Linux release/runtime smoke, Windows, macOS and Docker.
  - command: Security Validation run 29956181252 on 90687ecb13ec2e96a9f2a1ed3ae4ab514d84cd61
    result: PASS
    evidence: security scenario validation and exact-head Linux release build completed successfully.
  - command: Agent Task Ownership run 29956181022 on 90687ecb13ec2e96a9f2a1ed3ae4ab514d84cd61
    result: PASS
    evidence: changed checkpoint validation and full active ownership index validation completed successfully.
  - command: autofix run 29956180932 on 90687ecb13ec2e96a9f2a1ed3ae4ab514d84cd61
    result: PASS
    evidence: formatting validation completed with no repository mutation.
  - command: local C++ edit/build/test loop
    result: BLOCKED
    evidence: no local Canary checkout was available; exact-head GitHub CI is the compile/test evidence and no local build is claimed.
blockers:
  - Full OTClient -> Oteryn Gateway -> Canary native-auth E2E is unproven.
  - Production readiness remains blocked until missing Platform hardening is delivered and proven.
  - Production Gateway -> Canary private-network/TLS transport and credential rotation are unproven.
  - Immediate generation-based revocation, multi-world routing and same-world horizontal scaling are outside Gateway protocol v1.
next_action: Build and run one bounded cross-repository native-auth E2E that starts the Oteryn Platform Gateway against this Canary issuer and proves a maintained OTClient can redeem a fresh ticket, receive one Game Session, enter the intended character exactly once, and fail closed on replay.
```
