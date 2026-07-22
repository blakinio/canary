---
task_id: CAN-20260722-oteryn-game-session-adapter
program_id: none
coordination_id: OTS-20260721-oteryn-identity-auth
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/CAN-20260722-oteryn-game-session-adapter
base_branch: main
created: 2026-07-22T16:00:00+02:00
updated: 2026-07-22T19:04:15+02:00
last_verified_commit: b0bce72fd2a8f31374ea7a2181fef5a505b2ce85
risk: high
related_issue: ""
related_pr: "722"
depends_on:
  - "Oteryn Platform architecture/OAuth/ticket/Gateway phases"
  - "OTClient PR #17 merged as bb87346f6c516a19d19497d82bb01fb389334ff5"
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
  - ChannelContext
  - ServiceManager process lifecycle
  - existing GameSessionKey world-entry field consumed by ProtocolGame
public_interfaces:
  - POST /internal/v1/game-sessions
  - GET /health
cross_repo_tasks:
  - OTS-20260721-oteryn-identity-auth
---

# Goal

Implement the production Game Session -> Canary compatibility adapter for the Oteryn native-auth flow without transmitting or validating the user's Oteryn password in the supported path.

# Acceptance criteria

- [x] Revalidate current OTClient Phase 5 merge, Platform Gateway contract and Canary LoginSessionManager semantics.
- [x] Select Candidate B and document replay, expiry, revocation, restart and process/world semantics.
- [ ] Preserve final Canary character ownership/deletion/ban/runtime admission checks.
- [x] Keep legacy authentication unchanged while the adapter is disabled/not configured.
- [x] Bind external issuance to exact account, world/process route and ProtocolProfileId::Current without password fallback in implementation.
- [x] Use SHA-256 bearer service authentication and avoid logging raw Game Session/service credentials in implementation.
- [x] Add focused unit coverage for issue/consume, expiry, replay, wrong account/character/profile, restart and routing semantics.
- [x] Register new C++ source in CMake and the maintained Visual Studio property import.
- [ ] Prove implementation by current-head compile/tests and repair first failures.
- [ ] Update cross-repository contract/catalogue/changelog with rollout order and compatible version pair.
- [ ] Pass exact-final-head required CI and cross-repository E2E before any production-readiness claim.

## Selected design and implementation

Candidate B is selected. The branch now contains a disabled-by-default dedicated Asio HTTP issuer using the process-local LoginSessionManager.

Supported initial contract:

- `GET /health`;
- authenticated `POST /internal/v1/game-sessions`;
- exact Gateway protocol v1 fields only: protocol_version, canary_account_id, world_id and 32-hex-character login_attempt_id;
- request body capped at 8 KiB with bounded read timeout;
- `Cache-Control: no-store` and `Pragma: no-cache` on responses;
- expected bearer credential stored/configured only as a 64-character SHA-256 digest;
- request world_id must equal g_channelContext().getChannelId();
- account loaded by numeric Canary account id and allowed character names sourced from Account::getAccountPlayers();
- issued token bound to ProtocolProfileId::Current and consumed later by the unchanged ProtocolGame -> IOLoginData path;
- lifecycle owned by ServiceManager::run(), which starts only after Canary loader completion and stops the issuer with the service runtime;
- invalid enabled configuration or bind failure throws to main(), which logs a bounded error and exits nonzero;
- absent or explicitly disabled CANARY_GAME_SESSION_ISSUER_ENABLED leaves legacy behavior unchanged.

Environment contract: CANARY_GAME_SESSION_ISSUER_ENABLED, CANARY_GAME_SESSION_ISSUER_BIND, CANARY_GAME_SESSION_ISSUER_PORT, CANARY_GAME_SESSION_SERVICE_TOKEN_SHA256 and optional CANARY_GAME_SESSION_ISSUER_REQUEST_TIMEOUT_MS.

Current Gateway protocol v1 still has one GAME_SESSION_SERVICE_BASE_URL and does not forward Canary protocol profile or Identity security_generation. Immediate generation-based revocation, old-profile support, multi-world issuer selection and same-world horizontal scaling remain future contract work.

Current Oteryn Platform main still lacks pre-auth throttling, overlapping Gateway credential-hash rotation and full no-store coverage advertised by closed-unmerged PR #123. Production readiness also remains gated on a proven private-network/TLS boundary for Gateway -> Canary traffic.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T19:04:15+02:00
head: b0bce72fd2a8f31374ea7a2181fef5a505b2ce85
branch: feat/CAN-20260722-oteryn-game-session-adapter
pr: 722
status: implementing
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
proven:
  - OTClient PR 17 is merged and forwards the Gateway-issued Game Session through the existing GameSessionKey world-entry field.
  - LoginSessionManager provides process-local SHA-256-only storage, 60-second default TTL and atomic single-use consume bound to account, character names and protocol profile.
  - Account loads authoritatively by numeric Canary account id and exposes player names without password authentication.
  - Current implementation validates world_id against per-process ChannelContext and binds issued credentials to ProtocolProfileId::Current.
  - Current implementation is disabled by default, uses an independently configured literal bind address/port and verifies bearer credentials against a configured SHA-256 digest without logging raw credentials.
  - Current implementation is wired to ServiceManager::run() after loader completion and preserves existing ProtocolGame/IOLoginData authentication/admission code unchanged.
  - Focused unit tests cover disabled behavior, bearer auth, wrong world/account, no characters, account/character/current-profile binding, replay, expiry, wrong character/profile burn and process-local restart invalidation.
  - CMake and imported Visual Studio settings register the new runtime source; current-head CI, ownership and Security Validation are running.
  - Current Platform main still lacks the three hardening items advertised by closed-unmerged PR 123.
derived:
  - Candidate B preserves stronger single-use semantics than replayable account_sessions.
  - The first deployment can route to the exact consuming process by pointing the single Gateway session-service URL at the sole world process and rejecting mismatched world_id.
  - Gateway protocol v1 can safely issue only ProtocolProfileId::Current without expanding the cross-repository request contract.
unknown:
  - Whether current-head remote C++ compile/unit tests pass; first CI run is in progress.
  - Exact production private-network/TLS boundary and credential-rotation mechanism for Gateway -> Canary issuer traffic.
  - Whether future production requirements mandate multi-world routing or same-world horizontal replicas in the first expansion.
conflicts:
  - Prior handoff claimed Oteryn Platform PR 123 was merged; live PR state and current Platform main prove it was closed unmerged and its advertised hardening remains absent.
first_failure:
  marker: runtime-implementation-ci-pending
  evidence: runtime implementation is committed through b0bce72fd2a8f31374ea7a2181fef5a505b2ce85; CI run 29940748854, Agent Task Ownership run 29940748306 and Security Validation run 29940749623 have not yet produced final current-head evidence.
rejected_hypotheses:
  - Reuse ProtocolLogin issuer unchanged: it requires account password authentication.
  - Use DB account_sessions as single-use: current contract records replay until expiry/deletion.
  - Serve the issuer through existing Tibia ServicePort protocol multiplexing: it lacks the required HTTP/service-auth boundary.
  - Issue all tokens in the login-gateway process: LoginSessionManager storage is process-local.
changed_paths:
  - docs/agents/tasks/active/CAN-20260722-oteryn-game-session-adapter.md
  - src/security/game_session_http_issuer.hpp
  - src/security/game_session_http_issuer.cpp
  - src/security/CMakeLists.txt
  - src/server/server.cpp
  - src/main.cpp
  - vcproj/settings.props
  - tests/unit/security/game_session_http_issuer_test.cpp
  - tests/unit/security/CMakeLists.txt
validation:
  - command: prior documentation-only CI and Agent Task Ownership
    result: PASS
    evidence: CI run 29937722340 and Agent Task Ownership run 29937722005 completed successfully before runtime edits.
  - command: local C++ edit/build/test loop
    result: BLOCKED
    evidence: no local Canary checkout is present; runtime code is connector-written and must be proven by remote CI without claiming local build evidence.
  - command: current runtime implementation CI
    result: NOT_RUN
    evidence: current-head CI/Security Validation/ownership runs are in progress and not yet final.
blockers:
  - Production readiness remains blocked until missing Platform hardening is delivered and proven.
  - Production Gateway -> Canary transport security is not yet proven.
  - Immediate generation-based revocation, multi-world routing and same-world horizontal scaling are outside Gateway protocol v1.
next_action: Inspect the first completed current-head runtime CI/test failure, fix only its proven root cause, and repeat remote validation until the implementation compiles and focused tests pass.
```
