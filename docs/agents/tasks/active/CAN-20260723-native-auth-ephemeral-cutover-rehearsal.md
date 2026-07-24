---
task_id: CAN-20260723-native-auth-ephemeral-cutover-rehearsal
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-20260721-oteryn-identity-auth
status: implementing
agent: "GPT-5.6 Thinking"
branch: test/CAN-20260723-native-auth-ephemeral-cutover-rehearsal
base_branch: main
created: 2026-07-23T23:00:00+02:00
updated: 2026-07-24T12:25:00+02:00
last_verified_commit: 5b1a01850c6f04fc3c5319dbef40f43535918856
risk: high
related_issue: ""
related_pr: "841"
depends_on:
  - "Oteryn Platform runtime b5dd6a7be5c704d5706241240e06f8bb8c4b5efe"
  - "Game Gateway 53158217a6c6017230301cf4daa783b04fcc13d5"
  - "Canary runtime b15b7d544f4795e3a2a65b88de35391b9fd0a20d"
  - "OTClient bb87346f6c516a19d19497d82bb01fb389334ff5"
  - "Platform rehearsal PR 126"
blocks:
  - "production native-auth activation remains outside this task"
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260723-native-auth-ephemeral-cutover-rehearsal.md
    - .github/workflows/native-auth-ephemeral-cutover-rehearsal.yml
    - tests/e2e/native_auth_ephemeral_cutover/**
  shared: []
  read_only:
    - .github/workflows/universal-agent-e2e.yml
    - tools/e2e/**
    - src/security/game_session_http_issuer.*
modules_touched:
  - Universal OTS E2E validation infrastructure
  - Oteryn native-auth cross-repository production-like validation
reuses:
  - Universal Agent E2E physical native-auth scenario/evidence
  - prior production-like TLS/credential-rotation harness
  - Oteryn Platform Phase 7 production-like MariaDB/Redis provisioning patterns
public_interfaces:
  - retained production-like rehearsal evidence only
cross_repo_tasks:
  - OTERYN-20260723-native-auth-production-cutover
  - CAN-20260723-oteryn-native-auth-production-cutover
---

# Goal

Build and execute one ephemeral production-like native-auth cutover rehearsal that joins real Oteryn Platform, Game Gateway, Canary and OTClient with real MariaDB/Redis dependencies, verified TLS, exact revisions, OAuth Authorization Code + PKCE, Game Login Ticket, Canary Game Session, one physical world entry, logout, replay rejection, credential rotation, failure injection and rollback evidence.

The maximum evidence classification is `PRODUCTION_LIKE_PROVEN`; this task must never claim `PRODUCTION_PROVEN`, deploy production, or use production secrets/data.

# Acceptance criteria

- [x] Exact component revisions and artifact digests are retained by the Platform-hosted runner.
- [x] Real Platform OAuth Authorization Code + PKCE and negative cases execute over HTTPS.
- [x] Real Platform Game Login Ticket issue/redeem executes without a Platform stub.
- [x] Real Gateway obtains a real Canary Game Session through the private TLS boundary.
- [ ] Real OTClient enters the intended character exactly once, safely logs out and rejects replay.
- [x] TLS CA/hostname validation and negative trust cases fail closed without verification bypasses.
- [ ] Current/previous credential overlap, retirement, rollback and re-close complete end to end.
- [x] Private Canary issuer is unreachable from the client segment.
- [x] Dependency outages, malformed Canary responses and unauthorized cases fail closed without extra entries.
- [x] Sensitive response cache headers and request correlation are verified.
- [x] Retained partial evidence contains no detected runtime credentials or private keys.
- [ ] Cutover stages and rollback complete with `PRODUCTION_LIKE_PROVEN` result.
- [x] Production Go-Live Gate remains pending direct production verification.

## Security boundaries

- Trust boundary: OTClient -> Platform public OAuth/ticket API -> Gateway public login -> Platform private redeem/context -> Canary private Game Session issuer -> Canary game protocol.
- The client never chooses the authoritative Canary account; one-time OAuth/code/ticket/session material must fail closed on expiry/replay.
- Validation-only: no production schema migration or production session contract change is introduced.
- Browser diagnostics must never retain OAuth state, code challenge values, credentials, tokens or response bodies.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T12:25:00+02:00
head: 5b1a01850c6f04fc3c5319dbef40f43535918856
branch: test/CAN-20260723-native-auth-ephemeral-cutover-rehearsal
pr: 841
status: validating
context_routes:
  - universal-e2e
  - agent-governance
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260723-native-auth-ephemeral-cutover-rehearsal.md
  - .github/workflows/native-auth-ephemeral-cutover-rehearsal.yml
  - tests/e2e/native_auth_ephemeral_cutover/**
proven:
  - Platform rehearsal run 30084930018 passed all matrix gates through cache headers, correlation, physical random-session rejection, unauthorized-character burn and Canary restart invalidation/recovery.
  - The malformed Gateway helper still received HTTP 400 from Platform /oauth/authorize before the fake Gateway boundary; malformed-gateway-access.log remained empty.
  - Waiting for CharacterList was insufficient, so the invalid authorization request must be diagnosed from the captured URL contract rather than inferred from UI readiness.
  - Commit 5b1a01850c6f04fc3c5319dbef40f43535918856 records only sorted query parameter names, client-id equality, response type, scope presence, PKCE method, state/challenge lengths, redirect URI structure, HTTP status/path/phase and a fixed error classification.
  - The diagnostic does not retain query values, state, code challenge, credentials, tokens, cookies or raw error bodies.
  - Existing access-log proof remains mandatory; timeout-only Lua evidence cannot pass the physical malformed Gateway scenario.
derived:
  - The next Platform-hosted run should identify whether the malformed helper emits an invalid client, redirect URI, PKCE parameter, response type or another request-contract defect.
unknown:
  - sanitized authorization URL metadata for the malformed helper
  - physical malformed Gateway request/access result after the exact request defect is repaired
  - final happy-path world entry, logout, replay, rotation, rollback and final smoke results
conflicts: []
first_failure:
  marker: malformed-gateway-oauth-authorize-400
  evidence: Platform run 30084930018 artifact 8593440828; browser_driver retained failure_HTTPError and fake Gateway access remained empty
rejected_hypotheses:
  - accept the Lua rejection event as physical proof: rejected because the fake Gateway received no login request
  - retain the full authorization URL or HTTP error body: rejected because they may contain OAuth state or other sensitive material
  - classify the 400 as a Platform product defect without request metadata: rejected because all maintained OAuth probes pass on the same exact Platform revision
  - weaken TLS, rate limits or access-log assertions: rejected because those controls remain required
changed_paths:
  - .github/workflows/native-auth-ephemeral-cutover-rehearsal.yml
  - docs/agents/tasks/active/CAN-20260723-native-auth-ephemeral-cutover-rehearsal.md
  - tests/e2e/native_auth_ephemeral_cutover/browser_driver.py
  - tests/e2e/native_auth_ephemeral_cutover/capture-xdg-open.sh
  - tests/e2e/native_auth_ephemeral_cutover/oauth_probe.py
  - tests/e2e/native_auth_ephemeral_cutover/otclient_malformed_gateway_e2e.lua
  - tests/e2e/native_auth_ephemeral_cutover/otclient_native_flow_e2e.lua
  - tests/e2e/native_auth_ephemeral_cutover/platform_bootstrap.php
  - tests/e2e/native_auth_ephemeral_cutover/run_rehearsal.py
validation:
  - command: Platform Native Auth Ephemeral Cutover Rehearsal run 30084930018
    result: FAIL
    evidence: first failure remained the malformed Gateway physical OAuth request before the fake boundary
  - command: Canary browser diagnostic source inspection
    result: PASS
    evidence: only non-secret structural metadata and fixed classifications are retained
blockers:
  - none
next_action: pass Canary CI and ownership, pin the diagnostic harness exact SHA in Platform PR 126, and inspect the retained structural OAuth failure metadata.
```
