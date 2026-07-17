---
task_id: CAN-20260717-security-login-parser-boundaries
program_id: CAN-PROGRAM-SECURITY-VALIDATION
coordination_id: OTS-SEC-004
status: completed
agent: "GPT-5.5 Thinking"
branch: feat/security-login-parser-boundaries
base_branch: main
created: 2026-07-17T09:00:00+02:00
updated: 2026-07-17T08:55:41Z
last_verified_commit: "e5d85703ea464220569a36384de8c71ad40c69b8"
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
  - OTS Security Validation Platform runtime validation
  - Canary login protocol boundary evidence
reuses:
  - tools/e2e/run_agent_load_runtime.py RuntimeContext/run_runtime lifecycle callback
  - OTS-SEC-003 authorization and deterministic evidence patterns
public_interfaces:
  - ots-security-login-packet-plan-v1
  - ots-security-login-packet-report-v1
  - canary-login-parser-v1 built-in runtime driver
cross_repo_tasks: []
completed: 2026-07-17T08:55:41Z
---

# Goal

Deliver a bounded runtime-security validation pack for the Canary login protocol boundary on disposable literal-loopback infrastructure.

The task is limited to the registered pre-authentication login boundary cases. It does not claim successful authentication, character-list correctness, game-session establishment, post-login transport coverage, hostile-server coverage, packet-flood resistance or sustained-DoS capacity.

# Acceptance criteria

- [x] Strict versioned plan with exact repository authorization and only code-owned case identifiers.
- [x] No arbitrary payloads, credentials, commands or network targets in scenario manifests.
- [x] Reuse the existing disposable Canary runtime callback instead of duplicating lifecycle code.
- [x] Literal-loopback destination confinement and deterministic code-owned source isolation.
- [x] Bounded login-boundary rejection and negative-authentication cases.
- [x] Deterministic protocol-aware service control after every case.
- [x] Fail closed on timeout, unexpected response, process exit or fatal/sanitizer evidence.
- [x] Deterministic SHA-256-pinned machine-readable evidence.
- [x] Focused Python tests and exact-head disposable runtime execution in Security Validation CI.
- [x] Explicitly document non-coverage for successful authentication, game-session and post-login transport behavior.
- [ ] Pass exact-final-head merge gate and squash merge.

# Evidence summary

- Local focused validation passed 19 tests and Python bytecode compilation.
- Implementation head `8d10da7677b63685312281784c747bed117d6134` passed CI run 29562937900, Agent Task Ownership run 29562937739 and Security Validation run 29562937865.
- Review head `334ff426eb8bcaa892a8d78131bd7455bb7b9f15` passed CI run 29564760860, Agent Task Ownership run 29564760767 and Security Validation run 29564760809.
- Both review-head Security Validation runs included the exact-head build, the existing SEC-003 runtime regression and the new six-case SEC-004 runtime; all passed with no fatal/sanitizer findings.
- Durable platform, program, catalogue and changelog documentation record the bounded evidence boundary and explicit non-claims.
- Final synchronization head `649285d4f69debc90c6a1c960d35622a54eb581d` is based on current `main` `317c1c4235377c388883aa2fd425d324f8ce4d2e`, is `behind_by=0`, and contains exactly the 11 intended SEC-004 changed files.
- CHANGELOG differs from synchronized `main` by exactly one SEC-004 addition.
- Review gate is clean: no PR comments, reviews or unresolved review threads.
- PR #462 is Ready and `ci:final-gate` was applied before this final readiness checkpoint commit.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T10:10:00+02:00
head: 649285d4f69debc90c6a1c960d35622a54eb581d
branch: feat/security-login-parser-boundaries
pr: 462
status: ready
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
  - manifests remain confined to fixed code-owned case identifiers and authorization metadata
  - runtime target and source strategy remain confined to code-owned loopback behavior
  - local focused validation passed 19 tests and py_compile
  - implementation-head CI Ownership and Security Validation passed
  - review-head CI run 29564760860 passed
  - review-head Agent Task Ownership run 29564760767 passed
  - review-head Security Validation run 29564760809 passed exact-head build SEC-003 regression runtime and all six SEC-004 cases
  - the SEC-004 runtime reported no fatal or sanitizer findings
  - final synchronization head 649285d4f69debc90c6a1c960d35622a54eb581d uses current main 317c1c4235377c388883aa2fd425d324f8ce4d2e and is behind_by zero
  - final synchronized diff contains exactly 11 intended SEC-004 files
  - CHANGELOG differs from synchronized main by exactly one SEC-004 entry
  - review gate has no comments reviews or unresolved review threads
  - PR 462 is ready for review
  - ci:final-gate was applied before this final readiness checkpoint commit
derived:
  - the bounded SEC-004 implementation is ready for exact-final-head merge gating
unknown:
  - exact-final-head CI Security Validation and Agent Task Ownership results for this readiness commit
conflicts: []
first_failure:
  marker: checkpoint-schema
  evidence: initial Agent Task Ownership validation rejected missing checkpoint fields; the schema was corrected without changing runtime code
rejected_hypotheses:
  - weakening or disabling normal Canary admission protections for the test harness
  - accepting arbitrary payloads credentials or network targets from scenario manifests
  - treating process liveness or any nonempty response as sufficient service-control evidence
  - broadening SEC-004 into authenticated game-session testing
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
  - command: local focused SEC-004 tests and py_compile
    result: PASS
    evidence: 19 tests completed successfully
  - command: CI run 29562937900
    result: PASS
    evidence: implementation-head repository CI passed
  - command: Agent Task Ownership run 29562937739
    result: PASS
    evidence: implementation-head ownership validation passed
  - command: Security Validation run 29562937865
    result: PASS
    evidence: implementation-head focused validation exact-head build SEC-003 regression runtime and six-case SEC-004 runtime passed
  - command: CI run 29564760860
    result: PASS
    evidence: review-head repository CI passed
  - command: Agent Task Ownership run 29564760767
    result: PASS
    evidence: review-head ownership validation passed
  - command: Security Validation run 29564760809
    result: PASS
    evidence: review-head focused validation exact-head build SEC-003 regression runtime and six-case SEC-004 runtime passed
blockers: []
next_action: Let exact-final-head workflows run on this readiness commit. Make no further commits. If CI Security Validation and Agent Task Ownership all pass on the same head and PR 462 remains mergeable with no review blockers, squash merge using the exact final head SHA and then complete lifecycle archival.
```

## Automated lifecycle completion

- Feature PR: #462.
- Feature head: `729bea5910086ca7b90bb3132f92e55c7cda6e17`.
- Merge commit: `e5d85703ea464220569a36384de8c71ad40c69b8`.
- Merged at: `2026-07-17T08:55:41Z`.
- This record was moved from `tasks/active` by the post-merge lifecycle automation.
