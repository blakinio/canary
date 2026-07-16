# TSD-012 — Validation and Live Operations Decomposition

> Task-start main: `145929ec7f438dc492d4b618a386a4418953d7ec`.
> Inventory only. No validation result, deployment execution or production-safety claim is introduced by this package.

## Result

Registry grows from **61** to **62** records. Existing records remain unchanged.

Added only:

- `deployment-operations`.

Preserved unchanged:

- `otbm-tooling`;
- `physical-client-e2e`;
- `upstream-intelligence`;
- the Real Tibia registry/generator/mapper;
- all existing gameplay and validation records.

## Evidence inventory

### Canonical OTBM analysis

The existing `otbm-tooling` record already owns the durable read-only OTBM analysis surface: World Index, item/mechanic audit, script resolution, reachability, spawn/NPC evidence, storage graph, semantic diff, geometry audit and factual rendering.

Quest Map Validator, reachability, spawn/NPC, storage dependency graph, semantic diff and geometry audit therefore remain capabilities of this canonical stack or of the gameplay modules they inspect. TSD-012 does not create a second parser, indexer, renderer, resolver or validation umbrella.

### Universal physical-client E2E

The existing `physical-client-e2e` record already owns reusable exact-head Canary plus controlled OTClient scenario execution, disposable database setup, evidence artifacts and cleanup. Feature-specific validators must reuse this platform rather than creating a second orchestrator.

Open PR #245 remains independently owned and read-only to TSD-012. Its in-progress evidence does not change the existing registry maturity in this package.

### Upstream Intelligence

The existing `upstream-intelligence` record already owns read-only source watching, provenance, source-role-aware module mapping and reviewed candidate triage. UI-001A was the Upstream Intelligence source-role mapping prerequisite, not a separate user-interface module.

TSD-012 therefore creates no second watcher, source registry or mapper.

### Deployment operations

The existing Canary staging/deployment implementation under `tools/deploy/**` has its own durable operational lifecycle:

1. assemble a full staging datapack from a trusted base plus reviewed overlay;
2. run real Canary preflight smoke;
3. publish a complete release directory atomically;
4. atomically switch `active`/`previous` release pointers;
5. run post-switch smoke;
6. roll back automatically when that smoke fails and a previous release exists;
7. retain release directories and write SHA-256 manifests;
8. support dry-run and explicit production confirmation gates.

This is independent enough to register as `deployment-operations`. The module record remains inventory-only: implementation files, tests and workflows do not prove production safety, operator correctness, host-supervisor integration, rollback-target availability or runtime stability.

## Candidate decisions

| Candidate | Decision | Reason |
|---|---|---|
| deployment operations | ADD_NOW | Independent existing release/staging/switch/rollback/manifest lifecycle under `tools/deploy/**`. |
| OTBM world index | ALREADY_COVERED | Canonical `otbm-tooling`. |
| item/mechanic audit | ALREADY_COVERED | Canonical `otbm-tooling`. |
| script resolution | ALREADY_COVERED | Canonical `otbm-tooling`. |
| quest-map validator | ALREADY_COVERED | Reuses World Index/script resolution; no independent umbrella needed. |
| reachability validator | ALREADY_COVERED | Reuses canonical OTBM evidence/classification surfaces. |
| spawn/NPC validator | ALREADY_COVERED | Reuses canonical OTBM tooling and gameplay boundaries. |
| storage dependency graph | ALREADY_COVERED | OTBM/source-analysis capability, not a second top-level platform. |
| semantic OTBM diff | ALREADY_COVERED | Reuses canonical World Index and factual renderer. |
| geometry audit | ALREADY_COVERED | Reuses canonical World Index/classifier/renderer. |
| universal physical-client E2E | ALREADY_COVERED | Existing `physical-client-e2e` record; PR #245 remains independently owned. |
| Upstream Intelligence | ALREADY_COVERED | Existing `upstream-intelligence` record and single watcher/mapper. |
| generic validation platform | REJECT_DUPLICATE | Would collapse heterogeneous validators into a competing umbrella. |
| second deployment pipeline | REJECT_DUPLICATE | Existing `tools/deploy/**` implementation is the reusable operational root. |

## Registry impact

- Before: 61 records.
- After: 62 records.
- Added: `deployment-operations`.
- Existing records modified: 0.

The new record starts with lifecycle/implementation/evidence `inventory`. Persistence, protocol, automated tests, runtime validation and gameplay E2E remain `not-assessed`.

## Proof limits

This package does not prove:

- production deployment safety;
- operator correctness;
- availability of a valid rollback target;
- compatibility with a specific systemd/Docker/Kubernetes supervisor;
- real long-running server stability after deployment;
- completeness or correctness of any OTBM/gameplay validator result;
- physical-client E2E success for any gameplay module;
- semantic equivalence of watched upstream changes;
- Real Tibia parity;
- Oteryn readiness.

## Next package

After the TSD-012 feature and separate lifecycle archive both merge through exact-head Ready/Required gates, TSD-013 may classify migration posture for the completed registry inventory. TSD-013 must not copy code to Oteryn and must not create a second registry.
