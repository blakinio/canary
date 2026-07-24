---
task_id: CAN-20260724-game-session-cache-headers
program_id: CAN-PROGRAM-E2E-PLATFORM
status: blocked
agent: "GPT-5.6 Thinking"
branch: fix/CAN-20260724-game-session-cache-headers
base_branch: main
created: 2026-07-24T00:45:00+02:00
updated: 2026-07-24T07:35:00+02:00
last_verified_commit: fd1a5a15d90b6c21601545ecd4590225ac0ae18c
risk: medium
related_pr: "852"
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
- [x] Canary CI remains green.
- [ ] The production-like rehearsal verifies the header at runtime over the private TLS boundary.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T07:35:00+02:00
head: 40004ca772a149d7f35767282eac61ec4715e5f7
branch: fix/CAN-20260724-game-session-cache-headers
pr: 852
status: blocked
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
  - Canary CI run 30069523624 completed successfully for PR 852 head 40004ca772a149d7f35767282eac61ec4715e5f7.
derived:
  - Both successful and error issuer responses inherit the cache-header fix because all socket responses use serializeResponse.
unknown:
  - runtime header result over the private TLS proxy in the full rehearsal
conflicts: []
first_failure:
  marker: platform-actions-job-start-gate
  evidence: Oteryn Platform workflows and retries fail with steps null before runner allocation; the cross-repository runtime validation cannot currently execute
rejected_hypotheses:
  - fix only the rehearsal proxy: rejected because the security header belongs to the real issuer response contract
  - classify source inspection or Canary CI as private-TLS runtime proof: rejected because the cross-repository boundary still requires an executable rehearsal
changed_paths:
  - docs/agents/tasks/active/CAN-20260724-game-session-cache-headers.md
  - src/security/game_session_http_issuer.cpp
validation:
  - command: GitHub commit diff inspection for fd1a5a15d90b6c21601545ecd4590225ac0ae18c
    result: PASS
    evidence: shared serializer contains Expires 0 and no auth/session logic changes
  - command: Canary CI run 30069523624
    result: PASS
    evidence: repository CI completed successfully on PR 852 head 40004ca772a149d7f35767282eac61ec4715e5f7
blockers:
  - Platform private-repository GitHub-hosted jobs are failing before step 1, so the full private-TLS runtime rehearsal is unavailable.
next_action: execute the Platform-hosted native-auth rehearsal when private-repository hosted runners resume; verify Expires 0 over the real private TLS proxy, then mark the task ready.
```
