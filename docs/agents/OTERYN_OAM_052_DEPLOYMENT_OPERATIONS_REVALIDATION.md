# OAM-052 Deployment Operations revalidation

Status: **target disposition and lifecycle complete; Canary governance pending**

Program: `CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION`

Coordination: `OAM-052`

## Final disposition

```text
deployment-operations → DO_NOT_MIGRATE
```

The canonical Canary package remains reviewed-content staging and atomic datapack release infrastructure in the legacy laboratory. Otheryn does not receive a copy of `tools/deploy/**`, the Canary-aware smoke adapter, content-deployment workflows, release-root symlink model or manifest implementation.

This decision does not remove the need for Otheryn production deployment engineering. Target production backup, recovery, future Compose, supervisor, rollout and rollback responsibilities remain separately governed by the bounded Production Resilience (`PRS-*`) programme.

## Pinned evidence

```text
Canary preflight base:      4bb098d6401a40659b3de2ef506f093eb35ea8d8
Canary preflight merge:     80d5daebd1804edc6208e2312733b5b484490587
Otheryn target task start:  d585c1b8120973d50a3e846fb9e3b063ef3019ff
Otheryn feature head:       b0e6a965399008a9834f8449c95981d78885ed10
Otheryn feature merge:      2afcaef4a3d023a7ec987e4380e80905534fdd2b
Otheryn lifecycle head:     b5e6fbb7b99280c2d3cc011386d7e23e3a26c8ba
Otheryn lifecycle merge:    2c085eee1b1c430d09a87f567aac1a8e701721a4
upstream evidence baseline: 7644bcbcbbad4a09e52a5707ed531e4dd21d8a79
```

## Canonical boundary

The registry record owns:

- trusted base plus reviewed-overlay staging;
- real Canary preflight smoke;
- atomic release-directory publication;
- atomic `active` and `previous` switching;
- post-switch smoke and rollback when possible;
- SHA-256 release manifests;
- dry-run and explicit production confirmation gates.

It explicitly excludes content authoring, map mutation, host process-supervisor ownership, automatic production approval, guaranteed rollback-target availability and production-safety claims.

## Why DO_NOT_MIGRATE

Current Canary evidence is rooted in `tools/deploy/**` and assumes:

- Canary repository and datapack layout;
- a compiled Canary binary;
- explicit base datapack and reviewed overlay inputs;
- temporary smoke databases and ports;
- a filesystem release root with symlink switching;
- Canary-specific workflows and smoke integration.

Current Otheryn has no matching implementation root, workflow, startup hook, runtime consumer, release API, promotion handoff or supervisor contract. Generic atomic rename, checksums and rollback mechanics are not enough to prove `REUSE` or justify speculative `ADAPT`.

Otheryn PRS-001, merged as `3813a25cc91e37714b69d9eac2fff9e7aaaf3cb2`, owns disposable backup/PITR proof and recovery-set publication. It does not own datapack release switching. PRS-008 remains the future owner of production Compose and hardening. The target production boundary explicitly forbids gameplay/OAM packages from opportunistically adding production deployment behavior.

## Target delivery evidence

Otheryn PR #136 changed exactly:

- `docs/agents/tasks/active/OTH-20260726-oam052-deployment-operations-disposition.md`;
- `docs/oam-052-deployment-operations-disposition.md`.

Final head `b0e6a965399008a9834f8449c95981d78885ed10` passed exact-head Required run `30214361783`. Comments, reviews and review threads were empty, the branch was behind target `main` by zero, and the PR squash-merged with expected-head protection as `2afcaef4a3d023a7ec987e4380e80905534fdd2b`.

Lifecycle PR #138 moved the task to archive and updated only the disposition report. Final lifecycle head `b5e6fbb7b99280c2d3cc011386d7e23e3a26c8ba` passed Required run `30214475223`, had a clean discussion/path/drift audit and squash-merged as `2c085eee1b1c430d09a87f567aac1a8e701721a4`.

No target runtime, deployment script, workflow, Compose file, scheduler, service, schema, map/datapack content, endpoint, secret, production configuration or host action was added.

## Cross-repository responsibility

Canary retains the current content-release toolchain as laboratory and validation infrastructure. Otheryn may design a different target-owned release mechanism only through a separately authorized bounded package that defines:

- release artifact and target consumer;
- supervisor and lifecycle ownership;
- configuration and secret handling;
- serialization and failure injection;
- rollout, health, rollback and removal procedures;
- exact controlled validation and operator gates.

A future target package would be new engineering from current Otheryn requirements, not approval to copy the Canary package.

## Boundary classification

| Boundary | Result |
|---|---|
| ownership/lifecycle | Canary owns the existing package; no current Otheryn owner or consumer exists. |
| build/toolchain | No Otheryn build entry consumes Canary deployment Python tooling. |
| configuration | Target production configuration remains PRS-owned. |
| service/API | No target release/promotion/supervisor interface exists. |
| scheduling/concurrency | No production deployment scheduler or serialization contract exists. |
| persistence | Release manifests/symlinks are operational state, not gameplay/database persistence. |
| protocol/session | Not applicable. |
| identifiers/assets | No target asset or datapack migration is authorized. |
| world/map | Static/content validation does not authorize map mutation or blind import. |
| runtime | No target deployment runtime was added or executed. |
| tests | Docs-only exact-head gates validate the disposition, not production behavior. |
| physical-client E2E | Not applicable. |
| operations | Future target deployment remains separately governed under PRS. |
| security/privacy | No endpoint, credential, key, release root or host was accessed. |

## Rejected alternatives

- copy Canary `tools/deploy/**` and workflows wholesale;
- classify PRS-001 recovery-set publication as reviewed datapack deployment;
- add production Compose, scheduler or supervisor integration through OAM-052;
- infer `REUSE` from generic atomic filesystem mechanics;
- infer that `DO_NOT_MIGRATE` means Otheryn needs no future deployment implementation.

## Nonclaims

OAM-052 does not claim complete Otheryn production deployment, PRS-008 implementation, application rollout safety from backup/PITR, permanent sufficiency of Canary tooling, guaranteed rollback targets, real supervisor consumption of symlinked datapacks, production readiness, operator correctness, availability, RPO or RTO.
