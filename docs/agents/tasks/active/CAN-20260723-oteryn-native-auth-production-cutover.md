---
task_id: CAN-20260723-oteryn-native-auth-production-cutover
program_id: none
coordination_id: OTS-20260721-oteryn-identity-auth
status: validating
agent: "GPT-5.6 Thinking"
branch: feat/CAN-20260723-oteryn-native-auth-production-cutover
base_branch: main
created: 2026-07-23T15:00:00+02:00
updated: 2026-07-23T17:15:00+02:00
last_verified_commit: f0b6354417c891b731ab80952ea099120c9bf6f7
risk: high
related_issue: ""
related_pr: "807"
depends_on:
  - "Canary Game Session adapter PR #722 merged as b8a88f073b2609b444fa15370aae30ac9f80b908"
  - "Oteryn Platform hardening PR #124"
blocks:
  - "production native-auth activation"
  - "legacy password-auth cutover"
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260723-oteryn-native-auth-production-cutover.md
    - docs/agents/tasks/active/CAN-20260722-oteryn-game-session-adapter.md
    - docs/agents/tasks/archive/CAN-20260722-oteryn-game-session-adapter.md
    - src/security/game_session_http_issuer.hpp
    - src/security/game_session_http_issuer.cpp
    - tests/unit/security/game_session_http_issuer_test.cpp
  shared:
    - docs/agents/CROSS_REPO_CONTRACTS.md
    - docs/agents/MODULE_CATALOG.md
modules_touched:
  - Oteryn Game Session HTTP issuer service authentication
  - Oteryn native-auth production rollout
reuses:
  - Oteryn Game Session HTTP issuer
  - LoginSessionManager
  - OTS-20260721-oteryn-identity-auth cross-repository contract
public_interfaces:
  - CANARY_GAME_SESSION_SERVICE_TOKEN_SHA256
  - CANARY_GAME_SESSION_PREVIOUS_SERVICE_TOKEN_SHA256
  - POST /internal/v1/game-sessions
cross_repo_tasks:
  - OTERYN-20260723-native-auth-production-cutover
---

# Goal

Complete the Canary-owned production-boundary prerequisite for safe Gateway -> Canary service-credential rotation while keeping the Game Session issuer disabled by default until coordinated production cutover gates are proven.

# Acceptance criteria

- [x] Current Gateway -> Canary service credential SHA-256 hash remains required when the issuer is enabled.
- [x] One optional previous service credential SHA-256 hash is accepted during a bounded rotation overlap window.
- [x] Invalid previous-hash configuration fails closed and duplicate current/previous hashes collapse to one effective credential.
- [x] Focused unit coverage proves current and previous credential acceptance and wrong-credential rejection.
- [ ] Exact final-head Canary CI, Security Validation, ownership and formatting checks are green.
- [ ] Cross-repository contract records the finalized Platform hardening and rotation sequence.
- [ ] Hardened OTClient -> Gateway -> Canary native-auth E2E is re-proven on exact merged revisions before production activation.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T17:15:00+02:00
head: f0b6354417c891b731ab80952ea099120c9bf6f7
branch: feat/CAN-20260723-oteryn-native-auth-production-cutover
pr: 807
status: validating
context_routes:
  - agent-governance
  - cpp-runtime
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260723-oteryn-native-auth-production-cutover.md
  - docs/agents/tasks/active/CAN-20260722-oteryn-game-session-adapter.md
  - docs/agents/tasks/archive/CAN-20260722-oteryn-game-session-adapter.md
  - src/security/game_session_http_issuer.hpp
  - src/security/game_session_http_issuer.cpp
  - tests/unit/security/game_session_http_issuer_test.cpp
  - docs/agents/CROSS_REPO_CONTRACTS.md
  - docs/agents/MODULE_CATALOG.md
proven:
  - Canary PR #722 merged as b8a88f073b2609b444fa15370aae30ac9f80b908 and the Game Session issuer remains disabled unless explicitly enabled.
  - Prior bounded native-auth E2E runs 29988893301 and 29992417296 proved one successful world entry and fail-closed replay on pre-hardening revisions.
  - PR #807 adds optional CANARY_GAME_SESSION_PREVIOUS_SERVICE_TOKEN_SHA256 while preserving required CANARY_GAME_SESSION_SERVICE_TOKEN_SHA256.
  - The issuer normalizes both hashes, rejects malformed previous hashes, collapses duplicate current/previous hashes, computes presented bearer SHA-256 once and compares configured hashes with the existing constant-time comparator.
  - Focused unit coverage accepts current and previous rotation credentials and rejects a wrong credential.
  - The completed PR #722 task is archived and its active task record removed so stale exclusive issuer ownership is released.
  - PR #807 branch was rebased by resetting to current main 014f156a8df4f7910a206f104c24842f3748cf99 and reapplying only the intended runtime/test plus lifecycle changes.
  - Oteryn Platform PR #124 hardened code head 2e664c440379af45b6413a26c9c0ee968275d049 passed all Platform CI, Gateway, governance, concurrency, DB outage, Phase 7 production-like and Acceptance E2E workflows.
derived:
  - Current/previous hash overlap enables bounded zero-downtime Gateway -> Canary credential rotation without enabling the issuer by default.
  - Repository merge remains deploy-first-safe; actual production activation is a separate external deployment action.
unknown:
  - exact production private-network ingress/firewall topology for Gateway -> Canary
  - exact production TLS certificate/hostname and secret-manager deployment state
  - final merged Platform #124 and Canary #807 SHAs
  - hardened exact-revision OTClient -> Gateway -> Canary E2E result
conflicts:
  - none currently
first_failure:
  marker: hardened-cross-repo-e2e-not-yet-reproven
  evidence: successful native-auth runs 29988893301 and 29992417296 predate Platform PR #124 and Canary PR #807 hardening
rejected_hypotheses:
  - Treat prior bounded E2E as proof of the hardened production boundary: prior runs do not include the new TLS/rotation hardening revisions.
  - Keep completed adapter task #722 under tasks/active: ownership validation proved stale exclusive issuer ownership conflicts with the follow-up task.
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-oteryn-native-auth-production-cutover.md
  - docs/agents/tasks/active/CAN-20260722-oteryn-game-session-adapter.md
  - docs/agents/tasks/archive/CAN-20260722-oteryn-game-session-adapter.md
  - src/security/game_session_http_issuer.hpp
  - src/security/game_session_http_issuer.cpp
  - tests/unit/security/game_session_http_issuer_test.cpp
validation:
  - command: pre-rebase CI 30016554527 on c8503b7d35fe15015e89b9d0067a8614e7a9d7a9
    result: PASS
    evidence: Canary runtime/build CI succeeded with credential overlap implementation.
  - command: pre-rebase Agent Task Ownership 30016555803 on c8503b7d35fe15015e89b9d0067a8614e7a9d7a9
    result: PASS
    evidence: ownership succeeded after completed adapter task lifecycle archival.
  - command: controlled rebase to main 014f156a8df4f7910a206f104c24842f3748cf99
    result: PASS
    evidence: branch was force-reset to current main and only intended issuer/test/task lifecycle changes were reapplied.
blockers:
  - rebased exact-head Canary validation is pending
  - cross-repository durable contract synchronization is pending final Platform merge revision
  - hardened cross-repository native-auth E2E is not yet re-proven
  - irreversible production activation requires direct deployed network/TLS/secret evidence outside repository-only state
next_action: Validate and merge Platform PR #124 and rebased Canary PR #807, then rerun login/oteryn-native-auth against their exact merge SHAs before any production activation.
```
