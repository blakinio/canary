---
task_id: CAN-20260716-security-malformed-status-parser
program_id: CAN-PROGRAM-SECURITY-VALIDATION
coordination_id: OTS-SEC-003
status: review
agent: "GPT-5.5 Thinking"
branch: feat/security-malformed-status-parser
base_branch: main
created: 2026-07-16T23:57:00+02:00
updated: 2026-07-17T07:10:00+02:00
last_verified_commit: "979e69be26b3d383e6fe7971e1797f6fbd9eea4c"
risk: high
related_issue: ""
related_pr: "451"
depends_on:
  - "OTS-SEC-001 / PR #433"
  - "OTS-SEC-002 / PR #440"
  - "OTS-SEC-003-RUNTIME-HOOK / PR #444"
blocks:
  - future authenticated login/game malformed-packet security scenarios
owned_paths:
  exclusive:
    - tools/security/malformed_packet_runtime.py
    - tools/security/malformed_packet_runtime_runner.py
    - tests/security/test_malformed_packet_runtime.py
    - tests/security/test_malformed_packet_runtime_runner.py
    - tests/security/runtime_scenarios/canary-status-parser.json
    - docs/agents/tasks/active/CAN-20260716-security-malformed-status-parser.md
  shared:
    - .github/workflows/security-validation.yml
    - docs/security/SECURITY_VALIDATION_PLATFORM.md
    - docs/agents/programs/SECURITY_VALIDATION_PROGRAM.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/e2e/run_agent_load_runtime.py
    - .github/workflows/reusable-build-linux.yml
    - src/server/server.cpp
    - src/creatures/players/management/ban.cpp
    - src/server/network/connection/connection.cpp
    - src/server/network/protocol/protocolstatus.cpp
modules_touched:
  - OTS Security Validation Platform runtime attacks
  - Canary TCP framing and status protocol security evidence
reuses:
  - tools/e2e/run_agent_load_runtime.py RuntimeContext/run_runtime lifecycle callback
  - .github/workflows/reusable-build-linux.yml exact-head Canary build
public_interfaces:
  - ots-security-malformed-packet-plan-v1
  - ots-security-malformed-packet-report-v1
  - canary-status-parser-v1 built-in runtime driver
cross_repo_tasks: []
---

# Goal

Deliver the first bounded runtime parser-resilience pack for common TCP framing and unauthenticated Canary status protocol handling on disposable loopback-only infrastructure.

# Acceptance criteria

- [x] Strict versioned plan with exact repository authorization and code-owned case identifiers.
- [x] No manifest-provided packet bytes, commands, credentials or network targets.
- [x] Reuse the existing disposable Canary runtime callback rather than duplicate lifecycle code.
- [x] Keep the destination confined to callback-provided literal loopback.
- [x] Use distinct deterministic code-owned loopback sources for malformed and control probes while leaving production throttles enabled.
- [x] Require malformed connections to terminate and a valid status control response after every case.
- [x] Fail closed on process exit, transport timeout, control failure or fatal/sanitizer evidence.
- [x] Emit deterministic SHA-256-pinned machine-readable evidence.
- [x] Cover the driver with focused Python tests and exact-head disposable runtime CI.
- [x] Document the explicit non-coverage boundary for authenticated login/game, encryption, sequence/checksum and sustained load scenarios.
- [ ] Update shared catalogue and changelog from current main.
- [ ] Pass exact-final-head merge gate and squash merge.

# Evidence summary

- Current feature PR: #451.
- The packet corpus remains fixed and code-owned.
- Early runtime failures were traced to interactions with existing per-source admission and status-query throttles rather than a demonstrated Canary crash.
- The final harness keeps those protections enabled and uses separate deterministic loopback sources for malformed and control checks.
- Exact head `979e69be26b3d383e6fe7971e1797f6fbd9eea4c` passed repository CI, Agent Task Ownership, focused Security Validation, exact-head Linux release build and the real eight-case runtime pack.
- No review comments are currently present on PR #451.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T07:10:00+02:00
head: 3cded3286882603e90760ea6e1a8aa223b28a295
branch: feat/security-malformed-status-parser
pr: 451
status: validating
context_routes:
  - agent-governance
  - universal-e2e
  - ci-repair
owned_paths:
  - tools/security/**
  - tests/security/**
  - .github/workflows/security-validation.yml
  - docs/security/SECURITY_VALIDATION_PLATFORM.md
  - docs/agents/programs/SECURITY_VALIDATION_PROGRAM.md
  - docs/agents/tasks/active/CAN-20260716-security-malformed-status-parser.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - only blakinio/canary is writable
  - the reusable disposable Canary runtime callback is reused without a second lifecycle implementation
  - manifests cannot choose packet bytes commands credentials or network targets
  - distinct code-owned loopback sources isolate malformed and control checks while production throttles remain enabled
  - CI and Agent Task Ownership passed on 979e69be26b3d383e6fe7971e1797f6fbd9eea4c
  - Security Validation run 29557681411 passed focused checks exact-head Linux build and all eight runtime cases
derived:
  - the bounded SEC-003 implementation is ready for shared-index finalization and final-head validation
unknown:
  - exact-final-head gate result after the final documentation and readiness checkpoint
conflicts: []
first_failure:
  marker: runtime-harness-source-isolation
  evidence: early runtime failures were reproduced and resolved by separating code-owned loopback sources without weakening server protections
rejected_hypotheses:
  - a demonstrated Canary process crash
  - disabling production throttling for tests
  - removing the affected regression cases
  - replacing service-responsiveness checks with process-liveness-only checks
changed_paths:
  - .github/workflows/security-validation.yml
  - docs/agents/programs/SECURITY_VALIDATION_PROGRAM.md
  - docs/agents/tasks/active/CAN-20260716-security-malformed-status-parser.md
  - docs/security/SECURITY_VALIDATION_PLATFORM.md
  - tests/security/runtime_scenarios/canary-status-parser.json
  - tests/security/test_malformed_packet_runtime.py
  - tests/security/test_malformed_packet_runtime_runner.py
  - tools/security/malformed_packet_runtime.py
  - tools/security/malformed_packet_runtime_runner.py
validation:
  - command: repository CI on 979e69be26b3d383e6fe7971e1797f6fbd9eea4c
    result: PASS
    evidence: CI completed successfully
  - command: Agent Task Ownership on 979e69be26b3d383e6fe7971e1797f6fbd9eea4c
    result: PASS
    evidence: ownership validation completed successfully
  - command: Security Validation run 29557681411
    result: PASS
    evidence: focused validation exact-head build and eight-case runtime completed successfully
blockers: []
next_action: Update shared indexes from current main, review the exact diff, apply ci:final-gate before one final ready checkpoint commit, then make no post-green commit and merge only if all exact-head checks pass.
```
