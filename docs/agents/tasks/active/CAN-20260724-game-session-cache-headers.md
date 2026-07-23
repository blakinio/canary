---
task_id: CAN-20260724-game-session-cache-headers
program_id: CAN-PROGRAM-E2E-PLATFORM
status: implementing
agent: "GPT-5.6 Thinking"
branch: fix/CAN-20260724-game-session-cache-headers
base_branch: main
created: 2026-07-24T00:45:00+02:00
updated: 2026-07-24T00:45:00+02:00
last_verified_commit: 8e114be985089cade84661cb185ca4f750a0597d
risk: medium
related_pr: ""
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260724-game-session-cache-headers.md
    - src/security/game_session_http_issuer.cpp
  shared:
    - tests/unit/security/game_session_http_issuer_test.cpp
modules_touched:
  - Canary private Game Session HTTP issuer
cross_repo_tasks:
  - CAN-20260723-native-auth-ephemeral-cutover-rehearsal
  - OTERYN-20260723-native-auth-ephemeral-cutover-rehearsal
---

# Goal

Bring the private Canary Game Session issuer sensitive-response cache headers into the production-like native-auth cutover acceptance contract by adding `Expires: 0` while preserving `Cache-Control: no-store` and `Pragma: no-cache`.

# Acceptance criteria

- [ ] Every HTTP response emitted by the private Game Session issuer includes `Cache-Control: no-store`, `Pragma: no-cache`, and `Expires: 0`.
- [ ] No authentication/session semantics change.
- [ ] Canary CI remains green.
- [ ] The production-like rehearsal verifies the header at runtime over the private TLS boundary.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T00:45:00+02:00
head: 8e114be985089cade84661cb185ca4f750a0597d
branch: fix/CAN-20260724-game-session-cache-headers
pr: null
status: implementing
context_routes:
  - cpp-runtime
  - universal-e2e
  - security
owned_paths:
  - docs/agents/tasks/active/CAN-20260724-game-session-cache-headers.md
  - src/security/game_session_http_issuer.cpp
  - tests/unit/security/game_session_http_issuer_test.cpp
proven:
  - src/security/game_session_http_issuer.cpp serializes every issuer HTTP response with Cache-Control no-store and Pragma no-cache.
  - The same serializer does not currently emit Expires: 0.
  - Gateway sensitive login responses already emit Cache-Control no-store/no-cache, Pragma no-cache and Expires 0.
derived:
  - Canary issuer cache metadata is the only discovered native-auth runtime response-header mismatch against the requested rehearsal acceptance contract.
unknown:
  - final CI workflow identifiers
conflicts: []
first_failure:
  marker: missing-expires-zero
  evidence: source inspection of GameSessionHttpIssuer serializeResponse
rejected_hypotheses:
  - this can be fixed only in the rehearsal proxy: rejected because the required security header belongs to the real issuer response contract
changed_paths:
  - docs/agents/tasks/active/CAN-20260724-game-session-cache-headers.md
validation: []
blockers:
  - none
next_action: add Expires 0 to the real issuer response serializer and validate with Canary CI plus the production-like runtime rehearsal.
```
