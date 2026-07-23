---
task_id: CAN-20260722-oteryn-game-session-adapter
program_id: none
coordination_id: OTS-20260721-oteryn-identity-auth
status: ready
agent: "GPT-5.6 Thinking"
branch: feat/CAN-20260722-oteryn-game-session-adapter
base_branch: main
created: 2026-07-22T16:00:00+02:00
updated: 2026-07-23T16:50:00+02:00
last_verified_commit: b8a88f073b2609b444fa15370aae30ac9f80b908
risk: high
related_issue: ""
related_pr: "722"
depends_on:
  - "OTClient PR #17 merged as bb87346f6c516a19d19497d82bb01fb389334ff5"
  - "Oteryn Platform Gateway PR #122 merged as 8006534108d835474dadd208b0ec934e4a12528b"
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/archive/CAN-20260722-oteryn-game-session-adapter.md
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
- [x] Squash-merge PR #722 without enabling the issuer.

Production activation is tracked separately by `CAN-20260723-oteryn-native-auth-production-cutover`; this archived task authorizes no issuer enablement or legacy-auth removal.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T16:50:00+02:00
head: b8a88f073b2609b444fa15370aae30ac9f80b908
branch: feat/CAN-20260722-oteryn-game-session-adapter
pr: 722
status: ready
context_routes:
  - agent-governance
  - cpp-runtime
  - cross-repo
owned_paths:
  - docs/agents/tasks/archive/CAN-20260722-oteryn-game-session-adapter.md
changed_paths:
  - docs/agents/CHANGELOG.md
  - docs/agents/CROSS_REPO_CONTRACTS.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/archive/CAN-20260722-oteryn-game-session-adapter.md
  - src/main.cpp
  - src/security/CMakeLists.txt
  - src/security/game_session_http_issuer.cpp
  - src/security/game_session_http_issuer.hpp
  - src/server/server.cpp
  - tests/unit/security/CMakeLists.txt
  - tests/unit/security/game_session_http_issuer_test.cpp
  - vcproj/settings.props
proven:
  - Candidate B is implemented as a disabled-by-default per-process HTTP issuer reusing LoginSessionManager with SHA-256-only storage, 60-second TTL, atomic single-use consume and duplicate login_attempt_id fail-closed behavior.
  - Canary loads authoritative account and allowed-character data by numeric Canary account id without Oteryn password authentication; existing ProtocolGame and IOLoginData admission checks remain authoritative.
  - Explicit CANARY_GAME_SESSION_ISSUER_WORLD_ID is separate from Canary ChannelContext channel_id and binds the configured Platform world to the exact issuer process.
  - OTClient PR #17 and Oteryn Platform Gateway PR #122 are merged at the pinned revisions recorded in CROSS_REPO_CONTRACTS.md.
  - Bounded native-auth E2E is proven by runs 29988893301 and 29992417296, including exactly one successful Knight 1 world entry and fail-closed replay.
  - Exact head fd6fc67ba8aa11834cebb79cc7539599e3c16e72 passed CI 30003004108, Security Validation 30003004106, Agent Task Ownership 30003003973 and autofix 30003003958.
  - PR #722 was squash-merged to main as b8a88f073b2609b444fa15370aae30ac9f80b908 on 2026-07-23 with the issuer still disabled by default.
derived:
  - Production hardening, private/TLS transport, service-credential rotation, security-generation revocation, multi-world routing and horizontal replicas remain outside this completed adapter implementation.
  - Active issuer-path ownership is released by archiving this completed task; follow-up changes belong to CAN-20260723-oteryn-native-auth-production-cutover.
unknown:
  - Exact production private-network/TLS and secret deployment state remains outside this completed adapter task.
conflicts:
  - Prior handoff claimed Oteryn Platform PR #123 was merged; verified live state showed it closed unmerged, so no production-hardening claim is inherited from it.
first_failure:
  marker: none
  evidence: Adapter acceptance criteria are complete and PR #722 is merged; production activation is tracked separately.
rejected_hypotheses:
  - Reuse ProtocolLogin issuer unchanged: it requires account password authentication.
  - Use DB account_sessions as single-use: current contract records replay until expiry or deletion.
  - Treat Platform game_worlds.id as Canary ChannelContext channel_id: the issuer uses a separately configured Platform world id.
validation:
  - command: bounded native-auth E2E runs 29988893301 and 29992417296
    result: PASS
    evidence: Successful world entry and fail-closed replay proven on pinned Canary, OTClient and Gateway revisions.
  - command: exact-head final gate on fd6fc67ba8aa11834cebb79cc7539599e3c16e72
    result: PASS
    evidence: CI 30003004108, Security Validation 30003004106, Agent Task Ownership 30003003973 and autofix 30003003958 all succeeded.
  - command: squash merge PR #722
    result: PASS
    evidence: merged commit b8a88f073b2609b444fa15370aae30ac9f80b908.
blockers:
  - none
next_action: Continue all production activation, TLS and credential-rotation work in CAN-20260723-oteryn-native-auth-production-cutover.
```
