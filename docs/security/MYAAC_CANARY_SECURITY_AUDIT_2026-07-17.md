# MyAAC / Canary / login-server security audit

Date: 2026-07-17

Status: security evidence and remediation input; not a production penetration-test certification.

## Executive summary

This document preserves an isolated offensive-security assessment of the MyAAC website/admin layer used by the Canary Docker quickstart, the Canary quickstart integration itself, and the external `opentibiabr/login-server` dependency used as the default client login webservice.

The assessment found multiple independent security weaknesses. The highest-priority themes are:

1. authentication policy is split across MyAAC and the external login-server and is not enforced consistently;
2. the quickstart publishes the login-server gRPC port even though the HTTP service is the intended client-facing layer, creating an alternate path around HTTP-only rate limiting;
3. the HTTP rate limiter trusts spoofable forwarded-IP headers unless trusted proxies are configured;
4. several MyAAC state-changing actions are reachable through request methods that bypass the current CSRF design;
5. MyAAC contains file-read, reset-token, rate-limit, XSS, weak-token-generation, and session-hardening weaknesses;
6. Canary quickstart composition amplifies some of those weaknesses through permissive defaults, a rolling MyAAC development ref, and a status-targeting mismatch between containers.

No public or third-party deployment was attacked, scanned, or fuzzed. Dynamic tests were limited to isolated local harnesses reproducing current-source logic.

## Repository and source baselines

### Canary fork

The report was committed from `blakinio/canary` and revalidated against the task branch base derived from `main` on 2026-07-17.

The following current fork files were re-read before publishing this report:

- `docker/docker-compose.yml`
- `docker/quickstart/myaac/bootstrap.php`
- `docker/quickstart/myaac/entrypoint.sh`

At the revalidation point, the quickstart still:

- builds MyAAC from a configurable ref whose default is the rolling `develop` branch;
- publishes MyAAC HTTP to the host;
- publishes both login-server HTTP and gRPC ports to the host;
- seeds static local-development account/database credentials unless the operator overrides them;
- creates a highly privileged MyAAC/Canary administrator account during bootstrap;
- generates the MyAAC-local Canary configuration with a loopback server IP by default;
- uses SHA-1 as the quickstart password hashing mode.

This report intentionally does not reproduce credential values.

### MyAAC

The audit referenced `slawkens/myaac` source around observed commit:

`a526b7e4363af53ea818c1f75b13a0c8c3248b72`

Canary quickstart currently defaults to a rolling MyAAC `develop` ref, so every remediation task must revalidate the exact MyAAC commit built by the target deployment before patching.

### login-server

The external login-server source reviewed during the audit was around commit:

`2612930de4d97123a397f8f2cd0d5f784094af40`

The repository is an upstream/read-only evidence source for this task.

## Evidence states

- **PROVEN** — directly reproduced in an isolated local harness or directly revalidated in current Canary fork source.
- **DERIVED** — strongly supported by source composition and control flow, but not executed end-to-end in the complete target stack.
- **CONFIGURATION-DEPENDENT** — reachable only when a related optional feature is enabled or the service is exposed beyond the documented local-only boundary.
- **UNKNOWN** — requires a real isolated full stack or an unavailable runtime dependency to validate.

## Lab limitations

Available in the original isolated lab:

- PHP 8.4.x CLI and built-in HTTP server;
- Python 3.13.x;
- local filesystem and process concurrency.

Unavailable in the original lab:

- Docker runtime;
- MySQL/MariaDB server and client;
- Composer runtime operations;
- PHP `pdo_mysql` and `mysqli` extensions;
- PHP GD;
- PHP ZipArchive/libzip;
- a fully integrated MyAAC + MariaDB + Canary + login-server instance.

Therefore this is not a full black-box or gray-box penetration test of a running production deployment. Findings below distinguish executed proof from source-derived risk.

---

# Findings

## SEC-01 — HIGH — Registration password is sent in a GET URL

Evidence: **PROVEN**

Current MyAAC registration validation sends `password` and `password_confirm` to `tools/validate.php` through an AJAX GET request, and the endpoint reads the values from `$_GET`.

An isolated HTTP harness reproduced the behavior and confirmed that the complete test password appeared in the server access-log request URL.

### Impact

Passwords can be copied into:

- web-server access logs;
- reverse-proxy logs;
- WAF logs;
- APM or tracing systems;
- browser/network diagnostic history.

### Recommendation

Remove password validation from GET entirely. Validate client-side for usability and validate again on the final account-creation POST. If an asynchronous server check is retained, use POST and do not log request bodies containing credentials.

---

## SEC-02 — HIGH — CSRF validation treats non-POST requests as valid

Evidence: **PROVEN**

The MyAAC CSRF helper accepts every non-POST request without requiring a token. Multiple state-changing paths are reachable through GET-capable routes or request variables.

An isolated authenticated harness reproduced a state-changing GET request without a CSRF token and successfully deleted the test resource.

Affected patterns observed during review include:

- gallery delete/hide/reorder operations;
- forum board administration operations;
- limited-role forum moderator actions;
- guild rank-saving paths that use request data in state-changing code.

### Impact

An authenticated victim can be induced to perform unwanted mutations by visiting or loading a crafted link.

### Recommendation

- Restrict every state-changing operation to POST/PUT/PATCH/DELETE as appropriate.
- Reject GET for mutations at the router and handler level.
- Validate CSRF tokens for all unsafe methods.
- Avoid `$_REQUEST` for mutation parameters.

---

## SEC-03 — HIGH — Admin log viewer path traversal / arbitrary readable-file disclosure

Evidence: **PROVEN**

The MyAAC admin log viewer accepts a file parameter, permits path separators and dots, concatenates the value to the log directory, and reads the resulting path without a canonical containment check.

Isolated CLI and HTTP harnesses reproduced traversal outside the log directory and read files available to the PHP process.

### Impact

A user who can access the admin log viewer can expand that privilege into disclosure of arbitrary locally readable files, potentially including application configuration.

### Recommendation

- Never accept arbitrary relative paths from the request.
- Enumerate available log files server-side and accept an opaque identifier or exact allowlisted basename.
- Resolve with `realpath()` and verify containment inside the expected log root before opening.

---

## SEC-04 — HIGH, configuration-dependent — Stored XSS through raw admin log rendering

Evidence: **PROVEN**, **CONFIGURATION-DEPENDENT**

The admin log template renders log content as raw HTML. When database logging is enabled, attacker-controlled request data can be written to a log and later rendered without HTML escaping.

An isolated chain stored an HTML event payload in a log-like file and confirmed that the viewer emitted it unchanged.

### Impact

An attacker who can inject content into a viewed log may execute script in an administrator's MyAAC origin.

### Recommendation

Render log content as escaped text, preferably inside a `<pre>` block. Never apply Twig `|raw` to untrusted log data.

---

## SEC-05 — HIGH — Password-reset code has no enforced expiry

Evidence: **PROVEN**

The lost-account flow stores a reset code and a separate mail-send cooldown, but reset-code validation compares only the submitted code. The reset path does not enforce an issue time or expiry time.

An isolated logic harness modeled a code issued one year earlier and the current validation logic still accepted it.

### Impact

A leaked reset bearer token can remain valid far longer than intended until it is used or replaced.

### Recommendation

- Generate a cryptographically random token.
- Store only a hash of the token.
- Store issue and expiry timestamps.
- Enforce a short TTL.
- Consume the token atomically on successful use.

---

## SEC-06 — MEDIUM — Password-reset bearer code appears in the query string

Evidence: **PROVEN**

The reset flow places the reset code in a URL query parameter. An isolated HTTP harness confirmed that the token appears in the access-log request line.

### Impact

Reset bearer material may persist in web-server, proxy, WAF, analytics, or browser logs.

### Recommendation

Use a short-lived, one-time reset token and minimize its lifetime in URLs. Scrub the query from subsequent navigation and avoid logging sensitive query parameters.

---

## SEC-07 — MEDIUM — Security-sensitive random strings use `mt_rand()`

Evidence: **PROVEN**

MyAAC's shared random-string helper uses PHP `mt_rand()` and is used in security-sensitive contexts including reset codes, recovery keys, and token construction.

An isolated deterministic-seed harness reproduced identical generated values from identical MT state.

### Impact

The generator is not a CSPRNG and should not be used for bearer secrets or recovery material.

This finding does **not** claim that remote PRNG-state recovery was demonstrated.

### Recommendation

Use `random_bytes()` / `random_int()` and store hashes of bearer tokens where practical.

---

## SEC-08 — MEDIUM — Login rate limiting silently stops working when cache is disabled

Evidence: **PROVEN**

The MyAAC rate limiter increments attempts only when the configured cache backend reports itself enabled.

An isolated exact-logic harness produced:

- cache disabled: repeated increments remained at zero and the limit was never exceeded;
- cache enabled: attempts increased as expected.

### Recommendation

Authentication rate limiting must not silently fail open because a performance cache is unavailable. Use a dedicated persistent/atomic rate-limit backend or an explicit fail-safe strategy.

---

## SEC-09 — HIGH — MyAAC rate limiter loses increments under concurrency

Evidence: **PROVEN**

The current limiter performs a non-atomic read-modify-write cycle over shared serialized cache state.

In an isolated multiprocess race harness:

- 40 concurrent increments were issued;
- only 4 attempts were recorded.

### Impact

Parallel password guessing can lose most limiter increments, substantially weakening brute-force protection even when cache is enabled.

### Recommendation

Use an atomic backend primitive such as `INCR` with TTL semantics, or protect the complete read-modify-write transaction with a shared lock that works across processes/hosts.

---

## SEC-10 — MEDIUM — Session cookie lacks the `Secure` attribute

Evidence: **PROVEN**

Isolated HTTP and simulated HTTPS-context tests showed MyAAC setting `HttpOnly` and `SameSite` but not `Secure` on the PHP session cookie.

### Impact

If the application is ever reachable over plain HTTP or proxy/TLS detection is misconfigured, the session cookie has weaker transport protection.

### Recommendation

Set `Secure` for HTTPS deployments and implement explicit trusted-proxy-aware scheme detection where TLS terminates upstream.

---

## SEC-11 — HIGH strategic risk — SHA-1 remains the quickstart password hashing mode

Evidence: **PROVEN** for current Canary quickstart configuration; offline weakness demonstrated locally.

The current quickstart generates Canary/MyAAC configuration using SHA-1 password hashing. Canary supports stronger password handling in other code paths, but the quickstart integration continues to select SHA-1.

A small offline demonstration confirmed that SHA-1 comparisons are extremely cheap once a password database is disclosed.

### Recommendation

Design a coordinated Argon2id migration across Canary, MyAAC, and the login-server authentication path. The migration must be treated as a shared authentication contract, not a one-sided configuration edit.

---

## SEC-12 — MEDIUM — Parsed `config.lua` expressions can reach PHP `eval()`

Evidence: **PROVEN at the sink**

MyAAC evaluates certain unquoted configuration expressions using PHP `eval()`.

An isolated harness passed a function-call expression and confirmed code execution at the sink.

### Qualification

No unauthenticated remote configuration-injection primitive was demonstrated. Exploitation requires control over a parsed configuration value or an equivalent write primitive.

### Recommendation

Replace `eval()` with a strict parser for the limited numeric/arithmetic syntax required by configuration values.

---

## SEC-13 — MEDIUM — Public account/email enumeration

Evidence: **DERIVED**

The public validation endpoint returns distinguishable responses for existing account identifiers and, when unique-email enforcement is enabled, existing email addresses.

### Impact

Attackers can improve credential-stuffing, phishing, and account-target selection.

### Recommendation

Return generic availability responses where possible and apply robust endpoint-level rate limiting.

---

## SEC-14 — MEDIUM — Lost-account and recovery paths lack dedicated robust rate limiting

Evidence: **DERIVED**

Recovery-key comparison and lost-account guessing paths do not consistently use a dedicated brute-force limiter. The mail cooldown is an account workflow cooldown, not a general source-IP abuse control.

### Recommendation

Apply atomic rate limits by account identifier and trusted client IP, with careful anti-enumeration behavior.

---

## SEC-15 — MEDIUM — Recovery flows display or email a newly generated password

Evidence: **DERIVED**

Reviewed recovery flows return or email a generated plaintext password.

### Impact

Passwords become exposed to mailbox retention, forwarding, support systems, and potentially logs.

### Recommendation

Use a one-time reset flow where the user chooses a new password over an authenticated reset session. Do not email plaintext passwords.

---

## SEC-16 — MEDIUM — Anonymous template selector permits constrained parent-directory traversal

Evidence: **PROVEN**

The template-selection flow validates the existing template value and then assigns a request-provided template value that is later used in path construction.

An isolated path-selection harness showed that a parent-directory selector resolved to the application root and selected the application's own `index.php`, producing a self-include condition.

### Impact

Confirmed impact is constrained traversal/self-include behavior with potential error or memory-exhaustion DoS. Arbitrary file disclosure or RCE was not demonstrated.

### Recommendation

Select templates only from a server-generated allowlist of installed template directory names. Never use raw request values in filesystem path selection.

---

## SEC-17 — MEDIUM — Limited FAQ content role can store event-handler XSS

Evidence: **PROVEN at HTML filtering layer**

A user with the FAQ content flag can save FAQ content. Rendering strips disallowed tags while explicitly preserving tags such as `<span>`, then emits the result as raw HTML.

An isolated exact-PHP filtering test confirmed that event-handler attributes on an allowed element survived filtering.

### Qualification

A browser-based zero-click execution chain was not proven in the original sandbox. The confirmed issue is stored active HTML/event-handler content that can execute with suitable user interaction.

### Recommendation

Use an allowlist HTML sanitizer that validates both tags and attributes. Do not rely on `strip_tags()` as an XSS sanitizer.

---

## SEC-18 — MEDIUM — Email change does not reset verification state

Evidence: **DERIVED**

When a verified account changes to a new email address, the reviewed flow updates the email but does not reset the `email_verified` field and does not require verification of the new mailbox.

### Impact

The verification bit can continue to represent the old mailbox while the account now points to a different, never-verified address.

### Recommendation

On email change:

1. verify password/re-authenticate;
2. verify uniqueness under a database constraint;
3. set `email_verified = 0`;
4. send a short-lived verification token to the new address;
5. optionally notify the old address;
6. finalize only after verification.

---

## SEC-19 — MEDIUM — Email uniqueness policy is not consistently enforced during email change

Evidence: **DERIVED**

The reviewed email-change path validates email format but does not consistently enforce the configured unique-email policy before storing the new value. Canary's account schema does not provide a universal database-level unique constraint protecting this policy.

### Impact

Duplicate emails can create ambiguous login/recovery behavior when email-based login is enabled.

### Recommendation

Enforce uniqueness transactionally and back it with an appropriate database constraint when the deployment policy requires one-email-per-account.

---

## SEC-20 — HIGH trust-boundary issue — `FLAG_ADMIN` can reach server-side code execution through plugin installation

Evidence: **DERIVED from source design**

The MyAAC plugin manager is available to the regular admin role when plugin management is enabled. Uploaded plugin archives are installed into the application tree and the plugin installation path executes plugin installer PHP.

### Interpretation

This may be intentional administrative functionality rather than a vulnerability in isolation. However, it means `FLAG_ADMIN` is effectively a code-execution-equivalent role and must not be treated as a limited content-management permission.

### Recommendation

- Disable plugin installation by default in hardened deployments.
- Require the highest privilege tier plus recent re-authentication/MFA.
- Consider an offline deployment workflow rather than runtime arbitrary plugin upload.

---

## SEC-21 — HIGH — Canary quickstart publishes gRPC login port alongside HTTP

Evidence: **PROVEN** for current Canary fork Compose configuration; bypass behavior is **DERIVED** from login-server source.

The Canary quickstart publishes both login-server HTTP and gRPC ports to the host.

The login-server documentation and code structure show HTTP operating over the gRPC login layer, while request rate limiting is installed as Gin HTTP middleware.

Direct external gRPC access therefore bypasses the HTTP middleware layer that contains the IP rate limiter.

### Impact

If the published gRPC port is reachable from an untrusted network, attackers gain an alternate authentication path without the HTTP rate limiter.

### Recommendation

Do not publish the gRPC port to the host by default. Keep it on the internal Compose network unless there is a documented external consumer and equivalent gRPC-side security controls.

---

## SEC-22 — HIGH — HTTP login rate limiter trusts spoofable forwarded IPs

Evidence: **DERIVED**

The external login-server keys its limiter on Gin `ClientIP()`. The reviewed Gin version trusts forwarded-client headers when the connecting proxy is trusted, and the default engine configuration historically trusts all proxy ranges unless explicitly replaced. No login-server call configuring a restricted trusted-proxy set was found in the reviewed source.

### Impact

A remote client may be able to rotate forwarded-IP headers to obtain fresh rate-limit buckets, falsify logged source IPs, or consume a target IP's bucket.

### Recommendation

- Explicitly configure trusted proxies.
- When exposed directly, disable forwarded-IP trust and use the socket peer address.
- Apply the same canonical client-IP policy across MyAAC and login-server.

---

## SEC-23 — HIGH — Login policy configured in MyAAC is not uniformly enforced by login-server

Evidence: **DERIVED**

Canary quickstart adds MyAAC-specific account fields including `email_verified`, but the reviewed login-server authentication query loads an account using `(email OR account name) + SHA-1(password)` and does not include the MyAAC email-verification flag.

The reviewed login-server authentication model also does not include the MyAAC TOTP secret used by the website/game-login PHP path.

### Impact

Depending on deployment configuration:

- MyAAC email-verification requirements can be bypassed for game login;
- an email-only login policy can be bypassed because account name remains accepted;
- TOTP enabled in MyAAC may not protect the external login-server path;
- security settings displayed in the website can provide a false sense of enforcement if the actual client login path is separate.

### Recommendation

Define one canonical authentication contract for MyAAC, Canary, and login-server. Enforcement of password algorithm, account state, email verification, MFA/TOTP, bans/locks, and accepted login identifier must be consistent across every login path.

---

## SEC-24 — HIGH — login-server gRPC dependency is affected by GO-2023-2153 in reviewed source

Evidence: **DERIVED from dependency version and official advisory**

The reviewed login-server source pins `google.golang.org/grpc` v1.37.1. The official Go vulnerability entry GO-2023-2153 describes request-cancellation resource exhaustion in vulnerable grpc-go versions and lists fixed versions newer than the reviewed pin.

### Impact

A reachable gRPC service may be exposed to pre-auth resource exhaustion. The Canary quickstart currently publishes the gRPC port.

### Recommendation

Upgrade grpc-go to a supported fixed version and stop publishing the internal gRPC port by default.

Reference: Go Vulnerability Database, `GO-2023-2153`.

---

## SEC-25 — MEDIUM/HIGH — login-server HTTP service lacks explicit server timeouts and login body limit

Evidence: **DERIVED**

The reviewed login-server starts HTTP using bare `http.ListenAndServe()` without explicit read-header/read/write/idle timeout configuration. The crash-report endpoint has an explicit body-size limit, while the login endpoint does not have an equivalent application-level cap in the reviewed code.

### Impact

When exposed directly, slow connections or oversized request bodies can consume server resources. Spoofable-IP rate-limit bypass increases the practical attack surface.

### Recommendation

Use an explicit `http.Server` with hardened timeouts, maximum header size, and bounded login request bodies.

---

## SEC-26 — MEDIUM — Successful login can create persistent session rows even when default password auth mode does not use them

Evidence: **DERIVED**

The reviewed gRPC login flow creates a random 24-hour `account_sessions` record after successful authentication. Canary's default runtime configuration uses password-based session authentication, and the HTTP response path can replace the generated random session key with the password-mode credential form.

### Impact

Repeated successful logins can grow `account_sessions`; direct gRPC access without the HTTP limiter can amplify this behavior.

### Recommendation

Create persistent session rows only when session-mode authentication actually requires them, and enforce cleanup, per-account/session limits, and rate limiting.

---

## SEC-27 — MEDIUM — Canary quickstart MyAAC status target defaults to container loopback

Evidence: **PROVEN** for current Canary fork configuration and MyAAC status-source behavior; end-to-end runtime effect is **DERIVED**.

The current MyAAC quickstart entrypoint generates `/canary/config.lua` using the quickstart server IP default, which is loopback. MyAAC reads the Lua `ip` value for status polling.

Because MyAAC and Canary are separate Compose services, loopback inside the MyAAC container refers to the MyAAC container, not the Canary `server` service.

The reviewed MyAAC status code updates `lastCheck` only after a successful server response. Failed checks can therefore remain immediately eligible for another poll, causing repeated socket attempts and status persistence work on public page requests.

### Recommendation

Use a dedicated internal status host such as the Compose service name for MyAAC status checks. Track failed-check timestamps and apply backoff/caching regardless of success.

---

## SEC-28 — MEDIUM — Forum anti-spam cooldown is global rather than per user/source

Evidence: **DERIVED**

The reviewed forum posting cooldown references the most recent post globally rather than isolating the cooldown to the current account or trusted client IP.

### Impact

One authenticated user can repeatedly post at the configured interval and keep other users inside the global cooldown window.

### Recommendation

Scope anti-spam cooldowns to account and trusted source IP, with separate global abuse controls if needed.

---

## SEC-29 — LOW/MEDIUM — Shared monster-list cache key varies by request parameter without key variation

Evidence: **DERIVED**

The reviewed monster-list cache uses a shared key while the cached callback result varies based on the `boss` request parameter.

### Impact

An anonymous request can prime the shared cache with a filtered variant that subsequent visitors receive until expiry.

### Recommendation

Include all response-varying inputs in the cache key or cache only the unfiltered base dataset.

---

## SEC-30 — MEDIUM — Quickstart uses static local-development secrets and highly privileged bootstrap defaults

Evidence: **PROVEN** for current Canary fork source.

The quickstart is documented as local-use oriented, but it contains static development defaults for database and administrator credentials and creates a highly privileged administrator account if operators do not override them.

This report does not reproduce the credential values.

### Impact

Accidentally exposing the unchanged quickstart outside a trusted local environment can convert otherwise authenticated MyAAC findings into immediate compromise paths.

### Recommendation

- Fail startup when known default credentials are used outside an explicitly declared local-development mode.
- Generate random bootstrap secrets where practical.
- Bind local-only services to loopback by default.
- Keep database and internal gRPC services unexposed.
- Pin reproducible dependency versions/commits instead of a rolling development branch for security-sensitive deployments.

---

## SEC-31 — LOW/MEDIUM — Account and email validation can disclose registration state

Evidence: **DERIVED**

Distinct public validation responses reveal whether account identifiers or email addresses are already registered.

This overlaps SEC-13 but is retained as a specific registration-surface observation because the endpoint also processes password validation through GET.

---

# Compatibility finding

## COMPAT-01 — Tournament coin column-name mismatch

Evidence: **PROVEN at schema/query reproduction level**

Canary schema uses `tournament_coins`, while the reviewed MyAAC account repository mapping referenced `coins_tournament`.

A local schema reproduction failed when selecting the mismatched column name.

This is a compatibility bug, not an offensive-security vulnerability.

---

# Race-condition candidates requiring real MariaDB E2E validation

These are not promoted to confirmed vulnerabilities without a real database-backed concurrent test.

## RACE-01 — Registration IP cooldown

Observed pattern: check cooldown, then create account, without a proven serialized transaction covering the complete policy decision.

Potential effect: concurrent account-creation requests may pass the same pre-check.

## RACE-02 — Premium-point operations

Observed pattern in selected paid account/character operations: read balance, validate balance, perform action, then write old balance minus price.

Potential effect: parallel requests may purchase multiple operations while charging once or producing inconsistent balances.

## RACE-03 — Email-verification reward

Potential effect: concurrent requests using one still-valid verification token may execute one-time reward hooks more than once before token consumption becomes visible globally.

---

# Regression and negative tests

The following candidates were tested or reviewed and did not become confirmed findings in this audit.

## Passed / mitigated

- Installer IP authorization ignored spoofed `CF-Connecting-IP` and `X-Forwarded-For` in the tested path and used the socket `REMOTE_ADDR`.
- Session fixation mitigation regenerated the PHP session ID before authenticated state was stored in the tested login sequence.
- CSRF token generation itself used cryptographically random bytes and constant-time comparison; the separate design flaw is that unsafe GET flows bypass token validation.
- Common external-origin open-redirect payloads tested against the current redirect guard were rejected.
- Normal-user forum payloads using `javascript:` URLs or raw event-handler HTML were neutralized in the reviewed normal-user rendering path.
- Current 404/405 rendering escaped request URI/method in the reviewed paths.
- Character comments were HTML-escaped before later raw rendering in the reviewed normal update flow.

## Rejected or not proven

- No confirmed current unauthenticated core SQL injection was found in the reviewed paths.
- No unauthenticated upload-to-RCE path was confirmed.
- No practical PHP-cache path-traversal file write was proven.
- No normal-flow XSS through quoted email-address syntax was proven because the primary MyAAC email validator rejects the required characters.
- No guild nickname/description XSS was confirmed through normal validated update flows.
- No exploit was assigned for recent Twig Sandbox advisories because the reviewed MyAAC configuration did not use Twig `SandboxExtension`.
- No PHPMailer 6.9.3 RCE was identified.
- No ZIP Slip claim is made because target ZipArchive/libzip behavior was not dynamically tested.
- FAQ zero-click browser execution was not proven; the confirmed result is persistence of active event attributes through the current tag-only filtering strategy.

---

# Priority remediation plan

## Priority 0 — Remove alternate weak authentication exposure

1. Stop publishing login-server gRPC to the host by default.
2. Upgrade grpc-go past affected vulnerable versions.
3. Configure explicit trusted proxies or disable forwarded-IP trust for directly exposed login-server instances.
4. Add equivalent rate limiting to every externally reachable authentication protocol.

## Priority 1 — Define one authentication policy

Create a bounded authentication-contract task covering:

- password hashing and Argon2id migration;
- accepted account identifier types;
- email verification state;
- TOTP/MFA enforcement;
- account locks/bans;
- session issuance and cleanup;
- trusted client-IP derivation.

The policy must be enforced consistently by MyAAC, login-server, and Canary.

## Priority 2 — Fix high-impact MyAAC web vulnerabilities

1. Remove passwords from GET validation.
2. Make all mutations unsafe-method-only and fix CSRF enforcement.
3. Fix admin log file containment.
4. Escape log rendering.
5. Add reset-token expiry and one-time atomic consumption.
6. Replace `mt_rand()` for security tokens.
7. Replace the cache-dependent/non-atomic login limiter.
8. Set secure session-cookie policy.

## Priority 3 — Harden Canary quickstart composition

1. Replace loopback MyAAC status target with the internal Canary service address.
2. Back off failed status checks.
3. Pin a reproducible MyAAC revision for security-sensitive quickstart releases.
4. Fail closed on unchanged development credentials outside explicit local mode.
5. Keep internal services on the Compose network rather than host-published ports.

## Priority 4 — Content-role and account hardening

1. Sanitize FAQ HTML with a real tag-and-attribute allowlist.
2. Reset email verification on address change and verify the new mailbox.
3. Enforce unique email transactionally where configured.
4. Treat runtime plugin installation as code execution and gate it accordingly.
5. Repair global forum cooldown and cache-key poisoning.

## Priority 5 — Execute full isolated E2E security validation

Build a disposable local environment containing:

- current Canary image/source;
- exact pinned MyAAC revision;
- exact login-server revision/image;
- MariaDB with representative schema;
- GD and ZipArchive enabled;
- reverse proxy/TLS configuration matching production expectations.

Then validate:

- SQL injection fuzzing against real PDO/MySQL behavior;
- concurrent registration, premium-point, reset, and verification races;
- login rate limiting through HTTP and gRPC;
- TOTP/email-verification enforcement across every login path;
- image and archive upload handling;
- session cleanup and growth limits;
- trusted-proxy/IP behavior;
- status polling during Canary outages;
- full role matrix for content/admin flags.

---

# Security boundary conclusion

The central architectural issue is not a single bug. Canary quickstart composes three authentication/security domains:

- MyAAC website/account policy;
- external login-server client authentication;
- Canary server account/session behavior.

Security controls configured in one domain are not automatically authoritative in the others. Until there is a single documented and tested authentication contract, operators can enable a control in MyAAC and incorrectly assume the same control protects the actual client login path.

The immediate safe deployment posture is therefore:

- treat the quickstart as local development only;
- do not expose internal gRPC or database services;
- place the HTTP login endpoint behind correctly configured TLS and trusted-proxy boundaries;
- replace development credentials;
- do not assume MyAAC email verification or MFA protects login-server authentication without explicit integration evidence;
- address the confirmed MyAAC web findings before exposing the website/admin interface to untrusted networks.

## Raw evidence handling

Raw harness outputs and proof-of-concept artifacts were intentionally not committed with this report. They may contain environment-specific paths, test secrets, or unnecessarily reusable exploit details. The durable repository artifact is this sanitized finding set and its task checkpoint.
