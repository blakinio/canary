---
task_id: CAN-20260717-security-login-parser-boundaries
program_id: CAN-PROGRAM-SECURITY-VALIDATION
coordination_id: OTS-SEC-004
status: review
agent: "GPT-5.5 Thinking"
branch: feat/security-login-parser-boundaries
base_branch: main
created: 2026-07-17T09:00:00+02:00
updated: 2026-07-17T09:55:00+02:00
last_verified_commit: "8d10da7677b63685312281784c747bed117d6134"
risk: high
related_issue: ""
related_pr: "462"
depends_on:
  - "OTS-SEC-003 / PR #451"
  - "OTS-SEC-003-RUNTIME-HOOK / PR #444"
blocks:
  - future authenticated game-session parser security scenarios
owned_paths:
  exclusive:
    - tools/security/login_packet_runtime.py
    - tools/security/login_packet_runtime_runner.py
    - tests/security/test_login_packet_runtime.py
    - tests/security/test_login_packet_runtime_runner.py
    - tests/security/runtime_scenarios/canary-login-parser.json
    - docs/agents/tasks/active/CAN-20260717-security-login-parser-boundaries.md
  shared:
    - .github/workflows/security-validation.yml
    - docs/security/SECURITY_VALIDATION_PLATFORM.md
    - docs/agents/programs/SECURITY_VALIDATION_PROGRAM.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/e2e/run_agent_load_runtime.py
    - src/server/network/protocol/protocollogin.cpp
    - src/server/network/protocol/protocollogin.hpp
    - src/server/network/protocol/protocol.cpp
    - src/server/network/protocol/protocol_profile.hpp
    - src/server/network/protocol/protocol_profile.cpp
    - src/security/rsa.cpp
    - src/security/rsa_backend_mbedtls.cpp
modules_touched:
  - OTS Security Validation Platform runtime attacks
  - Canary login first-message and RSA parser evidence
reuses:
  - tools/e2e/run_agent_load_runtime.py RuntimeContext/run_runtime lifecycle callback
  - OTS-SEC-003 authorization, deterministic evidence and code-owned packet-corpus patterns
public_interfaces:
  - ots-security-login-packet-plan-v1
  - ots-security-login-packet-report-v1
  - canary-login-parser-v1 built-in runtime driver
cross_repo_tasks: []
---

# Goal

Deliver the next bounded runtime-security pack for Canary login first-message parsing and the RSA-to-XTEA key handoff on disposable literal-loopback infrastructure.

The task is intentionally limited to the login service before successful account authentication or game-session establishment. It must not claim authenticated game-packet, post-login XTEA transport, sequence/checksum, hostile-server, flood or sustained-DoS coverage.

# Acceptance criteria

- [x] Define a strict versioned plan with exact repository authorization and only code-owned built-in case identifiers.
- [x] Keep packet bytes, RSA material derivation, credentials, source addresses, destination addresses and ports out of scenario manifests.
- [x] Reuse the existing disposable Canary `RuntimeContext` / `run_runtime` callback rather than create another lifecycle implementation.
- [x] Confine every destination to the callback-provided literal loopback login port.
- [x] Cover bounded login first-message/prelude truncation and unsupported-profile behavior.
- [x] Cover bounded RSA failure and successful raw-RSA handoff into code-owned XTEA-key/credential parsing cases without using real user credentials.
- [x] Require Canary to remain alive and prove the login service remains responsive after every case with a deterministic code-owned control exchange.
- [x] Fail closed on timeout, unexpected response, process exit or fatal/sanitizer evidence.
- [x] Emit deterministic SHA-256-pinned machine-readable evidence.
- [x] Add focused Python tests and exact-head disposable runtime execution in Security Validation CI.
- [x] Document the explicit non-coverage boundary for successful account authentication, game-session establishment and post-login encrypted game packets.
- [ ] Pass exact-final-head merge gate and squash merge.

# Evidence summary

- OTS-SEC-003 is merged and archived; its server-only disposable runtime callback is reused for login-port probes.
- The plan is strict and code-owned: manifests contain only repository, driver, service and fixed case identifiers, not arbitrary payloads, credentials or network coordinates.
- The fixed registry contains six bounded login-boundary cases and every case/control pair uses separate deterministic code-owned IPv4 loopback source addresses while server throttles stay enabled.
- The control oracle validates the expected CurrentLogin transport/result rather than accepting process liveness or any non-empty response.
- Local focused validation passed 19 tests and Python bytecode compilation.
- Implementation head `8d10da7677b63685312281784c747bed117d6134` passed repository CI run 29562937900 and Agent Task Ownership run 29562937739.
- Security Validation run 29562937865 passed focused validation, exact-head Linux release build, the existing eight-case SEC-003 regression runtime and the new six-case SEC-004 runtime.
- The real SEC-004 runtime completed all six cases, validated the service control after every case and reported no fatal/sanitizer findings.
- Durable platform/program/catalogue/changelog documentation records the exact bounded evidence boundary and explicitly excludes successful authentication, character-list, game-session and post-login transport claims.
- Branch was synchronized with current `main` `be9760a88d0c714dfd3e1b6a659e373380d03d65`; the review diff contains exactly 11 intended SEC-004 files and is `behind_by=0` at that synchronization point.
- CHANGELOG review patch contains only the single SEC-004 addition; previously detected accidental historical-text differences were restored from current `main`.
- Open-PR overlap search found no runtime login/game parser security implementation. PR #453 is documentation-only MyAAC/login-stack audit work and does not own these runtime paths.
- Draft PR: #462.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T09:55:00+02:00
head: dcf15db8ecdeb55dcf590ff7aa0422fb65ea16a3
branch: feat/security-login-parser-boundaries
pr: 462
status: validating
context_routes:
  - agent-governance
  - cpp-runtime
owned_paths:
  - tools/security/login_packet_runtime.py
  - tools/security/login_packet_runtime_runner.py
  - tests/security/test_login_packet_runtime.py
  - tests/security/test_login_packet_runtime_runner.py
  - tests/security/runtime_scenarios/canary-login-parser.json
  - docs/agents/tasks/active/CAN-20260717-security-login-parser-boundaries.md
  - .github/workflows/security-validation.yml
  - docs/security/SECURITY_VALIDATION_PLATFORM.md
  - docs/agents/programs/SECURITY_VALIDATION_PROGRAM.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - only blakinio/canary is writable
  - SEC-003 and its lifecycle cleanup are merged
  - the scenario manifest contains only fixed case identifiers and repository driver service metadata
  - distinct deterministic loopback source pairs preserve normal server admission protections
  - the control oracle is protocol-aware and cannot be satisfied by an unrelated plain response
  - local focused validation passed 19 tests and py_compile
  - CI run 29562937900 passed on implementation head 8d10da7677b63685312281784c747bed117d6134
  - Agent Task Ownership run 29562937739 passed on implementation head 8d10da7677b63685312281784c747bed117d6134
  - Security Validation run 29562937865 passed focused checks exact-head build SEC-003 regression runtime and all six SEC-004 cases
  - the SEC-004 runtime reported no fatal or sanitizer findings
  - shared documentation preserves the bounded non-coverage boundary
  - branch synchronization used current main be9760a88d0c714dfd3e1b6a659e373380d03d65 as base and retained exactly the intended SEC-004 file set
  - CHANGELOG differs from synchronized main by exactly one SEC-004 entry
derived:
  - the bounded SEC-004 implementation is ready for review-head validation before final-head gating
unknown:
  - review-head CI Security Validation and Agent Task Ownership results after durable documentation and task checkpoint updates
  - whether main advances again before final-head gating
conflicts: []
first_failure:
  marker: checkpoint-schema
  evidence: Agent Task Ownership run 29562807891 rejected the initial task checkpoint because three required checkpoint fields were missing; the schema was corrected without changing runtime code
rejected_hypotheses:
  - weakening or disabling Canary connection throttles for the security harness
  - accepting arbitrary packet data credentials or network targets from the scenario manifest
  - treating any nonempty login response as proof of the intended control boundary
  - broadening SEC-004 into authenticated game-session packet testing
changed_paths:
  - .github/workflows/security-validation.yml
  - docs/agents/CHANGELOG.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/programs/SECURITY_VALIDATION_PROGRAM.md
  - docs/agents/tasks/active/CAN-20260717-security-login-parser-boundaries.md
  - docs/security/SECURITY_VALIDATION_PLATFORM.md
  - tests/security/runtime_scenarios/canary-login-parser.json
  - tests/security/test_login_packet_runtime.py
  - tests/security/test_login_packet_runtime_runner.py
  - tools/security/login_packet_runtime.py
  - tools/security/login_packet_runtime_runner.py
validation:
  - command: local py_compile and focused unittest discovery for SEC-004 files
    result: PASS
    evidence: 19 tests completed successfully before repository commit
  - command: Agent Task Ownership run 29562807891
    result: FAIL
    evidence: initial checkpoint schema omitted three required fields; corrected without runtime changes
  - command: Agent Task Ownership run 29562937739
    result: PASS
    evidence: corrected task ownership and checkpoint validation passed
  - command: CI run 29562937900
    result: PASS
    evidence: repository CI passed on implementation head 8d10da7677b63685312281784c747bed117d6134
  - command: Security Validation run 29562937865
    result: PASS
    evidence: focused validation exact-head build SEC-003 regression runtime and six-case SEC-004 runtime all passed
blockers: []
next_action: Verify CI Security Validation and Agent Task Ownership on this review head. If all pass, mark PR 462 ready, verify review threads/comments, apply ci:final-gate before one final readiness checkpoint commit, make no post-green commit, and squash merge only after exact-final-head checks pass on the same SHA.
```
