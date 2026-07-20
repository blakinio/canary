---
task_id: CAN-20260720-oteryn-oam027-houses-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-027
status: completed
agent: "GPT-5.5 Thinking"
branch: docs/oam-027-houses-lifecycle
base_branch: main
created: 2026-07-20
updated: 2026-07-20
completed: 2026-07-20
last_verified_commit: "436b73863b81bfa1ba27f88642f3a816064759fc"
risk: medium
related_pr: "644"
depends_on:
  - canonical otbm-tooling active/mapped/audited foundation
  - completed OAM player-persistence foundation
blocks:
  - OAM-028
modules_touched:
  - houses
---

# Goal

Revalidate canonical OAM-027 `houses`, apply only independently reviewed house-transfer correctness that fits the clean target architecture, close target and Canary governance, then archive lifecycle before separate durable program reconciliation.

# Final disposition

```text
houses → ADAPT
```

# Immutable task-start baselines

- Canary: `0251b96105720cb67d5ed7a1b3ec8350baa8e312`
- Otheryn: `5003753e491250732910e9d5857b20293d1bd9ab`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `a6868920443dc285656bd016acdb2c1ea566e511`

# Accepted adaptation boundary

Task-start Otheryn and fresh upstream shared `src/map/house/house.cpp` blob `25fa954a55763bc9473234682d143c9761843403`, but blob identity was supporting evidence only. Merged legacy PR #60 final commit `a6977beb06883fb4384476315f3dc17772f99ba4` supplied the bounded accepted donor: snapshot live item collections before mutation, skip stale snapshot entries, deduplicate the depot move queue, and fail closed on invalid wrapped results while preserving the original item ID for diagnostics.

Whole-file legacy reuse was rejected because current legacy `house.cpp` also contains separately owned multichannel house ownership/mirroring architecture. No `account_house_ownership`, channel ownership, cluster handoff, protocol/client, map/OTBM, schema, asset or deployment change was imported.

# Exact target delivery

```text
Otheryn PR #55 final head: 3cfc133a835f7ad14ed8a94cc720c1f0b1a31a65
autofix.ci run 29782520081 / #167: SUCCESS
CI run 29782520156 / #202: SUCCESS
Required run 29782520075 / #184: SUCCESS
Linux debug Run Tests: SUCCESS
test-log artifact: 8477497565
test-log digest: sha256:548c9077d94c94c515bff2e33c574bcb67b5b9a31eb09124b152976eb048b349
target squash merge: c140c4bb9f40067acc36bc446c9e664e6f791c5a
```

The first ready-state Linux debug CTest on superseded head `e3c18e52940df481521ae9c8c413c3f5420a383f` passed 411/412; only a new synthetic `House` construction proof harness segfaulted without full runtime initialization, while the independent transfer-safety source-contract proof passed. The invalid harness was removed without production changes, and the final exact head passed the full suite and platform matrix.

PR #55 changed exactly five intended target paths. Target comments, reviews and review threads were empty, and target `main` had no task-start drift before expected-head squash merge.

# Canary governance proof

```text
governance PR #644 final head: a2410f8249b16cfc96991c98931d60d8c2f0e2f1
Agent Task Ownership run 29783747823 / #2924: SUCCESS
final-gate CI run 29783747923 / #4078: SUCCESS
governance changed paths: exactly 2
comments: 0
reviews: 0
review threads: 0
governance squash merge: 436b73863b81bfa1ba27f88642f3a816064759fc
```

The first governance Ownership run #2923 failed only because checkpoint `owned_paths` had not been duplicated into frontmatter `owned_paths`. The final-gate label was removed before that metadata-only repair and reapplied afterward. Final Ownership #2924 and CI #4078 passed on the repaired exact head.

The governance branch was reconstructed onto current non-overlapping Canary `main` `6b1bbadf5c9fdc9c4b5831dcfbdef9c9ed894b3d` after two independent OTBM/E2E commits. Their changed paths did not overlap OAM-027 governance or canonical house runtime, and Canary `main` remained unchanged through the final merge gate.

# Reviewed exclusions

OAM-027 does not claim generic house purchase/auction transaction atomicity, crash-safe transfer recovery, distributed or multiwriter house ownership, cross-channel house safety, Cyclopedia house-tab correctness, protocol/client UI compatibility, exhaustive rent/auction parity, physical-client house E2E closure, full Real Tibia house parity, or map/OTBM correctness.

# Lifecycle state

Target and governance stages are merged. This authoritative lifecycle PR owns only active-task deletion and archive addition. Separate one-file durable program reconciliation remains pending after this lifecycle merge. OAM-028 must remain NOT STARTED until that reconciliation merges.
