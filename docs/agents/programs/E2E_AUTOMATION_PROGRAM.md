---
program_id: CAN-PROGRAM-E2E-PLATFORM
name: Universal OTS E2E automation
status: active
owner: e2e-platform-agent
created: 2026-07-13T00:00:00+02:00
updated: 2026-07-13T00:30:00+02:00
last_verified_commit: 97639776bb37c4f9aa1fa301cf43e7693a03a735
primary_paths:
  - tools/e2e/**
  - tests/e2e/runtime/**
  - tests/e2e/client/**
shared_integration_paths:
  - .github/workflows/*e2e*.yml
  - tests/e2e/scenario_registry.*
related_programs:
  - CAN-PROGRAM-CYCLOPEDIA
  - CAN-PROGRAM-QUEST-AUDIT
  - CAN-PROGRAM-WHEEL-OF-DESTINY
  - CAN-PROGRAM-OTBM
cross_repo_contracts:
  - OTS-E2E-CANARY-OTCLIENT
---

# Mission

Build one reusable, disposable environment in which autonomous agents can run real Canary and a real OTClient, execute feature-specific scenarios, verify protocol and database effects, collect evidence, and clean up without touching production systems.

Cyclopedia is the first prototype consumer. It is not the owner of the common platform.

# Confirmed existing foundations

The repository already contains reusable pieces that must be extended rather than replaced:

- `docker/docker-compose.yml` starts the database, Canary, MyAAC, and login server with the global datapack contract;
- `.github/scripts/docker-quickstart-smoke.sh` already performs startup, health, login-server, diagnostics, and cleanup checks;
- `docker/data/01-test_account.sql` and `docker/data/02-test_account_players.sql` provide deterministic test accounts and characters;
- the main CI publishes Canary build artifacts and runs global datapack smoke checks;
- `blakinio/otclient` is the maintained user-owned client repository and must be the controlled client source for permanent cross-repository work;
- draft PR #224 is the first live Canary + MySQL + OTClient/Xvfb experiment and must be treated as prototype evidence, not copied into every feature suite.

# Platform responsibility

The E2E platform owns reusable infrastructure for:

- disposable MariaDB/MySQL bootstrap, schema import, fixture loading, snapshots, and teardown;
- Canary artifact resolution or local build, isolated configuration, startup, readiness, and shutdown;
- global datapack and map acquisition with hashes and no committed binary assets;
- OTClient artifact resolution or build from a pinned user-owned revision;
- temporary client assets installation with integrity evidence;
- Xvfb or another approved virtual display;
- deterministic account, character, world, host, port, and version configuration;
- login, logout, relog, timeout, crash, and cleanup handling;
- a stable Lua scenario API and generic scenario runner;
- SQL assertions, protocol-event assertions, screenshots, logs, traces, and machine-readable results;
- one-command local execution and reusable GitHub Actions execution.

The platform must not encode feature-specific expected gameplay values.

# Feature-suite responsibility

Feature programs own only their own scenario definitions, fixtures, and assertions. Planned suite roots include:

- `tests/e2e/scenarios/login/**`
- `tests/e2e/scenarios/cyclopedia/**`
- `tests/e2e/scenarios/quests/**`
- `tests/e2e/scenarios/wheel/**`
- `tests/e2e/scenarios/forge/**`
- `tests/e2e/scenarios/market/**`
- `tests/e2e/scenarios/npc/**`
- `tests/e2e/scenarios/combat/**`
- `tests/e2e/scenarios/instances/**`
- `tests/e2e/scenarios/protocol/**`

A feature task consumes platform code as read-only unless a separate platform task explicitly owns a required common-interface change.

# Ownership examples

## Platform task

```yaml
program_id: CAN-PROGRAM-E2E-PLATFORM
owned_paths:
  exclusive:
    - tools/e2e/**
    - tests/e2e/runtime/**
    - tests/e2e/client/**
  shared:
    - .github/workflows/universal-e2e.yml
    - tests/e2e/scenario_registry.*
  read_only:
    - tests/e2e/scenarios/**
```

## Feature scenario task

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

# Stable scenario contract

Each scenario must define:

- unique scenario ID and owning program;
- required server/client versions and capabilities;
- database and character fixture requirements;
- setup steps that are safe to repeat;
- client actions or protocol requests;
- observable server, client, UI, and SQL assertions;
- relog or persistence checks when relevant;
- timeout and failure markers;
- artifacts to retain;
- cleanup requirements;
- paths the feature task may and may not edit.

Use `docs/agents/templates/E2E_SCENARIO.md` when adding a suite.

# Interface-change rule

When a feature needs a new generic capability:

1. the feature task records the missing capability and proposed interface;
2. a separate E2E-platform task claims and implements the reusable capability;
3. the platform PR adds generic focused tests;
4. the feature PR consumes the stable interface without copying orchestration;
5. `depends_on` and `blocks` record merge order;
6. Canary/OTClient changes use a shared coordination ID and the cross-repository contract rules.

# Execution target

The eventual user-facing interface should support commands equivalent to:

```text
run-e2e --suite login
run-e2e --suite cyclopedia
run-e2e --suite quests
run-e2e --suite wheel
run-e2e --suite forge
run-e2e --all
```

The exact executable name and implementation language remain implementation decisions for the platform task. Agents must derive them from verified repository conventions rather than inventing a second runner.

# Current active prototype

| Task/PR | State | Reusable evidence | Required treatment |
|---|---|---|---|
| PR #224 `test/cyclopedia-live-e2e` | draft; live workflow currently under repair | MySQL service, Canary/global-map setup, OTClient/Xvfb automation, relog, protocol assertions, SQL checks, evidence artifacts | Extract common orchestration into the platform; keep Cyclopedia requests and assertions in its suite; do not merge copied feature-specific infrastructure as the final architecture. |

# Ordered queue

1. Merge the coordination and ownership contract in PR #222.
2. Repair the live prototype sufficiently to record the first complete physical-client run.
3. Extract common setup, artifact resolution, lifecycle, diagnostics, and result format into one platform task.
4. Convert Cyclopedia logic into the first feature suite.
5. Add a minimal login/relog baseline suite that every platform change must pass.
6. Add quest, Wheel, Forge, and other suites through separate feature-owned tasks.
7. Add local one-command execution after the CI contract is stable.

# Safety invariants

- no production credentials, database, host, or irreversible external action;
- no committed Tibia assets, downloaded OTBM files, database dumps, or secrets;
- every run uses a unique disposable environment and always attempts cleanup;
- external binaries and assets are pinned or hash-recorded;
- failures retain enough evidence to diagnose the exact phase;
- feature PRs never silently modify shared platform lifecycle behavior;
- platform PRs treat all registered feature suites as compatibility inputs;
- no E2E success claim without a verified real workflow result on the current commit.

# Handoff

## Start here

Read `AGENTS.md`, `docs/agents/README.md`, this program record, active E2E task records, PR #224, Docker quickstart smoke, and the current Canary/OTClient artifact contracts.

## Do not repeat

- Do not create one complete workflow per feature.
- Do not use `opentibiabr/otclient` as a writable target.
- Do not commit client assets or map binaries.
- Do not replace existing quickstart lifecycle logic without recording why it cannot be reused.

## Open questions

- Whether the first canonical database target should reuse MariaDB 11.4 quickstart or introduce a deliberate MariaDB/MySQL matrix.
- Which exact OTClient artifact layout is stable enough to become the resolver contract.
- Whether scenario automation should remain injected through `otclientrc.lua` or use a dedicated test module in `blakinio/otclient`.
