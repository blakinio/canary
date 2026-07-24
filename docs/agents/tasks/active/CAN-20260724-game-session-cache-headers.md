---
task_id: CAN-20260724-game-session-cache-headers
program_id: CAN-PROGRAM-E2E-PLATFORM
status: validating
agent: "GPT-5.6 Thinking"
branch: fix/CAN-20260724-game-session-cache-headers
base_branch: main
created: 2026-07-24T00:45:00+02:00
updated: 2026-07-24T10:55:00+02:00
last_verified_commit: b15b7d544f4795e3a2a65b88de35391b9fd0a20d
risk: medium
related_pr: "852"
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260724-game-session-cache-headers.md
  shared:
    - src/security/game_session_http_issuer.cpp
    - tests/unit/security/game_session_http_issuer_test.cpp
modules_touched:
  - Canary private Game Session HTTP issuer
cross_repo_tasks:
  - CAN-20260723-native-auth-ephemeral-cutover-rehearsal
  - OTERYN-20260723-native-auth-ephemeral-cutover-rehearsal
---

# Goal

Bring every response from the private Canary Game Session issuer into the complete sensitive-response cache contract used by Platform and Gateway.

# Acceptance criteria

- [x] Every HTTP response emitted by the private Game Session issuer includes `Cache-Control: no-store, no-cache, must-revalidate, private`, `Pragma: no-cache`, and `Expires: 0` in source.
- [x] Success and error responses share one serializer and therefore one cache policy.
- [x] No authentication, authorization, token, account, world-routing, TTL or session semantics change.
- [x] Canary CI remains green on the complete policy head.
- [ ] The production-like rehearsal verifies the complete policy at runtime over the private TLS boundary.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T10:55:00+02:00
head: b15b7d544f4795e3a2a65b88de35391b9fd0a20d
branch: fix/CAN-20260724-game-session-cache-headers
pr: 852
status: validating
context_routes:
  - cpp-runtime
  - universal-e2e
  - security
owned_paths:
  - docs/agents/tasks/active/CAN-20260724-game-session-cache-headers.md
  - src/security/game_session_http_issuer.cpp
  - tests/unit/security/game_session_http_issuer_test.cpp
proven:
  - src/security/game_session_http_issuer.cpp serializes every issuer HTTP response through one serializeResponse function.
  - Commit fd1a5a15d90b6c21601545ecd4590225ac0ae18c added Expires 0 beside the existing no-store and Pragma headers.
  - Commit c42adcbaf118e6622af362e5a652df57639fd537 completed Cache-Control with no-cache, must-revalidate and private while removing its one-shot source-edit workflow in the same commit.
  - The source diff changes no authentication, authorization, token, account, world-routing or session-lifetime logic.
  - Canary CI run 30080195391 passed on user-authored checkpoint head b15b7d544f4795e3a2a65b88de35391b9fd0a20d, which contains the complete cache policy source.
derived:
  - Both successful and error issuer responses inherit the complete cache policy because every socket response uses serializeResponse.
  - The issuer source is correctly declared shared because the active native-auth programme also coordinates that component.
unknown:
  - runtime header result over the private TLS proxy in the full rehearsal
conflicts: []
first_failure:
  marker: checkpoint-status-enum
  evidence: ownership run 30080195226 rejected unsupported checkpoint status review; supported validating status is now used
rejected_hypotheses:
  - fix only the rehearsal proxy: rejected because the security header belongs to the real issuer response contract
  - classify source inspection or Canary CI as private-TLS runtime proof: rejected because the cross-repository boundary still requires an executable rehearsal
  - retain partial Cache-Control no-store only: rejected because the acceptance contract requires no-store, no-cache, must-revalidate and private
changed_paths:
  - docs/agents/tasks/active/CAN-20260724-game-session-cache-headers.md
  - src/security/game_session_http_issuer.cpp
validation:
  - command: GitHub commit diff inspection for c42adcbaf118e6622af362e5a652df57639fd537
    result: PASS
    evidence: shared serializer has the complete cache policy and the temporary workflow is absent from the resulting tree
  - command: Canary CI run 30080195391
    result: PASS
    evidence: required Canary CI completed successfully on head b15b7d544f4795e3a2a65b88de35391b9fd0a20d
blockers:
  - none
next_action: complete the exact Canary binary build and run the full private-TLS native-auth rehearsal.
```
