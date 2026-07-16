# TSD-011 — Analytics, Security and AI Decomposition

> Task-start main: `c67c84749ffd1de04983be9ae9841b6ca5756aed`.
> Inventory only; no analytics completeness, security assurance, AI capability or production-readiness claim.

## Result

Registry grows from **60** to **61** records. Existing records remain unchanged.

Added only:

- `gameplay-analytics`.

Preserved unchanged:

- `account-authentication`;
- `sanctions`;
- `protocol`;
- `upstream-intelligence`;
- `otbm-tooling`;
- `physical-client-e2e`;
- all validation/audit tools and gameplay modules.

## Evidence inventory

### Gameplay Analytics

The current repository contains one independent durable analytics root: Gameplay Analytics. It has an optional Lua runtime with its own session model and lifecycle, bounded queues, retry/dead-letter handling, optional persistence, deterministic dry-run validators, MariaDB-backed validation/reporting surfaces and dedicated operational documentation.

The subsystem is disabled by default. Existing dry-run and database tests establish current implementation/test inventory only; they do not prove production runtime ordering, persistence under load, privacy, retention, telemetry completeness or gameplay-data correctness.

### Security boundaries

Credential verification, password hashing and short-lived login-token handling already belong to `account-authentication`. Connection throttling and account/IP/namelock sanctions already belong to `sanctions`. TSD-011 does not duplicate those boundaries under a new generic security module.

No independent current `security-analytics` lifecycle is registered. Creating one would implement or predeclare a planned system explicitly forbidden by this program.

### AI boundaries

Current `tools/ai-agent/**` content consists primarily of deterministic validation, OTBM, audit and evidence tooling. Those reusable validation/live-operations surfaces belong to TSD-012 classification and existing module records where already present. TSD-011 does not create a generic `ai-agent-tooling` umbrella and does not register or implement `ai-investigation`.

## Candidate decisions

| Candidate | Decision | Reason |
|---|---|---|
| `gameplay-analytics` | `ADD_NOW` | independent optional telemetry session/queue/retry/dry-run/reporting lifecycle with verified current roots |
| `authentication-security` | `ALREADY_COVERED` | password verification, hashing and login-token lifecycle remain `account-authentication` |
| `sanction-security` | `ALREADY_COVERED` | connection throttling and account/IP/namelock sanctions remain `sanctions` |
| `security-analytics` | `DEFER` | planned system explicitly forbidden; no independent current root may be invented |
| `chat-safety-intelligence` | `DEFER` | planned system explicitly forbidden |
| `ai-investigation` | `DEFER` | planned system explicitly forbidden |
| `ai-agent-tooling` | `DEFER` | broad umbrella would duplicate heterogeneous validators/OTBM tooling and preempt TSD-012 |
| existing OTBM validators | `ALREADY_COVERED` | preserve canonical `otbm-tooling`; no second parser/indexer/renderer |
| Upstream Intelligence | `ALREADY_COVERED` | preserve existing independent `upstream-intelligence` platform boundary |
| physical-client validation | `ALREADY_COVERED` | preserve `physical-client-e2e`; no second E2E orchestrator |
| individual analytics metrics/dashboards | `REJECT_AS_TOO_GRANULAR` | data dimensions and reporting assets, not independent module lifecycles |

## Dependencies

- `gameplay-analytics` depends on `lua-runtime`.
- It interacts with combat, database connection, parties, player persistence and world-map context without taking ownership of those domains.

The new record begins at lifecycle/implementation/evidence `inventory`; persistence, protocol, automated tests, runtime validation and gameplay E2E remain `not-assessed` under the decomposition program's conservative baseline.

## Discovery expectations

```text
data-otservbr-global/scripts/config/gameplay_analytics.lua
  → gameplay-analytics
data-otservbr-global/scripts/lib/gameplay_analytics.lua
  → gameplay-analytics
data-otservbr-global/scripts/systems/gameplay_analytics.lua
  → gameplay-analytics
tools/analytics/**
  → gameplay-analytics
.github/workflows/gameplay-analytics-dry-run.yml
  → gameplay-analytics
```

The runtime/data paths are Canary-side evidence. TSD-011 introduces no maintained-client mapping and no AI-generated runtime implementation.

## Evidence limits

TSD-011 does not prove telemetry completeness, metric semantics, queue durability, database transactionality, privacy, retention, production runtime stability, security posture, abuse detection, anomaly detection, AI investigation capability, physical-client E2E, Real Tibia parity or Oteryn readiness.

No `security-analytics`, `chat-safety-intelligence` or `ai-investigation` system is implemented or registered by this package.

## Next package

After feature merge and lifecycle archive:

```text
task: CAN-20260714-tibia-system-decomposition-validation-live-operations
package: TSD-012
branch: docs/tibia-system-decomposition-validation-live-operations
```
