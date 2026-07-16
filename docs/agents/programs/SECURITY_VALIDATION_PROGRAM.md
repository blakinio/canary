---
program_id: CAN-PROGRAM-SECURITY-VALIDATION
name: OTS Security Validation Platform
status: active
owner: security-validation-agent
created: 2026-07-16T20:10:00+02:00
updated: 2026-07-16T22:20:00+02:00
last_verified_commit: "6503f5312dbf13d0fddcc1da98a10343ed30525c"
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

Build one reusable security-validation layer for the OTS ecosystem that preserves confirmed security fixes as deterministic regressions and later drives authorized offensive tests against disposable server, client, web, database and cache targets.

The platform is not permanently tied to Canary. Canary is the first source/runtime adapter because it is the currently authorized implementation repository. Otheryn and the maintained client are future target adapters, not reasons to duplicate the core scenario/report contracts.

# Existing foundations to reuse

- Universal OTS E2E owns disposable database/server/client lifecycle, controlled OTClient execution, SQL/protocol assertions, artifacts and cleanup.
- Universal Agent Load owns literal-loopback-only bounded status-protocol load/stress evidence.
- Existing focused regressions remain authoritative implementation-level evidence and should be referenced by security scenarios rather than rewritten.
- Repository CI and exact-final-head merge gates remain the delivery boundary.

# Platform responsibility

The security platform owns:

- versioned security-scenario discovery and validation;
- explicit target authorization metadata;
- target-adapter selection contracts;
- security-specific static and future runtime executors;
- deterministic machine-readable findings and source/runtime evidence references;
- permanent regression registration after confirmed remediation;
- orchestration of approved security adapters without granting manifests arbitrary command execution.

It does not own generic server/database/client bootstrap already provided by Universal OTS E2E.

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

Active in PR #440. This bounded phase adds the code-owned `canary-universal-e2e` adapter and must:

- keep Universal OTS E2E lifecycle code read-only;
- resolve delegated suite/scenario metadata through the existing E2E resolver;
- require an exact authorized repository match;
- enforce a literal-loopback-only resolved fixture host;
- restrict the controlled client to the approved user-owned client repository for the provider;
- pin the canonical Universal E2E workflow, resolver, physical runner and selected scenario by SHA-256;
- emit deterministic `ots-security-runtime-delegation-v1` evidence;
- keep arbitrary commands, executable paths, credentials and free-form network targets out of adapter manifests.

This phase proves the runtime delegation boundary. It does not yet send malformed packets or add a generic attack-driver hook to Universal E2E.

# Ordered queue

1. `DONE` — OTS-SEC-001 foundation merged in PR #433.
2. `ACTIVE` — OTS-SEC-002 runtime delegation adapter in PR #440.
3. Add bounded malformed-packet/parser scenarios against the disposable server with crash/hang diagnostics and sanitizer-compatible evidence (`OTS-SEC-003`).
4. Add authenticated session, race, economy and transaction-abuse scenarios with disposable MariaDB state assertions.
5. Add Redis/multichannel failure and ownership scenarios without targeting shared or production infrastructure.
6. Add maintained-client hostile-server scenarios through an explicit cross-repository contract.
7. Add MyAAC web/auth/session scenarios against a pinned disposable MyAAC build.
8. Register Otheryn as a target adapter and require migrated security regressions to pass before declaring a security-sensitive migration preserved.

# Safety invariants

- Only repository-owner-authorized targets may be executed.
- No arbitrary public-target discovery or scanning.
- Runtime attack scenarios use disposable/isolated infrastructure unless an exact alternative target is explicitly authorized.
- No production credentials, database dumps, private data or secrets in manifests/reports.
- Scenario and adapter manifests never contain arbitrary shell commands.
- Generic E2E lifecycle and load infrastructure are reused rather than forked.
- A green static scenario or runtime-delegation proof is evidence for that exact assertion only; it never proves complete exploit resistance.
- Confirmed vulnerabilities become permanent regressions after the fix is merged.

# Handoff

Start from `AGENTS.md`, `docs/agents/CONTEXT_ROUTING.md`, this program, `docs/security/SECURITY_VALIDATION_PLATFORM.md`, the active security task and live PR. Load the Universal E2E route only when a task actually introduces or consumes runtime execution/delegation.
