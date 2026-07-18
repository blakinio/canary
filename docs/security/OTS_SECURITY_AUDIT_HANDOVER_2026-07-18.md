# OTS security audit continuation handover

Date: 2026-07-18

Status: continuation checkpoint for the MyAAC / login-server / Canary / OTClient / RME / client-editor security assessment. This document is evidence and remediation input, not a production penetration-test certification.

## Purpose

This file preserves the continuation state required for another agent to resume without reconstructing the audit from chat history.

The durable evidence model remains:

- `PROVEN` — directly reproduced or directly confirmed in current source;
- `DYNAMICALLY CONFIRMED` — reproduced in an isolated harness;
- `DERIVED` — strongly supported by composed source behavior but not executed end-to-end;
- `CANDIDATE` — requires additional call-chain or runtime proof;
- `REJECTED` / `FALSE POSITIVE` — explicitly traced and not currently a valid finding.

Do not promote a suspicious sink into a finding without tracing source, validation, call-site, state transition, retry/crash behavior and final security impact.

## Repository boundary

Writable repository:

- `blakinio/canary`

Read-only evidence sources unless separately authorized:

- `opentibiabr/canary`
- `opentibiabr/login-server`
- `slawkens/myaac`
- `opentibiabr/otclient`
- `opentibiabr/remeres-map-editor`
- `opentibiabr/client-editor`

No public or third-party deployment was attacked or scanned.

## Scope completed so far

The continued assessment expanded beyond the original MyAAC/login-stack report into:

- fragmented authentication and session architecture;
- MyAAC admin/RBAC/file/cache/CSRF/reset/XSS/rate-limit paths;
- Canary market, bank, GameStore and account-coin transaction ordering;
- multichannel Redis lease, fencing, persistence, handoff and leader-election behavior in `blakinio/canary`;
- OTClient updater/client-assets/credential-storage trust boundaries;
- RME malformed-map/archive/path handling;
- client-editor manifest/repack path handling.

The working audit matrix maintained outside the repository reached 102 tracked findings at the end of the continuation pass. The repository report remains the durable public/sanitized summary; this handover captures the additional continuation state and next work packages.

## Highest-priority authentication findings

### Bundled/default private RSA key

The reviewed native-login deployment path includes a reusable private RSA key in the repository/runtime image. An isolated proof confirmed that the bundled private key can decrypt the corresponding native RSA block. A complete packet-capture end-to-end replay was not executed because the original lab lacked a full local Docker/client/server stack.

Remediation direction:

- unique key per deployment;
- private key outside Git/images;
- key rotation for deployments that used a published/default key;
- migrate external authentication to a short-lived session-token design.

### Fragmented auth surface

Authentication policy is split across:

- login-server HTTP;
- login-server gRPC;
- Canary native login;
- Canary game login;
- legacy listeners.

Controls applied only to the HTTP layer do not protect direct gRPC/native/game paths.

### MFA / e-mail policy bypass

The external login-server authenticates credentials without enforcing MyAAC TOTP/MFA or `email_verified` policy. Direct password-mode game authentication also remains an alternate policy surface.

### Session replay and revocation

External `account_sessions` bearer tokens are reusable until expiry and are not consumed on successful game authentication. Password change/reset and MyAAC logout do not invalidate those external game sessions.

### Password-mode session material

In password mode, the external login response can construct the game SessionKey from the reusable account login plus plaintext password instead of issuing an independent scoped token.

### HTTP and gRPC hardening

Confirmed themes:

- public/reachable gRPC without application TLS/rate limiting;
- HTTP service without native TLS;
- spoofable forwarded-IP trust affecting HTTP rate-limit buckets unless trusted proxies are configured;
- HTTP server created without explicit read-header/read/write/idle deadlines and without an explicit login body cap.

## Highest-priority MyAAC findings

### Admin to Super Admin / game privilege / code execution chain

The continuation pass traced the RBAC chain through the central admin gate, account/player editors and plugin manager. A lower web admin can modify sensitive privilege fields and reach higher authority, including plugin installation / PHP execution capability.

Treat this as a critical broken-access-control finding. Sensitive account flags, game group/type fields and plugin management need separate capability checks and anti-self-escalation controls.

### Public predictable cache under webroot

The reviewed quickstart/file-cache model can place predictable cache files under the document root. Cached parsed configuration/settings can include database and infrastructure secrets. The web server must not serve runtime cache/log directories.

### Admin local-file read / include

Confirmed paths include:

- admin log viewer traversal;
- reports traversal;
- admin router local PHP include through path traversal to existing PHP files.

### Stored/reflected XSS families

Confirmed or source-proven chains include:

- dynamic menu content rendered unsafely;
- log/report raw rendering when server files are shared with MyAAC;
- forum error rendering where an allowed anchor tag can retain dangerous attributes before raw output.

The error-box design should default to escaped text and structured links rather than `striptags(...allowed tags...)` plus raw rendering.

### Password reset / recovery weaknesses

Confirmed themes:

- reset code without enforced expiry in the traced flow;
- bearer reset material in URLs;
- non-CSPRNG helper used by security-token generation paths;
- insufficiently unified recovery brute-force controls;
- selected mail/recovery configurations exposing newly generated plaintext passwords.

### Race conditions

Source-confirmed race patterns include:

- premium-point paid operations using read old balance -> perform operation -> write absolute old-minus-price;
- e-mail confirmation reward hook capable of concurrent duplicate reward execution;
- account-creation IP cooldown check not serialized with creation;
- verification-email resend cooldown check not atomic.

## Canary economy / exactly-once findings

### Market create/accept/cancel ordering

Confirmed classes:

- economic effects before final offer mutation;
- refunds before confirmed deletion/history transition;
- assets/fees removed before offer insertion with ignored insert result;
- multi-process double-accept and cancel-versus-accept races when the same offer is read without a transactional claim/row lock.

### Market expiry crash consistency

The traced expiry flow persists a pending ledger state, removes/finalizes the active offer, then performs refund/delivery and later marks committed. A crash or delivery failure after offer removal can leave a pending record with no active offer for the ordinary sweep to rediscover, causing unreconciled loss or partial delivery.

### Account coin read-modify-write

Single-type account coin updates use a read current value followed by an absolute write rather than an atomic arithmetic/conditional update or row-locked transaction. Concurrent writers can lose credits or double-consume accounting state.

### GameStore ordering

Confirmed patterns include:

- delivering a product/effect before final coin debit;
- crediting transferable coins to the receiver before a checked sender debit.

Failures/races in the later debit path can produce free products or currency creation.

### Bank crash consistency

Bank transfer state is not persisted as one atomic sender/receiver transaction. Depending on online/offline ownership and crash timing, one side can persist while the other reverts.

### Guild bank multichannel double-spend

Independent process-local guild balances can be spent on different channel processes without a single transactional database authority.

## Multichannel findings in `blakinio/canary`

These findings are primarily relevant when multichannel is enabled.

### Missing fencing at persistent player save

The full player save path does not enforce current fencing ownership at the persistent-write boundary. A stale/zombie process can therefore write old player state after losing the active lease.

### Fencing token monotonicity

The reviewed Redis fencing counter shares expiry lifecycle with lease state. After key expiry/reset, token values can restart rather than remaining globally monotonic, undermining fencing guarantees.

### DB session defense

The database session record uses latest-wins upsert semantics rather than rejecting an already active owner as an independent compare-and-swap safety layer.

### Mail handoff exactly-once failures

Confirmed classes:

- delivery and `markApplied` are not one atomic operation;
- retry can redeliver an item when application succeeded but state transition failed;
- operation identity is generated too late to cover all enqueue/source-removal crash windows.

### House isolation failures

Confirmed classes:

- schema identity conflicts with intended channel-scoped house identity;
- house/tile/list queries and cleanup are not consistently partitioned by channel;
- cross-channel ownership revocation is incomplete.

### Global shared-state interference

Per-channel startup/periodic jobs can overwrite or prune global shared tables such as presence/status and town state without consistent channel partitioning or singleton execution.

### Market multichannel races

Two processes can race on the same offer without a transactionally claimed state. This includes double-accept and accept-versus-cancel scenarios.

### Direct reconnect bypasses channel-switch policy

Target-channel login can acquire a session directly rather than proving that the request passed the full channel-switch policy evaluation. Cooldown/PvP/target-state policy therefore needs to be enforced at the target login boundary or through a signed one-time switch ticket.

### Stale/wrong-character switch handoff

Pending switch lookup is not sufficiently bound to the exact character and lacks a robust expiry/one-time proof in the traced flow, allowing stale or same-account handoff confusion.

### Cross-process offline-player loading

A process can treat a character that is actually online on another channel as an offline temporary player loaded from the database. Market/bank/house/depot/bed-related paths can mutate and full-save that stale snapshot, overwriting the actively playing character's persisted state.

### Redis heartbeat on the main game dispatcher

Lease renewals and channel-status reads are performed synchronously from the game dispatcher. With per-operation Redis timeouts, degraded/blackholed Redis can create long gameplay stalls proportional to tracked sessions/channels.

### Fail-closed policy gaps

The operational runbook describes immediate freezing of cross-channel/economic mutations during database/Redis coordination loss, but the traced runtime and market packet paths do not implement one central mutation gate matching that policy.

### Concurrent startup ban-history race

Multiple channel processes can observe the same expired ban and append duplicate history records because the select/insert/delete migration sequence is not claimed atomically or executed as a singleton job.

## OTClient continuation findings

### Updater trust model

Payload integrity metadata is supplied by the same updater authority as the payload. A compromised update source can therefore supply both malicious content and matching metadata unless an independent signing root is introduced.

### clientAssets supply-chain execution

The reviewed default asset installation path can prefer externally sourced release archives where an expected archive hash may be absent, while packaged archives can be extracted into the client work tree. A compromised external source can therefore become a client-code execution path if executable Lua/module startup files are replaced.

### Remembered credential storage

Remember-password storage uses reversible host-derived obfuscation rather than an operating-system credential vault. Treat it as local credential-at-rest hardening debt, not strong secret storage.

## RME continuation findings

### Deep OTBM nesting

Malformed deeply nested OTBM nodes can drive unbounded recursive traversal and process stack exhaustion.

### OTGZ size/decompression limits

Archive entry sizes are used for allocation without a sufficiently strong total/uncompressed-size policy, enabling local memory-exhaustion/decompression-bomb behavior from untrusted map archives.

### Auxiliary path traversal on save

OTBM-controlled auxiliary file names can escape the map directory. Opening a malicious map and saving can write generated XML through a parent-directory path and clobber an accessible local file.

## client-editor continuation findings

### Repack manifest traversal

Manifest-provided file paths can escape intended source/destination roots unless canonical containment is enforced, allowing local file inclusion in artifacts or output clobbering.

### Repack error propagation

The reviewed repack path can suppress an underlying file-operation failure and return success, allowing CI/release automation to accept a partial/broken artifact.

## Explicitly rejected / closed hypotheses

Do not reopen these without new evidence:

- account-ban bypass in traced game login flow;
- IP-ban bypass in traced game login flow;
- cross-account character login without ownership check;
- livestream viewer opcode `0x96 -> parseSay()` acting as caster;
- protected livestream direct password bypass;
- protocol session hint store containing plaintext credentials;
- classic recovery-key magic-hash bypass in the reviewed generator/format;
- password-reset step skipping in the traced flow;
- guild-nick stored XSS through the reviewed normal-user setter;
- custom-page cache authorization bypass after full access recheck tracing;
- PHP cache code injection through the reviewed cache serializer;
- OTClient updater parent-directory traversal through the reviewed PhysFS write path;
- current game-bot Config Manager MITM-to-RCE chain while its archive backend remains stubbed;
- production Whoops debug leak in the reviewed environment routing;
- daily-reward duplication from the reviewed startup reset hypothesis;
- `setGlobalStorage()` SQL injection as a current remote finding: the sink is unsafe for arbitrary strings, but no untrusted live call-site source was confirmed.

## Validation gaps that remain open

### Full RSA / session E2E

Still required in a disposable local environment:

- capture native login traffic;
- decrypt the RSA bootstrap with the deployment key;
- recover the negotiated session material;
- validate session replay boundaries.

Do not claim this full E2E was completed until it is actually executed.

### Quickstart auth-mode E2E

The source composition strongly indicates an auth-mode mismatch in the fresh quickstart path, but a complete Docker login -> game-world test was not available in the original lab.

### Multichannel dynamic race harness

Build a disposable environment with:

- at least two Canary channel processes;
- shared MariaDB;
- Redis;
- deterministic parallel clients/actions.

Prioritize dynamic confirmation of:

- market double accept / cancel-versus-accept;
- mail retry duplication;
- stale full player save after ownership change;
- guild-bank double spend;
- house cross-channel persistence corruption.

## Next audit priorities

1. Continue mechanical review of global/shared multichannel tables and jobs: global storage/KV, cleanup/optimize, highscore cache, event scheduler and any table written by each channel without channel partitioning.
2. Continue exactly-once review of market partial fills, bank transfer combinations, guild deposit/withdraw ordering, GameStore history versus balance commit, inbox/depot/stash handoff, trade completion and house auction/payment paths.
3. Continue MyAAC paid-operation race review for every `read balance -> perform action -> write absolute balance` pattern.
4. Continue universal raw-render review: Twig `|raw`, `striptags`, `nl2br`, disabled autoescape and direct request-derived echo paths.
5. Execute the full isolated authentication E2E package when Docker/MariaDB/client runtime are available.
6. For OTBM/assets work, reuse the repository's existing OTBM audit/script-resolution/World Index pipeline; do not build a separate parser or renderer.

## Continuation contract

A continuation agent should begin with:

1. root `AGENTS.md`;
2. `docs/agents/REPOSITORY_MAP.md`;
3. `docs/agents/CONTEXT_ROUTING.md`;
4. the active task record for this audit;
5. PR #453 and its current head;
6. this handover and the durable security report.

The next concrete action is to continue the multichannel global/shared-state and exactly-once economy review, recording every proven/rejected hypothesis in durable task evidence before remediation work is split into bounded fix tasks.
