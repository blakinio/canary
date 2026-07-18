---
program_id: CAN-PROGRAM-SECURITY-VALIDATION
name: OTS Security Validation Platform
status: active
owner: security-validation-agent
created: 2026-07-16T20:10:00+02:00
updated: 2026-07-17T22:07:49+02:00
last_verified_commit: "cb149d427e6a954ee3ab163758465627bc1e643c"
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
- Universal Agent Load owns literal-loopback-only bounded status-protocol load/stress evidence and exposes the code-owned server-only `RuntimeContext` / `run_runtime` callback used by OTS-SEC-003 and OTS-SEC-004.
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

# Ordered queue

1. `DONE` — OTS-SEC-001 foundation merged in PR #433.
2. `DONE` — OTS-SEC-002 runtime delegation adapter merged in PR #440; lifecycle completed in PR #443.
3. `DONE` — OTS-SEC-003 runtime hook merged in PR #444; lifecycle completed in PR #450.
4. `DONE` — OTS-SEC-003 bounded common-framing + unauthenticated `ProtocolStatus` runtime scenarios merged in PR #451; lifecycle completed in PR #459.
5. `DONE` — OTS-SEC-004 bounded login protocol boundary scenarios merged in PR #462; lifecycle task archived automatically.
6. `NEXT — NOT STARTED` — add authenticated game-session parser and post-login transport scenarios through a fresh bounded task after live ownership/overlap preflight. No task, branch or PR is created by this handoff.
7. `QUEUED` — add authenticated session, race, economy and transaction-abuse scenarios with disposable MariaDB state assertions.
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

There is no active OTS-SEC implementation task after OTS-SEC-004 lifecycle completion. `OTS-SEC-005` is not created and not started.

Durable workstream handoff:

`docs/agents/tasks/archive/CAN-20260717-security-validation-conversation-handoff.md`

A continuation agent must start from current `AGENTS.md`, `docs/agents/REPOSITORY_MAP.md`, `docs/agents/CONTEXT_ROUTING.md`, this program, the archived workstream handoff and live repository/PR/task state. It must not reconstruct completed SEC-001 through SEC-004 from chat history.

Before creating OTS-SEC-005, repeat the live ownership and overlap preflight and create one fresh active task, branch and draft PR. The separate open PR #453 is an independent MyAAC/login-stack audit and must not be absorbed or modified by the next runtime-security package without a fresh overlap review. Load the Universal E2E route only when the new bounded task actually introduces or consumes runtime execution/delegation.
