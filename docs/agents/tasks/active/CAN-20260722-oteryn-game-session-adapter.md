---
task_id: CAN-20260722-oteryn-game-session-adapter
program_id: none
coordination_id: OTS-20260721-oteryn-identity-auth
status: blocked
agent: "GPT-5.6 Thinking"
branch: feat/CAN-20260722-oteryn-game-session-adapter
base_branch: main
created: 2026-07-22T16:00:00+02:00
updated: 2026-07-22T21:45:00+02:00
last_verified_commit: bdd95eb847f17713f2788c2a10092d864c17e666
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
- [x] Prove Linux debug unit tests, Linux release/runtime smoke, macOS, Windows MSBuild and Docker on the validated runtime head.
- [x] Update cross-repository contract, module catalogue and changelog with rollout/failure semantics.
- [ ] Prove the final documentation/checkpoint head through the repository exact-final-head gate.
- [ ] Prove full OTClient -> Oteryn Gateway -> Canary native-auth E2E before any production-readiness claim.

## Selected design and implementation

Candidate B is implemented as a disabled-by-default dedicated Asio HTTP issuer that reuses the process-local LoginSessionManager.

Supported initial contract:

- `GET /health`;
- bearer-authenticated `POST /internal/v1/game-sessions`;
- exact Gateway protocol v1 fields: `protocol_version`, `canary_account_id`, Platform `world_id`, and a 32-hex-character `login_attempt_id`;
- request body capped at 8 KiB with bounded read timeout;
- `Cache-Control: no-store` and `Pragma: no-cache` responses;
- expected service bearer configured only as a SHA-256 digest;
- when enabled, `ServiceManager::run()` requires a positive `CANARY_GAME_SESSION_ISSUER_WORLD_ID` and overrides the issuer world callback with that Platform world ID before construction;
- Canary `ChannelContext::channel_id` is logged only as process/channel identity and is not equated with Platform `game_worlds.id`;
- the Gateway session-service base URL selects the exact Canary process for the supported single-world/single-process deployment;
- account is loaded by numeric Canary account id and allowed character names are resolved from Canary account data without password authentication;
- the issued credential is bound to ProtocolProfileId::Current and consumed by the unchanged ProtocolGame -> IOLoginData path;
- LoginSessionManager stores only the credential hash, applies the 60-second TTL and atomically removes the token before validation/consume completion;
- duplicate login_attempt_id requests are rejected for the same process/TTL; failed issuance releases the attempt reservation;
- restart loses all unconsumed process-local credentials and attempt reservations;
- absent or explicitly disabled issuer configuration preserves legacy authentication behavior.

Environment contract: `CANARY_GAME_SESSION_ISSUER_ENABLED`, `CANARY_GAME_SESSION_ISSUER_BIND`, `CANARY_GAME_SESSION_ISSUER_PORT`, `CANARY_GAME_SESSION_ISSUER_WORLD_ID`, `CANARY_GAME_SESSION_SERVICE_TOKEN_SHA256`, and optional `CANARY_GAME_SESSION_ISSUER_REQUEST_TIMEOUT_MS`.

Gateway protocol v1 still exposes one `GAME_SESSION_SERVICE_BASE_URL` and does not forward Canary protocol profile or Identity `security_generation`. Immediate generation-based revocation, old-profile support, multi-world issuer selection and same-world horizontal replicas therefore remain outside the current contract.

Current Oteryn Platform main still lacks pre-auth throttling, overlapping Gateway service-credential hash rotation and full ticket-boundary no-store coverage advertised by closed-unmerged PR #123. Production readiness also remains gated on a proven private-network/TLS boundary for Gateway -> Canary traffic.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T21:45:00+02:00
head: bdd95eb847f17713f2788c2a10092d864c17e666
branch: feat/CAN-20260722-oteryn-game-session-adapter
pr: 722
status: blocked
context_routes:
  - agent-governance
  - cpp-runtime
  - cross-repo
proven:
  - Candidate B is implemented as a disabled-by-default per-process HTTP issuer reusing LoginSessionManager.
  - LoginSessionManager provides SHA-256-only process-local storage, 60-second default TTL and atomic single-use consume bound to account, allowed character names and protocol profile.
  - Account data is loaded authoritatively by numeric Canary account id without Oteryn password authentication.
  - ServiceManager requires a positive CANARY_GAME_SESSION_ISSUER_WORLD_ID when the issuer is enabled and overrides the production issuer world callback with that explicit Platform ID; Platform game_worlds.id is not Canary ChannelContext channel_id.
  - The supported first deployment uses the sole Gateway session-service URL for exact process affinity and the explicit configured Platform world ID for world affinity.
  - Duplicate login_attempt_id issuance is fail-closed for the token TTL; failed issuance releases the reservation and raw Game Session credentials are not retained by the replay guard.
  - Existing ProtocolGame and IOLoginData world-entry checks remain unchanged and authoritative after token issuance.
  - Runtime head f71ce24d75b920bac10fedb4b04601ac75c01a2f passed full CI run 29944180006, including Linux debug tests, Linux release/runtime smoke, macOS, Windows MSBuild and Docker; Security Validation run 29944179785 and Agent Task Ownership run 29944179536 also passed.
  - Cross-repository contract, module catalogue and changelog now document the issuer, rollout order, retry/failure semantics and production blockers.
  - Documentation head 8b73252a5943d633a5d59d86114a3d72185f0258 passed CI run 29947152600, Security Validation run 29947152617, Agent Task Ownership run 29947152833 and autofix run 29947152495.
  - Current Platform main still lacks the three hardening items advertised by closed-unmerged PR 123.
derived:
  - Candidate B preserves stronger single-use world-entry semantics than replayable account_sessions.
  - A lost successful create-session response intentionally cannot be recovered by repeating the same login_attempt_id; the orphan token expires and the client must start a fresh native-login attempt.
  - Gateway protocol v1 can safely issue only ProtocolProfileId::Current without expanding the cross-repository request contract.
unknown:
  - Full native OTClient -> Oteryn Gateway -> Canary E2E behavior has not yet been proven by an orchestrator covering all three repositories.
  - Exact production private-network/TLS boundary and service-credential rotation mechanism for Gateway -> Canary remain unproven.
  - Whether future production requirements mandate multi-world routing or same-world horizontal replicas in the first expansion remains unresolved.
conflicts:
  - Prior handoff claimed Oteryn Platform PR 123 was merged; live PR state and current Platform main prove it was closed unmerged and its advertised hardening remains absent.
first_failure:
  marker: cross-repo-native-auth-e2e-unproven
  evidence: Canary runtime compile/unit/security validation is green, but the existing Universal Agent E2E workflow does not orchestrate the Oteryn Platform Gateway, so no full OTClient -> Gateway -> Canary native-auth proof exists yet.
rejected_hypotheses:
  - Reuse ProtocolLogin issuer unchanged: it requires account password authentication.
  - Use DB account_sessions as single-use: current contract records replay until expiry/deletion.
  - Serve the issuer through existing Tibia ServicePort multiplexing: it lacks the required HTTP/service-auth boundary.
  - Issue all tokens in the login-gateway process: LoginSessionManager storage is process-local.
  - Treat Platform game_worlds.id as Canary ChannelContext channel_id: ServiceManager uses a separately configured Platform world id and only logs the local channel identity.
validation:
  - command: full CI run 29944180006 on runtime head f71ce24d75b920bac10fedb4b04601ac75c01a2f
    result: PASS
    evidence: Linux debug Run Tests, Linux release/runtime smoke, macOS, Windows MSBuild and Docker completed successfully.
  - command: Security Validation run 29944179785 on runtime head f71ce24d75b920bac10fedb4b04601ac75c01a2f
    result: PASS
  - command: documentation-head CI/Security/Ownership/autofix on 8b73252a5943d633a5d59d86114a3d72185f0258
    result: PASS
  - command: local C++ edit/build/test loop
    result: BLOCKED
    evidence: no local Canary checkout was available; remote exact-head CI is the compile/test evidence and no local build is claimed.
blockers:
  - Full OTClient -> Oteryn Gateway -> Canary native-auth E2E is unproven.
  - Production readiness remains blocked until missing Platform hardening is delivered and proven.
  - Production Gateway -> Canary private-network/TLS transport and credential rotation are unproven.
  - Immediate generation-based revocation, multi-world routing and same-world horizontal scaling are outside Gateway protocol v1.
next_action: Build and run one bounded cross-repository native-auth E2E that starts the Oteryn Platform Gateway against this Canary issuer and proves a maintained OTClient can redeem a fresh ticket, receive one Game Session, enter the intended character exactly once, and fail closed on replay.
```
