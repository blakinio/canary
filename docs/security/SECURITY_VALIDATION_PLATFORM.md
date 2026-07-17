# OTS Security Validation Platform

## Purpose

The OTS Security Validation Platform is the repository-owned security regression layer for the evolving server, client, web, database and cache stack. Its core contract is intentionally product-neutral so the same scenario and report model can be adapted from Canary to Otheryn and later to the maintained client and MyAAC.

The foundation shipped by `OTS-SEC-001` validates and executes deterministic source-regex scenarios. `OTS-SEC-002` adds the first code-owned runtime delegation adapter: it proves exact repository authorization, resolves an existing Universal OTS E2E scenario, enforces literal-loopback confinement, and pins the delegated provider files by SHA-256. `OTS-SEC-003` adds the first bounded offensive runtime pack for common TCP framing and unauthenticated Canary `ProtocolStatus` parser resilience. `OTS-SEC-004` adds a separate bounded login first-message/RSA parser pack that proves fixed prelude/RSA rejection cases and code-owned raw-RSA-to-XTEA handoff into deterministic encrypted login-error responses. Successful account authentication, game-session parsing, post-login XTEA/checksum/sequence coverage, database mutation, client-hostile-server cases and web security probes remain later bounded scenarios/adapters.

## Reuse boundary

Runtime security scenarios must reuse existing OTS runtime lifecycle ownership. Universal OTS E2E remains authoritative for disposable MariaDB/MySQL bootstrap, exact Canary plus controlled OTClient execution, evidence collection and cleanup. Universal Agent Load owns the lighter server-only disposable Canary lifecycle now exposed through its code-owned `RuntimeContext` / `run_runtime` callback seam. Security work may add security-specific drivers and assertions, but it must not create a second general runtime orchestrator.

The Universal Agent Load runner remains the canonical bounded status-protocol load/stress implementation. Security scenarios consume its local runtime callback for server-only probes instead of copying map/database/config/process lifecycle.

## Current CLI

From the repository root:

```text
python tools/security/security_validation.py list
python tools/security/security_validation.py validate
python tools/security/security_validation.py run --scenario <id> --authorized-repository blakinio/canary
python tools/security/security_validation.py run-all --authorized-repository blakinio/canary --report-dir artifacts/security-validation

python tools/security/runtime_adapter.py list
python tools/security/runtime_adapter.py validate
python tools/security/runtime_adapter.py resolve --adapter canary-universal-e2e --authorized-repository blakinio/canary

python tools/security/malformed_packet_runtime_runner.py \
  --binary-path <exact-head-canary> \
  --plan tests/security/runtime_scenarios/canary-status-parser.json \
  --authorized-repository blakinio/canary

python tools/security/login_packet_runtime_runner.py \
  --binary-path <exact-head-canary> \
  --plan tests/security/runtime_scenarios/canary-login-parser.json \
  --authorized-repository blakinio/canary
```

Security scenario execution and runtime-adapter resolution fail closed unless the caller supplies an authorized repository that exactly matches the corresponding registry record. The malformed-status and login-parser plans do not accept hosts, ports, commands, executables, credentials, packet payloads or RSA key material; network coordinates and disposable runtime details come only from code-owned drivers and the runtime context.

## `ots-security-scenario-v1`

Every source-regression scenario is JSON under `tests/security/scenarios/**` and contains exactly these top-level fields:

- `schema_version`: currently `1`;
- `id`: globally unique stable slug;
- `name` and `description`;
- `component`: `server`, `client`, `web`, `database` or `cache`;
- `target_adapter`: stable adapter slug;
- `mode`: currently only `source-regex`;
- `severity`: `low`, `medium`, `high` or `critical`;
- `authorization`: explicit `scope=repository` and `owner/name` repository;
- `source`: explicit regular files plus forbidden/required regular expressions;
- `evidence`: existing regression-test paths and related merged PR numbers.

Unknown fields are rejected. The manifest cannot provide shell commands, executable paths, network targets, credentials or arbitrary plugins.

For `source-regex` mode, every source and regression-evidence path must be a normalized repository-relative regular file. Absolute paths, `..`, symlinks, missing files and files larger than 1 MiB are rejected before execution.

## `ots-security-validation-report-v1`

Each source-regression execution emits deterministic JSON containing:

- scenario identity, component, adapter, severity and authorization;
- `pass` or `fail` result;
- exact assertion findings with file, regex, line and column when applicable;
- SHA-256 and byte size for every inspected source file;
- pinned existing regression-test paths and related PRs.

No timestamp is included, so the same repository state and scenario produce byte-stable report content.

## Seeded source regressions

The initial registry contains two already-fixed critical boundaries:

1. `lua-fs-shell-execution` — forbids `os.execute(...)` in the Lua filesystem helper and requires the native `FileSystem.createDirectory` / `createDirectories` calls from PR #326.
2. `lua-table-unserialize-arbitrary-eval` — forbids direct `load(...)` / `loadstring(...)` evaluation in `tables.lua` and requires the bounded parser markers from PR #328.

These source scenarios complement the existing Lua/C++ regressions. They do not replace them and do not claim that the historical primitives were remotely exploitable through the default client path.

## `ots-security-runtime-adapter-v1`

Runtime-adapter manifests live under `tests/security/runtime_adapters/**`. They are strict data records with exactly:

- `schema_version`;
- stable `id`, `target_adapter` and `component`;
- exact repository `authorization`;
- `delegate.provider`, `delegate.suite` and `delegate.scenario`;
- `confinement.network`.

The first and currently only provider is `universal-e2e`. Provider workflow/resolver/runner paths are code-owned constants in `tools/security/runtime_adapter.py`; the JSON manifest cannot replace them with commands or executable paths. The adapter imports the existing `tools/e2e/run_agent_e2e.py` resolver instead of implementing another E2E scenario parser.

The `literal-loopback-only` policy requires the resolved E2E fixture host itself to be a literal IP address accepted by Python's `ipaddress` module and marked loopback. Hostnames such as `localhost` are rejected rather than DNS-resolved, and non-loopback literals fail closed. The Universal E2E provider also restricts the delegated controlled-client repository to the user-owned `blakinio/otclient` contract.

`canary-universal-e2e` is the first adapter. It delegates to the existing `login/relog` E2E baseline without executing a second lifecycle implementation.

## `ots-security-runtime-delegation-v1`

A successful runtime-adapter resolution emits deterministic JSON with:

- adapter identity, source and target adapter;
- exact repository authorization;
- delegated provider and E2E scenario key;
- selected controlled-client repository/ref;
- literal-loopback host, IP version and game port;
- SHA-256 and byte size for the canonical Universal E2E workflow, resolver, physical runner and selected E2E scenario manifest;
- `result=pass` only after all authorization and confinement checks succeed.

The report is a **delegation proof**, not an offensive-test success claim.

## `ots-security-malformed-packet-plan-v1`

The first offensive runtime plan lives under `tests/security/runtime_scenarios/**`. Its strict top-level contract is limited to:

- `schema`;
- stable `id`;
- exact `authorized_repository`;
- code-owned `driver`;
- code-owned `service`;
- a bounded, unique ordered list of built-in `cases` identifiers.

Unknown fields are rejected. A plan cannot provide packet bytes or hex strings, shell commands, executable paths, credentials, hostnames, target IPs or ports. The reviewed packet corpus remains in code. The canonical `canary-status-parser-baseline` selects eight fixed cases covering zero and oversized frame lengths, truncated declared bodies, unknown service selection and truncated/unknown status payloads.

`tools/security/malformed_packet_runtime.py` owns the strict plan contract, fixed case registry, individual transport/control probes and deterministic report primitives. `tools/security/malformed_packet_runtime_runner.py` is the canonical runtime entry point: it consumes the merged Universal Agent Load `run_runtime` callback and adds code-owned loopback source isolation for malformed and control probes.

## `ots-security-malformed-packet-report-v1`

A malformed-parser execution records deterministic evidence for the exact run:

- plan identity and SHA-256;
- exact repository authorization;
- driver/service identity;
- confined callback-provided loopback target host and status port;
- exact Canary binary SHA-256;
- SHA-256 pins for the packet core, canonical runner and reused runtime provider;
- ordered per-case code-owned malformed/control source IPs, packet SHA-256/size and normalized malformed/control outcomes;
- fatal/sanitizer log findings;
- one stable failure code or success.

No timestamps or scheduler-dependent retry counts are recorded.

Canary has two independent source-IP protections relevant to this pack. `Ban::acceptConnection` rejects excessive rapid accepted connections per source IP, while `ProtocolStatus::ipConnectMap` rate-limits repeated status queries for non-exempt source addresses. The runtime pack does not disable or modify either protection. Instead, every bounded parser case gets two deterministic code-owned IPv4 loopback sources: one for the malformed probe and a distinct one for the valid control probe. Across the maximum 16-case contract those addresses occupy `127.0.0.2` through `127.0.0.33`, while every destination remains the callback-provided `127.0.0.1` status port. Plans cannot choose either source or destination addresses.

After each malformed connection terminates, exactly one valid XML status request is sent from that case's distinct control source and must return `<tsqp` plus `<serverinfo`. This isolates parser-resilience evidence from the independent admission/status-query throttles without weakening those production protections. A failed control request remains fail-closed as its exact stable control failure code.

The runtime also fails closed on malformed-case read timeout, unexpected malformed response, target/source confinement failure, Canary process exit and fatal/sanitizer signatures. The outer `run_runtime` callback remains responsible for exact-head Canary startup, database/config/map preparation and cleanup.

## OTS-SEC-003 evidence boundary

A green `canary-status-parser-baseline` proves only that the tested exact Canary binary survived and remained responsive across the registered common framing and unauthenticated `ProtocolStatus` cases under the bounded disposable-loopback runtime.

It does **not** prove complete protocol exploit resistance and specifically does not cover:

- authenticated login protocol parsing;
- game protocol parsing after session establishment;
- XTEA-encrypted message handling;
- checksum/sequence-number combinations;
- maintained-client hostile-server parsing;
- packet flood or sustained DoS capacity;
- correctness or strength of either independent per-IP admission/status-query policy.

Those require separate bounded tasks and protocol-aware fixtures. Future confirmed parser vulnerabilities should become permanent fixed-case regressions after remediation rather than broadening this plan with arbitrary packet input.

## `ots-security-login-packet-plan-v1`

The bounded login-parser plan reuses the same exact-field data shape as the malformed-status plan: schema, stable id, exact repository authorization, code-owned driver/service and a bounded unique ordered list of built-in case identifiers. It likewise rejects unknown fields and never accepts packet bytes, RSA key material, credentials, source addresses, destinations or ports from JSON.

`canary-login-parser-baseline` selects six fixed code-owned cases:

- an unsupported version with a valid login-service frame;
- the current login prelude without an RSA block;
- the current prelude with a 127-byte truncated RSA block;
- a valid raw-RSA block whose decrypted marker is intentionally invalid;
- a valid raw-RSA handoff with an empty account descriptor;
- a valid raw-RSA handoff with the code-owned non-user account marker and an empty password.

`tools/security/login_packet_runtime.py` owns the framing, public-RSA fixture generation, code-owned XTEA key, fixed cases, response policies and CurrentLogin response decoder. It stores only the public modulus corresponding to Canary's repository-owned default OpenTibia RSA key; scenario manifests cannot supply or replace RSA material. `tools/security/login_packet_runtime_runner.py` reuses `run_runtime` and gives every case and its control exchange distinct deterministic IPv4 loopback source addresses while keeping server admission protections enabled.

The deterministic control is stronger than process liveness or a generic non-empty reply. It sends the code-owned valid-RSA empty-account request, then requires a correctly framed CurrentLogin response whose Adler32 validates, whose XTEA payload decrypts with the code-owned key, whose padding and opcode are valid, and whose decoded error is exactly `Invalid email.`. A plain unsupported-version response therefore cannot satisfy the control oracle.

## `ots-security-login-packet-report-v1`

A login-parser execution records:

- plan identity and SHA-256;
- exact repository authorization and login driver/service identity;
- callback-provided literal-loopback login target;
- exact Canary binary SHA-256 plus provider/core/runner SHA-256 pins;
- the code-owned control-packet SHA-256;
- ordered per-case case/control source IPs, packet SHA-256/size and response policy;
- normalized case outcome plus response SHA-256/size when a bounded response exists;
- decoded CurrentLogin error text only for code-owned encrypted-error cases;
- the validated control error and control-response hash/size after every case;
- fatal/sanitizer findings and one stable failure code or success.

The report contains no arbitrary response body, credential or timestamp. It fails closed on target/source confinement errors, transport timeout/error, unexpected response policy, malformed CurrentLogin framing/checksum/XTEA/padding/opcode/string evidence, wrong control error, Canary process exit or fatal/sanitizer signatures.

## OTS-SEC-004 evidence boundary

A green `canary-login-parser-baseline` proves only that the tested exact Canary binary survived the six registered login first-message/RSA cases and that, after every case, the login service still completed the code-owned RSA-to-XTEA handoff sufficiently to return the expected encrypted `Invalid email.` control response.

The initial real exact-head run also proves the two successful-RSA negative-authentication fixtures reached deterministic encrypted `Invalid email.` and `Invalid password.` responses respectively, while the prelude-only, truncated-RSA and invalid-marker cases terminated without a response. This is bounded parser/handoff evidence, not successful authentication evidence.

It does **not** cover:

- successful account authentication or authorization;
- character-list contents or account entitlement correctness;
- game-session establishment;
- post-login game-protocol packet parsing;
- post-login game XTEA/checksum/sequence-number handling;
- session races, replay or reconnect abuse;
- maintained-client hostile-server parsing;
- packet flood or sustained DoS capacity.

Those remain separate bounded tasks. In particular, authenticated game-session and post-login transport coverage must not be inferred from a successful SEC-004 login-service control exchange.

## Runtime adapter safety contract

Every runtime adapter or runtime security driver must satisfy all of the following before it can be registered:

- execute only against a disposable environment explicitly created for the test or another target explicitly authorized by the repository owner;
- reuse Universal OTS E2E / Universal Agent Load lifecycle contracts where those platforms already own the capability;
- fail closed on ambiguous target identity or missing authorization;
- never discover arbitrary public targets;
- never embed production credentials or secrets in scenario/adapter manifests;
- keep packet bytes, source-address strategy and executable behavior code-owned rather than manifest-supplied;
- retain enough server/client/database/network evidence to reproduce a failure;
- convert a confirmed vulnerability into a permanent regression scenario after remediation.

## Planned adapters and scenarios

Planned bounded additions, each through a separate task/PR, are:

- authenticated game-session parser and post-login checksum/sequence/XTEA transport scenarios;
- authenticated session, race, economy and transaction-abuse scenarios with disposable MariaDB state assertions;
- Redis/multichannel ownership and fail-closed scenarios;
- maintained-client hostile-server payload scenarios;
- MyAAC authentication, session and web-input scenarios;
- full-stack attack chains composed from already-approved component adapters.

The core registry/report formats must remain independent of any single server name. Target-specific behavior belongs in adapters and scenarios.
