# OAM-027 Houses Revalidation

## Final disposition

```text
houses ADAPT
```

## Immutable task-start baselines

- legacy/governance Canary: `0251b96105720cb67d5ed7a1b3ec8350baa8e312`
- Otheryn target: `5003753e491250732910e9d5857b20293d1bd9ab`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `a6868920443dc285656bd016acdb2c1ea566e511`

Canonical `houses` owns `src/map/house/**` and `src/io/iohouse.*`. Its canonical dependencies are `otbm-tooling` and `player-persistence`; the former is active/mapped/audited as the map evidence foundation and the latter is already completed by the OAM persistence foundation.

## Revalidation evidence

Task-start Otheryn and fresh upstream shared `src/map/house/house.cpp` blob `25fa954a55763bc9473234682d143c9761843403`. Blob identity alone was not accepted. Delivered legacy history was reviewed and identified merged Canary PR #60, final commit `a6977beb06883fb4384476315f3dc17772f99ba4`, as a bounded single-file correctness donor for house transfer orchestration.

The accepted donor boundary contains four related safety corrections:

1. snapshot tile/container item collections before wrapping or recursion can mutate the live collection;
2. ignore stale snapshot entries whose parent already changed;
3. deduplicate the final depot move queue by item identity;
4. validate wrapped results before queueing and preserve the original item ID for failure diagnostics.

Whole-file legacy reuse was rejected because current legacy `house.cpp` also contains separately owned multichannel house ownership/mirroring architecture. OAM-027 deliberately does not import `account_house_ownership`, `houses.channel_id`, cross-channel ownership handoff, cluster mirroring, or generic multichannel house state.

Fresh open-PR/ownership audit found no active writer over the canonical house production paths. The open house-related security PR #526 is evidence-only documentation and does not own house runtime.

## Target delivery

Otheryn PR #55 final head `3cfc133a835f7ad14ed8a94cc720c1f0b1a31a65` changed exactly five intended paths:

- `docs/agents/tasks/active/OTH-20260720-oam027-houses-adapt.md`
- `docs/oam-027-houses-adapt.md`
- `src/map/house/house.cpp`
- `tests/unit/game/CMakeLists.txt`
- `tests/unit/game/oam_027_houses_adapt_test.cpp`

Temporary materialization helper/workflow paths were removed before final gating. The first ready-state Linux debug CTest on head `e3c18e52940df481521ae9c8c413c3f5420a383f` passed 411/412 tests; the sole failure was a new synthetic `House` construction test that segfaulted without full runtime initialization. The independent OAM-027 transfer-safety source-contract test passed. That failing proof-only harness was removed without production changes.

The resulting exact final head `3cfc133a835f7ad14ed8a94cc720c1f0b1a31a65` passed autofix.ci #167 run `29782520081`, CI #202 run `29782520156`, and Required #184 run `29782520075`. Linux debug compilation, Canary runtime smoke, database schema import and full `Run Tests` passed; Linux release, macOS, both Windows build paths, Docker, Fast Checks and Lua Tests passed. Final test-log artifact `8477497565` has digest `sha256:548c9077d94c94c515bff2e33c574bcb67b5b9a31eb09124b152976eb048b349`.

Target comments, submitted reviews and review threads were empty. Otheryn `main` had no drift from immutable target base `5003753e491250732910e9d5857b20293d1bd9ab` through the merge gate. PR #55 merged by expected-head squash as `c140c4bb9f40067acc36bc446c9e664e6f791c5a`.

## Canary drift audit

Before governance completion Canary `main` advanced from task-start `0251b96105720cb67d5ed7a1b3ec8350baa8e312` to `6b1bbadf5c9fdc9c4b5831dcfbdef9c9ed894b3d` through independent OTBM/E2E work. The exact changed paths were `docs/agents/MODULE_CATALOG.md`, the OTBM-E2E-008 archive, two OTBM E2E impacted-selection documents and two OTBM impacted-selection tooling/test files. None overlaps the OAM-027 governance paths or canonical house runtime. The governance branch was therefore reconstructed onto current `main` rather than carrying stale ancestry.

## Explicit non-claims

OAM-027 does not claim generic house purchase/auction transaction atomicity, crash-safe transfer recovery, distributed or multiwriter house ownership, cross-channel house safety, Cyclopedia house-tab correctness, protocol/client UI compatibility, exhaustive rent/auction parity, physical-client house E2E closure, full Real Tibia house parity, or map/OTBM correctness. It changes no maintained OTClient, map/OTBM data, schema, assets or deployment.
