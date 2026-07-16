# ADR: Security validation platform boundary

- Status: Accepted
- Date: 2026-07-16
- Decision ID: `OTS-SEC-001`

## Context

Security validation for the evolving OTS stack must eventually cover the server, maintained client, MyAAC, MariaDB and Redis and must remain useful when security-sensitive behavior migrates from Canary into Otheryn.

The repository already has a Universal OTS E2E platform that owns disposable MariaDB/Canary/OTClient lifecycle, assertions, evidence and cleanup, plus a separate bounded Universal Agent Load runner. Building a new security-specific full-stack launcher would duplicate lifecycle logic and create competing safety boundaries.

Security scenarios also need a durable regression registry. Allowing JSON manifests to carry arbitrary commands or network targets would turn the registry itself into an execution boundary that is difficult to review and unsafe to reuse across repositories.

## Decision

Create one product-neutral security scenario/report contract under `tools/security/**` and `tests/security/**`.

The foundation supports only a built-in `source-regex` executor. Manifests are strict data, not scripts: unknown fields are rejected and there is no command/plugin field. Execution requires the caller to provide an exact authorized repository that matches the scenario record.

Future runtime security adapters will be explicit code-owned adapters. They must reuse Universal OTS E2E for lifecycle capabilities already owned there and must add only security-specific drivers/assertions. Load/stress scenarios reuse the Universal Agent Load layer where applicable.

Target-specific names such as Canary, Otheryn, the maintained client and MyAAC belong in adapter/scenario configuration. The core `ots-security-scenario-v1` and `ots-security-validation-report-v1` contracts remain product-neutral.

## Consequences

### Positive

- Confirmed security fixes can become stable, machine-readable regressions.
- Otheryn migrations can rerun the same security intent through a new adapter rather than rewriting the platform.
- Runtime offensive capability can grow without duplicating disposable-environment orchestration.
- Manifests cannot directly introduce arbitrary shell/network execution.
- Reports are deterministic and pin inspected source bytes by SHA-256.

### Trade-offs

- Phase 1 is intentionally static and does not prove runtime exploit resistance.
- Each new runtime capability requires a reviewed adapter implementation rather than a free-form manifest command.
- Cross-repository client/web adapters need their own authorization and compatibility contracts before execution.

## Rejected alternatives

### Build a second security-specific Docker/E2E stack

Rejected because Universal OTS E2E already owns the required lifecycle and evidence responsibilities.

### Put arbitrary commands in scenario JSON

Rejected because it would make data manifests an unbounded code-execution interface and weaken reviewability.

### Tie the registry permanently to Canary

Rejected because Otheryn is the target server evolution path and the same security regressions must be portable across adapters.
