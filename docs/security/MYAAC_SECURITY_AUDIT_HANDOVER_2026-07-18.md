# MyAAC security audit continuation handover — 2026-07-18

This handover is intentionally limited to MyAAC and the MyAAC → login-server → Canary authentication boundary. It does not cover multichannel, Redis, OTBM, maps, RME, OTClient, client-editor, or unrelated gameplay/economy mechanics.

## Continuation baseline

- Durable predecessor report: `docs/security/MYAAC_CANARY_SECURITY_AUDIT_2026-07-17.md`.
- Predecessor task: `CAN-20260717-myaac-canary-security-audit` (archived after merge).
- Predecessor PR: #453, merged.
- PR #453 final head: `f1961e9ce6a1f231a0ed8900519a9f4634fe4ea8`.
- PR #453 merge commit: `6b42890347338a13daca5fd6291b56b8dc6aa091`.
- Reviewed MyAAC pinned baseline: `slawkens/myaac@a526b7e4363af53ea818c1f75b13a0c8c3248b72`.
- Canary quickstart still defaults `MYAAC_REF` to rolling `develop`; material chains below were also re-read against current `develop` file contents where noted. The exact future `develop` SHA used by an arbitrary deployment remains deployment-time evidence, not a stable audit baseline.

## New finding

### MYAAC-036 — HIGH — Attacker-controlled successful login resets the shared IP brute-force bucket

Evidence: **DYNAMICALLY CONFIRMED in an isolated exact-logic harness; full-stack E2E not executed**.

Affected reviewed paths:

- `system/pages/account/login.php`
- `login.php` (native MyAAC game-login JSON endpoint)
- `system/src/RateLimit.php`

Full call chain:

`attacker POST/JSON login input`
→ public login routing
→ account lookup and password verification
→ `RateLimit('failed_logins', ...)` loaded as a shared per-IP bucket
→ wrong victim password increments `data[ip].attempts`
→ before `max_attempts` is reached, attacker submits correct credentials for an attacker-controlled account from the same IP
→ successful-credential branch passes `!$limiter->exceeded($ip)`
→ `RateLimit::reset($ip)` removes the complete IP bucket
→ attacker repeats victim guesses from zero
→ the intended brute-force threshold is never reached.

The web-login path resets the bucket after the valid-password branch even when the account is rejected for failed email verification. The native MyAAC game-login path resets the bucket before checking `email_verified`. Therefore the reset primitive does not require the attacker-controlled account to become a successfully authenticated web/game session; possession of valid credentials for an account that reaches the valid-credential branch is sufficient. Registration availability may lower the practical barrier, but is not required by the finding.

The limiter is not keyed by target account. A successful login to account A therefore clears failed guesses previously accumulated from the same IP against account B.

Isolated exact-logic harness result with `max_attempts=5`:

```text
victim_guesses=80 remaining_attempts=0 blocked=no
```

The harness executed 20 cycles of four failed victim guesses followed by a correct attacker-account login/reset. This confirms the deterministic state-machine bypass; it is not represented as a running MyAAC/MariaDB E2E test.

Current rolling `develop` revalidation:

- web login still constructs the per-IP `failed_logins` limiter and calls `reset($ip)` after valid credentials;
- `RateLimit::reset()` still deletes the entire IP entry;
- native `login.php` still resets before the email-verification rejection.

Impact:

- an attacker with any usable valid account credential can repeatedly reset their own source-IP bucket and perform unbounded sequences of password guesses against other accounts, limited by request throughput rather than the configured attempt threshold;
- the bypass is independent of the already known cache-disabled fail-open behavior and the already known non-atomic lost-update race.

Recommended remediation:

1. Do not clear a source-wide failure bucket merely because one account authenticates successfully.
2. Track failures atomically by at least a tuple such as trusted source IP + normalized target account identifier, with a separate bounded source-wide abuse control.
3. Reset only the bucket corresponding to the account that actually authenticated, not unrelated target-account failures.
4. Apply the same policy consistently to web login and native MyAAC game login.
5. Add regression tests that interleave `N-1` failures against account B with a valid login to account A and assert that account B's throttling state is preserved.

## Extended existing findings

### MYAAC-005 — CRITICAL — Broken admin access control has additional direct takeover and RCE chains

Evidence: **PROVEN by static full call-chain review; no full browser E2E executed**.

Additional direct account-takeover chain:

`FLAG_ADMIN`
→ central admin router accepts `admin()`
→ Account Editor has no target-privilege hierarchy check
→ select arbitrary Super Admin account
→ change password and/or TOTP `secret`
→ save account
→ attacker can take over the higher-privilege account.

This is stronger than only self-editing `web_flags`: a regular Admin can directly rewrite authentication material of a higher-privilege target.

Additional PHP-code-execution chain:

`FLAG_ADMIN`
→ Account Editor self-grants `FLAG_CONTENT_PAGES`
→ Settings endpoint, guarded only by `admin()`, enables `core.admin_pages_php_enable`
→ Pages backend accepts `php=1` with attacker-controlled body
→ body is stored in the database
→ public database-page routing calls `getCustomPage()`
→ `eval($tmp)` executes the stored body.

This provides an alternate PHP RCE path even when plugin ZIP installation is unavailable. It remains an extension of MYAAC-005 because the root cause is the same Admin-to-SuperAdmin/content-permission broken access control.

Additional configuration observation:

- a regular Admin can also change core settings through `admin/tools/settings_save.php` and can enable plugin management before using the existing plugin-install execution path;
- disabling Plugin Manager in configuration is therefore not a durable mitigation against a compromised `FLAG_ADMIN` account unless settings changes are independently restricted.

### MYAAC-009 — HIGH — Gallery SSRF can reveal valid image responses

Evidence: **PROVEN at source/API capability level; live GD network E2E not executed**.

Existing chain:

`FLAG_CONTENT_GALLERY`
→ Gallery add/edit accepts attacker-controlled `image` through request data
→ `Gallery::resize()` passes the value to `imagecreatefromgif/jpeg/png()`
→ PHP GD may fetch a URL when URL-aware fopen wrappers are enabled.

Material impact extension:

- on successful decoding of a remote GIF/JPEG/PNG resource, MyAAC re-encodes and writes the image into the gallery directory;
- the gallery database stores the resulting path and the resource can then be rendered through the site;
- therefore, for internal/network targets that return a valid supported image, the SSRF is conditionally response-revealing rather than strictly blind.

Qualification:

- this does not establish arbitrary text-response exfiltration;
- the target response must be decodable by the selected GD image loader;
- PHP GD and a live target stack were unavailable in the current sandbox, so no end-to-end HTTP fetch was performed.

### SEC-28 / forum cooldown — existing finding extended with a concurrent bypass

Do **not** assign a new MYAAC number for the global forum cooldown itself. The durable predecessor report already records it as `SEC-28 — Forum anti-spam cooldown is global rather than per user/source`.

Additional concurrency chain:

`authenticated account allowed by Forum::canPost()`
→ query most recent post timestamp
→ compare against `forum_post_interval`
→ no transaction/row lock/atomic guard covers the policy decision
→ separate thread/post insert
→ parallel requests after the cooldown boundary can observe the same eligible old timestamp and all insert.

Impact extension:

- the existing global design allows cross-user contention/starvation;
- independently, the non-atomic precheck allows burst posting through concurrent requests, bypassing the intended one-post-per-interval behavior.

No real MariaDB concurrent E2E was executed in this continuation.

### MYAAC-001 — HIGH — Loose password comparison also affects sensitive re-authentication checks

Evidence: **PROVEN by static source review; no new practical magic-hash account-takeover claim beyond MYAAC-001**.

The reviewed password re-authentication checks for account email change, password change, and character deletion also use loose password-hash comparison patterns. This expands the set of sensitive actions that must be converted to strict, algorithm-appropriate verification during remediation.

### MYAAC-031 / MYAAC-032 — paid/reward race scan status

The continuation re-scanned core premium-point/coin/premium-day patterns that were discoverable through the connector.

- `change-name` and `change-sex` still match the known read-balance → check → paid mutation → write old balance minus price pattern already covered by MYAAC-031.
- email-confirm reward handling still uses read-modify-write reward updates and remains within the already documented MYAAC-032 race chain.
- no distinct new core paid-operation or payment-callback finding was promoted in this pass.

## Rejected / not promoted

- **Global forum cooldown as a new finding** — rejected as duplicate; already preserved as `SEC-28` in the durable report.
- **ZIP Slip arbitrary overwrite/RCE** — not proven for the current target PHP ZipArchive/libzip runtime. The plugin installer does call `ZipArchive::extractTo()` into cache and application root, but no current traversal bypass was dynamically demonstrated. Keep closed without new target-runtime evidence.
- **Normal character-comment stored XSS** — rejected for the reviewed normal update path because the comment is HTML-escaped before the later raw rendering sink.
- **Normal guild-description stored XSS** — rejected for the reviewed normal update path because the description is HTML-escaped before storage/rendering.
- **MyAAC XFF/forwarded-header limiter bypass** — rejected for the reviewed MyAAC compatibility path because `get_browser_real_ip()` uses `REMOTE_ADDR`; this does not change the separate external login-server trusted-proxy finding.
- **New paid-operation race beyond existing MYAAC-031/MYAAC-032** — not found in the reviewed core paths during this continuation.

## Dynamic tests performed in this continuation

1. **Rate-limit reset exact-logic harness** — PASS.
   - configuration: `max_attempts=5`;
   - pattern: four wrong victim guesses, then valid attacker-account reset, repeated 20 times;
   - result: `victim_guesses=80 remaining_attempts=0 blocked=no`.
2. Environment capability checks confirmed PHP CLI availability but no usable Docker/MariaDB full stack and no PHP GD/ZipArchive support for the requested end-to-end image/archive tests.

No public or third-party deployment was tested.

## Tests not executed

- disposable full MyAAC + MariaDB + login-server + Canary E2E;
- real MariaDB concurrency test for premium-point operations;
- real MariaDB concurrency test for email-confirm reward;
- real MariaDB concurrency test for forum cooldown bypass;
- live GD-backed Gallery SSRF request/response test;
- current-runtime ZipArchive traversal test;
- password-change/reset followed by external `account_sessions` replay E2E;
- direct login-server HTTP 8088 / gRPC 9090 E2E;
- direct Canary password-path bypass E2E;
- XFF trusted-proxy bypass E2E against login-server;
- exact future quickstart build of rolling MyAAC `develop`.

## Repository / task / PR handover

- repository: `blakinio/canary`
- task ID: `CAN-20260718-myaac-security-audit-continuation`
- branch: `docs/myaac-security-audit-continuation-20260718`
- PR: `#556` — draft
- base: `main`
- base SHA at branch creation: `6c2ed7fd5d7e0f51bf7bfc75ebcc30b840315e41`
- current documented head at first task commit: `a804ad8c774b299e49b57067770f01f6db9051b5`
- CI status: not yet validated on final head
- merge status: not merged

## Exact next_action

Update the active task checkpoint to PR #556 and the latest documentation head, inspect the complete changed-file list and diff, run the repository task/checkpoint validation available through CI, then apply `ci:final-gate`; do not merge until the exact final head is fully green and review-clean. Full MyAAC/login-server/Canary E2E remains a separate unavailable validation item and must not be represented as completed.
