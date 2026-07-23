---
task_id: CAN-20260723-oteryn-native-auth-production-cutover
program_id: none
coordination_id: OTS-20260721-oteryn-identity-auth
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/CAN-20260723-oteryn-native-auth-production-cutover
base_branch: main
created: 2026-07-23T15:00:00+02:00
updated: 2026-07-23T17:30:00+02:00
last_verified_commit: 46f60f1efc04349e707250de8965338f94d90d71
risk: high
related_issue: ""
related_pr: "807"
depends_on:
  - "Canary Game Session adapter PR #722 merged as b8a88f073b2609b444fa15370aae30ac9f80b908"
  - "Oteryn Platform hardening PR #124 merged as 53158217a6c6017230301cf4daa783b04fcc13d5"
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
- [x] Cross-repository contract records merged Platform hardening and the finalized rotation/transport sequence.
- [ ] Hardened OTClient -> Gateway -> Canary native-auth E2E is re-proven on exact merged revisions before production activation.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T17:30:00+02:00
head: 46f60f1efc04349e707250de8965338f94d90d71
branch: feat/CAN-20260723-oteryn-native-auth-production-cutover
pr: 807
status: implementing
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
  - PR #807 branch was rebased onto Canary main 014f156a8df4f7910a206f104c24842f3748cf99 and the resulting delta contained only intended issuer/test/task-lifecycle changes before durable contract synchronization.
  - Oteryn Platform PR #124 merged as 53158217a6c6017230301cf4daa783b04fcc13d5 after all final-head Platform CI, Gateway, governance, concurrency, DB outage, Phase 7 production-like and Acceptance E2E workflows passed.
  - docs/agents/CROSS_REPO_CONTRACTS.md now records Platform #124 as merged, separate Gateway->Platform and Gateway->Canary overlap rotation, non-loopback HTTPS enforcement, prior bounded E2E and the remaining hardened-E2E/production-environment activation gates.
  - Exact-head ownership run 30019332976 failed only because an active task record used status validating; runtime/source ownership analysis did not run after the checkpoint validator rejected that non-active status.
derived:
  - Current/previous hash overlap enables bounded zero-downtime Gateway -> Canary credential rotation without enabling the issuer by default.
  - Repository merge remains deploy-first-safe; actual production activation is a separate deployment action requiring evidence unavailable from Git state alone.
  - Platform production hardening is no longer a blocker; remaining activation blockers are hardened exact-revision E2E plus direct deployed network/TLS/secret/revision evidence.
unknown:
  - exact production private-network ingress/firewall topology for Gateway -> Canary
  - exact production TLS certificate/hostname and secret-manager deployment state
  - final Canary #807 merge SHA
  - hardened exact-revision OTClient -> Gateway -> Canary E2E result
conflicts:
  - docs/agents/MODULE_CATALOG.md still describes Platform hardening as a production blocker; the current connector exposes only full-file replacement for this concurrently changed large catalogue, so an unsafe partial reconstruction was rejected and the stale catalogue record must be synchronized after hardened E2E evidence is finalized.
first_failure:
  marker: hardened-cross-repo-e2e-not-yet-reproven
  evidence: successful native-auth runs 29988893301 and 29992417296 predate merged Platform hardening #124 and Canary rotation PR #807
rejected_hypotheses:
  - Treat prior bounded E2E as proof of the hardened production boundary: prior runs do not include the new TLS/rotation hardening revisions.
  - Keep completed adapter task #722 under tasks/active: ownership validation proved stale exclusive issuer ownership conflicts with the follow-up task.
  - Rewrite MODULE_CATALOG.md from an incomplete/truncated connector read: that could discard unrelated catalogue updates made after PR #722.
  - Use validating as an active-task status: Agent Task Ownership run 30019332976 rejects records under tasks/active with non-active status validating.
changed_paths:
  - docs/agents/CROSS_REPO_CONTRACTS.md
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
  - command: Oteryn Platform PR #124 final-head validation and squash merge
    result: PASS
    evidence: all final-head workflows passed and PR #124 merged as 53158217a6c6017230301cf4daa783b04fcc13d5.
  - command: Agent Task Ownership 30019332976 on 46f60f1efc04349e707250de8965338f94d90d71
    result: FAIL
    evidence: checkpoint validator rejected status validating for a record under tasks/active; status is corrected to implementing in this final commit.
  - command: exact final-head Canary validation after this checkpoint correction
    result: NOT_RUN
    evidence: ci:final-gate remains applied; no further branch commits are permitted before evaluating exact-head CI/Ownership/autofix. Security Validation is not path-triggered by this PR delta.
blockers:
  - exact final-head Canary validation is pending
  - hardened cross-repository native-auth E2E is not yet re-proven
  - exact production private-network/TLS/secret-manager/deployed-revision evidence is unavailable from repository state
next_action: Complete the exact-head final gate and squash-merge Canary PR #807, then rerun the proven login/oteryn-native-auth harness pinned to Platform 53158217a6c6017230301cf4daa783b04fcc13d5 and the resulting Canary merge SHA.
```
