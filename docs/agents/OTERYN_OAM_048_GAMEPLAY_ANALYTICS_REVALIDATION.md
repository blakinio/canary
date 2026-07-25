# OAM-048 Gameplay Analytics revalidation

## Final disposition

`gameplay-analytics → EXPERIMENTAL_ONLY`

## Exact baselines and delivery

- Canary preflight merge: `4d47714756b67cd632aeedd6c405a7fc8dba4a79`
- Otheryn task-start main: `68e2b233b02356a79a03422ed51d757b85915bc5`
- reviewed upstream: `7644bcbcbbad4a09e52a5707ed531e4dd21d8a79`
- Otheryn disposition merge: `a6e2993ed32b1316168045ad0b97ddebb50a2128`
- Otheryn lifecycle merge: `fc93848796f05108684dfbb218f7434a8cb88755`
- Canary governance task-start main: `4d47714756b67cd632aeedd6c405a7fc8dba4a79`

## Canonical responsibility

Gameplay Analytics is optional laboratory telemetry. It owns disabled-by-default Global datapack configuration, telemetry session collection, bounded buffering/retry/dead-letter behavior, optional analytics persistence, deterministic dry-run tooling, maintenance and aggregate-report discovery. It excludes gameplay formula correctness, complete telemetry coverage, production stability, privacy assurance, retention assurance, security analytics and AI investigation.

## Target proof

At the pinned Otheryn head:

- the representative analytics config path is absent;
- repository search found no `GameplayAnalytics` or `gameplay_analytics` consumer;
- no canonical module depends on Gameplay Analytics;
- no Otheryn core startup, build or runtime root requires it.

The legacy config blob `939b8b8b51fdf0c1157afb7df8af5cccf1d3ebdf` sets `enabled = false` and `anonymizePlayers = false`. The legacy loader blob `86f6ae164077ce616e87f278e553475225a52f8a` composes core, context, schema, batching, reliability and correctness layers. Existing dry-run and database tests establish selected laboratory contracts only; they do not establish target privacy, retention, deletion, schema migration, realistic load capacity or production operations.

## Isolation contract

The package may remain in Canary or a separately authorized experimental target branch only when it remains disabled and independent from core, adds no target dependency, is not automatically copied, and cannot be activated in production without a separate product/privacy/retention/deletion/schema/capacity/operations contract. Analytics failures must not affect gameplay or persistence correctness.

## Exact-head target gates

Otheryn disposition head `620d29db5d7bb9ef1fa8b39f1d1b7f70dc91c75b` passed Required `30170065044`. PR #109 had no comments, reviews or threads, target main had zero drift, and expected-head squash merge produced `a6e2993ed32b1316168045ad0b97ddebb50a2128`.

Otheryn lifecycle head `f5a8a05c942433a412300a8046f91c98eefc5362` passed Required `30170145992`, had clean discussions and zero target-main drift, and merged as `fc93848796f05108684dfbb218f7434a8cb88755`.

## Rejected alternatives

- `REUSE`: target ownership, privacy and production criteria are not established.
- `ADAPT`: no bounded core need justifies importing legacy telemetry.
- `REWRITE`: no target product contract exists.
- `DO_NOT_MIGRATE`: too strong because isolated laboratory use remains legitimate.

## Final conclusion

OAM-048 is `gameplay-analytics → EXPERIMENTAL_ONLY`. The package is useful as isolated laboratory telemetry but is not approved for Otheryn core and introduces no target runtime path.

## Nonclaims

This disposition does not prove production privacy, anonymization, retention, deletion, schema migration, aggregation correctness, complete telemetry coverage, failure isolation under load, performance, security/AI suitability, physical-client behavior or production readiness.
