---
program_id: CAN-PROGRAM-SECURITY-VALIDATION
name: OTS Security Validation Platform
status: active
owner: security-validation-agent
created: 2026-07-16T20:10:00+02:00
updated: 2026-07-17T00:25:00+02:00
last_verified_commit: "35b9f7d734add288c7c3b9f6be733807d8329c4a"
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

Merged in PR #433. The foundation supports `source-regex` scenarios with:

- strict exact-field JSON validation;
- repository-relative regular-file confinement;
- symlink/path-escape and size rejection;
- forbidden/required regex assertions;
- explicit repository authorization checked at execution time;
- deterministic `ots-security-validation-report-v1` output with SHA-256 source evidence;
- seeded regressions for merged PRs #326 and #328;
- focused tests and dedicated workflow.

No network or runtime offensive action is part of Phase 1.

# Phase 2 — runtime delegation adapter (`OTS-SEC-002`)

Merged in PR #440. This phase added the code-owned `canary-universal-e2e` adapter and:

- kept Universal OTS E2E lifecycle code read-only;
- resolved delegated suite/scenario metadata through the existing E2E resolver;
- required an exact authorized repository match;
- enforced a literal-loopback-only resolved fixture host;
- restricted the controlled client to the approved user-owned client repository for the provider;
- pinned the canonical Universal E2E workflow, resolver, physical runner and selected scenario by SHA-256;
- emitted deterministic `ots-security-runtime-delegation-v1` evidence;
- kept arbitrary commands, executable paths, credentials and free-form network targets out of adapter manifests.

Its lifecycle record was archived before OTS-SEC-003 began.

# Runtime-hook dependency (`OTS-SEC-003-RUNTIME-HOOK`)

Merged in PR #444 with lifecycle completed in PR #450. This narrow E2E-platform dependency exposes the existing Universal Agent Load exact-head Canary lifecycle through a typed in-process `RuntimeContext` / `run_runtime` callback while preserving the existing load CLI.

The callback is intentionally code-owned: manifests cannot provide commands, executables or target hosts. It owns map/database/config/server startup and cleanup, invokes one caller-supplied in-process executor only after Canary reports online, and verifies the process remains alive afterward.

# Phase 3 — malformed framing/status parser runtime (`OTS-SEC-003`)

Active in PR #451. This first offensive runtime phase is intentionally bounded to common TCP framing and unauthenticated Canary `ProtocolStatus` parsing.

The phase introduces:

- strict `ots-security-malformed-packet-plan-v1` data with exact repository authorization and a bounded ordered list of code-owned built-in case identifiers;
- no manifest-provided packet bytes/hex, commands, executables, credentials, hosts, IP targets or ports;
- fixed cases for zero/oversized frame lengths, truncated declared bodies, unknown service selection and truncated/unknown status payloads;
- a canonical security-owned runtime runner that reuses `run_runtime` instead of duplicating Canary lifecycle;
- literal `127.0.0.1` confinement inherited from the runtime callback context;
- malformed-connection termination checks plus a normal XML status control probe after every case;
- bounded service-recovery semantics after asynchronous connection cleanup: four code-owned attempts separated by 50 ms, normalized to deterministic `pass`/`control-unresponsive` report outcomes;
- fatal/sanitizer log diagnostics and outer process-liveness enforcement;
- deterministic `ots-security-malformed-packet-report-v1` evidence with plan, provider and exact Canary binary SHA-256 pins;
- dedicated exact-head Security Validation runtime execution on disposable MySQL + Canary infrastructure.

The first implementation runtime proved zero-length and oversized framing cases and reproduced a scheduler-immediate control failure after the truncated-body EOF path without a Canary crash or fatal/sanitizer finding. The canonical runner was then narrowed to bounded recovery semantics rather than dropping the case or weakening the gate to process liveness only. Exact-head validation of that repair remains the current delivery boundary.

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
- Runtime packet corpora and recovery limits are code-owned and reviewable.
- A green static scenario, delegation proof or bounded runtime pack is evidence for that exact assertion only; it never proves complete exploit resistance.
- Confirmed vulnerabilities become permanent regressions after the fix is merged.

# Handoff

Start from `AGENTS.md`, `docs/agents/CONTEXT_ROUTING.md`, this program, `docs/security/SECURITY_VALIDATION_PLATFORM.md`, the active security task and live PR. Load the Universal E2E route only when a task actually introduces or consumes runtime execution/delegation. For OTS-SEC-003 specifically, treat `tools/e2e/run_agent_load_runtime.py` as the reused lifecycle boundary and keep authenticated login/game protocol coverage in separate tasks.
