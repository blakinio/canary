---
task_id: CAN-20260722-oteryn-game-session-adapter
program_id: none
coordination_id: OTS-20260721-oteryn-identity-auth
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/CAN-20260722-oteryn-game-session-adapter
base_branch: main
created: 2026-07-22T16:00:00+02:00
updated: 2026-07-22T18:53:18+02:00
last_verified_commit: 3a442735b6d2bb2191bb4791e607b4b96da1fb93
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
    - src/canary_server.hpp
    - src/canary_server.cpp
    - vcproj/canary.vcxproj
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
- [x] Select Candidate B explicitly and document replay, expiry, revocation, restart and process/world semantics.
- [ ] Preserve final Canary character ownership/deletion/ban/runtime admission checks.
- [ ] Keep legacy authentication unchanged while the adapter is disabled/not configured.
- [ ] Bind external issuance to exact account, world/process route and ProtocolProfileId::Current without password fallback.
- [ ] Use least-privilege service authentication and never log raw Game Session credentials.
- [ ] Add focused coverage for issue/consume, expiry, replay, wrong account/character/profile, restart and routing behavior.
- [ ] Register new C++ sources in CMake and maintained Visual Studio project entry points.
- [ ] Update cross-repository contract/catalogue/changelog with rollout order and compatible version pair.
- [ ] Pass exact-final-head required CI and cross-repository E2E before any production-readiness claim.

## Selected design

Candidate B is selected: a disabled-by-default internal HTTP issuer runs inside the exact Canary world process and issues through the existing process-local LoginSessionManager.

Initial supported scope:

- Gateway protocol v1 only;
- exactly one advertised world mapped to exactly one Canary process;
- request world_id must equal g_channelContext().getChannelId();
- account is loaded by canary_account_id and allowed character names come from Account::getAccountPlayers();
- issued credential is bound to ProtocolProfileId::Current;
- existing ProtocolGame -> IOLoginData admission path remains authoritative;
- legacy password/session authentication remains unchanged when issuer configuration is absent or disabled.

Issuer configuration is environment-only and disabled by default. Planned variables are CANARY_GAME_SESSION_ISSUER_ENABLED, CANARY_GAME_SESSION_ISSUER_BIND, CANARY_GAME_SESSION_ISSUER_PORT, CANARY_GAME_SESSION_SERVICE_TOKEN_SHA256 and CANARY_GAME_SESSION_ISSUER_REQUEST_TIMEOUT_MS. The service stores only the expected SHA-256 credential hash, exposes GET /health and authenticated POST /internal/v1/game-sessions, bounds request size/time, returns no-store responses and never logs raw bearer or session credentials.

Current Gateway protocol v1 has one GAME_SESSION_SERVICE_BASE_URL and does not forward Canary protocol profile or Identity security_generation. Immediate generation-based revocation, old-profile support, multi-world issuer selection and same-world horizontal scaling remain explicit future contract work.

Current Oteryn Platform main still lacks the three hardening items advertised by closed-unmerged PR #123: pre-auth throttling, overlapping Gateway credential-hash rotation and full no-store coverage. Production readiness also remains gated on a proven private-network/TLS boundary for Gateway -> Canary traffic.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T18:53:18+02:00
head: 3a442735b6d2bb2191bb4791e607b4b96da1fb93
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
  - src/canary_server.hpp
  - src/canary_server.cpp
  - vcproj/canary.vcxproj
  - tests/unit/security/game_session_http_issuer_test.cpp
  - tests/unit/security/CMakeLists.txt
proven:
  - OTClient PR 17 is merged and forwards the Gateway-issued Game Session through the existing GameSessionKey world-entry field.
  - LoginSessionManager stores SHA-256 token hashes in process memory, uses a 60-second default TTL and atomically consumes matching tokens exactly once while binding account id, allowed character names and ProtocolProfileId.
  - Account can load authoritatively by numeric Canary account id and expose its current player names without password authentication.
  - Canary multi-channel architecture uses one OS process per channel and ChannelContext resolves the exact process channel id.
  - Merged Oteryn Platform Gateway PR 122 calls POST /internal/v1/game-sessions with bearer auth and one global session-service base URL, and rejects login contexts that do not contain exactly one world.
  - Current Platform main still has one configured Gateway token hash, service-auth-before-throttle route ordering and ticket controllers without no-store headers.
  - No open discovered Canary PR owns the runtime paths claimed by this task; PR 514 remains security validation tooling/docs and PR 526 audit docs.
  - Current connector execution environment has no local Canary checkout, so compilation/runtime proof must come from remote CI until a local execution capability becomes available.
derived:
  - Candidate B preserves stronger single-use semantics than replayable account_sessions.
  - The first deployment can route to the exact consuming process by pointing the Gateway session-service URL at the sole world process and rejecting mismatched world_id.
  - Gateway protocol v1 can safely issue only ProtocolProfileId::Current without expanding the cross-repository request contract.
unknown:
  - Exact production private-network/TLS boundary and credential-rotation mechanism for Gateway -> Canary issuer traffic.
  - Whether future production requirements mandate multi-world routing or same-world horizontal replicas in the first expansion.
conflicts:
  - Prior handoff claimed Oteryn Platform PR 123 was merged; live PR state and current Platform main prove it was closed unmerged and its advertised hardening remains absent.
first_failure:
  marker: runtime-implementation-not-yet-validated
  evidence: Discovery/design and current documentation CI are green, but no Canary runtime issuer implementation has yet been compiled or tested.
rejected_hypotheses:
  - Reuse ProtocolLogin issuer unchanged: it requires account password authentication.
  - Use DB account_sessions as single-use: current contract records replay until expiry/deletion.
  - Reuse ServiceManager unchanged as authenticated HTTP issuer: it has no service-auth primitive and uses shared listener binding policy.
  - Issue all tokens in the login-gateway process: LoginSessionManager storage is process-local.
changed_paths:
  - docs/agents/tasks/active/CAN-20260722-oteryn-game-session-adapter.md
validation:
  - command: current documentation CI and Agent Task Ownership on 3a442735b6d2bb2191bb4791e607b4b96da1fb93
    result: PASS
    evidence: CI run 29937722340 and Agent Task Ownership run 29937722005 completed successfully.
  - command: local C++ edit/build/test loop
    result: BLOCKED
    evidence: no local Canary checkout is present in the current execution environment; implementation will be connector-written and validated by remote CI without claiming local build proof.
blockers:
  - Production readiness remains blocked until missing Platform hardening is delivered and proven.
  - Production Gateway -> Canary transport security is not yet proven.
  - Immediate generation-based revocation, multi-world routing and same-world horizontal scaling are outside Gateway protocol v1.
next_action: Implement the claimed disabled-by-default per-process Candidate B HTTP issuer, integrate it into CanaryServer lifecycle, register CMake/Visual Studio sources, add focused unit coverage, then use remote CI to resolve compile/test failures before updating shared contracts and final E2E gates.
```
