---
task_id: CAN-20260717-security-login-parser-boundaries
program_id: CAN-PROGRAM-SECURITY-VALIDATION
coordination_id: OTS-SEC-004
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/security-login-parser-boundaries
base_branch: main
created: 2026-07-17T09:00:00+02:00
updated: 2026-07-17T09:23:00+02:00
last_verified_commit: "d00f4da2c7c40fcda114f68fa73dbd1633ef263a"
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
- [ ] Add focused Python tests and exact-head disposable runtime execution in Security Validation CI.
- [ ] Document the explicit non-coverage boundary for successful account authentication, game-session establishment and post-login encrypted game packets.
- [ ] Pass exact-final-head merge gate and squash merge.

# Evidence summary

- OTS-SEC-003 is merged and archived; its server-only disposable runtime callback is reused for login-port probes.
- `ProtocolLogin::onRecvFirstMessage` resolves a login layout, performs raw 128-byte RSA decryption, reads four XTEA key words, enables XTEA and Adler32 response transport, then reads account descriptor and password.
- The driver contains only the public modulus for the repository-owned default OpenTibia RSA key and code-owned non-user XTEA/credential fixtures; manifests cannot supply key material or credentials.
- The fixed registry contains six cases: unsupported version, current prelude without RSA, 127-byte truncated RSA, valid raw-RSA block with invalid marker, valid RSA with empty account, and valid RSA with a non-user account marker plus empty password.
- The control oracle requires a correctly framed Adler32 + XTEA CurrentLogin error response and decodes the expected `Invalid email.` result; a plain unsupported-version response cannot satisfy the control.
- Every case/control pair uses separate deterministic code-owned IPv4 loopback source addresses while server throttles stay enabled.
- Local focused validation before repository commit passed 19 tests and Python bytecode compilation.
- Open-PR overlap search found no runtime login/game parser security implementation. PR #453 is documentation-only MyAAC/login-stack audit work and does not own these runtime paths.
- Draft PR: #462.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T09:23:00+02:00
head: d00f4da2c7c40fcda114f68fa73dbd1633ef263a
branch: feat/security-login-parser-boundaries
pr: 462
status: implementing
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
  - run_agent_load_runtime RuntimeContext exposes literal-loopback login game and status ports
  - ProtocolLogin reads a raw RSA block before enabling XTEA and Adler32 login responses
  - the scenario manifest contains only fixed case identifiers and repository/driver/service metadata
  - the control oracle validates CurrentLogin block framing Adler32 XTEA padding opcode and error string
  - plain unsupported-version responses cannot satisfy the RSA-to-XTEA control oracle
  - distinct deterministic loopback source pairs preserve production admission throttles
  - local focused validation passed 19 tests and py_compile before repository commit
  - no open runtime login parser security PR overlap was found
derived:
  - the bounded SEC-004 implementation is ready for current-head repository validation and real disposable Canary runtime evidence
unknown:
  - current-head Security Validation result including exact-head Canary build and six-case login runtime
  - whether any real runtime case exposes a server behavior different from the source-derived fixture expectations
conflicts: []
first_failure:
  marker: checkpoint-schema
  evidence: Agent Task Ownership run 29562807891 rejected the task checkpoint because derived first_failure and rejected_hypotheses fields were missing
rejected_hypotheses:
  - weakening or disabling Canary connection throttles for the security harness
  - accepting arbitrary packet bytes RSA material credentials or network targets from the scenario manifest
  - treating any nonempty login response as proof of successful RSA-to-XTEA handoff
  - broadening SEC-004 into authenticated game-session packet fuzzing
changed_paths:
  - .github/workflows/security-validation.yml
  - docs/agents/tasks/active/CAN-20260717-security-login-parser-boundaries.md
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
    evidence: checkpoint schema omitted three required fields; this commit supplies them without changing runtime code
blockers: []
next_action: Verify Agent Task Ownership and Security Validation on this corrected head. If focused validation passes, inspect the exact-head six-case real runtime result before any documentation or readiness changes.
```
