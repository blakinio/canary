# Universal Agent E2E

This directory contains feature-neutral scenario manifests consumed by one shared Canary + OTClient physical-client workflow.

The platform owns database setup, Canary lifecycle, OTClient lifecycle, login, evidence collection, timeouts and cleanup. Feature programs own only their scenario manifests, fixtures and assertions.

## Commands

From the repository root:

```text
python tools/e2e/run_agent_e2e.py list
python tools/e2e/run_agent_e2e.py validate
python tools/e2e/run_agent_e2e.py resolve \
  --suite login \
  --scenario relog \
  --manifest artifacts/scenario-manifest.json
```

The first physical proof is the feature-neutral `login/relog` scenario. It starts a disposable database, exact-head Canary and a real OTClient, then verifies login, clean logout, relog and final offline database state.

Current validation must run from the pull-request merge ref against the latest `main`, so server-side transport fixes already merged into Canary are included without changing the pinned OTClient revision or the physical-client scenario contract.

## Adding a scenario

1. Create `tests/e2e/scenarios/<suite>/<name>.json`.
2. Use schema version `1` and a unique `<suite>/<id>` key.
3. Reference the shared client automation or a feature-owned automation adapter.
4. Do not embed credentials, production hosts, downloaded assets, maps or database dumps.
5. Declare observable client markers and SQL assertions.
6. Validate every scenario with `run_agent_e2e.py validate`.
7. Run the existing `.github/workflows/universal-agent-e2e.yml` workflow with the suite and scenario inputs.

Do not copy the complete workflow into a feature PR. A missing generic capability must be implemented through a separate `CAN-PROGRAM-E2E-PLATFORM` task.

## Scenario contract

Required top-level fields:

- `schema_version`;
- `id`, `suite`, `name`, `program_id`, `description`;
- `client.repository`, `client.ref`, `client.automation`;
- `server.database_image`, `server.datapack`, `server.map`;
- deterministic `fixture` values and a password environment-variable reference;
- `timing` values;
- client `required_markers` and SQL assertions;
- retained artifact names.

The validator rejects malformed manifests, duplicate scenario keys, missing automation files, embedded credentials, unsafe artifact paths and repository escapes.

## Ownership example

```yaml
program_id: CAN-PROGRAM-QUEST-AUDIT
owned_paths:
  exclusive:
    - tests/e2e/scenarios/quests/**
  shared: []
  read_only:
    - tools/e2e/**
    - tests/e2e/client/**
    - .github/workflows/universal-agent-e2e.yml
```

## Evidence boundary

A successful environment startup is not a successful scenario. The workflow must retain and verify:

- exact server, client and asset references;
- scenario manifest;
- client event stream;
- server and client logs;
- SQL state while online and after exit;
- screenshot and packet records when available;
- a final machine-readable `result.json`;
- cleanup on success, failure, cancellation and timeout.
