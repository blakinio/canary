---
task_id: CAN-20260723-native-auth-ephemeral-cutover-rehearsal
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-20260721-oteryn-identity-auth
status: implementing
agent: "GPT-5.6 Thinking"
branch: test/CAN-20260723-native-auth-ephemeral-cutover-rehearsal
base_branch: main
created: 2026-07-23T23:00:00+02:00
updated: 2026-07-24T12:05:00+02:00
last_verified_commit: fdab1a6b7e4fe8275f12c19812194fbc2ee01c2c
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
- Only ephemeral generated credentials are used and retained evidence is scanned.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T12:05:00+02:00
head: fdab1a6b7e4fe8275f12c19812194fbc2ee01c2c
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
  - Platform rehearsal run 30083664968 passed OAuth PKCE, real authorization-code expiry, ticket and service credential checks, outage recovery, cache headers, correlation, physical random-session rejection, unauthorized-character burn and Canary restart invalidation/recovery.
  - The same run retained malformed-gateway-client-events.tsv with malformed_gateway_response rejected, successful_world_entries 0 and e2e success.
  - The static malformed Gateway access log was empty and browser_driver recorded failure_HTTPError; Platform logged GET /oauth/authorize status 400 before the ticket could reach the fake Gateway boundary.
  - The malformed Gateway helper was the only native OAuth helper that did not wait for CharacterList before starting OterynIdentity.
  - Commit fdab1a6b7e4fe8275f12c19812194fbc2ee01c2c aligns its readiness predicate with the maintained happy-path helper by requiring CharacterList.
  - No Platform, Gateway, Canary runtime or OTClient binary source was changed by this harness correction.
derived:
  - The previous apparent malformed-response rejection was observation-only because the OTClient never reached the malformed Gateway; access-log proof remains mandatory.
  - Waiting for the complete native-auth UI stack should allow the browser flow to obtain a real ticket and exercise malformed Gateway parsing physically.
unknown:
  - physical malformed Gateway request/access result after complete UI readiness
  - final happy-path world entry, logout, replay, rotation, rollback and final smoke results
conflicts: []
first_failure:
  marker: malformed-gateway-native-ui-readiness
  evidence: Platform run 30083664968 artifact 8592956146; OAuth authorize returned 400, browser driver failed, and malformed Gateway access log remained empty
rejected_hypotheses:
  - accept the Lua timeout observation as physical malformed Gateway proof: rejected because the fake Gateway saw no POST /v1/login
  - weaken the access-log requirement: rejected because the real OTClient must cross the malformed boundary
  - classify the Platform 400 as an OAuth product defect: rejected because all maintained OAuth probes and previous physical flows passed on the same exact Platform revision
  - change production rate limits or TLS verification: rejected because both controls are functioning and remain required
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
  - command: Platform Native Auth Ephemeral Cutover Rehearsal run 30083664968
    result: FAIL
    evidence: complete matrix through physical negative Game Session and Canary restart checks passed; first failure was malformed Gateway helper readiness before the fake boundary
  - command: Canary CI run 30084397393
    result: PASS
    evidence: required CI passed for the helper change
blockers:
  - none
next_action: pass ownership on this checkpoint head, pin the exact harness revision in Platform PR 126, and rerun the full rehearsal.
```
