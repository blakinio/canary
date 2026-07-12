# Universal OTS E2E Automation Program

The E2E platform is a repository-wide test system for any Canary and OTClient feature. Cyclopedia is only one possible scenario suite.

## Program identity

Recommended ID: `CAN-PROGRAM-E2E-PLATFORM`

The platform owns reusable infrastructure for:

- isolated MySQL bootstrap and teardown;
- Canary build, configuration, startup, health checks, and shutdown;
- global datapack loading;
- deterministic test account, character, and fixture provisioning;
- OTClient build, startup, virtual display, input automation, and shutdown;
- login and session establishment;
- server, client, database, screenshot, video, trace, and crash artifacts;
- common retry, timeout, cleanup, and failure diagnostics;
- a generic scenario runner and stable scenario API;
- local one-command execution and CI execution where supported.

## Scenario suites

Each feature program owns only its scenarios, fixtures, and assertions. Example suites:

- `tests/e2e/scenarios/cyclopedia/**`
- `tests/e2e/scenarios/quests/**`
- `tests/e2e/scenarios/wheel/**`
- `tests/e2e/scenarios/forge/**`
- `tests/e2e/scenarios/market/**`
- `tests/e2e/scenarios/npc/**`
- `tests/e2e/scenarios/combat/**`
- `tests/e2e/scenarios/instances/**`
- `tests/e2e/scenarios/protocol/**`
- `tests/e2e/scenarios/login/**`

No feature program owns the shared platform exclusively.

## Ownership split

### E2E platform task

```yaml
program_id: CAN-PROGRAM-E2E-PLATFORM
owned_paths:
  exclusive:
    - tools/e2e/**
    - tests/e2e/runtime/**
    - tests/e2e/client/**
  shared:
    - tests/e2e/scenario_registry.*
  read_only:
    - tests/e2e/scenarios/**
```

### Feature scenario task

```yaml
program_id: CAN-PROGRAM-QUEST-AUDIT
owned_paths:
  exclusive:
    - tests/e2e/scenarios/quests/**
  shared:
    - tests/e2e/scenario_registry.*
  read_only:
    - tools/e2e/**
    - tests/e2e/runtime/**
    - tests/e2e/client/**
depends_on:
  - CAN-E2E-PLATFORM-BOOTSTRAP
```

The same pattern applies to Cyclopedia, Wheel, Forge, market, NPCs, combat, instances, protocol, and future modules.

## Interface rule

When a feature needs a new generic capability:

1. the feature task documents the missing capability and required interface;
2. a separate E2E-platform task implements the reusable capability;
3. the platform PR adds generic focused tests;
4. feature programs consume the stable interface without duplicating orchestration;
5. dependency ordering is recorded with `depends_on` and `blocks`.

## Execution model

A feature agent may autonomously:

1. provision the isolated environment through the shared platform;
2. run its own scenario suite;
3. collect evidence;
4. create focused remediation tasks and PRs;
5. rerun the same scenarios until they pass;
6. continue to the next finding.

It must not silently modify shared MySQL bootstrap, Canary startup, client automation, login, global timeout, or cleanup behavior inside a feature-specific repair PR.

## Target outcome

One reusable command should eventually support filtered execution, for example:

```text
run-e2e --suite cyclopedia
run-e2e --suite quests
run-e2e --suite wheel
run-e2e --suite forge
run-e2e --all
```

The exact implementation command is not defined by this coordination document and must be derived from the actual repository, available assets, supported client, and verified runtime environment.
