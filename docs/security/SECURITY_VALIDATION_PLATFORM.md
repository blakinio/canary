# OTS Security Validation Platform

## Purpose

The OTS Security Validation Platform is the repository-owned security regression layer for the evolving server, client, web, database and cache stack. Its core contract is intentionally product-neutral so the same scenario and report model can be adapted from Canary to Otheryn and later to the maintained client and MyAAC.

The foundation shipped by `OTS-SEC-001` is deliberately small. It validates and executes deterministic source-regex scenarios only. Runtime protocol fuzzing, authenticated abuse cases, database mutation, client-hostile-server cases and web security probes require later bounded adapters.

## Reuse boundary

Runtime security scenarios must reuse the existing Universal OTS E2E platform for disposable MariaDB/MySQL bootstrap, Canary lifecycle, controlled OTClient execution, evidence collection and cleanup. Security work may add security-specific drivers and assertions, but it must not create a second general runtime orchestrator.

The Universal Agent Load runner remains the canonical bounded status-protocol load/stress implementation. Security scenarios that need load evidence should consume or extend that layer through a separate owned task instead of copying it.

## Current CLI

From the repository root:

```text
python tools/security/security_validation.py list
python tools/security/security_validation.py validate
python tools/security/security_validation.py run --scenario <id> --authorized-repository blakinio/canary
python tools/security/security_validation.py run-all --authorized-repository blakinio/canary --report-dir artifacts/security-validation
```

`run` and `run-all` fail closed unless the caller supplies an authorized repository that exactly matches the scenario's authorization record.

## `ots-security-scenario-v1`

Every scenario is JSON under `tests/security/scenarios/**` and contains exactly these top-level fields:

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

Each execution emits deterministic JSON containing:

- scenario identity, component, adapter, severity and authorization;
- `pass` or `fail` result;
- exact assertion findings with file, regex, line and column when applicable;
- SHA-256 and byte size for every inspected source file;
- pinned existing regression-test paths and related PRs.

No timestamp is included, so the same repository state and scenario produce byte-stable report content.

## Seeded regressions

The initial registry contains two already-fixed critical boundaries:

1. `lua-fs-shell-execution` — forbids `os.execute(...)` in the Lua filesystem helper and requires the native `FileSystem.createDirectory` / `createDirectories` calls from PR #326.
2. `lua-table-unserialize-arbitrary-eval` — forbids direct `load(...)` / `loadstring(...)` evaluation in `tables.lua` and requires the bounded parser markers from PR #328.

These source scenarios complement the existing Lua/C++ regressions. They do not replace them and do not claim that the historical primitives were remotely exploitable through the default client path.

## Runtime adapter safety contract

A future runtime adapter must satisfy all of the following before it can be registered:

- execute only against a disposable environment explicitly created for the test or another target explicitly authorized by the repository owner;
- reuse Universal OTS E2E lifecycle and evidence contracts where that platform already owns the capability;
- fail closed on ambiguous target identity or missing authorization;
- never discover arbitrary public targets;
- never embed production credentials or secrets in scenario manifests;
- retain enough server/client/database/network evidence to reproduce a failure;
- convert a confirmed vulnerability into a permanent regression scenario after remediation.

## Planned adapters

Planned bounded additions, each through a separate task/PR, are:

- Canary/Otheryn runtime protocol and parser scenarios;
- MariaDB transaction, concurrency and persistence-abuse scenarios;
- Redis/multichannel ownership and fail-closed scenarios;
- maintained-client hostile-server payload scenarios;
- MyAAC authentication, session and web-input scenarios;
- full-stack attack chains composed from already-approved component adapters.

The core registry/report format must remain independent of any single server name. Target-specific behavior belongs in adapters and scenarios.
