# OWA-003D — Exact TCR-to-QA Operational Execution

## Disposition

```text
EXECUTED_OPERATIONAL_EVIDENCE
OWA003D_RETAINED_TCR_QA_FRESHNESS_IMPACT
```

The exact externally supplied snapshot-B package removed the OWA-003C recovery blocker. Existing merged owners were executed without adding another parser, gateway, router, provenance engine, dependency graph, Semantic Diff implementation, QA engine or renderer.

The first canonical downstream stage remains fail closed:

```text
BLOCKED_EXTERNAL_EVIDENCE
OWA003D_NO_REVIEWED_QA008_ROOT_AND_CANONICAL_MAP_CHANGE_CHAIN
```

This is not a failure of the executed TCR-to-QA chain. It records that client-reference drift is not itself a map change and cannot be converted into a synthetic/no-op Semantic Diff or an OWA-006 candidate.

## Exact external inputs

| Input | Identity |
|---|---|
| Snapshot A archive | version `15.25.bd5a04`; SHA-256 `01c45146e2fcec3f4087844e0cbc1817fb1d60b310a35ac5d88c07aab6f73d1a` |
| Snapshot B archive | version `15.31.69f220`; SHA-256 `95093b15462573cc413fc7752d99ab258f97b58734bc59a8f6ef34cc1921a0f8` |
| Parser revision | `b68fbf7bf26b57f0cf716abffb52cfa951fa66ce` |
| Current source map | SHA-256 `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2` |

Snapshot B exactly matches the package identity recorded by accepted TCR-009 evidence. The source map is the current OWA-001 map and was never treated as a distinct candidate.

## TCR-009 deterministic rematerialization

The historical reviewer-authored manifest path/metadata bytes were not retained, so their old file hashes were not reconstructed from prose. The exact package bytes, selected package inputs and accepted parser revision were instead rerun through the existing manifest and index owners.

The fresh deterministic drift has:

- file SHA-256 `5006bf1cac1b9b0da91c500debedc15270224801abcf5202b01b938d5f691fbb`;
- exactly `27` findings, matching the accepted semantic result;
- `23` added and `4` changed findings;
- component distribution: package metadata `1`, proficiencies `24`, StaticData `2`;
- family distribution: input-component `3`, proficiency definition `23`, StaticData schema-family `1`;
- field-change count `8`.

Fresh final manifests are independently hash-closed as:

- snapshot A: `093be8456aa21e7081208c055443b3b72f4d9afa45b65a90279c5d58f5fc90f9`;
- snapshot B: `e97291b857992414714030136f378e693db8335ee7d51ad3df37ace7ea2a6a9f`.

They are new executions over the exact accepted package identities, not claims that missing historical reviewer-authored bytes were recovered.

## TCR-010 exact evidence gateway

A reviewer-authored binding selected exactly four existing drift fragments: `/findings/0`, `/findings/1`, `/findings/25` and `/findings/26`.

- binding SHA-256: `6db1167b70141798eeaa43590392235adb631cb043d99a426986f32f316dc1b9`;
- gateway file SHA-256: `04fb4447be7e8a263d2808908e94528178447afcbf06fedcf3e4da54c0646776`;
- gateway report SHA-256: `9de775ee19304140c26b7f80e80b477589a8e4f58460fe87649c2f5e60f4d782`;
- evidence-bundle SHA-256: `5245026071cd9af395cd97cc599643fdbdee0bbba033e6843abbda52518ba87f`.

## TCR-011 exact adoption routing

- request SHA-256: `76b4f0da321c795c0b5275664e18ebc40178cd48b341b2e523f0f7705672ec41`;
- routing file SHA-256: `21345ba21a1bad3f0f08e259663cd10abb9101e5a9db1e50e1f63793dbe8600e`;
- routing report SHA-256: `83466a8e8377876e067e535e492ea2998fac9158dfae96585c520451e8cde800`.

The exact reviewed result contains four extracts:

1. package metadata is routed to existing `tcr-client-manifest` / `canary-tibia-client-reference-manifest-v1` ownership;
2. proficiencies are routed to existing `tcr-proficiency-correlation` / `canary-tibia-proficiency-reference-correlation-v1` ownership;
3. StaticData input identity remains targetless `unsupported-fragment-shape`;
4. StaticData schema-family drift remains targetless `unsupported-fragment-shape`.

Unsupported fragments were not silently promoted into handled routes.

## QA-016 exact BOM and release provenance

The existing QA-016 owner was executed over one exact previous/current BOM pair:

- previous canonical BOM SHA-256: `92e82bd868da5b279f36aca4f3429e9831c82892fde7acd0077c2bb075f6dada`;
- current canonical BOM SHA-256: `a1743f9203cac5679b4be7e5b094822d07638b6f95f16e223035f205f0eed6c6`;
- release-provenance file SHA-256: `dab40d9317d262eda7bd5b667d9a480c89f1f64212d0650feebc276acd5f44c0`;
- release-provenance report SHA-256: `e4ed44bc2bb2fa08c232f7d02db1b23143cd75f6610085abbc94b079e7dc7f96`.

The current map and StaticMapData remain current. Client manifest, proficiencies and StaticData are changed and their declared dimensions are stale.

## OWA-003A exact freshness impact

Reviewer-authored mapping:

- review ID: `owa003d.owa003a.review.20260731`;
- review statement: `Exact reviewed mapping binds the routed package-manifest and proficiency-reference extracts to the matching changed QA-016 components and their sole stale dimensions; both unsupported StaticData routes remain targetless and unmapped.`

Exact output identities:

- manifest file SHA-256: `95b5be1dfc130a766ee75473db5b7f113c20cf151bf963e0dc6f8a159d5649c8`;
- manifest canonical SHA-256: `b3a98430c22ce9e7d94742249975907113efd21a24d2e9496544c973f669b7a0`;
- freshness-impact file SHA-256: `6c0334f18cd35524dd85465a0a7d6cf0c8a6e9c959d29c3dbf7352cbb673e241`;
- freshness-impact report SHA-256: `8dbec4bac254a53d4138a50baebce1167993329d50217e9e0d1e9f51250e372c`;
- byte size: `5316`.

The output contains two routed stale dimensions:

- `qa006.tcr-client-manifest`;
- `qa006.tcr-proficiency-reference`.

Both StaticData routes remain explicit targetless `unsupported` impacts. QA-008, QA-002 and QA-007 remain `not-evaluated`; QA-006 remains `not-refreshed`.

## Durable retained artifact

The exact impact and its associated execution identities are retained outside Git:

- workflow run ID: `30614565219`;
- artifact ID: `8786807858`;
- artifact name: `owa-003d-operational-evidence`;
- artifact digest: `sha256:48c79f9ecff88782d4711bb0de7e312d008dca058975123ed4a9a5b55f2d24ea`;
- source branch head: `a68ee8c032415591a07334e663affee930764d35`;
- retention expiry: `2026-10-29T07:56:51Z`.

The downloaded artifact was independently hash-checked. It contains the exact freshness-impact JSON, an execution-metadata JSON binding all upstream report/BOM/provenance/package/map/review identities, and `SHA256SUMS`.

The proprietary archives, selected client inputs, generated manifests, six indexes and full drift/gateway/routing/provenance reports remain outside Git.

## Validation

- `95` focused existing-owner tests pass after reconstructing the expected repository layout from the source artifact;
- relevant Python modules compile;
- drift, gateway, router, QA-016 and freshness execution reruns are byte-deterministic;
- duplicate-key, NaN/Infinity, exact-hash, route-coverage, unsupported-preservation, changed-dependency equality, no-clobber, symlink and input/output-alias protections pass;
- retained artifact SHA-256 checks pass.

## First downstream failure

QA-008 is the first separate canonical owner after the executed impact. It requires a reviewer-declared dependency graph and compatible exact QA-001 and QA-002 reports. No such reviewed root is retained for this client-reference-only change, and no distinct reviewed before/after OTBM change exists from which canonical Semantic Diff and QA-002 evidence could be generated.

Rejected substitutions:

- client-reference drift as map authority;
- current map as both before and candidate;
- a synthetic or no-op Semantic Diff;
- guessed QA-008 dependency edges;
- mapping unsupported StaticData fragments to a convenient owner;
- validators, Physical E2E, QA-007 or QA-006 refresh without their canonical exact inputs.

Re-entry requires, in order:

1. one reviewer-authored QA-008 graph root bound to this exact impact and compatible exact QA-001/QA-002 identities;
2. one real distinct reviewed before/after map-change chain and canonical `canary-otbm-semantic-diff-v1` when map-change regression evidence is required;
3. canonical QA-002 selection, owning validators and selected Universal Physical E2E;
4. QA-007 exact result-set assurance;
5. QA-006 refresh over the resulting exact compatible evidence.

OWA-006 remains independently blocked by `OWA006_NO_RETAINED_REVIEWED_REAL_CANDIDATE_CHAIN`.
