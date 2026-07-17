---
program_id: CAN-PROGRAM-SECURITY-VALIDATION
name: OTS Security Validation Platform
status: active
owner: security-validation-agent
created: 2026-07-16T20:10:00+02:00
updated: 2026-07-17T07:00:00+02:00
last_verified_commit: "979e69be26b3d383e6fe7971e1797f6fbd9eea4c"
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

Build one reusable security-validation layer for the OTS ecosystem that preserves confirmed security fixes as deterministic regressions and drives authorized offensive tests against disposable server, client, web, database and cache targets.

The platform is not permanently tied to Canary. Canary is the first source/runtime adapter because it is the currently authorized implementation repository. Otheryn and the maintained client are future target adapters, not reasons to duplicate the core scenario/report contracts.

# Existing foundations to reuse

- Universal OTS E2E owns disposable database/server/client lifecycle, controlled OTClient execution, SQL/protocol assertions, artifacts and cleanup.
- Universal Agent Load owns literal-loopback-only bounded status-protocol load/stress evidence and exposes the code-owned server-only `RuntimeContext` / `run_runtime` callback used by OTS-SEC-003.
- Existing focused regressions remain authoritative implementation-level evidence and should be referenced by security scenarios rather than rewritten.
- Repository CI and exact-final-head merge gates remain the delivery boundary.

# Platform responsibility

The security platform owns:

- versioned security-scenario discovery and validation;
- explicit target authorization metadata;
- target-adapter selection contracts;
- security-specific static and runtime executors;
- code-owned bounded packet/probe corpora for approved runtime attack scenarios;
- deterministic machine-readable findings and source/runtime evidence references;
- permanent regression registration after confirmed remediation;
- orchestration of approved security adapters without granting manifests arbitrary command or packet execution.

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

Active in PR #451. This first offensive runtime phase is intentionally bounded to common TCP framing and unauthenticated Canary `ProtocolStatus` parsing.

The phase introduces:

- strict `ots-security-malformed-packet-plan-v1` data with exact repository authorization and a bounded ordered list of code-owned built-in case identifiers;
- no manifest-provided packet bytes/hex, commands, executables, credentials, hosts, source IPs, target IPs or ports;
- fixed cases for zero/oversized frame lengths, truncated declared bodies, unknown service selection and truncated/unknown status payloads;
- a canonical security-owned runtime runner that reuses `run_runtime` instead of duplicating Canary lifecycle;
- destination confinement to callback-provided literal `127.0.0.1`;
- distinct deterministic code-owned loopback sources for each malformed probe and its control probe, preventing independent production admission/status-query throttles from invalidating parser-resilience assertions without disabling those protections;
- malformed-connection termination checks plus exactly one normal XML status control probe after every case;
- fatal/sanitizer log diagnostics and outer process-liveness enforcement;
- deterministic `ots-security-malformed-packet-report-v1` evidence with plan, provider and exact Canary binary SHA-256 pins;
- dedicated exact-head Security Validation runtime execution on disposable MySQL + Canary infrastructure.

Initial runtime attempts failed without a Canary crash because the harness reused source IPs across unrelated checks. Source review proved two independent protections: `Ban::acceptConnection` can reject excessive rapid accepted connections per IP, and `ProtocolStatus::ipConnectMap` rate-limits repeated status queries for non-exempt source addresses. The corrected runner assigns separate malformed/control source addresses per case and preserves both production protections.

Exact-head head `979e69be26b3d383e6fe7971e1797f6fbd9eea4c` passed focused security validation, repository CI, Agent Task Ownership, exact-head Linux release build and the real eight-case malformed status-parser runtime.

OTS-SEC-003 does not claim authenticated login/game, XTEA, checksum/sequence, maintained-client hostile-server, packet-flood or sustained-DoS coverage.

# Ordered queue

1. `DONE` — OTS-SEC-001 foundation merged in PR #433.
2. `DONE` — OTS-SEC-002 runtime delegation adapter merged in PR #440.
3. `ACTIVE` — OTS-SEC-003 bounded common-framing + unauthenticated `ProtocolStatus` runtime scenarios in PR #451.
4. Add authenticated login/game parser and session scenarios, including protocol-aware checksum/sequence/XTEA boundaries, through separate bounded tasks.
5. Add authenticated session, race, economy and transaction-abuse scenarios with disposable MariaDB state assertions.
6. Add Redis/multichannel failure and ownership scenarios without targeting shared or production infrastructure.
7. Add maintained-client hostile-server scenarios through an explicit cross-repository contract.
8. Add MyAAC web/auth/session scenarios against a pinned disposable MyAAC build.
9. Register Otheryn as a target adapter and require migrated security regressions to pass before declaring a security-sensitive migration preserved.

# Safety invariants

- Only repository-owner-authorized targets may be executed.
- No arbitrary public-target discovery or scanning.
- Runtime attack scenarios use disposable/isolated infrastructure unless an exact alternative target is explicitly authorized.
- No production credentials, database dumps, private data or secrets in manifests/reports.
- Scenario and adapter manifests never contain arbitrary shell commands or arbitrary packet payloads.
- Generic E2E/load lifecycle infrastructure is reused rather than forked.
- Runtime packet corpora and source-address strategies are code-owned and reviewable.
- A green static scenario, delegation proof or bounded runtime pack is evidence for that exact assertion only; it never proves complete exploit resistance.
- Confirmed vulnerabilities become permanent regressions after the fix is merged.

# Handoff

Start from `AGENTS.md`, `docs/agents/CONTEXT_ROUTING.md`, this program, `docs/security/SECURITY_VALIDATION_PLATFORM.md`, the active security task and live PR. Load the Universal E2E route only when a task actually introduces or consumes runtime execution/delegation. For OTS-SEC-003 specifically, treat `tools/e2e/run_agent_load_runtime.py` as the reused lifecycle boundary and keep authenticated login/game protocol coverage in separate tasks.
