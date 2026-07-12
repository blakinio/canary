---
scenario_id: E2E-SUITE-SCENARIO
suite: feature-suite
program_id: CAN-PROGRAM-FEATURE
owner: autonomous-agent-name
status: planned
risk: low
requires:
  server_ref: main
  client_repository: blakinio/otclient
  client_ref: main
  client_version: ""
  database: disposable
  datapack: data-otservbr-global
  map: verified-download
  capabilities: []
fixture_files: []
expected_artifacts:
  - result.json
  - canary.log
  - otclient.log
  - database-after.tsv
  - screenshot.png
---

# Goal

State one observable behavior that the real server and client must prove.

# Ownership

```yaml
owned_paths:
  exclusive:
    - tests/e2e/scenarios/<suite>/<scenario>/**
  shared:
    - tests/e2e/scenario_registry.*
  read_only:
    - tools/e2e/**
    - tests/e2e/runtime/**
    - tests/e2e/client/**
```

# Preconditions

- Required Canary commit or PR:
- Required OTClient commit or PR:
- Required protocol/client version:
- Required account and character state:
- Required map positions, item IDs, storage IDs, NPCs, monsters, or capabilities:
- Evidence for every non-obvious value:

Do not invent fixtures, coordinates, identifiers, credentials, or protocol capabilities.

# Setup

1. Exact idempotent fixture action.
2. Exact readiness check.

The setup must be safe to repeat in a disposable environment and must not depend on production state.

# Client actions

1. Login action.
2. Exact UI, movement, chat, item, combat, or protocol action.
3. Logout/relog action when persistence is part of the behavior.

# Assertions

## Client/UI

- Observable widget, text, state, event, or parser result.

## Server

- Expected server log, state transition, or protocol response.

## Database

- Exact precondition query:
- Exact post-action query:
- Exact post-relog query:

## Negative checks

- No crash, assertion, parser error, protocol error, unhandled exception, or forbidden warning.

# Timeouts and failure markers

- Per-phase timeout:
- Global timeout:
- Required failure marker written before exit:
- Required process exit behavior:

# Artifacts

- machine-readable result with scenario ID, refs, versions, phase results, and final status;
- Canary stdout/stderr;
- OTClient stdout/stderr;
- SQL snapshots before, during, and after the scenario;
- screenshot at the relevant state;
- map, asset, binary, and configuration hashes when externally resolved;
- crash or core evidence when available.

# Cleanup

1. Logout the test character when possible.
2. Stop OTClient, Canary, virtual display, and helper processes.
3. Remove the disposable database, volumes, temporary assets, downloaded map, and generated config.
4. Preserve only approved workflow artifacts.

Cleanup must run on success, failure, cancellation, and timeout.

# Local execution

```text
run-e2e --suite <suite> --scenario <scenario_id>
```

This command is the target interface. Use the actual canonical runner command once the E2E platform task defines it.

# CI execution

- Trigger conditions:
- Required or optional check:
- Expected maximum duration:
- Artifact retention:

# Acceptance criteria

- [ ] Real Canary starts and reports readiness.
- [ ] Real OTClient connects and performs the scenario.
- [ ] Every required client, server, and SQL assertion passes.
- [ ] Relog/persistence assertions pass when applicable.
- [ ] Failure evidence is useful and cleanup completes.
- [ ] No production or proprietary data is used or retained.
- [ ] The workflow result is verified on the current commit.

# Handoff

## Start here

List the exact platform version, task, PR, and evidence artifact needed to continue.

## Do not repeat

Record failed setup, asset, protocol, timing, and automation approaches.

## Open questions

- None.
