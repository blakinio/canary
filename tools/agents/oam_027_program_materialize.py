#!/usr/bin/env python3
from pathlib import Path

path = Path("docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md")
text = path.read_text(encoding="utf-8")

replacements = [
    (
        'updated: 2026-07-20T22:58:58+02:00\nlast_verified_commit: "99b9dec84d953d3f200284d0cf193261027650ca"',
        'updated: 2026-07-21T00:30:38+02:00\nlast_verified_commit: "562961ee0dd0c2626ab845dc307ec748e2a6bfb7"',
    ),
    (
        '| OAM-026 | `guilds → ADAPT` | target `418a9f0bfc72cc58b9806a49e966d9c3ea3c1a6d`; feature `5a2bc2be3b91abdd46c9edf2f825336472515299`; lifecycle `99b9dec84d953d3f200284d0cf193261027650ca` |',
        '| OAM-026 | `guilds → ADAPT` | target `418a9f0bfc72cc58b9806a49e966d9c3ea3c1a6d`; feature `5a2bc2be3b91abdd46c9edf2f825336472515299`; lifecycle `99b9dec84d953d3f200284d0cf193261027650ca` |\n| OAM-027 | `houses → ADAPT` | target `c140c4bb9f40067acc36bc446c9e664e6f791c5a`; feature `436b73863b81bfa1ba27f88642f3a816064759fc`; lifecycle `562961ee0dd0c2626ab845dc307ec748e2a6bfb7` |',
    ),
    (
        '# Current state',
        '''# OAM-027 durable completion

Final disposition:

```text
houses ADAPT
```

Task-start baselines were Canary `0251b96105720cb67d5ed7a1b3ec8350baa8e312`, Otheryn `5003753e491250732910e9d5857b20293d1bd9ab`, fresh upstream Canary `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`, and maintained OTClient `a6868920443dc285656bd016acdb2c1ea566e511`. Canonical `houses` depends on the active/mapped/audited `otbm-tooling` evidence foundation and completed player-persistence foundation.

Task-start Otheryn and fresh upstream shared `src/map/house/house.cpp` blob `25fa954a55763bc9473234682d143c9761843403`, but blob identity was supporting evidence only. Merged legacy PR #60 final commit `a6977beb06883fb4384476315f3dc17772f99ba4` supplied the bounded accepted donor: snapshot item collections before mutation, skip stale snapshot entries, deduplicate the depot move queue, and fail closed on invalid wrapped results while preserving the original item ID. Whole-file legacy reuse was rejected because current legacy `house.cpp` also contains separately owned multichannel house ownership/mirroring architecture.

Otheryn PR #55 final head `3cfc133a835f7ad14ed8a94cc720c1f0b1a31a65` changed exactly five intended target paths and no temporary materializer path. The first ready-state Linux debug CTest on superseded head `e3c18e52940df481521ae9c8c413c3f5420a383f` passed 411/412; only a new synthetic `House` proof harness segfaulted while the independent transfer-safety source-contract proof passed. The invalid harness was removed without production changes. Final autofix.ci #167 run `29782520081`, CI #202 run `29782520156`, and Required #184 run `29782520075` all succeeded on the exact final head, including Linux debug `Run Tests`. Test-log artifact `8477497565` has digest `sha256:548c9077d94c94c515bff2e33c574bcb67b5b9a31eb09124b152976eb048b349`. Comments/reviews/threads were empty, target-main drift was none, and PR #55 merged by expected-head squash as `c140c4bb9f40067acc36bc446c9e664e6f791c5a`.

Canary governance PR #644 was reconstructed onto non-overlapping Canary `main` `6b1bbadf5c9fdc9c4b5831dcfbdef9c9ed894b3d` after independent OTBM/E2E drift. Final head `a2410f8249b16cfc96991c98931d60d8c2f0e2f1` changed exactly the OAM-027 report and active-task record. The first Ownership attempt failed only because checkpoint `owned_paths` were absent from frontmatter; after the metadata-only repair, Agent Task Ownership #2924 run `29783747823` and final-gate CI #4078 run `29783747923` succeeded. Comments/reviews/threads were empty and no further main drift occurred before expected-head squash merge `436b73863b81bfa1ba27f88642f3a816064759fc`.

Authoritative lifecycle PR #647 final head `75decbd6b05e4f5a008f1db0dab110198439c683` changed exactly the active-delete/archive-add lifecycle paths. Agent Task Ownership #2926 run `29783964089` and final-gate CI #4080 run `29783972947` succeeded; heavy builds were correctly skipped for lifecycle-only scope. Comments/reviews/threads were empty, Canary `main` had no drift from the governance merge, and PR #647 merged by expected-head squash as `562961ee0dd0c2626ab845dc307ec748e2a6bfb7`.

OAM-027 does not claim generic house purchase/auction transaction atomicity, crash-safe transfer recovery, distributed or multiwriter house ownership, cross-channel house safety, Cyclopedia house-tab correctness, protocol/client UI compatibility, exhaustive rent/auction parity, physical-client house E2E closure, full Real Tibia house parity, or map/OTBM correctness. It changes no maintained OTClient, map/OTBM data, schema, assets or deployment.

# Current state''',
    ),
    (
        '''Canary reconciliation base: 99b9dec84d953d3f200284d0cf193261027650ca
Otheryn target head after OAM-026: 418a9f0bfc72cc58b9806a49e966d9c3ea3c1a6d
maintained OTClient: a6868920443dc285656bd016acdb2c1ea566e511
OAM-001..OAM-026: feature/lifecycle complete
OAM-026 task: archived
OAM-027: NOT STARTED''',
        '''Canary reconciliation base: 562961ee0dd0c2626ab845dc307ec748e2a6bfb7
Otheryn target head after OAM-027: c140c4bb9f40067acc36bc446c9e664e6f791c5a
maintained OTClient: a6868920443dc285656bd016acdb2c1ea566e511
OAM-001..OAM-027: feature/lifecycle complete
OAM-027 task: archived
OAM-028: NOT STARTED''',
    ),
    (
        '| OAM-001..OAM-026 | completed | preserve durable evidence |\n| OAM-027+ | planned, not active | only after this reconciliation merges: perform fresh live-state/open-PR/ownership and exact target/upstream/legacy preflight, then select one dependency-valid canonical package |',
        '| OAM-001..OAM-027 | completed | preserve durable evidence |\n| OAM-028+ | planned, not active | only after this reconciliation merges: perform fresh live-state/open-PR/ownership and exact target/upstream/legacy preflight, then select one dependency-valid canonical package |',
    ),
    (
        '- OAM-026 does not claim distributed guild ownership, multiwriter guild-bank safety, Real Tibia guild parity, website guild-management parity, guild-chat delivery parity, protocol/client UI parity, generic transaction atomicity, generic crash/restart durability, physical-client guild E2E closure, or map/asset/schema/deployment migration.',
        '- OAM-026 does not claim distributed guild ownership, multiwriter guild-bank safety, Real Tibia guild parity, website guild-management parity, guild-chat delivery parity, protocol/client UI parity, generic transaction atomicity, generic crash/restart durability, physical-client guild E2E closure, or map/asset/schema/deployment migration.\n- OAM-027 does not claim generic house purchase/auction transaction atomicity, crash-safe transfer recovery, distributed or multiwriter house ownership, cross-channel house safety, Cyclopedia house-tab correctness, protocol/client UI compatibility, exhaustive rent/auction parity, physical-client house E2E closure, full Real Tibia house parity, or map/OTBM correctness.',
    ),
    (
        'Merge this program-only OAM-026 completion reconciliation after exact-head Ownership/CI/review gates. Only then may a fresh OAM-027 preflight begin. OAM-027 is NOT STARTED by this record.',
        'Merge this program-only OAM-027 completion reconciliation after exact-head Ownership/CI/review gates. Only then may a fresh OAM-028 preflight begin. OAM-028 is NOT STARTED by this record.',
    ),
]

for old, new in replacements:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"expected exactly one match, found {count}: {old[:120]!r}")
    text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8")
print("materialized OAM-027 durable program reconciliation")
