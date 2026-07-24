---
task_id: CAN-20260724-game-session-cache-headers
program_id: CAN-PROGRAM-E2E-PLATFORM
status: ready
agent: "GPT-5.6 Thinking"
branch: fix/CAN-20260724-game-session-cache-headers
base_branch: main
created: 2026-07-24T00:45:00+02:00
updated: 2026-07-24T17:42:00+02:00
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
- [x] The production-like rehearsal verifies the complete policy at runtime over the private TLS boundary.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T17:42:00+02:00
head: 4953f04117b635f7ea1f1185f52844995273b76d
branch: fix/CAN-20260724-game-session-cache-headers
pr: 852
status: ready
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
  - Canary CI run 30080469762 and Agent Task Ownership run 30080469519 passed on final pre-rehearsal head 4953f04117b635f7ea1f1185f52844995273b76d.
  - Production-like rehearsal run 30095854266 verified the complete cache policy on successful and error responses over the private TLS boundary using exact Canary source b15b7d544f4795e3a2a65b88de35391b9fd0a20d.
  - Retained rehearsal artifact 8597730728 has digest sha256:e7e908e9129658654054a96adf641757edc2c904fc2b01a5b9fc97e393d18009 and classification PRODUCTION_LIKE_PROVEN.
derived:
  - Both successful and error issuer responses inherit the complete cache policy because every socket response uses serializeResponse.
unknown: []
conflicts: []
first_failure:
  marker: none
  evidence: Source validation, Canary CI and the full private-TLS production-like rehearsal passed.
rejected_hypotheses:
  - fix only the rehearsal proxy: rejected because the security header belongs to the real issuer response contract.
  - classify source inspection or Canary CI as private-TLS runtime proof: rejected because the boundary required an executable rehearsal.
  - retain partial Cache-Control no-store only: rejected because the acceptance contract requires no-store, no-cache, must-revalidate and private.
changed_paths:
  - docs/agents/tasks/active/CAN-20260724-game-session-cache-headers.md
  - src/security/game_session_http_issuer.cpp
validation:
  - command: GitHub commit diff inspection for c42adcbaf118e6622af362e5a652df57639fd537
    result: PASS
    evidence: Shared serializer has the complete cache policy and the temporary workflow is absent from the resulting tree.
  - command: Canary CI run 30080469762
    result: PASS
    evidence: Required Canary CI completed successfully on the final pre-rehearsal head.
  - command: Agent Task Ownership run 30080469519
    result: PASS
    evidence: Task ownership validation completed successfully.
  - command: Platform Native Auth Ephemeral Cutover Rehearsal run 30095854266
    result: PASS
    evidence: Complete successful and error response cache headers were verified over the private TLS boundary.
blockers: []
next_action: Integrate current main without changing the proven issuer behavior, pass the ci:final-gate checks, mark PR 852 ready, and squash-merge.
```
