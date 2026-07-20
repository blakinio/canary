# OAM-023 — Parties revalidation

## Result

Final disposition:

```text
parties → REUSE
```

OAM-023 revalidated the canonical `parties` package and required no production runtime, persistence, protocol, maintained OTClient, data, schema, map/OTBM, asset or deployment change.

## Immutable task-start baselines

- Canary: `0a39a0f76d5f811098dfaa7be9deea40347279d5`
- Otheryn: `50dfa248251f245f5519495a4fbd430b6814ffe4`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`

The fresh preflight confirmed that OAM-022 was fully and durably complete and that OAM-023 had not started. The durable program record contained no active OAM implementation task at task start.

## Package selection

Canonical `parties` was selected as the smallest dependency-valid package found in the fresh registry and ownership review.

Its canonical production boundary is:

```text
src/creatures/players/grouping/party.*
```

Its only canonical dependency is completed OAM-005 `character-lifecycle`.

`cyclopedia` was not selected because it is a materially broader multi-surface server/client/protocol domain. `wheel-of-destiny` was not selected because it remains under a separate parity program with independent ownership. Fresh open-PR changed-file audits showed no overlap between current parallel Canary work and canonical `party.*`.

## Evidence-driven classification

The bounded files at the immutable baselines were exact-identical across target, fresh upstream and legacy:

- `party.cpp`: `c3493c962548bffa5e393adc3359137b200b6384`
- `party.hpp`: `52b08e7321dd4e35bfb68415254239245ed236ee`

This identity was supporting evidence only, not the basis of `REUSE` by itself.

The Party core was reviewed semantically across Party creation and leader binding, member and invitation state, invite/join/leave/revoke/leadership transitions, disband cleanup, shared-experience state and fail-closed no-leader behavior. Relevant legacy-history candidates around multichannel behavior, Gameplay Analytics shared experience and Forge premium Dust were audited and did not modify the canonical `party.*` boundary. No stronger independent legacy donor for the canonical Party core was identified.

The existing Party implementation contains interaction points with vocation/Wheel behavior. Those interaction points were already identical across target, fresh upstream and legacy and remain outside this package's correctness claim; OAM-023 does not use them to claim Wheel or vocation parity.

## Target proof

Otheryn PR:

```text
#47 — test(parties): prove OAM-023 reuse
```

Final target head:

```text
c3ff8bb09b736ec835ce1f49ee0d96b8e208ea88
```

Squash merge:

```text
bcc3e9f7e3e704f3c012bda8693648d52741630f
```

Final target diff contained exactly three proof-only paths:

```text
docs/oam-023-parties-reuse.md
tests/unit/game/CMakeLists.txt
tests/unit/game/oam_023_parties_reuse_test.cpp
```

No production `party.*` file was changed.

Exact-head ready-state gates on `c3ff8bb09b736ec835ce1f49ee0d96b8e208ea88`:

- `autofix.ci` #147, run `29728346604`: SUCCESS
- `CI` #172, run `29728346757`: SUCCESS
- `Required` #154, run `29728346586`: SUCCESS

Linux debug proof:

```text
CTest: 403/403 PASS
Oam023PartiesReuseTest: 3/3 PASS
```

Test-log artifact:

```text
8455540885
```

Digest:

```text
sha256:8c3868b1047057d8419194ce7a555566b8db7dd32024f1ecb1c2cdec1424938b
```

Immediately before target merge:

- changed files: exactly 3 intended proof-only paths;
- comments: 0;
- reviews: 0;
- review threads: 0;
- Otheryn `main` drift from immutable target baseline: 0;
- PR head matched the expected final head.

PR #47 was squash-merged using expected-head protection.

## Canary main drift audit

After the target merge and before final governance reconciliation, Canary `main` advanced from the immutable task-start baseline to:

```text
e81ae95d60096db84d00b0f4ff5516b58c1ecc2d
```

The single intervening commit was the independent Thais temple-to-depot physical-route E2E/OTBM work. Its changed paths were limited to `.github/workflows/universal-agent-e2e.yml`, its OTBM task record, `tests/e2e/**` and `tools/e2e/**`.

There is no overlap with OAM-023 governance paths or canonical `src/creatures/players/grouping/party.*`, so the drift is non-overlapping and does not invalidate the immutable OAM-023 evidence baselines.

## Maintained client and protocol

The canonical `parties` registry record has no maintained OTClient path. Protocol packet compatibility and party chat transport are outside this package. No OTClient write was required or authorized.

OAM-023 does not claim physical-client Party UI, party-channel or wire-protocol E2E closure.

## Explicit exclusions

OAM-023 does not claim or change:

- party chat transport or channel behavior;
- protocol packet compatibility or maintained OTClient behavior;
- complete shared-experience formula parity beyond the focused structural proof;
- generic combat correctness;
- vocation or Wheel of Destiny correctness;
- persistent guild membership or guild lifecycle;
- generic persistence redesign;
- OAM-004 player SQL / later KV atomicity;
- physical-client Party E2E closure;
- map, OTBM, `items.otb`, assets, schema or deployment.

## Lifecycle constraint

OAM-024 must remain not started until this governance reconciliation is merged, the OAM-023 active task is separately archived, and a separate durable program reconciliation is merged.
