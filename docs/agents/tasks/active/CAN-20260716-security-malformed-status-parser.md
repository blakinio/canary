---
task_id: CAN-20260716-security-malformed-status-parser
program_id: CAN-PROGRAM-SECURITY-VALIDATION
coordination_id: OTS-SEC-003
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/security-malformed-status-parser
base_branch: main
created: 2026-07-16T23:57:00+02:00
updated: 2026-07-17T00:20:00+02:00
last_verified_commit: "88b398eb91290a5ef09ce6fd7eaa6f0dfffe574d"
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
    - tools/e2e/run_agent_load.py
    - .github/workflows/universal-agent-load.yml
    - .github/workflows/reusable-build-linux.yml
    - src/server/network/connection/connection.cpp
    - src/server/network/protocol/protocolstatus.cpp
    - src/server/network/message/**
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

- [x] Add strict `ots-security-malformed-packet-plan-v1` validation with exact fields, exact repository authorization, one code-owned driver and a bounded unique list of built-in case IDs.
- [x] Do not allow plans to provide raw/hex packet payloads, arbitrary commands, executable paths, credentials, hostnames, IP targets or ports.
- [x] Add fixed reviewed malformed cases for zero/oversized framing, truncated declared body, unknown service identifier and truncated/unknown status parser payloads.
- [x] Reuse `tools/e2e/run_agent_load_runtime.py::run_runtime`; do not duplicate map/database/config/server lifecycle.
- [x] Execute only against the callback-provided literal loopback target and status port.
- [x] Require malformed connections to terminate without an unexpected response or bounded read timeout.
- [x] Run a valid XML status request after every malformed case and require bounded recovery of a valid `<tsqp`/`<serverinfo` response, proving the server remains responsive without depending on one scheduler-immediate connection.
- [x] Fail closed when the Canary process exits, bounded control recovery fails, a malformed case hangs, or fatal/sanitizer signatures appear in Canary logs.
- [x] Emit deterministic `ots-security-malformed-packet-report-v1` evidence with plan/provider/binary SHA-256, ordered per-case results and fatal-log findings.
- [x] Add focused unit/integration-style Python tests for plan validation, fixed case registry, loopback confinement, connection outcomes, bounded control recovery/failure, timeout failure, fatal-log detection and deterministic report generation.
- [x] Extend Security Validation CI to compile/test the driver, build exact-head Canary and execute the canonical runtime plan in disposable MySQL + Canary infrastructure; parser source paths trigger the permanent regression.
- [ ] Update platform/program/catalogue/changelog documentation narrowly and explicitly state the non-coverage boundary for authenticated login/game protocols.
- [ ] Review the exact diff and pass current-head plus exact-final-head required CI before squash merge.

# Confirmed context

- Writable repository is exactly `blakinio/canary`; upstream/donor repositories remain read-only.
- Task-start `main` is `35b9f7d734add288c7c3b9f6be733807d8329c4a`.
- OTS-SEC-002 merged in PR #440 and established strict code-owned runtime delegation.
- Runtime-hook dependency PR #444 merged as `44d8c97bdf1add97acba719a7342b712de5be1fb`; lifecycle PR #450 merged as task-start main.
- `run_agent_load_runtime.py` exposes `RuntimeContext` and `run_runtime` while retaining ownership of disposable map/database/config/Canary lifecycle.
- `Connection::parseHeader` closes zero-length and oversized declared frames; `Connection::parsePacket` fails closed when no protocol can be selected.
- `ProtocolStatus::onRecvFirstMessage` accepts XML opcode `0xFF` + literal `info`, accepts bounded binary-info opcode `0x01`, and disconnects unknown/truncated invalid input paths.
- Status throttling exempts literal `127.0.0.1`.
- Open gameplay-E2E PRs #446/#447 own physical-client runner paths and share catalogue/changelog only; this task does not modify their exclusive paths and defers shared-index finalization until current-main synchronization.
- Initial real-runtime execution and one exact job rerun produced the same result: zero-length and oversized framing cases terminated and passed their control probes; the truncated-declared-body connection terminated, but a scheduler-immediate single control probe returned empty/invalid. Canary stayed alive with no fatal/sanitizer finding.
- The repair keeps the packet corpus unchanged and adds a separate code-owned canonical runner with four control attempts separated by 50 ms. Reports normalize successful recovery to `pass` and do not record scheduler-dependent attempt counts.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T00:20:00+02:00
head: 4cf746226b96f051d98654f21e409924957a2d02
branch: feat/security-malformed-status-parser
pr: 451
status: implementing
context_routes:
  - agent-governance
  - universal-e2e
  - ci-repair
owned_paths:
  - tools/security/malformed_packet_runtime.py
  - tools/security/malformed_packet_runtime_runner.py
  - tests/security/test_malformed_packet_runtime.py
  - tests/security/test_malformed_packet_runtime_runner.py
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
  - fixed packet bytes live in code and plans can select only reviewed built-in case identifiers
  - normal CI run 29538427774 passed on implementation head 88b398eb91290a5ef09ce6fd7eaa6f0dfffe574d
  - Security Validation run 29538427899 Validate security scenarios and exact-head linux-release build passed on implementation head 88b398eb91290a5ef09ce6fd7eaa6f0dfffe574d
  - first real malformed runtime and its exact failed-job rerun both reached truncated-declared-body after two successful cases and reported control-invalid-response while Canary remained alive
  - both real-runtime failures contained zero fatal or sanitizer log findings and the same exact Canary binary SHA-256 aa2a8c98fe97c2507f3aa56e55b53b618d2a50f052debb92bf77e9da54f12c08
  - repair preserves the packet corpus and adds bounded code-owned status recovery with deterministic normalized report semantics
  - Security Validation workflow now triggers on connection framing ProtocolStatus and NetworkMessage source changes
derived:
  - scheduler-immediate single-shot status responsiveness is too strict after the truncated-body EOF path because connection cleanup is asynchronous even when the process remains healthy
  - four code-owned attempts with 50 millisecond spacing preserve a bounded fail-closed responsiveness assertion without recording nondeterministic timing or attempt counts
  - the security runner can own recovery semantics while the core packet corpus and Universal Agent Load lifecycle remain unchanged
unknown:
  - whether the repaired canonical runner passes all eight built-in cases on exact-head disposable Canary
  - exact current-head CI Ownership and Security Validation results after the recovery-runner checkpoint
conflicts:
  - PR 446 and PR 447 share MODULE_CATALOG.md and CHANGELOG.md; defer shared-index edits and synchronize from current main before finalization
first_failure:
  marker: Security Validation 29538427899 / Malformed status parser runtime
  evidence: initial execution and exact failed-job rerun both failed deterministically at truncated-declared-body:control-invalid-response after the malformed connection terminated; runtime-summary kept canary_exit_code null and fatal_log_findings was empty, so the failure was isolated to scheduler-immediate single-shot control semantics rather than a demonstrated Canary crash
rejected_hypotheses:
  - first failure proves a Canary crash: rejected because canary_exit_code remained null and logs contained no fatal or sanitizer signature
  - first failure is a one-off CI flake: rejected because the exact failed runtime job reproduced the same case and failure code
  - remove the truncated-declared-body case: rejected because the case is valuable framing coverage and the malformed connection itself was handled correctly
  - weaken the gate to process liveness only: rejected because post-case service responsiveness remains required
  - build a second security-specific Canary launcher
  - allow raw packet bytes or arbitrary targets in scenario manifests
  - claim login/game/XTEA/checksum coverage from an unauthenticated status-protocol slice
changed_paths:
  - .github/workflows/security-validation.yml
  - docs/agents/tasks/active/CAN-20260716-security-malformed-status-parser.md
  - tests/security/runtime_scenarios/canary-status-parser.json
  - tests/security/test_malformed_packet_runtime.py
  - tests/security/test_malformed_packet_runtime_runner.py
  - tools/security/malformed_packet_runtime.py
  - tools/security/malformed_packet_runtime_runner.py
validation:
  - command: CI run 29538427774
    result: PASS
    evidence: repository CI passed on implementation head 88b398eb91290a5ef09ce6fd7eaa6f0dfffe574d
  - command: Security Validation run 29538427899 / Validate security scenarios
    result: PASS
    evidence: compile full tests/security discovery registry validation runtime-adapter resolution and permanent source regressions passed
  - command: Security Validation run 29538427899 / Build exact Canary head
    result: PASS
    evidence: linux-release exact-head Canary artifact built successfully
  - command: Security Validation run 29538427899 / Malformed status parser runtime attempt 1
    result: FAIL
    evidence: zero-length and oversized cases passed; truncated-declared-body terminated but the immediate control probe returned control-invalid-response; Canary stayed alive and fatal_log_findings was empty
  - command: Security Validation run 29538427899 / Malformed status parser runtime exact job rerun
    result: FAIL
    evidence: reproduced truncated-declared-body:control-invalid-response on the same binary with Canary alive and no fatal/sanitizer finding
  - command: Agent Task Ownership run 29538427514
    result: FAIL
    evidence: task metadata related_pr was empty instead of current PR 451; corrected in this checkpoint
blockers: []
next_action: Verify CI Ownership and Security Validation on the bounded recovery-runner head. If the exact-head real runtime passes all eight cases, update security platform/program docs, synchronize with current main, finalize shared indexes, review the full diff and run the exact-final-head gate.
```
