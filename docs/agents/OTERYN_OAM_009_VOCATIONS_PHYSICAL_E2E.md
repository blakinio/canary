# OAM-009 — vocations physical-client E2E proof

## Scope

OAM-009 proves one bounded runtime claim for the already accepted OAM-008 `vocations → REUSE` disposition:

> Exact target `blakinio/Otheryn@f59a58426b4d3910ba0cdc0d2332c24f31a1db4f` can physically log in the deterministic fixture player `Knight 1`, whose persisted database `vocation` is `4`, through the migrated vocation registry.

This package does not claim broader vocation gameplay correctness, promotion behavior, combat behavior, spell behavior, persistence atomicity, or any new migration disposition.

## Exact task-start baselines

- governance / E2E repository: `blakinio/canary@4154d43a5b89ddc067569fde6d70f3d2c1e1e320`
- target server: `blakinio/Otheryn@f59a58426b4d3910ba0cdc0d2332c24f31a1db4f`
- maintained client: `blakinio/otclient@2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`

## Deterministic fixture

`docker/data/02-test_account_players.sql` defines:

- character: `Knight 1`
- level: `500`
- persisted vocation: `4`

## Fail-closed target load path

Exact target path:

`src/io/functions/iologindata_load_player.cpp`

`IOLoginDataLoad::loadPlayerBasicInfo`:

1. reads `vocation` into `vocationId`;
2. calls `player->setVocation(vocationId)`;
3. logs an error and returns `false` when the vocation ID cannot be resolved.

Therefore, a successful physical login of `Knight 1` on the exact target is bounded runtime evidence that vocation ID `4` resolves successfully. The SQL assertion below additionally proves that the deterministic persisted fixture value remained `4`; it is not treated as a substitute for the physical login.

## Exact registry evidence

Exact target `data/XML/vocations.xml` defines vocation ID `4` as `Knight`.

## Existing physical scenario reused

`tests/e2e/scenarios/login/scenario.json` uses:

- maintained OTClient `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`;
- fixture character `Knight 1`;
- physical login;
- safe logout;
- relog;
- second safe logout;
- `lastlogin > 0` and `lastlogout > 0` SQL assertions.

OAM-009 adds exactly one bounded scenario SQL assertion:

```sql
SELECT vocation = 4 FROM players WHERE name = 'Knight 1'
```

## SQL assertion runner gap and bounded fix

The first physical run, Universal Agent E2E run `29589941229`, physically passed `login/relog` on the exact Otheryn target, but inspection showed that `tools/e2e/run_physical_e2e.sh` did not execute `scenario.assertions.sql`; it only evaluated the existing hardcoded `lastlogin` and `lastlogout` checks. That run is retained as preliminary evidence only and is not accepted as OAM-009 proof.

The existing generic physical runner was then extended without adding a second orchestrator. It now:

- reads every canonical `scenario.assertions.sql` entry;
- accepts only one semicolon-free `SELECT` statement per assertion;
- executes each assertion independently through the existing MariaDB client;
- requires return code `0` and scalar stdout exactly `1`;
- records per-assertion evidence in `sql-assertions.json`;
- fails the physical scenario unless every canonical SQL assertion passes.

The existing hardcoded `lastlogin` and `lastlogout` evidence remains in place.

## Controlled target execution

The package reuses the existing Universal Agent E2E controlled-server contract. During proof collection only, the same-repository PR carried `.github/e2e-controlled-server.env` pinned to:

```text
SERVER_REPOSITORY=blakinio/Otheryn
SERVER_REF=f59a58426b4d3910ba0cdc0d2332c24f31a1db4f
```

No second workflow, runner, orchestrator, client fork, or arbitrary target source was introduced. The temporary controlled-server pin was removed before final merge validation; the accepted physical evidence below remains durable.

## Accepted physical evidence

Universal Agent E2E:

- workflow run: `29593102547` / run number `191`
- PR test head: `97ee305ae8960d2df2edb16f3051fbd8b702c2a0`
- GitHub pull-request merge test SHA reported by runtime `GITHUB_SHA`: `3ab27bebaa980272c3ee0f5bc15b98d810de0d5e`
- physical job: `Physical client / login/relog` — SUCCESS
- required physical E2E gate — SUCCESS
- controlled server repository: `blakinio/Otheryn`
- controlled server requested ref: `f59a58426b4d3910ba0cdc0d2332c24f31a1db4f`
- controlled server resolved commit: `f59a58426b4d3910ba0cdc0d2332c24f31a1db4f`
- maintained OTClient resolved commit: `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`
- physical artifact: `universal-agent-e2e-login-relog`
- physical artifact digest: `sha256:f880b2fb58c53d8e53aad4cc30725a26a050c352bd5412a10c56b8a61f327f3f`
- exact controlled-server executable SHA256: `3a191e398ea22818a9e71cd3ce0fe60486e1e0592cddb379295504a77dc62925`
- controlled-client executable SHA256: `5dcaed6cdfcaecf2de4b9de80183a28fe8e0722e21b4df588cc627c558da5ee9`

Physical markers:

- first physical login — SUCCESS
- first stable online state — confirmed
- first safe logout — complete
- second physical login / relog — SUCCESS
- second stable online state — confirmed
- second safe logout — complete
- two server logins observed
- two packet records present
- client exit code `0`
- no fatal runtime log hits
- final `players_online` count `0`

Canonical SQL assertion evidence from `sql-assertions.json`:

1. `SELECT lastlogin > 0 FROM players WHERE name = 'Knight 1'` — executed, stdout `1`, PASS
2. `SELECT lastlogout > 0 FROM players WHERE name = 'Knight 1'` — executed, stdout `1`, PASS
3. `SELECT vocation = 4 FROM players WHERE name = 'Knight 1'` — executed, stdout `1`, PASS

`result.json` records:

- `status: success`
- `checks.required_markers: true`
- `checks.scenario_sql_assertions: true`
- `checks.two_server_logins_observed: true`
- `checks.two_packet_records_present: true`
- `checks.lastlogin_persisted: true`
- `checks.lastlogout_persisted: true`
- `checks.no_fatal_runtime_log: true`

This is accepted as the bounded OAM-009 physical proof that exact target Otheryn resolves persisted vocation ID `4` sufficiently for `Knight 1` to complete the canonical physical login/logout/relog/logout flow. It does not expand the claim beyond that boundary.

## Final feature baseline

Before final feature gates, the branch was reconstructed directly on latest non-overlapping Canary `main@8aa4d7def083c3701b9c81119ec2aa8ea26a68af` with only the four durable OAM-009 feature paths:

- `docs/agents/OTERYN_OAM_009_VOCATIONS_PHYSICAL_E2E.md`
- `docs/agents/tasks/active/CAN-20260717-oteryn-vocations-physical-e2e.md`
- `tests/e2e/scenarios/login/scenario.json`
- `tools/e2e/run_physical_e2e.sh`

The temporary controlled-server pin is absent from the final PR diff. No unrelated `main` changes remain in PR #489.

## Remaining lifecycle work

Before OAM-009 is fully complete:

- require final exact-head ownership/CI/review gates with zero unresolved review threads;
- merge the feature PR;
- complete the separate lifecycle/archive PR;
- reconcile the durable program record in a separate program-only PR.

OAM-010 must not start before those steps are complete.

## Status

Physical proof accepted. Final feature gates, merge, lifecycle/archive, and durable program reconciliation remain pending.
