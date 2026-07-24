---
task_id: CAN-20260723-native-auth-ephemeral-cutover-rehearsal
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-20260721-oteryn-identity-auth
status: ready
agent: "GPT-5.6 Thinking"
branch: test/CAN-20260723-native-auth-ephemeral-cutover-rehearsal
base_branch: main
created: 2026-07-23T23:00:00+02:00
updated: 2026-07-24T17:59:00+02:00
last_verified_commit: f46ae126557d4d26043c77fe17968b72fd5bc688
risk: high
related_issue: ""
related_pr: "841"
depends_on:
  - "Oteryn Platform runtime b5dd6a7be5c704d5706241240e06f8bb8c4b5efe"
  - "Game Gateway 53158217a6c6017230301cf4daa783b04fcc13d5"
  - "Canary runtime b15b7d544f4795e3a2a65b88de35391b9fd0a20d"
  - "OTClient implementation 9189d1063e968a0c2ffab11c5069db192e753397"
  - "Platform rehearsal merge b520cf78ac1b488a289b156b492539b2a047f299"
blocks:
  - "production native-auth activation remains outside this task"
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260723-native-auth-ephemeral-cutover-rehearsal.md
    - .github/workflows/native-auth-ephemeral-cutover-rehearsal.yml
    - tests/e2e/native_auth_ephemeral_cutover/browser_driver.py
    - tests/e2e/native_auth_ephemeral_cutover/capture-xdg-open.sh
    - tests/e2e/native_auth_ephemeral_cutover/oauth_probe.py
    - tests/e2e/native_auth_ephemeral_cutover/otclient_malformed_gateway_e2e.lua
    - tests/e2e/native_auth_ephemeral_cutover/otclient_native_flow_e2e.lua
    - tests/e2e/native_auth_ephemeral_cutover/otclient_session_negative_e2e.lua
    - tests/e2e/native_auth_ephemeral_cutover/platform_bootstrap.php
    - tests/e2e/native_auth_ephemeral_cutover/run_rehearsal.py
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
- [x] Real OTClient enters the intended character exactly once, safely logs out and rejects replay.
- [x] TLS CA/hostname validation and negative trust cases fail closed without verification bypasses.
- [x] Current/previous credential overlap, retirement, rollback and re-close complete end to end.
- [x] Private Canary issuer is unreachable from the client segment.
- [x] Dependency outages, malformed Canary responses and unauthorized cases fail closed without extra entries.
- [x] Sensitive response cache headers and request correlation are verified.
- [x] Retained evidence contains no detected runtime credentials or private keys.
- [x] Cutover stages and rollback complete with `PRODUCTION_LIKE_PROVEN` result.
- [x] Production Go-Live Gate remains pending direct production verification.

## Security boundaries

- Trust boundary: OTClient -> Platform public OAuth/ticket API -> Gateway public login -> Platform private redeem/context -> Canary private Game Session issuer -> Canary game protocol.
- The client never chooses the authoritative Canary account; one-time OAuth/code/ticket/session material must fail closed on expiry/replay.
- Validation-only: no production schema migration or production session contract change is introduced.
- Browser diagnostics never retain OAuth state, code challenge values, credentials, tokens or response bodies.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T17:59:00+02:00
head: 79a17470babd1386e5ebd864d46b44ce19091020
branch: test/CAN-20260723-native-auth-ephemeral-cutover-rehearsal
pr: 841
status: ready
context_routes:
  - universal-e2e
  - agent-governance
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260723-native-auth-ephemeral-cutover-rehearsal.md
  - .github/workflows/native-auth-ephemeral-cutover-rehearsal.yml
  - tests/e2e/native_auth_ephemeral_cutover/browser_driver.py
  - tests/e2e/native_auth_ephemeral_cutover/capture-xdg-open.sh
  - tests/e2e/native_auth_ephemeral_cutover/oauth_probe.py
  - tests/e2e/native_auth_ephemeral_cutover/otclient_malformed_gateway_e2e.lua
  - tests/e2e/native_auth_ephemeral_cutover/otclient_native_flow_e2e.lua
  - tests/e2e/native_auth_ephemeral_cutover/otclient_session_negative_e2e.lua
  - tests/e2e/native_auth_ephemeral_cutover/platform_bootstrap.php
  - tests/e2e/native_auth_ephemeral_cutover/run_rehearsal.py
proven:
  - The harness records only sanitized structural OAuth metadata and fixed classifications; it does not retain state, code challenges, credentials, tokens, cookies or raw error bodies.
  - OTClient source 9189d1063e968a0c2ffab11c5069db192e753397 launches Unix URLs through argv and produced Linux artifact 8595332324 with archive digest sha256:396e0e1fed38c14f43c88cba4e578997ecbd56c2f211ee8b398c712a10c44850.
  - Canary harness f46ae126557d4d26043c77fe17968b72fd5bc688 selects the exact authorized Knight 1 widget before CharacterList.doLogin and includes physical malformed-Gateway fail-closed coverage.
  - Platform rehearsal run 30095854266 completed successfully using the exact Canary harness and runtime pins.
  - Retained artifact 8597730728 has digest sha256:e7e908e9129658654054a96adf641757edc2c904fc2b01a5b9fc97e393d18009 and classification PRODUCTION_LIKE_PROVEN.
  - Retained evidence records one Knight 1 world entry, nonzero lastlogin and lastlogout, zero players_online, safe logout and replay rejection.
  - OAuth verifier rejection, code reuse rejection, scope enforcement, ticket replay rejection, malformed responses, unauthorized character use and dependency outage cases fail closed.
  - TLS certificate and hostname verification, private issuer segmentation, current and previous credential overlap, retirement, rollback, re-close and final smoke all passed.
  - OAuth token and Canary Game Session success and error responses carried the complete sensitive no-cache policy, and request correlation was verified.
derived:
  - The cross-repository production-like native-auth acceptance gate is green without making a production deployment claim.
unknown: []
conflicts: []
first_failure:
  marker: none
  evidence: All required production-like stages passed in Platform run 30095854266.
rejected_hypotheses:
  - accept a Lua rejection event without fake-Gateway access proof: rejected because the physical malformed scenario requires boundary evidence.
  - retain full authorization URLs or HTTP error bodies: rejected because they may contain sensitive OAuth material.
  - disable TLS, rate limits or access-log assertions: rejected because those controls remain required.
  - infer the logged-in character from implicit widget focus: rejected because exact Knight 1 selection is required.
changed_paths:
  - .github/workflows/native-auth-ephemeral-cutover-rehearsal.yml
  - docs/agents/tasks/active/CAN-20260723-native-auth-ephemeral-cutover-rehearsal.md
  - tests/e2e/native_auth_ephemeral_cutover/browser_driver.py
  - tests/e2e/native_auth_ephemeral_cutover/capture-xdg-open.sh
  - tests/e2e/native_auth_ephemeral_cutover/oauth_probe.py
  - tests/e2e/native_auth_ephemeral_cutover/otclient_malformed_gateway_e2e.lua
  - tests/e2e/native_auth_ephemeral_cutover/otclient_native_flow_e2e.lua
  - tests/e2e/native_auth_ephemeral_cutover/otclient_session_negative_e2e.lua
  - tests/e2e/native_auth_ephemeral_cutover/platform_bootstrap.php
  - tests/e2e/native_auth_ephemeral_cutover/run_rehearsal.py
validation:
  - command: Platform Native Auth Ephemeral Cutover Rehearsal run 30084930018
    result: FAIL
    evidence: The malformed Gateway physical OAuth request failed before the fake boundary, leading to the shell-safe URL diagnosis.
  - command: Canary CI run 30095688030
    result: PASS
    evidence: Canary CI passed on harness head f46ae126557d4d26043c77fe17968b72fd5bc688.
  - command: Canary Agent Task Ownership run 30095687494
    result: PASS
    evidence: Task ownership validation passed on harness head f46ae126557d4d26043c77fe17968b72fd5bc688.
  - command: Canary Universal Agent E2E run 30095687917
    result: PASS
    evidence: Universal Agent E2E passed on harness head f46ae126557d4d26043c77fe17968b72fd5bc688.
  - command: Platform Native Auth Ephemeral Cutover Rehearsal run 30095854266
    result: PASS
    evidence: Full OAuth PKCE, ticket, Gateway, Game Session, physical world entry, logout, replay, rotation, failure injection, rollback and final smoke completed.
  - command: Retained evidence artifact 8597730728
    result: PASS
    evidence: PRODUCTION_LIKE_PROVEN with digest sha256:e7e908e9129658654054a96adf641757edc2c904fc2b01a5b9fc97e393d18009.
blockers: []
next_action: Pass exact-head Agent Task Ownership, CI, Universal Agent E2E and retained-proof gate, then mark PR 841 ready and squash-merge.
```
