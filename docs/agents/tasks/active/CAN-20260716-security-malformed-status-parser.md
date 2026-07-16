---
task_id: CAN-20260716-security-malformed-status-parser
program_id: CAN-PROGRAM-SECURITY-VALIDATION
coordination_id: OTS-SEC-003
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/security-malformed-status-parser
base_branch: main
created: 2026-07-16T23:57:00+02:00
updated: 2026-07-16T23:57:00+02:00
last_verified_commit: "35b9f7d734add288c7c3b9f6be733807d8329c4a"
risk: high
related_issue: ""
related_pr: ""
depends_on:
  - "OTS-SEC-001 / PR #433"
  - "OTS-SEC-002 / PR #440"
  - "OTS-SEC-003-RUNTIME-HOOK / PR #444"
blocks:
  - future authenticated login/game malformed-packet security scenarios
owned_paths:
  exclusive:
    - tools/security/malformed_packet_runtime.py
    - tests/security/test_malformed_packet_runtime.py
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
    - tools/e2e/run_agent_load.py
    - .github/workflows/universal-agent-load.yml
    - .github/workflows/reusable-build-linux.yml
    - src/server/network/connection/connection.cpp
    - src/server/network/protocol/protocolstatus.cpp
modules_touched:
  - OTS Security Validation Platform runtime attacks
  - Canary TCP framing and status protocol security evidence
reuses:
  - tools/e2e/run_agent_load_runtime.py RuntimeContext/run_runtime lifecycle callback
  - .github/workflows/reusable-build-linux.yml exact-head Canary build
  - existing status XML control request contract
public_interfaces:
  - ots-security-malformed-packet-plan-v1
  - ots-security-malformed-packet-report-v1
  - canary-status-parser-v1 built-in runtime driver
cross_repo_tasks: []
---

# Goal

Implement OTS-SEC-003 as the first bounded offensive runtime-security scenario pack: deterministic malformed TCP framing and `ProtocolStatus` parser probes against an exact-head disposable Canary bound to loopback, with a valid status control probe after every malformed case, server-liveness enforcement, fatal/sanitizer log diagnostics and machine-readable evidence. This task deliberately does not claim authenticated login/game/XTEA/checksum parser coverage.

# Acceptance criteria

- [ ] Add strict `ots-security-malformed-packet-plan-v1` validation with exact fields, exact repository authorization, one code-owned driver and a bounded unique list of built-in case IDs.
- [ ] Do not allow plans to provide raw/hex packet payloads, arbitrary commands, executable paths, credentials, hostnames, IP targets or ports.
- [ ] Add fixed reviewed malformed cases for zero/oversized framing, truncated declared body, unknown service identifier and truncated/unknown status parser payloads.
- [ ] Reuse `tools/e2e/run_agent_load_runtime.py::run_runtime`; do not duplicate map/database/config/server lifecycle.
- [ ] Execute only against the callback-provided literal loopback target and status port.
- [ ] Require malformed connections to terminate without an unexpected response or bounded read timeout.
- [ ] Run a valid XML status request after every malformed case and require a valid `<tsqp`/`<serverinfo` response, proving the server remains responsive.
- [ ] Fail closed when the Canary process exits, a control probe fails, a malformed case hangs, or fatal/sanitizer signatures appear in Canary logs.
- [ ] Emit deterministic `ots-security-malformed-packet-report-v1` evidence with plan/provider/binary SHA-256, ordered per-case results and fatal-log findings.
- [ ] Add focused unit/integration-style Python tests for plan validation, fixed case registry, loopback confinement, connection outcomes, control-probe failure, timeout failure, fatal-log detection and deterministic report generation.
- [ ] Extend Security Validation CI to compile/test the driver, build exact-head Canary and execute the canonical runtime plan in disposable MySQL + Canary infrastructure.
- [ ] Update platform/program/catalogue/changelog documentation narrowly and explicitly state the non-coverage boundary for authenticated login/game protocols.
- [ ] Review the exact diff and pass current-head plus exact-final-head required CI before squash merge.

# Confirmed context

- Writable repository is exactly `blakinio/canary`; upstream/donor repositories remain read-only.
- Task-start `main` is `35b9f7d734add288c7c3b9f6be733807d8329c4a`.
- OTS-SEC-002 merged in PR #440 and established strict code-owned runtime delegation.
- Runtime-hook dependency PR #444 merged as `44d8c97bdf1add97acba719a7342b712de5be1fb`; lifecycle PR #450 merged as task-start main.
- `run_agent_load_runtime.py` now exposes `RuntimeContext` and `run_runtime` while retaining ownership of disposable map/database/config/Canary lifecycle.
- `Connection::parseHeader` closes zero-length and oversized declared frames; `Connection::parsePacket` fails closed when no protocol can be selected.
- `ProtocolStatus::onRecvFirstMessage` accepts XML opcode `0xFF` + literal `info`, accepts bounded binary-info opcode `0x01`, and disconnects unknown/truncated invalid input paths.
- Status throttling exempts literal `127.0.0.1`, making repeated canonical control probes deterministic in the disposable runtime.
- Open gameplay-E2E PRs #446/#447 own physical-client runner paths and share catalogue/changelog only; this task does not modify their exclusive paths and will defer shared-index finalization until current-main synchronization.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T23:57:00+02:00
head: 35b9f7d734add288c7c3b9f6be733807d8329c4a
branch: feat/security-malformed-status-parser
pr: null
status: implementing
context_routes:
  - agent-governance
  - universal-e2e
owned_paths:
  - tools/security/malformed_packet_runtime.py
  - tests/security/test_malformed_packet_runtime.py
  - tests/security/runtime_scenarios/canary-status-parser.json
  - docs/agents/tasks/active/CAN-20260716-security-malformed-status-parser.md
  - .github/workflows/security-validation.yml
  - docs/security/SECURITY_VALIDATION_PLATFORM.md
  - docs/agents/programs/SECURITY_VALIDATION_PROGRAM.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - only blakinio/canary is writable
  - main at task start is 35b9f7d734add288c7c3b9f6be733807d8329c4a
  - PR 444 provides a code-owned callback into the existing disposable Universal Agent Load Canary lifecycle
  - connection framing rejects zero and oversized body lengths before protocol dispatch
  - ProtocolStatus disconnects invalid status opcodes and malformed XML-info requests
  - 127.0.0.1 is exempt from ProtocolStatus query throttling
  - open gameplay E2E PRs do not own tools/security or security-validation workflow paths
derived:
  - the smallest non-overlapping SEC-003 slice is common TCP framing plus unauthenticated ProtocolStatus parser resilience
  - fixed built-in case identifiers preserve reviewability and prevent the scenario manifest from becoming an arbitrary packet-sending interface
  - a valid status control probe after every malformed case provides stronger responsiveness evidence than process liveness alone
unknown:
  - whether any first runtime case reveals a crash hang sanitizer signature or unexpected parser response
  - exact current-head Security Validation runtime result until implementation executes in CI
conflicts:
  - PR 446 and PR 447 share MODULE_CATALOG.md and CHANGELOG.md; defer shared-index edits and synchronize from current main before finalization
first_failure:
  marker: none
  evidence: no task-specific validation failure observed at task creation
rejected_hypotheses:
  - build a second security-specific Canary launcher
  - allow raw packet bytes or arbitrary targets in scenario manifests
  - claim login/game/XTEA/checksum coverage from an unauthenticated status-protocol slice
changed_paths:
  - docs/agents/tasks/active/CAN-20260716-security-malformed-status-parser.md
validation: []
blockers: []
next_action: Open the draft PR, implement the strict built-in malformed-packet driver and focused tests, then extend Security Validation CI with exact-head disposable runtime execution.
```
