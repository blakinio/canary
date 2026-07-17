# CAN-20260717 — MyAAC / Canary security audit record

## Status

Active documentation task.

## Goal

Preserve the isolated offensive-security assessment of the Canary Docker quickstart, MyAAC integration, and the external login-server dependency as durable repository evidence. This task records findings only; it does not modify upstream repositories or implement remediations.

## Routes

- `agent-governance`
- `cross-repo` for documenting authentication and login-policy boundaries involving the read-only `opentibiabr/login-server` dependency

## Authorization and repository boundary

- Writable repository: `blakinio/canary` only.
- `opentibiabr/canary`, `opentibiabr/login-server`, `slawkens/myaac`, `opentibiabr/otclient`, `opentibiabr/remeres-map-editor`, and `opentibiabr/client-editor` are evidence sources only and remain read-only.
- No public or third-party deployment was tested.

## Owned paths

- `docs/security/MYAAC_CANARY_SECURITY_AUDIT_2026-07-17.md`
- `docs/agents/tasks/active/CAN-20260717-myaac-canary-security-audit.md`

## Scope

The report consolidates:

- source review of MyAAC account, admin, CSRF, reset, session, template, plugin, FAQ, status, and rate-limit paths;
- source review of Canary Docker quickstart integration;
- source review of the external `opentibiabr/login-server` authentication, HTTP, gRPC, rate-limit, session, and dependency behavior;
- isolated local PHP/Python harness tests reproducing selected current-source logic;
- explicit limitations where Docker, MariaDB/MySQL, Composer, GD, ZipArchive, or full E2E integration were unavailable.

## Evidence model

- `PROVEN`: directly reproduced in an isolated local harness or revalidated against the current `blakinio/canary:main` source.
- `DERIVED`: strongly supported by source composition but not executed end-to-end in the target stack.
- `UNKNOWN`: requires a real isolated MyAAC + MariaDB + Canary + login-server environment or unavailable runtime extension.
- Rejected hypotheses are retained in the report where useful to prevent rediscovery.

## Acceptance criteria

- [ ] Consolidated report committed under `docs/security/`.
- [ ] Report distinguishes proven, derived, configuration-dependent, and unverified findings.
- [ ] Report contains no private secrets, private logs, local absolute paths, or production-target instructions.
- [ ] Current Canary quickstart observations are revalidated against the branch base.
- [ ] Draft PR targets `blakinio/canary:main` from the dedicated task branch.
- [ ] Documentation-only diff reviewed for unrelated or forbidden files.

## Context checkpoint

### Current state

- Branch: `docs/myaac-canary-security-audit-20260717`.
- Base commit: `35b9f7d734add288c7c3b9f6be733807d8329c4a`.
- No overlapping open PR was found by a narrow search for MyAAC, login-server, security-audit, or Docker-quickstart work.
- Current fork `docker/docker-compose.yml`, `docker/quickstart/myaac/bootstrap.php`, and `docker/quickstart/myaac/entrypoint.sh` were re-read at the base commit and still contain the integration surfaces referenced by the audit.

### Key evidence

- `PROVEN`: MyAAC local harnesses reproduced password-in-GET logging, GET-CSRF behavior, admin log path traversal, log-viewer raw XSS sink, non-expiring reset-code logic, reset-code URL leakage, non-CSPRNG token generation, disabled-cache limiter bypass, missing `Secure` session cookie, config-expression `eval`, and a non-atomic limiter race.
- `PROVEN`: the rate-limit race harness recorded only 4 increments from 40 concurrent attempts.
- `PROVEN`: the template-selection harness demonstrated constrained traversal/self-include behavior for a parent-directory selector.
- `PROVEN`: current Canary quickstart publishes both login-server HTTP and gRPC ports and builds MyAAC from a rolling development ref by default.
- `PROVEN`: current Canary MyAAC bootstrap adds `email_verified` and grants the bootstrapped administrator high web/server privileges.
- `DERIVED`: direct gRPC access bypasses the HTTP-only rate limiter in the external login-server.
- `DERIVED`: MyAAC verification/TOTP/login-mode policies are not uniformly enforced by the external login-server authentication query.
- `DERIVED`: the MyAAC quickstart status target defaults to loopback inside the MyAAC container, while the Canary server is a separate Compose service.

### Limitations

- No full-stack MariaDB/MySQL E2E execution was available in the original lab.
- No real GD image-decoder or ZipArchive/libzip testing was available.
- No public deployment was attacked or scanned.
- External dependency findings are documented for Canary integration risk; remediation in read-only upstream repositories is outside this task.

### next_action

Commit the consolidated security report, review the branch diff, and keep the PR as documentation/evidence unless a separate bounded remediation task is opened.
