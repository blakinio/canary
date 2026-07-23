---
task_id: CAN-20260722-oteryn-game-session-adapter
program_id: none
coordination_id: OTS-20260721-oteryn-identity-auth
status: ready
agent: "GPT-5.6 Thinking"
branch: feat/CAN-20260722-oteryn-game-session-adapter
base_branch: main
created: 2026-07-22T16:00:00+02:00
updated: 2026-07-23T15:10:00+02:00
last_verified_commit: 0d16b90d641655310142d7fa45b017bcb86684f9
risk: high
related_issue: ""
related_pr: "722"
depends_on:
  - "OTClient PR #17 merged as bb87346f6c516a19d19497d82bb01fb389334ff5"
  - "Oteryn Platform Gateway PR #122 merged as 8006534108d835474dadd208b0ec934e4a12528b"
blocks: []
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
- [x] Separate production activation gates from the deploy-first-safe disabled Canary implementation.

Production activation is tracked separately by `CAN-20260723-oteryn-native-auth-production-cutover`; merging this task does not authorize enabling the issuer or removing legacy authentication.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T15:10:00+02:00
head: 0d16b90d641655310142d7fa45b017bcb86684f9
branch: feat/CAN-20260722-oteryn-game-session-adapter
pr: 722
status: ready
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
proven:
  - Candidate B is implemented as a disabled-by-default per-process HTTP issuer reusing LoginSessionManager with SHA-256-only storage, 60-second TTL, atomic single-use consume and duplicate login_attempt_id fail-closed behavior.
  - Canary loads authoritative account and allowed-character data by numeric Canary account id without Oteryn password authentication; existing ProtocolGame and IOLoginData admission checks remain authoritative.
  - Explicit CANARY_GAME_SESSION_ISSUER_WORLD_ID is separate from Canary ChannelContext channel_id and binds the configured Platform world to the exact issuer process.
  - OTClient PR #17 and Oteryn Platform Gateway PR #122 are merged at the pinned revisions recorded in CROSS_REPO_CONTRACTS.md.
  - Bounded native-auth E2E is proven by runs 29988893301 and 29992417296, including exactly one successful Knight 1 world entry and fail-closed replay.
  - docs/agents/CROSS_REPO_CONTRACTS.md records activation as atomic-required while Canary deployment is deploy-first-safe with the issuer disabled.
  - docs/agents/MODULE_CATALOG.md records bounded native-auth E2E as proven and keeps production activation controls separate.
  - Exact head fd6fc67ba8aa11834cebb79cc7539599e3c16e72 passed CI 30003004108, Security Validation 30003004106, Agent Task Ownership 30003003973 and autofix 30003003958.
  - Production activation blockers are tracked by separate follow-up task CAN-20260723-oteryn-native-auth-production-cutover and do not block merging the disabled-by-default Canary implementation.
derived:
  - PR #722 can be merged independently without activating native auth because the issuer remains disabled unless explicitly configured.
  - Production hardening, private/TLS transport, service-credential rotation, security-generation revocation, multi-world routing and horizontal replicas remain outside this completed adapter implementation and are not claimed by this merge.
unknown:
  - Exact production private-network/TLS boundary and service-credential rotation remain unresolved in the separate production-cutover task.
conflicts:
  - Prior handoff claimed Oteryn Platform PR #123 was merged; verified live state on 2026-07-23 showed it closed unmerged, so no production-hardening claim is inherited from it.
first_failure:
  marker: none
  evidence: All acceptance criteria for the disabled-by-default Canary adapter are satisfied; remaining production activation gates are tracked separately.
rejected_hypotheses:
  - Reuse ProtocolLogin issuer unchanged: it requires account password authentication.
  - Use DB account_sessions as single-use: current contract records replay until expiry or deletion.
  - Treat Platform game_worlds.id as Canary ChannelContext channel_id: the issuer uses a separately configured Platform world id.
changed_paths:
  - docs/agents/CHANGELOG.md
  - docs/agents/CROSS_REPO_CONTRACTS.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260722-oteryn-game-session-adapter.md
  - docs/agents/tasks/active/CAN-20260723-oteryn-native-auth-production-cutover.md
  - src/main.cpp
  - src/security/CMakeLists.txt
  - src/security/game_session_http_issuer.cpp
  - src/security/game_session_http_issuer.hpp
  - src/server/server.cpp
  - tests/unit/security/CMakeLists.txt
  - tests/unit/security/game_session_http_issuer_test.cpp
  - vcproj/settings.props
validation:
  - command: bounded native-auth E2E runs 29988893301 and 29992417296
    result: PASS
    evidence: Successful world entry and fail-closed replay proven on pinned Canary, OTClient and Gateway revisions.
  - command: exact-head final gate on fd6fc67ba8aa11834cebb79cc7539599e3c16e72
    result: PASS
    evidence: CI 30003004108, Security Validation 30003004106, Agent Task Ownership 30003003973 and autofix 30003003958 all succeeded.
  - command: final gate after task-scope split
    result: NOT_RUN
    evidence: The resulting final head must pass the ci:final-gate validation before squash merge.
blockers:
  - none
next_action: Squash-merge PR #722 after the resulting exact head passes all required ci:final-gate checks.
```
