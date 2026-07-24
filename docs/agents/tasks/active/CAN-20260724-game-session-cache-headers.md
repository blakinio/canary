---
task_id: CAN-20260724-game-session-cache-headers
program_id: CAN-PROGRAM-E2E-PLATFORM
status: blocked_external
agent: "GPT-5.6 Thinking"
branch: fix/CAN-20260724-game-session-cache-headers
base_branch: main
created: 2026-07-24T00:45:00+02:00
updated: 2026-07-24T07:30:00+02:00
last_verified_commit: fd1a5a15d90b6c21601545ecd4590225ac0ae18c
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

- [x] Every HTTP response emitted by the private Game Session issuer includes `Cache-Control: no-store`, `Pragma: no-cache`, and `Expires: 0` in source.
- [x] No authentication/session semantics change.
- [ ] Canary CI remains green.
- [ ] The production-like rehearsal verifies the header at runtime over the private TLS boundary.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T07:30:00+02:00
head: fd1a5a15d90b6c21601545ecd4590225ac0ae18c
branch: fix/CAN-20260724-game-session-cache-headers
pr: null
status: blocked_external
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
  - Commit fd1a5a15d90b6c21601545ecd4590225ac0ae18c adds Expires 0 beside Cache-Control no-store and Pragma no-cache in that shared serializer.
  - The source diff changes no authentication, authorization, token, account, world-routing or session-lifetime logic.
derived:
  - Both successful and error issuer responses inherit the cache-header fix because all socket responses use serializeResponse.
unknown:
  - Canary compile/unit/format result while GitHub-hosted jobs are failing before step allocation
  - runtime header result over the private TLS proxy in the full rehearsal
conflicts: []
first_failure:
  marker: github-actions-job-start-gate
  evidence: Oteryn Platform workflows and retries on the same account fail with steps null before runner allocation; source validation cannot currently execute
rejected_hypotheses:
  - fix only the rehearsal proxy: rejected because the security header belongs to the real issuer response contract
  - classify source inspection as runtime proof: rejected because the private TLS boundary still requires an executable rehearsal
changed_paths:
  - docs/agents/tasks/active/CAN-20260724-game-session-cache-headers.md
  - src/security/game_session_http_issuer.cpp
validation:
  - command: GitHub commit diff inspection for fd1a5a15d90b6c21601545ecd4590225ac0ae18c
    result: PASS
    evidence: shared serializer contains Expires 0 and no auth/session logic changes
blockers:
  - GitHub-hosted Actions jobs are currently failing before step 1, so compile, unit, formatter and runtime validation are unavailable.
next_action: execute Canary CI and the Platform-hosted native-auth rehearsal when hosted runners resume; only then mark the task ready.
```
