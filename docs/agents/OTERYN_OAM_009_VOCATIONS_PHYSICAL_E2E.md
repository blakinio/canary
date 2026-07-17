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

`tests/e2e/scenarios/login/scenario.json` already uses:

- maintained OTClient `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`;
- fixture character `Knight 1`;
- physical login;
- safe logout;
- relog;
- second safe logout;
- `lastlogin > 0` and `lastlogout > 0` SQL assertions.

OAM-009 adds exactly one bounded SQL assertion:

```sql
SELECT vocation = 4 FROM players WHERE name = 'Knight 1'
```

## Controlled target execution

The package reuses the existing Universal Agent E2E controlled-server contract. During proof collection only, the same-repository PR may carry `.github/e2e-controlled-server.env` pinned to:

```text
SERVER_REPOSITORY=blakinio/Otheryn
SERVER_REF=f59a58426b4d3910ba0cdc0d2332c24f31a1db4f
```

The temporary pin must be removed before final merge. No second workflow, runner, orchestrator, client fork, or arbitrary target source is introduced.

## Required final evidence

Before completion, record:

- exact Universal Agent E2E workflow/run;
- successful physical login/logout/relog/logout markers;
- successful SQL assertion `vocation = 4`;
- exact controlled-server source SHA;
- maintained OTClient source SHA;
- artifact digest;
- server executable SHA256;
- client executable SHA256;
- clean final PR comments/reviews/unresolved-thread state;
- final feature merge SHA;
- separate lifecycle/archive merge SHA.

## Status

Implementation started. Physical evidence not yet collected.
