---
program_id: CAN-PROGRAM-SECURITY-VALIDATION
name: OTS Security Validation Platform
status: active
owner: security-validation-agent
created: 2026-07-16T20:10:00+02:00
updated: 2026-07-18T01:05:00+02:00
last_verified_commit: "c45050f81ce4b2f337b4573df60384627affd8fc"
primary_paths:
  - tools/security/**
  - tests/security/**
  - docs/security/**
shared_integration_paths:
  - .github/workflows/security-validation.yml
  - tools/e2e/**
  - tests/e2e/**
related_programs:
  - CAN-PROGRAM-E2E-PLATFORM
cross_repo_contracts: []
---

# Mission

Build one reusable security-validation layer for the OTS ecosystem that preserves confirmed security fixes as deterministic regressions and drives authorized security tests against disposable server, client, web, database and cache targets.

The platform is not permanently tied to Canary. Canary is the first source/runtime adapter because it is the currently authorized implementation repository. Otheryn and the maintained client are future target adapters, not reasons to duplicate the core scenario/report contracts.

# Existing foundations to reuse

- Universal OTS E2E owns disposable database/server/client lifecycle, controlled OTClient execution, SQL/protocol assertions, artifacts and cleanup.
- Universal Agent Load owns literal-loopback-only bounded status-protocol load/stress evidence and exposes the code-owned server-only `RuntimeContext` / `run_runtime` callback used by OTS-SEC-003, OTS-SEC-004 and OTS-SEC-005.
- Existing focused regressions remain authoritative implementation-level evidence and should be referenced by security scenarios rather than rewritten.
- Repository CI and exact-final-head merge gates remain the delivery boundary.

# Platform responsibility

The security platform owns:

- versioned security-scenario discovery and validation;
- explicit target authorization metadata;
- target-adapter selection contracts;
- security-specific static and runtime executors;
- code-owned bounded probe corpora for approved runtime scenarios;
- deterministic machine-readable findings and source/runtime evidence references;
- permanent regression registration after confirmed remediation;
- orchestration of approved security adapters without granting manifests arbitrary execution.

It does not own generic server/database/client bootstrap already provided by Universal OTS E2E / Universal Agent Load.

# Phase 1 — foundation (`OTS-SEC-001`)

Merged in PR #433. The foundation supports `source-regex` scenarios with strict exact-field JSON validation, repository-relative file confinement, explicit repository authorization, deterministic `ots-security-validation-report-v1` evidence, seeded regressions for PRs #326/#328, focused tests and a dedicated workflow.

Final feature head: `b2ceed93b4b9d4cd64d2a59757f583cf25648845`. Squash merge: `6503f5312dbf13d0fddcc1da98a10343ed30525c`.

# Phase 2 — runtime delegation adapter (`OTS-SEC-002`)

Merged in PR #440. This phase added the code-owned `canary-universal-e2e` adapter with exact repository authorization, literal-loopback confinement, controlled-client restriction and deterministic SHA-256 delegation evidence while keeping arbitrary commands, credentials and free-form network targets out of manifests.

Final feature head: `e7c5562d0d63b813cc4b5951c628465ca800c595`. Squash merge: `597011f0ea0673c005a5a513806df9f65a3d28e6`. Lifecycle completed in PR #443 before OTS-SEC-003 began.

# Runtime-hook dependency (`OTS-SEC-003-RUNTIME-HOOK`)

Merged in PR #444 with lifecycle completed in PR #450. This narrow E2E-platform dependency exposes the existing Universal Agent Load exact-head Canary lifecycle through a typed in-process `RuntimeContext` / `run_runtime` callback while preserving the existing load CLI.

The callback is intentionally code-owned: manifests cannot provide commands, executables or target hosts. It owns map/database/config/server startup and cleanup, invokes one caller-supplied in-process executor only after Canary reports online, and verifies the process remains alive afterward.

Final feature head: `a8ae4b5c9563e8e620a1bc466c4096d588c11fbd`. Squash merge: `44d8c97bdf1add97acba719a7342b712de5be1fb`.

# Phase 3 — malformed framing/status parser runtime (`OTS-SEC-003`)

Merged in PR #451 with lifecycle completed in PR #459. This first bounded runtime phase covers common TCP framing and unauthenticated Canary `ProtocolStatus` resilience through a fixed code-owned case registry, literal-loopback confinement, deterministic source isolation, exact-head runtime execution and machine-readable evidence.

Final feature head: `f1cb8a27671ee715b3d85fd3fad759cef7258421`. Squash merge: `b5962f7ae78545f84f46201670d80c99b59b1015`.

OTS-SEC-003 does not claim authenticated login/game, encrypted post-login transport, maintained-client hostile-server, packet-flood or sustained-DoS coverage.

# Phase 4 — login protocol boundary runtime (`OTS-SEC-004`)

Merged in PR #462 and lifecycle-completed by the post-merge task archival automation. The completed task record is `docs/agents/tasks/archive/CAN-20260717-security-login-parser-boundaries.md`.

This phase is intentionally limited to the Canary login service before successful account authentication or game-session establishment. It adds a strict code-owned runtime plan and report contract, fixed bounded login-boundary cases, literal-loopback confinement, distinct deterministic case/control sources, a protocol-aware control oracle, deterministic evidence and a dedicated exact-head Security Validation runtime job. Manifests cannot supply arbitrary payloads, credentials, key material or network coordinates.

Final feature head: `729bea5910086ca7b90bb3132f92e55c7cda6e17`. Squash merge: `e5d85703ea464220569a36384de8c71ad40c69b8`.

Exact-final-head validation on the feature head:

- Agent Task Ownership run `29565606950`: PASS;
- Security Validation run `29565607073`: PASS;
- repository CI run `29565607123`: PASS.

The final Security Validation run included the exact-head Canary build, the existing SEC-003 runtime regression and the six-case SEC-004 runtime; both runtime suites passed.

The green run proves only the registered login-boundary assertions and the service control check after every case. It does not claim successful account authentication, character-list correctness, game-session establishment, post-login game transport coverage, session-race/replay resistance, maintained-client hostile-server handling or flood/sustained-DoS capacity.

# Phase 5 — authenticated game-session and post-login transport (`OTS-SEC-005`)

Active in PR #514. This phase adds a strict `ots-security-game-session-plan-v1` / `ots-security-game-session-report-v1` contract and the code-owned `canary-game-session-v1` runtime driver while reusing the existing disposable Canary/MariaDB `run_runtime` lifecycle.

The runtime authenticates directly to the disposable Canary game port with repository-owned test fixtures that never enter the scenario manifest. It mirrors the maintained current-client first-game wire boundary: pre-XTEA Adler32 framing with modern padding and `ClientPendingGame`, then RSA handoff to XTEA and client sequence 1 for the first post-login packet. Five fixed cases cover authenticated control, zero sequence, sequence gap, sequence replay and invalid XTEA padding. Every malformed case requires same-session recovery with the still-expected sequence and is followed by a fresh authenticated control session from a distinct deterministic loopback source and fixture.

Validated implementation head `c45050f81ce4b2f337b4573df60384627affd8fc` passed Agent Task Ownership run `29618885740`, repository CI run `29618885853` and Security Validation run `29618885799`. The Security Validation run passed focused security tests, exact-head Linux release build, SEC-003 malformed-status runtime, SEC-004 login-parser runtime and the new five-case SEC-005 authenticated game-session runtime.

The SEC-005 artifact reported `status=success`, `failure=null`, five case probes PASS, five fresh control probes PASS and no fatal/sanitizer findings. Server diagnostics explicitly recorded rejection reasons `zero-sequence`, `sequence-mismatch` for gap and replay, and `decrypt-failure` after invalid modern padding `255 > 8`; each case then recovered using the expected accepted sequence.

The bounded evidence proves successful authentication/session establishment for the repository-owned disposable fixtures and the registered post-login sequence/XTEA rejection-and-recovery assertions only. It does not prove authorization correctness across arbitrary accounts, session fixation/token replay, reconnect/logout races, multiclient concurrency, economy/transaction safety, sustained flood/DoS capacity, hostile-server client resilience or production deployment safety.

# Ordered queue

1. `DONE` — OTS-SEC-001 foundation merged in PR #433.
2. `DONE` — OTS-SEC-002 runtime delegation adapter merged in PR #440; lifecycle completed in PR #443.
3. `DONE` — OTS-SEC-003 runtime hook merged in PR #444; lifecycle completed in PR #450.
4. `DONE` — OTS-SEC-003 bounded common-framing + unauthenticated `ProtocolStatus` runtime scenarios merged in PR #451; lifecycle completed in PR #459.
5. `DONE` — OTS-SEC-004 bounded login protocol boundary scenarios merged in PR #462; lifecycle task archived automatically.
6. `ACTIVE` — OTS-SEC-005 authenticated game-session and post-login sequence/XTEA validation in PR #514.
7. `QUEUED` — add authenticated session fixation/replay/reconnect/logout race scenarios and economy/transaction-abuse scenarios with disposable MariaDB state assertions.
8. `QUEUED` — add Redis/multichannel failure and ownership scenarios without targeting shared or production infrastructure.
9. `QUEUED` — add maintained-client hostile-server scenarios through an explicit cross-repository contract.
10. `QUEUED` — add MyAAC web/auth/session scenarios against a pinned disposable MyAAC build.
11. `QUEUED` — register Otheryn as a target adapter and require migrated security regressions to pass before declaring a security-sensitive migration preserved.

# Safety invariants

- Only repository-owner-authorized targets may be executed.
- No arbitrary public-target discovery or scanning.
- Runtime security scenarios use disposable/isolated infrastructure unless an exact alternative target is explicitly authorized.
- No production credentials, database dumps, private data or secrets in manifests/reports.
- Scenario and adapter manifests never contain arbitrary shell commands or arbitrary packet payloads.
- Generic E2E/load lifecycle infrastructure is reused rather than forked.
- Runtime probe corpora and source-address strategies are code-owned and reviewable.
- A green static scenario, delegation proof or bounded runtime pack is evidence for that exact assertion only; it never proves complete exploit resistance.
- Confirmed vulnerabilities become permanent regressions after the fix is merged.

# Handoff

OTS-SEC-005 is active in PR #514. Its authoritative continuation record is:

`docs/agents/tasks/active/CAN-20260718-security-authenticated-session-transport.md`

A continuation agent must start from current `AGENTS.md`, `docs/agents/REPOSITORY_MAP.md`, `docs/agents/CONTEXT_ROUTING.md`, this program, the active SEC-005 task checkpoint and live PR #514. It must verify current main/head and current-head workflow evidence rather than reconstructing state from chat history.

Keep the separate PR #453 MyAAC/login-stack audit independent. Do not start the queued session-race/economy package until SEC-005 is merged and lifecycle archival completes, then repeat the live ownership and overlap preflight before creating a fresh bounded task.
