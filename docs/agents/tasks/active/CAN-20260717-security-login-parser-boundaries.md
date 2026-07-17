---
task_id: CAN-20260717-security-login-parser-boundaries
program_id: CAN-PROGRAM-SECURITY-VALIDATION
coordination_id: OTS-SEC-004
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/security-login-parser-boundaries
base_branch: main
created: 2026-07-17T09:00:00+02:00
updated: 2026-07-17T09:04:00+02:00
last_verified_commit: "cc2d9990346ad6d2d903d66ff7af4a450a1922d0"
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
  - planned ots-security-login-packet-plan-v1
  - planned ots-security-login-packet-report-v1
cross_repo_tasks: []
---

# Goal

Deliver the next bounded runtime-security pack for Canary login first-message parsing and the RSA-to-XTEA key handoff on disposable literal-loopback infrastructure.

The task is intentionally limited to the login service before successful account authentication or game-session establishment. It must not claim authenticated game-packet, post-login XTEA transport, sequence/checksum, hostile-server, flood or sustained-DoS coverage.

# Acceptance criteria

- [ ] Define a strict versioned plan with exact repository authorization and only code-owned built-in case identifiers.
- [ ] Keep packet bytes, RSA material derivation, credentials, source addresses, destination addresses and ports out of scenario manifests.
- [ ] Reuse the existing disposable Canary `RuntimeContext` / `run_runtime` callback rather than create another lifecycle implementation.
- [ ] Confine every destination to the callback-provided literal loopback login port.
- [ ] Cover bounded login first-message/prelude truncation and unsupported-profile behavior.
- [ ] Cover bounded RSA failure and successful raw-RSA handoff into code-owned XTEA-key/credential parsing cases without using real user credentials.
- [ ] Require Canary to remain alive and prove the login service remains responsive after every case with a deterministic code-owned control exchange.
- [ ] Fail closed on timeout, unexpected response, process exit or fatal/sanitizer evidence.
- [ ] Emit deterministic SHA-256-pinned machine-readable evidence.
- [ ] Add focused Python tests and exact-head disposable runtime execution in Security Validation CI.
- [ ] Document the explicit non-coverage boundary for successful account authentication, game-session establishment and post-login encrypted game packets.
- [ ] Pass exact-final-head merge gate and squash merge.

# Evidence summary

- OTS-SEC-003 is merged and archived; its server-only disposable runtime callback is reusable for login-port probes.
- `ProtocolLogin::onRecvFirstMessage` resolves a login layout, performs raw 128-byte RSA decryption, reads four XTEA key words, enables XTEA and Adler32 response transport, then reads account descriptor and password.
- The default RSA fallback key is repository-defined and uses exponent 65537; the test driver may derive the public modulus from those code-owned factors but must not accept key material from a manifest.
- Open-PR overlap search found no runtime login/game parser security implementation. PR #453 is documentation-only MyAAC/login-stack audit work and does not own these runtime paths.
- Draft PR: #462.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T09:04:00+02:00
head: cc2d9990346ad6d2d903d66ff7af4a450a1922d0
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
  - default fallback RSA uses repository-defined factors and exponent 65537
  - no open runtime login parser security PR overlap was found
  - draft PR 462 owns this bounded task
unknown:
  - exact current-client prelude bytes needed for a deterministic valid login control exchange
  - minimal response decoder needed to prove login-service responsiveness after RSA handoff
  - final fixed case registry after protocol-layout fixture review
conflicts: []
changed_paths:
  - docs/agents/tasks/active/CAN-20260717-security-login-parser-boundaries.md
validation: []
blockers: []
next_action: Implement and unit-test the smallest code-owned current-profile login packet builder and deterministic control exchange, then register only cases proven by those fixtures.
```
