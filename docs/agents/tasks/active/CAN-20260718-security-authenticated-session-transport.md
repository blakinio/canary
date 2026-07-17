---
task_id: CAN-20260718-security-authenticated-session-transport
program_id: CAN-PROGRAM-SECURITY-VALIDATION
coordination_id: OTS-SEC-005
status: review
agent: "GPT-5.5 Thinking"
branch: feat/security-authenticated-session-transport
base_branch: main
created: 2026-07-18T00:06:00+02:00
updated: 2026-07-18T01:19:00+02:00
last_verified_commit: "23a2d437866a99f921aa8462f84805e0143ba513"
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
    - docs/security/SECURITY_VALIDATION_SEC005.md
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

Deliver one bounded authenticated Canary game-session and post-login transport security pack on disposable literal-loopback infrastructure. Prove successful current-protocol game authentication with repository-owned disposable fixtures, then exercise fixed code-owned sequence/XTEA rejection cases without accepting arbitrary credentials, packet payloads or network targets from manifests.

# Acceptance criteria

- [x] Start from current `main` after the SEC-004 durable handoff and repeat live PR/path overlap preflight.
- [x] Keep PR #453 independent; do not absorb MyAAC/login-server audit scope.
- [x] Reuse the existing `run_runtime` disposable Canary/MariaDB lifecycle; do not create a second general orchestrator.
- [x] Add a strict versioned plan with exact repository authorization and only code-owned case identifiers.
- [x] Keep account/password/character test fixture selection code-owned and derived only from existing disposable repository fixtures; no manifest credentials.
- [x] Parse the code-owned current game challenge and complete a real current-client-compatible first-game RSA-to-XTEA authenticated login on literal loopback.
- [x] Prove session establishment with a valid decryptable non-auth-error post-login server frame plus a valid sequence-1 client exchange before malformed transport probes.
- [x] Add bounded fixed post-login transport cases covering zero sequence, sequence gap, sequence replay and invalid XTEA padding/decrypt handling.
- [x] Use deterministic distinct loopback source addresses for each case and control session while leaving normal server admission protections enabled.
- [x] Require same-session recovery with the expected accepted sequence and a fresh successful authenticated control session after every registered case.
- [x] Fail closed on timeout, malformed challenge, authentication failure, failed recovery/control, process exit or fatal/sanitizer evidence.
- [x] Emit normalized SHA-256-pinned machine-readable evidence without arbitrary response bodies, credentials or timestamps.
- [x] Add focused Python tests and exact-head disposable runtime execution in Security Validation CI.
- [x] Update durable program/catalogue/changelog documentation and add the bounded `docs/security/SECURITY_VALIDATION_SEC005.md` platform addendum with explicit evidence boundaries and non-claims.
- [ ] Pass exact-final-head merge gate and squash merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-18T01:19:00+02:00
head: 23a2d437866a99f921aa8462f84805e0143ba513
branch: feat/security-authenticated-session-transport
pr: 514
status: ready
context_routes:
  - agent-governance
  - cpp-runtime
owned_paths:
  - .github/workflows/security-validation.yml
  - docs/agents/CHANGELOG.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/programs/SECURITY_VALIDATION_PROGRAM.md
  - docs/agents/tasks/active/CAN-20260718-security-authenticated-session-transport.md
  - docs/security/SECURITY_VALIDATION_SEC005.md
  - tests/security/runtime_scenarios/canary-game-session.json
  - tests/security/test_game_session_runtime.py
  - tests/security/test_game_session_runtime_runner.py
  - tools/security/game_session_runtime.py
  - tools/security/game_session_runtime_runner.py
proven:
  - current main at task start was 676add3be5626e5f0dbe1a22783d26f423d8a095 after durable SEC-004 handoff merge PR 513
  - OTS-SEC-005 was not active before this task and live open-PR/path preflight found no exclusive-path overlap
  - PR 453 changes only MyAAC audit documentation/task paths and remains independent
  - generic E2E lifecycle code remains read-only and run_agent_load_runtime supplies the reused disposable database/config/map/server lifecycle
  - current ProtocolGame uses a server challenge then a pre-XTEA first-game packet and enables XTEA/sequenced transport only after first-message acceptance
  - maintained OTClient source and Canary transport source prove the current first game packet uses modern padding plus ClientPendingGame and Adler32 before RSA handoff; the first post-login client sequence is one
  - strict game-session plan contains only repository authorization and five code-owned case identifiers; credentials packet bytes key material commands and network coordinates are not manifest inputs
  - disposable account password and character values remain code-owned and are not emitted as passwords in reports
  - fixed cases cover authenticated control zero sequence sequence gap sequence replay and invalid XTEA padding
  - each negative case requires same-session recovery with the expected accepted sequence and each registered case is followed by a distinct-source distinct-fixture fresh authenticated control session
  - corrected Agent Task Ownership run 29618885740 passed on implementation head c45050f81ce4b2f337b4573df60384627affd8fc
  - repository CI run 29618885853 passed on implementation head c45050f81ce4b2f337b4573df60384627affd8fc
  - Security Validation run 29618885799 passed focused tests exact-head Linux release build SEC-003 malformed-status runtime SEC-004 login-parser runtime and SEC-005 authenticated game-session runtime on implementation head c45050f81ce4b2f337b4573df60384627affd8fc
  - SEC-005 artifact 8421679031 reported status success failure null five case probes pass five fresh control probes pass and no fatal or sanitizer findings
  - server-side transport diagnostics explicitly recorded zero-sequence sequence-mismatch for gap sequence-mismatch for replay and decrypt-failure for invalid padding 255 greater than 8 before expected-sequence recovery succeeded
  - durable SEC-005 evidence is recorded in SECURITY_VALIDATION_PROGRAM.md SECURITY_VALIDATION_SEC005.md MODULE_CATALOG.md and CHANGELOG.md
  - docs head 23a2d437866a99f921aa8462f84805e0143ba513 passed repository CI run 29620170020 and Agent Task Ownership run 29620169895
  - PR 514 changed-file review contains exactly eleven intended SEC-005 paths and no map binary asset production configuration or unrelated source path
  - relative to current main before final checkpoint CHANGELOG differs by exactly one SEC-005 addition MODULE_CATALOG by three additions and three deletions and SECURITY_VALIDATION_PROGRAM by twenty-one additions and eleven deletions
  - current main before final checkpoint was 354abbbeeff7f7c3470987b32e873527fc6e1a2f and the two main-only commits since task start add only physical floor-change E2E archive/scenario files with no SEC-005 path overlap
  - PR 514 remained mergeable despite being two independent non-overlapping commits behind current main
  - ci:final-gate label was applied before this final readiness checkpoint commit
  - no external or public target is authorized by this task
derived:
  - direct game-port authentication exercises the current protocol without depending on MyAAC or external login-server behavior
  - same-session recovery with the still-expected sequence proves the tested rejected frame did not consume accepted client sequence state for the registered cases
  - the non-overlapping main advancement does not require rewriting SEC-005 history while PR 514 remains mergeable; exact-final-head checks still remain mandatory before merge
unknown:
  - exact-final-head CI Agent Task Ownership and Security Validation results for this readiness checkpoint commit
  - whether main will advance again before merge; mergeability and overlap must be rechecked immediately before squash merge
conflicts: []
first_failure:
  marker: ownership-related-pr
  evidence: Agent Task Ownership run 29617554455 rejected the first changed active task because related_pr was empty instead of PR 514; task metadata was corrected and later ownership runs passed
rejected_hypotheses:
  - adding arbitrary packet bytes credentials commands or network targets to scenario JSON
  - creating a second disposable server database orchestrator
  - modifying maintained OTClient or external repositories for SEC-005
  - treating SEC-004 encrypted negative-auth responses as proof of successful game authentication
  - treating process liveness alone as proof that rejected post-login sequence state recovered
  - treating the current game first packet as a sequenced XTEA frame; the first real runtime failure plus maintained-client/server source proved the pre-XTEA Adler32 envelope
  - accepting the first SEC-005 runtime failure as transient; artifact and server logs were inspected and the wire-format root cause was fixed
  - forcing a whole-file rewrite of SECURITY_VALIDATION_PLATFORM.md after the connector safety layer blocked that documentation mutation; the existing platform document was preserved and a bounded SEC-005 addendum was added instead
changed_paths:
  - .github/workflows/security-validation.yml
  - docs/agents/CHANGELOG.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/programs/SECURITY_VALIDATION_PROGRAM.md
  - docs/agents/tasks/active/CAN-20260718-security-authenticated-session-transport.md
  - docs/security/SECURITY_VALIDATION_SEC005.md
  - tests/security/runtime_scenarios/canary-game-session.json
  - tests/security/test_game_session_runtime.py
  - tests/security/test_game_session_runtime_runner.py
  - tools/security/game_session_runtime.py
  - tools/security/game_session_runtime_runner.py
validation:
  - command: live repository PR path overlap preflight
    result: PASS
    evidence: no active SEC-005 before task creation and no exclusive-path overlap found
  - command: local isolated Python py_compile and XTEA frame sanity checks
    result: PASS
    evidence: core and runner compiled and XTEA round-tripped bounded fixtures
  - command: Agent Task Ownership run 29617554455
    result: FAIL
    evidence: active task related_pr was initially empty; corrected to PR 514
  - command: Security Validation run 29617798990
    result: FAIL
    evidence: first SEC-005 runtime reached ProtocolGame but used the wrong first-game framing; artifact and server logs identified the pre-XTEA Adler32 wire-format mismatch and no fatal findings
  - command: Agent Task Ownership run 29618885740
    result: PASS
    evidence: corrected implementation-head ownership validation passed
  - command: CI run 29618885853
    result: PASS
    evidence: corrected implementation-head repository CI passed
  - command: Security Validation run 29618885799
    result: PASS
    evidence: focused tests exact-head build SEC-003 SEC-004 and five-case SEC-005 runtime all passed; artifact 8421679031 has five passing case/control pairs and no fatal findings
  - command: CI run 29620170020
    result: PASS
    evidence: durable-docs head repository CI passed
  - command: Agent Task Ownership run 29620169895
    result: PASS
    evidence: durable-docs head ownership validation passed
blockers: []
next_action: Let exact-final-head CI Agent Task Ownership and Security Validation run on this readiness commit. Make no further commits. If all required checks pass on the same final head and PR 514 remains mergeable with no review blockers or overlapping main changes, mark ready and squash merge using the exact final head SHA, then verify task lifecycle archival and reconcile the program to DONE without starting the next queued security task.
```
