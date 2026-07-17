---
task_id: CAN-20260718-security-authenticated-session-transport
program_id: CAN-PROGRAM-SECURITY-VALIDATION
coordination_id: OTS-SEC-005
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/security-authenticated-session-transport
base_branch: main
created: 2026-07-18T00:06:00+02:00
updated: 2026-07-18T00:24:00+02:00
last_verified_commit: "d58c7514ddfe6c26ab8e32675d95257bc8616822"
risk: high
related_issue: ""
related_pr: "514"
depends_on:
  - "OTS-SEC-004 / PR #462"
  - "OTS-SEC-003-RUNTIME-HOOK / PR #444"
blocks:
  - future authenticated session race and replay scenarios
  - future economy and transaction-abuse security scenarios
owned_paths:
  exclusive:
    - tools/security/game_session_runtime.py
    - tools/security/game_session_runtime_runner.py
    - tests/security/test_game_session_runtime.py
    - tests/security/test_game_session_runtime_runner.py
    - tests/security/runtime_scenarios/canary-game-session.json
    - docs/agents/tasks/active/CAN-20260718-security-authenticated-session-transport.md
  shared:
    - .github/workflows/security-validation.yml
    - docs/security/SECURITY_VALIDATION_PLATFORM.md
    - docs/agents/programs/SECURITY_VALIDATION_PROGRAM.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/e2e/run_agent_load_runtime.py
    - .github/scripts/smoke_test_canary.py
    - docker/data/01-test_account.sql
    - docker/data/02-test_account_players.sql
    - src/server/network/protocol/protocolgame.cpp
    - src/server/network/protocol/protocolgame.hpp
    - src/server/network/protocol/protocol.cpp
    - src/server/network/protocol/protocol_profile.cpp
    - src/server/network/protocol/transport_codec.cpp
modules_touched:
  - OTS Security Validation Platform runtime validation
  - Canary authenticated game-session and post-login transport evidence
reuses:
  - tools/e2e/run_agent_load_runtime.py RuntimeContext/run_runtime lifecycle callback
  - existing disposable test-account/player SQL fixtures
  - OTS-SEC-004 public-RSA and deterministic XTEA framing patterns
public_interfaces:
  - ots-security-game-session-plan-v1
  - ots-security-game-session-report-v1
  - canary-game-session-v1 built-in runtime driver
cross_repo_tasks: []
---

# Goal

Deliver one bounded authenticated Canary game-session and post-login transport security pack on disposable literal-loopback infrastructure. Prove successful current-protocol game authentication with the repository-owned disposable test fixture, then exercise fixed code-owned sequence/XTEA rejection cases without accepting arbitrary credentials, packet payloads or network targets from manifests.

# Acceptance criteria

- [x] Start from current `main` after the SEC-004 durable handoff and repeat live PR/path overlap preflight.
- [x] Keep PR #453 independent; do not absorb MyAAC/login-server audit scope.
- [x] Reuse the existing `run_runtime` disposable Canary/MariaDB lifecycle; do not create a second general orchestrator.
- [x] Add a strict versioned plan with exact repository authorization and only code-owned case identifiers.
- [x] Keep account/password/character test fixture selection code-owned and derived only from existing disposable repository fixtures; no manifest credentials.
- [ ] Parse the code-owned current game challenge and complete a real RSA-to-XTEA authenticated game login on literal loopback.
- [ ] Prove session establishment with a valid decryptable non-auth-error post-login server frame before any malformed transport probe.
- [x] Add bounded fixed post-login transport cases covering zero sequence, sequence gap, sequence replay and invalid XTEA padding/decrypt handling.
- [x] Use deterministic distinct loopback source addresses for each case and control session while leaving normal server admission protections enabled.
- [x] Require a fresh successful authenticated control session after every rejection case.
- [x] Fail closed on timeout, malformed challenge, authentication failure, process exit or fatal/sanitizer evidence.
- [x] Emit normalized SHA-256-pinned machine-readable evidence without arbitrary response bodies, credentials or timestamps.
- [ ] Add focused Python tests and exact-head disposable runtime execution in Security Validation CI.
- [ ] Update durable platform/program/catalogue/changelog documentation with explicit evidence boundaries and non-claims.
- [ ] Pass exact-final-head merge gate and squash merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-18T00:24:00+02:00
head: d58c7514ddfe6c26ab8e32675d95257bc8616822
branch: feat/security-authenticated-session-transport
pr: 514
status: implementing
context_routes:
  - agent-governance
  - cpp-runtime
owned_paths:
  - tools/security/game_session_runtime.py
  - tools/security/game_session_runtime_runner.py
  - tests/security/test_game_session_runtime.py
  - tests/security/test_game_session_runtime_runner.py
  - tests/security/runtime_scenarios/canary-game-session.json
  - docs/agents/tasks/active/CAN-20260718-security-authenticated-session-transport.md
  - .github/workflows/security-validation.yml
  - docs/security/SECURITY_VALIDATION_PLATFORM.md
  - docs/agents/programs/SECURITY_VALIDATION_PROGRAM.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - current main at task start was 676add3be5626e5f0dbe1a22783d26f423d8a095 after durable SEC-004 handoff merge PR 513
  - OTS-SEC-005 was not active before this task
  - open PR 453 changes only MyAAC security audit documentation/task paths and remains independent
  - open PRs 511 and 512 own physical E2E scenario/task paths; this task keeps generic E2E lifecycle files read-only
  - open PR 509 is OAM character-progression documentation and does not overlap this task
  - open PRs 485 and 487 are Windows build/test fixes and do not overlap this task
  - run_agent_load_runtime initializes schema plus repository-owned disposable test account/player fixtures before starting exact-head Canary
  - current ProtocolGame uses server challenge before login, sequence transport, RSA first-message handoff and XTEA after first-message acceptance
  - current game-login layout uses session-key wire shape, challenge response and current protocol version 1525
  - default password-auth compatibility splits the session-key field at newline before IOLoginData game-world authentication
  - rejected post-login transport frames return false without advancing accepted sequence and the connection loop reads the next packet
  - strict game-session plan contains only code-owned case identifiers and repository authorization
  - disposable account/password/character values remain code-owned and are not accepted from the plan
  - fixed case logic covers authenticated control zero sequence sequence gap sequence replay and invalid XTEA padding with same-session recovery
  - every case is followed by a distinct-source distinct-fixture authenticated control session
  - CI run 29617554553 passed on head d58c7514ddfe6c26ab8e32675d95257bc8616822
  - no external/public target is authorized by this task
derived:
  - direct game-port authentication can exercise the current protocol without depending on MyAAC or external login-server behavior
  - same-session recovery with the still-expected sequence directly tests that rejected transport input did not consume accepted sequence state
unknown:
  - real exact-head authenticated game-login outcome until the new runtime job is wired and executed
  - exact first successful post-login server opcode/compression shape until real runtime evidence exists
  - current Security Validation outcome for focused tests on head d58c7514ddfe6c26ab8e32675d95257bc8616822
conflicts: []
first_failure:
  marker: ownership-related-pr
  evidence: Agent Task Ownership run 29617554455 rejected changed active task because related_pr was empty instead of current PR 514; task metadata and checkpoint were corrected
rejected_hypotheses:
  - adding arbitrary packet bytes or credentials to scenario JSON
  - creating a second disposable server/database orchestrator
  - modifying maintained OTClient or external repositories for SEC-005
  - treating SEC-004 encrypted negative-auth responses as proof of a game session
  - treating process liveness alone as proof that rejected post-login sequence state recovered
changed_paths:
  - docs/agents/tasks/active/CAN-20260718-security-authenticated-session-transport.md
  - tests/security/runtime_scenarios/canary-game-session.json
  - tests/security/test_game_session_runtime.py
  - tests/security/test_game_session_runtime_runner.py
  - tools/security/game_session_runtime.py
  - tools/security/game_session_runtime_runner.py
validation:
  - command: live repository/PR/path overlap preflight
    result: PASS
    evidence: no active SEC-005 before task creation; open PR scopes inspected and no exclusive-path overlap found
  - command: local isolated Python py_compile and XTEA/frame sanity checks
    result: PASS
    evidence: core and runner compiled; XTEA encrypt/decrypt round-tripped 8 16 and 24 byte fixtures; login and post-login frame lengths matched current transport block semantics
  - command: CI run 29617554553
    result: PASS
    evidence: repository CI passed on implementation head d58c7514ddfe6c26ab8e32675d95257bc8616822
  - command: Agent Task Ownership run 29617554455
    result: FAIL
    evidence: changed active task related_pr did not match PR 514; metadata corrected in the next commit
blockers: []
next_action: Verify corrected Agent Task Ownership and focused Security Validation on the new head, repair any focused test failures, then wire the authenticated game-session runtime job into Security Validation.
```
