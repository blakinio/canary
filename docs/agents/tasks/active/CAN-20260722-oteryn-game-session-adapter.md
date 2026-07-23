---
task_id: CAN-20260722-oteryn-game-session-adapter
program_id: none
coordination_id: OTS-20260721-oteryn-identity-auth
status: blocked
agent: "GPT-5.6 Thinking"
branch: feat/CAN-20260722-oteryn-game-session-adapter
base_branch: main
created: 2026-07-22T16:00:00+02:00
updated: 2026-07-23T13:12:00+02:00
last_verified_commit: c75f90d97a33645bcd5e1654ae071add9b382839
risk: high
related_issue: ""
related_pr: "722"
depends_on:
  - "Oteryn Platform architecture/OAuth/ticket/Gateway phases"
  - "OTClient PR #17 merged as bb87346f6c516a19d19497d82bb01fb389334ff5"
  - "Oteryn Platform Gateway PR #122 merged as 8006534108d835474dadd208b0ec934e4a12528b"
  - "Oteryn Platform docs/contracts/GAME_SESSION_CANARY_CONTRACT.md"
blocks:
  - "production Oteryn native-auth cutover pending Platform hardening and deployment-boundary proof"
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

- [x] Canary adapter implementation, focused tests, build registration and documentation are complete.
- [x] Exact-head Canary CI, security, ownership and formatting validation are green.
- [x] Prove full OTClient -> Oteryn Gateway -> Canary native-auth E2E before any production-readiness claim.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T13:12:00+02:00
head: c75f90d97a33645bcd5e1654ae071add9b382839
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
  - LoginSessionManager provides SHA-256-only process-local storage, 60-second TTL and atomic single-use consume; duplicate login_attempt_id issuance is fail-closed for the token TTL.
  - Existing ProtocolGame and IOLoginData world-entry ownership, deletion, ban and runtime checks remain unchanged and authoritative after token issuance.
  - Cross-repository contracts document the issuer and rollout; OTClient PR #17 is merged at bb87346f6c516a19d19497d82bb01fb389334ff5 and Oteryn Platform Gateway PR #122 is merged at 8006534108d835474dadd208b0ec934e4a12528b.
  - Canary implementation head 285dec6a034aa3620ae5ca12549fb9e8e1b35631 passed CI run 29957357479, Security Validation run 29957357463, Agent Task Ownership run 29957357248 and autofix run 29957357043.
  - Bounded cross-repository E2E is proven: behavior run 29988893301 recorded one successful Knight 1 world entry and replay_rejected=login_error with successful_world_entries=1; final evidence run 29992417296 also passed physical job 89166128089 and Required physical E2E job 89167924405 using Canary 285dec6a034aa3620ae5ca12549fb9e8e1b35631, OTClient bb87346f6c516a19d19497d82bb01fb389334ff5 and Gateway 8006534108d835474dadd208b0ec934e4a12528b.
  - Documentation checkpoint head 9383fb3d7fa13e66b29bce798b3eaa2fddd4c2e9 passed CI run 29995633375, Security Validation run 29995633305, Agent Task Ownership run 29995632827 and autofix run 29995633398.
  - Exact head c75f90d97a33645bcd5e1654ae071add9b382839 passed final-gate CI run 29998294235, Security Validation run 29998294153, Agent Task Ownership run 29998294025 and autofix run 29998293999.
  - PR #722 is open and non-draft; current main is 5d5f719406746fba06aa1d9ed175edccc83bf05e, the branch is 40 commits behind main, and GitHub currently reports mergeable false.
  - Since PR #722 branched from 997343078104831ae3761e691c96fd8ff8d6cfa2, current main changed both docs/agents/CHANGELOG.md and docs/agents/MODULE_CATALOG.md while PR #722 also changes those shared files.
  - Oteryn Platform PR #123 remains closed unmerged with zero commits and zero changed files; a bounded PR search found no successor delivering its advertised throttling, overlapping service-credential hash rotation and full no-store/no-cache hardening.
derived:
  - Candidate B preserves stronger single-use world-entry semantics than replayable account_sessions.
  - A lost successful create-session response intentionally cannot be recovered by repeating the same login_attempt_id; the orphan token expires and the client must start a fresh native-login attempt.
  - Gateway protocol v1 safely supports only ProtocolProfileId::Current without expanding the cross-repository request contract.
  - PR #722 requires a current-main branch refresh and controlled shared-document reconciliation before any future merge consideration.
unknown:
  - Exact production private-network/TLS boundary and service-credential rotation mechanism for Gateway -> Canary remain unproven.
  - Future requirements for immediate security-generation revocation, multi-world routing and same-world horizontal replicas remain outside the proven v1 deployment model.
conflicts:
  - Prior handoff claimed Oteryn Platform PR #123 was merged; live state on 2026-07-23 confirms it is closed unmerged and its advertised hardening remains absent.
  - docs/agents/MODULE_CATALOG.md still describes full Gateway -> Canary -> OTClient E2E as a production blocker even though runs 29988893301 and 29992417296 prove the bounded E2E; preserve current-main catalogue changes while correcting this entry during branch refresh.
first_failure:
  marker: pr-not-mergeable-stale-base
  evidence: PR #722 is currently mergeable=false; its head c75f90d97a33645bcd5e1654ae071add9b382839 is 40 commits behind main 5d5f719406746fba06aa1d9ed175edccc83bf05e and both sides changed shared CHANGELOG/MODULE_CATALOG paths since merge base 997343078104831ae3761e691c96fd8ff8d6cfa2.
rejected_hypotheses:
  - Reuse ProtocolLogin issuer unchanged: it requires account password authentication.
  - Use DB account_sessions as single-use: current contract records replay until expiry or deletion.
  - Serve the issuer through existing Tibia ServicePort multiplexing: it lacks the required HTTP and service-auth boundary.
  - Issue all tokens in the login-gateway process: LoginSessionManager storage is process-local.
  - Treat Platform game_worlds.id as Canary ChannelContext channel_id: ServiceManager uses a separately configured Platform world id and only logs local channel identity.
validation:
  - command: exact-head CI run 29957357479 on 285dec6a034aa3620ae5ca12549fb9e8e1b35631
    result: PASS
    evidence: Canary implementation CI completed successfully.
  - command: Security Validation run 29957357463 on 285dec6a034aa3620ae5ca12549fb9e8e1b35631
    result: PASS
    evidence: Canary implementation security validation completed successfully.
  - command: Agent Task Ownership run 29957357248 and autofix run 29957357043 on 285dec6a034aa3620ae5ca12549fb9e8e1b35631
    result: PASS
    evidence: ownership/checkpoint validation passed and formatting completed without mutation.
  - command: exact-head documentation CI/Security/Ownership/autofix on 9383fb3d7fa13e66b29bce798b3eaa2fddd4c2e9
    result: PASS
    evidence: runs 29995633375, 29995633305, 29995632827 and 29995633398 all completed successfully.
  - command: Universal Agent E2E behavior run 29988893301
    result: PASS
    evidence: maintained OTClient entered Knight 1 exactly once through Gateway and Canary, then replay of the same Game Session failed with login_error and successful_world_entries=1.
  - command: Universal Agent E2E final evidence run 29992417296 on E2E head 804e7c0e233305592d941525951e2e124d407149
    result: PASS
    evidence: physical job 89166128089 and Required physical E2E job 89167924405 completed successfully; CI, ownership and autofix for the evidence head were also green.
  - command: final-gate validation on c75f90d97a33645bcd5e1654ae071add9b382839
    result: PASS
    evidence: CI 29998294235, Security Validation 29998294153, Agent Task Ownership 29998294025 and autofix 29998293999 all completed successfully.
blockers:
  - PR #722 current head is not mergeable against current main and requires a branch refresh with shared-document reconciliation.
  - Production readiness remains blocked until the missing Oteryn Platform hardening is delivered and proven.
  - Production Gateway -> Canary private-network/TLS transport and service-credential rotation remain unproven.
  - Immediate generation-based revocation, multi-world routing and same-world horizontal scaling are outside Gateway protocol v1 and require separate design before they are claimed.
next_action: Refresh PR #722 onto current main, preserving current-main CHANGELOG/MODULE_CATALOG changes while applying the corrected Oteryn Game Session entries, then rerun the final gate on the resulting exact head.
```
