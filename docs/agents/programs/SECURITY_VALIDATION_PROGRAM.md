---
program_id: CAN-PROGRAM-SECURITY-VALIDATION
name: OTS Security Validation Platform
status: active
owner: security-validation-agent
created: 2026-07-16T20:10:00+02:00
updated: 2026-07-17T09:35:00+02:00
last_verified_commit: "8d10da7677b63685312281784c747bed117d6134"
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

# Phase 2 — runtime delegation adapter (`OTS-SEC-002`)

Merged in PR #440. This phase added the code-owned `canary-universal-e2e` adapter with exact repository authorization, literal-loopback confinement, controlled-client restriction and deterministic SHA-256 delegation evidence while keeping arbitrary commands, credentials and free-form network targets out of manifests.

Its lifecycle record was archived before OTS-SEC-003 began.

# Runtime-hook dependency (`OTS-SEC-003-RUNTIME-HOOK`)

Merged in PR #444 with lifecycle completed in PR #450. This narrow E2E-platform dependency exposes the existing Universal Agent Load exact-head Canary lifecycle through a typed in-process `RuntimeContext` / `run_runtime` callback while preserving the existing load CLI.

The callback is intentionally code-owned: manifests cannot provide commands, executables or target hosts. It owns map/database/config/server startup and cleanup, invokes one caller-supplied in-process executor only after Canary reports online, and verifies the process remains alive afterward.

# Phase 3 — malformed framing/status parser runtime (`OTS-SEC-003`)

Merged in PR #451 with lifecycle completed in PR #459. This first bounded runtime phase covers common TCP framing and unauthenticated Canary `ProtocolStatus` resilience through a fixed code-owned case registry, literal-loopback confinement, deterministic source isolation, exact-head runtime execution and machine-readable evidence.

The final feature head passed focused security validation, repository CI, Agent Task Ownership, exact-head Linux release build and the real eight-case runtime before squash merge.

OTS-SEC-003 does not claim authenticated login/game, encrypted post-login transport, maintained-client hostile-server, packet-flood or sustained-DoS coverage.

# Phase 4 — login protocol boundary runtime (`OTS-SEC-004`)

Active in draft PR #462. This phase is intentionally limited to the Canary login service before successful account authentication or game-session establishment.

It adds a strict code-owned runtime plan and report contract, fixed bounded login-boundary cases, literal-loopback confinement, distinct deterministic case/control sources, a protocol-aware control oracle, deterministic evidence and a dedicated exact-head Security Validation runtime job. Manifests cannot supply arbitrary payloads, credentials, key material or network coordinates.

Implementation head `8d10da7677b63685312281784c747bed117d6134` passed repository CI run 29562937900, Agent Task Ownership run 29562937739 and Security Validation run 29562937865. The exact-head Linux release build passed; the existing SEC-003 runtime regression passed; and the new six-case login-boundary runtime passed with no fatal/sanitizer findings.

The green run proves only the registered login-boundary assertions and the service control check after every case. It does not claim successful account authentication, character-list correctness, game-session establishment, post-login game transport coverage, session-race/replay resistance, maintained-client hostile-server handling or flood/sustained-DoS capacity.

# Ordered queue

1. `DONE` — OTS-SEC-001 foundation merged in PR #433.
2. `DONE` — OTS-SEC-002 runtime delegation adapter merged in PR #440.
3. `DONE` — OTS-SEC-003 bounded common-framing + unauthenticated `ProtocolStatus` runtime scenarios merged in PR #451; lifecycle completed in PR #459.
4. `ACTIVE` — OTS-SEC-004 bounded login protocol boundary scenarios in PR #462.
5. Add authenticated game-session parser and post-login transport scenarios through a separate bounded task.
6. Add authenticated session, race, economy and transaction-abuse scenarios with disposable MariaDB state assertions.
7. Add Redis/multichannel failure and ownership scenarios without targeting shared or production infrastructure.
8. Add maintained-client hostile-server scenarios through an explicit cross-repository contract.
9. Add MyAAC web/auth/session scenarios against a pinned disposable MyAAC build.
10. Register Otheryn as a target adapter and require migrated security regressions to pass before declaring a security-sensitive migration preserved.

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

Start from `AGENTS.md`, `docs/agents/CONTEXT_ROUTING.md`, this program, `docs/security/SECURITY_VALIDATION_PLATFORM.md`, the active security task and live PR. Load the Universal E2E route only when a task actually introduces or consumes runtime execution/delegation. For OTS-SEC-004 specifically, treat `tools/e2e/run_agent_load_runtime.py` as the reused server-only lifecycle boundary and keep successful authentication plus game-session/post-login transport coverage in separate tasks.
