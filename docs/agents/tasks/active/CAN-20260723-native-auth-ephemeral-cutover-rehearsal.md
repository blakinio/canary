---
task_id: CAN-20260723-native-auth-ephemeral-cutover-rehearsal
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-20260721-oteryn-identity-auth
status: implementing
agent: "GPT-5.6 Thinking"
branch: test/CAN-20260723-native-auth-ephemeral-cutover-rehearsal
base_branch: main
created: 2026-07-23T23:00:00+02:00
updated: 2026-07-23T23:35:00+02:00
last_verified_commit: 457c48bb81f2bbc0bdf69bce46541015ab316124
risk: high
related_issue: ""
related_pr: "841"
depends_on:
  - "Oteryn Platform native-auth hardening 53158217a6c6017230301cf4daa783b04fcc13d5"
  - "Canary Game Session credential-rotation implementation 981c82f5ebb6bc22c867312c2b274a71f6aeeb3e"
  - "OTClient native-auth implementation bb87346f6c516a19d19497d82bb01fb389334ff5"
  - "Hardened physical E2E run 30021347231"
  - "Production-like TLS/rotation run 30025787404"
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

Build and execute one ephemeral production-like native-auth cutover rehearsal in GitHub Actions that joins real Oteryn Platform, real Game Gateway, real Canary and real OTClient with real MariaDB/Redis dependencies, verified TLS, exact revision pins, OAuth Authorization Code + PKCE, Game Login Ticket, Canary Game Session, one physical world entry, logout, replay rejection, credential rotation, fail-closed failure injection and rollback evidence.

The maximum evidence classification is `PRODUCTION_LIKE_PROVEN`; this task must never claim `PRODUCTION_PROVEN` and must not perform a production deployment or use production secrets/data.

# Acceptance criteria

- [ ] Exact component revisions and artifact digests are retained for Platform, Gateway, Canary and OTClient.
- [ ] Real Platform OAuth Authorization Code + PKCE executes over HTTP(S), including required negative cases.
- [ ] Real Platform Game Login Ticket issue/redeem path executes without a Platform stub.
- [ ] Real Gateway obtains a real Canary Game Session through a private/TLS boundary.
- [ ] Real OTClient enters the intended character exactly once, safely logs out and replay of the same Game Session fails closed.
- [ ] TLS CA/hostname validation and negative trust cases fail closed without insecure verification bypasses.
- [ ] Current/previous service credential overlap, retirement, wrong credential, rollback and re-close are proven on applicable boundaries.
- [ ] Private Canary issuer is unreachable from the client segment.
- [ ] Dependency outages and malformed/unauthorized cases fail closed without extra world entries.
- [ ] Sensitive response cache headers are verified.
- [ ] Retained evidence is scanned and contains no raw OAuth/Game Login Ticket/Game Session/service credentials, passwords, TOTP secrets, private keys or credential-bearing connection strings.
- [ ] Cutover stages 1-8 and rollback are represented and machine-readable.
- [ ] `result.json` reports classification `PRODUCTION_LIKE_PROVEN` only when every required gate passes.
- [ ] Production Go-Live Gate remains pending direct production verification.

## Security boundaries

- Trust boundary: OTClient -> Platform public OAuth/ticket API -> Gateway public login -> Platform private redeem/context -> Canary private Game Session issuer -> Canary game protocol.
- Authentication/authorization invariant: the client never chooses the authoritative Canary account; one-time OAuth/code/ticket/session material must fail closed on expiry/replay and service credentials must be independently rotatable.
- Schema/session compatibility: validation-only; no production schema migration or production session contract change is introduced.
- Rollback: required and exercised by disabling native issuer/routing while preserving legacy auth code paths.
- Secrets: only ephemeral generated credentials are used at runtime; no production secret is required or retained.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T23:35:00+02:00
head: 457c48bb81f2bbc0bdf69bce46541015ab316124
branch: test/CAN-20260723-native-auth-ephemeral-cutover-rehearsal
pr: 841
status: implementing
context_routes:
  - universal-e2e
  - agent-governance
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260723-native-auth-ephemeral-cutover-rehearsal.md
  - .github/workflows/native-auth-ephemeral-cutover-rehearsal.yml
  - tests/e2e/native_auth_ephemeral_cutover/**
proven:
  - Canary main preflight SHA is 0a2ae8e3d504ab2398395820512cd45f3b169722.
  - Oteryn Platform main/native-auth hardening SHA is 53158217a6c6017230301cf4daa783b04fcc13d5.
  - OTClient main has advanced to 1e5305395159142634f182d9e888e5f9164228c6 and its only commit after native-auth bb87346f6c516a19d19497d82bb01fb389334ff5 changes task documentation, not runtime code.
  - Canary credential-rotation/native-auth implementation is pinned at 981c82f5ebb6bc22c867312c2b274a71f6aeeb3e for this rehearsal; later main changes do not touch its native-auth issuer implementation.
  - Hardened physical E2E run 30021347231 used real Gateway/Canary/OTClient but a local Platform upstream stub.
  - Production-like run 30025787404 proved TLS/hostname and credential-rotation boundary behavior but did not join the full OAuth/Platform/OTClient world-entry flow.
  - Draft PR 841 owns only the new rehearsal workflow, harness directory and this task record.
  - Agent Task Ownership run 30046454857 first failed because this checkpoint omitted mandatory blockers and rejected_hypotheses fields.
derived:
  - The new rehearsal must compose existing evidence/harnesses rather than treat either historical run as sufficient.
  - Canary is the orchestration owner because the maintained physical OTClient/Universal Agent E2E driver lives here.
unknown:
  - final outcome of Native Auth Ephemeral Cutover Rehearsal run 30046454944
  - final workflow job and evidence artifact identifiers
conflicts:
  - docs/agents/PROJECT_STATE.md in Oteryn Platform predates the native-auth commits and still describes the authoritative game-login bridge as unimplemented; current native-auth code supersedes that stale repository-capability statement, not the production activation gate.
first_failure:
  marker: changed active task checkpoint validation
  evidence: Agent Task Ownership run 30046454857 job 89338626717; artifact 8579302455 reports missing blockers and rejected_hypotheses
rejected_hypotheses:
  - product or native-auth runtime defect caused the first CI failure: disproven because the failing job stopped at deterministic task checkpoint validation before runtime execution
changed_paths:
  - .github/workflows/native-auth-ephemeral-cutover-rehearsal.yml
  - docs/agents/tasks/active/CAN-20260723-native-auth-ephemeral-cutover-rehearsal.md
  - tests/e2e/native_auth_ephemeral_cutover/browser_driver.py
  - tests/e2e/native_auth_ephemeral_cutover/capture-xdg-open.sh
  - tests/e2e/native_auth_ephemeral_cutover/oauth_probe.py
  - tests/e2e/native_auth_ephemeral_cutover/otclient_native_flow_e2e.lua
  - tests/e2e/native_auth_ephemeral_cutover/platform_bootstrap.php
  - tests/e2e/native_auth_ephemeral_cutover/run_rehearsal.py
validation:
  - command: Agent Task Ownership run 30046454857 / job 89338626717
    result: FAIL
    evidence: artifact 8579302455; checkpoint omitted blockers and rejected_hypotheses, repaired in this update
  - command: Native Auth Ephemeral Cutover Rehearsal run 30046454944
    result: NOT_RUN
    evidence: workflow still in progress at last verification
blockers:
  - none
next_action: inspect run 30046454944 to identify the first runtime or harness failure and repair only that root cause on PR 841.
```
